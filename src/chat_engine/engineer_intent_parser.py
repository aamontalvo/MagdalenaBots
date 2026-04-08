"""
Chat Engine for MagdalenaBot
Natural language processor for engineer requests

Understands requests like:
- "Necesito el análisis de probabilidad mensual para Calamar"
- "Envíame la curva de duración de niveles de Magangué"
- "Quiero ver las frecuencias de excedencia de Barrancabermeja"
"""

import re
from typing import Dict, Optional, List
from dataclasses import dataclass
from enum import Enum


class AnalysisType(Enum):
    MONTHLY_PROBABILITY = "monthly_probability"
    EXCEEDANCE_FREQUENCY = "exceedance_frequency"
    DURATION_CURVE = "duration_curve"
    ALL = "all"


class StationCode(Enum):
    CALAMAR = "29037020"
    MAGANGUE = "25027680"
    BARRANCABERMEJA = "23157030"


@dataclass
class EngineerRequest:
    """Parsed request from engineer"""
    station_code: str
    station_name: str
    analysis_type: AnalysisType
    email: str
    filters: Dict[str, any]
    raw_message: str


class EngineerIntentParser:
    """
    Parser for natural language requests from hydrological engineers.
    
    Recognizes:
    - Station names (Calamar, Magangué, Barrancabermeja)
    - Analysis types (probabilidad, excedencia, duración)
    - Time filters (últimos 5 años, 2020-2024, etc.)
    - Email destinations
    """
    
    STATION_KEYWORDS = {
        'calamar': StationCode.CALAMAR,
        'calamar1': StationCode.CALAMAR,
        'calamar2': StationCode.CALAMAR,
        'calamar3': StationCode.CALAMAR,
        'magangue': StationCode.MAGANGUE,
        'magangué': StationCode.MAGANGUE,
        'magangue1': StationCode.MAGANGUE,
        'magangue2': StationCode.MAGANGUE,
        'barrancabermeja': StationCode.BARRANCABERMEJA,
        'barranca': StationCode.BARRANCABERMEJA,
    }
    
    ANALYSIS_KEYWORDS = {
        # Probability analysis
        'probabilidad': AnalysisType.MONTHLY_PROBABILITY,
        'probabilidades': AnalysisType.MONTHLY_PROBABILITY,
        'mensual': AnalysisType.MONTHLY_PROBABILITY,
        'mes': AnalysisType.MONTHLY_PROBABILITY,
        'kernel': AnalysisType.MONTHLY_PROBABILITY,
        'densidad': AnalysisType.MONTHLY_PROBABILITY,
        'distribucion': AnalysisType.MONTHLY_PROBABILITY,
        'violin': AnalysisType.MONTHLY_PROBABILITY,
        'boxplot': AnalysisType.MONTHLY_PROBABILITY,
        
        # Exceedance frequency
        'excedencia': AnalysisType.EXCEEDANCE_FREQUENCY,
        'excedencias': AnalysisType.EXCEEDANCE_FREQUENCY,
        'frecuencia': AnalysisType.EXCEEDANCE_FREQUENCY,
        'frecuencias': AnalysisType.EXCEEDANCE_FREQUENCY,
        'excedido': AnalysisType.EXCEEDANCE_FREQUENCY,
        'superado': AnalysisType.EXCEEDANCE_FREQUENCY,
        'umbral': AnalysisType.EXCEEDANCE_FREQUENCY,
        
        # Duration curve
        'duracion': AnalysisType.DURATION_CURVE,
        'duración': AnalysisType.DURATION_CURVE,
        'curva de duracion': AnalysisType.DURATION_CURVE,
        'fdc': AnalysisType.DURATION_CURVE,
        'persistencia': AnalysisType.DURATION_CURVE,
        'tiempo': AnalysisType.DURATION_CURVE,
        
        # All
        'todos': AnalysisType.ALL,
        'todo': AnalysisType.ALL,
        'completo': AnalysisType.ALL,
        'general': AnalysisType.ALL,
    }
    
    def __init__(self):
        self.email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
        self.year_pattern = re.compile(r'20\d{2}')  # Years 2000-2099
        
    def parse(self, message: str, default_email: Optional[str] = None) -> EngineerRequest:
        """
        Parse engineer's natural language request
        
        Args:
            message: Raw message from engineer
            default_email: Default email if not found in message
            
        Returns:
            EngineerRequest with parsed parameters
        """
        message_lower = message.lower()
        
        # Extract station
        station_code, station_name = self._extract_station(message_lower)
        if not station_code:
            raise ValueError(
                "No se reconoció la estación. "
                "Use: Calamar, Magangué o Barrancabermeja"
            )
        
        # Extract analysis type
        analysis_type = self._extract_analysis_type(message_lower)
        
        # Extract email
        email = self._extract_email(message) or default_email
        if not email:
            raise ValueError(
                "No se encontró email de destino. "
                "Incluya su email o configure uno por defecto"
            )
        
        # Extract filters
        filters = self._extract_filters(message_lower)
        
        return EngineerRequest(
            station_code=station_code.value,
            station_name=station_name,
            analysis_type=analysis_type,
            email=email,
            filters=filters,
            raw_message=message
        )
    
    def _extract_station(self, message: str) -> tuple:
        """Extract station code and name from message"""
        for keyword, station in self.STATION_KEYWORDS.items():
            if keyword in message:
                # Get station name from enum name
                station_name = station.name.title()
                if station_name == 'Magangue':
                    station_name = 'Magangué'
                return station, station_name
        return None, None
    
    def _extract_analysis_type(self, message: str) -> AnalysisType:
        """Determine which analysis is requested"""
        scores = {
            AnalysisType.MONTHLY_PROBABILITY: 0,
            AnalysisType.EXCEEDANCE_FREQUENCY: 0,
            AnalysisType.DURATION_CURVE: 0,
            AnalysisType.ALL: 0
        }
        
        for keyword, analysis in self.ANALYSIS_KEYWORDS.items():
            if keyword in message:
                scores[analysis] += 1
        
        # Return analysis with highest score, or ALL if no match
        if max(scores.values()) == 0:
            return AnalysisType.ALL
        
        return max(scores, key=scores.get)
    
    def _extract_email(self, message: str) -> Optional[str]:
        """Extract email address from message"""
        match = self.email_pattern.search(message)
        if match:
            return match.group(0)
        return None
    
    def _extract_filters(self, message: str) -> Dict:
        """Extract date/time filters from message"""
        filters = {}
        
        # Extract years
        years = self.year_pattern.findall(message)
        if len(years) >= 2:
            filters['start_year'] = int(years[0])
            filters['end_year'] = int(years[1])
        elif len(years) == 1:
            filters['year'] = int(years[0])
        
        # Extract relative time expressions
        if 'ultimo' in message or 'último' in message:
            if 'año' in message or 'ano' in message:
                filters['last_years'] = 1
            elif any(x in message for x in ['2', 'dos']):
                filters['last_years'] = 2
            elif any(x in message for x in ['3', 'tres']):
                filters['last_years'] = 3
            elif any(x in message for x in ['5', 'cinco']):
                filters['last_years'] = 5
            elif any(x in message for x in ['10', 'diez']):
                filters['last_years'] = 10
        
        return filters
    
    def get_help_text(self) -> str:
        """Return help text for engineers"""
        return """
🌊 **MagdalenaBot - Asistente de Análisis Hidrológico**

Puedes pedirme análisis usando lenguaje natural. Aquí hay ejemplos:

**Estaciones disponibles:**
- Calamar (29037020)
- Magangué (25027680)  
- Barrancabermeja (23157030)

**Tipos de análisis:**

1️⃣ **Probabilidad Mensual** (gráficos de densidad)
   - "Necesito el análisis de probabilidad mensual para Calamar"
   - "Envíame las distribuciones por mes de Magangué"
   - "Quiero ver los boxplots de Barrancabermeja"

2️⃣ **Frecuencia de Excedencia** (probabilidad de superación)
   - "Calcula las frecuencias de excedencia de Calamar"
   - "Necesito curvas de excedencia para Magangué"
   - "Análisis de niveles superados en Barrancabermeja"

3️⃣ **Curva de Duración** (tiempo de persistencia)
   - "Genera la curva de duración de Calamar"
   - "Quiero ver cuánto tiempo persisten los niveles en Magangué"
   - "Análisis de persistencia de Barrancabermeja"

4️⃣ **Todos los análisis**
   - "Envíame todo el análisis de Calamar"
   - "Necesito el informe completo de Magangué"

**Filtros de tiempo (opcional):**
- "últimos 5 años"
- "desde 2020 hasta 2024"
- "solo 2023"

**Ejemplos completos:**
- "Envíame la curva de duración de Calamar a juan@empresa.com"
- "Necesito las frecuencias de excedencia de Magangué de los últimos 3 años"
- "Genera todo el análisis de Barrancabermeja desde 2020"

Los resultados se enviarán por email en formato CSV para que puedas crear tus propios gráficos.
"""


def test_parser():
    """Test the parser with various inputs"""
    parser = EngineerIntentParser()
    
    test_messages = [
        "Necesito el análisis de probabilidad mensual para Calamar a ingeniero@hidro.com",
        "Envíame la curva de duración de niveles de Magangué",
        "Quiero ver las frecuencias de excedencia de Barrancabermeja",
        "Genera todo el análisis de Calamar de los últimos 5 años",
        "Calcula las probabilidades de excedencia para Magangué desde 2020 hasta 2024",
    ]
    
    print(parser.get_help_text())
    print("\n" + "="*60)
    print("PRUEBAS DE PARSING:")
    print("="*60)
    
    for msg in test_messages:
        print(f"\n📝 Input: {msg}")
        try:
            result = parser.parse(msg, default_email="default@magdalenabot.com")
            print(f"   ✅ Station: {result.station_name} ({result.station_code})")
            print(f"   ✅ Analysis: {result.analysis_type.value}")
            print(f"   ✅ Email: {result.email}")
            print(f"   ✅ Filters: {result.filters}")
        except ValueError as e:
            print(f"   ❌ Error: {e}")


if __name__ == '__main__':
    test_parser()
