# Metricas consolidadas - Niveles y caudales

> **Corte de datos:** 24-ago-2026. **Generado:** 19-oct-2026.
> **Fuentes:** datasets finales, resumenes de imputacion, cartillas, borradores y reportes de validacion.
> **Regla:** no se modificaron datos originales; todas las cifras se recalcularon desde los archivos citados.

## 0. Definiciones

- **Datos ingresados:** filas de la fuente cruda recibida (incluye faltantes).
- **Datos recibidos/procesados:** filas del dataset final después de preparar, imputar y documentar faltantes.
- **L0:** dato original valido. **L1:** interpolacion local. **L2/L3:** modelos H-H o N-C.
- **Cobertura:** porcentaje de dias con dato (original o imputado) dentro del rango oficial.
- **Vigente:** figura o cartilla de la version final (niveles v2.1, caudales v1).

## 1. Tablero de metricas

| Metrica | Niveles | Caudales | Total |
|---|---:|---:|---:|
| Estaciones en la fuente | 24 | 25 | 35 unicas |
| Estaciones en el dataset final | 24 | 14 | 38 plazas (14 comunes; 35 unicas) |
| Registros ingresados (crudo) | 394.772 | 481.435 | 876.207 |
| Registros recibidos/procesados | 394.772 | 299.239 | 694.011 |
| Datos originales validos (L0) | 335.501 | 262.425 | 597.926 |
| Datos imputados (L1+L2+L3) | 54.835 | 28.981 | 83.816 |
| Faltantes finales (NaN) | 4.436 | 7.833 | 12.269 |
| Cobertura media | 98.87% | 97.74% | - |
| Cartillas por estacion | 24 | 14 | 38 |
| Figuras vigentes | 150 | 101 | 251 |
| Secciones de estación en los informes | 24 | 11 | 35 |
| Estaciones no incluidas en el informe | 0 | 14 | 14 |

> **Nota:** las 11 estaciones del informe de caudales son un subconjunto de las 24 de niveles. En total hay **24 estaciones únicas incluidas en al menos un informe** y **11 estaciones solo-caudales que no aparecen en ningún informe**.

## 2. Datos ingresados vs datos recibidos

### 2.1 Niveles

| Concepto | Valor |
|---|---:|
| Archivo crudo | `backend\entregables\niveles_v2_1\01_datos_originales\Resumen_Crudos_IDEAM_2026_v2_1.csv` |
| Filas crudas | 394.772 |
| Estaciones crudas | 24 |
| Rango crudo | 1960-01-01 a 2025-12-31 |
| Valores crudos validos | 335.501 |
| Valores crudos faltantes | 59.271 |
| Duplicados (estacion, fecha) | 0 |
| Filas del dataset final | 394.772 |
| L0 validos | 335.501 (84.99%) |
| L1 | 1.222 (0.31%) |
| L2 | 36.758 (9.31%) |
| L3 | 16.855 (4.27%) |
| Total imputado | 54.835 (13.89%) |
| NaN restantes | 4.436 (1.12%) |
| Cobertura media | 98.87% |
| Cobertura ponderada | 98.88% |
| Estaciones 100% | 12 |
| Estaciones >95% | 23 |
| Estaciones <95% | 1 |
| Estaciones descartadas por inhomogeneidad | 4 |

**Lectura:** el crudo tiene 394.772 filas y 59.271 faltantes. La imputacion lleno 54.835 valores y dejo 4.436 NaN documentados. El 85,0% del dataset final es dato original valido.

### 2.2 Caudales

| Concepto | Valor |
|---|---:|
| Archivo crudo largo | `backend\data\raw\SERIE_CAUDALES\analisis\caudales_formato_largo.csv` |
| Filas crudas | 481.435 |
| Estaciones crudas | 25 |
| Rango crudo | 1936-01-01 a 2026-12-31 |
| Ultima fecha con dato valido | 2026-03-14 |
| Valores crudos validos | 433.425 |
| Valores crudos faltantes | 48.010 |
| Duplicados (estacion, fecha) | 0 |
| Base unificada (ancho) | 205.722 filas x 25 estaciones |
| Fechas unicas en la base unificada | 32.946 |
| Lecturas por dia (promedio) | 6.24 |
| Celdas validas / faltantes | 850.273 / 4.292.777 |
| Filas del dataset final | 299.239 |
| L0 validos | 262.425 (87.7%) |
| L1 | 349 (0.12%) |
| L2 | 28.632 (9.57%) |
| Total imputado | 28.981 (9.68%) |
| NaN restantes | 7.833 (2.62%) |
| Cobertura media | 97.74% |
| Cobertura ponderada | 97.38% |
| Estaciones 100% | 7 |
| Estaciones >95% | 12 |
| Estaciones <95% | 2 |

**Lectura:** el crudo largo tiene 481.435 filas para 25 estaciones. La base unificada es sub-diaria (205.722 filas, 32.946 fechas); los scripts la promedian a diario. El dataset final se limita a las 14 estaciones comunes con niveles y a sus periodos oficiales: 299.239 filas, 87,7% originales, 9,7% imputadas y 2,6% NaN.

## 3. Niveles: desglose por estacion

| Estacion | Inicio | Fin | Dias | L0 | L1 | L2 | L3 | Imputados | NaN | Cobertura | Estado | Descartada |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| ARMENIA | 1973-02-01 | 2025-10-15 | 19.237 | 14.932 | 44 | 2.589 | 1.644 | 4.277 | 28 | 99.85% | OK | Si |
| BARBOSA | 1973-10-01 | 2024-12-20 | 18.696 | 14.350 | 27 | 3.658 | 0 | 3.685 | 661 | 96.46% | OK | Si |
| BARRANCABERMEJA | 1971-01-01 | 2025-12-31 | 20.075 | 19.116 | 62 | 23 | 0 | 85 | 874 | 95.65% | INCOMPLETA | No |
| CALAMAR | 1967-02-01 | 2025-12-31 | 21.500 | 19.887 | 13 | 86 | 83 | 182 | 1.431 | 93.34% | INCOMPLETA | No |
| COYONGAL | 1975-03-01 | 2025-12-27 | 18.552 | 15.633 | 44 | 1.860 | 1.015 | 2.919 | 0 | 100.0% | OK | No |
| EL_BANCO | 1972-10-01 | 2025-12-31 | 19.437 | 18.706 | 21 | 626 | 0 | 647 | 84 | 99.57% | INCOMPLETA | No |
| EL_CONTENTO | 1974-09-01 | 2025-12-31 | 18.737 | 12.692 | 98 | 2.506 | 3.441 | 6.045 | 0 | 100.0% | OK | No |
| GAMARRA | 1991-02-07 | 2018-10-29 | 10.120 | 6.906 | 44 | 1.822 | 1.348 | 3.214 | 0 | 100.0% | OK | No |
| GAMARRA_AUT | 2013-01-01 | 2025-12-31 | 4.745 | 4.397 | 18 | 0 | 99 | 117 | 231 | 95.13% | INCOMPLETA | No |
| LAS_AGUADAS | 1973-04-01 | 2025-08-31 | 19.133 | 18.749 | 19 | 365 | 0 | 384 | 0 | 100.0% | OK | No |
| LAS_PALOMAS | 1973-08-01 | 2025-06-30 | 18.949 | 15.689 | 72 | 3.188 | 0 | 3.260 | 0 | 100.0% | OK | No |
| LA_GLORIA | 1991-04-21 | 2025-12-31 | 12.665 | 11.109 | 57 | 1.136 | 0 | 1.193 | 363 | 97.13% | INCOMPLETA | No |
| MAGANGUE | 1973-04-01 | 2025-12-30 | 19.254 | 15.774 | 74 | 1.761 | 1.645 | 3.480 | 0 | 100.0% | OK | No |
| PENONCITO | 1972-10-01 | 2025-06-30 | 19.253 | 17.024 | 61 | 2.117 | 0 | 2.178 | 51 | 99.74% | INCOMPLETA | No |
| PLATO | 1976-06-01 | 2025-12-11 | 18.079 | 16.162 | 81 | 115 | 1.721 | 1.917 | 0 | 100.0% | OK | No |
| PUERTO_BERRIO | 1997-01-01 | 2025-11-10 | 10.534 | 10.297 | 20 | 217 | 0 | 237 | 0 | 100.0% | OK | No |
| PUERTO_SALGAR | 1960-01-01 | 2025-12-31 | 23.787 | 23.168 | 53 | 0 | 0 | 53 | 566 | 97.62% | INCOMPLETA | No |
| PUERTO_WILCHES | 2003-05-07 | 2025-09-11 | 8.158 | 7.806 | 36 | 191 | 0 | 227 | 125 | 98.47% | INCOMPLETA | No |
| RIO_NUEVO | 1974-10-01 | 2025-10-23 | 18.638 | 14.206 | 85 | 4.347 | 0 | 4.432 | 0 | 100.0% | OK | No |
| SAN_PABLO | 1977-08-01 | 2025-12-31 | 17.673 | 10.294 | 65 | 2.508 | 4.806 | 7.379 | 0 | 100.0% | OK | No |
| SAN_PEDRITO | 1979-01-01 | 2025-12-31 | 17.155 | 16.364 | 33 | 740 | 0 | 773 | 18 | 99.9% | INCOMPLETA | No |
| SITIO_NUEVO | 1979-03-01 | 2025-12-31 | 17.096 | 15.086 | 87 | 870 | 1.053 | 2.010 | 0 | 100.0% | OK | Si |
| TEBSA | 2014-01-02 | 2025-08-01 | 4.227 | 2.978 | 77 | 1.172 | 0 | 1.249 | 0 | 100.0% | OK | No |
| TENERIFE | 1973-10-01 | 2025-12-31 | 19.072 | 14.176 | 31 | 4.861 | 0 | 4.892 | 4 | 99.98% | OK | Si |

> **L0:** Dias - NaN - imputados. No incluye los NaN. La columna 'Original' de la auditoria incluye los NaN, por eso puede ser mayor.

## 4. Caudales: desglose por estacion

| Estacion | Inicio | Fin | Dias | L0 | L1 | L2 | Imputados | NaN | Cobertura | R2 N-C | L2 aceptado |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Calamar | 1940-07-23 | 2026-03-11 | 31.257 | 30.766 | 14 | 58 | 72 | 419 | 98.66% | 0.958 | Si |
| Magangué | 1973-03-01 | 2026-03-11 | 19.356 | 16.816 | 6 | 2.495 | 2.501 | 39 | 99.8% | 0.8342 | Si |
| Barbosa | 1973-10-01 | 2024-12-20 | 18.696 | 15.538 | 21 | 0 | 21 | 3.137 | 83.22% | 0.6734 | No |
| Armenia | 1973-02-01 | 2019-12-31 | 17.124 | 14.745 | 8 | 2.371 | 2.379 | 0 | 100.0% | 0.7752 | Si |
| Río Nuevo | 1974-09-01 | 2025-10-23 | 18.668 | 15.369 | 58 | 3.241 | 3.299 | 0 | 100.0% | 0.861 | Si |
| Las Palomas | 1973-08-01 | 2020-12-31 | 17.308 | 15.162 | 39 | 2.107 | 2.146 | 0 | 100.0% | 0.8846 | Si |
| Las Aguadas | 1973-04-01 | 2024-12-31 | 18.890 | 18.775 | 9 | 106 | 115 | 0 | 100.0% | 0.9676 | Si |
| El Banco | 1972-10-01 | 2026-02-25 | 19.493 | 18.944 | 15 | 450 | 465 | 84 | 99.57% | 0.888 | Si |
| Peñoncito | 1972-10-01 | 2026-01-31 | 19.468 | 18.195 | 26 | 1.196 | 1.222 | 51 | 99.74% | 0.8398 | Si |
| El Contento | 1975-02-01 | 2026-03-10 | 18.653 | 14.375 | 62 | 4.216 | 4.278 | 0 | 100.0% | 0.8773 | Si |
| Sitio Nuevo | 1979-02-01 | 2026-03-11 | 17.194 | 15.649 | 52 | 1.493 | 1.545 | 0 | 100.0% | 0.8809 | Si |
| San Pablo | 1977-07-01 | 2026-03-14 | 17.777 | 7.073 | 9 | 10.695 | 10.704 | 0 | 100.0% | 0.8339 | Si |
| Puerto Berrío | 1936-01-01 | 2025-11-11 | 32.800 | 32.488 | 21 | 203 | 224 | 88 | 99.73% | 0.8595 | Si |
| Puerto Salgar | 1937-01-01 | 2026-03-11 | 32.555 | 28.530 | 9 | 1 | 10 | 4.015 | 87.67% | 0.8832 | Si |

## 5. Figuras y cartillas

### 5.1 Vigentes

| Concepto | Niveles | Caudales | Total |
|---|---:|---:|---:|
| Cartillas por estacion | 24 | 14 | 38 |
| PNG dentro de cartillas | 143 | 98 | 241 |
| PNG globales (todas las estaciones) | 7 | 3 | 10 |
| **Total PNG vigentes** | **150** | **101** | **251** |

**Tipos por estacion - niveles:** Fig1=24, Fig2=24, Fig3=24, Fig4=24, Fig5=24, Fig6=23

**Tipos por estacion - caudales:** Fig1=14, Fig2=14, Fig3=14, Fig4=14, Fig6=14, Fig5_max=14, Fig5_min=14

### 5.2 Figuras historicas (no vigentes)

| Conjunto | PNG |
|---|---:|
| Niveles v4.2 | 151 |
| Niveles v4.3 | 91 |
| Curvas H-H v4.2 | 30 |
| Informes/estaciones | 10 |
| Informes/homogeneidad | 8 |
| Imagenes/Niveles | 6 |

### 5.3 Figuras en los borradores

| Borrador | Imagenes | Leyendas | Parrafos | Tablas | Comentarios |
|---|---:|---:|---:|---:|---:|
| Caudales - mayo 2026 | 37 | 38 | 110 | 0 | 7 |
| Caudales - julio 2026 | 57 | 37 | 175 | 0 | 11 |
| Niveles - julio 2026 | 105 | 112 | 424 | 4 | 19 |

- Niveles: 143 PNG de cartilla; el informe usa 96 (24 estaciones x 4 figuras). Quedan **47** figuras de cartilla sin insertar (Fig5 y Fig6; Puerto Salgar no tiene Fig6).
- Caudales: 98 PNG de cartilla; el informe usa 53 imagenes de estacion (57 totales: 4 generales + 53 de estacion). Quedan **45** figuras de estacion sin insertar: 22 de Fig3/Fig6 en las 11 incluidas + 21 de las 3 estaciones faltantes + 2 imagenes de extremos no insertadas.
- Caudales: 57 imagenes en el borrador y solo 37 leyendas; hay 20 imagenes sin caption (las de ajuste de extremos).

## 6. Estaciones incluidas y no incluidas en los informes

### 6.1 Niveles

- Incluidas en el informe: **24 de 24**.
- No incluidas: **0**.
- Marcadas como descartadas por inhomogeneidad (pero presentes en el informe): **4** (Armenia, Barbosa, Sitio Nuevo, Tenerife).

### 6.2 Caudales

- Incluidas en el informe: **11 de 14** estaciones comunes.
- Faltantes en el informe: **3** -> PUERTO_BERRIO, PUERTO_SALGAR, SAN_PABLO.
- No incluidas del universo de caudales: **14 de 25** (3 comunes faltantes + 11 solo-caudales).
- Solo-caudales (sin niveles): BARREDERO_FINCA, NOBLEZA_LA, PALENQUITO, PENAS_BLANCAS, PUENTE_SOGAMOSO, PUERTO_ARAUJO, PUERTO_LIBRE, SANTA_ANA, SANTA_ROSA, SAN_MIGUEL, SAN_ROQUE.

### 6.3 Universo combinado

- Estaciones unicas: **35** (14 comunes + 10 solo-niveles + 11 solo-caudales).
- Solo-niveles: BARRANCABERMEJA, COYONGAL, GAMARRA, GAMARRA_AUT, LA_GLORIA, PLATO, PUERTO_WILCHES, SAN_PEDRITO, TEBSA, TENERIFE.

## 7. Pruebas y validaciones

### 7.1 Niveles

- 0 violaciones de rango de cota, 0 registros fuera de rango temporal, 0 saltos temporales anomalos.
- 1 alerta del agente de validacion: Calamar con cobertura 93,34%.
- 88 pares con baja coherencia espacial (r < 0,7); correlacion espacial minima 0,2295.
- Comparacion con la corrida de estudiantes: 292.885 registros comparables; diferencia media absoluta 0,3220 m; maxima 3,8058 m.
- Modelos: 23 H-H L2 y 10 H-H L3; 552 parejas evaluadas.
- Homogeneidad: 25 estaciones, 7 pruebas (Pettitt, Mann-Kendall, F, t-Student, Cramer, Mann-Whitney, Shapiro-Wilk).

### 7.2 Caudales

- Verificacion de integridad: **9 checks ejecutados** (6 PASS, 0 FAIL, 2 INFO); el resumen final reporta que todos los checks criticos pasaron.
- Sin 29 de febrero, sin duplicados (estacion, fecha), sin caudales <= 0; estadisticos por estacion y anuales coinciden con los Excel originales.
- Curvas N-C: **14 modelos**, **222.993 pares**; R2 orden 2 entre **0.6734** y **0.9676**.
- L2 aceptado en **13** estaciones; rechazado en **1** (Barbosa, R2=0,6734).
- Homogeneidad del equipo: **25 estaciones**; **23** con Mann-Kendall significativo (p<0,05); **25** no normales.
- Tendencias MK: Creciente=14, Decreciente=9, Sin Tendencia=2.

## 8. Scripts y archivos

| Concepto | Valor |
|---|---:|
| Scripts de caudales | 6 |
| Scripts de niveles v2.1 | 13 |
| Modulos del pipeline reutilizable | 7 |

| Archivo clave | Tamano (MB) |
|---|---:|
| Niveles: resumen crudo | 10.65 |
| Niveles: dataset final | 16.58 |
| Niveles: resumen imputacion | 0.0 |
| Caudales: formato largo crudo | 19.58 |
| Caudales: base unificada | 14.74 |
| Caudales: dataset final | 12.14 |
| Caudales: resumen imputacion | 0.0 |
| Caudales: curvas N-C | 0.0 |
| Caudales: curvas de duracion | 0.0 |

## 9. Dudas abiertas de procesamiento

| Tema | Estado | Impacto | Siguiente paso |
|---|---|---|---|
| Estadistico Cramer del equipo | Descartado | No se reproduce con convenciones estandar | Documentar que no se uso |
| El Banco sub-diario vs equipo | Abierto | Pettitt/MK no coinciden | Confirmar version de datos del equipo |
| Barbosa sin L2 | Abierto | Cobertura 83,22% | Evaluar L3 Q-Q o curva N-C segmentada |
| Puerto Salgar 1937-1960 | Abierto | Sin niveles concurrentes | Mantener NaN documentado |
| L3 Q-Q entre estaciones | Standby | Barbosa y otras <95% | Disenar y ejecutar si se requiere |
| Curvas N-C segmentadas | Standby | Barbosa y Armenia con ramas paralelas | Evaluar por periodo |
| 11 vs 14 estaciones en el informe | Abierto | Faltan San Pablo, Puerto Berrio y Puerto Salgar | Actualizar el borrador |
| Outliers vs equipo | Resuelto | Diferencias de pruebas | Base oficial sin outliers |
| 29-feb y agregacion sub-diaria | Resuelto | Evita sesgos | Documentado en scripts |
| Figuras sin caption en caudales | Abierto | 20 imagenes sin leyenda | Agregar captions |
| Fig6 de Puerto Salgar en niveles | Abierto | No hay modelo H-H | Nota de no aplicabilidad |
| Versionado de datos y figuras | Abierto | Mucho material fuera de git | Release/ZIP + manifiesto |

## 10. Fuentes

- `backend\entregables\niveles_v2_1\01_datos_originales\Resumen_Crudos_IDEAM_2026_v2_1.csv`
- `backend\entregables\niveles_v2_1\02_datos_imputados\Datos_Imputados.csv`
- `backend\entregables\niveles_v2_1\05_validacion_y_auditoria\Resumen_Imputacion.csv`
- `backend\data\raw\SERIE_CAUDALES\analisis\caudales_formato_largo.csv`
- `backend\data\processed\caudales_unificados.csv`
- `backend\data\work\caudales_v1\output\Datos_Imputados_Caudales.csv`
- `backend\data\work\caudales_v1\output\Resumen_Imputacion_Caudales.csv`
- `cartillas_estaciones\Caudales\curvas_nivel_caudal_resumen.csv`
- `cartillas_estaciones\Caudales\curvas_duracion_caudales_resumen.csv`
- `backend\data\processed\Resultados_Pruebas_Homogeneidad.csv`
- `backend\data\raw\SERIE_CAUDALES\analisis\comparacion_estaciones.csv`
- `backend\data\raw\SERIE_CAUDALES\analisis\verificacion_caudales.txt`
- `backend\entregables\niveles_v2_1\05_validacion_y_auditoria\validacion_post_imputacion.md`
- `backend\entregables\niveles_v2_1\05_validacion_y_auditoria\agente_validacion_reporte.md`
- `docs\DRAFT_Caudales_Mayo2026_Informe_AED.docx`
- `docs\DRAFTS\CAUDALES\DRAFT_Caudales_Julio2026_Informe_AED (1).docx`
- `docs\DRAFTS\NIVELES\DRAFT_JULIO_2026_Informe_Analisis_Exploratorio_Magdalena_NIVELES.docx`

## 11. Métricas sugeridas para las diapositivas

1. **35 estaciones unicas** analizadas: 24 con niveles, 25 con caudales, 14 comunes.
2. **694.011 registros procesados** en total: 394.772 de niveles + 299.239 de caudales.
3. **54.835 datos imputados en niveles** (13,9%) y **28.981 en caudales** (9,7%).
4. **Cobertura media:** 98,87% en niveles y 97,74% en caudales.
5. **38 cartillas** generadas: 24 de niveles + 14 de caudales.
6. **251 figuras vigentes:** 150 de niveles + 101 de caudales.
7. **Informe de niveles:** 24/24 estaciones incluidas; 105 imagenes.
8. **Informe de caudales:** 11/14 estaciones comunes; faltan San Pablo, Puerto Berrio y Puerto Salgar; 57 imagenes y 37 leyendas.
9. **Pruebas:** 9 checks de caudales (6 PASS, 0 FAIL, 2 INFO), 0 violaciones de rango en niveles, 25 estaciones de homogeneidad.
10. **Brecha principal:** actualizar el informe de caudales a 14 estaciones y agregar Fig3/Fig6; resolver Barbosa y Puerto Salgar.
