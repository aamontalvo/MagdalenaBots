#!/usr/bin/env python3
"""
04_imputacion_caudales.py
=========================

Imputacion de caudales diarios para las 14 estaciones comunes.

Niveles:
- L1: interpolacion local ponderada (kernel {-2:0.1, -1:0.2, 0:0.4, 1:0.2, 2:0.1})
  para gaps <= 3 dias con vecinos validos a ambos lados (misma logica que niveles).
- L2: curva Nivel-Caudal propia Q = f(H), polinomio orden 2 (orden 3 solo si
  mejora R2 en mas de 0.01), entrenada con pares originales concurrentes de la
  serie de niveles aceptada v2.1 y la base oficial de caudales sin outliers.
  Umbral de aceptacion: R2 >= 0.75.

Reglas duras:
- Nada fuera del periodo oficial de cada estacion (primer/ultimo caudal valido).
- Sin soporte empirico -> NaN documentado.
- Trazabilidad por nivel en cada registro (columna Nivel_Imputacion y Metodo).

Salidas (backend/data/work/caudales_v1/output/):
- Datos_Imputados_Caudales.csv (long format)
- Resumen_Imputacion_Caudales.csv
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys
import warnings

warnings.filterwarnings("ignore")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parents[3]
CAUDALES_FILE = PROJECT_ROOT / "backend" / "data" / "processed" / "caudales_unificados.csv"
NIVELES_FILE = (
    PROJECT_ROOT / "backend" / "data" / "work" / "imputation_v2_1"
    / "output" / "Datos_Imputados.csv"
)
OUT_DIR = PROJECT_ROOT / "backend" / "data" / "work" / "caudales_v1" / "output"
OUT_DIR.mkdir(parents=True, exist_ok=True)

COL_MAP = {
    "CALAMAR_29037020": "CALAMAR",
    "MAGANGUE_25027680": "MAGANGUE",
    "BARBOSA_25027530": "BARBOSA",
    "ARMENIA_25027360": "ARMENIA",
    "RIO NUEVO_25027630": "RIO_NUEVO",
    "LAS PALOMAS_25027390": "LAS_PALOMAS",
    "LAS AGUADAS_25027490": "LAS_AGUADAS",
    "EL BANCO - AUT_25027020": "EL_BANCO",
    "PENONCITO_25027330": "PENONCITO",
    "EL CONTENTO_23217030": "EL_CONTENTO",
    "SITIO NUEVO_23187280": "SITIO_NUEVO",
    "SAN PABLO RIO MAGDALENA  - AUT_": "SAN_PABLO",
    "PUERTO BERRIO - AUT_23097030": "PUERTO_BERRIO",
    "PUERTO SALGAR - AUT_23037010": "PUERTO_SALGAR",
}

DISPLAY_NAMES = {
    "CALAMAR": "Calamar", "MAGANGUE": "Magangué", "BARBOSA": "Barbosa",
    "ARMENIA": "Armenia", "RIO_NUEVO": "Río Nuevo", "LAS_PALOMAS": "Las Palomas",
    "LAS_AGUADAS": "Las Aguadas", "EL_BANCO": "El Banco", "PENONCITO": "Peñoncito",
    "EL_CONTENTO": "El Contento", "SITIO_NUEVO": "Sitio Nuevo",
    "SAN_PABLO": "San Pablo", "PUERTO_BERRIO": "Puerto Berrío",
    "PUERTO_SALGAR": "Puerto Salgar",
}

L1_MAX_GAP = 3
L1_KERNEL = {-2: 0.1, -1: 0.2, 0: 0.4, 1: 0.2, 2: 0.1}
R2_UMBRAL_NC = 0.75
DELTA_R2_ORDEN3 = 0.01


def load_caudales():
    df = pd.read_csv(CAUDALES_FILE)
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    df = df[df["fecha"].dt.strftime("%m-%d") != "02-29"]
    df = df.rename(columns=COL_MAP)
    station_cols = list(COL_MAP.values())
    df["fecha"] = df["fecha"].dt.normalize()
    df = df.groupby("fecha")[station_cols].mean().reset_index()
    return df


def load_niveles():
    df = pd.read_csv(NIVELES_FILE, low_memory=False)
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
    df = df[df["Fecha"].dt.strftime("%m-%d") != "02-29"]
    return df[["NombreEstacion", "Fecha", "Cota"]].rename(
        columns={"NombreEstacion": "station", "Fecha": "fecha", "Cota": "nivel"}
    )


def apply_l1(series, max_gap=L1_MAX_GAP, kernel=L1_KERNEL):
    """Interpolacion local ponderada (identica a la de niveles)."""
    s = series.copy()
    imputed = np.zeros(len(s), dtype=bool)
    isnan = s.isna().values
    if not isnan.any():
        return s, imputed

    valid_idx = np.where(~isnan)[0]
    if len(valid_idx) == 0:
        return s, imputed
    first_valid, last_valid = valid_idx[0], valid_idx[-1]

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
        if g_end - g_start > max_gap:
            continue
        if g_start <= first_valid or g_end >= last_valid + 1:
            continue
        valores, pesos = [], []
        for offset, weight in kernel.items():
            idx = g_start + offset
            if 0 <= idx < len(s) and not pd.isna(s.iloc[idx]):
                valores.append(s.iloc[idx])
                pesos.append(weight)
        if len(valores) < 2:
            continue
        pesos = np.array(pesos) / np.sum(pesos)
        imp_val = np.sum(np.array(valores) * pesos)
        for i in range(g_start, g_end):
            s.iloc[i] = imp_val
            imputed[i] = True
    return s, imputed


def fit_nc_model(nivel_train, caudal_train):
    """Ajusta polinomios orden 2 y 3; retorna el mejor segun regla."""
    c2 = np.polyfit(nivel_train, caudal_train, 2)
    c3 = np.polyfit(nivel_train, caudal_train, 3)
    q2 = np.polyval(c2, nivel_train)
    q3 = np.polyval(c3, nivel_train)
    ss_tot = np.sum((caudal_train - caudal_train.mean()) ** 2)
    r2_2 = 1 - np.sum((caudal_train - q2) ** 2) / ss_tot
    r2_3 = 1 - np.sum((caudal_train - q3) ** 2) / ss_tot
    if r2_3 > r2_2 + DELTA_R2_ORDEN3:
        return {"coefs": c3, "orden": 3, "r2": r2_3}
    return {"coefs": c2, "orden": 2, "r2": r2_2}


def main():
    print("=" * 70)
    print("IMPUTACION DE CAUDALES - Nivel 1 (local) + Nivel 2 (curva N-C)")
    print("=" * 70)

    print("\nCargando base oficial de caudales...")
    df_q = load_caudales()
    print(f"  Dias: {len(df_q):,}")

    print("Cargando niveles aceptados v2.1...")
    niveles = load_niveles()
    niveles_idx = {
        st: grp.set_index("fecha")["nivel"]
        for st, grp in niveles.groupby("station")
    }

    registros = []
    resumen = []

    for st, nombre in DISPLAY_NAMES.items():
        # Serie diaria completa dentro del calendario del archivo
        s = df_q.set_index("fecha")[st]

        # Periodo oficial: primer y ultimo caudal valido
        validos = s.dropna()
        if len(validos) == 0:
            continue
        f0, f1 = validos.index[0], validos.index[-1]
        s_oficial = s.loc[f0:f1]

        # Estado original
        n_total = len(s_oficial)
        n_orig = s_oficial.notna().sum()

        # --- L1 ---
        s_l1, mask_l1 = apply_l1(s_oficial)
        n_l1 = mask_l1.sum()

        # --- L2: curva N-C ---
        # Entrenamiento: pares donde caudal original (no L1) y nivel existen
        nivel_st = niveles_idx.get(st)
        n_l2 = 0
        modelo = None
        s_l2 = s_l1.copy()
        mask_l2 = np.zeros(len(s_l2), dtype=bool)

        if nivel_st is not None:
            nivel_al = nivel_st.reindex(s_oficial.index)
            train_mask = s_oficial.notna() & nivel_al.notna()
            if train_mask.sum() >= 100:
                modelo = fit_nc_model(
                    nivel_al[train_mask].values, s_oficial[train_mask].values
                )
                if modelo["r2"] >= R2_UMBRAL_NC:
                    # Aplicar donde sigue habiendo NaN tras L1 y hay nivel
                    aplicar = s_l2.isna() & nivel_al.notna()
                    pred = np.polyval(modelo["coefs"], nivel_al[aplicar].values)
                    s_l2.loc[aplicar] = pred
                    mask_l2 = aplicar.values
                    n_l2 = int(aplicar.sum())
                else:
                    modelo["rechazado"] = True

        n_nan_final = s_l2.isna().sum()
        cobertura = (s_l2.notna().sum() / n_total) * 100

        # Construir registros long
        metodo = pd.Series("Original", index=s_l2.index, dtype=object)
        metodo[mask_l1] = "L1_Interpolacion"
        metodo[mask_l2] = f"L2_NC_orden{modelo['orden']}" if modelo and not modelo.get("rechazado") else metodo[mask_l2]
        nivel_imp = pd.Series(0, index=s_l2.index, dtype=int)
        nivel_imp[mask_l1] = 1
        nivel_imp[mask_l2] = 2
        nivel_imp[s_l2.isna()] = 0  # NaN documentado sigue siendo nivel 0 sin dato

        df_st = pd.DataFrame({
            "NombreEstacion": st,
            "Fecha": s_l2.index,
            "Caudal": s_l2.values,
            "Nivel_Imputacion": nivel_imp.values,
            "Metodo": metodo.values,
        })
        # Marcar NaN explicitamente
        df_st.loc[df_st["Caudal"].isna(), "Metodo"] = np.nan
        registros.append(df_st)

        resumen.append({
            "Estacion": nombre,
            "Inicio": f0.date(),
            "Fin": f1.date(),
            "Dias": n_total,
            "Original": int(n_orig),
            "L1": int(n_l1),
            "L2": n_l2,
            "NC_orden": modelo["orden"] if modelo and not modelo.get("rechazado") else None,
            "NC_R2": round(modelo["r2"], 4) if modelo else None,
            "NC_aceptado": bool(modelo and not modelo.get("rechazado")),
            "NaN_restantes": int(n_nan_final),
            "Cobertura_pct": round(cobertura, 2),
        })
        estado = f"R2={modelo['r2']:.3f}" if modelo else "sin modelo"
        flag = "" if modelo and not modelo.get("rechazado") else " [NC NO ACEPTADO]"
        print(f"  {nombre:15s} L1={n_l1:5d}  L2={n_l2:5d}  "
              f"NaN={n_nan_final:5d}  Cob={cobertura:5.1f}%  {estado}{flag}")

    df_out = pd.concat(registros, ignore_index=True)
    out_path = OUT_DIR / "Datos_Imputados_Caudales.csv"
    df_out.to_csv(out_path, index=False)
    print(f"\nGuardado: {out_path}")

    res_path = OUT_DIR / "Resumen_Imputacion_Caudales.csv"
    df_res = pd.DataFrame(resumen)
    df_res.to_csv(res_path, index=False)
    print(f"Guardado: {res_path}")

    print("\n--- Resumen global ---")
    print(f"Total registros: {len(df_out):,}")
    for n, lab in [(1, "L1"), (2, "L2")]:
        c = (df_out["Nivel_Imputacion"] == n).sum()
        print(f"  {lab}: {c:,} valores")
    print(f"  NaN restantes: {df_out['Caudal'].isna().sum():,}")
    rechazadas = df_res[~df_res["NC_aceptado"]]["Estacion"].tolist()
    if rechazadas:
        print(f"  Estaciones sin L2 (R2 < {R2_UMBRAL_NC} o sin modelo): {rechazadas}")


if __name__ == "__main__":
    main()
