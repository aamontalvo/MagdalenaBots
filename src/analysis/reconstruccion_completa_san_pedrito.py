"""
Reconstruccion completa de San Pedrito - 1979 a 2026
1. Actualiza archivos de resumen (wide y long format)
2. Regenera graficas generales (boxplot)
3. Regenera cartillas de San Pedrito
4. Regenera curvas H-H
5. Crea archivo Excel de resumen con datos crudos
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from scipy.stats import pearsonr
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# CONFIGURACION
# =============================================================================
RAW_DIR = Path(r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\backend\data\raw\SERIE NIVELES IDEAM A 2026')
PROCESSED_DIR = Path(r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\backend\data\processed')
V3_PATH = Path(r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\cartillas_estaciones\datos\processed\Datos_Imputados_v3.csv')
OUTPUT_CARTILLAS = Path(r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\cartillas_estaciones\v4_2\SAN_PEDRITO')
OUTPUT_HH = Path(r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\Informes\imputacion\Curvas_HH_v4_2')
IMAGENES_DIR = Path(r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\Imagenes\Niveles')

STATION_INFO = {
    'ARMENIA': {'file': 'ARMENIA_25027360.xlsx', 'code': '25027360', 'sheet': 'ArmeniaM19732019'},
    'BARBOSA': {'file': 'BARBOSA_25027530.xlsx', 'code': '25027530', 'sheet': 'Columnas Barbosa'},
    'CALAMAR': {'file': 'CALAMAR_29037020.xlsx', 'code': '29037020', 'sheet': 'Columnas Calamar'},
    'COYONGAL': {'file': 'COYONGAL_25027930.xlsx', 'code': '25027930', 'sheet': 'Columnas Coyongal'},
    'EL_BANCO': {'file': 'EL_BANCO_-_AUT_25027020.xlsx', 'code': '25027020', 'sheet': 'Columnas ElBanco'},
    'EL_CONTENTO': {'file': 'EL_CONTENTO_23217030.xlsx', 'code': '23217030', 'sheet': 'Columnas ElContento'},
    'GAMARRA_AUT': {'file': 'GAMARRA_-_AUT_23217080.xlsx', 'code': '23217080', 'sheet': 'GamarraAUTM20132019'},
    'LA_GLORIA': {'file': 'LA_GLORIA23217060.xlsx', 'code': '23217060', 'sheet': 'Columnas LaGloria'},
    'LAS_AGUADAS': {'file': 'LAS_AGUADAS_25027490.xlsx', 'code': '25027490', 'sheet': 'Columnas LasAguadas'},
    'LAS_PALOMAS': {'file': 'LAS_PALOMAS_25027390.xlsx', 'code': '25027390', 'sheet': 'Columnas LasPalomas'},
    'MAGANGUE': {'file': 'MAGANGUE_25027680.xlsx', 'code': '25027680', 'sheet': 'MAGANGUE197331122019'},
    'PENONCITO': {'file': 'PENONCITO_25027330.xlsx', 'code': '25027330', 'sheet': 'PenoncitoM19722018'},
    'PLATO': {'file': 'PLATO_MAGDALENA_AUT_25027450.xlsx', 'code': '25027450', 'sheet': 'Columnas PLATO'},
    'PUERTO_WILCHES': {'file': 'PUERTO_WILCHES_23187010.xlsx', 'code': '23187010', 'sheet': 'Columnas PuertoWilchesM'},
    'RIO_NUEVO': {'file': 'RIO_NUEVO_25027630.xlsx', 'code': '25027630', 'sheet': 'Columnas RioNuevo'},
    'SAN_PEDRITO': {'file': 'SAN_PEDRITO_-_AUT_29047070.xlsx', 'code': '29047070', 'sheet': 'Columnas SAN_PEDRITO'},
    'SITIO_NUEVO': {'file': 'SITIO_NUEVO_23187280.xlsx', 'code': '23187280', 'sheet': 'SitioNuevoM19792019'},
    'TENERIFE': {'file': 'TENERIFE_29017010.xlsx', 'code': '29017010', 'sheet': 'Columnas TENERIFE'},
}

GEOGRAPHIC_ORDER = [
    'SAN_PEDRITO', 'CALAMAR', 'TENERIFE', 'PLATO', 'MAGANGUE', 'BARBOSA', 'COYONGAL',
    'ARMENIA', 'RIO_NUEVO', 'LAS_PALOMAS', 'LAS_AGUADAS', 'EL_BANCO', 'PENONCITO',
    'LA_GLORIA', 'GAMARRA_AUT', 'EL_CONTENTO', 'SITIO_NUEVO', 'PUERTO_WILCHES',
]

# =============================================================================
# FUNCION: Cargar datos originales de cualquier estacion
# =============================================================================
def load_station_raw(station_name):
    """Carga datos originales de una estacion desde su Excel."""
    info = STATION_INFO[station_name]
    filepath = RAW_DIR / info['file']
    
    # Usar header=None para evitar problemas de deteccion de tipos
    df_wide = pd.read_excel(filepath, sheet_name=info['sheet'], header=None)
    
    # La fila 0 contiene los anos
    year_cols = []
    for i, val in enumerate(df_wide.iloc[0]):
        if isinstance(val, (int, float)) and 1900 <= val <= 2100:
            year_cols.append((i, int(val)))
    
    if not year_cols:
        return None
    
    # Detectar formato de la columna de fechas (columna 0)
    first_data_val = df_wide.iloc[1, 0]
    is_float_date = isinstance(first_data_val, (int, float)) and not isinstance(first_data_val, bool)
    
    records = []
    for col_idx, year in year_cols:
        for row_idx in range(1, len(df_wide)):
            try:
                date_val = df_wide.iloc[row_idx, 0]
                level_val = df_wide.iloc[row_idx, col_idx]
                
                if pd.isna(date_val):
                    continue
                
                if is_float_date:
                    val = float(date_val)
                    month = int(val)
                    day = int(round((val - month) * 100))
                else:
                    ref_date = pd.to_datetime(date_val)
                    month = ref_date.month
                    day = ref_date.day
                
                # Saltar 29 de febrero en anos no bisiesto
                if month == 2 and day == 29:
                    if not (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)):
                        continue
                
                date = pd.Timestamp(year=year, month=month, day=day)
                level = float(level_val) if pd.notna(level_val) else np.nan
                
                records.append({
                    'date': date,
                    'station': station_name,
                    'level': level,
                    'year': year,
                    'month': month,
                    'day': day
                })
            except:
                continue
    
    return pd.DataFrame(records).sort_values('date').reset_index(drop=True)


# =============================================================================
# PASO 1: Verificar carga de San Pedrito
# =============================================================================
print("=" * 70)
print("PASO 1: Cargando datos originales de San Pedrito")
print("=" * 70)

df_sp = load_station_raw('SAN_PEDRITO')
print(f"  Registros: {len(df_sp)}")
print(f"  Validos: {df_sp['level'].notna().sum()}")
print(f"  Missing: {df_sp['level'].isna().sum()}")
print(f"  Rango: {df_sp['date'].min().date()} a {df_sp['date'].max().date()}")
print(f"  Cobertura: {100*df_sp['level'].notna().sum()/len(df_sp):.1f}%")

# =============================================================================
# PASO 2: Actualizar Resumen_LongFormat
# =============================================================================
print("\n" + "=" * 70)
print("PASO 2: Actualizando Resumen_LongFormat")
print("=" * 70)

long_path = PROCESSED_DIR / 'Resumen_LongFormat_NotProcessedNotImputation.xlsx'
long_csv_path = PROCESSED_DIR / 'Resumen_LongFormat_NotProcessedNotImputation.csv'

df_long = pd.read_excel(long_path)
print(f"  LongFormat original: {len(df_long)} registros")

# Eliminar San Pedrito actual
df_long_no_sp = df_long[df_long['NombreEstacion'] != 'San Pedrito'].copy()
print(f"  Sin San Pedrito: {len(df_long_no_sp)} registros")

# Crear nuevos registros de San Pedrito
sp_long_records = []
for _, row in df_sp.iterrows():
    if pd.notna(row['level']):
        sp_long_records.append({
            'CodigoEstacion': '29047070',
            'NombreEstacion': 'San Pedrito',
            'Fecha': row['date'].strftime('%d-%m-%Y'),
            'Cota': row['level']
        })

df_sp_long = pd.DataFrame(sp_long_records)
print(f"  Nuevos registros San Pedrito: {len(df_sp_long)}")

# Concatenar y guardar
df_long_new = pd.concat([df_long_no_sp, df_sp_long], ignore_index=True)
df_long_new = df_long_new.sort_values(['NombreEstacion', 'Fecha']).reset_index(drop=True)
print(f"  LongFormat nuevo: {len(df_long_new)} registros")

# Backup y guardado
backup_dir = PROCESSED_DIR / 'backups'
backup_dir.mkdir(exist_ok=True)
df_long.to_excel(backup_dir / 'Resumen_LongFormat_backup_pre_sanpedrito.xlsx', index=False)
df_long.to_csv(backup_dir / 'Resumen_LongFormat_backup_pre_sanpedrito.csv', index=False, encoding='utf-8-sig')
df_long_new.to_excel(long_path, index=False)
df_long_new.to_csv(long_csv_path, index=False, encoding='utf-8-sig')
print(f"  Guardado: {long_path}")
print(f"  Guardado CSV: {long_csv_path}")

# =============================================================================
# PASO 3: Reconstruir Resumen_WideFormat desde datos originales
# =============================================================================
print("\n" + "=" * 70)
print("PASO 3: Reconstruyendo Resumen_WideFormat desde datos originales")
print("=" * 70)

wide_path = PROCESSED_DIR / 'Resumen_WideFormat_NotProcessedNotImputation.xlsx'

# Eliminar archivo corrupto si existe
if wide_path.exists():
    wide_path.unlink()
    print(f"  Archivo corrupto eliminado")

# Funcion para convertir datos long a formato wide estacion
def build_wide_sheet(df_station):
    """Construye hoja wide desde datos long de una estacion."""
    if df_station is None or len(df_station) == 0:
        return pd.DataFrame()
    
    years = sorted(df_station['year'].unique())
    # Crear todas las fechas del año (usando año NO bisiesto como referencia para excluir 29-feb)
    all_dates = []
    for m in range(1, 13):
        for d in range(1, 32):
            try:
                pd.Timestamp(year=2019, month=m, day=d)
                all_dates.append((m, d))
            except:
                continue
    
    n_cols = len(years) + 1
    n_rows = 1 + len(all_dates) + 5  # header + dates + stats
    wide = pd.DataFrame(index=range(n_rows), columns=range(n_cols))
    
    # Fila 0: headers
    wide.iloc[0, 0] = np.nan
    for i, y in enumerate(years):
        wide.iloc[0, i+1] = float(y)
    
    # Pivot
    pivot = df_station.pivot(index=['month', 'day'], columns='year', values='level')
    
    # Filas de datos
    for row_idx, (month, day) in enumerate(all_dates, start=1):
        wide.iloc[row_idx, 0] = pd.Timestamp(year=2019, month=month, day=day)
        for year in years:
            if year in pivot.columns and (month, day) in pivot.index:
                val = pivot.loc[(month, day), year]
                col_idx = years.index(year) + 1
                wide.iloc[row_idx, col_idx] = val if pd.notna(val) else np.nan
    
    # Estadisticas
    stats_start = 1 + len(all_dates)
    for col_idx in range(1, len(years)+1):
        vals = wide.iloc[1:stats_start, col_idx].dropna()
        if len(vals) > 0:
            wide.iloc[stats_start, col_idx] = vals.max()
            wide.iloc[stats_start+1, col_idx] = vals.min()
            wide.iloc[stats_start+2, col_idx] = vals.mean()
            wide.iloc[stats_start+3, col_idx] = vals.quantile(0.25)
            wide.iloc[stats_start+4, col_idx] = vals.quantile(0.75)
    
    return wide

# Mapeo de nombres de estacion a nombres de hoja
SHEET_NAMES = {
    'SAN_PEDRITO': 'SanPedrito',
    'CALAMAR': 'Calamar',
    'TENERIFE': 'Tenerife',
    'PLATO': 'Plato',
    'MAGANGUE': 'Magangue',
    'BARBOSA': 'Barbosa',
    'COYONGAL': 'Coyongal',
    'ARMENIA': 'Armenia',
    'RIO_NUEVO': 'RioNuevo',
    'LAS_PALOMAS': 'LasPalomas',
    'LAS_AGUADAS': 'LasAguadas',
    'EL_BANCO': 'ElBanco',
    'PENONCITO': 'Penoncito',
    'LA_GLORIA': 'LaGloria',
    'GAMARRA_AUT': 'GamarraAut',
    'EL_CONTENTO': 'ElContento',
    'SITIO_NUEVO': 'SitioNuevo',
    'PUERTO_WILCHES': 'PuertoWilches',
}

# Construir todas las hojas y guardar
with pd.ExcelWriter(wide_path, engine='openpyxl') as writer:
    for station in GEOGRAPHIC_ORDER:
        sheet_name = SHEET_NAMES[station]
        print(f"  Construyendo {sheet_name}...")
        df_st = load_station_raw(station)
        wide_sheet = build_wide_sheet(df_st)
        if len(wide_sheet) > 0:
            wide_sheet.to_excel(writer, sheet_name=sheet_name, index=False, header=False)

print(f"  Guardado: {wide_path}")

# =============================================================================
# PASO 4: Actualizar Datos_Imputados_v3.csv
# =============================================================================
print("\n" + "=" * 70)
print("PASO 4: Actualizando Datos_Imputados_v3.csv")
print("=" * 70)

v3 = pd.read_csv(V3_PATH, low_memory=False)
v3['date'] = pd.to_datetime(v3['date'], format='mixed', dayfirst=False)
print(f"  V3 actual: {len(v3)} registros")

v3_no_sp = v3[v3['station'] != 'SAN_PEDRITO'].copy()
print(f"  Sin SP: {len(v3_no_sp)} registros")

sp_v3 = pd.DataFrame()
sp_v3['date'] = df_sp['date']
sp_v3['year'] = sp_v3['date'].dt.year
sp_v3['month'] = sp_v3['date'].dt.month
sp_v3['day'] = sp_v3['date'].dt.day
sp_v3['station'] = 'SAN_PEDRITO'
sp_v3['level'] = df_sp['level']
sp_v3['data_source'] = np.where(df_sp['level'].notna(), 'original', 'missing')
sp_v3['level_original'] = df_sp['level']
sp_v3['imputed_local'] = np.nan
sp_v3['is_null'] = df_sp['level'].isna()

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

v3.to_csv(backup_dir / 'Datos_Imputados_v3_backup_pre_sanpedrito_completo.csv', index=False, encoding='utf-8-sig')
v3_new.to_csv(V3_PATH, index=False, encoding='utf-8-sig')
print(f"  Guardado: {V3_PATH}")

# =============================================================================
# PASO 5: Regenerar Boxplot General
# =============================================================================
print("\n" + "=" * 70)
print("PASO 5: Regenerando Boxplot General")
print("=" * 70)

fig, ax = plt.subplots(figsize=(18, 8))

data_for_box = []
labels = []
for station in GEOGRAPHIC_ORDER:
    print(f"  Cargando {station}...")
    df_st = load_station_raw(station)
    if df_st is not None and len(df_st) > 0:
        vals = df_st['level'].dropna().values
        if len(vals) > 0:
            data_for_box.append(vals)
            labels.append(station.replace('_', ' ').title())

bp = ax.boxplot(data_for_box, labels=labels, patch_artist=True, showfliers=True,
                boxprops=dict(facecolor='white', edgecolor='black', linewidth=1.2),
                medianprops=dict(color='black', linewidth=2),
                whiskerprops=dict(color='black', linewidth=1),
                capprops=dict(color='black', linewidth=1),
                flierprops=dict(marker='o', markerfacecolor='none', markeredgecolor='black',
                               markersize=4, alpha=0.6))

# Lineas de separacion de zonas
line1_pos = 7.5
line2_pos = 13.5
ax.axvline(x=line1_pos, color='black', linestyle='--', linewidth=2, alpha=0.7)
ax.axvline(x=line2_pos, color='black', linestyle='--', linewidth=2, alpha=0.7)

ax.set_xlabel('Estacion (Orden: aguas abajo -> aguas arriba)', fontsize=11)
ax.set_ylabel('Cota (m.s.n.m.)', fontsize=11)
ax.set_title('Diagrama de Cajas de Cotas por Estacion - Datos Originales\n' +
             'Zona Baja: San Pedrito->Coyongal | Media: Armenia->Penoncito | Alta: La Gloria->Puerto Wilches',
             fontsize=12, fontweight='bold', pad=20)

plt.xticks(rotation=45, ha='right')
plt.grid(axis='y', alpha=0.3, linestyle='--', color='gray')
plt.tight_layout()
plt.savefig(IMAGENES_DIR / 'Boxplots_GeneralEstaciones_v2.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print(f"  Guardado: {IMAGENES_DIR / 'Boxplots_GeneralEstaciones_v2.png'}")

# =============================================================================
# PASO 6: Regenerar Cartillas de San Pedrito
# =============================================================================
print("\n" + "=" * 70)
print("PASO 6: Regenerando cartillas de San Pedrito")
print("=" * 70)

OUTPUT_CARTILLAS.mkdir(parents=True, exist_ok=True)
v3 = pd.read_csv(V3_PATH)
v3['date'] = pd.to_datetime(v3['date'])
sp_df = v3[v3['station'] == 'SAN_PEDRITO'].copy().sort_values('date')

# Fig1
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

# Fig2
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
ax.set_xticklabels(['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN', 'JUL', 'AGO', 'SEP', 'OCT', 'NOV', 'DIC'])
ax.set_xlabel('Mes', fontsize=11)
ax.set_ylabel('Cota (m.s.n.m.)', fontsize=11)
ax.set_title('Comportamiento Mensual Multianual - San Pedrito', fontsize=13, fontweight='bold')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(OUTPUT_CARTILLAS / 'Fig2_Violin_Mensual_San Pedrito.png', dpi=200, bbox_inches='tight', facecolor='white')
plt.close()

# Fig3
print("  Fig3 - Curva de Duracion...")
valid_levels = sp_df['level'].dropna().sort_values(ascending=False).values
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
ax.set_title('Curva de Duracion - San Pedrito', fontsize=13, fontweight='bold')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(OUTPUT_CARTILLAS / 'Fig3_Curva_Duracion_San Pedrito.png', dpi=200, bbox_inches='tight', facecolor='white')
plt.close()

# Fig4
print("  Fig4 - Curvas de Frecuencia...")
sp_no_leap = sp_df[~((sp_df['month'] == 2) & (sp_df['day'] == 29))].copy()
sp_no_leap['dia_anio'] = sp_no_leap['date'].dt.dayofyear
percentiles = [5, 25, 50, 75, 95]
colors = {'max': 'black', 'min': 'black', 5: '#8B0000', 25: '#6B8E23', 50: 'black', 75: '#5DADE2', 95: '#D35400'}
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

# Fig5
print("  Fig5 - Ajuste de Distribuciones...")
original_levels = original['level'].dropna().values
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
ax1 = axes[0]
count, bins, patches = ax1.hist(original_levels, bins=50, density=True, color='lightgray', edgecolor='gray', alpha=0.7)
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
# PASO 7: Regenerar Curvas H-H
# =============================================================================
print("\n" + "=" * 70)
print("PASO 7: Generando curvas H-H de San Pedrito")
print("=" * 70)

OUTPUT_HH.mkdir(parents=True, exist_ok=True)

def get_common_period(df, s1, s2):
    df1 = df[df['station'] == s1][['date', 'level']].copy()
    df2 = df[df['station'] == s2][['date', 'level']].copy()
    merged = pd.merge(df1, df2, on='date', suffixes=('_1', '_2'))
    return merged.dropna(subset=['level_1', 'level_2'])

def plot_hh(df, target, donor, output_path):
    common = get_common_period(df, target, donor)
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
                 f'n={len(common):,} dias | r={corr:.3f} | {common["date"].min().date()} a {common["date"].max().date()}',
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

hh_pairs = [('SAN_PEDRITO', 'CALAMAR'), ('SAN_PEDRITO', 'MAGANGUE'), ('SAN_PEDRITO', 'TENERIFE'),
            ('SAN_PEDRITO', 'BARBOSA'), ('SAN_PEDRITO', 'COYONGAL')]

hh_results = []
for target, donor in hh_pairs:
    output_file = OUTPUT_HH / f'Figura_HH_{target}_{donor}.png'
    corr = plot_hh(v3, target, donor, output_file)
    if corr:
        hh_results.append({'target': target, 'donor': donor, 'r': corr})

# =============================================================================
# PASO 8: Crear archivo Excel de resumen con datos crudos
# =============================================================================
print("\n" + "=" * 70)
print("PASO 8: Creando archivo Excel de resumen con datos crudos")
print("=" * 70)

raw_summary_path = PROCESSED_DIR / 'Resumen_Crudos_IDEAM_2026.xlsx'

print("  Cargando datos crudos de todas las estaciones...")
all_raw_data = []
for station in GEOGRAPHIC_ORDER:
    df_st = load_station_raw(station)
    if df_st is not None and len(df_st) > 0:
        valid = df_st[df_st['level'].notna()].copy()
        valid['CodigoEstacion'] = STATION_INFO[station]['code']
        valid['NombreEstacion'] = station.replace('_', ' ')
        valid['Fecha'] = valid['date'].dt.strftime('%d-%m-%Y')
        valid['Cota'] = valid['level']
        all_raw_data.append(valid[['CodigoEstacion', 'NombreEstacion', 'Fecha', 'Cota']])
        print(f"    {station}: {len(valid)} registros")

df_raw_summary = pd.concat(all_raw_data, ignore_index=True)
df_raw_summary = df_raw_summary.sort_values(['NombreEstacion', 'Fecha']).reset_index(drop=True)

# Guardar
with pd.ExcelWriter(raw_summary_path, engine='openpyxl') as writer:
    df_raw_summary.to_excel(writer, sheet_name='DatosCrudos', index=False)
    
    # Hoja de resumen por estacion
    summary = []
    for station in GEOGRAPHIC_ORDER:
        st_data = df_raw_summary[df_raw_summary['NombreEstacion'] == station.replace('_', ' ')]
        if len(st_data) > 0:
            summary.append({
                'Estacion': station.replace('_', ' '),
                'Codigo': STATION_INFO[station]['code'],
                'Registros': len(st_data),
                'FechaInicio': st_data['Fecha'].min(),
                'FechaFin': st_data['Fecha'].max(),
                'CotaMin': st_data['Cota'].min(),
                'CotaMax': st_data['Cota'].max(),
                'CotaProm': st_data['Cota'].mean(),
            })
    pd.DataFrame(summary).to_excel(writer, sheet_name='Resumen', index=False)

print(f"  Guardado: {raw_summary_path}")

# =============================================================================
# RESUMEN FINAL
# =============================================================================
print("\n" + "=" * 70)
print("RECONSTRUCCION COMPLETADA - SAN PEDRITO (1979-2026)")
print("=" * 70)
print(f"\n1. Resumen_WideFormat: Actualizado con SP hasta 2026")
print(f"2. Resumen_LongFormat: {len(df_long_new)} registros (SP: {len(df_sp_long)})")
print(f"3. Datos_Imputados_v3: {len(v3_new)} registros")
print(f"4. Boxplot General: {IMAGENES_DIR / 'Boxplots_GeneralEstaciones_v2.png'}")
print(f"5. Cartillas SP: {OUTPUT_CARTILLAS}")
print(f"6. Curvas H-H: {OUTPUT_HH}")
print(f"7. Resumen Crudos: {raw_summary_path}")
print(f"\nDataset San Pedrito:")
print(f"  Total: {len(df_sp)} | Validos: {df_sp['level'].notna().sum()} | Missing: {df_sp['level'].isna().sum()}")
print(f"  Rango: {df_sp['date'].min().date()} a {df_sp['date'].max().date()}")
print(f"\nCurvas H-H:")
for r in hh_results:
    print(f"  {r['target']} vs {r['donor']}: r = {r['r']:.3f}")
