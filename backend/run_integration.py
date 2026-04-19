#!/usr/bin/env python3
"""Simple integration script for water level data - standalone version."""

import pandas as pd
from pathlib import Path
import logging
from datetime import datetime
import sys

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('water_level_integration.log')
    ]
)
logger = logging.getLogger(__name__)


def format_date(date_string):
    """Format date to YYYY-MM-DD format."""
    try:
        if pd.isna(date_string):
            return None
        
        # Handle different date formats
        date_str = str(date_string).strip()
        
        # Remove time portion if present
        if ' ' in date_str:
            date_part = date_str.split(' ')[0]
        else:
            date_part = date_str
        
        # Parse the date
        if '-' in date_part:
            # Assume YYYY-MM-DD format
            year, month, day = date_part.split('-')
            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        elif '/' in date_part:
            # Handle MM/DD/YYYY or DD/MM/YYYY
            parts = date_part.split('/')
            if len(parts[0]) == 4:  # YYYY/MM/DD
                year, month, day = parts
            else:  # Assume MM/DD/YYYY
                month, day, year = parts
            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        else:
            # Try pandas parsing
            parsed_date = pd.to_datetime(date_part, errors='coerce')
            if pd.notna(parsed_date):
                return parsed_date.strftime('%Y-%m-%d')
            return None
            
    except Exception as e:
        logger.warning(f"Failed to format date '{date_string}': {e}")
        return None


def read_and_clean_csv(file_path):
    """Read and clean a CSV file."""
    try:
        logger.info(f"Reading CSV file: {file_path}")
        df = pd.read_csv(file_path, encoding='utf-8')
        
        logger.info(f"File contains {len(df)} rows and {len(df.columns)} columns")
        
        # Clean column names
        df.columns = df.columns.str.strip()
        
        # Clean string data
        string_columns = df.select_dtypes(include=['object']).columns
        for col in string_columns:
            df[col] = df[col].str.strip()
        
        # Format dates
        if 'Fecha' in df.columns:
            logger.info("Formatting dates...")
            df['Fecha'] = df['Fecha'].apply(format_date)
        
        # Convert numeric columns
        if 'Valor' in df.columns:
            df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')
        
        # Remove rows with missing critical data
        initial_count = len(df)
        if 'Fecha' in df.columns and 'Valor' in df.columns:
            df = df.dropna(subset=['Fecha', 'Valor'])
            removed_count = initial_count - len(df)
            if removed_count > 0:
                logger.info(f"Removed {removed_count} rows with missing critical data")
        
        # Remove duplicates
        initial_count = len(df)
        df = df.drop_duplicates()
        duplicates_removed = initial_count - len(df)
        if duplicates_removed > 0:
            logger.info(f"Removed {duplicates_removed} duplicate rows")
        
        return df
        
    except Exception as e:
        logger.error(f"Failed to read CSV file {file_path}: {e}")
        return None


def merge_csv_files(file_paths):
    """Merge multiple CSV files into one."""
    try:
        dataframes = []
        
        for file_path in file_paths:
            df = read_and_clean_csv(file_path)
            if df is not None:
                dataframes.append(df)
                logger.info(f"Added {len(df)} rows from {file_path.name}")
            else:
                logger.warning(f"Skipping invalid file: {file_path}")
        
        if not dataframes:
            logger.error("No valid dataframes to merge")
            return None
        
        # Merge all dataframes
        merged_df = pd.concat(dataframes, ignore_index=True)
        
        # Sort by date if available
        if 'Fecha' in merged_df.columns:
            merged_df = merged_df.sort_values('Fecha')
            logger.info("Sorted data by date")
        
        # Remove any duplicates that might have been introduced
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


def validate_data(df):
    """Perform basic data validation."""
    try:
        logger.info("Performing data validation...")
        
        validation_results = {
            'total_rows': len(df),
            'missing_dates': 0,
            'missing_values': 0,
            'invalid_dates': 0,
            'outliers': 0
        }
        
        # Check for missing dates
        if 'Fecha' in df.columns:
            validation_results['missing_dates'] = df['Fecha'].isna().sum()
            
            # Check for invalid dates
            for date_val in df['Fecha']:
                if pd.notna(date_val):
                    try:
                        datetime.strptime(str(date_val), '%Y-%m-%d')
                    except:
                        validation_results['invalid_dates'] += 1
        
        # Check for missing values
        if 'Valor' in df.columns:
            validation_results['missing_values'] = df['Valor'].isna().sum()
            
            # Check for outliers (simple IQR method)
            values = pd.to_numeric(df['Valor'], errors='coerce')
            values = values.dropna()
            
            if len(values) > 0:
                Q1 = values.quantile(0.25)
                Q3 = values.quantile(0.75)
                IQR = Q3 - Q1
                
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outliers = ((values < lower_bound) | (values > upper_bound)).sum()
                validation_results['outliers'] = int(outliers)
        
        # Log validation results
        logger.info("=== Data Validation Results ===")
        logger.info(f"Total rows: {validation_results['total_rows']}")
        logger.info(f"Missing dates: {validation_results['missing_dates']}")
        logger.info(f"Missing values: {validation_results['missing_values']}")
        logger.info(f"Invalid dates: {validation_results['invalid_dates']}")
        logger.info(f"Outliers: {validation_results['outliers']}")
        
        return validation_results
        
    except Exception as e:
        logger.error(f"Data validation failed: {e}")
        return {}


def generate_summary_report(df, output_file):
    """Generate a summary report of the integrated data."""
    try:
        logger.info("Generating summary report...")
        
        summary = {
            'total_records': len(df),
            'date_range': {
                'start': df['Fecha'].min() if 'Fecha' in df.columns else 'N/A',
                'end': df['Fecha'].max() if 'Fecha' in df.columns else 'N/A'
            },
            'stations': df['CodigoEstacion'].nunique() if 'CodigoEstacion' in df.columns else 0,
            'unique_dates': df['Fecha'].nunique() if 'Fecha' in df.columns else 0
        }
        
        if 'Valor' in df.columns:
            values = pd.to_numeric(df['Valor'], errors='coerce')
            values = values.dropna()
            
            if len(values) > 0:
                summary['water_level_stats'] = {
                    'min': float(values.min()),
                    'max': float(values.max()),
                    'mean': float(values.mean()),
                    'median': float(values.median())
                }
        
        # Log summary
        logger.info("=== Integration Summary ===")
        logger.info(f"Total records: {summary['total_records']}")
        logger.info(f"Date range: {summary['date_range']['start']} to {summary['date_range']['end']}")
        logger.info(f"Number of stations: {summary['stations']}")
        logger.info(f"Unique dates: {summary['unique_dates']}")
        
        if 'water_level_stats' in summary:
            stats = summary['water_level_stats']
            logger.info(f"Water level statistics:")
            logger.info(f"  Min: {stats['min']:.2f} cm")
            logger.info(f"  Max: {stats['max']:.2f} cm")
            logger.info(f"  Mean: {stats['mean']:.2f} cm")
            logger.info(f"  Median: {stats['median']:.2f} cm")
        
        return summary
        
    except Exception as e:
        logger.error(f"Failed to generate summary report: {e}")
        return {}


def main():
    """Main function to run the water level data integration."""
    try:
        logger.info("=" * 60)
        logger.info("Water Level Data Integration Started")
        logger.info("=" * 60)
        
        # Configuration
        input_dir = Path("../Data/Niveles")
        output_file = Path("calamar.csv")
        
        logger.info(f"Input directory: {input_dir}")
        logger.info(f"Output file: {output_file}")
        
        # Find CSV files
        if not input_dir.exists():
            logger.error(f"Input directory does not exist: {input_dir}")
            return 1
        
        csv_files = list(input_dir.glob("Calamar*.csv"))
        if not csv_files:
            logger.error("No Calamar*.csv files found in input directory")
            return 1
        
        logger.info(f"Found {len(csv_files)} CSV files:")
        for file in csv_files:
            logger.info(f"  - {file.name}")
        
        # Merge CSV files
        logger.info("Merging CSV files...")
        merged_df = merge_csv_files(csv_files)
        if merged_df is None:
            logger.error("Failed to merge CSV files")
            return 1
        
        # Validate data
        logger.info("Validating merged data...")
        validation_results = validate_data(merged_df)
        
        # Save to output file
        logger.info(f"Saving integrated data to {output_file}...")
        try:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            merged_df.to_csv(output_file, index=False, encoding='utf-8')
            logger.info(f"Successfully saved {len(merged_df)} rows to {output_file}")
        except Exception as e:
            logger.error(f"Failed to save output file: {e}")
            return 1
        
        # Generate summary report
        summary = generate_summary_report(merged_df, output_file)
        
        logger.info("=" * 60)
        logger.info("Water Level Data Integration Completed Successfully!")
        logger.info("=" * 60)
        
        return 0
        
    except Exception as e:
        logger.error(f"Water level data integration failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())