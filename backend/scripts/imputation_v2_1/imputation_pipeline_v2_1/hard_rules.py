"""
hard_rules.py
=============

Reglas duras (hard rules) para el pipeline de imputacion v2.1.

Nota de version v2.1+:
----------------------
Ya NO se impone ninguna restriccion de orientacion geografica (aguas arriba/
aguas abajo) ni se interpreta el rango historico como una ley fisica. El unico
proposito de las funciones aqui es:

1. Calcular el rango observado [min, max] de los datos originales por estacion.
2. Ofrecer un clip opcional a ese rango como sanity check numerico.
3. Verificar que ningun valor imputado exceda ese rango observado.

El clip es una medida defensiva, no una restriccion de modelo. Si el usuario
decide desactivarlo, puede hacerlo desde el script principal.
"""

import numpy as np
from .config import COL_STATION, COL_LEVEL


def compute_original_ranges(df_long):
    """
    Calcula el rango observado [min, max] de cada estacion usando SOLO datos
    originales (Nivel_Imputacion == 0).
    """
    ranges = {}
    for estacion in df_long[COL_STATION].unique():
        vals = df_long[
            (df_long[COL_STATION] == estacion) & (df_long.get("Nivel_Imputacion", 0) == 0)
        ][COL_LEVEL].dropna()
        if len(vals) > 0:
            ranges[estacion] = (vals.min(), vals.max())
    return ranges


def apply_hard_rule_clip(df_wide, ranges, verbose=True):
    """
    Limita todos los valores al rango observado original de cada estacion.
    Modifica df_wide IN-PLACE.

    Esta funcion es un sanity check numerico, no una restriccion fisica.
    """
    clipped = {}
    for col in df_wide.columns:
        if col not in ranges:
            continue
        rmin, rmax = ranges[col]
        vals = df_wide[col]
        below = vals < rmin
        above = vals > rmax
        n_clip = int(below.sum()) + int(above.sum())
        if n_clip > 0:
            df_wide.loc[below, col] = rmin
            df_wide.loc[above, col] = rmax
            clipped[col] = n_clip
            if verbose:
                print(f"  [CLIP] {col}: {n_clip} valores ajustados a [{rmin:.3f}, {rmax:.3f}]")
    return clipped


def verify_no_outliers(df_wide, ranges):
    """
    Verifica que no haya valores fuera del rango observado original.
    Retorna lista de violaciones (deberia estar vacia despues del clip).
    """
    violations = []
    for col in df_wide.columns:
        if col not in ranges:
            continue
        rmin, rmax = ranges[col]
        mask = (df_wide[col] < rmin) | (df_wide[col] > rmax)
        for fecha in df_wide.index[mask]:
            violations.append(
                {
                    "estacion": col,
                    "fecha": fecha,
                    "valor": df_wide.loc[fecha, col],
                    "rango_min": rmin,
                    "rango_max": rmax,
                }
            )
    return violations


def verify_temporal_bounds(df_long, official_ranges):
    """
    Verifica que no haya registros fuera del rango oficial de cada estacion.
    Retorna DataFrame de violaciones.
    """
    import pandas as pd

    violations = []
    for estacion, grp in df_long.groupby(COL_STATION):
        if estacion not in official_ranges:
            continue
        start, end = official_ranges[estacion]
        mask = (grp[COL_LEVEL].notna()) & (
            (grp[COL_DATE] < start) | (grp[COL_DATE] > end)
        )
        for _, row in grp[mask].iterrows():
            violations.append(
                {
                    "estacion": estacion,
                    "fecha": row[COL_DATE],
                    "valor": row[COL_LEVEL],
                    "rango_inicio": start,
                    "rango_fin": end,
                }
            )
    return pd.DataFrame(violations)
