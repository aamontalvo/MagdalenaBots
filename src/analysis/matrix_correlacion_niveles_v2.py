"""
Matriz de Correlacion de Niveles - Version 2
============================================
- Datos originales/medidos IDEAM (NO imputados)
- Correspondencia temporal estricta por fecha
- Escala de colores azul (0 a 1)
- Sin lineas de division de cuencas
- Nombres de estaciones formateados: "El Contento"
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from scipy.stats import pearsonr
import warnings
warnings.filterwarnings('ignore')

# ---------------------------------------------------------------------------
# CONFIGURACION
# ---------------------------------------------------------------------------
RAW_DATA_DIR = Path(r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\backend\data\raw\SERIE NIVELES IDEAM A 2026')
OUTPUT_PATH = Path(r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\Imagenes\Niveles\MatrixCorrelationNiveles_v2.png')

# Orden geografico: aguas abajo -> aguas arriba
GEOGRAPHIC_ORDER = [
    'SAN_PEDRITO', 'CALAMAR', 'TENERIFE', 'PLATO', 'MAGANGUE', 'BARBOSA', 'COYONGAL',
    'ARMENIA', 'RIO_NUEVO', 'LAS_PALOMAS', 'LAS_AGUADAS', 'EL_BANCO', 'PENONCITO',
    'LA_GLORIA', 'GAMARRA_AUT', 'EL_CONTENTO', 'SITIO_NUEVO', 'PUERTO_WILCHES',
]

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


# ---------------------------------------------------------------------------
# FUNCIONES DE CARGA
# ---------------------------------------------------------------------------
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
    
    # Detectar formato de la columna de fechas
    # Algunas estaciones (ej: San Pedrito) usan float MM.DD en lugar de datetime
    first_val = df_wide.iloc[0, 0]
    is_float_date = isinstance(first_val, (int, float)) and not isinstance(first_val, bool)
    
    for year in year_cols:
        year_data = df_wide[[date_col, year]].copy()
        year_data = year_data.dropna(subset=[year])
        
        for _, row in year_data.iterrows():
            try:
                date_val = row[date_col]
                
                if is_float_date and pd.notna(date_val):
                    # Formato MM.DD (ej: 1.01 = 1 de enero, 12.31 = 31 de diciembre)
                    val = float(date_val)
                    month = int(val)
                    day = int(round((val - month) * 100))
                else:
                    # Formato datetime normal
                    ref_date = pd.to_datetime(date_val)
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
    """Carga todas las estaciones desde archivos Excel originales."""
    data_dir = Path(data_dir)
    all_data = []
    
    for file in sorted(data_dir.glob('*.xlsx')):
        df = load_station_data(file)
        if df is not None and len(df) > 0:
            all_data.append(df)
    
    return pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()


# ---------------------------------------------------------------------------
# FUNCIONES DE CORRELACION
# ---------------------------------------------------------------------------
def get_common_period(df, station1, station2):
    """Obtiene periodo con datos concurrentes entre dos estaciones (mismo indice de fecha)."""
    df1 = df[df['station'] == station1][['date', 'level']].copy()
    df2 = df[df['station'] == station2][['date', 'level']].copy()
    
    merged = pd.merge(df1, df2, on='date', suffixes=('_1', '_2'))
    merged = merged.dropna(subset=['level_1', 'level_2'])
    
    return merged


def calculate_correlation_matrix(df):
    """Calcula matriz de correlacion usando SOLO datos medidos concurrentes."""
    stations = [s for s in GEOGRAPHIC_ORDER if s in df['station'].values]
    corr_matrix = pd.DataFrame(index=stations, columns=stations)
    
    # Matriz de dias concurrentes (para reporte)
    n_matrix = pd.DataFrame(index=stations, columns=stations)
    
    for s1 in stations:
        for s2 in stations:
            if s1 == s2:
                corr_matrix.loc[s1, s2] = 1.0
                n_matrix.loc[s1, s2] = df[df['station'] == s1]['level'].notna().sum()
            else:
                common = get_common_period(df, s1, s2)
                if len(common) > 30:
                    corr, _ = pearsonr(common['level_1'], common['level_2'])
                    corr_matrix.loc[s1, s2] = corr
                    n_matrix.loc[s1, s2] = len(common)
                else:
                    corr_matrix.loc[s1, s2] = np.nan
                    n_matrix.loc[s1, s2] = len(common) if len(common) > 0 else 0
    
    corr_matrix = corr_matrix.astype(float)
    n_matrix = n_matrix.astype(float)
    
    return corr_matrix, n_matrix


def format_station_name(name):
    """Formatea nombre de estacion: EL_CONTENTO -> El Contento"""
    return name.replace('_', ' ').title()


# ---------------------------------------------------------------------------
# VISUALIZACION
# ---------------------------------------------------------------------------
def plot_correlation_matrix(corr_matrix, output_path):
    """Genera heatmap de matriz de correlacion con especificaciones v2."""
    
    # Formatear nombres de estaciones
    formatted_names = [format_station_name(s) for s in corr_matrix.index]
    corr_matrix.index = formatted_names
    corr_matrix.columns = formatted_names
    
    # Plot
    fig, ax = plt.subplots(figsize=(14, 12))
    
    # Mascara triangulo superior
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool), k=1)
    
    # Colormap azul: 0 = blanco/claro, 1 = azul oscuro
    sns.heatmap(
        corr_matrix, 
        mask=mask,
        annot=True, 
        fmt='.2f',
        cmap='Blues',           # Escala de azules
        vmin=0, vmax=1,         # Rango 0 a 1 (no hay correlaciones negativas)
        square=True,
        linewidths=0.5,
        linecolor='white',
        cbar_kws={
            'label': 'Correlacion de Pearson',
            'shrink': 0.8,
        },
        ax=ax
    )
    
    # SIN lineas de separacion de zonas (eliminadas segun solicitud)
    # ax.axhline(...)
    # ax.axvline(...)
    
    ax.set_title(
        'Matriz de Correlacion entre Estaciones\n' +
        '(Datos medidos originales IDEAM - Solo triangulo inferior)', 
        fontsize=13, fontweight='bold', pad=15
    )
    
    plt.xticks(rotation=45, ha='right', fontsize=10)
    plt.yticks(rotation=0, fontsize=10)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"Guardado: {output_path}")
    return fig


# ---------------------------------------------------------------------------
# EXPORTAR MATRICES A CSV
# ---------------------------------------------------------------------------
def export_matrices(corr_matrix, n_matrix, output_dir):
    """Exporta matrices de correlacion y N a CSV."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Formatear nombres
    formatted_names = [format_station_name(s) for s in corr_matrix.index]
    corr_matrix.index = formatted_names
    corr_matrix.columns = formatted_names
    n_matrix.index = formatted_names
    n_matrix.columns = formatted_names
    
    corr_matrix.to_csv(output_dir / 'Matriz_Correlacion_Niveles.csv', encoding='utf-8-sig')
    n_matrix.to_csv(output_dir / 'Matriz_N_Concurrentes_Niveles.csv', encoding='utf-8-sig')
    
    print(f"Matrices exportadas en: {output_dir}")


# ---------------------------------------------------------------------------
# REPORTE DE PARES
# ---------------------------------------------------------------------------
def export_pairs_report(corr_matrix, n_matrix, output_path, min_corr=0.7):
    """Exporta reporte de pares con alta correlacion."""
    records = []
    stations = corr_matrix.index.tolist()
    
    for i, s1 in enumerate(stations):
        for j, s2 in enumerate(stations):
            if i >= j:
                continue
            val = corr_matrix.loc[s1, s2]
            n = n_matrix.loc[s1, s2]
            if pd.notna(val) and val >= min_corr:
                records.append({
                    'Estacion_1': s1,
                    'Estacion_2': s2,
                    'Correlacion_Pearson': round(val, 4),
                    'Dias_Concurrentes': int(n),
                })
    
    df_pairs = pd.DataFrame(records).sort_values('Correlacion_Pearson', ascending=False)
    df_pairs.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"Reporte de pares exportado: {output_path}")
    return df_pairs


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main():
    print("=" * 70)
    print("MATRIZ DE CORRELACION DE NIVELES - V2")
    print("Datos: Originales IDEAM (NO imputados)")
    print("=" * 70)
    
    # 1. Cargar datos originales
    print("\n[1/4] Cargando datos originales IDEAM...")
    df = load_all_stations(RAW_DATA_DIR)
    print(f"  Total registros: {len(df):,}")
    print(f"  Estaciones: {df['station'].nunique()}")
    print(f"  Rango: {df['date'].min().date()} a {df['date'].max().date()}")
    
    # 2. Calcular matriz de correlacion
    print("\n[2/4] Calculando correlaciones (solo datos concurrentes)...")
    corr_matrix, n_matrix = calculate_correlation_matrix(df)
    print(f"  Matriz: {corr_matrix.shape}")
    
    # 3. Generar grafica
    print("\n[3/4] Generando heatmap v2...")
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    plot_correlation_matrix(corr_matrix, OUTPUT_PATH)
    
    # 4. Exportar matrices y reporte
    print("\n[4/4] Exportando matrices y reporte de pares...")
    export_matrices(corr_matrix, n_matrix, OUTPUT_PATH.parent)
    
    pairs_path = OUTPUT_PATH.parent / 'Pares_Alta_Correlacion.csv'
    df_pairs = export_pairs_report(corr_matrix, n_matrix, pairs_path, min_corr=0.7)
    
    print("\n" + "=" * 70)
    print("PROCESO COMPLETADO")
    print("=" * 70)
    print(f"Figura: {OUTPUT_PATH}")
    print(f"\nTop 5 pares con mayor correlacion:")
    for _, row in df_pairs.head(5).iterrows():
        print(f"  {row['Estacion_1']} - {row['Estacion_2']}: r = {row['Correlacion_Pearson']:.3f}  (n = {row['Dias_Concurrentes']:,} dias)")


if __name__ == '__main__':
    main()
