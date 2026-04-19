# -*- coding: utf-8 -*-
import pandas as pd
from pathlib import Path

BASE_DIR = Path('cartillas_estaciones/v4_2')
csv_files = list(BASE_DIR.rglob('Fig4_Percentiles_*.csv'))
csv_files = [f for f in csv_files if '_FINAL' in f.name or f.name.count('_') <= 3]

print('='*90)
print('FIG4 - PERCENTILES GENERADOS PARA TODAS LAS ESTACIONES')
print('REGLA: Excluyendo 29 de febrero')
print('='*90)
print(f'{"Estacion":<20} | Dias | Obs/dia | Cota MAX | Cota MIN')
print('-'*90)

for csv_file in sorted(csv_files):
    df = pd.read_csv(csv_file)
    estacion = csv_file.stem.replace('Fig4_Percentiles_', '').replace('_FINAL', '')
    n_obs_mean = df['n_obs'].mean()
    cota_max = df['max'].max()
    cota_min = df['min'].min()
    print(f'{estacion:<20} | {len(df):>4} | {n_obs_mean:>7.0f} | {cota_max:>8.2f} | {cota_min:>8.2f}')

print('='*90)
print(f'Total estaciones procesadas: {len(csv_files)}')
