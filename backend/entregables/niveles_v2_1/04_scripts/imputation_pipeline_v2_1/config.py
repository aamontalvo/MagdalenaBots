"""
config.py
=========

Configuracion del pipeline de imputacion v2.1.
"""

# Umbrales y parametros
R2_UMBRAL = 0.75
MIN_N_TRAIN = 50
L1_MAX_GAP = 3
L1_KERNEL = {-2: 0.1, -1: 0.2, 0: 0.4, 1: 0.2, 2: 0.1}

# Orden geografico (aguas abajo -> aguas arriba), segun listado IDEAM.
GEO_ORDER = {
    "TEBSA": 0,
    "SAN_PEDRITO": 1,
    "CALAMAR": 2,
    "TENERIFE": 3,
    "PLATO": 4,
    "MAGANGUE": 5,
    "BARBOSA": 6,
    "COYONGAL": 7,
    "ARMENIA": 8,
    "RIO_NUEVO": 9,
    "LAS_PALOMAS": 10,
    "LAS_AGUADAS": 11,
    "EL_BANCO": 12,
    "PENONCITO": 13,
    "LA_GLORIA": 14,
    "GAMARRA": 15,
    "GAMARRA_AUT": 16,
    "EL_CONTENTO": 17,
    "SITIO_NUEVO": 18,
    "PUERTO_WILCHES": 19,
    "BARRANCABERMEJA": 20,
    "SAN_PABLO": 21,
    "PUERTO_BERRIO": 22,
    "PUERTO_SALGAR": 23,
}

# Division en zonas para figuras globales (indices de GEO_ORDER)
ZONA_BAJA = ("TEBSA", "COYONGAL")      # 0 - 7
ZONA_MEDIA = ("ARMENIA", "PENONCITO")  # 8 - 13
ZONA_ALTA = ("LA_GLORIA", "PUERTO_SALGAR")  # 14 - 23

# Nombres para visualizacion en figuras (sin guiones bajos, sin codigos)
DISPLAY_NAMES = {
    "TEBSA": "TEBSA",
    "SAN_PEDRITO": "San Pedrito",
    "CALAMAR": "Calamar",
    "TENERIFE": "Tenerife",
    "PLATO": "Plato",
    "MAGANGUE": "Magangué",
    "BARBOSA": "Barbosa",
    "COYONGAL": "Coyongal",
    "ARMENIA": "Armenia",
    "RIO_NUEVO": "Río Nuevo",
    "LAS_PALOMAS": "Las Palomas",
    "LAS_AGUADAS": "Las Aguadas",
    "EL_BANCO": "El Banco",
    "PENONCITO": "Peñoncito",
    "LA_GLORIA": "La Gloria",
    "GAMARRA": "Gamarra",
    "GAMARRA_AUT": "Gamarra Aut.",
    "EL_CONTENTO": "El Contento",
    "PUERTO_WILCHES": "Puerto Wilches",
    "BARRANCABERMEJA": "Barrancabermeja",
    "SITIO_NUEVO": "Sitio Nuevo",
    "SAN_PABLO": "San Pablo",
    "PUERTO_BERRIO": "Puerto Berrío",
    "PUERTO_SALGAR": "Puerto Salgar",
}

# Codigos oficiales IDEAM por estacion
STATION_CODES = {
    "TEBSA": "29047000",
    "SAN_PEDRITO": "29047070",
    "CALAMAR": "29037020",
    "TENERIFE": "29017010",
    "PLATO": "25027450",
    "MAGANGUE": "25027680",
    "BARBOSA": "25027530",
    "COYONGAL": "25027930",
    "ARMENIA": "25027360",
    "RIO_NUEVO": "25027630",
    "LAS_PALOMAS": "25027390",
    "LAS_AGUADAS": "25027490",
    "EL_BANCO": "25027020",
    "PENONCITO": "25027330",
    "LA_GLORIA": "23217060",
    "GAMARRA": "23217020",
    "GAMARRA_AUT": "23217080",
    "EL_CONTENTO": "23217030",
    "PUERTO_WILCHES": "23187010",
    "BARRANCABERMEJA": "23207040",
    "SITIO_NUEVO": "23187280",
    "SAN_PABLO": "23157030",
    "PUERTO_BERRIO": "23097030",
    "PUERTO_SALGAR": "23037010",
}


def display_name(station, with_code=False):
    """Retorna nombre de visualizacion de una estacion."""
    name = DISPLAY_NAMES.get(station, station.replace("_", " ").title())
    if with_code:
        code = STATION_CODES.get(station, "")
        return f"{name} ({code})" if code else name
    return name


def geo_sorted(stations):
    """Ordena estaciones geograficamente (aguas abajo -> aguas arriba)."""
    return sorted(stations, key=lambda s: GEO_ORDER.get(s, 999))

# Estaciones descartadas por inhomogeneidad (se completan pero no se exige 100%)
DESCARTADAS = ["ARMENIA", "TENERIFE", "BARBOSA", "SITIO_NUEVO"]

# Formato de entrada
INPUT_COL_STATION = "station"
INPUT_COL_LEVEL = "level"
INPUT_COL_DATE = "date"
INPUT_DATE_FORMAT = "%Y-%m-%d"

# Nombres estandarizados internos
COL_STATION = "NombreEstacion"
COL_LEVEL = "Cota"
COL_DATE = "Fecha"

# Rango oficial por estacion (se carga desde CSV externo)
RANGES_CSV_NAME = "resumen_rangos_estaciones.csv"
