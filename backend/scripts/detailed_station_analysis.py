#!/usr/bin/env python3
"""
Analisis Detallado por Estaciones - Seccion de Analisis de Hidrologia
=====================================================================

Analisis estadistico detallado para estaciones con datos completos:
- Violinplots mensuales multianuales
- Ajustes de distribuciones de probabilidad (PDF)
- Verificacion de supuestos estadisticos
- Pruebas de bondad de ajuste

Metodologia:
- Analisis mensual agregado de todos los anos
- Ajuste de distribuciones parametricas convencionales
- Pruebas de normalidad (Shapiro-Wilk, Kolmogorov-Smirnov)
- Seleccion del mejor ajuste por criterios AIC/BIC

Autor: Seccion de Analisis de Hidrologia
Fecha: 2026-02-25
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.stats import (
    norm, lognorm, gamma, gumbel_r, 
    expon, weibull_min, pearson3
)
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Configuracion de estilo
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("Blues")

# Rutas
DATA_PATH = Path(r"C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\Data\Niveles")
PROCESSED_PATH = DATA_PATH / "01_processed"
ANALYSIS_PATH = DATA_PATH / "02_analysis"
FIGURES_PATH = DATA_PATH / "03_figures" / "detailed_analysis"
FIGURES_PATH.mkdir(parents=True, exist_ok=True)

# Estaciones con buenos datos (>=85% completitud)
GOOD_STATIONS = ['Calamar', 'Las Aguadas', 'El Banco']

# Distribuciones a probar
DISTRIBUTIONS = {
    'Normal': norm,
    'Log-Normal': lognorm,
    'Gamma': gamma,
    'Gumbel': gumbel_r,
    'Weibull': weibull_min,
    'Pearson III': pearson3
}


class DetailedStationAnalysis:
    """Analisis estadistico detallado por estacion."""
    
    def __init__(self):
        self.df = None
        self.results = {}
        
    def load_data(self):
        """Carga datos imputados."""
        print("=" * 70)
        print("ANALISIS DETALLADO POR ESTACIONES")
        print("Seccion de Analisis de Hidrologia")
        print("=" * 70)
        
        self.df = pd.read_csv(PROCESSED_PATH / "magdalena_levels_imputed.csv")
        self.df['fecha'] = pd.to_datetime(self.df['fecha'])
        
        print(f"\nDatos cargados: {len(self.df):,} registros")
        
        return self.df
    
    def monthly_violin_analysis(self, station):
        """
        Genera violinplots mensuales multianuales para una estacion.
        """
        print(f"\nGenerando violinplots mensuales para {station}...")
        
        # Filtrar datos de la estacion
        station_data = self.df[self.df['estacion'] == station].copy()
        station_data = station_data[station_data['nivel_msnm'].notna()]
        
        # Agregar nombre del mes
        month_names = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
                      'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
        station_data['mes_nombre'] = station_data['mes'].apply(lambda x: month_names[x-1])
        station_data['mes_nombre'] = pd.Categorical(
            station_data['mes_nombre'], 
            categories=month_names, 
            ordered=True
        )
        
        # Estadisticas mensuales
        monthly_stats = station_data.groupby('mes')['nivel_msnm'].agg([
            'count', 'mean', 'std', 'min', 'max',
            lambda x: x.quantile(0.25),
            lambda x: x.quantile(0.50),
            lambda x: x.quantile(0.75)
        ]).round(3)
        monthly_stats.columns = ['N', 'Media', 'Desv_Est', 'Min', 'Max', 'Q1', 'Q2', 'Q3']
        monthly_stats['Mes'] = month_names
        
        # Crear figura
        fig, axes = plt.subplots(2, 1, figsize=(14, 12))
        
        # 1. Violin plot mensual
        ax1 = axes[0]
        sns.violinplot(data=station_data, x='mes_nombre', y='nivel_msnm',
                      palette='Blues', ax=ax1, inner='box', linewidth=1)
        
        ax1.set_xlabel('Mes', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Cota (m.s.n.m.)', fontsize=12, fontweight='bold')
        ax1.set_title(f'Distribucion Mensual Multianual de Cotas - {station}\n'
                     '(Violin plot con estadisticas internas)', 
                     fontsize=13, fontweight='bold')
        ax1.grid(axis='y', alpha=0.3)
        
        # 2. Boxplot mensual con puntos de outliers
        ax2 = axes[1]
        bp = station_data.boxplot(column='nivel_msnm', by='mes_nombre',
                                 ax=ax2, patch_artist=True,
                                 boxprops=dict(facecolor='#4A6FA5', alpha=0.7, edgecolor='white'),
                                 medianprops=dict(color='white', linewidth=2),
                                 whiskerprops=dict(color='#666666'),
                                 capprops=dict(color='#666666'),
                                 flierprops=dict(marker='o', markerfacecolor='#333333',
                                                markersize=4, alpha=0.5))
        
        ax2.set_xlabel('Mes', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Cota (m.s.n.m.)', fontsize=12, fontweight='bold')
        ax2.set_title(f'Diagramas de Caja Mensuales - {station}\n'
                     '(Valores atipicos mostrados como puntos)',
                     fontsize=13, fontweight='bold')
        ax2.grid(axis='y', alpha=0.3)
        
        plt.suptitle('')  # Remover titulo automatico
        plt.tight_layout()
        
        # Guardar
        output_file = FIGURES_PATH / f"{station}_monthly_violin_analysis.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"  Guardado: {output_file}")
        plt.close()
        
        return monthly_stats
    
    def fit_distributions(self, data, station, month=None):
        """
        Ajusta multiples distribuciones y selecciona la mejor.
        
        Returns:
            dict con resultados de cada distribucion
        """
        results = {}
        
        # Limpiar datos
        clean_data = data.dropna()
        if len(clean_data) < 30:
            return None
        
        for dist_name, dist in DISTRIBUTIONS.items():
            try:
                # Ajustar distribucion
                params = dist.fit(clean_data)
                
                # Calcular log-likelihood
                log_likelihood = np.sum(dist.logpdf(clean_data, *params))
                
                # Numero de parametros
                k = len(params)
                n = len(clean_data)
                
                # Criterios de informacion
                aic = 2 * k - 2 * log_likelihood
                bic = np.log(n) * k - 2 * log_likelihood
                
                # Prueba KS
                ks_stat, ks_pvalue = stats.kstest(clean_data, lambda x: dist.cdf(x, *params))
                
                # Guardar resultados
                results[dist_name] = {
                    'params': params,
                    'log_likelihood': log_likelihood,
                    'AIC': aic,
                    'BIC': bic,
                    'KS_statistic': ks_stat,
                    'KS_pvalue': ks_pvalue,
                    'n_params': k
                }
                
            except Exception as e:
                results[dist_name] = {'error': str(e)}
        
        return results
    
    def test_normality_assumptions(self, data):
        """
        Verifica supuestos de normalidad.
        """
        clean_data = data.dropna()
        
        if len(clean_data) < 30:
            return None
        
        # Shapiro-Wilk (solo para n < 5000)
        if len(clean_data) <= 5000:
            shapiro_stat, shapiro_p = stats.shapiro(clean_data)
        else:
            shapiro_stat, shapiro_p = None, None
        
        # Kolmogorov-Smirnov
        ks_stat, ks_p = stats.kstest(clean_data, 'norm', 
                                     args=(clean_data.mean(), clean_data.std()))
        
        # D'Agostino
        dagostino_stat, dagostino_p = stats.normaltest(clean_data)
        
        # Asimetria y curtosis
        skewness = stats.skew(clean_data)
        kurtosis = stats.kurtosis(clean_data)
        
        return {
            'Shapiro_Stat': shapiro_stat,
            'Shapiro_p': shapiro_p,
            'KS_Stat': ks_stat,
            'KS_p': ks_p,
            'DAgostino_Stat': dagostino_stat,
            'DAgostino_p': dagostino_p,
            'Asimetria': skewness,
            'Curtosis': kurtosis
        }
    
    def plot_pdf_fits(self, data, station, month=None):
        """
        Grafica las distribuciones ajustadas vs histograma de datos.
        """
        clean_data = data.dropna()
        if len(clean_data) < 30:
            return None
        
        # Ajustar distribuciones
        fit_results = self.fit_distributions(clean_data, station, month)
        if not fit_results:
            return None
        
        # Seleccionar top 3 por AIC
        valid_results = {k: v for k, v in fit_results.items() if 'AIC' in v}
        if not valid_results:
            return None
        
        top_3 = sorted(valid_results.items(), key=lambda x: x[1]['AIC'])[:3]
        
        # Crear figura
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        
        # 1. Histograma con PDFs ajustadas
        ax1 = axes[0]
        ax1.hist(clean_data, bins=50, density=True, alpha=0.5, 
                color='#2E5EAA', edgecolor='white', label='Datos observados')
        
        x = np.linspace(clean_data.min(), clean_data.max(), 1000)
        
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
        for idx, (dist_name, result) in enumerate(top_3):
            dist = DISTRIBUTIONS[dist_name]
            params = result['params']
            pdf = dist.pdf(x, *params)
            ax1.plot(x, pdf, linewidth=2, color=colors[idx],
                    label=f"{dist_name} (AIC={result['AIC']:.1f})")
        
        periodo = f"Mes {month}" if month else "Anual"
        ax1.set_xlabel('Cota (m.s.n.m.)', fontsize=11)
        ax1.set_ylabel('Densidad de probabilidad', fontsize=11)
        ax1.set_title(f'Ajuste de Distribuciones - {station}\n{periodo}', 
                     fontsize=12, fontweight='bold')
        ax1.legend(loc='best', fontsize=9)
        ax1.grid(alpha=0.3)
        
        # 2. Q-Q plot para la mejor distribucion
        ax2 = axes[1]
        best_dist_name, best_result = top_3[0]
        best_dist = DISTRIBUTIONS[best_dist_name]
        
        # Calcular cuantiles teoricos
        params = best_result['params']
        theoretical_quantiles = best_dist.ppf(
            np.linspace(0.01, 0.99, len(clean_data)), 
            *params
        )
        observed_quantiles = np.sort(clean_data)
        
        ax2.scatter(theoretical_quantiles, observed_quantiles, 
                   alpha=0.5, s=20, color='#2E5EAA', edgecolors='none')
        
        # Linea 1:1
        min_val = min(theoretical_quantiles.min(), observed_quantiles.min())
        max_val = max(theoretical_quantiles.max(), observed_quantiles.max())
        ax2.plot([min_val, max_val], [min_val, max_val], 'r--', 
                linewidth=2, label='1:1')
        
        ax2.set_xlabel(f'Cuantiles teoricos ({best_dist_name})', fontsize=11)
        ax2.set_ylabel('Cuantiles observados', fontsize=11)
        ax2.set_title(f'Q-Q Plot - Mejor Ajuste: {best_dist_name}\n'
                     f"KS p-value: {best_result['KS_pvalue']:.4f}",
                     fontsize=12, fontweight='bold')
        ax2.legend(loc='best')
        ax2.grid(alpha=0.3)
        
        plt.tight_layout()
        
        # Guardar
        suffix = f"_mes{month:02d}" if month else "_anual"
        output_file = FIGURES_PATH / f"{station}_pdf_fits{suffix}.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        return fit_results, top_3[0]
    
    def analyze_station(self, station):
        """
        Analisis completo de una estacion.
        """
        print(f"\n{'='*70}")
        print(f"ANALISIS DETALLADO: {station.upper()}")
        print(f"{'='*70}")
        
        station_data = self.df[self.df['estacion'] == station].copy()
        levels = station_data['nivel_msnm']
        
        # 1. Estadisticas descriptivas
        print("\n1. ESTADISTICAS DESCRIPTIVAS:")
        print("-" * 50)
        desc_stats = levels.describe()
        print(f"   N registros: {int(desc_stats['count']):,}")
        print(f"   Media: {desc_stats['mean']:.3f} m")
        print(f"   Desv. Est.: {desc_stats['std']:.3f} m")
        print(f"   Min: {desc_stats['min']:.3f} m")
        print(f"   Max: {desc_stats['max']:.3f} m")
        print(f"   Mediana: {levels.median():.3f} m")
        
        # 2. Violinplots mensuales
        print("\n2. VIOLINPLOTS MENSUALES:")
        print("-" * 50)
        monthly_stats = self.monthly_violin_analysis(station)
        print(f"   Guardado: {station}_monthly_violin_analysis.png")
        
        # 3. Verificacion de supuestos (anual)
        print("\n3. VERIFICACION DE SUPUESTOS (ANUAL):")
        print("-" * 50)
        normality = self.test_normality_assumptions(levels)
        
        if normality:
            print(f"   Shapiro-Wilk p-value: {normality['Shapiro_p']:.4f}" 
                  if normality['Shapiro_p'] else "   Shapiro-Wilk: N/A (n>5000)")
            print(f"   Kolmogorov-Smirnov p-value: {normality['KS_p']:.4f}")
            print(f"   D'Agostino p-value: {normality['DAgostino_p']:.4f}")
            print(f"   Asimetria: {normality['Asimetria']:.3f}")
            print(f"   Curtosis: {normality['Curtosis']:.3f}")
            
            # Interpretacion
            if normality['KS_p'] > 0.05:
                print("   -> Los datos NO rechazan normalidad (p > 0.05)")
            else:
                print("   -> Los datos rechazan normalidad (p < 0.05)")
        
        # 4. Ajuste de distribuciones (anual)
        print("\n4. AJUSTE DE DISTRIBUCIONES (ANUAL):")
        print("-" * 50)
        fit_results, best_fit = self.plot_pdf_fits(levels, station)
        
        if best_fit:
            dist_name, result = best_fit
            print(f"   Mejor distribucion: {dist_name}")
            print(f"   AIC: {result['AIC']:.2f}")
            print(f"   BIC: {result['BIC']:.2f}")
            print(f"   KS p-value: {result['KS_pvalue']:.4f}")
            print(f"   Parametros: {[f'{p:.4f}' for p in result['params']]}")
        
        # 5. Ajuste mensual
        print("\n5. AJUSTE DE DISTRIBUCIONES (MENSUAL):")
        print("-" * 50)
        monthly_fits = []
        
        for month in range(1, 13):
            month_data = station_data[station_data['mes'] == month]['nivel_msnm']
            
            if len(month_data.dropna()) < 30:
                continue
            
            fit_results, best = self.plot_pdf_fits(month_data, station, month)
            
            if best:
                dist_name, result = best
                monthly_fits.append({
                    'Mes': month,
                    'Distribucion': dist_name,
                    'AIC': result['AIC'],
                    'KS_pvalue': result['KS_pvalue'],
                    'Media': month_data.mean(),
                    'Desv_Est': month_data.std()
                })
                print(f"   Mes {month:2d}: {dist_name:15s} "
                      f"(AIC={result['AIC']:.1f}, KS p={result['KS_pvalue']:.4f})")
        
        # Guardar resultados
        self.results[station] = {
            'monthly_stats': monthly_stats,
            'normality_tests': normality,
            'best_fit_annual': best_fit,
            'monthly_fits': monthly_fits
        }
        
        return self.results[station]
    
    def generate_summary_report(self):
        """Genera tabla resumen de todos los analisis."""
        print(f"\n{'='*70}")
        print("RESUMEN DE AJUSTES POR ESTACION")
        print(f"{'='*70}")
        
        summary_data = []
        
        for station, results in self.results.items():
            if results['best_fit_annual']:
                dist_name, result = results['best_fit_annual']
                summary_data.append({
                    'Estacion': station,
                    'Mejor_Dist_Anual': dist_name,
                    'AIC_Anual': round(result['AIC'], 1),
                    'KS_pvalue_Anual': round(result['KS_pvalue'], 4),
                    'Cumple_Normal': 'Si' if results['normality_tests'] and 
                                           results['normality_tests']['KS_p'] > 0.05 else 'No'
                })
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_csv(ANALYSIS_PATH / "distribution_fits_summary.csv", index=False)
        
        print("\n" + summary_df.to_string(index=False))
        
        return summary_df
    
    def run_analysis(self):
        """Ejecuta analisis completo."""
        self.load_data()
        
        for station in GOOD_STATIONS:
            self.analyze_station(station)
        
        self.generate_summary_report()
        
        print(f"\n{'='*70}")
        print("ANALISIS DETALLADO FINALIZADO")
        print(f"{'='*70}")
        print(f"Figuras guardadas en: {FIGURES_PATH}")
        
        return self.results


if __name__ == '__main__':
    analyzer = DetailedStationAnalysis()
    results = analyzer.run_analysis()
