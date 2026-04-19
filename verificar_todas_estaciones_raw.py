"""
Verificar TODAS las estaciones desde la PRIMERA HOJA (formato wide)
Las columnas son anos, las filas son dias del ano
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

resultados = []

print('=' * 110)
print('VERIFICACION DESDE PRIMERA HOJA (Formato WIDE - Columnas por ano)')
print('Ruta: ' + path)
print('=' * 110)
print()

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
        
        df_wide = pd.read_excel(file_path, sheet_name=primera_hoja)
        
        # Identificar columnas de anos (enteros entre 1900-2100)
        ano_cols = []
        for c in df_wide.columns:
            if isinstance(c, (int, float)) and 1900 <= c <= 2100:
                ano_cols.append(int(c))
        
        # Encontrar el primer ano y ultimo ano CON DATOS
        ano_inicio_real = None
        ano_fin_real = None
        
        for ano in sorted(ano_cols):
            if df_wide[ano].notna().sum() > 0:
                if ano_inicio_real is None:
                    ano_inicio_real = ano
                ano_fin_real = ano
        
        # Contar total de registros validos
        total_registros = 0
        for ano in ano_cols:
            total_registros += df_wide[ano].notna().sum()
        
        if ano_inicio_real and ano_fin_real:
            resultados.append({
                'Estacion': estacion,
                'Archivo': archivo,
                'Ano_Inicio': ano_inicio_real,
                'Mes_Inicio': 1,  # Asumimos enero como inicio
                'Ano_Fin': ano_fin_real,
                'Mes_Fin': 12,    # Asumimos diciembre como fin
                'Fecha_Inicio': f"{ano_inicio_real}-01-01",
                'Fecha_Fin': f"{ano_fin_real}-12-31",
                'Total_Registros': total_registros,
                'Ano_Min_Columna': min(ano_cols),
                'Ano_Max_Columna': max(ano_cols)
            })
            
            print(estacion[:20].ljust(20) + " | " + 
                  "Rango columnas: " + str(min(ano_cols)) + "-" + str(max(ano_cols)) + " | " +
                  "Datos reales: " + str(ano_inicio_real) + " a " + str(ano_fin_real) + " | " + 
                  str(total_registros).rjust(6) + " registros")
        else:
            print(estacion[:20].ljust(20) + " | ERROR: No se encontraron anos con datos")
            
    except Exception as e:
        print(archivo[:30].ljust(30) + " | ERROR: " + str(e)[:50])

print()
print('=' * 110)
print('TABLA RESUMEN - DATOS DESDE PRIMERA HOJA (Formato WIDE)')
print('=' * 110)
print()

if resultados:
    resumen_df = pd.DataFrame(resultados)
    resumen_df = resumen_df.sort_values('Ano_Inicio')

    header = "Estacion            | Ano Ini Col | Ano Real Ini | Ano Real Fin | Total Reg   "
    print(header)
    print('-' * 90)
    for _, row in resumen_df.iterrows():
        line = f"{row['Estacion']:<20} | {row['Ano_Min_Columna']:<11} | {row['Ano_Inicio']:<12} | {row['Ano_Fin']:<12} | {row['Total_Registros']:<12}"
        print(line)

    print()
    print('=' * 110)
    print('RESUMEN EJECUTIVO')
    print('=' * 110)
    print("Total estaciones procesadas: " + str(len(resumen_df)))
    print("Ano de inicio mas antiguo: " + str(resumen_df['Ano_Inicio'].min()))
    print("Ano de inicio mas reciente: " + str(resumen_df['Ano_Inicio'].max()))
    print()
    print("Estaciones por decada de inicio REAL:")
    for decada in [1960, 1970, 1980, 1990, 2000, 2010]:
        count = len(resumen_df[(resumen_df['Ano_Inicio'] >= decada) & (resumen_df['Ano_Inicio'] < decada + 10)])
        if count > 0:
            print("  " + str(decada) + "s: " + str(count) + " estaciones")

    # Guardar resultados actualizados
    resumen_df.to_csv('resumen_fechas_raw.csv', index=False)
    print()
    print("Archivo actualizado: resumen_fechas_raw.csv")
else:
    print("No se encontraron resultados validos.")
