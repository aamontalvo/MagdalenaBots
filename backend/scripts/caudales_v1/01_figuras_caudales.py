#!/usr/bin/env python3
"""
01_figuras_caudales.py
======================

Genera las figuras de caudales con el formato adoptado en niveles v2.1:

1. Fig2 - Distribucion mensual multianual (violines) por estacion,
   sobrescribiendo cartillas_estaciones/Caudales/<ESTACION>/.
   Titulo solo con el nombre de la estacion (sin codigo), eje "Caudal (m3/s)".
2. Matriz de correlacion de Pearson (azul -> rojo, min_periods=150).
3. Diagrama de cajas por estacion con zonas Baja / Media / Alta.
4. Mapa de calor de cobertura anual con "X" en los años fuera del
   periodo oficial (primer y ultimo dato valido de cada estacion).

Base oficial: backend/data/processed/caudales_unificados.csv (sin outliers).
Estaciones: las 14 comunes entre niveles y caudales.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
INPUT_FILE = PROJECT_ROOT / "backend" / "data" / "processed" / "caudales_unificados.csv"
CARTILLAS_DIR = PROJECT_ROOT / "cartillas_estaciones" / "Caudales"

# Mapeo columna cruda -> nombre interno (igual que en niveles)
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

# Orden geografico (aguas abajo -> aguas arriba), subconjunto del de niveles
GEO_ORDER = [
    "CALAMAR", "MAGANGUE", "BARBOSA", "ARMENIA", "RIO_NUEVO",
    "LAS_PALOMAS", "LAS_AGUADAS", "EL_BANCO", "PENONCITO",
    "EL_CONTENTO", "SITIO_NUEVO", "SAN_PABLO", "PUERTO_BERRIO", "PUERTO_SALGAR",
]

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

# Zonas para el boxplot (subconjunto de la division de niveles)
ZONA_BAJA = ("CALAMAR", "BARBOSA")
ZONA_MEDIA = ("ARMENIA", "PENONCITO")
ZONA_ALTA = ("EL_CONTENTO", "PUERTO_SALGAR")

MESES = ["ENE", "FEB", "MAR", "ABR", "MAY", "JUN",
         "JUL", "AGO", "SEP", "OCT", "NOV", "DIC"]

plt.rcParams["font.size"] = 10
plt.rcParams["axes.grid"] = True
plt.rcParams["grid.alpha"] = 0.3


def load_data():
    df = pd.read_csv(INPUT_FILE)
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    df = df[df["fecha"].dt.strftime("%m-%d") != "02-29"]
    df = df.rename(columns=COL_MAP)
    station_cols = list(COL_MAP.values())
    df["fecha"] = df["fecha"].dt.normalize()
    df = df.groupby("fecha")[station_cols].mean().reset_index()
    df["month"] = df["fecha"].dt.month
    df["year"] = df["fecha"].dt.year
    return df


def plot_violin_mensual(df, station, output_path):
    s = df[["month", station]].dropna()
    if len(s) < 30:
        print(f"  AVISO {station}: datos insuficientes")
        return False

    data, positions = [], []
    for m in range(1, 13):
        vals = s.loc[s["month"] == m, station].values
        if len(vals) > 0:
            data.append(vals)
            positions.append(m)

    fig, ax = plt.subplots(figsize=(14, 6))
    parts = ax.violinplot(
        data, positions=positions, widths=0.7,
        showmeans=True, showmedians=True, showextrema=True,
    )
    for pc in parts["bodies"]:
        pc.set_facecolor("lightgray")
        pc.set_edgecolor("gray")
        pc.set_alpha(0.7)
    parts["cmeans"].set_color("red")
    parts["cmeans"].set_linewidth(2)
    parts["cmedians"].set_color("black")
    parts["cmedians"].set_linewidth(2)
    for key in ("cbars", "cmins", "cmaxes"):
        parts[key].set_color("gray")

    legend_elements = [
        Line2D([0], [0], color="red", linewidth=2, label="Media"),
        Line2D([0], [0], color="black", linewidth=2, label="Mediana"),
    ]
    ax.legend(handles=legend_elements, loc="upper right", fontsize=10)

    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(MESES)
    ax.set_title(
        f"Distribucion Mensual de Caudales - {DISPLAY_NAMES[station]}",
        fontsize=13, fontweight="bold",
    )
    ax.set_xlabel("Mes", fontsize=11)
    ax.set_ylabel("Caudal (m3/s)", fontsize=11)
    ax.grid(True, alpha=0.3, axis="y")
    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close()
    return True


def plot_boxplot(df):
    data, labels = [], []
    for st in GEO_ORDER:
        vals = df[st].dropna().values
        if len(vals) > 0:
            data.append(vals)
            labels.append(DISPLAY_NAMES[st])

    fig, ax = plt.subplots(figsize=(16, 8))
    ax.boxplot(
        data, tick_labels=labels, patch_artist=True, widths=0.6,
        medianprops=dict(color="black", linewidth=2),
        boxprops=dict(facecolor="white", edgecolor="black"),
        whiskerprops=dict(color="black"),
        capprops=dict(color="black"),
        flierprops=dict(marker="o", markersize=2, alpha=0.2),
    )

    idx_armenia = GEO_ORDER.index("ARMENIA")
    idx_elcontento = GEO_ORDER.index("EL_CONTENTO")
    for boundary in (idx_armenia, idx_elcontento):
        ax.axvline(x=boundary + 0.5, color="gray", linestyle="--", linewidth=1.5)

    ax.set_title(
        "Diagrama de Cajas de Caudales por Estacion\n"
        "Zona Baja : Calamar -> Barbosa | Media : Armenia -> Penoncito | "
        "Alta : El Contento -> Puerto Salgar",
        fontsize=14, fontweight="bold",
    )
    ax.set_ylabel("Caudal (m3/s)", fontsize=12)
    ax.grid(True, axis="y", alpha=0.3)
    ax.set_yscale("log")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    fig_path = CARTILLAS_DIR / "figura_boxplot_caudales_estaciones.png"
    plt.savefig(fig_path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close()
    return fig_path


def plot_correlation_matrix(df):
    wide = df[GEO_ORDER].copy()
    corr = wide.corr(method="pearson", min_periods=150)
    mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
    corr_masked = corr.mask(mask)
    labels = [DISPLAY_NAMES[s] for s in corr.columns]

    fig, ax = plt.subplots(figsize=(13, 11))
    im = ax.imshow(corr_masked, cmap="coolwarm", vmin=0, vmax=1, aspect="auto")

    n = len(corr.columns)
    ax.set_xticks(range(n))
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=9)
    ax.set_yticks(range(n))
    ax.set_yticklabels(labels, fontsize=9)
    ax.grid(False)

    for i in range(n):
        for j in range(n):
            if not mask[i, j] and not np.isnan(corr_masked.iloc[i, j]):
                val = corr_masked.iloc[i, j]
                color = "white" if val > 0.75 else "black"
                ax.text(
                    j, i, f"{val:.2f}", ha="center", va="center",
                    fontsize=8, color=color, fontweight="bold",
                )

    cbar = fig.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label("Coeficiente de Correlacion de Pearson (r)", fontsize=11)
    ax.set_title(
        "Matriz de Correlacion entre Estaciones - Caudales\n"
        "(Serie oficial sin outliers, minimo 150 dias concurrentes)",
        fontsize=14, fontweight="bold", pad=15,
    )
    plt.tight_layout()
    fig_path = CARTILLAS_DIR / "figura_matriz_correlacion_caudales.png"
    plt.savefig(fig_path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close()
    return fig_path


def plot_heatmap_cobertura(df):
    years = list(range(df["year"].min(), df["year"].max() + 1))
    stations = GEO_ORDER

    mat = pd.DataFrame(np.nan, index=stations, columns=years)
    fuera = pd.DataFrame(False, index=stations, columns=years)

    grp = (
        df.groupby("year")[stations]
        .agg(["size", "count"])
    )

    for st in stations:
        s = df[st].dropna()
        if len(s) == 0:
            fuera.loc[st, :] = True
            continue
        y0 = df.loc[s.index[0], "year"]
        y1 = df.loc[s.index[-1], "year"]
        for y in years:
            if y < y0 or y > y1:
                fuera.loc[st, y] = True
            else:
                try:
                    total = grp.loc[y, (st, "size")]
                    valid = grp.loc[y, (st, "count")]
                    mat.loc[st, y] = (1 - valid / total) * 100
                except KeyError:
                    mat.loc[st, y] = 100.0

    fig, ax = plt.subplots(figsize=(18, 8))
    im = ax.imshow(
        mat.values, cmap="Blues", vmin=0, vmax=100,
        aspect="auto", interpolation="nearest",
    )

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
    ax.set_yticklabels([DISPLAY_NAMES[s] for s in stations], fontsize=9)
    ax.grid(False)

    cbar = fig.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label("Porcentaje de Datos Faltantes (%)", fontsize=11)
    ax.set_title(
        "Mapa de calor: Cobertura de caudales por Estacion y Año\n"
        "(Serie oficial sin outliers; X = fuera del periodo oficial)",
        fontsize=14, fontweight="bold", pad=15,
    )
    ax.set_xlabel("Año", fontsize=12)
    ax.set_ylabel("Estacion", fontsize=12)

    plt.tight_layout()
    fig_path = CARTILLAS_DIR / "figura_heatmap_cobertura_anual_caudales.png"
    plt.savefig(fig_path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close()
    return fig_path


def main():
    print("=" * 70)
    print("FIGURAS CAUDALES - FORMATO v2.1")
    print("=" * 70)

    print(f"\nCargando base oficial: {INPUT_FILE.name}")
    df = load_data()
    print(f"Registros: {len(df):,} | Estaciones comunes: {len(GEO_ORDER)}")

    print("\n[1/4] Sobrescribiendo Fig2 - Distribucion mensual por estacion...")
    for st in GEO_ORDER:
        out = CARTILLAS_DIR / st / f"Fig2_Violin_Mensual_{st}.png"
        out.parent.mkdir(parents=True, exist_ok=True)
        if plot_violin_mensual(df, st, out):
            print(f"  OK {st} -> {out.relative_to(PROJECT_ROOT)}")

    print("\n[2/4] Generando diagrama de cajas con zonas...")
    print(f"  {plot_boxplot(df).name}")

    print("\n[3/4] Generando matriz de correlacion...")
    print(f"  {plot_correlation_matrix(df).name}")

    print("\n[4/4] Generando mapa de calor de cobertura anual...")
    print(f"  {plot_heatmap_cobertura(df).name}")

    print(f"\nDirectorio de salida: {CARTILLAS_DIR}")


if __name__ == "__main__":
    main()
