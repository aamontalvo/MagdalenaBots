#!/usr/bin/env python3
"""
09_experimento_l2b.py
=====================

Aplica un nivel L2b complementario (segunda donante H-H) a SAN_PABLO,
EL_CONTENTO y GAMARRA, usando como donante a PENONCITO segun la evaluacion
08_evaluar_candidatos_l2b.py.

Reglas:
- L2b NO reemplaza L0/L1/L2 existentes.
- Solo imputa fechas donde el objetivo sigue siendo NaN despues de L2.
- Usa como features/donante valores originales o ya imputados (L1/L2) del donante.
- Modelo entrenado solo con datos originales (L0) del objetivo.
- Salidas separadas del pipeline principal.
"""

import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
OUTPUT_DIR = PROJECT_ROOT / "backend" / "data" / "work" / "imputation_v2_1" / "output"

IMPUTED_PATH = OUTPUT_DIR / "Datos_Imputados.csv"
RANGES_PATH = OUTPUT_DIR / "resumen_rangos_estaciones.csv"

# Donantes seleccionados por evaluacion 08
L2B_MODELS = {
    "SAN_PABLO": "PENONCITO",
    "EL_CONTENTO": "PENONCITO",
    "GAMARRA": "PENONCITO",
}


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
    all_dates = pd.date_range(wide.index.min(), wide.index.max(), freq="D")
    wide = wide.reindex(all_dates)
    wide.index.name = "Fecha"
    return wide


def train_hh_model(x, y):
    r, _ = stats.pearsonr(x, y)
    coeffs = np.polyfit(x, y, 2)
    y_pred = coeffs[0] * x**2 + coeffs[1] * x + coeffs[2]
    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0
    return {
        "r": r,
        "r2": r2,
        "n_train": len(x),
        "a": coeffs[0],
        "b": coeffs[1],
        "c": coeffs[2],
    }


def apply_l2b(wide_l2, target, donor, official_ranges, original_ranges):
    start, end = official_ranges[target]
    mask_range = (wide_l2.index >= start) & (wide_l2.index <= end)

    y_orig = wide_l2.loc[mask_range, target]
    x_donor = wide_l2.loc[mask_range, donor]

    df_orig = pd.read_csv(IMPUTED_PATH)
    df_orig["Fecha"] = pd.to_datetime(df_orig["Fecha"], errors="coerce")
    df_orig_target = df_orig[
        (df_orig["NombreEstacion"] == target) & (df_orig["Nivel_Imputacion"] == 0)
    ].set_index("Fecha")["Cota"]
    y_train = df_orig_target.reindex(wide_l2.index[mask_range])

    mask_train = y_train.notna() & x_donor.notna()
    if mask_train.sum() < 50:
        raise ValueError(f"Pocos datos de entrenamiento para {target}")

    model = train_hh_model(x_donor[mask_train].values, y_train[mask_train].values)

    # Aplicar solo donde target es NaN despues de L2 y donor tiene dato
    mask_l2b = y_orig.isna() & x_donor.notna()
    n_imp = mask_l2b.sum()
    if n_imp > 0:
        x = x_donor[mask_l2b].values
        y_pred = model["a"] * x**2 + model["b"] * x + model["c"]
        wide_l2.loc[wide_l2.index[mask_range][mask_l2b], target] = y_pred

        # Hard rule: clip al rango historico original
        rmin, rmax = original_ranges.get(target, (y_pred.min(), y_pred.max()))
        col = wide_l2.loc[mask_range, target]
        below = col < rmin
        above = col > rmax
        wide_l2.loc[wide_l2.index[mask_range][below], target] = rmin
        wide_l2.loc[wide_l2.index[mask_range][above], target] = rmax

    return model, n_imp


def main():
    print("=" * 70)
    print("EXPERIMENTO L2b - Segunda donante H-H complementaria")
    print("=" * 70)

    df_long, official_ranges = load_data()

    # Wide con L0/L1/L2
    wide_l2 = to_wide(df_long, "Cota")

    # Rango historico original por estacion
    original_ranges = {}
    for station, grp in df_long[df_long["Nivel_Imputacion"] == 0].groupby("NombreEstacion"):
        valid = grp["Cota"].dropna()
        if len(valid) > 0:
            original_ranges[station] = (valid.min(), valid.max())

    # Copia para L2b
    wide_l2b = wide_l2.copy()

    # Tracking de L2b
    l2b_records = []

    results = []
    for target, donor in L2B_MODELS.items():
        print(f"\nAplicando L2b a {target} usando {donor}...")
        model, n_imp = apply_l2b(wide_l2b, target, donor, official_ranges, original_ranges)
        results.append(
            {
                "objetivo": target,
                "donante": donor,
                "r": round(model["r"], 4),
                "r2": round(model["r2"], 4),
                "n_train": int(model["n_train"]),
                "a": model["a"],
                "b": model["b"],
                "c": model["c"],
                "n_imputados_l2b": int(n_imp),
            }
        )
        print(f"  R2={model['r2']:.4f}  r={model['r']:.4f}  n_train={model['n_train']}  imputados={n_imp}")

        # Registrar fechas imputadas por L2b
        start, end = official_ranges[target]
        mask_range = (wide_l2.index >= start) & (wide_l2.index <= end)
        mask_l2b = wide_l2.loc[mask_range, target].isna() & wide_l2b.loc[mask_range, target].notna()
        for fecha in wide_l2.index[mask_range][mask_l2b]:
            l2b_records.append(
                {
                    "Fecha": fecha,
                    "NombreEstacion": target,
                    "Cota_L2b": wide_l2b.loc[fecha, target],
                    "Nivel_Imputacion_L2b": 3,
                    "Metodo_L2b": f"L2b_HH_{target}_vs_{donor}",
                }
            )

    # Guardar dataset L2b como long
    df_l2b_long = (
        wide_l2b.reset_index()
        .melt(id_vars="Fecha", var_name="NombreEstacion", value_name="Cota")
    )
    df_l2b_long = df_l2b_long.merge(
        df_long[["Fecha", "NombreEstacion", "Nivel_Imputacion", "Metodo"]],
        on=["Fecha", "NombreEstacion"],
        how="left",
    )

    # Agregar tracking L2b
    df_l2b_tracking = pd.DataFrame(l2b_records)
    df_l2b_long = df_l2b_long.merge(
        df_l2b_tracking,
        on=["Fecha", "NombreEstacion"],
        how="left",
    )

    out_csv = OUTPUT_DIR / "Datos_Imputados_L2b_experimento.csv"
    df_l2b_long.to_csv(out_csv, index=False)
    print(f"\nGuardado: {out_csv}")

    # Tabla de modelos L2b
    df_results = pd.DataFrame(results)
    out_models = OUTPUT_DIR / "Tabla_Modelos_L2b_experimento.csv"
    df_results.to_csv(out_models, index=False)
    print(f"Guardado: {out_models}")

    # Resumen de cobertura
    coverage_rows = []
    for target in L2B_MODELS.keys():
        start, end = official_ranges[target]
        mask_range = (wide_l2.index >= start) & (wide_l2.index <= end)
        n_total = mask_range.sum()
        n_nan_l2 = wide_l2.loc[mask_range, target].isna().sum()
        n_nan_l2b = wide_l2b.loc[mask_range, target].isna().sum()
        coverage_rows.append(
            {
                "Estacion": target,
                "Dias_Rango": int(n_total),
                "NaN_L2": int(n_nan_l2),
                "Cobertura_L2_pct": round(100 * (n_total - n_nan_l2) / n_total, 2),
                "NaN_L2b": int(n_nan_l2b),
                "Cobertura_L2b_pct": round(100 * (n_total - n_nan_l2b) / n_total, 2),
            }
        )
    df_coverage = pd.DataFrame(coverage_rows)
    out_cov = OUTPUT_DIR / "Resumen_Cobertura_L2b_experimento.csv"
    df_coverage.to_csv(out_cov, index=False)
    print(f"Guardado: {out_cov}")
    print("\nResumen de cobertura:")
    print(df_coverage.to_string(index=False))

    # Reporte Markdown
    report = []
    report.append("# Experimento L2b - Segunda donante H-H complementaria")
    report.append("")
    report.append("## Modelos aplicados")
    report.append("")
    report.append("| Objetivo | Donante | R2 | r | n_train | Imputados L2b |")
    report.append("|----------|---------|----|---|---------|---------------|")
    for _, row in df_results.iterrows():
        report.append(
            f"| {row['objetivo']} | {row['donante']} | {row['r2']:.4f} | {row['r']:.4f} | "
            f"{int(row['n_train'])} | {int(row['n_imputados_l2b'])} |"
        )
    report.append("")
    report.append("## Cobertura antes y despues de L2b")
    report.append("")
    report.append("| Estacion | Dias | NaN L2 | Cobertura L2 | NaN L2b | Cobertura L2b |")
    report.append("|----------|------|--------|--------------|---------|---------------|")
    for _, row in df_coverage.iterrows():
        report.append(
            f"| {row['Estacion']} | {row['Dias_Rango']} | {row['NaN_L2']} | "
            f"{row['Cobertura_L2_pct']}% | {row['NaN_L2b']} | {row['Cobertura_L2b_pct']}% |"
        )
    report.append("")
    report.append("## Archivos generados")
    report.append("")
    report.append("- `Datos_Imputados_L2b_experimento.csv`")
    report.append("- `Tabla_Modelos_L2b_experimento.csv`")
    report.append("- `Resumen_Cobertura_L2b_experimento.csv`")

    out_md = OUTPUT_DIR / "experimento_l2b.md"
    with open(out_md, "w", encoding="utf-8") as f:
        f.write("\n".join(report))
    print(f"\nGuardado: {out_md}")

    print("\n" + "=" * 70)
    print("EXPERIMENTO L2b FINALIZADO")
    print("=" * 70)


if __name__ == "__main__":
    main()
