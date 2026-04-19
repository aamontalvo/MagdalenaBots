# -*- coding: utf-8 -*-
"""
Regenera Fig4 para todas las estaciones con margen fijo de +/- 2m en eje Y
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

BASE_DIR = Path(r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\cartillas_estaciones\v4_2')

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
    ('Calamar', 'CALAMAR'),
    ('San Pedrito', 'SAN_PEDRITO'),
]

def generar_fig4_corregido(estacion_nombre, estacion_key):
    """Genera Fig4 con margen fijo de +/- 2m"""
    
    csv_path = BASE_DIR / estacion_key / f'Fig4_Percentiles_{estacion_key}.csv'
    if not csv_path.exists():
        csv_path = BASE_DIR / estacion_key / f'Fig4_Percentiles_{estacion_key}_FINAL.csv'
    
    if not csv_path.exists():
        print(f'  [ERROR] No encontrado: {csv_path}')
        return False
    
    df = pd.read_csv(csv_path)
    
    fig, ax = plt.subplots(figsize=(14, 8))
    days = df['day_of_year'].values
    
    colors = {
        'max': 'black', 'p95': '#8B0000', 'p75': '#6B8E23',
        'p50': 'black', 'p25': '#5DADE2', 'p5': '#D35400', 'min': 'black'
    }
    linewidths = {
        'max': 1.2, 'p95': 1.2, 'p75': 1.2, 'p50': 2.5,
        'p25': 1.2, 'p5': 1.2, 'min': 1.2
    }
    
    for col in ['max', 'p95', 'p75', 'p50', 'p25', 'p5', 'min']:
        ax.plot(days, df[col], color=colors[col], linewidth=linewidths[col])
    
    ax.axvline(x=365, color='black', linewidth=2.5, linestyle='-', zorder=10)
    
    x_label = 368
    last_day = df[df['day_of_year'] == 365].iloc[0]
    labels_data = [
        ('max', last_day['max'], 'MAX'), ('p95', last_day['p95'], '5%'),
        ('p75', last_day['p75'], '25%'), ('p50', last_day['p50'], '50%'),
        ('p25', last_day['p25'], '75%'), ('p5', last_day['p5'], '95%'),
        ('min', last_day['min'], 'MIN')
    ]
    
    for col, value, label in labels_data:
        ax.text(x_label, value, label, fontsize=11, fontweight='bold',
                color=colors[col], va='center', ha='left')
    
    month_days = [1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335]
    month_labels = ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN',
                    'JUL', 'AGO', 'SEP', 'OCT', 'NOV', 'DIC']
    
    ax.set_xlim(1, 365)
    ax.set_xticks(month_days)
    ax.set_xticklabels(month_labels, fontsize=11)
    
    ax.grid(True, alpha=0.3, which='both', linestyle='-', linewidth=0.5)
    ax.minorticks_on()
    ax.grid(True, alpha=0.15, which='minor', linestyle=':', linewidth=0.5)
    
    ax.set_xlabel('Mes', fontsize=12, fontweight='bold')
    ax.set_ylabel('Cota (m)', fontsize=12, fontweight='bold')
    ax.set_title(f'Fig4. Curvas de Frecuencia de Niveles Excedidos - {estacion_nombre.upper()}',
                 fontsize=14, fontweight='bold', pad=20)
    
    # CORRECCION: Margen fijo de +/- 2m
    y_min = df['min'].min() - 2
    y_max = df['max'].max() + 2
    ax.set_ylim(y_min, y_max)
    
    plt.tight_layout()
    plt.subplots_adjust(right=0.88)
    
    output_file = BASE_DIR / estacion_key / f'Fig4_Curvas_Excedidos_{estacion_key}_v2.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f'  {estacion_nombre}: Y [{y_min:.1f}, {y_max:.1f}]')
    return True

print('='*70)
print('REGENERANDO FIG4 CON MARGEN FIJO +/- 2m')
print('='*70)

for nombre, key in ESTACIONES:
    generar_fig4_corregido(nombre, key)

print('\n' + '='*70)
print('COMPLETADO')
print('='*70)
