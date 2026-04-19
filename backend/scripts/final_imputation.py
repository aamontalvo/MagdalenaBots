#!/usr/bin/env python3
"""
Imputacion Final - Seccion de Analisis de Hidrologia
====================================================

Imputacion usando H-H Simple (modelo cuadratico) para todas las estaciones:
- Calamar ← Magangue
- Las Aguadas ← El Banco  
- El Banco ← La Gloria

Autor: Seccion de Analisis de Hidrologia
Fecha: 2026-02-25
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from sklearn.metrics import r2_score, mean_squared_error
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Rutas
DATA_PATH = Path(r"C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\Data\Niveles")
PROCESSED_PATH = DATA_PATH / "01_processed"
ANALYSIS_PATH = DATA_PATH / "02_analysis"
FIGURES_PATH = DATA_PATH / "03_figures" / "imputation"


def format_significant(x, n=4):
    if pd.isna(x):
        return x
    if isinstance(x, (int, np.integer)):
        return int(x)
    return float(f"{x:.{n}g}")


def quadratic_model(x, a, b, c):
    """Modelo cuadratico: y = ax^2 + bx + c"""
    return a * x**2 + b * x + c


def build_hh_model(target_data, donor_data, target_name, donor_name):
    """Construye modelo H-H cuadratico y evalua."""
    
    # Merge datos
    merged = pd.merge(target_data, donor_data, on='fecha', 
                     suffixes=('_target', '_donor'))
    merged = merged.dropna()
    
    if len(merged) < 30:
        return None
    
    x = merged['nivel_msnm_donor'].values
    y = merged['nivel_msnm_target'].values
    
    # Ajustar modelo cuadratico
    try:
        popt, _ = curve_fit(quadratic_model, x, y)
        y_pred = quadratic_model(x, *popt)
        r2 = r2_score(y, y_pred)
        
        # Validacion cruzada
        np.random.seed(42)
        mask = np.random.rand(len(x)) < 0.8
        if mask.sum() > 10 and (~mask).sum() > 10:
            popt_cv, _ = curve_fit(quadratic_model, x[mask], y[mask])
            y_pred_cv = quadratic_model(x[~mask], *popt_cv)
            rmse_cv = np.sqrt(mean_squared_error(y[~mask], y_pred_cv))
        else:
            rmse_cv = np.sqrt(mean_squared_error(y, y_pred))
        
        return {
            'params': popt,
            'r2': r2,
            'rmse_cv': rmse_cv,
            'equation': f"y = {popt[0]:.4f}x^2 + {popt[1]:.4f}x + {popt[2]:.4f}",
            'n_points': len(merged)
        }
    except:
        return None


def run_final_imputation():
    """Ejecuta imputacion final con H-H simple."""
    
    print("=" * 70)
    print("IMPUTACION FINAL - H-H SIMPLE (CUADRATICO)")
    print("=" * 70)
    
    # Cargar datos
    df = pd.read_csv(PROCESSED_PATH / "magdalena_levels_long_format.csv")
    df['fecha'] = pd.to_datetime(df['fecha'])
    
    # Definir relaciones: target -> (donor, nombre)
    hh_relationships = {
        'Calamar': ('Magangue', 'Magangue'),
        'Las Aguadas': ('El Banco', 'El Banco'),
        'El Banco': ('La Gloria', 'La Gloria')
    }
    
    # DataFrame para resultados
    df_imputed = df.copy()
    df_imputed['nivel_msnm_original'] = df_imputed['nivel_msnm']
    df_imputed['imputed'] = False
    df_imputed['imputation_method'] = None
    df_imputed['donor_station'] = None
    df_imputed['imputation_r2'] = np.nan
    
    models = {}
    imputation_stats = []
    total_imputed = 0
    
    for station, (donor, donor_label) in hh_relationships.items():
        print(f"\n{station} ← {donor}:")
        
        # Obtener datos
        target_data = df[df['estacion'] == station][['fecha', 'nivel_msnm']].copy()
        donor_data = df[df['estacion'] == donor][['fecha', 'nivel_msnm']].copy()
        
        # Construir modelo
        model = build_hh_model(target_data, donor_data, station, donor)
        
        if not model:
            print(f"  ERROR: No se pudo construir modelo")
            continue
        
        models[station] = model
        
        print(f"  Ecuacion: {model['equation']}")
        print(f"  R2 = {model['r2']:.4f}, RMSE-CV = {model['rmse_cv']:.4f} m")
        print(f"  N puntos concurrentes: {model['n_points']}")
        
        # Imputar valores faltantes
        station_mask = (df_imputed['estacion'] == station) & (df_imputed['nivel_msnm'].isna())
        missing_dates = df_imputed[station_mask]['fecha']
        
        if len(missing_dates) == 0:
            print(f"  No hay valores faltantes para imputar")
            continue
        
        # Obtener valores del donante para fechas faltantes
        donor_for_missing = donor_data[donor_data['fecha'].isin(missing_dates)]
        
        imputed_count = 0
        for _, row in donor_for_missing.iterrows():
            if pd.notna(row['nivel_msnm']):
                # Aplicar modelo cuadratico
                x = row['nivel_msnm']
                a, b, c = model['params']
                imputed_value = a * x**2 + b * x + c
                
                # Actualizar
                mask = (df_imputed['estacion'] == station) & (df_imputed['fecha'] == row['fecha'])
                df_imputed.loc[mask, 'nivel_msnm'] = imputed_value
                df_imputed.loc[mask, 'imputed'] = True
                df_imputed.loc[mask, 'imputation_method'] = f"HH_{donor}_cuadratico"
                df_imputed.loc[mask, 'donor_station'] = donor
                df_imputed.loc[mask, 'imputation_r2'] = model['r2']
                
                imputed_count += 1
        
        total_imputed += imputed_count
        
        imputation_stats.append({
            'Estacion': station,
            'Donante': donor,
            'Modelo': 'H-H Cuadratico',
            'Ecuacion': model['equation'],
            'R2': format_significant(model['r2'], 4),
            'RMSE_CV_m': format_significant(model['rmse_cv'], 4),
            'Valores_Imputados': imputed_count,
            'N_Concurrentes': model['n_points']
        })
        
        print(f"  -> {imputed_count} valores imputados")
    
    # Guardar resultados
    print(f"\n{'='*70}")
    print(f"TOTAL VALORES IMPUTADOS: {total_imputed:,}")
    print(f"{'='*70}")
    
    # Guardar estadisticas
    stats_df = pd.DataFrame(imputation_stats)
    stats_df.to_csv(ANALYSIS_PATH / "final_imputation_statistics.csv", index=False)
    print("\nResumen de imputacion:")
    print(stats_df.to_string(index=False))
    
    # Guardar datos imputados
    output_csv = PROCESSED_PATH / "magdalena_levels_imputed_final.csv"
    df_imputed.to_csv(output_csv, index=False)
    print(f"\nDataset imputado guardado: {output_csv}")
    
    # Generar figura
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    for idx, (station, (donor, _)) in enumerate(hh_relationships.items()):
        ax = axes[idx]
        
        # Datos originales
        station_data = df[df['estacion'] == station].sort_values('fecha')
        imputed_data = df_imputed[df_imputed['estacion'] == station].sort_values('fecha')
        
        # Plot
        ax.plot(station_data['fecha'], station_data['nivel_msnm'], 
               'o-', color='#2E5EAA', markersize=1, linewidth=0.5, 
               label='Original', alpha=0.7)
        
        # Valores imputados
        imputed_only = imputed_data[imputed_data['imputed'] == True]
        if len(imputed_only) > 0:
            ax.scatter(imputed_only['fecha'], imputed_only['nivel_msnm'], 
                      color='red', s=10, alpha=0.7, label='Imputado', zorder=5)
        
        ax.set_title(f'{station} ← {donor}\n({len(imputed_only)} imputados)', 
                    fontsize=11, fontweight='bold')
        ax.set_xlabel('Fecha', fontsize=10)
        ax.set_ylabel('Cota (m.s.n.m.)', fontsize=10)
        ax.legend(loc='best', fontsize=8)
        ax.grid(True, alpha=0.3)
    
    plt.suptitle('Imputacion H-H Simple (Cuadratico) - Series Temporales', 
                fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    output_fig = FIGURES_PATH / "final_imputation_hh_simple.png"
    plt.savefig(output_fig, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"\nFigura guardada: {output_fig}")
    plt.close()
    
    return df_imputed, imputation_stats


if __name__ == '__main__':
    run_final_imputation()
