# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from pathlib import Path

# FUENTE CORRECTA v4.2
DATA_PATH = r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\Informes\imputacion\Datos_Imputados_v4_2_Complete.csv'
OUTPUT_DIR = r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\cartillas_estaciones\v4_2\CALAMAR'

def calcular_percentiles_por_dia(df):
    """Calcula percentiles por dia exacto del ano (1-366)"""
    df = df.copy()
    df['Fecha'] = pd.to_datetime(df['Fecha'], format='%d-%m-%Y')
    df['day_of_year'] = df['Fecha'].dt.dayofyear
    
    # Solo necesitamos la columna Cota - no importa el Metodo
    df_clean = df[df['Cota'].notna()].copy()
    
    results = {}
    for doy in range(1, 367):
        day_data = df_clean[df_clean['day_of_year'] == doy]['Cota'].values
        if len(day_data) > 0:
            results[doy] = {
                'day_of_year': doy,
                'fecha_referencia': pd.to_datetime(f'2020-{doy:03d}', format='%Y-%j').strftime('%d-%m'),
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

# Calcular percentiles
print('Calculando percentiles por dia del ano...')
percentiles_df = calcular_percentiles_por_dia(df_calamar)

# Guardar CSV
output_file = Path(OUTPUT_DIR) / 'Fig4_Percentiles_CALAMAR.csv'
percentiles_df.to_csv(output_file, index=False)
print(f'Guardado: {output_file}')
print(f'Total dias calculados: {len(percentiles_df)}')
print('\nPrimeros 10 registros:')
print(percentiles_df.head(10).to_string())
print('\nUltimos 10 registros:')
print(percentiles_df.tail(10).to_string())
print('\nResumen estadistico:')
print(percentiles_df[['max', 'p95', 'p75', 'p50', 'p25', 'p5', 'min']].describe())
