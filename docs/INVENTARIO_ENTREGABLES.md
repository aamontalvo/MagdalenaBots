# Inventario de entregables - Niveles y caudales

> **Corte:** 24-ago-2026. **Generado:** 19-oct-2026.
> Los tamanos son aproximados y sirven para dimensionar el paquete; no reemplazan los archivos originales.

## 1. Datos

| Archivo | Filas | Estaciones | Periodo | Tamano | Estado |
|---|---:|---:|---|---:|---|
| `backend/entregables/niveles_v2_1/01_datos_originales/Resumen_Crudos_IDEAM_2026_v2_1.csv` | 394.772 | 24 | 1960-2025 | 10,65 MB | Crudo preparado |
| `backend/entregables/niveles_v2_1/02_datos_imputados/Datos_Imputados.csv` | 394.772 | 24 | 1960-2025 | 16,58 MB | Final vigente |
| `backend/entregables/niveles_v2_1/05_validacion_y_auditoria/Resumen_Imputacion.csv` | 24 | 24 | - | <0,1 MB | Resumen |
| `backend/data/raw/SERIE_CAUDALES/analisis/caudales_formato_largo.csv` | 481.435 | 25 | 1936-2026 | 19,58 MB | Crudo largo |
| `backend/data/processed/caudales_unificados.csv` | 205.722 | 25 | 1936-2026-03 | 14,74 MB | Base sub-diaria |
| `backend/data/work/caudales_v1/output/Datos_Imputados_Caudales.csv` | 299.239 | 14 | 1936-2026-03 | 12,14 MB | Final vigente |
| `backend/data/work/caudales_v1/output/Resumen_Imputacion_Caudales.csv` | 14 | 14 | - | <0,1 MB | Resumen |
| `backend/data/processed/Resultados_Pruebas_Homogeneidad.csv` | 25 | 25 | - | <0,1 MB | Pruebas del equipo |
| `backend/data/raw/SERIE_CAUDALES/analisis/comparacion_estaciones.csv` | 29 | 29 | - | <0,1 MB | Comparacion niveles-caudales |
| `backend/data/raw/SERIE_CAUDALES/analisis/verificacion_caudales.txt` | - | - | - | <0,1 MB | 9 checks |

## 2. Resumenes y metricas

| Archivo | Contenido | Estado |
|---|---|---|
| `docs/METRICAS_CAUDALES_NIVELES.md` | Tablero completo de metricas, pruebas, figuras y estaciones | Vigente |
| `docs/metricas_caudales_niveles.json` | Misma informacion en formato maquina | Vigente |
| `docs/CONTEXTO_MAESTRO_CAUDALES.md` | Contexto, linaje, scripts, informes y dudas | Vigente |
| `cartillas_estaciones/Caudales/curvas_nivel_caudal_resumen.csv` | 14 modelos N-C, R2 y ecuaciones | Vigente |
| `cartillas_estaciones/Caudales/curvas_duracion_caudales_resumen.csv` | P50, P90, P95 y P100 por estacion | Vigente |
| `cartillas_estaciones/Caudales/Cobertura_Caudales.csv` | Cobertura anual por estacion | Vigente |
| `cartillas_estaciones/Caudales/Outliers_Caudales.csv` | Outliers detectados | Vigente |
| `cartillas_estaciones/Caudales/Eventos_Abruptos_Caudales.csv` | Eventos abruptos | Vigente |
| `cartillas_estaciones/Caudales/Matriz_Correlacion_Caudales.csv` | Correlacion entre estaciones | Vigente |
| `cartillas_estaciones/Caudales/Matriz_N_Concurrentes_Caudales.csv` | Pares concurrentes | Vigente |
| `cartillas_estaciones/Caudales/Resumen_Homogeneidad_Caudales.csv` | Homogeneidad de caudales | Vigente |

## 3. Figuras y cartillas

| Concepto | Cantidad | Ruta |
|---|---:|---|
| Cartillas de niveles | 24 | `backend/entregables/niveles_v2_1/07_cartillas/` |
| PNG de cartillas de niveles | 143 | `backend/entregables/niveles_v2_1/07_cartillas/` |
| PNG globales de niveles | 7 | `backend/entregables/niveles_v2_1/06_figuras/` |
| Cartillas de caudales | 14 | `cartillas_estaciones/Caudales/` |
| PNG de cartillas de caudales | 98 | `cartillas_estaciones/Caudales/<ESTACION>/` |
| PNG globales de caudales | 3 | `cartillas_estaciones/Caudales/` |
| **Total figuras vigentes** | **251** | - |

### Figuras historicas

| Conjunto | PNG |
|---|---:|
| `cartillas_estaciones/v4_2/` | 151 |
| `cartillas_estaciones/v4_3/` | 91 |
| `Informes/imputacion/Curvas_HH_v4_2/` | 30 |
| `Informes/estaciones/` | 10 |
| `Informes/homogeneidad/` | 8 |
| `Imagenes/Niveles/` | 6 |

## 4. Informes

| Archivo | Estaciones | Imagenes | Leyendas | Tamano | Estado |
|---|---:|---:|---:|---:|---|
| `docs/DRAFT_Caudales_Mayo2026_Informe_AED.docx` | 11 | 37 | 38 | 7,0 MB | Historico |
| `docs/DRAFTS/CAUDALES/DRAFT_Caudales_Julio2026_Informe_AED (1).docx` | 11 | 57 | 37 | 11,5 MB | Borrador vigente |
| `docs/DRAFTS/NIVELES/DRAFT_JULIO_2026_Informe_Analisis_Exploratorio_Magdalena_NIVELES.docx` | 24 | 105 | 112 | 27,2 MB | Borrador vigente |

## 5. Scripts

| Grupo | Archivos | Ruta |
|---|---:|---|
| Caudales v1 | 7 | `backend/scripts/caudales_v1/` |
| Niveles v2.1 | 13 | `backend/scripts/imputation_v2_1/` |
| Pipeline reutilizable | 7 | `backend/scripts/imputation_v2_1/imputation_pipeline_v2_1/` |

### Scripts de caudales

| Script | Funcion |
|---|---|
| `01_figuras_caudales.py` | Fig2, boxplot, correlacion y heatmap. |
| `02_cartillas_caudales_resto.py` | Fig1, Fig4, Fig5 max/min. |
| `03_curvas_nivel_caudal.py` | Fig6 y resumen N-C. |
| `04_imputacion_caudales.py` | L1 + L2. |
| `05_curva_duracion_caudales.py` | Fig3 (nueva, alineacion con niveles). |
| `06_metricas_consolidadas.py` | Metricas y JSON. |
| `07_consolidado_excel.py` | Excel consolidado con hojas de resumen. |

## 6. Pruebas y auditoria

| Archivo | Contenido |
|---|---|
| `backend/entregables/niveles_v2_1/05_validacion_y_auditoria/validacion_post_imputacion.md` | Validacion de niveles |
| `backend/entregables/niveles_v2_1/05_validacion_y_auditoria/agente_validacion_reporte.md` | Alertas del agente |
| `backend/entregables/niveles_v2_1/05_validacion_y_auditoria/auditoria_todas_estaciones.md` | Auditoria de 24 estaciones |
| `backend/data/raw/SERIE_CAUDALES/analisis/verificacion_caudales.txt` | 9 checks de caudales |
| `backend/data/processed/Resultados_Pruebas_Homogeneidad.csv` | 25 estaciones, 7 pruebas |

## 7. Comentarios y revision

| Archivo | Contenido |
|---|---|
| `docs/RESPUESTAS_COMENTARIOS_STEFANY.md` | Comentarios de Stefany y respuestas de Alex |
| `docs/ESTADO_CAUDALES_PARA_STEPHANIE.md` | Estado actual, brechas y preguntas |
| `docs/METRICAS_CAUDALES_NIVELES.md` | Tablero de cifras para diapositivas |

## 8. Paquete consolidado

| Archivo | Contenido |
|---|---|
| `backend/entregables/caudales_v1/Consolidado_Caudales_Niveles.xlsx` | Hojas de KPIs, resumenes, curvas, homogeneidad y dudas |
| `backend/entregables/caudales_v1/README.md` | Guia de uso del consolidado |

> Los datos completos y las figuras no se duplican en el Excel; se referencian por ruta para evitar un archivo de cientos de MB.
