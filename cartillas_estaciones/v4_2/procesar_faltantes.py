# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from pathlib import Path

DATA_PATH = r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\Informes\imputacion\Datos_Imputados_v4_2_Complete.csv'
BASE_OUTPUT_DIR = r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\cartillas_estaciones\v4_2'

# Procesar estaciones faltantes
for estacion in ['Calamar', 'San Pedrito']:
    print(f'Procesando {estacion}...')
    
    df = pd.read_csv(DATA_PATH)
    df_est = df[df['NombreEstacion'] == estacion].copy()
    
    df_est['Fecha'] = pd.to_datetime(df_est['Fecha'], format='%d-%m-%Y')
    df_est['mes_dia'] = df_est['Fecha'].dt.strftime('%m-%d')
    df_est = df_est[df_est['mes_dia'] != '02-29']
    df_clean = df_est[df_est['Cota'].notna()].copy()
    
    fecha_base = pd.date_range('2020-01-01', '2020-12-31', freq='D')
    fecha_base = fecha_base[fecha_base.strftime('%m-%d') != '02-29']
    
    results = {}
    for i, fecha in enumerate(fecha_base, 1):
        mes_dia = fecha.strftime('%m-%d')
        day_data = df_clean[df_clean['mes_dia'] == mes_dia]['Cota'].values
        if len(day_data) > 0:
            results[i] = {
                'day_of_year': i, 'mes_dia': mes_dia, 'fecha_referencia': mes_dia,
                'max': round(np.max(day_data), 3), 'p95': round(np.percentile(day_data, 95), 3),
                'p75': round(np.percentile(day_data, 75), 3), 'p50': round(np.percentile(day_data, 50), 3),
                'p25': round(np.percentile(day_data, 25), 3), 'p5': round(np.percentile(day_data, 5), 3),
                'min': round(np.min(day_data), 3), 'n_obs': len(day_data)
            }
    
    percentiles_df = pd.DataFrame(results).T
    
    estacion_dir = Path(BASE_OUTPUT_DIR) / estacion.upper().replace(' ', '_')
    estacion_dir.mkdir(parents=True, exist_ok=True)
    
    safe_name = estacion.upper().replace(' ', '_')
    output_file = estacion_dir / f'Fig4_Percentiles_{safe_name}_FINAL.csv'
    percentiles_df.to_csv(output_file, index=False)
    print(f'  Guardado: {output_file}')
    print(f'  Dias: {len(percentiles_df)}, Prom obs/dia: {percentiles_df["n_obs"].mean():.0f}')
