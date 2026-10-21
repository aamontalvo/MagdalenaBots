"""
Generar archivo maestro LONG fuente de la verdad desde datos raw IDEAM.

REGLAS (Hard Rules):
1. Formato LONG unicamente (no wide).
2. Cada estacion tiene su propio rango temporal: desde su PRIMERA fecha con 
   dato real (no NaN) hasta su ULTIMA fecha con dato real, CORTADO al 
   31-12-2025 como maximo.
3. NO se extrapola/imputa fuera del rango real de datos de cada estacion.
4. Dentro del rango real, los dias faltantes se crean con valor en blanco (NaN).
5. Se excluye SIEMPRE el 29 de febrero (anos bisiestos).
6. La columna Fecha es tipo datetime.
7. Fuente unica: backend/data/raw/SERIE NIVELES IDEAM A 2026
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# CONFIGURACION
# =============================================================================
RAW_DIR = Path(r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\backend\data\raw\SERIE NIVELES IDEAM A 2026')
PROCESSED_DIR = Path(r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\backend\data\processed')
OUTPUT_CSV = PROCESSED_DIR / 'Resumen_Crudos_IDEAM_2026.csv'
OUTPUT_XLSX = PROCESSED_DIR / 'Resumen_Crudos_IDEAM_2026.xlsx'
CUTOFF_DATE = pd.Timestamp('2025-12-31')

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

# Orden alfabetico para reporte
STATIONS_ALPHABETICAL = sorted(STATION_INFO.keys())

# =============================================================================
# FUNCIONES
# =============================================================================

def load_station_raw_data(station_name):
    """
    Lee datos crudos de una estacion desde su Excel IDEAM.
    Retorna DataFrame con columnas: date, year, month, day, level
    donde level = NaN si no hay dato en esa fecha.
    Solo incluye fechas DENTRO del rango real [primera_fecha, ultima_fecha].
    """
    info = STATION_INFO[station_name]
    filepath = RAW_DIR / info['file']
    
    # Leer sin header para detectar anos en fila 0
    df_wide = pd.read_excel(filepath, sheet_name=info['sheet'], header=None)
    
    # Detectar columnas de ano en fila 0
    year_cols = []
    for i, val in enumerate(df_wide.iloc[0]):
        if isinstance(val, (int, float)) and not isinstance(val, bool) and 1900 <= val <= 2100:
            year_cols.append((i, int(val)))
    
    if not year_cols:
        print(f"    [WARNING] No se encontraron anos para {station_name}")
        return pd.DataFrame()
    
    # Detectar formato de columna de fechas (columna 0)
    first_data_val = None
    for row_idx in range(1, len(df_wide)):
        val = df_wide.iloc[row_idx, 0]
        if pd.notna(val):
            first_data_val = val
            break
    
    is_float_date = isinstance(first_data_val, (int, float)) and not isinstance(first_data_val, bool)
    
    # Extraer registros reales (con o sin dato)
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
                
                # Saltar 29-feb SIEMPRE
                if month == 2 and day == 29:
                    continue
                
                date = pd.Timestamp(year=year, month=month, day=day)
                level = float(level_val) if pd.notna(level_val) else np.nan
                
                records.append({
                    'date': date,
                    'level': level,
                })
            except:
                continue
    
    df = pd.DataFrame(records)
    if len(df) == 0:
        return pd.DataFrame()
    
    df = df.sort_values('date').reset_index(drop=True)
    
    # Encontrar rango REAL de datos (primer y ultimo dato no-NaN)
    valid_mask = df['level'].notna()
    if valid_mask.sum() == 0:
        print(f"    [WARNING] {station_name}: no tiene datos validos")
        return pd.DataFrame()
    
    first_valid_date = df.loc[valid_mask, 'date'].min()
    last_valid_date = df.loc[valid_mask, 'date'].max()
    
    # Aplicar corte al 31-12-2025
    last_date = min(last_valid_date, CUTOFF_DATE)
    
    # Si el corte es antes del primer dato valido, no hay nada que hacer
    if last_date < first_valid_date:
        print(f"    [WARNING] {station_name}: corte {last_date.date()} antes del inicio {first_valid_date.date()}")
        return pd.DataFrame()
    
    # Generar serie continua de fechas dentro del rango real [inicio, fin_cortado]
    # excluyendo 29-feb
    date_range = pd.date_range(start=first_valid_date, end=last_date, freq='D')
    date_range = date_range[~((date_range.month == 2) & (date_range.day == 29))]
    
    df_range = pd.DataFrame({'date': date_range})
    df_range['year'] = df_range['date'].dt.year
    df_range['month'] = df_range['date'].dt.month
    df_range['day'] = df_range['date'].dt.day
    
    # Hacer merge con datos reales: dias sin datos quedan como NaN
    df_merged = pd.merge(df_range, df, on='date', how='left')
    df_merged['station'] = station_name
    df_merged['code'] = info['code']
    
    # Reordenar columnas
    df_merged = df_merged[['station', 'code', 'date', 'year', 'month', 'day', 'level']]
    
    return df_merged


# =============================================================================
# PROCESAMIENTO
# =============================================================================
print("=" * 80)
print("GENERANDO FUENTE DE LA VERDAD - DATOS CRUDOS IDEAM (LONG FORMAT)")
print("=" * 80)
print(f"Corte maximo: {CUTOFF_DATE.strftime('%d-%m-%Y')}")
print(f"Excluye: 29 de febrero")
print(f"Rango: desde PRIMER dato real de cada estacion hasta ULTIMO dato real o corte")
print("=" * 80)

all_stations = []
summary = []

for station in STATIONS_ALPHABETICAL:
    print(f"\n[{station}]")
    df = load_station_raw_data(station)
    
    if len(df) == 0:
        summary.append({
            'station': station,
            'code': STATION_INFO[station]['code'],
            'start_date': None,
            'end_date': None,
            'total_days': 0,
            'valid_days': 0,
            'missing_days': 0,
            'coverage_pct': 0.0,
            'status': 'ERROR - Sin datos'
        })
        continue
    
    total_days = len(df)
    valid_days = df['level'].notna().sum()
    missing_days = total_days - valid_days
    coverage = 100 * valid_days / total_days if total_days > 0 else 0
    start_date = df['date'].min()
    end_date = df['date'].max()
    
    print(f"  Rango: {start_date.strftime('%d-%m-%Y')} a {end_date.strftime('%d-%m-%Y')}")
    print(f"  Total dias: {total_days:,} | Validos: {valid_days:,} | Faltantes: {missing_days:,}")
    print(f"  Cobertura: {coverage:.2f}%")
    
    summary.append({
        'station': station,
        'code': STATION_INFO[station]['code'],
        'start_date': start_date.strftime('%d-%m-%Y'),
        'end_date': end_date.strftime('%d-%m-%Y'),
        'total_days': total_days,
        'valid_days': valid_days,
        'missing_days': missing_days,
        'coverage_pct': round(coverage, 2),
        'status': 'OK'
    })
    
    all_stations.append(df)

# Concatenar todas las estaciones
print("\n" + "=" * 80)
print("CONSOLIDANDO ARCHIVO MAESTRO")
print("=" * 80)

df_master = pd.concat(all_stations, ignore_index=True)
print(f"Total registros maestro: {len(df_master):,}")
print(f"Estaciones: {df_master['station'].nunique()}")
print(f"Rango global: {df_master['date'].min().strftime('%d-%m-%Y')} a {df_master['date'].max().strftime('%d-%m-%Y')}")

# Guardar CSV
df_master.to_csv(OUTPUT_CSV, index=False, encoding='utf-8-sig', date_format='%d-%m-%Y')
print(f"\nGuardado CSV: {OUTPUT_CSV}")

# Guardar Excel (con fecha como datetime real, no string)
with pd.ExcelWriter(OUTPUT_XLSX, engine='openpyxl') as writer:
    df_master.to_excel(writer, sheet_name='Datos_Crudos', index=False)
print(f"Guardado Excel: {OUTPUT_XLSX}")

# =============================================================================
# REPORTE RESUMEN
# =============================================================================
print("\n" + "=" * 80)
print("RESUMEN POR ESTACION (ORDEN ALFABETICO)")
print("=" * 80)

df_summary = pd.DataFrame(summary)
df_summary = df_summary.sort_values('station')

# Mostrar tabla en consola
print(f"{'Estacion':<20} {'Codigo':<12} {'Inicio':<12} {'Fin':<12} {'Total':>8} {'Validos':>8} {'Faltan':>8} {'Cob.':>6} {'Estado':<10}")
print("-" * 100)
for _, row in df_summary.iterrows():
    start = row['start_date'] if row['start_date'] else 'N/A'
    end = row['end_date'] if row['end_date'] else 'N/A'
    print(f"{row['station']:<20} {row['code']:<12} {start:<12} {end:<12} {row['total_days']:>8,} {row['valid_days']:>8,} {row['missing_days']:>8,} {row['coverage_pct']:>5.1f}% {row['status']:<10}")

# Guardar resumen
df_summary.to_csv(PROCESSED_DIR / 'Resumen_Crudos_IDEAM_2026_metadata.csv', index=False, encoding='utf-8-sig')
print(f"\nMetadatos guardados: {PROCESSED_DIR / 'Resumen_Crudos_IDEAM_2026_metadata.csv'}")

print("\n" + "=" * 80)
print("PROCESO COMPLETADO")
print("=" * 80)
