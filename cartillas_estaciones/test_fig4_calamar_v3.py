"""
Script de prueba para Fig4 - Curvas de Frecuencia de Niveles Excedidos
Solo para estacion CALAMAR - Iteracion 3
FUENTE DE DATOS: Datos_Imputados_v4_2_Complete.csv (UNICA FUENTE VERDADERA)
Matplotlib puro, sin suavizado, agrupacion por dia exacta
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Configuracion de estilo
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12

# Rutas - FUENTE UNICA DE DATOS IMPUTADOS V4.2
INPUT_FILE = Path(r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\Informes\imputacion\Datos_Imputados_v4_2_Complete.csv')
OUTPUT_DIR = Path(r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\cartillas_estaciones\v4_2\CALAMAR')

# Meses en espanol
MESES = ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN', 
         'JUL', 'AGO', 'SEP', 'OCT', 'NOV', 'DIC']

def load_data():
    """Carga los datos imputados v4.2 - FUENTE UNICA."""
    df = pd.read_csv(INPUT_FILE)
    df['Fecha'] = pd.to_datetime(df['Fecha'], format='%d-%m-%Y')
    return df

def plot_curvas_excedidos_calamar():
    """Figura 4: Curvas de frecuencia de niveles excedidos - matplotlib puro."""
    
    # Cargar datos v4.2
    df_all = load_data()
    station = 'Calamar'
    station_df = df_all[df_all['NombreEstacion'] == station].copy()
    
    # Filtrar datos validos
    df = station_df[station_df['Cota'].notna()].copy()
    
    if len(df) < 365:
        print(f"Datos insuficientes para {station}")
        return False
    
    # Agrupar por dia del ano
    df['day_of_year'] = df['Fecha'].dt.dayofyear
    
    # Calcular percentiles para CADA DIA del ano exacto
    days = range(1, 367)
    p_max, p5, p25, p50, p75, p95, p_min = [], [], [], [], [], [], []
    
    for day in days:
        day_data = df[df['day_of_year'] == day]['Cota']
        
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
    
    days_array = np.array(days)
    p_max = np.array(p_max)
    p5 = np.array(p5)
    p25 = np.array(p25)
    p50 = np.array(p50)
    p75 = np.array(p75)
    p95 = np.array(p95)
    p_min = np.array(p_min)
    
    # Crear figura
    fig = plt.figure(figsize=(14, 8))
    ax = fig.add_axes([0.08, 0.10, 0.75, 0.80])
    
    # Colores
    ax.plot(days_array, p_max, color='black', linewidth=1.5)
    ax.plot(days_array, p5, color='#8B0000', linewidth=1.5)
    ax.plot(days_array, p25, color='#6B8E23', linewidth=1.5)
    ax.plot(days_array, p50, color='black', linewidth=2.5)
    ax.plot(days_array, p75, color='#5DADE2', linewidth=1.5)
    ax.plot(days_array, p95, color='#D35400', linewidth=1.5)
    ax.plot(days_array, p_min, color='black', linewidth=1.5)
    
    # Eje X
    month_starts = [1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335]
    ax.set_xticks(month_starts)
    ax.set_xticklabels(MESES, fontsize=11)
    
    secondary_ticks = [15, 47, 75, 106, 136, 167, 197, 228, 259, 289, 320, 350]
    ax.set_xticks(secondary_ticks, minor=True)
    ax.tick_params(axis='x', which='minor', length=4, color='gray')
    
    # Grid
    ax.grid(True, which='major', alpha=0.4, linestyle='-', linewidth=0.5)
    ax.grid(True, which='minor', alpha=0.2, linestyle=':', linewidth=0.5)
    
    # Limites
    ax.set_xlim(1, 366)
    
    # Linea de corte
    ax.axvline(x=366, color='black', linewidth=2.5, linestyle='-')
    
    # Etiquetas
    def get_last_valid(arr):
        valid = arr[~np.isnan(arr)]
        return valid[-1] if len(valid) > 0 else np.nan
    
    y_max_val = get_last_valid(p_max)
    y_5_val = get_last_valid(p5)
    y_25_val = get_last_valid(p25)
    y_50_val = get_last_valid(p50)
    y_75_val = get_last_valid(p75)
    y_95_val = get_last_valid(p95)
    y_min_val = get_last_valid(p_min)
    
    def add_label_right(y_value, label, color, y_offset=0, fontweight='normal'):
        ax.plot([366, 368], [y_value, y_value], color=color, 
                linewidth=1.5, linestyle='--', alpha=0.6)
        ax.text(370, y_value + y_offset, label, fontsize=11, 
                va='center', color=color, fontweight=fontweight)
    
    add_label_right(y_max_val, 'MAX', 'black', 0.15, 'bold')
    add_label_right(y_5_val, '5%', '#8B0000', 0)
    add_label_right(y_25_val, '25%', '#6B8E23', 0)
    add_label_right(y_50_val, '50%', 'black', 0, 'bold')
    add_label_right(y_75_val, '75%', '#5DADE2', 0)
    add_label_right(y_95_val, '95%', '#D35400', 0)
    add_label_right(y_min_val, 'MIN', 'black', -0.15, 'bold')
    
    # Titulo
    year_start = int(df['Fecha'].dt.year.min())
    year_end = int(df['Fecha'].dt.year.max())
    
    ax.set_title(f'CURVA DE FRECUENCIA DE NIVELES EXCEDIDOS - {station.upper()}\n{year_start} - {year_end}', 
                 fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('Mes', fontsize=12)
    ax.set_ylabel('NIVEL (m.s.n.m.)', fontsize=12)
    
    y_min, y_max = ax.get_ylim()
    ax.set_ylim(y_min - 0.3, y_max + 0.3)
    
    # Guardar
    output_path = OUTPUT_DIR / f"Fig4_Curvas_Excedidos_{station.upper()}_TEST_v3.png"
    plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"Figura guardada: {output_path}")
    print(f"FUENTE: Datos_Imputados_v4_2_Complete.csv")
    print(f"Dias calculados: {len([x for x in p50 if not np.isnan(x)])}/366")
    return True

if __name__ == '__main__':
    print("=" * 60)
    print("TEST - Figura 4: Curvas de Excedidos - CALAMAR v3")
    print("FUENTE: Datos_Imputados_v4_2_Complete.csv")
    print("=" * 60)
    plot_curvas_excedidos_calamar()
