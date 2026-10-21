"""
Imputation Pipeline - Sistema de Imputacion de Datos Hidrologicos
Genera automaticamente curvas H-H, selecciona las mejores, y aplica imputacion en cascada.

Uso:
    from imputation_pipeline.pipeline import run_pipeline
    run_pipeline(
        data_path="ruta/a/datos_crudos.csv",
        output_dir="ruta/a/resultados",
        date_format="%d-%m-%Y"
    )
"""

__version__ = "1.0.0"
