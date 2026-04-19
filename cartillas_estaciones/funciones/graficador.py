"""
Funciones para generar cartillas de estaciones - Rio Magdalena
Este archivo contiene el codigo de las graficas. NO MODIFICAR.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.stats import norm, lognorm, gamma, gumbel_r, weibull_min, pearson3
import warnings
warnings.filterwarnings('ignore')

# Configuracion de estilo
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['axes.grid'] = True


def cargar_datos_estacion(nombre_archivo, data_path='./datos/processed/'):
    """Carga los datos de una estacion especifica."""
    # Cargar datos procesados
    df = pd.read_csv(f'{data_path}Datos_Imputados_v3.csv')
    df['date'] = pd.to_datetime(df['date'])
    
    # Filtrar estacion
    df_estacion = df[df['station'] == nombre_archivo].copy()
    
    if len(df_estacion) == 0:
        raise ValueError(f"Estacion '{nombre_archivo}' no encontrada en los datos.")
    
    return df_estacion


def fig1_serie_tiempo(df_estacion, station, output_dir='../resultados/'):
    """Figura 1: Serie de tiempo de cotas."""
    fig, ax = plt.subplots(figsize=(14, 6))
    
    # Plotear todos los datos en negro
    df_plot = df_estacion.dropna(subset=['level'])
    ax.plot(df_plot['date'], df_plot['level'], color='black', 
            linewidth=0.6, alpha=0.9)
    
    ax.set_xlabel('Fecha', fontsize=12)
    ax.set_ylabel('Cota (m.s.n.m.)', fontsize=12)
    ax.set_title(f'Serie de Tiempo de Cotas - {station}', 
                 fontsize=13, fontweight='bold')
    
    # Grid principal y secundario
    ax.grid(True, which='major', alpha=0.4, linestyle='-')
    ax.grid(True, which='minor', alpha=0.2, linestyle=':')
    ax.minorticks_on()
    
    # Estadisticas
    n_total = len(df_estacion)
    n_validos = len(df_plot)
    primer_ano = df_estacion['year'].min()
    ultimo_ano = df_estacion['year'].max()
    
    stats_text = f'Periodo: {primer_ano:.0f}-{ultimo_ano:.0f} | Total: {n_validos:,} observaciones'
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=9,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}Fig1_Serie_Tiempo_{station}.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"  [OK] Figura 1: Serie de tiempo ({n_validos:,} observaciones)")


def fig2_violinplot_mensual(df_estacion, station, output_dir='../resultados/'):
    """Figura 2: Comportamiento mensual multianual."""
    fig, ax = plt.subplots(figsize=(14, 7))
    
    df_clean = df_estacion.dropna(subset=['level', 'month'])
    
    months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 
              'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
    
    # Violinplot
    violin_parts = ax.violinplot([df_clean[df_clean['month'] == m]['level'].values 
                                   for m in range(1, 13)],
                                  positions=range(1, 13),
                                  showmeans=False, showmedians=False, showextrema=False)
    
    for pc in violin_parts['bodies']:
        pc.set_facecolor('#E0E0E0')
        pc.set_edgecolor('black')
        pc.set_alpha(0.7)
    
    # Boxplot interno
    bp = ax.boxplot([df_clean[df_clean['month'] == m]['level'].values 
                     for m in range(1, 13)],
                    positions=range(1, 13), widths=0.15,
                    patch_artist=True, showfliers=False,
                    medianprops=dict(color='black', linewidth=2),
                    boxprops=dict(facecolor='black', alpha=0.3))
    
    # Linea de media
    monthly_means = df_clean.groupby('month')['level'].mean()
    ax.plot(range(1, 13), monthly_means, 'k--', linewidth=2, 
            label='Media mensual multianual', marker='o', markersize=4)
    
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(months)
    ax.set_xlabel('Mes', fontsize=12)
    ax.set_ylabel('Cota (m.s.n.m.)', fontsize=12)
    ax.set_title(f'Comportamiento Mensual Multianual - {station}',
                 fontsize=13, fontweight='bold')
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}Fig2_Comportamiento_Mensual_{station}.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"  ✓ Figura 2: Comportamiento mensual")


def fig3_curva_duracion(df_estacion, station, output_dir='../resultados/'):
    """Figura 3: Curva de duracion."""
    fig, ax = plt.subplots(figsize=(10, 7))
    
    levels = df_estacion['level'].dropna().sort_values(ascending=False).values
    n = len(levels)
    
    percentiles = np.arange(1, n + 1) / n * 100
    
    ax.plot(percentiles, levels, color='#1976D2', linewidth=2)
    
    ax.set_xlabel('Porcentaje de tiempo excedido (%)', fontsize=12)
    ax.set_ylabel('Cota (m.s.n.m.)', fontsize=12)
    ax.set_title(f'Curva de Duracion - {station}',
                 fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    # Estadisticas
    p50_idx = np.argmin(np.abs(percentiles - 50))
    
    stats_text = f'Nivel medio (P50): {levels[p50_idx]:.2f} m'
    ax.text(0.98, 0.98, stats_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}Fig3_Curva_Duracion_{station}.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"  ✓ Figura 3: Curva de duracion")


def fig4_curvas_excedidos(df_estacion, station, output_dir='../resultados/'):
    """Figura 4: Curvas de frecuencias de cotas excedidas."""
    fig, ax = plt.subplots(figsize=(14, 7))
    
    df_clean = df_estacion.dropna(subset=['level', 'month', 'day'])
    df_clean = df_clean[~((df_clean['month'] == 2) & (df_clean['day'] == 29))]
    
    # Crear dia del ano
    month_days = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    cum_days = np.cumsum(month_days)
    
    df_clean['day_of_year'] = df_clean.apply(
        lambda row: cum_days[int(row['month']) - 1] + int(row['day']), axis=1
    )
    
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
    
    # Plotear
    ax.plot(days, p_max, color='gray', linestyle='-', linewidth=1.5, label='Maximo', alpha=0.8)
    ax.plot(days, p_min, color='gray', linestyle='-', linewidth=1.5, label='Minimo', alpha=0.8)
    ax.plot(days, p_median, color='gray', linestyle='--', linewidth=1.5, label='Mediana (P50)')
    
    # Ano 2025
    year_data = df_clean[df_clean['year'] == 2025]
    if len(year_data) > 0:
        year_sorted = year_data.sort_values('day_of_year')
        ax.plot(year_sorted['day_of_year'], year_sorted['level'], 
               color='#0D47A1', linewidth=2, label='2025', alpha=0.9)
    
    month_labels = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 
                    'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
    month_positions = [15, 45, 75, 105, 135, 165, 195, 225, 255, 285, 315, 345]
    
    ax.set_xticks(month_positions)
    ax.set_xticklabels(month_labels)
    ax.set_xlabel('Tiempo', fontsize=12)
    ax.set_ylabel('Cota (m.s.n.m.)', fontsize=12)
    ax.set_title(f'Curvas de Frecuencias de Cotas Excedidas - {station}',
                 fontsize=13, fontweight='bold')
    ax.legend(loc='best', fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(1, 365)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}Fig4_Curvas_Excedidos_{station}.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"  ✓ Figura 4: Curvas de frecuencias")


def fig5_ajuste_distribuciones(df_estacion, station, output_dir='../resultados/'):
    """Figura 5: Ajuste de distribuciones."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    data = df_estacion['level'].dropna().values
    
    if len(data) < 30:
        print(f"  ⚠ Advertencia: Datos insuficientes para ajuste de distribuciones")
        return
    
    DISTRIBUTIONS = {
        'Weibull': weibull_min,
        'Log-Normal': lognorm,
        'Gamma': gamma,
        'Gumbel': gumbel_r,
        'Pearson III': pearson3,
        'Normal': norm
    }
    
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
        except:
            continue
    
    if not results:
        print(f"  ⚠ No se pudieron ajustar distribuciones")
        return
    
    # Top 3 por AIC
    top_3 = sorted(results.items(), key=lambda x: x[1]['AIC'])[:3]
    best_name, best_result = top_3[0]
    
    # Panel izquierdo
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
    ax1.set_title(f'Ajuste de Distribuciones - {station}',
                 fontsize=12, fontweight='bold')
    ax1.legend(loc='best', fontsize=9)
    ax1.grid(True, alpha=0.3)
    
    # Panel derecho: Q-Q plot
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
    ax2.set_title(f'Q-Q Plot - Mejor Ajuste: {best_name}',
                 fontsize=12, fontweight='bold')
    ax2.legend(loc='best', fontsize=9)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}Fig5_Distribucion_Probabilidad_{station}.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"  ✓ Figura 5: Distribucion de probabilidad (mejor ajuste: {best_name})")


def generar_cartilla_completa(nombre_estacion, data_path='./datos/processed/', 
                               output_dir='./resultados/'):
    """
    Genera las 5 figuras de la cartilla para una estacion.
    
    Parametros:
    -----------
    nombre_estacion : str
        Nombre de la estacion (ej: 'CALAMAR', 'BARBOSA')
    data_path : str
        Ruta a los datos procesados
    output_dir : str
        Ruta donde se guardaran las figuras
    """
    print(f"\n{'='*60}")
    print(f"GENERANDO CARTILLA PARA: {nombre_estacion}")
    print(f"{'='*60}\n")
    
    # Cargar datos
    print("1. Cargando datos...")
    try:
        df = cargar_datos_estacion(nombre_estacion, data_path)
        print(f"   ✓ {len(df):,} registros encontrados")
        print(f"   ✓ Periodo: {df['year'].min():.0f}-{df['year'].max():.0f}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return
    
    # Generar figuras
    print("\n2. Generando figuras...")
    try:
        fig1_serie_tiempo(df, nombre_estacion, output_dir)
        fig2_violinplot_mensual(df, nombre_estacion, output_dir)
        fig3_curva_duracion(df, nombre_estacion, output_dir)
        fig4_curvas_excedidos(df, nombre_estacion, output_dir)
        fig5_ajuste_distribuciones(df, nombre_estacion, output_dir)
    except Exception as e:
        print(f"   ✗ Error generando figuras: {e}")
        return
    
    print(f"\n{'='*60}")
    print(f"✓ CARTILLA COMPLETADA: {nombre_estacion}")
    print(f"{'='*60}")
    print(f"\nFiguras guardadas en: {output_dir}")
    print(f"  - Fig1_Serie_Tiempo_{nombre_estacion}.png")
    print(f"  - Fig2_Comportamiento_Mensual_{nombre_estacion}.png")
    print(f"  - Fig3_Curva_Duracion_{nombre_estacion}.png")
    print(f"  - Fig4_Curvas_Excedidos_{nombre_estacion}.png")
    print(f"  - Fig5_Distribucion_Probabilidad_{nombre_estacion}.png")
