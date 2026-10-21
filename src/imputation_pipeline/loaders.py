"""
Carga y preprocesamiento de datos crudos.
"""
import pandas as pd
from pathlib import Path
from .config import (
    INPUT_COL_STATION, INPUT_COL_LEVEL, INPUT_COL_DATE,
    INPUT_DATE_FORMAT, COL_STATION, COL_LEVEL, COL_DATE
)


def load_raw_data(csv_path, date_format=None):
    """
    Carga datos crudos desde CSV en formato LONG.

    Parametros:
        csv_path : str o Path
            Ruta al CSV con columnas: station, level, date
        date_format : str, opcional
            Formato de fecha. Por defecto: '%d-%m-%Y'

    Retorna:
        DataFrame con columnas: NombreEstacion, Fecha, Cota
    """
    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"No se encontro el archivo: {csv_path}")

    df = pd.read_csv(csv_path)

    # Validar columnas requeridas
    required = [INPUT_COL_STATION, INPUT_COL_LEVEL, INPUT_COL_DATE]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Columnas faltantes en el CSV: {missing}. "
                         f"Columnas encontradas: {list(df.columns)}")

    fmt = date_format or INPUT_DATE_FORMAT
    df[INPUT_COL_DATE] = pd.to_datetime(df[INPUT_COL_DATE], format=fmt, errors='coerce')

    # Renombrar a estandar interno
    df = df.rename(columns={
        INPUT_COL_STATION: COL_STATION,
        INPUT_COL_LEVEL: COL_LEVEL,
        INPUT_COL_DATE: COL_DATE
    })

    # Validar fechas nulas
    n_null_dates = df[COL_DATE].isna().sum()
    if n_null_dates > 0:
        print(f"  [AVISO] {n_null_dates} fechas no pudieron parsearse y seran descartadas.")
        df = df.dropna(subset=[COL_DATE])

    return df[[COL_STATION, COL_DATE, COL_LEVEL]].copy()


def to_wide_format(df):
    """
    Convierte DataFrame LONG a formato WIDE (fechas x estaciones).
    """
    wide = df.pivot(index=COL_DATE, columns=COL_STATION, values=COL_LEVEL)
    return wide


def get_station_list(df):
    """Retorna lista de estaciones unicas ordenadas geograficamente."""
    from .config import GEO_ORDER
    stations = df[COL_STATION].unique()
    # Ordenar segun GEO_ORDER si esta disponible
    ordered = sorted(stations, key=lambda s: GEO_ORDER.get(s, 999))
    return ordered
