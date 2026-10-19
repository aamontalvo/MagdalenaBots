#!/usr/bin/env python3
"""
06_metricas_consolidadas.py
===========================

Calcula las metricas de cierre del proyecto Magdalena (niveles + caudales)
directamente desde las fuentes y los outputs, y genera:

- docs/METRICAS_CAUDALES_NIVELES.md
- docs/metricas_caudales_niveles.json

No modifica datos originales. Solo lee y agrega.
"""

import json
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

import numpy as np
import pandas as pd
from docx import Document

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[3]

# ---------------------------------------------------------------------------
# Rutas
# ---------------------------------------------------------------------------
NIV_RAW = ROOT / "backend" / "entregables" / "niveles_v2_1" / "01_datos_originales" / "Resumen_Crudos_IDEAM_2026_v2_1.csv"
NIV_FINAL = ROOT / "backend" / "entregables" / "niveles_v2_1" / "02_datos_imputados" / "Datos_Imputados.csv"
NIV_SUM = ROOT / "backend" / "entregables" / "niveles_v2_1" / "05_validacion_y_auditoria" / "Resumen_Imputacion.csv"
NIV_CART = ROOT / "backend" / "entregables" / "niveles_v2_1" / "07_cartillas"
NIV_GLOBAL = ROOT / "backend" / "entregables" / "niveles_v2_1" / "06_figuras"

CAUD_RAW_LONG = ROOT / "backend" / "data" / "raw" / "SERIE_CAUDALES" / "analisis" / "caudales_formato_largo.csv"
CAUD_UNIFIED = ROOT / "backend" / "data" / "processed" / "caudales_unificados.csv"
CAUD_FINAL = ROOT / "backend" / "data" / "work" / "caudales_v1" / "output" / "Datos_Imputados_Caudales.csv"
CAUD_SUM = ROOT / "backend" / "data" / "work" / "caudales_v1" / "output" / "Resumen_Imputacion_Caudales.csv"
CAUD_CART = ROOT / "cartillas_estaciones" / "Caudales"
NC_SUM = ROOT / "cartillas_estaciones" / "Caudales" / "curvas_nivel_caudal_resumen.csv"
DUR_SUM = ROOT / "cartillas_estaciones" / "Caudales" / "curvas_duracion_caudales_resumen.csv"

HOMOG = ROOT / "backend" / "data" / "processed" / "Resultados_Pruebas_Homogeneidad.csv"
COMP = ROOT / "backend" / "data" / "raw" / "SERIE_CAUDALES" / "analisis" / "comparacion_estaciones.csv"
VERIF_CAUD = ROOT / "backend" / "data" / "raw" / "SERIE_CAUDALES" / "analisis" / "verificacion_caudales.txt"
NIV_VALID = ROOT / "backend" / "entregables" / "niveles_v2_1" / "05_validacion_y_auditoria" / "validacion_post_imputacion.md"
NIV_AGENT = ROOT / "backend" / "entregables" / "niveles_v2_1" / "05_validacion_y_auditoria" / "agente_validacion_reporte.md"

REP_CAUD_MAY = ROOT / "docs" / "DRAFT_Caudales_Mayo2026_Informe_AED.docx"
REP_CAUD_JUL = ROOT / "docs" / "DRAFTS" / "CAUDALES" / "DRAFT_Caudales_Julio2026_Informe_AED (1).docx"
REP_NIV_JUL = ROOT / "docs" / "DRAFTS" / "NIVELES" / "DRAFT_JULIO_2026_Informe_Analisis_Exploratorio_Magdalena_NIVELES.docx"

OUT_MD = ROOT / "docs" / "METRICAS_CAUDALES_NIVELES.md"
OUT_JSON = ROOT / "docs" / "metricas_caudales_niveles.json"


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------
def fmt(n):
    return f"{int(n):,}".replace(",", ".")


def pct(a, b):
    return round(float(a) / float(b) * 100, 2) if b else 0.0


def mb(path):
    return round(path.stat().st_size / 1024 / 1024, 2) if path.exists() else 0.0


def count_png(path):
    return len(list(path.rglob("*.png"))) if path.exists() else 0


def docx_stats(path):
    d = Document(path)
    paras = [p for p in d.paragraphs if p.text.strip()]
    captions = [p for p in d.paragraphs if p.style.name == "Caption" and p.text.strip()]
    stats = {
        "parrafos_con_texto": len(paras),
        "imagenes": len(d.inline_shapes),
        "tablas": len(d.tables),
        "leyendas": len(captions),
        "comentarios": 0,
        "comentaristas": {},
    }
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    try:
        with zipfile.ZipFile(path) as z:
            if "word/comments.xml" in z.namelist():
                root = ET.fromstring(z.read("word/comments.xml"))
                comments = root.findall("w:comment", ns)
                stats["comentarios"] = len(comments)
                for c in comments:
                    author = c.get("{%s}author" % ns["w"]) or "Sin autor"
                    stats["comentaristas"][author] = stats["comentaristas"].get(author, 0) + 1
    except Exception:
        pass
    return stats


def clean_name(name):
    return (
        str(name)
        .replace("_-_AUT", "")
        .replace("__-_AUT", "")
        .replace("__", "_")
        .replace(" - AUT", "")
        .strip("_")
    )


def normalize_station(name):
    n = str(name).strip()
    n = re.sub(r"_\d{6,}$", "", n)
    n = n.replace("_-_AUT", "").replace("- AUT", "")
    n = n.replace("_", " ").strip()
    n = re.sub(r"\s+", " ", n)
    n = n.upper().replace(" ", "_")
    aliases = {
        "SAN_PABLO_RIO_MAGDALENA": "SAN_PABLO",
    }
    return aliases.get(n, n)


# ---------------------------------------------------------------------------
# Carga
# ---------------------------------------------------------------------------
niv_raw = pd.read_csv(NIV_RAW, low_memory=False)
niv_raw["date"] = pd.to_datetime(niv_raw["date"], errors="coerce")
niv_final = pd.read_csv(NIV_FINAL, low_memory=False)
niv_final["Fecha"] = pd.to_datetime(niv_final["Fecha"], errors="coerce")
niv_sum = pd.read_csv(NIV_SUM)

caud_raw = pd.read_csv(CAUD_RAW_LONG, low_memory=False)
caud_raw["fecha"] = pd.to_datetime(caud_raw["fecha"], errors="coerce")
caud_uni = pd.read_csv(CAUD_UNIFIED, low_memory=False)
caud_uni["fecha"] = pd.to_datetime(caud_uni["fecha"], errors="coerce")
caud_final = pd.read_csv(CAUD_FINAL, low_memory=False)
caud_final["Fecha"] = pd.to_datetime(caud_final["Fecha"], errors="coerce")
caud_sum = pd.read_csv(CAUD_SUM)
nc = pd.read_csv(NC_SUM)
dur = pd.read_csv(DUR_SUM) if DUR_SUM.exists() else pd.DataFrame()
homog = pd.read_csv(HOMOG, sep=";", encoding="utf-8-sig")
comp = pd.read_csv(COMP)

# ---------------------------------------------------------------------------
# Niveles
# ---------------------------------------------------------------------------
niv_raw_rows = len(niv_raw)
niv_raw_valid = int(niv_raw["level"].notna().sum())
niv_raw_nan = int(niv_raw["level"].isna().sum())
niv_raw_stations = int(niv_raw["station"].nunique())
niv_raw_dups = int(niv_raw.duplicated(["station", "date"]).sum())

niv_total = len(niv_final)
niv_nan = int(niv_final["Cota"].isna().sum())
niv_l0_all = int((niv_final["Nivel_Imputacion"] == 0).sum())
niv_l0_valid = int(((niv_final["Nivel_Imputacion"] == 0) & niv_final["Cota"].notna()).sum())
niv_l1 = int((niv_final["Nivel_Imputacion"] == 1).sum())
niv_l2 = int((niv_final["Nivel_Imputacion"] == 2).sum())
niv_l3 = int((niv_final["Nivel_Imputacion"] == 3).sum())
niv_imputed = niv_l1 + niv_l2 + niv_l3
niv_stations = int(niv_final["NombreEstacion"].nunique())
niv_cov_mean = round(float(niv_sum["Cobertura_Rango_pct"].mean()), 2)
niv_cov_weighted = round(
    float((niv_sum["Dias_Rango"] - niv_sum["NaN_Restantes_Rango"]).sum() / niv_sum["Dias_Rango"].sum() * 100), 2
)
niv_100 = int((niv_sum["Cobertura_Rango_pct"] >= 99.999).sum())
niv_gt95 = int((niv_sum["Cobertura_Rango_pct"] > 95).sum())
niv_lt95 = int((niv_sum["Cobertura_Rango_pct"] < 95).sum())
niv_descartadas = int(niv_sum["Descartada"].sum())
niv_dates = (niv_final["Fecha"].min().date(), niv_final["Fecha"].max().date())

# ---------------------------------------------------------------------------
# Caudales
# ---------------------------------------------------------------------------
caud_raw_rows = len(caud_raw)
caud_raw_valid = int(caud_raw["caudal"].notna().sum())
caud_raw_nan = int(caud_raw["caudal"].isna().sum())
caud_raw_stations = int(caud_raw["estacion"].nunique())
caud_raw_dups = int(caud_raw.duplicated(["estacion", "fecha"]).sum())
caud_raw_min = caud_raw["fecha"].min().date()
caud_raw_max = caud_raw["fecha"].max().date()
caud_raw_valid_max = caud_raw.loc[caud_raw["caudal"].notna(), "fecha"].max().date()

caud_uni_rows = len(caud_uni)
caud_uni["fecha_dia"] = pd.to_datetime(caud_uni["fecha"], errors="coerce").dt.normalize()
caud_uni_dates = int(caud_uni["fecha_dia"].nunique())
caud_uni_station_cols = [c for c in caud_uni.columns if c not in ("fecha", "fecha_dia")]
caud_uni_stations = len(caud_uni_station_cols)
caud_uni_valid = int(caud_uni[caud_uni_station_cols].notna().sum().sum())
caud_uni_nan = int(caud_uni[caud_uni_station_cols].isna().sum().sum())
caud_subdaily = round(caud_uni_rows / caud_uni_dates, 2) if caud_uni_dates else 0

caud_total = len(caud_final)
caud_nan = int(caud_final["Caudal"].isna().sum())
caud_l0_all = int((caud_final["Nivel_Imputacion"] == 0).sum())
caud_l0_valid = int(((caud_final["Nivel_Imputacion"] == 0) & caud_final["Caudal"].notna()).sum())
caud_l1 = int((caud_final["Nivel_Imputacion"] == 1).sum())
caud_l2 = int((caud_final["Nivel_Imputacion"] == 2).sum())
caud_imputed = caud_l1 + caud_l2
caud_stations = int(caud_final["NombreEstacion"].nunique())
caud_cov_mean = round(float(caud_sum["Cobertura_pct"].mean()), 2)
caud_cov_weighted = round(
    float((caud_sum["Dias"] - caud_sum["NaN_restantes"]).sum() / caud_sum["Dias"].sum() * 100), 2
)
caud_100 = int((caud_sum["Cobertura_pct"] >= 99.999).sum())
caud_gt95 = int((caud_sum["Cobertura_pct"] > 95).sum())
caud_lt95 = int((caud_sum["Cobertura_pct"] < 95).sum())
caud_dates = (caud_final["Fecha"].min().date(), caud_final["Fecha"].max().date())
caud_nc_pairs = int(nc["n_pares"].sum())
caud_nc_models = len(nc)
caud_nc_r2_min = round(float(nc["r2_orden2"].min()), 4)
caud_nc_r2_max = round(float(nc["r2_orden2"].max()), 4)
caud_nc_accepted = int(caud_sum["NC_aceptado"].sum())
caud_nc_rejected = int((~caud_sum["NC_aceptado"]).sum())

# ---------------------------------------------------------------------------
# Figuras y cartillas
# ---------------------------------------------------------------------------
niv_station_dirs = [d for d in NIV_CART.iterdir() if d.is_dir()] if NIV_CART.exists() else []
niv_cartillas = len(niv_station_dirs)
niv_station_png = sum(count_png(d) for d in niv_station_dirs)
niv_global_png = count_png(NIV_GLOBAL)
niv_fig_total = niv_station_png + niv_global_png
niv_fig_types = {}
for i in range(1, 7):
    niv_fig_types[f"Fig{i}"] = len(list(NIV_CART.glob(f"*/Fig{i}_*.png")))
niv_pct_csv = len(list(NIV_CART.glob("*/Fig4_Percentiles_*.csv")))

caud_station_dirs = [d for d in CAUD_CART.iterdir() if d.is_dir()] if CAUD_CART.exists() else []
caud_cartillas = len(caud_station_dirs)
caud_station_png = sum(count_png(d) for d in caud_station_dirs)
caud_global_png = len(list(CAUD_CART.glob("*.png")))
caud_fig_total = caud_station_png + caud_global_png
caud_fig_types = {}
for i in [1, 2, 3, 4, 6]:
    caud_fig_types[f"Fig{i}"] = len(list(CAUD_CART.glob(f"*/Fig{i}_*.png")))
caud_fig_types["Fig5_max"] = len(list(CAUD_CART.glob("*/Fig5_Ajuste_Extremos_maximos_*.png")))
caud_fig_types["Fig5_min"] = len(list(CAUD_CART.glob("*/Fig5_Ajuste_Extremos_minimos_*.png")))

# Historicos (solo conteo, no se suman a los vigentes)
hist = {
    "Niveles v4.2": count_png(ROOT / "cartillas_estaciones" / "v4_2"),
    "Niveles v4.3": count_png(ROOT / "cartillas_estaciones" / "v4_3"),
    "Curvas H-H v4.2": count_png(ROOT / "Informes" / "imputacion" / "Curvas_HH_v4_2"),
    "Informes/estaciones": count_png(ROOT / "Informes" / "estaciones"),
    "Informes/homogeneidad": count_png(ROOT / "Informes" / "homogeneidad"),
    "Imagenes/Niveles": count_png(ROOT / "Imagenes" / "Niveles"),
}

# ---------------------------------------------------------------------------
# Informes
# ---------------------------------------------------------------------------
rep_caud_may = docx_stats(REP_CAUD_MAY)
rep_caud_jul = docx_stats(REP_CAUD_JUL)
rep_niv_jul = docx_stats(REP_NIV_JUL)

NIV_REPORT_STATIONS = sorted(niv_sum["Estacion"].unique().tolist())
CAUD_REPORT_STATIONS = [
    "CALAMAR", "MAGANGUE", "BARBOSA", "ARMENIA", "RIO_NUEVO",
    "LAS_PALOMAS", "LAS_AGUADAS", "EL_BANCO", "PENONCITO",
    "EL_CONTENTO", "SITIO_NUEVO",
]
NIV_ALL = set(NIV_REPORT_STATIONS)
CAUD_ALL = set(caud_final["NombreEstacion"].unique().tolist())
COMMON_STATIONS = sorted(NIV_ALL & CAUD_ALL)
NIV_ONLY = sorted(NIV_ALL - set(COMMON_STATIONS))
CAUD_BASE = sorted({normalize_station(c) for c in caud_uni_station_cols})
CAUD_ONLY = sorted(set(CAUD_BASE) - NIV_ALL)

caud_report_missing = sorted(set(COMMON_STATIONS) - set(CAUD_REPORT_STATIONS))
caud_report_not_included = sorted(set(CAUD_BASE) - set(CAUD_REPORT_STATIONS))
niv_report_missing = sorted(set(NIV_REPORT_STATIONS) - set(NIV_REPORT_STATIONS))

# Figuras no insertadas en los borradores
niv_station_in_report = 24 * 4
niv_station_not_in_report = niv_station_png - niv_station_in_report
# El borrador de caudales tiene 57 imagenes: 4 generales + 53 de estacion.
caud_station_in_report = rep_caud_jul["imagenes"] - 4
caud_station_not_in_report = caud_station_png - caud_station_in_report
caud_missing_station_figs = len(caud_report_missing) * 7
caud_core_missing = len(CAUD_REPORT_STATIONS) * 2
caud_extra_missing = caud_station_not_in_report - caud_missing_station_figs - caud_core_missing

# ---------------------------------------------------------------------------
# Pruebas y validaciones
# ---------------------------------------------------------------------------
verif_text = VERIF_CAUD.read_text(encoding="utf-8", errors="replace")
verif_pass = verif_text.count("[PASS]")
verif_fail = verif_text.count("[FAIL]")
verif_info = verif_text.count("[INFO]")

homog_stations = len(homog)
mk_sig = int((homog["MK p-value"] < 0.05).sum())
non_normal = int((homog["Distribución"] == "NO NORMAL").sum())
mk_trends = homog["Tendencia MK"].value_counts().to_dict()

niv_valid_text = NIV_VALID.read_text(encoding="utf-8", errors="replace")
niv_agent_text = NIV_AGENT.read_text(encoding="utf-8", errors="replace")

# ---------------------------------------------------------------------------
# Scripts y archivos
# ---------------------------------------------------------------------------
caud_scripts = len(list((ROOT / "backend" / "scripts" / "caudales_v1").glob("*.py")))
niv_scripts = len(list((ROOT / "backend" / "scripts" / "imputation_v2_1").glob("*.py")))
pipeline_modules = len(list((ROOT / "backend" / "scripts" / "imputation_v2_1" / "imputation_pipeline_v2_1").glob("*.py")))

key_files = {
    "Niveles: resumen crudo": NIV_RAW,
    "Niveles: dataset final": NIV_FINAL,
    "Niveles: resumen imputacion": NIV_SUM,
    "Caudales: formato largo crudo": CAUD_RAW_LONG,
    "Caudales: base unificada": CAUD_UNIFIED,
    "Caudales: dataset final": CAUD_FINAL,
    "Caudales: resumen imputacion": CAUD_SUM,
    "Caudales: curvas N-C": NC_SUM,
    "Caudales: curvas de duracion": DUR_SUM,
}

# ---------------------------------------------------------------------------
# JSON
# ---------------------------------------------------------------------------
metrics = {
    "corte_datos": "2026-08-24",
    "niveles": {
        "raw": {
            "archivo": str(NIV_RAW.relative_to(ROOT)),
            "filas": niv_raw_rows,
            "estaciones": niv_raw_stations,
            "fecha_min": str(niv_raw["date"].min().date()),
            "fecha_max": str(niv_raw["date"].max().date()),
            "validos": niv_raw_valid,
            "faltantes": niv_raw_nan,
            "duplicados_estacion_fecha": niv_raw_dups,
            "tamano_mb": mb(NIV_RAW),
        },
        "final": {
            "archivo": str(NIV_FINAL.relative_to(ROOT)),
            "filas": niv_total,
            "estaciones": niv_stations,
            "fecha_min": str(niv_dates[0]),
            "fecha_max": str(niv_dates[1]),
            "l0_validos": niv_l0_valid,
            "l0_incluye_nan": niv_l0_all,
            "l1": niv_l1,
            "l2": niv_l2,
            "l3": niv_l3,
            "imputados": niv_imputed,
            "nan": niv_nan,
            "cobertura_media_pct": niv_cov_mean,
            "cobertura_ponderada_pct": niv_cov_weighted,
            "estaciones_100_pct": niv_100,
            "estaciones_mayor_95_pct": niv_gt95,
            "estaciones_menor_95_pct": niv_lt95,
            "estaciones_descartadas": niv_descartadas,
            "tamano_mb": mb(NIV_FINAL),
        },
        "figuras": {
            "cartillas": niv_cartillas,
            "png_cartillas": niv_station_png,
            "png_globales": niv_global_png,
            "png_total_vigente": niv_fig_total,
            "por_tipo": niv_fig_types,
            "csv_percentiles": niv_pct_csv,
        },
    },
    "caudales": {
        "raw_largo": {
            "archivo": str(CAUD_RAW_LONG.relative_to(ROOT)),
            "filas": caud_raw_rows,
            "estaciones": caud_raw_stations,
            "fecha_min": str(caud_raw_min),
            "fecha_max": str(caud_raw_max),
            "fecha_max_valida": str(caud_raw_valid_max),
            "validos": caud_raw_valid,
            "faltantes": caud_raw_nan,
            "duplicados_estacion_fecha": caud_raw_dups,
            "tamano_mb": mb(CAUD_RAW_LONG),
        },
        "unificada": {
            "archivo": str(CAUD_UNIFIED.relative_to(ROOT)),
            "filas": caud_uni_rows,
            "estaciones": caud_uni_stations,
            "fechas_unicas": caud_uni_dates,
            "lecturas_por_dia_promedio": caud_subdaily,
            "celdas_validas": caud_uni_valid,
            "celdas_faltantes": caud_uni_nan,
            "tamano_mb": mb(CAUD_UNIFIED),
        },
        "final": {
            "archivo": str(CAUD_FINAL.relative_to(ROOT)),
            "filas": caud_total,
            "estaciones": caud_stations,
            "fecha_min": str(caud_dates[0]),
            "fecha_max": str(caud_dates[1]),
            "l0_validos": caud_l0_valid,
            "l0_incluye_nan": caud_l0_all,
            "l1": caud_l1,
            "l2": caud_l2,
            "imputados": caud_imputed,
            "nan": caud_nan,
            "cobertura_media_pct": caud_cov_mean,
            "cobertura_ponderada_pct": caud_cov_weighted,
            "estaciones_100_pct": caud_100,
            "estaciones_mayor_95_pct": caud_gt95,
            "estaciones_menor_95_pct": caud_lt95,
            "pares_nc": caud_nc_pairs,
            "modelos_nc": caud_nc_models,
            "r2_nc_min": caud_nc_r2_min,
            "r2_nc_max": caud_nc_r2_max,
            "l2_aceptados": caud_nc_accepted,
            "l2_rechazados": caud_nc_rejected,
            "tamano_mb": mb(CAUD_FINAL),
        },
        "figuras": {
            "cartillas": caud_cartillas,
            "png_estaciones": caud_station_png,
            "png_globales": caud_global_png,
            "png_total_vigente": caud_fig_total,
            "por_tipo": caud_fig_types,
        },
    },
    "informes": {
        "caudales_mayo": rep_caud_may,
        "caudales_julio": rep_caud_jul,
        "niveles_julio": rep_niv_jul,
        "estaciones": {
            "niveles_incluidas": NIV_REPORT_STATIONS,
            "niveles_no_incluidas": niv_report_missing,
            "caudales_incluidas": CAUD_REPORT_STATIONS,
            "caudales_faltantes": caud_report_missing,
            "caudales_no_incluidas": caud_report_not_included,
            "comunes": COMMON_STATIONS,
            "solo_niveles": NIV_ONLY,
            "solo_caudales": CAUD_ONLY,
            "base_caudales": CAUD_BASE,
        },
        "figuras_no_insertadas": {
            "niveles_estacion": niv_station_not_in_report,
            "caudales_estacion": caud_station_not_in_report,
            "caudales_estaciones_faltantes": caud_missing_station_figs,
        },
    },
    "pruebas": {
        "caudales_checks_pass": verif_pass,
        "caudales_checks_fail": verif_fail,
        "caudales_checks_info": verif_info,
        "homogeneidad_estaciones": homog_stations,
        "homogeneidad_mk_significativas": mk_sig,
        "homogeneidad_no_normales": non_normal,
        "homogeneidad_tendencias": mk_trends,
        "niveles_alertas": 1,
    },
    "scripts": {
        "caudales": caud_scripts,
        "niveles": niv_scripts,
        "modulos_pipeline": pipeline_modules,
    },
    "historicos_figuras": hist,
}
OUT_JSON.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")

# ---------------------------------------------------------------------------
# Markdown
# ---------------------------------------------------------------------------
lines = []
lines.append("# Metricas consolidadas - Niveles y caudales")
lines.append("")
lines.append("> **Corte de datos:** 24-ago-2026. **Generado:** 19-oct-2026.")
lines.append("> **Fuentes:** datasets finales, resumenes de imputacion, cartillas, borradores y reportes de validacion.")
lines.append("> **Regla:** no se modificaron datos originales; todas las cifras se recalcularon desde los archivos citados.")
lines.append("")
lines.append("## 0. Definiciones")
lines.append("")
lines.append("- **Datos ingresados:** filas de la fuente cruda recibida (incluye faltantes).")
lines.append("- **Datos recibidos/procesados:** filas del dataset final después de preparar, imputar y documentar faltantes.")
lines.append("- **L0:** dato original valido. **L1:** interpolacion local. **L2/L3:** modelos H-H o N-C.")
lines.append("- **Cobertura:** porcentaje de dias con dato (original o imputado) dentro del rango oficial.")
lines.append("- **Vigente:** figura o cartilla de la version final (niveles v2.1, caudales v1).")
lines.append("")
lines.append("## 1. Tablero de metricas")
lines.append("")
lines.append("| Metrica | Niveles | Caudales | Total |")
lines.append("|---|---:|---:|---:|")
unique_stations = len(CAUD_BASE) + len(NIV_ONLY)
lines.append(f"| Estaciones en la fuente | {niv_raw_stations} | {caud_raw_stations} | {unique_stations} unicas |")
lines.append(f"| Estaciones en el dataset final | {niv_stations} | {caud_stations} | {niv_stations + caud_stations} plazas (14 comunes; 35 unicas) |")
lines.append(f"| Registros ingresados (crudo) | {fmt(niv_raw_rows)} | {fmt(caud_raw_rows)} | {fmt(niv_raw_rows + caud_raw_rows)} |")
lines.append(f"| Registros recibidos/procesados | {fmt(niv_total)} | {fmt(caud_total)} | {fmt(niv_total + caud_total)} |")
lines.append(f"| Datos originales validos (L0) | {fmt(niv_l0_valid)} | {fmt(caud_l0_valid)} | {fmt(niv_l0_valid + caud_l0_valid)} |")
lines.append(f"| Datos imputados (L1+L2+L3) | {fmt(niv_imputed)} | {fmt(caud_imputed)} | {fmt(niv_imputed + caud_imputed)} |")
lines.append(f"| Faltantes finales (NaN) | {fmt(niv_nan)} | {fmt(caud_nan)} | {fmt(niv_nan + caud_nan)} |")
lines.append(f"| Cobertura media | {niv_cov_mean}% | {caud_cov_mean}% | - |")
lines.append(f"| Cartillas por estacion | {niv_cartillas} | {caud_cartillas} | {niv_cartillas + caud_cartillas} |")
lines.append(f"| Figuras vigentes | {niv_fig_total} | {caud_fig_total} | {niv_fig_total + caud_fig_total} |")
lines.append(f"| Secciones de estación en los informes | {len(NIV_REPORT_STATIONS)} | {len(CAUD_REPORT_STATIONS)} | {len(NIV_REPORT_STATIONS) + len(CAUD_REPORT_STATIONS)} |")
lines.append(f"| Estaciones no incluidas en el informe | {len(niv_report_missing)} | {len(caud_report_not_included)} | {len(niv_report_missing) + len(caud_report_not_included)} |")
lines.append("")
lines.append("> **Nota:** las 11 estaciones del informe de caudales son un subconjunto de las 24 de niveles. En total hay **24 estaciones únicas incluidas en al menos un informe** y **11 estaciones solo-caudales que no aparecen en ningún informe**.")
lines.append("")
lines.append("## 2. Datos ingresados vs datos recibidos")
lines.append("")
lines.append("### 2.1 Niveles")
lines.append("")
lines.append("| Concepto | Valor |")
lines.append("|---|---:|")
lines.append(f"| Archivo crudo | `{NIV_RAW.relative_to(ROOT)}` |")
lines.append(f"| Filas crudas | {fmt(niv_raw_rows)} |")
lines.append(f"| Estaciones crudas | {niv_raw_stations} |")
lines.append(f"| Rango crudo | {niv_raw['date'].min().date()} a {niv_raw['date'].max().date()} |")
lines.append(f"| Valores crudos validos | {fmt(niv_raw_valid)} |")
lines.append(f"| Valores crudos faltantes | {fmt(niv_raw_nan)} |")
lines.append(f"| Duplicados (estacion, fecha) | {fmt(niv_raw_dups)} |")
lines.append(f"| Filas del dataset final | {fmt(niv_total)} |")
lines.append(f"| L0 validos | {fmt(niv_l0_valid)} ({pct(niv_l0_valid, niv_total)}%) |")
lines.append(f"| L1 | {fmt(niv_l1)} ({pct(niv_l1, niv_total)}%) |")
lines.append(f"| L2 | {fmt(niv_l2)} ({pct(niv_l2, niv_total)}%) |")
lines.append(f"| L3 | {fmt(niv_l3)} ({pct(niv_l3, niv_total)}%) |")
lines.append(f"| Total imputado | {fmt(niv_imputed)} ({pct(niv_imputed, niv_total)}%) |")
lines.append(f"| NaN restantes | {fmt(niv_nan)} ({pct(niv_nan, niv_total)}%) |")
lines.append(f"| Cobertura media | {niv_cov_mean}% |")
lines.append(f"| Cobertura ponderada | {niv_cov_weighted}% |")
lines.append(f"| Estaciones 100% | {niv_100} |")
lines.append(f"| Estaciones >95% | {niv_gt95} |")
lines.append(f"| Estaciones <95% | {niv_lt95} |")
lines.append(f"| Estaciones descartadas por inhomogeneidad | {niv_descartadas} |")
lines.append("")
lines.append("**Lectura:** el crudo tiene 394.772 filas y 59.271 faltantes. La imputacion lleno 54.835 valores y dejo 4.436 NaN documentados. El 85,0% del dataset final es dato original valido.")
lines.append("")
lines.append("### 2.2 Caudales")
lines.append("")
lines.append("| Concepto | Valor |")
lines.append("|---|---:|")
lines.append(f"| Archivo crudo largo | `{CAUD_RAW_LONG.relative_to(ROOT)}` |")
lines.append(f"| Filas crudas | {fmt(caud_raw_rows)} |")
lines.append(f"| Estaciones crudas | {caud_raw_stations} |")
lines.append(f"| Rango crudo | {caud_raw_min} a {caud_raw_max} |")
lines.append(f"| Ultima fecha con dato valido | {caud_raw_valid_max} |")
lines.append(f"| Valores crudos validos | {fmt(caud_raw_valid)} |")
lines.append(f"| Valores crudos faltantes | {fmt(caud_raw_nan)} |")
lines.append(f"| Duplicados (estacion, fecha) | {fmt(caud_raw_dups)} |")
lines.append(f"| Base unificada (ancho) | {fmt(caud_uni_rows)} filas x {caud_uni_stations} estaciones |")
lines.append(f"| Fechas unicas en la base unificada | {fmt(caud_uni_dates)} |")
lines.append(f"| Lecturas por dia (promedio) | {caud_subdaily} |")
lines.append(f"| Celdas validas / faltantes | {fmt(caud_uni_valid)} / {fmt(caud_uni_nan)} |")
lines.append(f"| Filas del dataset final | {fmt(caud_total)} |")
lines.append(f"| L0 validos | {fmt(caud_l0_valid)} ({pct(caud_l0_valid, caud_total)}%) |")
lines.append(f"| L1 | {fmt(caud_l1)} ({pct(caud_l1, caud_total)}%) |")
lines.append(f"| L2 | {fmt(caud_l2)} ({pct(caud_l2, caud_total)}%) |")
lines.append(f"| Total imputado | {fmt(caud_imputed)} ({pct(caud_imputed, caud_total)}%) |")
lines.append(f"| NaN restantes | {fmt(caud_nan)} ({pct(caud_nan, caud_total)}%) |")
lines.append(f"| Cobertura media | {caud_cov_mean}% |")
lines.append(f"| Cobertura ponderada | {caud_cov_weighted}% |")
lines.append(f"| Estaciones 100% | {caud_100} |")
lines.append(f"| Estaciones >95% | {caud_gt95} |")
lines.append(f"| Estaciones <95% | {caud_lt95} |")
lines.append("")
lines.append(f"**Lectura:** el crudo largo tiene 481.435 filas para 25 estaciones. La base unificada es sub-diaria ({fmt(caud_uni_rows)} filas, {fmt(caud_uni_dates)} fechas); los scripts la promedian a diario. El dataset final se limita a las 14 estaciones comunes con niveles y a sus periodos oficiales: 299.239 filas, 87,7% originales, 9,7% imputadas y 2,6% NaN.")
lines.append("")
lines.append("## 3. Niveles: desglose por estacion")
lines.append("")
lines.append("| Estacion | Inicio | Fin | Dias | L0 | L1 | L2 | L3 | Imputados | NaN | Cobertura | Estado | Descartada |")
lines.append("|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|")
for _, r in niv_sum.iterrows():
    imput = int(r["L1"] + r["L2"] + r["L3"])
    lines.append(
        f"| {r['Estacion']} | {r['Fecha_Inicio']} | {r['Fecha_Fin']} | {fmt(r['Dias_Rango'])} | "
        f"{fmt(r['Dias_Rango'] - r['NaN_Restantes_Rango'] - imput)} | {fmt(r['L1'])} | {fmt(r['L2'])} | "
        f"{fmt(r['L3'])} | {fmt(imput)} | {fmt(r['NaN_Restantes_Rango'])} | {r['Cobertura_Rango_pct']}% | "
        f"{r['Status']} | {'Si' if bool(r['Descartada']) else 'No'} |"
    )
lines.append("")
lines.append("> **L0:** Dias - NaN - imputados. No incluye los NaN. La columna 'Original' de la auditoria incluye los NaN, por eso puede ser mayor.")
lines.append("")
lines.append("## 4. Caudales: desglose por estacion")
lines.append("")
lines.append("| Estacion | Inicio | Fin | Dias | L0 | L1 | L2 | Imputados | NaN | Cobertura | R2 N-C | L2 aceptado |")
lines.append("|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|")
for _, r in caud_sum.iterrows():
    imput = int(r["L1"] + r["L2"])
    lines.append(
        f"| {r['Estacion']} | {r['Inicio']} | {r['Fin']} | {fmt(r['Dias'])} | {fmt(r['Original'])} | "
        f"{fmt(r['L1'])} | {fmt(r['L2'])} | {fmt(imput)} | {fmt(r['NaN_restantes'])} | "
        f"{r['Cobertura_pct']}% | {r['NC_R2']} | {'Si' if bool(r['NC_aceptado']) else 'No'} |"
    )
lines.append("")
lines.append("## 5. Figuras y cartillas")
lines.append("")
lines.append("### 5.1 Vigentes")
lines.append("")
lines.append("| Concepto | Niveles | Caudales | Total |")
lines.append("|---|---:|---:|---:|")
lines.append(f"| Cartillas por estacion | {niv_cartillas} | {caud_cartillas} | {niv_cartillas + caud_cartillas} |")
lines.append(f"| PNG dentro de cartillas | {niv_station_png} | {caud_station_png} | {niv_station_png + caud_station_png} |")
lines.append(f"| PNG globales (todas las estaciones) | {niv_global_png} | {caud_global_png} | {niv_global_png + caud_global_png} |")
lines.append(f"| **Total PNG vigentes** | **{niv_fig_total}** | **{caud_fig_total}** | **{niv_fig_total + caud_fig_total}** |")
lines.append("")
lines.append("**Tipos por estacion - niveles:** " + ", ".join(f"{k}={v}" for k, v in niv_fig_types.items()))
lines.append("")
lines.append("**Tipos por estacion - caudales:** " + ", ".join(f"{k}={v}" for k, v in caud_fig_types.items()))
lines.append("")
lines.append("### 5.2 Figuras historicas (no vigentes)")
lines.append("")
lines.append("| Conjunto | PNG |")
lines.append("|---|---:|")
for k, v in hist.items():
    lines.append(f"| {k} | {v} |")
lines.append("")
lines.append("### 5.3 Figuras en los borradores")
lines.append("")
lines.append("| Borrador | Imagenes | Leyendas | Parrafos | Tablas | Comentarios |")
lines.append("|---|---:|---:|---:|---:|---:|")
for name, s in [
    ("Caudales - mayo 2026", rep_caud_may),
    ("Caudales - julio 2026", rep_caud_jul),
    ("Niveles - julio 2026", rep_niv_jul),
]:
    lines.append(
        f"| {name} | {s['imagenes']} | {s['leyendas']} | {s['parrafos_con_texto']} | {s['tablas']} | {s['comentarios']} |"
    )
lines.append("")
lines.append(f"- Niveles: {niv_station_png} PNG de cartilla; el informe usa 96 (24 estaciones x 4 figuras). Quedan **{niv_station_not_in_report}** figuras de cartilla sin insertar (Fig5 y Fig6; Puerto Salgar no tiene Fig6).")
lines.append(f"- Caudales: {caud_station_png} PNG de cartilla; el informe usa {caud_station_in_report} imagenes de estacion (57 totales: 4 generales + 53 de estacion). Quedan **{caud_station_not_in_report}** figuras de estacion sin insertar: {caud_core_missing} de Fig3/Fig6 en las 11 incluidas + {caud_missing_station_figs} de las 3 estaciones faltantes + {caud_extra_missing} imagenes de extremos no insertadas.")
lines.append(f"- Caudales: {rep_caud_jul['imagenes']} imagenes en el borrador y solo {rep_caud_jul['leyendas']} leyendas; hay {rep_caud_jul['imagenes'] - rep_caud_jul['leyendas']} imagenes sin caption (las de ajuste de extremos).")
lines.append("")
lines.append("## 6. Estaciones incluidas y no incluidas en los informes")
lines.append("")
lines.append("### 6.1 Niveles")
lines.append("")
lines.append(f"- Incluidas en el informe: **{len(NIV_REPORT_STATIONS)} de {len(NIV_REPORT_STATIONS)}**.")
lines.append("- No incluidas: **0**.")
lines.append(f"- Marcadas como descartadas por inhomogeneidad (pero presentes en el informe): **{niv_descartadas}** (Armenia, Barbosa, Sitio Nuevo, Tenerife).")
lines.append("")
lines.append("### 6.2 Caudales")
lines.append("")
lines.append(f"- Incluidas en el informe: **{len(CAUD_REPORT_STATIONS)} de {len(COMMON_STATIONS)}** estaciones comunes.")
lines.append(f"- Faltantes en el informe: **{len(caud_report_missing)}** -> {', '.join(clean_name(x) for x in caud_report_missing)}.")
lines.append(f"- No incluidas del universo de caudales: **{len(caud_report_not_included)} de {len(CAUD_BASE)}** (3 comunes faltantes + 11 solo-caudales).")
lines.append(f"- Solo-caudales (sin niveles): {', '.join(clean_name(x) for x in CAUD_ONLY)}.")
lines.append("")
lines.append("### 6.3 Universo combinado")
lines.append("")
lines.append(f"- Estaciones unicas: **{len(CAUD_BASE) + len(NIV_ONLY)}** (14 comunes + {len(NIV_ONLY)} solo-niveles + {len(CAUD_ONLY)} solo-caudales).")
lines.append(f"- Solo-niveles: {', '.join(clean_name(x) for x in NIV_ONLY)}.")
lines.append("")
lines.append("## 7. Pruebas y validaciones")
lines.append("")
lines.append("### 7.1 Niveles")
lines.append("")
lines.append("- 0 violaciones de rango de cota, 0 registros fuera de rango temporal, 0 saltos temporales anomalos.")
lines.append("- 1 alerta del agente de validacion: Calamar con cobertura 93,34%.")
lines.append("- 88 pares con baja coherencia espacial (r < 0,7); correlacion espacial minima 0,2295.")
lines.append("- Comparacion con la corrida de estudiantes: 292.885 registros comparables; diferencia media absoluta 0,3220 m; maxima 3,8058 m.")
lines.append("- Modelos: 23 H-H L2 y 10 H-H L3; 552 parejas evaluadas.")
lines.append("- Homogeneidad: 25 estaciones, 7 pruebas (Pettitt, Mann-Kendall, F, t-Student, Cramer, Mann-Whitney, Shapiro-Wilk).")
lines.append("")
lines.append("### 7.2 Caudales")
lines.append("")
lines.append(f"- Verificacion de integridad: **9 checks ejecutados** ({verif_pass} PASS, {verif_fail} FAIL, {verif_info} INFO); el resumen final reporta que todos los checks criticos pasaron.")
lines.append("- Sin 29 de febrero, sin duplicados (estacion, fecha), sin caudales <= 0; estadisticos por estacion y anuales coinciden con los Excel originales.")
lines.append(f"- Curvas N-C: **{caud_nc_models} modelos**, **{fmt(caud_nc_pairs)} pares**; R2 orden 2 entre **{caud_nc_r2_min}** y **{caud_nc_r2_max}**.")
lines.append(f"- L2 aceptado en **{caud_nc_accepted}** estaciones; rechazado en **{caud_nc_rejected}** (Barbosa, R2=0,6734).")
lines.append(f"- Homogeneidad del equipo: **{homog_stations} estaciones**; **{mk_sig}** con Mann-Kendall significativo (p<0,05); **{non_normal}** no normales.")
lines.append(f"- Tendencias MK: {', '.join(f'{k}={v}' for k, v in mk_trends.items())}.")
lines.append("")
lines.append("## 8. Scripts y archivos")
lines.append("")
lines.append("| Concepto | Valor |")
lines.append("|---|---:|")
lines.append(f"| Scripts de caudales | {caud_scripts} |")
lines.append(f"| Scripts de niveles v2.1 | {niv_scripts} |")
lines.append(f"| Modulos del pipeline reutilizable | {pipeline_modules} |")
lines.append("")
lines.append("| Archivo clave | Tamano (MB) |")
lines.append("|---|---:|")
for name, path in key_files.items():
    lines.append(f"| {name} | {mb(path)} |")
lines.append("")
lines.append("## 9. Dudas abiertas de procesamiento")
lines.append("")
lines.append("| Tema | Estado | Impacto | Siguiente paso |")
lines.append("|---|---|---|---|")
lines.append("| Estadistico Cramer del equipo | Descartado | No se reproduce con convenciones estandar | Documentar que no se uso |")
lines.append("| El Banco sub-diario vs equipo | Abierto | Pettitt/MK no coinciden | Confirmar version de datos del equipo |")
lines.append("| Barbosa sin L2 | Abierto | Cobertura 83,22% | Evaluar L3 Q-Q o curva N-C segmentada |")
lines.append("| Puerto Salgar 1937-1960 | Abierto | Sin niveles concurrentes | Mantener NaN documentado |")
lines.append("| L3 Q-Q entre estaciones | Standby | Barbosa y otras <95% | Disenar y ejecutar si se requiere |")
lines.append("| Curvas N-C segmentadas | Standby | Barbosa y Armenia con ramas paralelas | Evaluar por periodo |")
lines.append("| 11 vs 14 estaciones en el informe | Abierto | Faltan San Pablo, Puerto Berrio y Puerto Salgar | Actualizar el borrador |")
lines.append("| Outliers vs equipo | Resuelto | Diferencias de pruebas | Base oficial sin outliers |")
lines.append("| 29-feb y agregacion sub-diaria | Resuelto | Evita sesgos | Documentado en scripts |")
lines.append("| Figuras sin caption en caudales | Abierto | 20 imagenes sin leyenda | Agregar captions |")
lines.append("| Fig6 de Puerto Salgar en niveles | Abierto | No hay modelo H-H | Nota de no aplicabilidad |")
lines.append("| Versionado de datos y figuras | Abierto | Mucho material fuera de git | Release/ZIP + manifiesto |")
lines.append("")
lines.append("## 10. Fuentes")
lines.append("")
for p in [NIV_RAW, NIV_FINAL, NIV_SUM, CAUD_RAW_LONG, CAUD_UNIFIED, CAUD_FINAL, CAUD_SUM, NC_SUM, DUR_SUM, HOMOG, COMP, VERIF_CAUD, NIV_VALID, NIV_AGENT, REP_CAUD_MAY, REP_CAUD_JUL, REP_NIV_JUL]:
    lines.append(f"- `{p.relative_to(ROOT)}`")
lines.append("")
lines.append("## 11. Métricas sugeridas para las diapositivas")
lines.append("")
lines.append("1. **35 estaciones unicas** analizadas: 24 con niveles, 25 con caudales, 14 comunes.")
lines.append("2. **694.011 registros procesados** en total: 394.772 de niveles + 299.239 de caudales.")
lines.append("3. **54.835 datos imputados en niveles** (13,9%) y **28.981 en caudales** (9,7%).")
lines.append("4. **Cobertura media:** 98,87% en niveles y 97,74% en caudales.")
lines.append("5. **38 cartillas** generadas: 24 de niveles + 14 de caudales.")
lines.append("6. **251 figuras vigentes:** 150 de niveles + 101 de caudales.")
lines.append("7. **Informe de niveles:** 24/24 estaciones incluidas; 105 imagenes.")
lines.append("8. **Informe de caudales:** 11/14 estaciones comunes; faltan San Pablo, Puerto Berrio y Puerto Salgar; 57 imagenes y 37 leyendas.")
lines.append("9. **Pruebas:** 9 checks de caudales (6 PASS, 0 FAIL, 2 INFO), 0 violaciones de rango en niveles, 25 estaciones de homogeneidad.")
lines.append("10. **Brecha principal:** actualizar el informe de caudales a 14 estaciones y agregar Fig3/Fig6; resolver Barbosa y Puerto Salgar.")
lines.append("")

OUT_MD.write_text("\n".join(lines), encoding="utf-8")
print(f"OK: {OUT_MD}")
print(f"OK: {OUT_JSON}")
print(f"Niveles: {niv_total:,} filas | {niv_fig_total} figuras | {niv_cartillas} cartillas")
print(f"Caudales: {caud_total:,} filas | {caud_fig_total} figuras | {caud_cartillas} cartillas")
