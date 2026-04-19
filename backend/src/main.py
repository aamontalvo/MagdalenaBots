"""Main integration script for water level data processing."""

import time
from pathlib import Path
from typing import List, Optional
import argparse

from src.config.settings import settings
from src.utils.logger import logger
from src.utils.date_utils import date_formatter
from src.data_processing.csv_processor import CSVProcessor
from src.data_processing.data_validator import DataValidator
from src.config.supabase_config import supabase_manager


class WaterLevelDataIntegrator:
    """Main class for integrating water level data from multiple CSV files."""
    
    def __init__(self):
        """Initialize the data integrator."""
        self.csv_processor = CSVProcessor()
        self.data_validator = DataValidator(strict_mode=settings.data_validation_strict)
        
    def find_csv_files(self, directory: Path, pattern: str = "*.csv") -> List[Path]:
        """
        Find CSV files in the specified directory.
        
        Args:
            directory: Directory to search
            pattern: File pattern to match
            
        Returns:
            List of CSV file paths
        """
        try:
            if not directory.exists():
                logger.error(f"Directory does not exist: {directory}")
                return []
            
            csv_files = list(directory.glob(pattern))
            logger.info(f"Found {len(csv_files)} CSV files in {directory}")
            
            for file in csv_files:
                logger.info(f"  - {file.name}")
            
            return csv_files
            
        except Exception as e:
            logger.error(f"Error finding CSV files: {e}")
            return []
    
    def process_water_level_data(self, input_directory: Path, output_file: Path, upload_to_supabase: bool = False) -> bool:
        """
        Process water level data from multiple CSV files.
        
        Args:
            input_directory: Directory containing input CSV files
            output_file: Path for the output CSV file
            upload_to_supabase: Whether to upload data to Supabase
            
        Returns:
            True if processing successful, False otherwise
        """
        start_time = time.time()
        
        try:
            logger.info("Starting water level data integration process")
            logger.info(f"Input directory: {input_directory}")
            logger.info(f"Output file: {output_file}")
            logger.info(f"Upload to Supabase: {upload_to_supabase}")
            
            # Find CSV files
            csv_files = self.find_csv_files(input_directory)
            if not csv_files:
                logger.error("No CSV files found to process")
                return False
            
            # Merge CSV files
            logger.info("Merging CSV files...")
            merged_df = self.csv_processor.merge_csv_files(csv_files)
            if merged_df is None:
                logger.error("Failed to merge CSV files")
                return False
            
            # Validate merged data
            logger.info("Validating merged data...")
            quality_report = self.data_validator.generate_quality_report(merged_df, time.time() - start_time)
            
            # Log quality report
            logger.info("=== Data Quality Report ===")
            logger.info(f"Total records: {quality_report.total_records}")
            logger.info(f"Valid records: {quality_report.valid_records}")
            logger.info(f"Invalid records: {quality_report.invalid_records}")
            logger.info(f"Validation rate: {quality_report.get_validation_rate():.2f}%")
            logger.info(f"Missing dates: {quality_report.missing_dates}")
            logger.info(f"Duplicate records: {quality_report.duplicate_records}")
            logger.info(f"Outlier records: {quality_report.outlier_records}")
            logger.info(f"Processing time: {quality_report.processing_time:.2f} seconds")
            
            if quality_report.validation_errors:
                logger.warning("Validation errors found:")
                for error in quality_report.validation_errors:
                    logger.warning(f"  - {error}")
            
            # Ensure proper date format
            logger.info("Ensuring proper date format...")
            if 'Fecha' in merged_df.columns:
                merged_df['Fecha'] = merged_df['Fecha'].apply(
                    lambda x: date_formatter.format_date(x) if pd.notna(x) else None
                )
            
            # Save to output file
            logger.info(f"Saving integrated data to {output_file}...")
            success = self.csv_processor.save_to_csv(merged_df, output_file)
            if not success:
                logger.error("Failed to save output file")
                return False
            
            # Upload to Supabase if requested
            if upload_to_supabase and settings.supabase_url and settings.supabase_key:
                logger.info("Uploading data to Supabase...")
                
                # Connect to Supabase
                if not supabase_manager.connect():
                    logger.error("Failed to connect to Supabase")
                    return False
                
                # Create table if needed
                if not supabase_manager.create_water_level_table():
                    logger.error("Failed to create Supabase table")
                    return False
                
                # Convert to measurements and upload
                measurements = self.csv_processor.convert_to_measurements(merged_df)
                stats = supabase_manager.insert_measurements_batch(measurements)
                
                logger.info(f"Supabase upload completed: {stats['success']} successful, {stats['failed']} failed")
                
                # Disconnect from Supabase
                supabase_manager.disconnect()
            
            processing_time = time.time() - start_time
            logger.info(f"Water level data integration completed successfully in {processing_time:.2f} seconds")
            logger.info(f"Final dataset: {len(merged_df)} records")
            
            return True
            
        except Exception as e:
            logger.error(f"Water level data integration failed: {e}")
            return False
    
    def generate_summary_report(self, output_file: Path) -> dict:
        """
        Generate a summary report of the integrated data.
        
        Args:
            output_file: Path to the integrated CSV file
            
        Returns:
            Dictionary with summary statistics
        """
        try:
            import pandas as pd
            
            # Read the integrated file
            df = pd.read_csv(output_file)
            
            # Generate summary statistics
            summary = {
                'total_records': len(df),
                'date_range': {
                    'start': df['Fecha'].min() if 'Fecha' in df.columns else 'N/A',
                    'end': df['Fecha'].max() if 'Fecha' in df.columns else 'N/A'
                },
                'stations': df['CodigoEstacion'].nunique() if 'CodigoEstacion' in df.columns else 0,
                'unique_dates': df['Fecha'].nunique() if 'Fecha' in df.columns else 0,
                'water_level_stats': {
                    'min': float(df['Valor'].min()) if 'Valor' in df.columns else 0,
                    'max': float(df['Valor'].max()) if 'Valor' in df.columns else 0,
                    'mean': float(df['Valor'].mean()) if 'Valor' in df.columns else 0,
                    'median': float(df['Valor'].median()) if 'Valor' in df.columns else 0
                } if 'Valor' in df.columns else {}
            }
            
            logger.info("=== Integration Summary Report ===")
            logger.info(f"Total records: {summary['total_records']}")
            logger.info(f"Date range: {summary['date_range']['start']} to {summary['date_range']['end']}")
            logger.info(f"Number of stations: {summary['stations']}")
            logger.info(f"Unique dates: {summary['unique_dates']}")
            
            if summary['water_level_stats']:
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
    parser = argparse.ArgumentParser(description="Integrate water level data from multiple CSV files")
    parser.add_argument("--input-dir", "-i", type=str, default="Data/Niveles",
                       help="Input directory containing CSV files (default: Data/Niveles)")
    parser.add_argument("--output", "-o", type=str, default="calamar.csv",
                       help="Output CSV file name (default: calamar.csv)")
    parser.add_argument("--upload", "-u", action="store_true",
                       help="Upload data to Supabase")
    parser.add_argument("--validate", "-v", action="store_true",
                       help="Perform strict data validation")
    
    args = parser.parse_args()
    
    # Convert relative paths to absolute paths
    input_directory = Path(args.input_dir).resolve()
    output_file = Path(args.output).resolve()
    
    # Create integrator instance
    integrator = WaterLevelDataIntegrator()
    
    # Process data
    success = integrator.process_water_level_data(
        input_directory=input_directory,
        output_file=output_file,
        upload_to_supabase=args.upload
    )
    
    if success:
        # Generate summary report
        summary = integrator.generate_summary_report(output_file)
        logger.info("Water level data integration completed successfully!")
        return 0
    else:
        logger.error("Water level data integration failed!")
        return 1


if __name__ == "__main__":
    exit(main())