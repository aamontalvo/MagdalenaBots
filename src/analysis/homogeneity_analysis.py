"""
Analisis de Homogeneidad de Estaciones - Rio Magdalena
Pruebas: Pettitt, SNHT, Mann-Kendall, Correlacion, Doble Masa
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from scipy import stats
from scipy.stats import pearsonr, spearmanr, kendalltau
import warnings
warnings.filterwarnings('ignore')

# Estilo
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

# Orden de estaciones
GEOGRAPHIC_ORDER = [
    'SAN_PEDRITO', 'CALAMAR', 'TENERIFE', 'PLATO', 'MAGANGUE', 'BARBOSA', 'COYONGAL',
    'ARMENIA', 'RIO_NUEVO', 'LAS_PALOMAS', 'LAS_AGUADAS', 'EL_BANCO', 'PENONCITO',
    'LA_GLORIA', 'GAMARRA_AUT', 'EL_CONTENTO', 'SITIO_NUEVO', 'PUERTO_WILCHES',
]


# =============================================================================
# FUNCIONES DE PRUEBAS DE HOMOGENEIDAD
# =============================================================================

def pettitt_test(data):
    """
    Prueba de Pettitt para detectar un punto de quiebre.
    Retorna: estadistico, p_value, punto_cambio (indice)
    """
    n = len(data)
    if n < 10:
        return None, None, None
    
    # Calcular estadístico de Pettitt
    u = np.zeros(n)
    
    for t in range(1, n):
        # Sumar signos de diferencias entre todos los pares (i <= t < j)
        s = 0
        for i in range(t):
            for j in range(t, n):
                s += np.sign(data[i] - data[j])
        u[t] = s
    
    # Encontrar máximo absoluto
    k_opt = np.argmax(np.abs(u[1:])) + 1
    u_max = u[k_opt]
    
    # Calcular p-value aproximado
    p_value = 2 * np.exp(-6 * u_max**2 / (n**3 + n**2))
    
    return u_max, p_value, k_opt


def snht_test(data):
    """
    Standard Normal Homogeneity Test (SNHT).
    Detecta saltos en la media.
    Retorna: estadistico, p_value, punto_cambio
    """
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
    
    # Valor crítico aproximado para p=0.05 (n>100)
    critical_value = 9.5  # Aproximado para n grande
    p_value = 0.05 if t_max > critical_value else 0.5
    
    return t_max, p_value, k_opt


def mann_kendall_test(data):
    """
    Prueba de Mann-Kendall para detectar tendencias monotonicas.
    Retorna: tau, p_value, tendencia
    """
    n = len(data)
    if n < 10:
        return None, None, None
    
    # Eliminar NaN
    clean_data = data[~np.isnan(data)]
    if len(clean_data) < 10:
        return None, None, None
    
    # Calcular S
    s = 0
    for i in range(len(clean_data)-1):
        for j in range(i+1, len(clean_data)):
            s += np.sign(clean_data[j] - clean_data[i])
    
    # Varianza
    var_s = len(clean_data) * (len(clean_data) - 1) * (2*len(clean_data) + 5) / 18
    
    if var_s == 0:
        return None, None, None
    
    # Estadístico Z
    if s > 0:
        z = (s - 1) / np.sqrt(var_s)
    elif s < 0:
        z = (s + 1) / np.sqrt(var_s)
    else:
        z = 0
    
    # p-value
    p_value = 2 * (1 - stats.norm.cdf(abs(z)))
    
    # Tau de Kendall
    tau = s / (len(clean_data) * (len(clean_data) - 1) / 2)
    
    return tau, p_value, s


# =============================================================================
# FUNCIONES DE PREPARACION DE DATOS
# =============================================================================

def load_data_long(data_dir):
    """Carga datos y los transforma a formato long."""
    from ideam_levels_analysis import load_all_stations
    return load_all_stations(data_dir)


def get_common_period(df, station1, station2):
    """Obtiene periodo con datos concurrentes entre dos estaciones."""
    df1 = df[df['station'] == station1][['date', 'level', 'year']].copy()
    df2 = df[df['station'] == station2][['date', 'level', 'year']].copy()
    
    merged = pd.merge(df1, df2, on='date', suffixes=('_1', '_2'))
    merged = merged.dropna(subset=['level_1', 'level_2'])
    
    return merged


def get_station_annual_stats(df, station):
    """Obtiene estadísticas anuales de una estación."""
    station_data = df[df['station'] == station].copy()
    
    # Calcular medias anuales
    annual = station_data.groupby('year').agg({
        'level': ['mean', 'median', 'std', 'count']
    }).reset_index()
    
    annual.columns = ['year', 'mean_level', 'median_level', 'std_level', 'count']
    annual = annual[annual['count'] >= 300]  # Al menos 300 días
    
    return annual


# =============================================================================
# ANALISIS DE CORRELACION ENTRE PARES
# =============================================================================

def analyze_all_pairs(df):
    """Analiza correlaciones entre todos los pares posibles."""
    results = []
    
    stations = [s for s in GEOGRAPHIC_ORDER if s in df['station'].values]
    
    for i, s1 in enumerate(stations):
        for s2 in stations[i+1:]:
            common = get_common_period(df, s1, s2)
            
            if len(common) < 365:  # Al menos 1 año de datos concurrentes
                continue
            
            # Correlacion
            corr, p_value = pearsonr(common['level_1'], common['level_2'])
            
            results.append({
                'station_1': s1,
                'station_2': s2,
                'n_concurrent': len(common),
                'years_concurrent': len(common) / 365.25,
                'pearson_r': round(corr, 3),
                'pearson_p': round(p_value, 4),
                'period_start': int(common['year_1'].min()),
                'period_end': int(common['year_1'].max())
            })
    
    return pd.DataFrame(results)


def find_best_pairs(corr_results, min_correlation=0.7, top_n=10):
    """Encuentra los mejores pares basados en correlacion y cobertura."""
    
    # Filtrar por correlacion minima
    good_pairs = corr_results[corr_results['pearson_r'] >= min_correlation].copy()
    
    # Ordenar por correlacion y años concurrentes
    good_pairs['score'] = good_pairs['pearson_r'] * np.log(good_pairs['years_concurrent'] + 1)
    good_pairs = good_pairs.sort_values('score', ascending=False)
    
    return good_pairs.head(top_n)


# =============================================================================
# PRUEBAS DE HOMOGENEIDAD POR ESTACION
# =============================================================================

def homogeneity_tests_by_station(df):
    """Aplica pruebas de homogeneidad a cada estación."""
    results = []
    
    for station in GEOGRAPHIC_ORDER:
        if station not in df['station'].values:
            continue
        
        annual = get_station_annual_stats(df, station)
        
        if len(annual) < 10:
            continue
        
        # Datos de nivel medio anual
        levels = annual['mean_level'].values
        years = annual['year'].values
        
        # Prueba Pettitt
        pettitt_stat, pettitt_p, pettitt_year_idx = pettitt_test(levels)
        pettitt_year = years[pettitt_year_idx] if pettitt_year_idx else None
        
        # Prueba SNHT
        snht_stat, snht_p, snht_year_idx = snht_test(levels)
        snht_year = years[snht_year_idx] if snht_year_idx else None
        
        # Prueba Mann-Kendall
        mk_tau, mk_p, mk_s = mann_kendall_test(levels)
        
        results.append({
            'station': station,
            'n_years': len(annual),
            'period_start': int(years.min()),
            'period_end': int(years.max()),
            
            # Pettitt
            'pettitt_stat': round(pettitt_stat, 2) if pettitt_stat else None,
            'pettitt_p': round(pettitt_p, 4) if pettitt_p else None,
            'pettitt_year': int(pettitt_year) if pettitt_year else None,
            'pettitt_significant': pettitt_p < 0.05 if pettitt_p else False,
            
            # SNHT
            'snht_stat': round(snht_stat, 2) if snht_stat else None,
            'snht_p': 'p<0.05' if snht_stat and snht_stat > 9.5 else 'ns',
            'snht_year': int(snht_year) if snht_year else None,
            
            # Mann-Kendall
            'mk_tau': round(mk_tau, 3) if mk_tau else None,
            'mk_p': round(mk_p, 4) if mk_p else None,
            'mk_significant': mk_p < 0.05 if mk_p else False,
            'trend': 'Increasing' if mk_tau and mk_tau > 0 and mk_p < 0.05 
                     else 'Decreasing' if mk_tau and mk_tau < 0 and mk_p < 0.05 
                     else 'No trend'
        })
    
    return pd.DataFrame(results)


# =============================================================================
# VISUALIZACIONES
# =============================================================================

def plot_correlation_matrix(df, output_path):
    """Genera heatmap de matriz de correlación entre estaciones."""
    
    # Calcular correlaciones
    stations = [s for s in GEOGRAPHIC_ORDER if s in df['station'].values]
    corr_matrix = pd.DataFrame(index=stations, columns=stations)
    
    for s1 in stations:
        for s2 in stations:
            if s1 == s2:
                corr_matrix.loc[s1, s2] = 1.0
            else:
                common = get_common_period(df, s1, s2)
                if len(common) > 30:
                    corr, _ = pearsonr(common['level_1'], common['level_2'])
                    corr_matrix.loc[s1, s2] = corr
                else:
                    corr_matrix.loc[s1, s2] = np.nan
    
    corr_matrix = corr_matrix.astype(float)
    
    # Plot
    fig, ax = plt.subplots(figsize=(14, 12))
    
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool), k=1)
    
    sns.heatmap(corr_matrix, 
                mask=mask,
                annot=True, 
                fmt='.2f',
                cmap='RdBu_r',
                center=0,
                vmin=-1, vmax=1,
                square=True,
                linewidths=0.5,
                cbar_kws={'label': 'Correlacion de Pearson'},
                ax=ax)
    
    # Lineas de separacion de zonas
    ax.axhline(y=7, color='black', linewidth=2)
    ax.axhline(y=13, color='black', linewidth=2)
    ax.axvline(x=7, color='black', linewidth=2)
    ax.axvline(x=13, color='black', linewidth=2)
    
    ax.set_title('Matriz de Correlacion entre Estaciones\n' +
                 '(Solo triangulo inferior - Valores altos indican buena relacion)', 
                 fontsize=12, fontweight='bold')
    
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    return corr_matrix


def plot_double_mass(df, station_target, station_ref, output_path):
    """Genera curva de doble masa entre dos estaciones."""
    
    common = get_common_period(df, station_target, station_ref)
    
    if len(common) == 0:
        print(f"No hay datos concurrentes para {station_target} - {station_ref}")
        return None
    
    # Calcular acumulados
    common = common.sort_values('date')
    common['cumsum_target'] = common['level_1'].cumsum()
    common['cumsum_ref'] = common['level_2'].cumsum()
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Linea de doble masa
    ax.plot(common['cumsum_ref'], common['cumsum_target'], 
            'b-', linewidth=1, alpha=0.7, label='Doble Masa')
    
    # Linea de referencia (1:1 aproximada)
    max_val = max(common['cumsum_ref'].max(), common['cumsum_target'].max())
    ax.plot([0, max_val], [0, max_val], 'r--', linewidth=1.5, label='Linea 1:1 teórica')
    
    ax.set_xlabel(f'{station_ref.replace("_", " ").title()} - Niveles Acumulados (msnm)', fontsize=11)
    ax.set_ylabel(f'{station_target.replace("_", " ").title()} - Niveles Acumulados (msnm)', fontsize=11)
    ax.set_title(f'Curva de Doble Masa\n{station_target.replace("_", " ").title()} vs {station_ref.replace("_", " ").title()}\n' +
                 f'Periodo: {int(common["year_1"].min())}-{int(common["year_1"].max())} ({len(common)/365.25:.1f} años)',
                 fontsize=12, fontweight='bold')
    
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    return common


def plot_normalized_series(df, output_path):
    """Genera series temporales normalizadas (Z-score) por estación."""
    
    fig, axes = plt.subplots(3, 1, figsize=(16, 12), sharex=True)
    
    zones = [
        ('Zona Baja', GEOGRAPHIC_ORDER[:7]),
        ('Zona Media', GEOGRAPHIC_ORDER[7:13]),
        ('Zona Alta', GEOGRAPHIC_ORDER[13:])
    ]
    
    for idx, (zone_name, stations) in enumerate(zones):
        ax = axes[idx]
        
        for station in stations:
            if station not in df['station'].values:
                continue
            
            annual = get_station_annual_stats(df, station)
            if len(annual) < 5:
                continue
            
            # Calcular Z-score
            mean = annual['mean_level'].mean()
            std = annual['mean_level'].std()
            
            if std > 0:
                z_scores = (annual['mean_level'] - mean) / std
                ax.plot(annual['year'], z_scores, 
                       marker='o', markersize=3, linewidth=1.5, 
                       label=station.replace('_', ' ').title(), alpha=0.8)
        
        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8, alpha=0.5)
        ax.axhline(y=2, color='red', linestyle='--', linewidth=0.8, alpha=0.3)
        ax.axhline(y=-2, color='red', linestyle='--', linewidth=0.8, alpha=0.3)
        ax.set_ylabel('Z-score (desviaciones estándar)', fontsize=10)
        ax.set_title(f'{zone_name}', fontsize=11, fontweight='bold')
        ax.legend(loc='best', fontsize=8, ncol=2)
        ax.grid(True, alpha=0.3)
    
    axes[-1].set_xlabel('Año', fontsize=11)
    plt.suptitle('Series Temporales Normalizadas (Z-score) por Zona\n' +
                 'Valor 0 = Media histórica de la estación',
                 fontsize=13, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()


def plot_homogeneity_tests_summary(homog_results, output_path):
    """Genera gráfico resumen de pruebas de homogeneidad."""
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    stations = homog_results['station'].values
    x_pos = np.arange(len(stations))
    
    # 1. Pettitt Statistic
    ax = axes[0, 0]
    colors = ['red' if sig else 'gray' for sig in homog_results['pettitt_significant']]
    bars = ax.bar(x_pos, homog_results['pettitt_stat'].fillna(0), color=colors, alpha=0.7)
    ax.set_xticks(x_pos)
    ax.set_xticklabels([s.replace('_', '\n') for s in stations], rotation=45, ha='right', fontsize=8)
    ax.set_ylabel('Estadístico de Pettitt', fontsize=10)
    ax.set_title('Prueba de Pettitt (Cambio de Régimen)\nRojo = Significativo (p<0.05)', fontsize=11, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    
    # 2. SNHT Statistic
    ax = axes[0, 1]
    snht_vals = homog_results['snht_stat'].fillna(0)
    colors = ['red' if v > 9.5 else 'gray' for v in snht_vals]
    bars = ax.bar(x_pos, snht_vals, color=colors, alpha=0.7)
    ax.axhline(y=9.5, color='red', linestyle='--', linewidth=1.5, label='Umbral significativo')
    ax.set_xticks(x_pos)
    ax.set_xticklabels([s.replace('_', '\n') for s in stations], rotation=45, ha='right', fontsize=8)
    ax.set_ylabel('Estadístico SNHT', fontsize=10)
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
    
    # 4. Años de datos
    ax = axes[1, 1]
    bars = ax.bar(x_pos, homog_results['n_years'], color='steelblue', alpha=0.7)
    ax.set_xticks(x_pos)
    ax.set_xticklabels([s.replace('_', '\n') for s in stations], rotation=45, ha='right', fontsize=8)
    ax.set_ylabel('Número de años con datos', fontsize=10)
    ax.set_title('Longitud de Registros por Estación', fontsize=11, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.suptitle('Resumen de Pruebas de Homogeneidad', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()


# =============================================================================
# FUNCION PRINCIPAL
# =============================================================================

def main():
    """Ejecuta el análisis completo de homogeneidad."""
    
    print("=" * 70)
    print("ANALISIS DE HOMOGENEIDAD DE ESTACIONES - RIO MAGDALENA")
    print("=" * 70)
    
    # Rutas
    data_dir = r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\backend\data\raw\RawData\SERIE NIVELES IDEAM A 2026'
    output_dir = Path(r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\informes\homogeneidad')
    output_dir.mkdir(exist_ok=True)
    
    # 1. Cargar datos
    print("\n[1/6] Cargando datos...")
    df = load_data_long(data_dir)
    print(f"  Datos cargados: {len(df):,} registros de {df['station'].nunique()} estaciones")
    
    # 2. Analizar correlaciones entre pares
    print("\n[2/6] Analizando correlaciones entre pares...")
    corr_results = analyze_all_pairs(df)
    best_pairs = find_best_pairs(corr_results, min_correlation=0.7, top_n=10)
    
    print(f"  Total pares analizados: {len(corr_results)}")
    print(f"  Mejores pares (r>0.7): {len(best_pairs)}")
    print("\n  Top 5 mejores pares:")
    for idx, row in best_pairs.head(5).iterrows():
        print(f"    {row['station_1']} - {row['station_2']}: r={row['pearson_r']:.3f} ({row['years_concurrent']:.1f} anos)")
    
    # 3. Pruebas de homogeneidad por estación
    print("\n[3/6] Aplicando pruebas de homogeneidad...")
    homog_results = homogeneity_tests_by_station(df)
    print(f"  Estaciones analizadas: {len(homog_results)}")
    
    problematicas = homog_results[homog_results['pettitt_significant'] == True]
    print(f"  Estaciones con cambio significativo (Pettitt): {len(problematicas)}")
    if len(problematicas) > 0:
        for _, row in problematicas.iterrows():
            print(f"    - {row['station']}: cambio en {int(row['pettitt_year'])}")
    
    # 4. Generar visualizaciones
    print("\n[4/6] Generando visualizaciones...")
    
    # Matriz de correlación
    print("  - Matriz de correlacion...")
    corr_matrix = plot_correlation_matrix(df, output_dir / 'Figura_H1_Matriz_Correlacion.png')
    
    # Series normalizadas
    print("  - Series temporales normalizadas...")
    plot_normalized_series(df, output_dir / 'Figura_H2_Series_Normalizadas.png')
    
    # Resumen de pruebas
    print("  - Resumen de pruebas de homogeneidad...")
    plot_homogeneity_tests_summary(homog_results, output_dir / 'Figura_H3_Resumen_Pruebas.png')
    
    # Doble masa para mejores pares
    print("  - Curvas de doble masa (top 5 pares)...")
    for idx, row in best_pairs.head(5).iterrows():
        s1, s2 = row['station_1'], row['station_2']
        filename = f"Figura_H4_DobleMasa_{s1}_{s2}.png".replace(' ', '_')
        plot_double_mass(df, s1, s2, output_dir / filename)
    
    # 5. Guardar resultados
    print("\n[5/6] Guardando resultados...")
    homog_results.to_csv(output_dir / 'Tabla_H1_Resultados_Homogeneidad.csv', index=False, encoding='utf-8-sig')
    corr_results.to_csv(output_dir / 'Tabla_H2_Correlaciones_Pares.csv', index=False, encoding='utf-8-sig')
    best_pairs.to_csv(output_dir / 'Tabla_H3_Mejores_Pares.csv', index=False, encoding='utf-8-sig')
    
    # 6. Reporte final
    print("\n[6/6] Generando reporte de hallazgos...")
    generate_findings_report(homog_results, best_pairs, output_dir)
    
    print("\n" + "=" * 70)
    print("ANALISIS COMPLETADO")
    print(f"Resultados guardados en: {output_dir}")
    print("=" * 70)
    
    return homog_results, best_pairs, corr_results


def generate_findings_report(homog_results, best_pairs, output_dir):
    """Genera un archivo de texto con hallazgos principales."""
    
    report_path = output_dir / 'HALLAZGOS_HOMOGENEIDAD.txt'
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("HALLAZGOS DEL ANALISIS DE HOMOGENEIDAD\n")
        f.write("Rio Magdalena - Serie de Niveles IDEAM 1967-2026\n")
        f.write("=" * 70 + "\n\n")
        
        # Estaciones problematicas
        f.write("1. ESTACIONES CON CAMBIOS DE REGIMEN SIGNIFICATIVOS\n")
        f.write("-" * 70 + "\n")
        problematicas = homog_results[homog_results['pettitt_significant'] == True]
        if len(problematicas) > 0:
            for _, row in problematicas.iterrows():
                f.write(f"\n{row['station']}:\n")
                f.write(f"  - Cambio detectado en año: {int(row['pettitt_year'])}\n")
                f.write(f"  - Estadistico Pettitt: {row['pettitt_stat']:.2f} (p={row['pettitt_p']:.4f})\n")
        else:
            f.write("No se detectaron cambios significativos con la prueba de Pettitt.\n")
        
        # Estaciones con tendencias
        f.write("\n\n2. ESTACIONES CON TENDENCIAS SIGNIFICATIVAS\n")
        f.write("-" * 70 + "\n")
        tendencias = homog_results[homog_results['mk_significant'] == True]
        if len(tendencias) > 0:
            for _, row in tendencias.iterrows():
                f.write(f"\n{row['station']}:\n")
                f.write(f"  - Tendencia: {row['trend']}\n")
                f.write(f"  - Tau de Kendall: {row['mk_tau']:.3f} (p={row['mk_p']:.4f})\n")
        else:
            f.write("No se detectaron tendencias significativas con Mann-Kendall.\n")
        
        # Mejores pares
        f.write("\n\n3. MEJORES PARES DE ESTACIONES (ALTA CORRELACION)\n")
        f.write("-" * 70 + "\n")
        for idx, row in best_pairs.head(10).iterrows():
            f.write(f"\n{idx+1}. {row['station_1']} - {row['station_2']}\n")
            f.write(f"   Correlacion: r = {row['pearson_r']:.3f}\n")
            f.write(f"   Periodo comun: {int(row['period_start'])}-{int(row['period_end'])}\n")
            f.write(f"   Años concurrentes: {row['years_concurrent']:.1f}\n")
        
        # Estaciones de referencia
        f.write("\n\n4. ESTACIONES RECOMENDADAS COMO REFERENCIA\n")
        f.write("-" * 70 + "\n")
        ref_candidates = homog_results[
            (homog_results['pettitt_significant'] == False) & 
            (homog_results['mk_significant'] == False) &
            (homog_results['n_years'] > 30)
        ].sort_values('n_years', ascending=False)
        
        f.write("Estaciones homogeneas con largos registros (candidatas a donantes):\n")
        for _, row in ref_candidates.head(5).iterrows():
            f.write(f"  - {row['station']}: {int(row['n_years'])} años\n")
        
        f.write("\n" + "=" * 70 + "\n")
        f.write("Fin del reporte\n")
    
    print(f"  Reporte de hallazgos guardado: {report_path}")


if __name__ == '__main__':
    homog_results, best_pairs, corr_results = main()
