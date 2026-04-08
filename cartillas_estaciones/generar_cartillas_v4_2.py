"""
Generador de Cartillas de Estaciones v4.2
Crea 5 figuras por estación con datos imputados del sistema v4.2
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import scipy.stats as stats
from scipy.interpolate import make_interp_spline
import warnings
warnings.filterwarnings('ignore')

# Configuración de estilo
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['axes.grid'] = True
plt.rcParams['grid.alpha'] = 0.3

# Rutas
INPUT_FILE = Path(r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\Informes\imputacion\Datos_Imputados_v3.csv')
OUTPUT_DIR = Path(r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\cartillas_estaciones\v4_2')

# Lista de estaciones
ESTACIONES = [
    'SAN_PEDRITO', 'CALAMAR', 'TENERIFE', 'PLATO', 'MAGANGUE', 'BARBOSA', 
    'COYONGAL', 'ARMENIA', 'RIO_NUEVO', 'LAS_PALOMAS', 'LAS_AGUADAS', 
    'EL_BANCO', 'PENONCITO', 'LA_GLORIA', 'GAMARRA_AUT', 'EL_CONTENTO', 
    'SITIO_NUEVO', 'PUERTO_WILCHES'
]

# Meses en español
MESES = ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN', 
         'JUL', 'AGO', 'SEP', 'OCT', 'NOV', 'DIC']

def load_data():
    """Carga los datos imputados."""
    df = pd.read_csv(INPUT_FILE)
    df['date'] = pd.to_datetime(df['date'])
    return df

def get_station_data(df, station):
    """Obtiene datos de una estación específica."""
    station_df = df[df['station'] == station].copy()
    station_df = station_df.sort_values('date')
    return station_df

def plot_serie_tiempo(station_df, station, output_path):
    """Figura 1: Serie temporal completa (datos imputados)."""
    fig, ax = plt.subplots(figsize=(14, 6))
    
    # Separar datos originales vs imputados
    original = station_df[station_df['data_source'] == 'original']
    imputed_hh = station_df[station_df['data_source'] == 'imputed_hh']
    imputed_local = station_df[station_df['data_source'] == 'imputed_local']
    
    # Plotear
    ax.plot(original['date'], original['level'], 'b-', linewidth=0.8, 
            label='Datos originales', alpha=0.8)
    
    if len(imputed_hh) > 0:
        ax.plot(imputed_hh['date'], imputed_hh['level'], 'r-', linewidth=0.8, 
                label='Imputado H-H', alpha=0.7)
    
    if len(imputed_local) > 0:
        ax.plot(imputed_local['date'], imputed_local['level'], 'g-', linewidth=0.8, 
                label='Imputado local', alpha=0.7)
    
    ax.set_title(f'SERIE DE TIEMPO DE NIVELES - {station.replace("_", " ")}', 
                 fontsize=13, fontweight='bold')
    ax.set_xlabel('Fecha', fontsize=11)
    ax.set_ylabel('Nivel (m.s.n.m.)', fontsize=11)
    ax.legend(loc='best', fontsize=9)
    ax.grid(True, alpha=0.3)
    
    # Formato de fechas en eje x
    ax.xaxis.set_major_locator(plt.MaxNLocator(10))
    fig.autofmt_xdate()
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    return True

def plot_violin_mensual(station_df, station, output_path):
    """Figura 2: Violin plot mensual (datos originales)."""
    # Solo datos originales
    original = station_df[station_df['data_source'] == 'original'].copy()
    
    if len(original) < 30:
        print(f"  AVISO {station}: Insuficientes datos originales para violin")
        return False
    
    fig, ax = plt.subplots(figsize=(14, 6))
    
    # Preparar datos por mes
    data_by_month = []
    positions = []
    for month in range(1, 13):
        month_data = original[original['month'] == month]['level'].dropna()
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
        pc.set_facecolor('steelblue')
        pc.set_alpha(0.7)
    
    parts['cmeans'].set_color('red')
    parts['cmedians'].set_color('black')
    
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(MESES)
    ax.set_title(f'DISTRIBUCIÓN MENSUAL DE NIVELES - {station.replace("_", " ")}', 
                 fontsize=13, fontweight='bold')
    ax.set_xlabel('Mes', fontsize=11)
    ax.set_ylabel('Nivel (m.s.n.m.)', fontsize=11)
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    return True

def plot_curva_duracion(station_df, station, output_path):
    """Figura 3: Curva de duración (datos imputados)."""
    fig, ax = plt.subplots(figsize=(10, 7))
    
    # Usar datos imputados (completos)
    levels = station_df['level'].dropna().sort_values(ascending=False)
    
    if len(levels) < 10:
        return False
    
    # Calcular probabilidad de excedencia
    n = len(levels)
    exceedance_prob = np.arange(1, n + 1) / (n + 1) * 100
    
    ax.plot(exceedance_prob, levels, 'b-', linewidth=1.5)
    
    # Líneas de referencia para percentiles comunes
    percentiles = [5, 25, 50, 75, 95]
    colors = ['#8B0000', '#6B8E23', 'black', '#5DADE2', '#D35400']
    for p, color in zip(percentiles, colors):
        level_p = np.percentile(levels, 100-p)
        ax.axhline(y=level_p, color=color, linestyle='--', alpha=0.5, linewidth=1)
        ax.text(95, level_p, f'{p}%', fontsize=9, va='center', color=color)
    
    ax.set_title(f'CURVA DE DURACIÓN - {station.replace("_", " ")}', 
                 fontsize=13, fontweight='bold')
    ax.set_xlabel('Probabilidad de Excedencia (%)', fontsize=11)
    ax.set_ylabel('Nivel (m.s.n.m.)', fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 100)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    return True

def plot_curvas_excedidos(station_df, station, output_path):
    """Figura 4: Curvas de frecuencia de niveles excedidos (datos imputados)."""
    fig, ax = plt.subplots(figsize=(14, 7))
    
    # Usar datos imputados
    df = station_df[station_df['level'].notna()].copy()
    
    if len(df) < 365:
        return False
    
    # Agrupar por día del año
    df['day_of_year'] = df['date'].dt.dayofyear
    
    # Calcular percentiles por día del año (usando ventana móvil)
    days = range(1, 367)
    p_max, p5, p25, p50, p75, p95, p_min = [], [], [], [], [], [], []
    
    for day in days:
        # Ventana de ±15 días para suavizar
        window_days = [(day + offset - 1) % 365 + 1 for offset in range(-15, 16)]
        day_data = df[df['day_of_year'].isin(window_days)]['level']
        
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
    
    # Colores según especificación
    ax.plot(days_smooth, p_max_s, color='black', linewidth=1.5, label='Máx')
    ax.plot(days_smooth, p5_s, color='#8B0000', linewidth=1.5, label='5%')      # rojo oscuro
    ax.plot(days_smooth, p25_s, color='#6B8E23', linewidth=1.5, label='25%')    # verde
    ax.plot(days_smooth, p50_s, color='black', linewidth=2.5, label='50%')      # mediana gruesa
    ax.plot(days_smooth, p75_s, color='#5DADE2', linewidth=1.5, label='75%')    # azul
    ax.plot(days_smooth, p95_s, color='#D35400', linewidth=1.5, label='95%')    # naranja
    ax.plot(days_smooth, p_min_s, color='black', linewidth=1.5, label='Mín')
    
    # Etiquetas de percentiles al final
    ax.text(367, p_max_s[-1], 'MAX', fontsize=9, va='center')
    ax.text(367, p5_s[-1], '5%', fontsize=9, va='center', color='#8B0000')
    ax.text(367, p25_s[-1], '25%', fontsize=9, va='center', color='#6B8E23')
    ax.text(367, p50_s[-1], '50%', fontsize=9, va='center', fontweight='bold')
    ax.text(367, p75_s[-1], '75%', fontsize=9, va='center', color='#5DADE2')
    ax.text(367, p95_s[-1], '95%', fontsize=9, va='center', color='#D35400')
    ax.text(367, p_min_s[-1], 'MIN', fontsize=9, va='center')
    
    # Formato
    year_start = df['year'].min()
    year_end = df['year'].max()
    ax.set_title(f'CURVA DE FRECUENCIA DE NIVELES EXCEDIDOS - {station.replace("_", " ")}\n{year_start} - {year_end}', 
                 fontsize=13, fontweight='bold')
    ax.set_xlabel('Mes', fontsize=11)
    ax.set_ylabel('NIVEL (m.s.n.m.)', fontsize=11)
    ax.set_xlim(0, 380)
    
    # Eje X con meses
    month_starts = [1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335]
    ax.set_xticks(month_starts)
    ax.set_xticklabels(MESES)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    return True

def plot_ajuste_distribuciones(station_df, station, output_path):
    """Figura 5: Ajuste de distribuciones (datos originales)."""
    # Solo datos originales
    original = station_df[station_df['data_source'] == 'original']['level'].dropna()
    
    if len(original) < 30:
        print(f"  AVISO {station}: Insuficientes datos originales para distribuciones")
        return False
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Panel izquierdo: Histograma con ajuste Normal
    ax1 = axes[0]
    mu, sigma = stats.norm.fit(original)
    
    n, bins, patches = ax1.hist(original, bins=30, density=True, alpha=0.7, 
                                color='steelblue', edgecolor='black')
    
    # Curva de ajuste normal
    x = np.linspace(original.min(), original.max(), 100)
    ax1.plot(x, stats.norm.pdf(x, mu, sigma), 'r-', linewidth=2, 
             label=f'Normal: μ={mu:.2f}, σ={sigma:.2f}')
    
    # Ajuste Log-normal
    shape, loc, scale = stats.lognorm.fit(original)
    ax1.plot(x, stats.lognorm.pdf(x, shape, loc, scale), 'g--', linewidth=2,
             label=f'Log-normal')
    
    ax1.set_title(f'DISTRIBUCIÓN DE NIVELES - {station.replace("_", " ")}', 
                  fontsize=12, fontweight='bold')
    ax1.set_xlabel('Nivel (m.s.n.m.)', fontsize=11)
    ax1.set_ylabel('Densidad de Probabilidad', fontsize=11)
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3)
    
    # Panel derecho: Q-Q plot
    ax2 = axes[1]
    stats.probplot(original, dist="norm", plot=ax2)
    ax2.set_title('Q-Q Plot (Normal)', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    # Prueba de normalidad
    stat, p_value = stats.shapiro(original[:min(5000, len(original))])
    normalidad = "Normal" if p_value > 0.05 else "No Normal"
    ax2.text(0.05, 0.95, f'Shapiro-Wilk: p={p_value:.4f}\n{normalidad}',
             transform=ax2.transAxes, fontsize=10, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    return True

def main():
    """Genera todas las cartillas."""
    print("=" * 70)
    print("GENERADOR DE CARTILLAS DE ESTACIONES v4.2")
    print("=" * 70)
    
    # Cargar datos
    print("\nCargando datos imputados...")
    df = load_data()
    print(f"Total registros: {len(df):,}")
    print(f"Estaciones: {df['station'].nunique()}")
    
    stats_summary = []
    
    for station in ESTACIONES:
        print(f"\n{'='*70}")
        print(f"Procesando: {station}")
        print('='*70)
        
        # Crear directorio de estación
        station_dir = OUTPUT_DIR / station
        station_dir.mkdir(exist_ok=True)
        
        # Obtener datos de la estación
        station_df = get_station_data(df, station)
        
        if len(station_df) == 0:
            print(f"  AVISO Sin datos para {station}")
            continue
        
        # Estadísticas
        original_count = (station_df['data_source'] == 'original').sum()
        imputed_count = (station_df['data_source'] != 'original').sum()
        total_count = len(station_df)
        coverage = (station_df['level'].notna().sum() / total_count) * 100
        
        print(f"  Datos originales: {original_count:,}")
        print(f"  Datos imputados: {imputed_count:,}")
        print(f"  Cobertura: {coverage:.1f}%")
        
        # Generar figuras
        figuras_generadas = 0
        
        # Figura 1: Serie de tiempo
        try:
            output = station_dir / f"Fig1_Serie_Tiempo_{station}.png"
            if plot_serie_tiempo(station_df, station, output):
                print(f"  OK Fig1_Serie_Tiempo_{station}.png")
                figuras_generadas += 1
        except Exception as e:
            print(f"  ERROR Fig1 error: {e}")
        
        # Figura 2: Violin mensual
        try:
            output = station_dir / f"Fig2_Violin_Mensual_{station}.png"
            if plot_violin_mensual(station_df, station, output):
                print(f"  OK Fig2_Violin_Mensual_{station}.png")
                figuras_generadas += 1
        except Exception as e:
            print(f"  ERROR Fig2 error: {e}")
        
        # Figura 3: Curva de duración
        try:
            output = station_dir / f"Fig3_Curva_Duracion_{station}.png"
            if plot_curva_duracion(station_df, station, output):
                print(f"  OK Fig3_Curva_Duracion_{station}.png")
                figuras_generadas += 1
        except Exception as e:
            print(f"  ERROR Fig3 error: {e}")
        
        # Figura 4: Curvas excedidos
        try:
            output = station_dir / f"Fig4_Curvas_Excedidos_{station}.png"
            if plot_curvas_excedidos(station_df, station, output):
                print(f"  OK Fig4_Curvas_Excedidos_{station}.png")
                figuras_generadas += 1
        except Exception as e:
            print(f"  ERROR Fig4 error: {e}")
        
        # Figura 5: Ajuste distribuciones
        try:
            output = station_dir / f"Fig5_Ajuste_Distribuciones_{station}.png"
            if plot_ajuste_distribuciones(station_df, station, output):
                print(f"  OK Fig5_Ajuste_Distribuciones_{station}.png")
                figuras_generadas += 1
        except Exception as e:
            print(f"  ERROR Fig5 error: {e}")
        
        stats_summary.append({
            'station': station,
            'total_records': total_count,
            'original': original_count,
            'imputed': imputed_count,
            'coverage_pct': coverage,
            'figuras_generadas': figuras_generadas
        })
    
    # Reporte final
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
