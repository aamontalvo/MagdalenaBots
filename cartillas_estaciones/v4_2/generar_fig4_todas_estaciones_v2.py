# -*- coding: utf-8 -*-
"""
Fig4 - Curvas de Frecuencia de Niveles Excedidos
PARA TODAS LAS ESTACIONES
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Configuracion
BASE_DIR = r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\cartillas_estaciones\v4_2'

# Lista de estaciones con sus nombres de archivo
ESTACIONES = [
    ('Puerto Wilches', 'PUERTO_WILCHES'),
    ('Sitio Nuevo', 'SITIO_NUEVO'),
    ('El Contento', 'EL_CONTENTO'),
    ('La Gloria', 'LA_GLORIA'),
    ('Gamarra Aut', 'GAMARRA_AUT'),
    ('El Banco', 'EL_BANCO'),
    ('Penoncito', 'PENONCITO'),
    ('Armenia', 'ARMENIA'),
    ('Las Palomas', 'LAS_PALOMAS'),
    ('Plato', 'PLATO'),
    ('Las Aguadas', 'LAS_AGUADAS'),
    ('Barbosa', 'BARBOSA'),
    ('Rio Nuevo', 'RIO_NUEVO'),
    ('Magangue', 'MAGANGUE'),
    ('Coyongal', 'COYONGAL'),
    ('Tenerife', 'TENERIFE'),
    ('San Pedrito', 'SAN_PEDRITO'),
    ('Calamar', 'CALAMAR'),
]

def generar_fig4(estacion_nombre, estacion_key):
    """Genera Fig4 para una estacion"""
    
    # Buscar archivo de percentiles (con o sin _FINAL)
    estacion_dir = Path(BASE_DIR) / estacion_key
    percentiles_path = estacion_dir / f'Fig4_Percentiles_{estacion_key}_FINAL.csv'
    
    if not percentiles_path.exists():
        percentiles_path = estacion_dir / f'Fig4_Percentiles_{estacion_key}.csv'
    
    if not percentiles_path.exists():
        print(f'  [ERROR] No se encontro percentiles para {estacion_nombre}')
        return False
    
    df = pd.read_csv(percentiles_path)
    print(f'  Percentiles: {len(df)} dias')
    
    # Crear figura
    fig, ax = plt.subplots(figsize=(14, 8))
    days = df['day_of_year'].values
    
    # Colores y grosores
    colors = {
        'max': 'black', 'p95': '#8B0000', 'p75': '#6B8E23',
        'p50': 'black', 'p25': '#5DADE2', 'p5': '#D35400', 'min': 'black'
    }
    linewidths = {
        'max': 1.2, 'p95': 1.2, 'p75': 1.2, 'p50': 2.5,
        'p25': 1.2, 'p5': 1.2, 'min': 1.2
    }
    
    # Dibujar lineas
    for col in ['max', 'p95', 'p75', 'p50', 'p25', 'p5', 'min']:
        ax.plot(days, df[col], color=colors[col], linewidth=linewidths[col])
    
    # Linea de corte
    ax.axvline(x=365, color='black', linewidth=2.5, linestyle='-', zorder=10)
    
    # Etiquetas
    x_label = 368
    last_day = df[df['day_of_year'] == 365].iloc[0]
    labels_data = [
        ('max', last_day['max'], 'MAX'),
        ('p95', last_day['p95'], '5%'),
        ('p75', last_day['p75'], '25%'),
        ('p50', last_day['p50'], '50%'),
        ('p25', last_day['p25'], '75%'),
        ('p5', last_day['p5'], '95%'),
        ('min', last_day['min'], 'MIN')
    ]
    
    for col, value, label in labels_data:
        ax.text(x_label, value, label, fontsize=11, fontweight='bold',
                color=colors[col], va='center', ha='left')
    
    # Ejes X (meses)
    month_days = [1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335]
    month_labels = ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN',
                    'JUL', 'AGO', 'SEP', 'OCT', 'NOV', 'DIC']
    
    ax.set_xlim(1, 365)
    ax.set_xticks(month_days)
    ax.set_xticklabels(month_labels, fontsize=11)
    
    # Grid
    ax.grid(True, alpha=0.3, which='both', linestyle='-', linewidth=0.5)
    ax.minorticks_on()
    ax.grid(True, alpha=0.15, which='minor', linestyle=':', linewidth=0.5)
    
    # Etiquetas
    ax.set_xlabel('Mes', fontsize=12, fontweight='bold')
    ax.set_ylabel('Cota (m)', fontsize=12, fontweight='bold')
    ax.set_title(f'Fig4. Curvas de Frecuencia de Niveles Excedidos - {estacion_nombre.upper()}',
                 fontsize=14, fontweight='bold', pad=20)
    
    # Limites Y
    y_min = df['min'].min() * 0.9
    y_max = df['max'].max() * 1.05
    ax.set_ylim(y_min, y_max)
    
    plt.tight_layout()
    plt.subplots_adjust(right=0.88)
    
    # Guardar figura
    output_file = estacion_dir / f'Fig4_Curvas_Excedidos_{estacion_key}.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f'  Figura: {output_file.name}')
    return True

def crear_script(estacion_nombre, estacion_key):
    """Crea el script para regenerar la figura"""
    
    script_content = f'''# -*- coding: utf-8 -*-
"""
Fig4 - Curvas de Frecuencia de Niveles Excedidos
{estacion_nombre} - Version con percentiles corregidos (sin 29-feb)
REGLA CRITICA: Excluir 29 de febrero completamente
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Rutas
PERCENTILES_PATH = r'C:\\Users\\alexa\\Documents\\PERSONAL PROJECTS\\MagdalenaBot\\cartillas_estaciones\\v4_2\\{estacion_key}\\Fig4_Percentiles_{estacion_key}.csv'
OUTPUT_DIR = r'C:\\Users\\alexa\\Documents\\PERSONAL PROJECTS\\MagdalenaBot\\cartillas_estaciones\\v4_2\\{estacion_key}'

# Leer percentiles
df = pd.read_csv(PERCENTILES_PATH)
print(f'Percentiles cargados: {{len(df)}} dias')

# Configuracion de la figura
fig, ax = plt.subplots(figsize=(14, 8))
days = df['day_of_year'].values

# Colores y grosores
colors = {{
    'max': 'black', 'p95': '#8B0000', 'p75': '#6B8E23',
    'p50': 'black', 'p25': '#5DADE2', 'p5': '#D35400', 'min': 'black'
}}
linewidths = {{
    'max': 1.2, 'p95': 1.2, 'p75': 1.2, 'p50': 2.5,
    'p25': 1.2, 'p5': 1.2, 'min': 1.2
}}

# Dibujar lineas de percentiles
for col in ['max', 'p95', 'p75', 'p50', 'p25', 'p5', 'min']:
    ax.plot(days, df[col], color=colors[col], linewidth=linewidths[col])

# Linea de corte vertical en dia 365
ax.axvline(x=365, color='black', linewidth=2.5, linestyle='-', zorder=10)

# Etiquetas fuera del bbox, alineadas con el dia 365
x_label = 368
last_day = df[df['day_of_year'] == 365].iloc[0]
labels_data = [
    ('max', last_day['max'], 'MAX'),
    ('p95', last_day['p95'], '5%'),
    ('p75', last_day['p75'], '25%'),
    ('p50', last_day['p50'], '50%'),
    ('p25', last_day['p25'], '75%'),
    ('p5', last_day['p5'], '95%'),
    ('min', last_day['min'], 'MIN')
]

for col, value, label in labels_data:
    ax.text(x_label, value, label, fontsize=11, fontweight='bold', 
            color=colors[col], va='center', ha='left')

# Configuracion de ejes X (meses)
month_days = [1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335]
month_labels = ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN', 
                'JUL', 'AGO', 'SEP', 'OCT', 'NOV', 'DIC']

ax.set_xlim(1, 365)
ax.set_xticks(month_days)
ax.set_xticklabels(month_labels, fontsize=11)

# Grid
ax.grid(True, alpha=0.3, which='both', linestyle='-', linewidth=0.5)
ax.minorticks_on()
ax.grid(True, alpha=0.15, which='minor', linestyle=':', linewidth=0.5)

# Etiquetas de ejes
ax.set_xlabel('Mes', fontsize=12, fontweight='bold')
ax.set_ylabel('Cota (m)', fontsize=12, fontweight='bold')
ax.set_title('Fig4. Curvas de Frecuencia de Niveles Excedidos - {estacion_nombre.upper()}', 
             fontsize=14, fontweight='bold', pad=20)

# Ajustar limites Y
y_min = df['min'].min() * 0.9
y_max = df['max'].max() * 1.05
ax.set_ylim(y_min, y_max)

plt.tight_layout()
plt.subplots_adjust(right=0.88)

# Guardar figura
output_file = Path(OUTPUT_DIR) / 'Fig4_Curvas_Excedidos_{estacion_key}.png'
plt.savefig(output_file, dpi=150, bbox_inches='tight')
print(f'Figura guardada: {{output_file}}')
plt.close()
'''
    
    estacion_dir = Path(BASE_DIR) / estacion_key
    estacion_dir.mkdir(parents=True, exist_ok=True)
    
    script_path = estacion_dir / f'generar_fig4_{estacion_key.lower()}.py'
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print(f'  Script: {script_path.name}')

print('='*70)
print('GENERANDO FIG4 PARA TODAS LAS ESTACIONES')
print('='*70)

for estacion_nombre, estacion_key in ESTACIONES:
    print(f'\n[{estacion_nombre}]')
    if generar_fig4(estacion_nombre, estacion_key):
        crear_script(estacion_nombre, estacion_key)

print('\n' + '='*70)
print('PROCESO COMPLETADO')
print('='*70)
