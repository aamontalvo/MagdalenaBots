"""
Script de prueba para Fig4 - Curvas de Frecuencia de Niveles Excedidos
Solo para estación CALAMAR - Iteración 1
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from scipy.interpolate import make_interp_spline

# Configuración de estilo
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['axes.grid'] = True
plt.rcParams['grid.alpha'] = 0.3

# Rutas
INPUT_FILE = Path(r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\Informes\imputacion\Datos_Imputados_v3.csv')
OUTPUT_DIR = Path(r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\cartillas_estaciones\v4_2\CALAMAR')

# Meses en español
MESES = ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN', 
         'JUL', 'AGO', 'SEP', 'OCT', 'NOV', 'DIC']

def load_data():
    """Carga los datos imputados."""
    df = pd.read_csv(INPUT_FILE)
    df['date'] = pd.to_datetime(df['date'])
    return df

def plot_curvas_excedidos_calamar():
    """Figura 4: Curvas de frecuencia de niveles excedidos - versión corregida."""
    
    # Cargar datos
    df_all = load_data()
    station = 'CALAMAR'
    station_df = df_all[df_all['station'] == station].copy()
    
    # Filtrar datos válidos
    df = station_df[station_df['level'].notna()].copy()
    
    if len(df) < 365:
        print(f"Datos insuficientes para {station}")
        return False
    
    # Crear figura con tamaño específico
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Agrupar por día del año
    df['day_of_year'] = df['date'].dt.dayofyear
    
    # Calcular percentiles por día del año
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
        try:
            spl = make_interp_spline(np.array(days)[mask], y[mask], k=2)
            return spl(days_smooth)
        except:
            return y
    
    p_max_s = smooth_curve(p_max)
    p5_s = smooth_curve(p5)
    p25_s = smooth_curve(p25)
    p50_s = smooth_curve(p50)
    p75_s = smooth_curve(p75)
    p95_s = smooth_curve(p95)
    p_min_s = smooth_curve(p_min)
    
    # Colores según especificación
    ax.plot(days_smooth, p_max_s, color='black', linewidth=1.5, label='_nolegend_')
    ax.plot(days_smooth, p5_s, color='#8B0000', linewidth=1.5, label='_nolegend_')
    ax.plot(days_smooth, p25_s, color='#6B8E23', linewidth=1.5, label='_nolegend_')
    ax.plot(days_smooth, p50_s, color='black', linewidth=2.5, label='_nolegend_')
    ax.plot(days_smooth, p75_s, color='#5DADE2', linewidth=1.5, label='_nolegend_')
    ax.plot(days_smooth, p95_s, color='#D35400', linewidth=1.5, label='_nolegend_')
    ax.plot(days_smooth, p_min_s, color='black', linewidth=1.5, label='_nolegend_')
    
    # === CONFIGURACIÓN DEL EJE X ===
    # Meses principales (líneas verticales principales)
    month_starts = [1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335]
    ax.set_xticks(month_starts)
    ax.set_xticklabels(MESES, fontsize=11)
    
    # Días intermedios (ticks secundarios cada 15 días aprox)
    secondary_ticks = [15, 47, 75, 106, 136, 167, 197, 228, 259, 289, 320, 350]
    ax.set_xticks(secondary_ticks, minor=True)
    ax.tick_params(axis='x', which='minor', length=4, color='gray')
    
    # Líneas verticales para cada mes (grid principal)
    for m in month_starts:
        ax.axvline(x=m, color='lightgray', linestyle='-', alpha=0.5, linewidth=0.8)
    
    # === LÍNEA DE CORTE/DELIMITACIÓN AL FINAL ===
    # Línea vertical gruesa al final del eje X (día 366)
    ax.axvline(x=366, color='black', linewidth=3, linestyle='-')
    
    # === ETIQUETAS FUERA DEL BOX ===
    # Extender el eje X para dar espacio a las etiquetas
    ax.set_xlim(0, 400)
    
    # Obtener el rango Y para posicionar etiquetas
    y_min, y_max = ax.get_ylim()
    y_range = y_max - y_min
    
    # Dibujar líneas horizontales punteadas desde cada curva hasta la línea de corte
    # y luego etiquetas fuera
    def add_label_with_line(y_value, label, color, y_offset=0):
        # Línea punteada desde el final de la curva hasta la línea de corte
        ax.plot([366, 375], [y_value, y_value], color=color, 
                linewidth=1.5, linestyle='--', alpha=0.7)
        # Etiqueta fuera del box
        ax.text(378, y_value + y_offset, label, fontsize=11, 
                va='center', color=color, fontweight='bold' if label in ['MAX', 'MIN', '50%'] else 'normal')
    
    # Agregar etiquetas para cada percentil
    add_label_with_line(p_max_s[-1], 'MAX', 'black', 0.2)
    add_label_with_line(p5_s[-1], '5%', '#8B0000', 0)
    add_label_with_line(p25_s[-1], '25%', '#6B8E23', 0)
    add_label_with_line(p50_s[-1], '50%', 'black', 0)
    add_label_with_line(p75_s[-1], '75%', '#5DADE2', 0)
    add_label_with_line(p95_s[-1], '95%', '#D35400', 0)
    add_label_with_line(p_min_s[-1], 'MIN', 'black', -0.2)
    
    # === GRID CONFIGURACIÓN ===
    ax.grid(True, which='major', alpha=0.4, linestyle='-', linewidth=0.5)
    ax.grid(True, which='minor', alpha=0.2, linestyle=':', linewidth=0.5)
    
    # === TÍTULO Y EJES ===
    year_start = df['year'].min()
    year_end = df['year'].max()
    
    ax.set_title(f'CURVA DE FRECUENCIA DE NIVELES EXCEDIDOS - {station}\n{year_start} - {year_end}', 
                 fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('Mes', fontsize=12)
    ax.set_ylabel('NIVEL (m.s.n.m.)', fontsize=12)
    
    # Ajustar límites Y para dar espacio
    ax.set_ylim(y_min - 0.5, y_max + 0.5)
    
    # === LÍNEA DE CORTE VISUAL ADICIONAL ===
    # Agregar una línea vertical adicional más marcada para el "corte"
    ax.axvline(x=366, color='darkgray', linewidth=1, linestyle='-', alpha=0.3, zorder=0)
    
    plt.tight_layout()
    
    # Guardar figura
    output_path = OUTPUT_DIR / f"Fig4_Curvas_Excedidos_{station}_TEST.png"
    plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"✓ Figura de prueba guardada: {output_path}")
    return True

if __name__ == '__main__':
    print("=" * 60)
    print("TEST - Figura 4: Curvas de Excedidos - CALAMAR")
    print("=" * 60)
    plot_curvas_excedidos_calamar()
    print("\nRevisa la imagen generada y dime qué ajustes necesitas.")
