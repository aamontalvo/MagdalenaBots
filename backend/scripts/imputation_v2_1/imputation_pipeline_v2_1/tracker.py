"""
tracker.py
==========

Tracking de metodos de imputacion en el dataset final.
"""

import pandas as pd
from .config import COL_DATE, COL_STATION, COL_LEVEL


def build_tracked_dataset(df_wide_final, df_wide_orig, df_wide_after_l1, official_ranges=None):
    """
    Construye dataset LONG con tracking de nivel de imputacion y metodo.

    Columnas de salida:
        Fecha, NombreEstacion, Cota, Nivel_Imputacion, Metodo

    Si se proporciona official_ranges, se descartan filas fuera del rango oficial.
    """
    df_long = (
        df_wide_final.reset_index()
        .melt(
            id_vars=[df_wide_final.index.name or COL_DATE],
            var_name=COL_STATION,
            value_name=COL_LEVEL,
        )
    )

    fecha_col = df_long.columns[0]
    if fecha_col != COL_DATE:
        df_long = df_long.rename(columns={fecha_col: COL_DATE})

    df_long["Nivel_Imputacion"] = 0
    df_long["Metodo"] = "Original"

    for col in df_wide_final.columns:
        mask_orig_nan = df_wide_orig[col].isna()
        mask_l1 = mask_orig_nan & df_wide_after_l1[col].notna()
        mask_l2 = (
            mask_orig_nan & df_wide_after_l1[col].isna() & df_wide_final[col].notna()
        )

        fechas_l1 = df_wide_orig.index[mask_l1]
        fechas_l2 = df_wide_orig.index[mask_l2]

        df_long.loc[
            (df_long[COL_STATION] == col) & df_long[COL_DATE].isin(fechas_l1),
            ["Nivel_Imputacion", "Metodo"],
        ] = [1, "L1_Interpolacion"]

        df_long.loc[
            (df_long[COL_STATION] == col) & df_long[COL_DATE].isin(fechas_l2),
            ["Nivel_Imputacion", "Metodo"],
        ] = [2, f"L2_HH_{col}_quadratic"]

    if official_ranges:
        mask_keep = pd.Series(False, index=df_long.index)
        for col in df_long[COL_STATION].unique():
            if col not in official_ranges:
                continue
            start, end = official_ranges[col]
            mask_station = df_long[COL_STATION] == col
            mask_in_range = (df_long[COL_DATE] >= start) & (df_long[COL_DATE] <= end)
            mask_keep = mask_keep | (mask_station & mask_in_range)
        df_long = df_long[mask_keep]

    return df_long
