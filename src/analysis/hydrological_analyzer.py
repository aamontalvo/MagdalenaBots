"""
Hydrological Analysis Module for MagdalenaBot
Generates 3 types of standard hydrological analyses:
1. Monthly Probability Distributions (Kernel Density)
2. Exceedance Frequency Curves
3. Duration Curves

Optimized for CSV export to engineers (no graphics generation)
"""

import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import io


class HydrologicalAnalyzer:
    """
    Analyzer for river water level time series data.
    Generates processed CSVs for engineers to create their own charts.
    """
    
    def __init__(self, data: pd.DataFrame):
        """
        Initialize with water level data.
        
        Args:
            data: DataFrame with columns [date, water_level_cm, station_code]
        """
        self.df = data.copy()
        self.df['date'] = pd.to_datetime(self.df['date'])
        self.df['month'] = self.df['date'].dt.month
        self.df['year'] = self.df['date'].dt.year
        self.df['day_of_year'] = self.df['date'].dt.dayofyear
        
    def analyze_all(self, station_code: str, email: str) -> Dict[str, io.StringIO]:
        """
        Generate all 3 analyses for a station.
        
        Returns:
            Dictionary with CSV buffers for each analysis type
        """
        station_data = self.df[self.df['station_code'] == station_code]
        
        if len(station_data) == 0:
            raise ValueError(f"No data found for station {station_code}")
        
        return {
            'monthly_probability': self._generate_monthly_probability_csv(station_data, station_code),
            'exceedance_frequency': self._generate_exceedance_frequency_csv(station_data, station_code),
            'duration_curve': self._generate_duration_curve_csv(station_data, station_code),
            'metadata': self._generate_metadata_csv(station_data, station_code, email)
        }
    
    def _generate_monthly_probability_csv(
        self, 
        data: pd.DataFrame, 
        station_code: str
    ) -> io.StringIO:
        """
        1. Monthly Probability Analysis
        
        Generates probability distributions by month using kernel density estimation.
        Engineers can use this to create violin plots, box plots, or density curves.
        
        Output columns:
        - month: Month number (1-12)
        - month_name: Month name in Spanish
        - level_value: Water level values for density estimation
        - probability_density: KDE values (for plotting density curves)
        - percentile_10,25,50,75,90: Percentiles for box plot creation
        - mean: Monthly average
        - std: Standard deviation
        - count: Number of observations
        """
        output = io.StringIO()
        
        # Calculate percentiles and statistics per month
        monthly_stats = []
        
        for month in range(1, 13):
            month_data = data[data['month'] == month]['water_level_cm'].dropna()
            
            if len(month_data) < 5:
                continue
                
            # Basic statistics
            stats_dict = {
                'month': month,
                'month_name': self._get_month_name(month),
                'count': len(month_data),
                'mean': round(month_data.mean(), 2),
                'std': round(month_data.std(), 2),
                'min': round(month_data.min(), 2),
                'max': round(month_data.max(), 2),
                'percentile_10': round(np.percentile(month_data, 10), 2),
                'percentile_25': round(np.percentile(month_data, 25), 2),
                'percentile_50': round(np.percentile(month_data, 50), 2),
                'percentile_75': round(np.percentile(month_data, 75), 2),
                'percentile_90': round(np.percentile(month_data, 90), 2),
            }
            
            # Kernel Density Estimation points for curve plotting
            if len(month_data) > 10:
                kde = stats.gaussian_kde(month_data)
                level_range = np.linspace(month_data.min(), month_data.max(), 100)
                density = kde(level_range)
                
                # Store KDE points as JSON-like string for CSV
                kde_points = [{'level': round(l, 2), 'density': round(d, 6)} 
                             for l, d in zip(level_range, density)]
                stats_dict['kde_points'] = str(kde_points).replace("'", '"')
            else:
                stats_dict['kde_points'] = '[]'
            
            monthly_stats.append(stats_dict)
        
        df_stats = pd.DataFrame(monthly_stats)
        df_stats.to_csv(output, index=False)
        output.seek(0)
        return output
    
    def _generate_exceedance_frequency_csv(
        self, 
        data: pd.DataFrame, 
        station_code: str
    ) -> io.StringIO:
        """
        2. Exceedance Frequency Curves
        
        Shows the probability that a water level is exceeded during the year.
        Critical for flood risk assessment and reservoir management.
        
        Output columns:
        - exceedance_probability: Probability of exceedance (%) - X-axis
        - water_level_cm: Level corresponding to that probability - Y-axis
        - classification: minimo (90%), promedio (50%), maximo (10%)
        - reference_lines: Boolean if this point is a reference (10%,25%,50%,75%,90%)
        """
        output = io.StringIO()
        
        levels = data['water_level_cm'].dropna().sort_values()
        n = len(levels)
        
        if n == 0:
            return output
        
        # Calculate exceedance probability for each unique level
        # P(X > x) = rank / (n + 1) * 100
        unique_levels = levels.unique()
        exceedance_data = []
        
        for level in unique_levels:
            # Count how many values are greater than this level
            exceed_count = (levels > level).sum()
            prob = (exceed_count / n) * 100
            
            # Determine classification
            if prob >= 90:
                classification = 'minimo'
            elif prob >= 50:
                classification = 'bajo_promedio'
            elif prob >= 25:
                classification = 'promedio'
            elif prob >= 10:
                classification = 'alto_promedio'
            else:
                classification = 'maximo'
            
            # Check if this is a reference percentile
            is_ref = prob in [10, 25, 50, 75, 90]
            
            exceedance_data.append({
                'exceedance_probability_percent': round(prob, 2),
                'water_level_cm': round(level, 2),
                'water_level_m': round(level / 100, 2),
                'classification': classification,
                'is_reference_percentile': is_ref,
                'observations_count': exceed_count
            })
        
        df_exceed = pd.DataFrame(exceedance_data)
        
        # Add reference percentiles explicitly
        percentiles = [10, 25, 50, 75, 90]
        ref_data = []
        for p in percentiles:
            level = np.percentile(levels, 100 - p)  # Invert because exceedance
            ref_data.append({
                'exceedance_probability_percent': p,
                'water_level_cm': round(level, 2),
                'water_level_m': round(level / 100, 2),
                'classification': self._classify_percentile(p),
                'is_reference_percentile': True,
                'observations_count': int((p / 100) * n),
                'note': 'REFERENCE_PERCENTILE'
            })
        
        df_refs = pd.DataFrame(ref_data)
        df_final = pd.concat([df_exceed, df_refs], ignore_index=True)
        df_final = df_final.sort_values('exceedance_probability_percent')
        
        df_final.to_csv(output, index=False)
        output.seek(0)
        return output
    
    def _generate_duration_curve_csv(
        self, 
        data: pd.DataFrame, 
        station_code: str
    ) -> io.StringIO:
        """
        3. Duration Curves (Flow Duration Curve concept adapted for levels)
        
        Shows percentage of time a level is equaled or exceeded.
        Essential for water resource planning and environmental flow studies.
        
        Output columns:
        - duration_percent: Percentage of time level is equaled or exceeded
        - water_level_cm: Level
        - water_level_m: Level in meters
        - days_per_year: Equivalent days per year
        - classification: How often this level occurs
        """
        output = io.StringIO()
        
        levels = data['water_level_cm'].dropna().sort_values(ascending=False)
        n = len(levels)
        
        if n == 0:
            return output
        
        duration_data = []
        
        # Use percentiles for cleaner curve
        percentiles = np.linspace(0, 100, 101)  # Every percentile
        
        for p in percentiles:
            level = np.percentile(levels, p)
            duration_percent = 100 - p  # Invert: % of time >= this level
            days_per_year = (duration_percent / 100) * 365
            
            # Classification
            if duration_percent >= 90:
                classification = 'muy_frecuente'
            elif duration_percent >= 50:
                classification = 'frecuente'
            elif duration_percent >= 10:
                classification = 'poco_frecuente'
            else:
                classification = 'muy_poco_frecuente'
            
            duration_data.append({
                'duration_percent': round(duration_percent, 2),
                'water_level_cm': round(level, 2),
                'water_level_m': round(level / 100, 2),
                'days_per_year': round(days_per_year, 1),
                'classification': classification,
                'observations_count': int((duration_percent / 100) * n)
            })
        
        df_duration = pd.DataFrame(duration_data)
        df_duration.to_csv(output, index=False)
        output.seek(0)
        return output
    
    def _generate_metadata_csv(
        self, 
        data: pd.DataFrame, 
        station_code: str,
        email: str
    ) -> io.StringIO:
        """
        Generate metadata summary for the engineer
        """
        output = io.StringIO()
        
        metadata = {
            'station_code': station_code,
            'report_generated': datetime.now().isoformat(),
            'email_destination': email,
            'total_observations': len(data),
            'date_range_start': data['date'].min().isoformat(),
            'date_range_end': data['date'].max().isoformat(),
            'years_of_data': data['year'].nunique(),
            'level_min_cm': round(data['water_level_cm'].min(), 2),
            'level_max_cm': round(data['water_level_cm'].max(), 2),
            'level_mean_cm': round(data['water_level_cm'].mean(), 2),
            'level_median_cm': round(data['water_level_cm'].median(), 2),
            'level_std_cm': round(data['water_level_cm'].std(), 2),
            'analyses_included': 'monthly_probability, exceedance_frequency, duration_curve'
        }
        
        df_meta = pd.DataFrame([metadata])
        df_meta.to_csv(output, index=False)
        output.seek(0)
        return output
    
    def _get_month_name(self, month: int) -> str:
        """Get Spanish month name"""
        months = {
            1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
            5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
            9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
        }
        return months.get(month, '')
    
    def _classify_percentile(self, p: float) -> str:
        """Classify percentile for exceedance analysis"""
        if p >= 90:
            return 'minimo'
        elif p >= 50:
            return 'promedio'
        else:
            return 'maximo'


def create_sample_analysis():
    """Create sample data to demonstrate the analyzer"""
    np.random.seed(42)
    dates = pd.date_range('2020-01-01', '2024-12-31', freq='D')
    
    # Simulate seasonal water levels
    base_level = 500
    seasonal = 200 * np.sin(2 * np.pi * np.arange(len(dates)) / 365.25)
    noise = np.random.normal(0, 50, len(dates))
    levels = base_level + seasonal + noise
    
    df = pd.DataFrame({
        'date': dates,
        'water_level_cm': levels,
        'station_code': '29037020'
    })
    
    analyzer = HydrologicalAnalyzer(df)
    results = analyzer.analyze_all('29037020', 'engineer@example.com')
    
    return results


if __name__ == '__main__':
    # Test the analyzer
    results = create_sample_analysis()
    
    for name, buffer in results.items():
        print(f"\n=== {name} ===")
        print(buffer.read()[:500])
        print("...")
