"""
Reconstruccion completa de San Pedrito con datos hasta 2026-02-09
Combina:
  - Hoja 'Columnas SAN_PEDRITO' para 1979-2003
  - Hoja 'Crudos' para 2004-2026
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from scipy.stats import pearsonr
import warnings
warnings.filterwarnings('ignore')

RAW_DIR = Path(r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\backend\data\raw\SERIE NIVELES IDEAM A 2026')
V3_PATH = Path(r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\cartillas_estaciones\datos\processed\Datos_Imputados_v3.csv')
OUTPUT_CARTILLAS = Path(r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\cartillas_estaciones\v4_2\SAN_PEDRITO')
OUTPUT_HH = Path(r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\Informes\imputacion\Curvas_HH_v4_2')

# =============================================================================
# PASO 1: Leer ambas hojas y combinar
# =============================================================================
print("=" * 70)
print("PASO 1: Leyendo datos de San Pedrito de ambas hojas")
print("=" * 70)

filepath = RAW_DIR / 'SAN_PEDRITO_-_AUT_29047070.xlsx'

# Hoja 1: Columnas SAN_PEDRITO (1979-2019, formato wide)
print("  Leyendo 'Columnas SAN_PEDRITO'...")
df_wide = pd.read_excel(filepath, sheet_name='Columnas SAN_PEDRITO')
year_cols = [c for c in df_wide.columns if isinstance(c, (int, float)) and 1900 <= c <= 2100]

records_wide = []
for year in year_cols:
    for _, row in df_wide.iterrows():
        try:
            val = float(row.iloc[0])
            month = int(val)
            day = int(round((val - month) * 100))
            if month == 2 and day == 29:
                if not (int(year) % 4 == 0 and (int(year) % 100 != 0 or int(year) % 400 == 0)):
                    continue
            date = pd.Timestamp(year=int(year), month=month, day=day)
            level = float(row[year]) if pd.notna(row[year]) else np.nan
            records_wide.append({'date': date, 'level': level, 'source': 'wide'})
        except:
            continue

df_sp_wide = pd.DataFrame(records_wide).sort_values('date').reset_index(drop=True)
print(f"    Registros: {len(df_sp_wide)} | Validos: {df_sp_wide['level'].notna().sum()} | Rango: {df_sp_wide['date'].min().date()} a {df_sp_wide['date'].max().date()}")

# Hoja 2: Crudos (2004-2026, formato long)
print("  Leyendo 'Crudos'...")
df_crudos = pd.read_excel(filepath, sheet_name='Crudos')
df_crudos['fecha'] = pd.to_datetime(df_crudos['fecha'], errors='coerce')
df_crudos = df_crudos.rename(columns={'cota nivel (m.s.n.m)': 'level', 'fecha': 'date'})
df_crudos = df_crudos[['date', 'level']].copy()
df_crudos['source'] = 'crudos'
df_crudos = df_crudos.sort_values('date').reset_index(drop=True)
print(f"    Registros: {len(df_crudos)} | Validos: {df_crudos['level'].notna().sum()} | Rango: {df_crudos['date'].min().date()} a {df_crudos['date'].max().date()}")

# Combinar: usar wide para 1979-2003, crudos para 2004-2026
print("  Combinando fuentes...")
cutoff_date = pd.Timestamp('2004-12-04')

sp_wide_early = df_sp_wide[df_sp_wide['date'] < cutoff_date].copy()
sp_crudos_late = df_crudos[df_crudos['date'] >= cutoff_date].copy()

# Verificar solapamiento
sp_wide_overlap = df_sp_wide[(df_sp_wide['date'] >= cutoff_date) & (df_sp_wide['date'] <= '2019-12-31')]
print(f"    Datos wide 1979-2003: {len(sp_wide_early)} registros ({sp_wide_early['level'].notna().sum()} validos)")
print(f"    Datos crudos 2004-2026: {len(sp_crudos_late)} registros ({sp_crudos_late['level'].notna().sum()} validos)")
print(f"    Solapamiento wide 2004-2019: {len(sp_wide_overlap)} registros ({sp_wide_overlap['level'].notna().sum()} validos)")

# Concatenar
sp_combined = pd.concat([sp_wide_early[['date', 'level']], sp_crudos_late[['date', 'level']]], ignore_index=True)
sp_combined = sp_combined.sort_values('date').reset_index(drop=True)
print(f"\n  DATASET COMBINADO:")
print(f"    Total registros: {len(sp_combined)}")
print(f"    Validos: {sp_combined['level'].notna().sum()}")
print(f"    Missing: {sp_combined['level'].isna().sum()}")
print(f"    Rango: {sp_combined['date'].min().date()} a {sp_combined['date'].max().date()}")

# =============================================================================
# PASO 2: Actualizar Datos_Imputados_v3.csv
# =============================================================================
print("\n" + "=" * 70)
print("PASO 2: Actualizando Datos_Imputados_v3.csv")
print("=" * 70)

v3 = pd.read_csv(V3_PATH)
v3['date'] = pd.to_datetime(v3['date'])
print(f"  V3 actual: {len(v3)} registros")

v3_no_sp = v3[v3['station'] != 'SAN_PEDRITO'].copy()
print(f"  Sin SP: {len(v3_no_sp)} registros")

# Crear San Pedrito en formato v3
sp_v3 = pd.DataFrame()
sp_v3['date'] = sp_combined['date']
sp_v3['year'] = sp_v3['date'].dt.year
sp_v3['month'] = sp_v3['date'].dt.month
sp_v3['day'] = sp_v3['date'].dt.day
sp_v3['station'] = 'SAN_PEDRITO'
sp_v3['level'] = sp_combined['level']
sp_v3['data_source'] = np.where(sp_combined['level'].notna(), 'original', 'missing')
sp_v3['level_original'] = sp_combined['level']
sp_v3['imputed_local'] = np.nan
sp_v3['is_null'] = sp_combined['level'].isna()

gap_counter = 0
current_gap = 0
gap_ids = []
for is_null in sp_v3['is_null']:
    if is_null:
        if current_gap == 0:
            gap_counter += 1
            current_gap = gap_counter
        gap_ids.append(current_gap)
    else:
        current_gap = 0
        gap_ids.append(0)
sp_v3['gap_id'] = gap_ids
sp_v3['donor_station'] = np.nan

v3_new = pd.concat([v3_no_sp, sp_v3], ignore_index=True)
v3_new = v3_new.sort_values(['station', 'date']).reset_index(drop=True)
print(f"  V3 nuevo: {len(v3_new)} registros")

backup_dir = V3_PATH.parent / 'backups'
backup_dir.mkdir(exist_ok=True)
v3.to_csv(backup_dir / 'Datos_Imputados_v3_backup_pre_sanpedrito_completo.csv', index=False, encoding='utf-8-sig')
v3_new.to_csv(V3_PATH, index=False, encoding='utf-8-sig')
print(f"  Guardado: {V3_PATH}")

# =============================================================================
# PASO 3: Regenerar cartillas
# =============================================================================
print("\n" + "=" * 70)
print("PASO 3: Regenerando cartillas de San Pedrito")
print("=" * 70)

OUTPUT_CARTILLAS.mkdir(parents=True, exist_ok=True)
v3 = pd.read_csv(V3_PATH)
v3['date'] = pd.to_datetime(v3['date'])
sp_df = v3[v3['station'] == 'SAN_PEDRITO'].copy().sort_values('date')

# Fig1: Serie de Tiempo
print("  Fig1 - Serie de Tiempo...")
fig, ax = plt.subplots(figsize=(14, 6))
valid_data = sp_df[sp_df['level'].notna()]
ax.plot(valid_data['date'], valid_data['level'], 'k-', linewidth=0.8, alpha=0.85)

total_valid = len(valid_data)
original_count = (sp_df['data_source'] == 'original').sum()
imputed_count = total_valid - original_count
pct_original = (original_count / total_valid) * 100 if total_valid > 0 else 0
pct_imputed = (imputed_count / total_valid) * 100 if total_valid > 0 else 0
year_start = int(sp_df['year'].min())
year_end = int(sp_df['year'].max())

annotation = (f'Periodo: {year_start}-{year_end} Total: {total_valid:,} registros\n'
              f'Medidos: {pct_original:.1f}% | Imputados: {pct_imputed:.1f}%')
ax.text(0.02, 0.98, annotation, transform=ax.transAxes, fontsize=10,
        verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.9))
ax.set_title('Serie de Tiempo de Cotas - San Pedrito', fontsize=13, fontweight='bold')
ax.set_xlabel('Fecha', fontsize=11)
ax.set_ylabel('Cota (m.s.n.m.)', fontsize=11)
ax.grid(True, alpha=0.3)
ax.xaxis.set_major_locator(plt.MaxNLocator(10))
fig.autofmt_xdate()
plt.tight_layout()
plt.savefig(OUTPUT_CARTILLAS / 'Fig1_Serie_Tiempo_San Pedrito.png', dpi=200, bbox_inches='tight', facecolor='white')
plt.close()

# Fig2: Violin Mensual
print("  Fig2 - Violin Mensual...")
original = sp_df[sp_df['data_source'] == 'original'].copy()
fig, ax = plt.subplots(figsize=(14, 6))
data_by_month = []
positions = []
for month in range(1, 13):
    month_data = original[original['month'] == month]['level'].dropna()
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
ax.set_xticklabels(['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN',
                    'JUL', 'AGO', 'SEP', 'OCT', 'NOV', 'DIC'])
ax.set_xlabel('Mes', fontsize=11)
ax.set_ylabel('Cota (m.s.n.m.)', fontsize=11)
ax.set_title('Comportamiento Mensual Multianual - San Pedrito', fontsize=13, fontweight='bold')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(OUTPUT_CARTILLAS / 'Fig2_Violin_Mensual_San Pedrito.png', dpi=200, bbox_inches='tight', facecolor='white')
plt.close()

# Fig3: Curva de Duracion
print("  Fig3 - Curva de Duracion...")
valid_levels = sp_df['level'].dropna().sort_values(ascending=False).values
n = len(valid_levels)
exceedance = np.arange(1, n + 1) / n * 100
fig, ax = plt.subplots(figsize=(10, 7))
ax.plot(exceedance, valid_levels, color='#1f77b4', linewidth=2.5)
percentiles = [50, 90, 95, 100]
for p in percentiles:
    idx = int(np.ceil(n * p / 100)) - 1
    idx = max(0, min(idx, n - 1))
    val = valid_levels[idx]
    ax.plot(exceedance[idx], val, 'o', markersize=10, markerfacecolor='white',
            markeredgecolor='black', markeredgewidth=1.5)
    ax.annotate(f'P{p}: {val:.2f} m', xy=(exceedance[idx], val),
                xytext=(10, 10), textcoords='offset points',
                fontsize=10, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='gray', alpha=0.8))
ax.set_xlabel('Porcentaje de tiempo excedido (%)', fontsize=11)
ax.set_ylabel('Cota (m.s.n.m.)', fontsize=11)
ax.set_title('Curva de Duracion - San Pedrito', fontsize=13, fontweight='bold')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(OUTPUT_CARTILLAS / 'Fig3_Curva_Duracion_San Pedrito.png', dpi=200, bbox_inches='tight', facecolor='white')
plt.close()

# Fig4: Curvas de Frecuencia de Niveles Excedidos
print("  Fig4 - Curvas de Frecuencia...")
sp_no_leap = sp_df[~((sp_df['month'] == 2) & (sp_df['day'] == 29))].copy()
sp_no_leap['dia_anio'] = sp_no_leap['date'].dt.dayofyear

percentiles = [5, 25, 50, 75, 95]
colors = {'max': 'black', 'min': 'black', 5: '#8B0000', 25: '#6B8E23',
          50: 'black', 75: '#5DADE2', 95: '#D35400'}

fig, ax = plt.subplots(figsize=(14, 8))
for p in ['max', 'min'] + percentiles:
    if p == 'max':
        vals = sp_no_leap.groupby('dia_anio')['level'].max()
    elif p == 'min':
        vals = sp_no_leap.groupby('dia_anio')['level'].min()
    else:
        vals = sp_no_leap.groupby('dia_anio')['level'].quantile(p / 100)
    
    x = vals.index.values
    y = vals.values
    color = colors.get(p, 'gray')
    lw = 3 if p == 50 else 1.5
    ax.plot(x, y, color=color, linewidth=lw, label=f'{p}%')
    ax.text(x[-1] + 5, y[-1], f'{p}%', fontsize=9, va='center')

ax.set_xlim(0, 370)
ax.set_xlabel('Dia del Anio', fontsize=11)
ax.set_ylabel('Cota (m.s.n.m.)', fontsize=11)
ax.set_title('Curvas de Frecuencia de Niveles Excedidos - San Pedrito', fontsize=13, fontweight='bold')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(OUTPUT_CARTILLAS / 'Fig4_Curvas_Excedidos_SAN_PEDRITO_v2.png', dpi=200, bbox_inches='tight', facecolor='white')
plt.close()

# Fig5: Ajuste de Distribuciones
print("  Fig5 - Ajuste de Distribuciones...")
original_levels = original['level'].dropna().values
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

ax1 = axes[0]
count, bins, patches = ax1.hist(original_levels, bins=50, density=True,
                                 color='lightgray', edgecolor='gray', alpha=0.7)
from scipy import stats
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
plt.savefig(OUTPUT_CARTILLAS / 'Fig5_Ajuste_Distribuciones_SAN_PEDRITO.png', dpi=200, bbox_inches='tight', facecolor='white')
plt.close()

print(f"  Cartillas guardadas en: {OUTPUT_CARTILLAS}")

# =============================================================================
# PASO 4: Curvas H-H
# =============================================================================
print("\n" + "=" * 70)
print("PASO 4: Generando curvas H-H")
print("=" * 70)

OUTPUT_HH.mkdir(parents=True, exist_ok=True)

def get_common_period_v3(df, s1, s2):
    df1 = df[df['station'] == s1][['date', 'level']].copy()
    df2 = df[df['station'] == s2][['date', 'level']].copy()
    merged = pd.merge(df1, df2, on='date', suffixes=('_1', '_2'))
    return merged.dropna(subset=['level_1', 'level_2'])

def plot_hh_curve(df, target, donor, output_path):
    common = get_common_period_v3(df, target, donor)
    if len(common) < 30:
        print(f"  Insuficientes datos: {target} - {donor}")
        return None
    corr, _ = pearsonr(common['level_1'], common['level_2'])
    z = np.polyfit(common['level_2'], common['level_1'], 2)
    p = np.poly1d(z)
    x_fit = np.linspace(common['level_2'].min(), common['level_2'].max(), 200)
    y_fit = p(x_fit)
    
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.scatter(common['level_2'], common['level_1'], alpha=0.3, s=8, c='steelblue', edgecolors='none')
    ax.plot(x_fit, y_fit, 'r-', linewidth=2, label=f'Cuadratico (R2={corr**2:.3f})')
    lim_min = min(common['level_2'].min(), common['level_1'].min())
    lim_max = max(common['level_2'].max(), common['level_1'].max())
    ax.plot([lim_min, lim_max], [lim_min, lim_max], 'k--', linewidth=1, alpha=0.5, label='1:1')
    ax.set_xlabel(f'{donor.replace("_", " ")} - Cota (m.s.n.m.)', fontsize=11)
    ax.set_ylabel(f'{target.replace("_", " ")} - Cota (m.s.n.m.)', fontsize=11)
    ax.set_title(f'Curva H-H: {target.replace("_", " ")} vs {donor.replace("_", " ")}\n'
                 f'n={len(common):,} dias | r={corr:.3f} | Periodo: {common["date"].min().date()} a {common["date"].max().date()}',
                 fontsize=12, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  {target} vs {donor}: r={corr:.3f}, n={len(common):,}")
    return corr

v3 = pd.read_csv(V3_PATH)
v3['date'] = pd.to_datetime(v3['date'])

hh_pairs = [
    ('SAN_PEDRITO', 'CALAMAR'),
    ('SAN_PEDRITO', 'MAGANGUE'),
    ('SAN_PEDRITO', 'TENERIFE'),
    ('SAN_PEDRITO', 'BARBOSA'),
    ('SAN_PEDRITO', 'COYONGAL'),
]

hh_results = []
for target, donor in hh_pairs:
    output_file = OUTPUT_HH / f'Figura_HH_{target}_{donor}.png'
    corr = plot_hh_curve(v3, target, donor, output_file)
    if corr:
        hh_results.append({'target': target, 'donor': donor, 'r': corr})

# =============================================================================
# RESUMEN
# =============================================================================
print("\n" + "=" * 70)
print("RECONSTRUCCION COMPLETADA - SAN PEDRITO (1979-2026)")
print("=" * 70)
print(f"\nDataset combinado:")
print(f"  Total registros: {len(sp_combined)}")
print(f"  Validos: {sp_combined['level'].notna().sum()}")
print(f"  Missing: {sp_combined['level'].isna().sum()}")
print(f"  Rango: {sp_combined['date'].min().date()} a {sp_combined['date'].max().date()}")
print(f"\nV3 actualizado: {V3_PATH}")
print(f"Cartillas: {OUTPUT_CARTILLAS}")
print(f"Curvas H-H: {OUTPUT_HH}")
print(f"\nResultados H-H:")
for r in hh_results:
    print(f"  {r['target']} vs {r['donor']}: r = {r['r']:.3f}")
