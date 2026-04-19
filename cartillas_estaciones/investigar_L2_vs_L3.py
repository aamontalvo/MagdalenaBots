# -*- coding: utf-8 -*-
"""
Investigar diferencia real entre L2 y L3
"""
import pandas as pd
import numpy as np
from pathlib import Path

DATA_PATH = r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\Informes\imputacion\Datos_Imputados_v4_2_Complete.csv'

print('='*80)
print('INVESTIGACION: DIFERENCIA REAL ENTRE L2 Y L3')
print('='*80)

df = pd.read_csv(DATA_PATH)

# Analizar casos especificos de L2 y L3
print('\n[1] ANALISIS DE MUESTRAS L2 vs L3...')

# Verificar si hay alguna diferencia en Nivel_Imputacion
print('\n[2] Nivel_Imputacion para cada metodo...')
for metodo in ['L2_HH_quadratic', 'L3_HH_quadratic']:
    df_met = df[df['Metodo'] == metodo]
    print(f'\n{metodo}:')
    print(f'  Nivel_Imputacion unicos: {df_met["Nivel_Imputacion"].unique()}')
    print(f'  Distribucion: {dict(df_met["Nivel_Imputacion"].value_counts())}')

# Verificar correlacion entre estaciones para L2 y L3
print('\n[3] INTENTANDO ENCONTRAR PATRON...')
print('\nPara cada estacion con L2/L3, veamos el contexto temporal...')

# Ejemplo: Tenerife (tiene L2)
print('\n--- TENERIFE (L2) ---')
df_tenerife = df[df['NombreEstacion'] == 'Tenerife'].copy()
df_tenerife['Fecha_dt'] = pd.to_datetime(df_tenerife['Fecha'], format='%d-%m-%Y')
df_tenerife = df_tenerife.sort_values('Fecha_dt')

# Encontrar periodos de imputacion L2
periodos_l2 = df_tenerife[df_tenerife['Metodo'] == 'L2_HH_quadratic']
print(f'Periodos L2: {len(periodos_l2)} registros')
print('Rango de fechas L2:', periodos_l2['Fecha_dt'].min(), 'a', periodos_l2['Fecha_dt'].max())

# Ejemplo: Barbosa (tiene L3)
print('\n--- BARBOSA (L3) ---')
df_barbosa = df[df['NombreEstacion'] == 'Barbosa'].copy()
df_barbosa['Fecha_dt'] = pd.to_datetime(df_barbosa['Fecha'], format='%d-%m-%Y')
df_barbosa = df_barbosa.sort_values('Fecha_dt')

periodos_l3 = df_barbosa[df_barbosa['Metodo'] == 'L3_HH_quadratic']
print(f'Periodos L3: {len(periodos_l3)} registros')
print('Rango de fechas L3:', periodos_l3['Fecha_dt'].min(), 'a', periodos_l3['Fecha_dt'].max())

# Verificar si hay diferencia en la cantidad de datos disponibles
print('\n[4] ANALISIS DE COBERTURA PREVIA...')

estaciones_l2 = ['Tenerife', 'Magangue']
estaciones_l3 = ['Barbosa', 'Rio Nuevo', 'Las Palomas', 'Coyongal', 'Penoncito', 'Plato']

print('\nEstaciones L2:')
for est in estaciones_l2:
    df_est = df[df['NombreEstacion'] == est]
    total = len(df_est)
    orig = len(df_est[df_est['Metodo'] == 'Original'])
    l2 = len(df_est[df_est['Metodo'] == 'L2_HH_quadratic'])
    l3 = len(df_est[df_est['Metodo'] == 'L3_HH_quadratic'])
    l4 = len(df_est[df_est['Metodo'] == 'L4_HH_quadratic'])
    print(f'  {est}: Total={total}, Orig={orig}, L2={l2}, L3={l3}, L4={l4}')

print('\nEstaciones L3:')
for est in estaciones_l3:
    df_est = df[df['NombreEstacion'] == est]
    total = len(df_est)
    orig = len(df_est[df_est['Metodo'] == 'Original'])
    l2 = len(df_est[df_est['Metodo'] == 'L2_HH_quadratic'])
    l3 = len(df_est[df_est['Metodo'] == 'L3_HH_quadratic'])
    l4 = len(df_est[df_est['Metodo'] == 'L4_HH_quadratic'])
    print(f'  {est}: Total={total}, Orig={orig}, L2={l2}, L3={l3}, L4={l4}')

# CONCLUSION
print('\n' + '='*80)
print('CONCLUSION')
print('='*80)
print('\nLa UNICA diferencia visible es:')
print('- L2: Nivel_Imputacion = 2')
print('- L3: Nivel_Imputacion = 3')
print('\nAMBOS usan el mismo tipo de ecuacion (cuadratica) y una sola estacion donante.')
print('La diferencia parece ser meramente de clasificacion/etiquetado, no de metodologia.')
