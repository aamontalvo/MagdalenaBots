#!/usr/bin/env python3
"""
Heatmap v2 - Seccion de Analisis de Hidrologia
==============================================

Version 2: Heatmap con mascara de "No Instalada" para años previos a operacion.
Colores: Blanco/Gris claro = No instalada | Escala azul = Datos faltantes

Autor: Seccion de Analisis de Hidrologia
Fecha: 2026-02-25
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Rutas
DATA_PATH = Path(r"C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\Data\Niveles")
PROCESSED_PATH = DATA_PATH / "01_processed"
ANALYSIS_PATH = DATA_PATH / "02_analysis"
FIGURES_PATH = DATA_PATH / "03_figures" / "exploratory"

# Orden corregido: aguas arriba -> aguas abajo
GEOGRAPHIC_ORDER_CORRECTED = [
    'Puerto Wilches',    # 1. Aguas arriba
    'Sitio Nuevo',       # 2
    'El Contento',       # 3
    'Gamarra Aut',       # 4
    'La Gloria',         # 5
    'Peñoncito',         # 6 (CORREGIDO - antes de El Banco)
    'El Banco',          # 7 (CORREGIDO - después de Peñoncito)
    'Las Aguadas',       # 8
    'Las Palomas',       # 9
    'Rio Nuevo',         # 10
    'Armenia',           # 11
    'Coyongal',          # 12
    'Barbosa',           # 13
    'Magangue',          # 14
    'Plato',             # 15
    'Tenerife',          # 16
    'Calamar',           # 17. Aguas abajo
]


def generate_heatmap_v2():
    """Genera heatmap con mascara de 'No Instalada'."""
    
    print("=" * 70)
    print("GENERACION DE HEATMAP v2 - MASCARA 'NO INSTALADA'")
    print("=" * 70)
    
    # Cargar datos
    df = pd.read_csv(PROCESSED_PATH / "magdalena_levels_long_format.csv")
    df['fecha'] = pd.to_datetime(df['fecha'])
    
    # Cargar metadatos
    metadata = pd.read_csv(ANALYSIS_PATH / "station_coverage_summary.csv")
    
    # Crear matriz de cobertura
    coverage = df.groupby(['estacion', 'anio']).agg({
        'nivel_msnm': lambda x: x.notna().sum()
    }).reset_index()
    
    coverage_matrix = coverage.pivot(index='estacion', columns='anio', values='nivel_msnm')
    
    # Año bisiesto = 366, normal = 365
    expected_days = {}
    for year in coverage_matrix.columns:
        is_leap = (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
        expected_days[year] = 366 if is_leap else 365
    
    # Calcular matriz de nulos
    null_matrix = coverage_matrix.copy()
    for col in null_matrix.columns:
        null_matrix[col] = expected_days.get(col, 365) - null_matrix[col].fillna(0)
    
    # Determinar años de instalación
    installation_years = {}
    for station in null_matrix.index:
        station_data = df[df['estacion'] == station]
        first_valid = station_data[station_data['nivel_msnm'].notna()]
        if not first_valid.empty:
            installation_years[station] = first_valid['anio'].min()
        else:
            installation_years[station] = None
    
    # Crear matriz de visualizacion con mascara
    # 0 = No instalada (mostrar en gris/blanco)
    # 1-365 = Dias sin datos (escala azul)
    display_matrix = null_matrix.copy()
    mask_not_installed = pd.DataFrame(False, index=null_matrix.index, columns=null_matrix.columns)
    
    for station in display_matrix.index:
        install_year = installation_years.get(station)
        if install_year:
            for year in display_matrix.columns:
                if year < install_year:
                    mask_not_installed.loc[station, year] = True
                    display_matrix.loc[station, year] = np.nan  # Será transparente/mascarado
    
    # Ordenar por orden geografico corregido
    order_dict = {name: idx for idx, name in enumerate(GEOGRAPHIC_ORDER_CORRECTED)}
    
    # Filtrar solo estaciones que existen en los datos
    available_stations = [s for s in GEOGRAPHIC_ORDER_CORRECTED if s in display_matrix.index]
    display_matrix = display_matrix.reindex(available_stations)
    mask_not_installed = mask_not_installed.reindex(available_stations)
    
    # Crear figura
    fig, ax = plt.subplots(figsize=(18, 12))
    
    # Colores personalizados
    # Fondo gris muy claro para "No instalada"
    # Escala azul para datos faltantes
    cmap = sns.color_palette("Blues", as_cmap=True)
    
    # Dibujar heatmap principal
    sns.heatmap(display_matrix, 
               cmap=cmap,
               cbar_kws={'label': 'Dias sin datos', 'shrink': 0.8},
               linewidths=0.5,
               linecolor='white',
               ax=ax,
               vmin=0,
               vmax=366,
               mask=mask_not_installed.values,  # Mascarar valores no instalados
               )
    
    # Colorear celdas "No Instalada" con gris claro
    for i, station in enumerate(display_matrix.index):
        install_year = installation_years.get(station)
        if install_year:
            for j, year in enumerate(display_matrix.columns):
                if year < install_year:
                    # Dibujar rectángulo gris
                    rect = plt.Rectangle((j, i), 1, 1, 
                                        fill=True, 
                                        facecolor='#E8E8E8',  # Gris muy claro
                                        edgecolor='white',
                                        linewidth=0.5,
                                        zorder=0)
                    ax.add_patch(rect)
                    # Agregar texto "NI" (No Instalada) pequeño
                    ax.text(j + 0.5, i + 0.5, 'NI', 
                           ha='center', va='center', 
                           fontsize=6, color='#999999',
                           fontweight='bold')
    
    # Configurar ejes
    ax.set_xlabel('Año', fontsize=14, fontweight='bold')
    ax.set_ylabel('Estacion (aguas arriba -> abajo)', fontsize=14, fontweight='bold')
    ax.set_title('Mapa de Calor: Datos Faltantes por Estacion y Año\n'
                '(NI = Estacion No Instalada | Intensidad azul = Dias sin datos)', 
                fontsize=16, fontweight='bold', pad=20)
    
    # Rotar etiquetas
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    
    # Agregar leyenda manual para "No Instalada"
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#E8E8E8', edgecolor='white', label='No Instalada (NI)'),
        Patch(facecolor='#08306B', edgecolor='white', label='365 dias faltantes'),
        Patch(facecolor='#F7FBFF', edgecolor='white', label='0 dias faltantes')
    ]
    ax.legend(handles=legend_elements, loc='upper left', 
             title='Leyenda', title_fontsize=11, fontsize=9)
    
    plt.tight_layout()
    
    # Guardar
    output_file = FIGURES_PATH / "heatmap_nulls_v2.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"\nHeatmap v2 guardado: {output_file}")
    plt.close()
    
    # Guardar metadatos actualizados
    install_df = pd.DataFrame([
        {'Estacion': k, 'Anio_Instalacion': v} 
        for k, v in installation_years.items() if v
    ])
    install_df = install_df.sort_values('Anio_Instalacion')
    install_df.to_csv(ANALYSIS_PATH / "installation_years.csv", index=False)
    
    print("\nAños de instalacion por estacion:")
    for _, row in install_df.iterrows():
        print(f"  - {row['Estacion']:20s}: {int(row['Anio_Instalacion'])}")
    
    return output_file


if __name__ == '__main__':
    generate_heatmap_v2()
