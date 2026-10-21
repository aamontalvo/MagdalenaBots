#!/usr/bin/env python3
"""
08_export_softr_csvs.py
=======================

Genera los CSV de importación para el database "Magdalena SGR" de Softr.

Salidas en backend/entregables/softr_import/:
- estaciones.csv
- resumen_niveles.csv
- resumen_caudales.csv
- datasets.csv
- metricas.csv
- figuras.csv
- niveles_diarios/part_XX.csv  (50.000 filas por parte)
- caudales_diarios/part_XX.csv (50.000 filas por parte)
- README_IMPORT.md
- manifest.csv

No sube nada a Softr: solo prepara los archivos para el importador CSV.
"""

import hashlib
import os
import re
import sys
from pathlib import Path
from urllib.parse import quote

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "backend" / "entregables" / "softr_import"
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "niveles_diarios").mkdir(exist_ok=True)
(OUT / "caudales_diarios").mkdir(exist_ok=True)

NIV_SUM = ROOT / "backend" / "entregables" / "niveles_v2_1" / "05_validacion_y_auditoria" / "Resumen_Imputacion.csv"
NIV_FINAL = ROOT / "backend" / "entregables" / "niveles_v2_1" / "02_datos_imputados" / "Datos_Imputados.csv"
NIV_CART = ROOT / "backend" / "entregables" / "niveles_v2_1" / "07_cartillas"
NIV_GLOBAL = ROOT / "backend" / "entregables" / "niveles_v2_1" / "06_figuras"

CAUD_SUM = ROOT / "backend" / "data" / "work" / "caudales_v1" / "output" / "Resumen_Imputacion_Caudales.csv"
CAUD_FINAL = ROOT / "backend" / "data" / "work" / "caudales_v1" / "output" / "Datos_Imputados_Caudales.csv"
CAUD_CART = ROOT / "cartillas_estaciones" / "Caudales"
CAUD_UNI = ROOT / "backend" / "data" / "processed" / "caudales_unificados.csv"
CAUD_RAW_LONG = ROOT / "backend" / "data" / "raw" / "SERIE_CAUDALES" / "analisis" / "caudales_formato_largo.csv"

FIGURE_BASE = os.environ.get("SOFTR_FIGURE_BASE_URL", "https://PENDING_HOST").rstrip("/")
CUTOFF = "2026-08-24"
PART_ROWS = 50_000

DISPLAY = {
    "ARMENIA": "Armenia", "BARBOSA": "Barbosa", "BARRANCABERMEJA": "Barrancabermeja",
    "CALAMAR": "Calamar", "COYONGAL": "Coyongal", "EL_BANCO": "El Banco",
    "EL_CONTENTO": "El Contento", "GAMARRA": "Gamarra", "GAMARRA_AUT": "Gamarra Automática",
    "LAS_AGUADAS": "Las Aguadas", "LAS_PALOMAS": "Las Palomas", "LA_GLORIA": "La Gloria",
    "MAGANGUE": "Magangué", "PENONCITO": "Peñoncito", "PLATO": "Plato",
    "PUERTO_BERRIO": "Puerto Berrío", "PUERTO_SALGAR": "Puerto Salgar",
    "PUERTO_WILCHES": "Puerto Wilches", "RIO_NUEVO": "Río Nuevo", "SAN_PABLO": "San Pablo",
    "SAN_PEDRITO": "San Pedrito", "SITIO_NUEVO": "Sitio Nuevo", "TEBSA": "Tebsa",
    "TENERIFE": "Tenerife",
    "BARREDERO_FINCA": "Barredero Finca", "NOBLEZA_LA": "Nobleza La",
    "PALENQUITO": "Palenquito", "PENAS_BLANCAS": "Peñas Blancas",
    "PUENTE_SOGAMOSO": "Puente Sogamoso", "PUERTO_ARAUJO": "Puerto Araujo",
    "PUERTO_LIBRE": "Puerto Libre", "SAN_MIGUEL": "San Miguel",
    "SAN_ROQUE": "San Roque", "SANTA_ANA": "Santa Ana", "SANTA_ROSA": "Santa Rosa",
}

CODES = {
    "ARMENIA": "25027360", "BARBOSA": "25027530", "BARRANCABERMEJA": "23157030",
    "CALAMAR": "29037020", "COYONGAL": "25027930", "EL_BANCO": "25027020",
    "EL_CONTENTO": "23217030", "GAMARRA": "23217020", "GAMARRA_AUT": "23217080",
    "LAS_AGUADAS": "25027490", "LAS_PALOMAS": "25027390", "LA_GLORIA": "23217060",
    "MAGANGUE": "25027680", "PENONCITO": "25027330", "PLATO": "25027450",
    "PUERTO_BERRIO": "23097030", "PUERTO_SALGAR": "23037010",
    "PUERTO_WILCHES": "23187010", "RIO_NUEVO": "25027630", "SAN_PABLO": "23207040",
    "SAN_PEDRITO": "29047070", "SITIO_NUEVO": "23187280", "TEBSA": "29047000",
    "TENERIFE": "29017010",
    "BARREDERO_FINCA": "23127050", "NOBLEZA_LA": "23207050", "PALENQUITO": "25027570",
    "PENAS_BLANCAS": "23167010", "PUENTE_SOGAMOSO": "24067020",
    "PUERTO_ARAUJO": "23127020", "PUERTO_LIBRE": "23067040",
    "SAN_MIGUEL": "23057140", "SAN_ROQUE": "25027320", "SANTA_ANA": "25027370",
    "SANTA_ROSA": "23127060",
}

ZONES = {
    "CALAMAR": "Baja", "TENERIFE": "Baja", "PLATO": "Baja", "MAGANGUE": "Baja",
    "BARBOSA": "Baja", "COYONGAL": "Baja", "SAN_PEDRITO": "Baja", "TEBSA": "Baja",
    "ARMENIA": "Media", "RIO_NUEVO": "Media", "LAS_PALOMAS": "Media",
    "LAS_AGUADAS": "Media", "EL_BANCO": "Media", "PENONCITO": "Media",
    "LA_GLORIA": "Alta", "GAMARRA_AUT": "Alta", "EL_CONTENTO": "Alta",
    "SITIO_NUEVO": "Alta", "PUERTO_WILCHES": "Alta", "BARRANCABERMEJA": "Alta",
    "GAMARRA": "Alta", "PUERTO_BERRIO": "Alta", "PUERTO_SALGAR": "Alta",
    "SAN_PABLO": "Alta",
}

KNOWN_ZONE = {
    "CALAMAR", "TENERIFE", "PLATO", "MAGANGUE", "BARBOSA", "COYONGAL",
    "SAN_PEDRITO", "ARMENIA", "RIO_NUEVO", "LAS_PALOMAS", "LAS_AGUADAS",
    "EL_BANCO", "PENONCITO", "LA_GLORIA", "GAMARRA_AUT", "EL_CONTENTO",
    "SITIO_NUEVO", "PUERTO_WILCHES",
}
INFERRED_ZONE = {"TEBSA", "BARRANCABERMEJA", "GAMARRA", "PUERTO_BERRIO", "PUERTO_SALGAR", "SAN_PABLO"}


def norm_raw(raw: str) -> str:
    n = str(raw).upper().strip()
    n = re.sub(r"_\d{6,}$", "", n)
    n = n.replace("_-_AUT", "").replace("- AUT", "")
    n = n.replace("_", " ").strip()
    n = re.sub(r"\s+", " ", n)
    n = n.upper().replace(" ", "_")
    return {"SAN_PABLO_RIO_MAGDALENA": "SAN_PABLO"}.get(n, n)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_csv(df: pd.DataFrame, path: Path):
    df.to_csv(path, index=False, encoding="utf-8")
    print(f"OK {path.relative_to(ROOT)} ({len(df):,} filas)")


niv_sum = pd.read_csv(NIV_SUM)
caud_sum = pd.read_csv(CAUD_SUM)
caud_uni_cols = pd.read_csv(CAUD_UNI, nrows=1).columns.tolist()
CAUD_BASE = sorted({norm_raw(c) for c in caud_uni_cols if c != "fecha"})
NIV = sorted(niv_sum["Estacion"].unique().tolist())
ALL = sorted(set(NIV) | set(CAUD_BASE))
DISPLAY_TO_INTERNAL = {v: k for k, v in DISPLAY.items()}

# ---------------------------------------------------------------------------
# Estaciones
# ---------------------------------------------------------------------------
niv_by = {r["Estacion"]: r for _, r in niv_sum.iterrows()}
caud_by = {
    DISPLAY_TO_INTERNAL.get(r["Estacion"], norm_raw(r["Estacion"])): r
    for _, r in caud_sum.iterrows()
}

caud_raw = pd.read_csv(CAUD_RAW_LONG, usecols=["fecha", "estacion", "caudal"], low_memory=False)
caud_raw["fecha"] = pd.to_datetime(caud_raw["fecha"], errors="coerce")
caud_raw["station_code"] = caud_raw["estacion"].map(norm_raw)
raw_by = {}
for st, g in caud_raw.groupby("station_code"):
    valid = g["caudal"].notna()
    raw_by[st] = {
        "records": len(g),
        "original_valid": int(valid.sum()),
        "nan": int((~valid).sum()),
        "coverage_pct": round(float(valid.mean() * 100), 2) if len(g) else 0,
        "start": str(g.loc[valid, "fecha"].min().date()) if valid.any() else "",
        "end": str(g.loc[valid, "fecha"].max().date()) if valid.any() else "",
    }

rows = []
for st in ALL:
    has_levels = st in niv_by
    has_caudales = st in CAUD_BASE
    n = niv_by.get(st)
    c = caud_by.get(st)
    raw = raw_by.get(st, {})

    levels_start = str(n["Fecha_Inicio"]) if has_levels else ""
    levels_end = str(n["Fecha_Fin"]) if has_levels else ""
    caudales_start = str(c["Inicio"]) if c is not None else raw.get("start", "")
    caudales_end = str(c["Fin"]) if c is not None else raw.get("end", "")

    levels_imputed = int(n["L1"] + n["L2"] + n["L3"]) if has_levels else ""
    levels_nan = int(n["NaN_Restantes_Rango"]) if has_levels else ""
    levels_records = int(n["Dias_Rango"]) if has_levels else ""
    levels_orig = int(n["Dias_Rango"] - n["NaN_Restantes_Rango"] - (n["L1"] + n["L2"] + n["L3"])) if has_levels else ""

    caudales_imputed = int(c["L1"] + c["L2"]) if c is not None else 0
    caudales_nan = int(c["NaN_restantes"]) if c is not None else raw.get("nan", "")
    caudales_records = int(c["Dias"]) if c is not None else raw.get("records", "")
    caudales_orig = int(c["Original"]) if c is not None else raw.get("original_valid", "")

    starts = [x for x in [levels_start, caudales_start] if x]
    ends = [x for x in [levels_end, caudales_end] if x]
    official_start = min(starts) if starts else ""
    official_end = max(ends) if ends else ""

    if has_levels and has_caudales:
        notes = "Común"
    elif has_levels:
        notes = "Solo niveles"
    else:
        notes = "Solo caudales (fuente)"
    if has_levels and bool(n["Descartada"]):
        notes += " · Descartada por inhomogeneidad"

    if st in KNOWN_ZONE:
        zone_source = "ZONIFICACION_ESTACIONES.md / MAESTRO_PROYECTO.md"
    elif st in INFERRED_ZONE:
        zone_source = "Inferida por orden geográfico del informe"
    else:
        zone_source = "Sin zonificación"

    rows.append({
        "station_code": st,
        "station_name": DISPLAY.get(st, st.replace("_", " ").title()),
        "zone": ZONES.get(st, ""),
        "zone_source": zone_source,
        "status": n["Status"] if has_levels else "Solo caudales",
        "ideam_code": CODES.get(st, ""),
        "official_start": official_start,
        "official_end": official_end,
        "coverage_pct": "",
        "records": "",
        "original_valid": "",
        "imputed": "",
        "nan": "",
        "has_levels": "TRUE" if has_levels else "FALSE",
        "has_caudales": "TRUE" if has_caudales else "FALSE",
        "latitude": "",
        "longitude": "",
        "notes": notes,
        "levels_start": levels_start,
        "levels_end": levels_end,
        "caudales_start": caudales_start,
        "caudales_end": caudales_end,
        "levels_records": levels_records,
        "levels_original_valid": levels_orig,
        "levels_imputed": levels_imputed,
        "levels_nan": levels_nan,
        "levels_coverage_pct": n["Cobertura_Rango_pct"] if has_levels else "",
        "caudales_records": caudales_records,
        "caudales_original_valid": caudales_orig,
        "caudales_imputed": caudales_imputed,
        "caudales_nan": caudales_nan,
        "caudales_coverage_pct": c["Cobertura_pct"] if c is not None else raw.get("coverage_pct", ""),
    })

estaciones = pd.DataFrame(rows)
write_csv(estaciones, OUT / "estaciones.csv")

# ---------------------------------------------------------------------------
# Resúmenes
# ---------------------------------------------------------------------------
res_niv = []
for st in NIV:
    r = niv_by[st]
    imput = int(r["L1"] + r["L2"] + r["L3"])
    res_niv.append({
        "station_code": st,
        "station_name": DISPLAY.get(st, st),
        "records": int(r["Dias_Rango"]),
        "original_valid": int(r["Dias_Rango"] - r["NaN_Restantes_Rango"] - imput),
        "imputed": imput,
        "nan": int(r["NaN_Restantes_Rango"]),
        "coverage_pct": r["Cobertura_Rango_pct"],
        "start_date": r["Fecha_Inicio"],
        "end_date": r["Fecha_Fin"],
        "dataset_id": "levels_final_v2_1",
        "figures_count": len(list((NIV_CART / st).glob("*.png"))),
    })
write_csv(pd.DataFrame(res_niv), OUT / "resumen_niveles.csv")

res_caud = []
for st, r in caud_by.items():
    imput = int(r["L1"] + r["L2"])
    res_caud.append({
        "station_code": st,
        "station_name": DISPLAY.get(st, st),
        "records": int(r["Dias"]),
        "original_valid": int(r["Original"]),
        "imputed": imput,
        "nan": int(r["NaN_restantes"]),
        "coverage_pct": r["Cobertura_pct"],
        "start_date": r["Inicio"],
        "end_date": r["Fin"],
        "nc_r2": r["NC_R2"],
        "nc_accepted": "TRUE" if bool(r["NC_aceptado"]) else "FALSE",
        "dataset_id": "caudales_final_v1",
        "figures_count": len(list((CAUD_CART / st).glob("*.png"))),
    })
write_csv(pd.DataFrame(res_caud), OUT / "resumen_caudales.csv")

# ---------------------------------------------------------------------------
# Métricas
# ---------------------------------------------------------------------------
metric_rows = [
    ("general_stations_unique", "General", "Estaciones únicas", "Estaciones únicas analizadas", 35, "conteo"),
    ("general_records", "General", "Registros procesados", "Registros procesados totales", 694011, "registros"),
    ("general_imputed", "General", "Datos imputados", "Datos imputados totales", 83816, "registros"),
    ("general_cartillas", "General", "Cartillas", "Cartillas generadas", 38, "conteo"),
    ("general_figures", "General", "Figuras", "Figuras vigentes", 251, "conteo"),
    ("levels_stations", "Niveles", "Estaciones", "Estaciones con niveles", 24, "conteo"),
    ("levels_records", "Niveles", "Registros", "Registros finales de niveles", 394772, "registros"),
    ("levels_original_valid", "Niveles", "Originales válidos", "Registros originales válidos", 335501, "registros"),
    ("levels_original_pct", "Niveles", "Originales válidos %", "Porcentaje de originales válidos", 84.99, "%"),
    ("levels_imputed", "Niveles", "Datos imputados", "Datos imputados", 54835, "registros"),
    ("levels_imputed_pct", "Niveles", "Datos imputados %", "Porcentaje de datos imputados", 13.89, "%"),
    ("levels_nan", "Niveles", "Faltantes", "NaN documentados", 4436, "registros"),
    ("levels_coverage_pct", "Niveles", "Cobertura", "Cobertura media", 98.87, "%"),
    ("levels_stations_100", "Niveles", "Estaciones 100%", "Estaciones con cobertura 100%", 12, "conteo"),
    ("levels_stations_gt95", "Niveles", "Estaciones >95%", "Estaciones con cobertura >95%", 23, "conteo"),
    ("levels_stations_lt95", "Niveles", "Estaciones <95%", "Estaciones con cobertura <95%", 1, "conteo"),
    ("levels_cartillas", "Niveles", "Cartillas", "Cartillas de niveles", 24, "conteo"),
    ("levels_figures", "Niveles", "Figuras", "Figuras vigentes de niveles", 150, "conteo"),
    ("levels_report_stations", "Niveles", "Estaciones en informe", "Estaciones incluidas en el informe", 24, "conteo"),
    ("levels_report_images", "Niveles", "Imágenes en informe", "Imágenes del informe de niveles", 105, "conteo"),
    ("caudales_stations", "Caudales", "Estaciones", "Estaciones con caudales", 14, "conteo"),
    ("caudales_records", "Caudales", "Registros", "Registros finales de caudales", 299239, "registros"),
    ("caudales_original_valid", "Caudales", "Originales válidos", "Registros originales válidos", 262425, "registros"),
    ("caudales_original_pct", "Caudales", "Originales válidos %", "Porcentaje de originales válidos", 87.70, "%"),
    ("caudales_imputed", "Caudales", "Datos imputados", "Datos imputados", 28981, "registros"),
    ("caudales_imputed_pct", "Caudales", "Datos imputados %", "Porcentaje de datos imputados", 9.68, "%"),
    ("caudales_nan", "Caudales", "Faltantes", "NaN documentados", 7833, "registros"),
    ("caudales_coverage_pct", "Caudales", "Cobertura", "Cobertura media", 97.74, "%"),
    ("caudales_stations_100", "Caudales", "Estaciones 100%", "Estaciones con cobertura 100%", 7, "conteo"),
    ("caudales_stations_gt95", "Caudales", "Estaciones >95%", "Estaciones con cobertura >95%", 12, "conteo"),
    ("caudales_stations_lt95", "Caudales", "Estaciones <95%", "Estaciones con cobertura <95%", 2, "conteo"),
    ("caudales_cartillas", "Caudales", "Cartillas", "Cartillas de caudales", 14, "conteo"),
    ("caudales_figures", "Caudales", "Figuras", "Figuras vigentes de caudales", 101, "conteo"),
    ("caudales_report_stations", "Caudales", "Estaciones en informe", "Estaciones incluidas en el informe", 14, "conteo"),
    ("caudales_nc_models", "Caudales", "Modelos N-C", "Curvas Nivel-Caudal", 14, "modelos"),
    ("caudales_nc_pairs", "Caudales", "Pares N-C", "Pares concurrentes N-C", 222993, "pares"),
    ("caudales_nc_r2_min", "Caudales", "R² N-C mínimo", "R² mínimo de las curvas N-C", 0.6734, "R²"),
    ("caudales_nc_r2_max", "Caudales", "R² N-C máximo", "R² máximo de las curvas N-C", 0.9676, "R²"),
    ("quality_caudales_checks_pass", "Calidad", "Checks PASS", "Checks de caudales aprobados", 6, "conteo"),
    ("quality_caudales_checks_fail", "Calidad", "Checks FAIL", "Checks de caudales fallidos", 0, "conteo"),
    ("quality_homogeneity_stations", "Calidad", "Estaciones homogeneidad", "Estaciones evaluadas en homogeneidad", 25, "conteo"),
    ("quality_mk_significant", "Calidad", "Mann-Kendall significativo", "Estaciones con Mann-Kendall significativo", 23, "conteo"),
]
metricas = pd.DataFrame(metric_rows, columns=["metric_id", "variable", "metric", "label", "value", "unit"])
metricas["source"] = "docs/METRICAS_CAUDALES_NIVELES.md"
metricas["cutoff"] = CUTOFF
write_csv(metricas, OUT / "metricas.csv")

# ---------------------------------------------------------------------------
# Figuras
# ---------------------------------------------------------------------------
LEVEL_TYPE = {
    "Fig1": "Fig1 Serie de tiempo",
    "Fig2": "Fig2 Violín mensual",
    "Fig3": "Fig3 Curva de duración",
    "Fig4": "Fig4 Curvas de excedidos",
    "Fig5": "Fig5 Ajuste de distribuciones",
    "Fig6": "Fig6 Relación H-H",
}
CAUD_TYPE = {
    "Fig1": "Fig1 Serie de tiempo",
    "Fig2": "Fig2 Violín mensual",
    "Fig3": "Fig3 Curva de duración",
    "Fig4": "Fig4 Curvas de excedidos",
    "Fig5_max": "Fig5 Ajuste de máximos",
    "Fig5_min": "Fig5 Ajuste de mínimos",
    "Fig6": "Fig6 Curva Nivel-Caudal",
}


def fig_type_level(name: str) -> str:
    for key, label in LEVEL_TYPE.items():
        if name.startswith(key + "_"):
            return label
    return "Global"


def fig_type_caud(name: str) -> str:
    if name.startswith("Fig5_Ajuste_Extremos_maximos"):
        return CAUD_TYPE["Fig5_max"]
    if name.startswith("Fig5_Ajuste_Extremos_minimos"):
        return CAUD_TYPE["Fig5_min"]
    for key in ["Fig1", "Fig2", "Fig3", "Fig4", "Fig6"]:
        if name.startswith(key + "_"):
            return CAUD_TYPE[key]
    return "Global"


def slug(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")


def url_for(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    return f"{FIGURE_BASE}/{quote(rel)}"


fig_rows = []
for st_dir in sorted([d for d in NIV_CART.iterdir() if d.is_dir()]):
    st = st_dir.name
    for png in sorted(st_dir.glob("*.png")):
        typ = fig_type_level(png.name)
        fig_rows.append({
            "figure_id": f"levels_{st}_{slug(png.stem)}",
            "variable": "Niveles",
            "station_code": st,
            "figure_type": typ,
            "caption": f"{typ} - {DISPLAY.get(st, st)}",
            "image_url": url_for(png),
            "report_use": "Cartilla",
            "generated_at": CUTOFF,
            "dataset_id": "levels_final_v2_1",
            "local_path": png.relative_to(ROOT).as_posix(),
        })
for png in sorted(NIV_GLOBAL.glob("*.png")):
    fig_rows.append({
        "figure_id": f"levels_global_{slug(png.stem)}",
        "variable": "Niveles",
        "station_code": "",
        "figure_type": "Global",
        "caption": f"Global - {png.stem.replace('_', ' ')}",
        "image_url": url_for(png),
        "report_use": "Dashboard",
        "generated_at": CUTOFF,
        "dataset_id": "levels_final_v2_1",
        "local_path": png.relative_to(ROOT).as_posix(),
    })

for st_dir in sorted([d for d in CAUD_CART.iterdir() if d.is_dir()]):
    st = st_dir.name
    for png in sorted(st_dir.glob("*.png")):
        typ = fig_type_caud(png.name)
        fig_rows.append({
            "figure_id": f"caudales_{st}_{slug(png.stem)}",
            "variable": "Caudales",
            "station_code": st,
            "figure_type": typ,
            "caption": f"{typ} - {DISPLAY.get(st, st)}",
            "image_url": url_for(png),
            "report_use": "Cartilla",
            "generated_at": CUTOFF,
            "dataset_id": "caudales_final_v1",
            "local_path": png.relative_to(ROOT).as_posix(),
        })
for png in sorted(CAUD_CART.glob("*.png")):
    fig_rows.append({
        "figure_id": f"caudales_global_{slug(png.stem)}",
        "variable": "Caudales",
        "station_code": "",
        "figure_type": "Global",
        "caption": f"Global - {png.stem.replace('_', ' ')}",
        "image_url": url_for(png),
        "report_use": "Dashboard",
        "generated_at": CUTOFF,
        "dataset_id": "caudales_final_v1",
        "local_path": png.relative_to(ROOT).as_posix(),
    })

figuras = pd.DataFrame(fig_rows)
write_csv(figuras, OUT / "figuras.csv")

# ---------------------------------------------------------------------------
# Datasets
# ---------------------------------------------------------------------------
def ds_row(dataset_id, name, variable, version, rows, stations, dmin, dmax, path, status):
    p = ROOT / path
    return {
        "dataset_id": dataset_id,
        "name": name,
        "variable": variable,
        "version": version,
        "rows": rows,
        "stations": stations,
        "date_min": dmin,
        "date_max": dmax,
        "file_path": path,
        "sha256": sha256(p) if p.exists() else "",
        "status": status,
    }

datasets = pd.DataFrame([
    ds_row("levels_raw_v2_1", "Resumen_Crudos_IDEAM_2026_v2_1.csv", "Niveles", "v2.1", 394772, 24, "1960-01-01", "2025-12-31", "backend/entregables/niveles_v2_1/01_datos_originales/Resumen_Crudos_IDEAM_2026_v2_1.csv", "Crudo"),
    ds_row("levels_final_v2_1", "Datos_Imputados.csv", "Niveles", "v2.1", 394772, 24, "1960-01-01", "2025-12-31", "backend/entregables/niveles_v2_1/02_datos_imputados/Datos_Imputados.csv", "Final"),
    ds_row("levels_summary_v2_1", "Resumen_Imputacion.csv", "Niveles", "v2.1", 24, 24, "", "", "backend/entregables/niveles_v2_1/05_validacion_y_auditoria/Resumen_Imputacion.csv", "Resumen"),
    ds_row("caudales_raw_long", "caudales_formato_largo.csv", "Caudales", "v1", 481435, 25, "1936-01-01", "2026-12-31", "backend/data/raw/SERIE_CAUDALES/analisis/caudales_formato_largo.csv", "Crudo"),
    ds_row("caudales_unified", "caudales_unificados.csv", "Caudales", "v1", 205722, 25, "1936-01-01", "2026-03-14", "backend/data/processed/caudales_unificados.csv", "Base"),
    ds_row("caudales_final_v1", "Datos_Imputados_Caudales.csv", "Caudales", "v1", 299239, 14, "1936-01-01", "2026-03-14", "backend/data/work/caudales_v1/output/Datos_Imputados_Caudales.csv", "Final"),
    ds_row("caudales_summary_v1", "Resumen_Imputacion_Caudales.csv", "Caudales", "v1", 14, 14, "", "", "backend/data/work/caudales_v1/output/Resumen_Imputacion_Caudales.csv", "Resumen"),
    ds_row("nc_curves_v1", "curvas_nivel_caudal_resumen.csv", "Caudales", "v1", 14, 14, "", "", "cartillas_estaciones/Caudales/curvas_nivel_caudal_resumen.csv", "Modelos"),
    ds_row("duration_curves_v1", "curvas_duracion_caudales_resumen.csv", "Caudales", "v1", 14, 14, "", "", "cartillas_estaciones/Caudales/curvas_duracion_caudales_resumen.csv", "Figuras"),
    ds_row("metrics_v1", "metricas_caudales_niveles.json", "General", "v1", "", "", "", "", "docs/metricas_caudales_niveles.json", "Métricas"),
    ds_row("figures_manifest_v1", "figuras.csv", "General", "v1", 251, "", "", "", "backend/entregables/softr_import/figuras.csv", "Catálogo"),
])
write_csv(datasets, OUT / "datasets.csv")

# ---------------------------------------------------------------------------
# Series diarias
# ---------------------------------------------------------------------------
def split_write(df: pd.DataFrame, folder: Path, prefix: str):
    n = len(df)
    parts = (n + PART_ROWS - 1) // PART_ROWS
    for i in range(parts):
        chunk = df.iloc[i * PART_ROWS:(i + 1) * PART_ROWS].copy()
        path = folder / f"{prefix}_{i + 1:02d}.csv"
        chunk.to_csv(path, index=False, encoding="utf-8")
        print(f"OK {path.relative_to(ROOT)} ({len(chunk):,} filas)")
    return parts


niv = pd.read_csv(NIV_FINAL, low_memory=False)
niv["Fecha"] = pd.to_datetime(niv["Fecha"], errors="coerce")
niv["station_code"] = niv["NombreEstacion"].str.upper().str.strip()
niv["station_name"] = niv["station_code"].map(DISPLAY).fillna(niv["station_code"].str.replace("_", " ").str.title())
niv["date"] = niv["Fecha"].dt.strftime("%Y-%m-%d")
niv["value_m"] = niv["Cota"]
niv["data_source"] = np.where(niv["Cota"].isna(), "Faltante", np.where(niv["Nivel_Imputacion"] > 0, "Imputado", "Original"))
niv["method"] = niv["Metodo"].fillna("")
niv.loc[niv["data_source"] == "Faltante", "method"] = ""
niv["dataset_id"] = "levels_final_v2_1"
niv["Name"] = niv["station_code"] + "|" + niv["date"]
niv_out = niv[["Name", "station_code", "station_name", "date", "value_m", "data_source", "method", "dataset_id"]].copy()
niv_out = niv_out.sort_values(["station_code", "date"]).reset_index(drop=True)
niv_parts = split_write(niv_out, OUT / "niveles_diarios", "part")

caud = pd.read_csv(CAUD_FINAL, low_memory=False)
caud["Fecha"] = pd.to_datetime(caud["Fecha"], errors="coerce")
caud["station_code"] = caud["NombreEstacion"].str.upper().str.strip()
caud["station_name"] = caud["station_code"].map(DISPLAY).fillna(caud["station_code"].str.replace("_", " ").str.title())
caud["date"] = caud["Fecha"].dt.strftime("%Y-%m-%d")
caud["value_m3s"] = caud["Caudal"]
caud["data_source"] = np.where(caud["Caudal"].isna(), "Faltante", np.where(caud["Nivel_Imputacion"] > 0, "Imputado", "Original"))
caud["method"] = caud["Metodo"].fillna("")
caud.loc[caud["data_source"] == "Faltante", "method"] = ""
caud["dataset_id"] = "caudales_final_v1"
caud["Name"] = caud["station_code"] + "|" + caud["date"]
caud_out = caud[["Name", "station_code", "station_name", "date", "value_m3s", "data_source", "method", "dataset_id"]].copy()
caud_out = caud_out.sort_values(["station_code", "date"]).reset_index(drop=True)
caud_parts = split_write(caud_out, OUT / "caudales_diarios", "part")

# ---------------------------------------------------------------------------
# Manifiesto y README
# ---------------------------------------------------------------------------
manifest_rows = []
for p in sorted(OUT.rglob("*.csv")):
    if p.name == "manifest.csv":
        continue
    try:
        nrows = sum(1 for _ in p.open("r", encoding="utf-8")) - 1
    except Exception:
        nrows = ""
    manifest_rows.append({"file": p.relative_to(ROOT).as_posix(), "rows": nrows, "bytes": p.stat().st_size})
write_csv(pd.DataFrame(manifest_rows), OUT / "manifest.csv")

readme = f"""# Importación a Softr - Magdalena SGR

Database: `Magdalena SGR`
ID: `cdc45f86-e02c-4c19-8e65-5854d6e8a816`

## Orden de importación

1. `estaciones.csv` -> tabla `Estaciones` (35 filas).
2. `datasets.csv` -> tabla `Datasets` (11 filas).
3. `resumen_niveles.csv` -> tabla `Resumen_Niveles` (24 filas).
4. `resumen_caudales.csv` -> tabla `Resumen_Caudales` (14 filas).
5. `metricas.csv` -> tabla `Metricas` (42 filas).
6. `niveles_diarios/part_01.csv` ... `part_{niv_parts:02d}.csv` -> tabla `Niveles` (394.772 filas).
7. `caudales_diarios/part_01.csv` ... `part_{caud_parts:02d}.csv` -> tabla `Caudales` (299.239 filas).
8. `figuras.csv` -> tabla `Figuras` (251 filas).

## Notas de importación

- Codificación: UTF-8.
- Fechas: `YYYY-MM-DD`.
- Booleanos: `TRUE` / `FALSE`.
- El campo primario de `Niveles` y `Caudales` es `Name`; el valor es `station_code|date` y es único.
- `data_source` toma `Original`, `Imputado` o `Faltante`.
- Los 3 registros vacíos que ya existen en `Niveles` y `Caudales` se dejan; Alex los borrará después.
- Si el importador rechaza una parte por tamaño, dividirla en dos.
- `figuras.csv` se genera con `PENDING_HOST`; el paso `10_publish_figures_repo.py` lo actualiza a URLs raw de GitHub en `cartillas_estaciones/figuras_publicas/`. El repo debe ser público para que Softr cargue las imágenes.
- Las tablas creadas contienen campos genéricos (`official_start`, `records`, etc.) que se dejan vacíos; los valores específicos están en `levels_*` y `caudales_*`.
"""
(OUT / "README_IMPORT.md").write_text(readme, encoding="utf-8")

print("\nResumen:")
print(f"  estaciones: {len(estaciones)}")
print(f"  resumen_niveles: {len(res_niv)}")
print(f"  resumen_caudales: {len(res_caud)}")
print(f"  metricas: {len(metricas)}")
print(f"  figuras: {len(figuras)}")
print(f"  niveles diarios: {len(niv_out):,} en {niv_parts} partes")
print(f"  caudales diarios: {len(caud_out):,} en {caud_parts} partes")
print(f"  salida: {OUT}")
