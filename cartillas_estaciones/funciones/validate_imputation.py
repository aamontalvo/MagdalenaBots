"""
Sistema de Validacion de Imputacion de Datos - Rio Magdalena
Detecta problemas en series temporales imputadas usando 3 filtros hidrologicos

Filtros:
1. Velocidad de cambio hidrologica (comparada con percentiles historicos)
2. Coherencia espacial (correlacion con estaciones vecinas)
3. Continuidad en fronteras (saltos observado->imputado)
"""

import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')


class ImputationValidator:
    """Clase para validar la calidad de datos imputados en estaciones hidrometricas."""
    
    def __init__(self, data_path: str = './datos/processed/'):
        """
        Inicializa el validador cargando los datos.
        
        Parameters:
        -----------
        data_path : str
            Ruta a los datos procesados (Datos_Imputados_v3.csv)
        """
        self.data_path = data_path
        self.df = None
        self.df_observed_only = None
        self.station_stats = {}
        self.load_data()
        
    def load_data(self):
        """Carga los datos imputados y calcula estadisticas base."""
        print(f"Cargando datos desde: {self.data_path}Datos_Imputados_v3.csv")
        self.df = pd.read_csv(f'{self.data_path}Datos_Imputados_v3.csv')
        self.df['date'] = pd.to_datetime(self.df['date'])
        
        # Detectar cuales son datos observados vs imputados
        # Los datos imputados vienen de los archivos originales (water_level_measurements)
        # Los observados son los que no tienen flag de imputacion
        # Asumimos que hay una columna 'imputed' o inferimos de los datos
        
        if 'imputed' not in self.df.columns:
            # Si no hay columna explicita, inferimos que todos los datos validos son observados
            # y marcamos como imputados aquellos que aparecen en los gaps
            self.df['imputed'] = False
        
        # Para el analisis, necesitamos solo datos observados para calibrar los umbrales
        self.df_observed_only = self.df[self.df['imputed'] == False].copy() if 'imputed' in self.df.columns else self.df.copy()
        
        print(f"✓ Datos cargados: {len(self.df):,} registros totales")
        print(f"✓ Estaciones disponibles: {self.df['station'].nunique()}")
        
    def calculate_station_statistics(self, station: str) -> Dict:
        """
        Calcula estadisticas historicas de una estacion para establecer umbrales.
        
        Returns:
        --------
        Dict con estadisticas de la estacion
        """
        if station in self.station_stats:
            return self.station_stats[station]
        
        df_station = self.df[self.df['station'] == station].copy()
        
        if len(df_station) == 0:
            return None
        
        # Calcular cambios diarios (velocidad de variacion)
        df_station = df_station.sort_values('date')
        df_station['daily_change'] = df_station['level'].diff().abs()
        
        # Estadisticas de cambios diarios (solo datos observados o todos si no hay flag)
        daily_changes = df_station['daily_change'].dropna()
        
        stats_dict = {
            'station': station,
            'n_total': len(df_station),
            'n_valid': df_station['level'].notna().sum(),
            'mean_level': df_station['level'].mean(),
            'std_level': df_station['level'].std(),
            'min_level': df_station['level'].min(),
            'max_level': df_station['level'].max(),
            'p95_change': daily_changes.quantile(0.95),
            'p99_change': daily_changes.quantile(0.99),
            'p995_change': daily_changes.quantile(0.995),
            'max_change': daily_changes.max(),
            'mean_change': daily_changes.mean(),
            'std_change': daily_changes.std(),
            'year_start': df_station['year'].min(),
            'year_end': df_station['year'].max(),
        }
        
        self.station_stats[station] = stats_dict
        return stats_dict
    
    def detect_imputed_gaps(self, station: str) -> pd.DataFrame:
        """
        Detecta periodos imputados basandose en discontinuidades en los datos.
        
        Returns:
        --------
        DataFrame con periodos imputados detectados
        """
        df_station = self.df[self.df['station'] == station].copy()
        df_station = df_station.sort_values('date').reset_index(drop=True)
        
        # Calcular diferencias de tiempo
        df_station['time_diff'] = df_station['date'].diff().dt.days
        
        # Detectar gaps (diferencias > 1 dia)
        gaps = df_station[df_station['time_diff'] > 1].copy()
        
        # Tambien detectar valores que parecen imputados por patron
        # (esto es una heuristica simple)
        
        gap_list = []
        for idx, row in gaps.iterrows():
            gap_start = df_station.loc[idx - 1, 'date'] if idx > 0 else None
            gap_end = row['date']
            gap_duration = row['time_diff']
            
            if gap_start is not None:
                gap_list.append({
                    'station': station,
                    'gap_start': gap_start,
                    'gap_end': gap_end,
                    'duration_days': gap_duration,
                    'value_before': df_station.loc[idx - 1, 'level'],
                    'value_after': row['level'],
                })
        
        return pd.DataFrame(gap_list)
    
    def validate_velocity_filter(self, station: str, threshold_multiplier: float = 2.0) -> pd.DataFrame:
        """
        Filtro 1: Valida velocidad de cambio hidrologica.
        
        Detecta cambios diarios que exceden multiplicador * percentil 99.5 historico.
        
        Parameters:
        -----------
        station : str
            Nombre de la estacion
        threshold_multiplier : float
            Multiplicador del percentil 99.5 para establecer umbral critico
            
        Returns:
        --------
        DataFrame con flags de velocidad anomala
        """
        df_station = self.df[self.df['station'] == station].copy()
        df_station = df_station.sort_values('date')
        
        stats = self.calculate_station_statistics(station)
        if stats is None:
            return pd.DataFrame()
        
        # Calcular cambios diarios
        df_station['daily_change'] = df_station['level'].diff().abs()
        df_station['change_rate'] = df_station['daily_change'] / df_station['level'].shift(1).abs()
        
        # Umbrales
        threshold_warning = stats['p99_change']
        threshold_critical = stats['p995_change'] * threshold_multiplier
        
        # Flags
        flags = []
        for idx, row in df_station.iterrows():
            if pd.notna(row['daily_change']):
                severity = None
                if row['daily_change'] > threshold_critical:
                    severity = 'CRITICAL'
                elif row['daily_change'] > threshold_warning:
                    severity = 'WARNING'
                
                if severity:
                    flags.append({
                        'station': station,
                        'date': row['date'],
                        'level': row['level'],
                        'daily_change_m': row['daily_change'],
                        'threshold_warning': threshold_warning,
                        'threshold_critical': threshold_critical,
                        'severity': severity,
                        'flag_type': 'VELOCITY',
                        'description': f'Cambio diario de {row["daily_change"]:.3f}m excede umbral {severity}'
                    })
        
        return pd.DataFrame(flags)
    
    def validate_spatial_coherence(self, station: str, neighbor_stations: List[str], 
                                   window_days: int = 3, min_correlation: float = 0.7) -> pd.DataFrame:
        """
        Filtro 2: Valida coherencia espacial con estaciones vecinas.
        
        Calcula correlacion en ventana movil y detecta inconsistencias.
        
        Parameters:
        -----------
        station : str
            Estacion objetivo
        neighbor_stations : List[str]
            Lista de estaciones vecinas para comparar
        window_days : int
            Tamaño de ventana para correlacion (dias)
        min_correlation : float
            Correlacion minima aceptable
            
        Returns:
        --------
        DataFrame con flags de incoherencia espacial
        """
        df_target = self.df[self.df['station'] == station].copy()
        df_target = df_target.set_index('date')['level']
        
        flags = []
        
        for neighbor in neighbor_stations:
            if neighbor == station:
                continue
                
            df_neighbor = self.df[self.df['station'] == neighbor].copy()
            if len(df_neighbor) == 0:
                continue
                
            df_neighbor = df_neighbor.set_index('date')['level']
            
            # Reindexar para alinear fechas
            common_dates = df_target.index.intersection(df_neighbor.index)
            
            if len(common_dates) < window_days * 2:
                continue
            
            target_aligned = df_target.loc[common_dates]
            neighbor_aligned = df_neighbor.loc[common_dates]
            
            # Calcular correlacion en ventana movil
            for i in range(window_days, len(common_dates) - window_days):
                window_dates = common_dates[i-window_days:i+window_days]
                target_window = target_aligned.loc[window_dates]
                neighbor_window = neighbor_aligned.loc[window_dates]
                
                # Solo evaluar si hay suficientes datos
                if target_window.notna().sum() < window_days or neighbor_window.notna().sum() < window_days:
                    continue
                
                # Calcular correlacion
                corr = target_window.corr(neighbor_window)
                
                if pd.notna(corr) and corr < min_correlation:
                    center_date = common_dates[i]
                    flags.append({
                        'station': station,
                        'date': center_date,
                        'level': target_aligned.loc[center_date],
                        'neighbor_station': neighbor,
                        'correlation': corr,
                        'min_correlation': min_correlation,
                        'severity': 'WARNING' if corr < min_correlation else 'OK',
                        'flag_type': 'SPATIAL',
                        'description': f'Correlacion {corr:.3f} con {neighbor} < {min_correlation}'
                    })
        
        return pd.DataFrame(flags)
    
    def validate_boundary_continuity(self, station: str, max_std_multiplier: float = 3.0) -> pd.DataFrame:
        """
        Filtro 3: Valida continuidad en fronteras de gaps.
        
        Detecta saltos bruscos en los limites de periodos imputados.
        
        Parameters:
        -----------
        station : str
            Nombre de la estacion
        max_std_multiplier : float
            Multiplicador de desviacion estandar para detectar saltos
            
        Returns:
        --------
        DataFrame con flags de discontinuidad en fronteras
        """
        df_station = self.df[self.df['station'] == station].copy()
        df_station = df_station.sort_values('date').reset_index(drop=True)
        
        stats = self.calculate_station_statistics(station)
        if stats is None:
            return pd.DataFrame()
        
        # Detectar gaps (dias faltantes)
        df_station['time_diff'] = df_station['date'].diff().dt.days
        df_station['is_gap_start'] = df_station['time_diff'] > 1
        
        # Calcular variabilidad local (usando ventana de 7 dias)
        df_station['local_std'] = df_station['level'].rolling(window=7, center=True).std()
        
        flags = []
        
        for idx, row in df_station.iterrows():
            if row['is_gap_start'] and idx > 0:
                # Gap detectado: comparar valor anterior con actual
                val_pre = df_station.loc[idx - 1, 'level']
                val_current = row['level']
                
                if pd.notna(val_pre) and pd.notna(val_current):
                    jump = abs(val_current - val_pre)
                    
                    # Variabilidad local antes del gap
                    local_std = df_station.loc[max(0, idx-7):idx-1, 'level'].std()
                    if pd.notna(local_std) and local_std > 0:
                        jump_relative = jump / local_std
                    else:
                        jump_relative = jump / stats['std_level'] if stats['std_level'] > 0 else 0
                    
                    if jump_relative > max_std_multiplier:
                        flags.append({
                            'station': station,
                            'date': row['date'],
                            'level': val_current,
                            'previous_level': val_pre,
                            'jump_m': jump,
                            'local_std': local_std,
                            'jump_relative': jump_relative,
                            'severity': 'CRITICAL' if jump_relative > 5 else 'WARNING',
                            'flag_type': 'BOUNDARY',
                            'description': f'Salto de {jump:.3f}m ({jump_relative:.1f}σ) al inicio de gap'
                        })
        
        return pd.DataFrame(flags)
    
    def validate_station(self, station: str, neighbor_stations: List[str] = None) -> Dict:
        """
        Ejecuta todos los filtros de validacion para una estacion.
        
        Parameters:
        -----------
        station : str
            Nombre de la estacion
        neighbor_stations : List[str]
            Estaciones vecinas para validacion espacial (opcional)
            
        Returns:
        --------
        Dict con resultados de validacion
        """
        print(f"\n{'='*60}")
        print(f"VALIDANDO ESTACION: {station}")
        print(f"{'='*60}")
        
        # Estadisticas base
        stats = self.calculate_station_statistics(station)
        print(f"\nEstadisticas base:")
        print(f"  - Registros: {stats['n_valid']:,} / {stats['n_total']:,}")
        print(f"  - Periodo: {stats['year_start']:.0f}-{stats['year_end']:.0f}")
        print(f"  - Rango: {stats['min_level']:.2f} - {stats['max_level']:.2f} m")
        print(f"  - Cambio max historico: {stats['max_change']:.3f} m/dia")
        
        # Filtro 1: Velocidad
        print(f"\n[Filtro 1] Validando velocidad de cambio...")
        velocity_flags = self.validate_velocity_filter(station)
        print(f"  - Flags detectados: {len(velocity_flags)}")
        if len(velocity_flags) > 0:
            critical = len(velocity_flags[velocity_flags['severity'] == 'CRITICAL'])
            print(f"    CRITICAL: {critical}, WARNING: {len(velocity_flags) - critical}")
        
        # Filtro 2: Coherencia espacial
        spatial_flags = pd.DataFrame()
        if neighbor_stations:
            print(f"\n[Filtro 2] Validando coherencia espacial...")
            spatial_flags = self.validate_spatial_coherence(station, neighbor_stations)
            print(f"  - Flags detectados: {len(spatial_flags)}")
        
        # Filtro 3: Fronteras
        print(f"\n[Filtro 3] Validando continuidad de fronteras...")
        boundary_flags = self.validate_boundary_continuity(station)
        print(f"  - Flags detectados: {len(boundary_flags)}")
        
        # Consolidar resultados
        all_flags = pd.concat([velocity_flags, spatial_flags, boundary_flags], ignore_index=True)
        
        # Detectar periodos problemáticos
        problem_periods = self._identify_problem_periods(all_flags)
        
        results = {
            'station': station,
            'statistics': stats,
            'total_flags': len(all_flags),
            'critical_flags': len(all_flags[all_flags['severity'] == 'CRITICAL']) if len(all_flags) > 0 else 0,
            'warning_flags': len(all_flags[all_flags['severity'] == 'WARNING']) if len(all_flags) > 0 else 0,
            'velocity_flags': velocity_flags,
            'spatial_flags': spatial_flags,
            'boundary_flags': boundary_flags,
            'all_flags': all_flags,
            'problem_periods': problem_periods,
            'assessment': self._generate_assessment(len(all_flags), stats['n_valid'])
        }
        
        print(f"\n{'='*60}")
        print(f"RESUMEN: {results['assessment']}")
        print(f"  Total flags: {results['total_flags']} (CRITICAL: {results['critical_flags']}, WARNING: {results['warning_flags']})")
        print(f"{'='*60}")
        
        return results
    
    def _identify_problem_periods(self, flags_df: pd.DataFrame) -> pd.DataFrame:
        """Identifica periodos con problemas agrupando flags consecutivos."""
        if len(flags_df) == 0:
            return pd.DataFrame()
        
        flags_df = flags_df.sort_values('date')
        
        # Agrupar flags cercanos (dentro de 30 dias)
        periods = []
        current_period = {
            'start_date': flags_df.iloc[0]['date'],
            'end_date': flags_df.iloc[0]['date'],
            'flags': [flags_df.iloc[0].to_dict()]
        }
        
        for idx in range(1, len(flags_df)):
            row = flags_df.iloc[idx]
            days_diff = (row['date'] - current_period['end_date']).days
            
            if days_diff <= 30:  # Mismo periodo
                current_period['end_date'] = row['date']
                current_period['flags'].append(row.to_dict())
            else:  # Nuevo periodo
                periods.append(self._summarize_period(current_period))
                current_period = {
                    'start_date': row['date'],
                    'end_date': row['date'],
                    'flags': [row.to_dict()]
                }
        
        periods.append(self._summarize_period(current_period))
        
        return pd.DataFrame(periods)
    
    def _summarize_period(self, period: Dict) -> Dict:
        """Resume un periodo problemático."""
        flags = period['flags']
        flag_types = [f['flag_type'] for f in flags]
        severities = [f['severity'] for f in flags]
        
        return {
            'start_date': period['start_date'],
            'end_date': period['end_date'],
            'duration_days': (period['end_date'] - period['start_date']).days + 1,
            'n_flags': len(flags),
            'flag_types': ', '.join(set(flag_types)),
            'max_severity': 'CRITICAL' if 'CRITICAL' in severities else 'WARNING',
            'description': self._generate_period_description(flags)
        }
    
    def _generate_period_description(self, flags: List[Dict]) -> str:
        """Genera descripción del periodo problemático."""
        descriptions = []
        
        # Agrupar por tipo
        velocity_flags = [f for f in flags if f['flag_type'] == 'VELOCITY']
        boundary_flags = [f for f in flags if f['flag_type'] == 'BOUNDARY']
        spatial_flags = [f for f in flags if f['flag_type'] == 'SPATIAL']
        
        if velocity_flags:
            max_change = max([f['daily_change_m'] for f in velocity_flags])
            descriptions.append(f"Cambios bruscos de hasta {max_change:.2f}m")
        
        if boundary_flags:
            max_jump = max([f['jump_m'] for f in boundary_flags])
            descriptions.append(f"Saltos en fronteras de hasta {max_jump:.2f}m")
        
        if spatial_flags:
            min_corr = min([f['correlation'] for f in spatial_flags])
            descriptions.append(f"Baja correlacion espacial ({min_corr:.2f})")
        
        return '; '.join(descriptions)
    
    def _generate_assessment(self, n_flags: int, n_data: int) -> str:
        """Genera evaluación general de la estación."""
        if n_flags == 0:
            return "✓ SERIE VALIDA - Sin problemas detectados"
        
        flag_ratio = n_flags / n_data if n_data > 0 else 0
        
        if flag_ratio > 0.1:
            return "✗ SERIE CRITICA - Requiere revision completa"
        elif flag_ratio > 0.05:
            return "⚠ SERIE DUDOSA - Revisar periodos marcados"
        else:
            return "⚠ REVISION MENOR - Algunos flags aislados"


def generate_validation_report(results_list: List[Dict], output_path: str = './resultados/'):
    """
    Genera reporte en Markdown con los resultados de validacion.
    
    Parameters:
    -----------
    results_list : List[Dict]
        Lista de resultados de validate_station()
    output_path : str
        Ruta donde guardar el reporte
    """
    
    md_content = """# Reporte de Validacion de Imputacion - Rio Magdalena

## Resumen Ejecutivo

Este reporte documenta los problemas detectados en las series temporales imputadas utilizando tres filtros hidrologicos:

1. **Velocidad de Cambio**: Detecta cambios diarios anomalos
2. **Coherencia Espacial**: Valida correlacion con estaciones vecinas
3. **Continuidad de Fronteras**: Detecta saltos en limites de gaps

---

## Tabla Resumen por Estacion

| Estacion | Registros | Flags Total | Critical | Warning | Evaluacion |
|----------|-----------|-------------|----------|---------|------------|
"""
    
    for result in results_list:
        stats = result['statistics']
        md_content += f"| {result['station']} | {stats['n_valid']:,} | {result['total_flags']} | "
        md_content += f"{result['critical_flags']} | {result['warning_flags']} | {result['assessment']} |\n"
    
    md_content += """
---

## Detalle de Problemas por Estacion

"""
    
    # Detalle por estacion
    for result in results_list:
        station = result['station']
        md_content += f"### {station}\n\n"
        md_content += f"**Evaluacion:** {result['assessment']}\n\n"
        md_content += f"**Estadisticas:** {result['statistics']['n_valid']:,} registros | "
        md_content += f"Periodo: {result['statistics']['year_start']:.0f}-{result['statistics']['year_end']:.0f}\n\n"
        
        if len(result['problem_periods']) > 0:
            md_content += "**Periodos Problematicos Detectados:**\n\n"
            md_content += "| Periodo Inicio | Periodo Fin | Duracion (dias) | Flags | Severidad | Descripcion |\n"
            md_content += "|----------------|-------------|-----------------|-------|-----------|-------------|\n"
            
            for _, period in result['problem_periods'].iterrows():
                start = period['start_date'].strftime('%Y-%m-%d')
                end = period['end_date'].strftime('%Y-%m-%d')
                md_content += f"| {start} | {end} | {period['duration_days']} | "
                md_content += f"{period['n_flags']} | {period['max_severity']} | {period['description']} |\n"
        else:
            md_content += "**✓ No se detectaron periodos problematicos**\n"
        
        md_content += "\n---\n\n"
    
    # Recomendaciones
    md_content += """## Recomendaciones

### Estaciones que requieren atencion inmediata:
"""
    
    critical_stations = [r for r in results_list if r['critical_flags'] > 0]
    if critical_stations:
        for result in critical_stations:
            md_content += f"- **{result['station']}**: {result['critical_flags']} flags CRITICAL\n"
    else:
        md_content += "- Ninguna estacion tiene flags CRITICAL\n"
    
    md_content += """
### Acciones sugeridas:

1. **Revisar manualmente** los periodos marcados como CRITICAL
2. **Comparar con datos brutos** originales para verificar si son errores de imputacion
3. **Ajustar modelos H-H** para estaciones con problemas de coherencia espacial
4. **Considerar exclusion** de periodos dudosos para analisis de frecuencia

### Metodologia:

- Umbral velocidad: 2x percentil 99.5 historico
- Umbral correlacion espacial: r < 0.7
- Umbral salto frontera: > 3 desviaciones estandar locales

---

**Fecha de generacion:** """ + pd.Timestamp.now().strftime('%Y-%m-%d %H:%M') + """
**Sistema:** MagdalenaBot Validacion v1.0
"""
    
    # Guardar archivo
    output_file = f'{output_path}validacion_imputacion_problemas.md'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"\n✓ Reporte guardado en: {output_file}")
    return output_file


# Estaciones vecinas para validacion espacial
STATION_NEIGHBORS = {
    'COYONGAL': ['BARBOSA', 'MAGANGUE'],
    'RIO_NUEVO': ['LAS_PALOMAS', 'LAS_AGUADAS', 'ARMENIA'],
    'LAS_PALOMAS': ['RIO_NUEVO', 'LAS_AGUADAS'],
    'ARMENIA': ['RIO_NUEVO', 'LAS_PALOMAS'],
    'GAMARRA_AUT': ['LA_GLORIA', 'EL_CONTENTO'],
}


if __name__ == '__main__':
    # Ejemplo de uso
    validator = ImputationValidator()
    
    # Estaciones problemáticas identificadas
    problem_stations = ['COYONGAL', 'RIO_NUEVO', 'LAS_PALOMAS', 'ARMENIA', 'GAMARRA_AUT']
    
    results = []
    for station in problem_stations:
        neighbors = STATION_NEIGHBORS.get(station, [])
        result = validator.validate_station(station, neighbors)
        results.append(result)
    
    # Generar reporte
    generate_validation_report(results)
