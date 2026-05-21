"""
Imputadores de nivel L1, L2 y L3.
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from .config import L1_MAX_GAP, L1_KERNEL, MISSFOREST_ESTIMATORS


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


def apply_l3_missforest(df_wide, target_col, n_estimators=MISSFOREST_ESTIMATORS):
    """
    Imputacion multivariada no parametrica con Random Forest.

    Retorna:
        numero de valores imputados
    """
    if target_col not in df_wide.columns:
        return 0

    target_nan = df_wide[target_col].isna()
    n_nan = target_nan.sum()
    if n_nan == 0:
        return 0

    feature_cols = [c for c in df_wide.columns if c != target_col]
    if len(feature_cols) == 0:
        return 0

    train_mask = df_wide[target_col].notna()
    if train_mask.sum() < 10:
        return 0

    X_train = df_wide.loc[train_mask, feature_cols].copy()
    y_train = df_wide.loc[train_mask, target_col].copy()

    for col in X_train.columns:
        X_train[col] = X_train[col].fillna(X_train[col].median())

    rf = RandomForestRegressor(n_estimators=n_estimators, random_state=42, n_jobs=-1)
    rf.fit(X_train, y_train)

    X_pred = df_wide.loc[target_nan, feature_cols].copy()
    for col in X_pred.columns:
        X_pred[col] = X_pred[col].fillna(X_pred[col].median())

    y_pred = rf.predict(X_pred)
    df_wide.loc[target_nan, target_col] = y_pred
    return n_nan
