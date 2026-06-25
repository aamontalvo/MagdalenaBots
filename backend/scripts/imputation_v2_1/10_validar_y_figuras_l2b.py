#!/usr/bin/env python3
"""
10_validar_y_figuras_l2b.py
===========================

Valida el experimento L2b y genera figuras comparativas.

Validaciones:
- Ningun valor fuera del rango historico original de cada estacion.
- Cobertura esperada dentro del rango oficial.

Figuras:
- Serie temporal L2 vs L2b para cada una de las 3 estaciones.
- Media mensual: crudo, L2, L2b.
- Dispersion H-H del nuevo modelo L2b.
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
OUTPUT_DIR = PROJECT_ROOT / "backend" / "data" / "work" / "imputation_v2_1" / "output"
FIGURES_DIR = OUTPUT_DIR / "figuras" / "l2b_experimento"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

L2B_PATH = OUTPUT_DIR / "Datos_Imputados_L2b_experimento.csv"
PREPARED_PATH = OUTPUT_DIR / "Resumen_Crudos_IDEAM_2026_v2_1.csv"
RANGES_PATH = OUTPUT_DIR / "resumen_rangos_estaciones.csv"
L2B_MODELS_PATH = OUTPUT_DIR / "Tabla_Modelos_L2b_experimento.csv"

TARGETS = ["SAN_PABLO", "EL_CONTENTO", "GAMARRA"]


def load_data():
    df_l2b = pd.read_csv(L2B_PATH, low_memory=False)
    df_l2b["Fecha"] = pd.to_datetime(df_l2b["Fecha"], errors="coerce")

    df_raw = pd.read_csv(PREPARED_PATH)
    df_raw["date"] = pd.to_datetime(df_raw["date"], errors="coerce")
    df_raw = df_raw.rename(columns={"station": "NombreEstacion", "level": "Cota", "date": "Fecha"})

    ranges = pd.read_csv(RANGES_PATH)
    ranges["Fecha_Inicio"] = pd.to_datetime(ranges["Fecha_Inicio"], errors="coerce")
    ranges["Fecha_Fin"] = pd.to_datetime(ranges["Fecha_Fin"], errors="coerce")
    official_ranges = {
        row["Estacion"]: (row["Fecha_Inicio"], row["Fecha_Fin"])
        for _, row in ranges.iterrows()
    }

    models = pd.read_csv(L2B_MODELS_PATH)
    models_dict = {row["objetivo"]: row.to_dict() for _, row in models.iterrows()}

    return df_l2b, df_raw, official_ranges, models_dict


def compute_original_ranges(df_raw):
    ranges = {}
    for station, grp in df_raw.groupby("NombreEstacion"):
        valid = grp["Cota"].dropna()
        if len(valid) > 0:
            ranges[station] = (valid.min(), valid.max())
    return ranges


def validate_l2b_ranges(df_l2b, original_ranges, official_ranges):
    violations = []
    for target in TARGETS:
        if target not in original_ranges:
            continue
        rmin, rmax = original_ranges[target]
        start, end = official_ranges.get(target, (df_l2b["Fecha"].min(), df_l2b["Fecha"].max()))
        df_s = df_l2b[
            (df_l2b["NombreEstacion"] == target)
            & (df_l2b["Fecha"] >= start)
            & (df_l2b["Fecha"] <= end)
        ]
        mask = (df_s["Cota"] < rmin) | (df_s["Cota"] > rmax)
        for _, row in df_s[mask].iterrows():
            violations.append(
                {
                    "Estacion": target,
                    "Fecha": row["Fecha"].strftime("%Y-%m-%d"),
                    "Cota": row["Cota"],
                    "Rango_Min": rmin,
                    "Rango_Max": rmax,
                }
            )
    return pd.DataFrame(violations)


def plot_comparison(target, df_l2b, df_raw, model, official_ranges):
    start, end = official_ranges.get(target, (df_l2b["Fecha"].min(), df_l2b["Fecha"].max()))
    df_s = df_l2b[
        (df_l2b["NombreEstacion"] == target)
        & (df_l2b["Fecha"] >= start)
        & (df_l2b["Fecha"] <= end)
    ].sort_values("Fecha").reset_index(drop=True)
    df_s_raw = df_raw[
        (df_raw["NombreEstacion"] == target)
        & (df_raw["Fecha"] >= start)
        & (df_raw["Fecha"] <= end)
    ].sort_values("Fecha").reset_index(drop=True)

    fig, axes = plt.subplots(3, 1, figsize=(16, 14), sharex=True)

    # Panel 1: serie temporal
    ax = axes[0]
    orig = df_s[df_s["Nivel_Imputacion"] == 0]
    l1 = df_s[df_s["Nivel_Imputacion"] == 1]
    l2 = df_s[df_s["Nivel_Imputacion"] == 2]
    l2b = df_s[df_s["Nivel_Imputacion_L2b"] == 3]
    ax.scatter(orig["Fecha"], orig["Cota"], s=2, color="#4A6FA5", label="Original", alpha=0.7)
    if len(l1) > 0:
        ax.scatter(l1["Fecha"], l1["Cota"], s=2, color="#8FB8ED", label="L1")
    if len(l2) > 0:
        ax.scatter(l2["Fecha"], l2["Cota"], s=2, color="#F4A261", label="L2", alpha=0.7)
    if len(l2b) > 0:
        ax.scatter(l2b["Fecha"], l2b["Cota"], s=2, color="#2A9D8F", label="L2b")
    nan_l2 = df_s[(df_s["Nivel_Imputacion"].isna()) & (df_s["Nivel_Imputacion_L2b"].isna()) & (df_s["Cota"].isna())]
    if len(nan_l2) > 0:
        y_min, _ = ax.get_ylim()
        ax.scatter(nan_l2["Fecha"], [y_min] * len(nan_l2), s=2, color="#E63946", label="NaN", marker="x", alpha=0.5)
    ax.set_title(f"{target} - Serie temporal L2 vs L2b", fontweight="bold")
    ax.set_ylabel("Cota (m)")
    ax.legend(loc="upper right")
    ax.grid(alpha=0.3)

    # Panel 2: media mensual multianual
    ax = axes[1]
    df_s["Mes"] = df_s["Fecha"].dt.month
    df_s_raw["Mes"] = df_s_raw["Fecha"].dt.month
    monthly_raw = df_s_raw.groupby("Mes")["Cota"].mean()
    monthly_l2b = df_s.groupby("Mes")["Cota"].mean()
    ax.plot(monthly_raw.index, monthly_raw.values, marker="o", color="#4A6FA5", label="Crudo")
    ax.plot(monthly_l2b.index, monthly_l2b.values, marker="s", color="#2A9D8F", label="L2b")
    ax.set_title(f"{target} - Media mensual multianual", fontweight="bold")
    ax.set_ylabel("Cota media (m)")
    ax.set_xticks(range(1, 13))
    ax.legend()
    ax.grid(alpha=0.3)

    # Panel 3: dispersion H-H del modelo L2b
    ax = axes[2]
    donor = model["donante"]
    df_don = df_l2b[df_l2b["NombreEstacion"] == donor][["Fecha", "Cota"]].rename(columns={"Cota": "Cota_donante"})
    df_obj = df_s[["Fecha", "Cota"]].rename(columns={"Cota": "Cota_objetivo"})
    merged = pd.merge(df_obj, df_don, on="Fecha", how="inner").dropna()
    if len(merged) > 0:
        x = merged["Cota_donante"].values
        y = merged["Cota_objetivo"].values
        a, b, c = model["a"], model["b"], model["c"]
        x_line = np.linspace(x.min(), x.max(), 200)
        y_line = a * x_line**2 + b * x_line + c
        ax.scatter(x, y, s=8, alpha=0.4, color="#4A6FA5", label="Datos concurrentes")
        ax.plot(x_line, y_line, color="#E63946", linewidth=2, label=f"Curva H-H (R2={model['r2']:.4f})")
        ax.set_title(f"Relacion H-H L2b: {target} vs {donor}", fontweight="bold")
        ax.set_xlabel(f"Cota {donor} (m)")
        ax.set_ylabel(f"Cota {target} (m)")
        ax.legend()
        ax.grid(alpha=0.3)

    fig.suptitle(f"Experimento L2b - {target}", fontsize=16, fontweight="bold", y=0.995)
    fig_path = FIGURES_DIR / f"comparacion_l2b_{target}.png"
    plt.tight_layout()
    plt.savefig(fig_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return fig_path


def main():
    print("=" * 70)
    print("VALIDACION Y FIGURAS DEL EXPERIMENTO L2b")
    print("=" * 70)

    df_l2b, df_raw, official_ranges, models_dict = load_data()
    original_ranges = compute_original_ranges(df_raw)

    print("\n[1/3] Validando rangos historicos en L2b...")
    violations = validate_l2b_ranges(df_l2b, original_ranges, official_ranges)
    print(f"      Violaciones: {len(violations)}")

    print("\n[2/3] Generando figuras comparativas...")
    fig_paths = []
    for target in TARGETS:
        fig_path = plot_comparison(target, df_l2b, df_raw, models_dict[target], official_ranges)
        fig_paths.append(fig_path)
        print(f"      {fig_path.name}")

    print("\n[3/3] Guardando validacion...")
    out_csv = OUTPUT_DIR / "validacion_violaciones_l2b.csv"
    violations.to_csv(out_csv, index=False)
    print(f"      {out_csv.name}")

    report = []
    report.append("# Validacion del experimento L2b")
    report.append("")
    report.append(f"- **Violaciones de rango historico:** {len(violations)}")
    report.append("")
    report.append("## Figuras generadas")
    report.append("")
    for target in TARGETS:
        report.append(f"- {target}: `figuras/l2b_experimento/comparacion_l2b_{target}.png`")

    out_md = OUTPUT_DIR / "validacion_l2b.md"
    with open(out_md, "w", encoding="utf-8") as f:
        f.write("\n".join(report))
    print(f"      {out_md.name}")

    print("\n" + "=" * 70)
    print("VALIDACION Y FIGURAS FINALIZADAS")
    print("=" * 70)


if __name__ == "__main__":
    main()
