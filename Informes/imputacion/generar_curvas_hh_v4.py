"""
Generador de Curvas H-H (Altura-Altura) para Sistema de Imputación v4.2
Genera figuras con dos paneles: dispersión y residuos
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import re
import warnings
warnings.filterwarnings('ignore')

# Configuración de estilo
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['axes.grid'] = True
plt.rcParams['grid.alpha'] = 0.3

# Directorios
INPUT_DIR = Path(r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\Informes\imputacion')
OUTPUT_DIR = INPUT_DIR / 'Curvas_HH_v4_2'
OUTPUT_DIR.mkdir(exist_ok=True)

# Cargar datos imputados para obtener los valores originales
def load_data():
    """Carga los datos imputados v3."""
    data_file = INPUT_DIR / 'Datos_Imputados_v3.csv'
    if data_file.exists():
        df = pd.read_csv(data_file)
        df['date'] = pd.to_datetime(df['date'])
        return df
    return None

# Cargar información de modelos
def load_models():
    """Carga la tabla de modelos H-H."""
    models_file = INPUT_DIR / 'Tabla_I2_Modelos_HH_v3.csv'
    if models_file.exists():
        df = pd.read_csv(models_file)
        return df
    return None

def parse_equation(equation_str):
    """Parsea la ecuación del modelo para extraer coeficientes."""
    # Formato: "H_target = 0.012947*H^2 + 0.5795*H + -6.5749"
    pattern = r'([\-\.\d]+)\*H\^2\s*\+\s*([\-\.\d]+)\*H\s*\+\s*([\-\.\d]+)'
    match = re.search(pattern, equation_str)
    if match:
        a = float(match.group(1))
        b = float(match.group(2))
        c = float(match.group(3))
        return a, b, c
    return None, None, None

def prepare_pair_data(df_all, target_station, donor_station):
    """Prepara datos concurrentes para el par objetivo-donante."""
    target_data = df_all[df_all['station'] == target_station][['date', 'level']].copy()
    target_data = target_data[target_data['level'].notna()]
    target_data = target_data.rename(columns={'level': 'target'})
    
    donor_data = df_all[df_all['station'] == donor_station][['date', 'level']].copy()
    donor_data = donor_data[donor_data['level'].notna()]
    donor_data = donor_data.rename(columns={'level': 'donor'})
    
    merged = pd.merge(target_data, donor_data, on='date', how='inner')
    return merged

def plot_hh_curve(model_info, pair_data, output_path):
    """Genera la figura H-H con dos paneles."""
    
    target = model_info['target']
    donor = model_info['donor']
    model_type = model_info['model_type']
    r2 = model_info['r2']
    r2_alt = model_info['r2_alternative']
    rmse = model_info['rmse']
    equation = model_info['equation']
    acceptable = model_info['acceptable']
    
    # Extraer coeficientes
    a, b, c = parse_equation(equation)
    
    X = pair_data['donor'].values
    y = pair_data['target'].values
    
    # Calcular predicciones
    y_pred = a * X**2 + b * X + c
    residuals = y - y_pred
    
    # Crear figura con dos paneles
    fig, axes = plt.subplots(2, 1, figsize=(10, 12), 
                             gridspec_kw={'height_ratios': [2, 1]})
    
    # Panel superior: Dispersión y modelo
    ax_main = axes[0]
    
    # Puntos de datos concurrentes
    ax_main.scatter(X, y, alpha=0.3, s=8, color='steelblue', 
                   edgecolors='none', label=f'Datos concurrentes (n={len(y):,})')
    
    # Línea del modelo
    x_range = np.linspace(X.min() * 0.98, X.max() * 1.02, 500)
    y_range = a * x_range**2 + b * x_range + c
    model_label = f"Cuadratico: y = {a:.4f}x^2 + {b:.4f}x + {c:.4f}"
    ax_main.plot(x_range, y_range, 'r-', linewidth=2, label=model_label)
    
    # Línea 1:1
    min_val = min(X.min(), y.min())
    max_val = max(X.max(), y.max())
    ax_main.plot([min_val, max_val], [min_val, max_val], 'k--', 
                linewidth=1, alpha=0.5, label='1:1')
    
    # Caja de métricas
    status = "ACEPTADO" if acceptable else "RECHAZADO (R² < 0.75)"
    alt_type = "linear" if model_type == "quadratic" else "quadratic"
    metrics_text = (f"R² = {r2:.4f}\n"
                   f"RMSE = {rmse:.3f} m\n"
                   f"Modelo alternativo ({alt_type}): R² = {r2_alt:.4f}\n"
                   f"Estado: {status}")
    
    ax_main.text(0.05, 0.95, metrics_text,
                transform=ax_main.transAxes, fontsize=10,
                verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.9))
    
    # Título y etiquetas
    target_clean = target.replace('_', ' ')
    donor_clean = donor.replace('_', ' ')
    title_suffix = f" ({model_type.title()})"
    ax_main.set_title(f"{target_clean} vs {donor_clean}{title_suffix}",
                     fontsize=13, fontweight='bold', pad=10)
    ax_main.set_xlabel(f'{donor_clean} (m.s.n.m.)', fontsize=11)
    ax_main.set_ylabel(f'{target_clean} (m.s.n.m.)', fontsize=11)
    ax_main.legend(loc='lower right', fontsize=9)
    ax_main.grid(True, alpha=0.3)
    
    # Panel inferior: Residuos
    ax_res = axes[1]
    ax_res.scatter(y_pred, residuals, alpha=0.3, s=8, color='steelblue', 
                  edgecolors='none')
    ax_res.axhline(y=0, color='red', linewidth=1.5, label='Media = 0')
    ax_res.axhline(y=0.5, color='gray', linestyle='--', alpha=0.4)
    ax_res.axhline(y=-0.5, color='gray', linestyle='--', alpha=0.4)
    
    ax_res.set_xlabel('Valores predichos (m.s.n.m.)', fontsize=11)
    ax_res.set_ylabel('Residuos (m)', fontsize=11)
    ax_res.set_title(f'Residuos - {model_type.title()}\n'
                    f'Media residuos: {residuals.mean():.4f} m',
                    fontsize=11)
    ax_res.legend(loc='upper right')
    ax_res.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    return True

def main():
    """Genera todas las curvas H-H."""
    
    print("=" * 70)
    print("GENERADOR DE CURVAS H-H v4.2")
    print("=" * 70)
    
    # Cargar datos
    df = load_data()
    if df is None:
        print("ERROR: No se encontraron datos imputados")
        return
    
    models_df = load_models()
    if models_df is None:
        print("ERROR: No se encontró la tabla de modelos")
        return
    
    print(f"\nDatos cargados: {len(df):,} registros")
    print(f"Modelos encontrados: {len(models_df)}")
    print(f"Directorio de salida: {OUTPUT_DIR}\n")
    
    # Generar figuras para cada modelo
    generated = 0
    errors = []
    
    for idx, model in models_df.iterrows():
        target = model['target']
        donor = model['donor']
        
        print(f"Generando: {target} <- {donor}...", end=' ')
        
        try:
            # Preparar datos del par
            pair_data = prepare_pair_data(df, target, donor)
            
            if len(pair_data) < 100:
                print(f"INSUFICIENTE ({len(pair_data)} puntos)")
                errors.append(f"{target} <- {donor}: datos insuficientes")
                continue
            
            # Generar figura
            output_path = OUTPUT_DIR / f"Figura_HH_{target}_{donor}_{model['model_type']}.png"
            plot_hh_curve(model, pair_data, output_path)
            
            print(f"OK (R²={model['r2']:.3f})")
            generated += 1
            
        except Exception as e:
            print(f"ERROR: {e}")
            errors.append(f"{target} <- {donor}: {str(e)}")
    
    # Reporte final
    print("\n" + "=" * 70)
    print("RESUMEN")
    print("=" * 70)
    print(f"Figuras generadas: {generated}/{len(models_df)}")
    
    if errors:
        print(f"\nErrores ({len(errors)}):")
        for err in errors:
            print(f"  - {err}")
    
    print(f"\nArchivos guardados en: {OUTPUT_DIR}")

if __name__ == '__main__':
    main()
