# Informe de entrega - Imputacion de niveles IDEAM v2.1+

> **Nota:** No se dispone del plugin de WPS/Word en este entorno, por lo que se genera este documento en Markdown para que otro agente con el plugin correspondiente lo convierta a `.docx` si es necesario.

---

## 1. Contexto y objetivo

Se construyo el pipeline v2.1+ de imputacion de niveles de agua del IDEAM para la cuenca del Magdalena, con las siguientes reglas de negocio:

- Incluir las 24 estaciones del raw corregido (Version Homegeneizada HAR STEFY).
- Corte temporal global al 31 de diciembre de 2025.
- Eliminar el 29 de febrero de todos los anos.
- Respetar el **rango oficial** de cada estacion: para estaciones comunes con el raw anterior se conservo su rango historico; para las nuevas se uso su propio rango valido.
- No imputar **fuera del rango oficial** de ninguna estacion.
- No hay restriccion de orientacion geografica para donantes H-H; cualquier estacion puede ser donante de cualquier otra.
- Mantener R2 >= 0.75 para modelos H-H de primer nivel (L2).
- Aplicar un **segundo nivel H-H complementario (L3)** a estaciones con cobertura < 95% tras L2, usando R2 >= 0.65 y Pearson >= 0.8.
- Descartar (pero conservar en el output) las estaciones inhomogeneas: ARMENIA, BARBOSA, SITIO_NUEVO, TENERIFE.
- Conservar los `NaN` dentro del rango oficial para que el dataset final refleje cobertura real.

Commit de referencia: `ed1bfb0` — `feat(imputation): pipeline v2.1 con mascara de rango oficial y auditoria`

---

## 2. Que se hizo

### 2.1 Pipeline v2.1+ (`backend/scripts/imputation_v2_1/`)

| Script / Paquete | Funcion |
|---|---|
| `01_compare_raw_versions.py` | Comparacion del raw nuevo vs el raw anterior. |
| `02_prepare_dataset.py` | Limpieza, normalizacion de nombres, corte 2025, eliminacion 29-Feb, deduplicacion y generacion de `resumen_rangos_estaciones.csv`. |
| `03_hh_discovery.py` | Descubrimiento y seleccion de modelos H-H sin restriccion de orientacion. |
| `04_run_imputation.py` | Imputacion en cascada L1 -> L2 -> L3, respetando la mascara de rango oficial. |
| `05_validate_and_report.py` | Validaciones post-imputacion, comparacion con corrida anterior y heatmaps de nulos. |
| `06_auditoria_12_estaciones.py` | Auditoria detallada de 12 estaciones representativas. |
| `07_auditoria_todas_estaciones.py` | Auditoria detallada de las 24 estaciones con figura individual por estacion. |
| `08_evaluar_candidatos_l3.py` | Evaluacion de candidatos para segunda donante H-H complementaria (L3). |
| `09_experimento_l3.py` | Aplicacion de L3 a estaciones criticas sin modificar L0/L1/L2. |
| `10_validar_y_figuras_l3.py` | Validacion de L3 y generacion de figuras comparativas. |
| `13_agente_validacion.py` | Agente de validacion automatica para detectar problemas en el output. |
| `14_generar_cartillas_v2_1.py` | Generacion de cartillas tecnicas (5 figuras) por estacion a partir del dataset final. |
| `imputation_pipeline_v2_1/` | Paquete reutilizable: config, loaders, hh_selector, imputers, hard_rules, tracker. |

### 2.2 Outputs principales (`backend/data/work/imputation_v2_1/output/`)

| Archivo | Descripcion |
|---|---|
| `Resumen_Crudos_IDEAM_2026_v2_1.csv` | Dataset crudo preparado (sin imputar). |
| `resumen_rangos_estaciones.csv` | Rango oficial usado por estacion. |
| `Tabla_Modelos_HH_Seleccionados.csv` | 23 modelos H-H seleccionados (R2 >= 0.75). |
| `Tabla_Modelos_L3.csv` | Modelos H-H usados para el nivel L3. |
| `Datos_Imputados.csv` | Dataset final con niveles L0/L1/L2/L3, acotado a rangos oficiales, incluye NaN. |
| `Datos_Imputados_sin_L3.csv` | Dataset con solo L0/L1/L2 (backup antes de aplicar L3). |
| `Resumen_Imputacion.csv` | Cobertura real por estacion. |
| `validacion_post_imputacion.md` | Reporte de validacion. |
| `agente_validacion_reporte.md` | Reporte del agente de validacion automatica. |
| `agente_validacion_alertas.csv` | Alertas detectadas por el agente. |
| `figura_heatmap_nulos_antes_despues.png` | Heatmap de datos nulos antes y despues de la imputacion. |
| `figura_cobertura_imputacion.png` | Barras apiladas de originales, L1, L2 y L3. |
| `figura_series_temporales.png` | Series temporales de ejemplo. |
| `auditoria_12_estaciones.md` | Reporte Markdown con tablas y 12 figuras. |
| `auditoria_todas_estaciones.md` | Reporte Markdown con tablas y 24 figuras. |
| `figuras/auditoria/auditoria_<ESTACION>.png` | Figura de auditoria individual por estacion. |
| `07_cartillas/<ESTACION>/Fig*_..._v2_1.png` | Cartillas tecnicas por estacion (5 figuras cada una). |

---

## 3. Hallazgos clave

### 3.1 Correccion critica: imputacion fuera de rango

En la primera version del pipeline se generaron **44,599 registros fuera del rango oficial** (44,598 de ellos imputaciones L2). Esto se detecto en la auditoria de las 12 estaciones.

**Solucion aplicada:**
- Se cargo `resumen_rangos_estaciones.csv` como mascara oficial.
- Se forzaron a `NaN` todas las fechas fuera del rango antes de la imputacion.
- L1 no imputa gaps que toquen los bordes del rango.
- L2 y L3 solo imputan cuando el objetivo esta dentro de su rango oficial.
- `build_tracked_dataset()` descarta registros fuera del rango oficial.

**Verificacion final:**
- Registros fuera de rango oficial: **0**
- Violaciones de rango historico de cota: **0**
- Saltos temporales anomalos: **0**

### 3.2 Cobertura del dataset final

- **Registros totales en `Datos_Imputados.csv`:** 394,772
- **Originales (L0):** ~82.0%
- **Imputados L1:** 1,222
- **Imputados L2:** 36,758
- **Imputados L3:** 16,855
- **Total imputados:** 54,835

### 3.3 Modelos H-H

- **L2 (primer nivel):** se evaluaron **552 parejas** y se seleccionaron **23 modelos** (R2 >= 0.75).
- **L3 (segundo nivel complementario):** se aplicaron **10 modelos** adicionales a estaciones con cobertura < 95% tras L2 (R2 >= 0.65, Pearson >= 0.8).
- Unica estacion **sin modelo H-H viable en L2:** `PUERTO_SALGAR` (llego a 97.62% de cobertura solo con L1).

### 3.4 Estaciones con cobertura completa dentro del rango oficial (100%)

`LAS_AGUADAS`, `LAS_PALOMAS`, `PUERTO_BERRIO`, `RIO_NUEVO`, `TEBSA`, `COYONGAL`, `EL_CONTENTO`, `GAMARRA`, `MAGANGUE`, `PLATO`, `SAN_PABLO`, `SITIO_NUEVO`

### 3.5 Estaciones con cobertura alta pero no completa (>95%)

| Estacion | Cobertura | NaN restantes | Observacion |
|---|---|---|---|
| EL_BANCO | 99.57% | 84 | Muy alta, NaN aislados. |
| SAN_PEDRITO | 99.90% | 18 | Muy alta. |
| TENERIFE | 99.98% | 4 | Marcada como descartada pero casi completa. |
| PENONCITO | 99.74% | 51 | Muy alta. |
| BARBOSA | 96.46% | 661 | Descartada por inhomogeneidad. |
| PUERTO_WILCHES | 98.47% | 125 | Alta. |
| BARRANCABERMEJA | 95.65% | 874 | Sin donante L3 viable. |
| GAMARRA_AUT | 95.13% | 231 | Sin donante L3 viable para periodos iniciales. |
| ARMENIA | 99.85% | 28 | Descartada por inhomogeneidad; L3 cubrio la mayoria. |

### 3.6 Estaciones con cobertura problematica (<95%)

| Estacion | Cobertura | NaN restantes | Razon |
|---|---|---|---|
| CALAMAR | 93.34% | 1,431 | Los NaN estan concentrados en 1967-1973; ninguna otra estacion del dataset tiene datos en ese periodo. |

### 3.7 Comparacion con corrida anterior (estudiantes)

- Registros comparables: **292,885**
- Diferencia media absoluta: **0.3220 m**
- Diferencia maxima absoluta: **3.8058 m**

### 3.8 Resultados del nivel L3

El nivel L3 se aplico automaticamente a todas las estaciones con cobertura < 95% tras L2. Se selecciono una segunda donante por estacion maximizando la cobertura de NaN restantes, con R2 >= 0.65 y Pearson >= 0.8.

| Estacion | Donante L3 | R2 L3 | r L3 | Imputados L3 | Cobertura final |
|---|---|---|---|---|---|
| ARMENIA | PENONCITO | 0.7463 | 0.8352 | 1,644 | 99.85% |
| CALAMAR | EL_BANCO | 0.7831 | 0.8835 | 83 | 93.34% |
| COYONGAL | EL_BANCO | 0.8556 | 0.9203 | 1,015 | 100.00% |
| EL_CONTENTO | EL_BANCO | 0.7726 | 0.8782 | 3,441 | 100.00% |
| GAMARRA | EL_BANCO | 0.8179 | 0.9040 | 1,348 | 100.00% |
| GAMARRA_AUT | GAMARRA | 0.9989 | 0.9993 | 99 | 95.13% |
| MAGANGUE | EL_BANCO | 0.7393 | 0.8577 | 1,645 | 100.00% |
| PLATO | TENERIFE | 0.7938 | 0.8908 | 1,721 | 100.00% |
| SAN_PABLO | EL_BANCO | 0.6548 | 0.8085 | 4,806 | 100.00% |
| SITIO_NUEVO | EL_BANCO | 0.6740 | 0.8164 | 1,053 | 100.00% |

**Validacion L3:**
- Violaciones de rango historico tras hard rules: **0**
- Registros fuera de rango temporal oficial: **0**
- Saltos temporales anomalos: **0**

---

## 4. Entrega organizada

Todo el material definitivo se encuentra en:

```
backend/entregables/niveles_v2_1/
├── 01_datos_originales/
├── 02_datos_imputados/
├── 03_modelos/
├── 04_scripts/
├── 05_validacion_y_auditoria/
├── 06_figuras/
├── 07_cartillas/
├── anotaciones/CASO_CALAMAR.md
└── README.md
```

- **Datos originales:** crudos y rangos oficiales.
- **Datos imputados:** `Datos_Imputados.csv` en formato long, con columna `Nivel_Imputacion`.
- **Modelos:** tablas de modelos H-H para L2 y L3.
- **Scripts:** pipeline reproducible y paquete reutilizable.
- **Validacion y auditoria:** reportes, resumenes y comparaciones.
- **Figuras:** heatmap, cobertura, series temporales y diagrama de flujo.
- **Cartillas:** 5 figuras tecnicas por cada una de las 24 estaciones.

---

## 5. Estado de tareas pendientes

| Tarea | Estado |
|---|---|
| Decision sobre NaN de CALAMAR | **Resuelto**: se dejan como NaN y se documentan en `anotaciones/CASO_CALAMAR.md`. |
| Revision visual de estaciones con alto L3 | **Pendiente de aprobacion del usuario**. Las figuras estan en `07_cartillas/` y en `figuras/auditoria/`. |
| Formato de entrega final | **Resuelto**: formato long, incluye NaN. |
| Integracion con backend | **Pendiente**: definir ruta final esperada por el backend. |
| Documentacion tecnica | **Resuelto**: `README.md` en la carpeta de entrega. |
| Conversion a Word | **Pendiente**: se trabajara titulo a titulo con el usuario. |
| Validaciones adicionales | **Opcional**: residuos, sensibilidad, estacionalidad. |

---

## 6. Archivos para revision inmediata

- `backend/entregables/niveles_v2_1/README.md`
- `backend/entregables/niveles_v2_1/anotaciones/CASO_CALAMAR.md`
- `backend/entregables/niveles_v2_1/02_datos_imputados/Datos_Imputados.csv`
- `backend/entregables/niveles_v2_1/03_modelos/Tabla_Modelos_L3.csv`
- `backend/entregables/niveles_v2_1/05_validacion_y_auditoria/Resumen_Imputacion.csv`
- `backend/entregables/niveles_v2_1/05_validacion_y_auditoria/auditoria_todas_estaciones.md`
- `backend/entregables/niveles_v2_1/06_figuras/diagrama_flujo_imputacion_v2_1.png`
- `backend/entregables/niveles_v2_1/07_cartillas/`

---

## 7. Instrucciones de ejecucion (resumen)

```bash
# 1. Preparar dataset
py backend/scripts/imputation_v2_1/02_prepare_dataset.py

# 2. Descubrir modelos H-H
py backend/scripts/imputation_v2_1/03_hh_discovery.py

# 3. Ejecutar imputacion (L1 -> L2 -> L3)
py backend/scripts/imputation_v2_1/04_run_imputation.py

# 4. Validacion y reportes
py backend/scripts/imputation_v2_1/05_validate_and_report.py

# 5. Auditoria de 12 estaciones
py backend/scripts/imputation_v2_1/06_auditoria_12_estaciones.py

# 6. Auditoria de todas las estaciones
py backend/scripts/imputation_v2_1/07_auditoria_todas_estaciones.py

# 7. Agente de validacion
py backend/scripts/imputation_v2_1/13_agente_validacion.py

# 8. Generar cartillas
py backend/scripts/imputation_v2_1/14_generar_cartillas_v2_1.py
```

---

*Generado automaticamente por el agente opencode.*
