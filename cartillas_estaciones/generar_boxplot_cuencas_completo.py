# -*- coding: utf-8 -*-
"""
Boxplot por Cuencas - Datos RAW - TODAS LAS ESTACIONES (18)
Incluye San Pedrito y La Gloria
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Rutas
RAW_DATA_DIR = r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\backend\data\raw\SERIE NIVELES IDEAM A 2026'
OUTPUT_DIR = r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\cartillas_estaciones'

# ORDEN DEFINITIVO CON TODAS LAS ESTACIONES (18)
GEOGRAPHIC_ORDER = [
    # Cuenca Baja (7 estaciones)
    'SAN_PEDRITO',
    'CALAMAR',
    'TENERIFE',
    'PLATO',
    'MAGANGUE',
    'BARBOSA',
    'COYONGAL',
    # Cuenca Media (6 estaciones)
    'ARMENIA',
    'RIO_NUEVO',
    'LAS_PALOMAS',
    'LAS_AGUADAS',
    'EL_BANCO',
    'PENONCITO',
    # Cuenca Alta (5 estaciones)
    'LA_GLORIA',
    'GAMARRA_AUT',
    'EL_CONTENTO',
    'SITIO_NUEVO',
    'PUERTO_WILCHES',
]

# Mapeo de archivos - TODOS LOS ARCHIVOS EXISTENTES
STATION_FILES = {
    'SAN_PEDRITO': 'SAN_PEDRITO_-_AUT_29047070.xlsx',
    'CALAMAR': 'CALAMAR_29037020.xlsx',
    'TENERIFE': 'TENERIFE_29017010.xlsx',
    'PLATO': 'PLATO_MAGDALENA_AUT_25027450.xlsx',
    'MAGANGUE': 'MAGANGUE_25027680.xlsx',
    'BARBOSA': 'BARBOSA_25027530.xlsx',
    'COYONGAL': 'COYONGAL_25027930.xlsx',
    'ARMENIA': 'ARMENIA_25027360.xlsx',
    'RIO_NUEVO': 'RIO_NUEVO_25027630.xlsx',
    'LAS_PALOMAS': 'LAS_PALOMAS_25027390.xlsx',
    'LAS_AGUADAS': 'LAS_AGUADAS_25027490.xlsx',
    'EL_BANCO': 'EL_BANCO_-_AUT_25027020.xlsx',
    'PENONCITO': 'PENONCITO_25027330.xlsx',
    'LA_GLORIA': 'LA_GLORIA23217060.xlsx',  # SIN GUION
    'GAMARRA_AUT': 'GAMARRA_-_AUT_23217080.xlsx',
    'EL_CONTENTO': 'EL_CONTENTO_23217030.xlsx',
    'SITIO_NUEVO': 'SITIO_NUEVO_23187280.xlsx',
    'PUERTO_WILCHES': 'PUERTO_WILCHES_23187010.xlsx',
}


def load_station_raw(filepath, station_name):
    """Carga datos RAW de una estacion."""
    try:
        df_wide = pd.read_excel(filepath, sheet_name=0)
        
        # Obtener columnas de años
        year_cols = [c for c in df_wide.columns if isinstance(c, (int, float)) and 1900 <= c <= 2100]
        if not year_cols:
            return None
        
        date_col = df_wide.columns[0]
        records = []
        
        for year in year_cols:
            year_data = df_wide[[date_col, year]].copy()
            year_data = year_data.dropna(subset=[year])
            
            for _, row in year_data.iterrows():
                try:
                    ref_date = pd.to_datetime(row[date_col])
                    month = ref_date.month
                    day = ref_date.day
                    date = pd.Timestamp(year=int(year), month=month, day=day)
                    
                    records.append({
                        'date': date,
                        'station': station_name,
                        'level': float(row[year]) if pd.notna(row[year]) else np.nan,
                        'year': int(year),
                    })
                except:
                    continue
        
        return pd.DataFrame(records) if records else None
    except Exception as e:
        print(f'  Error cargando {station_name}: {e}')
        return None


def create_boxplot_cuencas_complete(output_path):
    """
    Boxplot por Cuencas con datos RAW - TODAS LAS ESTACIONES.
    """
    print('='*70)
    print('GENERANDO BOXPLOT POR CUENCAS - DATOS RAW - 18 ESTACIONES')
    print('='*70)
    
    # Cargar datos de todas las estaciones
    all_data = []
    estaciones_cargadas = []
    
    for station in GEOGRAPHIC_ORDER:
        filename = STATION_FILES.get(station)
        if not filename:
            print(f'[SKIP] No hay archivo mapeado para {station}')
            continue
        
        filepath = Path(RAW_DATA_DIR) / filename
        if not filepath.exists():
            print(f'[SKIP] No encontrado: {filename}')
            continue
        
        print(f'Cargando {station}...')
        df = load_station_raw(filepath, station)
        if df is not None and len(df) > 0:
            all_data.append(df)
            estaciones_cargadas.append(station)
            print(f'  OK Registros: {len(df)}')
        else:
            print(f'  ERROR Sin datos')
    
    if not all_data:
        print('[ERROR] No se cargaron datos')
        return
    
    df_all = pd.concat(all_data, ignore_index=True)
    print(f'\nTotal registros cargados: {len(df_all)}')
    print(f'Estaciones cargadas: {len(estaciones_cargadas)}/18')
    
    # Verificar cuales faltan
    faltantes = set(GEOGRAPHIC_ORDER) - set(estaciones_cargadas)
    if faltantes:
        print(f'Estaciones faltantes: {faltantes}')
    
    # Filtrar estaciones disponibles en el orden correcto
    available_stations = [s for s in GEOGRAPHIC_ORDER if s in estaciones_cargadas]
    
    # Crear figura
    fig, ax = plt.subplots(figsize=(20, 8))
    
    # Crear boxplot en BLANCO Y NEGRO
    bp = ax.boxplot(
        [df_all[df_all['station'] == s]['level'].dropna().values 
         for s in available_stations],
        labels=[s.replace('_', ' ').title() for s in available_stations],
        patch_artist=True,
        showfliers=True,
        boxprops=dict(facecolor='white', edgecolor='black', linewidth=1.2),
        medianprops=dict(color='black', linewidth=2),
        whiskerprops=dict(color='black', linewidth=1),
        capprops=dict(color='black', linewidth=1),
        flierprops=dict(marker='o', markerfacecolor='none', markeredgecolor='black', 
                       markersize=4, alpha=0.6)
    )
    
    # Lineas verticales separando Cuencas (ahora con 18 estaciones)
    line1_pos = 7.5   # Despues de Coyongal (7ma estacion)
    line2_pos = 13.5  # Despues de Penoncito (13ra estacion)
    
    ax.axvline(x=line1_pos, color='black', linestyle='--', linewidth=1.5, alpha=0.5)
    ax.axvline(x=line2_pos, color='black', linestyle='--', linewidth=1.5, alpha=0.5)
    
    # Etiquetas de Cuencas
    mid_cuenca_baja = (1 + line1_pos) / 2
    mid_cuenca_media = (line1_pos + line2_pos) / 2
    mid_cuenca_alta = (line2_pos + len(available_stations) + 1) / 2
    
    ax.text(mid_cuenca_baja, ax.get_ylim()[1] * 0.98, 'CUENCA BAJA\n(7 est)', 
            ha='center', va='top', fontsize=11, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.5))
    
    ax.text(mid_cuenca_media, ax.get_ylim()[1] * 0.98, 'CUENCA MEDIA\n(6 est)', 
            ha='center', va='top', fontsize=11, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.5))
    
    ax.text(mid_cuenca_alta, ax.get_ylim()[1] * 0.98, 'CUENCA ALTA\n(5 est)', 
            ha='center', va='top', fontsize=11, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.5))
    
    ax.set_xlabel('Estacion (Orden: aguas abajo → aguas arriba)', fontsize=12)
    ax.set_ylabel('Cota (msnm)', fontsize=12)
    ax.set_title('Diagrama de Cajas de Cotas por Estacion - Datos Originales (18 estaciones)\n' + 
                 'Cuenca Baja: San Pedrito→Coyongal | Media: Armenia→Penoncito | Alta: La Gloria→Puerto Wilches',
                 fontsize=13, fontweight='bold', pad=20)
    
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', alpha=0.3, linestyle='--', color='gray')
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f'\n✓ Figura guardada: {output_path}')
    print(f'✓ Estaciones incluidas: {len(available_stations)}')


if __name__ == '__main__':
    output_file = Path(OUTPUT_DIR) / 'Figura_3_1_Boxplot_Cuencas_18_ESTACIONES.png'
    create_boxplot_cuencas_complete(output_file)
    print('\n[COMPLETADO - VERIFICAR RUTA ARRIBA]')
