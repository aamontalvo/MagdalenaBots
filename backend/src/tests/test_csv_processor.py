"""Tests for CSV processing utilities."""

import pytest
import pandas as pd
from pathlib import Path
import tempfile
import os

from src.data_processing.csv_processor import CSVProcessor


class TestCSVProcessor:
    
    def setup_method(self):
        """Set up test fixtures."""
        self.processor = CSVProcessor()
        
        # Create temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        
        # Sample water level data
        self.sample_data = pd.DataFrame({
            'CodigoEstacion': ['29037020', '29037020', '29037020'],
            'NombreEstacion': ['CALAMAR [29037020]', 'CALAMAR [29037020]', 'CALAMAR [29037020]'],
            'Variable': ['NIVEL', 'NIVEL', 'NIVEL'],
            'Parametro': ['Nivel medio diario', 'Nivel medio diario', 'Nivel medio diario'],
            'Fecha': ['2023-01-01 00:00', '2023-01-02 00:00', '2023-01-03 00:00'],
            'Unidad': ['cm', 'cm', 'cm'],
            'Valor': [444, 440, 432],
            'NivelAprobacion': ['Preliminar', 'Preliminar', 'Preliminar']
        })
    
    def teardown_method(self):
        """Clean up test fixtures."""
        # Remove temporary directory and files
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_test_csv(self, filename: str, data: pd.DataFrame) -> Path:
        """Helper method to create test CSV files."""
        file_path = Path(self.temp_dir) / filename
        data.to_csv(file_path, index=False)
        return file_path
    
    def test_read_csv_file_valid(self):
        """Test reading a valid CSV file."""
        csv_path = self.create_test_csv("test_valid.csv", self.sample_data)
        
        result = self.processor.read_csv_file(csv_path)
        
        assert result is not None
        assert len(result) == 3
        assert list(result.columns) == list(self.sample_data.columns)
    
    def test_read_csv_file_nonexistent(self):
        """Test reading a non-existent CSV file."""
        nonexistent_path = Path(self.temp_dir) / "nonexistent.csv"
        
        result = self.processor.read_csv_file(nonexistent_path)
        
        assert result is None
    
    def test_validate_columns_valid(self):
        """Test column validation with valid data."""
        result = self.processor.validate_columns(self.sample_data)
        
        assert result is True
    
    def test_validate_columns_missing_columns(self):
        """Test column validation with missing columns."""
        incomplete_data = self.sample_data.drop(columns=['Valor'])
        
        result = self.processor.validate_columns(incomplete_data)
        
        assert result is False
    
    def test_validate_columns_empty_dataframe(self):
        """Test column validation with empty DataFrame."""
        empty_df = pd.DataFrame()
        
        result = self.processor.validate_columns(empty_df)
        
        assert result is False
    
    def test_clean_data(self):
        """Test data cleaning functionality."""
        # Create data with issues
        dirty_data = self.sample_data.copy()
        dirty_data.loc[0, 'Valor'] = None  # Missing value
        dirty_data.loc[1, 'Fecha'] = 'invalid-date'  # Invalid date
        dirty_data = pd.concat([dirty_data, dirty_data.iloc[:1]], ignore_index=True)  # Duplicate
        
        result = self.processor.clean_data(dirty_data)
        
        assert result is not None
        assert len(result) < len(dirty_data)  # Some rows should be removed
        assert 'Fecha' in result.columns
    
    def test_convert_to_measurements(self):
        """Test conversion to WaterLevelMeasurement objects."""
        result = self.processor.convert_to_measurements(self.sample_data)
        
        assert result is not None
        assert len(result) == 3
        
        # Check first measurement
        first_measurement = result[0]
        assert first_measurement.station_code == '29037020'
        assert first_measurement.value == 444
        assert first_measurement.unit == 'cm'
    
    def test_merge_csv_files(self):
        """Test merging multiple CSV files."""
        # Create multiple CSV files
        csv1 = self.create_test_csv("file1.csv", self.sample_data.iloc[:2])
        csv2 = self.create_test_csv("file2.csv", self.sample_data.iloc[1:])
        
        result = self.processor.merge_csv_files([csv1, csv2])
        
        assert result is not None
        assert len(result) >= len(self.sample_data)  # Should have at least as many rows
    
    def test_merge_csv_files_empty_list(self):
        """Test merging with empty file list."""
        result = self.processor.merge_csv_files([])
        
        assert result is None
    
    def test_save_to_csv(self):
        """Test saving DataFrame to CSV."""
        output_path = Path(self.temp_dir) / "output.csv"
        
        success = self.processor.save_to_csv(self.sample_data, output_path)
        
        assert success is True
        assert output_path.exists()
        
        # Verify saved content
        loaded_data = pd.read_csv(output_path)
        assert len(loaded_data) == len(self.sample_data)
    
    def test_save_to_csv_creates_directory(self):
        """Test that save_to_csv creates necessary directories."""
        nested_path = Path(self.temp_dir) / "nested" / "deep" / "output.csv"
        
        success = self.processor.save_to_csv(self.sample_data, nested_path)
        
        assert success is True
        assert nested_path.exists()
    
    def test_merge_with_different_date_ranges(self):
        """Test merging files with different date ranges."""
        # Create files with different date ranges
        data1 = self.sample_data.copy()
        data1['Fecha'] = ['2020-01-01 00:00', '2020-01-02 00:00', '2020-01-03 00:00']
        
        data2 = self.sample_data.copy()
        data2['Fecha'] = ['2021-01-01 00:00', '2021-01-02 00:00', '2021-01-03 00:00']
        
        data3 = self.sample_data.copy()
        data3['Fecha'] = ['2022-01-01 00:00', '2022-01-02 00:00', '2022-01-03 00:00']
        
        csv1 = self.create_test_csv("calamar1.csv", data1)
        csv2 = self.create_test_csv("calamar2.csv", data2)
        csv3 = self.create_test_csv("calamar3.csv", data3)
        
        result = self.processor.merge_csv_files([csv1, csv2, csv3])
        
        assert result is not None
        assert len(result) == 9  # Should have all records
        
        # Check that dates are sorted
        if 'Fecha' in result.columns:
            dates = result['Fecha'].tolist()
            assert dates == sorted(dates)