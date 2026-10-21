"""
Tracking de metodos de imputacion en el dataset final.
Solo L1 (interpolacion local) y L2 (curvas H-H cuadraticas).
"""
import pandas as pd


def build_tracked_dataset(df_wide_final, df_wide_orig, df_wide_after_l1):
    """
    Construye dataset LONG con tracking de nivel de imputacion y metodo.

    Parametros:
        df_wide_final     : DataFrame wide despues de L1+L2
        df_wide_orig      : DataFrame wide original (solo crudos)
        df_wide_after_l1  : DataFrame wide despues de L1 (para detectar L1)

    Retorna:
        DataFrame LONG con columnas:
            Fecha, NombreEstacion, Cota, Nivel_Imputacion, Metodo
    """
    from .config import COL_DATE, COL_STATION, COL_LEVEL

    df_long = df_wide_final.reset_index().melt(
        id_vars=[df_wide_final.index.name or COL_DATE],
        var_name=COL_STATION,
        value_name=COL_LEVEL
    ).dropna(subset=[COL_LEVEL])

    # Renombrar columna de fecha si es necesario
    fecha_col = df_long.columns[0]
    if fecha_col != COL_DATE:
        df_long = df_long.rename(columns={fecha_col: COL_DATE})

    df_long['Nivel_Imputacion'] = 0
    df_long['Metodo'] = 'Original'

    # Determinar metodo por estacion y fecha
    for col in df_wide_final.columns:
        mask_orig_nan = df_wide_orig[col].isna()

        # L1: valido despues de L1, pero NaN en originales
        mask_l1 = mask_orig_nan & df_wide_after_l1[col].notna()

        # L2: valido en final, pero aun NaN despues de L1
        mask_l2 = mask_orig_nan & df_wide_after_l1[col].isna() & df_wide_final[col].notna()

        fechas_l1 = df_wide_orig.index[mask_l1]
        fechas_l2 = df_wide_orig.index[mask_l2]

        df_long.loc[
            (df_long[COL_STATION] == col) & df_long[COL_DATE].isin(fechas_l1),
            ['Nivel_Imputacion', 'Metodo']
        ] = [1, 'L1_Interpolacion']

        df_long.loc[
            (df_long[COL_STATION] == col) & df_long[COL_DATE].isin(fechas_l2),
            ['Nivel_Imputacion', 'Metodo']
        ] = [2, f"L2_HH_{col}_quadratic"]

    return df_long
