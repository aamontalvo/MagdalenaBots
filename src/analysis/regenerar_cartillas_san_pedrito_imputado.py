"""
Regenerar cartillas de San Pedrito con datos imputados v4_2 actualizados.
Genera Fig1-5 en la carpeta v4_2/SAN_PEDRITO
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Configuracion
V4_2_PATH = Path(r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\backend\data\processed\imputation\Datos_Imputados_v4_2_Complete.csv')
OUTPUT_DIR = Path(r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\cartillas_estaciones\v4_2\SAN_PEDRITO')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Cargar datos imputados
df = pd.read_csv(V4_2_PATH)
df['Fecha'] = pd.to_datetime(df['Fecha'], format='%d-%m-%Y')

# Filtrar San Pedrito
sp = df[df['NombreEstacion'] == 'San Pedrito'].copy().sort_values('Fecha').reset_index(drop=True)
sp['year'] = sp['Fecha'].dt.year
sp['month'] = sp['Fecha'].dt.month
sp['day'] = sp['Fecha'].dt.day
sp['dia_anio'] = sp['Fecha'].dt.dayofyear

print(f"San Pedrito imputado: {len(sp):,} registros")
print(f"  Original: {(sp['Nivel_Imputacion'] == 0).sum():,}")
print(f"  L1: {(sp['Nivel_Imputacion'] == 1).sum():,}")
print(f"  H-H: {(sp['Nivel_Imputacion'] == 2).sum():,}")
print(f"  Cobertura: {100 * sp['Cota'].notna().sum() / len(sp):.2f}%")

# Separar original vs imputado
original = sp[sp['Nivel_Imputacion'] == 0].copy()
imputado = sp[sp['Nivel_Imputacion'] > 0].copy()

# =============================================================================
# FIGURA 1: Serie de Tiempo
# =============================================================================
print("\nGenerando Fig1 - Serie de Tiempo...")
fig, ax = plt.subplots(figsize=(14, 6))

# Datos originales en negro
ax.plot(original['Fecha'], original['Cota'], 'k-', linewidth=0.8, alpha=0.85, label='Original')
# Datos imputados en rojo
ax.plot(imputado['Fecha'], imputado['Cota'], 'r-', linewidth=0.8, alpha=0.6, label='Imputado')

total_valid = len(sp)
original_count = len(original)
imputed_count = len(imputado)
pct_original = (original_count / total_valid) * 100
pct_imputed = (imputed_count / total_valid) * 100
year_start = int(sp['year'].min())
year_end = int(sp['year'].max())

annotation = (f'Periodo: {year_start}-{year_end}\n'
              f'Total: {total_valid:,} registros\n'
              f'Medidos: {pct_original:.1f}% | Imputados: {pct_imputed:.1f}%')
ax.text(0.02, 0.98, annotation, transform=ax.transAxes, fontsize=10,
        verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.9))

ax.set_title('Serie de Tiempo de Cotas - San Pedrito (v4.2 Imputado)', fontsize=13, fontweight='bold')
ax.set_xlabel('Fecha', fontsize=11)
ax.set_ylabel('Cota (m.s.n.m.)', fontsize=11)
ax.grid(True, alpha=0.3)
ax.legend(loc='upper right')
ax.xaxis.set_major_locator(plt.MaxNLocator(10))
fig.autofmt_xdate()
plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'Fig1_Serie_Tiempo_San Pedrito.png', dpi=200, bbox_inches='tight', facecolor='white')
plt.close()

# =============================================================================
# FIGURA 2: Violin Mensual (solo datos originales)
# =============================================================================
print("Generando Fig2 - Violin Mensual...")
fig, ax = plt.subplots(figsize=(14, 6))
data_by_month = []
positions = []
for month in range(1, 13):
    month_data = original[original['month'] == month]['Cota'].dropna()
    if len(month_data) > 0:
        data_by_month.append(month_data.values)
        positions.append(month)

parts = ax.violinplot(data_by_month, positions=positions, widths=0.7,
                      showmeans=True, showmedians=True, showextrema=True)
for pc in parts['bodies']:
    pc.set_facecolor('#D3D3D3')
    pc.set_edgecolor('black')
    pc.set_alpha(0.7)
parts['cmeans'].set_color('red')
parts['cmedians'].set_color('black')
parts['cmedians'].set_linewidth(2)

ax.set_xticks(range(1, 13))
ax.set_xticklabels(['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN', 'JUL', 'AGO', 'SEP', 'OCT', 'NOV', 'DIC'])
ax.set_xlabel('Mes', fontsize=11)
ax.set_ylabel('Cota (m.s.n.m.)', fontsize=11)
ax.set_title('Comportamiento Mensual Multianual - San Pedrito (Datos Originales)', fontsize=13, fontweight='bold')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'Fig2_Violin_Mensual_San Pedrito.png', dpi=200, bbox_inches='tight', facecolor='white')
plt.close()

# =============================================================================
# FIGURA 3: Curva de Duracion
# =============================================================================
print("Generando Fig3 - Curva de Duracion...")
valid_levels = sp['Cota'].dropna().sort_values(ascending=False).values
n = len(valid_levels)
exceedance = np.arange(1, n + 1) / n * 100
fig, ax = plt.subplots(figsize=(10, 7))
ax.plot(exceedance, valid_levels, color='#1f77b4', linewidth=2.5)
for p in [50, 90, 95, 100]:
    idx = int(np.ceil(n * p / 100)) - 1
    idx = max(0, min(idx, n - 1))
    val = valid_levels[idx]
    ax.plot(exceedance[idx], val, 'o', markersize=10, markerfacecolor='white',
            markeredgecolor='black', markeredgewidth=1.5)
    ax.annotate(f'P{p}: {val:.2f} m', xy=(exceedance[idx], val),
                xytext=(10, 10), textcoords='offset points', fontsize=10, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='gray', alpha=0.8))
ax.set_xlabel('Porcentaje de tiempo excedido (%)', fontsize=11)
ax.set_ylabel('Cota (m.s.n.m.)', fontsize=11)
ax.set_title('Curva de Duracion - San Pedrito (Serie Completa Imputada)', fontsize=13, fontweight='bold')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'Fig3_Curva_Duracion_San Pedrito.png', dpi=200, bbox_inches='tight', facecolor='white')
plt.close()

# =============================================================================
# FIGURA 4: Curvas de Frecuencia / Excedidos
# =============================================================================
print("Generando Fig4 - Curvas de Frecuencia...")
sp_no_leap = sp[~((sp['month'] == 2) & (sp['day'] == 29))].copy()
sp_no_leap['dia_anio'] = sp_no_leap['Fecha'].dt.dayofyear
percentiles = [5, 25, 50, 75, 95]
colors = {'max': 'black', 'min': 'black', 5: '#8B0000', 25: '#6B8E23', 50: 'black', 75: '#5DADE2', 95: '#D35400'}
fig, ax = plt.subplots(figsize=(14, 8))
for p in ['max', 'min'] + percentiles:
    if p == 'max':
        vals = sp_no_leap.groupby('dia_anio')['Cota'].max()
    elif p == 'min':
        vals = sp_no_leap.groupby('dia_anio')['Cota'].min()
    else:
        vals = sp_no_leap.groupby('dia_anio')['Cota'].quantile(p / 100)
    x = vals.index.values
    y = vals.values
    color = colors.get(p, 'gray')
    lw = 3 if p == 50 else 1.5
    ax.plot(x, y, color=color, linewidth=lw, label=f'{p}%')
    ax.text(x[-1] + 5, y[-1], f'{p}%', fontsize=9, va='center')

ax.set_xlim(0, 370)
ax.set_xlabel('Dia del Anio', fontsize=11)
ax.set_ylabel('Cota (m.s.n.m.)', fontsize=11)
ax.set_title('Curvas de Frecuencia de Niveles Excedidos - San Pedrito (Serie Completa)', fontsize=13, fontweight='bold')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'Fig4_Curvas_Excedidos_SAN_PEDRITO_v2.png', dpi=200, bbox_inches='tight', facecolor='white')
plt.close()

# =============================================================================
# FIGURA 5: Ajuste de Distribuciones
# =============================================================================
print("Generando Fig5 - Ajuste de Distribuciones...")
original_levels = original['Cota'].dropna().values
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
ax1 = axes[0]
count, bins, patches = ax1.hist(original_levels, bins=50, density=True, color='lightgray', edgecolor='gray', alpha=0.7)
mu, sigma = stats.norm.fit(original_levels)
shape, loc, scale = stats.pearson3.fit(original_levels)
c, loc_w, scale_w = stats.weibull_min.fit(original_levels)
x_pdf = np.linspace(original_levels.min(), original_levels.max(), 200)
ax1.plot(x_pdf, stats.norm.pdf(x_pdf, mu, sigma), 'k-', linewidth=1.5, label='Normal')
ax1.plot(x_pdf, stats.pearson3.pdf(x_pdf, shape, loc=loc, scale=scale), 'k--', linewidth=1.5, label='Pearson III')
ax1.plot(x_pdf, stats.weibull_min.pdf(x_pdf, c, loc=loc_w, scale=scale_w), 'k:', linewidth=1.5, label='Weibull')
ax1.set_xlabel('Cota (m.s.n.m.)', fontsize=11)
ax1.set_ylabel('Densidad de probabilidad', fontsize=11)
ax1.set_title('Histograma y Ajuste de Distribuciones', fontsize=12, fontweight='bold')
ax1.legend()
ax1.grid(True, alpha=0.3)
ax2 = axes[1]
stats.probplot(original_levels, dist=stats.norm, plot=ax2)
ax2.get_lines()[0].set_markerfacecolor('gray')
ax2.get_lines()[0].set_markeredgecolor('none')
ax2.get_lines()[0].set_alpha(0.5)
ax2.get_lines()[1].set_color('black')
ax2.set_title('Q-Q Plot vs Normal', fontsize=12, fontweight='bold')
ax2.grid(True, alpha=0.3)
plt.suptitle('Ajuste de Distribuciones de Probabilidad - San Pedrito', fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'Fig5_Ajuste_Distribuciones_SAN_PEDRITO.png', dpi=200, bbox_inches='tight', facecolor='white')
plt.close()

print(f"\nCartillas guardadas en: {OUTPUT_DIR}")
print("PROCESO COMPLETADO")
