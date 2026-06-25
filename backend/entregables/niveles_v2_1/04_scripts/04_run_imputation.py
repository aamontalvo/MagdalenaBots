#!/usr/bin/env python3
"""
04_run_imputation.py
====================

PASO 2 del pipeline v2.1+: imputacion en cascada L1 -> L2 -> L3.

Requiere:
- Resumen_Crudos_IDEAM_2026_v2_1.csv
- Tabla_Modelos_HH_Seleccionados.csv (generado por 03_hh_discovery.py)
- resumen_rangos_estaciones.csv (generado por 02_prepare_dataset.py)

Salidas:
- Datos_Imputados.csv
- Resumen_Imputacion.csv
- Tabla_Modelos_L3.csv
- log_imputacion.txt

Asunciones y reglas:
- No hay restriccion de orientacion geografica para donantes H-H.
- Cada estacion tiene un rango oficial; no se imputa fuera de ese rango.
- L1: interpolacion local para gaps <= 3 dias, sin tocar bordes del rango.
- L2: primera donante H-H cuadratica (mayor R2 >= 0.75).
- L3: segunda donante H-H complementaria para estaciones con cobertura < 95%
  tras L2. Se selecciona por maxima cobertura de NaN restantes con R2 >= 0.65
  y Pearson >= 0.8, entrenando solo con datos originales del objetivo.
- Hard rules: clip defensivo al rango observado original (sanity check numerico).
"""

import sys
from pathlib import Path
import time

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import pandas as pd
import numpy as np
from scipy import stats
from imputation_pipeline_v2_1.loaders import (
    load_raw_data,
    to_wide_format,
    load_official_ranges,
    apply_range_mask,
)
from imputation_pipeline_v2_1.imputers import (
    apply_l1_interpolation,
    apply_l2_hh_imputation,
    apply_l3_hh_imputation,
)
from imputation_pipeline_v2_1.hard_rules import (
    compute_original_ranges,
    apply_hard_rule_clip,
    verify_no_outliers,
)
from imputation_pipeline_v2_1.tracker import build_tracked_dataset
from imputation_pipeline_v2_1.config import DESCARTADAS

DATA_PATH = (
    PROJECT_ROOT
    / "backend"
    / "data"
    / "work"
    / "imputation_v2_1"
    / "output"
    / "Resumen_Crudos_IDEAM_2026_v2_1.csv"
)
RANGES_PATH = (
    PROJECT_ROOT
    / "backend"
    / "data"
    / "work"
    / "imputation_v2_1"
    / "output"
    / "resumen_rangos_estaciones.csv"
)
OUTPUT_DIR = (
    PROJECT_ROOT / "backend" / "data" / "work" / "imputation_v2_1" / "output"
)

COBERTURA_MIN_L3 = 95.0
R2_MIN_L3 = 0.65
PEARSON_MIN_L3 = 0.8
MIN_N_TRAIN_L3 = 50


def load_selected_models(output_dir):
    """Carga modelos H-H seleccionados desde CSV generado por paso 1."""
    path = Path(output_dir) / "Tabla_Modelos_HH_Seleccionados.csv"
    if not path.exists():
        raise FileNotFoundError(
            f"No se encontro {path}.\n"
            "Ejecuta primero: py backend/scripts/imputation_v2_1/03_hh_discovery.py"
        )
    df = pd.read_csv(path)
    return df.to_dict("records")


def select_best_l3_donor(df_wide_l2, df_wide_orig, target, official_ranges, all_stations):
    """
    Selecciona la mejor segunda donante para una estacion objetivo.
    Criterio: maxima cobertura de NaN restantes, con R2 >= 0.65 y r >= 0.8.
    """
    best = None
    best_cover = -1

    for donor in all_stations:
        if donor == target:
            continue
        model, n_imp = apply_l3_hh_imputation(
            df_wide_l2.copy(),
            target,
            donor,
            df_wide_orig,
            official_ranges,
            r2_min=R2_MIN_L3,
            pearson_min=PEARSON_MIN_L3,
            min_n_train=MIN_N_TRAIN_L3,
        )
        if model is None:
            continue
        if n_imp > best_cover:
            best_cover = n_imp
            best = {"donante": donor, "modelo": model, "n_imp": n_imp}

    return best


if __name__ == "__main__":
    output_dir = Path(OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)
    log_lines = []

    def log(msg):
        print(msg)
        log_lines.append(msg)

    log("=" * 70)
    log("PASO 2: Imputacion en cascada v2.1+ (L1 -> L2 -> L3)")
    log("=" * 70)
    log(f"Datos de entrada : {DATA_PATH}")
    log(f"Salida           : {OUTPUT_DIR}")
    log("")

    log("[1/7] Cargando datos crudos...")
    t0 = time.time()
    df_long = load_raw_data(DATA_PATH, date_format="%Y-%m-%d")
    log(f"      {time.time()-t0:.1f}s - {len(df_long):,} registros")

    log("[2/7] Cargando modelos H-H seleccionados...")
    modelos = load_selected_models(output_dir)
    log(f"      {len(modelos)} modelos cargados")
    for m in modelos:
        log(f"      {m['objetivo']} <- {m['donante']}  (R2={m['r2']:.4f})")

    log("\n[3/7] Cargando rangos oficiales de estaciones...")
    official_ranges = load_official_ranges(RANGES_PATH)
    log(f"      Rangos cargados para {len(official_ranges)} estaciones")

    log("\n[4/7] Preparando datos...")
    t0 = time.time()
    df_wide_orig = to_wide_format(df_long)
    apply_range_mask(df_wide_orig, official_ranges)
    rangos = compute_original_ranges(df_long)
    log(
        f"      {time.time()-t0:.1f}s - {len(df_wide_orig):,} fechas x "
        f"{len(df_wide_orig.columns)} estaciones"
    )

    log("\n[5/7] Aplicando L1 - Interpolacion local...")
    t0 = time.time()
    df_wide_l1 = df_wide_orig.copy()
    l1_counts = {}
    for col in df_wide_l1.columns:
        s_imp, mask = apply_l1_interpolation(df_wide_l1[col])
        df_wide_l1[col] = s_imp
        l1_counts[col] = int(mask.sum())
    total_l1 = sum(l1_counts.values())
    log(f"      {time.time()-t0:.1f}s - Total L1: {total_l1:,}")

    log("\n[6/7] Aplicando L2 - H-H cuadratica...")
    t0 = time.time()
    df_wide_l2 = df_wide_l1.copy()
    l2_counts = {}
    for m in modelos:
        n = apply_l2_hh_imputation(df_wide_l2, m, official_ranges=official_ranges)
        l2_counts[m["objetivo"]] = n
        if n > 0:
            log(f"      {m['objetivo']:<18} <- {m['donante']:<18} : {n:>4} valores")
    total_l2 = sum(l2_counts.values())
    log(f"      {time.time()-t0:.1f}s - Total L2: {total_l2:,}")

    log("\n[7/7] Aplicando L3 - Segunda donante H-H complementaria...")
    t0 = time.time()
    df_wide_l3 = df_wide_l2.copy()
    l3_counts = {}
    l3_models = []
    l3_model_dict = {}

    all_stations = list(df_wide_l3.columns)
    for col in df_wide_l3.columns:
        if col not in official_ranges:
            continue
        start, end = official_ranges[col]
        mask_range = (df_wide_l2.index >= start) & (df_wide_l2.index <= end)
        n_total = mask_range.sum()
        n_nan_l2 = df_wide_l2.loc[mask_range, col].isna().sum()
        cobertura_l2 = (n_total - n_nan_l2) / n_total * 100

        if cobertura_l2 >= COBERTURA_MIN_L3:
            continue

        log(f"      {col}: cobertura L2 = {cobertura_l2:.2f}%, buscando segunda donante...")
        best = select_best_l3_donor(df_wide_l2, df_wide_orig, col, official_ranges, all_stations)
        if best is None:
            log(f"      {col}: no se encontro donante L3 viable")
            continue

        donor = best["donante"]
        model = best["modelo"]
        model_l3, n_imp = apply_l3_hh_imputation(
            df_wide_l3,
            col,
            donor,
            df_wide_orig,
            official_ranges,
            r2_min=R2_MIN_L3,
            pearson_min=PEARSON_MIN_L3,
            min_n_train=MIN_N_TRAIN_L3,
        )
        if n_imp > 0:
            l3_counts[col] = n_imp
            l3_model_dict[col] = {"donante": donor}
            l3_models.append(
                {
                    "objetivo": col,
                    "donante": donor,
                    "r": round(model["r"], 4),
                    "r2": round(model["r2"], 4),
                    "n_train": int(model["n_train"]),
                    "n_imp": int(n_imp),
                    "a": model["a"],
                    "b": model["b"],
                    "c": model["c"],
                }
            )
            log(
                f"      {col:<18} <- {donor:<18} : {n_imp:>4} valores  "
                f"(R2={model['r2']:.4f}, r={model['r']:.4f})"
            )

    total_l3 = sum(l3_counts.values())
    log(f"      {time.time()-t0:.1f}s - Total L3: {total_l3:,}")

    if l3_models:
        pd.DataFrame(l3_models).to_csv(output_dir / "Tabla_Modelos_L3.csv", index=False)
        log(f"      Guardado: Tabla_Modelos_L3.csv")

    log("\nAplicando hard rules (clip defensivo)...")
    t0 = time.time()
    clipped = apply_hard_rule_clip(df_wide_l3, rangos, verbose=False)
    if clipped:
        log(f"      Valores clipeados: {sum(clipped.values())}")
    violations = verify_no_outliers(df_wide_l3, rangos)
    log(f"      {time.time()-t0:.1f}s - Violaciones: {len(violations)}")

    log("\nGuardando resultados...")
    df_long_final = build_tracked_dataset(
        df_wide_l3,
        df_wide_orig,
        df_wide_l1,
        df_wide_after_l2=df_wide_l2,
        official_ranges=official_ranges,
        l3_models=l3_model_dict,
    )
    df_long_final.to_csv(output_dir / "Datos_Imputados.csv", index=False)
    log(f"      Datos_Imputados.csv  ({len(df_long_final):,} registros)")

    # Backup del resultado sin L3
    df_long_l2_only = build_tracked_dataset(
        df_wide_l2,
        df_wide_orig,
        df_wide_l1,
        official_ranges=official_ranges,
    )
    df_long_l2_only.to_csv(output_dir / "Datos_Imputados_sin_L3.csv", index=False)
    log(f"      Datos_Imputados_sin_L3.csv  ({len(df_long_l2_only):,} registros)")

    resumen = []
    for col in df_wide_l3.columns:
        if col not in official_ranges:
            continue
        start, end = official_ranges[col]
        mask_range = (df_wide_l3.index >= start) & (df_wide_l3.index <= end)

        s_final = df_wide_l3.loc[mask_range, col]
        n_total_range = mask_range.sum()
        n_nan_range = s_final.isna().sum()
        is_desc = col in DESCARTADAS

        resumen.append(
            {
                "Estacion": col,
                "Fecha_Inicio": start.strftime("%Y-%m-%d"),
                "Fecha_Fin": end.strftime("%Y-%m-%d"),
                "Dias_Rango": int(n_total_range),
                "NaN_Restantes_Rango": int(n_nan_range),
                "Cobertura_Rango_pct": round((n_total_range - n_nan_range) / n_total_range * 100, 2),
                "L1": l1_counts.get(col, 0),
                "L2": l2_counts.get(col, 0),
                "L3": l3_counts.get(col, 0),
                "Descartada": is_desc,
                "Status": "OK" if (n_nan_range == 0 or is_desc) else "INCOMPLETA",
            }
        )
    df_resumen = pd.DataFrame(resumen)
    df_resumen.to_csv(output_dir / "Resumen_Imputacion.csv", index=False)
    log(f"      Resumen_Imputacion.csv")

    with open(output_dir / "log_imputacion.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines) + "\n")

    log("\n" + "=" * 70)
    log("PASO 2 COMPLETADO")
    log("=" * 70)
    log(f"Dataset final   : {len(df_long_final):,} registros")
    log(f"Imputados L1    : {total_l1:,}")
    log(f"Imputados L2    : {total_l2:,}")
    log(f"Imputados L3    : {total_l3:,}")
    log(f"Total imputados : {total_l1 + total_l2 + total_l3:,}")

    no_desc = df_resumen[~df_resumen["Descartada"]]
    incompletas = no_desc[no_desc["Status"] == "INCOMPLETA"]
    if len(incompletas) == 0:
        log("[EXITO] Todas las estaciones no descartadas tienen 100% cobertura dentro de su rango!")
    else:
        log(f"[ALERTA] {len(incompletas)} estaciones incompletas dentro de su rango:")
        for _, row in incompletas.iterrows():
            log(f"         - {row['Estacion']}: {row['NaN_Restantes_Rango']} NaN")
