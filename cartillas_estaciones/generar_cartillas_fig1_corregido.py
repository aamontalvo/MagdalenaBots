"""
Generador de Cartillas Figura 1 - CORREGIDO
Crea solo Figura 1 (Serie de Tiempo) para todas las estaciones
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path
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
    'Sitio Nuevo', 'Puerto Wilches'
]

def load_data():
    """Carga los datos imputados."""
    df = pd.read_csv(INPUT_FILE)
    df['Fecha'] = pd.to_datetime(df['Fecha'], format='%d-%m-%Y')
    return df

def get_station_data(df, station_name):
    """Obtiene datos de una estacion especifica por nombre exacto."""
    station_df = df[df['NombreEstacion'] == station_name].copy()
    station_df = station_df.sort_values('Fecha')
    return station_df

def plot_serie_tiempo(station_df, station_name, output_path):
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
    ax.set_title(f'Serie de Tiempo - {station_name.replace("_", " ")}', 
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

def plot_curva_duracion(station_df, station_name, output_path):
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
    
    ax.set_title(f'Curva de Duracion de Cotas - {station_name.replace("_", " ")}', 
                 fontsize=13, fontweight='bold')
    ax.set_xlabel('Porcentaje de tiempo excedido (%)', fontsize=11)
    ax.set_ylabel('Cota (m.s.n.m.)', fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 100)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    return True

def main():
    """Genera Figura 1 y Figura 3 para todas las estaciones."""
    print("=" * 70)
    print("GENERADOR DE FIGURAS 1 Y 3")
    print("=" * 70)
    
    # Cargar datos
    print("\nCargando datos imputados...")
    df = load_data()
    print(f"Total registros: {len(df):,}")
    print(f"Estaciones unicas: {df['NombreEstacion'].nunique()}")
    
    for station in ESTACIONES:
        print(f"\nProcesando: {station}")
        
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
        
        # Generar Figura 1
        try:
            output = station_dir / f"Fig1_Serie_Tiempo_{station}.png"
            if plot_serie_tiempo(station_df, station, output):
                print(f"  OK: Fig1_Serie_Tiempo_{station}.png")
        except Exception as e:
            print(f"  ERROR Fig1: {e}")
        
        # Generar Figura 3
        try:
            output = station_dir / f"Fig3_Curva_Duracion_{station}.png"
            if plot_curva_duracion(station_df, station, output):
                print(f"  OK: Fig3_Curva_Duracion_{station}.png")
        except Exception as e:
            print(f"  ERROR Fig3: {e}")
    
    print("\n" + "=" * 70)
    print("PROCESO COMPLETADO")
    print(f"Directorio: {OUTPUT_DIR}")

if __name__ == '__main__':
    main()
