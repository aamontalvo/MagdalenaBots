# -*- coding: utf-8 -*-
"""
Genera archivo Excel resumen de Fig4 - Curvas de Frecuencia de Niveles Excedidos
Formato LONG (tidy data) con todos los percentiles de todas las estaciones
"""
import pandas as pd
import numpy as np
from pathlib import Path

# Directorio base con los datos v4.2
BASE_DIR = Path(r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\cartillas_estaciones\v4_2')
OUTPUT_DIR = Path(r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\cartillas_estaciones')

# Lista de estaciones y sus carpetas
ESTACIONES = [
    ('Puerto Wilches', 'PUERTO_WILCHES'),
    ('Sitio Nuevo', 'SITIO_NUEVO'),
    ('El Contento', 'EL_CONTENTO'),
    ('La Gloria', 'LA_GLORIA'),
    ('Gamarra Aut', 'GAMARRA_AUT'),
    ('El Banco', 'EL_BANCO'),
    ('Penoncito', 'PENONCITO'),
    ('Armenia', 'ARMENIA'),
    ('Las Palomas', 'LAS_PALOMAS'),
    ('Plato', 'PLATO'),
    ('Las Aguadas', 'LAS_AGUADAS'),
    ('Barbosa', 'BARBOSA'),
    ('Rio Nuevo', 'RIO_NUEVO'),
    ('Magangue', 'MAGANGUE'),
    ('Coyongal', 'COYONGAL'),
    ('Tenerife', 'TENERIFE'),
    ('Calamar', 'CALAMAR'),
    ('San Pedrito', 'SAN_PEDRITO'),
]

def day_of_year_to_date_str(day_of_year):
    """Convierte dia del año (1-365) a formato 'Jan-01'"""
    import datetime
    # 2020 es año bisiesto pero no importa porque usamos solo 1-365
    fecha = datetime.datetime.strptime(f'2020-{int(day_of_year)}', '%Y-%j')
    return fecha.strftime('%b-%d')  # Formato: Jan-01, Feb-15, etc.

print('='*70)
print('GENERANDO RESUMEN EXCEL - FIG4 PERCENTILES')
print('='*70)

all_data = []

for estacion_nombre, estacion_key in ESTACIONES:
    print(f'Procesando {estacion_nombre}...')
    
    # Buscar archivo de percentiles
    csv_path = BASE_DIR / estacion_key / f'Fig4_Percentiles_{estacion_key}.csv'
    
    if not csv_path.exists():
        # Intentar con _FINAL
        csv_path = BASE_DIR / estacion_key / f'Fig4_Percentiles_{estacion_key}_FINAL.csv'
    
    if not csv_path.exists():
        print(f'  [WARN] No encontrado: {csv_path}')
        continue
    
    # Leer datos
    df = pd.read_csv(csv_path)
    
    # Usar day_of_year para generar la fecha legible
    if 'day_of_year' not in df.columns:
        print(f'  [WARN] No se encontro columna day_of_year en {csv_path}')
        continue
    
    # Convertir day_of_year a formato legible (Jan-01)
    df['dia_anio'] = df['day_of_year'].apply(day_of_year_to_date_str)
    
    # Crear filas en formato LONG
    for _, row in df.iterrows():
        all_data.append({
            'dia_anio': row['dia_anio'],
            'nombre_estacion': estacion_nombre,
            'max': row['max'],
            'p95': row['p95'],
            'p75': row['p75'],
            'p50': row['p50'],
            'p25': row['p25'],
            'p5': row['p5'],
            'min': row['min']
        })
    
    print(f'  Registros agregados: {len(df)}')

# Crear DataFrame final
resumen_df = pd.DataFrame(all_data)
print(f'\nTotal registros en resumen: {len(resumen_df)}')
print(f'Estaciones incluidas: {resumen_df["nombre_estacion"].nunique()}')
print(f'Dias por estacion: {len(resumen_df) // resumen_df["nombre_estacion"].nunique()}')

# Guardar en Excel
output_file = OUTPUT_DIR / 'resumen de graficas.xlsx'
with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
    resumen_df.to_excel(writer, sheet_name='resumen frecuencia de niveles excedidos', index=False)

print(f'\nArchivo Excel guardado: {output_file}')
print(f'Hoja: resumen frecuencia de niveles excedidos')
print(f'\nEstructura del DataFrame:')
print(resumen_df.head(15).to_string())
print(f'\n...')
print(resumen_df.tail(10).to_string())
