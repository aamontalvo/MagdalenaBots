# -*- coding: utf-8 -*-
"""
Fig4 - Curvas de Frecuencia de Niveles Excedidos
REGLA CRITICA: Excluir 29 de febrero (año bisiesto) completamente
"""
import pandas as pd
import numpy as np
from pathlib import Path

# FUENTE v4.2
DATA_PATH = r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\Informes\imputacion\Datos_Imputados_v4_2_Complete.csv'
ORIGINAL_EXCEL = r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\backend\data\raw\SERIE NIVELES IDEAM A 2026\CALAMAR_29037020.xlsx'
OUTPUT_DIR = r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\cartillas_estaciones\v4_2\CALAMAR'

def calcular_percentiles_excluir_29feb(df):
    """Calcula percentiles por MES-DIA excluyendo 29 de febrero"""
    df = df.copy()
    df['Fecha'] = pd.to_datetime(df['Fecha'], format='%d-%m-%Y')
    
    # REGLA CRITICA: Excluir 29 de febrero
    df['mes_dia'] = df['Fecha'].dt.strftime('%m-%d')
    df = df[df['mes_dia'] != '02-29']
    
    df_clean = df[df['Cota'].notna()].copy()
    
    # Generar dias 1-365 (sin 29-feb)
    fecha_base = pd.date_range('2020-01-01', '2020-12-31', freq='D')
    fecha_base = fecha_base[fecha_base.strftime('%m-%d') != '02-29']
    
    results = {}
    for i, fecha in enumerate(fecha_base, 1):
        mes_dia = fecha.strftime('%m-%d')
        day_data = df_clean[df_clean['mes_dia'] == mes_dia]['Cota'].values
        
        if len(day_data) > 0:
            results[i] = {
                'day_of_year': i,
                'mes_dia': mes_dia,
                'fecha_referencia': mes_dia,
                'max': round(np.max(day_data), 3),
                'p95': round(np.percentile(day_data, 95), 3),
                'p75': round(np.percentile(day_data, 75), 3),
                'p50': round(np.percentile(day_data, 50), 3),
                'p25': round(np.percentile(day_data, 25), 3),
                'p5': round(np.percentile(day_data, 5), 3),
                'min': round(np.min(day_data), 3),
                'n_obs': len(day_data)
            }
    return pd.DataFrame(results).T

print('='*60)
print('FIG4 - PERCENTILES POR DIA (EXCLUYENDO 29 DE FEBRERO)')
print('='*60)

# 1. Cargar datos v4.2
print('\n[1] Cargando datos v4.2...')
df = pd.read_csv(DATA_PATH)
df_calamar = df[df['NombreEstacion'] == 'Calamar'].copy()
print(f'    Total registros Calamar v4.2: {len(df_calamar)}')

# Verificar cuantos 29-feb hay
fechas = pd.to_datetime(df_calamar['Fecha'], format='%d-%m-%Y')
feb_29 = df_calamar[fechas.dt.strftime('%m-%d') == '02-29']
print(f'    Registros 29-feb en v4.2: {len(feb_29)}')

# 2. Calcular percentiles EXCLUYENDO 29-feb
print('\n[2] Calculando percentiles (sin 29-feb)...')
percentiles_df = calcular_percentiles_excluir_29feb(df_calamar)
print(f'    Total dias calculados: {len(percentiles_df)}')

# 3. Quality Check - Verificacion manual del 31 de diciembre
print('\n[3] QUALITY CHECK - 31 de Diciembre:')
df_calamar['Fecha_dt'] = pd.to_datetime(df_calamar['Fecha'], format='%d-%m-%Y')
df_calamar['mes_dia'] = df_calamar['Fecha_dt'].dt.strftime('%m-%d')
df_31_12 = df_calamar[df_calamar['mes_dia'] == '12-31']
print(f'    Total registros 31-12: {len(df_31_12)}')
print(f'    MAX: {df_31_12["Cota"].max():.3f}')
print(f'    MIN: {df_31_12["Cota"].min():.3f}')
print(f'    P50: {df_31_12["Cota"].median():.3f}')

# Valor del archivo generado
row_31_12 = percentiles_df[percentiles_df['mes_dia'] == '12-31'].iloc[0]
print(f'    CSV MAX: {row_31_12["max"]}')
print(f'    CSV MIN: {row_31_12["min"]}')
print(f'    CSV P50: {row_31_12["p50"]}')

# Guardar CSV
output_file = Path(OUTPUT_DIR) / 'Fig4_Percentiles_CALAMAR_FINAL.csv'
percentiles_df.to_csv(output_file, index=False)
print(f'\n[4] Guardado: {output_file}')
