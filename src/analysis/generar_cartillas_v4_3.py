"""
Generador de Cartillas v4.3 - Rio Magdalena
Genera 5 figuras por estacion usando datos imputados v4.3

Diferenciacion visual en Fig1 para verificar artefactos:
  - Original (L0): azul oscuro
  - Interpolacion (L1): naranja
  - H-H Cuadratico (L2): verde
  - missForest (L3): rojo

Uso: Probar primero con CALAMAR y EL_BANCO, luego todas.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from scipy import stats
from scipy.stats import norm, lognorm, gamma, gumbel_r, weibull_min, pearson3
import warnings
warnings.filterwarnings('ignore')

# Configuracion de estilo
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['axes.grid'] = True

# Colores por nivel de imputacion (para verificacion visual de artefactos)
COLOR_L0 = '#1565C0'      # Azul oscuro - Original
COLOR_L1 = '#FF9800'      # Naranja - Interpolacion
COLOR_L2 = '#4CAF50'      # Verde - H-H Cuadratico
COLOR_L3 = '#F44336'      # Rojo - missForest
COLOR_MEDIA = '#212121'   # Negro

def clasificar_metodo(metodo_str):
    """Clasifica el metodo del CSV en L0-L3."""
    if metodo_str == 'Original':
        return 'L0'
    elif metodo_str == 'L1_Interpolacion':
        return 'L1'
    elif metodo_str.startswith('L2_HH_') and 'quadratic' in metodo_str:
        return 'L2'
    elif metodo_str == 'L3_missForest':
        return 'L3'
    else:
        return 'L3'

NIVEL_COLOR = {
    'L0': COLOR_L0,
    'L1': COLOR_L1,
    'L2': COLOR_L2,
    'L3': COLOR_L3,
}

NIVEL_LABEL = {
    'L0': 'L0 - Original',
    'L1': 'L1 - Interpolacion',
    'L2': 'L2 - H-H Cuadratico',
    'L3': 'L3 - missForest',
}

# Distribuciones a probar
DISTRIBUTIONS = {
    'Weibull': weibull_min,
    'Log-Normal': lognorm,
    'Gamma': gamma,
    'Gumbel': gumbel_r,
    'Pearson III': pearson3,
    'Normal': norm
}


def load_imputed_data():
    """Carga datos imputados v4.3."""
    data_path = Path(r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\backend\data\processed\imputation')
    df = pd.read_csv(data_path / 'Datos_Imputados_v4_3_Corrected.csv')
    df['date'] = pd.to_datetime(df['Fecha'])
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['day'] = df['date'].dt.day
    return df


def setup_output_dirs(station):
    """Crea directorios de salida para la estacion en cartillas_estaciones/v4_3/."""
    base_dir = Path(r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\cartillas_estaciones\v4_3')
    station_dir = base_dir / station
    station_dir.mkdir(parents=True, exist_ok=True)
    return station_dir


def fig1_serie_tiempo(df_station, station, output_dir):
    """
    Figura 1: Serie de tiempo de niveles con diferenciacion por metodo de imputacion.
    Dibuja originales como linea continua e imputados como puntos (scatter) para 
    verificacion visual de artefactos.
    """
    fig, ax = plt.subplots(figsize=(16, 7))
    
    # Clasificar metodos
    df_station = df_station.copy()
    df_station['nivel_imp'] = df_station['Metodo'].apply(clasificar_metodo)
    df_station = df_station.sort_values('date')
    
    # 1. Dibujar originales (L0) como linea continua en el fondo
    df_l0 = df_station[df_station['nivel_imp'] == 'L0'].dropna(subset=['Cota'])
    if len(df_l0) > 0:
        ax.plot(df_l0['date'], df_l0['Cota'], 
                color=NIVEL_COLOR['L0'], linewidth=0.5, alpha=0.75,
                label=f"{NIVEL_LABEL['L0']} ({len(df_l0):,})")
    
    # 2. Dibujar imputados como puntos encima (mas visibles)
    for nivel in ['L1', 'L2', 'L3']:
        df_imp = df_station[df_station['nivel_imp'] == nivel].dropna(subset=['Cota'])
        if len(df_imp) > 0:
            ax.scatter(df_imp['date'], df_imp['Cota'],
                      color=NIVEL_COLOR[nivel], s=8, alpha=0.9, zorder=5,
                      label=f"{NIVEL_LABEL[nivel]} ({len(df_imp):,})")
    
    ax.set_xlabel('Fecha', fontsize=12)
    ax.set_ylabel('Cota (m.s.n.m.)', fontsize=12)
    ax.set_title(f'Serie de Tiempo de Cotas - {station.replace("_", " ")}\nDatos Imputados v4.3 (puntos = imputados)',
                 fontsize=13, fontweight='bold')
    
    # Grid principal y secundario
    ax.grid(True, which='major', alpha=0.4, linestyle='-')
    ax.grid(True, which='minor', alpha=0.2, linestyle=':')
    ax.minorticks_on()
    
    # Leyenda
    ax.legend(loc='upper left', fontsize=8, ncol=2, 
              framealpha=0.95, edgecolor='gray')
    
    # Estadisticas
    n_total = len(df_station)
    n_validos = len(df_station.dropna(subset=['Cota']))
    pct_l0 = (df_station['Nivel_Imputacion'] == 0).sum() / n_total * 100
    
    stats_text = (f'Periodo: {df_station["year"].min():.0f}-{df_station["year"].max():.0f} | '
                  f'Total: {n_validos:,} obs | L0: {pct_l0:.1f}%')
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=9,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(output_dir / f'Fig1_Serie_Tiempo_{station}.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Conteo por nivel
    counts = df_station['nivel_imp'].value_counts().to_dict()
    return f"Serie temporal {df_station['year'].min():.0f}-{df_station['year'].max():.0f} | {counts}"


def fig2_violinplot_mensual(df_station, station, output_dir):
    """Figura 2: Comportamiento mensual multianual (violinplots)."""
    fig, ax = plt.subplots(figsize=(14, 7))
    
    df_clean = df_station.dropna(subset=['Cota', 'month'])
    
    months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 
              'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
    
    violin_parts = ax.violinplot([df_clean[df_clean['month'] == m]['Cota'].values 
                                   for m in range(1, 13)],
                                  positions=range(1, 13),
                                  showmeans=False, showmedians=False, showextrema=False)
    
    for pc in violin_parts['bodies']:
        pc.set_facecolor('#E0E0E0')
        pc.set_edgecolor('black')
        pc.set_alpha(0.7)
    
    bp = ax.boxplot([df_clean[df_clean['month'] == m]['Cota'].values 
                     for m in range(1, 13)],
                    positions=range(1, 13), widths=0.15,
                    patch_artist=True, showfliers=False,
                    medianprops=dict(color='black', linewidth=2),
                    boxprops=dict(facecolor='black', alpha=0.3),
                    whiskerprops=dict(color='black'),
                    capprops=dict(color='black'))
    
    monthly_means = df_clean.groupby('month')['Cota'].mean()
    ax.plot(range(1, 13), monthly_means, 'k--', linewidth=2, 
            label='Media mensual multianual', marker='o', markersize=4)
    
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(months)
    ax.set_xlabel('Mes', fontsize=12)
    ax.set_ylabel('Cota (m.s.n.m.)', fontsize=12)
    ax.set_title(f'Distribucion Mensual Multianual de Cotas - {station.replace("_", " ")}\n(v4.3)',
                 fontsize=13, fontweight='bold')
    ax.legend(loc='best', fontsize=10)
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig(output_dir / f'Fig2_Violin_Mensual_{station}.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    return "Distribucion mensual multianual con violinplots, boxplot interno y media."


def fig3_curva_duracion(df_station, station, output_dir):
    """Figura 3: Curva de duracion."""
    fig, ax = plt.subplots(figsize=(10, 7))
    
    levels = df_station['Cota'].dropna().sort_values(ascending=False).values
    n = len(levels)
    
    percentiles = np.arange(1, n + 1) / n * 100
    
    ax.plot(percentiles, levels, color='#1976D2', linewidth=2)
    
    ax.set_xlabel('Porcentaje de tiempo excedido (%)', fontsize=12)
    ax.set_ylabel('Cota (m.s.n.m.)', fontsize=12)
    ax.set_title(f'Curva de Duracion de Cotas - {station.replace("_", " ")}\n(v4.3)',
                 fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    p50_idx = np.argmin(np.abs(percentiles - 50))
    p95_idx = np.argmin(np.abs(percentiles - 95))
    
    stats_text = f'Nivel medio (P50): {levels[p50_idx]:.2f} m\nNivel Q95: {levels[p95_idx]:.2f} m'
    ax.text(0.98, 0.98, stats_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(output_dir / f'Fig3_Curva_Duracion_{station}.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    return f"Curva de duracion: {len(levels):,} obs. P50={levels[p50_idx]:.2f} m."


def fig4_curvas_excedidos(df_station, station, output_dir):
    """Figura 4: Curvas de niveles excedidos (hidrograma de percentiles)."""
    fig, ax = plt.subplots(figsize=(14, 7))
    
    df_clean = df_station.dropna(subset=['Cota', 'month', 'day'])
    df_clean = df_clean[~((df_clean['month'] == 2) & (df_clean['day'] == 29))]
    
    month_days = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    cum_days = np.cumsum(month_days)
    
    df_clean = df_clean.copy()
    df_clean['day_of_year'] = df_clean.apply(
        lambda row: cum_days[int(row['month']) - 1] + int(row['day']), axis=1
    )
    
    days = range(1, 366)
    p_max = []
    p_min = []
    p_median = []
    
    for d in days:
        day_data = df_clean[df_clean['day_of_year'] == d]['Cota']
        if len(day_data) > 0:
            p_max.append(day_data.max())
            p_min.append(day_data.min())
            p_median.append(day_data.median())
        else:
            p_max.append(np.nan)
            p_min.append(np.nan)
            p_median.append(np.nan)
    
    ax.plot(days, p_max, color='gray', linestyle='-', linewidth=1.5, label='Maximo', alpha=0.8)
    ax.plot(days, p_min, color='gray', linestyle='-', linewidth=1.5, label='Minimo', alpha=0.8)
    ax.plot(days, p_median, color='gray', linestyle='--', linewidth=1.5, label='Mediana (P50)')
    
    year_data = df_clean[df_clean['year'] == 2025]
    if len(year_data) > 0:
        year_sorted = year_data.sort_values('day_of_year')
        ax.plot(year_sorted['day_of_year'], year_sorted['Cota'], 
               color='#0D47A1', linewidth=2, label='2025', alpha=0.9)
    
    month_labels = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 
                    'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
    month_positions = [15, 45, 75, 105, 135, 165, 195, 225, 255, 285, 315, 345]
    
    ax.set_xticks(month_positions)
    ax.set_xticklabels(month_labels)
    ax.set_xlabel('Tiempo', fontsize=12)
    ax.set_ylabel('Cota (m.s.n.m.)', fontsize=12)
    ax.set_title(f'Curvas de Frecuencias de Cotas Excedidas - {station.replace("_", " ")}\n(v4.3)',
                 fontsize=13, fontweight='bold')
    ax.legend(loc='best', fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(1, 365)
    
    plt.tight_layout()
    plt.savefig(output_dir / f'Fig4_Curvas_Excedidos_{station}.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    return "Hidrograma de percentiles: Max, Min, Mediana, 2025."


def fig5_ajuste_distribuciones(df_station, station, output_dir):
    """Figura 5: Ajuste de distribuciones PDF."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    data = df_station['Cota'].dropna().values
    
    if len(data) < 30:
        print(f"  Advertencia: {station} tiene pocos datos para ajuste")
        return "Datos insuficientes."
    
    results = {}
    for name, dist in DISTRIBUTIONS.items():
        try:
            params = dist.fit(data)
            log_likelihood = np.sum(np.log(dist.pdf(data, *params)))
            n = len(data)
            k = len(params)
            aic = 2 * k - 2 * log_likelihood
            ks_stat, ks_pvalue = stats.kstest(data, lambda x: dist.cdf(x, *params))
            
            results[name] = {
                'params': params,
                'AIC': aic,
                'KS_pvalue': ks_pvalue,
                'dist': dist
            }
        except Exception as e:
            print(f"  Error ajustando {name}: {e}")
            continue
    
    if not results:
        return "No se pudieron ajustar distribuciones."
    
    top_3 = sorted(results.items(), key=lambda x: x[1]['AIC'])[:3]
    best_name, best_result = top_3[0]
    
    ax1 = axes[0]
    ax1.hist(data, bins=50, density=True, alpha=0.5, color='#BDBDBD', 
             edgecolor='black', label='Datos observados')
    
    x = np.linspace(data.min(), data.max(), 500)
    colors = ['black', '#424242', '#757575']
    linestyles = ['-', '--', '-.']
    
    for idx, (name, result) in enumerate(top_3):
        pdf = result['dist'].pdf(x, *result['params'])
        label = f"{name} (AIC={result['AIC']:.1e})"
        ax1.plot(x, pdf, linewidth=2, color=colors[idx], 
                linestyle=linestyles[idx], label=label)
    
    ax1.set_xlabel('Cota (m.s.n.m.)', fontsize=11)
    ax1.set_ylabel('Densidad de probabilidad', fontsize=11)
    ax1.set_title(f'Ajuste de Distribuciones - {station.replace("_", " ")}\nAnual (v4.3)',
                 fontsize=12, fontweight='bold')
    ax1.legend(loc='best', fontsize=9)
    ax1.grid(True, alpha=0.3)
    
    ax2 = axes[1]
    sorted_data = np.sort(data)
    n = len(sorted_data)
    p = np.arange(1, n + 1) / (n + 1)
    
    theoretical_quantiles = best_result['dist'].ppf(p, *best_result['params'])
    
    ax2.scatter(theoretical_quantiles, sorted_data, alpha=0.5, s=10, color='black')
    
    min_val = min(theoretical_quantiles.min(), sorted_data.min())
    max_val = max(theoretical_quantiles.max(), sorted_data.max())
    ax2.plot([min_val, max_val], [min_val, max_val], 'k--', linewidth=1.5, label='1:1')
    
    ax2.set_xlabel(f'Cuantiles teoricos ({best_name})', fontsize=11)
    ax2.set_ylabel('Cuantiles observados', fontsize=11)
    ax2.set_title(f'Q-Q Plot - Mejor Ajuste: {best_name}\nKS p-value: {best_result["KS_pvalue"]:.2e}',
                 fontsize=12, fontweight='bold')
    ax2.legend(loc='best', fontsize=9)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / f'Fig5_Ajuste_Distribuciones_{station}.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    params_str = ', '.join([f'{p:.4f}' for p in best_result['params']])
    return f"Mejor ajuste: {best_name} (AIC={best_result['AIC']:.2f}). Params: [{params_str}]"


def generate_all_figures(stations):
    """Genera todas las figuras para las estaciones especificadas."""
    print("=" * 70)
    print("GENERADOR DE CARTILLAS v4.3 - Rio Magdalena")
    print("Datos: Datos_Imputados_v4_3_Corrected.csv")
    print("=" * 70)
    
    print("\n[1/3] Cargando datos imputados v4.3...")
    df = load_imputed_data()
    print(f"  Datos cargados: {len(df):,} registros")
    print(f"  Estaciones: {len(df['NombreEstacion'].unique())}")
    print(f"  Periodo: {df['year'].min():.0f}-{df['year'].max():.0f}")
    
    descriptions = {}
    
    for station in stations:
        print(f"\n{'-' * 60}")
        print(f"Procesando: {station}")
        print(f"{'-' * 60}")
        
        df_station = df[df['NombreEstacion'] == station].copy()
        
        if len(df_station) == 0:
            print(f"  ERROR: No se encontraron datos para {station}")
            continue
        
        print(f"  Registros: {len(df_station):,}")
        print(f"  Periodo: {df_station['year'].min():.0f}-{df_station['year'].max():.0f}")
        print(f"  L0 (Original): {(df_station['Nivel_Imputacion'] == 0).sum():,}")
        print(f"  L1 (Interpolacion): {(df_station['Nivel_Imputacion'] == 1).sum():,}")
        print(f"  L2 (H-H): {(df_station['Nivel_Imputacion'] == 2).sum():,}")
        print(f"  L3 (missForest): {(df_station['Nivel_Imputacion'] == 3).sum():,}")
        
        output_dir = setup_output_dirs(station)
        print(f"  Directorio: {output_dir}")
        
        desc = {}
        
        print("  Generando Figura 1: Serie de tiempo (con diferenciacion de metodos)...")
        desc['fig1'] = fig1_serie_tiempo(df_station, station, output_dir)
        
        print("  Generando Figura 2: Violinplot mensual...")
        desc['fig2'] = fig2_violinplot_mensual(df_station, station, output_dir)
        
        print("  Generando Figura 3: Curva de duracion...")
        desc['fig3'] = fig3_curva_duracion(df_station, station, output_dir)
        
        print("  Generando Figura 4: Curvas de excedidos...")
        desc['fig4'] = fig4_curvas_excedidos(df_station, station, output_dir)
        
        print("  Generando Figura 5: Ajuste de distribuciones...")
        desc['fig5'] = fig5_ajuste_distribuciones(df_station, station, output_dir)
        
        descriptions[station] = desc
        
        print(f"  [OK] Completado: 5 figuras generadas")
    
    print("\n" + "=" * 70)
    print("RESUMEN")
    print("=" * 70)
    
    for station, desc in descriptions.items():
        print(f"\n{station}:")
        for fig_name, description in desc.items():
            print(f"  {fig_name}: {description}")
    
    return descriptions


def main():
    """Funcion principal - genera cartillas v4.3 para estaciones de prueba."""
    # Estaciones de prueba (esperar aprobacion para todas)
    stations_test = ['CALAMAR', 'EL_BANCO']
    
    descriptions = generate_all_figures(stations_test)
    
    print("\n" + "=" * 70)
    print("PROCESO COMPLETADO - ESTACIONES DE PRUEBA")
    print("=" * 70)
    print(f"\nFiguras guardadas en: cartillas_estaciones/v4_3/[ESTACION]/")
    print("Revise Fig1 para verificar artefactos visuales en imputados.")
    
    return descriptions


if __name__ == '__main__':
    descriptions = main()
