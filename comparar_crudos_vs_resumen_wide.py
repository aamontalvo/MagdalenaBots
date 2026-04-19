#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comparacion entre datos CRUDOS de archivos Excel originales vs 
Resumen_WideFormat_NotProcessedNotImputation.xlsx (formato wide)
"""

import pandas as pd
import glob
import os
from datetime import datetime
import re

def get_station_name(filename):
    base = os.path.basename(filename)
    name = base.replace('.xlsx', '').replace('_', ' ')
    name = re.sub(r'\s+\d{8,}$', '', name)
    return name.strip()

def find_sheet_name(xl, pattern):
    for sheet in xl.sheet_names:
        if pattern.lower() in sheet.lower():
            return sheet
    return None

def read_crudos_data(file_path):
    try:
        xl = pd.ExcelFile(file_path)
        crudos_sheet = find_sheet_name(xl, 'crudo')
        if not crudos_sheet:
            return None, "No hoja crudos"
        
        df = pd.read_excel(file_path, sheet_name=crudos_sheet)
        
        fecha_col = None
        nivel_col = None
        
        for col in df.columns:
            col_str = str(col).lower()
            if 'fecha' in col_str:
                fecha_col = col
            elif 'cota' in col_str or 'nivel' in col_str:
                nivel_col = col
        
        if not fecha_col or not nivel_col:
            return None, "Columnas no encontradas"
        
        df[fecha_col] = pd.to_datetime(df[fecha_col], errors='coerce')
        df = df.dropna(subset=[fecha_col, nivel_col])
        df = df[df[nivel_col] != 0]
        
        return {
            'min_date': df[fecha_col].min(),
            'max_date': df[fecha_col].max(),
            'count': len(df)
        }, None
        
    except Exception as e:
        return None, str(e)

def read_resumen_wide_data(file_path, sheet_name):
    try:
        df_wide = pd.read_excel(file_path, sheet_name=sheet_name)
        
        # Primera columna contiene fechas (mes-dia)
        fecha_col = df_wide.columns[0]
        
        # Columnas de años (1967-2026)
        year_cols = [c for c in df_wide.columns if isinstance(c, int) and 1900 <= c <= 2030]
        
        if not year_cols:
            return None, "No columnas de años encontradas"
        
        dates_list = []
        
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
            
            # Para cada año, verificar si hay datos
            for year in year_cols:
                val = df_wide.iloc[idx, df_wide.columns.get_loc(year)]
                if pd.notna(val) and val != 0:
                    try:
                        full_date = datetime(year, month, day)
                        dates_list.append(full_date)
                    except:
                        pass
        
        if not dates_list:
            return None, "No datos validos encontrados"
        
        df_result = pd.DataFrame({'fecha': dates_list})
        df_result = df_result.sort_values('fecha')
        
        return {
            'min_date': df_result['fecha'].min(),
            'max_date': df_result['fecha'].max(),
            'count': len(df_result)
        }, None
        
    except Exception as e:
        return None, str(e)

def map_station_to_sheet(station_name):
    """Mapea nombre de estacion a nombre de hoja en el archivo resumen"""
    mapping = {
        'ARMENIA': 'Armenia',
        'BARBOSA': 'Barbosa',
        'CALAMAR': 'Calamar',
        'COYONGAL': 'Coyongal',
        'EL BANCO - AUT': 'ElBanco',
        'EL CONTENTO': 'ElContento',
        'GAMARRA - AUT': 'GamarraAut',
        'LAS AGUADAS': 'LasAguadas',
        'LAS PALOMAS': 'LasPalomas',
        'LA GLORIA': 'LaGloria',
        'MAGANGUE': 'Magangue',
        'PENONCITO': 'Penoncito',
        'PLATO MAGDALENA AUT': 'Plato',
        'PUERTO WILCHES': 'PuertoWilches',
        'RIO NUEVO': 'RioNuevo',
        'SAN PEDRITO - AUT': 'SanPedrito',
        'SITIO NUEVO': 'SitioNuevo',
        'TENERIFE': 'Tenerife'
    }
    
    # Limpiar nombre de estacion
    clean_name = station_name.replace('23217060', '').strip()
    return mapping.get(clean_name, None)

def main():
    raw_path = r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\backend\data\raw\SERIE NIVELES IDEAM A 2026'
    resumen_file = r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\backend\data\processed\Resumen_WideFormat_NotProcessedNotImputation.xlsx'
    
    excel_files = glob.glob(os.path.join(raw_path, '*.xlsx'))
    
    results = []
    
    for file_path in sorted(excel_files):
        station_name = get_station_name(file_path)
        sheet_name = map_station_to_sheet(station_name)
        
        # Leer datos crudos del archivo original
        crudos_data, crudos_error = read_crudos_data(file_path)
        
        # Leer datos del resumen wide
        if sheet_name:
            resumen_data, resumen_error = read_resumen_wide_data(resumen_file, sheet_name)
        else:
            resumen_data, resumen_error = None, "No mapeo encontrado"
        
        results.append({
            'station': station_name,
            'sheet': sheet_name,
            'crudos': crudos_data,
            'resumen': resumen_data
        })
    
    # Guardar resultados
    output_file = 'comparacion_crudos_vs_resumen_wide.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 120 + "\n")
        f.write("COMPARACION: DATOS CRUDOS (originales) vs RESUMEN WIDE FORMAT\n")
        f.write("=" * 120 + "\n")
        f.write(f"{'Estacion':<35} {'Formato':<12} {'Inicio':<14} {'Fin':<14} {'Registros':<12} {'Rango'}\n")
        f.write("-" * 120 + "\n")
        
        for r in results:
            station = r['station']
            crudos = r['crudos']
            resumen = r['resumen']
            
            if crudos:
                year_range = crudos['max_date'].year - crudos['min_date'].year + 1
                f.write(f"{station:<35} {'CRUDOS':<12} {str(crudos['min_date'].date()):<14} "
                      f"{str(crudos['max_date'].date()):<14} {crudos['count']:<12} {year_range} años\n")
            else:
                f.write(f"{station:<35} {'CRUDOS':<12} ERROR\n")
            
            if resumen:
                year_range = resumen['max_date'].year - resumen['min_date'].year + 1
                f.write(f"{station:<35} {'RESUMEN':<12} {str(resumen['min_date'].date()):<14} "
                      f"{str(resumen['max_date'].date()):<14} {resumen['count']:<12} {year_range} años\n")
            else:
                f.write(f"{station:<35} {'RESUMEN':<12} ERROR: {r.get('error', 'No data')}\n")
            
            f.write("-" * 120 + "\n")
        
        # Analisis de discrepancias
        f.write("\n")
        f.write("=" * 120 + "\n")
        f.write("ANALISIS DE DISCREPANCIAS CRUDOS vs RESUMEN WIDE\n")
        f.write("=" * 120 + "\n")
        
        for r in results:
            station = r['station']
            crudos = r['crudos']
            resumen = r['resumen']
            
            f.write(f"\n[+] {station} (Hoja: {r['sheet']})\n")
            f.write("-" * 80 + "\n")
            
            if not crudos and not resumen:
                f.write("   [!] No se pudieron leer datos de ningun formato\n")
                continue
            
            if not crudos:
                f.write(f"   [!] CRUDOS: Error\n")
                if resumen:
                    f.write(f"   [OK] RESUMEN: {resumen['count']} registros desde {resumen['min_date'].date()}\n")
                continue
            
            if not resumen:
                f.write(f"   [OK] CRUDOS: {crudos['count']} registros desde {crudos['min_date'].date()}\n")
                f.write(f"   [!] RESUMEN: Error o sin mapeo\n")
                continue
            
            diff_start = (crudos['min_date'] - resumen['min_date']).days
            diff_end = (crudos['max_date'] - resumen['max_date']).days
            diff_count = crudos['count'] - resumen['count']
            
            # Fecha de inicio
            if diff_start > 0:
                years = diff_start / 365.25
                f.write(f"   [DIF] INICIO: RESUMEN tiene {years:.1f} años mas de datos historicos\n")
                f.write(f"              RESUMEN: {resumen['min_date'].date()} | Crudos: {crudos['min_date'].date()}\n")
            elif diff_start < 0:
                years = abs(diff_start) / 365.25
                f.write(f"   [DIF] INICIO: CRUDOS tiene {years:.1f} años mas de datos historicos\n")
                f.write(f"              Crudos: {crudos['min_date'].date()} | RESUMEN: {resumen['min_date'].date()}\n")
            else:
                f.write(f"   [OK] INICIO: Ambos coinciden ({crudos['min_date'].date()})\n")
            
            # Fecha de fin
            if diff_end < 0:
                f.write(f"   [DIF] FIN: RESUMEN tiene {abs(diff_end)} dias mas de datos recientes\n")
                f.write(f"           RESUMEN: {resumen['max_date'].date()} | Crudos: {crudos['max_date'].date()}\n")
            elif diff_end > 0:
                f.write(f"   [DIF] FIN: CRUDOS tiene {diff_end} dias mas de datos recientes\n")
                f.write(f"           Crudos: {crudos['max_date'].date()} | RESUMEN: {resumen['max_date'].date()}\n")
            else:
                f.write(f"   [OK] FIN: Ambos coinciden ({crudos['max_date'].date()})\n")
            
            # Cantidad de registros
            if diff_count != 0:
                pct = (diff_count / max(resumen['count'], 1)) * 100
                f.write(f"   [DIF] REGISTROS: Diferencia de {diff_count} registros ({pct:+.1f}%)\n")
                f.write(f"                 Crudos: {crudos['count']} | RESUMEN: {resumen['count']}\n")
            else:
                f.write(f"   [OK] REGISTROS: Misma cantidad ({crudos['count']})\n")
            
            # Años cubiertos
            years_crudos = crudos['max_date'].year - crudos['min_date'].year + 1
            years_resumen = resumen['max_date'].year - resumen['min_date'].year + 1
            
            if years_crudos != years_resumen:
                f.write(f"   [DIF] AÑOS: Crudos={years_crudos} años, RESUMEN={years_resumen} años\n")
                if years_resumen > years_crudos:
                    f.write(f"              RESUMEN tiene {years_resumen - years_crudos} años adicionales\n")
        
        # Resumen general
        f.write("\n")
        f.write("=" * 120 + "\n")
        f.write("RESUMEN GENERAL DE HALLAZGOS\n")
        f.write("=" * 120 + "\n")
        
        more_in_resumen = []
        more_in_crudos = []
        equal = []
        errors = []
        
        for r in results:
            crudos = r['crudos']
            resumen = r['resumen']
            
            if not crudos or not resumen:
                errors.append(r['station'])
                continue
            
            diff_start = (crudos['min_date'] - resumen['min_date']).days
            diff_end = (crudos['max_date'] - resumen['max_date']).days
            
            if diff_start > 0:
                more_in_resumen.append({'station': r['station'], 'extra': diff_start})
            elif diff_start < 0:
                more_in_crudos.append({'station': r['station'], 'extra': abs(diff_start)})
            
            if diff_start == 0 and diff_end == 0 and (crudos['count'] == resumen['count']):
                equal.append(r['station'])
        
        f.write(f"\n[ESTADISTICAS]\n")
        f.write(f"  Total estaciones: {len(results)}\n")
        f.write(f"  Datos identicos: {len(equal)}\n")
        f.write(f"  Con diferencias o errores: {len(results) - len(equal)}\n")
        f.write(f"  Errores de lectura: {len(errors)}\n")
        
        if more_in_resumen:
            f.write(f"\n[HALLAZGO] Estaciones donde RESUMEN tiene mas datos historicos:\n")
            for s in more_in_resumen:
                years = s['extra'] / 365.25
                f.write(f"    - {s['station']}: {years:.1f} años adicionales\n")
        
        if more_in_crudos:
            f.write(f"\n[NOTA] Estaciones donde CRUDOS tiene mas datos historicos:\n")
            for s in more_in_crudos:
                years = s['extra'] / 365.25
                f.write(f"    - {s['station']}: {years:.1f} años adicionales\n")
        
        f.write("\n" + "=" * 120 + "\n")
    
    print(f"Resultados guardados en: {output_file}")

if __name__ == "__main__":
    main()
