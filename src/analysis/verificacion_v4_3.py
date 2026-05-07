"""
VERIFICACION ANTI DATA-LEAKAGE - Sistema de Imputacion v4.3
============================================================
"""

import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# CONFIGURACION
# ============================================================
ORIG_PATH = r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\backend\data\processed\Resumen_Crudos_IDEAM_2026.csv'
V43_PATH = r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\backend\data\processed\imputation\Datos_Imputados_v4_3_Corrected.csv'
V42_PATH = r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\backend\data\processed\imputation\Datos_Imputados_v4_2_Complete.csv'
MODELS_PATH = r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\backend\data\processed\imputation\Tabla_Modelos_HH_v4_3.csv'
REPORT_PATH = r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\docs\REPORTE_VERIFICACION_v4_3.md'

GEO_ORDER = {
    'San Pedrito': 0, 'Calamar': 1, 'Tenerife': 2, 'Plato': 3, 'Magangue': 4,
    'Barbosa': 5, 'Coyongal': 6, 'Armenia': 7, 'Rio Nuevo': 8, 'Las Palomas': 9,
    'Las Aguadas': 10, 'El Banco': 11, 'Penoncito': 12, 'La Gloria': 13,
    'Gamarra Aut': 14, 'El Contento': 15, 'Sitio Nuevo': 16, 'Puerto Wilches': 17,
}
DESCARTADAS = ['Armenia', 'Tenerife', 'Barbosa', 'Sitio Nuevo']

report_lines = []
def log(msg):
    print(msg)
    report_lines.append(msg)

def normalize_name(name):
    """Convierte nombres como 'MAGANGUE' -> 'Magangue'"""
    name_map_upper = {k.upper(): k for k in GEO_ORDER.keys()}
    return name_map_upper.get(name.upper(), name)

def to_upper_name(name):
    """Convierte nombres como 'Magangue' -> 'MAGANGUE'"""
    return name.upper().replace(' ', '_')

# ============================================================
# CHECK #1: Inmutabilidad de datos originales
# ============================================================
log("\n" + "="*80)
log("CHECK #1: Inmutabilidad de datos originales")
log("="*80)

orig = pd.read_csv(ORIG_PATH)
orig['date'] = pd.to_datetime(orig['date'], format='%d-%m-%Y')
orig = orig.rename(columns={'station': 'NombreEstacion', 'level': 'Cota', 'date': 'Fecha'})

v43 = pd.read_csv(V43_PATH)
v43['Fecha'] = pd.to_datetime(v43['Fecha'])

merged = orig.merge(v43, on=['NombreEstacion', 'Fecha'], how='inner')
diff = np.abs(merged['Cota_x'] - merged['Cota_y'])
mismatches = merged[diff > 1e-6]

if len(mismatches) == 0:
    log("[PASS] Todos los valores originales coinciden exactamente con v4.3")
else:
    log(f"[FAIL] {len(mismatches)} valores originales fueron modificados en v4.3")

# ============================================================
# CHECK #2: Hard rule (no imputacion fuera de rango)
# ============================================================
log("\n" + "="*80)
log("CHECK #2: Hard rule - No imputacion fuera de rango original")
log("="*80)

rangos = orig.groupby('NombreEstacion')['Fecha'].agg(['min', 'max'])
violaciones = []
for est in v43['NombreEstacion'].unique():
    subset = v43[v43['NombreEstacion'] == est]
    rmin, rmax = rangos.loc[est]
    fuera = subset[(subset['Fecha'] < rmin) | (subset['Fecha'] > rmax)]
    if len(fuera) > 0:
        violaciones.append(f"{est}: {len(fuera)} registros fuera de rango")

if len(violaciones) == 0:
    log("[PASS] 0 registros fuera del rango original")
else:
    for v in violaciones:
        log(f"[FAIL] {v}")

# ============================================================
# CHECK #3: Orientacion H-H correcta
# ============================================================
log("\n" + "="*80)
log("CHECK #3: Orientacion H-H correcta (independiente aguas arriba)")
log("="*80)

models = pd.read_csv(MODELS_PATH)
violaciones_orient = []
for _, row in models.iterrows():
    dep = normalize_name(row['Recipiente'])
    ind = normalize_name(row['Independiente'])
    if dep not in GEO_ORDER or ind not in GEO_ORDER:
        continue
    if GEO_ORDER[ind] <= GEO_ORDER[dep]:
        violaciones_orient.append(f"{dep} <- {ind}: independiente esta aguas ABAJO")

if len(violaciones_orient) == 0:
    log("[PASS] Todos los modelos H-H respetan orientacion hidrologica")
else:
    for v in violaciones_orient:
        log(f"[FAIL] {v}")

# ============================================================
# CHECK #4: Coherencia fisica de valores imputados
# ============================================================
log("\n" + "="*80)
log("CHECK #4: Coherencia fisica de valores imputados")
log("="*80)

pct_orig = orig.groupby('NombreEstacion')['Cota'].quantile([0.01, 0.99]).unstack()
pct_orig.columns = ['p01', 'p99']

alertas_fisicas = []
for est in v43['NombreEstacion'].unique():
    if est not in pct_orig.index:
        continue
    p01, p99 = pct_orig.loc[est]
    margin = (p99 - p01) * 0.3
    subset = v43[(v43['NombreEstacion'] == est) & (v43['Nivel_Imputacion'] > 0)]
    if len(subset) == 0:
        continue
    outliers = subset[(subset['Cota'] < p01 - margin) | (subset['Cota'] > p99 + margin)]
    pct_out = len(outliers) / len(subset) * 100
    if pct_out > 1.0:
        alertas_fisicas.append(f"{est}: {len(outliers)}/{len(subset)} imputados ({pct_out:.1f}%) fuera de rango esperado")

if len(alertas_fisicas) == 0:
    log("[PASS] Todos los valores imputados dentro de rangos fisicos razonables")
else:
    for a in alertas_fisicas:
        log(f"[WARN] {a}")

# ============================================================
# CHECK #5: Data leakage en entrenamiento
# ============================================================
log("\n" + "="*80)
log("CHECK #5: Data leakage en entrenamiento H-H")
log("="*80)

leakage = []
for _, model in models.iterrows():
    dep_upper = to_upper_name(model['Recipiente'])
    ind_upper = to_upper_name(model['Independiente'])
    n_train = model['N_Entrenamiento']
    
    orig_dep = orig[orig['NombreEstacion'] == dep_upper].dropna(subset=['Cota'])
    orig_ind = orig[orig['NombreEstacion'] == ind_upper].dropna(subset=['Cota'])
    concurrentes = orig_dep.merge(orig_ind, on='Fecha', how='inner')
    n_conc = len(concurrentes)
    
    if n_train > n_conc:
        leakage.append(f"{model['Recipiente']} <- {model['Independiente']}: n_train={n_train} > originales={n_conc}")

if len(leakage) == 0:
    log("[PASS] Todos los modelos fueron entrenados solo con datos originales concurrentes")
else:
    for l in leakage:
        log(f"[FAIL] {l}")

# ============================================================
# CHECK #6: Cobertura 100% en estaciones no descartadas
# ============================================================
log("\n" + "="*80)
log("CHECK #6: Cobertura 100% en estaciones no descartadas")
log("="*80)

incompletas = []
for est in v43['NombreEstacion'].unique():
    if est in DESCARTADAS:
        continue
    n_nan = v43[v43['NombreEstacion'] == est]['Cota'].isna().sum()
    if n_nan > 0:
        incompletas.append(f"{est}: {n_nan} NaN")

if len(incompletas) == 0:
    log("[PASS] Las 14 estaciones no descartadas tienen 0 NaN")
else:
    for i in incompletas:
        log(f"[FAIL] {i}")

# ============================================================
# CHECK #7: Comparacion v4.2 vs v4.3
# ============================================================
log("\n" + "="*80)
log("CHECK #7: Comparacion estadistica v4.2 vs v4.3")
log("="*80)

v42 = pd.read_csv(V42_PATH)
v42['Fecha'] = pd.to_datetime(v42['Fecha'], format='mixed', dayfirst=True)

stats_42 = v42.groupby('NombreEstacion')['Cota'].agg(['mean','std','min','max','count'])
stats_43 = v43.groupby('NombreEstacion')['Cota'].agg(['mean','std','min','max','count'])

comparacion = []
for est in stats_43.index:
    if est not in stats_42.index:
        continue
    m42 = stats_42.loc[est, 'mean']
    m43 = stats_43.loc[est, 'mean']
    cambio_pct = abs((m43 - m42) / m42 * 100) if m42 != 0 else 0
    comparacion.append((est, cambio_pct))
    
    status = "PASS" if cambio_pct < 5.0 else "WARN"
    log(f"  [{status}] {est:<18} media v4.2={m42:.3f}  media v4.3={m43:.3f}  cambio={cambio_pct:.2f}%")

# ============================================================
# CHECK #8: Continuidad de serie de tiempo (sin saltos bruscos)
# ============================================================
log("\n" + "="*80)
log("CHECK #8: Continuidad de serie de tiempo (deteccion de saltos bruscos)")
log("="*80)

saltos_detectados = []
for est in v43['NombreEstacion'].unique():
    subset = v43[v43['NombreEstacion'] == est].sort_values('Fecha').reset_index(drop=True)
    if len(subset) < 3:
        continue
    
    subset['diff'] = subset['Cota'].diff().abs()
    
    # Calcular percentil 99 de diferencias en datos originales
    orig_diff = subset[subset['Nivel_Imputacion'] == 0]['diff'].dropna()
    if len(orig_diff) < 10:
        continue
    p99_diff = orig_diff.quantile(0.99)
    
    # Verificar saltos en fechas de imputacion
    imputados = subset[subset['Nivel_Imputacion'] > 0]
    for _, row in imputados.iterrows():
        idx = row.name
        if idx == 0 or idx >= len(subset) - 1:
            continue
        diff_prev = subset.loc[idx, 'diff']
        diff_next = subset.loc[idx + 1, 'diff'] if idx + 1 < len(subset) else 0
        if diff_prev > 2 * p99_diff or diff_next > 2 * p99_diff:
            saltos_detectados.append(f"{est} @ {row['Fecha'].strftime('%Y-%m-%d')}: salto={diff_prev:.2f}m (p99_orig={p99_diff:.2f}m)")
            if len(saltos_detectados) >= 20:
                break

if len(saltos_detectados) == 0:
    log("[PASS] Ningun valor imputado genera saltos bruscos en la serie de tiempo")
else:
    log(f"[WARN] {len(saltos_detectados)} saltos bruscos detectados:")
    for s in saltos_detectados[:10]:
        log(f"       {s}")
    if len(saltos_detectados) > 10:
        log(f"       ... y {len(saltos_detectados)-10} mas")

# ============================================================
# CHECK #9: Autocorrelacion de residuos de imputacion
# ============================================================
log("\n" + "="*80)
log("CHECK #9: Autocorrelacion de residuos de imputacion")
log("="*80)

autocorr_issues = []
for _, model in models.iterrows():
    dep_upper = to_upper_name(model['Recipiente'])
    ind_upper = to_upper_name(model['Independiente'])
    
    orig_dep = orig[orig['NombreEstacion'] == dep_upper][['Fecha', 'Cota']].rename(columns={'Cota': 'dep'})
    orig_ind = orig[orig['NombreEstacion'] == ind_upper][['Fecha', 'Cota']].rename(columns={'Cota': 'ind'})
    conc = pd.merge(orig_dep, orig_ind, on='Fecha').dropna()
    
    if len(conc) < 100:
        continue
    
    a, b, c = model['a'], model['b'], model['c']
    pred = a * conc['ind']**2 + b * conc['ind'] + c
    residuos = conc['dep'] - pred
    
    autocorr = residuos.autocorr(lag=1)
    if abs(autocorr) > 0.3:
        autocorr_issues.append(f"{model['Recipiente']} <- {model['Independiente']}: autocorr lag-1 = {autocorr:.3f} (posible patron sistematico)")

if len(autocorr_issues) == 0:
    log("[PASS] Residuos de modelos H-H sin autocorrelacion significativa")
else:
    for a in autocorr_issues:
        log(f"[WARN] {a}")

# ============================================================
# RESUMEN FINAL
# ============================================================
log("\n" + "="*80)
log("RESUMEN FINAL DE VERIFICACION")
log("="*80)

pass_count = sum(1 for line in report_lines if '[PASS]' in line)
warn_count = sum(1 for line in report_lines if '[WARN]' in line)
fail_count = sum(1 for line in report_lines if '[FAIL]' in line)

log(f"\nChecks PASS:   {pass_count}")
log(f"Checks WARN:   {warn_count}")
log(f"Checks FAIL:   {fail_count}")

if fail_count == 0:
    log("\n[EXITO] Sistema v4.3 APROBADO para uso en analisis hidrologicos.")
else:
    log("\n[ALERTA] Sistema v4.3 requiere correcciones antes de su uso.")

# Guardar reporte
with open(REPORT_PATH, 'w', encoding='utf-8') as f:
    f.write("# Reporte de Verificacion - Sistema de Imputacion v4.3\n\n")
    f.write(f"**Fecha:** 2026-05-07\n")
    f.write(f"**Dataset:** Datos_Imputados_v4_3_Corrected.csv\n")
    f.write(f"**Total registros:** {len(v43):,}\n\n")
    f.write("## Resultados\n\n")
    for line in report_lines:
        f.write(line + "\n")
    f.write("\n## Conclusion\n\n")
    if fail_count == 0:
        f.write("El sistema v4.3 ha superado todas las verificaciones criticas y esta aprobado para su uso en analisis hidrologicos del Rio Magdalena.\n")
    else:
        f.write(f"Se detectaron {fail_count} fallos criticos que deben corregirse antes de aprobar el sistema v4.3.\n")

log(f"\nReporte guardado: {REPORT_PATH}")
