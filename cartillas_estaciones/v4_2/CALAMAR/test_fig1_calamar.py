# -*- coding: utf-8 -*-
"""
Fig1 - Serie de Tiempo - CALAMAR (Version de prueba)
Cambio: Eje X muestra solo anos en 1 de enero, con intervalo dinamico
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import matplotlib.dates as mdates

# Datos
DATA_PATH = r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\Informes\imputacion\Datos_Imputados_v4_2_Complete.csv'
OUTPUT_DIR = r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\cartillas_estaciones\v4_2\CALAMAR'

# Cargar datos
df = pd.read_csv(DATA_PATH)
df_calamar = df[df['NombreEstacion'] == 'Calamar'].copy()
df_calamar['Fecha'] = pd.to_datetime(df_calamar['Fecha'], format='%d-%m-%Y')
df_calamar = df_calamar.sort_values('Fecha')

# Calcular duracion de la serie para determinar intervalo
fecha_inicio = df_calamar['Fecha'].min()
fecha_fin = df_calamar['Fecha'].max()
duracion_anos = fecha_fin.year - fecha_inicio.year

print(f'Calamar: {fecha_inicio.year} - {fecha_fin.year} ({duracion_anos} anos)')

# Determinar intervalo de anos segun duracion
if duracion_anos <= 10:
    intervalo = 2  # Cada 2 anos para series cortas
elif duracion_anos <= 30:
    intervalo = 5  # Cada 5 anos para series medianas
else:
    intervalo = 10  # Cada 10 anos para series largas

print(f'Intervalo seleccionado: {intervalo} anos')

# Crear figura
fig, ax = plt.subplots(figsize=(14, 6))

# Graficar serie de tiempo
ax.plot(df_calamar['Fecha'], df_calamar['Cota'], color='black', linewidth=1)

# Configurar eje X: solo anos, en 1 de enero
# Crear ticks en 1 de enero de cada intervalo
ticks = []
tick_labels = []
for year in range(fecha_inicio.year, fecha_fin.year + 1, intervalo):
    tick_date = pd.Timestamp(f'{year}-01-01')
    if tick_date >= fecha_inicio and tick_date <= fecha_fin:
        ticks.append(tick_date)
        tick_labels.append(str(year))

# Asegurar que el ultimo ano esta incluido
if fecha_fin.year not in [t.year for t in ticks]:
    ticks.append(pd.Timestamp(f'{fecha_fin.year}-01-01'))
    tick_labels.append(str(fecha_fin.year))

ax.set_xticks(ticks)
ax.set_xticklabels(tick_labels, rotation=0, ha='center')

# Configuracion de ejes
ax.set_xlabel('Fecha', fontsize=12)
ax.set_ylabel('Cota (m)', fontsize=12)
ax.set_title('Serie de Tiempo - CALAMAR', fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.3)

# Anotacion con estadisticas
total_reg = len(df_calamar)
orig_reg = len(df_calamar[df_calamar['Metodo'] == 'Original'])
pct_orig = (orig_reg / total_reg) * 100

info_text = f'Periodo: {fecha_inicio.year}-{fecha_fin.year}\n'
info_text += f'Total: {total_reg:,} registros\n'
info_text += f'Original: {pct_orig:.1f}%'

ax.text(0.02, 0.98, info_text, transform=ax.transAxes, 
        fontsize=10, verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.tight_layout()

# Guardar
output_file = Path(OUTPUT_DIR) / 'Fig1_Serie_Tiempo_CALAMAR_TEST.png'
plt.savefig(output_file, dpi=150, bbox_inches='tight')
print(f'Figura guardada: {output_file}')

plt.close()
print('Prueba completada. Revisar figuras generadas.')
