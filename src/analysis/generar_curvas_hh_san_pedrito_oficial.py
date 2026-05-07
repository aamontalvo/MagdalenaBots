"""
Generar curvas H-H oficiales para San Pedrito (formato v4.2 del sistema)
Usa la fuente de la verdad: Resumen_Crudos_IDEAM_2026.csv
Genera figuras con dos paneles: dispersion y residuos
Exporta tabla de modelos H-H para San Pedrito
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Configuracion de estilo
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['axes.grid'] = True
plt.rcParams['grid.alpha'] = 0.3

# Rutas
SOURCE_PATH = Path(r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\backend\data\processed\Resumen_Crudos_IDEAM_2026.csv')
OUTPUT_DIR = Path(r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\Informes\imputacion\Curvas_HH_v4_2')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Cargar fuente de la verdad
df = pd.read_csv(SOURCE_PATH)
df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y')

# Donantes candidatos para San Pedrito (ordenados por correlacion)
DONORS = [
    ('CALAMAR', 'Magangue'),  # Nota: Calamar tambien puede ser donante de San Pedrito
]

# San Pedrito es el OBJETIVO, buscamos donantes para ella
# Segun matriz de correlacion: Calamar(r=0.996), Magangue(r=0.985), Tenerife(r=0.983), Barbosa(r=0.964), Coyongal(r=0.945)
TARGET = 'SAN_PEDRITO'
DONOR_CANDIDATES = ['CALAMAR', 'MAGANGUE', 'TENERIFE', 'BARBOSA', 'COYONGAL']


def get_concurrent_data(target, donor):
    """Obtiene datos concurrentes entre objetivo y donante."""
    t = df[df['station'] == target][['date', 'level']].copy()
    t = t[t['level'].notna()].rename(columns={'level': 'target'})
    
    d = df[df['station'] == donor][['date', 'level']].copy()
    d = d[d['level'].notna()].rename(columns={'level': 'donor'})
    
    merged = pd.merge(t, d, on='date', how='inner')
    return merged


def fit_models(X, y):
    """Ajusta modelos lineal y cuadratico. Retorna dict con resultados."""
    n = len(X)
    
    # Lineal
    slope, intercept, r_value, _, std_err = stats.linregress(X, y)
    y_pred_lin = slope * X + intercept
    ss_res_lin = np.sum((y - y_pred_lin) ** 2)
    ss_tot_lin = np.sum((y - np.mean(y)) ** 2)
    r2_lin = 1 - ss_res_lin / ss_tot_lin if ss_tot_lin > 0 else 0
    rmse_lin = np.sqrt(ss_res_lin / n)
    
    # Cuadratico
    coeffs_quad = np.polyfit(X, y, 2)
    y_pred_quad = np.polyval(coeffs_quad, X)
    ss_res_quad = np.sum((y - y_pred_quad) ** 2)
    ss_tot_quad = np.sum((y - np.mean(y)) ** 2)
    r2_quad = 1 - ss_res_quad / ss_tot_quad if ss_tot_quad > 0 else 0
    rmse_quad = np.sqrt(ss_res_quad / n)
    
    return {
        'linear': {
            'r2': r2_lin,
            'rmse': rmse_lin,
            'coeffs': (slope, intercept),
            'equation': f'H_target = {slope:.4f}*H + {intercept:.4f}'
        },
        'quadratic': {
            'r2': r2_quad,
            'rmse': rmse_quad,
            'coeffs': coeffs_quad,
            'equation': f'H_target = {coeffs_quad[0]:.6f}*H^2 + {coeffs_quad[1]:.4f}*H + {coeffs_quad[2]:.4f}'
        }
    }


# =============================================================================
# PROCESAMIENTO
# =============================================================================
print("=" * 80)
print("GENERANDO CURVAS H-H OFICIALES - SAN PEDRITO")
print("Fuente: Resumen_Crudos_IDEAM_2026.csv")
print("=" * 80)

results = []

for donor in DONOR_CANDIDATES:
    print(f"\n[San Pedrito vs {donor}]")
    
    pair = get_concurrent_data(TARGET, donor)
    if len(pair) < 30:
        print(f"  Insuficientes datos concurrentes ({len(pair)})")
        continue
    
    X = pair['donor'].values
    y = pair['target'].values
    
    # Ajustar modelos
    models = fit_models(X, y)
    
    # Seleccionar mejor modelo
    best_type = 'quadratic' if models['quadratic']['r2'] > models['linear']['r2'] else 'linear'
    best = models[best_type]
    alt = models['linear'] if best_type == 'quadratic' else models['quadratic']
    
    print(f"  Datos concurrentes: {len(pair):,}")
    print(f"  Lineal:    R2 = {models['linear']['r2']:.4f}, RMSE = {models['linear']['rmse']:.4f}")
    print(f"  Cuadratico: R2 = {models['quadratic']['r2']:.4f}, RMSE = {models['quadratic']['rmse']:.4f}")
    print(f"  Mejor: {best_type.upper()} (R2 = {best['r2']:.4f})")
    print(f"  Ecuacion: {best['equation']}")
    
    # Calcular predicciones y residuos del mejor modelo
    if best_type == 'quadratic':
        y_pred = np.polyval(best['coeffs'], X)
    else:
        y_pred = best['coeffs'][0] * X + best['coeffs'][1]
    
    residuals = y - y_pred
    
    # Guardar resultado
    results.append({
        'target': TARGET,
        'donor': donor,
        'model_type': best_type,
        'r2': best['r2'],
        'r2_alternative': alt['r2'],
        'rmse': best['rmse'],
        'equation': best['equation'],
        'acceptable': best['r2'] >= 0.75,
        'n_training': len(pair),
        'n_imputed': 0  # Se calculara despues
    })
    
    # =============================================================================
    # GENERAR FIGURA OFICIAL (2 paneles)
    # =============================================================================
    fig, axes = plt.subplots(2, 1, figsize=(10, 12), gridspec_kw={'height_ratios': [2, 1]})
    
    # Panel superior: Dispersion y modelo
    ax_main = axes[0]
    ax_main.scatter(X, y, alpha=0.3, s=8, color='steelblue', edgecolors='none', label='Datos concurrentes')
    
    # Linea 1:1
    min_val = min(X.min(), y.min())
    max_val = max(X.max(), y.max())
    ax_main.plot([min_val, max_val], [min_val, max_val], 'k--', linewidth=1.5, alpha=0.5, label='1:1')
    
    # Curva del modelo
    x_line = np.linspace(X.min(), X.max(), 200)
    if best_type == 'quadratic':
        y_line = np.polyval(best['coeffs'], x_line)
    else:
        y_line = best['coeffs'][0] * x_line + best['coeffs'][1]
    
    ax_main.plot(x_line, y_line, 'r-', linewidth=2, label=f'Modelo {best_type} (R2 = {best["r2"]:.4f})')
    
    ax_main.set_xlabel(f'{donor.replace("_", " ").title()} - Cota (m.s.n.m.)')
    ax_main.set_ylabel('San Pedrito - Cota (m.s.n.m.)')
    ax_main.set_title(f'Curva H-H: San Pedrito vs {donor.replace("_", " ").title()}\n'
                      f'Modelo: {best_type.upper()} | R2 = {best["r2"]:.4f} | RMSE = {best["rmse"]:.4f} | n = {len(pair):,}',
                      fontweight='bold')
    ax_main.legend(loc='upper left')
    ax_main.set_aspect('equal', adjustable='box')
    
    # Panel inferior: Residuos
    ax_res = axes[1]
    ax_res.scatter(X, residuals, alpha=0.3, s=8, color='steelblue', edgecolors='none')
    ax_res.axhline(y=0, color='red', linestyle='-', linewidth=1)
    ax_res.axhline(y=2*best['rmse'], color='orange', linestyle='--', linewidth=1, alpha=0.7, label=f'+/- 2*RMSE ({2*best["rmse"]:.3f})')
    ax_res.axhline(y=-2*best['rmse'], color='orange', linestyle='--', linewidth=1, alpha=0.7)
    ax_res.set_xlabel(f'{donor.replace("_", " ").title()} - Cota (m.s.n.m.)')
    ax_res.set_ylabel('Residuos (m)')
    ax_res.set_title('Analisis de Residuos', fontweight='bold')
    ax_res.legend()
    
    # Anotacion con ecuacion
    eq_text = best['equation'].replace('*H^2', 'H\u00b2').replace('*H', 'H').replace('_target', '')
    fig.text(0.5, 0.02, f'Ecuacion: {eq_text}', ha='center', fontsize=10, 
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout(rect=[0, 0.04, 1, 1])
    
    fname = f'Figura_HH_SAN_PEDRITO_{donor}_{best_type}.png'
    plt.savefig(OUTPUT_DIR / fname, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  Guardado: {fname}")

# Guardar tabla de modelos
print("\n" + "=" * 80)
print("TABLA DE MODELOS H-H - SAN PEDRITO")
print("=" * 80)

df_models = pd.DataFrame(results)
print(df_models.to_string(index=False))

df_models.to_csv(OUTPUT_DIR / 'Tabla_Modelos_HH_SanPedrito.csv', index=False, encoding='utf-8-sig')
print(f"\nGuardado: {OUTPUT_DIR / 'Tabla_Modelos_HH_SanPedrito.csv'}")

print("\n" + "=" * 80)
print("PROCESO COMPLETADO")
print("=" * 80)
