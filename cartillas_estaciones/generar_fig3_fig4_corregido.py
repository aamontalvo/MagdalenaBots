"""
Generador de Figuras 3 y 4 con formato exacto de las versiones v2 aprobadas
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from scipy.interpolate import make_interp_spline
import warnings
warnings.filterwarnings('ignore')

# Rutas
INPUT_FILE = Path(r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\Informes\imputacion\Datos_Imputados_v4_2_Complete.csv')
OUTPUT_DIR = Path(r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\cartillas_estaciones\v4_2')

ESTACIONES = [
    'Calamar', 'Tenerife', 'Plato', 'Magangue', 'Barbosa', 
    'Coyongal', 'Armenia', 'Rio Nuevo', 'Las Palomas', 'Las Aguadas', 
    'El Banco', 'Penoncito', 'La Gloria', 'Gamarra Aut', 'El Contento', 
    'Sitio Nuevo', 'Puerto Wilches', 'San Pedrito'
]

MESES = ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN', 
         'JUL', 'AGO', 'SEP', 'OCT', 'NOV', 'DIC']

def load_data():
    df = pd.read_csv(INPUT_FILE)
    df['Fecha'] = pd.to_datetime(df['Fecha'], format='%d-%m-%Y')
    df['month'] = df['Fecha'].dt.month
    df['year'] = df['Fecha'].dt.year
    df['day_of_year'] = df['Fecha'].dt.dayofyear
    return df

def plot_fig3_curva_duracion(station_df, station_name, output_path):
    """Figura 3: Curva de duracion con marcadores en P50, P90, P95, P100."""
    fig, ax = plt.subplots(figsize=(10, 7))
    
    levels = station_df['Cota'].dropna().sort_values(ascending=False)
    
    if len(levels) < 10:
        return False
    
    n = len(levels)
    exceedance_prob = np.arange(1, n + 1) / (n + 1) * 100
    
    # Curva principal en azul
    ax.plot(exceedance_prob, levels, color='#1f77b4', linewidth=2.5)
    
    # Calcular percentiles clave
    p50_level = np.percentile(levels, 50)
    p90_level = np.percentile(levels, 10)  # 90% de tiempo excedido
    p95_level = np.percentile(levels, 5)   # 95% de tiempo excedido
    p100_level = levels.min()  # Valor minimo (100% excedido)
    
    # Encontrar posiciones x para cada percentil
    p50_idx = np.argmin(np.abs(exceedance_prob - 50))
    p90_idx = np.argmin(np.abs(exceedance_prob - 90))
    p95_idx = np.argmin(np.abs(exceedance_prob - 95))
    p100_idx = np.argmin(np.abs(exceedance_prob - 99.5))  # Cerca del final
    
    # Marcadores circulares blancos con borde negro
    ax.plot(50, p50_level, 'o', markersize=12, markerfacecolor='white', markeredgecolor='black', markeredgewidth=1.5)
    ax.plot(90, p90_level, 'o', markersize=12, markerfacecolor='white', markeredgecolor='black', markeredgewidth=1.5)
    ax.plot(95, p95_level, 'o', markersize=12, markerfacecolor='white', markeredgecolor='black', markeredgewidth=1.5)
    ax.plot(99.5, p100_level, 'o', markersize=12, markerfacecolor='white', markeredgecolor='black', markeredgewidth=1.5)
    
    # Anotaciones con valores
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
    
    # Titulo con nombre en mayusculas
    ax.set_title(f'Curva de Duracion - {station_name.upper()}', 
                 fontsize=14, fontweight='bold')
    ax.set_xlabel('Porcentaje de tiempo excedido (%)', fontsize=12)
    ax.set_ylabel('Cota (m.s.n.m.)', fontsize=12)
    ax.grid(True, alpha=0.3, linestyle='-')
    ax.set_xlim(-2, 102)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    return True

def plot_fig4_curvas_excedidos(station_df, station_name, output_path):
    """Figura 4: Curvas de frecuencia con etiquetas a la derecha."""
    fig, ax = plt.subplots(figsize=(14, 8))
    
    df_valid = station_df[station_df['Cota'].notna()].copy()
    
    if len(df_valid) < 365:
        return False
    
    days = range(1, 367)
    p_max, p5, p25, p50, p75, p95, p_min = [], [], [], [], [], [], []
    
    for day in days:
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
    ax.plot(days_smooth, p5_s, color='#8B0000', linewidth=1.5)   # rojo oscuro
    ax.plot(days_smooth, p25_s, color='#6B8E23', linewidth=1.5)  # verde oliva
    ax.plot(days_smooth, p50_s, color='black', linewidth=3)      # negro grueso
    ax.plot(days_smooth, p75_s, color='#5DADE2', linewidth=1.5)  # azul claro
    ax.plot(days_smooth, p95_s, color='#D35400', linewidth=1.5)  # naranja
    ax.plot(days_smooth, p_min_s, color='black', linewidth=1.5)
    
    # Etiquetas a la derecha (alineadas con el valor final de cada curva)
    ax.text(370, p_max_s[-1], 'MAX', fontsize=12, va='center', fontweight='bold')
    ax.text(370, p5_s[-1], '5%', fontsize=12, va='center', color='#8B0000', fontweight='bold')
    ax.text(370, p25_s[-1], '25%', fontsize=12, va='center', color='#6B8E23', fontweight='bold')
    ax.text(370, p50_s[-1], '50%', fontsize=12, va='center', fontweight='bold')
    ax.text(370, p75_s[-1], '75%', fontsize=12, va='center', color='#5DADE2', fontweight='bold')
    ax.text(370, p95_s[-1], '95%', fontsize=12, va='center', color='#D35400', fontweight='bold')
    ax.text(370, p_min_s[-1], 'MIN', fontsize=12, va='center', fontweight='bold')
    
    # Titulo con formato "Fig4. ... - ESTACION"
    ax.set_title(f'Fig4. Curvas de Frecuencia de Niveles Excedidos - {station_name.upper()}', 
                 fontsize=14, fontweight='bold')
    ax.set_xlabel('Mes', fontsize=12, fontweight='bold')
    ax.set_ylabel('Cota (m)', fontsize=12, fontweight='bold')
    
    # Eje X con meses
    month_starts = [1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335]
    ax.set_xticks(month_starts)
    ax.set_xticklabels(MESES, fontsize=11)
    ax.grid(True, alpha=0.2, linestyle='-')
    
    # Extender limites para etiquetas
    ax.set_xlim(0, 420)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    return True

def main():
    print("=" * 80)
    print("GENERADOR DE FIGURAS 3 Y 4 - FORMATO CORREGIDO")
    print("=" * 80)
    print()
    
    df = load_data()
    
    for i, station in enumerate(ESTACIONES, 1):
        print(f"\n[{i}/18] {station}")
        
        station_dir = OUTPUT_DIR / station
        station_dir.mkdir(exist_ok=True, parents=True)
        
        station_df = df[df['NombreEstacion'] == station].copy()
        
        if len(station_df) == 0:
            print(f"  SIN DATOS")
            continue
        
        # Figura 3
        try:
            output = station_dir / f"Fig3_Curva_Duracion_{station}.png"
            if plot_fig3_curva_duracion(station_df, station, output):
                print(f"  [OK] Fig3 - Curva de Duracion")
        except Exception as e:
            print(f"  [ERROR] Fig3: {e}")
        
        # Figura 4
        try:
            output = station_dir / f"Fig4_Curvas_Excedidos_{station}.png"
            if plot_fig4_curvas_excedidos(station_df, station, output):
                print(f"  [OK] Fig4 - Curvas Excedidos")
        except Exception as e:
            print(f"  [ERROR] Fig4: {e}")
    
    print("\n" + "=" * 80)
    print("PROCESO COMPLETADO")

if __name__ == '__main__':
    main()
