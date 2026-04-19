"""CSV processing utilities for water level data."""

import pandas as pd
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

from src.utils.logger import logger
from src.utils.date_utils import date_formatter
from src.models.water_level import WaterLevelMeasurement


class CSVProcessor:
    """Processor for CSV files containing water level data."""
    
    def __init__(self, expected_columns: Optional[List[str]] = None):
        """
        Initialize the CSV processor.
        
        Args:
            expected_columns: List of expected column names
        """
        self.expected_columns = expected_columns or [
            'CodigoEstacion', 'NombreEstacion', 'Variable', 'Parametro',
            'Fecha', 'Unidad', 'Valor', 'NivelAprobacion'
        ]
        
    def read_csv_file(self, file_path: Path) -> Optional[pd.DataFrame]:
        """
        Read a CSV file and return a DataFrame.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            DataFrame or None if reading fails
        """
        try:
            if not file_path.exists():
                logger.error(f"CSV file not found: {file_path}")
                return None
                
            df = pd.read_csv(file_path, encoding='utf-8')
            logger.info(f"Successfully read CSV file: {file_path.name} ({len(df)} rows)")
            return df
            
        except Exception as e:
            logger.error(f"Failed to read CSV file {file_path}: {e}")
            return None
    
    def validate_columns(self, df: pd.DataFrame) -> bool:
        """
        Validate that the DataFrame has the expected columns.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            True if valid, False otherwise
        """
        if df.empty:
            logger.error("DataFrame is empty")
            return False
            
        missing_columns = set(self.expected_columns) - set(df.columns)
        if missing_columns:
            logger.error(f"Missing required columns: {missing_columns}")
            return False
            
        logger.info("DataFrame columns validation passed")
        return True
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and standardize the data.
        
        Args:
            df: Raw DataFrame
            
        Returns:
            Cleaned DataFrame
        """
        try:
            # Create a copy to avoid modifying the original
            cleaned_df = df.copy()
            
            # Remove leading/trailing whitespace from string columns
            string_columns = cleaned_df.select_dtypes(include=['object']).columns
            for col in string_columns:
                cleaned_df[col] = cleaned_df[col].str.strip()
            
            # Convert date column to proper format
            if 'Fecha' in cleaned_df.columns:
                cleaned_df['Fecha'] = cleaned_df['Fecha'].apply(
                    lambda x: date_formatter.format_date(x) if pd.notna(x) else None
                )
            
            # Convert numeric columns
            if 'Valor' in cleaned_df.columns:
                cleaned_df['Valor'] = pd.to_numeric(cleaned_df['Valor'], errors='coerce')
            
            # Remove duplicates
            initial_count = len(cleaned_df)
            cleaned_df = cleaned_df.drop_duplicates()
            duplicates_removed = initial_count - len(cleaned_df)
            
            if duplicates_removed > 0:
                logger.info(f"Removed {duplicates_removed} duplicate rows")
            
            # Remove rows with missing critical data
            critical_columns = ['Fecha', 'Valor']
            missing_before = len(cleaned_df)
            cleaned_df = cleaned_df.dropna(subset=critical_columns)
            missing_removed = missing_before - len(cleaned_df)
            
            if missing_removed > 0:
                logger.info(f"Removed {missing_removed} rows with missing critical data")
            
            logger.info(f"Data cleaning completed. Final row count: {len(cleaned_df)}")
            return cleaned_df
            
        except Exception as e:
            logger.error(f"Data cleaning failed: {e}")
            return df
    
    def convert_to_measurements(self, df: pd.DataFrame) -> List[WaterLevelMeasurement]:
        """
        Convert DataFrame rows to WaterLevelMeasurement objects.
        
        Args:
            df: DataFrame with water level data
            
        Returns:
            List of WaterLevelMeasurement objects
        """
        measurements = []
        
        for _, row in df.iterrows():
            try:
                measurement = WaterLevelMeasurement(
                    station_code=str(row['CodigoEstacion']),
                    station_name=str(row['NombreEstacion']),
                    variable=str(row['Variable']),
                    parameter=str(row['Parametro']),
                    date=date_formatter.parse_date(row['Fecha']),
                    unit=str(row['Unidad']),
                    value=float(row['Valor']),
                    approval_level=str(row['NivelAprobacion'])
                )
                measurements.append(measurement)
                
            except (ValueError, TypeError) as e:
                logger.warning(f"Skipping invalid row: {e}")
                continue
        
        logger.info(f"Converted {len(measurements)} rows to measurements")
        return measurements
    
    def merge_csv_files(self, file_paths: List[Path]) -> Optional[pd.DataFrame]:
        """
        Merge multiple CSV files into a single DataFrame.
        
        Args:
            file_paths: List of CSV file paths
            
        Returns:
            Merged DataFrame or None if processing fails
        """
        try:
            dataframes = []
            
            for file_path in file_paths:
                df = self.read_csv_file(file_path)
                if df is not None and self.validate_columns(df):
                    cleaned_df = self.clean_data(df)
                    dataframes.append(cleaned_df)
                else:
                    logger.warning(f"Skipping invalid file: {file_path}")
            
            if not dataframes:
                logger.error("No valid dataframes to merge")
                return None
            
            # Merge all dataframes
            merged_df = pd.concat(dataframes, ignore_index=True)
            
            # Sort by date
            if 'Fecha' in merged_df.columns:
                merged_df = merged_df.sort_values('Fecha')
            
            # Remove any duplicates that might have been introduced during merge
            initial_count = len(merged_df)
            merged_df = merged_df.drop_duplicates()
            duplicates_removed = initial_count - len(merged_df)
            
            if duplicates_removed > 0:
                logger.info(f"Removed {duplicates_removed} duplicate rows during merge")
            
            logger.info(f"Successfully merged {len(file_paths)} files into {len(merged_df)} rows")
            return merged_df
            
        except Exception as e:
            logger.error(f"Failed to merge CSV files: {e}")
            return None
    
    def save_to_csv(self, df: pd.DataFrame, output_path: Path, include_index: bool = False) -> bool:
        """
        Save DataFrame to CSV file.
        
        Args:
            df: DataFrame to save
            output_path: Output file path
            include_index: Whether to include index in CSV
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save to CSV
            df.to_csv(output_path, index=include_index, encoding='utf-8')
            
            logger.info(f"Successfully saved {len(df)} rows to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save CSV file {output_path}: {e}")
            return False