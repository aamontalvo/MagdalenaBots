#!/usr/bin/env python3
"""
10_publish_figures_repo.py
==========================

Copia las 251 figuras a cartillas_estaciones/figuras_publicas/ y actualiza
figuras.csv con URLs raw de GitHub para Softr.

Uso:
  py backend/scripts/caudales_v1/10_publish_figures_repo.py

Variables:
  REPO_BRANCH=main (por defecto)
  REPO_SLUG=aamontalvo/MagdalenaBots (por defecto)
"""

import hashlib
import os
import shutil
import sys
from pathlib import Path
from urllib.parse import quote

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "backend" / "entregables" / "softr_import"
PUBLIC = ROOT / "cartillas_estaciones" / "figuras_publicas" / "figures"
REPO_SLUG = os.environ.get("REPO_SLUG", "aamontalvo/MagdalenaBots")
BRANCH = os.environ.get("REPO_BRANCH", "main")
RAW_BASE = f"https://raw.githubusercontent.com/{REPO_SLUG}/{BRANCH}/cartillas_estaciones/figuras_publicas"

figuras = pd.read_csv(BASE / "figuras.csv")
rows = []
for _, row in figuras.iterrows():
    src = ROOT / row["local_path"]
    if not src.exists():
        # Si ya se movió al espejo público, resolver desde allí
        alt = ROOT / row["local_path"].replace(
            "backend/entregables/softr_import/figures_public/",
            "cartillas_estaciones/figuras_publicas/",
        )
        src = alt
    if not src.exists():
        print(f"FALTA: {row['local_path']}")
        continue
    variable = "niveles" if row["variable"] == "Niveles" else "caudales"
    station = row["station_code"] if isinstance(row["station_code"], str) and row["station_code"] else "global"
    dest_dir = PUBLIC / variable / station
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / src.name
    if not dest.exists():
        shutil.copy2(src, dest)

    rel = f"figures/{variable}/{station}/{src.name}"
    repo_path = f"cartillas_estaciones/figuras_publicas/{rel}"
    rows.append({
        **row.to_dict(),
        "image_url": f"{RAW_BASE}/{quote(rel)}",
        "local_path": repo_path,
    })

out = pd.DataFrame(rows)
out.to_csv(BASE / "figuras.csv", index=False, encoding="utf-8")
print(f"OK figuras.csv actualizado ({len(out)} filas)")
print(f"Base URL: {RAW_BASE}")

# Actualizar hash del manifiesto en datasets.csv
datasets_path = BASE / "datasets.csv"
if datasets_path.exists():
    datasets = pd.read_csv(datasets_path)
    h = hashlib.sha256((BASE / "figuras.csv").read_bytes()).hexdigest()
    datasets.loc[datasets["dataset_id"] == "figures_manifest_v1", "sha256"] = h
    datasets.to_csv(datasets_path, index=False, encoding="utf-8")
    print("OK datasets.csv actualizado")

print(f"PNG en espejo: {len(list(PUBLIC.rglob('*.png')))}")
