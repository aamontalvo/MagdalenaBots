#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Convierte Resumen_WideFormat_NotProcessedNotImputation.xlsx a formato LONG
"""

import pandas as pd
import os
from datetime import datetime

# Mapeo de hojas a códigos y nombres IDEAM
ESTACIONES_INFO = {
    'SanPedrito': {'codigo': '29047070', 'nombre': 'San Pedrito'},
    'Calamar': {'codigo': '29037020', 'nombre': 'Calamar'},
    'Tenerife': {'codigo': '29017010', 'nombre': 'Tenerife'},
    'Plato': {'codigo': '25027450', 'nombre': 'Plato'},
    'Magangue': {'codigo': '25027680', 'nombre': 'Magangue'},
    'Barbosa': {'codigo': '25027530', 'nombre': 'Barbosa'},
    'Coyongal': {'codigo': '25027930', 'nombre': 'Coyongal'},
    'Armenia': {'codigo': '25027360', 'nombre': 'Armenia'},
    'RioNuevo': {'codigo': '25027630', 'nombre': 'Rio Nuevo'},
    'LasPalomas': {'codigo': '25027390', 'nombre': 'Las Palomas'},
    'LasAguadas': {'codigo': '25027490', 'nombre': 'Las Aguadas'},
    'ElBanco': {'codigo': '25027020', 'nombre': 'El Banco'},
    'Penoncito': {'codigo': '25027330', 'nombre': 'Penoncito'},
    'LaGloria': {'codigo': '23217060', 'nombre': 'La Gloria'},
    'GamarraAut': {'codigo': '23217080', 'nombre': 'Gamarra Aut'},
    'ElContento': {'codigo': '23217030', 'nombre': 'El Contento'},
    'SitioNuevo': {'codigo': '23187280', 'nombre': 'Sitio Nuevo'},
    'PuertoWilches': {'codigo': '23187010', 'nombre': 'Puerto Wilches'}
}

def procesar_hoja_wide(file_path, sheet_name):
    """Procesa una hoja en formato wide y devuelve dataframe en formato long"""
    try:
        df_wide = pd.read_excel(file_path, sheet_name=sheet_name)
        
        # Primera columna contiene fechas (mes-dia)
        fecha_col = df_wide.columns[0]
        
        # Columnas de años (1967-2026)
        year_cols = [c for c in df_wide.columns if isinstance(c, int) and 1900 <= c <= 2030]
        
        if not year_cols:
            return None, f"No columnas de años en {sheet_name}"
        
        info = ESTACIONES_INFO.get(sheet_name, {'codigo': '00000000', 'nombre': sheet_name})
        
        registros = []
        
        for idx in range(len(df_wide)):
            row_date = df_wide.iloc[idx, 0]
            if pd.isna(row_date):
                continue
            
            # Convertir a datetime si es string
            if isinstance(row_date, str):
                if row_date in ['Max', 'Min', 'Prom']:
                    continue
                try:
                    row_date = pd.to_datetime(row_date)
                except:
                    continue
            elif not hasattr(row_date, 'month'):
                continue
            
            month = row_date.month
            day = row_date.day
            
            # Para cada año, extraer valor
            for year in year_cols:
                val = df_wide.iloc[idx, df_wide.columns.get_loc(year)]
                if pd.notna(val) and val != 0:
                    try:
                        full_date = datetime(year, month, day)
                        # Formato dd-mm-yyyy
                        fecha_str = full_date.strftime('%d-%m-%Y')
                        registros.append({
                            'CodigoEstacion': info['codigo'],
                            'NombreEstacion': info['nombre'],
                            'Fecha': fecha_str,
                            'Cota': float(val)
                        })
                    except:
                        pass
        
        if not registros:
            return None, f"No registros encontrados en {sheet_name}"
        
        df_long = pd.DataFrame(registros)
        # Ordenar por fecha
        df_long['FechaSort'] = pd.to_datetime(df_long['Fecha'], format='%d-%m-%Y')
        df_long = df_long.sort_values('FechaSort').drop('FechaSort', axis=1)
        
        return df_long, None
        
    except Exception as e:
        return None, f"Error en {sheet_name}: {str(e)}"

def main():
    input_file = r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\backend\data\processed\Resumen_WideFormat_NotProcessedNotImputation.xlsx'
    output_dir = r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\backend\data\processed'
    output_file = os.path.join(output_dir, 'Resumen_LongFormat_NotProcessedNotImputation.csv')
    
    xl = pd.ExcelFile(input_file)
    
    all_data = []
    resumen_estaciones = []
    
    print("Procesando hojas...")
    print("-" * 80)
    
    for sheet in xl.sheet_names:
        if sheet == 'RawAll':
            continue
            
        print(f"Procesando: {sheet}...", end=" ")
        
        df_long, error = procesar_hoja_wide(input_file, sheet)
        
        if error:
            print(f"ERROR: {error}")
            continue
        
        all_data.append(df_long)
        
        # Calcular estadísticos
        fecha_min = pd.to_datetime(df_long['Fecha'], format='%d-%m-%Y').min()
        fecha_max = pd.to_datetime(df_long['Fecha'], format='%d-%m-%Y').max()
        
        resumen_estaciones.append({
            'Hoja': sheet,
            'Codigo': df_long['CodigoEstacion'].iloc[0],
            'Nombre': df_long['NombreEstacion'].iloc[0],
            'Registros': len(df_long),
            'FechaInicio': fecha_min.strftime('%d-%m-%Y'),
            'FechaFin': fecha_max.strftime('%d-%m-%Y'),
            'Anos': fecha_max.year - fecha_min.year + 1
        })
        
        print(f"OK - {len(df_long)} registros")
    
    print("-" * 80)
    
    # Combinar todos los datos
    if all_data:
        df_final = pd.concat(all_data, ignore_index=True)
        
        # Guardar CSV
        df_final.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"\nArchivo guardado: {output_file}")
        print(f"Total registros: {len(df_final):,}")
        
        # Guardar también Excel
        output_excel = output_file.replace('.csv', '.xlsx')
        df_final.to_excel(output_excel, index=False)
        print(f"Archivo Excel: {output_excel}")
        
        # Mostrar resumen
        print("\n" + "=" * 80)
        print("RESUMEN POR ESTACION")
        print("=" * 80)
        print(f"{'Estacion':<20} {'Codigo':<12} {'Registros':<12} {'Inicio':<12} {'Fin':<12} {'Años'}")
        print("-" * 80)
        
        for r in resumen_estaciones:
            print(f"{r['Nombre']:<20} {r['Codigo']:<12} {r['Registros']:<12} {r['FechaInicio']:<12} {r['FechaFin']:<12} {r['Anos']}")
        
        # Calcular y mostrar estadísticos
        print("\n" + "=" * 80)
        print("ESTADISTICOS POR ESTACION (del archivo convertido)")
        print("=" * 80)
        
        df_final['FechaDT'] = pd.to_datetime(df_final['Fecha'], format='%d-%m-%Y')
        df_final['CotaNum'] = pd.to_numeric(df_final['Cota'], errors='coerce')
        
        stats_rows = []
        for codigo in df_final['CodigoEstacion'].unique():
            df_est = df_final[df_final['CodigoEstacion'] == codigo]
            nombre = df_est['NombreEstacion'].iloc[0]
            
            stats = {
                'Codigo': codigo,
                'Nombre': nombre,
                'N': len(df_est),
                'Media': df_est['CotaNum'].mean(),
                'Mediana': df_est['CotaNum'].median(),
                'Std': df_est['CotaNum'].std(),
                'Min': df_est['CotaNum'].min(),
                'Max': df_est['CotaNum'].max(),
                'P10': df_est['CotaNum'].quantile(0.10),
                'P90': df_est['CotaNum'].quantile(0.90)
            }
            stats_rows.append(stats)
        
        df_stats = pd.DataFrame(stats_rows)
        df_stats = df_stats.sort_values('Media')
        
        print(f"{'Nombre':<18} {'Codigo':<10} {'N':<8} {'Media':<8} {'Mediana':<8} {'Std':<7} {'Min':<7} {'Max':<7} {'P10':<7} {'P90':<7}")
        print("-" * 100)
        
        for _, row in df_stats.iterrows():
            print(f"{row['Nombre']:<18} {row['Codigo']:<10} {row['N']:<8} "
                  f"{row['Media']:<8.3f} {row['Mediana']:<8.3f} {row['Std']:<7.3f} "
                  f"{row['Min']:<7.3f} {row['Max']:<7.3f} {row['P10']:<7.3f} {row['P90']:<7.3f}")
        
        # Guardar estadísticos
        stats_file = os.path.join(output_dir, 'Estadisticos_LongFormat.csv')
        df_stats.to_csv(stats_file, index=False)
        print(f"\nEstadísticos guardados en: {stats_file}")
        
    else:
        print("No se procesó ninguna hoja")

if __name__ == "__main__":
    main()
