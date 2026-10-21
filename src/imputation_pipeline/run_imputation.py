"""
PASO 2: Imputacion en cascada (L1 -> L2)
=========================================

Este script aplica la imputacion usando los modelos H-H ya descubiertos
por run_hh_discovery.py.

NO utiliza missForest. El pipeline se limita a:
  L1 : Interpolacion local (gaps <= 3 dias)
  L2 : Curvas H-H cuadraticas (modelos auto-descubiertos)

REQUIERE:
  - Tabla_Modelos_HH_Seleccionados.csv  (generado por el paso 1)
  - Datos crudos originales

SALIDAS:
  - Datos_Imputados.csv          (dataset final con tracking L1/L2)
  - Resumen_Imputacion.csv       (estadisticas por estacion)
  - log_imputacion.txt           (log de ejecucion)

INSTRUCCIONES:
  1. Asegurate de haber ejecutado run_hh_discovery.py primero.
  2. Edita DATA_PATH y OUTPUT_DIR abajo (deben coincidir con el paso 1).
  3. Ejecuta: python src/imputation_pipeline/run_imputation.py
  4. Este paso es rapido (tipicamente < 10 segundos).
"""

import sys
from pathlib import Path

# ============================================================
# CONFIGURACION DEL USUARIO - EDITAR SOLO ESTAS LINEAS
# ============================================================
DATA_PATH = r"C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\backend\data\processed\Resumen_Crudos_IDEAM_2026.csv"
OUTPUT_DIR = r"C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\backend\data\processed\imputation\pipeline_output"
DATE_FORMAT = "%d-%m-%Y"
# ============================================================

project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import pandas as pd
import time
from imputation_pipeline.loaders import load_raw_data, to_wide_format
from imputation_pipeline.imputers import apply_l1_interpolation, apply_l2_hh_imputation
from imputation_pipeline.hard_rules import compute_original_ranges, apply_hard_rule_clip, verify_no_outliers
from imputation_pipeline.tracker import build_tracked_dataset
from imputation_pipeline.config import DESCARTADAS


def load_selected_models(output_dir):
    """Carga modelos H-H seleccionados desde CSV generado por paso 1."""
    path = Path(output_dir) / 'Tabla_Modelos_HH_Seleccionados.csv'
    if not path.exists():
        raise FileNotFoundError(
            f"No se encontro {path}.\n"
            "Ejecuta primero: python src/imputation_pipeline/run_hh_discovery.py"
        )
    df = pd.read_csv(path)
    return df.to_dict('records')


if __name__ == '__main__':
    output_dir = Path(OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)
    log_lines = []

    def log(msg):
        print(msg)
        log_lines.append(msg)

    log("=" * 70)
    log("PASO 2: Imputacion en cascada (L1 -> L2)")
    log("=" * 70)
    log(f"Datos de entrada : {DATA_PATH}")
    log(f"Salida           : {OUTPUT_DIR}")
    log("")

    # [1] Cargar datos y modelos
    log("[1/5] Cargando datos crudos...")
    t0 = time.time()
    df_long = load_raw_data(DATA_PATH, date_format=DATE_FORMAT)
    log(f"      {time.time()-t0:.1f}s - {len(df_long):,} registros")

    log("[2/5] Cargando modelos H-H seleccionados...")
    modelos = load_selected_models(output_dir)
    log(f"      {len(modelos)} modelos cargados")
    for m in modelos:
        log(f"      {m['objetivo']} <- {m['donante']}  (R2={m['r2']:.4f})")

    # [2] Preparar formato wide
    log("\n[3/5] Preparando datos...")
    t0 = time.time()
    df_wide_orig = to_wide_format(df_long)
    rangos = compute_original_ranges(df_long)
    log(f"      {time.time()-t0:.1f}s - {len(df_wide_orig):,} fechas x {len(df_wide_orig.columns)} estaciones")

    # [3] L1 - Interpolacion
    log("\n[4/5] Aplicando L1 - Interpolacion local...")
    t0 = time.time()
    df_wide_l1 = df_wide_orig.copy()
    l1_counts = {}
    for col in df_wide_l1.columns:
        s_imp, mask = apply_l1_interpolation(df_wide_l1[col])
        df_wide_l1[col] = s_imp
        l1_counts[col] = int(mask.sum())
    total_l1 = sum(l1_counts.values())
    log(f"      {time.time()-t0:.1f}s - Total L1: {total_l1:,}")

    # [4] L2 - H-H
    log("\n[5/5] Aplicando L2 - H-H cuadratica...")
    t0 = time.time()
    df_wide_l2 = df_wide_l1.copy()
    l2_counts = {}
    for m in modelos:
        n = apply_l2_hh_imputation(df_wide_l2, m)
        l2_counts[m['objetivo']] = n
        if n > 0:
            log(f"      {m['objetivo']:<18} <- {m['donante']:<18} : {n:>4} valores")
    total_l2 = sum(l2_counts.values())
    log(f"      {time.time()-t0:.1f}s - Total L2: {total_l2:,}")

    # Hard rules
    log("\nAplicando hard rules...")
    t0 = time.time()
    clipped = apply_hard_rule_clip(df_wide_l2, rangos)
    if clipped:
        log(f"      Valores clipeados: {sum(clipped.values())}")
    violations = verify_no_outliers(df_wide_l2, rangos)
    log(f"      {time.time()-t0:.1f}s - Violaciones: {len(violations)}")

    # Tracking y guardado
    log("\nGuardando resultados...")
    df_long_final = build_tracked_dataset(df_wide_l2, df_wide_orig, df_wide_l1)
    df_long_final.to_csv(output_dir / 'Datos_Imputados.csv', index=False)
    log(f"      Datos_Imputados.csv  ({len(df_long_final):,} registros)")

    # Resumen
    resumen = []
    for col in df_wide_l2.columns:
        n_total = len(df_wide_l2[col])
        n_nan = df_wide_l2[col].isna().sum()
        is_desc = col in DESCARTADAS
        resumen.append({
            'Estacion': col, 'Total': n_total, 'NaN_Restantes': n_nan,
            'Cobertura_pct': round((n_total - n_nan) / n_total * 100, 2),
            'L1': l1_counts.get(col, 0), 'L2': l2_counts.get(col, 0),
            'Descartada': is_desc, 'Status': 'OK' if (n_nan == 0 or is_desc) else 'INCOMPLETA',
        })
    df_resumen = pd.DataFrame(resumen)
    df_resumen.to_csv(output_dir / 'Resumen_Imputacion.csv', index=False)
    log(f"      Resumen_Imputacion.csv")

    # Log
    with open(output_dir / 'log_imputacion.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(log_lines) + '\n')

    # Reporte final
    log("\n" + "=" * 70)
    log("PASO 2 COMPLETADO")
    log("=" * 70)
    log(f"Dataset final   : {len(df_long_final):,} registros")
    log(f"Imputados L1    : {total_l1:,}")
    log(f"Imputados L2    : {total_l2:,}")
    log(f"Total imputados : {total_l1 + total_l2:,}")

    no_desc = df_resumen[~df_resumen['Descartada']]
    incompletas = no_desc[no_desc['Status'] == 'INCOMPLETA']
    if len(incompletas) == 0:
        log("[EXITO] Todas las estaciones no descartadas tienen 100% cobertura!")
    else:
        log(f"[ALERTA] {len(incompletas)} estaciones incompletas:")
        for _, row in incompletas.iterrows():
            log(f"         - {row['Estacion']}: {row['NaN_Restantes']} NaN")
