"""
Generador de todas las figuras (Fig1, Fig2, Fig3, Fig4) para todas las estaciones
Usando datos imputados v4.2
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
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

# Lista de estaciones (nombres exactos del archivo CSV)
ESTACIONES = [
    'Calamar', 'Tenerife', 'Plato', 'Magangue', 'Barbosa', 
    'Coyongal', 'Armenia', 'Rio Nuevo', 'Las Palomas', 'Las Aguadas', 
    'El Banco', 'Penoncito', 'La Gloria', 'Gamarra Aut', 'El Contento', 
    'Sitio Nuevo', 'Puerto Wilches', 'San Pedrito'
]

# Meses en espanol
MESES = ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN', 
         'JUL', 'AGO', 'SEP', 'OCT', 'NOV', 'DIC']

def load_data():
    """Carga los datos imputados v4.2."""
    print(f"Cargando datos desde: {INPUT_FILE}")
    df = pd.read_csv(INPUT_FILE)
    df['Fecha'] = pd.to_datetime(df['Fecha'], format='%d-%m-%Y')
    df['month'] = df['Fecha'].dt.month
    df['year'] = df['Fecha'].dt.year
    df['day_of_year'] = df['Fecha'].dt.dayofyear
    print(f"Total registros cargados: {len(df):,}")
    print(f"Estaciones en datos: {df['NombreEstacion'].nunique()}")
    return df

def get_station_data(df, station_name):
    """Obtiene datos de una estacion especifica por nombre exacto."""
    station_df = df[df['NombreEstacion'] == station_name].copy()
    station_df = station_df.sort_values('Fecha')
    return station_df

def plot_fig1_serie_tiempo(station_df, station_name, output_path):
    """Figura 1: Serie temporal completa con eje X cada 5 anos."""
    fig, ax = plt.subplots(figsize=(14, 6))
    
    # Linea negra continua con transparencia para datos validos
    valid_data = station_df[station_df['Cota'].notna()]
    ax.plot(valid_data['Fecha'], valid_data['Cota'], 'k-', linewidth=0.8, alpha=0.85)
    
    # Calcular estadisticas - SOLO de registros con Cota valida
    valid_data_with_source = station_df[station_df['Cota'].notna()]
    total_valid = len(valid_data_with_source)
    original_count = (valid_data_with_source['Metodo'] == 'Original').sum()
    imputed_count = total_valid - original_count
    
    pct_original = (original_count / total_valid) * 100 if total_valid > 0 else 0
    pct_imputed = (imputed_count / total_valid) * 100 if total_valid > 0 else 0
    
    year_start = int(station_df['Fecha'].dt.year.min())
    year_end = int(station_df['Fecha'].dt.year.max())
    
    # Anotacion compacta - solo 2 lineas con fuente mas pequena
    annotation_text = (f'Periodo: {year_start}-{year_end} Total: {total_valid:,} registros\n'
                      f'Medidos: {pct_original:.1f}% | Imputados: {pct_imputed:.1f}%')
    
    ax.text(0.02, 0.98, annotation_text,
            transform=ax.transAxes, fontsize=8,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.9, pad=0.3))
    
    # Titulo sin "(Datos v4.2)"
    ax.set_title(f'Serie de Tiempo - {station_name}', 
                 fontsize=13, fontweight='bold')
    ax.set_xlabel('Fecha', fontsize=11)
    ax.set_ylabel('Cota (m.s.n.m.)', fontsize=11)
    ax.grid(True, alpha=0.3)
    
    # Configuracion eje X: ticks principales cada 5 anos, ticks secundarios cada 1 ano
    ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))
    
    # Encontrar rango de anos para ticks
    years_range = range((year_start // 5) * 5, year_end + 6, 5)
    ax.set_xticks([pd.Timestamp(year=y, month=1, day=1) for y in years_range if y >= year_start - 2 and y <= year_end + 2])
    
    # Ticks secundarios cada ano
    ax.xaxis.set_minor_locator(plt.MultipleLocator(365.25))
    ax.tick_params(axis='x', which='minor', length=3, color='#AAAAAA')
    
    # Formato de fecha solo mostrando el ano
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    
    # Rotar etiquetas
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    return True

def plot_fig2_violin_mensual(station_df, station_name, output_path):
    """Figura 2: Violin plot mensual con leyenda para media y mediana."""
    # Solo datos originales
    original = station_df[station_df['Metodo'] == 'Original'].copy()
    
    if len(original) < 30:
        print(f"    AVISO: Insuficientes datos originales para violin ({len(original)})")
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

def plot_fig3_curva_duracion(station_df, station_name, output_path):
    """Figura 3: Curva de duracion con Q95 en negro dashed."""
    fig, ax = plt.subplots(figsize=(10, 7))
    
    # Usar datos imputados (completos)
    levels = station_df['Cota'].dropna().sort_values(ascending=False)
    
    if len(levels) < 10:
        return False
    
    # Calcular probabilidad de excedencia
    n = len(levels)
    exceedance_prob = np.arange(1, n + 1) / (n + 1) * 100
    
    # Curva principal en azul
    ax.plot(exceedance_prob, levels, 'b-', linewidth=1.5)
    
    # Linea Q95 (95% de tiempo excedido = zona baja) en negro dashed
    q95_level = np.percentile(levels, 5)
    ax.axhline(y=q95_level, color='black', linestyle='--', linewidth=2, label='Q95')
    
    # Otras lineas de referencia
    percentiles = [50]
    for p in percentiles:
        level_p = np.percentile(levels, 100-p)
        ax.axhline(y=level_p, color='gray', linestyle=':', alpha=0.6, linewidth=1)
    
    # Anotacion con valores
    p50_level = np.percentile(levels, 50)
    annotation_text = f'Nivel medio (P50): {p50_level:.2f} m\nNivel Q95: {q95_level:.2f} m'
    
    ax.text(0.98, 0.98, annotation_text,
            transform=ax.transAxes, fontsize=10,
            verticalalignment='top', horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.9))
    
    ax.set_title(f'Curva de Duracion de Cotas - {station_name}', 
                 fontsize=13, fontweight='bold')
    ax.set_xlabel('Porcentaje de tiempo excedido (%)', fontsize=11)
    ax.set_ylabel('Cota (m.s.n.m.)', fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 100)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    return True

def plot_fig4_curvas_excedidos(station_df, station_name, output_path):
    """Figura 4: Curvas de frecuencia con etiquetas FUERA del box."""
    fig, ax = plt.subplots(figsize=(14, 7))
    
    # Usar datos imputados
    df_valid = station_df[station_df['Cota'].notna()].copy()
    
    if len(df_valid) < 365:
        print(f"    AVISO: Insuficientes datos para curvas excedidos ({len(df_valid)})")
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

def main():
    """Genera Figuras 1-4 para todas las estaciones."""
    print("=" * 80)
    print("GENERADOR DE FIGURAS 1-4 - DATOS v4.2 IMPUTADOS")
    print("=" * 80)
    print()
    
    # Cargar datos
    df = load_data()
    print()
    
    # Resumen
    resumen = []
    
    for i, station in enumerate(ESTACIONES, 1):
        print(f"\n[{i}/18] Procesando: {station}")
        print("-" * 60)
        
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
        print(f"  Datos: Total={total_count:,} | Originales={original_count:,}")
        
        figuras_ok = 0
        
        # Figura 1: Serie de tiempo
        try:
            output = station_dir / f"Fig1_Serie_Tiempo_{station}.png"
            if plot_fig1_serie_tiempo(station_df, station, output):
                print(f"  [OK] Fig1 - Serie de Tiempo")
                figuras_ok += 1
        except Exception as e:
            print(f"  [ERROR] Fig1: {e}")
        
        # Figura 2: Violin mensual
        try:
            output = station_dir / f"Fig2_Violin_Mensual_{station}.png"
            if plot_fig2_violin_mensual(station_df, station, output):
                print(f"  [OK] Fig2 - Violin Mensual")
                figuras_ok += 1
        except Exception as e:
            print(f"  [ERROR] Fig2: {e}")
        
        # Figura 3: Curva de duracion
        try:
            output = station_dir / f"Fig3_Curva_Duracion_{station}.png"
            if plot_fig3_curva_duracion(station_df, station, output):
                print(f"  [OK] Fig3 - Curva de Duracion")
                figuras_ok += 1
        except Exception as e:
            print(f"  [ERROR] Fig3: {e}")
        
        # Figura 4: Curvas excedidos
        try:
            output = station_dir / f"Fig4_Curvas_Excedidos_{station}.png"
            if plot_fig4_curvas_excedidos(station_df, station, output):
                print(f"  [OK] Fig4 - Curvas Excedidos")
                figuras_ok += 1
        except Exception as e:
            print(f"  [ERROR] Fig4: {e}")
        
        print(f"  Figuras generadas: {figuras_ok}/4")
        resumen.append({'estacion': station, 'figuras': figuras_ok})
    
    print("\n" + "=" * 80)
    print("RESUMEN FINAL")
    print("=" * 80)
    total_figuras = sum(r['figuras'] for r in resumen)
    print(f"Total figuras generadas: {total_figuras} / {len(ESTACIONES) * 4}")
    print(f"Directorio: {OUTPUT_DIR}")
    
    for r in resumen:
        status = "OK" if r['figuras'] == 4 else "INCOMPLETO"
        print(f"  {r['estacion']}: {r['figuras']}/4 [{status}]")

if __name__ == '__main__':
    main()
