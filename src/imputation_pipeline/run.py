"""
Script ejecutable del pipeline de imputacion.

INSTRUCCIONES:
1. Edita las dos variables de abajo (DATA_PATH y OUTPUT_DIR).
2. Ejecuta: python src/imputation_pipeline/run.py

El pipeline automaticamente:
   - Carga datos crudos en formato long
   - Descubre y selecciona las MEJORES curvas H-H
   - Aplica imputacion en cascada: L1 -> L2 -> L3
   - Aplica hard rules de rango
   - Genera dataset final con tracking de metodos
"""

import sys
from pathlib import Path

# ============================================================
# CONFIGURACION DEL USUARIO - EDITAR SOLO ESTAS LINEAS
# ============================================================

# Ruta al CSV con datos crudos (formato long: station, level, date)
# Ejemplo: DATA_PATH = r"C:\Datos\mis_crudos.csv"
DATA_PATH = r"C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\backend\data\processed\Resumen_Crudos_IDEAM_2026.csv"

# Carpeta donde se guardaran los resultados
# Ejemplo: OUTPUT_DIR = r"C:\Resultados\imputacion"
OUTPUT_DIR = r"C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\backend\data\processed\imputation\pipeline_output"

# Formato de fecha en el CSV (dejar por defecto si es %d-%m-%Y)
DATE_FORMAT = "%d-%m-%Y"

# ============================================================
# NO MODIFICAR NADA DEBAJO DE ESTA LINEA
# ============================================================

# Agregar src/ al path para importar el paquete
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from imputation_pipeline.pipeline import run_pipeline


if __name__ == '__main__':
    print("=" * 70)
    print("PIPELINE DE IMPUTACION - EJECUCION")
    print("=" * 70)
    print(f"Datos de entrada : {DATA_PATH}")
    print(f"Salida           : {OUTPUT_DIR}")
    print(f"Formato fecha    : {DATE_FORMAT}")
    print("")

    run_pipeline(
        data_path=DATA_PATH,
        output_dir=OUTPUT_DIR,
        date_format=DATE_FORMAT,
    )
