# Auditoria de 12 estaciones - Imputacion v2.1

## Estaciones seleccionadas

- **10 de alta cobertura:** LAS_AGUADAS, LAS_PALOMAS, PUERTO_BERRIO, RIO_NUEVO, TEBSA, EL_BANCO, SAN_PEDRITO, TENERIFE, CALAMAR, PENONCITO
- **1 de menor cobertura:** SAN_PABLO
- **1 nueva:** PUERTO_BERRIO

## Rangos oficiales usados en la auditoria

| Estacion | Inicio oficial | Fin oficial |
|----------|----------------|-------------|
| LAS_AGUADAS | 1973-04-01 | 2025-08-31 |
| LAS_PALOMAS | 1973-08-01 | 2025-06-30 |
| PUERTO_BERRIO | 1997-01-01 | 2025-11-10 |
| RIO_NUEVO | 1974-10-01 | 2025-10-23 |
| TEBSA | 2014-01-02 | 2025-08-01 |
| EL_BANCO | 1972-10-01 | 2025-12-31 |
| SAN_PEDRITO | 1979-01-01 | 2025-12-31 |
| TENERIFE | 1973-10-01 | 2025-12-31 |
| CALAMAR | 1967-02-01 | 2025-12-31 |
| PENONCITO | 1972-10-01 | 2025-06-30 |
| SAN_PABLO | 1977-08-01 | 2025-12-31 |
| LA_GLORIA | 1991-04-21 | 2025-12-31 |

## Resumen agregado

| Estacion | Inicio | Fin | Dias | Original | L1 | L2 | NaN | Cobertura % | Donante H-H | R2 |
|----------|--------|-----|------|----------|----|----|-----|-------------|-------------|-----|
| LAS_AGUADAS | 1973-04-01 | 2025-08-31 | 19133 | 18749 | 19 | 365 | 0 | 100.0 | EL_BANCO | 0.9741 |
| LAS_PALOMAS | 1973-08-01 | 2025-06-30 | 18949 | 15689 | 72 | 3188 | 0 | 100.0 | EL_BANCO | 0.9215 |
| PUERTO_BERRIO | 1997-01-01 | 2025-11-10 | 10534 | 10297 | 20 | 217 | 0 | 100.0 | BARRANCABERMEJA | 0.8349 |
| RIO_NUEVO | 1974-10-01 | 2025-10-23 | 18638 | 14206 | 85 | 4347 | 0 | 100.0 | LAS_AGUADAS | 0.9157 |
| TEBSA | 2014-01-02 | 2025-08-01 | 4227 | 2978 | 77 | 1172 | 0 | 100.0 | CALAMAR | 0.952 |
| EL_BANCO | 1972-10-01 | 2025-12-31 | 19437 | 18790 | 21 | 626 | 84 | 99.57 | LAS_AGUADAS | 0.9752 |
| SAN_PEDRITO | 1979-01-01 | 2025-12-31 | 17155 | 16382 | 33 | 740 | 18 | 99.9 | CALAMAR | 0.9958 |
| TENERIFE | 1973-10-01 | 2025-12-31 | 19072 | 14180 | 31 | 4861 | 4 | 99.98 | CALAMAR | 0.9626 |
| CALAMAR | 1967-02-01 | 2025-12-31 | 21500 | 21318 | 13 | 86 | 1431 | 93.34 | SAN_PEDRITO | 0.9958 |
| PENONCITO | 1972-10-01 | 2025-06-30 | 19253 | 17075 | 61 | 2117 | 51 | 99.74 | EL_BANCO | 0.8971 |
| SAN_PABLO | 1977-08-01 | 2025-12-31 | 17673 | 10294 | 65 | 2508 | 0 | 100.0 | PUERTO_WILCHES | 0.9297 |
| LA_GLORIA | 1991-04-21 | 2025-12-31 | 12665 | 11472 | 57 | 1136 | 363 | 97.13 | GAMARRA | 0.8681 |

## Percentiles: crudo vs imputado

| Estacion | n crudo | media crudo | p5 crudo | p95 crudo | n imp | media imp | p5 imp | p95 imp |
|----------|---------|-------------|----------|-----------|-------|-----------|--------|---------|
| LAS_AGUADAS | 18749 | 24.6717 | 22.155 | 26.865 | 19133 | 24.6486 | 22.105 | 26.865 |
| LAS_PALOMAS | 15689 | 22.7131 | 20.6498 | 24.391 | 18949 | 22.5493 | 20.2953 | 24.317 |
| PUERTO_BERRIO | 10297 | 108.2743 | 107.266 | 109.4462 | 10534 | 108.2801 | 107.276 | 109.4477 |
| RIO_NUEVO | 14206 | 21.6027 | 19.516 | 23.255 | 18638 | 21.477 | 19.359 | 23.186 |
| TEBSA | 2978 | 1.013 | 0.31 | 1.8856 | 4227 | 0.9894 | 0.3223 | 1.8764 |
| EL_BANCO | 18706 | 25.8736 | 23.436 | 28.1555 | 19353 | 25.87 | 23.4358 | 28.164 |
| SAN_PEDRITO | 16364 | 5.2125 | 2.21 | 7.94 | 17137 | 5.1996 | 2.218 | 7.9 |
| TENERIFE | 14176 | 8.9458 | 5.829 | 11.96 | 19068 | 8.5846 | 5.1662 | 11.83 |
| CALAMAR | 19887 | 5.2804 | 2.17 | 7.9649 | 20069 | 5.2681 | 2.165 | 7.96 |
| PENONCITO | 17024 | 26.5228 | 24.05 | 28.88 | 19202 | 26.4227 | 23.814 | 28.876 |
| SAN_PABLO | 10294 | 97.71 | 96.0 | 99.33 | 17673 | 97.6383 | 95.99 | 99.2144 |
| LA_GLORIA | 11109 | 33.0931 | 31.0682 | 35.223 | 12302 | 32.9842 | 30.933 | 35.173 |

## Medias mensuales: diferencia imputado - crudo

| Estacion | Ene | Feb | Mar | Abr | May | Jun | Jul | Ago | Sep | Oct | Nov | Dic |
|----------|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|
| LAS_AGUADAS | -0.049 | -0.061 | -0.031 | -0.002 | -0.001 | 0.000 | -0.012 | -0.002 | -0.013 | -0.004 | -0.003 | 0.002 |
| LAS_PALOMAS | -0.189 | -0.167 | -0.179 | -0.072 | -0.022 | -0.046 | -0.036 | -0.117 | -0.129 | -0.027 | -0.017 | -0.022 |
| PUERTO_BERRIO | -0.001 | 0.014 | 0.017 | 0.012 | 0.017 | 0.008 | 0.006 | 0.004 | -0.004 | -0.000 | 0.001 | -0.014 |
| RIO_NUEVO | -0.220 | -0.126 | -0.097 | 0.011 | -0.053 | -0.090 | -0.072 | -0.051 | -0.025 | 0.017 | -0.008 | -0.045 |
| TEBSA | -0.025 | -0.006 | 0.003 | -0.021 | 0.006 | 0.006 | -0.002 | -0.017 | -0.009 | 0.020 | -0.026 | -0.005 |
| EL_BANCO | 0.018 | 0.018 | -0.028 | 0.002 | 0.012 | 0.001 | 0.013 | -0.017 | -0.018 | 0.025 | 0.021 | 0.044 |
| SAN_PEDRITO | 0.002 | -0.033 | -0.011 | -0.014 | -0.030 | -0.021 | -0.031 | -0.004 | 0.008 | 0.008 | 0.002 | 0.016 |
| TENERIFE | -0.761 | -0.308 | -0.247 | -0.173 | 0.013 | -0.093 | -0.191 | -0.130 | -0.074 | -0.067 | 0.002 | -0.129 |
| CALAMAR | -0.020 | -0.001 | -0.019 | -0.024 | -0.010 | 0.000 | -0.003 | -0.001 | 0.000 | -0.001 | 0.005 | -0.003 |
| PENONCITO | -0.076 | -0.187 | -0.174 | 0.026 | -0.001 | -0.023 | -0.009 | -0.074 | -0.089 | -0.001 | 0.009 | 0.079 |
| SAN_PABLO | -0.022 | -0.173 | -0.103 | -0.024 | -0.056 | 0.095 | 0.057 | -0.042 | -0.096 | -0.006 | 0.096 | 0.113 |
| LA_GLORIA | -0.077 | -0.064 | -0.151 | -0.049 | -0.024 | -0.069 | -0.071 | -0.106 | -0.084 | -0.052 | -0.055 | -0.120 |

## Comparacion con corrida anterior (estudiantes)

| Estacion | N comparable | Diff media (m) | Diff max (m) |
|----------|--------------|----------------|--------------|
| LAS_AGUADAS | 19133 | 0.2219 | 0.5771 |
| LAS_PALOMAS | 18150 | 0.1147 | 2.1155 |
| RIO_NUEVO | 18638 | 0.244 | 0.5842 |
| EL_BANCO | 19132 | 0.3028 | 1.0023 |
| SAN_PEDRITO | 17137 | 0.2632 | 0.64 |
| TENERIFE | 18682 | 0.4257 | 2.244 |
| CALAMAR | 19982 | 0.2247 | 2.7997 |
| PENONCITO | 18880 | 0.1772 | 2.45 |
| LA_GLORIA | 12275 | 0.1812 | 1.6911 |

## Figuras por estacion

### LAS_AGUADAS
![LAS_AGUADAS](figuras/auditoria/auditoria_LAS_AGUADAS.png)

### LAS_PALOMAS
![LAS_PALOMAS](figuras/auditoria/auditoria_LAS_PALOMAS.png)

### PUERTO_BERRIO
![PUERTO_BERRIO](figuras/auditoria/auditoria_PUERTO_BERRIO.png)

### RIO_NUEVO
![RIO_NUEVO](figuras/auditoria/auditoria_RIO_NUEVO.png)

### TEBSA
![TEBSA](figuras/auditoria/auditoria_TEBSA.png)

### EL_BANCO
![EL_BANCO](figuras/auditoria/auditoria_EL_BANCO.png)

### SAN_PEDRITO
![SAN_PEDRITO](figuras/auditoria/auditoria_SAN_PEDRITO.png)

### TENERIFE
![TENERIFE](figuras/auditoria/auditoria_TENERIFE.png)

### CALAMAR
![CALAMAR](figuras/auditoria/auditoria_CALAMAR.png)

### PENONCITO
![PENONCITO](figuras/auditoria/auditoria_PENONCITO.png)

### SAN_PABLO
![SAN_PABLO](figuras/auditoria/auditoria_SAN_PABLO.png)

### LA_GLORIA
![LA_GLORIA](figuras/auditoria/auditoria_LA_GLORIA.png)
