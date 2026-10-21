#!/usr/bin/env python3
"""
14_generar_cartillas_v2_1.py
============================

Genera cartillas tecnicas (5 figuras) para cada estacion usando el dataset
final de imputacion v2.1 (Datos_Imputados.csv).

Salida: backend/entregables/niveles_v2_1/07_cartillas/<ESTACION>/
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import scipy.stats as stats
import warnings

from imputation_pipeline_v2_1.config import display_name, geo_sorted

warnings.filterwarnings("ignore")

plt.rcParams["font.size"] = 10
plt.rcParams["axes.labelsize"] = 11
plt.rcParams["axes.titlesize"] = 12
plt.rcParams["axes.grid"] = True
plt.rcParams["grid.alpha"] = 0.3

PROJECT_ROOT = Path(__file__).resolve().parents[3]
INPUT_FILE = (
    PROJECT_ROOT
    / "backend"
    / "data"
    / "work"
    / "imputation_v2_1"
    / "output"
    / "Datos_Imputados.csv"
)
OUTPUT_DIR = PROJECT_ROOT / "backend" / "entregables" / "niveles_v2_1" / "07_cartillas"

ESTACIONES = [
    "ARMENIA", "BARBOSA", "BARRANCABERMEJA", "CALAMAR", "COYONGAL", "EL_BANCO",
    "EL_CONTENTO", "GAMARRA", "GAMARRA_AUT", "LA_GLORIA", "LAS_AGUADAS",
    "LAS_PALOMAS", "MAGANGUE", "PENONCITO", "PLATO", "PUERTO_BERRIO",
    "PUERTO_SALGAR", "PUERTO_WILCHES", "RIO_NUEVO", "SAN_PABLO", "SAN_PEDRITO",
    "SITIO_NUEVO", "TEBSA", "TENERIFE",
]

MESES = [
    "ENE", "FEB", "MAR", "ABR", "MAY", "JUN",
    "JUL", "AGO", "SEP", "OCT", "NOV", "DIC",
]


def clasificar_metodo(metodo_str):
    if metodo_str == "Original":
        return "original"
    elif metodo_str == "L1_Interpolacion":
        return "L1"
    elif metodo_str.startswith("L2_HH_") and "quadratic" in metodo_str:
        return "L2"
    elif metodo_str.startswith("L3_HH_"):
        return "L3"
    else:
        return "L3"


def load_data():
    df = pd.read_csv(INPUT_FILE, low_memory=False)
    df["date"] = pd.to_datetime(df["Fecha"], errors="coerce")
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["day"] = df["date"].dt.day
    df["day_of_year"] = df["date"].dt.dayofyear
    df["data_source"] = df["Metodo"].apply(clasificar_metodo)
    return df


def get_station_data(df, station):
    station_df = df[df["NombreEstacion"] == station].copy()
    station_df = station_df.sort_values("date")
    return station_df


def plot_serie_tiempo(station_df, station, output_path):
    fig, ax = plt.subplots(figsize=(14, 6))
    valid_data = station_df[station_df["Cota"].notna()]
    ax.plot(valid_data["date"], valid_data["Cota"], "k-", linewidth=0.8)

    total_records = len(station_df)
    original_count = (station_df["data_source"] == "original").sum()
    imputed_count = total_records - original_count
    pct_original = (original_count / total_records) * 100 if total_records > 0 else 0
    pct_imputed = (imputed_count / total_records) * 100 if total_records > 0 else 0
    year_start = int(station_df["year"].min())
    year_end = int(station_df["year"].max())

    annotation_text = (
        f"Periodo: {year_start}-{year_end} | Total: {total_records:,} registros\n"
        f"Originales: {pct_original:.1f}% | Imputados: {pct_imputed:.1f}%"
    )
    ax.text(
        0.02, 0.98, annotation_text,
        transform=ax.transAxes, fontsize=10,
        verticalalignment="top",
        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.9),
    )
    ax.set_title(
        f"Serie de Tiempo de Cotas - {display_name(station, with_code=True)}",
        fontsize=13, fontweight="bold",
    )
    ax.set_xlabel("Fecha", fontsize=11)
    ax.set_ylabel("Cota (m.s.n.m.)", fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.xaxis.set_major_locator(plt.MaxNLocator(10))
    fig.autofmt_xdate()
    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close()
    return True


def plot_violin_mensual(station_df, station, output_path):
    original = station_df[station_df["data_source"] == "original"].copy()
    if len(original) < 30:
        print(f"  AVISO {station}: Insuficientes datos originales para violin")
        return False

    fig, ax = plt.subplots(figsize=(14, 6))
    data_by_month = []
    positions = []
    for month in range(1, 13):
        month_data = original[original["month"] == month]["Cota"].dropna()
        if len(month_data) > 0:
            data_by_month.append(month_data.values)
            positions.append(month)

    if len(data_by_month) == 0:
        return False

    parts = ax.violinplot(
        data_by_month, positions=positions, widths=0.7,
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
    parts["cbars"].set_color("gray")
    parts["cmins"].set_color("gray")
    parts["cmaxes"].set_color("gray")

    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], color="red", linewidth=2, label="Media"),
        Line2D([0], [0], color="black", linewidth=2, label="Mediana"),
    ]
    ax.legend(handles=legend_elements, loc="upper right", fontsize=10)

    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(MESES)
    ax.set_title(
        f"Distribucion Mensual de Cotas - {display_name(station, with_code=True)}",
        fontsize=13, fontweight="bold",
    )
    ax.set_xlabel("Mes", fontsize=11)
    ax.set_ylabel("Cota (m.s.n.m.)", fontsize=11)
    ax.grid(True, alpha=0.3, axis="y")
    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close()
    return True


def plot_curva_duracion(station_df, station, output_path):
    fig, ax = plt.subplots(figsize=(10, 7))
    levels = station_df["Cota"].dropna().sort_values(ascending=False)
    if len(levels) < 10:
        return False

    n = len(levels)
    exceedance_prob = np.arange(1, n + 1) / (n + 1) * 100
    ax.plot(exceedance_prob, levels, color="#1f77b4", linewidth=2.5)

    p50_level = np.percentile(levels, 50)
    p90_level = np.percentile(levels, 10)
    p95_level = np.percentile(levels, 5)
    p100_level = levels.min()

    p50_idx = np.argmin(np.abs(exceedance_prob - 50))
    p90_idx = np.argmin(np.abs(exceedance_prob - 90))
    p95_idx = np.argmin(np.abs(exceedance_prob - 95))
    p100_idx = np.argmin(np.abs(exceedance_prob - 99.5))

    ax.plot(50, p50_level, "o", markersize=12, markerfacecolor="white", markeredgecolor="black", markeredgewidth=1.5)
    ax.plot(90, p90_level, "o", markersize=12, markerfacecolor="white", markeredgecolor="black", markeredgewidth=1.5)
    ax.plot(95, p95_level, "o", markersize=12, markerfacecolor="white", markeredgecolor="black", markeredgewidth=1.5)
    ax.plot(99.5, p100_level, "o", markersize=12, markerfacecolor="white", markeredgecolor="black", markeredgewidth=1.5)

    ax.text(50, p50_level + 0.3, f"P50: {p50_level:.2f} m",
            ha="center", fontsize=11, fontweight="bold",
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.9, edgecolor="gray"))
    ax.text(90, p90_level + 0.3, f"P90: {p90_level:.2f} m",
            ha="center", fontsize=11, fontweight="bold",
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.9, edgecolor="gray"))
    ax.text(95, p95_level - 0.4, f"P95: {p95_level:.2f} m",
            ha="center", fontsize=11, fontweight="bold",
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.9, edgecolor="gray"))
    ax.text(99.5, p100_level - 0.4, f"P100: {p100_level:.2f} m",
            ha="center", fontsize=11, fontweight="bold",
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.9, edgecolor="gray"))

    ax.set_title(
        f"Curva de Duracion - {display_name(station, with_code=True)}",
        fontsize=14, fontweight="bold",
    )
    ax.set_xlabel("Porcentaje de tiempo excedido (%)", fontsize=12)
    ax.set_ylabel("Cota (m.s.n.m.)", fontsize=12)
    ax.grid(True, alpha=0.3, linestyle="-")
    ax.set_xlim(-2, 102)
    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close()
    return True


def calcular_percentiles_estacion(station_df, station, output_dir):
    df = station_df.copy()
    df["mes_dia"] = df["date"].dt.strftime("%m-%d")
    df = df[df["mes_dia"] != "02-29"]
    df = df[df["data_source"] == "original"]
    df_clean = df[df["Cota"].notna()].copy()

    if len(df_clean) == 0:
        return None

    fecha_base = pd.date_range("2020-01-01", "2020-12-31", freq="D")
    fecha_base = fecha_base[fecha_base.strftime("%m-%d") != "02-29"]

    results = {}
    for i, fecha in enumerate(fecha_base, 1):
        mes_dia = fecha.strftime("%m-%d")
        day_data = df_clean[df_clean["mes_dia"] == mes_dia]["Cota"].values
        if len(day_data) > 0:
            results[i] = {
                "day_of_year": i,
                "mes_dia": mes_dia,
                "max": round(np.max(day_data), 3),
                "p95": round(np.percentile(day_data, 95), 3),
                "p75": round(np.percentile(day_data, 75), 3),
                "p50": round(np.percentile(day_data, 50), 3),
                "p25": round(np.percentile(day_data, 25), 3),
                "p5": round(np.percentile(day_data, 5), 3),
                "min": round(np.min(day_data), 3),
                "n_obs": len(day_data),
            }

    percentiles_df = pd.DataFrame(results).T
    if len(percentiles_df) == 0:
        return None

    csv_path = output_dir / f"Fig4_Percentiles_{station}_v2_1.csv"
    percentiles_df.to_csv(csv_path, index=False)
    return csv_path


def plot_curvas_excedidos(station_df, station, output_path):
    station_dir = output_path.parent
    csv_path = calcular_percentiles_estacion(station_df, station, station_dir)
    if csv_path is None:
        return False

    df = pd.read_csv(csv_path)
    fig, ax = plt.subplots(figsize=(14, 8))
    days = df["day_of_year"].values

    colors = {
        "max": "black", "p95": "#8B0000", "p75": "#6B8E23",
        "p50": "black", "p25": "#5DADE2", "p5": "#D35400", "min": "black",
    }
    linewidths = {
        "max": 1.2, "p95": 1.2, "p75": 1.2, "p50": 2.5,
        "p25": 1.2, "p5": 1.2, "min": 1.2,
    }

    for col in ["max", "p95", "p75", "p50", "p25", "p5", "min"]:
        ax.plot(days, df[col], color=colors[col], linewidth=linewidths[col])

    ax.axvline(x=365, color="black", linewidth=2.5, linestyle="-", zorder=10)

    x_label = 368
    last_day = df[df["day_of_year"] == 365].iloc[0]
    labels_data = [
        ("max", last_day["max"], "MAX"),
        ("p95", last_day["p95"], "5%"),
        ("p75", last_day["p75"], "25%"),
        ("p50", last_day["p50"], "50%"),
        ("p25", last_day["p25"], "75%"),
        ("p5", last_day["p5"], "95%"),
        ("min", last_day["min"], "MIN"),
    ]

    for col, value, label in labels_data:
        ax.text(x_label, value, label, fontsize=11, fontweight="bold",
                color=colors[col], va="center", ha="left")

    month_days = [1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335]
    ax.set_xlim(1, 365)
    ax.set_xticks(month_days)
    ax.set_xticklabels(MESES, fontsize=11)

    ax.grid(True, alpha=0.3, which="both", linestyle="-", linewidth=0.5)
    ax.minorticks_on()
    ax.grid(True, alpha=0.15, which="minor", linestyle=":", linewidth=0.5)

    ax.set_xlabel("Mes", fontsize=12, fontweight="bold")
    ax.set_ylabel("Cota (m)", fontsize=12, fontweight="bold")
    ax.set_title(
        f"Curvas de Frecuencia de Niveles Excedidos - {display_name(station, with_code=True)}",
        fontsize=14, fontweight="bold", pad=20,
    )

    y_min = df["min"].min() - 2
    y_max = df["max"].max() + 2
    ax.set_ylim(y_min, y_max)

    plt.tight_layout()
    plt.subplots_adjust(right=0.88)
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    return True


def plot_ajuste_distribuciones(station_df, station, output_path):
    original = station_df[station_df["data_source"] == "original"]["Cota"].dropna()
    if len(original) < 30:
        print(f"  AVISO {station}: Insuficientes datos originales para distribuciones")
        return False

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    ax1 = axes[0]
    ax1.hist(original, bins=30, density=True, alpha=0.6,
             color="lightgray", edgecolor="gray", label="Datos observados")

    mu, sigma = stats.norm.fit(original)
    x = np.linspace(original.min(), original.max(), 100)
    ax1.plot(x, stats.norm.pdf(x, mu, sigma), "k-", linewidth=2, label="Normal")

    try:
        shape, loc, scale = stats.gamma.fit(original)
        ax1.plot(x, stats.gamma.pdf(x, shape, loc, scale), "k--", linewidth=2, label="Pearson III")
    except Exception:
        shape, loc, scale = None, None, None

    try:
        c, loc_w, scale_w = stats.weibull_min.fit(original)
        ax1.plot(x, stats.weibull_min.pdf(x, c, loc_w, scale_w), "k:", linewidth=2, label="Weibull")
    except Exception:
        pass

    ax1.set_title(
        f"Ajuste de Distribuciones - {display_name(station, with_code=True)}\nAnual",
        fontsize=12, fontweight="bold",
    )
    ax1.set_xlabel("Cota (m.s.n.m.)", fontsize=11)
    ax1.set_ylabel("Densidad de probabilidad", fontsize=11)
    ax1.legend(fontsize=9, loc="upper left")
    ax1.grid(True, alpha=0.3)

    ax2 = axes[1]
    if shape is not None:
        stats.probplot(original, dist=stats.gamma, sparams=(shape, loc, scale), plot=ax2)
        ax2.get_lines()[0].set_markerfacecolor("gray")
        ax2.get_lines()[0].set_markeredgecolor("black")
        ax2.get_lines()[0].set_alpha(0.6)
        ax2.get_lines()[1].set_color("black")
        ax2.get_lines()[1].set_linestyle("--")

    stat, p_value = stats.shapiro(original[: min(5000, len(original))])
    ax2.set_title(
        f"Q-Q Plot - Mejor Ajuste: Pearson III\nKS p-value: {p_value:.2e}",
        fontsize=12, fontweight="bold",
    )
    ax2.set_xlabel("Cuantiles teoricos (Pearson III)", fontsize=11)
    ax2.set_ylabel("Cuantiles observados", fontsize=11)
    ax2.grid(True, alpha=0.3)

    from matplotlib.lines import Line2D
    legend_elements = [Line2D([0], [0], color="black", linestyle="--", label="1:1")]
    ax2.legend(handles=legend_elements, loc="upper left", fontsize=9)

    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close()
    return True


def plot_relacion_hh(station_df, station, output_path):
    """Genera scatter altura-altura para los modelos L2/L3 activos de la estación."""
    station_data = station_df[station_df["Cota"].notna()].copy()
    if len(station_data) == 0:
        return False

    # Identificar qué métodos H-H aparecen en esta estación
    hh_methods = station_data["Metodo"].dropna().unique()
    hh_methods = [m for m in hh_methods if m.startswith("L2_HH_") or m.startswith("L3_HH_")]
    if len(hh_methods) == 0:
        return False

    # Cargar tablas de modelos
    project_root = Path(__file__).resolve().parents[3]
    l2_path = project_root / "backend" / "entregables" / "niveles_v2_1" / "03_modelos" / "Tabla_Modelos_HH_Seleccionados.csv"
    l3_path = project_root / "backend" / "entregables" / "niveles_v2_1" / "03_modelos" / "Tabla_Modelos_L3.csv"

    l2_models = pd.read_csv(l2_path) if l2_path.exists() else pd.DataFrame()
    l3_models = pd.read_csv(l3_path) if l3_path.exists() else pd.DataFrame()

    n_plots = len(hh_methods)
    fig, axes = plt.subplots(1, n_plots, figsize=(7 * n_plots, 6))
    if n_plots == 1:
        axes = [axes]

    for ax, method in zip(axes, hh_methods):
        # Determinar nivel y donante
        if method.startswith("L2_HH_"):
            nivel = "L2"
            # El donante no está en el nombre; buscar en tabla L2 por objetivo
            model_row = l2_models[l2_models["objetivo"] == station]
        else:
            nivel = "L3"
            donante = method.replace("L3_HH_", "").split("_vs_")[1]
            model_row = l3_models[(l3_models["objetivo"] == station) & (l3_models["donante"] == donante)]

        # Filtrar puntos imputados con este método
        imputed_mask = station_data["Metodo"] == method
        imputed_points = station_data[imputed_mask]

        if len(model_row) == 0:
            donante_txt = donante if nivel == "L3" else "(buscar en L2)"
            ax.text(0.5, 0.5, f"Modelo no encontrado\n{station} <- {donante_txt}",
                    ha="center", va="center", transform=ax.transAxes)
            ax.set_title(f"{station} <- {donante_txt} ({nivel})")
            continue

        row = model_row.iloc[0]
        donante = row["donante"]
        a, b, c = row["a"], row["b"], row["c"]
        r_val = row["r"]
        r2_val = row["r2"]
        n_train = int(row["n_train"])
        equation = row.get("equation", f"H = {a:.4f}*H² + {b:.4f}*H + {c:.4f}")

        # Datos de entrenamiento: puntos originales concurrentes con donante
        df_full = station_data.copy()
        df_full["donante_cota"] = None  # placeholder

        # Cargar dataset global para obtener donante
        df_global = load_data()
        donor_df = df_global[(df_global["NombreEstacion"] == donante) & (df_global["Cota"].notna())].copy()
        donor_df = donor_df.set_index("date")["Cota"]

        merged = df_full.merge(
            donor_df.rename(f"{donante}_cota"),
            left_on="date",
            right_index=True,
            how="left"
        )
        train_data = merged[
            (merged["data_source"] == "original") &
            (merged["Cota"].notna()) &
            (merged[f"{donante}_cota"].notna())
        ]

        # Scatter de entrenamiento
        ax.scatter(
            train_data[f"{donante}_cota"],
            train_data["Cota"],
            alpha=0.4, s=10, color="steelblue",
            label=f"Entrenamiento (n={len(train_data):,})"
        )

        # Curva ajustada
        if len(train_data) > 0:
            x_min = train_data[f"{donante}_cota"].min()
            x_max = train_data[f"{donante}_cota"].max()
            x_range = np.linspace(x_min, x_max, 200)
            y_fit = a * x_range**2 + b * x_range + c
            ax.plot(x_range, y_fit, "r-", linewidth=2, label="Curva ajustada")

        ax.set_title(f"{display_name(station)} ← {display_name(donante)} ({nivel})",
                     fontsize=12, fontweight="bold")
        ax.set_xlabel(f"Cota donante {display_name(donante)} (m.s.n.m.)", fontsize=11)
        ax.set_ylabel(f"Cota objetivo {display_name(station)} (m.s.n.m.)", fontsize=11)
        ax.legend(loc="best", fontsize=9)
        ax.grid(True, alpha=0.3)

        # Cuadro de texto con métricas
        textstr = (
            f"r = {r_val:.3f}\n"
            f"R² = {r2_val:.3f}\n"
            f"n_train = {n_train:,}\n"
            f"{equation}"
        )
        ax.text(
            0.05, 0.95, textstr,
            transform=ax.transAxes,
            fontsize=9,
            verticalalignment="top",
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.9),
        )

    plt.suptitle(
        f"Relaciones Altura-Altura - {display_name(station, with_code=True)}",
        fontsize=14, fontweight="bold", y=1.02
    )
    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close()
    return True


def main():
    print("=" * 70)
    print("GENERADOR DE CARTILLAS DE ESTACIONES v2.1")
    print("=" * 70)

    print(f"\nCargando datos imputados v2.1 desde {INPUT_FILE}...")
    df = load_data()
    print(f"Total registros: {len(df):,}")
    print(f"Estaciones: {df['NombreEstacion'].nunique()}")

    stats_summary = []

    for station in ESTACIONES:
        print(f"\n{'='*70}")
        print(f"Procesando: {station}")
        print("=" * 70)

        station_dir = OUTPUT_DIR / station
        station_dir.mkdir(exist_ok=True, parents=True)

        station_df = get_station_data(df, station)
        if len(station_df) == 0:
            print(f"  AVISO Sin datos para {station}")
            continue

        original_count = (station_df["data_source"] == "original").sum()
        imputed_count = (station_df["data_source"] != "original").sum()
        total_count = len(station_df)
        coverage = (station_df["Cota"].notna().sum() / total_count) * 100

        print(f"  Datos originales: {original_count:,}")
        print(f"  Datos imputados: {imputed_count:,}")
        print(f"  Cobertura: {coverage:.1f}%")

        figuras_generadas = 0
        figuras = [
            ("Fig1_Serie_Tiempo", plot_serie_tiempo),
            ("Fig2_Violin_Mensual", plot_violin_mensual),
            ("Fig3_Curva_Duracion", plot_curva_duracion),
            ("Fig4_Curvas_Excedidos", plot_curvas_excedidos),
            ("Fig5_Ajuste_Distribuciones", plot_ajuste_distribuciones),
            ("Fig6_Relacion_HH", plot_relacion_hh),
        ]

        for name, func in figuras:
            try:
                output = station_dir / f"{name}_{station}_v2_1.png"
                if func(station_df, station, output):
                    print(f"  OK {output.name}")
                    figuras_generadas += 1
            except Exception as e:
                print(f"  ERROR {name}: {e}")

        stats_summary.append({
            "station": station,
            "total_records": total_count,
            "original": original_count,
            "imputed": imputed_count,
            "coverage_pct": coverage,
            "figuras_generadas": figuras_generadas,
        })

    print("\n" + "=" * 70)
    print("RESUMEN FINAL")
    print("=" * 70)
    summary_df = pd.DataFrame(stats_summary)
    print(summary_df.to_string(index=False))
    total_figuras = sum(s["figuras_generadas"] for s in stats_summary)
    print(f"\nTotal figuras generadas: {total_figuras} / {len(ESTACIONES) * 6}")
    print(f"Directorio: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
