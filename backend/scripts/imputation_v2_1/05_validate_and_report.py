#!/usr/bin/env python3
"""
05_validate_and_report.py
=========================

Validacion post-imputacion y generacion de reporte para el pipeline v2.1.

Validaciones:
- Todos los valores dentro del rango historico original.
- Deteccion de saltos temporales anomalos.
- Coherencia espacial con estaciones vecinas (ventana movil 3 dias).
- Analisis de residuos de modelos H-H.
- Comparacion con corrida anterior (estudiantes).

Salidas:
- validacion_post_imputacion.csv
- validacion_post_imputacion.md
- figura_series_temporales.png
- figura_cobertura_imputacion.png
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
WORK_DIR = PROJECT_ROOT / "backend" / "data" / "work" / "imputation_v2_1"
OUTPUT_DIR = WORK_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

IMPUTED_PATH = OUTPUT_DIR / "Datos_Imputados.csv"
MODELS_PATH = OUTPUT_DIR / "Tabla_Modelos_HH_Seleccionados.csv"
RESUMEN_PATH = OUTPUT_DIR / "Resumen_Imputacion.csv"
PREPARED_PATH = OUTPUT_DIR / "Resumen_Crudos_IDEAM_2026_v2_1.csv"
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
STUDENT_RESUMEN_PATH = (
    PROJECT_ROOT
    / "backend"
    / "data"
    / "raw"
    / "SERIE NIVELES IDEAM A 2026"
    / "Version Homegeneizada HAR STEFY"
    / "Resultados primera corrida Harstefy"
    / "imputation_pipeline"
    / "Resumen_Imputacion.csv"
)


def load_official_ranges():
    df = pd.read_csv(RANGES_PATH)
    df["Fecha_Inicio"] = pd.to_datetime(df["Fecha_Inicio"], errors="coerce")
    df["Fecha_Fin"] = pd.to_datetime(df["Fecha_Fin"], errors="coerce")
    return {
        row["Estacion"]: (row["Fecha_Inicio"], row["Fecha_Fin"])
        for _, row in df.iterrows()
    }


def load_imputed():
    df = pd.read_csv(IMPUTED_PATH)
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
    return df


def compute_original_ranges(df_prepared):
    ranges = {}
    for station, grp in df_prepared.groupby("station"):
        valid = grp["level"].dropna()
        if len(valid) > 0:
            ranges[station] = (valid.min(), valid.max())
    return ranges


def validate_ranges(df_imputed, ranges):
    violations = []
    for station, grp in df_imputed.groupby("NombreEstacion"):
        if station not in ranges:
            continue
        rmin, rmax = ranges[station]
        mask = (grp["Cota"] < rmin) | (grp["Cota"] > rmax)
        for _, row in grp[mask].iterrows():
            violations.append(
                {
                    "Estacion": station,
                    "Fecha": row["Fecha"].strftime("%Y-%m-%d"),
                    "Cota": row["Cota"],
                    "Rango_Min": rmin,
                    "Rango_Max": rmax,
                }
            )
    return pd.DataFrame(violations)


def validate_temporal_ranges(df_imputed, official_ranges):
    """Verifica que no haya registros fuera del rango oficial de cada estacion."""
    violations = []
    for station, grp in df_imputed.groupby("NombreEstacion"):
        if station not in official_ranges:
            continue
        start, end = official_ranges[station]
        mask = (grp["Fecha"] < start) | (grp["Fecha"] > end)
        for _, row in grp[mask].iterrows():
            violations.append(
                {
                    "Estacion": station,
                    "Fecha": row["Fecha"].strftime("%Y-%m-%d"),
                    "Cota": row["Cota"],
                    "Rango_Inicio": start.strftime("%Y-%m-%d"),
                    "Rango_Fin": end.strftime("%Y-%m-%d"),
                }
            )
    return pd.DataFrame(violations)


def detect_temporal_jumps(df_imputed):
    """Detecta saltos diarios que exceden 2x el percentil 99.5 historico por estacion."""
    flags = []
    for station, grp in df_imputed.groupby("NombreEstacion"):
        grp = grp.sort_values("Fecha")
        diffs = grp["Cota"].diff().abs()
        threshold = grp["Cota"].quantile(0.995) * 2
        if pd.isna(threshold) or threshold == 0:
            threshold = diffs.quantile(0.99)
        mask = diffs > threshold
        for _, row in grp[mask].iterrows():
            flags.append(
                {
                    "Estacion": station,
                    "Fecha": row["Fecha"].strftime("%Y-%m-%d"),
                    "Cota": row["Cota"],
                    "Salto_m": diffs.loc[row.name],
                    "Umbral_m": threshold,
                }
            )
    return pd.DataFrame(flags)


def spatial_coherence(df_imputed):
    """Correlacion general entre pares de estaciones con datos concurrentes."""
    wide = df_imputed.pivot(index="Fecha", columns="NombreEstacion", values="Cota")
    results = []
    stations = wide.columns
    for i, s1 in enumerate(stations):
        for s2 in stations[i + 1 :]:
            pair = wide[[s1, s2]].dropna()
            if len(pair) < 30:
                continue
            r = pair[s1].corr(pair[s2])
            results.append(
                {
                    "Estacion_1": s1,
                    "Estacion_2": s2,
                    "Correlacion": r,
                    "N_Concurrentes": len(pair),
                }
            )
    df = pd.DataFrame(results)
    if not df.empty:
        df = df.sort_values("Correlacion")
    return df


def compare_with_student_run(df_imputed):
    if not STUDENT_IMP_PATH.exists():
        return None
    df_student = pd.read_csv(STUDENT_IMP_PATH)
    df_student["Fecha"] = pd.to_datetime(df_student["Fecha"], errors="coerce")

    # Normalizar nombres de estacion
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
    df_student["NombreEstacion"] = df_student["NombreEstacion"].map(name_map).fillna(
        df_student["NombreEstacion"]
    )

    merged = pd.merge(
        df_imputed,
        df_student,
        on=["Fecha", "NombreEstacion"],
        suffixes=("_v2_1", "_student"),
        how="inner",
    )
    merged["Diferencia_m"] = merged["Cota_v2_1"] - merged["Cota_student"]
    return merged


def plot_coverage(df_imputed, output_dir):
    """Genera figura de cobertura por estacion y nivel de imputacion."""
    counts = (
        df_imputed.groupby(["NombreEstacion", "Nivel_Imputacion"])
        .size()
        .unstack(fill_value=0)
    )
    counts = counts.rename(columns={0: "Original", 1: "L1", 2: "L2", 3: "L3"})
    counts = counts.sort_values("Original", ascending=True)

    fig, ax = plt.subplots(figsize=(12, 10))
    counts[["Original", "L1", "L2", "L3"]].plot(
        kind="barh", stacked=True, ax=ax, color=["#4A6FA5", "#8FB8ED", "#F4A261", "#2A9D8F"]
    )
    ax.set_xlabel("Numero de registros")
    ax.set_ylabel("Estacion")
    ax.set_title("Cobertura y niveles de imputacion v2.1", fontweight="bold")
    ax.legend(title="Nivel", loc="lower right")
    plt.tight_layout()
    fig_path = output_dir / "figura_cobertura_imputacion.png"
    plt.savefig(fig_path, dpi=300, bbox_inches="tight")
    return fig_path


def plot_sample_series(df_imputed, output_dir, n_stations=8):
    """Genera figura con series temporales de ejemplo."""
    stations = sorted(df_imputed["NombreEstacion"].unique())[:n_stations]
    fig, axes = plt.subplots(n_stations, 1, figsize=(14, 3 * n_stations), sharex=True)
    if n_stations == 1:
        axes = [axes]

    for ax, station in zip(axes, stations):
        df_s = df_imputed[df_imputed["NombreEstacion"] == station].sort_values("Fecha")
        orig = df_s[df_s["Nivel_Imputacion"] == 0]
        imp = df_s[df_s["Nivel_Imputacion"] > 0]
        ax.scatter(orig["Fecha"], orig["Cota"], s=1, label="Original", color="#4A6FA5")
        ax.scatter(imp["Fecha"], imp["Cota"], s=1, label="Imputado", color="#F4A261")
        ax.set_ylabel("Cota (m)")
        ax.set_title(station, fontweight="bold")
        ax.legend(loc="upper right")
        ax.grid(alpha=0.3)

    axes[-1].set_xlabel("Fecha")
    plt.tight_layout()
    fig_path = output_dir / "figura_series_temporales.png"
    plt.savefig(fig_path, dpi=300, bbox_inches="tight")
    return fig_path


def build_na_matrix(df, station_order, value_col="Cota"):
    """Construye matriz de presencia/ausencia de datos por fecha y estacion."""
    df = df.copy()
    df["tiene_dato"] = df[value_col].notna().astype(int)
    matrix = df.pivot(index="Fecha", columns="NombreEstacion", values="tiene_dato")
    for st in station_order:
        if st not in matrix.columns:
            matrix[st] = np.nan
    return matrix[station_order]


def plot_null_heatmaps(df_prepared, df_imputed, official_ranges, output_dir):
    """Genera dos heatmaps de datos nulos: antes y despues de imputacion."""
    # Asegurar que ambos datasets esten filtrados al rango oficial
    df_prepared_f = df_prepared.copy()
    df_prepared_f = df_prepared_f.rename(
        columns={"station": "NombreEstacion", "date": "Fecha", "level": "Cota"}
    )
    df_prepared_f["Fecha"] = pd.to_datetime(df_prepared_f["Fecha"], errors="coerce")

    mask_keep = pd.Series(False, index=df_prepared_f.index)
    for st, (start, end) in official_ranges.items():
        m = (df_prepared_f["NombreEstacion"] == st) & (
            df_prepared_f["Fecha"] >= start
        ) & (df_prepared_f["Fecha"] <= end)
        mask_keep = mask_keep | m
    df_prepared_f = df_prepared_f[mask_keep]

    df_imputed_f = df_imputed.copy()
    mask_keep2 = pd.Series(False, index=df_imputed_f.index)
    for st, (start, end) in official_ranges.items():
        m = (df_imputed_f["NombreEstacion"] == st) & (
            df_imputed_f["Fecha"] >= start
        ) & (df_imputed_f["Fecha"] <= end)
        mask_keep2 = mask_keep2 | m
    df_imputed_f = df_imputed_f[mask_keep2]

    station_order = sorted(official_ranges.keys())
    mat_before = build_na_matrix(df_prepared_f, station_order)
    mat_after = build_na_matrix(df_imputed_f, station_order)

    # Samplear fechas para no matar la memoria visual (max ~2000 filas)
    if len(mat_before) > 2000:
        step = len(mat_before) // 2000 + 1
        mat_before = mat_before.iloc[::step]
        mat_after = mat_after.loc[mat_before.index]

    fig, axes = plt.subplots(2, 1, figsize=(18, 16), sharex=True)

    sns.heatmap(
        mat_before.T,
        cmap="RdYlGn",
        vmin=0,
        vmax=1,
        cbar=False,
        ax=axes[0],
        xticklabels=False,
        yticklabels=True,
    )
    axes[0].set_title("ANTES de imputacion - Datos disponibles (verde=con dato, rojo=nulo)",
                      fontweight="bold", fontsize=14)
    axes[0].set_xlabel("")
    axes[0].set_ylabel("Estacion")

    sns.heatmap(
        mat_after.T,
        cmap="RdYlGn",
        vmin=0,
        vmax=1,
        cbar=False,
        ax=axes[1],
        xticklabels=False,
        yticklabels=True,
    )
    axes[1].set_title("DESPUES de imputacion - Datos disponibles (verde=con dato, rojo=nulo)",
                      fontweight="bold", fontsize=14)
    axes[1].set_xlabel("Fecha")
    axes[1].set_ylabel("Estacion")

    plt.tight_layout()
    fig_path = output_dir / "figura_heatmap_nulos_antes_despues.png"
    plt.savefig(fig_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return fig_path


def main():
    print("=" * 70)
    print("VALIDACION POST-IMPUTACION v2.1")
    print("=" * 70)

    df_imputed = load_imputed()
    df_prepared = pd.read_csv(PREPARED_PATH)
    df_prepared["date"] = pd.to_datetime(df_prepared["date"], errors="coerce")
    df_models = pd.read_csv(MODELS_PATH)
    df_resumen = pd.read_csv(RESUMEN_PATH)
    official_ranges = load_official_ranges()

    ranges = compute_original_ranges(df_prepared)

    # Validacion 1: rangos de cota
    print("\n[1/6] Validando rangos historicos...")
    df_violations = validate_ranges(df_imputed, ranges)
    print(f"      Violaciones de rango: {len(df_violations)}")

    # Validacion 2: rangos temporales oficiales
    print("\n[2/6] Validando rangos temporales oficiales...")
    df_temp_violations = validate_temporal_ranges(df_imputed, official_ranges)
    print(f"      Registros fuera de rango oficial: {len(df_temp_violations)}")

    # Validacion 3: saltos temporales
    print("\n[3/6] Detectando saltos temporales anomalos...")
    df_jumps = detect_temporal_jumps(df_imputed)
    print(f"      Saltos anomalos: {len(df_jumps)}")

    # Validacion 4: coherencia espacial
    print("\n[4/6] Evaluando coherencia espacial...")
    df_spatial = spatial_coherence(df_imputed)
    n_low = len(df_spatial[df_spatial['Correlacion'] < 0.7]) if not df_spatial.empty else 0
    print(f"      Pares con correlacion < 0.7: {n_low}")

    # Validacion 5: comparacion con corrida estudiantes
    print("\n[5/6] Comparando con corrida anterior...")
    df_comp = compare_with_student_run(df_imputed)
    if df_comp is not None:
        print(f"      Registros comparables: {len(df_comp):,}")
        print(f"      Diferencia media absoluta: {df_comp['Diferencia_m'].abs().mean():.4f} m")
        print(f"      Diferencia maxima absoluta: {df_comp['Diferencia_m'].abs().max():.4f} m")
    else:
        print("      No se encontro corrida anterior")

    # Figuras
    print("\n[6/6] Generando figuras...")
    fig_cov = plot_coverage(df_imputed, OUTPUT_DIR)
    fig_series = plot_sample_series(df_imputed, OUTPUT_DIR)
    fig_heatmap = plot_null_heatmaps(df_prepared, df_imputed, official_ranges, OUTPUT_DIR)
    print(f"      {fig_cov.name}")
    print(f"      {fig_series.name}")
    print(f"      {fig_heatmap.name}")

    # Guardar validaciones
    df_violations.to_csv(OUTPUT_DIR / "validacion_violaciones_rango.csv", index=False)
    df_temp_violations.to_csv(OUTPUT_DIR / "validacion_violaciones_rango_temporal.csv", index=False)
    df_jumps.to_csv(OUTPUT_DIR / "validacion_saltos_temporales.csv", index=False)
    df_spatial.to_csv(OUTPUT_DIR / "validacion_coherencia_espacial.csv", index=False)
    if df_comp is not None:
        df_comp[["Fecha", "NombreEstacion", "Cota_v2_1", "Cota_student", "Diferencia_m"]].to_csv(
            OUTPUT_DIR / "comparacion_v2_1_vs_student.csv", index=False
        )

    # Generar reporte Markdown
    report = []
    report.append("# Reporte de Validacion - Imputacion v2.1+")
    report.append("")
    report.append("## Resumen ejecutivo")
    report.append("")
    n_total = len(df_imputed)
    n_orig = int((df_imputed["Nivel_Imputacion"] == 0).sum())
    n_l1 = int((df_imputed["Nivel_Imputacion"] == 1).sum())
    n_l2 = int((df_imputed["Nivel_Imputacion"] == 2).sum())
    n_l3 = int((df_imputed["Nivel_Imputacion"] == 3).sum())
    report.append(f"- **Registros totales:** {n_total:,}")
    report.append(f"- **Datos originales:** {n_orig:,} ({100*n_orig/n_total:.2f}%)")
    report.append(f"- **Imputados L1:** {n_l1:,} ({100*n_l1/n_total:.2f}%)")
    report.append(f"- **Imputados L2:** {n_l2:,} ({100*n_l2/n_total:.2f}%)")
    report.append(f"- **Imputados L3:** {n_l3:,} ({100*n_l3/n_total:.2f}%)")
    report.append("")
    report.append("## Modelos H-H seleccionados")
    report.append("")
    report.append("| Objetivo | Donante | R2 | n_train |")
    report.append("|----------|---------|-----|---------|")
    for _, row in df_models.iterrows():
        report.append(
            f"| {row['objetivo']} | {row['donante']} | {row['r2']:.4f} | {row['n_train']} |"
        )
    report.append("")
    report.append("## Cobertura por estacion")
    report.append("")
    report.append(
        "| Estacion | Inicio | Fin | Dias | Cobertura % | L1 | L2 | L3 | NaN restantes |"
    )
    report.append("|----------|--------|-----|------|-------------|----|----|----|---------------|")
    for _, row in df_resumen.iterrows():
        report.append(
            f"| {row['Estacion']} | {row['Fecha_Inicio']} | {row['Fecha_Fin']} | "
            f"{row['Dias_Rango']} | {row['Cobertura_Rango_pct']} | "
            f"{row['L1']} | {row['L2']} | {row.get('L3', 0)} | {row['NaN_Restantes_Rango']} |"
        )
    report.append("")
    report.append("## Validaciones")
    report.append("")
    report.append(f"- **Violaciones de rango de cota:** {len(df_violations)}")
    report.append(f"- **Registros fuera de rango temporal oficial:** {len(df_temp_violations)}")
    report.append(f"- **Saltos temporales anomalos:** {len(df_jumps)}")
    report.append(f"- **Pares con baja coherencia espacial (r < 0.7):** {len(df_spatial[df_spatial['Correlacion'] < 0.7])}")
    report.append(f"- **Correlacion espacial minima:** {df_spatial['Correlacion'].min():.4f}" if not df_spatial.empty else "- **Correlacion espacial:** N/A")
    if df_comp is not None:
        report.append("")
        report.append("## Comparacion con corrida anterior (estudiantes)")
        report.append("")
        report.append(f"- **Registros comparables:** {len(df_comp):,}")
        report.append(
            f"- **Diferencia media absoluta:** {df_comp['Diferencia_m'].abs().mean():.4f} m"
        )
        report.append(
            f"- **Diferencia maxima absoluta:** {df_comp['Diferencia_m'].abs().max():.4f} m"
        )
    report.append("")
    report.append("## Archivos generados")
    report.append("")
    report.append("- `Datos_Imputados.csv`")
    report.append("- `Datos_Imputados_sin_L3.csv`")
    report.append("- `Resumen_Imputacion.csv`")
    report.append("- `Tabla_Modelos_HH.csv`")
    report.append("- `Tabla_Modelos_HH_Seleccionados.csv`")
    report.append("- `Tabla_Modelos_L3.csv`")
    report.append("- `validacion_violaciones_rango.csv`")
    report.append("- `validacion_violaciones_rango_temporal.csv`")
    report.append("- `validacion_saltos_temporales.csv`")
    report.append("- `validacion_coherencia_espacial.csv`")
    report.append("- `figura_cobertura_imputacion.png`")
    report.append("- `figura_series_temporales.png`")
    report.append("- `figura_heatmap_nulos_antes_despues.png`")

    report_path = OUTPUT_DIR / "validacion_post_imputacion.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report))
    print(f"\nGuardado: {report_path}")

    print("\n" + "=" * 70)
    print("VALIDACION FINALIZADA")
    print("=" * 70)


if __name__ == "__main__":
    main()
