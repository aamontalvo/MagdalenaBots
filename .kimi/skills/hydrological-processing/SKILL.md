---
name: hydrological-data-analysis
description: Specialized workflows for hydrological data processing, analysis, and visualization. Use when working with water level measurements, flow data, time series analysis, station metadata, and hydrological statistics. Covers data transformation (wide to long format), quality control (missing data analysis, outlier detection), and standard hydrological visualizations (heatmap coverage, boxplots, duration curves, exceedance probabilities).
---

# Hydrological Data Analysis

Specialized workflows for processing and analyzing hydrological time series data from river monitoring stations.

## Data Structure Standards

### Wide Format (Source)
Excel files typically contain:
- Rows: Days of year (1-366)
- Columns: Years as column headers
- First column: Date reference (e.g., 2019-01-01)
- Last columns: Summary statistics (Max, Prom, Min, percentiles)

### Long Format (Analysis)
Transform to:
```
date | station | level | year | month | day | value_available
```

## Standard Workflows

### 1. Data Loading and Transformation

```python
import pandas as pd
import numpy as np

def load_hydrological_data(filepath, sheet_name=0):
    """Load Excel with wide format, return long format DataFrame."""
    df_wide = pd.read_excel(filepath, sheet_name=sheet_name)
    
    # Extract station name from filename
    station_name = Path(filepath).stem.split('_')[0]
    
    # Identify year columns (numeric columns excluding stats)
    year_cols = [c for c in df_wide.columns if isinstance(c, (int, float))]
    
    # Get date reference from first column
    dates = pd.to_datetime(df_wide.iloc[:, 0])
    
    # Melt to long format
    df_long = pd.melt(
        df_wide,
        id_vars=[df_wide.columns[0]],
        value_vars=year_cols,
        var_name='year',
        value_name='level'
    )
    
    # Create full date
    df_long['date'] = pd.to_datetime(
        df_long['year'].astype(str) + '-' + 
        dates[df_long.index % len(dates)].dt.strftime('%m-%d'),
        errors='coerce'
    )
    
    df_long['station'] = station_name
    df_long['month'] = df_long['date'].dt.month
    df_long['day'] = df_long['date'].dt.day
    
    return df_long[['date', 'station', 'level', 'year', 'month', 'day']].dropna(subset=['date'])
```

### 2. Missing Data Analysis

Calculate coverage by station and year:
```python
def calculate_coverage(df):
    """Returns DataFrame with % available data by station-year."""
    coverage = df.groupby(['station', 'year'])['level'].apply(
        lambda x: (x.notna().sum() / len(x)) * 100
    ).reset_index()
    coverage.columns = ['station', 'year', 'coverage_pct']
    return coverage
```

### 3. Standard Visualizations

#### Coverage Heatmap
- X-axis: Years
- Y-axis: Stations (ordered geographically)
- Color: Blue intensity for missing data %, Gray/White for "station not existing"

#### Boxplot by Station
- X-axis: Stations (ordered geographically)
- Y-axis: Level (cota in msnm)
- Dashed vertical lines separating geographic zones

## Geographic Ordering

Standard downstream-to-upstream order for Río Magdalena:
```
[Calamar → ... → Coyongal]  # Zona Baja (aguas abajo del Cauca)
--- Línea zona baja/media ---
[Armenia → ... → Peñoncito]  # Zona Media
--- Línea zona media/alta ---
[La Gloria → ... → Barrancabermeja]  # Zona Alta
```

## Statistical Conventions

- **Cotas**: Metros sobre el nivel del mar (msnm)
- **Decimal precision**: 3 significant figures (e.g., 4.334, 0.599)
- **Missing data threshold**: < 80% coverage = questionable for analysis
- **Outlier detection**: IQR method (1.5 × IQR beyond Q1/Q3)

## Quality Control Checks

1. **Temporal coverage**: Verify start/end years per station
2. **Gaps**: Identify years with < 50% data availability
3. **Outliers**: Boxplot visualization by station
4. **Consistency**: Check for impossible values (negative levels if appropriate)
