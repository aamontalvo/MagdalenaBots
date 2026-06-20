# -*- coding: utf-8 -*-
"""
Analisis de calidad de caudales para estaciones comunes con niveles.

Aplica las mismas familias de pruebas usadas para niveles:
- Homogeneidad: Pettitt, SNHT, Mann-Kendall sobre medias anuales.
- Eventos abruptos: saltos diarios que superan 2 * p99 de diferencias originales.
- Outliers fisicos: valores fuera de [P1 - margen, P99 + margen] por estacion.
- Cobertura temporal: porcentaje de datos validos por estacion y ano.

Inputs:
    - caudales_formato_largo.csv

Outputs en cartillas_estaciones/caudales_comunes_niveles:
    - Resumen_Homogeneidad_Caudales.csv
    - ResumenpruebasHomogeneidad_Caudales.png
    - Eventos_Abruptos_Caudales.csv
    - Outliers_Caudales.csv
    - Cobertura_Caudales.csv
    - Heatmap_Cobertura_Caudales.png
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from scipy import stats
import sys
import warnings

warnings.filterwarnings('ignore')
sys.stdout.reconfigure(encoding='utf-8')

# Importar verificacion de integridad
from verificar_caudales_formato_largo import verificar_caudales, ESTACIONES_COMUNES

PROJECT_ROOT = Path(r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot')
INPUT_CSV = PROJECT_ROOT / 'backend' / 'data' / 'raw' / 'SERIE_CAUDALES' / 'analisis' / 'caudales_formato_largo.csv'
OUTPUT_BASE = PROJECT_ROOT / 'cartillas_estaciones' / 'caudales_comunes_niveles'
OUTPUT_BASE.mkdir(parents=True, exist_ok=True)

GEOGRAPHIC_ORDER = [
    'CALAMAR', 'MAGANGUE', 'BARBOSA', 'ARMENIA', 'RIO_NUEVO', 'LAS_PALOMAS',
    'LAS_AGUADAS', 'EL_BANCO', 'PENONCITO', 'EL_CONTENTO', 'SITIO_NUEVO'
]

STATION_NAME_MAP = {
    'CALAMAR': 'Calamar', 'MAGANGUE': 'Magangue', 'BARBOSA': 'Barbosa',
    'ARMENIA': 'Armenia', 'RIO_NUEVO': 'Rio Nuevo', 'LAS_PALOMAS': 'Las Palomas',
    'LAS_AGUADAS': 'Las Aguadas', 'EL_BANCO': 'El Banco', 'PENONCITO': 'Penoncito',
    'EL_CONTENTO': 'El Contento', 'SITIO_NUEVO': 'Sitio Nuevo'
}


def format_station_name(key):
    return STATION_NAME_MAP.get(key, key.replace('_', ' ').title())


# =============================================================================
# PRUEBAS ESTADISTICAS
# =============================================================================
def pettitt_test(data):
    """Prueba de Pettitt para detectar un punto de quiebre."""
    n = len(data)
    if n < 10:
        return None, None, None
    u = np.zeros(n)
    for t in range(1, n):
        s = 0
        for i in range(t):
            for j in range(t, n):
                s += np.sign(data[i] - data[j])
        u[t] = s
    k_opt = np.argmax(np.abs(u[1:])) + 1
    u_max = u[k_opt]
    p_value = 2 * np.exp(-6 * u_max**2 / (n**3 + n**2))
    return u_max, p_value, k_opt


def snht_test(data):
    """Standard Normal Homogeneity Test (SNHT)."""
    n = len(data)
    if n < 10:
        return None, None, None
    t_stats = []
    for k in range(1, n - 1):
        x1 = data[:k]
        x2 = data[k:]
        if len(x1) < 2 or len(x2) < 2:
            t_stats.append(0)
            continue
        mean1, mean2 = np.mean(x1), np.mean(x2)
        var = np.var(data, ddof=1)
        if var == 0:
            t_stats.append(0)
            continue
        t_k = k * (mean1 - np.mean(data))**2 / var + (n - k) * (mean2 - np.mean(data))**2 / var
        t_stats.append(t_k)
    if len(t_stats) == 0:
        return None, None, None
    t_max = np.max(t_stats)
    k_opt = np.argmax(t_stats) + 1
    return t_max, None, k_opt


def mann_kendall_test(data):
    """Prueba de Mann-Kendall para tendencias monotonicas."""
    n = len(data)
    if n < 10:
        return None, None, None
    clean_data = data[~np.isnan(data)]
    if len(clean_data) < 10:
        return None, None, None
    s = 0
    for i in range(len(clean_data) - 1):
        for j in range(i + 1, len(clean_data)):
            s += np.sign(clean_data[j] - clean_data[i])
    var_s = len(clean_data) * (len(clean_data) - 1) * (2 * len(clean_data) + 5) / 18
    if var_s == 0:
        return None, None, None
    if s > 0:
        z = (s - 1) / np.sqrt(var_s)
    elif s < 0:
        z = (s + 1) / np.sqrt(var_s)
    else:
        z = 0
    p_value = 2 * (1 - stats.norm.cdf(abs(z)))
    tau = s / (len(clean_data) * (len(clean_data) - 1) / 2)
    return tau, p_value, s


# =============================================================================
# PREPARACION
# =============================================================================
def get_station_annual_stats(df, station):
    """Obtiene estadisticas anuales de caudal para una estacion."""
    station_data = df[df['estacion'] == station].copy()
    annual = station_data.groupby('year').agg({
        'caudal': ['mean', 'median', 'std', 'count']
    }).reset_index()
    annual.columns = ['year', 'mean_q', 'median_q', 'std_q', 'count']
    annual = annual[annual['count'] >= 300]
    return annual


def homogeneity_tests_by_station(df):
    """Aplica pruebas de homogeneidad a cada estacion."""
    results = []
    for station in GEOGRAPHIC_ORDER:
        if station not in df['estacion'].values:
            continue
        annual = get_station_annual_stats(df, station)
        if len(annual) < 10:
            continue
        q_values = annual['mean_q'].values
        years = annual['year'].values

        pettitt_stat, pettitt_p, pettitt_idx = pettitt_test(q_values)
        pettitt_year = years[pettitt_idx] if pettitt_idx is not None else None

        snht_stat, _, snht_idx = snht_test(q_values)
        snht_year = years[snht_idx] if snht_idx is not None else None

        mk_tau, mk_p, mk_s = mann_kendall_test(q_values)

        results.append({
            'station': station,
            'n_years': len(annual),
            'period_start': int(years.min()),
            'period_end': int(years.max()),
            'pettitt_stat': round(pettitt_stat, 2) if pettitt_stat is not None else None,
            'pettitt_p': round(pettitt_p, 4) if pettitt_p is not None else None,
            'pettitt_year': int(pettitt_year) if pettitt_year is not None else None,
            'pettitt_significant': pettitt_p < 0.05 if pettitt_p is not None else False,
            'snht_stat': round(snht_stat, 2) if snht_stat is not None else None,
            'snht_year': int(snht_year) if snht_year is not None else None,
            'mk_tau': round(mk_tau, 3) if mk_tau is not None else None,
            'mk_p': round(mk_p, 4) if mk_p is not None else None,
            'mk_significant': mk_p < 0.05 if mk_p is not None else False,
            'trend': 'Creciente' if mk_tau and mk_tau > 0 and mk_p < 0.05
                     else 'Decreciente' if mk_tau and mk_tau < 0 and mk_p < 0.05
                     else 'Sin tendencia'
        })
    return pd.DataFrame(results)


# =============================================================================
# VISUALIZACION HOMOGENEIDAD
# =============================================================================
def plot_homogeneity_tests_summary(homog_results, output_path):
    """Genera figura resumen de pruebas de homogeneidad."""
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))

    stations = homog_results['station'].values
    x_pos = np.arange(len(stations))
    labels = [format_station_name(s) for s in stations]

    # Pettitt
    ax = axes[0, 0]
    colors = ['red' if sig else 'gray' for sig in homog_results['pettitt_significant']]
    ax.bar(x_pos, homog_results['pettitt_stat'].fillna(0), color=colors, alpha=0.7)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=9)
    ax.set_ylabel('Estadistico de Pettitt', fontsize=10)
    ax.set_title('Prueba de Pettitt - Cambio de Regimen', fontsize=11, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')

    # SNHT
    ax = axes[0, 1]
    snht_vals = homog_results['snht_stat'].fillna(0)
    colors = ['red' if v > 9.5 else 'gray' for v in snht_vals]
    ax.bar(x_pos, snht_vals, color=colors, alpha=0.7)
    ax.axhline(y=9.5, color='red', linestyle='--', linewidth=1.5, label='Umbral significativo')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=9)
    ax.set_ylabel('Estadistico SNHT', fontsize=10)
    ax.set_title('Prueba SNHT - Salto en la Media', fontsize=11, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')

    # Mann-Kendall
    ax = axes[1, 0]
    tau_vals = homog_results['mk_tau'].fillna(0)
    colors = ['blue' if t > 0 and p else 'red' if t < 0 and p else 'gray'
              for t, p in zip(tau_vals, homog_results['mk_significant'])]
    ax.bar(x_pos, tau_vals, color=colors, alpha=0.7)
    ax.axhline(y=0, color='black', linestyle='-', linewidth=1)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=9)
    ax.set_ylabel('Tau de Kendall', fontsize=10)
    ax.set_title('Prueba Mann-Kendall - Tendencia', fontsize=11, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')

    # Anos de datos
    ax = axes[1, 1]
    ax.bar(x_pos, homog_results['n_years'], color='steelblue', alpha=0.7)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=9)
    ax.set_ylabel('Numero de anos con datos', fontsize=10)
    ax.set_title('Longitud de Registros por Estacion', fontsize=11, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')

    fig.suptitle('Resumen de Pruebas de Homogeneidad - Caudales', fontsize=14, fontweight='bold')
    plt.tight_layout(rect=[0, 0, 1, 0.97])
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()


# =============================================================================
# EVENTOS ABRUPTOS
# =============================================================================
def detectar_eventos_abruptos(df):
    """Detecta saltos bruscos en la serie diaria de caudal."""
    eventos = []
    for est in GEOGRAPHIC_ORDER:
        subset = df[df['estacion'] == est].sort_values('fecha').reset_index(drop=True)
        if len(subset) < 3:
            continue
        subset['diff'] = subset['caudal'].diff().abs()
        orig_diff = subset['diff'].dropna()
        if len(orig_diff) < 10:
            continue
        p99_diff = orig_diff.quantile(0.99)
        umbral = 2 * p99_diff

        candidatos = subset[subset['diff'] > umbral].copy()
        for _, row in candidatos.iterrows():
            idx = int(row.name)
            caudal_actual = row['caudal']
            caudal_previo = subset.loc[idx - 1, 'caudal'] if idx > 0 else np.nan
            eventos.append({
                'estacion': est,
                'fecha': row['fecha'].date(),
                'year': row['year'],
                'caudal_actual': round(caudal_actual, 3),
                'caudal_previo': round(caudal_previo, 3) if pd.notna(caudal_previo) else None,
                'diferencia': round(row['diff'], 3),
                'umbral_p99_x2': round(umbral, 3),
                'p99_diff_orig': round(p99_diff, 3)
            })
    return pd.DataFrame(eventos)


# =============================================================================
# OUTLIERS FISICOS
# =============================================================================
def detectar_outliers_fisicos(df):
    """Detecta valores originales fuera del rango fisico esperado."""
    outliers = []
    for est in GEOGRAPHIC_ORDER:
        subset = df[(df['estacion'] == est) & (df['caudal'].notna())].copy()
        if len(subset) < 10:
            continue
        p01 = subset['caudal'].quantile(0.01)
        p99 = subset['caudal'].quantile(0.99)
        margin = (p99 - p01) * 0.3
        lim_inf = p01 - margin
        lim_sup = p99 + margin

        sospechosos = subset[(subset['caudal'] < lim_inf) | (subset['caudal'] > lim_sup)]
        for _, row in sospechosos.iterrows():
            outliers.append({
                'estacion': est,
                'fecha': row['fecha'].date(),
                'year': row['year'],
                'caudal': round(row['caudal'], 3),
                'p01': round(p01, 3),
                'p99': round(p99, 3),
                'limite_inferior': round(lim_inf, 3),
                'limite_superior': round(lim_sup, 3)
            })
    return pd.DataFrame(outliers)


# =============================================================================
# COBERTURA
# =============================================================================
def calcular_cobertura(df):
    """Calcula cobertura de datos por estacion y ano."""
    cobertura = []
    for est in GEOGRAPHIC_ORDER:
        est_data = df[df['estacion'] == est]
        years = sorted(est_data['year'].unique())
        for year in range(int(min(years)), int(max(years)) + 1):
            year_data = est_data[est_data['year'] == year]
            total_expected = 366 if pd.Timestamp(year, 12, 31).dayofyear == 366 else 365
            available = year_data['caudal'].notna().sum()
            missing_pct = ((total_expected - available) / total_expected) * 100
            cobertura.append({
                'estacion': est,
                'year': year,
                'available': available,
                'expected': total_expected,
                'missing_pct': round(missing_pct, 1),
                'coverage_pct': round(100 - missing_pct, 1)
            })
    return pd.DataFrame(cobertura)


def plot_cobertura_heatmap(coverage_df, output_path):
    """Genera heatmap de cobertura de datos."""
    pivot = coverage_df.pivot(index='estacion', columns='year', values='missing_pct')
    available = [s for s in GEOGRAPHIC_ORDER if s in pivot.index]
    pivot = pivot.reindex(available)
    pivot.index = [format_station_name(s) for s in pivot.index]

    station_start_years = {s: coverage_df[coverage_df['estacion'] == s]['year'].min()
                           for s in pivot.index}
    mask = np.zeros_like(pivot, dtype=bool)
    for i, station in enumerate(pivot.index):
        start_year = station_start_years[station]
        for j, year in enumerate(pivot.columns):
            if year < start_year:
                mask[i, j] = True

    fig, ax = plt.subplots(figsize=(16, 8))
    sns.heatmap(pivot, mask=mask, cmap='Blues', vmin=0, vmax=100,
                cbar_kws={'label': '% Datos Faltantes'}, ax=ax,
                linewidths=0.5, linecolor='white')

    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):
            if mask[i, j]:
                ax.add_patch(plt.Rectangle((j, i), 1, 1, fill=True,
                                           facecolor='#CCCCCC', edgecolor='white', linewidth=0.5))

    ax.set_xlabel('Ano', fontsize=12)
    ax.set_ylabel('Estacion', fontsize=12)
    ax.set_title('Mapa de Calor: Cobertura de Datos de Caudales', fontsize=14, fontweight='bold', pad=20)
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()


# =============================================================================
# MAIN
# =============================================================================
def main():
    print('=' * 70)
    print('ANALISIS DE CALIDAD DE CAUDALES - ESTACIONES COMUNES CON NIVELES')
    print('=' * 70)

    # Verificar integridad
    print('\n' + '-' * 70)
    print('VERIFICANDO INTEGRIDAD DE DATOS')
    print('-' * 70)
    ok, reporte = verificar_caudales(
        csv_path=INPUT_CSV,
        estaciones_comunes=set(GEOGRAPHIC_ORDER)
    )
    print(reporte)
    if not ok:
        print('\n[ERROR] La verificacion de integridad fallo. No se generaran analisis.')
        sys.exit(1)

    df = pd.read_csv(INPUT_CSV, parse_dates=['fecha'])
    df['estacion'] = df['estacion'].str.upper().str.strip()
    df['year'] = df['fecha'].dt.year
    df['month'] = df['fecha'].dt.month
    df = df[df['estacion'].isin(GEOGRAPHIC_ORDER)].copy()

    print(f'\nRegistros cargados: {len(df):,}')
    print(f'Estaciones: {sorted(GEOGRAPHIC_ORDER)}')

    # 1. Homogeneidad
    print('\n' + '-' * 70)
    print('1. PRUEBAS DE HOMOGENEIDAD')
    print('-' * 70)
    homog = homogeneity_tests_by_station(df)
    homog.to_csv(OUTPUT_BASE / 'Resumen_Homogeneidad_Caudales.csv', index=False, encoding='utf-8-sig')
    plot_homogeneity_tests_summary(homog, OUTPUT_BASE / 'ResumenpruebasHomogeneidad_Caudales.png')
    print(f'  Registros: {len(homog)} estaciones')
    print(f'  Cambios significativos Pettitt: {homog["pettitt_significant"].sum()}')
    print(f'  Tendencias significativas MK: {homog["mk_significant"].sum()}')

    # 2. Eventos abruptos
    print('\n' + '-' * 70)
    print('2. EVENTOS ABRUPTOS')
    print('-' * 70)
    eventos = detectar_eventos_abruptos(df)
    eventos.to_csv(OUTPUT_BASE / 'Eventos_Abruptos_Caudales.csv', index=False, encoding='utf-8-sig')
    print(f'  Eventos detectados: {len(eventos)}')

    # 3. Outliers fisicos
    print('\n' + '-' * 70)
    print('3. OUTLIERS FISICOS')
    print('-' * 70)
    outliers = detectar_outliers_fisicos(df)
    outliers.to_csv(OUTPUT_BASE / 'Outliers_Caudales.csv', index=False, encoding='utf-8-sig')
    print(f'  Outliers detectados: {len(outliers)}')

    # 4. Cobertura
    print('\n' + '-' * 70)
    print('4. COBERTURA TEMPORAL')
    print('-' * 70)
    cobertura = calcular_cobertura(df)
    cobertura.to_csv(OUTPUT_BASE / 'Cobertura_Caudales.csv', index=False, encoding='utf-8-sig')
    plot_cobertura_heatmap(cobertura, OUTPUT_BASE / 'Heatmap_Cobertura_Caudales.png')
    print(f'  Registros de cobertura: {len(cobertura)}')

    print('\n' + '=' * 70)
    print('PROCESO COMPLETADO')
    print(f'Resultados en: {OUTPUT_BASE}')
    print('=' * 70)


if __name__ == '__main__':
    main()
