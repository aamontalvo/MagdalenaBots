#!/usr/bin/env python3
"""
01_compare_raw_versions.py
==========================

Compara el raw nuevo (HAR/STEFY corregido) contra el raw anterior
(Resumen_Crudos_IDEAM_2026.csv) para las estaciones comunes.

Metricas calculadas:
- Numero de registros y cobertura por estacion
- Medias mensuales multianuales y sus diferencias
- Estadisticas descriptivas (min, max, p5, p95, media)
- Estaciones presentes solo en uno de los dos datasets

Salidas:
- comparacion_raw_nuevo_vs_anterior.csv
- diferencias_medias_mensuales.csv
- figura_diferencias_medias_mensuales.png
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import re

PROJECT_ROOT = Path(__file__).resolve().parents[3]
WORK_DIR = PROJECT_ROOT / "backend" / "data" / "work" / "imputation_v2_1"
OUTPUT_DIR = WORK_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

NEW_RAW_PATH = (
    PROJECT_ROOT
    / "backend"
    / "data"
    / "raw"
    / "SERIE NIVELES IDEAM A 2026"
    / "Version Homegeneizada HAR STEFY"
    / "estaciones_formato_long.csv"
)
OLD_RAW_PATH = PROJECT_ROOT / "backend" / "data" / "processed" / "Resumen_Crudos_IDEAM_2026.csv"


def normalize_station_name(station_series):
    """Extrae el nombre base de estacion quitando el codigo IDEAM de 8 digitos al final."""

    def _clean(name):
        name = str(name).strip().upper()
        m = re.search(r"^(.*?)(\d{8})$", name)
        if m:
            base = m.group(1).rstrip("_- ")
            return base
        return name

    return station_series.apply(_clean)


STATION_NAME_MAP = {
    "EL_BANCO_-_AUT": "EL_BANCO",
    "PLATO_MAGDALENA_AUT": "PLATO",
    "SAN_PEDRITO_-_AUT": "SAN_PEDRITO",
    "GAMARRA_-_AUT": "GAMARRA_AUT",
    "BARRANCABERMEJA_-_AUT": "BARRANCABERMEJA",
    "PUERTO_BERRIO_-_AUT": "PUERTO_BERRIO",
    "SAN_PABLO_RIO_MAGDALENA_-_AUT": "SAN_PABLO",
    "TEBSA_BQUILLA_AUT": "TEBSA",
}


def standardize_station_name(station_series):
    base = normalize_station_name(station_series)
    return base.map(STATION_NAME_MAP).fillna(base)


def load_new_raw():
    df = pd.read_csv(NEW_RAW_PATH)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["level"] = pd.to_numeric(df["level"], errors="coerce")
    df["NombreBase"] = standardize_station_name(df["station"])
    df = df.rename(columns={"date": "Fecha", "level": "Cota"})
    return df[["Fecha", "station", "NombreBase", "Cota"]]


def load_old_raw():
    df = pd.read_csv(OLD_RAW_PATH)
    df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y", errors="coerce")
    df["level"] = pd.to_numeric(df["level"], errors="coerce")
    df["NombreBase"] = df["station"].str.upper().str.strip()
    df = df.rename(columns={"date": "Fecha", "level": "Cota"})
    return df[["Fecha", "station", "NombreBase", "Cota"]]


def compute_coverage(df):
    return (
        df.groupby("NombreBase")
        .agg(Total=("Cota", "size"), Validos=("Cota", lambda x: x.notna().sum()))
        .reset_index()
    )


def monthly_means(df):
    df = df.copy()
    df["Mes"] = df["Fecha"].dt.month
    return (
        df.groupby(["NombreBase", "Mes"])["Cota"]
        .mean()
        .reset_index()
        .rename(columns={"Cota": "MediaMensual"})
    )


def main():
    print("=" * 70)
    print("COMPARACION RAW NUEVO vs RAW ANTERIOR")
    print("=" * 70)

    df_new = load_new_raw()
    df_old = load_old_raw()

    print(f"\nRaw nuevo : {len(df_new):,} registros, {df_new['NombreBase'].nunique()} estaciones")
    print(f"Raw anterior: {len(df_old):,} registros, {df_old['NombreBase'].nunique()} estaciones")

    stations_new = set(df_new["NombreBase"].unique())
    stations_old = set(df_old["NombreBase"].unique())
    common = sorted(stations_new & stations_old)
    only_new = sorted(stations_new - stations_old)
    only_old = sorted(stations_old - stations_new)

    print(f"\nEstaciones comunes   : {len(common)}")
    print(f"Solo en raw nuevo    : {only_new}")
    print(f"Solo en raw anterior : {only_old}")

    # Cobertura
    cov_new = compute_coverage(df_new)
    cov_old = compute_coverage(df_old)
    cov_new["Dataset"] = "Nuevo"
    cov_old["Dataset"] = "Anterior"
    cov_new["Cobertura_pct"] = 100 * cov_new["Validos"] / cov_new["Total"]
    cov_old["Cobertura_pct"] = 100 * cov_old["Validos"] / cov_old["Total"]

    cov_comp = pd.merge(
        cov_new, cov_old, on="NombreBase", suffixes=("_Nuevo", "_Anterior"), how="outer"
    )
    cov_comp["Diferencia_Cobertura_pct"] = (
        cov_comp["Cobertura_pct_Nuevo"] - cov_comp["Cobertura_pct_Anterior"]
    )
    cov_comp = cov_comp.sort_values("NombreBase")
    cov_comp.to_csv(OUTPUT_DIR / "comparacion_cobertura_raw.csv", index=False)
    print(f"\nGuardado: {OUTPUT_DIR / 'comparacion_cobertura_raw.csv'}")
    print(cov_comp[["NombreBase", "Cobertura_pct_Nuevo", "Cobertura_pct_Anterior", "Diferencia_Cobertura_pct"]].to_string(index=False))

    # Medias mensuales multianuales para estaciones comunes
    mm_new = monthly_means(df_new[df_new["NombreBase"].isin(common)])
    mm_old = monthly_means(df_old[df_old["NombreBase"].isin(common)])
    mm_comp = pd.merge(
        mm_new, mm_old, on=["NombreBase", "Mes"], suffixes=("_Nuevo", "_Anterior")
    )
    mm_comp["Diferencia_m"] = mm_comp["MediaMensual_Nuevo"] - mm_comp["MediaMensual_Anterior"]
    mm_comp["Diferencia_pct"] = 100 * mm_comp["Diferencia_m"] / mm_comp["MediaMensual_Anterior"]
    mm_comp.to_csv(OUTPUT_DIR / "diferencias_medias_mensuales.csv", index=False)
    print(f"\nGuardado: {OUTPUT_DIR / 'diferencias_medias_mensuales.csv'}")

    # Estadisticas descriptivas
    desc_new = (
        df_new[df_new["NombreBase"].isin(common)]
        .groupby("NombreBase")["Cota"]
        .agg(["count", "mean", "std", "min", "max"])
        .reset_index()
    )
    desc_new["p5"] = df_new[df_new["NombreBase"].isin(common)].groupby("NombreBase")["Cota"].quantile(0.05).values
    desc_new["p95"] = df_new[df_new["NombreBase"].isin(common)].groupby("NombreBase")["Cota"].quantile(0.95).values

    desc_old = (
        df_old[df_old["NombreBase"].isin(common)]
        .groupby("NombreBase")["Cota"]
        .agg(["count", "mean", "std", "min", "max"])
        .reset_index()
    )
    desc_old["p5"] = df_old[df_old["NombreBase"].isin(common)].groupby("NombreBase")["Cota"].quantile(0.05).values
    desc_old["p95"] = df_old[df_old["NombreBase"].isin(common)].groupby("NombreBase")["Cota"].quantile(0.95).values

    desc_comp = pd.merge(
        desc_new, desc_old, on="NombreBase", suffixes=("_Nuevo", "_Anterior"), how="outer"
    )
    desc_comp.to_csv(OUTPUT_DIR / "comparacion_estadisticas_descriptivas.csv", index=False)
    print(f"Guardado: {OUTPUT_DIR / 'comparacion_estadisticas_descriptivas.csv'}")

    # Figura de diferencias medias mensuales
    pivot_diff = mm_comp.pivot(index="NombreBase", columns="Mes", values="Diferencia_m")
    fig, ax = plt.subplots(figsize=(14, 10))
    sns.heatmap(
        pivot_diff,
        cmap="RdBu_r",
        center=0,
        annot=True,
        fmt=".2f",
        linewidths=0.5,
        ax=ax,
        cbar_kws={"label": "Diferencia media mensual (m)"},
    )
    ax.set_title("Diferencia medias mensuales multianuales\n(Nuevo - Anterior)", fontweight="bold")
    ax.set_xlabel("Mes")
    ax.set_ylabel("Estacion")
    plt.tight_layout()
    fig_path = OUTPUT_DIR / "figura_diferencias_medias_mensuales.png"
    plt.savefig(fig_path, dpi=300, bbox_inches="tight")
    print(f"Guardado: {fig_path}")

    print("\n" + "=" * 70)
    print("COMPARACION FINALIZADA")
    print("=" * 70)


if __name__ == "__main__":
    main()
