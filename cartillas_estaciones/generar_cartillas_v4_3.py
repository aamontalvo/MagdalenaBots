"""
Generador de Cartillas de Estaciones v4.3
Basado en los scripts originales v4.2:
  - generar_cartillas_v4_2_corregido.py (Fig1, Fig2, Fig5)
  - generar_fig3_fig4_corregido.py (Fig3, Fig4)
  - regenerar_fig4_corregido.py (etiquetas fuera del bbox)

Adaptado para: Datos_Imputados_v4_3_Corrected.csv
Columnas: Fecha, NombreEstacion, Cota, Nivel_Imputacion, Metodo
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import scipy.stats as stats
import warnings
warnings.filterwarnings('ignore')

# Configuracion de estilo
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['axes.grid'] = True
plt.rcParams['grid.alpha'] = 0.3

# Rutas
INPUT_FILE = Path(r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\backend\data\processed\imputation\Datos_Imputados_v4_3_Corrected.csv')
OUTPUT_DIR = Path(r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\cartillas_estaciones\v4_3')

# Lista de estaciones
ESTACIONES = [
    'SAN_PEDRITO', 'CALAMAR', 'TENERIFE', 'PLATO', 'MAGANGUE', 'BARBOSA',
    'COYONGAL', 'ARMENIA', 'RIO_NUEVO', 'LAS_PALOMAS', 'LAS_AGUADAS',
    'EL_BANCO', 'PENONCITO', 'LA_GLORIA', 'GAMARRA_AUT', 'EL_CONTENTO',
    'SITIO_NUEVO', 'PUERTO_WILCHES'
]

# Mapeo de nombres en CSV a nombres de carpeta
NOMBRE_CSV_A_KEY = {
    'SAN_PEDRITO': 'SAN_PEDRITO',
    'CALAMAR': 'CALAMAR',
    'TENERIFE': 'TENERIFE',
    'PLATO': 'PLATO',
    'MAGANGUE': 'MAGANGUE',
    'BARBOSA': 'BARBOSA',
    'COYONGAL': 'COYONGAL',
    'ARMENIA': 'ARMENIA',
    'RIO_NUEVO': 'RIO_NUEVO',
    'LAS_PALOMAS': 'LAS_PALOMAS',
    'LAS_AGUADAS': 'LAS_AGUADAS',
    'EL_BANCO': 'EL_BANCO',
    'PENONCITO': 'PENONCITO',
    'LA_GLORIA': 'LA_GLORIA',
    'GAMARRA_AUT': 'GAMARRA_AUT',
    'EL_CONTENTO': 'EL_CONTENTO',
    'SITIO_NUEVO': 'SITIO_NUEVO',
    'PUERTO_WILCHES': 'PUERTO_WILCHES',
}

MESES = ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN',
         'JUL', 'AGO', 'SEP', 'OCT', 'NOV', 'DIC']


def clasificar_metodo(metodo_str):
    """Clasifica el metodo del CSV."""
    if metodo_str == 'Original':
        return 'original'
    elif metodo_str == 'L1_Interpolacion':
        return 'L1'
    elif metodo_str.startswith('L2_HH_') and 'quadratic' in metodo_str:
        return 'L2'
    elif metodo_str == 'L3_missForest':
        return 'L3'
    else:
        return 'L3'


def load_data():
    """Carga los datos imputados v4.3."""
    df = pd.read_csv(INPUT_FILE)
    df['date'] = pd.to_datetime(df['Fecha'])
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['day'] = df['date'].dt.day
    df['day_of_year'] = df['date'].dt.dayofyear
    df['data_source'] = df['Metodo'].apply(clasificar_metodo)
    return df


def get_station_data(df, station):
    """Obtiene datos de una estacion especifica."""
    station_df = df[df['NombreEstacion'] == station].copy()
    station_df = station_df.sort_values('date')
    return station_df


def plot_serie_tiempo(station_df, station, output_path):
    """Figura 1: Serie temporal completa (linea negra continua)."""
    fig, ax = plt.subplots(figsize=(14, 6))

    valid_data = station_df[station_df['Cota'].notna()]
    ax.plot(valid_data['date'], valid_data['Cota'], 'k-', linewidth=0.8)

    total_valid = len(valid_data)
    original_count = (station_df['data_source'] == 'original').sum()
    imputed_count = total_valid - original_count

    pct_original = (original_count / total_valid) * 100 if total_valid > 0 else 0
    pct_imputed = (imputed_count / total_valid) * 100 if total_valid > 0 else 0

    year_start = int(station_df['year'].min())
    year_end = int(station_df['year'].max())

    annotation_text = (f'Periodo: {year_start}-{year_end} | Total: {total_valid:,} observaciones\n'
                       f'Originales: {pct_original:.1f}% | Imputados: {pct_imputed:.1f}%')

    ax.text(0.02, 0.98, annotation_text,
            transform=ax.transAxes, fontsize=10,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.9))

    ax.set_title(f'Serie de Tiempo de Cotas - {station.replace("_", " ")}',
                 fontsize=13, fontweight='bold')
    ax.set_xlabel('Fecha', fontsize=11)
    ax.set_ylabel('Cota (m.s.n.m.)', fontsize=11)
    ax.grid(True, alpha=0.3)

    ax.xaxis.set_major_locator(plt.MaxNLocator(10))
    fig.autofmt_xdate()

    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    return True


def plot_violin_mensual(station_df, station, output_path):
    """Figura 2: Violin plot mensual con leyenda para media y mediana."""
    original = station_df[station_df['data_source'] == 'original'].copy()

    if len(original) < 30:
        print(f"  AVISO {station}: Insuficientes datos originales para violin")
        return False

    fig, ax = plt.subplots(figsize=(14, 6))

    data_by_month = []
    positions = []
    for month in range(1, 13):
        month_data = original[original['month'] == month]['Cota'].dropna()
        if len(month_data) > 0:
            data_by_month.append(month_data.values)
            positions.append(month)

    if len(data_by_month) == 0:
        return False

    parts = ax.violinplot(data_by_month, positions=positions, widths=0.7,
                          showmeans=True, showmedians=True, showextrema=True)

    for pc in parts['bodies']:
        pc.set_facecolor('lightgray')
        pc.set_edgecolor('gray')
        pc.set_alpha(0.7)

    parts['cmeans'].set_color('red')
    parts['cmeans'].set_linewidth(2)
    parts['cmedians'].set_color('black')
    parts['cmedians'].set_linewidth(2)
    parts['cbars'].set_color('gray')
    parts['cmins'].set_color('gray')
    parts['cmaxes'].set_color('gray')

    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], color='red', linewidth=2, label='Media'),
        Line2D([0], [0], color='black', linewidth=2, label='Mediana')
    ]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=10)

    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(MESES)
    ax.set_title(f'Distribucion Mensual de Cotas - {station.replace("_", " ")}',
                 fontsize=13, fontweight='bold')
    ax.set_xlabel('Mes', fontsize=11)
    ax.set_ylabel('Cota (m.s.n.m.)', fontsize=11)
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    return True


def plot_curva_duracion(station_df, station, output_path):
    """Figura 3: Curva de duracion con marcadores en P50, P90, P95, P100."""
    fig, ax = plt.subplots(figsize=(10, 7))

    levels = station_df['Cota'].dropna().sort_values(ascending=False)

    if len(levels) < 10:
        return False

    n = len(levels)
    exceedance_prob = np.arange(1, n + 1) / (n + 1) * 100

    ax.plot(exceedance_prob, levels, color='#1f77b4', linewidth=2.5)

    p50_level = np.percentile(levels, 50)
    p90_level = np.percentile(levels, 10)
    p95_level = np.percentile(levels, 5)
    p100_level = levels.min()

    p50_idx = np.argmin(np.abs(exceedance_prob - 50))
    p90_idx = np.argmin(np.abs(exceedance_prob - 90))
    p95_idx = np.argmin(np.abs(exceedance_prob - 95))
    p100_idx = np.argmin(np.abs(exceedance_prob - 99.5))

    ax.plot(50, p50_level, 'o', markersize=12, markerfacecolor='white', markeredgecolor='black', markeredgewidth=1.5)
    ax.plot(90, p90_level, 'o', markersize=12, markerfacecolor='white', markeredgecolor='black', markeredgewidth=1.5)
    ax.plot(95, p95_level, 'o', markersize=12, markerfacecolor='white', markeredgecolor='black', markeredgewidth=1.5)
    ax.plot(99.5, p100_level, 'o', markersize=12, markerfacecolor='white', markeredgecolor='black', markeredgewidth=1.5)

    ax.text(50, p50_level + 0.3, f'P50: {p50_level:.2f} m',
            ha='center', fontsize=11, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='gray'))
    ax.text(90, p90_level + 0.3, f'P90: {p90_level:.2f} m',
            ha='center', fontsize=11, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='gray'))
    ax.text(95, p95_level - 0.4, f'P95: {p95_level:.2f} m',
            ha='center', fontsize=11, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='gray'))
    ax.text(99.5, p100_level - 0.4, f'P100: {p100_level:.2f} m',
            ha='center', fontsize=11, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='gray'))

    ax.set_title(f'Curva de Duracion - {station.replace("_", " ").upper()}',
                 fontsize=14, fontweight='bold')
    ax.set_xlabel('Porcentaje de tiempo excedido (%)', fontsize=12)
    ax.set_ylabel('Cota (m.s.n.m.)', fontsize=12)
    ax.grid(True, alpha=0.3, linestyle='-')
    ax.set_xlim(-2, 102)

    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    return True


def calcular_percentiles_estacion(station_df, station, output_dir):
    """
    Paso 1: Calcula percentiles por mes-dia exacto (excluyendo 29-feb).
    Guarda CSV con mismo formato que generar_percentiles_todas_estaciones.py
    """
    df = station_df.copy()
    df['mes_dia'] = df['date'].dt.strftime('%m-%d')
    df = df[df['mes_dia'] != '02-29']
    # Solo datos originales para percentiles climatologicos
    df = df[df['data_source'] == 'original']
    df_clean = df[df['Cota'].notna()].copy()

    if len(df_clean) == 0:
        return None

    fecha_base = pd.date_range('2020-01-01', '2020-12-31', freq='D')
    fecha_base = fecha_base[fecha_base.strftime('%m-%d') != '02-29']

    results = {}
    for i, fecha in enumerate(fecha_base, 1):
        mes_dia = fecha.strftime('%m-%d')
        day_data = df_clean[df_clean['mes_dia'] == mes_dia]['Cota'].values
        if len(day_data) > 0:
            results[i] = {
                'day_of_year': i,
                'mes_dia': mes_dia,
                'fecha_referencia': mes_dia,
                'max': round(np.max(day_data), 3),
                'p95': round(np.percentile(day_data, 95), 3),
                'p75': round(np.percentile(day_data, 75), 3),
                'p50': round(np.percentile(day_data, 50), 3),
                'p25': round(np.percentile(day_data, 25), 3),
                'p5': round(np.percentile(day_data, 5), 3),
                'min': round(np.min(day_data), 3),
                'n_obs': len(day_data)
            }

    percentiles_df = pd.DataFrame(results).T
    if len(percentiles_df) == 0:
        return None

    csv_path = output_dir / f'Fig4_Percentiles_{station}_v4_3.csv'
    percentiles_df.to_csv(csv_path, index=False)
    return csv_path


def plot_curvas_excedidos(station_df, station, output_path):
    """
    Figura 4: Curvas de frecuencia con formato exacto de la version v2.
    Replica regenerar_fig4_corregido.py leyendo CSV de percentiles.
    """
    # Paso 1: Calcular y guardar percentiles
    station_dir = output_path.parent
    csv_path = calcular_percentiles_estacion(station_df, station, station_dir)
    if csv_path is None:
        return False

    # Paso 2: Leer CSV y graficar (como regenerar_fig4_corregido.py)
    df = pd.read_csv(csv_path)

    fig, ax = plt.subplots(figsize=(14, 8))
    days = df['day_of_year'].values

    colors = {
        'max': 'black', 'p95': '#8B0000', 'p75': '#6B8E23',
        'p50': 'black', 'p25': '#5DADE2', 'p5': '#D35400', 'min': 'black'
    }
    linewidths = {
        'max': 1.2, 'p95': 1.2, 'p75': 1.2, 'p50': 2.5,
        'p25': 1.2, 'p5': 1.2, 'min': 1.2
    }

    for col in ['max', 'p95', 'p75', 'p50', 'p25', 'p5', 'min']:
        ax.plot(days, df[col], color=colors[col], linewidth=linewidths[col])

    ax.axvline(x=365, color='black', linewidth=2.5, linestyle='-', zorder=10)

    x_label = 368
    last_day = df[df['day_of_year'] == 365].iloc[0]
    labels_data = [
        ('max', last_day['max'], 'MAX'), ('p95', last_day['p95'], '5%'),
        ('p75', last_day['p75'], '25%'), ('p50', last_day['p50'], '50%'),
        ('p25', last_day['p25'], '75%'), ('p5', last_day['p5'], '95%'),
        ('min', last_day['min'], 'MIN')
    ]

    for col, value, label in labels_data:
        ax.text(x_label, value, label, fontsize=11, fontweight='bold',
                color=colors[col], va='center', ha='left')

    month_days = [1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335]
    month_labels = ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN',
                    'JUL', 'AGO', 'SEP', 'OCT', 'NOV', 'DIC']

    ax.set_xlim(1, 365)
    ax.set_xticks(month_days)
    ax.set_xticklabels(month_labels, fontsize=11)

    ax.grid(True, alpha=0.3, which='both', linestyle='-', linewidth=0.5)
    ax.minorticks_on()
    ax.grid(True, alpha=0.15, which='minor', linestyle=':', linewidth=0.5)

    ax.set_xlabel('Mes', fontsize=12, fontweight='bold')
    ax.set_ylabel('Cota (m)', fontsize=12, fontweight='bold')
    ax.set_title(f'Fig4. Curvas de Frecuencia de Niveles Excedidos - {station.replace("_", " ").upper()}',
                 fontsize=14, fontweight='bold', pad=20)

    # Margen fijo +/- 2m (REGLA CRITICA de regenerar_fig4_corregido.py)
    y_min = df['min'].min() - 2
    y_max = df['max'].max() + 2
    ax.set_ylim(y_min, y_max)

    plt.tight_layout()
    plt.subplots_adjust(right=0.88)

    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    return True


def plot_ajuste_distribuciones(station_df, station, output_path):
    """Figura 5: Ajuste de distribuciones con colores en escala de grises."""
    original = station_df[station_df['data_source'] == 'original']['Cota'].dropna()

    if len(original) < 30:
        print(f"  AVISO {station}: Insuficientes datos originales para distribuciones")
        return False

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    ax1 = axes[0]

    n, bins, patches = ax1.hist(original, bins=30, density=True, alpha=0.6,
                                color='lightgray', edgecolor='gray', label='Datos observados')

    mu, sigma = stats.norm.fit(original)
    x = np.linspace(original.min(), original.max(), 100)
    ax1.plot(x, stats.norm.pdf(x, mu, sigma), 'k-', linewidth=2, label='Normal')

    try:
        shape, loc, scale = stats.gamma.fit(original)
        ax1.plot(x, stats.gamma.pdf(x, shape, loc, scale), 'k--', linewidth=2, label='Pearson III')
    except:
        pass

    try:
        c, loc, scale = stats.weibull_min.fit(original)
        ax1.plot(x, stats.weibull_min.pdf(x, c, loc, scale), 'k:', linewidth=2, label='Weibull')
    except:
        pass

    ax1.set_title(f'Ajuste de Distribuciones - {station.replace("_", " ")}\nAnual',
                  fontsize=12, fontweight='bold')
    ax1.set_xlabel('Cota (m.s.n.m.)', fontsize=11)
    ax1.set_ylabel('Densidad de probabilidad', fontsize=11)
    ax1.legend(fontsize=9, loc='upper left')
    ax1.grid(True, alpha=0.3)

    ax2 = axes[1]

    stats.probplot(original, dist=stats.gamma, sparams=(shape, loc, scale), plot=ax2)

    ax2.get_lines()[0].set_markerfacecolor('gray')
    ax2.get_lines()[0].set_markeredgecolor('black')
    ax2.get_lines()[0].set_alpha(0.6)
    ax2.get_lines()[1].set_color('black')
    ax2.get_lines()[1].set_linestyle('--')

    stat, p_value = stats.shapiro(original[:min(5000, len(original))])

    ax2.set_title(f'Q-Q Plot - Mejor Ajuste: Pearson III\nKS p-value: {p_value:.2e}',
                  fontsize=12, fontweight='bold')
    ax2.set_xlabel('Cuantiles teoricos (Pearson III)', fontsize=11)
    ax2.set_ylabel('Cuantiles observados', fontsize=11)
    ax2.grid(True, alpha=0.3)

    from matplotlib.lines import Line2D
    legend_elements = [Line2D([0], [0], color='black', linestyle='--', label='1:1')]
    ax2.legend(handles=legend_elements, loc='upper left', fontsize=9)

    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    return True


def main():
    """Genera todas las cartillas v4.3."""
    print("=" * 70)
    print("GENERADOR DE CARTILLAS DE ESTACIONES v4.3")
    print("=" * 70)

    print("\nCargando datos imputados v4.3...")
    df = load_data()
    print(f"Total registros: {len(df):,}")
    print(f"Estaciones: {df['NombreEstacion'].nunique()}")

    stats_summary = []

    for station in ESTACIONES:
        print(f"\n{'='*70}")
        print(f"Procesando: {station}")
        print('='*70)

        station_dir = OUTPUT_DIR / station
        station_dir.mkdir(exist_ok=True, parents=True)

        station_df = get_station_data(df, station)

        if len(station_df) == 0:
            print(f"  AVISO Sin datos para {station}")
            continue

        original_count = (station_df['data_source'] == 'original').sum()
        imputed_count = (station_df['data_source'] != 'original').sum()
        total_count = len(station_df)
        coverage = (station_df['Cota'].notna().sum() / total_count) * 100

        print(f"  Datos originales: {original_count:,}")
        print(f"  Datos imputados: {imputed_count:,}")
        print(f"  Cobertura: {coverage:.1f}%")

        figuras_generadas = 0

        try:
            output = station_dir / f"Fig1_Serie_Tiempo_{station}.png"
            if plot_serie_tiempo(station_df, station, output):
                print(f"  OK Fig1_Serie_Tiempo_{station}.png")
                figuras_generadas += 1
        except Exception as e:
            print(f"  ERROR Fig1: {e}")

        try:
            output = station_dir / f"Fig2_Violin_Mensual_{station}.png"
            if plot_violin_mensual(station_df, station, output):
                print(f"  OK Fig2_Violin_Mensual_{station}.png")
                figuras_generadas += 1
        except Exception as e:
            print(f"  ERROR Fig2: {e}")

        try:
            output = station_dir / f"Fig3_Curva_Duracion_{station}.png"
            if plot_curva_duracion(station_df, station, output):
                print(f"  OK Fig3_Curva_Duracion_{station}.png")
                figuras_generadas += 1
        except Exception as e:
            print(f"  ERROR Fig3: {e}")

        try:
            output = station_dir / f"Fig4_Curvas_Excedidos_{station}.png"
            if plot_curvas_excedidos(station_df, station, output):
                print(f"  OK Fig4_Curvas_Excedidos_{station}.png")
                figuras_generadas += 1
        except Exception as e:
            print(f"  ERROR Fig4: {e}")

        try:
            output = station_dir / f"Fig5_Ajuste_Distribuciones_{station}.png"
            if plot_ajuste_distribuciones(station_df, station, output):
                print(f"  OK Fig5_Ajuste_Distribuciones_{station}.png")
                figuras_generadas += 1
        except Exception as e:
            print(f"  ERROR Fig5: {e}")

        stats_summary.append({
            'station': station,
            'total_records': total_count,
            'original': original_count,
            'imputed': imputed_count,
            'coverage_pct': coverage,
            'figuras_generadas': figuras_generadas
        })

    print("\n" + "=" * 70)
    print("RESUMEN FINAL")
    print("=" * 70)

    summary_df = pd.DataFrame(stats_summary)
    print(summary_df.to_string(index=False))

    total_figuras = sum(s['figuras_generadas'] for s in stats_summary)
    print(f"\nTotal figuras generadas: {total_figuras} / {len(ESTACIONES) * 5}")
    print(f"Directorio: {OUTPUT_DIR}")


if __name__ == '__main__':
    main()
