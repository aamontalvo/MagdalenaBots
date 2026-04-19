"""Data validation utilities for water level measurements."""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime

from src.utils.logger import logger
from src.utils.date_utils import date_formatter
from src.models.water_level import WaterLevelMeasurement, DataQualityReport


class DataValidator:
    """Validator for water level data quality and consistency."""
    
    def __init__(self, strict_mode: bool = True):
        """
        Initialize the data validator.
        
        Args:
            strict_mode: If True, apply strict validation rules
        """
        self.strict_mode = strict_mode
        
    def validate_measurement(self, measurement: WaterLevelMeasurement) -> List[str]:
        """
        Validate a single water level measurement.
        
        Args:
            measurement: WaterLevelMeasurement object to validate
            
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        # Validate station code
        if not measurement.station_code or len(measurement.station_code.strip()) == 0:
            errors.append("Missing or empty station code")
        
        # Validate date
        if not measurement.date:
            errors.append("Missing or invalid date")
        else:
            # Check if date is reasonable (not in the future, not too old)
            current_year = datetime.now().year
            if measurement.date.year > current_year + 1:
                errors.append(f"Date is in the future: {measurement.date.year}")
            elif measurement.date.year < 1900:
                errors.append(f"Date is too old: {measurement.date.year}")
        
        # Validate water level value
        if measurement.value is None or np.isnan(measurement.value):
            errors.append("Missing water level value")
        else:
            # Check for reasonable water level values (in cm)
            if measurement.value < -1000:  # Unrealistically low
                errors.append(f"Water level too low: {measurement.value} cm")
            elif measurement.value > 10000:  # Unrealistically high (100 meters)
                errors.append(f"Water level too high: {measurement.value} cm")
        
        # Validate unit
        if not measurement.unit or measurement.unit.strip() != "cm":
            errors.append(f"Invalid unit: {measurement.unit}")
        
        # Validate approval level
        valid_approval_levels = ["Preliminar", "Aprobado", "Validado"]
        if measurement.approval_level not in valid_approval_levels:
            if self.strict_mode:
                errors.append(f"Invalid approval level: {measurement.approval_level}")
            else:
                logger.warning(f"Non-standard approval level: {measurement.approval_level}")
        
        return errors
    
    def validate_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate a DataFrame containing water level data.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            Dictionary with validation results
        """
        validation_results = {
            'total_rows': len(df),
            'valid_rows': 0,
            'invalid_rows': 0,
            'missing_dates': 0,
            'duplicate_rows': 0,
            'outlier_values': 0,
            'errors': []
        }
        
        try:
            # Check for missing dates
            if 'Fecha' in df.columns:
                missing_dates = df['Fecha'].isna().sum()
                validation_results['missing_dates'] = int(missing_dates)
                
                # Check for invalid date formats
                invalid_dates = 0
                for idx, date_val in enumerate(df['Fecha']):
                    if pd.notna(date_val) and not date_formatter.is_valid_date_string(str(date_val)):
                        invalid_dates += 1
                        validation_results['errors'].append(f"Row {idx}: Invalid date format '{date_val}'")
                
                if invalid_dates > 0:
                    validation_results['errors'].append(f"Found {invalid_dates} invalid date formats")
            
            # Check for missing values
            if 'Valor' in df.columns:
                missing_values = df['Valor'].isna().sum()
                if missing_values > 0:
                    validation_results['errors'].append(f"Found {missing_values} missing water level values")
            
            # Check for duplicates
            duplicates = df.duplicated().sum()
            validation_results['duplicate_rows'] = int(duplicates)
            
            # Check for outliers in water level values
            if 'Valor' in df.columns:
                values = pd.to_numeric(df['Valor'], errors='coerce')
                values = values.dropna()
                
                if len(values) > 0:
                    # Use IQR method for outlier detection
                    Q1 = values.quantile(0.25)
                    Q3 = values.quantile(0.75)
                    IQR = Q3 - Q1
                    
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR
                    
                    outliers = ((values < lower_bound) | (values > upper_bound)).sum()
                    validation_results['outlier_values'] = int(outliers)
                    
                    if outliers > 0:
                        validation_results['errors'].append(
                            f"Found {outliers} outlier values (outside range {lower_bound:.1f}-{upper_bound:.1f})"
                        )
            
            # Calculate valid/invalid rows
            # For simplicity, consider rows with errors as invalid
            if validation_results['errors']:
                # Estimate invalid rows based on error types
                validation_results['invalid_rows'] = (
                    validation_results['missing_dates'] +
                    validation_results['duplicate_rows'] +
                    validation_results['outlier_values']
                )
            
            validation_results['valid_rows'] = (
                validation_results['total_rows'] - validation_results['invalid_rows']
            )
            
            logger.info(f"DataFrame validation completed: {validation_results['valid_rows']}/{validation_results['total_rows']} valid rows")
            
        except Exception as e:
            logger.error(f"DataFrame validation failed: {e}")
            validation_results['errors'].append(f"Validation error: {str(e)}")
        
        return validation_results
    
    def detect_gaps_in_time_series(self, df: pd.DataFrame, date_column: str = 'Fecha') -> List[Dict[str, Any]]:
        """
        Detect gaps in time series data.
        
        Args:
            df: DataFrame with time series data
            date_column: Name of the date column
            
        Returns:
            List of gaps with start and end dates
        """
        gaps = []
        
        try:
            if date_column not in df.columns:
                logger.error(f"Date column '{date_column}' not found in DataFrame")
                return gaps
            
            # Convert dates to datetime objects
            dates = pd.to_datetime(df[date_column], errors='coerce')
            dates = dates.dropna().sort_values()
            
            if len(dates) < 2:
                return gaps
            
            # Calculate differences between consecutive dates
            date_diffs = dates.diff()
            
            # Expected daily frequency (can be adjusted)
            expected_freq = pd.Timedelta(days=1)
            
            # Find gaps larger than expected frequency
            gap_indices = date_diffs > expected_freq
            
            for idx in gap_indices[gap_indices].index:
                gap_start = dates.loc[idx - 1] if idx - 1 in dates.index else None
                gap_end = dates.loc[idx] if idx in dates.index else None
                
                if gap_start and gap_end:
                    gap_duration = (gap_end - gap_start).days
                    gaps.append({
                        'start_date': gap_start.strftime('%Y-%m-%d'),
                        'end_date': gap_end.strftime('%Y-%m-%d'),
                        'duration_days': gap_duration
                    })
            
            logger.info(f"Found {len(gaps)} gaps in time series data")
            
        except Exception as e:
            logger.error(f"Gap detection failed: {e}")
        
        return gaps
    
    def generate_quality_report(self, df: pd.DataFrame, processing_time: float) -> DataQualityReport:
        """
        Generate a comprehensive data quality report.
        
        Args:
            df: DataFrame to analyze
            processing_time: Time taken to process the data
            
        Returns:
            DataQualityReport object
        """
        validation_results = self.validate_dataframe(df)
        
        # Detect time series gaps
        gaps = self.detect_gaps_in_time_series(df)
        
        # Create quality report
        report = DataQualityReport(
            total_records=validation_results['total_rows'],
            valid_records=validation_results['valid_rows'],
            invalid_records=validation_results['invalid_rows'],
            missing_dates=validation_results['missing_dates'],
            duplicate_records=validation_results['duplicate_rows'],
            outlier_records=validation_results['outlier_values'],
            validation_errors=validation_results['errors'],
            processing_time=processing_time
        )
        
        # Add gap information to errors if any
        if gaps:
            gap_summary = f"Found {len(gaps)} time series gaps"
            report.validation_errors.append(gap_summary)
        
        return report