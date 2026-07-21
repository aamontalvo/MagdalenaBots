"""
hh_selector.py
==============

Generador y selector automatico de modelos Altura-Altura (H-H) v2.1.

Cambio principal: NO se restringe la orientacion aguas arriba/aguas abajo.
Se evaluan TODAS las parejas posibles (objetivo != donante) y se selecciona
la de mayor R2 que supere el umbral.
"""

import numpy as np
import pandas as pd
from scipy import stats
from .config import R2_UMBRAL, MIN_N_TRAIN, COL_STATION, COL_DATE, COL_LEVEL


def _train_hh_model(df_long, objetivo, donante):
    """
    Entrena modelo cuadratico H-H para una pareja (objetivo, donante).
    Usa SOLO datos originales concurrentes (sin NaN en ninguna de las dos).
    """
    dep_data = (
        df_long[df_long[COL_STATION] == objetivo][[COL_DATE, COL_LEVEL]]
        .rename(columns={COL_LEVEL: "dep"})
    )
    ind_data = (
        df_long[df_long[COL_STATION] == donante][[COL_DATE, COL_LEVEL]]
        .rename(columns={COL_LEVEL: "ind"})
    )

    merged = pd.merge(dep_data, ind_data, on=COL_DATE, how="inner").dropna()
    n = len(merged)

    if n < MIN_N_TRAIN:
        return None, n

    x = merged["ind"].values
    y = merged["dep"].values

    r, _ = stats.pearsonr(x, y)

    coeffs = np.polyfit(x, y, 2)
    y_pred = coeffs[0] * x**2 + coeffs[1] * x + coeffs[2]

    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0

    model = {
        "objetivo": objetivo,
        "donante": donante,
        "r": r,
        "r2": r2,
        "n_train": n,
        "a": coeffs[0],
        "b": coeffs[1],
        "c": coeffs[2],
        "equation": f"H = {coeffs[0]:.6f}*H^2 + {coeffs[1]:.6f}*H + {coeffs[2]:.6f}",
    }
    return model, n


def discover_all_hh_models(df_long):
    """
    Genera y evalua TODAS las parejas H-H posibles sin restriccion de orientacion.
    """
    stations = df_long[COL_STATION].unique()
    results = []

    for objetivo in stations:
        for donante in stations:
            if objetivo == donante:
                continue

            model, n = _train_hh_model(df_long, objetivo, donante)
            if model is None:
                results.append(
                    {
                        "objetivo": objetivo,
                        "donante": donante,
                        "r": np.nan,
                        "r2": np.nan,
                        "n_train": n,
                        "a": np.nan,
                        "b": np.nan,
                        "c": np.nan,
                        "equation": "SIN_DATOS_SUFICIENTES",
                        "seleccionado": False,
                        "motivo": "n_insuficiente" if n < MIN_N_TRAIN else "otro",
                    }
                )
            else:
                results.append(
                    {
                        "objetivo": objetivo,
                        "donante": donante,
                        "r": model["r"],
                        "r2": model["r2"],
                        "n_train": model["n_train"],
                        "a": model["a"],
                        "b": model["b"],
                        "c": model["c"],
                        "equation": model["equation"],
                        "seleccionado": False,
                        "motivo": "",
                    }
                )

    return pd.DataFrame(results)


def select_best_hh_models(df_evaluado):
    """
    Selecciona la MEJOR donante por estacion objetivo (mayor R2 >= umbral).
    """
    if df_evaluado.empty:
        return [], df_evaluado

    seleccionados = []
    df = df_evaluado.copy()
    df["seleccionado"] = False
    df["motivo"] = df["motivo"].fillna("")

    for objetivo in df["objetivo"].unique():
        candidatos = df[(df["objetivo"] == objetivo) & (df["r2"].notna())]
        if candidatos.empty:
            continue

        candidatos = candidatos.sort_values("r2", ascending=False)
        mejor = candidatos.iloc[0]

        if mejor["r2"] >= R2_UMBRAL:
            idx = mejor.name
            df.loc[idx, "seleccionado"] = True
            df.loc[idx, "motivo"] = "mejor_r2"

            seleccionados.append(
                {
                    "objetivo": mejor["objetivo"],
                    "donante": mejor["donante"],
                    "r": mejor["r"],
                    "r2": mejor["r2"],
                    "n_train": int(mejor["n_train"]),
                    "a": mejor["a"],
                    "b": mejor["b"],
                    "c": mejor["c"],
                    "equation": mejor["equation"],
                }
            )
        else:
            for idx in candidatos.index:
                df.loc[idx, "motivo"] = "r2_bajo"

    return seleccionados, df


def run_hh_discovery(df_long):
    """Funcion principal: descubre, evalua y selecciona modelos H-H."""
    print("[HH] Descubriendo TODAS las parejas H-H posibles (sin restriccion de orientacion)...")
    df_todas = discover_all_hh_models(df_long)
    n_parejas = len(df_todas)
    print(f"[HH] Total parejas evaluadas: {n_parejas}")

    print(f"[HH] Seleccionando mejores modelos (R2 >= {R2_UMBRAL})...")
    modelos, df_completo = select_best_hh_models(df_todas)
    print(f"[HH] Modelos seleccionados: {len(modelos)}")

    for m in modelos:
        print(
            f"     [OK] {m['objetivo']} <- {m['donante']}: R2={m['r2']:.4f}, n={m['n_train']}"
        )

    estaciones_con_modelo = set(m["objetivo"] for m in modelos)
    estaciones_totales = set(df_long[COL_STATION].unique())
    sin_modelo = estaciones_totales - estaciones_con_modelo
    if sin_modelo:
        print(f"[HH] Estaciones SIN modelo H-H viable: {', '.join(sorted(sin_modelo))}")

    return modelos, df_completo
