"""Date formatting and validation utilities."""

from datetime import datetime
from typing import Optional, Union

import pandas as pd
from dateutil import parser as date_parser

from src.utils.logger import logger


class DateFormatter:
    """Utility class for date formatting and validation."""
    
    def __init__(self, date_format: str = "%Y-%m-%d"):
        """Initialize the date formatter with a specific format."""
        self.date_format = date_format
        
    def parse_date(self, date_string: str) -> Optional[datetime]:
        """
        Parse a date string into a datetime object.
        
        Args:
            date_string: String representation of date/time
            
        Returns:
            datetime object or None if parsing fails
        """
        try:
            # Handle various date formats
            if isinstance(date_string, str):
                # Remove time portion if present (HH:MM:SS)
                if ' ' in date_string:
                    date_part = date_string.split(' ')[0]
                else:
                    date_part = date_string
                    
                # Parse the date
                parsed_date = date_parser.parse(date_part)
                return parsed_date
            elif isinstance(date_string, datetime):
                return date_string
            elif isinstance(date_string, pd.Timestamp):
                return date_string.to_pydatetime()
            else:
                logger.warning(f"Unsupported date type: {type(date_string)}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to parse date '{date_string}': {e}")
            return None
    
    def format_date(self, date_obj: Union[datetime, pd.Timestamp, str]) -> Optional[str]:
        """
        Format a date object to the specified format.
        
        Args:
            date_obj: Date object to format
            
        Returns:
            Formatted date string or None if formatting fails
        """
        try:
            if isinstance(date_obj, str):
                # First parse the string, then format
                parsed = self.parse_date(date_obj)
                if parsed:
                    return parsed.strftime(self.date_format)
                return None
            elif isinstance(date_obj, (datetime, pd.Timestamp)):
                if isinstance(date_obj, pd.Timestamp):
                    date_obj = date_obj.to_pydatetime()
                return date_obj.strftime(self.date_format)
            else:
                logger.warning(f"Unsupported date object type: {type(date_obj)}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to format date '{date_obj}': {e}")
            return None
    
    def validate_date_range(self, start_date: str, end_date: str) -> bool:
        """
        Validate that start_date is before end_date.
        
        Args:
            start_date: Start date string
            end_date: End date string
            
        Returns:
            True if valid, False otherwise
        """
        try:
            start = self.parse_date(start_date)
            end = self.parse_date(end_date)
            
            if start and end:
                return start <= end
            return False
            
        except Exception as e:
            logger.error(f"Date range validation failed: {e}")
            return False
    
    def is_valid_date_string(self, date_string: str) -> bool:
        """
        Check if a string is a valid date.
        
        Args:
            date_string: String to validate
            
        Returns:
            True if valid date string, False otherwise
        """
        try:
            parsed = self.parse_date(date_string)
            return parsed is not None
        except Exception:
            return False
    
    def extract_year_month_day(self, date_string: str) -> Optional[dict]:
        """
        Extract year, month, day components from a date string.
        
        Args:
            date_string: Date string to extract from
            
        Returns:
            Dictionary with year, month, day or None if parsing fails
        """
        try:
            parsed = self.parse_date(date_string)
            if parsed:
                return {
                    'year': parsed.year,
                    'month': parsed.month,
                    'day': parsed.day
                }
            return None
            
        except Exception as e:
            logger.error(f"Failed to extract date components from '{date_string}': {e}")
            return None


# Global date formatter instance
date_formatter = DateFormatter()