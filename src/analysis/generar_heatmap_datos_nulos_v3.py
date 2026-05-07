#!/usr/bin/env python3
"""
Heatmap v3 - Datos Nulos por Estacion y Año
============================================

Actualizado con datos crudos corregidos de San Pedrito (2026-05-06).
Muestra % de datos faltantes por estacion y año.

Estilo: Igual a la referencia original "Datos nulos.png"
- Blanco/azul claro = 0% faltantes (100% datos)
- Azul oscuro = 100% faltantes (0% datos)
- Gris = Estacion no existia (antes de instalacion)

Autor: MagdalenaBot
Fecha: 2026-05-06
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Rutas
PROJECT_ROOT = Path(r"C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot")
DATA_PATH = PROJECT_ROOT / "backend" / "data" / "processed"
OUTPUT_PATH = PROJECT_ROOT / "Imagenes" / "Niveles"

# Orden del eje Y: de aguas abajo a aguas arriba (igual a la figura original)
# San Pedrito se coloca justo debajo de Calamar (correlacion 0.996)
GEOGRAPHIC_ORDER_Y = [
    'CALAMAR',
    'SAN_PEDRITO',       # Nueva estacion - cercana a Calamar
    'TENERIFE',
    'PLATO',
    'MAGANGUE',
    'BARBOSA',
    'COYONGAL',
    'ARMENIA',
    'RIO_NUEVO',
    'LAS_PALOMAS',
    'LAS_AGUADAS',
    'EL_BANCO',
    'PENONCITO',
    'LA_GLORIA',
    'GAMARRA_AUT',
    'EL_CONTENTO',
    'SITIO_NUEVO',
    'PUERTO_WILCHES',
]


def get_expected_days(year):
    """Devuelve el numero esperado de dias para un año (365 o 366)."""
    return 366 if ((year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)) else 365


def generate_heatmap_datos_nulos():
    """Genera heatmap de % datos faltantes por estacion y año."""
    
    print("=" * 70)
    print("GENERACION DE HEATMAP v3 - DATOS NULOS")
    print("=" * 70)
    
    # Cargar datos crudos (fuente de verdad)
    print(f"\nCargando datos crudos desde: {DATA_PATH}")
    df = pd.read_csv(DATA_PATH / "Resumen_Crudos_IDEAM_2026.csv")
    df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y')
    
    # Asegurar nombres en mayusculas consistentes
    df['station'] = df['station'].str.upper().str.replace(' ', '_')
    
    # Rango completo de años
    all_years = range(int(df['year'].min()), int(df['year'].max()) + 1)
    print(f"Rango de anos: {min(all_years)} - {max(all_years)}")
    
    # Calcular cobertura por estacion y año
    coverage_records = []
    for station in df['station'].unique():
        df_st = df[df['station'] == station].copy()
        
        # Primer y ultimo año con datos validos
        valid_data = df_st[df_st['level'].notna()]
        if valid_data.empty:
            continue
        
        first_year = int(valid_data['year'].min())
        last_year = int(valid_data['year'].max())
        
        for year in all_years:
            expected = get_expected_days(year)
            
            if year < first_year or year > last_year:
                # Año fuera del rango operativo de la estacion
                # Antes de instalacion = No Instalada (NaN)
                # Despues del ultimo dato = No Instalada (NaN) - puede que ya no opera
                coverage_records.append({
                    'station': station,
                    'year': year,
                    'pct_missing': np.nan,  # Se mostrara en gris
                    'days_missing': np.nan,
                    'days_valid': 0,
                    'expected_days': expected,
                    'installed': False
                })
            else:
                df_year = df_st[df_st['year'] == year]
                valid_days = df_year['level'].notna().sum()
                missing_days = expected - valid_days
                pct_missing = (missing_days / expected) * 100
                
                coverage_records.append({
                    'station': station,
                    'year': year,
                    'pct_missing': pct_missing,
                    'days_missing': missing_days,
                    'days_valid': valid_days,
                    'expected_days': expected,
                    'installed': True
                })
    
    coverage_df = pd.DataFrame(coverage_records)
    
    # Crear matriz pivot
    pivot = coverage_df.pivot(index='station', columns='year', values='pct_missing')
    installed_mask = coverage_df.pivot(index='station', columns='year', values='installed')
    
    # Reordenar segun orden geografico
    available_stations = [s for s in GEOGRAPHIC_ORDER_Y if s in pivot.index]
    pivot = pivot.reindex(available_stations)
    installed_mask = installed_mask.reindex(available_stations)
    
    # Quitar nombre del indice para evitar guion en etiquetas del eje Y
    pivot.index.name = None
    
    print(f"\nEstaciones incluidas ({len(available_stations)}):")
    for s in available_stations:
        print(f"  - {s}")
    
    # Crear mascara para "No Instalada" (invertir: True donde NO esta instalada)
    mask_not_installed = ~installed_mask.fillna(False)
    
    # Crear figura con estilo similar a la referencia
    fig, ax = plt.subplots(figsize=(16, 10))
    
    # Colormap Blues (como la referencia)
    cmap = sns.color_palette("Blues", as_cmap=True)
    
    # Dibujar heatmap
    sns.heatmap(
        pivot,
        cmap=cmap,
        vmin=0,
        vmax=100,
        mask=mask_not_installed.values,
        linewidths=0.5,
        linecolor='white',
        cbar_kws={
            'label': '% Datos Faltantes',
            'shrink': 0.8,
        },
        ax=ax,
    )
    
    # Colorear celdas "No Instalada" con gris claro
    for i, station in enumerate(pivot.index):
        for j, year in enumerate(pivot.columns):
            if mask_not_installed.iloc[i, j]:
                rect = plt.Rectangle(
                    (j, i), 1, 1,
                    fill=True,
                    facecolor='#E8E8E8',  # Gris muy claro (igual referencia)
                    edgecolor='white',
                    linewidth=0.5,
                    zorder=2
                )
                ax.add_patch(rect)
    
    # Configurar ejes
    ax.set_xlabel('Ano', fontsize=14, fontweight='bold')
    ax.set_ylabel('Estacion', fontsize=14, fontweight='bold')
    
    # Titulo igual a la referencia
    ax.set_title(
        'Mapa de Calor: Cobertura de Datos por Estacion y Ano\n'
        '(Azul oscuro = mas datos faltantes, Azul claro = menos datos faltantes, Gris = Estacion no existia)',
        fontsize=14, fontweight='bold', pad=15
    )
    
    # Rotar etiquetas del eje X
    plt.xticks(rotation=45, ha='right', fontsize=10)
    plt.yticks(rotation=0, fontsize=11)
    
    # Ajustar layout
    plt.tight_layout()
    
    # Guardar
    output_file = OUTPUT_PATH / "Datos nulos_v3.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"\nHeatmap guardado: {output_file}")
    plt.close()
    
    # Guardar datos subyacentes
    pivot.to_csv(OUTPUT_PATH / "heatmap_datos_nulos_matrix.csv")
    print(f"Matriz guardada: {OUTPUT_PATH / 'heatmap_datos_nulos_matrix.csv'}")
    
    # Resumen
    print("\n" + "=" * 70)
    print("RESUMEN DE COBERTURA POR ESTACION")
    print("=" * 70)
    for station in available_stations:
        st_data = coverage_df[coverage_df['station'] == station]
        installed = st_data[st_data['installed'] == True]
        if installed.empty:
            continue
        avg_missing = installed['pct_missing'].mean()
        max_missing = installed['pct_missing'].max()
        years_installed = len(installed)
        first_y = int(installed['year'].min())
        last_y = int(installed['year'].max())
        print(f"  {station:20s}: {first_y}-{last_y} | {years_installed} anos | "
              f"Prom faltante: {avg_missing:.1f}% | Max faltante: {max_missing:.1f}%")
    
    return output_file


if __name__ == '__main__':
    generate_heatmap_datos_nulos()
