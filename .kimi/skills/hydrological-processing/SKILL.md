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

## CRITICAL RULE: Exclude February 29 (Leap Year Day)

**MANDATORY**: For all hydrological analyses involving daily aggregation or percentiles (Fig4, seasonal patterns, etc.), **EXCLUDE February 29** completely:

```python
# ALWAYS filter out February 29 before analysis
df = df[df['Fecha'].dt.strftime('%m-%d') != '02-29']
```

**Rationale**:
- February 29 only occurs every 4 years (25% of data points)
- Introduces statistical noise in percentile calculations
- Creates inconsistent sample sizes across days
- For Fig4 (Frequency Curves), daily percentiles must be based on consistent N across all days

**Apply to**: Fig4, seasonal analysis, daily statistics, any analysis grouping by day-of-year

## Quality Control Checks

1. **Temporal coverage**: Verify start/end years per station
2. **Gaps**: Identify years with < 50% data availability
3. **Outliers**: Boxplot visualization by station
4. **Consistency**: Check for impossible values (negative levels if appropriate)

## Imputation System Architecture (v4.2)

The imputation system has **3 main levels**, where Level 2 has **2 sub-levels** based on correlation quality:

### Level 1: Local Interpolation (L1)
- **Condition**: Gap ≤ 3 consecutive days with valid data on both sides
- **Method**: Weighted moving average
- **Nivel_Imputacion**: 1
- **Records**: ~1,000

### Level 2: Height-Height Curves (L2/L3)
**Both L2 and L3 use the same method** (quadratic regression with single donor station), but are classified based on R² quality:

| Sub-level | R² Range | Stations | Records | Nivel_Imputacion |
|-----------|----------|----------|---------|------------------|
| **L2 (High confidence)** | ≥ 0.95 | Tenerife, Magangue | 8,227 | 2 |
| **L3 (Medium confidence)** | 0.75 - 0.95 | Barbosa, Rio Nuevo, Las Palomas, Coyongal, Penoncito, Plato | 17,793 | 3 |

**Common characteristics**:
- Single donor station per target
- Quadratic equation: `H_target = a·H_donor² + b·H_donor + c`
- Minimum R² threshold: ≥ 0.75
- Minimum training data: n ≥ 50

### Level 4: Advanced Methods (L4)
- **Condition**: No suitable donor stations available
- **Methods**: 
  - L4_HH_quadratic: Extended HH extrapolation
  - L4_missForest: Machine learning model (last resort)
- **Nivel_Imputacion**: 4
- **Records**: ~5,300 (HH) + 15 (missForest)

### Summary Table

| Method | Nivel_Imputacion | Count | % of Total |
|--------|------------------|-------|------------|
| Original | 0 | 272,055 | 89.3% |
| L1_Interpolacion | 1 | 1,005 | 0.4% |
| L2_HH_quadratic | 2 | 8,227 | 2.7% |
| L3_HH_quadratic | 3 | 17,793 | 5.6% |
| L4_HH_quadratic | 4 | 5,348 | 1.6% |
| L4_missForest | 4 | 15 | ~0% |
