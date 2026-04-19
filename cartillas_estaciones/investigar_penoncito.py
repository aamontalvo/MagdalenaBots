# -*- coding: utf-8 -*-
"""
Investigacion profunda del problema en Penoncito
"""
import pandas as pd
import numpy as np
from pathlib import Path

DATA_PATH = r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\Informes\imputacion\Datos_Imputados_v4_2_Complete.csv'

print('='*80)
print('INVESTIGACION: PENONCITO - Valor 19.637 repetido')
print('='*80)

df = pd.read_csv(DATA_PATH)
df_pen = df[df['NombreEstacion'] == 'Penoncito'].copy()
df_pen['Fecha'] = pd.to_datetime(df_pen['Fecha'], format='%d-%m-%Y')
df_pen['mes'] = df_pen['Fecha'].dt.month
df_pen['year'] = df_pen['Fecha'].dt.year
df_pen['mes_dia'] = df_pen['Fecha'].dt.strftime('%m-%d')

# Analizar el valor 19.637
print('\n1. ANALISIS DEL VALOR 19.637:')
print('-'*40)
valores_19_637 = df_pen[df_pen['Cota'] == 19.637]
print(f'Total registros con valor 19.637: {len(valores_19_637)}')
print()
print('Distribucion por year:')
print(valores_19_637['year'].value_counts().sort_index())
print()
print('Distribucion por mes:')
print(valores_19_637['mes'].value_counts().sort_index())
print()
print('Metodos de imputacion para estos registros:')
print(valores_19_637['Metodo'].value_counts())
print()
print('Nivel de imputacion:')
print(valores_19_637['Nivel_Imputacion'].value_counts())

# Ver las fechas especificas
print()
print('Primeros 20 registros con 19.637:')
print(valores_19_637[['Fecha', 'year', 'mes', 'Cota', 'Metodo', 'Nivel_Imputacion']].head(20))

# Analizar el minimo historico por dia
print()
print('\n2. MINIMO HISTORICO POR DIA (marzo-mayo):')
print('-'*40)
mar_may = df_pen[df_pen['mes'].isin([3, 4, 5])]
min_por_dia = mar_may.groupby('mes_dia')['Cota'].min().reset_index()
min_por_dia.columns = ['mes_dia', 'min_historico']

# Ver cuantos dias tienen el mismo minimo
print('Dias con minimo historico = 19.637:')
dias_19_637 = min_por_dia[min_por_dia['min_historico'] == 19.637]
print(f'Total dias: {len(dias_19_637)}')
print(dias_19_637.head(20))

# Analizar los valores originales vs imputados
print()
print('\n3. DATOS ORIGINALES vs IMPUTADOS en marzo:')
print('-'*40)
marzo = df_pen[(df_pen['mes'] == 3)]
print('Por metodo:')
print(marzo.groupby('Metodo')['Cota'].agg(['count', 'min', 'max', 'mean']))

# Verificar si 19.637 es un valor original o imputado
print()
print('Registros con 19.637 que son ORIGINALES:')
orig_19_637 = valores_19_637[valores_19_637['Metodo'] == 'Original']
print(f'Cantidad: {len(orig_19_637)}')
if len(orig_19_637) > 0:
    print(orig_19_637[['Fecha', 'year', 'Cota']].head(10))

print()
print('Registros con 19.637 que son IMPUTADOS:')
imp_19_637 = valores_19_637[valores_19_637['Metodo'] != 'Original']
print(f'Cantidad: {len(imp_19_637)}')
if len(imp_19_637) > 0:
    print(imp_19_637[['Fecha', 'year', 'Cota', 'Metodo']].head(10))
