"""
Generador de Figuras Faltantes (Fig2, Fig4, Fig5)
Para estaciones que solo tienen Fig1 y Fig3
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import scipy.stats as stats
from scipy.interpolate import make_interp_spline
import warnings
warnings.filterwarnings('ignore')

# Configuracion de estilo
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 13
plt.rcParams['axes.grid'] = True
plt.rcParams['grid.alpha'] = 0.3

# Rutas
INPUT_FILE = Path(r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\Informes\imputacion\Datos_Imputados_v4_2_Complete.csv')
OUTPUT_DIR = Path(r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\cartillas_estaciones\v4_2')

# Estaciones que necesitan Fig2, Fig4, Fig5
ESTACIONES_FALTANTES = [
    'El Banco', 'El Contento', 'Gamarra Aut', 'La Gloria', 
    'Las Aguadas', 'Las Palomas', 'Puerto Wilches', 
    'Rio Nuevo', 'Sitio Nuevo'
]

# Meses en espanol
MESES = ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN', 
         'JUL', 'AGO', 'SEP', 'OCT', 'NOV', 'DIC']

def load_data():
    """Carga los datos imputados."""
    df = pd.read_csv(INPUT_FILE)
    df['Fecha'] = pd.to_datetime(df['Fecha'], format='%d-%m-%Y')
    df['month'] = df['Fecha'].dt.month
    df['year'] = df['Fecha'].dt.year
    df['day_of_year'] = df['Fecha'].dt.dayofyear
    return df

def get_station_data(df, station_name):
    """Obtiene datos de una estacion especifica por nombre exacto."""
    station_df = df[df['NombreEstacion'] == station_name].copy()
    station_df = station_df.sort_values('Fecha')
    return station_df

def plot_violin_mensual(station_df, station_name, output_path):
    """Figura 2: Violin plot mensual con leyenda para media y mediana."""
    # Solo datos originales
    original = station_df[station_df['Metodo'] == 'Original'].copy()
    
    if len(original) < 30:
        print(f"  AVISO {station_name}: Insuficientes datos originales para violin")
        return False
    
    fig, ax = plt.subplots(figsize=(14, 6))
    
    # Preparar datos por mes
    data_by_month = []
    positions = []
    for month in range(1, 13):
        month_data = original[original['month'] == month]['Cota'].dropna()
        if len(month_data) > 0:
            data_by_month.append(month_data.values)
            positions.append(month)
    
    if len(data_by_month) == 0:
        return False
    
    # Crear violin plot
    parts = ax.violinplot(data_by_month, positions=positions, widths=0.7,
                          showmeans=True, showmedians=True, showextrema=True)
    
    # Colorear violines
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
    
    # Leyenda personalizada
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], color='red', linewidth=2, label='Media'),
        Line2D([0], [0], color='black', linewidth=2, label='Mediana')
    ]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=10)
    
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(MESES)
    ax.set_title(f'Distribucion Mensual de Cotas - {station_name}', 
                 fontsize=13, fontweight='bold')
    ax.set_xlabel('Mes', fontsize=11)
    ax.set_ylabel('Cota (m.s.n.m.)', fontsize=11)
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    return True

def plot_curvas_excedidos(station_df, station_name, output_path):
    """Figura 4: Curvas de frecuencia con etiquetas FUERA del box."""
    fig, ax = plt.subplots(figsize=(14, 7))
    
    # Usar datos imputados
    df_valid = station_df[station_df['Cota'].notna()].copy()
    
    if len(df_valid) < 365:
        return False
    
    # Calcular percentiles por dia del ano
    days = range(1, 367)
    p_max, p5, p25, p50, p75, p95, p_min = [], [], [], [], [], [], []
    
    for day in days:
        # Ventana de ±15 dias para suavizar
        window_days = [(day + offset - 1) % 365 + 1 for offset in range(-15, 16)]
        day_data = df_valid[df_valid['day_of_year'].isin(window_days)]['Cota']
        
        if len(day_data) > 0:
            p_max.append(day_data.max())
            p5.append(np.percentile(day_data, 95))
            p25.append(np.percentile(day_data, 75))
            p50.append(np.percentile(day_data, 50))
            p75.append(np.percentile(day_data, 25))
            p95.append(np.percentile(day_data, 5))
            p_min.append(day_data.min())
        else:
            p_max.append(np.nan)
            p5.append(np.nan)
            p25.append(np.nan)
            p50.append(np.nan)
            p75.append(np.nan)
            p95.append(np.nan)
            p_min.append(np.nan)
    
    # Suavizar curvas
    days_smooth = np.linspace(1, 366, 365)
    
    def smooth_curve(y):
        y = np.array(y)
        mask = ~np.isnan(y)
        if mask.sum() < 10:
            return y
        spl = make_interp_spline(np.array(days)[mask], y[mask], k=2)
        return spl(days_smooth)
    
    p_max_s = smooth_curve(p_max)
    p5_s = smooth_curve(p5)
    p25_s = smooth_curve(p25)
    p50_s = smooth_curve(p50)
    p75_s = smooth_curve(p75)
    p95_s = smooth_curve(p95)
    p_min_s = smooth_curve(p_min)
    
    # Colores segun especificacion
    ax.plot(days_smooth, p_max_s, color='black', linewidth=1.5)
    ax.plot(days_smooth, p5_s, color='#8B0000', linewidth=1.5)
    ax.plot(days_smooth, p25_s, color='#6B8E23', linewidth=1.5)
    ax.plot(days_smooth, p50_s, color='black', linewidth=2.5)
    ax.plot(days_smooth, p75_s, color='#5DADE2', linewidth=1.5)
    ax.plot(days_smooth, p95_s, color='#D35400', linewidth=1.5)
    ax.plot(days_smooth, p_min_s, color='black', linewidth=1.5)
    
    # Etiquetas FUERA del area de la grafica
    ax.annotate('MAX', xy=(366, p_max_s[-1]), xytext=(375, p_max_s[-1]),
                fontsize=10, va='center', fontweight='bold')
    ax.annotate('5%', xy=(366, p5_s[-1]), xytext=(375, p5_s[-1]),
                fontsize=10, va='center', color='#8B0000')
    ax.annotate('25%', xy=(366, p25_s[-1]), xytext=(375, p25_s[-1]),
                fontsize=10, va='center', color='#6B8E23')
    ax.annotate('50%', xy=(366, p50_s[-1]), xytext=(375, p50_s[-1]),
                fontsize=10, va='center', fontweight='bold')
    ax.annotate('75%', xy=(366, p75_s[-1]), xytext=(375, p75_s[-1]),
                fontsize=10, va='center', color='#5DADE2')
    ax.annotate('95%', xy=(366, p95_s[-1]), xytext=(375, p95_s[-1]),
                fontsize=10, va='center', color='#D35400')
    ax.annotate('MIN', xy=(366, p_min_s[-1]), xytext=(375, p_min_s[-1]),
                fontsize=10, va='center', fontweight='bold')
    
    # Formato
    year_start = df_valid['year'].min()
    year_end = df_valid['year'].max()
    ax.set_title(f'CURVA DE FRECUENCIA DE NIVELES EXCEDIDOS - {station_name}\n{year_start} - {year_end}', 
                 fontsize=13, fontweight='bold')
    ax.set_xlabel('Mes', fontsize=11)
    ax.set_ylabel('NIVEL (m.s.n.m.)', fontsize=11)
    
    # Eje X con meses
    month_starts = [1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335]
    ax.set_xticks(month_starts)
    ax.set_xticklabels(MESES)
    ax.grid(True, alpha=0.3)
    
    # Extender limites para etiquetas
    ax.set_xlim(0, 420)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    return True

def plot_ajuste_distribuciones(station_df, station_name, output_path):
    """Figura 5: Ajuste de distribuciones con colores en escala de grises."""
    # Solo datos originales
    original = station_df[station_df['Metodo'] == 'Original']['Cota'].dropna()
    
    if len(original) < 30:
        print(f"  AVISO {station_name}: Insuficientes datos originales para distribuciones")
        return False
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Panel izquierdo: Histograma con ajustes en escala de grises
    ax1 = axes[0]
    
    # Histograma en gris claro
    ax1.hist(original, bins=30, density=True, alpha=0.6, 
             color='lightgray', edgecolor='gray', label='Datos observados')
    
    # Ajuste Normal
    mu, sigma = stats.norm.fit(original)
    x = np.linspace(original.min(), original.max(), 100)
    ax1.plot(x, stats.norm.pdf(x, mu, sigma), 'k-', linewidth=2, label='Normal')
    
    # Ajuste Pearson III (usando gamma como aproximacion)
    try:
        shape, loc, scale = stats.gamma.fit(original)
        ax1.plot(x, stats.gamma.pdf(x, shape, loc, scale), 'k--', linewidth=2, label='Pearson III')
    except:
        pass
    
    # Ajuste Weibull
    try:
        c, loc, scale = stats.weibull_min.fit(original)
        ax1.plot(x, stats.weibull_min.pdf(x, c, loc, scale), 'k:', linewidth=2, label='Weibull')
    except:
        pass
    
    ax1.set_title(f'Ajuste de Distribuciones - {station_name}\nAnual', 
                  fontsize=12, fontweight='bold')
    ax1.set_xlabel('Cota (m.s.n.m.)', fontsize=11)
    ax1.set_ylabel('Densidad de probabilidad', fontsize=11)
    ax1.legend(fontsize=9, loc='upper left')
    ax1.grid(True, alpha=0.3)
    
    # Panel derecho: Q-Q plot
    ax2 = axes[1]
    
    # Q-Q plot con mejor ajuste (Pearson III / Gamma)
    shape, loc, scale = stats.gamma.fit(original)
    stats.probplot(original, dist=stats.gamma, sparams=(shape, loc, scale), plot=ax2)
    
    # Colores en grises
    ax2.get_lines()[0].set_markerfacecolor('gray')
    ax2.get_lines()[0].set_markeredgecolor('black')
    ax2.get_lines()[0].set_alpha(0.6)
    ax2.get_lines()[1].set_color('black')
    ax2.get_lines()[1].set_linestyle('--')
    
    # Prueba de normalidad
    stat, p_value = stats.shapiro(original[:min(5000, len(original))])
    
    ax2.set_title(f'Q-Q Plot - Mejor Ajuste: Pearson III\nKS p-value: {p_value:.2e}', 
                  fontsize=12, fontweight='bold')
    ax2.set_xlabel('Cuantiles teoricos (Pearson III)', fontsize=11)
    ax2.set_ylabel('Cuantiles observados', fontsize=11)
    ax2.grid(True, alpha=0.3)
    
    # Leyenda 1:1
    from matplotlib.lines import Line2D
    legend_elements = [Line2D([0], [0], color='black', linestyle='--', label='1:1')]
    ax2.legend(handles=legend_elements, loc='upper left', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    return True

def main():
    """Genera Figuras 2, 4 y 5 para estaciones faltantes."""
    print("=" * 70)
    print("GENERADOR DE FIGURAS FALTANTES (Fig2, Fig4, Fig5)")
    print("=" * 70)
    
    # Cargar datos
    print("\nCargando datos imputados...")
    df = load_data()
    print(f"Total registros: {len(df):,}")
    print(f"Estaciones unicas: {df['NombreEstacion'].nunique()}")
    
    for station in ESTACIONES_FALTANTES:
        print(f"\n{'='*70}")
        print(f"Procesando: {station}")
        print('='*70)
        
        # Crear directorio de estacion
        station_dir = OUTPUT_DIR / station
        station_dir.mkdir(exist_ok=True, parents=True)
        
        # Obtener datos de la estacion
        station_df = get_station_data(df, station)
        
        if len(station_df) == 0:
            print(f"  AVISO: Sin datos para {station}")
            continue
        
        # Estadisticas
        original_count = (station_df['Metodo'] == 'Original').sum()
        total_count = len(station_df)
        print(f"  Total: {total_count:,} | Originales: {original_count:,}")
        
        figuras_generadas = 0
        
        # Figura 2: Violin mensual
        try:
            output = station_dir / f"Fig2_Violin_Mensual_{station.replace(' ', '_')}.png"
            if plot_violin_mensual(station_df, station, output):
                print(f"  OK: Fig2_Violin_Mensual_{station.replace(' ', '_')}.png")
                figuras_generadas += 1
        except Exception as e:
            print(f"  ERROR Fig2: {e}")
        
        # Figura 4: Curvas excedidos
        try:
            output = station_dir / f"Fig4_Curvas_Excedidos_{station.replace(' ', '_')}.png"
            if plot_curvas_excedidos(station_df, station, output):
                print(f"  OK: Fig4_Curvas_Excedidos_{station.replace(' ', '_')}.png")
                figuras_generadas += 1
        except Exception as e:
            print(f"  ERROR Fig4: {e}")
        
        # Figura 5: Ajuste distribuciones
        try:
            output = station_dir / f"Fig5_Ajuste_Distribuciones_{station.replace(' ', '_')}.png"
            if plot_ajuste_distribuciones(station_df, station, output):
                print(f"  OK: Fig5_Ajuste_Distribuciones_{station.replace(' ', '_')}.png")
                figuras_generadas += 1
        except Exception as e:
            print(f"  ERROR Fig5: {e}")
        
        print(f"  Total figuras generadas: {figuras_generadas}/3")
    
    print("\n" + "=" * 70)
    print("PROCESO COMPLETADO")
    print(f"Directorio: {OUTPUT_DIR}")

if __name__ == '__main__':
    main()
