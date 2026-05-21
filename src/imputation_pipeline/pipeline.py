"""
Orquestador principal del pipeline de imputacion.
Ejecuta todo el flujo: carga -> HH -> L1 -> L2 -> hard rules -> tracking -> guardado.

NOTA: Este modulo NO incluye L3 (missForest). El pipeline se limita a:
      L1 = interpolacion local (gaps <= 3 dias)
      L2 = curvas H-H cuadraticas auto-descubiertas
"""

import pandas as pd
from pathlib import Path

from .config import DESCARTADAS
from .loaders import load_raw_data, to_wide_format, get_station_list
from .hh_selector import run_hh_discovery
from .imputers import apply_l1_interpolation, apply_l2_hh_imputation
from .hard_rules import compute_original_ranges, apply_hard_rule_clip, verify_no_outliers
from .tracker import build_tracked_dataset


def run_pipeline(data_path, output_dir, date_format=None):
    """
    Ejecuta el pipeline completo de imputacion.

    Parametros:
        data_path : str o Path
            Ruta al CSV con datos crudos (formato long: station, level, date)
        output_dir : str o Path
            Carpeta donde se guardaran los resultados
        date_format : str, opcional
            Formato de fecha. Por defecto '%d-%m-%Y'

    Salidas generadas en output_dir:
        - Datos_Imputados.csv          : Dataset long final con tracking
        - Tabla_Modelos_HH.csv         : Todos los modelos H-H evaluados
        - Tabla_Modelos_HH_Seleccionados.csv : Modelos H-H que pasaron el umbral
        - Resumen_Imputacion.csv       : Estadisticas por estacion
        - log_pipeline.txt             : Log de ejecucion
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    log_lines = []

    def log(msg):
        print(msg)
        log_lines.append(msg)

    # ============================================================
    # [1] CARGA
    # ============================================================
    log("=" * 70)
    log("PIPELINE DE IMPUTACION v2.0 (L1 + L2, sin missForest)")
    log("=" * 70)
    log(f"\n[1/6] Cargando datos crudos desde: {data_path}")

    df_long = load_raw_data(data_path, date_format=date_format)
    log(f"       Registros cargados: {len(df_long):,}")
    log(f"       Estaciones: {df_long['NombreEstacion'].nunique()}")
    log(f"       Periodo: {df_long['Fecha'].min().date()} a {df_long['Fecha'].max().date()}")

    # ============================================================
    # [2] WIDE + RANGOS ORIGINALES
    # ============================================================
    log("\n[2/6] Pivotando a formato wide y calculando rangos originales...")
    df_wide_orig = to_wide_format(df_long)
    log(f"       Fechas: {len(df_wide_orig):,}, Estaciones: {len(df_wide_orig.columns)}")

    rangos_originales = compute_original_ranges(df_long)
    for est, (rmin, rmax) in sorted(rangos_originales.items()):
        log(f"       {est:<18} rango=[{rmin:>8.3f}, {rmax:>8.3f}]")

    # ============================================================
    # [3] DESCUBRIR Y SELECCIONAR MODELOS H-H
    # ============================================================
    log("\n[3/6] Descubriendo y seleccionando modelos H-H...")
    modelos_hh, df_todas_hh = run_hh_discovery(df_long)

    # Guardar tabla completa de HH
    df_todas_hh.to_csv(output_dir / 'Tabla_Modelos_HH.csv', index=False)
    log(f"       Guardado: Tabla_Modelos_HH.csv ({len(df_todas_hh)} parejas)")

    # Guardar tabla de seleccionados
    if modelos_hh:
        df_sel = pd.DataFrame(modelos_hh)
        df_sel.to_csv(output_dir / 'Tabla_Modelos_HH_Seleccionados.csv', index=False)
        log(f"       Guardado: Tabla_Modelos_HH_Seleccionados.csv ({len(df_sel)} modelos)")

    # ============================================================
    # [4] L1 - INTERPOLACION LOCAL
    # ============================================================
    log("\n[4/6] Aplicando L1 - Interpolacion local...")
    df_wide_l1 = df_wide_orig.copy()
    l1_counts = {}
    for col in df_wide_l1.columns:
        s_imp, mask = apply_l1_interpolation(df_wide_l1[col])
        df_wide_l1[col] = s_imp
        l1_counts[col] = mask.sum()
    total_l1 = sum(l1_counts.values())
    log(f"       Total imputados L1: {total_l1:,}")

    # ============================================================
    # [5] L2 - H-H CUADRATICA
    # ============================================================
    log("\n[5/6] Aplicando L2 - Curvas H-H cuadraticas...")
    df_wide_l2 = df_wide_l1.copy()
    l2_counts = {}
    for model in modelos_hh:
        n = apply_l2_hh_imputation(df_wide_l2, model)
        l2_counts[model['objetivo']] = n
        if n > 0:
            log(f"       {model['objetivo']:<18} <- {model['donante']:<18} : {n:>4} valores")
    total_l2 = sum(l2_counts.values())
    log(f"       Total imputados L2: {total_l2:,}")

    # ============================================================
    # [6] HARD RULES + TRACKING + GUARDADO
    # ============================================================
    log("\n[6/6] Hard rules, tracking y guardado...")
    clipped = apply_hard_rule_clip(df_wide_l2, rangos_originales)
    if clipped:
        log(f"       Valores clipeados:")
        for est, n in sorted(clipped.items()):
            log(f"       {est:<18} : {n:>4} valores")
    else:
        log("       Ningun valor requirio clip (todos dentro de rango)")

    violations = verify_no_outliers(df_wide_l2, rangos_originales)
    if violations:
        log(f"       [ALERTA] {len(violations)} violaciones detectadas post-hard-rule!")
    else:
        log("       [OK] Sin violaciones de rango")

    # Tracking
    df_long_final = build_tracked_dataset(
        df_wide_final=df_wide_l2,
        df_wide_orig=df_wide_orig,
        df_wide_after_l1=df_wide_l1,
    )

    output_file = output_dir / 'Datos_Imputados.csv'
    df_long_final.to_csv(output_file, index=False)
    log(f"       Guardado: {output_file.name} ({len(df_long_final):,} registros)")

    # Resumen por estacion
    resumen = []
    for col in df_wide_l2.columns:
        n_total = len(df_wide_l2[col])
        n_nan = df_wide_l2[col].isna().sum()
        is_desc = col in DESCARTADAS
        resumen.append({
            'Estacion': col,
            'Total': n_total,
            'NaN_Restantes': n_nan,
            'Cobertura_pct': round((n_total - n_nan) / n_total * 100, 2),
            'L1': l1_counts.get(col, 0),
            'L2': l2_counts.get(col, 0),
            'Descartada': is_desc,
            'Status': 'OK' if (n_nan == 0 or is_desc) else 'INCOMPLETA',
        })
    df_resumen = pd.DataFrame(resumen)
    df_resumen.to_csv(output_dir / 'Resumen_Imputacion.csv', index=False)
    log(f"       Guardado: Resumen_Imputacion.csv")

    # Log
    log_file = output_dir / 'log_pipeline.txt'
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(log_lines) + '\n')

    # ============================================================
    # RESUMEN FINAL
    # ============================================================
    log("\n" + "=" * 70)
    log("PIPELINE COMPLETADO")
    log("=" * 70)
    log(f"Dataset final      : {len(df_long_final):,} registros")
    log(f"Modelos H-H        : {len(modelos_hh)} seleccionados")
    log(f"Imputados L1       : {total_l1:,}")
    log(f"Imputados L2       : {total_l2:,}")
    log(f"Total imputados    : {total_l1 + total_l2:,}")
    log(f"Output             : {output_dir}")

    no_desc = df_resumen[~df_resumen['Descartada']]
    incompletas = no_desc[no_desc['Status'] == 'INCOMPLETA']
    if len(incompletas) == 0:
        log("[EXITO] Todas las estaciones no descartadas tienen cobertura 100%!")
    else:
        log(f"[ALERTA] {len(incompletas)} estaciones incompletas:")
        for _, row in incompletas.iterrows():
            log(f"         - {row['Estacion']}: {row['NaN_Restantes']} NaN")

    return df_long_final, df_resumen
