#!/usr/bin/env python3
"""
Analisis Exploratorio de Datos - Niveles del Rio Magdalena
==========================================================

Este script realiza un analisis inicial de la calidad de datos de cotas 
absolutas (msnm) de estaciones del IDEAM en el rio Magdalena.

Autor: MagdalenaBot Hydrology Team
Fecha: 2026-02-25
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# Configuracion de estilo minimalista
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("Blues")

# Constantes
RAW_DATA_PATH = Path(r"C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\backend\data\raw\RawData\SERIE NIVELES IDEAM A 2026")
OUTPUT_PATH = Path(r"C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\backend\data\analysis_output")
MISSING_VALUE_CODE = -9999

# Orden geografico: aguas arriba -> aguas abajo (invertido del orden del usuario)
# Segun el usuario: su lista es aguas abajo -> aguas arriba
GEOGRAPHIC_ORDER = [
    'Barrancabermeja',   # Aguas arriba (no disponible)
    'Puerto Wilches',    # [OK] Disponible
    'San Pablo',         # No disponible
    'Sitio Nuevo',       # [OK] Disponible (23187280)
    'Badillo',           # No disponible
    'El Contento',       # [OK] Disponible
    'Gamarra Aut',       # [OK] Disponible (como GAMARRA_-_AUT_)
    'Gamarra',           # No disponible (separada de Gamarra Aut)
    'La Gloria',         # [OK] Disponible
    'Penoncito',         # [OK] Disponible
    'El Banco',          # [OK] Disponible
    'La Aguadas',        # [OK] Disponible (como LAS_AGUADAS)
    'Las Palomas',       # [OK] Disponible
    'Rio Nuevo',         # [OK] Disponible
    'Armenia',           # [OK] Disponible
    'Coyongal',          # [OK] Disponible
    'Sitio Nuevo',       # Segunda mencion - misma estacion
    'Barbosa',           # [OK] Disponible
    'Planta Bomba Ecopetrol',  # No disponible
    'Magangue',          # [OK] Disponible
    'Tacamocho',         # No disponible
    'Plato',             # [OK] Disponible
    'Tenerife',          # [OK] Disponible
    'Barrancavieja',     # No disponible
    'Calamar',           # [OK] Disponible (mas antigua, desde 1967)
    'San Pedrito',       # [OK] Disponible
    'Sitio Nuevo (Remolino)',  # No disponible
    'Tebsa',             # Aguas abajo (no disponible)
]

# Mapeo de archivos a nombres estandarizados
STATION_MAPPING = {
    'ARMENIA_25027360.xlsx': {'name': 'Armenia', 'code': '25027360', 'order': 14},
    'BARBOSA_25027530.xlsx': {'name': 'Barbosa', 'code': '25027530', 'order': 17},
    'CALAMAR_29037020.xlsx': {'name': 'Calamar', 'code': '29037020', 'order': 25},
    'COYONGAL_25027930.xlsx': {'name': 'Coyongal', 'code': '25027930', 'order': 15},
    'EL_BANCO_-_AUT_25027020.xlsx': {'name': 'El Banco', 'code': '25027020', 'order': 11},
    'EL_CONTENTO_23217030.xlsx': {'name': 'El Contento', 'code': '23217030', 'order': 6},
    'GAMARRA_-_AUT_23217080.xlsx': {'name': 'Gamarra Aut', 'code': '23217080', 'order': 7},
    'LAS_AGUADAS_25027490.xlsx': {'name': 'Las Aguadas', 'code': '25027490', 'order': 12},
    'LAS_PALOMAS_25027390.xlsx': {'name': 'Las Palomas', 'code': '25027390', 'order': 13},
    'LA_GLORIA23217060.xlsx': {'name': 'La Gloria', 'code': '23217060', 'order': 10},
    'MAGANGUE_25027680.xlsx': {'name': 'Magangue', 'code': '25027680', 'order': 20},
    'PENONCITO_25027330.xlsx': {'name': 'Penoncito', 'code': '25027330', 'order': 9},
    'PLATO_MAGDALENA_AUT_25027450.xlsx': {'name': 'Plato', 'code': '25027450', 'order': 22},
    'PUERTO_WILCHES_23187010.xlsx': {'name': 'Puerto Wilches', 'code': '23187010', 'order': 2},
    'RIO_NUEVO_25027630.xlsx': {'name': 'Rio Nuevo', 'code': '25027630', 'order': 14},
    'SAN_PEDRITO_-_AUT_29047070.xlsx': {'name': 'San Pedrito', 'code': '29047070', 'order': 26},
    'SITIO_NUEVO_23187280.xlsx': {'name': 'Sitio Nuevo', 'code': '23187280', 'order': 4},
    'TENERIFE_29017010.xlsx': {'name': 'Tenerife', 'code': '29017010', 'order': 23},
}


class MagdalenaDataAnalyzer:
    """Analizador de datos de niveles del rio Magdalena."""
    
    def __init__(self):
        self.raw_data = {}  # Datos en formato wide (originales)
        self.long_data = []  # Datos en formato long
        self.station_metadata = {}  # Metadatos por estacion
        self.OUTPUT_PATH = OUTPUT_PATH
        self.OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
        
    def load_all_stations(self) -> Dict[str, pd.DataFrame]:
        """
        Carga todos los archivos Excel de estaciones.
        
        Returns:
            Diccionario con DataFrames por estacion
        """
        print("=" * 70)
        print("CARGA DE DATOS RAW - NIVELES MAGDALENA")
        print("=" * 70)
        
        for filename, info in STATION_MAPPING.items():
            filepath = RAW_DATA_PATH / filename
            if filepath.exists():
                try:
                    # Leer primera hoja
                    df = pd.read_excel(filepath, sheet_name=0)
                    
                    # Extraer metadatos
                    year_cols = [c for c in df.columns 
                                if isinstance(c, int) and 1900 < c < 2100]
                    
                    self.station_metadata[info['name']] = {
                        'code': info['code'],
                        'filename': filename,
                        'order': info['order'],
                        'years': year_cols,
                        'start_year': min(year_cols) if year_cols else None,
                        'end_year': max(year_cols) if year_cols else None,
                        'total_years': len(year_cols),
                        'shape': df.shape
                    }
                    
                    self.raw_data[info['name']] = df
                    print(f"[OK] {info['name']:20s} ({info['code']}): "
                          f"{len(year_cols)} anos [{min(year_cols)}-{max(year_cols)}]")
                    
                except Exception as e:
                    print(f"[ERROR] {filename}: {e}")
            else:
                print(f"[NO FOUND] {filename}")
        
        print(f"\nTotal estaciones cargadas: {len(self.raw_data)}")
        print("=" * 70)
        return self.raw_data
    
    def convert_to_long_format(self) -> pd.DataFrame:
        """
        Convierte datos de formato wide a long.
        
        Estructura de salida:
        - fecha: datetime
        - nivel_msnm: float (cota absoluta)
        - estacion: str
        - codigo_ideam: str
        - anio: int
        - mes: int
        - dia: int
        
        Returns:
            DataFrame en formato long
        """
        print("\nConvirtiendo a formato LONG...")
        
        long_records = []
        
        for station_name, df in self.raw_data.items():
            metadata = self.station_metadata[station_name]
            year_cols = metadata['years']
            
            # La primera columna contiene las fechas (mes-dia)
            date_col = df.columns[0]
            
            for year in year_cols:
                if year not in df.columns:
                    continue
                    
                for idx, row in df.iterrows():
                    # Obtener mes-dia de la primera columna
                    date_val = row[date_col]
                    
                    # Parsear fecha segun el tipo
                    if pd.isna(date_val):
                        continue
                    
                    try:
                        from datetime import datetime
                        if isinstance(date_val, (pd.Timestamp, datetime)):
                            month = date_val.month
                            day = date_val.day
                        elif isinstance(date_val, str):
                            # Intentar parsear string
                            parts = str(date_val).split('-')
                            if len(parts) >= 3:
                                month = int(parts[1])
                                day = int(parts[2].split()[0])
                            else:
                                continue
                        else:
                            continue
                        
                        # Crear fecha completa
                        try:
                            full_date = pd.Timestamp(year=year, month=month, day=day)
                        except ValueError:
                            # Fecha invalida (ej: 29 feb en ano no bisiesto)
                            continue
                        
                        # Obtener valor de nivel
                        level_value = row[year]
                        
                        # Validar valor
                        if pd.isna(level_value):
                            level_value = np.nan
                        elif isinstance(level_value, (int, float)):
                            # Reemplazar valores obvios de error con NaN
                            if level_value < -100 or level_value > 1000:
                                level_value = np.nan
                        else:
                            level_value = np.nan
                        
                        long_records.append({
                            'fecha': full_date,
                            'anio': year,
                            'mes': month,
                            'dia': day,
                            'nivel_msnm': level_value,
                            'estacion': station_name,
                            'codigo_ideam': metadata['code']
                        })
                        
                    except Exception as e:
                        continue
        
        # Crear DataFrame
        df_long = pd.DataFrame(long_records)
        
        # Ordenar
        df_long = df_long.sort_values(['estacion', 'fecha']).reset_index(drop=True)
        
        print(f"Registros totales en formato long: {len(df_long):,}")
        print(f"Estaciones: {df_long['estacion'].nunique()}")
        print(f"Rango temporal: {df_long['fecha'].min()} a {df_long['fecha'].max()}")
        
        self.long_data = df_long
        return df_long
    
    def generate_null_heatmap(self) -> Tuple[plt.Figure, pd.DataFrame]:
        """
        Genera heatmap de datos nulos por estacion y ano.
        
        Returns:
            Tupla de (figura, DataFrame de resumen)
        """
        print("\nGenerando heatmap de datos nulos...")
        
        # Crear matriz de cobertura
        df = self.long_data.copy()
        
        # Agrupar por estacion y anio
        coverage = df.groupby(['estacion', 'anio']).agg({
            'nivel_msnm': lambda x: x.notna().sum()
        }).reset_index()
        
        # Pivotar para heatmap
        coverage_matrix = coverage.pivot(index='estacion', columns='anio', values='nivel_msnm')
        
        # Ordenar por orden geografico (aguas arriba -> abajo)
        order_dict = {info['name']: info['order'] for _, info in STATION_MAPPING.items()}
        coverage_matrix['order'] = coverage_matrix.index.map(order_dict)
        coverage_matrix = coverage_matrix.sort_values('order', ascending=False)
        coverage_matrix = coverage_matrix.drop('order', axis=1)
        
        # Calcular matriz de nulos (esperados - observados)
        # Ano bisiesto = 366, normal = 365
        expected_days = {}
        for year in coverage_matrix.columns:
            is_leap = (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
            expected_days[year] = 366 if is_leap else 365
        
        null_matrix = coverage_matrix.copy()
        for col in null_matrix.columns:
            null_matrix[col] = expected_days.get(col, 365) - null_matrix[col].fillna(0)
        
        # Determinar anos de instalacion (cuando la estacion comenzo a operar)
        installation_years = {}
        for station in null_matrix.index:
            station_data = df[df['estacion'] == station]
            if not station_data.empty:
                first_valid = station_data[station_data['nivel_msnm'].notna()]
                if not first_valid.empty:
                    installation_years[station] = first_valid['anio'].min()
                else:
                    installation_years[station] = None
            else:
                installation_years[station] = None
        
        # Crear figura con estilo minimalista
        fig, ax = plt.subplots(figsize=(16, 10))
        
        # Colores: blanco (0 nulos) -> gris -> azul oscuro (muchos nulos)
        cmap = sns.color_palette("Blues", as_cmap=True)
        
        # Dibujar heatmap
        sns.heatmap(null_matrix, 
                   cmap=cmap,
                   cbar_kws={'label': 'Dias sin datos'},
                   linewidths=0.5,
                   linecolor='white',
                   ax=ax,
                   vmin=0,
                   vmax=366)
        
        # Agregar hatch pattern para anos antes de instalacion
        for i, station in enumerate(null_matrix.index):
            install_year = installation_years.get(station)
            if install_year:
                for j, year in enumerate(null_matrix.columns):
                    if year < install_year:
                        # Dibujar X (tachado) para anos antes de instalacion
                        ax.plot([j, j+1], [i, i+1], 'k-', linewidth=0.5, alpha=0.3)
                        ax.plot([j, j+1], [i+1, i], 'k-', linewidth=0.5, alpha=0.3)
        
        # Configurar ejes
        ax.set_xlabel('Ano', fontsize=12, fontweight='bold')
        ax.set_ylabel('Estacion (aguas arriba -> abajo)', fontsize=12, fontweight='bold')
        ax.set_title('Mapa de Calor: Datos Faltantes por Estacion y Ano\n'
                    '(X = Estacion aun no instalada)', 
                    fontsize=14, fontweight='bold', pad=20)
        
        # Rotar etiquetas de anos
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        
        plt.tight_layout()
        
        # Guardar
        output_file = self.OUTPUT_PATH / 'heatmap_nulls.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"Guardado: {output_file}")
        
        # Crear resumen
        summary_data = []
        for station in coverage_matrix.index:
            row_data = coverage_matrix.loc[station]
            null_row = null_matrix.loc[station]
            
            total_expected = sum(expected_days.get(y, 365) for y in row_data.index if pd.notna(row_data[y]) or pd.notna(null_row[y]))
            total_nulls = null_row.sum()
            
            summary_data.append({
                'Estacion': station,
                'Codigo': self.station_metadata[station]['code'],
                'Anio_Inicio': installation_years.get(station),
                'Anio_Fin': self.station_metadata[station]['end_year'],
                'Total_Anios': len([y for y in row_data.index if pd.notna(row_data[y])]),
                'Dias_Esperados': int(total_expected),
                'Dias_Nulos': int(total_nulls),
                'Completitud_Pct': round(100 * (1 - total_nulls/total_expected), 1) if total_expected > 0 else 0
            })
        
        summary_df = pd.DataFrame(summary_data)
        summary_df = summary_df.sort_values('Anio_Inicio', na_position='last')
        
        return fig, summary_df
    
    def generate_distribution_plots(self) -> plt.Figure:
        """
        Genera boxplots/violin plots de distribucion por estacion.
        
        Returns:
            Figura de matplotlib
        """
        print("\nGenerando graficos de distribucion...")
        
        df = self.long_data.copy()
        
        # Filtrar valores validos
        df_valid = df[df['nivel_msnm'].notna()].copy()
        
        # Ordenar por ubicacion geografica (aguas arriba -> abajo)
        order_dict = {info['name']: info['order'] for _, info in STATION_MAPPING.items()}
        df_valid['order'] = df_valid['estacion'].map(order_dict)
        
        # Obtener orden unico de estaciones
        station_order = df_valid.groupby('estacion')['order'].first().sort_values(ascending=False).index.tolist()
        
        # Crear figura con dos subplots
        fig, axes = plt.subplots(2, 1, figsize=(16, 14))
        
        # Colores minimalistas
        box_color = '#4A6FA5'  # Azul medio
        
        # 1. Boxplot
        ax1 = axes[0]
        
        # Preparar datos para boxplot
        data_for_box = []
        labels = []
        for station in station_order:
            station_values = df_valid[df_valid['estacion'] == station]['nivel_msnm'].values
            if len(station_values) > 0:
                data_for_box.append(station_values)
                labels.append(station)
        
        bp = ax1.boxplot(data_for_box, labels=labels, patch_artist=True,
                        boxprops=dict(facecolor=box_color, alpha=0.7, edgecolor='white'),
                        medianprops=dict(color='white', linewidth=2),
                        whiskerprops=dict(color='#666666'),
                        capprops=dict(color='#666666'),
                        flierprops=dict(marker='o', markerfacecolor='#333333', 
                                       markersize=3, alpha=0.5))
        
        ax1.set_xlabel('Estacion (aguas arriba -> abajo)', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Cota (m.s.n.m.)', fontsize=12, fontweight='bold')
        ax1.set_title('Diagrama de Cajas: Distribucion de Cotas por Estacion\n'
                     '(Valores atipicos mostrados como puntos)', 
                     fontsize=13, fontweight='bold')
        
        plt.sca(ax1)
        plt.xticks(rotation=45, ha='right')
        ax1.grid(axis='y', alpha=0.3)
        
        # 2. Violin plot con seaborn
        ax2 = axes[1]
        
        sns.violinplot(data=df_valid, x='estacion', y='nivel_msnm', 
                      order=station_order,
                      palette='Blues', ax=ax2, inner='box',
                      linewidth=1)
        
        ax2.set_xlabel('Estacion (aguas arriba -> abajo)', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Cota (m.s.n.m.)', fontsize=12, fontweight='bold')
        ax2.set_title('Grafico de Violin: Densidad de Probabilidad de Cotas\n'
                     '(Ancho indica frecuencia de valores)', 
                     fontsize=13, fontweight='bold')
        
        plt.sca(ax2)
        plt.xticks(rotation=45, ha='right')
        
        plt.tight_layout()
        
        # Guardar
        output_file = self.OUTPUT_PATH / 'distribution_analysis.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"Guardado: {output_file}")
        
        return fig
    
    def generate_outlier_analysis(self) -> pd.DataFrame:
        """
        Analisis estadistico de outliers por estacion.
        
        Returns:
            DataFrame con estadisticas de outliers
        """
        print("\nAnalizando outliers...")
        
        df = self.long_data.copy()
        
        outlier_stats = []
        
        for station in df['estacion'].unique():
            station_data = df[(df['estacion'] == station) & (df['nivel_msnm'].notna())]['nivel_msnm']
            
            if len(station_data) < 10:
                continue
            
            # Calcular IQR
            Q1 = station_data.quantile(0.25)
            Q3 = station_data.quantile(0.75)
            IQR = Q3 - Q1
            
            # Limites de outliers
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            # Contar outliers
            outliers_low = (station_data < lower_bound).sum()
            outliers_high = (station_data > upper_bound).sum()
            outliers_total = outliers_low + outliers_high
            
            # Estadisticas
            outlier_stats.append({
                'Estacion': station,
                'Codigo': self.station_metadata[station]['code'],
                'N_Registros': len(station_data),
                'Media': round(station_data.mean(), 2),
                'Mediana': round(station_data.median(), 2),
                'Desv_Est': round(station_data.std(), 2),
                'Min': round(station_data.min(), 2),
                'Max': round(station_data.max(), 2),
                'Q1': round(Q1, 2),
                'Q3': round(Q3, 2),
                'IQR': round(IQR, 2),
                'Limite_Inferior': round(lower_bound, 2),
                'Limite_Superior': round(upper_bound, 2),
                'Outliers_Inferiores': int(outliers_low),
                'Outliers_Superiores': int(outliers_high),
                'Total_Outliers': int(outliers_total),
                'Porcentaje_Outliers': round(100 * outliers_total / len(station_data), 2)
            })
        
        stats_df = pd.DataFrame(outlier_stats)
        
        # Ordenar por orden geografico
        order_dict = {info['name']: info['order'] for _, info in STATION_MAPPING.items()}
        stats_df['order'] = stats_df['Estacion'].map(order_dict)
        stats_df = stats_df.sort_values('order', ascending=False).drop('order', axis=1)
        
        return stats_df
    
    def export_to_csv(self):
        """Exporta el dataset long a CSV."""
        output_file = self.OUTPUT_PATH / 'magdalena_levels_long_format.csv'
        self.long_data.to_csv(output_file, index=False, encoding='utf-8')
        print(f"\nDataset long exportado: {output_file}")
        print(f"Total registros: {len(self.long_data):,}")
        
    def run_full_analysis(self):
        """Ejecuta el analisis completo."""
        print("\n" + "=" * 70)
        print("ANALISIS EXPLORATORIO - NIVELES RIO MAGDALENA")
        print("=" * 70)
        
        # 1. Cargar datos
        self.load_all_stations()
        
        # 2. Convertir a long
        self.convert_to_long_format()
        
        # 3. Generar visualizaciones
        fig_heatmap, summary_df = self.generate_null_heatmap()
        fig_dist = self.generate_distribution_plots()
        
        # 4. Analisis de outliers
        outlier_df = self.generate_outlier_analysis()
        
        # 5. Exportar datos
        self.export_to_csv()
        
        # 6. Guardar resumenes
        summary_file = self.OUTPUT_PATH / 'station_coverage_summary.csv'
        summary_df.to_csv(summary_file, index=False, encoding='utf-8')
        
        outlier_file = self.OUTPUT_PATH / 'outlier_analysis.csv'
        outlier_df.to_csv(outlier_file, index=False, encoding='utf-8')
        
        print("\n" + "=" * 70)
        print("ANALISIS COMPLETADO")
        print("=" * 70)
        print(f"Archivos generados en: {self.OUTPUT_PATH}")
        
        return {
            'summary': summary_df,
            'outliers': outlier_df,
            'long_data': self.long_data
        }


if __name__ == '__main__':
    analyzer = MagdalenaDataAnalyzer()
    results = analyzer.run_full_analysis()
