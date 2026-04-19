#!/usr/bin/env python3
"""
Imputacion de Datos v3 - Seccion de Analisis de Hidrologia
=========================================================

Version 3: 
- Orden geografico corregido (Peñoncito antes de El Banco)
- Relaciones unidireccionales: aguas arriba -> aguas abajo
- Alternativas de imputacion para El Banco (regresion multiple, combinaciones)
- Comparacion de metodos y seleccion por AIC/RMSE

Autor: Seccion de Analisis de Hidrologia
Fecha: 2026-02-25
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.optimize import curve_fit
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Rutas
DATA_PATH = Path(r"C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\Data\Niveles")
PROCESSED_PATH = DATA_PATH / "01_processed"
ANALYSIS_PATH = DATA_PATH / "02_analysis"
FIGURES_PATH = DATA_PATH / "03_figures"

# Umbrales
COMPLETENESS_THRESHOLD = 85.0
MIN_CORRELATION = 0.70

# Orden corregido: aguas arriba -> aguas abajo
GEOGRAPHIC_ORDER = {
    'Puerto Wilches': 1,
    'Sitio Nuevo': 2,
    'El Contento': 3,
    'Gamarra Aut': 4,
    'La Gloria': 5,
    'Peñoncito': 6,      # CORREGIDO
    'El Banco': 7,       # CORREGIDO
    'Las Aguadas': 8,
    'Las Palomas': 9,
    'Rio Nuevo': 10,
    'Armenia': 11,
    'Coyongal': 12,
    'Barbosa': 13,
    'Magangue': 14,
    'Plato': 15,
    'Tenerife': 16,
    'Calamar': 17,
}


def format_significant(x, n=4):
    """Formatea numero a n cifras significativas."""
    if pd.isna(x):
        return x
    if isinstance(x, (int, np.integer)):
        return int(x)
    return float(f"{x:.{n}g}")


class SpatialImputationV3:
    """Clase para imputacion espacial con orden geografico corregido."""
    
    def __init__(self):
        self.df = None
        self.stations_metadata = None
        self.candidate_stations = []
        self.donor_stations = {}  # Solo aguas arriba
        self.imputation_models = {}
        self.imputed_data = None
        
    def load_data(self):
        """Carga datos procesados y metadatos."""
        print("=" * 70)
        print("IMPUTACION ESPACIAL v3 - SECCION DE ANALISIS DE HIDROLOGIA")
        print("Orden geografico corregido")
        print("=" * 70)
        
        self.df = pd.read_csv(PROCESSED_PATH / "magdalena_levels_long_format.csv")
        self.df['fecha'] = pd.to_datetime(self.df['fecha'])
        
        self.stations_metadata = pd.read_csv(ANALYSIS_PATH / "station_coverage_summary.csv")
        
        print(f"\nDatos cargados: {len(self.df):,} registros")
        print(f"Estaciones: {self.df['estacion'].nunique()}")
        
        return self.df
    
    def identify_candidate_stations(self):
        """Identifica estaciones candidatas."""
        print("\n" + "-" * 70)
        print("IDENTIFICACION DE ESTACIONES CANDIDATAS")
        print("-" * 70)
        
        candidates = self.stations_metadata[
            self.stations_metadata['Completitud_Pct'] >= COMPLETENESS_THRESHOLD
        ].copy()
        
        candidates = candidates.sort_values('Completitud_Pct', ascending=False)
        self.candidate_stations = candidates['Estacion'].tolist()
        
        print(f"\nEstaciones con >= {COMPLETENESS_THRESHOLD}% completitud: {len(candidates)}")
        print("\nLista de estaciones candidatas:")
        for _, row in candidates.iterrows():
            missing = row['Dias_Nulos']
            print(f"  - {row['Estacion']:20s} ({row['Codigo']}): "
                  f"{row['Completitud_Pct']:5.1f}% | {missing:5d} dias faltantes")
        
        return candidates
    
    def find_valid_donors(self):
        """
        Identifica donantes VALIDOS: solo estaciones aguas ARRIBA.
        """
        print("\n" + "-" * 70)
        print("IDENTIFICACION DE ESTACIONES DONANTES VALIDAS")
        print("(Solo aguas arriba -> aguas abajo)")
        print("-" * 70)
        
        # Calcular correlaciones
        pivot_df = self.df.pivot_table(
            index='fecha', 
            columns='estacion', 
            values='nivel_msnm',
            aggfunc='first'
        )
        correlation_matrix = pivot_df.corr(method='pearson')
        
        for station in self.candidate_stations:
            if station not in GEOGRAPHIC_ORDER:
                continue
            
            station_order = GEOGRAPHIC_ORDER[station]
            
            # Buscar estaciones aguas ARRIBA (orden menor)
            upstream_stations = []
            for other_station, other_order in GEOGRAPHIC_ORDER.items():
                if other_station == station:
                    continue
                if other_order < station_order:  # Aguas arriba
                    if other_station in correlation_matrix.columns:
                        corr = correlation_matrix.loc[station, other_station]
                        if not pd.isna(corr) and corr >= MIN_CORRELATION:
                            upstream_stations.append((other_station, corr))
            
            # Ordenar por correlacion
            upstream_stations.sort(key=lambda x: x[1], reverse=True)
            
            if upstream_stations:
                self.donor_stations[station] = upstream_stations
                print(f"\n{station} (posicion {station_order}):")
                for donor, corr in upstream_stations[:3]:
                    print(f"    -> {donor:20s} (r = {corr:.3f}) [aguas arriba]")
            else:
                print(f"\n{station}: Sin donantes aguas arriba con r >= {MIN_CORRELATION}")
        
        return self.donor_stations
    
    def build_imputation_models(self):
        """
        Construye modelos de imputacion para cada estacion candidata.
        Para El Banco: prueba H-H simple, regresion multiple, y promedio ponderado.
        """
        print("\n" + "-" * 70)
        print("CONSTRUCCION DE MODELOS DE IMPUTACION")
        print("-" * 70)
        
        model_comparison = []
        
        for station in self.candidate_stations:
            if station not in self.donor_stations:
                print(f"\n{station}: Sin donantes validos - NO se imputa")
                continue
            
            donors = self.donor_stations[station]
            
            print(f"\n{station}:")
            print("  Evaluando metodos de imputacion...")
            
            # Obtener datos de la estacion target
            target_data = self.df[self.df['estacion'] == station][['fecha', 'nivel_msnm']].copy()
            
            # Metodo 1: H-H simple (mejor donante unico)
            best_donor = donors[0][0]
            hh_model = self._build_hh_model(target_data, station, best_donor)
            
            # Metodo 2: Regresion multiple (si hay 2+ donantes)
            multi_model = None
            if len(donors) >= 2:
                multi_donors = [d[0] for d in donors[:2]]  # Max 2 donantes
                multi_model = self._build_multiple_regression(target_data, station, multi_donors)
            
            # Metodo 3: Promedio ponderado por correlacion
            weighted_model = self._build_weighted_average(target_data, station, donors[:3])
            
            # Comparar modelos y seleccionar el mejor
            models_to_compare = []
            if hh_model:
                models_to_compare.append(('H-H Simple', hh_model))
            if multi_model:
                models_to_compare.append(('Regresion Multiple', multi_model))
            if weighted_model:
                models_to_compare.append(('Promedio Ponderado', weighted_model))
            
            if not models_to_compare:
                print(f"    Ningun modelo convergio")
                continue
            
            # Seleccionar por RMSE de validacion cruzada
            best_model_name, best_model = min(models_to_compare, key=lambda x: x[1]['rmse_cv'])
            
            self.imputation_models[station] = best_model
            
            print(f"    -> Mejor modelo: {best_model_name}")
            print(f"       R2 = {best_model['r2']:.4f}, RMSE-CV = {best_model['rmse_cv']:.4f} m")
            
            # Guardar comparacion
            for name, model in models_to_compare:
                model_comparison.append({
                    'Estacion': station,
                    'Metodo': name,
                    'R2': format_significant(model['r2'], 4),
                    'RMSE_CV': format_significant(model['rmse_cv'], 4),
                    'Donantes': ', '.join(model['donors']),
                    'Seleccionado': 'SI' if name == best_model_name else 'NO'
                })
        
        # Guardar comparacion
        if model_comparison:
            comparison_df = pd.DataFrame(model_comparison)
            comparison_df.to_csv(ANALYSIS_PATH / "imputation_method_comparison.csv", index=False)
            
            print(f"\n{'='*70}")
            print("COMPARACION DE METODOS DE IMPUTACION")
            print(f"{'='*70}")
            print(comparison_df.to_string(index=False))
        
        return self.imputation_models
    
    def _build_hh_model(self, target_data, station, donor):
        """Construye modelo H-H simple (cuadratico)."""
        donor_data = self.df[self.df['estacion'] == donor][['fecha', 'nivel_msnm']].copy()
        
        merged = pd.merge(target_data, donor_data, on='fecha', suffixes=('_target', '_donor'))
        merged = merged.dropna()
        
        if len(merged) < 50:
            return None
        
        x = merged['nivel_msnm_donor'].values
        y = merged['nivel_msnm_target'].values
        
        # Modelo cuadratico
        try:
            popt, _ = curve_fit(lambda x, a, b, c: a*x**2 + b*x + c, x, y)
            y_pred = popt[0]*x**2 + popt[1]*x + popt[2]
            r2 = r2_score(y, y_pred)
            
            # Validacion cruzada simple
            np.random.seed(42)
            mask = np.random.rand(len(x)) < 0.8
            if mask.sum() > 10 and (~mask).sum() > 10:
                x_train, y_train = x[mask], y[mask]
                x_test, y_test = x[~mask], y[~mask]
                popt_cv, _ = curve_fit(lambda x, a, b, c: a*x**2 + b*x + c, x_train, y_train)
                y_pred_cv = popt_cv[0]*x_test**2 + popt_cv[1]*x_test + popt_cv[2]
                rmse_cv = np.sqrt(mean_squared_error(y_test, y_pred_cv))
            else:
                rmse_cv = np.sqrt(mean_squared_error(y, y_pred))
            
            return {
                'type': 'hh_quadratic',
                'donors': [donor],
                'params': popt,
                'r2': r2,
                'rmse_cv': rmse_cv,
                'equation': f"y = {popt[0]:.4f}x^2 + {popt[1]:.4f}x + {popt[2]:.4f}"
            }
        except:
            return None
    
    def _build_multiple_regression(self, target_data, station, donors):
        """Construye regresion multiple con 2 donantes."""
        donor_data_list = []
        for donor in donors:
            dd = self.df[self.df['estacion'] == donor][['fecha', 'nivel_msnm']].copy()
            dd.columns = ['fecha', f'nivel_{donor}']
            donor_data_list.append(dd)
        
        # Merge todos los donantes
        merged = target_data.copy()
        for dd in donor_data_list:
            merged = pd.merge(merged, dd, on='fecha', how='inner')
        
        merged = merged.dropna()
        if len(merged) < 50:
            return None
        
        # Preparar variables
        X_cols = [c for c in merged.columns if c.startswith('nivel_') and c != 'nivel_msnm']
        X = merged[X_cols].values
        y = merged['nivel_msnm'].values
        
        # Agregar terminos cuadraticos
        X_quad = np.column_stack([X, X**2])
        
        try:
            model = LinearRegression()
            model.fit(X_quad, y)
            y_pred = model.predict(X_quad)
            r2 = r2_score(y, y_pred)
            
            # Validacion cruzada
            np.random.seed(42)
            mask = np.random.rand(len(y)) < 0.8
            if mask.sum() > 10 and (~mask).sum() > 10:
                model_cv = LinearRegression()
                model_cv.fit(X_quad[mask], y[mask])
                y_pred_cv = model_cv.predict(X_quad[~mask])
                rmse_cv = np.sqrt(mean_squared_error(y[~mask], y_pred_cv))
            else:
                rmse_cv = np.sqrt(mean_squared_error(y, y_pred))
            
            return {
                'type': 'multiple_regression',
                'donors': donors,
                'model': model,
                'r2': r2,
                'rmse_cv': rmse_cv,
                'coefficients': model.coef_,
                'intercept': model.intercept_
            }
        except:
            return None
    
    def _build_weighted_average(self, target_data, station, donors):
        """Construye modelo de promedio ponderado por correlacion."""
        donor_data_list = []
        weights = []
        
        for donor, corr in donors:
            dd = self.df[self.df['estacion'] == donor][['fecha', 'nivel_msnm']].copy()
            dd.columns = ['fecha', f'nivel_{donor}']
            donor_data_list.append(dd)
            weights.append(corr)
        
        # Normalizar pesos
        weights = np.array(weights)
        weights = weights / weights.sum()
        
        # Merge todos los donantes
        merged = target_data.copy()
        for dd in donor_data_list:
            merged = pd.merge(merged, dd, on='fecha', how='inner')
        
        merged = merged.dropna()
        if len(merged) < 50:
            return None
        
        X_cols = [c for c in merged.columns if c.startswith('nivel_') and c != 'nivel_msnm']
        
        # Calcular promedio ponderado
        X = merged[X_cols].values
        y = merged['nivel_msnm'].values
        
        # Ajuste lineal del promedio ponderado
        weighted_pred = np.average(X, axis=1, weights=weights)
        
        # Ajuste lineal simple para calibrar
        slope, intercept, r_value, p_value, std_err = stats.linregress(weighted_pred, y)
        y_pred = slope * weighted_pred + intercept
        r2 = r_value**2
        
        # Validacion cruzada
        np.random.seed(42)
        mask = np.random.rand(len(y)) < 0.8
        if mask.sum() > 10 and (~mask).sum() > 10:
            wp_train = np.average(X[mask], axis=1, weights=weights)
            slope_cv, intercept_cv, _, _, _ = stats.linregress(wp_train, y[mask])
            wp_test = np.average(X[~mask], axis=1, weights=weights)
            y_pred_cv = slope_cv * wp_test + intercept_cv
            rmse_cv = np.sqrt(mean_squared_error(y[~mask], y_pred_cv))
        else:
            rmse_cv = np.sqrt(mean_squared_error(y, y_pred))
        
        return {
            'type': 'weighted_average',
            'donors': [d[0] for d in donors],
            'weights': weights,
            'slope': slope,
            'intercept': intercept,
            'r2': r2,
            'rmse_cv': rmse_cv
        }
    
    def plot_models(self):
        """Visualiza los modelos seleccionados."""
        print("\n" + "-" * 70)
        print("VISUALIZACION DE MODELOS DE IMPUTACION")
        print("-" * 70)
        
        n_models = len(self.imputation_models)
        if n_models == 0:
            print("No hay modelos para visualizar")
            return
        
        fig, axes = plt.subplots(2, n_models, figsize=(6*n_models, 10))
        if n_models == 1:
            axes = axes.reshape(-1, 1)
        
        for idx, (station, model) in enumerate(self.imputation_models.items()):
            # Obtener datos
            target_data = self.df[self.df['estacion'] == station][['fecha', 'nivel_msnm']].copy()
            
            # Panel superior: scatter con modelo
            ax1 = axes[0, idx]
            
            if model['type'] == 'hh_quadratic':
                donor = model['donors'][0]
                donor_data = self.df[self.df['estacion'] == donor][['fecha', 'nivel_msnm']].copy()
                merged = pd.merge(target_data, donor_data, on='fecha', suffixes=('_target', '_donor'))
                merged = merged.dropna()
                
                x = merged['nivel_msnm_donor'].values
                y = merged['nivel_msnm_target'].values
                
                ax1.scatter(x, y, alpha=0.3, s=10, color='#2E5EAA', edgecolors='none')
                
                # Linea del modelo
                x_line = np.linspace(x.min(), x.max(), 100)
                popt = model['params']
                y_line = popt[0]*x_line**2 + popt[1]*x_line + popt[2]
                ax1.plot(x_line, y_line, 'r-', linewidth=2, label=model['equation'])
                
                ax1.set_xlabel(f'{donor} (m.s.n.m.)', fontsize=10)
                
            elif model['type'] in ['multiple_regression', 'weighted_average']:
                # Para modelos multivariados, mostrar prediccion vs observado
                # (simplificado para visualizacion)
                ax1.text(0.5, 0.5, f"Modelo: {model['type']}\n"
                                f"Donantes: {', '.join(model['donors'])}\n"
                                f"R2 = {model['r2']:.4f}",
                        ha='center', va='center', transform=ax1.transAxes,
                        fontsize=10, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
                ax1.set_xlabel('Multiple donantes', fontsize=10)
            
            ax1.set_ylabel(f'{station} (m.s.n.m.)', fontsize=10)
            ax1.set_title(f'{station}\n{model["type"]}', fontsize=11, fontweight='bold')
            ax1.legend(loc='best', fontsize=8)
            ax1.grid(True, alpha=0.3)
            
            # Panel inferior: serie temporal con imputados
            ax2 = axes[1, idx]
            ax2.plot(target_data['fecha'], target_data['nivel_msnm'], 
                    'o-', color='#2E5EAA', markersize=1, linewidth=0.5, alpha=0.7)
            ax2.set_xlabel('Fecha', fontsize=10)
            ax2.set_ylabel('Cota (m.s.n.m.)', fontsize=10)
            ax2.set_title(f'Serie temporal - {station}', fontsize=11, fontweight='bold')
            ax2.grid(True, alpha=0.3)
        
        plt.suptitle('Modelos de Imputacion Seleccionados por Estacion', 
                    fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        output_file = FIGURES_PATH / "imputation" / "imputation_models_v3.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"\nFigura guardada: {output_file}")
        plt.close()
    
    def run_imputation(self):
        """Ejecuta el flujo completo de imputacion."""
        self.load_data()
        self.identify_candidate_stations()
        self.find_valid_donors()
        self.build_imputation_models()
        self.plot_models()
        
        print("\n" + "=" * 70)
        print("PROCESO DE IMPUTACION v3 FINALIZADO")
        print("=" * 70)
        
        return self.imputation_models


if __name__ == '__main__':
    imputer = SpatialImputationV3()
    results = imputer.run_imputation()
