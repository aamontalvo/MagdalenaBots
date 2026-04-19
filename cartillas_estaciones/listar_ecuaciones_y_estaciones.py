# -*- coding: utf-8 -*-
"""
Listar ecuaciones y estaciones dependientes para L2 y L3
"""
import pandas as pd
import numpy as np
from pathlib import Path

DATA_PATH = r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\Informes\imputacion\Datos_Imputados_v4_2_Complete.csv'
MODELS_PATH = r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\Informes\imputacion\Tabla_I2_Modelos_HH_v3.csv'

print('='*80)
print('ECUACIONES Y ESTACIONES - SISTEMA DE IMPUTACION L2/L3')
print('='*80)

# 1. Cargar datos imputados v4.2
print('\n[1] Analizando datos imputados v4.2...')
df = pd.read_csv(DATA_PATH)

# Estadisticas por metodo
print('\n--- Distribucion de metodos ---')
metodos = df['Metodo'].value_counts()
print(metodos)

# 2. Estaciones que tienen datos L2 (L2_HH_quadratic)
print('\n[2] Estaciones con imputaciones L2 (L2_HH_quadratic)...')
df_l2 = df[df['Metodo'] == 'L2_HH_quadratic']
estaciones_l2 = df_l2['NombreEstacion'].value_counts()
print(f'Total registros L2: {len(df_l2)}')
print('\nEstaciones con imputacion L2:')
for est, count in estaciones_l2.items():
    print(f'  - {est}: {count} registros')

# 3. Estaciones que tienen datos L3 (L3_HH_quadratic)
print('\n[3] Estaciones con imputaciones L3 (L3_HH_quadratic)...')
df_l3 = df[df['Metodo'] == 'L3_HH_quadratic']
estaciones_l3 = df_l3['NombreEstacion'].value_counts()
print(f'Total registros L3: {len(df_l3)}')
print('\nEstaciones con imputacion L3:')
for est, count in estaciones_l3.items():
    print(f'  - {est}: {count} registros')

# 4. Cargar tabla de modelos HH
print('\n[4] Cargando tabla de modelos H-H...')
try:
    models_df = pd.read_csv(MODELS_PATH)
    print(f'Modelos cargados: {len(models_df)}')
    print('\n--- Modelos disponibles ---')
    print(models_df[['target', 'donor', 'model_type', 'r2', 'n_training', 'n_imputed']].to_string())
    
    print('\n--- Ecuaciones de los modelos ---')
    for _, row in models_df.iterrows():
        print(f"\n{row['target']} <- {row['donor']}")
        print(f"  Tipo: {row['model_type']}")
        print(f"  R2: {row['r2']:.4f}")
        print(f"  Ecuacion: {row['equation']}")
        print(f"  Datos entrenamiento: {row['n_training']}")
        print(f"  Datos imputados: {row['n_imputed']}")
except FileNotFoundError:
    print(f'[ERROR] No se encontro: {MODELS_PATH}')

# 5. Resumen de estaciones dependientes (objetivo) unicas
print('\n[5] RESUMEN - Estaciones que reciben imputacion (variables dependientes)...')
print('\nEstaciones con L2:')
for est in sorted(estaciones_l2.index):
    print(f'  - {est}')

print('\nEstaciones con L3:')
for est in sorted(estaciones_l3.index):
    print(f'  - {est}')

# 6. Verificar estaciones que tienen AMBOS (L2 y L3)
estaciones_ambos = set(estaciones_l2.index) & set(estaciones_l3.index)
print(f'\n[6] Estaciones con AMBOS metodos (L2 y L3): {len(estaciones_ambos)}')
for est in sorted(estaciones_ambos):
    print(f'  - {est}')

# 7. Detalle de estaciones que NO tienen imputaciones
print('\n[7] Estaciones sin imputaciones L2 ni L3 (solo Original + L1 + L4):')
all_estaciones = df['NombreEstacion'].unique()
estaciones_con_l2_o_l3 = set(estaciones_l2.index) | set(estaciones_l3.index)
estaciones_sin_l2_l3 = set(all_estaciones) - estaciones_con_l2_o_l3
for est in sorted(estaciones_sin_l2_l3):
    total_reg = len(df[df['NombreEstacion'] == est])
    metodos_est = df[df['NombreEstacion'] == est]['Metodo'].value_counts()
    print(f'  - {est}: {total_reg} registros')
    print(f'    Metodos: {dict(metodos_est)}')
