"""
Generador de tabla y grafica de imputacion por METODOS de imputacion (L1, L2, L3, L4)
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
    """Carga los datos imputados v4.2."""
    df = pd.read_csv(INPUT_FILE)
    df['Fecha'] = pd.to_datetime(df['Fecha'], format='%d-%m-%Y')
    return df

def generar_tabla_metodos(df):
    """Genera tabla de imputacion por metodos (L1, L2, L3, L4)."""
    print('=' * 130)
    print('TABLA: IMPUTACION POR METODOS DE IMPUTACION POR ESTACION')
    print('=' * 130)
    print()
    
    resumen = []
    for estacion in sorted(df['NombreEstacion'].unique()):
        est_df = df[df['NombreEstacion'] == estacion]
        
        total_registros = len(est_df)
        
        # Datos medidos (originales con valor valido)
        datos_medidos = ((est_df['Metodo'] == 'Original') & (est_df['Cota'].notna())).sum()
        
        # Imputados por metodo/nivel
        imp_L1 = est_df[est_df['Metodo'] == 'L1_Interpolacion']['Cota'].notna().sum()
        imp_L2 = est_df[est_df['Metodo'] == 'L2_HH_quadratic']['Cota'].notna().sum()
        imp_L3 = est_df[est_df['Metodo'] == 'L3_HH_quadratic']['Cota'].notna().sum()
        imp_L4 = est_df[est_df['Metodo'].isin(['L4_HH_quadratic', 'L4_missForest'])]['Cota'].notna().sum()
        
        total_imputados = imp_L1 + imp_L2 + imp_L3 + imp_L4
        pct_imp_total = (total_imputados / total_registros * 100) if total_registros > 0 else 0
        
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
            'Imputados_L4': imp_L4,
            'Total_Imputados': total_imputados,
            'Pct_Imputado': pct_imp_total
        })
    
    metodos_df = pd.DataFrame(resumen)
    
    # Formatear para mostrar
    display_df = metodos_df.copy()
    display_df['Pct_Imputado'] = display_df['Pct_Imputado'].apply(lambda x: f"{x:.1f}%")
    print(display_df.to_string(index=False))
    print()
    print('-' * 130)
    
    # Totales
    totales = {
        'Estacion': 'TOTAL GENERAL',
        'Periodo': '',
        'Total_Registros': metodos_df['Total_Registros'].sum(),
        'Datos_Medidos': metodos_df['Datos_Medidos'].sum(),
        'Imputados_L1': metodos_df['Imputados_L1'].sum(),
        'Imputados_L2': metodos_df['Imputados_L2'].sum(),
        'Imputados_L3': metodos_df['Imputados_L3'].sum(),
        'Imputados_L4': metodos_df['Imputados_L4'].sum(),
        'Total_Imputados': metodos_df['Total_Imputados'].sum(),
        'Pct_Imputado': f"{(metodos_df['Total_Imputados'].sum() / metodos_df['Total_Registros'].sum() * 100):.1f}%"
    }
    print(f"{totales['Estacion']:<20} | {totales['Periodo']:<10} | {totales['Total_Registros']:>8} | {totales['Datos_Medidos']:>8} | {totales['Imputados_L1']:>8} | {totales['Imputados_L2']:>8} | {totales['Imputados_L3']:>8} | {totales['Imputados_L4']:>8} | {totales['Total_Imputados']:>8} | {totales['Pct_Imputado']:>8}")
    
    return metodos_df

def graficar_metodos_por_estacion(metodos_df, output_path):
    """Grafica barras apiladas de imputacion por metodos por estacion."""
    fig, ax = plt.subplots(figsize=(18, 8))
    
    x = np.arange(len(metodos_df))
    width = 0.7
    
    # Colores por metodo
    color_L1 = '#F4A261'  # Naranja claro
    color_L2 = '#E76F51'  # Naranja/rojo
    color_L3 = '#264653'  # Azul oscuro
    color_L4 = '#2A9D8F'  # Verde azulado
    
    bars1 = ax.bar(x, metodos_df['Imputados_L1'], width, label='L1 (Interpolacion)', color=color_L1, edgecolor='black')
    bars2 = ax.bar(x, metodos_df['Imputados_L2'], width, bottom=metodos_df['Imputados_L1'], 
                   label='L2 (HH Quadratic)', color=color_L2, edgecolor='black')
    bars3 = ax.bar(x, metodos_df['Imputados_L3'], width, 
                   bottom=metodos_df['Imputados_L1'] + metodos_df['Imputados_L2'],
                   label='L3 (HH Quadratic)', color=color_L3, edgecolor='black')
    bars4 = ax.bar(x, metodos_df['Imputados_L4'], width, 
                   bottom=metodos_df['Imputados_L1'] + metodos_df['Imputados_L2'] + metodos_df['Imputados_L3'],
                   label='L4 (HH Quadratic/missForest)', color=color_L4, edgecolor='black')
    
    # Porcentaje total encima de cada barra
    for i, (idx, row) in enumerate(metodos_df.iterrows()):
        total_imp = row['Total_Imputados']
        pct = row['Pct_Imputado']
        if total_imp > 0:
            ax.text(i, total_imp + max(metodos_df['Total_Imputados']) * 0.02, 
                    f'{pct:.1f}%', ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    ax.set_xlabel('Estacion', fontsize=12)
    ax.set_ylabel('Numero de Datos Imputados', fontsize=12)
    ax.set_title('Datos Imputados por Metodo de Imputacion y Estacion\n(L1: Interpolacion, L2/L3/L4: HH Quadratic)', 
                 fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(metodos_df['Estacion'], rotation=45, ha='right', fontsize=9)
    ax.legend(loc='upper right', fontsize=10)
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'Grafica guardada: {output_path}')
    return True

def main():
    """Genera tabla y grafica de imputacion por metodos."""
    print("=" * 100)
    print("GENERADOR DE TABLA Y GRAFICA - METODOS DE IMPUTACION")
    print("=" * 100)
    print()
    
    # Cargar datos
    df = load_data()
    print(f"Datos cargados: {len(df):,} registros")
    print(f"Estaciones: {df['NombreEstacion'].nunique()}")
    print()
    
    # Tabla por metodos de imputacion
    metodos_df = generar_tabla_metodos(df)
    
    # Grafica
    graficar_metodos_por_estacion(metodos_df, OUTPUT_DIR / 'Grafica_Imputados_por_Metodo_Estacion.png')
    
    print()
    print("=" * 100)
    print("PROCESO COMPLETADO")
    print(f"Directorio: {OUTPUT_DIR}")

if __name__ == '__main__':
    main()
