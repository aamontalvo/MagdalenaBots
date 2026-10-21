"""
Generar curvas H-H para San Pedrito usando datos actualizados v3
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from scipy.stats import pearsonr
import warnings
warnings.filterwarnings('ignore')

V3_PATH = Path(r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\cartillas_estaciones\datos\processed\Datos_Imputados_v3.csv')
OUTPUT_HH = Path(r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\Informes\imputacion\Curvas_HH_v4_2')

v3 = pd.read_csv(V3_PATH, low_memory=False)
v3['date'] = pd.to_datetime(v3['date'], format='mixed', dayfirst=False)

def get_common_period(df, s1, s2):
    d1 = df[df['station'] == s1][['date', 'level']].rename(columns={'level': 'l1'})
    d2 = df[df['station'] == s2][['date', 'level']].rename(columns={'level': 'l2'})
    merged = pd.merge(d1, d2, on='date')
    merged = merged.dropna()
    return merged['l1'].values, merged['l2'].values

# Estaciones candidatas (top correlaciones)
candidates = ['CALAMAR', 'TENERIFE', 'MAGANGUE', 'BARBOSA', 'COYONGAL']

OUTPUT_HH.mkdir(parents=True, exist_ok=True)

for candidate in candidates:
    print(f"  Generando H-H: San Pedrito vs {candidate}...")
    sp_vals, cand_vals = get_common_period(v3, 'SAN_PEDRITO', candidate)
    
    if len(sp_vals) < 10:
        print(f"    Insuficientes datos comunes ({len(sp_vals)})")
        continue
    
    r, _ = pearsonr(sp_vals, cand_vals)
    
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.scatter(cand_vals, sp_vals, c='black', s=15, alpha=0.5, edgecolors='none')
    
    # Linea 1:1
    min_val = min(sp_vals.min(), cand_vals.min())
    max_val = max(sp_vals.max(), cand_vals.max())
    ax.plot([min_val, max_val], [min_val, max_val], 'k--', linewidth=1.5, alpha=0.6, label='1:1')
    
    # Regresion
    m, b = np.polyfit(cand_vals, sp_vals, 1)
    x_line = np.linspace(cand_vals.min(), cand_vals.max(), 100)
    ax.plot(x_line, m * x_line + b, 'r-', linewidth=2, label=f'y = {m:.3f}x + {b:.3f}')
    
    ax.set_xlabel(f'{candidate.replace("_", " ").title()} - Cota (m.s.n.m.)', fontsize=12)
    ax.set_ylabel('San Pedrito - Cota (m.s.n.m.)', fontsize=12)
    ax.set_title(f'Curva H-H: San Pedrito vs {candidate.replace("_", " ").title()}\n'
                 f'r = {r:.4f} | n = {len(sp_vals):,} datos concurrentes',
                 fontsize=13, fontweight='bold')
    ax.legend(loc='upper left', fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_aspect('equal', adjustable='box')
    plt.tight_layout()
    
    fname = f'HH_SanPedrito_vs_{candidate}_v4_2.png'
    plt.savefig(OUTPUT_HH / fname, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"    Guardado: {fname} | r = {r:.4f}")

print(f"\nCurvas H-H guardadas en: {OUTPUT_HH}")
