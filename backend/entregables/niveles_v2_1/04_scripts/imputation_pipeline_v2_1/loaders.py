"""
loaders.py
==========

Carga y preprocesamiento de datos crudos para el pipeline v2.1.
"""

import pandas as pd
from pathlib import Path
from .config import (
    INPUT_COL_STATION,
    INPUT_COL_LEVEL,
    INPUT_COL_DATE,
    INPUT_DATE_FORMAT,
    COL_STATION,
    COL_LEVEL,
    COL_DATE,
    GEO_ORDER,
    RANGES_CSV_NAME,
)


def load_raw_data(csv_path, date_format=None):
    """
    Carga datos crudos desde CSV en formato LONG.

    Columnas esperadas: station, level, date
    """
    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"No se encontro el archivo: {csv_path}")

    df = pd.read_csv(csv_path)

    required = [INPUT_COL_STATION, INPUT_COL_LEVEL, INPUT_COL_DATE]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(
            f"Columnas faltantes en el CSV: {missing}. "
            f"Columnas encontradas: {list(df.columns)}"
        )

    fmt = date_format or INPUT_DATE_FORMAT
    df[INPUT_COL_DATE] = pd.to_datetime(df[INPUT_COL_DATE], format=fmt, errors="coerce")

    df = df.rename(
        columns={
            INPUT_COL_STATION: COL_STATION,
            INPUT_COL_LEVEL: COL_LEVEL,
            INPUT_COL_DATE: COL_DATE,
        }
    )

    n_null_dates = df[COL_DATE].isna().sum()
    if n_null_dates > 0:
        print(f"  [AVISO] {n_null_dates} fechas no pudieron parsearse y seran descartadas.")
        df = df.dropna(subset=[COL_DATE])

    return df[[COL_STATION, COL_DATE, COL_LEVEL]].copy()


def to_wide_format(df):
    """Convierte DataFrame LONG a formato WIDE (fechas x estaciones)."""
    wide = df.pivot(index=COL_DATE, columns=COL_STATION, values=COL_LEVEL)
    return wide


def get_station_list(df):
    """Retorna lista de estaciones unicas ordenadas geograficamente."""
    stations = df[COL_STATION].unique()
    ordered = sorted(stations, key=lambda s: GEO_ORDER.get(s, 999))
    return ordered


def load_official_ranges(ranges_csv_path):
    """
    Carga el rango oficial de cada estacion desde el CSV de resumen de rangos.
    Retorna dict: {estacion: (fecha_inicio, fecha_fin)}
    """
    ranges_csv_path = Path(ranges_csv_path)
    if not ranges_csv_path.exists():
        raise FileNotFoundError(f"No se encontro el archivo de rangos: {ranges_csv_path}")

    df = pd.read_csv(ranges_csv_path)
    required = {"Estacion", "Fecha_Inicio", "Fecha_Fin"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Columnas faltantes en CSV de rangos: {missing}")

    df["Fecha_Inicio"] = pd.to_datetime(df["Fecha_Inicio"], errors="coerce")
    df["Fecha_Fin"] = pd.to_datetime(df["Fecha_Fin"], errors="coerce")
    df = df.dropna(subset=["Fecha_Inicio", "Fecha_Fin"])

    return {
        row["Estacion"]: (row["Fecha_Inicio"], row["Fecha_Fin"])
        for _, row in df.iterrows()
    }


def apply_range_mask(df_wide, official_ranges):
    """
    Aplica mascara de rango oficial a un DataFrame WIDE.
    Todo valor fuera del rango oficial de cada estacion se fuerza a NaN.
    Modifica el DataFrame IN-PLACE.
    """
    for col in df_wide.columns:
        if col not in official_ranges:
            continue
        start, end = official_ranges[col]
        mask_outside = (df_wide.index < start) | (df_wide.index > end)
        n_masked = mask_outside.sum()
        if n_masked > 0:
            df_wide.loc[mask_outside, col] = pd.NA
    return df_wide
