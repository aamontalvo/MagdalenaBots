# -*- coding: utf-8 -*-
"""
Investigacion de problemas en Gamarra Aut, El Contento, Coyongal
"""
import pandas as pd
import numpy as np
from pathlib import Path

DATA_PATH = r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\Informes\imputacion\Datos_Imputados_v4_2_Complete.csv'

def investigar_estacion(nombre, columna_fecha='Fecha', columna_valor='Cota'):
    print('='*80)
    print(f'INVESTIGACION: {nombre.upper()}')
    print('='*80)
    
    df = pd.read_csv(DATA_PATH)
    df_est = df[df['NombreEstacion'] == nombre].copy()
    df_est['Fecha'] = pd.to_datetime(df_est['Fecha'], format='%d-%m-%Y')
    df_est['year'] = df_est['Fecha'].dt.year
    df_est['mes'] = df_est['Fecha'].dt.month
    df_est['mes_dia'] = df_est['Fecha'].dt.strftime('%m-%d')
    
    print(f'\nTotal registros: {len(df_est)}')
    print(f'Perido: {df_est["Fecha"].min()} a {df_est["Fecha"].max()}')
    
    # Valores mas frecuentes
    print('\n--- Valores mas frecuentes en Cota ---')
    valor_counts = df_est['Cota'].value_counts().head(10)
    print(valor_counts)
    
    # Buscar valores que se repiten muchas veces (posiblemente constantes)
    print('\n--- Valores que aparecen mas de 20 veces ---')
    valores_repetidos = df_est['Cota'].value_counts()
    valores_repetidos = valores_repetidos[valores_repetidos > 20]
    if len(valores_repetidos) > 0:
        print(valores_repetidos)
        
        # Para cada valor repetido, ver el periodo
        for valor in valores_repetidos.index[:3]:
            print(f'\n--- Analisis del valor {valor} ---')
            df_valor = df_est[df_est['Cota'] == valor]
            print(f'Total: {len(df_valor)} registros')
            print(f'Years: {sorted(df_valor["year"].unique())}')
            print(f'Meses: {sorted(df_valor["mes"].unique())}')
            print('Metodos:', df_valor['Metodo'].value_counts().to_dict())
            
            # Ver si es un periodo continuo
            df_valor_sorted = df_valor.sort_values('Fecha')
            print(f'Primer fecha: {df_valor_sorted["Fecha"].min()}')
            print(f'Ultima fecha: {df_valor_sorted["Fecha"].max()}')
            
            # Muestra de fechas
            print('Muestra de fechas:')
            print(df_valor_sorted[['Fecha', 'year', 'mes', 'Metodo']].head(10))
    else:
        print('No se encontraron valores repetidos mas de 20 veces')
    
    # Analizar minimos por mes
    print('\n--- Rango de MIN por mes ---')
    min_por_mes = df_est.groupby('mes')['Cota'].agg(['min', 'max', 'count'])
    print(min_por_mes)
    
    return df_est

# Investigar cada estacion
print('\n')
estaciones = ['Gamarra Aut', 'El Contento', 'Coyongal']

for estacion in estaciones:
    investigar_estacion(estacion)
    print('\n')
