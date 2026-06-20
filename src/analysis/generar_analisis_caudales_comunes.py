# -*- coding: utf-8 -*-
"""
Analisis de caudales para estaciones comunes con niveles (Rio Magdalena).

Inputs:
    - caudales_formato_largo.csv (generado por analisis_caudales.py)

Outputs:
    - Cartillas por estacion (11 estaciones coincidentes con niveles):
        * Fig1_Serie_Tiempo_{estacion}.png
        * Fig2_Violin_Mensual_{estacion}.png
        * Fig4_Curvas_Excedidos_{estacion}.png
        * Fig4_Percentiles_{estacion}.csv
    - Figuras generales:
        * Boxplots_GeneralEstaciones_Caudales.png
        * MatrixCorrelationCaudales.png
        * Matriz_Correlacion_Caudales.csv
        * Matriz_N_Concurrentes_Caudales.csv

Solo se usan las 11 estaciones de caudales que tambien existen en los datos de niveles.
Los datos originales son inmutables; la imputacion ligera solo se usa para visualizacion.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from pathlib import Path
from scipy.stats import pearsonr
import sys
import warnings

warnings.filterwarnings('ignore')
sys.stdout.reconfigure(encoding='utf-8')

# Importar verificacion de integridad
from verificar_caudales_formato_largo import verificar_caudales, ESTACIONES_COMUNES

# -----------------------------------------------------------------------------
# CONFIGURACION
# -----------------------------------------------------------------------------
INPUT_CSV = Path(r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\backend\data\raw\SERIE_CAUDALES\analisis\caudales_formato_largo.csv')
OUTPUT_BASE = Path(r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\cartillas_estaciones\caudales_comunes_niveles')
OUTPUT_BASE.mkdir(parents=True, exist_ok=True)

# 11 estaciones comunes con niveles, orden geografico (aguas abajo -> aguas arriba)
GEOGRAPHIC_ORDER = [
    'CALAMAR',
    'MAGANGUE',
    'BARBOSA',
    'ARMENIA',
    'RIO_NUEVO',
    'LAS_PALOMAS',
    'LAS_AGUADAS',
    'EL_BANCO',
    'PENONCITO',
    'EL_CONTENTO',
    'SITIO_NUEVO',
]

STATION_NAME_MAP = {
    'CALAMAR': 'Calamar',
    'MAGANGUE': 'Magangue',
    'BARBOSA': 'Barbosa',
    'ARMENIA': 'Armenia',
    'RIO_NUEVO': 'Rio Nuevo',
    'LAS_PALOMAS': 'Las Palomas',
    'LAS_AGUADAS': 'Las Aguadas',
    'EL_BANCO': 'El Banco',
    'PENONCITO': 'Penoncito',
    'EL_CONTENTO': 'El Contento',
    'SITIO_NUEVO': 'Sitio Nuevo',
}

MESES = ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN',
         'JUL', 'AGO', 'SEP', 'OCT', 'NOV', 'DIC']

plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['axes.grid'] = True


# -----------------------------------------------------------------------------
# FUNCIONES AUXILIARES
# -----------------------------------------------------------------------------
def format_station_name(key):
    """Formatea nombre de estacion: EL_CONTENTO -> El Contento."""
    return STATION_NAME_MAP.get(key, key.replace('_', ' ').title())


def imputar_ligero(df_est, limit_interp=15):
    """
    Imputacion minima para visualizacion. Marca originales vs imputados.
    1. Interpolacion lineal (limit_interp dias)
    2. Mediana del mismo mes-dia historico
    3. Mediana mensual historica
    """
    df = df_est.sort_values('fecha').copy().reset_index(drop=True)
    df['originales'] = df['caudal'].notna()

    # Interpolacion lineal
    df['caudal'] = df['caudal'].interpolate(method='linear', limit=limit_interp)

    # Mediana por mes-dia
    df['mes_dia'] = df['fecha'].dt.strftime('%m-%d')
    doy_median = df.groupby('mes_dia')['caudal'].median()
    missing = df['caudal'].isna()
    if missing.any():
        df.loc[missing, 'caudal'] = df.loc[missing, 'mes_dia'].map(doy_median)

    # Mediana mensual
    if df['caudal'].isna().any():
        df['mes_num'] = df['fecha'].dt.month
        mon_median = df.groupby('mes_num')['caudal'].median()
        missing = df['caudal'].isna()
        df.loc[missing, 'caudal'] = df.loc[missing, 'mes_num'].map(mon_median)

    return df


def serie_continua(df_est):
    """Genera serie continua desde la primera hasta la ultima fecha valida."""
    df = df_est.dropna(subset=['caudal']).copy()
    if df.empty:
        return df_est.copy()
    fecha_min = df['fecha'].min()
    fecha_max = df['fecha'].max()
    rango = pd.date_range(start=fecha_min, end=fecha_max, freq='D')
    rango = rango[rango.strftime('%m-%d') != '02-29']
    df_full = pd.DataFrame({'fecha': rango})
    df_full = df_full.merge(df_est[['fecha', 'caudal']], on='fecha', how='left')
    return df_full


# -----------------------------------------------------------------------------
# CARTILLAS POR ESTACION
# -----------------------------------------------------------------------------
def generar_fig1_serie_tiempo(df, est_key, est_name, output_dir):
    """Fig1 - Serie de tiempo completa (originales e imputados)."""
    fig, ax = plt.subplots(figsize=(16, 6))

    # Serie completa (con imputacion ligera)
    df_full = serie_continua(df)
    df_full = imputar_ligero(df_full)

    # Origenales e imputados
    ax.plot(df_full['fecha'], df_full['caudal'], color='black', linewidth=0.6, alpha=0.85)

    # Destacar datos originales con puntos mas oscuros
    df_orig = df_full[df_full['originales'] == True]
    if len(df_orig) > 0:
        ax.scatter(df_orig['fecha'], df_orig['caudal'], color='#1565C0', s=2, alpha=0.5, label='Original', zorder=3)

    fecha_inicio = df_full['fecha'].min()
    fecha_fin = df_full['fecha'].max()
    start_year = fecha_inicio.year
    end_year = fecha_fin.year

    ticks = []
    tick_labels = []
    for year in range(start_year, end_year + 1, 5):
        ticks.append(pd.Timestamp(f'{year}-01-01'))
        tick_labels.append(str(year))
    if end_year not in [t.year for t in ticks]:
        ticks.append(pd.Timestamp(f'{end_year}-01-01'))
        tick_labels.append(str(end_year))

    ax.set_xticks(ticks)
    ax.set_xticklabels(tick_labels, rotation=0, ha='center')
    ax.xaxis.set_minor_locator(mdates.YearLocator())

    ax.set_xlabel('Fecha', fontsize=12, fontweight='bold')
    ax.set_ylabel('Caudal (m3/s)', fontsize=12, fontweight='bold')
    ax.set_title(f'Serie de Tiempo - {est_name}', fontsize=14, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3, which='major')
    ax.grid(True, alpha=0.15, which='minor', linestyle=':')

    total = len(df_full)
    orig = int(df_full['originales'].sum())
    imp = total - orig
    pct_orig = (orig / total) * 100
    pct_imp = (imp / total) * 100

    info = (f'Periodo: {start_year}-{end_year}\n'
            f'Total: {total:,} registros\n'
            f'Original: {pct_orig:.1f}% | Imputado: {pct_imp:.1f}%')
    ax.text(0.02, 0.98, info, transform=ax.transAxes, fontsize=10,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.6))

    ax.legend(loc='upper right', fontsize=9)

    plt.tight_layout()
    out = output_dir / f'Fig1_Serie_Tiempo_{est_key}.png'
    plt.savefig(out, dpi=300, bbox_inches='tight')
    plt.close()
    print(f'  Fig1 guardada: {out.name}')


def generar_fig2_violin_mensual(df, est_key, est_name, output_dir):
    """Fig2 - Violin plot mensual multianual con boxplot interno y media."""
    fig, ax = plt.subplots(figsize=(14, 7))

    df_full = serie_continua(df)
    df_full = imputar_ligero(df_full)
    df_clean = df_full.dropna(subset=['caudal'])

    data_by_month = [df_clean[df_clean['fecha'].dt.month == m]['caudal'].values
                     for m in range(1, 13)]

    violin_parts = ax.violinplot(data_by_month, positions=range(1, 13), widths=0.7,
                                 showmeans=False, showmedians=False, showextrema=False)

    for pc in violin_parts['bodies']:
        pc.set_facecolor('#E0E0E0')
        pc.set_edgecolor('black')
        pc.set_alpha(0.7)

    bp = ax.boxplot(data_by_month, positions=range(1, 13), widths=0.15,
                    patch_artist=True, showfliers=False,
                    medianprops=dict(color='black', linewidth=2),
                    boxprops=dict(facecolor='black', alpha=0.3),
                    whiskerprops=dict(color='black'),
                    capprops=dict(color='black'))

    monthly_means = df_clean.groupby(df_clean['fecha'].dt.month)['caudal'].mean()
    months_with_data = sorted(monthly_means.index)
    ax.plot(months_with_data, monthly_means.loc[months_with_data].values,
            'k--', linewidth=2, label='Media mensual multianual', marker='o', markersize=4)

    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(MESES)
    ax.set_title(f'Distribucion Mensual Multianual de Caudales - {est_name}',
                 fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel('Mes', fontsize=12, fontweight='bold')
    ax.set_ylabel('Caudal (m3/s)', fontsize=12, fontweight='bold')
    ax.legend(loc='best', fontsize=10)
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    out = output_dir / f'Fig2_Violin_Mensual_{est_key}.png'
    plt.savefig(out, dpi=300, bbox_inches='tight')
    plt.close()
    print(f'  Fig2 guardada: {out.name}')


def generar_fig4_excedidos(df, est_key, est_name, output_dir):
    """Fig4 - Curvas de frecuencia de caudales excedidos (percentiles diarios)."""
    df_full = serie_continua(df)
    df_full = imputar_ligero(df_full)
    df_full['mes_dia'] = df_full['fecha'].dt.strftime('%m-%d')

    ref_2020 = pd.DataFrame({'fecha': pd.date_range('2020-01-01', '2020-12-31', freq='D')})
    ref_2020['mes_dia'] = ref_2020['fecha'].dt.strftime('%m-%d')
    ref_2020 = ref_2020[ref_2020['mes_dia'] != '02-29'].copy().reset_index(drop=True)
    ref_2020['day_of_year'] = range(1, 366)
    doy_map = ref_2020.set_index('mes_dia')['day_of_year'].to_dict()

    df_full['day_of_year'] = df_full['mes_dia'].map(doy_map)

    percentiles = []
    for doy in range(1, 366):
        vals = df_full.loc[df_full['day_of_year'] == doy, 'caudal'].dropna().values
        if len(vals) > 0:
            percentiles.append({
                'day_of_year': doy,
                'mes_dia': ref_2020.loc[ref_2020['day_of_year'] == doy, 'mes_dia'].values[0],
                'max': round(np.max(vals), 3),
                'p95': round(np.percentile(vals, 95), 3),
                'p75': round(np.percentile(vals, 75), 3),
                'p50': round(np.percentile(vals, 50), 3),
                'p25': round(np.percentile(vals, 25), 3),
                'p5': round(np.percentile(vals, 5), 3),
                'min': round(np.min(vals), 3),
                'n_obs': len(vals)
            })

    pct_df = pd.DataFrame(percentiles)
    pct_df.to_csv(output_dir / f'Fig4_Percentiles_{est_key}.csv', index=False, encoding='utf-8-sig')

    fig, ax = plt.subplots(figsize=(14, 8))
    days = pct_df['day_of_year'].values

    colors = {
        'max': 'black', 'p95': '#8B0000', 'p75': '#6B8E23',
        'p50': 'black', 'p25': '#5DADE2', 'p5': '#D35400', 'min': 'black'
    }
    linewidths = {
        'max': 1.2, 'p95': 1.2, 'p75': 1.2, 'p50': 2.5,
        'p25': 1.2, 'p5': 1.2, 'min': 1.2
    }

    for col in ['max', 'p95', 'p75', 'p50', 'p25', 'p5', 'min']:
        ax.plot(days, pct_df[col], color=colors[col], linewidth=linewidths[col])

    ax.axvline(x=365, color='black', linewidth=2.5, linestyle='-', zorder=10)

    x_label = 368
    last_day = pct_df[pct_df['day_of_year'] == 365].iloc[0]
    labels_data = [
        ('max', last_day['max'], 'MAX'),
        ('p95', last_day['p95'], '5%'),
        ('p75', last_day['p75'], '25%'),
        ('p50', last_day['p50'], '50%'),
        ('p25', last_day['p25'], '75%'),
        ('p5', last_day['p5'], '95%'),
        ('min', last_day['min'], 'MIN')
    ]

    for col, value, label in labels_data:
        ax.text(x_label, value, label, fontsize=11, fontweight='bold',
                color=colors[col], va='center', ha='left')

    month_days = [1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335]

    ax.set_xlim(1, 365)
    ax.set_xticks(month_days)
    ax.set_xticklabels(MESES, fontsize=11)
    ax.grid(True, alpha=0.3, which='both', linestyle='-', linewidth=0.5)
    ax.minorticks_on()
    ax.grid(True, alpha=0.15, which='minor', linestyle=':', linewidth=0.5)

    ax.set_xlabel('Mes', fontsize=12, fontweight='bold')
    ax.set_ylabel('Caudal (m3/s)', fontsize=12, fontweight='bold')
    ax.set_title(f'Curvas de Frecuencia de Caudales Excedidos - {est_name}',
                 fontsize=14, fontweight='bold', pad=20)

    y_min = pct_df['min'].min() * 0.9
    y_max = pct_df['max'].max() * 1.05
    ax.set_ylim(y_min, y_max)

    plt.tight_layout()
    plt.subplots_adjust(right=0.88)

    out = output_dir / f'Fig4_Curvas_Excedidos_{est_key}.png'
    plt.savefig(out, dpi=300, bbox_inches='tight')
    plt.close()
    print(f'  Fig4 guardada: {out.name}')


# -----------------------------------------------------------------------------
# FIGURAS GENERALES
# -----------------------------------------------------------------------------
def generar_boxplot_general(df_total):
    """Boxplot general de todas las estaciones en escala de grises, orden geografico."""
    available = [s for s in GEOGRAPHIC_ORDER if s in df_total['estacion'].values]
    df_filtered = df_total[df_total['estacion'].isin(available)].copy()
    df_filtered['estacion_label'] = df_filtered['estacion'].apply(format_station_name)

    # Orden para el plot
    order_labels = [format_station_name(s) for s in available]

    fig, ax = plt.subplots(figsize=(16, 8))

    sns.boxplot(data=df_filtered, x='estacion_label', y='caudal', order=order_labels,
                color='lightgray', ax=ax,
                medianprops=dict(color='black', linewidth=2),
                boxprops=dict(edgecolor='black', facecolor='white'),
                whiskerprops=dict(color='black'),
                capprops=dict(color='black'))

    ax.set_xlabel('Estacion - aguas abajo a aguas arriba', fontsize=12, fontweight='bold')
    ax.set_ylabel('Caudal (m3/s)', fontsize=12, fontweight='bold')
    ax.set_title('Distribucion de Caudales por Estacion - Rio Magdalena',
                 fontsize=14, fontweight='bold', pad=20)
    plt.xticks(rotation=45, ha='right')
    ax.grid(True, alpha=0.3, axis='y')

    # Lineas divisorias de zonas
    zona_baja_end = 2   # indices: Calamar, Magangue, Barbosa
    zona_media_end = 7  # hasta Penoncito

    if len(available) > zona_baja_end + 1:
        ax.axvline(x=zona_baja_end + 0.5, color='black', linestyle='--', linewidth=1.5, alpha=0.7)
    if len(available) > zona_media_end + 1:
        ax.axvline(x=zona_media_end + 0.5, color='black', linestyle='--', linewidth=1.5, alpha=0.7)

    # Anotaciones de zona (centradas en sus respectivas secciones)
    n = len(available)
    x_baja = ((min(zona_baja_end, n - 1) + 1) / 2) / n if n > 0 else 0.15
    x_media = ((zona_baja_end + 1) + (min(zona_media_end, n - 1) + 1)) / 2 / n if n > zona_baja_end else 0.5
    x_alta = ((zona_media_end + 1) + n) / 2 / n if n > zona_media_end else 0.85

    if len(available) > 0:
        ax.text(x_baja, 0.98, 'Zona Baja', transform=ax.transAxes, fontsize=11, fontweight='bold',
                verticalalignment='top', horizontalalignment='center',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    if len(available) > zona_baja_end + 1:
        ax.text(x_media, 0.98, 'Zona Media', transform=ax.transAxes, fontsize=11, fontweight='bold',
                verticalalignment='top', horizontalalignment='center',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    if len(available) > zona_media_end + 1:
        ax.text(x_alta, 0.98, 'Zona Alta', transform=ax.transAxes, fontsize=11, fontweight='bold',
                verticalalignment='top', horizontalalignment='center',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.tight_layout()
    out = OUTPUT_BASE / 'Boxplots_GeneralEstaciones_Caudales.png'
    plt.savefig(out, dpi=300, bbox_inches='tight')
    plt.close()
    print(f'Figura general guardada: {out.name}')


def generar_matriz_correlacion(df_total):
    """Matriz de correlacion de Pearson usando SOLO datos originales concurrentes."""
    available = [s for s in GEOGRAPHIC_ORDER if s in df_total['estacion'].values]
    df_orig = df_total[df_total['caudal'].notna()].copy()

    corr_matrix = pd.DataFrame(index=available, columns=available, dtype=float)
    n_matrix = pd.DataFrame(index=available, columns=available, dtype=float)

    for s1 in available:
        for s2 in available:
            if s1 == s2:
                corr_matrix.loc[s1, s2] = 1.0
                n_matrix.loc[s1, s2] = df_orig[df_orig['estacion'] == s1].shape[0]
            else:
                d1 = df_orig[df_orig['estacion'] == s1][['fecha', 'caudal']].rename(columns={'caudal': 'caudal_1'})
                d2 = df_orig[df_orig['estacion'] == s2][['fecha', 'caudal']].rename(columns={'caudal': 'caudal_2'})
                merged = pd.merge(d1, d2, on='fecha', how='inner').dropna()
                n = len(merged)
                n_matrix.loc[s1, s2] = n
                if n > 30:
                    corr, _ = pearsonr(merged['caudal_1'], merged['caudal_2'])
                    corr_matrix.loc[s1, s2] = corr
                else:
                    corr_matrix.loc[s1, s2] = np.nan

    # Guardar CSVs
    corr_matrix.to_csv(OUTPUT_BASE / 'Matriz_Correlacion_Caudales.csv', encoding='utf-8-sig')
    n_matrix.to_csv(OUTPUT_BASE / 'Matriz_N_Concurrentes_Caudales.csv', encoding='utf-8-sig')

    # Plot
    formatted_names = [format_station_name(s) for s in available]
    corr_plot = corr_matrix.copy()
    corr_plot.index = formatted_names
    corr_plot.columns = formatted_names

    fig, ax = plt.subplots(figsize=(12, 10))
    mask = np.triu(np.ones_like(corr_plot, dtype=bool), k=1)

    sns.heatmap(corr_plot, mask=mask, annot=True, fmt='.2f', cmap='Blues',
                vmin=0, vmax=1, linewidths=0.5, linecolor='white',
                cbar_kws={'label': 'Correlacion de Pearson'}, ax=ax,
                annot_kws={'size': 9})

    ax.set_title('Matriz de Correlacion de Caudales',
                 fontsize=14, fontweight='bold', pad=20)
    ax.minorticks_off()
    ax.grid(False)
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()

    out = OUTPUT_BASE / 'MatrixCorrelationCaudales.png'
    plt.savefig(out, dpi=300, bbox_inches='tight')
    plt.close()
    print(f'Figura general guardada: {out.name}')


# -----------------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------------
def main():
    print('=' * 70)
    print('ANALISIS DE CAUDALES - ESTACIONES COMUNES CON NIVELES')
    print('=' * 70)

    # Verificar integridad de datos antes de procesar
    print('\n' + '-' * 70)
    print('VERIFICANDO INTEGRIDAD DE DATOS')
    print('-' * 70)
    ok, reporte = verificar_caudales(
        csv_path=INPUT_CSV,
        estaciones_comunes=set(GEOGRAPHIC_ORDER)
    )
    print(reporte)
    if not ok:
        print('\n[ERROR] La verificacion de integridad fallo. No se generaran figuras.')
        sys.exit(1)

    df_total = pd.read_csv(INPUT_CSV, parse_dates=['fecha'])
    df_total['estacion'] = df_total['estacion'].str.upper().str.strip()
    df_total = df_total[df_total['estacion'].isin(GEOGRAPHIC_ORDER)].copy()

    print(f'\nRegistros cargados: {len(df_total):,}')
    print(f'Estaciones a procesar ({len(GEOGRAPHIC_ORDER)}):')
    for e in GEOGRAPHIC_ORDER:
        print(f'  - {format_station_name(e)}')

    # --- Figuras generales ---
    print('\n' + '-' * 70)
    print('GENERANDO FIGURAS GENERALES')
    print('-' * 70)
    generar_boxplot_general(df_total)
    generar_matriz_correlacion(df_total)

    # --- Cartillas por estacion ---
    print('\n' + '-' * 70)
    print('GENERANDO CARTILLAS POR ESTACION')
    print('-' * 70)

    for est_key in GEOGRAPHIC_ORDER:
        est_name = format_station_name(est_key)
        out_dir = OUTPUT_BASE / est_key
        out_dir.mkdir(parents=True, exist_ok=True)

        df_est = df_total[df_total['estacion'] == est_key].copy()
        if df_est.empty:
            print(f'\n[ADVERTENCIA] Sin datos para {est_name}')
            continue

        print(f'\n>>> {est_name} ({est_key}) - {df_est["caudal"].notna().sum():,} registros originales')
        generar_fig1_serie_tiempo(df_est, est_key, est_name, out_dir)
        generar_fig2_violin_mensual(df_est, est_key, est_name, out_dir)
        generar_fig4_excedidos(df_est, est_key, est_name, out_dir)

    print('\n' + '=' * 70)
    print('PROCESO COMPLETADO')
    print(f'Resultados en: {OUTPUT_BASE}')
    print('=' * 70)


if __name__ == '__main__':
    main()
