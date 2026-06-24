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

# Orden geografico (aguas abajo -> aguas arriba).
# Se conserva para referencia y reportes, pero ya NO se usa como restriccion.
GEO_ORDER = {
    "SAN_PEDRITO": 0,
    "CALAMAR": 1,
    "TENERIFE": 2,
    "PLATO": 3,
    "MAGANGUE": 4,
    "BARBOSA": 5,
    "COYONGAL": 6,
    "ARMENIA": 7,
    "RIO_NUEVO": 8,
    "LAS_PALOMAS": 9,
    "LAS_AGUADAS": 10,
    "EL_BANCO": 11,
    "PENONCITO": 12,
    "LA_GLORIA": 13,
    "GAMARRA_AUT": 14,
    "EL_CONTENTO": 15,
    "SITIO_NUEVO": 16,
    "PUERTO_WILCHES": 17,
    "BARRANCABERMEJA": 18,
    "GAMARRA": 19,
    "PUERTO_BERRIO": 20,
    "PUERTO_SALGAR": 21,
    "SAN_PABLO": 22,
    "TEBSA": 23,
}

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
