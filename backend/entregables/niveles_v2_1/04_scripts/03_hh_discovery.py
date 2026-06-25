#!/usr/bin/env python3
"""
03_hh_discovery.py
==================

PASO 1 del pipeline v2.1: descubrimiento y seleccion de modelos H-H
sin restriccion de orientacion aguas arriba/aguas abajo.

Salidas:
- Tabla_Modelos_HH.csv
- Tabla_Modelos_HH_Seleccionados.csv
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import pandas as pd
from imputation_pipeline_v2_1.loaders import load_raw_data
from imputation_pipeline_v2_1.hh_selector import run_hh_discovery

DATA_PATH = (
    PROJECT_ROOT
    / "backend"
    / "data"
    / "work"
    / "imputation_v2_1"
    / "output"
    / "Resumen_Crudos_IDEAM_2026_v2_1.csv"
)
OUTPUT_DIR = (
    PROJECT_ROOT / "backend" / "data" / "work" / "imputation_v2_1" / "output"
)


if __name__ == "__main__":
    output_dir = Path(OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("PASO 1: Descubrimiento de modelos H-H v2.1")
    print("=" * 70)
    print(f"Datos de entrada : {DATA_PATH}")
    print(f"Salida           : {OUTPUT_DIR}\n")

    print("[1/2] Cargando datos crudos...")
    df_long = load_raw_data(DATA_PATH, date_format="%Y-%m-%d")
    print(f"      Registros: {len(df_long):,} | Estaciones: {df_long['NombreEstacion'].nunique()}")

    print("\n[2/2] Descubriendo y seleccionando modelos H-H...")
    modelos, df_todas = run_hh_discovery(df_long)

    df_todas.to_csv(output_dir / "Tabla_Modelos_HH.csv", index=False)
    print(f"\nGuardado: Tabla_Modelos_HH.csv ({len(df_todas)} parejas)")

    if modelos:
        df_sel = pd.DataFrame(modelos)
        df_sel.to_csv(output_dir / "Tabla_Modelos_HH_Seleccionados.csv", index=False)
        print(f"Guardado: Tabla_Modelos_HH_Seleccionados.csv ({len(df_sel)} modelos)")

    print("\n" + "=" * 70)
    print("PASO 1 COMPLETADO")
    print("=" * 70)
    print("Revisa la tabla de modelos seleccionados antes de continuar.")
    print("Si todo es correcto, ejecuta ahora:")
    print("  py backend/scripts/imputation_v2_1/04_run_imputation.py")
