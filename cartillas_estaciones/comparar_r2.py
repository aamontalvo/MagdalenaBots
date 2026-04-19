# -*- coding: utf-8 -*-
import pandas as pd

# Tabla de modelos
models = pd.read_csv('Informes/imputacion/Tabla_I2_Modelos_HH_v3.csv')

# Estaciones L2 y L3
estaciones_l2 = ['Tenerife', 'Magangue']
estaciones_l3 = ['Barbosa', 'Rio Nuevo', 'Las Palomas', 'Coyongal', 'Penoncito', 'Plato']

print('=== ESTACIONES L2 ===')
for est in estaciones_l2:
    row = models[models['target'] == est.upper()]
    if not row.empty:
        r2 = row.iloc[0]['r2']
        n = row.iloc[0]['n_training']
        print(f'{est}: R2 = {r2:.4f}, n_training = {n}')

print('\n=== ESTACIONES L3 ===')
for est in estaciones_l3:
    target_name = est.upper().replace(' ', '_')
    row = models[models['target'] == target_name]
    if not row.empty:
        r2 = row.iloc[0]['r2']
        n = row.iloc[0]['n_training']
        print(f'{est}: R2 = {r2:.4f}, n_training = {n}')

# Calcular promedios
models_l2 = models[models['target'].isin([e.upper() for e in estaciones_l2])]
models_l3 = models[models['target'].isin([e.upper().replace(' ', '_') for e in estaciones_l3])]

print('\n=== COMPARACION ===')
print(f'R2 promedio L2: {models_l2["r2"].mean():.4f}')
print(f'R2 promedio L3: {models_l3["r2"].mean():.4f}')
print(f'R2 min L2: {models_l2["r2"].min():.4f}')
print(f'R2 min L3: {models_l3["r2"].min():.4f}')

# Verificar si hay diferencia estadistica
print('\n=== ANALISIS ===')
if models_l2['r2'].mean() > models_l3['r2'].mean():
    print('L2 tiene R2 promedio MAYOR que L3')
else:
    print('L3 tiene R2 promedio MAYOR o igual que L2')

print('\nOrdenando todos los modelos por R2:')
print(models[['target', 'r2']].sort_values('r2').to_string(index=False))
