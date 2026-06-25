# Reporte de Validacion - Imputacion v2.1+

## Resumen ejecutivo

- **Registros totales:** 394,772
- **Datos originales:** 339,937 (86.11%)
- **Imputados L1:** 1,222 (0.31%)
- **Imputados L2:** 36,758 (9.31%)
- **Imputados L3:** 16,855 (4.27%)

## Modelos H-H seleccionados

| Objetivo | Donante | R2 | n_train |
|----------|---------|-----|---------|
| ARMENIA | RIO_NUEVO | 0.8512 | 11599 |
| BARBOSA | SAN_PEDRITO | 0.9182 | 12324 |
| BARRANCABERMEJA | PUERTO_WILCHES | 0.8910 | 7764 |
| CALAMAR | SAN_PEDRITO | 0.9958 | 16270 |
| COYONGAL | SAN_PEDRITO | 0.8938 | 14469 |
| EL_BANCO | LAS_AGUADAS | 0.9752 | 18103 |
| EL_CONTENTO | LA_GLORIA | 0.8022 | 8576 |
| GAMARRA | GAMARRA_AUT | 0.9905 | 193 |
| GAMARRA_AUT | GAMARRA | 0.9902 | 193 |
| LAS_AGUADAS | EL_BANCO | 0.9741 | 18103 |
| LAS_PALOMAS | EL_BANCO | 0.9215 | 15280 |
| LA_GLORIA | GAMARRA | 0.8681 | 6229 |
| MAGANGUE | TENERIFE | 0.9446 | 12373 |
| PENONCITO | EL_BANCO | 0.8971 | 16565 |
| PLATO | TEBSA | 0.9352 | 2823 |
| PUERTO_BERRIO | BARRANCABERMEJA | 0.8349 | 10242 |
| PUERTO_WILCHES | SAN_PABLO | 0.9335 | 5293 |
| RIO_NUEVO | LAS_AGUADAS | 0.9157 | 13956 |
| SAN_PABLO | PUERTO_WILCHES | 0.9297 | 5293 |
| SAN_PEDRITO | CALAMAR | 0.9958 | 16270 |
| SITIO_NUEVO | PUERTO_WILCHES | 0.8535 | 6919 |
| TEBSA | CALAMAR | 0.9520 | 2923 |
| TENERIFE | CALAMAR | 0.9626 | 14089 |

## Cobertura por estacion

| Estacion | Inicio | Fin | Dias | Cobertura % | L1 | L2 | L3 | NaN restantes |
|----------|--------|-----|------|-------------|----|----|----|---------------|
| ARMENIA | 1973-02-01 | 2025-10-15 | 19237 | 99.85 | 44 | 2589 | 1644 | 28 |
| BARBOSA | 1973-10-01 | 2024-12-20 | 18696 | 96.46 | 27 | 3658 | 0 | 661 |
| BARRANCABERMEJA | 1971-01-01 | 2025-12-31 | 20075 | 95.65 | 62 | 23 | 0 | 874 |
| CALAMAR | 1967-02-01 | 2025-12-31 | 21500 | 93.34 | 13 | 86 | 83 | 1431 |
| COYONGAL | 1975-03-01 | 2025-12-27 | 18552 | 100.0 | 44 | 1860 | 1015 | 0 |
| EL_BANCO | 1972-10-01 | 2025-12-31 | 19437 | 99.57 | 21 | 626 | 0 | 84 |
| EL_CONTENTO | 1974-09-01 | 2025-12-31 | 18737 | 100.0 | 98 | 2506 | 3441 | 0 |
| GAMARRA | 1991-02-07 | 2018-10-29 | 10120 | 100.0 | 44 | 1822 | 1348 | 0 |
| GAMARRA_AUT | 2013-01-01 | 2025-12-31 | 4745 | 95.13 | 18 | 0 | 99 | 231 |
| LAS_AGUADAS | 1973-04-01 | 2025-08-31 | 19133 | 100.0 | 19 | 365 | 0 | 0 |
| LAS_PALOMAS | 1973-08-01 | 2025-06-30 | 18949 | 100.0 | 72 | 3188 | 0 | 0 |
| LA_GLORIA | 1991-04-21 | 2025-12-31 | 12665 | 97.13 | 57 | 1136 | 0 | 363 |
| MAGANGUE | 1973-04-01 | 2025-12-30 | 19254 | 100.0 | 74 | 1761 | 1645 | 0 |
| PENONCITO | 1972-10-01 | 2025-06-30 | 19253 | 99.74 | 61 | 2117 | 0 | 51 |
| PLATO | 1976-06-01 | 2025-12-11 | 18079 | 100.0 | 81 | 115 | 1721 | 0 |
| PUERTO_BERRIO | 1997-01-01 | 2025-11-10 | 10534 | 100.0 | 20 | 217 | 0 | 0 |
| PUERTO_SALGAR | 1960-01-01 | 2025-12-31 | 23787 | 97.62 | 53 | 0 | 0 | 566 |
| PUERTO_WILCHES | 2003-05-07 | 2025-09-11 | 8158 | 98.47 | 36 | 191 | 0 | 125 |
| RIO_NUEVO | 1974-10-01 | 2025-10-23 | 18638 | 100.0 | 85 | 4347 | 0 | 0 |
| SAN_PABLO | 1977-08-01 | 2025-12-31 | 17673 | 100.0 | 65 | 2508 | 4806 | 0 |
| SAN_PEDRITO | 1979-01-01 | 2025-12-31 | 17155 | 99.9 | 33 | 740 | 0 | 18 |
| SITIO_NUEVO | 1979-03-01 | 2025-12-31 | 17096 | 100.0 | 87 | 870 | 1053 | 0 |
| TEBSA | 2014-01-02 | 2025-08-01 | 4227 | 100.0 | 77 | 1172 | 0 | 0 |
| TENERIFE | 1973-10-01 | 2025-12-31 | 19072 | 99.98 | 31 | 4861 | 0 | 4 |

## Validaciones

- **Violaciones de rango de cota:** 0
- **Registros fuera de rango temporal oficial:** 0
- **Saltos temporales anomalos:** 0
- **Pares con baja coherencia espacial (r < 0.7):** 88
- **Correlacion espacial minima:** 0.2295

## Comparacion con corrida anterior (estudiantes)

- **Registros comparables:** 292,885
- **Diferencia media absoluta:** 0.3220 m
- **Diferencia maxima absoluta:** 3.8058 m

## Archivos generados

- `Datos_Imputados.csv`
- `Datos_Imputados_sin_L3.csv`
- `Resumen_Imputacion.csv`
- `Tabla_Modelos_HH.csv`
- `Tabla_Modelos_HH_Seleccionados.csv`
- `Tabla_Modelos_L3.csv`
- `validacion_violaciones_rango.csv`
- `validacion_violaciones_rango_temporal.csv`
- `validacion_saltos_temporales.csv`
- `validacion_coherencia_espacial.csv`
- `figura_cobertura_imputacion.png`
- `figura_series_temporales.png`
- `figura_heatmap_nulos_antes_despues.png`