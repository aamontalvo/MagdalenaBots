#!/usr/bin/env python3
"""
03_curvas_nivel_caudal.py
=========================

Construye las curvas Nivel-Caudal (rating curves) para las 14 estaciones
comunes entre niveles y caudales.

- Variable independiente: niveles (m.s.n.m.) de la serie aceptada v2.1
  (backend/data/work/imputation_v2_1/output/Datos_Imputados.csv).
- Variable dependiente: caudales (m3/s) de la base oficial sin outliers
  (backend/data/processed/caudales_unificados.csv, promedio diario).
- Modelos: polinomio orden 2 y orden 3 (Q = f(H)). Se reportan ambos y
  se selecciona el de mayor R2.

Salidas por estacion en cartillas_estaciones/Caudales/<ESTACION>/:
- Fig6_Curva_NivelCaudal_<ESTACION>.png
Resumen global:
- cartillas_estaciones/Caudales/curvas_nivel_caudal_resumen.csv
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import sys
import warnings

warnings.filterwarnings("ignore")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parents[3]
NIVELES_FILE = (
    PROJECT_ROOT / "backend" / "data" / "work" / "imputation_v2_1"
    / "output" / "Datos_Imputados.csv"
)
CAUDALES_FILE = PROJECT_ROOT / "backend" / "data" / "processed" / "caudales_unificados.csv"
CARTILLAS_DIR = PROJECT_ROOT / "cartillas_estaciones" / "Caudales"

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
    "CALAMAR": "Calamar",
    "MAGANGUE": "Magangué",
    "BARBOSA": "Barbosa",
    "ARMENIA": "Armenia",
    "RIO_NUEVO": "Río Nuevo",
    "LAS_PALOMAS": "Las Palomas",
    "LAS_AGUADAS": "Las Aguadas",
    "EL_BANCO": "El Banco",
    "PENONCITO": "Peñoncito",
    "EL_CONTENTO": "El Contento",
    "SITIO_NUEVO": "Sitio Nuevo",
    "SAN_PABLO": "San Pablo",
    "PUERTO_BERRIO": "Puerto Berrío",
    "PUERTO_SALGAR": "Puerto Salgar",
}

plt.rcParams["font.size"] = 10
plt.rcParams["axes.grid"] = True
plt.rcParams["grid.alpha"] = 0.3


def load_niveles():
    df = pd.read_csv(NIVELES_FILE, low_memory=False)
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
    df = df[df["Fecha"].dt.strftime("%m-%d") != "02-29"]
    return df[["NombreEstacion", "Fecha", "Cota"]].rename(
        columns={"NombreEstacion": "station", "Fecha": "fecha", "Cota": "nivel"}
    )


def load_caudales():
    df = pd.read_csv(CAUDALES_FILE)
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    df = df[df["fecha"].dt.strftime("%m-%d") != "02-29"]
    df = df.rename(columns=COL_MAP)
    station_cols = list(COL_MAP.values())
    df["fecha"] = df["fecha"].dt.normalize()
    df = df.groupby("fecha")[station_cols].mean().reset_index()
    long = df.melt(id_vars="fecha", var_name="station", value_name="caudal")
    return long.dropna(subset=["caudal"])


def fit_poly(H, Q, orden):
    coefs = np.polyfit(H, Q, orden)
    Q_pred = np.polyval(coefs, H)
    ss_res = np.sum((Q - Q_pred) ** 2)
    ss_tot = np.sum((Q - Q.mean()) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else np.nan
    r = np.corrcoef(H, Q)[0, 1]
    return coefs, r2, r


def poly_eq_text(coefs):
    orden = len(coefs) - 1
    partes = []
    for i, c in enumerate(coefs):
        pot = orden - i
        if pot == 0:
            partes.append(f"{c:+.4f}")
        elif pot == 1:
            partes.append(f"{c:+.4f}·H")
        else:
            partes.append(f"{c:+.6f}·H^{pot}")
    return "Q = " + " ".join(partes)


def plot_curva_nc(H, Q, station, fit2, fit3, output_path):
    fig, ax = plt.subplots(figsize=(11, 7))

    ax.scatter(H, Q, alpha=0.25, s=8, color="steelblue",
               label=f"Pares N-C (n={len(H):,})")

    H_range = np.linspace(H.min(), H.max(), 300)
    ax.plot(H_range, np.polyval(fit2["coefs"], H_range), "r-",
            linewidth=2.2, label=f"Orden 2 (R² = {fit2['r2']:.3f})")
    ax.plot(H_range, np.polyval(fit3["coefs"], H_range), color="darkorange",
            linewidth=2.2, linestyle="--",
            label=f"Orden 3 (R² = {fit3['r2']:.3f})")

    mejor = "Orden 2" if fit2["r2"] >= fit3["r2"] else "Orden 3"
    coefs_mejor = fit2["coefs"] if mejor == "Orden 2" else fit3["coefs"]
    textstr = (
        f"r = {fit2['r']:.3f}\n"
        f"R² orden 2 = {fit2['r2']:.4f}\n"
        f"R² orden 3 = {fit3['r2']:.4f}\n"
        f"Mejor: {mejor}\n"
        f"{poly_eq_text(coefs_mejor)}"
    )
    ax.text(
        0.03, 0.97, textstr, transform=ax.transAxes, fontsize=9,
        verticalalignment="top",
        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.9),
    )

    ax.set_title(
        f"Curva Nivel-Caudal - {DISPLAY_NAMES[station]}",
        fontsize=13, fontweight="bold",
    )
    ax.set_xlabel("Nivel (m.s.n.m.)", fontsize=11)
    ax.set_ylabel("Caudal (m3/s)", fontsize=11)
    ax.legend(loc="lower right", fontsize=9)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close()
    return mejor


def main():
    print("=" * 70)
    print("CURVAS NIVEL-CAUDAL (14 estaciones comunes)")
    print("=" * 70)

    print("\nCargando niveles (serie aceptada v2.1)...")
    niveles = load_niveles()
    print(f"  Registros: {len(niveles):,}")

    print("Cargando caudales (base oficial sin outliers, diario)...")
    caudales = load_caudales()
    print(f"  Registros: {len(caudales):,}")

    merged = niveles.merge(caudales, on=["station", "fecha"], how="inner")
    merged = merged.dropna(subset=["nivel", "caudal"])
    print(f"Pares N-C concurrentes: {len(merged):,}")

    resumen = []
    for st, nombre in DISPLAY_NAMES.items():
        s = merged[merged["station"] == st]
        if len(s) < 100:
            print(f"  AVISO {nombre}: solo {len(s)} pares, se omite")
            continue

        H = s["nivel"].values
        Q = s["caudal"].values
        c2, r2_2, r = fit_poly(H, Q, 2)
        c3, r2_3, _ = fit_poly(H, Q, 3)
        fit2 = {"coefs": c2, "r2": r2_2, "r": r}
        fit3 = {"coefs": c3, "r2": r2_3, "r": r}

        out = CARTILLAS_DIR / st / f"Fig6_Curva_NivelCaudal_{st}.png"
        out.parent.mkdir(parents=True, exist_ok=True)
        mejor = plot_curva_nc(H, Q, st, fit2, fit3, out)

        resumen.append({
            "estacion": nombre,
            "n_pares": len(s),
            "r": round(r, 4),
            "r2_orden2": round(r2_2, 4),
            "r2_orden3": round(r2_3, 4),
            "mejor_modelo": mejor,
            "ecuacion_orden2": poly_eq_text(c2),
            "ecuacion_orden3": poly_eq_text(c3),
        })
        print(f"  {nombre:15s} n={len(s):6d}  R2(2)={r2_2:.4f}  "
              f"R2(3)={r2_3:.4f}  mejor={mejor}")

    res_path = CARTILLAS_DIR / "curvas_nivel_caudal_resumen.csv"
    pd.DataFrame(resumen).to_csv(res_path, index=False)
    print(f"\nResumen: {res_path}")


if __name__ == "__main__":
    main()
