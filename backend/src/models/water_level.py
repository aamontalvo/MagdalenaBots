"""Data models for water level measurements."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class WaterLevelMeasurement:
    """Data model for a single water level measurement."""
    
    station_code: str
    station_name: str
    variable: str
    parameter: str
    date: datetime
    unit: str
    value: float
    approval_level: str
    
    def to_dict(self) -> dict:
        """Convert measurement to dictionary."""
        return {
            'CodigoEstacion': self.station_code,
            'NombreEstacion': self.station_name,
            'Variable': self.variable,
            'Parametro': self.parameter,
            'Fecha': self.date.strftime('%Y-%m-%d'),
            'Unidad': self.unit,
            'Valor': self.value,
            'NivelAprobacion': self.approval_level
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> Optional['WaterLevelMeasurement']:
        """Create measurement from dictionary."""
        try:
            from dateutil import parser as date_parser
            
            return cls(
                station_code=data['CodigoEstacion'],
                station_name=data['NombreEstacion'],
                variable=data['Variable'],
                parameter=data['Parametro'],
                date=date_parser.parse(data['Fecha']),
                unit=data['Unidad'],
                value=float(data['Valor']),
                approval_level=data['NivelAprobacion']
            )
        except (KeyError, ValueError, TypeError) as e:
            from src.utils.logger import logger
            logger.error(f"Failed to create WaterLevelMeasurement from dict: {e}")
            return None


@dataclass
class DataQualityReport:
    """Report on data quality and validation results."""
    
    total_records: int
    valid_records: int
    invalid_records: int
    missing_dates: int
    duplicate_records: int
    outlier_records: int
    validation_errors: list[str]
    processing_time: float
    
    def get_validation_rate(self) -> float:
        """Calculate the percentage of valid records."""
        if self.total_records == 0:
            return 0.0
        return (self.valid_records / self.total_records) * 100
    
    def to_dict(self) -> dict:
        """Convert report to dictionary."""
        return {
            'total_records': self.total_records,
            'valid_records': self.valid_records,
            'invalid_records': self.invalid_records,
            'missing_dates': self.missing_dates,
            'duplicate_records': self.duplicate_records,
            'outlier_records': self.outlier_records,
            'validation_rate': self.get_validation_rate(),
            'validation_errors': self.validation_errors,
            'processing_time': self.processing_time
        }