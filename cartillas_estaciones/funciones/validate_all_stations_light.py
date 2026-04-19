#!/usr/bin/env python3
"""
Validacion LIGHT para TODAS las estaciones - Rio Magdalena
Detecta problemas visuales: outliers, saltos en percentiles, desviaciones
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from typing import Dict, List
import warnings
warnings.filterwarnings('ignore')


class LightValidator:
    """Validador ligero para detectar problemas visuales en todas las estaciones."""
    
    def __init__(self, data_path: str = './datos/processed/'):
        self.data_path = data_path
        self.df = None
        self.results = {}
        self.load_data()
        
    def load_data(self):
        """Carga datos de todas las estaciones."""
        print(f"Cargando datos...")
        self.df = pd.read_csv(f'{self.data_path}Datos_Imputados_v3.csv')
        self.df['date'] = pd.to_datetime(self.df['date'])
        self.stations = sorted(self.df['station'].unique())
        print(f"OK {len(self.df):,} registros de {len(self.stations)} estaciones")
        
    def check_outliers_by_percentiles(self, station: str) -> Dict:
        """
        Check 1: Detecta outliers usando IQR modificado.
        Detecta valores que caen fuera de rangos razonables para la estacion.
        """
        df_stat = self.df[self.df['station'] == station]['level'].dropna()
        
        if len(df_stat) < 100:
            return {'status': 'INSUFFICIENT_DATA', 'n_outliers': 0}
        
        Q1 = df_stat.quantile(0.25)
        Q3 = df_stat.quantile(0.75)
        IQR = Q3 - Q1
        
        # Limites amplios (3*IQR para capturar valores extremos)
        lower_bound = Q1 - 3 * IQR
        upper_bound = Q3 + 3 * IQR
        
        outliers = df_stat[(df_stat < lower_bound) | (df_stat > upper_bound)]
        
        # Tambien verificar percentiles extremos
        p01 = df_stat.quantile(0.01)
        p99 = df_stat.quantile(0.99)
        
        # Outliers severos: fuera de [p01 - 2*IQR, p99 + 2*IQR]
        severe_lower = p01 - 2 * IQR
        severe_upper = p99 + 2 * IQR
        severe_outliers = df_stat[(df_stat < severe_lower) | (df_stat > severe_upper)]
        
        status = 'OK'
        if len(severe_outliers) > 5:
            status = 'CRITICAL'
        elif len(outliers) > 10:
            status = 'WARNING'
        elif len(outliers) > 0:
            status = 'OK'
            
        return {
            'check_name': 'Outliers_Percentiles',
            'status': status,
            'n_outliers': len(outliers),
            'n_severe': len(severe_outliers),
            'lower_bound': lower_bound,
            'upper_bound': upper_bound,
            'min_val': df_stat.min(),
            'max_val': df_stat.max(),
            'p01': p01,
            'p99': p99
        }
    
    def check_duration_curve_jumps(self, station: str) -> Dict:
        """
        Check 2: Detecta saltos artificiales en la curva de duracion.
        Similar al problema visto en Armenia: picos/valles en percentiles.
        """
        df_stat = self.df[self.df['station'] == station]['level'].dropna().sort_values()
        
        if len(df_stat) < 100:
            return {'status': 'INSUFFICIENT_DATA', 'max_jump': 0}
        
        n = len(df_stat)
        
        # Calcular diferencias entre percentiles consecutivos
        diffs = np.diff(df_stat.values)
        
        # Detectar saltos grandes (diferencias anomalas)
        median_diff = np.median(np.abs(diffs))
        mad_diff = np.median(np.abs(diffs - np.median(diffs)))
        
        # Umbral: diferencia > 5 * MAD
        threshold = 5 * mad_diff if mad_diff > 0 else median_diff * 3
        
        large_jumps = np.where(np.abs(diffs) > threshold)[0]
        
        # Verificar especificamente en extremos (donde suele haber problemas)
        lower_10pct = int(n * 0.1)
        upper_10pct = int(n * 0.9)
        
        jumps_lower = [i for i in large_jumps if i < lower_10pct]
        jumps_upper = [i for i in large_jumps if i > upper_10pct]
        
        # Calcular el salto maximo
        max_jump = np.max(np.abs(diffs)) if len(diffs) > 0 else 0
        max_jump_pct = max_jump / median_diff if median_diff > 0 else 0
        
        status = 'OK'
        if len(jumps_lower) > 0 or len(jumps_upper) > 0:
            status = 'CRITICAL'
        elif len(large_jumps) > 5:
            status = 'WARNING'
        
        return {
            'check_name': 'Duration_Curve_Jumps',
            'status': status,
            'n_jumps': len(large_jumps),
            'jumps_lower_pct': len(jumps_lower),
            'jumps_upper_pct': len(jumps_upper),
            'max_jump': max_jump,
            'max_jump_ratio': max_jump_pct,
            'threshold': threshold
        }
    
    def check_distribution_fit(self, station: str) -> Dict:
        """
        Check 3: Verifica calidad del ajuste de distribucion (como el Q-Q plot de Armenia).
        Detecta desviaciones sistematicas de la distribucion teorica.
        """
        from scipy.stats import weibull_min, lognorm, gamma, norm
        
        data = self.df[self.df['station'] == station]['level'].dropna()
        
        if len(data) < 100:
            return {'status': 'INSUFFICIENT_DATA', 'ks_stat': 0}
        
        # Probar Weibull (la mas comun en hidrologia)
        try:
            params = weibull_min.fit(data)
            ks_stat, ks_pvalue = stats.kstest(data, lambda x: weibull_min.cdf(x, *params))
            
            # Calcular correlacion en Q-Q plot (simplificado)
            sorted_data = np.sort(data)
            n = len(sorted_data)
            p = np.arange(1, n + 1) / (n + 1)
            theoretical = weibull_min.ppf(p, *params)
            
            # Correlacion entre cuantiles teoricos y observados
            qq_corr = np.corrcoef(theoretical, sorted_data)[0, 1]
            
        except:
            ks_stat = 1
            ks_pvalue = 0
            qq_corr = 0
        
        status = 'OK'
        if ks_pvalue < 0.001 or qq_corr < 0.9:
            status = 'CRITICAL'
        elif ks_pvalue < 0.05 or qq_corr < 0.95:
            status = 'WARNING'
        
        return {
            'check_name': 'Distribution_Fit',
            'status': status,
            'ks_statistic': ks_stat,
            'ks_pvalue': ks_pvalue,
            'qq_correlation': qq_corr,
            'best_dist': 'Weibull'
        }
    
    def check_monthly_ranges(self, station: str) -> Dict:
        """
        Check 4: Verifica que cada mes tenga rangos razonables.
        Detecta meses con valores atipicos comparados con el patron historico.
        """
        df_stat = self.df[self.df['station'] == station].copy()
        df_stat = df_stat.dropna(subset=['level', 'month'])
        
        if len(df_stat) < 100:
            return {'status': 'INSUFFICIENT_DATA', 'anomalous_months': []}
        
        # Calcular estadisticas por mes
        monthly_stats = df_stat.groupby('month')['level'].agg(['mean', 'std', 'min', 'max']).reset_index()
        
        # Verificar si hay meses con rangos muy diferentes
        overall_mean = df_stat['level'].mean()
        overall_std = df_stat['level'].std()
        
        anomalous_months = []
        
        for _, row in monthly_stats.iterrows():
            month = int(row['month'])
            month_mean = row['mean']
            month_std = row['std']
            
            # Detectar meses con medias muy diferentes (> 2 std del promedio general)
            if abs(month_mean - overall_mean) > 2 * overall_std:
                anomalous_months.append({
                    'month': month,
                    'mean': month_mean,
                    'std': month_std,
                    'deviation': abs(month_mean - overall_mean) / overall_std
                })
        
        status = 'OK'
        if len(anomalous_months) > 3:
            status = 'CRITICAL'
        elif len(anomalous_months) > 0:
            status = 'WARNING'
        
        return {
            'check_name': 'Monthly_Ranges',
            'status': status,
            'n_anomalous_months': len(anomalous_months),
            'anomalous_months': anomalous_months
        }
    
    def validate_station(self, station: str) -> Dict:
        """Ejecuta todos los checks para una estacion."""
        print(f"\nValidando: {station}")
        
        checks = {
            'outliers': self.check_outliers_by_percentiles(station),
            'duration_jumps': self.check_duration_curve_jumps(station),
            'distribution': self.check_distribution_fit(station),
            'monthly': self.check_monthly_ranges(station)
        }
        
        # Determinar estado general
        statuses = [c['status'] for c in checks.values() if c['status'] != 'INSUFFICIENT_DATA']
        
        if 'CRITICAL' in statuses:
            overall = 'CRITICAL'
        elif 'WARNING' in statuses:
            overall = 'WARNING'
        else:
            overall = 'OK'
        
        result = {
            'station': station,
            'overall_status': overall,
            'checks': checks,
            'n_critical': sum(1 for s in statuses if s == 'CRITICAL'),
            'n_warning': sum(1 for s in statuses if s == 'WARNING'),
            'n_ok': sum(1 for s in statuses if s == 'OK')
        }
        
        print(f"  Estado: {overall}")
        print(f"  Checks: CRITICAL={result['n_critical']}, WARNING={result['n_warning']}, OK={result['n_ok']}")
        
        return result
    
    def validate_all(self) -> List[Dict]:
        """Valida todas las estaciones."""
        print("="*70)
        print("VALIDACION LIGHT - TODAS LAS ESTACIONES")
        print("="*70)
        
        results = []
        for station in self.stations:
            result = self.validate_station(station)
            results.append(result)
            self.results[station] = result
        
        return results
    
    def generate_report(self, results: List[Dict], output_path: str = './resultados/'):
        """Genera reporte en Markdown."""
        
        critical_stations = [r for r in results if r['overall_status'] == 'CRITICAL']
        warning_stations = [r for r in results if r['overall_status'] == 'WARNING']
        ok_stations = [r for r in results if r['overall_status'] == 'OK']
        
        md = f"""# Reporte de Validacion LIGHT - Todas las Estaciones

## Resumen Ejecutivo

| Estado | N Estaciones | Lista |
|--------|--------------|-------|
| CRITICAL | {len(critical_stations)} | {', '.join([r['station'] for r in critical_stations]) if critical_stations else 'Ninguna'} |
| WARNING | {len(warning_stations)} | {', '.join([r['station'] for r in warning_stations]) if warning_stations else 'Ninguna'} |
| OK | {len(ok_stations)} | {', '.join([r['station'] for r in ok_stations]) if ok_stations else 'Ninguna'} |

## Detalle por Estacion

"""
        
        for r in sorted(results, key=lambda x: (0 if x['overall_status']=='CRITICAL' else 1 if x['overall_status']=='WARNING' else 2, x['station'])):
            md += f"""### {r['station']} - {r['overall_status']}

| Check | Estado | Detalle |
|-------|--------|---------|
"""
            for check_name, check_data in r['checks'].items():
                if check_data['status'] == 'INSUFFICIENT_DATA':
                    detail = 'Datos insuficientes'
                elif check_name == 'outliers':
                    detail = f"{check_data['n_outliers']} outliers ({check_data['n_severe']} severos)"
                elif check_name == 'duration_jumps':
                    detail = f"{check_data['n_jumps']} saltos, max={check_data['max_jump']:.2f}m"
                elif check_name == 'distribution':
                    detail = f"KS p={check_data['ks_pvalue']:.4f}, QQ corr={check_data['qq_correlation']:.3f}"
                elif check_name == 'monthly':
                    detail = f"{check_data['n_anomalous_months']} meses anomalos"
                else:
                    detail = ''
                
                md += f"| {check_name} | {check_data['status']} | {detail} |\n"
            
            md += "\n"
        
        md += f"""
## Checks Realizados

1. **Outliers_Percentiles**: Detecta valores fuera de rango usando IQR
2. **Duration_Curve_Jumps**: Detecta saltos en curva de duracion (como Armenia)
3. **Distribution_Fit**: Verifica calidad del ajuste Weibull (Q-Q plot)
4. **Monthly_Ranges**: Detecta meses con comportamiento atipico

## Recomendaciones

"""
        
        if critical_stations:
            md += "### Revisar URGENTEMENTE:\n"
            for r in critical_stations:
                md += f"- **{r['station']}**: {r['n_critical']} checks CRITICAL\n"
            md += "\n"
        
        if warning_stations:
            md += "### Revisar cuando sea posible:\n"
            for r in warning_stations:
                md += f"- **{r['station']}**: {r['n_warning']} checks WARNING\n"
            md += "\n"
        
        # Guardar
        output_file = f'{output_path}validacion_light_todas_estaciones.md'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(md)
        
        print(f"\nReporte guardado: {output_file}")
        return output_file


def main():
    validator = LightValidator()
    results = validator.validate_all()
    validator.generate_report(results)
    
    # Resumen final
    critical = len([r for r in results if r['overall_status'] == 'CRITICAL'])
    warning = len([r for r in results if r['overall_status'] == 'WARNING'])
    ok = len([r for r in results if r['overall_status'] == 'OK'])
    
    print("\n" + "="*70)
    print("RESUMEN FINAL")
    print("="*70)
    print(f"CRITICAL: {critical} estaciones")
    print(f"WARNING:  {warning} estaciones")
    print(f"OK:       {ok} estaciones")
    print("="*70)


if __name__ == '__main__':
    main()
