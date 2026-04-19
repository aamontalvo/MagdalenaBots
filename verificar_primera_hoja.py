"""
Verificar datos desde la PRIMERA HOJA (Columnas_ESTACION) de cada Excel
No desde la hoja Crudos
"""

import pandas as pd
import os

path = r'backend/data/raw/SERIE NIVELES IDEAM A 2026/'

archivos = [
    'ARMENIA_25027360.xlsx',
    'BARBOSA_25027530.xlsx',
    'CALAMAR_29037020.xlsx',
    'COYONGAL_25027930.xlsx',
    'EL_BANCO_-_AUT_25027020.xlsx',
    'EL_CONTENTO_23217030.xlsx',
    'GAMARRA_-_AUT_23217080.xlsx',
    'LAS_AGUADAS_25027490.xlsx',
    'LAS_PALOMAS_25027390.xlsx',
    'LA_GLORIA23217060.xlsx',
    'MAGANGUE_25027680.xlsx',
    'PENONCITO_25027330.xlsx',
    'PLATO_MAGDALENA_AUT_25027450.xlsx',
    'PUERTO_WILCHES_23187010.xlsx',
    'RIO_NUEVO_25027630.xlsx',
    'SAN_PEDRITO_-_AUT_29047070.xlsx',
    'SITIO_NUEVO_23187280.xlsx',
    'TENERIFE_29017010.xlsx'
]

print('=' * 100)
print('VERIFICACION DESDE PRIMERA HOJA (Columnas_ESTACION)')
print('=' * 100)
print()

resultados = []

for archivo in sorted(archivos):
    try:
        file_path = os.path.join(path, archivo)
        
        # Extraer nombre de estacion
        if '_-_AUT' in archivo:
            estacion = archivo.split('_-_')[0]
        elif '_AUT_' in archivo:
            estacion = archivo.split('_AUT_')[0].rstrip('_-')
        elif '_MAGADALENA' in archivo:
            estacion = 'PLATO'
        elif '_' in archivo:
            estacion = archivo.split('_')[0]
        else:
            estacion = archivo.replace('.xlsx', '')
        
        # Leer PRIMERA HOJA (indice 0)
        xl = pd.ExcelFile(file_path)
        primera_hoja = xl.sheet_names[0]
        
        df = pd.read_excel(file_path, sheet_name=primera_hoja)
        
        print(f"{estacion[:20].ljust(20)} | Hoja: {primera_hoja[:25].ljust(25)} | Shape: {str(df.shape).ljust(15)}")
        
        # Mostrar primeras columnas para entender estructura
        if len(df.columns) > 0:
            print(f"                    Columnas: {list(df.columns)[:5]}...")
        
        # Intentar encontrar fecha y valor
        # La primera columna suele ser fecha, las siguientes son años
        
    except Exception as e:
        print(archivo[:30].ljust(30) + " | ERROR: " + str(e)[:50])

print()
print('Analisis completo.')
