# Zonificación de Estaciones - Río Magdalena

**Fecha de actualización:** 2026-03-06  
**Versión:** 2.0 (actualizada según nueva clasificación)

## Orden Geográfico (Aguas Abajo → Aguas Arriba)

### Zona Baja (6 estaciones)
Estaciones aguas abajo de la confluencia con el río Cauca.

| Orden | Estación | Código IDEAM | Inicio | Observaciones |
|-------|----------|--------------|--------|---------------|
| 1 | Calamar | 29037020 | 1967 | Estación más antigua |
| 2 | Tenerife | 29017010 | 1973 | - |
| 3 | Plato | 25027450 | 1976 | - |
| 4 | Magangue | 25027680 | 1973 | - |
| 5 | Barbosa | 25027530 | 1973 | - |
| 6 | Coyongal | 25027930 | 1975 | Última de zona baja |

### Zona Media (6 estaciones)
Primera estación aguas arriba de la confluencia con el Cauca hasta Peñoncito.

| Orden | Estación | Código IDEAM | Inicio | Observaciones |
|-------|----------|--------------|--------|---------------|
| 7 | Armenia | 25027360 | 1973 | Primera aguas arriba del Cauca |
| 8 | Rio Nuevo | 25027630 | 1974 | - |
| 9 | Las Palomas | 25027390 | 1973 | - |
| 10 | Las Aguadas | 25027490 | 1973 | Excelente cobertura (96.8%) |
| 11 | El Banco | 25027020 | 1972 | - |
| 12 | Penoncito | 25027330 | 1972 | Última de zona media |

### Zona Alta (5 estaciones)
Tramo alto del río Magdalena.

| Orden | Estación | Código IDEAM | Inicio | Observaciones |
|-------|----------|--------------|--------|---------------|
| 13 | La Gloria | 23217060 | 1991 | - |
| 14 | Gamarra Aut | 23217080 | 2013 | Estación automática, registro más reciente |
| 15 | El Contento | 23217030 | 1974 | Mayor variabilidad en cobertura |
| 16 | Sitio Nuevo | 23187280 | 1979 | Cota anómala (~50 msnm) - ubicada en zona de remanso |
| 17 | Puerto Wilches | 23187010 | 2003 | Mayor cota promedio (63.68 msnm) |

**Nota:** Según especificación del usuario, Sitio Nuevo se incluye en Zona Alta a pesar de su cota anómala (~50 msnm), posiblemente por su ubicación en zona de remanso.

## Estaciones Excluidas de la Nueva Zonificación

| Estación | Código IDEAM | Motivo |
|----------|--------------|--------|
| San Pedrito | 29047070 | - |

## Rangos de Cotas por Zona

| Zona | Rango de Cotas (msnm) | Características |
|------|----------------------|-----------------|
| Baja | 5.26 - 17.90 | Influencia de cienagas y planicie aluvial |
| Media | 19.96 - 26.50 | Zona de transición, mayor variabilidad |
| Alta | 33.00 - 63.68 | Menor variabilidad, niveles más controlados |

## Cobertura de Datos por Zona

| Zona | Cobertura Promedio | Mejor Estación | Peor Estación |
|------|-------------------|----------------|---------------|
| Baja | 85.1% | Calamar (97.6%) | Tenerife (71.9%) |
| Media | 84.5% | Las Aguadas (96.8%) | Rio Nuevo (74.8%) |
| Alta | 83.5% | Puerto Wilches (92.9%) | El Contento (69.5%) |

## Uso en Código Python

```python
# Orden geográfico para análisis
GEOGRAPHIC_ORDER = [
    # Zona Baja
    'CALAMAR', 'TENERIFE', 'PLATO', 'MAGANGUE', 'BARBOSA', 'COYONGAL',
    # Zona Media
    'ARMENIA', 'RIO_NUEVO', 'LAS_PALOMAS', 'LAS_AGUADAS', 'EL_BANCO', 'PENONCITO',
    # Zona Alta
    'LA_GLORIA', 'GAMARRA_AUT', 'EL_CONTENTO', 'SITIO_NUEVO', 'PUERTO_WILCHES',
]

# Límites de zonas para visualización
ZONE_BOUNDARIES = {
    'zona_baja_end': 5,      # Índice de Coyongal
    'zona_media_end': 11,    # Índice de Penoncito
}
```

## Notas Importantes

1. **Sitio Nuevo**: Presenta una cota promedio de ~50.67 msnm, notablemente superior a las demás estaciones de la zona alta. Esto puede deberse a su ubicación en una zona de remanso o diferencias topográficas locales.

2. **Gamarra vs Gamarra Aut**: Solo se incluye Gamarra Aut (estación automática) con código 23217080. La estación Gamarra manual no está disponible en los datos.

3. **San Pedrito**: Excluido de la nueva zonificación aunque existe en los datos raw (código 29047070).
