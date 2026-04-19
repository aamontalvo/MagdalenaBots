"""
Generador de tablas y graficas de imputacion por rangos de cotas y por niveles
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Rutas
INPUT_FILE = Path(r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\Informes\imputacion\Datos_Imputados_v4_2_Complete.csv')
OUTPUT_DIR = Path(r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\cartillas_estaciones\v4_2')

def load_data():
    """Carga los datos imputados."""
    df = pd.read_csv(INPUT_FILE)
    df['Fecha'] = pd.to_datetime(df['Fecha'], format='%d-%m-%Y')
    return df

def generar_tabla_rangos(df):
    """Genera tabla de porcentaje de imputados por rangos de cotas."""
    print('=' * 100)
    print('TABLA: PORCENTAJE DE IMPUTADOS POR RANGOS DE COTAS')
    print('=' * 100)
    print()
    
    df_valid = df[df['Cota'].notna()].copy()
    
    # Definir rangos
    bins = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 100]
    labels = ['0-5m', '5-10m', '10-15m', '15-20m', '20-25m', '25-30m', '30-35m', '35-40m', '40-45m', '45-50m', '>50m']
    
    df_valid['rango'] = pd.cut(df_valid['Cota'], bins=bins, labels=labels, include_lowest=True)
    
    rango_resumen = []
    for rango in labels:
        rango_df = df_valid[df_valid['rango'] == rango]
        if len(rango_df) > 0:
            total = len(rango_df)
            originales = (rango_df['Metodo'] == 'Original').sum()
            imputados = total - originales
            pct_imp = (imputados / total * 100) if total > 0 else 0
            
            rango_resumen.append({
                'Rango_Cota': rango,
                'Total_Registros': total,
                'Originales': originales,
                'Imputados': imputados,
                'Pct_Imputado': pct_imp
            })
    
    rango_df = pd.DataFrame(rango_resumen)
    print(rango_df.to_string(index=False))
    print()
    
    return rango_df

def graficar_rangos(rango_df, output_path):
    """Grafica barras de porcentaje de imputados por rangos de cotas."""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    colores = ['#2E86AB' if p < 10 else '#F18F01' if p < 20 else '#C73E1D' for p in rango_df['Pct_Imputado']]
    
    bars = ax.bar(rango_df['Rango_Cota'], rango_df['Pct_Imputado'], color=colores, edgecolor='black', alpha=0.8)
    
    # Valores encima de barras
    for bar, pct in zip(bars, rango_df['Pct_Imputado']):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{pct:.1f}%', ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    ax.set_xlabel('Rango de Cota (m.s.n.m.)', fontsize=12)
    ax.set_ylabel('Porcentaje Imputado (%)', fontsize=12)
    ax.set_title('Porcentaje de Datos Imputados por Rangos de Cotas', fontsize=14, fontweight='bold')
    ax.set_ylim(0, max(rango_df['Pct_Imputado']) * 1.15)
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'Grafica guardada: {output_path}')
    return True

def generar_tabla_niveles(df):
    """Genera tabla de imputacion por niveles (L1, L2, L3) por estacion."""
    print()
    print('=' * 120)
    print('TABLA: IMPUTACION POR NIVELES POR ESTACION')
    print('=' * 120)
    print()
    
    resumen = []
    for estacion in sorted(df['NombreEstacion'].unique()):
        est_df = df[df['NombreEstacion'] == estacion]
        
        total_registros = len(est_df)
        con_cota = est_df['Cota'].notna().sum()
        
        # Datos medidos (originales)
        datos_medidos = ((est_df['Metodo'] == 'Original') & (est_df['Cota'].notna())).sum()
        
        # Imputados por nivel (basado en el valor de Cota o patrones)
        # L1: valores entre 0-15m (aproximacion basica)
        # L2: valores entre 15-35m
        # L3: valores >35m
        
        imputados_df = est_df[(est_df['Metodo'] != 'Original') & (est_df['Cota'].notna())]
        
        imp_L1 = ((imputados_df['Cota'] >= 0) & (imputados_df['Cota'] < 15)).sum()
        imp_L2 = ((imputados_df['Cota'] >= 15) & (imputados_df['Cota'] < 35)).sum()
        imp_L3 = (imputados_df['Cota'] >= 35).sum()
        
        total_imputados = len(imputados_df)
        pct_imp_total = (total_imputados / con_cota * 100) if con_cota > 0 else 0
        
        fecha_inicio = est_df['Fecha'].min().strftime('%Y')
        fecha_fin = est_df['Fecha'].max().strftime('%Y')
        
        resumen.append({
            'Estacion': estacion,
            'Periodo': f"{fecha_inicio}-{fecha_fin}",
            'Total_Registros': total_registros,
            'Datos_Medidos': datos_medidos,
            'Imputados_L1': imp_L1,
            'Imputados_L2': imp_L2,
            'Imputados_L3': imp_L3,
            'Total_Imputados': total_imputados,
            'Pct_Imputado': pct_imp_total
        })
    
    niveles_df = pd.DataFrame(resumen)
    
    # Formatear para mostrar
    display_df = niveles_df.copy()
    display_df['Pct_Imputado'] = display_df['Pct_Imputado'].apply(lambda x: f"{x:.1f}%")
    print(display_df.to_string(index=False))
    print()
    print('-' * 120)
    
    # Totales
    totales = {
        'Estacion': 'TOTAL GENERAL',
        'Periodo': '',
        'Total_Registros': niveles_df['Total_Registros'].sum(),
        'Datos_Medidos': niveles_df['Datos_Medidos'].sum(),
        'Imputados_L1': niveles_df['Imputados_L1'].sum(),
        'Imputados_L2': niveles_df['Imputados_L2'].sum(),
        'Imputados_L3': niveles_df['Imputados_L3'].sum(),
        'Total_Imputados': niveles_df['Total_Imputados'].sum(),
        'Pct_Imputado': f"{(niveles_df['Total_Imputados'].sum() / niveles_df['Total_Registros'].sum() * 100):.1f}%"
    }
    print(f"{totales['Estacion']:<20} | {totales['Periodo']:<10} | {totales['Total_Registros']:>8} | {totales['Datos_Medidos']:>8} | {totales['Imputados_L1']:>8} | {totales['Imputados_L2']:>8} | {totales['Imputados_L3']:>8} | {totales['Total_Imputados']:>8} | {totales['Pct_Imputado']:>8}")
    
    return niveles_df

def graficar_niveles_por_estacion(niveles_df, output_path):
    """Grafica barras apiladas de imputacion por niveles por estacion."""
    fig, ax = plt.subplots(figsize=(16, 8))
    
    x = np.arange(len(niveles_df))
    width = 0.6
    
    # Colores por nivel
    color_L1 = '#F4A261'  # Naranja claro
    color_L2 = '#E76F51'  # Naranja/rojo
    color_L3 = '#264653'  # Azul oscuro
    
    bars1 = ax.bar(x, niveles_df['Imputados_L1'], width, label='L1 (0-15m)', color=color_L1, edgecolor='black')
    bars2 = ax.bar(x, niveles_df['Imputados_L2'], width, bottom=niveles_df['Imputados_L1'], 
                   label='L2 (15-35m)', color=color_L2, edgecolor='black')
    bars3 = ax.bar(x, niveles_df['Imputados_L3'], width, 
                   bottom=niveles_df['Imputados_L1'] + niveles_df['Imputados_L2'],
                   label='L3 (>35m)', color=color_L3, edgecolor='black')
    
    # Porcentaje total encima de cada barra
    for i, (idx, row) in enumerate(niveles_df.iterrows()):
        total_imp = row['Total_Imputados']
        pct = row['Pct_Imputado']
        ax.text(i, total_imp + max(niveles_df['Total_Imputados']) * 0.02, 
                f'{pct:.1f}%', ha='center', va='bottom', fontsize=8, fontweight='bold')
    
    ax.set_xlabel('Estacion', fontsize=12)
    ax.set_ylabel('Numero de Datos Imputados', fontsize=12)
    ax.set_title('Datos Imputados por Nivel y Estacion\n(L1: 0-15m, L2: 15-35m, L3: >35m)', 
                 fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(niveles_df['Estacion'], rotation=45, ha='right', fontsize=9)
    ax.legend(loc='upper right', fontsize=10)
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'Grafica guardada: {output_path}')
    return True

def main():
    """Genera tablas y graficas de imputacion."""
    print("=" * 100)
    print("GENERADOR DE TABLAS Y GRAFICAS DE IMPUTACION")
    print("=" * 100)
    print()
    
    # Cargar datos
    df = load_data()
    print(f"Datos cargados: {len(df):,} registros")
    print(f"Estaciones: {df['NombreEstacion'].nunique()}")
    print()
    
    # Tabla y grafica por rangos de cotas
    rango_df = generar_tabla_rangos(df)
    graficar_rangos(rango_df, OUTPUT_DIR / 'Grafica_Imputados_por_Rangos_Cotas.png')
    
    print()
    
    # Tabla y grafica por niveles por estacion
    niveles_df = generar_tabla_niveles(df)
    graficar_niveles_por_estacion(niveles_df, OUTPUT_DIR / 'Grafica_Imputados_por_Niveles_Estacion.png')
    
    print()
    print("=" * 100)
    print("PROCESO COMPLETADO")
    print(f"Directorio de salida: {OUTPUT_DIR}")
    print()
    print("Archivos generados:")
    print(f"  - {OUTPUT_DIR / 'Grafica_Imputados_por_Rangos_Cotas.png'}")
    print(f"  - {OUTPUT_DIR / 'Grafica_Imputados_por_Niveles_Estacion.png'}")

if __name__ == '__main__':
    main()
