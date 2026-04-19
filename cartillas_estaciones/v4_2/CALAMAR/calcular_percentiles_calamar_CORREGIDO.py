# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from pathlib import Path

# FUENTE CORRECTA v4.2
DATA_PATH = r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\Informes\imputacion\Datos_Imputados_v4_2_Complete.csv'
OUTPUT_DIR = r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\cartillas_estaciones\v4_2\CALAMAR'

def calcular_percentiles_por_mes_dia(df):
    """Calcula percentiles por MES-DIA (ej: 31-12 incluye TODOS los años)"""
    df = df.copy()
    df['Fecha'] = pd.to_datetime(df['Fecha'], format='%d-%m-%Y')
    df['mes_dia'] = df['Fecha'].dt.strftime('%m-%d')  # Agrupar por MM-DD
    
    # Solo necesitamos la columna Cota
    df_clean = df[df['Cota'].notna()].copy()
    
    # Generar todos los dias del año en formato MM-DD
    fecha_base = pd.date_range('2020-01-01', '2020-12-31', freq='D')
    
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

# Leer datos
print('Leyendo datos v4.2...')
df = pd.read_csv(DATA_PATH)

# Filtrar Calamar
df_calamar = df[df['NombreEstacion'] == 'Calamar'].copy()
print(f'Total registros Calamar: {len(df_calamar)}')

# Verificar especificamente el 31 de diciembre
df_calamar['Fecha_dt'] = pd.to_datetime(df_calamar['Fecha'], format='%d-%m-%Y')
df_calamar['mes_dia'] = df_calamar['Fecha_dt'].dt.strftime('%m-%d')
df_31_12 = df_calamar[df_calamar['mes_dia'] == '12-31']
print(f'\n=== VERIFICACION 31 DE DICIEMBRE ===')
print(f'Total registros 31-12: {len(df_31_12)}')
print(f'MAX: {df_31_12["Cota"].max():.3f}')
print(f'MIN: {df_31_12["Cota"].min():.3f}')
print(f'P50: {df_31_12["Cota"].median():.3f}')
print(f'P95: {df_31_12["Cota"].quantile(0.95):.3f}')

# Calcular percentiles CORREGIDOS
print('\nCalculando percentiles por MES-DIA...')
percentiles_df = calcular_percentiles_por_mes_dia(df_calamar)

# Mostrar especificamente el dia 365 (31 de diciembre)
print('\n=== DIA 365 (31 de diciembre) en archivo CORREGIDO ===')
print(percentiles_df[percentiles_df['mes_dia'] == '12-31'].to_string())

# Guardar CSV
output_file = Path(OUTPUT_DIR) / 'Fig4_Percentiles_CALAMAR_CORREGIDO.csv'
percentiles_df.to_csv(output_file, index=False)
print(f'\nGuardado: {output_file}')
print(f'Total dias calculados: {len(percentiles_df)}')
