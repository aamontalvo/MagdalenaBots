"""
Configuracion del pipeline de imputacion.
Modificar solo las constantes de esta archivo para adaptar a otros proyectos.
"""

# ============================================================
# UMBRALES Y PARAMETROS
# ============================================================
R2_UMBRAL = 0.75           # R2 minimo para aceptar modelo H-H
MIN_N_TRAIN = 50           # Minimo de puntos concurrentes para entrenar H-H
L1_MAX_GAP = 3             # Maximo gap en dias para interpolacion local
L1_KERNEL = {-2: 0.1, -1: 0.2, 0: 0.4, 1: 0.2, 2: 0.1}  # Pesos interpolacion

# ============================================================
# ORDEN GEOGRAFICO (aguas abajo -> aguas arriba)
# La regla H-H exige: donante (independiente) debe estar aguas ARRIBA del objetivo.
# Es decir: GEO_ORDER[donante] > GEO_ORDER[objetivo]
# ============================================================
GEO_ORDER = {
    'SAN_PEDRITO': 0,
    'CALAMAR': 1,
    'TENERIFE': 2,
    'PLATO': 3,
    'MAGANGUE': 4,
    'BARBOSA': 5,
    'COYONGAL': 6,
    'ARMENIA': 7,
    'RIO_NUEVO': 8,
    'LAS_PALOMAS': 9,
    'LAS_AGUADAS': 10,
    'EL_BANCO': 11,
    'PENONCITO': 12,
    'LA_GLORIA': 13,
    'GAMARRA_AUT': 14,
    'EL_CONTENTO': 15,
    'SITIO_NUEVO': 16,
    'PUERTO_WILCHES': 17,
}

# Estaciones descartadas por inhomogeneidad (se completan pero no se usan en analisis)
DESCARTADAS = ['ARMENIA', 'TENERIFE', 'BARBOSA', 'SITIO_NUEVO']

# ============================================================
# FORMATO DE ENTRADA (configurable)
# ============================================================
# Nombres de columnas esperados en el CSV de entrada
INPUT_COL_STATION = 'station'
INPUT_COL_LEVEL = 'level'
INPUT_COL_DATE = 'date'
INPUT_DATE_FORMAT = '%d-%m-%Y'

# Nombres estandarizados internos
COL_STATION = 'NombreEstacion'
COL_LEVEL = 'Cota'
COL_DATE = 'Fecha'
