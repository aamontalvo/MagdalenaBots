# -*- coding: utf-8 -*-
"""
Fig3 - Curva de Duracion - CALAMAR (Version corregida)
Cambios: 
- Safe zone en eje X (padding en 0 y 100)
- Anotaciones en bottom-left
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Datos
DATA_PATH = r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\Informes\imputacion\Datos_Imputados_v4_2_Complete.csv'
OUTPUT_DIR = r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\cartillas_estaciones\v4_2\CALAMAR'

# Cargar datos
df = pd.read_csv(DATA_PATH)
df_calamar = df[df['NombreEstacion'] == 'Calamar'].copy()
df_calamar['Fecha'] = pd.to_datetime(df_calamar['Fecha'], format='%d-%m-%Y')

# Filtrar valores validos
valores = df_calamar['Cota'].dropna().sort_values(ascending=False).values
n = len(valores)

# Calcular percentiles (curva de duracion)
percentiles = np.arange(1, n+1) / n * 100  # 0-100%

# Crear figura
fig, ax = plt.subplots(figsize=(10, 7))

# Curva principal
ax.plot(percentiles, valores, color='#1f77b4', linewidth=2)

# Funcion para encontrar valor mas cercano a un percentil
def encontrar_percentil(pct):
    idx = int(pct * n / 100)
    idx = max(0, min(idx, n-1))  # Asegurar rango valido
    return percentiles[idx], valores[idx]

# Puntos a marcar (P50, P90, P95, P100)
puntos_marcar = [50, 90, 95, 100]

for p in puntos_marcar:
    x_val, y_val = encontrar_percentil(p)
    # Marcador: circulo blanco con borde negro
    ax.plot(x_val, y_val, 'o', color='white', markeredgecolor='black', 
            markersize=10, markeredgewidth=1.5, zorder=5)
    
    # Anotacion en BOTTOM-LEFT (cambio principal)
    ax.annotate(f'P{p}: {y_val:.2f} m', 
                xy=(x_val, y_val),
                xytext=(-15, -15),  # Offset a bottom-left
                textcoords='offset points',
                fontsize=11, 
                fontweight='bold',
                ha='right',      # Alineacion derecha (hacia la izquierda del punto)
                va='top',        # Alineacion arriba (hacia abajo del punto)
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.9, edgecolor='gray'))

# Configuracion de ejes
ax.set_xlabel('Porcentaje de tiempo excedido (%)', fontsize=12)
ax.set_ylabel('Cota (m.s.n.m.)', fontsize=12)
ax.set_title('Curva de Duracion - CALAMAR', fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.3)

# SAFE ZONE: Margen en eje X para que 0 y 100 no toquen el borde
ax.set_xlim(-5, 105)  # Padding de 5% en ambos lados

plt.tight_layout()

# Guardar
output_file = Path(OUTPUT_DIR) / 'Fig3_Curva_Duracion_CALAMAR_TEST_v2.png'
plt.savefig(output_file, dpi=150, bbox_inches='tight')
print(f'Figura guardada: {output_file}')

plt.close()
print('Correcciones aplicadas:')
print('  - Safe zone en eje X (-5 a 105)')
print('  - Anotaciones en bottom-left')
