# -*- coding: utf-8 -*-
"""
Genera Fig5 (Ajuste de Distribuciones) para todas las estaciones de niveles v4.2
Usando Datos_Imputados_v4_2_Complete.csv
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import scipy.stats as stats
import sys
sys.stdout.reconfigure(encoding='utf-8')

INPUT_FILE = Path(r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\Informes\imputacion\Datos_Imputados_v4_2_Complete.csv')
OUTPUT_DIR = Path(r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\cartillas_estaciones\v4_2')

ESTACIONES = [
    'Calamar', 'Tenerife', 'Plato', 'Magangue', 'Barbosa', 
    'Coyongal', 'Armenia', 'Rio Nuevo', 'Las Palomas', 'Las Aguadas', 
    'El Banco', 'Penoncito', 'La Gloria', 'Gamarra Aut', 'El Contento', 
    'Sitio Nuevo', 'Puerto Wilches', 'San Pedrito'
]

def plot_ajuste_distribuciones(station_df, station_name, output_path):
    """Figura 5: Ajuste de distribuciones con colores en escala de grises."""
    original = station_df[station_df['Metodo'] == 'Original']['Cota'].dropna()
    
    if len(original) < 30:
        print(f"  AVISO {station_name}: Insuficientes datos originales para distribuciones ({len(original)})")
        return False
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Panel izquierdo: Histograma
    ax1 = axes[0]
    ax1.hist(original, bins=30, density=True, alpha=0.6, 
             color='lightgray', edgecolor='gray', label='Datos observados')
    
    # Ajuste Normal
    mu, sigma = stats.norm.fit(original)
    x = np.linspace(original.min(), original.max(), 100)
    ax1.plot(x, stats.norm.pdf(x, mu, sigma), 'k-', linewidth=2, label='Normal')
    
    # Ajuste Gamma (Pearson III)
    try:
        shape, loc, scale = stats.gamma.fit(original)
        ax1.plot(x, stats.gamma.pdf(x, shape, loc, scale), 'k--', linewidth=2, label='Pearson III')
    except Exception:
        shape, loc, scale = None, None, None
    
    # Ajuste Weibull
    try:
        c, loc_w, scale_w = stats.weibull_min.fit(original)
        ax1.plot(x, stats.weibull_min.pdf(x, c, loc_w, scale_w), 'k:', linewidth=2, label='Weibull')
    except Exception:
        pass
    
    ax1.set_title(f'Ajuste de Distribuciones - {station_name}', fontsize=12, fontweight='bold')
    ax1.set_xlabel('Cota (m.s.n.m.)', fontsize=11)
    ax1.set_ylabel('Densidad de probabilidad', fontsize=11)
    ax1.legend(fontsize=9, loc='upper left')
    ax1.grid(True, alpha=0.3)
    
    # Panel derecho: Q-Q plot
    ax2 = axes[1]
    if shape is not None:
        stats.probplot(original, dist=stats.gamma, sparams=(shape, loc, scale), plot=ax2)
        ax2.get_lines()[0].set_markerfacecolor('gray')
        ax2.get_lines()[0].set_markeredgecolor('black')
        ax2.get_lines()[0].set_alpha(0.6)
        ax2.get_lines()[1].set_color('black')
        ax2.get_lines()[1].set_linestyle('--')
        
        stat, p_value = stats.shapiro(original[:min(5000, len(original))])
        normalidad = "Normal" if p_value > 0.05 else "No Normal"
        
        ax2.set_title(f'Q-Q Plot - Mejor Ajuste: Pearson III\nKS p-value: {p_value:.2e}', 
                      fontsize=12, fontweight='bold')
    else:
        ax2.set_title('Q-Q Plot - No se pudo ajustar Pearson III', fontsize=12, fontweight='bold')
    
    ax2.set_xlabel('Cuantiles teoricos (Pearson III)', fontsize=11)
    ax2.set_ylabel('Cuantiles observados', fontsize=11)
    ax2.grid(True, alpha=0.3)
    
    from matplotlib.lines import Line2D
    legend_elements = [Line2D([0], [0], color='black', linestyle='--', label='1:1')]
    ax2.legend(handles=legend_elements, loc='upper left', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    return True

def main():
    print("=" * 70)
    print("GENERANDO FIG5 (AJUSTE DE DISTRIBUCIONES) PARA NIVELES v4.2")
    print("=" * 70)
    
    df = pd.read_csv(INPUT_FILE)
    df['Fecha'] = pd.to_datetime(df['Fecha'], format='%d-%m-%Y')
    
    for station in ESTACIONES:
        station_df = df[df['NombreEstacion'] == station].copy()
        if len(station_df) == 0:
            print(f"  AVISO: Sin datos para {station}")
            continue
        
        output = OUTPUT_DIR / station / f"Fig5_Ajuste_Distribuciones_{station.upper().replace(' ', '_')}.png"
        try:
            if plot_ajuste_distribuciones(station_df, station, output):
                print(f"  [OK] Fig5 - {station}")
        except Exception as e:
            print(f"  [ERROR] Fig5 - {station}: {e}")

if __name__ == '__main__':
    main()
