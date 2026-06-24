# Informe de entrega - Imputacion de niveles IDEAM v2.1

> **Nota:** No se dispone del plugin de WPS/Word en este entorno, por lo que se genera este documento en Markdown para que otro agente con el plugin correspondiente lo convierta a `.docx` si es necesario.

---

## 1. Contexto y objetivo

Se construyo el pipeline v2.1 de imputacion de niveles de agua del IDEAM para la cuenca del Magdalena, con las siguientes reglas de negocio:

- Incluir las 24 estaciones del raw corregido (Version Homegeneizada HAR STEFY).
- Corte temporal global al 31 de diciembre de 2025.
- Eliminar el 29 de febrero de todos los anos.
- Respetar el **rango oficial** de cada estacion: para estaciones comunes con el raw anterior se conservo su rango historico; para las nuevas se uso su propio rango valido.
- No imputar **fuera del rango oficial** de ninguna estacion.
- Permitir donantes H-H en cualquier orientacion geografica (libre aguas arriba/abajo).
- Mantener R2 >= 0.75 para modelos H-H.
- Descartar (pero conservar en el output) las estaciones inhomogeneas: ARMENIA, BARBOSA, SITIO_NUEVO, TENERIFE.
- Conservar los `NaN` dentro del rango oficial para que el dataset final refleje cobertura real.

Commit de referencia: `ed1bfb0` — `feat(imputation): pipeline v2.1 con mascara de rango oficial y auditoria`

---

## 2. Que se hizo

### 2.1 Pipeline v2.1 (`backend/scripts/imputation_v2_1/`)

| Script / Paquete | Funcion |
|---|---|
| `01_compare_raw_versions.py` | Comparacion del raw nuevo vs el raw anterior. |
| `02_prepare_dataset.py` | Limpieza, normalizacion de nombres, corte 2025, eliminacion 29-Feb, deduplicacion y generacion de `resumen_rangos_estaciones.csv`. |
| `03_hh_discovery.py` | Descubrimiento y seleccion de modelos H-H sin restriccion de orientacion. |
| `04_run_imputation.py` | Imputacion en cascada L1 (interpolacion local) -> L2 (H-H cuadratica) respetando la mascara de rango oficial. |
| `05_validate_and_report.py` | Validaciones post-imputacion, comparacion con corrida anterior y nuevos heatmaps de nulos. |
| `06_auditoria_12_estaciones.py` | Auditoria detallada de 12 estaciones representativas. |
| `07_auditoria_todas_estaciones.py` | Auditoria detallada de las 24 estaciones con figura individual por estacion. |
| `imputation_pipeline_v2_1/` | Paquete reutilizable: config, loaders, hh_selector, imputers, hard_rules, tracker. |

### 2.2 Outputs principales (`backend/data/work/imputation_v2_1/output/`)

| Archivo | Descripcion |
|---|---|
| `Resumen_Crudos_IDEAM_2026_v2_1.csv` | Dataset crudo preparado (sin imputar). |
| `resumen_rangos_estaciones.csv` | Rango oficial usado por estacion. |
| `Tabla_Modelos_HH_Seleccionados.csv` | 23 modelos H-H seleccionados (R2 >= 0.75). |
| `Datos_Imputados.csv` | Dataset final con niveles de imputacion y metodo, acotado a rangos oficiales, incluye NaN. |
| `Resumen_Imputacion.csv` | Cobertura real por estacion. |
| `validacion_post_imputacion.md` | Reporte de validacion. |
| `figura_heatmap_nulos_antes_despues.png` | Heatmap de datos nulos antes y despues de la imputacion. |
| `figura_cobertura_imputacion.png` | Barras apiladas de originales, L1 y L2. |
| `figura_series_temporales.png` | Series temporales de ejemplo. |
| `auditoria_12_estaciones.md` | Reporte Markdown con tablas y 12 figuras. |
| `auditoria_todas_estaciones.md` | Reporte Markdown con tablas y 24 figuras. |
| `figuras/auditoria/auditoria_<ESTACION>.png` | Figura de auditoria individual por estacion. |

---

## 3. Hallazgos clave

### 3.1 Correccion critica: imputacion fuera de rango

En la primera version del pipeline se generaron **44,599 registros fuera del rango oficial** (44,598 de ellos imputaciones L2). Esto se detecto en la auditoria de las 12 estaciones (por ejemplo, TEBSA se extendia hasta 1971 a pesar de que su rango oficial inicia en 2014).

**Solucion aplicada:**
- Se cargo `resumen_rangos_estaciones.csv` como mascara oficial.
- Se forzaron a `NaN` todas las fechas fuera del rango antes de la imputacion.
- L1 no imputa gaps que toquen los bordes del rango.
- L2 solo imputa cuando el objetivo esta dentro de su rango oficial.
- `build_tracked_dataset()` descarta registros fuera del rango oficial.

**Verificacion final:**
- Registros fuera de rango oficial: **0**
- Violaciones de rango historico de cota: **0**
- Saltos temporales anomalos: **0**

### 3.2 Cobertura del dataset final

- **Registros totales en `Datos_Imputados.csv`:** 394,772
- **Originales:** ~89.7%
- **Imputados L1:** 1,222
- **Imputados L2:** 36,758

### 3.3 Modelos H-H

- Se evaluaron **552 parejas** y se seleccionaron **23 modelos**.
- Unica estacion **sin modelo H-H viable:** `PUERTO_SALGAR` (llego a 97.62% de cobertura solo con L1).

### 3.4 Estaciones con cobertura completa dentro del rango oficial (100%)

`LAS_AGUADAS`, `LAS_PALOMAS`, `PUERTO_BERRIO`, `RIO_NUEVO`, `TEBSA`

### 3.5 Estaciones con cobertura alta pero no completa (>95%)

| Estacion | Cobertura | NaN restantes | Observacion |
|---|---|---|---|
| EL_BANCO | 99.57% | 84 | Muy alta, NaN aislados. |
| SAN_PEDRITO | 99.90% | 18 | Muy alta. |
| TENERIFE | 99.98% | 4 | Marcada como descartada pero casi completa. |
| PENONCITO | 99.74% | 51 | Muy alta. |
| BARBOSA | 96.46% | 661 | Descartada por inhomogeneidad. |
| PUERTO_WILCHES | 98.47% | 125 | Alta. |
| BARRANCABERMEJA | 95.65% | 874 | Donante con poca concurrencia al inicio. |
| COYONGAL | 94.53% | 1,015 | Moderada. |
| LA_GLORIA | 97.13% | 363 | Alta. |
| SITIO_NUEVO | 93.84% | 1,053 | Descartada por inhomogeneidad. |
| GAMARRA_AUT | 93.05% | 330 | Sin L2 (no hay gaps L2 dentro del rango). |

### 3.6 Estaciones con cobertura problematica (<93%)

| Estacion | Cobertura | NaN restantes | Observacion |
|---|---|---|---|
| SAN_PABLO | 72.81% | 4,806 | La peor cobertura; el donante `PUERTO_WILCHES` no cubre gran parte del rango de SAN_PABLO. |
| EL_CONTENTO | 81.64% | 3,441 | Sin donante fuerte cercano; requiere revision. |
| GAMARRA | 86.68% | 1,348 | Serie corta; modelo con `GAMARRA_AUT` basado en solo 193 puntos. |
| ARMENIA | 91.31% | 1,672 | Descartada por inhomogeneidad. |
| MAGANGUE | 91.46% | 1,645 | Revisar donante `TENERIFE`. |
| CALAMAR | 92.96% | 1,514 | Sorprendentemente baja para una estacion con muchos datos; los NaN restantes estan en un periodo sin donante concurrente. |
| PLATO | 90.48% | 1,721 | Donante `TEBSA` con rango corto. |

### 3.7 Comparacion con corrida anterior (estudiantes)

- Registros comparables: **292,885**
- Diferencia media absoluta: **0.3174 m**
- Diferencia maxima absoluta: **3.8058 m**

La mayor diferencia maxima se presenta en estaciones con mucha imputacion L2 (CALAMAR, TENERIFE, LA_GLORIA), lo cual es esperado.

---

## 4. Que falta por hacer

1. **Decision sobre los NaN restantes**
   - Las estaciones con cobertura < 100% tienen `NaN` porque no hay donante concurrente en esos periodos y los gaps son mayores a 3 dias (L1 no aplica).
   - Se requiere decidir si se aceptan como tales, se busca un segundo donante, o se aplica una extrapolacion/estacionalidad para completarlas.

2. **Revision manual de estaciones criticas**
   - `SAN_PABLO`, `EL_CONTENTO`, `CALAMAR`, `MAGANGUE`, `PLATO` y `GAMARRA` necesitan revision hidrologica.
   - Verificar si los modelos H-H actuales son fisicamente razonables (especialmente `PLATO <- TEBSA` y `MAGANGUE <- TENERIFE`).

3. **Definir el formato de entrega final**
   - Actualmente `Datos_Imputados.csv` incluye columnas: `Fecha, NombreEstacion, Cota, Nivel_Imputacion, Metodo`.
   - Confirmar si el formato entregable debe ser wide (fechas x estaciones) o long, y si debe incluir/excluir NaN.

4. **Integracion con el resto del proyecto**
   - Mover/renombrar el output final al directorio que espera el backend.
   - Actualizar cualquier notebook o script downstream que use el dataset anterior.

5. **Documentacion tecnica**
   - Convertir este informe a Word si se requiere.
   - Anadir README dentro de `backend/scripts/imputation_v2_1/` con instrucciones de ejecucion.

6. **Validaciones adicionales (opcional pero recomendado)**
   - Analisis de residuos por estacion y por mes.
   - Prueba de sensibilidad al umbral de R2.
   - Revision de estacionalidad antes/después de la imputacion.

---

## 5. Archivos para revision inmediata

- `backend/scripts/imputation_v2_1/07_auditoria_todas_estaciones.py`
- `backend/data/work/imputation_v2_1/output/auditoria_todas_estaciones.md`
- `backend/data/work/imputation_v2_1/output/figura_heatmap_nulos_antes_despues.png`
- `backend/data/work/imputation_v2_1/output/Resumen_Imputacion.csv`

---

## 6. Instrucciones de ejecucion (resumen)

```bash
# 1. Preparar dataset
py backend/scripts/imputation_v2_1/02_prepare_dataset.py

# 2. Descubrir modelos H-H
py backend/scripts/imputation_v2_1/03_hh_discovery.py

# 3. Ejecutar imputacion
py backend/scripts/imputation_v2_1/04_run_imputation.py

# 4. Validacion y reportes
py backend/scripts/imputation_v2_1/05_validate_and_report.py

# 5. Auditoria de 12 estaciones
py backend/scripts/imputation_v2_1/06_auditoria_12_estaciones.py

# 6. Auditoria de todas las estaciones
py backend/scripts/imputation_v2_1/07_auditoria_todas_estaciones.py
```

---

*Generado automaticamente por el agente opencode el 24 de junio de 2026.*
