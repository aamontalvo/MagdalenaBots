# Informe Técnico: Validación y Clasificación de Estaciones

**Proyecto:** MagdalenaBot v3.0 - Análisis Hidrológico Río Magdalena  
**Fecha:** Marzo 2026  
**Responsable:** Alexander Alberto Montalvo Molina  
**Contrato:** UN-OJ-2025-66227 | BPIN: 2024000100122

---

## Resumen Ejecutivo

Este documento presenta el resultado del proceso de validación completo del sistema de imputación v3.0 para las 18 estaciones hidrométricas del Río Magdalena. Tras el análisis de las cartillas generadas y la revisión visual sistemática, se ha establecido una clasificación definitiva de estaciones según su aptitud para análisis de frecuencia y diseño hidráulico.

**Resultado principal:** De 18 estaciones procesadas, **4 estaciones (22%) están completamente validadas** para uso sin restricciones, **8 estaciones (44%) requieren precauciones específicas**, y **6 estaciones (33%) deben excluirse** del análisis estadístico formal.

---

## Metodología de Validación

### Criterios de Evaluación

Cada estación fue evaluada en 5 dimensiones críticas:

1. **Calidad de Imputación**: R² de modelos, coherencia espacial, saltos en fronteras
2. **Longevidad de Datos**: Años de registro, continuidad temporal, gaps significativos
3. **Confiabilidad Espacial**: Correlación con estaciones vecinas (r ≥ 0.85 requerido)
4. **Estabilidad Temporal**: Homogeneidad de series (pruebas Pettitt, SNHT, Mann-Kendall)
5. **Usabilidad Final**: Aptitud para análisis de frecuencia de eventos extremos

### Proceso de Validación Visual

Se generaron cartillas con 5 figuras técnicas por estación:
- Figura 1: Serie temporal completa
- Figura 2: Comportamiento mensual multianual (violinplots)
- Figura 3: Curva de duración
- Figura 4: Curvas de frecuencias de cotas excedidas
- Figura 5: Ajuste de distribuciones de probabilidad + Q-Q plot

Las revisiones se documentaron en el notebook `VALIDACION_VISUAL_COMPLETA.ipynb`.

---

## Clasificación de Estaciones

### 🟢 CATEGORÍA A: EXCELLENT (4 estaciones)
**Uso:** Sin restricciones para análisis de frecuencia, diseño hidráulico y análisis de tendencias

| Estación | Zona | Cobertura | Fortalezas Clave |
|----------|------|-----------|------------------|
| **CALAMAR** | Baja | 99.4% | Serie más larga (1967-2025). Modelo H-H robusto (R²=0.98). Referencia principal. |
| **BARBOSA** | Baja | 99.8% | Buena correlación con Magangué. Serie estable sin gaps críticos. |
| **MAGANGUE** | Baja | 99.8% | Donante confiable. Comportamiento predecible. Alta cobertura. |
| **EL_BANCO** | Media | 98.2% | Relación fuerte con Las Aguadas (R²=0.98). Serie homogénea completa. |

**Recomendación:** Estas 4 estaciones constituyen la base de datos principal para análisis de frecuencia.

---

### 🟡 CATEGORÍA B: USABLE WITH CAUTION (8 estaciones)
**Uso:** Requieren segmentación temporal o exclusiones específicas

#### Subcategoría B1: Revisar periodo 2010-2012 (4 estaciones)

| Estación | Zona | Problema | Solución Implementada |
|----------|------|----------|----------------------|
| **TENERIFE** | Baja | Anomalía detectada en 2010-2012 | Excluir periodo o verificar contra datos originales |
| **LA GLORIA** | Alta | Anomalía detectada en 2010-2012 | Excluir periodo 2010-2012 del análisis |
| **SITIO NUEVO** | Alta | Anomalía 2010-2012 + zona de remanso | Excluir periodo problemático. Cota ~50m real pero requiere tratamiento separado |
| **PUERTO_WILCHES** | Alta | Anomalía 2010-2012 + serie reciente | Usar solo para análisis post-2003 (inicia en 2003) |

**Acción requerida:** Verificación manual de datos originales (sin imputar) para el periodo 2010-2012 en estas 4 estaciones.

#### Subcategoría B2: Excluir primeros años (4 estaciones)

| Estación | Zona | Problema | Años a Excluir |
|----------|------|----------|----------------|
| **PLATO** | Baja | Cambios de cota iniciales | Primeros 2-3 años |
| **LAS AGUADAS** | Media | Problemas de instalación inicial | Primeros 2 años |
| **PEÑONCITO** | Media | Referencia inicial inestable | Primeros 2 años |
| **EL CONTENTO** | Alta | Inicio con gaps frecuentes | Primeros 3 años |

---

### 🔴 CATEGORÍA C: EXCLUDE (6 estaciones)
**Uso:** No aptas para análisis de frecuencia. Algunas permiten uso cualitativo limitado.

| Estación | Zona | Problema Irreparable | Razón Técnica |
|----------|------|---------------------|---------------|
| **ARMENIA** | Media | Sin donante confiable | Confluencia con Río Cauca. Correlación máxima r=0.72 (requerido ≥0.85). Dinámica hidrológica compleja no capturable por modelos bivariados. |
| **GAMARRA_AUT** | Alta | Serie corta + automática | 13 años (2013-2025). Protocolos de medición diferentes a estaciones convencionales. R² máximo=0.38 (imposible calibrar). |
| **SAN PEDRITO** | Baja | Estación terminal | No hay donantes aguas arriba. Imputación espacial inviable. Cobertura 45.4% insuficiente para análisis estadístico. |
| **RIO NUEVO** | Media | Extrapolación sistémica | Modelo cuadrático se invierte fuera de rango [21-26]m. Problemas de estabilidad numérica en valores extremos. |
| **LAS PALOMAS** | Media | Dependencia crítica de donante | Sin donante alternativo viable. Gaps en Las Aguadas propagan errores sistemáticos no corregibles. |
| **COYONGAL** | Baja | Saltos estructurales persistentes | Fronteras de gaps generan discontinuidades que persisten con diferentes modelos. |

**Nota:** Armenia y Gamarra Aut pueden usarse para análisis cualitativos de tendencias con advertencias explícitas. Las otras 4 deben excluirse completamente.

---

## Análisis de Problemas Específicos

### Problema 1: Anomalías 2010-2012

**Estaciones afectadas:** Tenerife, La Gloria, Sitio Nuevo, Puerto Wilches

**Descripción:** Se detectaron anomalías visuales en el periodo 2010-2012 en las cartillas de estas estaciones. Las posibles causas incluyen:
- Evento hidrológico real de magnitud excepcional
- Cambio instrumental o de referencia de cota
- Error de imputación en ese periodo específico

**Plan de acción:**
1. Comparar datos imputados vs datos originales (sin imputar) para 2010-2012
2. Si coinciden → Evento real, documentar en metadatos
3. Si difieren → Error de imputación, regenerar con método alternativo

### Problema 2: Estaciones Terminales y Sin Donante

**Estaciones:** Armenia, San Pedrito, Gamarra Aut

**Descripción:** La imputación espacial requiere estaciones donantes correlacionadas aguas arriba. Armenia (confluencia con Cauca) y San Pedrito (extremo aguas abajo) tienen dinámicas que no permiten establecer relaciones H-H robustas.

**Recomendación:** No imputar. Usar solo datos observados con cobertura que permitan (Armenia 77.9%, Gamarra 93% de serie corta).

### Problema 3: Inestabilidad Inicial

**Estaciones:** Plato, Las Aguadas, Peñoncito, El Contento

**Descripción:** Primeros años de operación muestran inestabilidad característica de estaciones recién instaladas: cambios de referencia de cero, calibraciones iniciales, ajustes de instrumental.

**Solución:** Excluir periodos iniciales marcados de los análisis estadísticos.

---

## Implicaciones para Análisis Futuros

### Para Análisis de Frecuencia y Diseño Hidráulico

**Base de datos principal:** 4 estaciones EXCELLENT
- Calamar, Barbosa, Magangué, El Banco

**Base de datos extendida (con segmentación):** 12 estaciones
- 4 EXCELLENT + 8 USABLE_WITH_CAUTION (aplicando exclusiones temporales)

### Para Análisis de Tendencias y Cambio Climático

**Usables:** 14 estaciones
- 4 EXCELLENT + 8 USABLE_WITH_CAUTION + 2 EXCLUDE para uso cualitativo (Armenia, Gamarra)

### Para Análisis de Variabilidad Reciente (2000-2025)

**Usables:** 15 estaciones
- Incluye Puerto Wilches (inicia 2003) y Gamarra (inicia 2013)

---

## Recomendaciones Operacionales

### Inmediatas (antes de abril 2026)

1. **Verificar periodo 2010-2012** en Tenerife, La Gloria, Sitio Nuevo, Puerto Wilches
2. **Documentar en metadatos** las exclusiones de periodos iniciales para 4 estaciones
3. **Actualizar informes técnicos** con nueva clasificación de estaciones

### Corto Plazo (abril-mayo 2026)

4. **Implementar validación automática** en pipeline de procesamiento
5. **Re-imputar** Río Nuevo con modelo lineal (no cuadrático) limitado a rango válido
6. **Investigar donantes alternativos** para Las Palomas

### Mediano Plazo (junio 2026)

7. **Evaluar re-imputación** de Coyongal con modelo diferente
8. **Acumular datos** de Gamarra para análisis futuro (meta: 20 años en 2033)

---

## Archivos Relacionados

- `docs/DIAGNOSTICO_COMPLETO_SISTEMA_v3.md` - Diagnóstico técnico detallado
- `cartillas_estaciones/VALIDACION_VISUAL_COMPLETA.ipynb` - Notebook de validación
- `database/schema.sql` - Esquema de base de datos
- `database/models.py` - Modelos Python para datos
- `workflows/integration_pipeline.py` - Pipeline de integración continua

---

**Elaborado por:** Alexander Alberto Montalvo Molina  
**Fecha:** Marzo 2026  
**Contrato:** UN-OJ-2025-66227
