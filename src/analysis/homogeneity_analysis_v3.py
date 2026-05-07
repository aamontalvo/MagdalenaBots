"""
Analisis de Homogeneidad v3 - Datos corregidos (Fuente de Verdad)
=================================================================

Actualizado 2026-05-06. Lee directamente de Resumen_Crudos_IDEAM_2026.csv
para garantizar que San Pedrito y todas las estaciones usen datos corregidos.

Pruebas: Pettitt, SNHT, Mann-Kendall
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Rutas
PROJECT_ROOT = Path(r"C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot")
DATA_PATH = PROJECT_ROOT / "backend" / "data" / "processed"
OUTPUT_PATH = PROJECT_ROOT / "Imagenes" / "Niveles"

# Orden de estaciones (aguas abajo -> aguas arriba)
GEOGRAPHIC_ORDER = [
    'SAN_PEDRITO', 'CALAMAR', 'TENERIFE', 'PLATO', 'MAGANGUE', 'BARBOSA', 'COYONGAL',
    'ARMENIA', 'RIO_NUEVO', 'LAS_PALOMAS', 'LAS_AGUADAS', 'EL_BANCO', 'PENONCITO',
    'LA_GLORIA', 'GAMARRA_AUT', 'EL_CONTENTO', 'SITIO_NUEVO', 'PUERTO_WILCHES',
]


# =============================================================================
# PRUEBAS ESTADISTICAS
# =============================================================================

def pettitt_test(data):
    """Prueba de Pettitt para detectar un punto de quiebre."""
    n = len(data)
    if n < 10:
        return None, None, None
    u = np.zeros(n)
    for t in range(1, n):
        s = 0
        for i in range(t):
            for j in range(t, n):
                s += np.sign(data[i] - data[j])
        u[t] = s
    k_opt = np.argmax(np.abs(u[1:])) + 1
    u_max = u[k_opt]
    p_value = 2 * np.exp(-6 * u_max**2 / (n**3 + n**2))
    return u_max, p_value, k_opt


def snht_test(data):
    """Standard Normal Homogeneity Test (SNHT)."""
    n = len(data)
    if n < 10:
        return None, None, None
    t_stats = []
    for k in range(1, n-1):
        x1 = data[:k]
        x2 = data[k:]
        if len(x1) < 2 or len(x2) < 2:
            t_stats.append(0)
            continue
        mean1, mean2 = np.mean(x1), np.mean(x2)
        var = np.var(data, ddof=1)
        if var == 0:
            t_stats.append(0)
            continue
        t_k = k * (mean1 - np.mean(data))**2 / var + (n-k) * (mean2 - np.mean(data))**2 / var
        t_stats.append(t_k)
    if len(t_stats) == 0:
        return None, None, None
    t_max = np.max(t_stats)
    k_opt = np.argmax(t_stats) + 1
    return t_max, None, k_opt


def mann_kendall_test(data):
    """Prueba de Mann-Kendall para tendencias monotonicas."""
    n = len(data)
    if n < 10:
        return None, None, None
    clean_data = data[~np.isnan(data)]
    if len(clean_data) < 10:
        return None, None, None
    s = 0
    for i in range(len(clean_data)-1):
        for j in range(i+1, len(clean_data)):
            s += np.sign(clean_data[j] - clean_data[i])
    var_s = len(clean_data) * (len(clean_data) - 1) * (2*len(clean_data) + 5) / 18
    if var_s == 0:
        return None, None, None
    if s > 0:
        z = (s - 1) / np.sqrt(var_s)
    elif s < 0:
        z = (s + 1) / np.sqrt(var_s)
    else:
        z = 0
    p_value = 2 * (1 - stats.norm.cdf(abs(z)))
    tau = s / (len(clean_data) * (len(clean_data) - 1) / 2)
    return tau, p_value, s


# =============================================================================
# FUNCIONES DE PREPARACION
# =============================================================================

def get_station_annual_stats(df, station):
    """Obtiene estadisticas anuales de una estacion."""
    station_data = df[df['station'] == station].copy()
    annual = station_data.groupby('year').agg({
        'level': ['mean', 'median', 'std', 'count']
    }).reset_index()
    annual.columns = ['year', 'mean_level', 'median_level', 'std_level', 'count']
    annual = annual[annual['count'] >= 300]  # Al menos 300 dias
    return annual


def homogeneity_tests_by_station(df):
    """Aplica pruebas de homogeneidad a cada estacion."""
    results = []
    for station in GEOGRAPHIC_ORDER:
        if station not in df['station'].values:
            continue
        annual = get_station_annual_stats(df, station)
        if len(annual) < 10:
            continue
        levels = annual['mean_level'].values
        years = annual['year'].values

        # Pettitt
        pettitt_stat, pettitt_p, pettitt_year_idx = pettitt_test(levels)
        pettitt_year = years[pettitt_year_idx] if pettitt_year_idx else None

        # SNHT
        snht_stat, _, snht_year_idx = snht_test(levels)
        snht_year = years[snht_year_idx] if snht_year_idx else None

        # Mann-Kendall
        mk_tau, mk_p, mk_s = mann_kendall_test(levels)

        results.append({
            'station': station,
            'n_years': len(annual),
            'period_start': int(years.min()),
            'period_end': int(years.max()),
            'pettitt_stat': round(pettitt_stat, 2) if pettitt_stat else None,
            'pettitt_p': round(pettitt_p, 4) if pettitt_p else None,
            'pettitt_year': int(pettitt_year) if pettitt_year else None,
            'pettitt_significant': pettitt_p < 0.05 if pettitt_p else False,
            'snht_stat': round(snht_stat, 2) if snht_stat else None,
            'snht_year': int(snht_year) if snht_year else None,
            'mk_tau': round(mk_tau, 3) if mk_tau else None,
            'mk_p': round(mk_p, 4) if mk_p else None,
            'mk_significant': mk_p < 0.05 if mk_p else False,
            'trend': 'Increasing' if mk_tau and mk_tau > 0 and mk_p < 0.05
                     else 'Decreasing' if mk_tau and mk_tau < 0 and mk_p < 0.05
                     else 'No trend'
        })
    return pd.DataFrame(results)


# =============================================================================
# VISUALIZACION
# =============================================================================

def plot_homogeneity_tests_summary(homog_results, output_path):
    """Genera grafico resumen de pruebas de homogeneidad (4 paneles)."""
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))

    stations = homog_results['station'].values
    x_pos = np.arange(len(stations))

    # 1. Pettitt
    ax = axes[0, 0]
    colors = ['red' if sig else 'gray' for sig in homog_results['pettitt_significant']]
    bars = ax.bar(x_pos, homog_results['pettitt_stat'].fillna(0), color=colors, alpha=0.7)
    ax.set_xticks(x_pos)
    ax.set_xticklabels([s.replace('_', '\n') for s in stations], rotation=45, ha='right', fontsize=8)
    ax.set_ylabel('Estadistico de Pettitt', fontsize=10)
    ax.set_title('Prueba de Pettitt (Cambio de Regimen)\nRojo = Significativo (p<0.05)', fontsize=11, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')

    # 2. SNHT
    ax = axes[0, 1]
    snht_vals = homog_results['snht_stat'].fillna(0)
    colors = ['red' if v > 9.5 else 'gray' for v in snht_vals]
    bars = ax.bar(x_pos, snht_vals, color=colors, alpha=0.7)
    ax.axhline(y=9.5, color='red', linestyle='--', linewidth=1.5, label='Umbral significativo')
    ax.set_xticks(x_pos)
    ax.set_xticklabels([s.replace('_', '\n') for s in stations], rotation=45, ha='right', fontsize=8)
    ax.set_ylabel('Estadistico SNHT', fontsize=10)
    ax.set_title('Prueba SNHT (Salto en la Media)\nRojo = Significativo', fontsize=11, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')

    # 3. Mann-Kendall Tau
    ax = axes[1, 0]
    tau_vals = homog_results['mk_tau'].fillna(0)
    colors = ['blue' if t > 0 and p else 'red' if t < 0 and p else 'gray'
              for t, p in zip(tau_vals, homog_results['mk_significant'])]
    bars = ax.bar(x_pos, tau_vals, color=colors, alpha=0.7)
    ax.axhline(y=0, color='black', linestyle='-', linewidth=1)
    ax.set_xticks(x_pos)
    ax.set_xticklabels([s.replace('_', '\n') for s in stations], rotation=45, ha='right', fontsize=8)
    ax.set_ylabel('Tau de Kendall', fontsize=10)
    ax.set_title('Prueba Mann-Kendall (Tendencia)\nAzul = Creciente, Rojo = Decreciente, Gris = No significativo',
                 fontsize=11, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')

    # 4. Anos de datos
    ax = axes[1, 1]
    bars = ax.bar(x_pos, homog_results['n_years'], color='steelblue', alpha=0.7)
    ax.set_xticks(x_pos)
    ax.set_xticklabels([s.replace('_', '\n') for s in stations], rotation=45, ha='right', fontsize=8)
    ax.set_ylabel('Numero de anos con datos', fontsize=10)
    ax.set_title('Longitud de Registros por Estacion', fontsize=11, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')

    plt.suptitle('Resumen de Pruebas de Homogeneidad (v3 - Datos Corregidos)', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figura guardada: {output_path}")


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 70)
    print("ANALISIS DE HOMOGENEIDAD v3 - DATOS CORREGIDOS")
    print("=" * 70)

    # Cargar fuente de verdad corregida
    print(f"\nCargando: {DATA_PATH / 'Resumen_Crudos_IDEAM_2026.csv'}")
    df = pd.read_csv(DATA_PATH / "Resumen_Crudos_IDEAM_2026.csv")
    df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y')
    print(f"  Registros: {len(df):,} | Estaciones: {df['station'].nunique()}")

    # Pruebas de homogeneidad
    print("\nAplicando pruebas de homogeneidad...")
    homog_results = homogeneity_tests_by_station(df)
    print(f"  Estaciones analizadas: {len(homog_results)}")

    problematicas = homog_results[homog_results['pettitt_significant'] == True]
    print(f"  Cambios significativos (Pettitt): {len(problematicas)}")
    for _, row in problematicas.iterrows():
        print(f"    - {row['station']}: cambio en {int(row['pettitt_year'])} (p={row['pettitt_p']:.4f})")

    tendencias = homog_results[homog_results['mk_significant'] == True]
    print(f"  Tendencias significativas (MK): {len(tendencias)}")
    for _, row in tendencias.iterrows():
        print(f"    - {row['station']}: {row['trend']} (tau={row['mk_tau']:.3f}, p={row['mk_p']:.4f})")

    # Generar figura
    print("\nGenerando figura...")
    plot_homogeneity_tests_summary(homog_results, OUTPUT_PATH / "Resumenpruebashomegeniedad_v3.png")

    # Guardar resultados
    homog_results.to_csv(OUTPUT_PATH / "Tabla_Homogeneidad_v3.csv", index=False)
    print(f"Tabla guardada: {OUTPUT_PATH / 'Tabla_Homogeneidad_v3.csv'}")

    # Comparacion con figura original (imprimir resumen)
    print("\n" + "=" * 70)
    print("COMPARACION CLAVE CON VERSION ANTERIOR")
    print("=" * 70)
    sp = homog_results[homog_results['station'] == 'SAN_PEDRITO']
    if not sp.empty:
        row = sp.iloc[0]
        print(f"\nSAN_PEDRITO:")
        print(f"  Anos analizados: {row['n_years']} ({row['period_start']}-{row['period_end']})")
        print(f"  Pettitt: stat={row['pettitt_stat']}, p={row['pettitt_p']}, significativo={row['pettitt_significant']}")
        print(f"  SNHT: stat={row['snht_stat']}")
        print(f"  MK: tau={row['mk_tau']}, p={row['mk_p']}, tendencia={row['trend']}")

    return homog_results


if __name__ == '__main__':
    homog_results = main()
