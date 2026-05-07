"""
Grafico de barras apiladas (stacked bars) - Composicion de Imputacion v4.3
Muestra el porcentaje de cada nivel de imputacion por estacion.
Eje X: estaciones | Eje Y: porcentaje (0-100%)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Configuracion
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12

# Colores
COLOR_L0 = '#9E9E9E'      # Gris - Original
COLOR_L1 = '#FF9800'      # Naranja - Interpolacion
COLOR_L2 = '#4CAF50'      # Verde - H-H Cuadratico
COLOR_L3 = '#F44336'      # Rojo - missForest


def clasificar_metodo(metodo_str):
    """Clasifica el metodo del CSV en L0-L3."""
    if metodo_str == 'Original':
        return 'L0'
    elif metodo_str == 'L1_Interpolacion':
        return 'L1'
    elif metodo_str.startswith('L2_HH_') and 'quadratic' in metodo_str:
        return 'L2'
    elif metodo_str == 'L3_missForest':
        return 'L3'
    else:
        return 'L3'


def generar_stacked_bars():
    """Genera el grafico de barras apiladas."""
    # Cargar datos
    data_path = Path(r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\backend\data\processed\imputation')
    df = pd.read_csv(data_path / 'Datos_Imputados_v4_3_Corrected.csv')
    
    # Clasificar metodos
    df['nivel_imp'] = df['Metodo'].apply(clasificar_metodo)
    
    # Calcular totales por estacion y nivel
    summary = df.groupby(['NombreEstacion', 'nivel_imp']).size().unstack(fill_value=0)
    
    # Asegurar columnas L0-L3
    for col in ['L0', 'L1', 'L2', 'L3']:
        if col not in summary.columns:
            summary[col] = 0
    
    # Calcular porcentajes
    summary['total'] = summary[['L0', 'L1', 'L2', 'L3']].sum(axis=1)
    for col in ['L0', 'L1', 'L2', 'L3']:
        summary[f'{col}_pct'] = summary[col] / summary['total'] * 100
    
    # Ordenar por orden hidrologico (aguas abajo -> arriba)
    geo_order = [
        'SAN_PEDRITO', 'CALAMAR', 'TENERIFE', 'PLATO', 'MAGANGUE', 'BARBOSA',
        'COYONGAL', 'ARMENIA', 'RIO_NUEVO', 'LAS_PALOMAS', 'LAS_AGUADAS',
        'EL_BANCO', 'PENONCITO', 'LA_GLORIA', 'GAMARRA_AUT', 'EL_CONTENTO',
        'SITIO_NUEVO', 'PUERTO_WILCHES'
    ]
    # Filtrar solo las que existen en los datos
    geo_order = [s for s in geo_order if s in summary.index]
    # Agregar cualquier otra que no esté en la lista
    for s in summary.index:
        if s not in geo_order:
            geo_order.append(s)
    
    summary = summary.reindex(geo_order)
    
    # Crear figura
    fig, ax = plt.subplots(figsize=(16, 8))
    
    x = np.arange(len(summary))
    width = 0.65
    
    # Barras apiladas
    bottom_l1 = summary['L0_pct'].values
    bottom_l2 = bottom_l1 + summary['L1_pct'].values
    bottom_l3 = bottom_l2 + summary['L2_pct'].values
    
    bars_l0 = ax.bar(x, summary['L0_pct'], width, label='L0 - Original', color=COLOR_L0, edgecolor='white', linewidth=0.5)
    bars_l1 = ax.bar(x, summary['L1_pct'], width, bottom=bottom_l1, label='L1 - Interpolacion', color=COLOR_L1, edgecolor='white', linewidth=0.5)
    bars_l2 = ax.bar(x, summary['L2_pct'], width, bottom=bottom_l2, label='L2 - H-H Cuadratico', color=COLOR_L2, edgecolor='white', linewidth=0.5)
    bars_l3 = ax.bar(x, summary['L3_pct'], width, bottom=bottom_l3, label='L3 - missForest', color=COLOR_L3, edgecolor='white', linewidth=0.5)
    
    # Etiquetas con porcentaje de imputados (solo si > 1%)
    for i, (idx, row) in enumerate(summary.iterrows()):
        imp_pct = 100 - row['L0_pct']
        if imp_pct > 1:
            ax.text(i, 102, f'{imp_pct:.1f}%', ha='center', va='bottom', fontsize=8, fontweight='bold', color='#424242')
        # Etiqueta de L0 en el centro de la barra gris
        if row['L0_pct'] > 15:
            ax.text(i, row['L0_pct'] / 2, f'{row["L0_pct"]:.0f}%', ha='center', va='center', fontsize=8, color='white', fontweight='bold')
    
    # Formato
    ax.set_xticks(x)
    ax.set_xticklabels([s.replace('_', ' ') for s in summary.index], rotation=45, ha='right', fontsize=9)
    ax.set_ylabel('Porcentaje de completitud (%)', fontsize=12)
    ax.set_xlabel('Estacion (aguas abajo \u2192 arriba)', fontsize=12)
    ax.set_title('Composicion de Imputacion v4.3 por Estacion\nPorcentaje de datos originales e imputados (L1, L2, L3)',
                 fontsize=14, fontweight='bold')
    ax.set_ylim(0, 115)
    ax.set_yticks(range(0, 101, 10))
    ax.grid(True, alpha=0.3, axis='y')
    ax.axhline(y=100, color='black', linestyle='--', linewidth=0.8, alpha=0.5)
    
    # Leyenda
    ax.legend(loc='upper right', fontsize=10, framealpha=0.95, edgecolor='gray')
    
    # Anotacion de estaciones descartadas
    descartadas = ['ARMENIA', 'BARBOSA', 'TENERIFE', 'SITIO_NUEVO']
    for i, est in enumerate(summary.index):
        if est in descartadas:
            ax.text(i, -8, '†', ha='center', va='top', fontsize=14, color='red', fontweight='bold')
    
    # Nota al pie
    fig.text(0.12, 0.02, '† Estaciones descartadas por homogeneidad (mantenidas con imputacion L3)',
             fontsize=9, style='italic', color='#616161')
    
    plt.tight_layout(rect=[0, 0.05, 1, 1])
    
    # Guardar
    output_dir = Path(r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\cartillas_estaciones\v4_3')
    output_dir.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_dir / 'Stacked_Bars_Composicion_Imputacion_v4_3.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Guardar tabla CSV
    csv_out = summary[['L0', 'L1', 'L2', 'L3', 'total', 'L0_pct', 'L1_pct', 'L2_pct', 'L3_pct']].copy()
    csv_out.columns = ['L0_Original', 'L1_Interpolacion', 'L2_HH', 'L3_missForest', 'Total',
                       'Pct_L0', 'Pct_L1', 'Pct_L2', 'Pct_L3']
    csv_out.to_csv(output_dir / 'Composicion_Imputacion_v4_3.csv')
    
    print(f"Grafico guardado: {output_dir / 'Stacked_Bars_Composicion_Imputacion_v4_3.png'}")
    print(f"Tabla CSV guardada: {output_dir / 'Composicion_Imputacion_v4_3.csv'}")
    print("\nResumen por estacion:")
    print(csv_out[['Pct_L0', 'Pct_L1', 'Pct_L2', 'Pct_L3']].round(1).to_string())
    
    return csv_out


if __name__ == '__main__':
    generar_stacked_bars()
