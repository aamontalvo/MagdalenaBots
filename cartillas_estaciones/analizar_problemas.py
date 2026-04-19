# -*- coding: utf-8 -*-
"""
Analisis de problemas reportados en Fig4
"""
import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = Path(r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\cartillas_estaciones\v4_2')
DATA_PATH = r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\Informes\imputacion\Datos_Imputados_v4_2_Complete.csv'

print('='*80)
print('ANALISIS DE PROBLEMAS EN FIG4')
print('='*80)

# ============================================================================
# PROBLEMA 1: Puerto Wilches y Sitio Nuevo - Eje Y distorsionado
# ============================================================================
print('\n' + '='*80)
print('PROBLEMA 1: PUERTO WILCHES - Rango del eje Y')
print('='*80)

df_pw = pd.read_csv(BASE_DIR / 'PUERTO_WILCHES' / 'Fig4_Percentiles_PUERTO_WILCHES.csv')
print(f'Minimo global en percentiles: {df_pw["min"].min()}')
print(f'Maximo global en percentiles: {df_pw["max"].max()}')
print(f'Rango real de datos: {df_pw["min"].min():.2f} - {df_pw["max"].max():.2f}')
print()
print('Dias con valores minimos mas bajos:')
print(df_pw.nsmallest(10, 'min')[['day_of_year', 'mes_dia', 'min', 'p5', 'p50', 'max']])

print('\n' + '-'*80)
print('SITIO NUEVO - Rango del eje Y')
print('-'*80)
df_sn = pd.read_csv(BASE_DIR / 'SITIO_NUEVO' / 'Fig4_Percentiles_SITIO_NUEVO.csv')
print(f'Minimo global: {df_sn["min"].min()}')
print(f'Maximo global: {df_sn["max"].max()}')
print(f'Rango real: {df_sn["min"].min():.2f} - {df_sn["max"].max():.2f}')

# ============================================================================
# PROBLEMA 2: Gamarra, Penoncito, El Contento, Coyongal - Minimos horizontales
# ============================================================================
print('\n' + '='*80)
print('PROBLEMA 2: MINIMOS HORIZONTALES / PICOS RAROS')
print('='*80)

estaciones_problema = [
    ('Gamarra Aut', 'GAMARRA_AUT'),
    ('Penoncito', 'PENONCITO'),
    ('El Contento', 'EL_CONTENTO'),
    ('Coyongal', 'COYONGAL')
]

for nombre, key in estaciones_problema:
    print(f'\n--- {nombre.upper()} ---')
    df = pd.read_csv(BASE_DIR / key / f'Fig4_Percentiles_{key}.csv')
    
    # Analizar el minimo
    print(f'Rango MIN: {df["min"].min():.2f} - {df["min"].max():.2f}')
    print(f'Media MIN: {df["min"].mean():.2f}')
    print(f'Desv. est. MIN: {df["min"].std():.2f}')
    
    # Verificar si hay valores constantes
    min_counts = df['min'].value_counts().head(5)
    print(f'Valores mas frecuentes en MIN:')
    print(min_counts)
    
    # Ver periodo marzo-mayo (dias 60-151 aprox)
    df_mar_may = df[(df['day_of_year'] >= 60) & (df['day_of_year'] <= 151)]
    print(f'MIN en marzo-mayo: {df_mar_may["min"].min():.2f} - {df_mar_may["min"].max():.2f}')
    print(f'Valores unicos en MIN (mar-may): {df_mar_may["min"].nunique()}')
    
    # Muestra de valores de min en marzo-mayo
    print('Muestra de MIN en marzo-mayo:')
    print(df_mar_may[['day_of_year', 'mes_dia', 'min']].head(15))

# ============================================================================
# Verificar datos originales para Peñoncito
# ============================================================================
print('\n' + '='*80)
print('VERIFICACION DATOS ORIGINALES - PENONCITO')
print('='*80)

df_orig = pd.read_csv(DATA_PATH)
df_pen = df_orig[df_orig['NombreEstacion'] == 'Penoncito'].copy()
df_pen['Fecha'] = pd.to_datetime(df_pen['Fecha'], format='%d-%m-%Y')
df_pen['mes'] = df_pen['Fecha'].dt.month

# Filtrar marzo-mayo
pen_mar_may = df_pen[df_pen['mes'].isin([3, 4, 5])]
print(f'Total registros Penoncito: {len(df_pen)}')
print(f'Registros Marzo-Mayo: {len(pen_mar_may)}')
print()
print('Estadisticas de Cota en Marzo-Mayo:')
print(pen_mar_may['Cota'].describe())
print()
print('Valores MIN por mes (Marzo-Mayo):')
for mes in [3, 4, 5]:
    mes_data = pen_mar_may[pen_mar_may['mes'] == mes]['Cota']
    print(f'Mes {mes}: MIN={mes_data.min()}, N={len(mes_data)}')

# Ver cuantos valores unicos hay
print()
print('Valores mas frecuentes en Cota (Marzo-Mayo):')
print(pen_mar_may['Cota'].value_counts().head(10))

# Verificar si hay valores constantes por dia
print()
print('Verificacion de dias con mismo valor minimo:')
pen_mar_may['mes_dia'] = pen_mar_may['Fecha'].dt.strftime('%m-%d')
min_por_dia = pen_mar_may.groupby('mes_dia')['Cota'].min()
print(f'Dias con mismo MIN: {min_por_dia.value_counts().head(10)}')
