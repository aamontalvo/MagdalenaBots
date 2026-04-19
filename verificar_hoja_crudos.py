"""
Verificar datos desde la hoja 'Crudos' de cada Excel
Identificar columna de fecha y nivel medio diario
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

print('=' * 120)
print('VERIFICACION DESDE HOJA CRUDOS - Fecha y Nivel Medio Diario')
print('=' * 120)
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
        
        # Leer Excel y encontrar hoja Crudos/Crudas
        xl = pd.ExcelFile(file_path)
        
        if 'Crudos' in xl.sheet_names:
            sheet_name = 'Crudos'
        elif 'Crudas' in xl.sheet_names:
            sheet_name = 'Crudas'
        else:
            sheet_name = xl.sheet_names[0]
        
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        
        # Analizar columnas
        fecha_col = None
        nivel_col = None
        cota_col = None
        
        for col in df.columns:
            col_str = str(col).lower()
            # Buscar columna de fecha
            if any(word in col_str for word in ['fecha', 'date', 'time']):
                fecha_col = col
            # Buscar columna de nivel
            if 'nivel' in col_str and 'cm' in col_str:
                nivel_col = col
            # Buscar columna de cota
            if 'cota' in col_str:
                cota_col = col
        
        # Usar cota si existe, si no usar nivel
        valor_col = cota_col if cota_col else nivel_col
        
        if fecha_col and valor_col:
            # Convertir fecha
            df['fecha_dt'] = pd.to_datetime(df[fecha_col], errors='coerce')
            df['valor_num'] = pd.to_numeric(df[valor_col], errors='coerce')
            
            # Filtrar validos
            df_valid = df.dropna(subset=['fecha_dt', 'valor_num'])
            
            if len(df_valid) > 0:
                fecha_inicio = df_valid['fecha_dt'].min()
                fecha_fin = df_valid['fecha_dt'].max()
                total = len(df_valid)
                
                resultados.append({
                    'Estacion': estacion,
                    'Hoja': sheet_name,
                    'Col_Fecha': str(fecha_col)[:20],
                    'Col_Valor': str(valor_col)[:30],
                    'Ano_Inicio': fecha_inicio.year,
                    'Mes_Inicio': fecha_inicio.month,
                    'Ano_Fin': fecha_fin.year,
                    'Mes_Fin': fecha_fin.month,
                    'Fecha_Inicio': fecha_inicio.strftime('%Y-%m-%d'),
                    'Fecha_Fin': fecha_fin.strftime('%Y-%m-%d'),
                    'Total_Registros': total
                })
                
                print(f"{estacion[:20].ljust(20)} | Hoja: {sheet_name[:8].ljust(8)} | {fecha_inicio.strftime('%Y-%m-%d')} a {fecha_fin.strftime('%Y-%m-%d')} | {str(total).rjust(6)} regs")
            else:
                print(f"{estacion[:20]} | No hay datos validos")
        else:
            print(f"{estacion[:20]} | No se encontraron columnas de fecha/valor")
            print(f"                    Columnas disponibles: {list(df.columns)}")
            
    except Exception as e:
        print(f"{archivo[:30]} | ERROR: {str(e)[:60]}")

print()
print('=' * 120)
print('TABLA RESUMEN - HOJA CRUDOS')
print('=' * 120)
print()

if resultados:
    resumen_df = pd.DataFrame(resultados)
    resumen_df = resumen_df.sort_values('Fecha_Inicio')

    header = "Estacion            | Ano Ini | Mes Ini | Ano Fin | Mes Fin | Total Reg | Hoja      "
    print(header)
    print('-' * 100)
    for _, row in resumen_df.iterrows():
        line = f"{row['Estacion']:<20} | {row['Ano_Inicio']:<7} | {row['Mes_Inicio']:<7} | {row['Ano_Fin']:<7} | {row['Mes_Fin']:<7} | {row['Total_Registros']:<9} | {row['Hoja']:<10}"
        print(line)

    print()
    print('=' * 120)
    print('RESUMEN EJECUTIVO')
    print('=' * 120)
    print(f"Total estaciones: {len(resumen_df)}")
    print(f"Inicio mas antiguo: {resumen_df['Fecha_Inicio'].min()}")
    print(f"Fin mas reciente: {resumen_df['Fecha_Fin'].max()}")
    
    # Guardar
    resumen_df.to_csv('resumen_fechas_crudos.csv', index=False)
    print(f"\nArchivo guardado: resumen_fechas_crudos.csv")
else:
    print("No se encontraron resultados.")
