# -*- coding: utf-8 -*-
"""
Fig1 - Serie de Tiempo - CALAMAR (Version corregida)
Cambios:
- Usar datos v4.2 completos (no raw)
- Ticks cada 5 años
- Minor ticks incluidos
- Iniciar en año de inicio de serie
- Terminar en año de fin de serie
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import matplotlib.dates as mdates

# Datos v4.2 COMPLETOS (con imputacion)
DATA_PATH = r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\Informes\imputacion\Datos_Imputados_v4_2_Complete.csv'
OUTPUT_DIR = r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\cartillas_estaciones\v4_2\CALAMAR'

# Cargar datos v4.2
df = pd.read_csv(DATA_PATH)
df_calamar = df[df['NombreEstacion'] == 'Calamar'].copy()
df_calamar['Fecha'] = pd.to_datetime(df_calamar['Fecha'], format='%d-%m-%Y')
df_calamar = df_calamar.sort_values('Fecha')

# Calcular duracion de la serie
fecha_inicio = df_calamar['Fecha'].min()
fecha_fin = df_calamar['Fecha'].max()
start_year = fecha_inicio.year
end_year = fecha_fin.year

print(f'Calamar v4.2: {start_year} - {end_year}')
print(f'Total registros: {len(df_calamar)}')

# Crear figura
fig, ax = plt.subplots(figsize=(14, 6))

# Graficar serie de tiempo (datos v4.2 completos)
ax.plot(df_calamar['Fecha'], df_calamar['Cota'], color='black', linewidth=0.8)

# Configurar eje X: ticks cada 5 años, iniciando en start_year y terminando en end_year
ticks = []
tick_labels = []

# Generar ticks cada 5 años desde el año de inicio
for year in range(start_year, end_year + 1, 5):
    tick_date = pd.Timestamp(f'{year}-01-01')
    ticks.append(tick_date)
    tick_labels.append(str(year))

# Asegurar que el ultimo año (end_year) este incluido
if end_year not in [t.year for t in ticks]:
    ticks.append(pd.Timestamp(f'{end_year}-01-01'))
    tick_labels.append(str(end_year))

ax.set_xticks(ticks)
ax.set_xticklabels(tick_labels, rotation=0, ha='center')

# Ticks secundarios (minor) cada año
ax.xaxis.set_minor_locator(mdates.YearLocator())

# Configuracion de ejes
ax.set_xlabel('Fecha', fontsize=12)
ax.set_ylabel('Cota (m)', fontsize=12)
ax.set_title('Serie de Tiempo - CALAMAR (Datos v4.2)', fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.3, which='major')
ax.grid(True, alpha=0.15, which='minor', linestyle=':')

# Anotacion con estadisticas
total_reg = len(df_calamar)
orig_reg = len(df_calamar[df_calamar['Metodo'] == 'Original'])
imp_reg = total_reg - orig_reg
pct_orig = (orig_reg / total_reg) * 100
pct_imp = (imp_reg / total_reg) * 100

info_text = f'Periodo: {start_year}-{end_year}\n'
info_text += f'Total: {total_reg:,} registros\n'
info_text += f'Original: {pct_orig:.1f}% | Imputado: {pct_imp:.1f}%'

ax.text(0.02, 0.98, info_text, transform=ax.transAxes, 
        fontsize=10, verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.tight_layout()

# Guardar
output_file = Path(OUTPUT_DIR) / 'Fig1_Serie_Tiempo_CALAMAR_TEST_v2.png'
plt.savefig(output_file, dpi=150, bbox_inches='tight')
print(f'Figura guardada: {output_file}')

plt.close()
print('Correcciones aplicadas:')
print(f'  - Datos v4.2 completos (no raw)')
print(f'  - Ticks cada 5 años ({start_year}, {start_year+5}, ..., {end_year})')
print(f'  - Minor ticks cada año')
print(f'  - Inicio: {start_year}, Fin: {end_year}')
