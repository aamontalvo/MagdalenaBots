# -*- coding: utf-8 -*-
"""
Verificar patrones especificos en las series temporales
"""
import pandas as pd
import numpy as np
from pathlib import Path

DATA_PATH = r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\Informes\imputacion\Datos_Imputados_v4_2_Complete.csv'

def analizar_saltos_y_constantes(nombre):
    print('='*80)
    print(f'ANALISIS DE PATRONES: {nombre.upper()}')
    print('='*80)
    
    df = pd.read_csv(DATA_PATH)
    df_est = df[df['NombreEstacion'] == nombre].copy()
    df_est['Fecha'] = pd.to_datetime(df_est['Fecha'], format='%d-%m-%Y')
    df_est = df_est.sort_values('Fecha')
    
    print(f'\nTotal registros: {len(df_est)}')
    
    # Calcular diferencias entre valores consecutivos
    df_est['diff'] = df_est['Cota'].diff().abs()
    
    # Buscar valores constantes (diferencia = 0)
    constantes = df_est[df_est['diff'] == 0]
    print(f'\nValores consecutivos iguales: {len(constantes)}')
    
    if len(constantes) > 0:
        print('\nMuestra de valores consecutivos iguales:')
        print(constantes[['Fecha', 'Cota', 'Metodo']].head(10).to_string())
    
    # Buscar saltos grandes (diferencia > 2m)
    saltos = df_est[df_est['diff'] > 2]
    print(f'\nSaltos grandes (>2m): {len(saltos)}')
    
    if len(saltos) > 0:
        print('\nMuestra de saltos grandes:')
        print(saltos[['Fecha', 'Cota', 'diff', 'Metodo']].head(5).to_string())
    
    # Analizar por metodo
    print('\n--- Distribucion por metodo ---')
    metodos = df_est.groupby('Metodo')['Cota'].agg(['count', 'min', 'max', 'mean', 'std'])
    print(metodos.to_string())
    
    # Buscar valores constantes por periodos largos (mismo valor por mas de 5 dias consecutivos)
    print('\n--- Busqueda de periodos con valor constante (>5 dias) ---')
    df_est['grupo'] = (df_est['Cota'] != df_est['Cota'].shift()).cumsum()
    grupos = df_est.groupby('grupo').agg({
        'Fecha': ['min', 'max', 'count'],
        'Cota': 'first',
        'Metodo': lambda x: x.mode()[0] if len(x.mode()) > 0 else 'Unknown'
    })
    grupos.columns = ['fecha_inicio', 'fecha_fin', 'duracion_dias', 'valor', 'metodo']
    
    periodos_constantes = grupos[grupos['duracion_dias'] > 5]
    print(f'Periodos con valor constante >5 dias: {len(periodos_constantes)}')
    
    if len(periodos_constantes) > 0:
        print(periodos_constantes.head(5).to_string())
    
    return df_est

# Analizar estaciones
estaciones = ['Gamarra Aut', 'El Contento', 'Coyongal', 'Penoncito']

for est in estaciones:
    analizar_saltos_y_constantes(est)
    print('\n')
