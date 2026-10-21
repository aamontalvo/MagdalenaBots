#!/usr/bin/env python3
"""
05_curva_duracion_caudales.py
=============================

Genera la Figura 3 (curva de duracion de caudales) para las 14 estaciones
comunes, replicando la estructura de la Fig3 de niveles v2.1.

- Fuente: backend/data/work/caudales_v1/output/Datos_Imputados_Caudales.csv
- Se usa la serie completa (originales + imputados), igual que en niveles.
- Salida: cartillas_estaciones/Caudales/<ESTACION>/Fig3_Curva_Duracion_<ESTACION>.png
- Resumen: cartillas_estaciones/Caudales/curvas_duracion_caudales_resumen.csv
"""

import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parents[3]
INPUT_FILE = (
    PROJECT_ROOT / "backend" / "data" / "work" / "caudales_v1"
    / "output" / "Datos_Imputados_Caudales.csv"
)
CARTILLAS_DIR = PROJECT_ROOT / "cartillas_estaciones" / "Caudales"

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


def plot_curva_duracion(station_df, station, output_path):
    q = station_df["Caudal"].dropna().sort_values(ascending=False)
    if len(q) < 10:
        return False

    n = len(q)
    exceedance = np.arange(1, n + 1) / (n + 1) * 100

    p50 = np.percentile(q, 50)
    p90 = np.percentile(q, 10)
    p95 = np.percentile(q, 5)
    p100 = q.min()

    fig, ax = plt.subplots(figsize=(10, 7))
    ax.plot(exceedance, q.values, color="#1f77b4", linewidth=2.5)

    for x, value, label, offset in [
        (50, p50, "P50", 1.0),
        (90, p90, "P90", 1.0),
        (95, p95, "P95", -1.0),
        (99.5, p100, "P100", -1.0),
    ]:
        ax.plot(
            x, value, "o", markersize=12, markerfacecolor="white",
            markeredgecolor="black", markeredgewidth=1.5,
        )
        ax.annotate(
            f"{label}: {value:,.0f} m3/s",
            xy=(x, value), xytext=(0, 14 if offset > 0 else -18),
            textcoords="offset points", ha="center", fontsize=10,
            fontweight="bold",
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.9,
                      edgecolor="gray"),
        )

    ax.set_title(
        f"Curva de Duracion - {DISPLAY_NAMES.get(station, station)}",
        fontsize=14, fontweight="bold",
    )
    ax.set_xlabel("Porcentaje de tiempo excedido (%)", fontsize=12)
    ax.set_ylabel("Caudal (m3/s)", fontsize=12)
    ax.grid(True, alpha=0.3, linestyle="-")
    ax.set_xlim(-2, 102)
    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close()

    return {
        "estacion": DISPLAY_NAMES.get(station, station),
        "n_registros": n,
        "p50_m3s": round(float(p50), 2),
        "p90_m3s": round(float(p90), 2),
        "p95_m3s": round(float(p95), 2),
        "p100_m3s": round(float(p100), 2),
    }


def main():
    print("=" * 70)
    print("CURVAS DE DURACION DE CAUDALES - 14 ESTACIONES")
    print("=" * 70)

    df = pd.read_csv(INPUT_FILE, low_memory=False)
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
    print(f"Registros cargados: {len(df):,}")

    resumen = []
    for station in DISPLAY_NAMES:
        station_df = df[df["NombreEstacion"] == station]
        out_dir = CARTILLAS_DIR / station
        out_dir.mkdir(parents=True, exist_ok=True)
        out = out_dir / f"Fig3_Curva_Duracion_{station}.png"
        row = plot_curva_duracion(station_df, station, out)
        if row:
            resumen.append(row)
            print(f"  OK {out.name}")
        else:
            print(f"  AVISO {station}: datos insuficientes")

    if resumen:
        res_path = CARTILLAS_DIR / "curvas_duracion_caudales_resumen.csv"
        pd.DataFrame(resumen).to_csv(res_path, index=False, encoding="utf-8-sig")
        print(f"\nResumen: {res_path}")

    print(f"Figuras generadas: {len(resumen)}")


if __name__ == "__main__":
    main()
