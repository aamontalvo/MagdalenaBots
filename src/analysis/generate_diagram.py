"""
Genera diagrama de flujo del Sistema de Imputación de Tres Niveles
Figura 5.1 para el informe técnico
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

fig, ax = plt.subplots(1, 1, figsize=(14, 16))
ax.set_xlim(0, 10)
ax.set_ylim(0, 20)
ax.axis('off')

# Colores
color_nivel1 = '#E3F2FD'  # Azul claro
color_nivel2 = '#E8F5E9'  # Verde claro
color_nivel3 = '#FFF3E0'  # Naranja claro
color_decision = '#FCE4EC'  # Rosa claro
color_inicio = '#E8EAF6'  # Lila claro

# Función para crear caja
def draw_box(ax, x, y, width, height, text, color, fontsize=10, text_color='black'):
    box = FancyBboxPatch((x - width/2, y - height/2), width, height,
                         boxstyle="round,pad=0.1", 
                         facecolor=color, edgecolor='black', linewidth=2)
    ax.add_patch(box)
    ax.text(x, y, text, ha='center', va='center', fontsize=fontsize,
            color=text_color, weight='bold', wrap=True)

# Función para crear diamante de decisión
def draw_diamond(ax, x, y, size, text, color):
    diamond = plt.Polygon([(x, y+size), (x+size*1.2, y), (x, y-size), (x-size*1.2, y)], 
                          facecolor=color, edgecolor='black', linewidth=2)
    ax.add_patch(diamond)
    ax.text(x, y, text, ha='center', va='center', fontsize=9, weight='bold')

# Función para dibujar flecha
def draw_arrow(ax, x1, y1, x2, y2, text='', color='black'):
    arrow = FancyArrowPatch((x1, y1), (x2, y2),
                           arrowstyle='->', mutation_scale=20,
                           linewidth=2, color=color)
    ax.add_patch(arrow)
    if text:
        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(mid_x + 0.3, mid_y, text, fontsize=9, 
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

# TÍTULO
ax.text(5, 19, 'SISTEMA DE IMPUTACIÓN DE DATOS FALTANTES - RÍO MAGDALENA', 
        ha='center', va='center', fontsize=16, weight='bold')
ax.text(5, 18.3, 'Estrategia de Tres Niveles con Criterio de Calidad R² ≥ 0.75', 
        ha='center', va='center', fontsize=12, style='italic')

# NIVEL 1: INTERPOLACIÓN LOCAL
ax.text(1.5, 17, 'NIVEL 1', fontsize=14, weight='bold', color='#1565C0')
ax.text(1.5, 16.5, 'Gaps ≤ 3 días', fontsize=10, style='italic')

draw_box(ax, 5, 16, 4, 1, 'Datos Faltantes\nIdentificación de gaps', color_inicio, 10)

draw_diamond(ax, 5, 14.5, 0.6, 'Gap ≤ 3\ndías?', color_decision)

draw_box(ax, 2.5, 14.5, 2.5, 1, 'NIVEL 1\nInterpolación Local\nMedia móvil ponderada', color_nivel1, 9)

ax.text(2.5, 13.5, 'Pesos: [0.1, 0.2, 0.4, 0.2, 0.1]', fontsize=8, ha='center')

# NIVEL 2: CURVAS H-H
ax.text(1.5, 11.5, 'NIVEL 2', fontsize=14, weight='bold', color='#2E7D32')
ax.text(1.5, 11, 'Curvas Altura-Altura', fontsize=10, style='italic')

draw_diamond(ax, 5, 12.5, 0.6, 'Gap > 3\ndías?', color_decision)

draw_box(ax, 5, 10.5, 3.5, 1, 'Buscar mejor estación donante\nr ≥ 0.85', color_inicio, 9)

draw_diamond(ax, 5, 9, 0.6, '¿Donante\ndisponible?', color_decision)

draw_box(ax, 2, 9, 2.5, 1, 'NIVEL 2\nCurvas H-H\nLineal vs Cuadrático', color_nivel2, 9)

draw_diamond(ax, 2, 7.5, 0.5, 'R² ≥ 0.75?', color_decision)

draw_box(ax, 2, 6, 2.5, 0.8, 'IMPUTACIÓN\nACEPTADA', '#C8E6C9', 9)

ax.text(2, 5.2, 'Modelo óptimo aplicado\nGap completado', fontsize=8, ha='center')

# NIVEL 3: MULTI-DONANTE
ax.text(8, 11.5, 'NIVEL 3', fontsize=14, weight='bold', color='#E65100')
ax.text(8, 11, 'Multi-donante', fontsize=10, style='italic')

draw_box(ax, 8, 9, 2.5, 1, 'NIVEL 3\nMulti-donante\nHasta 5 estaciones', color_nivel3, 9)

draw_diamond(ax, 8, 7.5, 0.5, 'R² ≥ 0.75?', color_decision)

draw_box(ax, 8, 6, 2.5, 0.8, 'IMPUTACIÓN\nACEPTADA', '#FFCC80', 9)

# RECHAZOS
draw_box(ax, 5, 7.5, 2.2, 0.8, 'SIN IMPUTACIÓN\nDatos faltantes', '#FFCDD2', 9)
ax.text(5, 6.7, '(R² < 0.75)', fontsize=8, ha='center', color='#C62828')

# Flechas
draw_arrow(ax, 5, 15.5, 5, 15.1)  # Inicio a decisión gap
draw_arrow(ax, 4.4, 14.5, 3.25, 14.5, 'Sí')  # Gap <=3 a Nivel 1
draw_arrow(ax, 5, 13.9, 5, 11)  # Gap >3 a buscar donante
draw_arrow(ax, 5, 10, 4.4, 9.6, 'Sí')  # Donante disponible a Nivel 2
draw_arrow(ax, 5.6, 9.3, 7.5, 9, 'No')  # No hay donante a Nivel 3
draw_arrow(ax, 2, 8.5, 2, 8)  # Nivel 2 a decisión R2
draw_arrow(ax, 2, 7, 2, 6.4, 'Sí')  # R2 OK a imputación aceptada
draw_arrow(ax, 2.5, 7.5, 4.5, 7.5, 'No')  # R2 no OK a sin imputación
draw_arrow(ax, 8, 8.5, 8, 8)  # Nivel 3 a decisión R2
draw_arrow(ax, 8, 7, 8, 6.4, 'Sí')  # R2 OK a imputación aceptada
draw_arrow(ax, 7.5, 7.5, 5.5, 7.5, 'No')  # R2 no OK a sin imputación

# Resultados finales
ax.text(5, 3.5, 'RESULTADOS DEL SISTEMA', ha='center', fontsize=13, weight='bold')

resultados = [
    ('Nivel 1:', '970 valores', '#1565C0'),
    ('Nivel 2:', '38,641 valores', '#2E7D32'),
    ('Sin imputar:', 'Armenia, San Pedrito', '#C62828'),
]

y_pos = 2.5
for label, value, color in resultados:
    ax.text(3.5, y_pos, label, fontsize=10, weight='bold', color=color)
    ax.text(5.5, y_pos, value, fontsize=10)
    y_pos -= 0.5

# Leyenda de criterios
ax.text(5, 0.5, 'Criterio de calidad: R² ≥ 0.75 para aceptar imputación | Correlación mínima r ≥ 0.85 para donantes', 
        ha='center', fontsize=9, style='italic',
        bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.5))

plt.tight_layout()
plt.savefig(r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\informes\imputacion\Figura_5_1_Esquema_Imputacion.png', 
            dpi=300, bbox_inches='tight', facecolor='white')
plt.close()

print("Figura 5.1 generada exitosamente")
