"""
Modelos Python para MagdalenaBot Database
Proyecto: Analisis Hidrologico Rio Magdalena
"""

from datetime import date, datetime
from typing import Optional, List, Dict
from dataclasses import dataclass, field
from enum import Enum
import json


class Zone(Enum):
    BAJA = "Baja"
    MEDIA = "Media"
    ALTA = "Alta"


class QualityStatus(Enum):
    EXCELLENT = "EXCELLENT"
    GOOD = "GOOD"
    USABLE_WITH_CAUTION = "USABLE_WITH_CAUTION"
    EXCLUDE = "EXCLUDE"
    PENDING = "PENDING"


class ImputationLevel(Enum):
    OBSERVED = 0
    INTERPOLATION = 1
    HEIGHT_HEIGHT = 2
    MULTI_DONOR = 3


@dataclass
class Station:
    """Representa una estacion hidrometrica."""
    station_id: str
    station_name: str
    station_code_ideam: Optional[str] = None
    zone: Optional[Zone] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    elevation_m: Optional[float] = None
    is_automatic: bool = False
    installation_year: Optional[int] = None
    quality_status: QualityStatus = QualityStatus.PENDING
    coverage_pct: Optional[float] = None
    total_records: int = 0
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    exclude_from_analysis: bool = False
    exclusion_reason: Optional[str] = None
    excluded_periods: List[Dict] = field(default_factory=list)
    upstream_station: Optional[str] = None
    downstream_station: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def is_usable_for_frequency_analysis(self) -> bool:
        """Verifica si la estacion es usable para analisis de frecuencia."""
        return (
            self.quality_status in [QualityStatus.EXCELLENT, QualityStatus.GOOD]
            and not self.exclude_from_analysis
            and self.coverage_pct and self.coverage_pct >= 90
        )
    
    def is_usable_with_caution(self) -> bool:
        """Verifica si la estacion es usable con precauciones."""
        return (
            self.quality_status == QualityStatus.USABLE_WITH_CAUTION
            and not self.exclude_from_analysis
        )
    
    def get_excluded_periods_list(self) -> List[tuple]:
        """Retorna lista de tuplas (start_date, end_date) de periodos excluidos."""
        periods = []
        for period in self.excluded_periods:
            start = datetime.strptime(period['start'], '%Y-%m-%d').date()
            end = datetime.strptime(period['end'], '%Y-%m-%d').date()
            periods.append((start, end))
        return periods
    
    def to_dict(self) -> Dict:
        """Convierte a diccionario para JSON/DB."""
        return {
            'station_id': self.station_id,
            'station_name': self.station_name,
            'station_code_ideam': self.station_code_ideam,
            'zone': self.zone.value if self.zone else None,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'elevation_m': self.elevation_m,
            'is_automatic': self.is_automatic,
            'installation_year': self.installation_year,
            'quality_status': self.quality_status.value,
            'coverage_pct': self.coverage_pct,
            'total_records': self.total_records,
            'exclude_from_analysis': self.exclude_from_analysis,
            'exclusion_reason': self.exclusion_reason,
            'excluded_periods': self.excluded_periods
        }


@dataclass
class WaterLevelMeasurement:
    """Representa una medicion de nivel de agua."""
    id: Optional[int] = None
    station_id: str = ""
    station_name: str = ""
    measurement_date: date = field(default_factory=date.today)
    water_level_m: float = 0.0
    is_imputed: bool = False
    imputation_level: ImputationLevel = ImputationLevel.OBSERVED
    quality_flag: str = "VALID"
    donor_station: Optional[str] = None
    r_squared: Optional[float] = None
    model_type: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    @property
    def water_level_cm(self) -> int:
        """Retorna nivel en centimetros."""
        return int(self.water_level_m * 100)
    
    def is_valid(self) -> bool:
        """Verifica si la medicion es valida."""
        return self.quality_flag == "VALID" and self.water_level_m is not None
    
    def is_reliable(self) -> bool:
        """Verifica si la medicion es confiable (observada o bien imputada)."""
        if not self.is_imputed:
            return True
        return self.r_squared is not None and self.r_squared >= 0.75


@dataclass
class ImputationModel:
    """Representa un modelo de imputacion H-H."""
    id: Optional[int] = None
    target_station: str = ""
    donor_station: str = ""
    model_type: str = "linear"  # 'linear' o 'quadratic'
    r_squared: float = 0.0
    rmse: Optional[float] = None
    coef_a: Optional[float] = None  # termino cuadratico o pendiente
    coef_b: Optional[float] = None  # termino lineal o intercepto
    coef_c: Optional[float] = None  # intercepto (solo cuadratico)
    valid_range_min: Optional[float] = None
    valid_range_max: Optional[float] = None
    is_active: bool = True
    is_accepted: bool = False
    calibration_start: Optional[date] = None
    calibration_end: Optional[date] = None
    n_calibration_points: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    
    def predict(self, donor_level: float) -> Optional[float]:
        """Predice nivel para estacion objetivo dado nivel de donante."""
        # Verificar rango de validez
        if self.valid_range_min is not None and donor_level < self.valid_range_min:
            return None
        if self.valid_range_max is not None and donor_level > self.valid_range_max:
            return None
        
        if self.model_type == 'linear':
            # H_target = m * H_donor + b
            return self.coef_a * donor_level + self.coef_b
        elif self.model_type == 'quadratic':
            # H_target = a * H_donor^2 + b * H_donor + c
            return self.coef_a * donor_level**2 + self.coef_b * donor_level + self.coef_c
        
        return None
    
    def is_acceptable(self) -> bool:
        """Verifica si el modelo cumple criterio de aceptacion (R² >= 0.75)."""
        return self.r_squared >= 0.75


@dataclass
class ValidationResult:
    """Resultado de validacion automatica de una estacion."""
    id: Optional[int] = None
    station_id: str = ""
    validation_date: datetime = field(default_factory=datetime.now)
    check_outliers_status: str = "OK"
    check_duration_jumps_status: str = "OK"
    check_distribution_status: str = "OK"
    check_spatial_coherence_status: str = "OK"
    n_outliers: int = 0
    n_duration_jumps: int = 0
    n_spatial_anomalies: int = 0
    quality_score: int = 100
    details: Dict = field(default_factory=dict)
    alerts: List[str] = field(default_factory=list)
    
    def has_critical_issues(self) -> bool:
        """Verifica si hay problemas criticos."""
        return (
            self.check_outliers_status == "CRITICAL" or
            self.check_duration_jumps_status == "CRITICAL" or
            self.check_distribution_status == "CRITICAL"
        )
    
    def has_warnings(self) -> bool:
        """Verifica si hay advertencias."""
        return (
            self.check_outliers_status == "WARNING" or
            self.check_duration_jumps_status == "WARNING" or
            self.check_distribution_status == "WARNING"
        )


# Datos de estaciones segun diagnostico
STATIONS_CATALOG = {
    # EXCELLENT - Usar sin restricciones
    'CALAMAR': Station(
        station_id='CALAMAR',
        station_name='Calamar',
        station_code_ideam='29037020',
        zone=Zone.BAJA,
        quality_status=QualityStatus.EXCELLENT,
        coverage_pct=99.4,
        start_date=date(1967, 1, 1),
        installation_year=1967
    ),
    'BARBOSA': Station(
        station_id='BARBOSA',
        station_name='Barbosa',
        station_code_ideam='25027530',
        zone=Zone.BAJA,
        quality_status=QualityStatus.EXCELLENT,
        coverage_pct=99.8,
        start_date=date(1973, 1, 1),
        installation_year=1973
    ),
    'MAGANGUE': Station(
        station_id='MAGANGUE',
        station_name='Magangue',
        station_code_ideam='25027680',
        zone=Zone.BAJA,
        quality_status=QualityStatus.EXCELLENT,
        coverage_pct=99.8,
        start_date=date(1973, 1, 1),
        installation_year=1973
    ),
    'EL_BANCO': Station(
        station_id='EL_BANCO',
        station_name='El Banco',
        station_code_ideam='25027020',
        zone=Zone.MEDIA,
        quality_status=QualityStatus.EXCELLENT,
        coverage_pct=98.2,
        start_date=date(1972, 1, 1),
        installation_year=1972
    ),
    
    # EXCLUDE - No usar
    'ARMENIA': Station(
        station_id='ARMENIA',
        station_name='Armenia',
        station_code_ideam='25027360',
        zone=Zone.MEDIA,
        quality_status=QualityStatus.EXCLUDE,
        coverage_pct=77.9,
        exclude_from_analysis=True,
        exclusion_reason='Sin donante confiable. Confluencia con Rio Cauca. Correlacion maxima r=0.72'
    ),
    'GAMARRA_AUT': Station(
        station_id='GAMARRA_AUT',
        station_name='Gamarra Automatica',
        station_code_ideam='23217080',
        zone=Zone.ALTA,
        is_automatic=True,
        quality_status=QualityStatus.EXCLUDE,
        coverage_pct=93.0,
        exclude_from_analysis=True,
        exclusion_reason='Serie corta (2013-2025). Estacion automatica con protocolos diferentes.',
        start_date=date(2013, 1, 1),
        installation_year=2013
    ),
    'SAN_PEDRITO': Station(
        station_id='SAN_PEDRITO',
        station_name='San Pedrito',
        station_code_ideam='29047070',
        zone=Zone.BAJA,
        quality_status=QualityStatus.EXCLUDE,
        coverage_pct=45.4,
        exclude_from_analysis=True,
        exclusion_reason='Estacion terminal. Imputacion espacial inviable.',
        start_date=date(1979, 1, 1),
        installation_year=1979
    ),
}


def get_stations_by_quality(status: QualityStatus) -> List[Station]:
    """Retorna estaciones filtradas por estado de calidad."""
    return [s for s in STATIONS_CATALOG.values() if s.quality_status == status]


def get_usable_stations() -> List[Station]:
    """Retorna estaciones usables para analisis (EXCELLENT + GOOD)."""
    return [s for s in STATIONS_CATALOG.values() 
            if s.is_usable_for_frequency_analysis()]


def get_excluded_stations() -> List[Station]:
    """Retorna estaciones excluidas."""
    return [s for s in STATIONS_CATALOG.values() 
            if s.exclude_from_analysis]
