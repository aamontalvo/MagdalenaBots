# -*- coding: utf-8 -*-
"""
Fig4 - Curvas de Frecuencia de Niveles Excedidos
PARA TODAS LAS ESTACIONES
REGLA CRITICA: Excluir 29 de febrero (año bisiesto) completamente
"""
import pandas as pd
import numpy as np
from pathlib import Path

# FUENTE v4.2
DATA_PATH = r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\Informes\imputacion\Datos_Imputados_v4_2_Complete.csv'
BASE_OUTPUT_DIR = r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\cartillas_estaciones\v4_2'

# Lista de estaciones
ESTACIONES = [
    'Puerto Wilches', 'Sitio Nuevo', 'El Contento', 'La Gloria', 
    'Gamarra Aut', 'El Banco', 'Penoncito', 'Armenia', 
    'Las Palomas', 'Plato', 'Las Aguadas', 'Barbosa', 
    'Rio Nuevo', 'Magangue', 'Coyongal', 'Tenerife', 
    'Calamar', 'San Pedrito'
]

def calcular_percentiles_excluir_29feb(df):
    """Calcula percentiles por MES-DIA excluyendo 29 de febrero"""
    df = df.copy()
    df['Fecha'] = pd.to_datetime(df['Fecha'], format='%d-%m-%Y')
    
    # REGLA CRITICA: Excluir 29 de febrero
    df['mes_dia'] = df['Fecha'].dt.strftime('%m-%d')
    df = df[df['mes_dia'] != '02-29']
    
    df_clean = df[df['Cota'].notna()].copy()
    
    if len(df_clean) == 0:
        return None
    
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

print('='*70)
print('FIG4 - PERCENTILES PARA TODAS LAS ESTACIONES')
print('REGLA: Excluyendo 29 de febrero')
print('='*70)

# Cargar datos una sola vez
print('\nCargando datos v4.2...')
df = pd.read_csv(DATA_PATH)
print(f'Total registros: {len(df)}')
print(f'Estaciones encontradas: {df["NombreEstacion"].nunique()}')

# Procesar cada estacion
resumen = []
for estacion in ESTACIONES:
    print(f'\n[{estacion}]')
    
    # Filtrar estacion
    df_est = df[df['NombreEstacion'] == estacion].copy()
    print(f'  Registros: {len(df_est)}')
    
    if len(df_est) == 0:
        print(f'  [WARN] Estacion no encontrada!')
        continue
    
    # Verificar 29-feb
    fechas = pd.to_datetime(df_est['Fecha'], format='%d-%m-%Y')
    feb_29_count = len(df_est[fechas.dt.strftime('%m-%d') == '02-29'])
    print(f'  29-feb excluidos: {feb_29_count}')
    
    # Calcular percentiles
    percentiles_df = calcular_percentiles_excluir_29feb(df_est)
    
    if percentiles_df is None or len(percentiles_df) == 0:
        print(f'  [WARN] No se pudieron calcular percentiles')
        continue
    
    print(f'  Dias calculados: {len(percentiles_df)}')
    
    # Crear directorio de salida
    estacion_dir = Path(BASE_OUTPUT_DIR) / estacion.upper().replace(' ', '_')
    estacion_dir.mkdir(parents=True, exist_ok=True)
    
    # Guardar CSV (usar _FINAL para evitar conflictos)
    output_file = estacion_dir / f'Fig4_Percentiles_{estacion.upper().replace(" ", "_")}_FINAL.csv'
    percentiles_df.to_csv(output_file, index=False)
    print(f'  [OK] Guardado: {output_file.name}')
    
    # Resumen
    resumen.append({
        'estacion': estacion,
        'registros': len(df_est),
        'dias_calc': len(percentiles_df),
        'n_obs_promedio': int(percentiles_df['n_obs'].mean()),
        'cota_max': percentiles_df['max'].max(),
        'cota_min': percentiles_df['min'].min()
    })

# Guardar resumen
resumen_df = pd.DataFrame(resumen)
resumen_file = Path(BASE_OUTPUT_DIR) / 'Fig4_resumen_estaciones.csv'
resumen_df.to_csv(resumen_file, index=False)

print('\n' + '='*70)
print('RESUMEN FINAL')
print('='*70)
print(resumen_df.to_string(index=False))
print(f'\nResumen guardado: {resumen_file}')
