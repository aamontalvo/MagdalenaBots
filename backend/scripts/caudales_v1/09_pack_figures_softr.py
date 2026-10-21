#!/usr/bin/env python3
"""
09_pack_figures_softr.py
========================

Empaqueta las 251 figuras en una carpeta pública con estructura estable y
actualiza figuras.csv para que image_url dependa solo de un dominio base.

Salida:
- backend/entregables/softr_import/figures_public/figures/...
- backend/entregables/softr_import/figures_public.zip
- backend/entregables/softr_import/figuras.csv (URLs actualizadas)
- backend/entregables/softr_import/datasets.csv (hash de figuras.csv actualizado)

Uso:
  set SOFTR_FIGURE_BASE_URL=https://midominio.com
  py backend/scripts/caudales_v1/09_pack_figures_softr.py
"""

import hashlib
import os
import shutil
import sys
import zipfile
from pathlib import Path
from urllib.parse import quote

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "backend" / "entregables" / "softr_import"
PUBLIC = BASE / "figures_public"
PUBLIC_FIG = PUBLIC / "figures"
URL_BASE = os.environ.get("SOFTR_FIGURE_BASE_URL", "https://PENDING_HOST").rstrip("/")
ZIP_PATH = BASE / "figures_public.zip"

figuras = pd.read_csv(BASE / "figuras.csv")

for _, row in figuras.iterrows():
    src = ROOT / row["local_path"]
    if not src.exists():
        print(f"FALTA: {row['local_path']}")
        continue
    variable = "niveles" if row["variable"] == "Niveles" else "caudales"
    station = row["station_code"] if isinstance(row["station_code"], str) and row["station_code"] else "global"
    dest_dir = PUBLIC_FIG / variable / station
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / src.name
    if not dest.exists():
        shutil.copy2(src, dest)

# Actualizar rutas y URLs
new_paths = []
new_urls = []
for _, row in figuras.iterrows():
    variable = "niveles" if row["variable"] == "Niveles" else "caudales"
    station = row["station_code"] if isinstance(row["station_code"], str) and row["station_code"] else "global"
    filename = Path(row["local_path"]).name
    rel = f"figures/{variable}/{station}/{filename}"
    new_paths.append(f"backend/entregables/softr_import/figures_public/{rel}")
    new_urls.append(f"{URL_BASE}/{quote(rel)}")

figuras["local_path"] = new_paths
figuras["image_url"] = new_urls
figuras.to_csv(BASE / "figuras.csv", index=False, encoding="utf-8")
print(f"OK figuras.csv actualizado ({len(figuras)} filas) con base {URL_BASE}")

# Actualizar hash del manifiesto de figuras en datasets.csv
datasets_path = BASE / "datasets.csv"
datasets = pd.read_csv(datasets_path)
h = hashlib.sha256((BASE / "figuras.csv").read_bytes()).hexdigest()
mask = datasets["dataset_id"] == "figures_manifest_v1"
datasets.loc[mask, "sha256"] = h
datasets.to_csv(datasets_path, index=False, encoding="utf-8")
print("OK datasets.csv actualizado con hash de figuras.csv")

# ZIP de la carpeta pública
if ZIP_PATH.exists():
    ZIP_PATH.unlink()
with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for p in PUBLIC.rglob("*"):
        if p.is_file():
            z.write(p, p.relative_to(PUBLIC.parent))
print(f"OK {ZIP_PATH.relative_to(ROOT)} ({ZIP_PATH.stat().st_size/1024/1024:.2f} MB)")

print(f"Figuras copiadas: {len(list(PUBLIC_FIG.rglob('*.png')))}")
