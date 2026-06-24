"""
hard_rules.py
=============

Restricciones de rango y coherencia fisica.
"""

import numpy as np
from .config import COL_STATION, COL_LEVEL


def compute_original_ranges(df_long):
    """Calcula el rango historico [min, max] de cada estacion usando SOLO datos originales."""
    ranges = {}
    for estacion in df_long[COL_STATION].unique():
        vals = df_long[df_long[COL_STATION] == estacion][COL_LEVEL].dropna()
        if len(vals) > 0:
            ranges[estacion] = (vals.min(), vals.max())
    return ranges


def apply_hard_rule_clip(df_wide, ranges):
    """
    Limita todos los valores al rango historico original de cada estacion.
    Modifica df_wide IN-PLACE.
    """
    clipped = {}
    for col in df_wide.columns:
        if col not in ranges:
            continue
        rmin, rmax = ranges[col]
        vals = df_wide[col]
        below = vals < rmin
        above = vals > rmax
        n_clip = below.sum() + above.sum()
        if n_clip > 0:
            df_wide.loc[below, col] = rmin
            df_wide.loc[above, col] = rmax
            clipped[col] = int(n_clip)
    return clipped


def verify_no_outliers(df_wide, ranges):
    """Verifica que no haya valores fuera del rango original."""
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
