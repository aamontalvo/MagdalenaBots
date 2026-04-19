#!/usr/bin/env python3
"""
Analisis Detallado por Estaciones v3 - Seccion de Analisis de Hidrologia
=====================================================================

Version 3: 
- Violinplots con boxplot interno (inner='box')
- Sin boxplots separados
- 4 cifras significativas
- Seccion 6 con introduccion y resumen por estacion

Autor: Seccion de Analisis de Hidrologia
Fecha: 2026-02-25
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.stats import norm, lognorm, gamma, gumbel_r, weibull_min, pearson3
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Rutas
DATA_PATH = Path(r"C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\Data\Niveles")
PROCESSED_PATH = DATA_PATH / "01_processed"
ANALYSIS_PATH = DATA_PATH / "02_analysis"
FIGURES_PATH = DATA_PATH / "03_figures" / "detailed_analysis"
FIGURES_PATH.mkdir(parents=True, exist_ok=True)

# Estaciones con buenos datos
GOOD_STATIONS = ['Calamar', 'Las Aguadas', 'El Banco']

# Distribuciones
DISTRIBUTIONS = {
    'Normal': norm,
    'Log-Normal': lognorm,
    'Gamma': gamma,
    'Gumbel': gumbel_r,
    'Weibull': weibull_min,
    'Pearson III': pearson3
}


def format_significant(x, n=4):
    if pd.isna(x):
        return x
    if isinstance(x, (int, np.integer)):
        return int(x)
    return float(f"{x:.{n}g}")


class DetailedStationAnalysisV3:
    """Analisis estadistico detallado por estacion - v3."""
    
    def __init__(self):
        self.df = None
        self.results = {}
        
    def load_data(self):
        print("=" * 70)
        print("ANALISIS DETALLADO POR ESTACIONES v3")
        print("Seccion de Analisis de Hidrologia")
        print("=" * 70)
        
        self.df = pd.read_csv(PROCESSED_PATH / "magdalena_levels_imputed.csv")
        self.df['fecha'] = pd.to_datetime(self.df['fecha'])
        
        print(f"\nDatos cargados: {len(self.df):,} registros")
        return self.df
    
    def monthly_violin_with_boxplot(self, station):
        """
        Genera violinplot mensual CON BOXPLOT INTERNO.
        """
        print(f"\nGenerando violinplot con boxplot interno para {station}...")
        
        station_data = self.df[self.df['estacion'] == station].copy()
        station_data = station_data[station_data['nivel_msnm'].notna()]
        
        month_names = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
                      'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
        station_data['mes_nombre'] = station_data['mes'].apply(lambda x: month_names[x-1])
        station_data['mes_nombre'] = pd.Categorical(
            station_data['mes_nombre'], categories=month_names, ordered=True
        )
        
        # Calcular medias mensuales
        monthly_means = station_data.groupby('mes_nombre')['nivel_msnm'].mean()
        
        # Crear figura
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Violin plot CON BOXPLOT INTERNO
        sns.violinplot(data=station_data, x='mes_nombre', y='nivel_msnm',
                      color='lightgray',
                      inner='box',  # <-- BOXPLOT INTERNO
                      linewidth=1.5,
                      edgecolor='black',
                      ax=ax)
        
        # Linea de media mensual multianual
        x_positions = range(12)
        ax.plot(x_positions, monthly_means.values, 
               color='black', 
               linestyle='--', 
               linewidth=2.5,
               marker='o',
               markersize=6,
               label='Media mensual multianual',
               zorder=10)
        
        ax.set_xlabel('Mes', fontsize=13, fontweight='bold')
        ax.set_ylabel('Cota (m.s.n.m.)', fontsize=13, fontweight='bold')
        ax.set_title(f'Distribucion Mensual Multianual de Cotas - {station}\n'
                    f'(Violin plot con boxplot interno y media mensual multianual)', 
                    fontsize=14, fontweight='bold')
        ax.legend(loc='upper left', fontsize=11)
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        
        output_file = FIGURES_PATH / f"{station}_monthly_violin_boxplot.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"  Guardado: {output_file}")
        plt.close()
        
        # Retornar estadisticas mensuales
        monthly_stats = station_data.groupby('mes')['nivel_msnm'].agg([
            'count', 'mean', 'std', 'min', 'max'
        ]).round(4)
        return monthly_stats
    
    def fit_distributions(self, data):
        """Ajusta distribuciones con 4 cifras significativas."""
        results = {}
        clean_data = data.dropna()
        if len(clean_data) < 30:
            return None
        
        for dist_name, dist in DISTRIBUTIONS.items():
            try:
                params = dist.fit(clean_data)
                log_likelihood = np.sum(dist.logpdf(clean_data, *params))
                k = len(params)
                n = len(clean_data)
                aic = 2 * k - 2 * log_likelihood
                bic = np.log(n) * k - 2 * log_likelihood
                ks_stat, ks_pvalue = stats.kstest(clean_data, lambda x: dist.cdf(x, *params))
                
                results[dist_name] = {
                    'params': [format_significant(p, 4) for p in params],
                    'AIC': format_significant(aic, 4),
                    'BIC': format_significant(bic, 4),
                    'KS_statistic': format_significant(ks_stat, 4),
                    'KS_pvalue': format_significant(ks_pvalue, 4),
                }
            except:
                results[dist_name] = {'error': 'No convergio'}
        
        return results
    
    def analyze_station(self, station):
        """Analisis completo de una estacion."""
        print(f"\n{'='*70}")
        print(f"ANALISIS DETALLADO: {station.upper()}")
        print(f"{'='*70}")
        
        station_data = self.df[self.df['estacion'] == station].copy()
        levels = station_data['nivel_msnm']
        
        # Estadisticas descriptivas
        print("\n1. ESTADISTICAS DESCRIPTIVAS:")
        desc = levels.describe()
        print(f"   N: {int(desc['count']):,}")
        print(f"   Media: {format_significant(desc['mean'], 4)} m")
        print(f"   Desv.Est: {format_significant(desc['std'], 4)} m")
        print(f"   Min: {format_significant(desc['min'], 4)} m")
        print(f"   Max: {format_significant(desc['max'], 4)} m")
        
        # Violinplot con boxplot interno
        print("\n2. VIOLINPLOT MENSUAL (CON BOXPLOT INTERNO):")
        monthly_stats = self.monthly_violin_with_boxplot(station)
        
        # Ajuste de distribuciones
        print("\n3. AJUSTE DE DISTRIBUCIONES:")
        fit_results = self.fit_distributions(levels)
        
        if fit_results:
            valid_results = {k: v for k, v in fit_results.items() if 'AIC' in v}
            if valid_results:
                best_dist = min(valid_results.items(), key=lambda x: x[1]['AIC'])
                dist_name, result = best_dist
                
                print(f"   Mejor distribucion: {dist_name}")
                print(f"   AIC: {result['AIC']}")
                print(f"   KS p-value: {result['KS_pvalue']}")
                print(f"   Parametros: {result['params']}")
                
                self.results[station] = {
                    'distribucion': dist_name,
                    'aic': result['AIC'],
                    'ks_pvalue': result['KS_pvalue'],
                    'parametros': result['params'],
                    'n': int(desc['count']),
                    'media': format_significant(desc['mean'], 4),
                    'desv_est': format_significant(desc['std'], 4)
                }
        
        return self.results.get(station)
    
    def generate_summary_table(self):
        """Genera tabla resumen para todas las estaciones."""
        print(f"\n{'='*70}")
        print("RESUMEN POR ESTACION - SECCION 6")
        print(f"{'='*70}")
        
        summary_data = []
        for station, results in self.results.items():
            summary_data.append({
                'Estacion': station,
                'N': results['n'],
                'Media_m': results['media'],
                'Desv_Est_m': results['desv_est'],
                'Mejor_Distribucion': results['distribucion'],
                'AIC': results['aic'],
                'Parametros': str(results['parametros'])
            })
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_csv(ANALYSIS_PATH / "station_summary_section6.csv", index=False)
        
        print("\nTabla resumen generada:")
        print(summary_df.to_string(index=False))
        
        return summary_df
    
    def run_analysis(self):
        self.load_data()
        
        for station in GOOD_STATIONS:
            self.analyze_station(station)
        
        self.generate_summary_table()
        
        print(f"\n{'='*70}")
        print("ANALISIS DETALLADO v3 FINALIZADO")
        print(f"{'='*70}")
        
        return self.results


if __name__ == '__main__':
    analyzer = DetailedStationAnalysisV3()
    results = analyzer.run_analysis()
