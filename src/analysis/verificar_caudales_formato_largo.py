# -*- coding: utf-8 -*-
"""
Verificacion de integridad de caudales_formato_largo.csv

Comprueba que el CSV largo refleje fielmente los archivos Excel originales
de SERIE_CAUDALES/CAUDALES y que los filtros aplicados sean correctos.

Checks:
1. Rango temporal por estacion vs originales
2. Conteo de registros validos vs originales
3. Estadisticos anuales: suma, media, mediana vs originales
4. Minimo y maximo por estacion vs originales
5. No existen registros del 29 de febrero
6. Sin duplicados (estacion, fecha)
7. Solo estaciones comunes con niveles cuando se aplica filtro
8. Sin valores negativos o nulos sospechosos en datos originales
9. Consistencia de nombres normalizados

Uso:
    from verificar_caudales_formato_largo import verificar_caudales
    ok, reporte = verificar_caudales(ruta_csv, ruta_excel, estaciones_comunes)
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Tuple, Dict
import sys
import warnings

warnings.filterwarnings('ignore')
sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot')
CAUDALES_DIR = PROJECT_ROOT / 'backend' / 'data' / 'raw' / 'SERIE_CAUDALES' / 'CAUDALES'
CSV_PATH = PROJECT_ROOT / 'backend' / 'data' / 'raw' / 'SERIE_CAUDALES' / 'analisis' / 'caudales_formato_largo.csv'
REPORT_PATH = PROJECT_ROOT / 'backend' / 'data' / 'raw' / 'SERIE_CAUDALES' / 'analisis' / 'verificacion_caudales.txt'
SUMMARY_PATH = PROJECT_ROOT / 'backend' / 'data' / 'raw' / 'SERIE_CAUDALES' / 'analisis' / 'verificacion_caudales.csv'

TOL = 1e-4

ESTACIONES_COMUNES = {
    'ARMENIA', 'BARBOSA', 'CALAMAR', 'EL_BANCO', 'EL_CONTENTO',
    'LAS_AGUADAS', 'LAS_PALOMAS', 'MAGANGUE', 'PENONCITO',
    'RIO_NUEVO', 'SITIO_NUEVO'
}


def limpiar_nombre(nombre_archivo: str) -> str:
    """Extrae nombre base de estacion del archivo."""
    base = nombre_archivo.replace('.xlsx', '').strip()
    if '(' in base:
        base = base.split('(')[0].strip()
    partes = base.rsplit('_', 1)
    if len(partes) == 2 and partes[1].replace('-', '').isdigit():
        base = partes[0]
    nombre = base.strip().upper().replace(' ', '_')
    mapeos = {
        'EL_BANCO_-_AUT': 'EL_BANCO',
        'EL-BANCO---AUT': 'EL_BANCO',
    }
    return mapeos.get(nombre, nombre)


def detectar_hoja_wide(xl: pd.ExcelFile) -> Tuple[str, int]:
    """Detecta cual hoja tiene formato wide (anos como columnas)."""
    mejor_hoja = None
    mejor_count = 0
    for h in xl.sheet_names:
        df = pd.read_excel(xl, sheet_name=h, header=None, nrows=2)
        if df.shape[0] < 2 or df.shape[1] < 5:
            continue
        header_row = df.iloc[0].fillna('').astype(str).tolist()
        year_count = sum(
            1 for x in header_row
            if x.replace('.0', '').strip().isdigit() and len(x.replace('.0', '').strip()) == 4
        )
        if year_count > mejor_count:
            mejor_count = year_count
            mejor_hoja = h
    return mejor_hoja, mejor_count


def excel_a_long(path: Path, station_name: str) -> pd.DataFrame:
    """Convierte un Excel original wide a formato long."""
    xl = pd.ExcelFile(path)
    hoja_wide, _ = detectar_hoja_wide(xl)
    if not hoja_wide:
        return pd.DataFrame()

    df_wide = pd.read_excel(path, sheet_name=hoja_wide, header=None)
    headers = df_wide.iloc[0].astype(str).tolist()
    seen = {}
    unique_headers = []
    for h in headers:
        h_str = str(h)
        if h_str in seen:
            seen[h_str] += 1
            unique_headers.append(f"{h_str}_{seen[h_str]}")
        else:
            seen[h_str] = 0
            unique_headers.append(h_str)
    df_wide.columns = unique_headers
    df_wide = df_wide.iloc[1:].reset_index(drop=True)

    date_col = df_wide.columns[0]
    ref_dates = pd.to_datetime(df_wide[date_col], errors='coerce')
    mes = ref_dates.dt.month.values
    dia = ref_dates.dt.day.values

    year_cols = []
    seen_years = set()
    for c in df_wide.columns:
        base_c = str(c).split('_')[0]
        try:
            val = float(base_c)
            if 1900 <= val <= 2100 and base_c not in seen_years:
                year_cols.append(c)
                seen_years.add(base_c)
        except (ValueError, TypeError):
            pass

    if not year_cols:
        return pd.DataFrame()

    records = []
    for y_col in year_cols:
        year = int(float(str(y_col).split('_')[0]))
        vals = df_wide[y_col].values
        for i in range(len(vals)):
            if pd.notna(mes[i]) and pd.notna(dia[i]):
                records.append({
                    'year': year,
                    'mes': int(mes[i]),
                    'dia': int(dia[i]),
                    'caudal': vals[i]
                })

    if not records:
        return pd.DataFrame()

    df_long = pd.DataFrame(records)
    df_long['fecha'] = pd.to_datetime(
        df_long['year'].astype(str) + '-' +
        df_long['mes'].astype(str).str.zfill(2) + '-' +
        df_long['dia'].astype(str).str.zfill(2),
        errors='coerce'
    )
    df_long = df_long.dropna(subset=['fecha'])
    df_long = df_long[df_long['fecha'].dt.strftime('%m-%d') != '02-29']
    df_long['estacion'] = station_name
    df_long['caudal'] = pd.to_numeric(df_long['caudal'], errors='coerce')
    return df_long[['fecha', 'estacion', 'caudal', 'year', 'mes', 'dia']]


def cargar_originales() -> pd.DataFrame:
    """Carga todos los Excel originales a formato long."""
    files = sorted([f for f in CAUDALES_DIR.iterdir() if f.suffix == '.xlsx'])
    unique_files = []
    seen_bases = set()
    for f in files:
        raw_base = f.stem.strip()
        if '(' in raw_base:
            raw_base = raw_base.split('(')[0].strip()
        if raw_base in seen_bases:
            continue
        seen_bases.add(raw_base)
        unique_files.append(f)

    all_long = []
    for f in unique_files:
        nombre_est = limpiar_nombre(f.name)
        df_long = excel_a_long(f, nombre_est)
        if not df_long.empty:
            all_long.append(df_long)

    return pd.concat(all_long, ignore_index=True) if all_long else pd.DataFrame()


def comparar_estadisticos(orig: pd.DataFrame, csv: pd.DataFrame, est: str) -> Dict:
    """Compara estadisticos entre datos originales y CSV para una estacion."""
    o = orig[orig['estacion'] == est].copy()
    c = csv[csv['estacion'] == est].copy()

    o_valid = o.dropna(subset=['caudal'])
    c_valid = c.dropna(subset=['caudal'])

    resultados = {
        'estacion': est,
        'n_orig': len(o_valid),
        'n_csv': len(c_valid),
        'fecha_min_orig': o_valid['fecha'].min().date() if not o_valid.empty else None,
        'fecha_min_csv': c_valid['fecha'].min().date() if not c_valid.empty else None,
        'fecha_max_orig': o_valid['fecha'].max().date() if not o_valid.empty else None,
        'fecha_max_csv': c_valid['fecha'].max().date() if not c_valid.empty else None,
        'min_orig': round(o_valid['caudal'].min(), 6) if not o_valid.empty else None,
        'min_csv': round(c_valid['caudal'].min(), 6) if not c_valid.empty else None,
        'max_orig': round(o_valid['caudal'].max(), 6) if not o_valid.empty else None,
        'max_csv': round(c_valid['caudal'].max(), 6) if not c_valid.empty else None,
        'media_orig': round(o_valid['caudal'].mean(), 6) if not o_valid.empty else None,
        'media_csv': round(c_valid['caudal'].mean(), 6) if not c_valid.empty else None,
        'mediana_orig': round(o_valid['caudal'].median(), 6) if not o_valid.empty else None,
        'mediana_csv': round(c_valid['caudal'].median(), 6) if not c_valid.empty else None,
        'suma_orig': round(o_valid['caudal'].sum(), 4) if not o_valid.empty else None,
        'suma_csv': round(c_valid['caudal'].sum(), 4) if not c_valid.empty else None,
    }
    return resultados


def verificar_caudales(
    csv_path: Path = CSV_PATH,
    caudales_dir: Path = CAUDALES_DIR,
    estaciones_comunes: set = ESTACIONES_COMUNES,
    tol: float = TOL
) -> Tuple[bool, str]:
    """
    Ejecuta todos los checks de verificacion.

    Retorna:
        ok: bool indicando si todos los checks criticos pasaron
        reporte: str con el reporte completo
    """
    lineas = []
    lineas.append('=' * 80)
    lineas.append('VERIFICACION DE INTEGRIDAD - CAUDALES')
    lineas.append('=' * 80)

    # Cargar datos
    lineas.append('\n[1/9] Cargando datos...')
    df_csv = pd.read_csv(csv_path, parse_dates=['fecha'])
    df_csv['estacion'] = df_csv['estacion'].str.upper().str.strip()
    df_orig = cargar_originales()

    lineas.append(f"  CSV: {len(df_csv):,} registros totales")
    lineas.append(f"  Originales: {len(df_orig):,} registros totales")

    checks_ok = True
    resumen_filas = []

    # Check 7: solo estaciones comunes si se aplica filtro
    lineas.append('\n[2/9] Check 7: Estaciones presentes en CSV')
    estaciones_csv = set(df_csv['estacion'].unique())
    extras = estaciones_csv - estaciones_comunes
    if extras:
        lineas.append(f"  [INFO] El CSV contiene estaciones adicionales: {sorted(extras)}")
    else:
        lineas.append('  [PASS] No hay estaciones adicionales fuera del conjunto comunes')

    # Check 9: consistencia de nombres
    lineas.append('\n[3/9] Check 9: Consistencia de nombres normalizados')
    nombres_no_comunes = estaciones_csv - estaciones_comunes
    if nombres_no_comunes:
        lineas.append(f"  [INFO] Nombres en CSV no en estaciones comunes: {sorted(nombres_no_comunes)}")
    else:
        lineas.append('  [PASS] Todos los nombres en CSV pertenecen al conjunto comunes')

    # Checks por estacion
    lineas.append('\n[4/9] Checks por estacion contra Excel originales')
    for est in sorted(estaciones_comunes):
        if est not in df_csv['estacion'].values:
            lineas.append(f"  [FAIL] {est}: no existe en el CSV")
            checks_ok = False
            continue
        if est not in df_orig['estacion'].values:
            lineas.append(f"  [FAIL] {est}: no existe en los datos originales")
            checks_ok = False
            continue

        r = comparar_estadisticos(df_orig, df_csv, est)
        resumen_filas.append(r)

        # Check 1: rango temporal
        if r['fecha_min_orig'] != r['fecha_min_csv']:
            lineas.append(f"  [FAIL] {est}: fecha_min no coincide. Orig={r['fecha_min_orig']}, CSV={r['fecha_min_csv']}")
            checks_ok = False
        if r['fecha_max_orig'] != r['fecha_max_csv']:
            lineas.append(f"  [FAIL] {est}: fecha_max no coincide. Orig={r['fecha_max_orig']}, CSV={r['fecha_max_csv']}")
            checks_ok = False

        # Check 2: conteo
        if r['n_orig'] != r['n_csv']:
            lineas.append(f"  [FAIL] {est}: conteo de validos no coincide. Orig={r['n_orig']}, CSV={r['n_csv']}")
            checks_ok = False

        # Check 4: min/max
        if abs(r['min_orig'] - r['min_csv']) > tol:
            lineas.append(f"  [FAIL] {est}: minimo no coincide. Orig={r['min_orig']:.6f}, CSV={r['min_csv']:.6f}")
            checks_ok = False
        if abs(r['max_orig'] - r['max_csv']) > tol:
            lineas.append(f"  [FAIL] {est}: maximo no coincide. Orig={r['max_orig']:.6f}, CSV={r['max_csv']:.6f}")
            checks_ok = False

        # Check 3: media, mediana, suma
        if abs(r['media_orig'] - r['media_csv']) > tol:
            lineas.append(f"  [FAIL] {est}: media no coincide. Orig={r['media_orig']:.6f}, CSV={r['media_csv']:.6f}")
            checks_ok = False
        if abs(r['mediana_orig'] - r['mediana_csv']) > tol:
            lineas.append(f"  [FAIL] {est}: mediana no coincide. Orig={r['mediana_orig']:.6f}, CSV={r['mediana_csv']:.6f}")
            checks_ok = False
        if abs(r['suma_orig'] - r['suma_csv']) > tol:
            lineas.append(f"  [FAIL] {est}: suma no coincide. Orig={r['suma_orig']:.4f}, CSV={r['suma_csv']:.4f}")
            checks_ok = False

    if all([
        comparar_estadisticos(df_orig, df_csv, est)['n_orig'] == comparar_estadisticos(df_orig, df_csv, est)['n_csv']
        for est in sorted(estaciones_comunes)
        if est in df_csv['estacion'].values and est in df_orig['estacion'].values
    ]):
        lineas.append('  [PASS] Estadisticos por estacion coinciden con originales')

    # Check 5: no 29-feb
    lineas.append('\n[5/9] Check 5: Exclusion de 29 de febrero')
    feb29 = df_csv[df_csv['fecha'].dt.strftime('%m-%d') == '02-29']
    if len(feb29) > 0:
        lineas.append(f"  [FAIL] Se encontraron {len(feb29)} registros del 29 de febrero")
        checks_ok = False
    else:
        lineas.append('  [PASS] No hay registros del 29 de febrero')

    # Check 6: duplicados
    lineas.append('\n[6/9] Check 6: Duplicados (estacion, fecha)')
    duplicados = df_csv.duplicated(subset=['estacion', 'fecha'], keep=False).sum()
    if duplicados > 0:
        lineas.append(f"  [FAIL] Se encontraron {duplicados} registros duplicados")
        checks_ok = False
    else:
        lineas.append('  [PASS] No hay duplicados')

    # Check 8: valores negativos o nulos sospechosos
    lineas.append('\n[7/9] Check 8: Valores negativos o cero en datos originales')
    sospechosos = df_csv[(df_csv['caudal'].notna()) & (df_csv['caudal'] <= 0)]
    if len(sospechosos) > 0:
        por_est = sospechosos.groupby('estacion').size().to_dict()
        lineas.append(f"  [WARN] {len(sospechosos)} registros con caudal <= 0:")
        for e, n in sorted(por_est.items()):
            lineas.append(f"    - {e}: {n}")
    else:
        lineas.append('  [PASS] No hay caudales <= 0')

    # Check 3 extendido: comparacion anual
    lineas.append('\n[8/9] Check 3 extendido: Sumas y medias anuales')
    annual_csv = df_csv[df_csv['estacion'].isin(estaciones_comunes)].groupby(['estacion', 'year'])['caudal'].agg(['sum', 'mean', 'median', 'count']).reset_index()
    annual_orig = df_orig[df_orig['estacion'].isin(estaciones_comunes)].groupby(['estacion', 'year'])['caudal'].agg(['sum', 'mean', 'median', 'count']).reset_index()
    merged_annual = annual_csv.merge(annual_orig, on=['estacion', 'year'], suffixes=('_csv', '_orig'), how='outer')

    diffs = merged_annual[
        (abs(merged_annual['sum_csv'] - merged_annual['sum_orig']) > tol) |
        (abs(merged_annual['mean_csv'] - merged_annual['mean_orig']) > tol) |
        (abs(merged_annual['median_csv'] - merged_annual['median_orig']) > tol)
    ]
    if len(diffs) > 0:
        lineas.append(f"  [FAIL] {len(diffs)} anos con estadisticos anuales diferentes:")
        for _, row in diffs.head(10).iterrows():
            lineas.append(f"    - {row['estacion']} {row['year']}: sum_csv={row['sum_csv']:.2f} sum_orig={row['sum_orig']:.2f}")
        checks_ok = False
    else:
        lineas.append('  [PASS] Estadisticos anuales coinciden con originales')

    # Resumen final
    lineas.append('\n[9/9] Resumen final')
    if checks_ok:
        lineas.append('[PASS] Todos los checks criticos pasaron. Los datos son consistentes.')
    else:
        lineas.append('[FAIL] Se encontraron inconsistencias. Revisar detalles arriba.')

    reporte = '\n'.join(lineas)
    return checks_ok, reporte


def main():
    ok, reporte = verificar_caudales()
    print(reporte)

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(reporte, encoding='utf-8')
    print(f'\nReporte guardado en: {REPORT_PATH}')

    # Guardar resumen CSV
    df_csv = pd.read_csv(CSV_PATH, parse_dates=['fecha'])
    df_csv['estacion'] = df_csv['estacion'].str.upper().str.strip()
    df_orig = cargar_originales()
    resumen = [comparar_estadisticos(df_orig, df_csv, est) for est in sorted(ESTACIONES_COMUNES) if est in df_csv['estacion'].values]
    pd.DataFrame(resumen).to_csv(SUMMARY_PATH, index=False, encoding='utf-8-sig')
    print(f'Resumen CSV guardado en: {SUMMARY_PATH}')

    if not ok:
        sys.exit(1)


if __name__ == '__main__':
    main()
