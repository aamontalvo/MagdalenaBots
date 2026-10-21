"""
PASO 1: Descubrimiento y seleccion de modelos H-H
=================================================

Este script es RAPIDO (tipicamente < 10 segundos).
Genera TODAS las parejas H-H posibles con orientacion correcta,
entrena modelos cuadraticos, y selecciona la MEJOR donante por estacion.

SALIDAS:
  - Tabla_Modelos_HH.csv              (todas las parejas evaluadas)
  - Tabla_Modelos_HH_Seleccionados.csv (las que pasaron el umbral R2 >= 0.75)

INSTRUCCIONES:
  1. Edita DATA_PATH y OUTPUT_DIR abajo.
  2. Ejecuta: python src/imputation_pipeline/run_hh_discovery.py
  3. Revisa Tabla_Modelos_HH_Seleccionados.csv para verificar los modelos.
  4. Si todo se ve bien, ejecuta el PASO 2: run_imputation.py
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

from imputation_pipeline.loaders import load_raw_data
from imputation_pipeline.hh_selector import run_hh_discovery
import pandas as pd
from pathlib import Path


if __name__ == '__main__':
    output_dir = Path(OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("PASO 1: Descubrimiento de modelos H-H")
    print("=" * 70)
    print(f"Datos de entrada : {DATA_PATH}")
    print(f"Salida           : {OUTPUT_DIR}")
    print("")

    print("[1/2] Cargando datos crudos...")
    df_long = load_raw_data(DATA_PATH, date_format=DATE_FORMAT)
    print(f"      Registros: {len(df_long):,} | Estaciones: {df_long['NombreEstacion'].nunique()}")

    print("")
    print("[2/2] Descubriendo y seleccionando modelos H-H...")
    modelos, df_todas = run_hh_discovery(df_long)

    # Guardar resultados
    df_todas.to_csv(output_dir / 'Tabla_Modelos_HH.csv', index=False)
    print(f"\nGuardado: Tabla_Modelos_HH.csv ({len(df_todas)} parejas)")

    if modelos:
        df_sel = pd.DataFrame(modelos)
        df_sel.to_csv(output_dir / 'Tabla_Modelos_HH_Seleccionados.csv', index=False)
        print(f"Guardado: Tabla_Modelos_HH_Seleccionados.csv ({len(df_sel)} modelos)")

    print("\n" + "=" * 70)
    print("PASO 1 COMPLETADO")
    print("=" * 70)
    print("Revisa la tabla de modelos seleccionados antes de continuar.")
    print("Si todo es correcto, ejecuta ahora:")
    print("  python src/imputation_pipeline/run_imputation.py")
