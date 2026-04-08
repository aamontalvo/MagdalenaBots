"""
Generador de Figuras de Analisis por Estacion - Rio Magdalena
Genera 5 tipos de figuras para estaciones seleccionadas:
  1. Serie de tiempo de niveles
  2. Comportamiento mensual multianual (violinplots)
  3. Curva de duracion
  4. Curvas de niveles excedidos
  5. Ajuste de distribuciones PDF

Uso: Genera figuras para CALAMAR y BARBOSA (ejemplo)
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

# Colores estandar
COLOR_ORIGINAL = '#1565C0'      # Azul oscuro
COLOR_IMPUTED_L1 = '#FF9800'    # Naranja
COLOR_IMPUTED_HH = '#4CAF50'    # Verde
COLOR_MEDIA = '#212121'         # Negro
COLOR_BEST_FIT = '#000000'      # Negro para mejor ajuste

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
    """Carga datos imputados desde processed folder."""
    data_path = Path(r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\backend\data\processed\imputation')
    df = pd.read_csv(data_path / 'Datos_Imputados_v3.csv')
    df['date'] = pd.to_datetime(df['date'])
    return df


def setup_output_dirs(station):
    """Crea directorios de salida para la estacion."""
    base_dir = Path(r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\informes\estaciones')
    station_dir = base_dir / station
    station_dir.mkdir(parents=True, exist_ok=True)
    return station_dir


def fig1_serie_tiempo(df_station, station, output_dir):
    """
    Figura 1: Serie de tiempo de niveles.
    X: Fecha (anos), Y: Cota (m.s.n.m.)
    Linea unica en negro con secondary grid.
    """
    fig, ax = plt.subplots(figsize=(14, 6))
    
    # Plotear todos los datos en negro sin diferenciar fuente
    df_plot = df_station.dropna(subset=['level'])
    ax.plot(df_plot['date'], df_plot['level'], color='black', 
            linewidth=0.6, alpha=0.9)
    
    ax.set_xlabel('Fecha', fontsize=12)
    ax.set_ylabel('Cota (m.s.n.m.)', fontsize=12)
    ax.set_title(f'Serie de Tiempo de Cotas - {station.replace("_", " ")}', 
                 fontsize=13, fontweight='bold')
    
    # Grid principal y secundario
    ax.grid(True, which='major', alpha=0.4, linestyle='-')
    ax.grid(True, which='minor', alpha=0.2, linestyle=':')
    ax.minorticks_on()
    
    # Agregar estadisticas
    n_total = len(df_station)
    n_validos = len(df_plot)
    
    stats_text = f'Periodo: {df_station["year"].min():.0f}-{df_station["year"].max():.0f} | Total: {n_validos:,} observaciones'
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=9,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(output_dir / f'Fig1_Serie_Tiempo_{station}.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    return f"Serie temporal completa ({df_station['year'].min():.0f}-{df_station['year'].max():.0f}) con {n_validos:,} observaciones validas. Linea continua en negro con grid principal y secundario."


def fig2_violinplot_mensual(df_station, station, output_dir):
    """
    Figura 2: Comportamiento mensual multianual (violinplots).
    X: Meses, Y: Cota. Incluye boxplot interno y linea de media.
    """
    fig, ax = plt.subplots(figsize=(14, 7))
    
    # Preparar datos
    df_clean = df_station.dropna(subset=['level', 'month'])
    
    # Crear violinplot
    months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 
              'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
    
    violin_parts = ax.violinplot([df_clean[df_clean['month'] == m]['level'].values 
                                   for m in range(1, 13)],
                                  positions=range(1, 13),
                                  showmeans=False, showmedians=False, showextrema=False)
    
    # Colorear violines
    for pc in violin_parts['bodies']:
        pc.set_facecolor('#E0E0E0')
        pc.set_edgecolor('black')
        pc.set_alpha(0.7)
    
    # Agregar boxplot interno
    bp = ax.boxplot([df_clean[df_clean['month'] == m]['level'].values 
                     for m in range(1, 13)],
                    positions=range(1, 13), widths=0.15,
                    patch_artist=True, showfliers=False,
                    medianprops=dict(color='black', linewidth=2),
                    boxprops=dict(facecolor='black', alpha=0.3),
                    whiskerprops=dict(color='black'),
                    capprops=dict(color='black'))
    
    # Calcular y plotear media mensual multianual
    monthly_means = df_clean.groupby('month')['level'].mean()
    ax.plot(range(1, 13), monthly_means, 'k--', linewidth=2, 
            label='Media mensual multianual', marker='o', markersize=4)
    
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(months)
    ax.set_xlabel('Mes', fontsize=12)
    ax.set_ylabel('Cota (m.s.n.m.)', fontsize=12)
    ax.set_title(f'Distribucion Mensual Multianual de Cotas - {station.replace("_", " ")}\n(Violin plot con boxplot interno y media mensual multianual)',
                 fontsize=13, fontweight='bold')
    ax.legend(loc='best', fontsize=10)
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig(output_dir / f'Fig2_Violin_Mensual_{station}.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    return "Distribucion mensual multianual mostrando variabilidad estacional con violinplots, boxplot interno y linea de media."


def fig3_curva_duracion(df_station, station, output_dir):
    """
    Figura 3: Curva de duracion.
    X: Percentil (0-100), Y: Nivel ordenado descendente.
    """
    fig, ax = plt.subplots(figsize=(10, 7))
    
    # Obtener datos limpios y ordenar DESCENDENTE
    levels = df_station['level'].dropna().sort_values(ascending=False).values
    n = len(levels)
    
    # Calcular percentiles de excedencia
    percentiles = np.arange(1, n + 1) / n * 100
    
    # Plotear
    ax.plot(percentiles, levels, color='#1976D2', linewidth=2)
    
    ax.set_xlabel('Porcentaje de tiempo excedido (%)', fontsize=12)
    ax.set_ylabel('Cota (m.s.n.m.)', fontsize=12)
    ax.set_title(f'Curva de Duracion de Cotas - {station.replace("_", " ")}',
                 fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    # Agregar estadisticas clave
    p50_idx = np.argmin(np.abs(percentiles - 50))
    p95_idx = np.argmin(np.abs(percentiles - 95))
    
    stats_text = f'Nivel medio (P50): {levels[p50_idx]:.2f} m\nNivel Q95: {levels[p95_idx]:.2f} m'
    ax.text(0.98, 0.98, stats_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(output_dir / f'Fig3_Curva_Duracion_{station}.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    return f"Curva de duracion mostrando niveles excedidos {len(levels):,} observaciones. Nivel medio (P50): {levels[p50_idx]:.2f} m.s.n.m."


def fig4_curvas_excedidos(df_station, station, output_dir):
    """
    Figura 4: Curvas de niveles excedidos (hidrograma de percentiles).
    X: Dia del ano (1-365), Y: Nivel.
    Lineas: Max, Min, Mediana, 2025, 2026.
    Excluye anos bisiestos.
    """
    fig, ax = plt.subplots(figsize=(14, 7))
    
    # Filtrar datos validos y excluir bisiestos (dia 366)
    df_clean = df_station.dropna(subset=['level', 'month', 'day'])
    df_clean = df_clean[~((df_clean['month'] == 2) & (df_clean['day'] == 29))]
    
    # Crear dia del ano (1-365)
    month_days = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    cum_days = np.cumsum(month_days)
    
    df_clean['day_of_year'] = df_clean.apply(
        lambda row: cum_days[int(row['month']) - 1] + int(row['day']), axis=1
    )
    
    # Calcular percentiles por dia del ano
    days = range(1, 366)
    p_max = []
    p_min = []
    p_median = []
    
    for d in days:
        day_data = df_clean[df_clean['day_of_year'] == d]['level']
        if len(day_data) > 0:
            p_max.append(day_data.max())
            p_min.append(day_data.min())
            p_median.append(day_data.median())
        else:
            p_max.append(np.nan)
            p_min.append(np.nan)
            p_median.append(np.nan)
    
    # Plotear percentiles historicos - Max y Min en gris, P50 en gris punteado
    ax.plot(days, p_max, color='gray', linestyle='-', linewidth=1.5, label='Maximo', alpha=0.8)
    ax.plot(days, p_min, color='gray', linestyle='-', linewidth=1.5, label='Minimo', alpha=0.8)
    ax.plot(days, p_median, color='gray', linestyle='--', linewidth=1.5, label='Mediana (P50)')
    
    # Ano 2025 en azul (2026 no requerido para el informe actual)
    year_data = df_clean[df_clean['year'] == 2025]
    if len(year_data) > 0:
        year_sorted = year_data.sort_values('day_of_year')
        ax.plot(year_sorted['day_of_year'], year_sorted['level'], 
               color='#0D47A1', linewidth=2, label='2025', alpha=0.9)
    
    # Etiquetas de meses en eje X
    month_labels = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 
                    'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
    month_positions = [15, 45, 75, 105, 135, 165, 195, 225, 255, 285, 315, 345]
    
    ax.set_xticks(month_positions)
    ax.set_xticklabels(month_labels)
    ax.set_xlabel('Tiempo', fontsize=12)
    ax.set_ylabel('Cota (m.s.n.m.)', fontsize=12)
    ax.set_title(f'Curvas de Frecuencias de Cotas Excedidas - {station.replace("_", " ")}',
                 fontsize=13, fontweight='bold')
    ax.legend(loc='best', fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(1, 365)
    
    plt.tight_layout()
    plt.savefig(output_dir / f'Fig4_Curvas_Excedidos_{station}.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    return "Hidrograma de percentiles mostrando variabilidad anual con maximos, minimos, mediana y anos recientes 2025-2026."


def fig5_ajuste_distribuciones(df_station, station, output_dir):
    """
    Figura 5: Ajuste de distribuciones PDF.
    Panel izquierdo: Histograma + PDFs (top 3 por AIC).
    Panel derecho: Q-Q plot del mejor ajuste.
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Obtener datos limpios (solo originales + imputados validos)
    data = df_station['level'].dropna().values
    
    if len(data) < 30:
        print(f"  Advertencia: {station} tiene pocos datos para ajuste de distribuciones")
        return "Datos insuficientes para ajuste de distribuciones."
    
    # Ajustar distribuciones
    results = {}
    for name, dist in DISTRIBUTIONS.items():
        try:
            # Ajustar
            params = dist.fit(data)
            
            # Calcular log-likelihood
            log_likelihood = np.sum(np.log(dist.pdf(data, *params)))
            n = len(data)
            k = len(params)
            
            # AIC
            aic = 2 * k - 2 * log_likelihood
            
            # Prueba KS
            ks_stat, ks_pvalue = stats.kstest(data, lambda x: dist.cdf(x, *params))
            
            results[name] = {
                'params': params,
                'AIC': aic,
                'KS_pvalue': ks_pvalue,
                'dist': dist
            }
        except Exception as e:
            print(f"  Error ajustando {name} para {station}: {e}")
            continue
    
    if not results:
        return "No se pudieron ajustar distribuciones."
    
    # Seleccionar top 3 por AIC
    top_3 = sorted(results.items(), key=lambda x: x[1]['AIC'])[:3]
    best_name, best_result = top_3[0]
    
    # Panel izquierdo: Histograma + PDFs
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
    ax1.set_title(f'Ajuste de Distribuciones - {station.replace("_", " ")}\nAnual',
                 fontsize=12, fontweight='bold')
    ax1.legend(loc='best', fontsize=9)
    ax1.grid(True, alpha=0.3)
    
    # Panel derecho: Q-Q plot del mejor ajuste
    ax2 = axes[1]
    
    # Calcular quantiles teoricos vs observados
    sorted_data = np.sort(data)
    n = len(sorted_data)
    p = np.arange(1, n + 1) / (n + 1)
    
    # Quantiles teoricos de la mejor distribucion
    theoretical_quantiles = best_result['dist'].ppf(p, *best_result['params'])
    
    ax2.scatter(theoretical_quantiles, sorted_data, alpha=0.5, s=10, color='black')
    
    # Linea 1:1
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
    
    # Retornar informacion del mejor ajuste
    params_str = ', '.join([f'{p:.4f}' for p in best_result['params']])
    return f"Mejor ajuste: {best_name} (AIC={best_result['AIC']:.2f}, KS p={best_result['KS_pvalue']:.4f}). Parametros: [{params_str}]"


def generate_all_figures(stations):
    """
    Genera todas las figuras para las estaciones especificadas.
    
    Args:
        stations: Lista de nombres de estaciones
    """
    print("=" * 70)
    print("GENERADOR DE FIGURAS DE ANALISIS POR ESTACION")
    print("Rio Magdalena - Datos Imputados v3.0")
    print("=" * 70)
    
    # Cargar datos
    print("\n[1/3] Cargando datos imputados...")
    df = load_imputed_data()
    print(f"  Datos cargados: {len(df):,} registros")
    
    # Procesar cada estacion
    descriptions = {}
    
    for station in stations:
        print(f"\n[2/3] Procesando estacion: {station}")
        print("-" * 50)
        
        # Filtrar datos de la estacion
        df_station = df[df['station'] == station].copy()
        
        if len(df_station) == 0:
            print(f"  ERROR: No se encontraron datos para {station}")
            continue
        
        print(f"  Registros: {len(df_station):,}")
        print(f"  Periodo: {df_station['year'].min():.0f}-{df_station['year'].max():.0f}")
        
        # Crear directorio de salida
        output_dir = setup_output_dirs(station)
        print(f"  Directorio: {output_dir}")
        
        # Generar figuras
        desc = {}
        
        print("  Generando Figura 1: Serie de tiempo...")
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
    
    # Resumen final
    print("\n" + "=" * 70)
    print("RESUMEN DE FIGURAS GENERADAS")
    print("=" * 70)
    
    for station, desc in descriptions.items():
        print(f"\n{station}:")
        for fig_name, description in desc.items():
            print(f"  {fig_name}: {description}")
    
    return descriptions


def main():
    """Funcion principal."""
    # Estaciones a procesar (ejemplo: Calamar y Barbosa)
    stations = ['CALAMAR', 'BARBOSA']
    
    # Generar figuras
    descriptions = generate_all_figures(stations)
    
    print("\n" + "=" * 70)
    print("PROCESO COMPLETADO")
    print("=" * 70)
    print(f"\nFiguras guardadas en: informes/estaciones/[ESTACION]/")
    
    return descriptions


if __name__ == '__main__':
    descriptions = main()
