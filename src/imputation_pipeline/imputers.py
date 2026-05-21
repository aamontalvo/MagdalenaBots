"""
Imputadores de nivel L1 (interpolacion local) y L2 (curvas H-H).
"""
import numpy as np
import pandas as pd
from .config import L1_MAX_GAP, L1_KERNEL


def apply_l1_interpolation(series, max_gap=L1_MAX_GAP):
    """
    Interpolacion local ponderada para gaps <= max_gap dias.

    Retorna:
        (serie_imputada, mask_imputados)
    """
    s = series.copy()
    imputed = np.zeros(len(s), dtype=bool)
    isnan = s.isna().values
    if not isnan.any():
        return s, imputed

    # Encontrar grupos de NaN consecutivos
    groups = []
    start = None
    for i, val in enumerate(isnan):
        if val and start is None:
            start = i
        elif not val and start is not None:
            groups.append((start, i))
            start = None
    if start is not None:
        groups.append((start, len(isnan)))

    for g_start, g_end in groups:
        gap_len = g_end - g_start
        if gap_len > max_gap:
            continue

        valores = []
        pesos = []
        for offset, weight in L1_KERNEL.items():
            idx = g_start + offset
            if 0 <= idx < len(s) and not pd.isna(s.iloc[idx]):
                valores.append(s.iloc[idx])
                pesos.append(weight)

        if len(valores) < 2:
            continue

        pesos = np.array(pesos)
        pesos = pesos / pesos.sum()
        imp_val = np.sum(np.array(valores) * pesos)

        for i in range(g_start, g_end):
            s.iloc[i] = imp_val
            imputed[i] = True

    return s, imputed


def apply_l2_hh_imputation(df_wide, model):
    """
    Aplica imputacion H-H cuadratica usando el modelo seleccionado.

    Retorna:
        numero de valores imputados
    """
    objetivo = model['objetivo']
    donante = model['donante']
    a, b, c = model['a'], model['b'], model['c']

    if objetivo not in df_wide.columns or donante not in df_wide.columns:
        return 0

    dep_series = df_wide[objetivo]
    ind_series = df_wide[donante]

    # Solo imputar donde el objetivo es NaN y el donante tiene dato
    mask = dep_series.isna() & ind_series.notna()
    n_imp = mask.sum()
    if n_imp == 0:
        return 0

    x = ind_series[mask].values
    y_pred = a * x**2 + b * x + c
    df_wide.loc[mask, objetivo] = y_pred
    return n_imp
