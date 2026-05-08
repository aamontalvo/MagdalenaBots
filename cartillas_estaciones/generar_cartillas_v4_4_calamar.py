"""
Generador rapido de cartillas CALAMAR v4.4
Solo regenera CALAMAR con el dataset v4.4 para verificar el parche.
Basado en generar_cartillas_v4_3.py
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import scipy.stats as stats
import warnings
warnings.filterwarnings('ignore')

plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['axes.grid'] = True
plt.rcParams['grid.alpha'] = 0.3

INPUT_FILE = Path(r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\backend\data\processed\imputation\Datos_Imputados_v4_4_ClimatologyPatch.csv')
OUTPUT_DIR = Path(r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\cartillas_estaciones\v4_4_CALAMAR')
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

MESES = ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN', 'JUL', 'AGO', 'SEP', 'OCT', 'NOV', 'DIC']

def clasificar_metodo(metodo_str):
    if metodo_str == 'Original':
        return 'original'
    elif metodo_str == 'L1_Interpolacion':
        return 'L1'
    elif metodo_str.startswith('L2_HH_') and 'quadratic' in metodo_str:
        return 'L2'
    elif metodo_str == 'L3_missForest':
        return 'L3'
    elif metodo_str == 'L4_Climatologia_Estacional':
        return 'L4'
    else:
        return 'L3'

def load_data():
    df = pd.read_csv(INPUT_FILE)
    df['date'] = pd.to_datetime(df['Fecha'])
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['day'] = df['date'].dt.day
    df['day_of_year'] = df['date'].dt.dayofyear
    df['data_source'] = df['Metodo'].apply(clasificar_metodo)
    return df

# Figura 1: Serie temporal
def plot_fig1(station_df, station, output_path):
    fig, ax = plt.subplots(figsize=(14, 6))
    valid_data = station_df[station_df['Cota'].notna()]
    ax.plot(valid_data['date'], valid_data['Cota'], 'k-', linewidth=0.8)

    total_valid = len(valid_data)
    original_count = (station_df['data_source'] == 'original').sum()
    imputed_count = total_valid - original_count
    pct_original = (original_count / total_valid) * 100 if total_valid > 0 else 0
    pct_imputed = (imputed_count / total_valid) * 100 if total_valid > 0 else 0
    year_start = int(station_df['year'].min())
    year_end = int(station_df['year'].max())

    annotation_text = (f'Periodo: {year_start}-{year_end} | Total: {total_valid:,} observaciones\n'
                       f'Originales: {pct_original:.1f}% | Imputados: {pct_imputed:.1f}%')
    ax.text(0.02, 0.98, annotation_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.9))
    ax.set_title(f'Serie de Tiempo de Cotas - {station.replace("_", " ")}', fontsize=13, fontweight='bold')
    ax.set_xlabel('Fecha', fontsize=11)
    ax.set_ylabel('Cota (m.s.n.m.)', fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.xaxis.set_major_locator(plt.MaxNLocator(10))
    fig.autofmt_xdate()
    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    return True

# Figura 2: Violin mensual
def plot_fig2(station_df, station, output_path):
    original = station_df[station_df['data_source'] == 'original'].copy()
    if len(original) < 30:
        return False
    fig, ax = plt.subplots(figsize=(14, 6))
    data_by_month = []
    positions = []
    for month in range(1, 13):
        month_data = original[original['month'] == month]['Cota'].dropna()
        if len(month_data) > 0:
            data_by_month.append(month_data.values)
            positions.append(month)
    if len(data_by_month) == 0:
        return False
    parts = ax.violinplot(data_by_month, positions=positions, widths=0.7,
                          showmeans=True, showmedians=True, showextrema=True)
    for pc in parts['bodies']:
        pc.set_facecolor('lightgray')
        pc.set_edgecolor('gray')
        pc.set_alpha(0.7)
    parts['cmeans'].set_color('red')
    parts['cmeans'].set_linewidth(2)
    parts['cmedians'].set_color('black')
    parts['cmedians'].set_linewidth(2)
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], color='red', linewidth=2, label='Media'),
        Line2D([0], [0], color='black', linewidth=2, label='Mediana')
    ]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=10)
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(MESES)
    ax.set_title(f'Distribucion Mensual de Cotas - {station.replace("_", " ")}', fontsize=13, fontweight='bold')
    ax.set_xlabel('Mes', fontsize=11)
    ax.set_ylabel('Cota (m.s.n.m.)', fontsize=11)
    ax.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    return True

# Figura 3: Curva de duracion
def plot_fig3(station_df, station, output_path):
    fig, ax = plt.subplots(figsize=(10, 7))
    levels = station_df['Cota'].dropna().sort_values(ascending=False)
    if len(levels) < 10:
        return False
    n = len(levels)
    exceedance_prob = np.arange(1, n + 1) / (n + 1) * 100
    ax.plot(exceedance_prob, levels, color='#1f77b4', linewidth=2.5)
    p50_level = np.percentile(levels, 50)
    p90_level = np.percentile(levels, 10)
    p95_level = np.percentile(levels, 5)
    p100_level = levels.min()
    p50_idx = np.argmin(np.abs(exceedance_prob - 50))
    p90_idx = np.argmin(np.abs(exceedance_prob - 90))
    p95_idx = np.argmin(np.abs(exceedance_prob - 95))
    p100_idx = np.argmin(np.abs(exceedance_prob - 99.5))
    ax.plot(50, p50_level, 'o', markersize=12, markerfacecolor='white', markeredgecolor='black', markeredgewidth=1.5)
    ax.plot(90, p90_level, 'o', markersize=12, markerfacecolor='white', markeredgecolor='black', markeredgewidth=1.5)
    ax.plot(95, p95_level, 'o', markersize=12, markerfacecolor='white', markeredgecolor='black', markeredgewidth=1.5)
    ax.plot(99.5, p100_level, 'o', markersize=12, markerfacecolor='white', markeredgecolor='black', markeredgewidth=1.5)
    ax.text(50, p50_level + 0.3, f'P50: {p50_level:.2f} m', ha='center', fontsize=11, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='gray'))
    ax.text(90, p90_level + 0.3, f'P90: {p90_level:.2f} m', ha='center', fontsize=11, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='gray'))
    ax.text(95, p95_level - 0.4, f'P95: {p95_level:.2f} m', ha='center', fontsize=11, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='gray'))
    ax.text(99.5, p100_level - 0.4, f'P100: {p100_level:.2f} m', ha='center', fontsize=11, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='gray'))
    ax.set_title(f'Curva de Duracion - {station.replace("_", " ").upper()}', fontsize=14, fontweight='bold')
    ax.set_xlabel('Porcentaje de tiempo excedido (%)', fontsize=12)
    ax.set_ylabel('Cota (m.s.n.m.)', fontsize=12)
    ax.grid(True, alpha=0.3, linestyle='-')
    ax.set_xlim(-2, 102)
    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    return True

# Figura 4: Percentiles diarios (solo originales)
def plot_fig4(station_df, station, output_path, csv_dir):
    df = station_df.copy()
    df['mes_dia'] = df['date'].dt.strftime('%m-%d')
    df = df[df['mes_dia'] != '02-29']
    df_clean = df[(df['Cota'].notna()) & (df['data_source'] == 'original')].copy()
    if len(df_clean) == 0:
        return False

    fecha_base = pd.date_range('2020-01-01', '2020-12-31', freq='D')
    fecha_base = fecha_base[fecha_base.strftime('%m-%d') != '02-29']
    results = []
    for i, fecha in enumerate(fecha_base, 1):
        mes_dia = fecha.strftime('%m-%d')
        day_data = df_clean[df_clean['mes_dia'] == mes_dia]['Cota'].values
        if len(day_data) > 0:
            results.append({
                'day_of_year': i, 'mes_dia': mes_dia,
                'max': round(np.max(day_data), 3), 'p95': round(np.percentile(day_data, 95), 3),
                'p90': round(np.percentile(day_data, 90), 3), 'p75': round(np.percentile(day_data, 75), 3),
                'p50': round(np.percentile(day_data, 50), 3), 'p25': round(np.percentile(day_data, 25), 3),
                'p10': round(np.percentile(day_data, 10), 3), 'p5': round(np.percentile(day_data, 5), 3),
                'min': round(np.min(day_data), 3), 'n_obs': len(day_data)
            })
    perc_df = pd.DataFrame(results)
    csv_path = csv_dir / f'percentiles_{station}.csv'
    perc_df.to_csv(csv_path, index=False)

    fig, ax = plt.subplots(figsize=(14, 7))
    days = perc_df['day_of_year'].values
    ax.fill_between(days, perc_df['p5'], perc_df['p95'], color='#d73027', alpha=0.15, label='P5-P95')
    ax.fill_between(days, perc_df['p25'], perc_df['p75'], color='#4575b4', alpha=0.3, label='P25-P75')
    ax.plot(days, perc_df['p50'], color='#1a1a1a', linewidth=2.2, label='Mediana (P50)')
    ax.plot(days, perc_df['max'], color='#d73027', linewidth=1.0, linestyle='--', alpha=0.7, label='Max')
    ax.plot(days, perc_df['min'], color='#4575b4', linewidth=1.0, linestyle='--', alpha=0.7, label='Min')

    month_starts = [1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335]
    month_labels = MESES
    ax.set_xticks(month_starts)
    ax.set_xticklabels(month_labels)
    ax.set_xlim(1, 365)
    ax.set_title(f'Percentiles Climatologicos Diarios - {station.replace("_", " ")}', fontsize=13, fontweight='bold')
    ax.set_xlabel('Mes', fontsize=11)
    ax.set_ylabel('Cota (m.s.n.m.)', fontsize=11)
    ax.legend(loc='upper right', fontsize=10, framealpha=0.9)
    ax.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    return True

# Figura 5: Distribuciones
def plot_fig5(station_df, station, output_path):
    original = station_df[station_df['data_source'] == 'original']['Cota'].dropna()
    if len(original) < 30:
        return False
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()

    dists = [
        ('Normal', stats.norm),
        ('Log-Normal', stats.lognorm),
        ('Gumbel', stats.gumbel_r),
        ('Weibull', stats.weibull_min),
        ('Gamma', stats.gamma),
        ('Exponencial', stats.expon)
    ]

    for idx, (name, dist) in enumerate(dists):
        ax = axes[idx]
        try:
            params = dist.fit(original)
            x = np.linspace(original.min(), original.max(), 200)
            pdf = dist.pdf(x, *params)
            ax.hist(original, bins=50, density=True, alpha=0.6, color='steelblue', edgecolor='white')
            ax.plot(x, pdf, 'r-', linewidth=2, label=f'{name}')
            ax.set_title(f'{name}', fontsize=11, fontweight='bold')
            ax.set_xlabel('Cota (m.s.n.m.)')
            ax.set_ylabel('Densidad')
            ax.legend(loc='best', fontsize=9)
        except Exception as e:
            ax.text(0.5, 0.5, f'Error ajustando\n{name}', transform=ax.transAxes, ha='center', va='center')
            ax.set_title(f'{name} (Error)')
        ax.grid(True, alpha=0.3)

    fig.suptitle(f'Ajuste de Distribuciones - {station.replace("_", " ")}', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    return True


# ===== MAIN =====
print("Generando cartillas CALAMAR v4.4...")
df = load_data()
station = 'CALAMAR'
station_df = df[df['NombreEstacion'] == station].copy().sort_values('date')

fig1_path = OUTPUT_DIR / f'Fig1_SerieTiempo_{station}_v4_4.png'
fig2_path = OUTPUT_DIR / f'Fig2_ViolinMensual_{station}_v4_4.png'
fig3_path = OUTPUT_DIR / f'Fig3_CurvaDuracion_{station}_v4_4.png'
fig4_path = OUTPUT_DIR / f'Fig4_PercentilesDiarios_{station}_v4_4.png'
fig5_path = OUTPUT_DIR / f'Fig5_Distribuciones_{station}_v4_4.png'

plot_fig1(station_df, station, fig1_path)
print(f"  Fig1: {fig1_path.name}")
plot_fig2(station_df, station, fig2_path)
print(f"  Fig2: {fig2_path.name}")
plot_fig3(station_df, station, fig3_path)
print(f"  Fig3: {fig3_path.name}")
plot_fig4(station_df, station, fig4_path, OUTPUT_DIR)
print(f"  Fig4: {fig4_path.name}")
plot_fig5(station_df, station, fig5_path)
print(f"  Fig5: {fig5_path.name}")

print(f"\nCartillas CALAMAR v4.4 guardadas en: {OUTPUT_DIR}")
