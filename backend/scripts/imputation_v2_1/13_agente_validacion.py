#!/usr/bin/env python3
"""
13_agente_validacion.py
=======================

Agente de validacion automatica para el pipeline de imputacion v2.1+.

Este script actua como un auditor independiente que verifica los resultados
del pipeline y detecta problemas como:
- Registros fuera del rango oficial de cada estacion.
- Valores fuera del rango historico observado.
- Saltos temporales anomalos.
- Inconsistencias en los niveles de imputacion.
- Estaciones con cobertura baja.
- Duplicados o faltantes en el grid de fechas.

Salidas:
- agente_validacion_reporte.md
- agente_validacion_alertas.csv
"""

import pandas as pd
import numpy as np
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
OUTPUT_DIR = PROJECT_ROOT / "backend" / "data" / "work" / "imputation_v2_1" / "output"

IMPUTED_PATH = OUTPUT_DIR / "Datos_Imputados.csv"
RANGES_PATH = OUTPUT_DIR / "resumen_rangos_estaciones.csv"
COBERTURA_MIN_ALERTA = 95.0
SALTO_QT_UMBRAL = 0.995


def load_data():
    df = pd.read_csv(IMPUTED_PATH, low_memory=False)
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")

    ranges = pd.read_csv(RANGES_PATH)
    ranges["Fecha_Inicio"] = pd.to_datetime(ranges["Fecha_Inicio"], errors="coerce")
    ranges["Fecha_Fin"] = pd.to_datetime(ranges["Fecha_Fin"], errors="coerce")
    official_ranges = {
        row["Estacion"]: (row["Fecha_Inicio"], row["Fecha_Fin"])
        for _, row in ranges.iterrows()
    }

    return df, official_ranges


def check_temporal_bounds(df, official_ranges):
    """Verifica que no haya registros con valor fuera del rango oficial."""
    alerts = []
    df_with_val = df[df["Cota"].notna()].copy()
    for estacion, grp in df_with_val.groupby("NombreEstacion"):
        if estacion not in official_ranges:
            continue
        start, end = official_ranges[estacion]
        mask = (grp["Fecha"] < start) | (grp["Fecha"] > end)
        if mask.any():
            alerts.append(
                {
                    "tipo": "fuera_de_rango_temporal",
                    "estacion": estacion,
                    "n_casos": int(mask.sum()),
                    "detalle": f"{mask.sum()} registros fuera de [{start.date()}, {end.date()}]",
                }
            )
    return alerts


def check_historical_ranges(df):
    """Verifica que no haya valores fuera del rango historico original por estacion."""
    alerts = []
    orig = df[df["Nivel_Imputacion"] == 0].groupby("NombreEstacion")["Cota"].agg(["min", "max"])
    for estacion, grp in df.groupby("NombreEstacion"):
        if estacion not in orig.index:
            continue
        rmin, rmax = orig.loc[estacion, "min"], orig.loc[estacion, "max"]
        mask = (grp["Cota"] < rmin) | (grp["Cota"] > rmax)
        n = int(mask.sum())
        if n > 0:
            alerts.append(
                {
                    "tipo": "fuera_de_rango_cota",
                    "estacion": estacion,
                    "n_casos": n,
                    "detalle": f"{n} valores fuera de [{rmin:.3f}, {rmax:.3f}]",
                }
            )
    return alerts


def check_temporal_jumps(df):
    """Detecta saltos diarios anomalos por estacion."""
    alerts = []
    for estacion, grp in df.groupby("NombreEstacion"):
        grp = grp.sort_values("Fecha").reset_index(drop=True)
        diffs = grp["Cota"].diff().abs()
        threshold = grp["Cota"].quantile(SALTO_QT_UMBRAL) * 2
        if pd.isna(threshold) or threshold == 0:
            threshold = diffs.quantile(0.99)
        mask = diffs > threshold
        n = int(mask.sum())
        if n > 0:
            alerts.append(
                {
                    "tipo": "salto_temporal_anomalo",
                    "estacion": estacion,
                    "n_casos": n,
                    "detalle": f"{n} saltos > {threshold:.3f} m",
                }
            )
    return alerts


def check_coverage(df, official_ranges):
    """Identifica estaciones con cobertura menor al umbral."""
    alerts = []
    for estacion, grp in df.groupby("NombreEstacion"):
        if estacion not in official_ranges:
            continue
        start, end = official_ranges[estacion]
        n_total = (end - start).days + 1
        n_valid = grp["Cota"].notna().sum()
        cob = 100 * n_valid / n_total
        if cob < COBERTURA_MIN_ALERTA:
            alerts.append(
                {
                    "tipo": "cobertura_baja",
                    "estacion": estacion,
                    "n_casos": int(n_total - n_valid),
                    "detalle": f"Cobertura {cob:.2f}% ({n_valid}/{n_total})",
                }
            )
    return alerts


def check_imputation_levels(df):
    """Verifica consistencia de niveles de imputacion."""
    alerts = []
    valid_levels = {0, 1, 2, 3}
    for estacion, grp in df.groupby("NombreEstacion"):
        n_invalid = (~grp["Nivel_Imputacion"].isin(valid_levels) & grp["Nivel_Imputacion"].notna()).sum()
        if n_invalid > 0:
            alerts.append(
                {
                    "tipo": "nivel_imputacion_invalido",
                    "estacion": estacion,
                    "n_casos": int(n_invalid),
                    "detalle": f"{n_invalid} registros con Nivel_Imputacion no valido",
                }
            )
    return alerts


def check_nan_with_level(df):
    """Verifica que los NaN no tengan nivel de imputacion > 0."""
    alerts = []
    mask = df["Cota"].isna() & (df["Nivel_Imputacion"] > 0)
    if mask.any():
        for estacion, grp in df[mask].groupby("NombreEstacion"):
            alerts.append(
                {
                    "tipo": "nan_con_nivel_imputacion",
                    "estacion": estacion,
                    "n_casos": int(len(grp)),
                    "detalle": f"{len(grp)} NaN con Nivel_Imputacion > 0",
                }
            )
    return alerts


def check_duplicate_dates(df):
    """Verifica que no haya fechas duplicadas por estacion."""
    alerts = []
    for estacion, grp in df.groupby("NombreEstacion"):
        n_dup = int(grp["Fecha"].duplicated().sum())
        if n_dup > 0:
            alerts.append(
                {
                    "tipo": "fechas_duplicadas",
                    "estacion": estacion,
                    "n_casos": n_dup,
                    "detalle": f"{n_dup} fechas duplicadas",
                }
            )
    return alerts


def check_l3_only_on_nan(df):
    """Verifica que L3 solo se haya aplicado donde originalmente habia NaN."""
    alerts = []
    # Se requiere Nivel_Imputacion_Original para verificarlo directamente;
    # sin esa columna se deja como placeholder.
    return alerts


def main():
    print("=" * 70)
    print("AGENTE DE VALIDACION - PIPELINE v2.1+")
    print("=" * 70)

    df, official_ranges = load_data()

    checks = [
        ("Rangos temporales", check_temporal_bounds),
        ("Rangos de cota", check_historical_ranges),
        ("Saltos temporales", check_temporal_jumps),
        ("Cobertura baja", check_coverage),
        ("Niveles de imputacion", check_imputation_levels),
        ("NaN con nivel", check_nan_with_level),
        ("Fechas duplicadas", check_duplicate_dates),
    ]

    all_alerts = []
    for name, func in checks:
        print(f"\n[CHECK] {name}...")
        if name in ["Rangos temporales", "Cobertura baja"]:
            alerts = func(df, official_ranges)
        else:
            alerts = func(df)
        print(f"        Alertas: {len(alerts)}")
        all_alerts.extend(alerts)

    df_alerts = pd.DataFrame(all_alerts)
    if not df_alerts.empty:
        out_csv = OUTPUT_DIR / "agente_validacion_alertas.csv"
        df_alerts.to_csv(out_csv, index=False)
        print(f"\nGuardado: {out_csv}")

    report = []
    report.append("# Reporte del Agente de Validacion v2.1+")
    report.append("")
    report.append(f"- **Total de alertas:** {len(all_alerts)}")
    report.append("")

    if all_alerts:
        report.append("## Alertas detectadas")
        report.append("")
        report.append("| Tipo | Estacion | N casos | Detalle |")
        report.append("|------|----------|---------|---------|")
        for a in all_alerts:
            report.append(
                f"| {a['tipo']} | {a['estacion']} | {a['n_casos']} | {a['detalle']} |"
            )
    else:
        report.append("## Sin alertas")
        report.append("")
        report.append("No se detectaron problemas en las validaciones automaticas.")

    report.append("")
    report.append("## Resumen por estacion")
    report.append("")
    report.append("| Estacion | Cobertura % | L0 | L1 | L2 | L3 | NaN |")
    report.append("|----------|-------------|----|----|----|----|-----|")
    for estacion, grp in df.groupby("NombreEstacion"):
        if estacion not in official_ranges:
            continue
        start, end = official_ranges[estacion]
        n_total = (end - start).days + 1
        n_nan = int(grp["Cota"].isna().sum())
        cob = 100 * (len(grp) - n_nan) / n_total
        counts = grp["Nivel_Imputacion"].value_counts().to_dict()
        report.append(
            f"| {estacion} | {cob:.2f}% | {counts.get(0, 0)} | {counts.get(1, 0)} | "
            f"{counts.get(2, 0)} | {counts.get(3, 0)} | {n_nan} |"
        )

    out_md = OUTPUT_DIR / "agente_validacion_reporte.md"
    with open(out_md, "w", encoding="utf-8") as f:
        f.write("\n".join(report))
    print(f"Guardado: {out_md}")

    print("\n" + "=" * 70)
    print("VALIDACION FINALIZADA")
    print("=" * 70)


if __name__ == "__main__":
    main()
