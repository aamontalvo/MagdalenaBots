"""
imputers.py
===========

Imputadores de nivel L1 (interpolacion local), L2 (curvas H-H) y
L3 (segunda donante H-H complementaria).
"""

import numpy as np
import pandas as pd
from scipy import stats
from .config import L1_MAX_GAP, L1_KERNEL


def apply_l1_interpolation(series, max_gap=L1_MAX_GAP):
    """
    Interpolacion local ponderada para gaps <= max_gap dias.
    No imputa en los extremos del rango valido (si el gap toca un borde,
    se ignora porque no hay vecinos a ambos lados).

    Retorna:
        (serie_imputada, mask_imputados)
    """
    s = series.copy()
    imputed = np.zeros(len(s), dtype=bool)
    isnan = s.isna().values
    if not isnan.any():
        return s, imputed

    # Primer y ultimo indice con dato valido para no imputar fuera del rango oficial
    valid_idx = np.where(~isnan)[0]
    if len(valid_idx) == 0:
        return s, imputed
    first_valid = valid_idx[0]
    last_valid = valid_idx[-1]

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

        # No imputar si el gap toca el borde del rango valido
        if g_start <= first_valid or g_end >= last_valid + 1:
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


def train_hh_model(x, y):
    """
    Entrena un modelo H-H cuadratico entre dos series.

    Retorna:
        dict con r, r2, n_train, a, b, c
    """
    r, _ = stats.pearsonr(x, y)
    coeffs = np.polyfit(x, y, 2)
    y_pred = coeffs[0] * x**2 + coeffs[1] * x + coeffs[2]
    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0
    return {
        "r": r,
        "r2": r2,
        "n_train": len(x),
        "a": coeffs[0],
        "b": coeffs[1],
        "c": coeffs[2],
    }


def apply_l2_hh_imputation(df_wide, model, official_ranges=None):
    """
    Aplica imputacion H-H cuadratica usando el modelo seleccionado.

    Solo imputa valores dentro del rango oficial de la estacion objetivo.

    Retorna:
        numero de valores imputados
    """
    objetivo = model["objetivo"]
    donante = model["donante"]
    a, b, c = model["a"], model["b"], model["c"]

    if objetivo not in df_wide.columns or donante not in df_wide.columns:
        return 0

    dep_series = df_wide[objetivo]
    ind_series = df_wide[donante]

    mask = dep_series.isna() & ind_series.notna()
    if official_ranges and objetivo in official_ranges:
        start, end = official_ranges[objetivo]
        mask = mask & (dep_series.index >= start) & (dep_series.index <= end)

    n_imp = mask.sum()
    if n_imp == 0:
        return 0

    x = ind_series[mask].values
    y_pred = a * x**2 + b * x + c
    df_wide.loc[mask, objetivo] = y_pred
    return n_imp


def apply_l3_hh_imputation(df_wide, target, donor, df_wide_orig, official_ranges,
                           r2_min=0.65, pearson_min=0.8, min_n_train=50):
    """
    Aplica una segunda donante H-H complementaria (L3) a una estacion objetivo.

    - Entrena el modelo usando SOLO datos originales (L0) del objetivo.
    - Usa como donante valores originales o ya imputados (L1/L2/L3 previos).
    - Solo imputa donde el objetivo es NaN despues de L2 y dentro de su rango oficial.
    - Retorna (modelo, n_imputados) o (None, 0) si no cumple criterios.
    """
    if target not in df_wide.columns or donor not in df_wide.columns:
        return None, 0

    start, end = official_ranges.get(target, (df_wide.index.min(), df_wide.index.max()))
    mask_range = (df_wide.index >= start) & (df_wide.index <= end)

    y_target_full = df_wide.loc[mask_range, target]
    x_donor_full = df_wide.loc[mask_range, donor]

    # Entrenamiento: solo datos originales del target vs cualquier dato del donor
    y_train = df_wide_orig.loc[mask_range, target]
    mask_train = y_train.notna() & x_donor_full.notna()
    if mask_train.sum() < min_n_train:
        return None, 0

    model = train_hh_model(x_donor_full[mask_train].values, y_train[mask_train].values)
    if model["r2"] < r2_min or abs(model["r"]) < pearson_min:
        return None, 0

    # Aplicar solo donde target es NaN y donor tiene dato
    mask_l3 = y_target_full.isna() & x_donor_full.notna()
    n_imp = mask_l3.sum()
    if n_imp == 0:
        return model, 0

    x = x_donor_full[mask_l3].values
    y_pred = model["a"] * x**2 + model["b"] * x + model["c"]
    df_wide.loc[df_wide.index[mask_range][mask_l3], target] = y_pred

    return model, n_imp
