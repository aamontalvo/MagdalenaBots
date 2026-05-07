"""
Imputacion quirurgica de San Pedrito para actualizar v4_2 Complete.

Estrategia:
1. Leer Datos_Imputados_v4_2_Complete.csv y extraer 17 estaciones (sin San Pedrito)
2. Leer datos originales de San Pedrito desde Resumen_Crudos_IDEAM_2026.csv
3. Aplicar Nivel 1: Interpolacion local ponderada para gaps <= 3 dias
4. Aplicar Nivel 2: Curva H-H con Calamar (cuadratico, R2=0.993) para gaps > 3 dias
5. Fusionar y guardar nuevo v4_2 Complete
6. Generar estadisticas y reportes

Hard Rules:
- Solo imputar dentro del rango real de San Pedrito: 01-01-1979 a 31-12-2025
- No extrapolar fuera del rango
- Respetar exclusion de 29-feb
"""

import pandas as pd
import numpy as np
from pathlib import Path
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# CONFIGURACION
# =============================================================================
SOURCE_TRUTH = Path(r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\backend\data\processed\Resumen_Crudos_IDEAM_2026.csv')
V4_2_COMPLETE = Path(r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\backend\data\processed\imputation\Datos_Imputados_v4_2_Complete.csv')
OUTPUT_DIR = Path(r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\backend\data\processed\imputation')
OUTPUT_CSV = OUTPUT_DIR / 'Datos_Imputados_v4_2_Complete.csv'

# Modelo H-H San Pedrito vs Calamar (cuadratico, R2=0.9930)
HH_COEFFS = np.array([0.002688, 0.9607, 0.0664])  # a*H^2 + b*H + c

STATION_CODE = '29047070'
STATION_NAME = 'San Pedrito'
DONOR_CODE = '29037020'
DONOR_NAME = 'Calamar'

# =============================================================================
# FUNCIONES
# =============================================================================

def load_source_truth(station):
    """Lee datos originales de la fuente de la verdad."""
    df = pd.read_csv(SOURCE_TRUTH)
    df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y')
    df_station = df[df['station'] == station].copy().sort_values('date').reset_index(drop=True)
    return df_station[['date', 'level']].copy()


def apply_level1(df_station):
    """
    Aplica interpolacion local ponderada para gaps <= 3 dias.
    Kernel: [-2:0.1, -1:0.2, +1:0.2, +2:0.1]
    Requiere al menos 2 vecinos validos.
    """
    df = df_station.copy().sort_values('date').reset_index(drop=True)
    missing_mask = df['level'].isna()
    missing_indices = df[missing_mask].index.tolist()
    
    if not missing_indices:
        return df, []
    
    # Agrupar gaps consecutivos
    gaps = []
    current_gap = [missing_indices[0]]
    for i in range(1, len(missing_indices)):
        if missing_indices[i] == missing_indices[i-1] + 1:
            current_gap.append(missing_indices[i])
        else:
            gaps.append(current_gap)
            current_gap = [missing_indices[i]]
    gaps.append(current_gap)
    
    imputations = []
    
    for gap in gaps:
        if len(gap) <= 3:
            for idx in gap:
                # Ventana de vecinos
                window_values = []
                weights = [0.1, 0.2, 0.2, 0.1]
                offsets = [-2, -1, 1, 2]
                
                for offset, weight in zip(offsets, weights):
                    check_idx = idx + offset
                    if 0 <= check_idx < len(df):
                        val = df.loc[check_idx, 'level']
                        if pd.notna(val):
                            window_values.append((val, weight))
                
                if len(window_values) >= 2:
                    total_weight = sum(w for _, w in window_values)
                    if total_weight > 0:
                        imputed = sum(v * w for v, w in window_values) / total_weight
                        df.loc[idx, 'level'] = imputed
                        imputations.append({
                            'date': df.loc[idx, 'date'],
                            'value': imputed,
                            'nivel': 1,
                            'metodo': 'L1_Interpolacion'
                        })
    
    return df, imputations


def apply_level2(df_station, df_donor):
    """
    Aplica H-H con Calamar para gaps > 3 dias.
    Modelo cuadratico: H_sp = 0.002688*H_cal^2 + 0.9607*H_cal + 0.0664
    """
    df = df_station.copy().sort_values('date').reset_index(drop=True)
    df_don = df_donor.copy().sort_values('date').reset_index(drop=True)
    
    # Merge para saber donde donante tiene datos
    merged = pd.merge(
        df[['date', 'level']].rename(columns={'level': 'target_level'}),
        df_don[['date', 'level']].rename(columns={'level': 'donor_level'}),
        on='date',
        how='left'
    )
    
    missing_mask = merged['target_level'].isna() & merged['donor_level'].notna()
    to_impute = merged[missing_mask].copy()
    
    imputations = []
    
    for _, row in to_impute.iterrows():
        donor_val = row['donor_level']
        imputed = np.polyval(HH_COEFFS, donor_val)
        
        idx = df[df['date'] == row['date']].index
        if len(idx) > 0:
            df.loc[idx[0], 'level'] = imputed
            imputations.append({
                'date': row['date'],
                'value': imputed,
                'nivel': 2,
                'metodo': f'HH_{DONOR_NAME}_quadratic'
            })
    
    return df, imputations


# =============================================================================
# MAIN
# =============================================================================
print("=" * 80)
print("IMPUTACION QUIRURGICA - SAN PEDRITO (Actualizacion v4.2)")
print("=" * 80)

# ---------------------------------------------------------------------------
# Paso 1: Extraer 17 estaciones intactas del v4_2 anterior
# ---------------------------------------------------------------------------
print("\n[Paso 1] Extrayendo 17 estaciones intactas del v4_2 anterior...")
df_v4 = pd.read_csv(V4_2_COMPLETE)
df_v4_no_sp = df_v4[df_v4['NombreEstacion'] != 'San Pedrito'].copy()
print(f"  Registros 17 estaciones: {len(df_v4_no_sp):,}")

# ---------------------------------------------------------------------------
# Paso 2: Leer datos originales de San Pedrito y Calamar
# ---------------------------------------------------------------------------
print("\n[Paso 2] Leyendo datos originales de San Pedrito y Calamar...")
df_sp_raw = load_source_truth('SAN_PEDRITO')
df_cal_raw = load_source_truth('CALAMAR')
print(f"  San Pedrito originales: {len(df_sp_raw):,} registros")
print(f"  Calamar originales: {len(df_cal_raw):,} registros")
print(f"  SP validos: {df_sp_raw['level'].notna().sum():,} | Faltantes: {df_sp_raw['level'].isna().sum():,}")

# ---------------------------------------------------------------------------
# Paso 3: Aplicar Nivel 1 (interpolacion local) a gaps <= 3 dias
# ---------------------------------------------------------------------------
print("\n[Paso 3] Aplicando Nivel 1: Interpolacion local ponderada (gaps <= 3 dias)...")
df_sp_l1, imp_l1 = apply_level1(df_sp_raw)
print(f"  Valores imputados Nivel 1: {len(imp_l1)}")
print(f"  Faltantes despues de L1: {df_sp_l1['level'].isna().sum():,}")

# ---------------------------------------------------------------------------
# Paso 4: Aplicar Nivel 2 (H-H con Calamar) a gaps > 3 dias
# ---------------------------------------------------------------------------
print("\n[Paso 4] Aplicando Nivel 2: Curva H-H con Calamar (gaps > 3 dias)...")
print(f"  Modelo: cuadratico | R2 = 0.9930")
df_sp_l2, imp_l2 = apply_level2(df_sp_l1, df_cal_raw)
print(f"  Valores imputados Nivel 2: {len(imp_l2)}")
print(f"  Faltantes despues de L2: {df_sp_l2['level'].isna().sum():,}")

# ---------------------------------------------------------------------------
# Paso 5: Formatear San Pedrito al formato v4_2 Complete
# ---------------------------------------------------------------------------
print("\n[Paso 5] Formateando San Pedrito al formato v4_2...")

df_sp_final = pd.DataFrame()
df_sp_final['Fecha'] = df_sp_l2['date'].dt.strftime('%d-%m-%Y')
df_sp_final['CodigoEstacion'] = int(STATION_CODE)
df_sp_final['NombreEstacion'] = STATION_NAME
df_sp_final['Cota'] = df_sp_l2['level']

# Determinar nivel de imputacion y metodo
df_sp_final['Nivel_Imputacion'] = 0
df_sp_final['Metodo'] = 'Original'

# Marcar interpolaciones L1
l1_dates = {d.strftime('%d-%m-%Y') for d in [x['date'] for x in imp_l1]}
mask_l1 = df_sp_final['Fecha'].isin(l1_dates)
df_sp_final.loc[mask_l1, 'Nivel_Imputacion'] = 1
df_sp_final.loc[mask_l1, 'Metodo'] = 'L1_Interpolacion'

# Marcar H-H L2
l2_dates = {d.strftime('%d-%m-%Y') for d in [x['date'] for x in imp_l2]}
mask_l2 = df_sp_final['Fecha'].isin(l2_dates)
df_sp_final.loc[mask_l2, 'Nivel_Imputacion'] = 2
df_sp_final.loc[mask_l2, 'Metodo'] = f'HH_{DONOR_NAME}_quadratic'

print(f"  San Pedrito final: {len(df_sp_final):,} registros")
print(f"    Original: {(df_sp_final['Nivel_Imputacion'] == 0).sum():,}")
print(f"    L1 Interpolacion: {(df_sp_final['Nivel_Imputacion'] == 1).sum():,}")
print(f"    H-H Calamar: {(df_sp_final['Nivel_Imputacion'] == 2).sum():,}")
print(f"    Aun faltantes: {df_sp_final['Cota'].isna().sum():,}")

# ---------------------------------------------------------------------------
# Paso 6: Fusionar y guardar
# ---------------------------------------------------------------------------
print("\n[Paso 6] Fusionando y guardando nuevo v4_2 Complete...")

# Asegurar que las columnas coincidan
df_v4_no_sp = df_v4_no_sp[['Fecha', 'CodigoEstacion', 'NombreEstacion', 'Cota', 'Nivel_Imputacion', 'Metodo']]
df_sp_final = df_sp_final[['Fecha', 'CodigoEstacion', 'NombreEstacion', 'Cota', 'Nivel_Imputacion', 'Metodo']]

# Backup del anterior
backup_path = OUTPUT_DIR / 'Datos_Imputados_v4_2_Complete_backup_pre_sanpedrito.csv'
df_v4.to_csv(backup_path, index=False, encoding='utf-8-sig')
print(f"  Backup guardado: {backup_path}")

# Fusionar
df_new = pd.concat([df_v4_no_sp, df_sp_final], ignore_index=True)
df_new = df_new.sort_values(['NombreEstacion', 'Fecha']).reset_index(drop=True)
print(f"  Nuevo v4_2 Complete: {len(df_new):,} registros")

df_new.to_csv(OUTPUT_CSV, index=False, encoding='utf-8-sig')
print(f"  Guardado: {OUTPUT_CSV}")

# ---------------------------------------------------------------------------
# Paso 7: Estadisticas globales
# ---------------------------------------------------------------------------
print("\n" + "=" * 80)
print("ESTADISTICAS GLOBALES - NUEVO v4_2 COMPLETE")
print("=" * 80)

total = len(df_new)
original = (df_new['Nivel_Imputacion'] == 0).sum()
l1 = (df_new['Nivel_Imputacion'] == 1).sum()
l2 = (df_new['Nivel_Imputacion'] == 2).sum()
missing = df_new['Cota'].isna().sum()

print(f"Total registros: {total:,}")
print(f"Datos originales: {original:,} ({100*original/total:.2f}%)")
print(f"Imputados Nivel 1 (interpolacion): {l1:,} ({100*l1/total:.2f}%)")
print(f"Imputados Nivel 2 (H-H): {l2:,} ({100*l2/total:.2f}%)")
print(f"Aun faltantes: {missing:,} ({100*missing/total:.2f}%)")
print(f"Cobertura global: {100*(original+l1+l2)/total:.2f}%")

# Estadisticas por estacion
print("\n" + "-" * 80)
print(f"{'Estacion':<20} {'Total':>8} {'Original':>8} {'L1':>8} {'L2':>8} {'Faltan':>8} {'Cob.':>7}")
print("-" * 80)
for est in sorted(df_new['NombreEstacion'].unique()):
    s = df_new[df_new['NombreEstacion'] == est]
    t = len(s)
    o = (s['Nivel_Imputacion'] == 0).sum()
    i1 = (s['Nivel_Imputacion'] == 1).sum()
    i2 = (s['Nivel_Imputacion'] == 2).sum()
    f = s['Cota'].isna().sum()
    cov = 100 * (o + i1 + i2) / t
    print(f"{est:<20} {t:>8,} {o:>8,} {i1:>8,} {i2:>8,} {f:>8,} {cov:>6.1f}%")

# Guardar estadisticas
stats_path = OUTPUT_DIR / 'Estadisticas_v4_2_Actualizado_SanPedrito.csv'
stats_data = []
for est in sorted(df_new['NombreEstacion'].unique()):
    s = df_new[df_new['NombreEstacion'] == est]
    t = len(s)
    o = (s['Nivel_Imputacion'] == 0).sum()
    i1 = (s['Nivel_Imputacion'] == 1).sum()
    i2 = (s['Nivel_Imputacion'] == 2).sum()
    f = s['Cota'].isna().sum()
    cov = 100 * (o + i1 + i2) / t
    stats_data.append({
        'Estacion': est,
        'Total': t,
        'Original': o,
        'L1_Interpolacion': i1,
        'L2_HH': i2,
        'Faltantes': f,
        'Cobertura_Pct': round(cov, 2)
    })
pd.DataFrame(stats_data).to_csv(stats_path, index=False, encoding='utf-8-sig')
print(f"\nEstadisticas guardadas: {stats_path}")

print("\n" + "=" * 80)
print("PROCESO COMPLETADO")
print("=" * 80)
