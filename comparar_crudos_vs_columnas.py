#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comparacion entre datos de hojas Crudos vs hojas Columnas (wide format)
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
    return name

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

def read_columnas_data(file_path):
    try:
        xl = pd.ExcelFile(file_path)
        
        columnas_sheet = None
        for sheet in xl.sheet_names:
            if 'columnas' in sheet.lower():
                columnas_sheet = sheet
                break
        
        if not columnas_sheet:
            return None, "No hoja columnas"
        
        df_wide = pd.read_excel(file_path, sheet_name=columnas_sheet, header=None)
        
        years_row = df_wide.iloc[0, 1:].values
        
        valid_years = []
        year_cols = []
        for i, val in enumerate(years_row):
            if pd.notna(val) and isinstance(val, (int, float)):
                year = int(val)
                if 1900 <= year <= 2030:
                    valid_years.append(year)
                    year_cols.append(i + 1)
        
        if not valid_years:
            return None, "No anos validos"
        
        dates_list = []
        values_list = []
        
        for idx in range(1, len(df_wide)):
            row_date = df_wide.iloc[idx, 0]
            if pd.isna(row_date):
                continue
            
            if isinstance(row_date, str):
                try:
                    row_date = pd.to_datetime(row_date)
                except:
                    continue
            
            if hasattr(row_date, 'month') and hasattr(row_date, 'day'):
                month = row_date.month
                day = row_date.day
            else:
                continue
            
            for year, col_idx in zip(valid_years, year_cols):
                val = df_wide.iloc[idx, col_idx]
                if pd.notna(val) and val != 0:
                    try:
                        full_date = datetime(year, month, day)
                        dates_list.append(full_date)
                        values_list.append(float(val))
                    except:
                        pass
        
        if not dates_list:
            return None, "No datos validos"
        
        df_result = pd.DataFrame({'fecha': dates_list, 'valor': values_list})
        df_result = df_result.sort_values('fecha')
        
        return {
            'min_date': df_result['fecha'].min(),
            'max_date': df_result['fecha'].max(),
            'count': len(df_result)
        }, None
        
    except Exception as e:
        return None, str(e)

def main():
    base_path = r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\backend\data\raw\SERIE NIVELES IDEAM A 2026'
    
    excel_files = glob.glob(os.path.join(base_path, '*.xlsx'))
    
    results = []
    
    for file_path in sorted(excel_files):
        station_name = get_station_name(file_path)
        
        crudos_data, crudos_error = read_crudos_data(file_path)
        columnas_data, columnas_error = read_columnas_data(file_path)
        
        results.append({
            'station': station_name,
            'crudos': crudos_data,
            'columnas': columnas_data
        })
    
    # Guardar resultados a archivo
    output_file = 'comparacion_crudos_columnas.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 120 + "\n")
        f.write("COMPARACION: DATOS CRUDOS vs DATOS COLUMNAS (WIDE FORMAT)\n")
        f.write("=" * 120 + "\n")
        f.write(f"{'Estacion':<35} {'Formato':<12} {'Inicio':<14} {'Fin':<14} {'Registros':<12} {'Rango'}\n")
        f.write("-" * 120 + "\n")
        
        for r in results:
            station = r['station']
            crudos = r['crudos']
            columnas = r['columnas']
            
            if crudos:
                year_range = crudos['max_date'].year - crudos['min_date'].year + 1
                f.write(f"{station:<35} {'CRUDOS':<12} {str(crudos['min_date'].date()):<14} "
                      f"{str(crudos['max_date'].date()):<14} {crudos['count']:<12} {year_range} años\n")
            else:
                f.write(f"{station:<35} {'CRUDOS':<12} ERROR\n")
            
            if columnas:
                year_range = columnas['max_date'].year - columnas['min_date'].year + 1
                f.write(f"{station:<35} {'COLUMNAS':<12} {str(columnas['min_date'].date()):<14} "
                      f"{str(columnas['max_date'].date()):<14} {columnas['count']:<12} {year_range} años\n")
            else:
                f.write(f"{station:<35} {'COLUMNAS':<12} ERROR\n")
            
            f.write("-" * 120 + "\n")
        
        # Analisis de discrepancias
        f.write("\n")
        f.write("=" * 120 + "\n")
        f.write("ANALISIS DE DISCREPANCIAS CRUDOS vs COLUMNAS\n")
        f.write("=" * 120 + "\n")
        
        for r in results:
            station = r['station']
            crudos = r['crudos']
            columnas = r['columnas']
            
            f.write(f"\n[+] {station}\n")
            f.write("-" * 80 + "\n")
            
            if not crudos and not columnas:
                f.write("   [!] No se pudieron leer datos de ningun formato\n")
                continue
            
            if not crudos:
                f.write(f"   [!] CRUDOS: Error\n")
                if columnas:
                    f.write(f"   [OK] COLUMNAS: {columnas['count']} registros desde {columnas['min_date'].date()}\n")
                continue
            
            if not columnas:
                f.write(f"   [OK] CRUDOS: {crudos['count']} registros desde {crudos['min_date'].date()}\n")
                f.write(f"   [!] COLUMNAS: Error\n")
                continue
            
            diff_start = (crudos['min_date'] - columnas['min_date']).days
            diff_end = (crudos['max_date'] - columnas['max_date']).days
            diff_count = crudos['count'] - columnas['count']
            
            # Fecha de inicio
            if diff_start > 0:
                years = diff_start / 365.25
                f.write(f"   [DIF] INICIO: Columnas tiene {years:.1f} años mas de datos historicos\n")
                f.write(f"              Columnas: {columnas['min_date'].date()} | Crudos: {crudos['min_date'].date()}\n")
            elif diff_start < 0:
                years = abs(diff_start) / 365.25
                f.write(f"   [DIF] INICIO: Crudos tiene {years:.1f} años mas de datos historicos\n")
                f.write(f"              Crudos: {crudos['min_date'].date()} | Columnas: {columnas['min_date'].date()}\n")
            else:
                f.write(f"   [OK] INICIO: Ambos coinciden ({crudos['min_date'].date()})\n")
            
            # Fecha de fin
            if diff_end < 0:
                f.write(f"   [DIF] FIN: Columnas tiene {abs(diff_end)} dias mas de datos recientes\n")
                f.write(f"           Columnas: {columnas['max_date'].date()} | Crudos: {crudos['max_date'].date()}\n")
            elif diff_end > 0:
                f.write(f"   [DIF] FIN: Crudos tiene {diff_end} dias mas de datos recientes\n")
                f.write(f"           Crudos: {crudos['max_date'].date()} | Columnas: {columnas['max_date'].date()}\n")
            else:
                f.write(f"   [OK] FIN: Ambos coinciden ({crudos['max_date'].date()})\n")
            
            # Cantidad de registros
            if diff_count != 0:
                pct = (diff_count / max(columnas['count'], 1)) * 100
                f.write(f"   [DIF] REGISTROS: Diferencia de {diff_count} registros ({pct:+.1f}%)\n")
                f.write(f"                 Crudos: {crudos['count']} | Columnas: {columnas['count']}\n")
            else:
                f.write(f"   [OK] REGISTROS: Misma cantidad ({crudos['count']})\n")
            
            # Anos cubiertos
            years_crudos = crudos['max_date'].year - crudos['min_date'].year + 1
            years_columnas = columnas['max_date'].year - columnas['min_date'].year + 1
            
            if years_crudos != years_columnas:
                f.write(f"   [DIF] AÑOS: Crudos={years_crudos} años, Columnas={years_columnas} años\n")
                if years_columnas > years_crudos:
                    f.write(f"              Columnas tiene {years_columnas - years_crudos} años adicionales\n")
        
        # Resumen general
        f.write("\n")
        f.write("=" * 120 + "\n")
        f.write("RESUMEN GENERAL DE HALLAZGOS\n")
        f.write("=" * 120 + "\n")
        
        more_in_columnas = []
        more_in_crudos = []
        differences = []
        equal = []
        
        for r in results:
            crudos = r['crudos']
            columnas = r['columnas']
            
            if crudos and columnas:
                diff_start = (crudos['min_date'] - columnas['min_date']).days
                diff_end = (crudos['max_date'] - columnas['max_date']).days
                
                if diff_start > 0:
                    more_in_columnas.append({'station': r['station'], 'extra': diff_start})
                elif diff_start < 0:
                    more_in_crudos.append({'station': r['station'], 'extra': abs(diff_start)})
                
                if diff_start != 0 or diff_end != 0 or (crudos['count'] != columnas['count']):
                    differences.append(r['station'])
                else:
                    equal.append(r['station'])
        
        f.write(f"\n[ESTADISTICAS]\n")
        f.write(f"  Total estaciones: {len(results)}\n")
        f.write(f"  Datos identicos: {len(equal)}\n")
        f.write(f"  Con diferencias: {len(differences)}\n")
        
        if more_in_columnas:
            f.write(f"\n[HALLAZGO CRITICO] Estaciones donde COLUMNAS tiene mas datos historicos:\n")
            for s in more_in_columnas:
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
