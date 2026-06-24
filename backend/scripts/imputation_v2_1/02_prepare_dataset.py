#!/usr/bin/env python3
"""
02_prepare_dataset.py
=====================

Prepara el dataset de trabajo a partir del raw nuevo corregido,
aplicando las reglas acordadas:

- Incluye las 24 estaciones del raw nuevo.
- Corte global al 31-12-2025.
- Elimina el 29 de febrero en todas las estaciones.
- Mantiene el mismo rango de fechas que el raw anterior para las
  estaciones comunes; para las estaciones nuevas se usa su rango valido.
- Formato de salida: station, level, date (compatible con el pipeline).

Salidas:
- Resumen_Crudos_IDEAM_2026_v2_1.csv
- resumen_rangos_estaciones.csv
"""

import pandas as pd
import numpy as np
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

CORTE_GLOBAL = pd.Timestamp("2025-12-31")


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


def get_old_ranges(df_old):
    """Obtiene rango valido (primera/ultima fecha con dato) por estacion del raw anterior."""
    ranges = {}
    for name, grp in df_old.groupby("NombreBase"):
        valid = grp[grp["Cota"].notna()]
        if not valid.empty:
            ranges[name] = (valid["Fecha"].min(), min(valid["Fecha"].max(), CORTE_GLOBAL))
    return ranges


def main():
    print("=" * 70)
    print("PREPARACION DEL DATASET v2.1")
    print("=" * 70)

    # Cargar raw nuevo
    df_new = pd.read_csv(NEW_RAW_PATH)
    df_new["date"] = pd.to_datetime(df_new["date"], errors="coerce").dt.normalize()
    df_new["level"] = pd.to_numeric(df_new["level"], errors="coerce")
    df_new["NombreBase"] = standardize_station_name(df_new["station"])
    df_new = df_new.drop(columns=["station"])
    df_new = df_new.rename(columns={"date": "Fecha", "level": "Cota"})
    print(f"\nRaw nuevo cargado: {len(df_new):,} registros, {df_new['NombreBase'].nunique()} estaciones")

    # Cargar raw anterior para rangos
    df_old = pd.read_csv(OLD_RAW_PATH)
    df_old["date"] = pd.to_datetime(df_old["date"], format="%d-%m-%Y", errors="coerce").dt.normalize()
    df_old["level"] = pd.to_numeric(df_old["level"], errors="coerce")
    df_old["NombreBase"] = df_old["station"].str.upper().str.strip()
    df_old = df_old.rename(columns={"date": "Fecha", "level": "Cota"})
    old_ranges = get_old_ranges(df_old)
    print(f"Rangos del raw anterior cargados para {len(old_ranges)} estaciones")

    # Aplicar corte global y eliminar 29-feb
    df_new = df_new[df_new["Fecha"] <= CORTE_GLOBAL]
    df_new = df_new[~((df_new["Fecha"].dt.month == 2) & (df_new["Fecha"].dt.day == 29))]

    # Filtrar por rangos
    records = []
    resumen_rangos = []
    for name, grp in df_new.groupby("NombreBase"):
        valid = grp[grp["Cota"].notna()]
        if name in old_ranges:
            start, end = old_ranges[name]
            rationale = "rango anterior"
        else:
            if valid.empty:
                print(f"  [AVISO] {name}: sin datos validos, se omite")
                continue
            start = valid["Fecha"].min()
            end = min(valid["Fecha"].max(), CORTE_GLOBAL)
            rationale = "rango propio (nueva)"

        grp_filtered = grp[(grp["Fecha"] >= start) & (grp["Fecha"] <= end)].copy()
        records.append(grp_filtered)

        resumen_rangos.append(
            {
                "Estacion": name,
                "Fecha_Inicio": start.strftime("%Y-%m-%d"),
                "Fecha_Fin": end.strftime("%Y-%m-%d"),
                "Dias": len(grp_filtered),
                "Validos": grp_filtered["Cota"].notna().sum(),
                "Faltantes": grp_filtered["Cota"].isna().sum(),
                "Cobertura_pct": round(100 * grp_filtered["Cota"].notna().sum() / len(grp_filtered), 2),
                "Rango_Usado": rationale,
            }
        )

    df_prepared = pd.concat(records, ignore_index=True)
    df_prepared = df_prepared.sort_values(["NombreBase", "Fecha"]).reset_index(drop=True)

    # Eliminar duplicados de fecha por estacion (conservar valor no nulo si existe)
    n_before = len(df_prepared)
    df_prepared = (
        df_prepared.sort_values("Cota", na_position="last")
        .groupby(["NombreBase", "Fecha"], as_index=False)
        .first()
    )
    n_after = len(df_prepared)
    if n_before != n_after:
        print(f"  [AVISO] Se eliminaron {n_before - n_after} registros duplicados (misma estacion y fecha)")

    # Formato final compatible con pipeline
    df_out = df_prepared.rename(
        columns={"NombreBase": "station", "Cota": "level", "Fecha": "date"}
    )[["station", "level", "date"]]
    df_out["date"] = df_out["date"].dt.strftime("%Y-%m-%d")

    out_csv = OUTPUT_DIR / "Resumen_Crudos_IDEAM_2026_v2_1.csv"
    df_out.to_csv(out_csv, index=False)
    print(f"\nGuardado: {out_csv} ({len(df_out):,} registros)")

    df_resumen = pd.DataFrame(resumen_rangos).sort_values("Estacion")
    df_resumen.to_csv(OUTPUT_DIR / "resumen_rangos_estaciones.csv", index=False)
    print(f"Guardado: {OUTPUT_DIR / 'resumen_rangos_estaciones.csv'}")
    print("\nResumen de estaciones:")
    print(df_resumen.to_string(index=False))

    print("\n" + "=" * 70)
    print("PREPARACION FINALIZADA")
    print("=" * 70)


if __name__ == "__main__":
    main()
