#!/usr/bin/env python3
"""
07_auditoria_todas_estaciones.py
================================

Auditoria detallada de TODAS las estaciones del pipeline v2.1.

Para cada estacion se genera una figura de cinco paneles:
- Serie temporal completa dentro del rango oficial
- Zoom a periodo con imputacion L2
- Boxplot crudo vs imputado
- Media mensual multianual
- Dispersion H-H con curva ajustada (si aplica)

Salidas:
- auditoria_todas_estaciones_resumen.csv
- auditoria_todas_estaciones_mensual.csv
- auditoria_todas_estaciones_percentiles.csv
- auditoria_todas_estaciones_vs_student.csv
- figuras/auditoria/auditoria_<ESTACION>.png (una por estacion)
- auditoria_todas_estaciones.md
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
WORK_DIR = PROJECT_ROOT / "backend" / "data" / "work" / "imputation_v2_1"
OUTPUT_DIR = WORK_DIR / "output"
FIGURES_DIR = OUTPUT_DIR / "figuras" / "auditoria"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

IMPUTED_PATH = OUTPUT_DIR / "Datos_Imputados.csv"
PREPARED_PATH = OUTPUT_DIR / "Resumen_Crudos_IDEAM_2026_v2_1.csv"
MODELS_PATH = OUTPUT_DIR / "Tabla_Modelos_HH_Seleccionados.csv"
RANGES_PATH = OUTPUT_DIR / "resumen_rangos_estaciones.csv"

STUDENT_IMP_PATH = (
    PROJECT_ROOT
    / "backend"
    / "data"
    / "raw"
    / "SERIE NIVELES IDEAM A 2026"
    / "Version Homegeneizada HAR STEFY"
    / "Resultados primera corrida Harstefy"
    / "imputation_pipeline"
    / "Datos_Imputados.csv"
)


def load_data():
    df_imp = pd.read_csv(IMPUTED_PATH)
    df_imp["Fecha"] = pd.to_datetime(df_imp["Fecha"], errors="coerce")

    df_raw = pd.read_csv(PREPARED_PATH)
    df_raw["date"] = pd.to_datetime(df_raw["date"], errors="coerce")
    df_raw = df_raw.rename(columns={"station": "NombreEstacion", "level": "Cota", "date": "Fecha"})

    df_models = pd.read_csv(MODELS_PATH)
    models_dict = {row["objetivo"]: row.to_dict() for _, row in df_models.iterrows()}

    df_ranges = pd.read_csv(RANGES_PATH)
    df_ranges["Fecha_Inicio"] = pd.to_datetime(df_ranges["Fecha_Inicio"], errors="coerce")
    df_ranges["Fecha_Fin"] = pd.to_datetime(df_ranges["Fecha_Fin"], errors="coerce")
    official_ranges = {
        row["Estacion"]: (row["Fecha_Inicio"], row["Fecha_Fin"])
        for _, row in df_ranges.iterrows()
    }

    return df_imp, df_raw, models_dict, official_ranges


def load_student_data():
    if not STUDENT_IMP_PATH.exists():
        return None
    df = pd.read_csv(STUDENT_IMP_PATH)
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
    name_map = {
        "ARMENIA": "ARMENIA",
        "BARBOSA": "BARBOSA",
        "CALAMAR": "CALAMAR",
        "COYONGAL": "COYONGAL",
        "EL_BANCO": "EL_BANCO",
        "EL_CONTENTO": "EL_CONTENTO",
        "GAMARRA_AUT": "GAMARRA_AUT",
        "LA_GLORIA": "LA_GLORIA",
        "LAS_AGUADAS": "LAS_AGUADAS",
        "LAS_PALOMAS": "LAS_PALOMAS",
        "MAGANGUE": "MAGANGUE",
        "PENONCITO": "PENONCITO",
        "PLATO": "PLATO",
        "PUERTO_WILCHES": "PUERTO_WILCHES",
        "RIO_NUEVO": "RIO_NUEVO",
        "SAN_PEDRITO": "SAN_PEDRITO",
        "SITIO_NUEVO": "SITIO_NUEVO",
        "TENERIFE": "TENERIFE",
    }
    df["NombreEstacion"] = df["NombreEstacion"].map(name_map).fillna(df["NombreEstacion"])
    return df


def apply_range_filter(df, official_ranges, station_col="NombreEstacion", date_col="Fecha"):
    mask_keep = pd.Series(False, index=df.index)
    for st, (start, end) in official_ranges.items():
        m = (df[station_col] == st) & (df[date_col] >= start) & (df[date_col] <= end)
        mask_keep = mask_keep | m
    return df[mask_keep].copy()


def compute_stats(series):
    s = series.dropna()
    if len(s) == 0:
        return {}
    return {
        "n": len(s),
        "media": round(s.mean(), 4),
        "mediana": round(s.median(), 4),
        "std": round(s.std(), 4),
        "min": round(s.min(), 4),
        "p5": round(s.quantile(0.05), 4),
        "p25": round(s.quantile(0.25), 4),
        "p75": round(s.quantile(0.75), 4),
        "p95": round(s.quantile(0.95), 4),
        "max": round(s.max(), 4),
    }


def find_l2_period(df_station, min_gap_days=30):
    df = df_station.sort_values("Fecha").reset_index(drop=True)
    mask_l2 = df["Nivel_Imputacion"] == 2
    if not mask_l2.any():
        return None, None

    groups = []
    start = None
    for i, is_l2 in enumerate(mask_l2):
        if is_l2 and start is None:
            start = i
        elif not is_l2 and start is not None:
            groups.append((start, i))
            start = None
    if start is not None:
        groups.append((start, len(mask_l2)))

    best = max(groups, key=lambda g: g[1] - g[0])
    if best[1] - best[0] < min_gap_days:
        best = groups[0]

    fecha_inicio = df.loc[best[0], "Fecha"]
    fecha_fin = df.loc[best[1] - 1, "Fecha"]
    fecha_inicio = max(df["Fecha"].min(), fecha_inicio - pd.Timedelta(days=15))
    fecha_fin = min(df["Fecha"].max(), fecha_fin + pd.Timedelta(days=15))
    return fecha_inicio, fecha_fin


def plot_station_audit(station, df_imp, df_raw, model, student_data, official_ranges):
    start, end = official_ranges.get(station, (df_imp["Fecha"].min(), df_imp["Fecha"].max()))
    df_s = df_imp[(df_imp["NombreEstacion"] == station) & (df_imp["Fecha"] >= start) & (df_imp["Fecha"] <= end)].sort_values("Fecha").reset_index(drop=True)
    df_s_raw = df_raw[(df_raw["NombreEstacion"] == station) & (df_raw["Fecha"] >= start) & (df_raw["Fecha"] <= end)].sort_values("Fecha").reset_index(drop=True)

    fig = plt.figure(figsize=(16, 20))
    gs = fig.add_gridspec(4, 2, hspace=0.35, wspace=0.25)

    # 1. Serie temporal completa
    ax1 = fig.add_subplot(gs[0, :])
    orig = df_s[df_s["Nivel_Imputacion"] == 0]
    l1 = df_s[df_s["Nivel_Imputacion"] == 1]
    l2 = df_s[df_s["Nivel_Imputacion"] == 2]
    nan_points = df_s[df_s["Cota"].isna()]
    ax1.scatter(orig["Fecha"], orig["Cota"], s=2, color="#4A6FA5", label=f"Original ({len(orig)})", alpha=0.7)
    if len(l1) > 0:
        ax1.scatter(l1["Fecha"], l1["Cota"], s=2, color="#8FB8ED", label=f"L1 ({len(l1)})")
    if len(l2) > 0:
        ax1.scatter(l2["Fecha"], l2["Cota"], s=2, color="#F4A261", label=f"L2 ({len(l2)})", alpha=0.7)
    if len(nan_points) > 0:
        y_min, y_max = ax1.get_ylim()
        ax1.scatter(nan_points["Fecha"], [y_min] * len(nan_points), s=2, color="#E63946", label=f"NaN ({len(nan_points)})", alpha=0.5, marker="x")
    ax1.set_title(f"{station} - Serie temporal completa ({start.date()} a {end.date()})", fontweight="bold", fontsize=14)
    ax1.set_ylabel("Cota (m)")
    ax1.legend(loc="upper right")
    ax1.grid(alpha=0.3)

    # 2. Zoom a periodo con L2
    ax2 = fig.add_subplot(gs[1, :])
    fecha_ini, fecha_fin = find_l2_period(df_s)
    if fecha_ini is not None:
        df_zoom = df_s[(df_s["Fecha"] >= fecha_ini) & (df_s["Fecha"] <= fecha_fin)]
        ax2.plot(df_zoom["Fecha"], df_zoom["Cota"], color="#333333", linewidth=0.8, alpha=0.5)
        for nivel, color, label in [(0, "#4A6FA5", "Original"), (1, "#8FB8ED", "L1"), (2, "#F4A261", "L2")]:
            sub = df_zoom[df_zoom["Nivel_Imputacion"] == nivel]
            if len(sub) > 0:
                ax2.scatter(sub["Fecha"], sub["Cota"], s=15, color=color, label=label, zorder=3)
        nan_zoom = df_zoom[df_zoom["Cota"].isna()]
        if len(nan_zoom) > 0:
            y_min2, y_max2 = ax2.get_ylim()
            ax2.scatter(nan_zoom["Fecha"], [y_min2] * len(nan_zoom), s=15, color="#E63946", label="NaN", marker="x", zorder=3)
        ax2.set_title(f"Zoom a periodo con imputacion L2 ({fecha_ini.date()} a {fecha_fin.date()})", fontweight="bold")
    else:
        ax2.text(0.5, 0.5, "Sin imputaciones L2", ha="center", va="center", transform=ax2.transAxes)
        ax2.set_title("Zoom a periodo con imputacion L2", fontweight="bold")
    ax2.set_ylabel("Cota (m)")
    handles, labels = ax2.get_legend_handles_labels()
    if handles:
        ax2.legend(handles, labels, loc="upper right")
    ax2.grid(alpha=0.3)

    # 3. Boxplot original vs imputado
    ax3 = fig.add_subplot(gs[2, 0])
    data_box = []
    labels = []
    if len(df_s_raw) > 0:
        data_box.append(df_s_raw["Cota"].dropna().values)
        labels.append("Crudo")
    data_box.append(df_s["Cota"].dropna().values)
    labels.append("Imputado")
    bp = ax3.boxplot(data_box, tick_labels=labels, patch_artist=True)
    colors = ["#4A6FA5", "#F4A261"]
    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    ax3.set_title("Distribucion: crudo vs imputado", fontweight="bold")
    ax3.set_ylabel("Cota (m)")
    ax3.grid(axis="y", alpha=0.3)

    # 4. Media mensual multianual
    ax4 = fig.add_subplot(gs[2, 1])
    df_s["Mes"] = df_s["Fecha"].dt.month
    df_s_raw["Mes"] = df_s_raw["Fecha"].dt.month
    monthly_imp = df_s.groupby("Mes")["Cota"].mean()
    monthly_raw = df_s_raw.groupby("Mes")["Cota"].mean()
    ax4.plot(monthly_raw.index, monthly_raw.values, marker="o", color="#4A6FA5", label="Crudo")
    ax4.plot(monthly_imp.index, monthly_imp.values, marker="s", color="#F4A261", label="Imputado")
    ax4.set_title("Media mensual multianual", fontweight="bold")
    ax4.set_xlabel("Mes")
    ax4.set_ylabel("Cota media (m)")
    ax4.set_xticks(range(1, 13))
    ax4.legend()
    ax4.grid(alpha=0.3)

    # 5. Dispersion H-H
    ax5 = fig.add_subplot(gs[3, :])
    if model is not None:
        donante = model["donante"]
        df_don = df_imp[df_imp["NombreEstacion"] == donante][["Fecha", "Cota"]].rename(
            columns={"Cota": "Cota_donante"}
        )
        df_obj = df_s[["Fecha", "Cota"]].rename(columns={"Cota": "Cota_objetivo"})
        merged = pd.merge(df_obj, df_don, on="Fecha", how="inner").dropna()
        if len(merged) > 0:
            x = merged["Cota_donante"].values
            y = merged["Cota_objetivo"].values
            a, b, c = model["a"], model["b"], model["c"]
            x_line = np.linspace(x.min(), x.max(), 200)
            y_line = a * x_line**2 + b * x_line + c
            ax5.scatter(x, y, s=8, alpha=0.4, color="#4A6FA5", label="Datos concurrentes")
            ax5.plot(x_line, y_line, color="#E63946", linewidth=2, label=f"Curva H-H (R2={model['r2']:.4f})")
            ax5.set_title(f"Relacion H-H: {station} (objetivo) vs {donante} (donante)", fontweight="bold")
            ax5.set_xlabel(f"Cota {donante} (m)")
            ax5.set_ylabel(f"Cota {station} (m)")
            ax5.legend()
            ax5.grid(alpha=0.3)
        else:
            ax5.text(0.5, 0.5, "Sin datos concurrentes para graficar", ha="center", va="center", transform=ax5.transAxes)
            ax5.set_title("Relacion H-H", fontweight="bold")
    else:
        ax5.text(0.5, 0.5, "Sin modelo H-H seleccionado", ha="center", va="center", transform=ax5.transAxes)
        ax5.set_title("Relacion H-H", fontweight="bold")

    fig.suptitle(f"Auditoria de imputacion v2.1 - Estacion: {station} ({start.date()} a {end.date()})", fontsize=16, fontweight="bold", y=0.995)

    fig_path = FIGURES_DIR / f"auditoria_{station}.png"
    plt.savefig(fig_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return fig_path, (start, end)


def main():
    print("=" * 70)
    print("AUDITORIA DE TODAS LAS ESTACIONES - IMPUTACION v2.1")
    print("=" * 70)

    df_imp, df_raw, models_dict, official_ranges = load_data()
    df_student = load_student_data()

    df_imp = apply_range_filter(df_imp, official_ranges)
    df_raw = apply_range_filter(df_raw, official_ranges)
    if df_student is not None:
        df_student = apply_range_filter(df_student, official_ranges)

    stations = sorted(official_ranges.keys())

    resumen_rows = []
    mensual_rows = []
    percentil_rows = []
    vs_student_rows = []

    fig_paths = []
    station_ranges = {}

    for station in stations:
        print(f"\nProcesando {station}...")
        df_s = df_imp[df_imp["NombreEstacion"] == station].sort_values("Fecha")
        df_s_raw = df_raw[df_raw["NombreEstacion"] == station].sort_values("Fecha")

        n_total = len(df_s)
        n_orig = int((df_s["Nivel_Imputacion"] == 0).sum())
        n_l1 = int((df_s["Nivel_Imputacion"] == 1).sum())
        n_l2 = int((df_s["Nivel_Imputacion"] == 2).sum())
        n_nan = int(df_s["Cota"].isna().sum())

        stats_raw = compute_stats(df_s_raw["Cota"])
        stats_imp = compute_stats(df_s["Cota"])

        model = models_dict.get(station)

        resumen_rows.append(
            {
                "Estacion": station,
                "Fecha_Inicio": df_s["Fecha"].min().strftime("%Y-%m-%d"),
                "Fecha_Fin": df_s["Fecha"].max().strftime("%Y-%m-%d"),
                "Dias_Rango": n_total,
                "N_Original": n_orig,
                "N_L1": n_l1,
                "N_L2": n_l2,
                "N_NaN": n_nan,
                "Cobertura_pct": round(100 * (n_total - n_nan) / n_total, 2),
                "Donante_HH": model["donante"] if model else None,
                "R2_HH": round(model["r2"], 4) if model else None,
                "N_Train_HH": model["n_train"] if model else None,
            }
        )

        row_pct = {"Estacion": station}
        for k, v in stats_raw.items():
            row_pct[f"crudo_{k}"] = v
        for k, v in stats_imp.items():
            row_pct[f"imputado_{k}"] = v
        percentil_rows.append(row_pct)

        df_s = df_s.copy()
        df_s_raw = df_s_raw.copy()
        df_s["Mes"] = df_s["Fecha"].dt.month
        df_s_raw["Mes"] = df_s_raw["Fecha"].dt.month
        monthly_imp = df_s.groupby("Mes")["Cota"].mean().reset_index()
        monthly_raw = df_s_raw.groupby("Mes")["Cota"].mean().reset_index()
        for mes in range(1, 13):
            v_raw = monthly_raw[monthly_raw["Mes"] == mes]["Cota"].values
            v_imp = monthly_imp[monthly_imp["Mes"] == mes]["Cota"].values
            mensual_rows.append(
                {
                    "Estacion": station,
                    "Mes": mes,
                    "Media_Crudo_m": round(v_raw[0], 4) if len(v_raw) > 0 else np.nan,
                    "Media_Imputado_m": round(v_imp[0], 4) if len(v_imp) > 0 else np.nan,
                    "Diferencia_m": round(v_imp[0] - v_raw[0], 4) if len(v_raw) > 0 and len(v_imp) > 0 else np.nan,
                }
            )

        if df_student is not None:
            merged = pd.merge(
                df_s[["Fecha", "Cota"]],
                df_student[df_student["NombreEstacion"] == station][["Fecha", "Cota"]],
                on="Fecha",
                suffixes=("_v2_1", "_student"),
                how="inner",
            ).dropna()
            if len(merged) > 0:
                diff = merged["Cota_v2_1"] - merged["Cota_student"]
                vs_student_rows.append(
                    {
                        "Estacion": station,
                        "N_Comparable": len(merged),
                        "Diff_Media_m": round(diff.abs().mean(), 4),
                        "Diff_Max_m": round(diff.abs().max(), 4),
                        "Diff_Std_m": round(diff.std(), 4),
                    }
                )

        fig_path, (st_start, st_end) = plot_station_audit(station, df_imp, df_raw, model, df_student, official_ranges)
        fig_paths.append(fig_path)
        station_ranges[station] = (st_start.date(), st_end.date())
        print(f"      Figura: {fig_path.name}")

    df_resumen = pd.DataFrame(resumen_rows)
    df_resumen.to_csv(OUTPUT_DIR / "auditoria_todas_estaciones_resumen.csv", index=False)
    print(f"\nGuardado: auditoria_todas_estaciones_resumen.csv")

    df_mensual = pd.DataFrame(mensual_rows)
    df_mensual.to_csv(OUTPUT_DIR / "auditoria_todas_estaciones_mensual.csv", index=False)
    print(f"Guardado: auditoria_todas_estaciones_mensual.csv")

    df_percentil = pd.DataFrame(percentil_rows)
    df_percentil.to_csv(OUTPUT_DIR / "auditoria_todas_estaciones_percentiles.csv", index=False)
    print(f"Guardado: auditoria_todas_estaciones_percentiles.csv")

    if vs_student_rows:
        df_vs = pd.DataFrame(vs_student_rows)
        df_vs.to_csv(OUTPUT_DIR / "auditoria_todas_estaciones_vs_student.csv", index=False)
        print(f"Guardado: auditoria_todas_estaciones_vs_student.csv")

    report = []
    report.append("# Auditoria de todas las estaciones - Imputacion v2.1")
    report.append("")
    report.append(f"- **Total de estaciones auditadas:** {len(stations)}")
    report.append("")
    report.append("## Rangos oficiales usados")
    report.append("")
    report.append("| Estacion | Inicio oficial | Fin oficial |")
    report.append("|----------|----------------|-------------|")
    for station in stations:
        st, en = station_ranges[station]
        report.append(f"| {station} | {st} | {en} |")
    report.append("")
    report.append("## Resumen agregado")
    report.append("")
    report.append("| Estacion | Inicio | Fin | Dias | Original | L1 | L2 | NaN | Cobertura % | Donante H-H | R2 |")
    report.append("|----------|--------|-----|------|----------|----|----|-----|-------------|-------------|-----|")
    for _, row in df_resumen.iterrows():
        report.append(
            f"| {row['Estacion']} | {row['Fecha_Inicio']} | {row['Fecha_Fin']} | "
            f"{row['Dias_Rango']} | {row['N_Original']} | {row['N_L1']} | {row['N_L2']} | "
            f"{row['N_NaN']} | {row['Cobertura_pct']} | {row['Donante_HH']} | {row['R2_HH']} |"
        )
    report.append("")
    report.append("## Percentiles: crudo vs imputado")
    report.append("")
    report.append("| Estacion | n crudo | media crudo | p5 crudo | p95 crudo | n imp | media imp | p5 imp | p95 imp |")
    report.append("|----------|---------|-------------|----------|-----------|-------|-----------|--------|---------|")
    for _, row in df_percentil.iterrows():
        report.append(
            f"| {row['Estacion']} | {row.get('crudo_n', '')} | {row.get('crudo_media', '')} | "
            f"{row.get('crudo_p5', '')} | {row.get('crudo_p95', '')} | {row.get('imputado_n', '')} | "
            f"{row.get('imputado_media', '')} | {row.get('imputado_p5', '')} | {row.get('imputado_p95', '')} |"
        )
    report.append("")
    report.append("## Medias mensuales: diferencia imputado - crudo")
    report.append("")
    df_mensual_pivot = df_mensual.pivot(index="Estacion", columns="Mes", values="Diferencia_m")
    report.append("| Estacion | Ene | Feb | Mar | Abr | May | Jun | Jul | Ago | Sep | Oct | Nov | Dic |")
    report.append("|----------|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|")
    for estacion in stations:
        vals = []
        for m in range(1, 13):
            v = df_mensual_pivot.loc[estacion, m] if (estacion in df_mensual_pivot.index and m in df_mensual_pivot.columns) else np.nan
            vals.append(f"{v:.3f}" if pd.notna(v) else "")
        report.append(f"| {estacion} | " + " | ".join(vals) + " |")
    report.append("")

    if vs_student_rows:
        report.append("## Comparacion con corrida anterior (estudiantes)")
        report.append("")
        report.append("| Estacion | N comparable | Diff media (m) | Diff max (m) |")
        report.append("|----------|--------------|----------------|--------------|")
        for _, row in df_vs.iterrows():
            report.append(
                f"| {row['Estacion']} | {row['N_Comparable']} | {row['Diff_Media_m']} | {row['Diff_Max_m']} |"
            )
        report.append("")

    report.append("## Figuras por estacion")
    report.append("")
    for station, fig_path in zip(stations, fig_paths):
        report.append(f"### {station}")
        report.append(f"![{station}]({fig_path.relative_to(OUTPUT_DIR).as_posix()})")
        report.append("")

    report_path = OUTPUT_DIR / "auditoria_todas_estaciones.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report))
    print(f"\nGuardado: {report_path}")

    print("\n" + "=" * 70)
    print("AUDITORIA FINALIZADA")
    print("=" * 70)


if __name__ == "__main__":
    main()
