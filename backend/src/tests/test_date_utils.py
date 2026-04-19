"""Tests for date utilities."""

import pytest
from datetime import datetime
from src.utils.date_utils import DateFormatter


class TestDateFormatter:
    
    def setup_method(self):
        """Set up test fixtures."""
        self.formatter = DateFormatter("%Y-%m-%d")
    
    def test_parse_date_valid_string(self):
        """Test parsing valid date strings."""
        # Test various date formats
        test_cases = [
            "2023-01-15",
            "2023-01-15 14:30:00",
            "2023/01/15",
            "15-01-2023",
            "2023-01-15T14:30:00Z"
        ]
        
        for date_str in test_cases:
            result = self.formatter.parse_date(date_str)
            assert result is not None
            assert isinstance(result, datetime)
    
    def test_parse_date_invalid_string(self):
        """Test parsing invalid date strings."""
        invalid_dates = [
            "invalid-date",
            "2023-13-45",  # Invalid month/day
            "",
            None
        ]
        
        for date_str in invalid_dates:
            result = self.formatter.parse_date(date_str)
            assert result is None
    
    def test_format_date_valid(self):
        """Test formatting valid date objects."""
        test_date = datetime(2023, 1, 15)
        result = self.formatter.format_date(test_date)
        assert result == "2023-01-15"
    
    def test_format_date_string_input(self):
        """Test formatting date from string input."""
        date_str = "2023-01-15 14:30:00"
        result = self.formatter.format_date(date_str)
        assert result == "2023-01-15"
    
    def test_format_date_invalid(self):
        """Test formatting invalid date inputs."""
        invalid_inputs = ["invalid", None, ""]
        
        for input_val in invalid_inputs:
            result = self.formatter.format_date(input_val)
            assert result is None
    
    def test_validate_date_range(self):
        """Test date range validation."""
        # Valid range
        assert self.formatter.validate_date_range("2023-01-01", "2023-12-31") is True
        
        # Same date
        assert self.formatter.validate_date_range("2023-01-15", "2023-01-15") is True
        
        # Invalid range (start after end)
        assert self.formatter.validate_date_range("2023-12-31", "2023-01-01") is False
        
        # Invalid dates
        assert self.formatter.validate_date_range("invalid", "2023-01-01") is False
    
    def test_is_valid_date_string(self):
        """Test date string validation."""
        # Valid dates
        assert self.formatter.is_valid_date_string("2023-01-15") is True
        assert self.formatter.is_valid_date_string("2023-01-15 14:30:00") is True
        
        # Invalid dates
        assert self.formatter.is_valid_date_string("invalid") is False
        assert self.formatter.is_valid_date_string("2023-13-45") is False
        assert self.formatter.is_valid_date_string("") is False
        assert self.formatter.is_valid_date_string(None) is False
    
    def test_extract_year_month_day(self):
        """Test extracting date components."""
        date_str = "2023-01-15"
        result = self.formatter.extract_year_month_day(date_str)
        
        assert result is not None
        assert result['year'] == 2023
        assert result['month'] == 1
        assert result['day'] == 15
    
    def test_different_date_formats(self):
        """Test formatter with different date formats."""
        # Test with different format
        formatter = DateFormatter("%d/%m/%Y")
        test_date = datetime(2023, 1, 15)
        result = formatter.format_date(test_date)
        assert result == "15/01/2023"