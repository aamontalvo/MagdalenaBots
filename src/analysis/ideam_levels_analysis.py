"""
Analisis de niveles IDEAM - Rio Magdalena
Version unica y definitiva

ORDEN DE ESTACIONES:
Zona Baja (7): San Pedrito → Calamar → Tenerife → Plato → Magangue → Barbosa → Coyongal
Zona Media (6): Armenia → Rio Nuevo → Las Palomas → Las Aguadas → El Banco → Penoncito
Zona Alta (5): La Gloria → Gamarra Aut → El Contento → Sitio Nuevo → Puerto Wilches
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from docx.shared import RGBColor, Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
import warnings
warnings.filterwarnings('ignore')

# Configuracion de estilo - solo blanco y negro para boxplots
plt.style.use('seaborn-v0_8-whitegrid')

# ORDEN DEFINITIVO DE ESTACIONES
GEOGRAPHIC_ORDER = [
    # Zona Baja (7 estaciones) - AGREGADO SAN PEDRITO AL INICIO
    'SAN_PEDRITO',
    'CALAMAR',
    'TENERIFE',
    'PLATO',
    'MAGANGUE',
    'BARBOSA',
    'COYONGAL',
    # Zona Media (6 estaciones)
    'ARMENIA',
    'RIO_NUEVO',
    'LAS_PALOMAS',
    'LAS_AGUADAS',
    'EL_BANCO',
    'PENONCITO',
    # Zona Alta (5 estaciones)
    'LA_GLORIA',
    'GAMARRA_AUT',
    'EL_CONTENTO',
    'SITIO_NUEVO',
    'PUERTO_WILCHES',
]

# Limites de zonas
ZONE_BOUNDARIES = {
    'zona_baja_end': 6,      # Coyongal (indice 6)
    'zona_media_end': 12,    # Penoncito (indice 12)
}

# Mapeo de archivos
STATION_NAME_MAP = {
    'ARMENIA': 'ARMENIA',
    'BARBOSA': 'BARBOSA',
    'CALAMAR': 'CALAMAR',
    'COYONGAL': 'COYONGAL',
    'EL_BANCO_-_AUT': 'EL_BANCO',
    'EL_CONTENTO': 'EL_CONTENTO',
    'GAMARRA_-_AUT': 'GAMARRA_AUT',
    'LA_GLORIA': 'LA_GLORIA',
    'LAS_AGUADAS': 'LAS_AGUADAS',
    'LAS_PALOMAS': 'LAS_PALOMAS',
    'MAGANGUE': 'MAGANGUE',
    'PENONCITO': 'PENONCITO',
    'PLATO_MAGDALENA_AUT': 'PLATO',
    'PUERTO_WILCHES': 'PUERTO_WILCHES',
    'RIO_NUEVO': 'RIO_NUEVO',
    'SAN_PEDRITO_-_AUT': 'SAN_PEDRITO',
    'SITIO_NUEVO': 'SITIO_NUEVO',
    'TENERIFE': 'TENERIFE',
}

# Codigos IDEAM
STATION_CODES = {
    'ARMENIA': '25027360',
    'BARBOSA': '25027530',
    'CALAMAR': '29037020',
    'COYONGAL': '25027930',
    'EL_BANCO': '25027020',
    'EL_CONTENTO': '23217030',
    'GAMARRA_AUT': '23217080',
    'LA_GLORIA': '23217060',
    'LAS_AGUADAS': '25027490',
    'LAS_PALOMAS': '25027390',
    'MAGANGUE': '25027680',
    'PENONCITO': '25027330',
    'PLATO': '25027450',
    'PUERTO_WILCHES': '23187010',
    'RIO_NUEVO': '25027630',
    'SAN_PEDRITO': '29047070',
    'SITIO_NUEVO': '23187280',
    'TENERIFE': '29017010',
}


def load_station_data(filepath):
    """Carga datos de Excel y transforma de wide a long format."""
    filename = Path(filepath).stem
    station_key = None
    for key in STATION_NAME_MAP:
        if filename.startswith(key):
            station_key = STATION_NAME_MAP[key]
            break
    
    if not station_key:
        return None
    
    df_wide = pd.read_excel(filepath, sheet_name=0)
    
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
                    'station': station_key,
                    'level': float(row[year]) if pd.notna(row[year]) else np.nan,
                    'year': int(year),
                    'month': month,
                    'day': day
                })
            except:
                continue
    
    return pd.DataFrame(records) if records else None


def load_all_stations(data_dir):
    """Carga todas las estaciones."""
    data_dir = Path(data_dir)
    all_data = []
    
    for file in sorted(data_dir.glob('*.xlsx')):
        print(f"  Cargando: {file.name}")
        df = load_station_data(file)
        if df is not None and len(df) > 0:
            all_data.append(df)
    
    return pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()


def calculate_coverage(df):
    """Calcula cobertura de datos por estacion y año."""
    coverage = []
    
    for station in df['station'].unique():
        station_data = df[df['station'] == station]
        years = sorted(station_data['year'].unique())
        
        for year in range(int(min(years)), int(max(years)) + 1):
            year_data = station_data[station_data['year'] == year]
            total_expected = 366 if pd.Timestamp(year, 12, 31).dayofyear == 366 else 365
            available = year_data['level'].notna().sum()
            missing_pct = ((total_expected - available) / total_expected) * 100
            
            coverage.append({
                'station': station,
                'year': year,
                'available': available,
                'expected': total_expected,
                'missing_pct': round(missing_pct, 1),
                'coverage_pct': round(100 - missing_pct, 1),
            })
    
    return pd.DataFrame(coverage)


def create_coverage_heatmap(coverage_df, output_path):
    """
    Heatmap de cobertura.
    Usando Blues_r: azul oscuro = menos faltantes (mejor cobertura)
                   azul claro/blanco = mas faltantes
    Gris = estacion no existia
    """
    pivot = coverage_df.pivot(index='station', columns='year', values='missing_pct')
    
    available_stations = [s for s in GEOGRAPHIC_ORDER if s in pivot.index]
    pivot = pivot.reindex(available_stations)
    
    # Mascara para estaciones que no existian
    station_start_years = {s: coverage_df[coverage_df['station'] == s]['year'].min() 
                          for s in pivot.index}
    
    mask = np.zeros_like(pivot, dtype=bool)
    for i, station in enumerate(pivot.index):
        start_year = station_start_years[station]
        for j, year in enumerate(pivot.columns):
            if year < start_year:
                mask[i, j] = True
    
    fig, ax = plt.subplots(figsize=(16, 10))
    
    # Blues_r invertido: azul oscuro = valores bajos (menos faltantes)
    # azul claro = valores altos (mas faltantes)
    sns.heatmap(pivot, 
                mask=mask,
                cmap='Blues',  # INVERTIDO
                vmin=0, vmax=100,
                cbar_kws={'label': '% Datos Faltantes'},
                ax=ax,
                linewidths=0.5,
                linecolor='white')
    
    # Color gris para no existia
    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):
            if mask[i, j]:
                ax.add_patch(plt.Rectangle((j, i), 1, 1, fill=True, 
                                          facecolor='#CCCCCC', edgecolor='white', linewidth=0.5))
    
    ax.set_xlabel('Año', fontsize=11)
    ax.set_ylabel('Estacion', fontsize=11)
    ax.set_title('Mapa de Calor: Cobertura de Datos por Estacion y Año\n' + 
                 '(Azul oscuro = mejor cobertura, Azul claro = mas faltantes, Gris = no existia)', 
                 fontsize=12, fontweight='bold', pad=20)
    
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()


def create_boxplot_by_station(df, output_path):
    """
    Boxplot en BLANCO Y NEGRO (sin colores).
    Orden: San Pedrito → ... → Coyongal → ... → Penoncito → ... → Puerto Wilches
    """
    available_stations = [s for s in GEOGRAPHIC_ORDER if s in df['station'].values]
    df_filtered = df[df['station'].isin(available_stations)].copy()
    
    fig, ax = plt.subplots(figsize=(18, 8))
    
    # Crear boxplot en BLANCO Y NEGRO
    bp = ax.boxplot(
        [df_filtered[df_filtered['station'] == s]['level'].dropna().values 
         for s in available_stations],
        labels=[s.replace('_', ' ').title() for s in available_stations],
        patch_artist=True,
        showfliers=True,
        # Colores en blanco y negro
        boxprops=dict(facecolor='white', edgecolor='black', linewidth=1.2),
        medianprops=dict(color='black', linewidth=2),
        whiskerprops=dict(color='black', linewidth=1),
        capprops=dict(color='black', linewidth=1),
        flierprops=dict(marker='o', markerfacecolor='none', markeredgecolor='black', 
                       markersize=4, alpha=0.6)
    )
    
    # Lineas de separacion de zonas
    line1_pos = ZONE_BOUNDARIES['zona_baja_end'] + 1.5
    line2_pos = ZONE_BOUNDARIES['zona_media_end'] + 1.5
    
    ax.axvline(x=line1_pos, color='black', linestyle='--', linewidth=2, alpha=0.7)
    ax.axvline(x=line2_pos, color='black', linestyle='--', linewidth=2, alpha=0.7)
    
    # Etiquetas de zonas
    mid_zona_baja = (1 + line1_pos) / 2
    mid_zona_media = (line1_pos + line2_pos) / 2
    mid_zona_alta = (line2_pos + len(available_stations) + 1) / 2
    
    ax.text(mid_zona_baja, ax.get_ylim()[1] * 0.98, 'ZONA BAJA\n(7 est)', 
            ha='center', va='top', fontsize=10, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.5))
    
    ax.text(mid_zona_media, ax.get_ylim()[1] * 0.98, 'ZONA MEDIA\n(6 est)', 
            ha='center', va='top', fontsize=10, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.5))
    
    ax.text(mid_zona_alta, ax.get_ylim()[1] * 0.98, 'ZONA ALTA\n(5 est)', 
            ha='center', va='top', fontsize=10, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.5))
    
    ax.set_xlabel('Estacion (Orden: aguas abajo → aguas arriba)', fontsize=11)
    ax.set_ylabel('Cota (msnm)', fontsize=11)
    ax.set_title('Diagrama de Cajas de Cotas por Estacion (Escala de Grises)\n' + 
                 'Zona Baja: San Pedrito→Coyongal | Media: Armenia→Penoncito | Alta: La Gloria→Puerto Wilches',
                 fontsize=12, fontweight='bold', pad=20)
    
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', alpha=0.3, linestyle='--', color='gray')
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()


def generate_summary_table(df, output_path):
    """Tabla de estadisticas."""
    summary = []
    
    for station in df['station'].unique():
        station_data = df[df['station'] == station]['level']
        if len(station_data.dropna()) == 0:
            continue
        
        stats = {
            'Estacion': station.replace('_', ' ').title(),
            'Codigo IDEAM': STATION_CODES.get(station, 'N/A'),
            'Ano Inicio': int(df[df['station'] == station]['year'].min()),
            'Ano Fin': int(df[df['station'] == station]['year'].max()),
            'n': int(station_data.notna().sum()),
            'Media': round(station_data.mean(), 3),
            'Mediana': round(station_data.median(), 3),
            'Desv. Std': round(station_data.std(), 3),
            'Min': round(station_data.min(), 3),
            'Max': round(station_data.max(), 3),
            'P10': round(station_data.quantile(0.10), 3),
            'P90': round(station_data.quantile(0.90), 3),
        }
        summary.append(stats)
    
    summary_df = pd.DataFrame(summary)
    
    # Ordenar
    order_map = {s.replace('_', ' ').title(): i for i, s in enumerate(GEOGRAPHIC_ORDER)}
    summary_df['order'] = summary_df['Estacion'].map(order_map)
    summary_df = summary_df.sort_values('order').drop('order', axis=1).reset_index(drop=True)
    
    # Agregar zona
    def get_zona(estacion):
        idx = [s.replace('_', ' ').title() for s in GEOGRAPHIC_ORDER].index(estacion)
        if idx <= ZONE_BOUNDARIES['zona_baja_end']:
            return 'Baja'
        elif idx <= ZONE_BOUNDARIES['zona_media_end']:
            return 'Media'
        else:
            return 'Alta'
    
    summary_df['Zona'] = summary_df['Estacion'].apply(get_zona)
    cols = ['Estacion', 'Zona', 'Codigo IDEAM', 'Ano Inicio', 'Ano Fin', 'n', 
            'Media', 'Mediana', 'Desv. Std', 'Min', 'Max', 'P10', 'P90']
    summary_df = summary_df[cols]
    
    summary_df.to_csv(output_path, index=False, encoding='utf-8-sig')
    return summary_df


def generate_coverage_table(coverage_df, output_path):
    """Tabla de cobertura."""
    summary = []
    
    for station in coverage_df['station'].unique():
        station_cov = coverage_df[coverage_df['station'] == station]
        good_years = station_cov[station_cov['coverage_pct'] >= 80]
        
        stats = {
            'Estacion': station.replace('_', ' ').title(),
            'Codigo IDEAM': STATION_CODES.get(station, 'N/A'),
            'Ano Inicio': int(station_cov['year'].min()),
            'Ano Fin': int(station_cov['year'].max()),
            'Anos Totales': int(len(station_cov)),
            'Anos con >=80% datos': int(len(good_years)),
            'Cobertura Promedio (%)': round(station_cov['coverage_pct'].mean(), 1),
            'Cobertura Minima (%)': round(station_cov['coverage_pct'].min(), 1),
            'Cobertura Maxima (%)': round(station_cov['coverage_pct'].max(), 1),
        }
        summary.append(stats)
    
    summary_df = pd.DataFrame(summary)
    
    order_map = {s.replace('_', ' ').title(): i for i, s in enumerate(GEOGRAPHIC_ORDER)}
    summary_df['order'] = summary_df['Estacion'].map(order_map)
    summary_df = summary_df.sort_values('order').drop('order', axis=1).reset_index(drop=True)
    
    def get_zona(estacion):
        idx = [s.replace('_', ' ').title() for s in GEOGRAPHIC_ORDER].index(estacion)
        if idx <= ZONE_BOUNDARIES['zona_baja_end']:
            return 'Baja'
        elif idx <= ZONE_BOUNDARIES['zona_media_end']:
            return 'Media'
        else:
            return 'Alta'
    
    summary_df.insert(1, 'Zona', summary_df['Estacion'].apply(get_zona))
    summary_df.to_csv(output_path, index=False, encoding='utf-8-sig')
    return summary_df


def update_word_document(figuras_path, tablas_path):
    """Actualiza el documento Word unico."""
    from docx import Document
    from docx.shared import Inches
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    
    informe_path = r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\Informes\INFORME_NIVELES_IDEAM_2026.docx'
    
    doc = Document(informe_path)
    tabla_cobertura = pd.read_csv(Path(tablas_path) / 'Tabla_2_1_Cobertura_Estaciones.csv', encoding='utf-8-sig')
    tabla_stats = pd.read_csv(Path(tablas_path) / 'Tabla_3_1_Estadisticas_Estaciones.csv', encoding='utf-8-sig')
    
    def add_heading(doc, text, level=1):
        heading = doc.add_heading(level=level)
        run = heading.add_run(text)
        run.font.color.rgb = RGBColor(0, 0, 0)
        return heading
    
    def add_paragraph(doc, text, bold=False):
        p = doc.add_paragraph()
        run = p.add_run(text)
        run.font.size = Pt(11)
        run.bold = bold
        return p
    
    def add_table_from_df(doc, df):
        table = doc.add_table(rows=1, cols=len(df.columns))
        hdr_cells = table.rows[0].cells
        for i, col in enumerate(df.columns):
            hdr_cells[i].text = str(col)
            hdr_cells[i].paragraphs[0].runs[0].bold = True
        for _, row in df.iterrows():
            row_cells = table.add_row().cells
            for i, value in enumerate(row):
                row_cells[i].text = str(value)
        return table
    
    # Agregar secciones
    doc.add_page_break()
    add_heading(doc, '2. ANALISIS DE CALIDAD DE DATOS', level=1)
    
    add_heading(doc, '2.1 Cobertura Temporal y Datos Faltantes', level=2)
    
    add_paragraph(doc, 
        "El presente estudio analizo 18 estaciones distribuidas en tres zonas geograficas del Rio Magdalena:")
    add_paragraph(doc, "- Zona Baja (7 estaciones): San Pedrito, Calamar, Tenerife, Plato, Magangue, Barbosa, Coyongal")
    add_paragraph(doc, "- Zona Media (6 estaciones): Armenia, Rio Nuevo, Las Palomas, Las Aguadas, El Banco, Penoncito")
    add_paragraph(doc, "- Zona Alta (5 estaciones): La Gloria, Gamarra Aut, El Contento, Sitio Nuevo, Puerto Wilches")
    
    add_paragraph(doc, 'Tabla 2.1. Resumen de cobertura de datos por estacion.', bold=True)
    add_table_from_df(doc, tabla_cobertura)
    
    add_heading(doc, '2.2 Mapa de Calor de Cobertura', level=2)
    add_paragraph(doc, 
        "La Figura 2.1 presenta el mapa de calor donde el azul oscuro indica mejor cobertura de datos "
        "(menos faltantes), el azul claro indica mayor porcentaje de datos faltantes, y el gris "
        "corresponde a periodos anteriores al inicio de operacion de cada estacion.")
    add_paragraph(doc, 'Figura 2.1. Mapa de calor de cobertura de datos.', bold=True)
    
    heatmap_path = Path(figuras_path) / 'Figura_2_1_Heatmap_Cobertura.png'
    if heatmap_path.exists():
        doc.add_picture(str(heatmap_path), width=Inches(6.5))
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    add_heading(doc, '2.3 Analisis de Distribucion y Valores Atipicos', level=2)
    add_paragraph(doc, 
        "La Figura 2.2 presenta los diagramas de cajas en escala de grises, ordenados geograficamente "
        "desde aguas abajo (San Pedrito) hasta aguas arriba (Puerto Wilches).")
    add_paragraph(doc, 'Figura 2.2. Diagrama de cajas de cotas por estacion.', bold=True)
    
    boxplot_path = Path(figuras_path) / 'Figura_3_1_Boxplot_Estaciones.png'
    if boxplot_path.exists():
        doc.add_picture(str(boxplot_path), width=Inches(6.5))
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    doc.add_page_break()
    add_heading(doc, '3. ESTADISTICAS DESCRIPTIVAS', level=1)
    add_heading(doc, '3.1 Resumen Estadistico', level=2)
    add_paragraph(doc, 'Tabla 3.1. Estadisticas descriptivas de cotas por estacion.', bold=True)
    add_table_from_df(doc, tabla_stats)
    
    # Guardar en el mismo archivo
    doc.save(informe_path)
    print(f"Documento actualizado: {informe_path}")


def main():
    """Funcion principal."""
    data_dir = r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\backend\data\raw\RawData\SERIE NIVELES IDEAM A 2026'
    output_figures = r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\Informes\Figuras'
    output_tables = r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\Informes\Tablas'
    
    print("=" * 70)
    print("ANALISIS DE NIVELES IDEAM - RIO MAGDALENA")
    print("=" * 70)
    print("\nORDEN DE ESTACIONES:")
    print(f"Zona Baja (7):  {GEOGRAPHIC_ORDER[:7]}")
    print(f"Zona Media (6): {GEOGRAPHIC_ORDER[7:13]}")
    print(f"Zona Alta (5):  {GEOGRAPHIC_ORDER[13:18]}")
    print("=" * 70)
    
    # Cargar datos
    print("\n[1/5] Cargando datos...")
    df = load_all_stations(data_dir)
    print(f"Total: {len(df):,} registros de {df['station'].nunique()} estaciones")
    
    # Filtrar
    df = df[df['station'].isin(GEOGRAPHIC_ORDER)].copy()
    print(f"En zonificacion: {df['station'].nunique()} estaciones")
    
    # Calcular cobertura
    print("\n[2/5] Calculando cobertura...")
    coverage_df = calculate_coverage(df)
    
    # Generar heatmap (rampa invertida)
    print("\n[3/5] Generando heatmap (Blues_r - rampa invertida)...")
    create_coverage_heatmap(coverage_df, Path(output_figures) / 'Figura_2_1_Heatmap_Cobertura.png')
    print("  Guardado: Figura_2_1_Heatmap_Cobertura.png")
    
    # Generar boxplot (blanco y negro)
    print("\n[4/5] Generando boxplot (blanco y negro)...")
    create_boxplot_by_station(df, Path(output_figures) / 'Figura_3_1_Boxplot_Estaciones.png')
    print("  Guardado: Figura_3_1_Boxplot_Estaciones.png")
    
    # Generar tablas
    print("\n[5/5] Generando tablas...")
    generate_coverage_table(coverage_df, Path(output_tables) / 'Tabla_2_1_Cobertura_Estaciones.csv')
    generate_summary_table(df, Path(output_tables) / 'Tabla_3_1_Estadisticas_Estaciones.csv')
    
    # Actualizar Word
    print("\n[6/6] Actualizando documento Word...")
    update_word_document(output_figures, output_tables)
    
    print("\n" + "=" * 70)
    print("PROCESO COMPLETADO")
    print("=" * 70)


if __name__ == '__main__':
    main()
