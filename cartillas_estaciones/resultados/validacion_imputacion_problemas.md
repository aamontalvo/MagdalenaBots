# Reporte de Validacion de Imputacion - Rio Magdalena

## Resumen Ejecutivo

Este reporte documenta los problemas detectados en las series temporales imputadas utilizando tres filtros hidrologicos:

1. **Velocidad de Cambio**: Detecta cambios diarios anomalos
2. **Coherencia Espacial**: Valida correlacion con estaciones vecinas
3. **Continuidad de Fronteras**: Detecta saltos en limites de gaps

---

## Tabla Resumen por Estacion

| Estacion | Registros | Flags Total | Critical | Warning | Evaluacion |
|----------|-----------|-------------|----------|---------|------------|
| COYONGAL | 18,628 | 9008 | 31 | 8977 | ✗ SERIE CRITICA - Requiere revision completa |
| RIO_NUEVO | 18,739 | 14335 | 20 | 14315 | ✗ SERIE CRITICA - Requiere revision completa |
| LAS_PALOMAS | 18,988 | 8918 | 18 | 8900 | ✗ SERIE CRITICA - Requiere revision completa |
| ARMENIA | 15,078 | 9972 | 19 | 9953 | ✗ SERIE CRITICA - Requiere revision completa |
| GAMARRA_AUT | 4,418 | 1426 | 2 | 1424 | ✗ SERIE CRITICA - Requiere revision completa |

---

## Detalle de Problemas por Estacion

### COYONGAL

**Evaluacion:** ✗ SERIE CRITICA - Requiere revision completa

**Estadisticas:** 18,628 registros | Periodo: 1975-2025

**Periodos Problematicos Detectados:**

| Periodo Inicio | Periodo Fin | Duracion (dias) | Flags | Severidad | Descripcion |
|----------------|-------------|-----------------|-------|-----------|-------------|
| 1975-01-07 | 1975-01-17 | 11 | 5 | WARNING | Cambios bruscos de hasta 0.70m; Baja correlacion espacial (0.54) |
| 1975-03-01 | 1975-08-17 | 170 | 98 | WARNING | Cambios bruscos de hasta 0.54m; Baja correlacion espacial (-0.97) |
| 1975-10-06 | 1976-01-02 | 89 | 22 | WARNING | Baja correlacion espacial (-0.92) |
| 1976-04-03 | 1976-04-12 | 10 | 7 | WARNING | Baja correlacion espacial (-0.36) |
| 1976-05-22 | 1976-11-18 | 181 | 74 | CRITICAL | Cambios bruscos de hasta 1.52m; Baja correlacion espacial (-0.99) |
| 1976-12-23 | 1977-09-22 | 274 | 190 | CRITICAL | Cambios bruscos de hasta 1.02m; Baja correlacion espacial (-1.00) |
| 1977-11-04 | 1978-02-14 | 103 | 70 | CRITICAL | Cambios bruscos de hasta 1.13m; Baja correlacion espacial (-0.91) |
| 1978-04-01 | 1978-04-24 | 24 | 17 | WARNING | Cambios bruscos de hasta 0.76m; Baja correlacion espacial (-0.48) |
| 1978-05-30 | 1978-08-24 | 87 | 67 | WARNING | Cambios bruscos de hasta 0.50m; Baja correlacion espacial (-0.99) |
| 1978-11-01 | 1978-12-24 | 54 | 38 | CRITICAL | Cambios bruscos de hasta 1.50m; Baja correlacion espacial (-0.96) |
| 1979-01-24 | 1979-01-28 | 5 | 5 | WARNING | Baja correlacion espacial (-0.51) |
| 1979-05-03 | 1979-07-20 | 79 | 41 | CRITICAL | Cambios bruscos de hasta 1.21m; Baja correlacion espacial (-0.93) |
| 1979-09-29 | 1981-02-25 | 516 | 347 | CRITICAL | Cambios bruscos de hasta 0.91m; Baja correlacion espacial (-0.98) |
| 1981-03-30 | 1981-05-02 | 34 | 15 | WARNING | Cambios bruscos de hasta 0.46m; Baja correlacion espacial (-0.99) |
| 1981-06-06 | 1981-10-11 | 128 | 116 | WARNING | Baja correlacion espacial (-0.98) |
| 1981-11-20 | 1982-04-29 | 161 | 147 | WARNING | Cambios bruscos de hasta 0.66m; Baja correlacion espacial (-1.00) |
| 1982-06-14 | 1984-03-05 | 631 | 394 | CRITICAL | Cambios bruscos de hasta 0.94m; Baja correlacion espacial (-0.99) |
| 1984-04-12 | 1984-05-11 | 30 | 21 | WARNING | Baja correlacion espacial (-0.63) |
| 1984-06-21 | 1984-09-10 | 82 | 66 | WARNING | Baja correlacion espacial (-0.99) |
| 1984-10-11 | 1984-10-17 | 7 | 6 | WARNING | Baja correlacion espacial (-0.48) |
| 1984-11-19 | 1984-12-01 | 13 | 22 | WARNING | Baja correlacion espacial (-0.95) |
| 1985-02-12 | 1986-09-23 | 589 | 343 | CRITICAL | Cambios bruscos de hasta 1.70m; Baja correlacion espacial (-0.99) |
| 1986-11-03 | 1987-10-03 | 335 | 235 | CRITICAL | Cambios bruscos de hasta 1.96m; Baja correlacion espacial (-1.00) |
| 1987-11-08 | 1988-01-12 | 66 | 74 | CRITICAL | Cambios bruscos de hasta 1.14m; Baja correlacion espacial (-1.00) |
| 1988-02-16 | 1988-08-20 | 187 | 93 | CRITICAL | Cambios bruscos de hasta 0.84m; Baja correlacion espacial (-0.99) |
| 1988-09-20 | 1989-01-27 | 130 | 142 | WARNING | Cambios bruscos de hasta 0.33m; Baja correlacion espacial (-0.98) |
| 1989-03-24 | 1989-10-10 | 201 | 134 | WARNING | Cambios bruscos de hasta 0.80m; Baja correlacion espacial (-0.96) |
| 1989-11-15 | 1989-12-10 | 26 | 34 | WARNING | Cambios bruscos de hasta 0.44m; Baja correlacion espacial (-0.98) |
| 1990-01-16 | 1990-09-24 | 252 | 104 | WARNING | Cambios bruscos de hasta 0.73m; Baja correlacion espacial (-0.99) |
| 1990-11-14 | 1990-12-15 | 32 | 39 | WARNING | Baja correlacion espacial (-0.99) |
| 1991-02-10 | 1993-04-24 | 805 | 520 | WARNING | Cambios bruscos de hasta 0.44m; Baja correlacion espacial (-0.98) |
| 1993-05-30 | 1993-07-07 | 39 | 32 | WARNING | Baja correlacion espacial (-0.99) |
| 1993-08-11 | 1993-10-22 | 73 | 54 | WARNING | Baja correlacion espacial (-0.95) |
| 1993-12-04 | 1994-05-11 | 159 | 102 | CRITICAL | Cambios bruscos de hasta 1.02m; Baja correlacion espacial (-0.99) |
| 1994-06-11 | 1995-11-22 | 530 | 214 | WARNING | Cambios bruscos de hasta 0.59m; Baja correlacion espacial (-0.95) |
| 1996-01-17 | 1996-04-28 | 103 | 42 | WARNING | Baja correlacion espacial (-0.83) |
| 1996-06-13 | 1996-12-12 | 183 | 159 | WARNING | Baja correlacion espacial (-0.93) |
| 1997-01-14 | 1997-11-24 | 315 | 197 | WARNING | Cambios bruscos de hasta 0.41m; Baja correlacion espacial (-1.00) |
| 1997-12-27 | 1997-12-31 | 5 | 11 | WARNING | Cambios bruscos de hasta 0.35m; Baja correlacion espacial (0.24) |
| 1998-02-10 | 1998-03-26 | 45 | 23 | WARNING | Cambios bruscos de hasta 0.62m; Baja correlacion espacial (-0.97) |
| 1998-04-30 | 1998-10-25 | 179 | 87 | WARNING | Baja correlacion espacial (-0.62) |
| 1998-11-27 | 1999-01-03 | 38 | 41 | WARNING | Baja correlacion espacial (-0.75) |
| 1999-02-10 | 2000-05-05 | 451 | 229 | WARNING | Cambios bruscos de hasta 0.37m; Baja correlacion espacial (-0.94) |
| 2000-06-08 | 2000-08-29 | 83 | 49 | WARNING | Baja correlacion espacial (-0.79) |
| 2000-10-12 | 2001-08-28 | 321 | 127 | WARNING | Cambios bruscos de hasta 0.74m; Baja correlacion espacial (-1.00) |
| 2001-10-03 | 2001-12-31 | 90 | 54 | WARNING | Baja correlacion espacial (-0.89) |
| 2002-02-04 | 2002-11-19 | 289 | 95 | WARNING | Cambios bruscos de hasta 0.51m; Baja correlacion espacial (-0.91) |
| 2002-12-23 | 2003-09-18 | 270 | 80 | WARNING | Cambios bruscos de hasta 0.50m; Baja correlacion espacial (-0.75) |
| 2003-11-21 | 2004-09-29 | 314 | 125 | WARNING | Cambios bruscos de hasta 0.33m; Baja correlacion espacial (-0.96) |
| 2004-11-25 | 2004-12-03 | 9 | 14 | WARNING | Baja correlacion espacial (-0.87) |
| 2005-01-11 | 2005-10-19 | 282 | 140 | WARNING | Cambios bruscos de hasta 0.36m; Baja correlacion espacial (-0.99) |
| 2005-12-01 | 2005-12-09 | 9 | 12 | WARNING | Baja correlacion espacial (-0.97) |
| 2006-02-02 | 2006-04-04 | 62 | 30 | WARNING | Cambios bruscos de hasta 0.37m; Baja correlacion espacial (-0.90) |
| 2006-05-25 | 2006-10-15 | 144 | 70 | WARNING | Baja correlacion espacial (-1.00) |
| 2006-12-03 | 2006-12-17 | 15 | 26 | WARNING | Baja correlacion espacial (-0.98) |
| 2007-01-29 | 2007-04-17 | 79 | 40 | WARNING | Cambios bruscos de hasta 0.35m; Baja correlacion espacial (-0.99) |
| 2007-06-14 | 2007-08-09 | 57 | 37 | WARNING | Baja correlacion espacial (-1.00) |
| 2007-09-10 | 2007-10-11 | 32 | 28 | WARNING | Baja correlacion espacial (-0.88) |
| 2007-11-13 | 2007-11-29 | 17 | 20 | WARNING | Baja correlacion espacial (-0.99) |
| 2008-02-10 | 2008-05-17 | 98 | 44 | WARNING | Baja correlacion espacial (-0.94) |
| 2008-06-18 | 2008-12-16 | 182 | 148 | WARNING | Baja correlacion espacial (-1.00) |
| 2009-01-23 | 2009-07-24 | 183 | 55 | WARNING | Baja correlacion espacial (-0.82) |
| 2009-08-26 | 2010-05-21 | 269 | 87 | CRITICAL | Cambios bruscos de hasta 1.68m; Baja correlacion espacial (-0.87) |
| 2010-07-02 | 2010-12-18 | 170 | 163 | WARNING | Baja correlacion espacial (-0.96) |
| 2011-01-20 | 2011-04-03 | 74 | 46 | CRITICAL | Cambios bruscos de hasta 1.06m; Baja correlacion espacial (-0.80) |
| 2011-05-11 | 2011-11-13 | 187 | 106 | WARNING | Baja correlacion espacial (-0.93) |
| 2011-12-20 | 2011-12-24 | 5 | 4 | WARNING | Baja correlacion espacial (-0.08) |
| 2012-03-09 | 2012-04-02 | 25 | 16 | WARNING | Baja correlacion espacial (-0.61) |
| 2012-05-17 | 2012-05-25 | 9 | 10 | WARNING | Baja correlacion espacial (0.18) |
| 2012-07-06 | 2012-11-25 | 143 | 40 | WARNING | Baja correlacion espacial (-0.78) |
| 2013-01-22 | 2013-08-05 | 196 | 68 | WARNING | Baja correlacion espacial (-0.69) |
| 2013-09-17 | 2013-12-12 | 87 | 77 | WARNING | Baja correlacion espacial (-0.82) |
| 2014-01-16 | 2014-08-19 | 216 | 90 | WARNING | Baja correlacion espacial (-0.92) |
| 2014-09-27 | 2015-11-01 | 401 | 246 | CRITICAL | Cambios bruscos de hasta 2.28m; Baja correlacion espacial (-0.99) |
| 2015-12-17 | 2015-12-22 | 6 | 6 | WARNING | Baja correlacion espacial (-0.50) |
| 2016-01-24 | 2016-10-03 | 254 | 86 | WARNING | Cambios bruscos de hasta 0.35m; Baja correlacion espacial (-0.80) |
| 2016-11-28 | 2017-01-18 | 52 | 21 | WARNING | Baja correlacion espacial (-0.91) |
| 2017-02-26 | 2017-04-16 | 50 | 24 | WARNING | Baja correlacion espacial (-0.93) |
| 2017-06-04 | 2018-01-11 | 222 | 162 | CRITICAL | Cambios bruscos de hasta 1.28m; Baja correlacion espacial (-0.99) |
| 2018-02-19 | 2018-03-22 | 32 | 19 | WARNING | Baja correlacion espacial (-0.95) |
| 2018-04-23 | 2018-06-22 | 61 | 49 | CRITICAL | Cambios bruscos de hasta 0.88m; Baja correlacion espacial (-0.93) |
| 2018-07-28 | 2018-09-22 | 57 | 62 | WARNING | Baja correlacion espacial (-0.95) |
| 2018-11-17 | 2019-10-01 | 319 | 244 | CRITICAL | Cambios bruscos de hasta 2.29m; Baja correlacion espacial (-0.99) |
| 2019-11-02 | 2020-10-30 | 364 | 290 | WARNING | Cambios bruscos de hasta 0.36m; Baja correlacion espacial (-0.98) |
| 2020-12-07 | 2021-02-21 | 77 | 50 | WARNING | Baja correlacion espacial (-0.94) |
| 2021-03-31 | 2021-11-29 | 244 | 158 | WARNING | Baja correlacion espacial (-1.00) |
| 2022-01-21 | 2022-04-02 | 72 | 68 | WARNING | Baja correlacion espacial (-0.97) |
| 2022-05-12 | 2022-12-01 | 204 | 217 | WARNING | Baja correlacion espacial (-0.97) |
| 2023-01-04 | 2025-10-14 | 1015 | 699 | CRITICAL | Cambios bruscos de hasta 1.11m; Baja correlacion espacial (-1.00) |
| 2025-11-26 | 2025-12-28 | 33 | 29 | CRITICAL | Cambios bruscos de hasta 0.86m; Baja correlacion espacial (-0.75) |

---

### RIO_NUEVO

**Evaluacion:** ✗ SERIE CRITICA - Requiere revision completa

**Estadisticas:** 18,739 registros | Periodo: 1974-2025

**Periodos Problematicos Detectados:**

| Periodo Inicio | Periodo Fin | Duracion (dias) | Flags | Severidad | Descripcion |
|----------------|-------------|-----------------|-------|-----------|-------------|
| 1974-01-04 | 1974-02-01 | 29 | 2 | WARNING | Baja correlacion espacial (0.18) |
| 1974-03-09 | 1974-08-19 | 164 | 58 | WARNING | Baja correlacion espacial (-0.75) |
| 1974-10-10 | 1975-01-09 | 92 | 135 | CRITICAL | Cambios bruscos de hasta 1.18m; Baja correlacion espacial (-0.96) |
| 1975-02-11 | 1976-12-03 | 662 | 541 | CRITICAL | Cambios bruscos de hasta 1.13m; Baja correlacion espacial (-1.00) |
| 1977-01-23 | 1977-11-29 | 311 | 217 | WARNING | Cambios bruscos de hasta 0.51m; Baja correlacion espacial (-0.85) |
| 1978-01-30 | 1978-04-15 | 76 | 28 | WARNING | Cambios bruscos de hasta 0.56m; Baja correlacion espacial (-0.56) |
| 1978-05-31 | 1978-07-19 | 50 | 31 | WARNING | Baja correlacion espacial (-0.32) |
| 1978-09-29 | 1978-10-04 | 6 | 11 | WARNING | Cambios bruscos de hasta 0.54m; Baja correlacion espacial (-0.15) |
| 1978-11-04 | 1979-08-31 | 301 | 154 | WARNING | Cambios bruscos de hasta 0.58m; Baja correlacion espacial (-1.00) |
| 1979-10-30 | 1981-04-04 | 523 | 401 | CRITICAL | Cambios bruscos de hasta 0.98m; Baja correlacion espacial (-1.00) |
| 1981-05-30 | 1981-06-19 | 21 | 14 | WARNING | Baja correlacion espacial (-0.36) |
| 1981-08-08 | 1981-10-08 | 62 | 59 | WARNING | Baja correlacion espacial (-1.00) |
| 1981-11-14 | 1982-04-02 | 140 | 110 | WARNING | Baja correlacion espacial (-0.99) |
| 1982-05-03 | 1982-08-29 | 119 | 109 | CRITICAL | Cambios bruscos de hasta 1.08m; Baja correlacion espacial (-0.91) |
| 1982-11-29 | 1985-01-10 | 774 | 632 | WARNING | Cambios bruscos de hasta 0.53m; Baja correlacion espacial (-1.00) |
| 1985-02-18 | 1986-09-24 | 584 | 330 | WARNING | Cambios bruscos de hasta 0.78m; Baja correlacion espacial (-0.97) |
| 1986-11-11 | 1987-01-06 | 57 | 19 | WARNING | Baja correlacion espacial (-0.99) |
| 1987-02-14 | 1987-10-04 | 233 | 249 | CRITICAL | Cambios bruscos de hasta 1.55m; Baja correlacion espacial (-0.93) |
| 1987-11-09 | 1988-01-02 | 55 | 36 | WARNING | Baja correlacion espacial (-0.96) |
| 1988-03-23 | 1992-08-26 | 1618 | 1315 | CRITICAL | Cambios bruscos de hasta 0.88m; Baja correlacion espacial (-0.99) |
| 1992-10-01 | 1993-01-08 | 100 | 62 | WARNING | Cambios bruscos de hasta 0.35m; Baja correlacion espacial (-0.69) |
| 1993-02-27 | 1993-06-24 | 118 | 55 | WARNING | Cambios bruscos de hasta 0.71m; Baja correlacion espacial (-0.95) |
| 1993-08-11 | 1993-11-03 | 85 | 86 | WARNING | Cambios bruscos de hasta 0.76m; Baja correlacion espacial (-0.98) |
| 1993-12-07 | 1994-04-21 | 136 | 97 | CRITICAL | Cambios bruscos de hasta 1.09m; Baja correlacion espacial (-0.89) |
| 1994-05-28 | 1995-06-23 | 392 | 203 | CRITICAL | Cambios bruscos de hasta 2.37m; Baja correlacion espacial (-1.00) |
| 1995-08-13 | 1995-12-26 | 136 | 190 | WARNING | Cambios bruscos de hasta 0.38m; Baja correlacion espacial (-0.93) |
| 1996-02-20 | 1996-05-07 | 78 | 72 | WARNING | Baja correlacion espacial (-0.99) |
| 1996-06-13 | 1997-11-25 | 531 | 454 | WARNING | Cambios bruscos de hasta 0.46m; Baja correlacion espacial (-1.00) |
| 1998-01-01 | 1999-02-12 | 408 | 351 | WARNING | Cambios bruscos de hasta 0.37m; Baja correlacion espacial (-0.99) |
| 1999-03-16 | 2003-10-05 | 1665 | 1320 | WARNING | Cambios bruscos de hasta 0.70m; Baja correlacion espacial (-1.00) |
| 2003-11-24 | 2005-09-25 | 672 | 718 | WARNING | Cambios bruscos de hasta 0.73m; Baja correlacion espacial (-1.00) |
| 2005-11-22 | 2007-04-19 | 514 | 374 | CRITICAL | Cambios bruscos de hasta 1.18m; Baja correlacion espacial (-0.99) |
| 2007-06-01 | 2012-04-04 | 1770 | 1785 | WARNING | Cambios bruscos de hasta 0.73m; Baja correlacion espacial (-0.99) |
| 2012-05-10 | 2018-11-30 | 2396 | 2471 | CRITICAL | Cambios bruscos de hasta 1.05m; Baja correlacion espacial (-1.00) |
| 2019-01-03 | 2022-03-21 | 1174 | 1039 | CRITICAL | Cambios bruscos de hasta 0.91m; Baja correlacion espacial (-1.00) |
| 2022-05-08 | 2023-06-22 | 411 | 254 | WARNING | Cambios bruscos de hasta 0.55m; Baja correlacion espacial (-0.98) |
| 2023-07-26 | 2024-04-26 | 276 | 220 | CRITICAL | Cambios bruscos de hasta 0.98m; Baja correlacion espacial (-0.91) |
| 2024-05-28 | 2024-06-15 | 19 | 20 | WARNING | Baja correlacion espacial (-0.25) |
| 2024-08-12 | 2024-11-04 | 85 | 26 | WARNING | Cambios bruscos de hasta 0.32m; Baja correlacion espacial (-0.29) |
| 2024-12-23 | 2025-04-07 | 106 | 78 | WARNING | Cambios bruscos de hasta 0.48m; Baja correlacion espacial (-1.00) |
| 2025-05-17 | 2025-05-19 | 3 | 3 | WARNING | Baja correlacion espacial (0.60) |
| 2025-08-05 | 2025-09-19 | 46 | 6 | WARNING | Baja correlacion espacial (0.08) |

---

### LAS_PALOMAS

**Evaluacion:** ✗ SERIE CRITICA - Requiere revision completa

**Estadisticas:** 18,988 registros | Periodo: 1973-2025

**Periodos Problematicos Detectados:**

| Periodo Inicio | Periodo Fin | Duracion (dias) | Flags | Severidad | Descripcion |
|----------------|-------------|-----------------|-------|-----------|-------------|
| 1973-04-10 | 1973-05-09 | 30 | 4 | WARNING | Cambios bruscos de hasta 0.56m |
| 1973-07-30 | 1973-08-19 | 21 | 14 | WARNING | Cambios bruscos de hasta 0.62m; Baja correlacion espacial (-0.38) |
| 1973-10-05 | 1973-10-31 | 27 | 11 | WARNING | Baja correlacion espacial (-0.00) |
| 1973-12-04 | 1973-12-05 | 2 | 2 | WARNING | Baja correlacion espacial (0.61) |
| 1974-02-01 | 1974-02-01 | 1 | 2 | WARNING | Baja correlacion espacial (0.31) |
| 1974-05-26 | 1974-06-28 | 34 | 12 | WARNING | Baja correlacion espacial (0.45) |
| 1974-08-13 | 1974-08-13 | 1 | 2 | WARNING | Baja correlacion espacial (0.57) |
| 1974-10-11 | 1974-12-30 | 81 | 87 | WARNING | Baja correlacion espacial (-0.96) |
| 1975-02-11 | 1976-12-20 | 679 | 293 | WARNING | Cambios bruscos de hasta 0.52m; Baja correlacion espacial (-1.00) |
| 1977-01-23 | 1977-09-20 | 241 | 113 | CRITICAL | Cambios bruscos de hasta 0.99m; Baja correlacion espacial (-0.85) |
| 1977-10-26 | 1977-11-29 | 35 | 30 | WARNING | Baja correlacion espacial (-0.70) |
| 1978-01-30 | 1978-04-15 | 76 | 19 | WARNING | Cambios bruscos de hasta 0.64m; Baja correlacion espacial (-0.41) |
| 1978-05-31 | 1978-07-19 | 50 | 21 | WARNING | Baja correlacion espacial (-0.32) |
| 1978-09-29 | 1978-10-04 | 6 | 6 | WARNING | Baja correlacion espacial (-0.14) |
| 1978-11-04 | 1978-12-18 | 45 | 20 | WARNING | Baja correlacion espacial (-0.91) |
| 1979-02-03 | 1979-03-05 | 31 | 4 | WARNING | Baja correlacion espacial (0.66) |
| 1979-04-05 | 1979-08-05 | 123 | 31 | WARNING | Baja correlacion espacial (-0.90) |
| 1979-10-30 | 1980-03-24 | 147 | 46 | WARNING | Cambios bruscos de hasta 0.51m; Baja correlacion espacial (-0.70) |
| 1980-04-27 | 1980-07-22 | 87 | 34 | WARNING | Cambios bruscos de hasta 0.33m; Baja correlacion espacial (-0.84) |
| 1980-08-22 | 1981-01-05 | 137 | 34 | WARNING | Cambios bruscos de hasta 0.36m; Baja correlacion espacial (-0.96) |
| 1981-02-23 | 1981-04-08 | 45 | 34 | WARNING | Cambios bruscos de hasta 0.51m; Baja correlacion espacial (-0.72) |
| 1981-05-30 | 1981-06-19 | 21 | 28 | WARNING | Baja correlacion espacial (-0.36) |
| 1981-08-08 | 1981-10-08 | 62 | 17 | WARNING | Baja correlacion espacial (0.33) |
| 1981-11-14 | 1981-12-10 | 27 | 44 | WARNING | Baja correlacion espacial (-0.68) |
| 1982-02-06 | 1982-04-02 | 56 | 39 | WARNING | Baja correlacion espacial (-0.57) |
| 1982-05-21 | 1982-08-29 | 101 | 55 | WARNING | Baja correlacion espacial (-0.90) |
| 1982-11-29 | 1983-12-25 | 392 | 126 | WARNING | Cambios bruscos de hasta 0.48m; Baja correlacion espacial (-0.85) |
| 1984-01-31 | 1984-08-30 | 213 | 113 | WARNING | Baja correlacion espacial (-0.96) |
| 1984-10-07 | 1985-01-10 | 96 | 72 | WARNING | Baja correlacion espacial (-0.99) |
| 1985-03-06 | 1985-07-19 | 136 | 42 | WARNING | Cambios bruscos de hasta 0.58m; Baja correlacion espacial (-0.90) |
| 1985-08-19 | 1985-09-20 | 33 | 12 | WARNING | Baja correlacion espacial (0.48) |
| 1985-11-20 | 1985-11-26 | 7 | 7 | WARNING | Baja correlacion espacial (0.35) |
| 1986-01-25 | 1986-07-05 | 162 | 39 | WARNING | Cambios bruscos de hasta 0.34m; Baja correlacion espacial (-0.36) |
| 1986-11-11 | 1986-12-18 | 38 | 19 | WARNING | Baja correlacion espacial (-0.85) |
| 1987-02-18 | 1987-08-27 | 191 | 76 | WARNING | Cambios bruscos de hasta 0.78m; Baja correlacion espacial (-0.80) |
| 1987-09-29 | 1987-10-02 | 4 | 8 | WARNING | Baja correlacion espacial (0.09) |
| 1987-11-09 | 1987-12-13 | 35 | 22 | WARNING | Baja correlacion espacial (-0.66) |
| 1988-04-06 | 1988-04-27 | 22 | 7 | WARNING | Cambios bruscos de hasta 0.40m; Baja correlacion espacial (-0.96) |
| 1988-06-25 | 1989-03-27 | 276 | 210 | WARNING | Cambios bruscos de hasta 0.35m; Baja correlacion espacial (-0.90) |
| 1989-04-28 | 1989-08-03 | 98 | 37 | WARNING | Baja correlacion espacial (-0.81) |
| 1989-09-12 | 1992-08-26 | 1080 | 414 | WARNING | Cambios bruscos de hasta 0.52m; Baja correlacion espacial (-0.99) |
| 1992-10-01 | 1993-01-04 | 96 | 32 | WARNING | Baja correlacion espacial (-0.69) |
| 1993-02-27 | 1993-06-24 | 118 | 45 | WARNING | Cambios bruscos de hasta 0.58m; Baja correlacion espacial (-0.70) |
| 1993-08-09 | 1993-11-03 | 87 | 71 | WARNING | Cambios bruscos de hasta 0.76m; Baja correlacion espacial (-0.96) |
| 1993-12-13 | 1993-12-19 | 7 | 8 | WARNING | Baja correlacion espacial (-0.40) |
| 1994-01-29 | 1994-02-27 | 30 | 19 | WARNING | Baja correlacion espacial (-0.88) |
| 1994-04-20 | 1994-04-21 | 2 | 2 | WARNING | Baja correlacion espacial (0.45) |
| 1994-05-28 | 1994-09-22 | 118 | 45 | WARNING | Baja correlacion espacial (-0.87) |
| 1994-11-10 | 1995-01-15 | 67 | 38 | CRITICAL | Cambios bruscos de hasta 1.01m; Baja correlacion espacial (-0.86) |
| 1995-02-25 | 1995-04-14 | 49 | 16 | WARNING | Cambios bruscos de hasta 0.54m; Baja correlacion espacial (-0.34) |
| 1995-05-16 | 1995-05-21 | 6 | 10 | WARNING | Baja correlacion espacial (0.52) |
| 1995-08-12 | 1995-12-24 | 135 | 94 | WARNING | Baja correlacion espacial (-0.91) |
| 1996-02-20 | 1996-05-07 | 78 | 33 | WARNING | Baja correlacion espacial (-0.99) |
| 1996-06-19 | 1997-02-03 | 230 | 173 | WARNING | Baja correlacion espacial (-1.00) |
| 1997-03-12 | 1997-09-27 | 200 | 116 | WARNING | Cambios bruscos de hasta 0.46m; Baja correlacion espacial (-0.84) |
| 1997-11-02 | 1997-11-25 | 24 | 13 | WARNING | Cambios bruscos de hasta 0.40m; Baja correlacion espacial (-0.38) |
| 1998-01-01 | 1999-02-12 | 408 | 258 | CRITICAL | Cambios bruscos de hasta 0.92m; Baja correlacion espacial (-0.98) |
| 1999-04-01 | 1999-09-10 | 163 | 152 | WARNING | Baja correlacion espacial (-0.99) |
| 1999-10-12 | 2002-10-13 | 1098 | 554 | CRITICAL | Cambios bruscos de hasta 1.45m; Baja correlacion espacial (-0.99) |
| 2002-11-14 | 2003-10-05 | 326 | 225 | CRITICAL | Cambios bruscos de hasta 0.83m; Baja correlacion espacial (-0.99) |
| 2003-11-24 | 2005-10-04 | 681 | 527 | WARNING | Cambios bruscos de hasta 0.47m; Baja correlacion espacial (-1.00) |
| 2005-11-23 | 2007-04-19 | 513 | 424 | CRITICAL | Cambios bruscos de hasta 1.19m; Baja correlacion espacial (-1.00) |
| 2007-06-06 | 2007-06-12 | 7 | 10 | WARNING | Baja correlacion espacial (-0.82) |
| 2007-07-17 | 2012-04-04 | 1724 | 1051 | WARNING | Cambios bruscos de hasta 0.43m; Baja correlacion espacial (-0.99) |
| 2012-05-10 | 2014-04-16 | 707 | 515 | WARNING | Cambios bruscos de hasta 0.65m; Baja correlacion espacial (-0.99) |
| 2014-05-18 | 2016-06-23 | 768 | 735 | WARNING | Cambios bruscos de hasta 0.45m; Baja correlacion espacial (-1.00) |
| 2016-07-24 | 2018-11-29 | 859 | 562 | WARNING | Cambios bruscos de hasta 0.45m; Baja correlacion espacial (-1.00) |
| 2019-01-03 | 2020-06-29 | 544 | 310 | WARNING | Cambios bruscos de hasta 0.48m; Baja correlacion espacial (-0.99) |
| 2020-08-13 | 2022-03-20 | 585 | 263 | WARNING | Baja correlacion espacial (-1.00) |
| 2022-05-08 | 2022-11-23 | 200 | 76 | WARNING | Baja correlacion espacial (-0.79) |
| 2023-01-22 | 2023-04-29 | 98 | 72 | WARNING | Baja correlacion espacial (-0.90) |
| 2023-06-05 | 2023-06-12 | 8 | 14 | WARNING | Baja correlacion espacial (-0.74) |
| 2023-07-26 | 2024-04-26 | 276 | 157 | WARNING | Cambios bruscos de hasta 0.61m; Baja correlacion espacial (-0.91) |
| 2024-05-28 | 2024-06-15 | 19 | 30 | WARNING | Baja correlacion espacial (-0.25) |
| 2024-08-18 | 2024-11-02 | 77 | 17 | WARNING | Cambios bruscos de hasta 0.34m; Baja correlacion espacial (0.02) |
| 2024-12-23 | 2025-01-27 | 36 | 6 | WARNING | Cambios bruscos de hasta 0.45m; Baja correlacion espacial (0.17) |
| 2025-03-02 | 2025-04-06 | 36 | 31 | WARNING | Baja correlacion espacial (-0.99) |
| 2025-05-17 | 2025-05-19 | 3 | 6 | WARNING | Baja correlacion espacial (0.17) |
| 2025-08-05 | 2025-08-22 | 18 | 2 | WARNING | Baja correlacion espacial (0.38) |

---

### ARMENIA

**Evaluacion:** ✗ SERIE CRITICA - Requiere revision completa

**Estadisticas:** 15,078 registros | Periodo: 1973-2025

**Periodos Problematicos Detectados:**

| Periodo Inicio | Periodo Fin | Duracion (dias) | Flags | Severidad | Descripcion |
|----------------|-------------|-----------------|-------|-----------|-------------|
| 1973-03-07 | 1973-03-26 | 20 | 4 | WARNING | Cambios bruscos de hasta 0.44m |
| 1973-05-09 | 1973-08-03 | 87 | 18 | CRITICAL | Cambios bruscos de hasta 1.34m; Baja correlacion espacial (-0.63) |
| 1973-10-04 | 1974-01-04 | 93 | 42 | WARNING | Baja correlacion espacial (-0.79) |
| 1974-03-09 | 1974-08-19 | 164 | 102 | WARNING | Baja correlacion espacial (-0.94) |
| 1974-10-16 | 1975-01-09 | 86 | 66 | WARNING | Baja correlacion espacial (-0.55) |
| 1975-04-02 | 1976-01-26 | 300 | 213 | WARNING | Cambios bruscos de hasta 0.38m; Baja correlacion espacial (-0.96) |
| 1976-03-01 | 1976-09-29 | 213 | 141 | WARNING | Cambios bruscos de hasta 0.25m; Baja correlacion espacial (-0.93) |
| 1976-11-14 | 1976-11-15 | 2 | 3 | WARNING | Baja correlacion espacial (0.28) |
| 1977-04-05 | 1977-04-13 | 9 | 9 | WARNING | Baja correlacion espacial (-0.69) |
| 1977-06-01 | 1977-06-03 | 3 | 5 | WARNING | Baja correlacion espacial (-0.00) |
| 1977-11-01 | 1977-11-30 | 30 | 29 | WARNING | Baja correlacion espacial (-0.50) |
| 1978-02-01 | 1978-02-14 | 14 | 23 | WARNING | Baja correlacion espacial (-0.88) |
| 1978-06-01 | 1978-06-12 | 12 | 9 | WARNING | Baja correlacion espacial (-0.90) |
| 1978-12-06 | 1979-03-06 | 91 | 86 | WARNING | Baja correlacion espacial (-1.00) |
| 1979-05-05 | 1979-07-10 | 67 | 35 | WARNING | Baja correlacion espacial (-0.94) |
| 1979-11-08 | 1980-04-23 | 168 | 159 | WARNING | Cambios bruscos de hasta 0.37m; Baja correlacion espacial (-0.89) |
| 1980-06-01 | 1980-10-28 | 150 | 173 | CRITICAL | Cambios bruscos de hasta 1.38m; Baja correlacion espacial (-0.96) |
| 1980-12-01 | 1981-02-07 | 69 | 63 | WARNING | Cambios bruscos de hasta 0.37m; Baja correlacion espacial (-0.97) |
| 1981-05-02 | 1981-05-02 | 1 | 1 | CRITICAL | Cambios bruscos de hasta 1.65m |
| 1981-09-01 | 1981-10-01 | 31 | 52 | CRITICAL | Cambios bruscos de hasta 0.77m; Baja correlacion espacial (-1.00) |
| 1981-12-01 | 1982-02-25 | 87 | 96 | CRITICAL | Cambios bruscos de hasta 1.00m; Baja correlacion espacial (-0.99) |
| 1982-04-02 | 1982-04-02 | 1 | 1 | WARNING | Cambios bruscos de hasta 0.29m |
| 1982-05-03 | 1982-07-09 | 68 | 58 | WARNING | Cambios bruscos de hasta 0.27m; Baja correlacion espacial (-0.93) |
| 1982-12-01 | 1983-01-11 | 42 | 53 | WARNING | Baja correlacion espacial (-0.98) |
| 1983-04-01 | 1983-04-09 | 9 | 16 | CRITICAL | Cambios bruscos de hasta 1.68m; Baja correlacion espacial (-0.89) |
| 1983-09-02 | 1984-06-30 | 303 | 285 | CRITICAL | Cambios bruscos de hasta 0.67m; Baja correlacion espacial (-1.00) |
| 1984-09-03 | 1985-01-10 | 130 | 104 | CRITICAL | Cambios bruscos de hasta 1.47m; Baja correlacion espacial (-0.94) |
| 1985-02-18 | 1985-02-23 | 6 | 12 | WARNING | Baja correlacion espacial (-0.87) |
| 1985-04-04 | 1985-04-24 | 21 | 20 | WARNING | Cambios bruscos de hasta 0.40m; Baja correlacion espacial (-0.61) |
| 1985-06-01 | 1986-02-25 | 270 | 257 | CRITICAL | Cambios bruscos de hasta 1.32m; Baja correlacion espacial (-0.97) |
| 1986-04-01 | 1986-10-09 | 192 | 166 | WARNING | Cambios bruscos de hasta 0.33m; Baja correlacion espacial (-0.96) |
| 1986-11-11 | 1987-01-06 | 57 | 23 | WARNING | Baja correlacion espacial (-0.99) |
| 1987-02-14 | 1987-10-04 | 233 | 293 | CRITICAL | Cambios bruscos de hasta 1.42m; Baja correlacion espacial (-0.95) |
| 1987-11-10 | 1988-01-01 | 53 | 45 | CRITICAL | Cambios bruscos de hasta 12.46m; Baja correlacion espacial (-0.96) |
| 1988-04-15 | 1989-02-19 | 311 | 247 | CRITICAL | Cambios bruscos de hasta 12.13m; Baja correlacion espacial (-0.92) |
| 1989-03-26 | 1989-08-22 | 150 | 79 | WARNING | Baja correlacion espacial (-0.95) |
| 1989-10-08 | 1989-12-25 | 79 | 37 | WARNING | Cambios bruscos de hasta 0.33m; Baja correlacion espacial (-0.98) |
| 1990-03-02 | 1990-04-17 | 47 | 30 | WARNING | Cambios bruscos de hasta 0.34m; Baja correlacion espacial (-0.88) |
| 1990-05-25 | 1990-07-24 | 61 | 47 | WARNING | Baja correlacion espacial (-0.97) |
| 1990-09-05 | 1990-10-02 | 28 | 20 | WARNING | Baja correlacion espacial (-0.70) |
| 1990-11-10 | 1991-01-10 | 62 | 36 | WARNING | Baja correlacion espacial (-0.72) |
| 1991-02-12 | 1991-06-28 | 137 | 89 | WARNING | Cambios bruscos de hasta 0.57m; Baja correlacion espacial (-0.97) |
| 1991-09-02 | 1991-12-21 | 111 | 52 | WARNING | Baja correlacion espacial (-0.83) |
| 1992-02-02 | 1992-08-25 | 206 | 120 | WARNING | Cambios bruscos de hasta 0.38m; Baja correlacion espacial (-1.00) |
| 1992-10-01 | 1993-01-08 | 100 | 46 | WARNING | Baja correlacion espacial (-0.41) |
| 1993-10-19 | 1993-11-02 | 15 | 9 | WARNING | Baja correlacion espacial (-0.12) |
| 1993-12-07 | 1994-03-28 | 112 | 78 | WARNING | Cambios bruscos de hasta 0.26m; Baja correlacion espacial (-0.92) |
| 1994-07-02 | 1995-06-23 | 357 | 188 | WARNING | Cambios bruscos de hasta 0.38m; Baja correlacion espacial (-1.00) |
| 1995-08-17 | 1995-12-19 | 125 | 103 | WARNING | Baja correlacion espacial (-0.93) |
| 1996-03-21 | 1996-05-06 | 47 | 25 | WARNING | Baja correlacion espacial (-0.99) |
| 1996-06-13 | 1997-06-05 | 358 | 250 | WARNING | Cambios bruscos de hasta 0.28m; Baja correlacion espacial (-0.99) |
| 1997-08-01 | 1997-11-24 | 116 | 47 | WARNING | Cambios bruscos de hasta 0.46m; Baja correlacion espacial (-0.72) |
| 1998-01-01 | 1998-03-23 | 82 | 58 | WARNING | Cambios bruscos de hasta 0.45m; Baja correlacion espacial (-1.00) |
| 1998-04-25 | 1999-02-11 | 293 | 236 | WARNING | Baja correlacion espacial (-0.99) |
| 1999-03-16 | 2001-02-10 | 698 | 489 | CRITICAL | Cambios bruscos de hasta 1.54m; Baja correlacion espacial (-1.00) |
| 2001-04-10 | 2001-06-09 | 61 | 41 | WARNING | Baja correlacion espacial (-0.78) |
| 2001-07-15 | 2001-07-31 | 17 | 19 | WARNING | Baja correlacion espacial (-0.60) |
| 2001-09-17 | 2003-02-28 | 530 | 323 | WARNING | Cambios bruscos de hasta 0.28m; Baja correlacion espacial (-1.00) |
| 2004-03-23 | 2004-11-28 | 251 | 161 | WARNING | Baja correlacion espacial (-0.99) |
| 2005-01-09 | 2005-09-25 | 260 | 201 | CRITICAL | Cambios bruscos de hasta 2.04m; Baja correlacion espacial (-0.99) |
| 2005-11-23 | 2006-01-01 | 40 | 36 | WARNING | Baja correlacion espacial (-0.99) |
| 2006-02-08 | 2006-06-28 | 141 | 67 | WARNING | Baja correlacion espacial (-0.90) |
| 2006-11-01 | 2007-04-19 | 170 | 104 | WARNING | Cambios bruscos de hasta 0.48m; Baja correlacion espacial (-0.99) |
| 2007-06-01 | 2012-04-03 | 1769 | 1434 | WARNING | Cambios bruscos de hasta 0.42m; Baja correlacion espacial (-0.99) |
| 2012-05-13 | 2018-06-07 | 2217 | 1429 | WARNING | Cambios bruscos de hasta 0.47m; Baja correlacion espacial (-1.00) |
| 2018-07-26 | 2020-10-31 | 829 | 503 | WARNING | Cambios bruscos de hasta 0.44m; Baja correlacion espacial (-1.00) |
| 2021-01-06 | 2021-12-04 | 333 | 197 | WARNING | Baja correlacion espacial (-0.99) |
| 2022-01-09 | 2022-03-21 | 72 | 42 | WARNING | Cambios bruscos de hasta 0.26m; Baja correlacion espacial (-0.84) |
| 2022-05-09 | 2022-06-27 | 50 | 60 | WARNING | Baja correlacion espacial (-0.94) |
| 2022-08-12 | 2023-06-11 | 304 | 229 | WARNING | Baja correlacion espacial (-0.99) |
| 2023-07-26 | 2024-04-26 | 276 | 149 | WARNING | Cambios bruscos de hasta 0.60m; Baja correlacion espacial (-0.86) |
| 2024-07-29 | 2024-08-15 | 18 | 10 | WARNING | Baja correlacion espacial (-0.29) |
| 2024-09-17 | 2024-11-04 | 49 | 8 | WARNING | Cambios bruscos de hasta 0.26m; Baja correlacion espacial (0.35) |
| 2024-12-23 | 2025-01-25 | 34 | 4 | WARNING | Cambios bruscos de hasta 0.28m; Baja correlacion espacial (0.46) |
| 2025-04-10 | 2025-04-20 | 11 | 6 | WARNING | Baja correlacion espacial (-0.02) |
| 2025-09-19 | 2025-09-19 | 1 | 1 | WARNING | Baja correlacion espacial (0.08) |

---

### GAMARRA_AUT

**Evaluacion:** ✗ SERIE CRITICA - Requiere revision completa

**Estadisticas:** 4,418 registros | Periodo: 2013-2025

**Periodos Problematicos Detectados:**

| Periodo Inicio | Periodo Fin | Duracion (dias) | Flags | Severidad | Descripcion |
|----------------|-------------|-----------------|-------|-----------|-------------|
| 2013-01-04 | 2014-02-25 | 418 | 168 | CRITICAL | Cambios bruscos de hasta 1.21m; Baja correlacion espacial (-0.96) |
| 2014-04-07 | 2014-11-26 | 234 | 90 | WARNING | Cambios bruscos de hasta 0.69m; Baja correlacion espacial (-0.78) |
| 2014-12-27 | 2015-03-22 | 86 | 40 | WARNING | Cambios bruscos de hasta 0.51m; Baja correlacion espacial (-0.09) |
| 2015-05-26 | 2016-01-01 | 221 | 188 | WARNING | Cambios bruscos de hasta 0.47m; Baja correlacion espacial (-0.83) |
| 2016-02-16 | 2017-03-03 | 382 | 236 | WARNING | Cambios bruscos de hasta 0.64m; Baja correlacion espacial (-0.98) |
| 2017-04-12 | 2017-09-25 | 167 | 37 | WARNING | Baja correlacion espacial (-0.83) |
| 2017-10-27 | 2017-11-13 | 18 | 3 | WARNING | Baja correlacion espacial (0.52) |
| 2017-12-25 | 2018-03-20 | 86 | 25 | WARNING | Cambios bruscos de hasta 0.46m; Baja correlacion espacial (-0.69) |
| 2018-04-25 | 2018-05-26 | 32 | 7 | WARNING | Baja correlacion espacial (-0.86) |
| 2018-07-16 | 2018-08-31 | 47 | 14 | WARNING | Baja correlacion espacial (-0.12) |
| 2018-10-09 | 2018-11-13 | 36 | 12 | WARNING | Baja correlacion espacial (0.04) |
| 2018-12-19 | 2019-04-17 | 120 | 83 | WARNING | Cambios bruscos de hasta 0.49m; Baja correlacion espacial (-0.98) |
| 2019-07-12 | 2019-10-11 | 92 | 59 | WARNING | Cambios bruscos de hasta 0.46m; Baja correlacion espacial (-0.74) |
| 2019-11-24 | 2019-12-10 | 17 | 2 | WARNING | Baja correlacion espacial (0.60) |
| 2020-01-12 | 2020-07-07 | 178 | 68 | CRITICAL | Cambios bruscos de hasta 1.91m; Baja correlacion espacial (-0.81) |
| 2020-08-12 | 2021-04-12 | 244 | 56 | WARNING | Baja correlacion espacial (-0.73) |
| 2021-05-19 | 2021-05-21 | 3 | 3 | WARNING | Baja correlacion espacial (0.44) |
| 2021-06-25 | 2021-08-02 | 39 | 13 | WARNING | Baja correlacion espacial (-0.85) |
| 2021-09-04 | 2022-03-11 | 189 | 66 | WARNING | Baja correlacion espacial (-0.94) |
| 2022-04-14 | 2022-07-23 | 101 | 38 | WARNING | Baja correlacion espacial (-0.98) |
| 2022-09-05 | 2023-02-25 | 174 | 60 | WARNING | Baja correlacion espacial (-0.77) |
| 2023-03-31 | 2023-03-31 | 1 | 1 | WARNING | Baja correlacion espacial (0.29) |
| 2023-05-19 | 2023-05-19 | 1 | 1 | WARNING | Baja correlacion espacial (0.28) |
| 2023-07-25 | 2023-08-20 | 27 | 22 | WARNING | Baja correlacion espacial (-0.93) |
| 2023-10-09 | 2024-01-07 | 91 | 38 | WARNING | Baja correlacion espacial (-0.92) |
| 2024-02-25 | 2024-03-03 | 8 | 10 | WARNING | Baja correlacion espacial (-0.60) |
| 2024-04-07 | 2024-06-28 | 83 | 9 | WARNING | Cambios bruscos de hasta 0.68m; Baja correlacion espacial (0.19) |
| 2024-08-24 | 2024-11-20 | 89 | 32 | WARNING | Cambios bruscos de hasta 0.65m; Baja correlacion espacial (-0.72) |
| 2024-12-29 | 2025-01-28 | 31 | 8 | WARNING | Cambios bruscos de hasta 0.57m; Baja correlacion espacial (-0.36) |
| 2025-05-25 | 2025-07-17 | 54 | 20 | WARNING | Baja correlacion espacial (-0.95) |
| 2025-09-18 | 2025-12-19 | 93 | 17 | WARNING | Cambios bruscos de hasta 0.46m; Baja correlacion espacial (-0.12) |

---

## Recomendaciones

### Estaciones que requieren atencion inmediata:
- **COYONGAL**: 31 flags CRITICAL
- **RIO_NUEVO**: 20 flags CRITICAL
- **LAS_PALOMAS**: 18 flags CRITICAL
- **ARMENIA**: 19 flags CRITICAL
- **GAMARRA_AUT**: 2 flags CRITICAL

### Acciones sugeridas:

1. **Revisar manualmente** los periodos marcados como CRITICAL
2. **Comparar con datos brutos** originales para verificar si son errores de imputacion
3. **Ajustar modelos H-H** para estaciones con problemas de coherencia espacial
4. **Considerar exclusion** de periodos dudosos para analisis de frecuencia

### Metodologia:

- Umbral velocidad: 2x percentil 99.5 historico
- Umbral correlacion espacial: r < 0.7
- Umbral salto frontera: > 3 desviaciones estandar locales

---

**Fecha de generacion:** 2026-03-24 15:12
**Sistema:** MagdalenaBot Validacion v1.0
