#!/usr/bin/env python3
"""
08_evaluar_candidatos_l2b.py
============================

Evalua candidatos para una segunda donante H-H (nivel L2b) para las estaciones
criticas SAN_PABLO, EL_CONTENTO y GAMARRA.

Criterios de seleccion:
- R2 del ajuste cuadratico >= 0.65
- Correlacion de Pearson >= 0.8
- Modelo entrenado SOLO con datos originales (Nivel_Imputacion == 0)
- Seleccion por maxima cobertura de NaN restantes del objetivo

Salidas:
- evaluacion_candidatos_l2b.csv
- evaluacion_candidatos_l2b.md
"""

import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
OUTPUT_DIR = PROJECT_ROOT / "backend" / "data" / "work" / "imputation_v2_1" / "output"

IMPUTED_PATH = OUTPUT_DIR / "Datos_Imputados.csv"
RANGES_PATH = OUTPUT_DIR / "resumen_rangos_estaciones.csv"

TARGET_STATIONS = ["SAN_PABLO", "EL_CONTENTO", "GAMARRA"]
R2_MIN = 0.65
PEARSON_MIN = 0.8
MIN_N_TRAIN = 50


def load_data():
    df = pd.read_csv(IMPUTED_PATH)
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")

    ranges = pd.read_csv(RANGES_PATH)
    ranges["Fecha_Inicio"] = pd.to_datetime(ranges["Fecha_Inicio"], errors="coerce")
    ranges["Fecha_Fin"] = pd.to_datetime(ranges["Fecha_Fin"], errors="coerce")
    official_ranges = {
        row["Estacion"]: (row["Fecha_Inicio"], row["Fecha_Fin"])
        for _, row in ranges.iterrows()
    }

    return df, official_ranges


def to_wide(df, value_col="Cota"):
    wide = df.pivot(index="Fecha", columns="NombreEstacion", values=value_col)
    # Asegurar que tenga todas las fechas posibles (union completa)
    all_dates = pd.date_range(wide.index.min(), wide.index.max(), freq="D")
    wide = wide.reindex(all_dates)
    wide.index.name = "Fecha"
    return wide


def train_hh_model(x, y):
    """Entrena modelo H-H cuadratico y retorna metricas."""
    if len(x) < MIN_N_TRAIN:
        return None

    r, _ = stats.pearsonr(x, y)
    if abs(r) < PEARSON_MIN:
        return None

    coeffs = np.polyfit(x, y, 2)
    y_pred = coeffs[0] * x**2 + coeffs[1] * x + coeffs[2]
    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0

    if r2 < R2_MIN:
        return None

    return {
        "r": r,
        "r2": r2,
        "n_train": len(x),
        "a": coeffs[0],
        "b": coeffs[1],
        "c": coeffs[2],
    }


def evaluate_candidate(df_wide_orig, df_wide_l2, target, donor, official_ranges):
    """
    Evalua un candidato donante para una estacion objetivo.
    Entrena con datos originales del objetivo vs originales/L2 del donante.
    Calcula cuantos NaN restantes del objetivo podria cubrir el donante.
    """
    if target not in df_wide_orig.columns or donor not in df_wide_orig.columns:
        return None

    start, end = official_ranges.get(target, (df_wide_orig.index.min(), df_wide_orig.index.max()))
    mask_range = (df_wide_orig.index >= start) & (df_wide_orig.index <= end)

    # Target: solo originales (L0). Donante: originales o imputados (L1/L2 permitidos)
    y = df_wide_orig.loc[mask_range, target]
    x_donor_full = df_wide_l2.loc[mask_range, donor]

    # Entrenamiento: ambos originales
    mask_train = y.notna() & x_donor_full.notna()
    if mask_train.sum() < MIN_N_TRAIN:
        return None

    model = train_hh_model(x_donor_full[mask_train].values, y[mask_train].values)
    if model is None:
        return None

    # NaN restantes del objetivo despues de L2
    y_after_l2 = df_wide_l2.loc[mask_range, target]
    mask_nan_after_l2 = y_after_l2.isna()

    # De esos NaN, cuantos podria cubrir el donante (donante tiene dato, sea orig o imputado)
    mask_coverable = mask_nan_after_l2 & x_donor_full.notna()
    n_coverable = mask_coverable.sum()

    # Cobertura actual y esperada
    n_total_range = mask_range.sum()
    n_nan_after_l2 = mask_nan_after_l2.sum()
    n_nan_after_l2b = n_nan_after_l2 - n_coverable
    coverage_after_l2 = 100 * (n_total_range - n_nan_after_l2) / n_total_range
    coverage_after_l2b = 100 * (n_total_range - n_nan_after_l2b) / n_total_range

    return {
        "objetivo": target,
        "donante": donor,
        "r": round(model["r"], 4),
        "r2": round(model["r2"], 4),
        "n_train": int(model["n_train"]),
        "a": model["a"],
        "b": model["b"],
        "c": model["c"],
        "n_nan_restantes_l2": int(n_nan_after_l2),
        "n_nan_cubribles_l2b": int(n_coverable),
        "n_nan_despues_l2b": int(n_nan_after_l2b),
        "cobertura_l2_pct": round(coverage_after_l2, 2),
        "cobertura_l2b_pct": round(coverage_after_l2b, 2),
        "ganancia_cobertura_pct": round(coverage_after_l2b - coverage_after_l2, 2),
    }


def main():
    print("=" * 70)
    print("EVALUACION DE CANDIDATOS L2b")
    print("=" * 70)

    df, official_ranges = load_data()

    # Separar originales (L0) del resto
    df_orig = df[df["Nivel_Imputacion"] == 0].copy()
    df_wide_orig = to_wide(df_orig, "Cota")
    df_wide_l2 = to_wide(df, "Cota")

    all_stations = [c for c in df_wide_l2.columns if c not in TARGET_STATIONS]
    results = []

    for target in TARGET_STATIONS:
        print(f"\nEvaluando candidatos para {target}...")
        for donor in all_stations:
            res = evaluate_candidate(df_wide_orig, df_wide_l2, target, donor, official_ranges)
            if res is not None:
                results.append(res)
                print(
                    f"  {donor:<18}  R2={res['r2']:.4f}  r={res['r']:.4f}  "
                    f"n_train={res['n_train']:>5}  cubre={res['n_nan_cubribles_l2b']:>4} "
                    f"cob={res['cobertura_l2b_pct']:.2f}%"
                )

    df_results = pd.DataFrame(results)
    if not df_results.empty:
        df_results = df_results.sort_values(["objetivo", "cobertura_l2b_pct", "r2"], ascending=[True, False, False])
        out_csv = OUTPUT_DIR / "evaluacion_candidatos_l2b.csv"
        df_results.to_csv(out_csv, index=False)
        print(f"\nGuardado: {out_csv}")

        # Seleccionar mejor por objetivo
        best = df_results.loc[df_results.groupby("objetivo")["cobertura_l2b_pct"].idxmax()]
        print("\nMejores candidatos por objetivo (max cobertura L2b):")
        print(best[["objetivo", "donante", "r2", "r", "n_train", "n_nan_cubribles_l2b", "cobertura_l2_pct", "cobertura_l2b_pct"]].to_string(index=False))

        report = []
        report.append("# Evaluacion de candidatos para segunda donante H-H (L2b)")
        report.append("")
        report.append(f"- **Criterios:** R2 >= {R2_MIN}, Pearson r >= {PEARSON_MIN}, entrenamiento con datos originales.")
        report.append("")
        report.append("## Mejores candidatos por estacion objetivo")
        report.append("")
        report.append("| Objetivo | Donante | R2 | r | n_train | NaN cubribles | Cobertura L2 | Cobertura L2b |")
        report.append("|----------|---------|----|---|---------|---------------|--------------|---------------|")
        for _, row in best.iterrows():
            report.append(
                f"| {row['objetivo']} | {row['donante']} | {row['r2']:.4f} | {row['r']:.4f} | "
                f"{int(row['n_train'])} | {int(row['n_nan_cubribles_l2b'])} | "
                f"{row['cobertura_l2_pct']:.2f}% | {row['cobertura_l2b_pct']:.2f}% |"
            )
        report.append("")
        report.append("## Todos los candidatos evaluados")
        report.append("")
        report.append("| Objetivo | Donante | R2 | r | n_train | NaN cubribles | Cobertura L2b |")
        report.append("|----------|---------|----|---|---------|---------------|---------------|")
        for _, row in df_results.iterrows():
            report.append(
                f"| {row['objetivo']} | {row['donante']} | {row['r2']:.4f} | {row['r']:.4f} | "
                f"{int(row['n_train'])} | {int(row['n_nan_cubribles_l2b'])} | {row['cobertura_l2b_pct']:.2f}% |"
            )

        out_md = OUTPUT_DIR / "evaluacion_candidatos_l2b.md"
        with open(out_md, "w", encoding="utf-8") as f:
            f.write("\n".join(report))
        print(f"Guardado: {out_md}")
    else:
        print("\nNo se encontraron candidatos que cumplan los criterios.")

    print("\n" + "=" * 70)
    print("EVALUACION FINALIZADA")
    print("=" * 70)


if __name__ == "__main__":
    main()
