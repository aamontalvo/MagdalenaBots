"""
Genera figuras de Curvas H-H en formato estandar de informe técnico.
Formato: Dos paneles - superior con dispersión y modelo, inferior con residuos.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from scipy import stats
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')

plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['axes.grid'] = True
plt.rcParams['font.family'] = 'sans-serif'


def fit_quadratic_model(pair_data):
    """Ajusta modelo cuadratico H-H."""
    X = pair_data['donor'].values.reshape(-1, 1)
    y = pair_data['target'].values
    
    poly_features = PolynomialFeatures(degree=2, include_bias=False)
    X_poly = poly_features.fit_transform(X)
    
    model = LinearRegression()
    model.fit(X_poly, y)
    
    y_pred = model.predict(X_poly)
    
    r2 = r2_score(y, y_pred)
    rmse = np.sqrt(mean_squared_error(y, y_pred))
    
    n = len(y)
    k = 3
    rss = np.sum((y - y_pred) ** 2)
    aic = n * np.log(rss / n) + 2 * k
    
    a, b = model.coef_
    c = model.intercept_
    
    return {
        'model': model,
        'poly': poly_features,
        'a': a, 'b': b, 'c': c,
        'r2': r2,
        'rmse': rmse,
        'aic': aic,
        'n': n,
        'y_pred': y_pred
    }


def plot_hh_figure_standard(pair_data, metrics, target_station, donor_station, output_path):
    """
    Genera figura estandar de Curva H-H con formato de informe técnico.
    Formato similar a la imagen adjunta por el usuario.
    """
    
    # Configurar figura con dos paneles verticales
    fig, axes = plt.subplots(2, 1, figsize=(10, 12), gridspec_kw={'height_ratios': [2, 1]})
    
    # Calcular residuos
    y_pred = metrics['y_pred']
    residuals = pair_data['target'].values - y_pred
    
    # ==========================================
    # PANEL SUPERIOR: Dispersion y modelo
    # ==========================================
    ax_main = axes[0]
    
    # Scatter de datos
    ax_main.scatter(pair_data['donor'], pair_data['target'], 
                   alpha=0.3, s=8, color='steelblue', edgecolors='none',
                   label=f'Datos concurrentes (n={metrics["n"]:,})')
    
    # Curva del modelo cuadratico
    x_range = np.linspace(pair_data['donor'].min() * 0.98, pair_data['donor'].max() * 1.02, 500)
    a, b, c = metrics['a'], metrics['b'], metrics['c']
    y_model = a * x_range**2 + b * x_range + c
    
    ax_main.plot(x_range, y_model, 'r-', linewidth=2, label='Cuadratico')
    
    # Linea 1:1
    min_val = min(pair_data['donor'].min(), pair_data['target'].min())
    max_val = max(pair_data['donor'].max(), pair_data['target'].max())
    ax_main.plot([min_val, max_val], [min_val, max_val], 'k--', linewidth=1, 
                alpha=0.5, label='1:1')
    
    # Configurar ejes y titulo
    target_clean = target_station.replace('_', ' ')
    donor_clean = donor_station.replace('_', ' ')
    
    # Titulo principal con ecuacion y R2 (formato similar a imagen adjunta)
    equation_text = f"y = {a:.4f}x² + {b:.4f}x + {c:.4f}"
    title_text = f"{target_clean} vs {donor_clean}\n(Cuadratico - AIC: {metrics['aic']:.1f})"
    
    ax_main.set_title(title_text, fontsize=13, fontweight='bold', pad=10)
    ax_main.set_xlabel(f'{donor_clean} (m.s.n.m.)', fontsize=11)
    ax_main.set_ylabel(f'{target_clean} (m.s.n.m.)', fontsize=11)
    
    # Leyenda con ecuacion y R2
    legend_text = f"{equation_text}\nR² = {metrics['r2']:.4f}"
    ax_main.legend([legend_text, '1:1'], loc='upper left', fontsize=9, 
                   framealpha=0.9, edgecolor='gray')
    
    ax_main.grid(True, alpha=0.3)
    ax_main.set_xlim(min_val * 0.9, max_val * 1.02)
    ax_main.set_ylim(min_val * 0.9, max_val * 1.02)
    
    # ==========================================
    # PANEL INFERIOR: Residuos
    # ==========================================
    ax_res = axes[1]
    
    ax_res.scatter(y_pred, residuals, alpha=0.3, s=8, color='steelblue', edgecolors='none')
    ax_res.axhline(y=0, color='red', linewidth=1.5, label='Media = 0')
    
    # Lineas de referencia
    ax_res.axhline(y=0.5, color='gray', linestyle='--', alpha=0.4)
    ax_res.axhline(y=-0.5, color='gray', linestyle='--', alpha=0.4)
    
    ax_res.set_xlabel('Valores predichos (m.s.n.m.)', fontsize=11)
    ax_res.set_ylabel('Residuos (m)', fontsize=11)
    ax_res.set_title(f'Residuos - Cuadratico\nMedia residuos: {residuals.mean():.4f} m', 
                    fontsize=11)
    ax_res.legend(loc='upper right')
    ax_res.grid(True, alpha=0.3)
    
    # Ajustar layout
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"  Figura guardada: {output_path.name}")
    
    return residuals


def generate_all_figures():
    """Genera todas las figuras H-H a partir de los datos de modelos."""
    
    output_dir = Path(r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\informes\imputacion')
    data_dir = r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\backend\data\raw\RawData\SERIE NIVELES IDEAM A 2026'
    
    # Leer tabla de modelos
    models_df = pd.read_csv(output_dir / 'Tabla_I2_Modelos_HH.csv', encoding='utf-8-sig')
    
    # Cargar datos originales
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from ideam_levels_analysis import load_all_stations
    
    print("Cargando datos...")
    df = load_all_stations(data_dir)
    
    print(f"\nGenerando {len(models_df)} figuras H-H...")
    print("=" * 60)
    
    generated = []
    
    for idx, row in models_df.iterrows():
        target = row['target']
        donor = row['donor']
        iteration = row['iteration']
        
        # Para iteraciones multiples, agregar sufijo
        suffix = f"_Iter{iteration}" if iteration > 1 else ""
        
        # Preparar datos del par
        target_df = df[df['station'] == target][['date', 'level']].rename(columns={'level': 'target'})
        donor_df = df[df['station'] == donor][['date', 'level']].rename(columns={'level': 'donor'})
        
        merged = pd.merge(target_df, donor_df, on='date').dropna()
        
        if len(merged) < 100:
            print(f"  Advertencia: {target} <- {donor} tiene pocos datos ({len(merged)})")
            continue
        
        # Ajustar modelo
        metrics = fit_quadratic_model(merged)
        
        # Generar figura
        fig_name = f"Figura_HH_{target}_{donor}{suffix}.png"
        fig_path = output_dir / fig_name
        
        plot_hh_figure_standard(merged, metrics, target, donor, fig_path)
        
        generated.append({
            'target': target,
            'donor': donor,
            'iteration': iteration,
            'r2': metrics['r2'],
            'rmse': metrics['rmse'],
            'aic': metrics['aic'],
            'equation': f"H = {metrics['a']:.6f}*H² + {metrics['b']:.4f}*H + {metrics['c']:.4f}",
            'filename': fig_name
        })
    
    print("=" * 60)
    print(f"\nTotal figuras generadas: {len(generated)}")
    
    # Guardar resumen de figuras
    summary_df = pd.DataFrame(generated)
    summary_df.to_csv(output_dir / 'Tabla_Figuras_HH_Generadas.csv', index=False, encoding='utf-8-sig')
    
    return generated


if __name__ == '__main__':
    figures = generate_all_figures()
