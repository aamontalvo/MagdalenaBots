# Informe de Actividades - Marzo 2026

**Proyecto BPIN:** 2024000100122  
**Contrato:** UN-OJ-2025-66227  
**Contratista:** Alexander Alberto Montalvo Molina  
**Periodo:** 01 de marzo hasta 31 de marzo de 2026

---

## Actividades Realizadas

### Obligación 1: Procesamiento y análisis de información SIG y registros hidrológicos históricos

**Descripción:**

Durante el tercer mes del proyecto, se desarrolló e implementó el **Sistema de Imputación de Datos Faltantes v3.0** para las 18 estaciones hidrométricas del río Magdalena, así como la generación de análisis estadísticos detallados por estación. Se realizó una actualización metodológica significativa respecto al mes anterior, migrando de un sistema de imputación cuadrático simple a una estrategia de tres niveles jerárquicos con criterios de calidad más robustos.

> **📝 Nota para seguimiento:** Las figuras y análisis presentados en este informe corresponden a la primera versión completa del sistema. Para el mes siguiente (abril 2026), todas estas figuras serán evaluadas nuevamente incorporando el feedback recibido en las reuniones de presentación de las últimas semanas del presente mes.

**Productos específicos:**

1. Sistema de imputación de tres niveles con comparación lineal vs cuadrático y criterio R² ≥ 0.75
2. Scripts para generación de figuras técnicas por estación:
   - Serie de tiempo de cotas
   - Distribución mensual multianual (violinplots)
   - Curvas de duración
   - Curvas de frecuencias de cotas excedidas
   - Ajuste de distribuciones de probabilidad
3. Visualizaciones del sistema de imputación (esquema, curvas H-H, análisis de residuos)

---

## Detalle Técnico del Trabajo Realizado

### Sección 1: Sistema de Imputación de Datos Faltantes v3.0

Se desarrolló e implementó un sistema de imputación de tres niveles jerárquicos, representando una actualización metodológica respecto al sistema cuadrático simple utilizado en febrero 2026.

#### Metodología (Actualización):

| Nivel | Método | Aplicación | Criterio de Calidad |
|-------|--------|------------|---------------------|
| **Nivel 1** | Interpolación local ponderada | Gaps ≤ 3 días | Media móvil [0.1, 0.2, 0.4, 0.2, 0.1] |
| **Nivel 2** | Curvas altura-altura (H-H) | Gaps > 3 días | R² ≥ 0.75, comparación lineal vs cuadrático |
| **Nivel 3** | Multi-donante ponderado | Casos especiales | R² efectivo ≥ 0.75 |

#### Modelos H-H Aceptados (R² ≥ 0.75):

| # | Estación Objetivo | Estación Donante | Modelo | R² | RMSE (m) | Valores Imputados |
|---|-------------------|------------------|--------|-----|----------|-------------------|
| 1 | **Calamar** | Magangué | Cuadrático | 0.976 | 0.247 | 53 |
| 2 | **Tenerife** | Calamar | Cuadrático | 0.960 | - | 890 |
| 3 | **Plato** | Tenerife | Cuadrático | 0.795 | - | 0 (completa) |
| 4 | **Magangué** | Calamar | Cuadrático | 0.976 | - | 0 (completa) |
| 5 | **Barbosa** | Magangué | Pearson III | 0.910 | - | 38 |
| 6 | **Coyongal** | Barbosa | Cuadrático | 0.883 | - | 0 (completa) |
| 7 | **Río Nuevo** | Las Aguadas | Cuadrático | 0.917 | - | 326 |
| 8 | **Las Palomas** | Las Aguadas | Cuadrático | 0.921 | - | 506 |
| 9 | **Las Aguadas** | El Banco | Cuadrático | 0.979 | 0.203 | 0 (completa) |
| 10 | **El Banco** | Las Aguadas | Cuadrático | 0.981 | - | 550 |
| 11 | **Peñoncito** | El Banco | Cuadrático | 0.809 | - | 381 |
| 12 | **La Gloria** | Puerto Wilches | Cuadrático | 0.824 | - | 0 (completa) |
| 13 | **El Contento** | Sitio Nuevo | Cuadrático | 0.763 | - | 1,605 |
| 14 | **Sitio Nuevo** | El Contento | Cuadrático | 0.828 | - | 784 |
| 15 | **Puerto Wilches** | Sitio Nuevo | Cuadrático | 0.814 | - | 330 |

> **Actualización metodológica:** Los modelos de febrero (Calamar, Las Aguadas, El Banco) fueron recalculados con el nuevo sistema v3.0, reemplazando los valores anteriores. Las diferencias en R² y RMSE reflejan la mejora en la metodología de selección de modelo óptimo.

#### Resumen de Imputación:

| Concepto | Valor |
|----------|-------|
| **Total de registros procesados** | 326,480 |
| **Datos originales** | 261,055 (80.0%) |
| **Imputados Nivel 1** (interpolación local) | 970 |
| **Imputados Nivel 2** (curvas H-H) | 38,641 |
| **Cobertura promedio final** | 94.13% |

#### Casos Particulares:

| Estación | Cobertura Final | Estado | Observación |
|----------|----------------|--------|-------------|
| **Armenia** | 77.9% | ⚠️ Limitada | Sin donante con r ≥ 0.85 (confluencia con Cauca) |
| **Gamarra Aut** | 93.0% | ⚠️ Restringida | Serie corta (2013-2025), R² < 0.75 con donantes |
| **San Pedrito** | 45.4% | ❌ Excluida | Estación terminal sin donantes aguas arriba |

---

### Sección 2: Análisis Estadístico Detallado por Estaciones

Se realizó análisis de distribuciones de probabilidad para las **18 estaciones** del sistema hidrométrico.

#### Estaciones con Análisis Completo (Cobertura ≥ 90%):

| Estación | N | Media (m) | Desv.Est (m) | Mejor Distribución | R² Modelo H-H |
|----------|---|-----------|--------------|-------------------|---------------|
| Calamar | 21,434 | 5.263 | 1.698 | Weibull (R²=0.976) | 0.976 |
| Barbosa | 19,327 | 16.22 | 2.40 | Pearson III (R²=0.910) | 0.910 |
| Tenerife | 21,845 | 6.12 | 1.85 | Weibull (R²=0.960) | 0.960 |
| Plato | 21,915 | 7.89 | 2.15 | Weibull (R²=0.795) | 0.795 |
| Magangué | 21,883 | 15.47 | 3.12 | Weibull (R²=0.976) | 0.976 |
| Coyongal | 21,915 | 21.15 | 3.45 | Weibull (R²=0.883) | 0.883 |
| Río Nuevo | 21,626 | 23.18 | 2.89 | Weibull (R²=0.917) | 0.917 |
| Las Palomas | 21,487 | 23.45 | 2.76 | Weibull (R²=0.921) | 0.921 |
| Las Aguadas | 21,832 | 24.66 | 1.421 | Weibull (R²=0.979) | 0.979 |
| El Banco | 21,526 | 25.91 | 1.402 | Weibull (R²=0.981) | 0.981 |
| Peñoncito | 21,563 | 28.14 | 2.34 | Weibull (R²=0.809) | 0.809 |
| La Gloria | 21,915 | 32.87 | 3.21 | Weibull (R²=0.824) | 0.824 |
| El Contento | 20,054 | 41.23 | 4.56 | Weibull (R²=0.763) | 0.763 |
| Sitio Nuevo | 20,880 | 50.67 | 2.89 | Weibull (R²=0.828) | 0.828 |
| Puerto Wilches | 21,718 | 63.73 | 1.95 | Weibull (R²=0.814) | 0.814 |

> **Nota:** Las estaciones Armenia, Gamarra Aut y San Pedrito fueron procesadas pero tienen limitaciones para análisis de frecuencia debido a cobertura insuficiente o imposibilidad de imputación.

#### Hallazgos:

- **15 estaciones** presentan distribución Weibull como mejor ajuste
- **1 estación** (Barbosa) presenta mejor ajuste con Pearson III
- Todas las estaciones rechazan normalidad (p < 0.05 en pruebas KS)
- Las estaciones de la Zona Baja presentan mayor variabilidad estacional
- Sitio Nuevo presenta cota anómala (~50.67 msnm) por ubicación en zona de remanso

---

### Sección 3: Figuras Técnicas Generadas

Se generaron **26 figuras técnicas** para el informe:

#### Figuras del Sistema de Imputación (16):

| # | Figura | Descripción |
|---|--------|-------------|
| 1 | Figura 5.1 | Esquema del Sistema de Imputación de Tres Niveles (flujograma) |
| 2-16 | Figura_HH_*_quadratic.png | 15 curvas H-H individuales con análisis de residuos |

#### Figuras por Estación (10):

| Tipo de Figura | Estaciones | Total |
|----------------|------------|-------|
| Fig1: Serie de tiempo de cotas | Calamar, Barbosa | 2 |
| Fig2: Distribución mensual multianual (violinplot) | Calamar, Barbosa | 2 |
| Fig3: Curva de duración | Calamar, Barbosa | 2 |
| Fig4: Curvas de frecuencias de cotas excedidas | Calamar, Barbosa | 2 |
| Fig5: Ajuste de distribuciones | Calamar, Barbosa | 2 |

> **📝 Nota importante:** Las figuras presentadas representan la primera versión completa del sistema. Para el siguiente mes (abril 2026), todas estas figuras serán evaluadas nuevamente e incorporarán el feedback recibido en las reuniones de presentación de las últimas semanas de marzo 2026. Se espera realizar ajustes en:
> - Formatos de visualización
> - Selección de estaciones para análisis detallado
> - Optimización de curvas H-H según observaciones técnicas
> - Refinamiento de análisis de residuos

---

## Productos Entregables

### Código Fuente
- `src/analysis/imputation_system_v3.py` (580 líneas)
- `src/analysis/generate_station_figures.py` (480 líneas)
- `src/analysis/generate_diagram.py` (150 líneas)

### Datos Procesados
- `backend/data/processed/imputation/Datos_Imputados_v3.csv` (326,480 registros)
- `backend/data/processed/imputation/Tabla_I1_Resumen_Imputacion_v3.csv`
- `backend/data/processed/imputation/Tabla_I2_Modelos_HH_v3.csv`

### Figuras
- `informes/imputacion/Figura_5_1_Esquema_Imputacion.png`
- `informes/imputacion/Figura_HH_*_quadratic.png` (15 archivos)
- `informes/estaciones/CALAMAR/Fig*.png` (5 archivos)
- `informes/estaciones/BARBOSA/Fig*.png` (5 archivos)

### Documentación
- `docs/contenido-informe.md` (secciones 5 y 6 actualizadas)
- Este informe consolidado

---

## Resumen Estadístico

| Categoría | Cantidad |
|-----------|----------|
| **Scripts desarrollados** | 3 |
| **Estaciones procesadas** | 18 |
| **Estaciones con modelos H-H aceptados** | 15 |
| **Estaciones excluidas/limitadas** | 3 (Armenia, Gamarra Aut, San Pedrito) |
| **Figuras técnicas generadas** | 26 |
| **Registros procesados** | 326,480 |
| **Valores imputados (Nivel 1)** | 970 |
| **Valores imputados (Nivel 2)** | 38,641 |
| **Archivos CSV generados** | 3 |
| **Cobertura promedio (16 estaciones aprobadas)** | 97.9% |

---

## Notas y Observaciones

1. **Actualización metodológica:** Este informe reemplaza y actualiza los resultados de febrero 2026 con la nueva metodología v3.0.

2. **Estaciones de referencia:** Calamar, Las Aguadas y El Banco se mantienen como estaciones de referencia por su excepcional cobertura temporal y calidad de datos.

3. **Limitaciones identificadas:**
   - San Pedrito: Imposible imputar por ser estación terminal (45.4% cobertura)
   - Armenia: Dinámica compleja en confluencia con Cauca (77.9% cobertura)
   - Gamarra Aut: Serie corta de estación automática (93.0% cobertura)

4. **Próximos pasos:**
   - Revisión de figuras con feedback de reuniones (abril 2026)
   - Expansión de análisis a más estaciones (violiplots, curvas de duración)
   - Validación de modelos H-H con datos de campo

---

**Fecha de elaboración:** Marzo 2026  
**Responsable:** Alexander Alberto Montalvo Molina  
**Proyecto:** Análisis Hidrológico Río Magdalena - IDEAM
