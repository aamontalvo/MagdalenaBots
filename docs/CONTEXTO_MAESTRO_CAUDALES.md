# Contexto maestro - Niveles y caudales del Rio Magdalena

> **Corte de datos:** 24-ago-2026. **Generado:** 19-oct-2026.
> **Proposito:** dejar en un solo documento el contexto, las cifras verificadas, los scripts, las figuras, los informes y las dudas abiertas del proyecto.
> **Regla:** este documento se apoya en los datasets y reportes existentes; no reemplaza los datos originales ni modifica sus valores.

---

## 1. Identificacion del proyecto

| Campo | Valor |
|---|---|
| Proyecto | Diseno de un sistema de monitoreo hidro-ambiental para las cuencas bajas de los rios Magdalena y Sinu |
| BPIN | 2024000100122 |
| Contrato | UN-OJ-2025-66227 |
| Responsable | Alexander Alberto Montalvo Molina |
| Fuente hidrometrica | IDEAM |
| Periodo de analisis | Niveles: 1960-2025. Caudales: 1936-2026 (corte efectivo 2026-03-14) |
| Repositorio | https://github.com/aamontalvo/MagdalenaBots |

---

## 2. Resumen ejecutivo

El proyecto trabaja dos variables hidrologicas sobre la misma red de estaciones:

- **Niveles (cotas):** 24 estaciones, 394.772 registros finales, 54.835 valores imputados (13,89%) y 4.436 NaN documentados (1,12%). Cobertura media: **98,87%**.
- **Caudales:** 25 estaciones en la fuente, 14 comunes con niveles, 299.239 registros finales, 28.981 valores imputados (9,68%) y 7.833 NaN documentados (2,62%). Cobertura media: **97,74%**.
- **Universo combinado:** 35 estaciones unicas (14 comunes + 10 solo-niveles + 11 solo-caudales).
- **Productos:** 38 cartillas (24 de niveles + 14 de caudales) y **251 figuras vigentes** (150 de niveles + 101 de caudales).
- **Informes:** el de niveles cubre 24/24 estaciones; el de caudales cubre 11/14 estaciones comunes y aun no incorpora San Pablo, Puerto Berrio ni Puerto Salgar.

**Lectura correcta de las cifras:**

- **Datos ingresados:** filas de la fuente cruda, incluyendo faltantes.
- **Datos recibidos/procesados:** filas del dataset final, después de preparar, imputar y documentar faltantes.
- **L0:** dato original valido. **L1:** interpolacion local. **L2/L3:** modelos H-H o N-C.
- **Cobertura:** porcentaje de dias con dato (original o imputado) dentro del rango oficial.

---

## 3. Universo de estaciones

### 3.1 Estaciones con niveles (24)

ARMENIA, BARBOSA, BARRANCABERMEJA, CALAMAR, COYONGAL, EL_BANCO, EL_CONTENTO, GAMARRA, GAMARRA_AUT, LAS_AGUADAS, LAS_PALOMAS, LA_GLORIA, MAGANGUE, PENONCITO, PLATO, PUERTO_BERRIO, PUERTO_SALGAR, PUERTO_WILCHES, RIO_NUEVO, SAN_PABLO, SAN_PEDRITO, SITIO_NUEVO, TEBSA, TENERIFE.

### 3.2 Estaciones con caudales (25 en la fuente; 14 en el dataset final)

Las 14 comunes con niveles son:

CALAMAR, MAGANGUE, BARBOSA, ARMENIA, RIO_NUEVO, LAS_PALOMAS, LAS_AGUADAS, EL_BANCO, PENONCITO, EL_CONTENTO, SITIO_NUEVO, SAN_PABLO, PUERTO_BERRIO, PUERTO_SALGAR.

Las 11 estaciones solo-caudales (sin niveles) son:

BARREDERO_FINCA, NOBLEZA_LA, PALENQUITO, PENAS_BLANCAS, PUENTE_SOGAMOSO, PUERTO_ARAUJO, PUERTO_LIBRE, SAN_MIGUEL, SAN_ROQUE, SANTA_ANA, SANTA_ROSA.

### 3.3 Estaciones solo-niveles (10)

BARRANCABERMEJA, COYONGAL, GAMARRA, GAMARRA_AUT, LA_GLORIA, PLATO, PUERTO_WILCHES, SAN_PEDRITO, TEBSA, TENERIFE.

---

## 4. Linaje de datos

### 4.1 Niveles

```
Excel IDEAM (18 archivos) + Version Homegeneizada HAR STEFY (24 estaciones)
        |
        v
Resumen_Crudos_IDEAM_2026_v2_1.csv     394.772 filas | 24 estaciones | 1960-2025
        |
        v
Datos_Imputados.csv                    394.772 filas | L0 335.501 | L1 1.222 | L2 36.758 | L3 16.855
        |
        +--> 24 cartillas x 6 figuras (143 PNG)
        +--> 7 figuras globales (PNG)
        +--> Informe de niveles (24 estaciones, 105 imagenes)
```

- **Crudo:** 394.772 filas, 335.501 valores validos, 59.271 faltantes, 0 duplicados `(estacion, fecha)`.
- **Final:** 394.772 filas, 335.501 L0 validos (84,99%), 1.222 L1 (0,31%), 36.758 L2 (9,31%), 16.855 L3 (4,27%), 54.835 imputados (13,89%), 4.436 NaN (1,12%).
- **Cobertura media:** 98,87%. **Ponderada:** 98,88%.
- **Estaciones al 100%:** 12. **>95%:** 23. **<95%:** 1 (Calamar, 93,34%).
- **Descartadas por inhomogeneidad:** 4 (Armenia, Barbosa, Sitio Nuevo, Tenerife), aunque permanecen en el informe con advertencia.

### 4.2 Caudales

```
26 archivos Excel de caudales (25 estaciones + 1 duplicado)
        |
        v
caudales_formato_largo.csv             481.435 filas | 25 estaciones | 1936-2026-12-31
        |
        v
caudales_unificados.csv                205.722 filas | 25 estaciones | sub-diario | 32.946 fechas
        |
        v  (promedio diario + periodos oficiales + 29-feb excluido)
Datos_Imputados_Caudales.csv           299.239 filas | 14 estaciones | L0 262.425 | L1 349 | L2 28.632
        |
        +--> 14 cartillas x 7 figuras (98 PNG)
        +--> 3 figuras globales (PNG)
        +--> Informe de caudales (11 estaciones, 57 imagenes)
```

- **Crudo largo:** 481.435 filas, 433.425 valores validos, 48.010 faltantes, 0 duplicados `(estacion, fecha)`.
- **Base unificada:** 205.722 filas sub-diarias, 25 estaciones, 32.946 fechas, 6,24 lecturas por dia en promedio.
- **Final:** 299.239 filas, 14 estaciones, 262.425 L0 validos (87,7%), 349 L1 (0,12%), 28.632 L2 (9,57%), 28.981 imputados (9,68%), 7.833 NaN (2,62%).
- **Cobertura media:** 97,74%. **Ponderada:** 97,38%.
- **Estaciones al 100%:** 7. **>95%:** 12. **<95%:** 2 (Barbosa 83,22% y Puerto Salgar 87,67%).
- **Curvas N-C:** 14 modelos, 222.993 pares, R2 orden 2 entre 0,6734 y 0,9676. L2 aceptado en 13 estaciones; rechazado en Barbosa (R2=0,6734).

---

## 5. Niveles v2.1

### 5.1 Pipeline

| Paso | Script | Funcion |
|---|---|---|
| 1 | `01_compare_raw_versions.py` | Comparacion del raw nuevo vs el anterior. |
| 2 | `02_prepare_dataset.py` | Limpieza, corte 2025, eliminacion 29-feb, deduplicacion y rangos oficiales. |
| 3 | `03_hh_discovery.py` | Descubrimiento y seleccion de modelos H-H. |
| 4 | `04_run_imputation.py` | Imputacion en cascada L1 -> L2 -> L3. |
| 5 | `05_validate_and_report.py` | Validaciones, comparacion con la corrida anterior y heatmaps. |
| 6 | `06_auditoria_12_estaciones.py` | Auditoria detallada de 12 estaciones. |
| 7 | `07_auditoria_todas_estaciones.py` | Auditoria de las 24 estaciones. |
| 8 | `13_agente_validacion.py` | Agente de validacion automatica. |
| 9 | `14_generar_cartillas_v2_1.py` | Cartillas tecnicas (6 figuras por estacion). |
| 10 | `15_figuras_globales_v2_1.py` | Figuras globales. |

El paquete reutilizable `imputation_pipeline_v2_1/` contiene `config`, `loaders`, `hh_selector`, `imputers`, `hard_rules` y `tracker`.

### 5.2 Resultados

- 23 modelos H-H L2 y 10 modelos H-H L3; 552 parejas evaluadas.
- 0 violaciones de rango de cota, 0 registros fuera de rango temporal y 0 saltos anomalos.
- 1 alerta del agente de validacion: Calamar con cobertura 93,34%.
- 88 pares con baja coherencia espacial (r < 0,7); correlacion minima 0,2295.
- Comparacion con la corrida de estudiantes: 292.885 registros comparables; diferencia media absoluta 0,3220 m; maxima 3,8058 m.

### 5.3 Figuras

- 24 cartillas, una por estacion.
- 143 PNG de cartilla: Fig1=24, Fig2=24, Fig3=24, Fig4=24, Fig5=24, Fig6=23 (Puerto Salgar no tiene H-H).
- 7 PNG globales.
- Total vigente: **150 PNG**.
- El informe de julio usa 96 figuras de estacion (24 x 4) y 9 imagenes generales; quedan **47** figuras de cartilla sin insertar (Fig5 y Fig6).

---

## 6. Caudales v1

### 6.1 Base y agregacion

- La fuente es sub-diaria. `caudales_unificados.csv` tiene 205.722 filas para 32.946 fechas; los scripts hacen `groupby(fecha).mean()` por estacion.
- Se excluye el 29 de febrero en todos los calculos.
- El periodo oficial va del primer al ultimo caudal valido de cada estacion.
- El dataset final se limita a las 14 estaciones comunes con niveles.

### 6.2 Imputacion

- **L1:** interpolacion local ponderada con kernel `{0,1; 0,2; 0,4; 0,2; 0,1}` para gaps de hasta 3 dias.
- **L2:** curva Nivel-Caudal propia `Q = f(H)`, polinomio de orden 2 (orden 3 solo si mejora R2 en mas de 0,01), entrenada con pares originales concurrentes. Umbral: R2 >= 0,75.
- **Reglas duras:** nada fuera del periodo oficial, nada sin soporte empirico, NaN documentado y trazabilidad por nivel.
- **Resultado:** 349 L1, 28.632 L2, 28.981 imputados, 7.833 NaN. Barbosa quedo sin L2 por R2=0,6734. Puerto Salgar conserva 4.015 NaN por falta de niveles antes de 1960.

### 6.3 Curvas N-C y curvas de duracion

- **N-C:** 14 modelos y 222.993 pares. R2 orden 2: 0,6734 (Barbosa) a 0,9676 (Las Aguadas). Orden 3 mejora marginalmente (Delta R2 < 0,003); orden 2 es suficiente.
- **Duracion:** se genero la Fig3 de caudales para las 14 estaciones, replicando la estructura de niveles. P50, P90, P95 y P100 estan en `curvas_duracion_caudales_resumen.csv`.

### 6.4 Figuras

- 14 cartillas, una por estacion.
- 98 PNG de cartilla: Fig1=14, Fig2=14, Fig3=14, Fig4=14, Fig5_max=14, Fig5_min=14, Fig6=14.
- 3 PNG globales: boxplot, matriz de correlacion y heatmap de cobertura.
- Total vigente: **101 PNG**.
- El informe de julio usa 57 imagenes: 4 generales + 53 de estacion; solo 37 tienen leyenda. Quedan **45** figuras de estacion sin insertar: 22 de Fig3/Fig6 en las 11 estaciones incluidas + 21 de las 3 estaciones faltantes + 2 imagenes de extremos no insertadas.

---

## 7. Pruebas y validaciones

### Niveles

- 0 violaciones de rango de cota, 0 registros fuera de rango temporal, 0 saltos anomalos.
- 1 alerta de cobertura (Calamar).
- 88 pares con r < 0,7; correlacion minima 0,2295.
- 23 modelos L2 + 10 modelos L3; 552 parejas evaluadas.
- Homogeneidad: 25 estaciones, 7 pruebas (Pettitt, Mann-Kendall, F, t-Student, Cramer, Mann-Whitney, Shapiro-Wilk).

### Caudales

- 9 checks ejecutados: 6 PASS, 0 FAIL, 2 INFO; el resumen final confirma que todos los checks criticos pasaron.
- Sin 29-feb, sin duplicados, sin caudales <= 0; estadisticos por estacion y anuales coinciden con los Excel originales.
- 14 modelos N-C; 222.993 pares; 13 L2 aceptados y 1 rechazado.
- Homogeneidad del equipo: 25 estaciones; 23 con Mann-Kendall significativo (p<0,05); 25 no normales. Tendencias: 14 crecientes, 9 decrecientes, 2 sin tendencia.

---

## 8. Informes

| Borrador | Estaciones | Imagenes | Leyendas | Parrafos | Tablas | Comentarios |
|---|---:|---:|---:|---:|---:|---:|
| Caudales - mayo 2026 | 11 | 37 | 38 | 110 | 0 | 7 |
| Caudales - julio 2026 | 11 | 57 | 37 | 175 | 0 | 11 |
| Niveles - julio 2026 | 24 | 105 | 112 | 424 | 4 | 19 |

### Brechas del informe de caudales

1. Cubre 11 de 14 estaciones comunes; faltan San Pablo, Puerto Berrio y Puerto Salgar.
2. La seccion "Imputacion de datos" esta vacia: solo tiene el titulo.
3. La seccion "Anexos" esta vacia.
4. 20 imagenes de ajuste de extremos no tienen leyenda.
5. Varios titulos y leyendas dicen "niveles" donde deberia decir "caudales".
6. Algunas cifras del resumen ejecutivo no coinciden con el dataset final; usar las metricas de este documento.
7. No incluye Fig3 (curva de duracion) ni Fig6 (curva N-C).

### Brechas del informe de niveles

1. Usa 4 figuras por estacion (Fig1-Fig4); no inserta Fig5 (ajuste de distribuciones) ni Fig6 (relacion H-H).
2. La numeracion de figuras se reinicia en la seccion de imputacion (comentario de Alex en el documento).
3. Puerto Salgar no tiene Fig6 porque no tiene modelo H-H aceptado.
4. El resumen ejecutivo dice "originales ~82,0%"; el dataset final da **84,99%**.

---

## 9. Scripts

| Grupo | Cantidad | Ruta |
|---|---:|---|
| Caudales v1 | 7 | `backend/scripts/caudales_v1/` |
| Niveles v2.1 | 13 | `backend/scripts/imputation_v2_1/` |
| Modulos del pipeline | 7 | `backend/scripts/imputation_v2_1/imputation_pipeline_v2_1/` |

Orden de ejecucion de caudales:

1. `01_figuras_caudales.py`
2. `02_cartillas_caudales_resto.py`
3. `03_curvas_nivel_caudal.py`
4. `04_imputacion_caudales.py`
5. `05_curva_duracion_caudales.py`
6. `06_metricas_consolidadas.py`
7. `07_consolidado_excel.py`

---

## 10. Inventario de figuras

### Vigentes

| Concepto | Niveles | Caudales | Total |
|---|---:|---:|---:|
| Cartillas | 24 | 14 | 38 |
| PNG dentro de cartillas | 143 | 98 | 241 |
| PNG globales | 7 | 3 | 10 |
| **Total** | **150** | **101** | **251** |

### Historicas (no vigentes)

| Conjunto | PNG |
|---|---:|
| Niveles v4.2 | 151 |
| Niveles v4.3 | 91 |
| Curvas H-H v4.2 | 30 |
| Informes/estaciones | 10 |
| Informes/homogeneidad | 8 |
| Imagenes/Niveles | 6 |

---

## 11. Estaciones incluidas y no incluidas en los informes

| Informe | Incluidas | No incluidas |
|---|---:|---|
| Niveles | 24 de 24 | 0 |
| Caudales | 11 de 14 comunes | 3 comunes (San Pablo, Puerto Berrio, Puerto Salgar) + 11 solo-caudales |

- **24 estaciones unicas** aparecen en al menos un informe.
- **11 estaciones solo-caudales** no aparecen en ningun informe.
- **4 estaciones** estan marcadas como inhomogeneas pero permanecen en el informe de niveles: Armenia, Barbosa, Sitio Nuevo y Tenerife.

---

## 12. Dudas abiertas de procesamiento

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

---

## 13. Proximos pasos recomendados

1. Actualizar el informe de caudales a 14 estaciones (agregar San Pablo, Puerto Berrio y Puerto Salgar).
2. Escribir la seccion de imputacion de caudales con la misma estructura de niveles.
3. Insertar Fig3 (duracion) y Fig6 (N-C) en el informe de caudales; agregar captions a las 20 imagenes de extremos.
4. Insertar Fig5 y Fig6 en el informe de niveles; documentar la ausencia de Fig6 en Puerto Salgar.
5. Corregir la cifra de originales de niveles a 84,99%.
6. Resolver Barbosa (L3 Q-Q o N-C segmentada) y documentar Puerto Salgar 1937-1960.
7. Versionar los scripts y documentos; mantener los datos y figuras en un paquete de respaldo con manifiesto.

---

## 14. Fuentes

- `backend/entregables/niveles_v2_1/01_datos_originales/Resumen_Crudos_IDEAM_2026_v2_1.csv`
- `backend/entregables/niveles_v2_1/02_datos_imputados/Datos_Imputados.csv`
- `backend/entregables/niveles_v2_1/05_validacion_y_auditoria/Resumen_Imputacion.csv`
- `backend/entregables/niveles_v2_1/05_validacion_y_auditoria/validacion_post_imputacion.md`
- `backend/data/raw/SERIE_CAUDALES/analisis/caudales_formato_largo.csv`
- `backend/data/processed/caudales_unificados.csv`
- `backend/data/work/caudales_v1/output/Datos_Imputados_Caudales.csv`
- `backend/data/work/caudales_v1/output/Resumen_Imputacion_Caudales.csv`
- `cartillas_estaciones/Caudales/curvas_nivel_caudal_resumen.csv`
- `cartillas_estaciones/Caudales/curvas_duracion_caudales_resumen.csv`
- `backend/data/processed/Resultados_Pruebas_Homogeneidad.csv`
- `backend/data/raw/SERIE_CAUDALES/analisis/verificacion_caudales.txt`
- `docs/DRAFT_Caudales_Mayo2026_Informe_AED.docx`
- `docs/DRAFTS/CAUDALES/DRAFT_Caudales_Julio2026_Informe_AED (1).docx`
- `docs/DRAFTS/NIVELES/DRAFT_JULIO_2026_Informe_Analisis_Exploratorio_Magdalena_NIVELES.docx`
- `docs/METRICAS_CAUDALES_NIVELES.md`
- `docs/metricas_caudales_niveles.json`
