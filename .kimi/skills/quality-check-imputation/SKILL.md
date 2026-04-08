# Skill: Quality Check for Data Imputation

Quality assurance workflows for validating hydrological data imputation results, ensuring data integrity, coverage, and adherence to HARD RULE constraints.

## When to Use This Skill

Use this skill when:
- Validating imputation results after running an imputation system
- Investigating why values remain missing after imputation
- Checking donor-recipient data overlap and coverage
- Verifying HARD RULE compliance (no imputation outside valid ranges)
- Generating quality reports for imputed datasets

## Quality Check Process

### Step 1: Generate Complete Time Series

Before imputation, ensure the dataset includes ALL dates in each station's valid range:

```python
def generate_complete_series(station_code, existing_data, start_date, end_date):
    """Generate complete daily series with missing values explicitly as NaN"""
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    df_complete = pd.DataFrame({'Fecha': date_range})
    df_merged = pd.merge(df_complete, existing_data, on='Fecha', how='left')
    return df_merged
```

**Critical**: Without this step, missing values won't be visible for imputation.

### Step 2: Coverage Analysis

Check coverage statistics by station:

```python
def analyze_coverage(df_imputed, station_ranges):
    results = []
    for code in df_imputed['CodigoEstacion'].unique():
        station_data = df_imputed[df_imputed['CodigoEstacion'] == code]
        total = len(station_data)
        original = station_data[station_data['Es_Imputado'] == False]['Cota'].notna().sum()
        imputed = station_data[station_data['Es_Imputado'] == True].shape[0]
        missing = station_data['Cota'].isna().sum()
        coverage = ((original + imputed) / total * 100) if total > 0 else 0
        
        results.append({
            'code': code,
            'total': total,
            'original': original,
            'imputed': imputed,
            'missing': missing,
            'coverage': coverage
        })
    return pd.DataFrame(results)
```

**Quality Thresholds**:
- ✅ **Excellent**: Coverage >= 95%
- ⚠️ **Acceptable**: Coverage 85-95%
- ❌ **Poor**: Coverage < 85%

### Step 3: Donor Coverage Analysis

Check if donors actually have data for the recipient's missing dates:

```python
def analyze_donor_coverage(df_imputed, recipient_code, donor_code):
    """Analyze how many missing values in recipient can be covered by donor"""
    recipient_data = df_imputed[df_imputed['CodigoEstacion'] == recipient_code]
    donor_data = df_imputed[df_imputed['CodigoEstacion'] == donor_code]
    
    # Find missing dates in recipient
    missing_dates = recipient_data[recipient_data['Cota'].isna()]['Fecha']
    
    # Check donor availability
    donor_for_missing = donor_data[donor_data['Fecha'].isin(missing_dates)]
    donor_has_data = donor_for_missing['Cota'].notna().sum()
    donor_missing = donor_for_missing['Cota'].isna().sum()
    
    return {
        'recipient_missing': len(missing_dates),
        'donor_covers': donor_has_data,
        'donor_also_missing': donor_missing,
        'coverage_pct': (donor_has_data / len(missing_dates) * 100) if len(missing_dates) > 0 else 0
    }
```

**Interpretation**:
- If `donor_also_missing` is high: Both stations have gaps in same periods
- If `coverage_pct` < 50%: Need alternative donor or multi-donant strategy

### Step 4: Temporal Gap Analysis

Analyze when gaps occur to identify systematic issues:

```python
def analyze_temporal_gaps(df_station):
    """Analyze distribution of missing values over time"""
    missing = df_station[df_station['Cota'].isna()].copy()
    missing['Year'] = missing['Fecha'].dt.year
    missing['Month'] = missing['Fecha'].dt.month
    
    yearly_counts = missing['Year'].value_counts().sort_index()
    monthly_counts = missing['Month'].value_counts().sort_index()
    
    return yearly_counts, monthly_counts
```

**Look for**:
- Specific years with many gaps (equipment failures)
- Seasonal patterns (winter gaps more common)
- Continuous long gaps (>30 days) vs scattered gaps

### Step 5: HARD RULE Verification

Verify no imputation occurred outside valid ranges:

```python
def verify_hard_rule(df_imputed, station_ranges):
    """Verify no imputation outside valid station ranges"""
    violations = []
    
    for code in df_imputed['CodigoEstacion'].unique():
        station_data = df_imputed[df_imputed['CodigoEstacion'] == code]
        imputed = station_data[station_data['Es_Imputado'] == True]
        
        start_limit = pd.to_datetime(station_ranges[code]['start'])
        end_limit = pd.to_datetime(station_ranges[code]['end'])
        
        # Check for violations
        before_start = imputed[imputed['Fecha'] < start_limit]
        after_end = imputed[imputed['Fecha'] > end_limit]
        
        if len(before_start) > 0 or len(after_end) > 0:
            violations.append({
                'code': code,
                'before_start': len(before_start),
                'after_end': len(after_end)
            })
    
    return violations
```

**Critical**: Any violations indicate a bug in the imputation system.

### Step 6: Cross-Station Consistency

Check if imputed values maintain hydraulic consistency:

```python
def check_hydraulic_consistency(df_imputed, station_pairs):
    """Check if imputed values maintain expected relationships"""
    issues = []
    
    for upstream_code, downstream_code in station_pairs:
        upstream = df_imputed[df_imputed['CodigoEstacion'] == upstream_code]
        downstream = df_imputed[df_imputed['CodigoEstacion'] == downstream_code]
        
        merged = pd.merge(upstream, downstream, on='Fecha', suffixes=('_up', '_down'))
        
        # Check if downstream > upstream (should be generally true for levels)
        inconsistent = merged[merged['Cota_down'] < merged['Cota_up']]
        
        if len(inconsistent) > 0:
            issues.append({
                'upstream': upstream_code,
                'downstream': downstream_code,
                'inconsistent_count': len(inconsistent)
            })
    
    return issues
```

## Quality Checklist

Before accepting imputation results:

- [ ] **Coverage Check**: All stations have >= 85% coverage
- [ ] **Donor Analysis**: Donors cover at least 70% of recipient's missing dates
- [ ] **HARD RULE**: No imputations outside valid station ranges
- [ ] **Temporal Check**: No suspicious temporal patterns (e.g., all gaps in same year)
- [ ] **Consistency**: Hydraulic relationships maintained
- [ ] **Documentation**: Report generated with all quality metrics

## Common Issues and Solutions

### Issue 1: High remaining missing values (>20%)
**Cause**: Donor also missing in same periods  
**Solution**: Implement multi-donor strategy or cascading imputation

### Issue 2: Low donor coverage (<50%)
**Cause**: Poor temporal overlap between recipient and donor  
**Solution**: Select different donor with better overlap

### Issue 3: Seasonal bias in gaps
**Cause**: Systematic data collection issues  
**Solution**: Document bias; consider seasonal correction models

### Issue 4: Long continuous gaps (>90 days)
**Cause**: Equipment failure or station closure  
**Solution**: Flag for manual review; may need exclusion from analysis

## Output Templates

### Quality Report Structure

```markdown
# Quality Check Report - Imputation [Version]

## Summary Statistics
- Total records: [N]
- Imputed values: [N] ([%])
- Still missing: [N] ([%])
- Coverage: [%]%

## Station-by-Station Analysis
| Station | Total | Original | Imputed | Missing | Coverage | Status |
|---------|-------|----------|---------|---------|----------|--------|

## Donor Coverage Analysis
| Recipient | Donor | Missing | Donor Covers | % Coverage |

## HARD RULE Verification
✅ All imputations within valid ranges

## Recommendations
1. [Specific recommendation based on analysis]
```

## References

- HARD RULE: Never impute outside original station ranges
- R² Threshold: >= 0.75 for H-H models
- Coverage Target: >= 90% for analysis-grade data
