#!/usr/bin/env python3
"""
15_figuras_globales_v2_1.py
===========================

Genera las figuras globales del pipeline v2.1 con orden geografico
(aguas abajo -> aguas arriba) y nombres limpios de estaciones:

1. Diagrama de cajas de cotas por estacion (datos originales dentro
   del rango oficial), con division en zonas Baja / Media / Alta.
2. Matriz de correlacion de Pearson (triangulo inferior) calculada
   solo con datos originales dentro del rango oficial.
3. Mapa de calor de cobertura anual por estacion (serie cruda sin
   imputar). Los años fuera del periodo oficial se marcan con "X".

Salidas:
- backend/entregables/niveles_v2_1/06_figuras/figura_boxplot_cotas_estaciones.png
- backend/entregables/niveles_v2_1/06_figuras/figura_matriz_correlacion.png
- backend/entregables/niveles_v2_1/06_figuras/figura_heatmap_cobertura_anual.png
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

from imputation_pipeline_v2_1.config import (
    DISPLAY_NAMES,
    GEO_ORDER,
    display_name,
    geo_sorted,
)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
WORK_DIR = PROJECT_ROOT / "backend" / "data" / "work" / "imputation_v2_1"
OUTPUT_DIR = WORK_DIR / "output"
FIG_DIR = PROJECT_ROOT / "backend" / "entregables" / "niveles_v2_1" / "06_figuras"
FIG_DIR.mkdir(parents=True, exist_ok=True)

IMPUTED_PATH = OUTPUT_DIR / "Datos_Imputados.csv"
RANGES_PATH = OUTPUT_DIR / "resumen_rangos_estaciones.csv"

plt.rcParams["font.size"] = 10
plt.rcParams["axes.grid"] = True
plt.rcParams["grid.alpha"] = 0.3


def load_data():
    df = pd.read_csv(IMPUTED_PATH, low_memory=False)
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
    df = df[df["Fecha"].dt.strftime("%m-%d") != "02-29"]
    return df


def load_ranges():
    df = pd.read_csv(RANGES_PATH)
    df["Fecha_Inicio"] = pd.to_datetime(df["Fecha_Inicio"], errors="coerce")
    df["Fecha_Fin"] = pd.to_datetime(df["Fecha_Fin"], errors="coerce")
    return {
        row["Estacion"]: (row["Fecha_Inicio"], row["Fecha_Fin"])
        for _, row in df.iterrows()
    }


def filter_official_range(df, ranges):
    keep = pd.Series(False, index=df.index)
    for st, (start, end) in ranges.items():
        m = (
            (df["NombreEstacion"] == st)
            & (df["Fecha"] >= start)
            & (df["Fecha"] <= end)
        )
        keep = keep | m
    return df[keep].copy()


def plot_boxplot(df, ranges):
    """Diagrama de cajas con datos originales (Nivel 0) dentro del rango oficial."""
    df_orig = df[df["Nivel_Imputacion"] == 0].copy()
    stations = geo_sorted(ranges.keys())

    data = []
    labels = []
    for st in stations:
        vals = df_orig.loc[df_orig["NombreEstacion"] == st, "Cota"].dropna()
        if len(vals) > 0:
            data.append(vals.values)
            labels.append(display_name(st))

    fig, ax = plt.subplots(figsize=(18, 8))
    bp = ax.boxplot(
        data,
        tick_labels=labels,
        patch_artist=True,
        widths=0.6,
        medianprops=dict(color="black", linewidth=2),
        boxprops=dict(facecolor="white", edgecolor="black"),
        whiskerprops=dict(color="black"),
        capprops=dict(color="black"),
        flierprops=dict(marker="o", markersize=3, alpha=0.3),
    )

    # Lineas divisorias de zonas segun GEO_ORDER
    order_names = [s for s, _ in sorted(GEO_ORDER.items(), key=lambda kv: kv[1])]
    idx_armenia = order_names.index("ARMENIA")
    idx_lagloria = order_names.index("LA_GLORIA")
    for boundary in (idx_armenia, idx_lagloria):
        ax.axvline(x=boundary + 0.5, color="gray", linestyle="--", linewidth=1.5)

    ax.set_title(
        "Diagrama de Cajas de Cotas por Estacion - Datos Originales\n"
        "Zona Baja : TEBSA -> Coyongal | Media : Armenia -> Penoncito | "
        "Alta : La Gloria -> Puerto Salgar",
        fontsize=14,
        fontweight="bold",
    )
    ax.set_ylabel("Cota (m.s.n.m.)", fontsize=12)
    ax.set_xlabel("")
    ax.grid(True, axis="y", alpha=0.3)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    fig_path = FIG_DIR / "figura_boxplot_cotas_estaciones.png"
    plt.savefig(fig_path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close()
    return fig_path


def plot_correlation_matrix(df, ranges):
    """Matriz de correlacion de Pearson (triangulo inferior), solo datos originales."""
    stations = geo_sorted(ranges.keys())
    df_orig = df[df["Nivel_Imputacion"] == 0].copy()
    wide = df_orig.pivot(index="Fecha", columns="NombreEstacion", values="Cota")
    wide = wide[[c for c in stations if c in wide.columns]]

    corr = wide.corr(method="pearson", min_periods=150)
    mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
    corr_masked = corr.mask(mask)

    labels = [display_name(s) for s in corr.columns]

    fig, ax = plt.subplots(figsize=(16, 14))
    im = ax.imshow(corr_masked, cmap="coolwarm", vmin=0, vmax=1, aspect="auto")

    n = len(corr.columns)
    ax.set_xticks(range(n))
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=9)
    ax.set_yticks(range(n))
    ax.set_yticklabels(labels, fontsize=9)
    ax.grid(False)

    # Anotar coeficientes en el triangulo inferior
    for i in range(n):
        for j in range(n):
            if not mask[i, j] and not np.isnan(corr_masked.iloc[i, j]):
                val = corr_masked.iloc[i, j]
                color = "white" if val > 0.75 else "black"
                ax.text(
                    j, i, f"{val:.2f}",
                    ha="center", va="center",
                    fontsize=7, color=color, fontweight="bold",
                )

    cbar = fig.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label("Coeficiente de Correlacion de Pearson (r)", fontsize=11)

    ax.set_title(
        "Matriz de Correlacion entre Estaciones\n"
        "(Solo datos originales dentro del rango oficial)",
        fontsize=14,
        fontweight="bold",
        pad=15,
    )
    plt.tight_layout()
    fig_path = FIG_DIR / "figura_matriz_correlacion.png"
    plt.savefig(fig_path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close()
    return fig_path


def plot_heatmap_cobertura_anual(df_raw, ranges):
    """Mapa de calor: porcentaje de datos faltantes por estacion y año.

    Usa la serie cruda sin imputar. Las celdas fuera del periodo oficial
    de cada estacion se marcan con una "X".
    """
    df = df_raw.copy()
    df["Fecha"] = pd.to_datetime(df["date"], errors="coerce")
    df = df[df["Fecha"].dt.strftime("%m-%d") != "02-29"]
    df["year"] = df["Fecha"].dt.year

    stations = geo_sorted(ranges.keys())
    years = list(range(df["year"].min(), df["year"].max() + 1))

    # Conteo de dias validos y totales por estacion-año
    grp = (
        df.groupby(["station", "year"])["level"]
        .agg(total="size", validos=lambda s: s.notna().sum())
        .reset_index()
    )
    grp["pct_faltantes"] = (1 - grp["validos"] / grp["total"]) * 100

    mat = pd.DataFrame(np.nan, index=stations, columns=years)
    for _, row in grp.iterrows():
        if row["station"] in mat.index and row["year"] in mat.columns:
            mat.loc[row["station"], row["year"]] = row["pct_faltantes"]

    # Mascara de celdas fuera del periodo oficial
    fuera = pd.DataFrame(False, index=stations, columns=years)
    for st in stations:
        start, end = ranges[st]
        for y in years:
            if y < start.year or y > end.year:
                fuera.loc[st, y] = True

    fig, ax = plt.subplots(figsize=(18, 10))
    im = ax.imshow(
        mat.values, cmap="Blues", vmin=0, vmax=100,
        aspect="auto", interpolation="nearest",
    )

    # Marcar con X las celdas fuera del periodo oficial
    for i, st in enumerate(stations):
        for j, y in enumerate(years):
            if fuera.loc[st, y]:
                ax.text(
                    j, i, "X", ha="center", va="center",
                    fontsize=5, color="gray", alpha=0.7,
                )

    ax.set_xticks(range(len(years)))
    ax.set_xticklabels(years, rotation=90, fontsize=7)
    ax.set_yticks(range(len(stations)))
    ax.set_yticklabels([display_name(s) for s in stations], fontsize=9)
    ax.grid(False)

    cbar = fig.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label("Porcentaje de Datos Faltantes (%)", fontsize=11)

    ax.set_title(
        "Mapa de calor: Cobertura de datos por Estacion y Año\n"
        "(Serie original sin imputar; X = fuera del periodo oficial)",
        fontsize=14, fontweight="bold", pad=15,
    )
    ax.set_xlabel("Año Hidrologico", fontsize=12)
    ax.set_ylabel("Estacion", fontsize=12)

    plt.tight_layout()
    fig_path = FIG_DIR / "figura_heatmap_cobertura_anual.png"
    plt.savefig(fig_path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close()
    return fig_path


def main():
    print("=" * 70)
    print("FIGURAS GLOBALES v2.1")
    print("=" * 70)

    print("\nCargando datos imputados...")
    df = load_data()
    ranges = load_ranges()
    df = filter_official_range(df, ranges)
    print(f"Registros dentro de rango oficial: {len(df):,}")

    print("\n[1/3] Generando diagrama de cajas (datos originales)...")
    p1 = plot_boxplot(df, ranges)
    print(f"      {p1.name}")

    print("\n[2/3] Generando matriz de correlacion (solo datos originales)...")
    p2 = plot_correlation_matrix(df, ranges)
    print(f"      {p2.name}")

    print("\n[3/3] Generando mapa de calor de cobertura anual (serie cruda)...")
    df_raw = pd.read_csv(
        OUTPUT_DIR / "Resumen_Crudos_IDEAM_2026_v2_1.csv", low_memory=False
    )
    p3 = plot_heatmap_cobertura_anual(df_raw, ranges)
    print(f"      {p3.name}")

    print(f"\nDirectorio de salida: {FIG_DIR}")


if __name__ == "__main__":
    main()
