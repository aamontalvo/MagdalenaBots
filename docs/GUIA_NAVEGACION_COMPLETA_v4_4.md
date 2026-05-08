# GUIA DE NAVEGACION COMPLETA - Sistema de Imputacion v4.4

**Proyecto:** BPIN 2024000100122 - Analisis Hidrologico Rio Magdalena  
**Responsable:** Alexander Alberto Montalvo Molina  
**Version:** v4.4 (correccion climatologica sobre v4.3)  
**Fecha:** 2026-05-08  
**Total estaciones:** 18 (14 homogeneas + 4 descartadas)

---

## 1. MAPA GENERAL DEL PIPELINE DE IMPUTACION

Este es el flujo completo de datos, desde los crudos del IDEAM hasta el dataset final v4.4:

```
CRUDOS IDEAM
    |
    v
[1] Resumen_Crudos_IDEAM_2026.csv          (datos originales medidos)
    |
    v
[2] imputation_system_v4_3.py              (SISTEMA PRINCIPAL)
    |   |-- L1: Interpolacion local (gaps <= 3 dias)
    |   |-- L2: H-H cuadratica (gaps > 3 dias, R2 >= 0.75)
    |   |-- L3: missForest (residuales, multivariado no parametrico)
    |   +-- Hard rule: nunca fuera del rango original
    |
    v
[3] Datos_Imputados_v4_3_Corrected.csv     (dataset base, 308,364 registros)
    |
    v
[4] parche_calamar_climatologia_v4_4.py    (PARCHE SELECTIVO)
    |   |-- Detecta artefacto: CALAMAR 1969-1970, 61 dias, std=0
    |   +-- Reemplaza por climatologia estacional ajustada
    |
    v
[5] Datos_Imputados_v4_4_ClimatologyPatch.csv  (DATASET FINAL)
```

### Evolucion de versiones

| Version | Que contiene | Registros | Archivo generado |
|---------|--------------|-----------|------------------|
| **v4.2** | Dataset base con imputaciones completas | 308,364 | `Datos_Imputados_v4_2_Complete.csv` |
| **v4.3** | v4.2 + correcciones (orientacion H-H, hard rule, San Pedrito) | 308,364 | `Datos_Imputados_v4_3_Corrected.csv` |
| **v4.4** | v4.3 + parche climatologico CALAMAR 1969 | 308,364 | `Datos_Imputados_v4_4_ClimatologyPatch.csv` |

**Clave:** Solo cambian los metadodos (como se imputo), no el numero de registros. Los datos originales son INMUTABLES entre versiones.

---

## 2. CODIGOS FUENTE - DONDE ESTA CADA COSA

### A. Sistema principal de imputacion (genera v4.3)

| Archivo | Ruta | Que hace | Tamano | Estado |
|---------|------|----------|--------|--------|
| **imputation_system_v4_3.py** | `src/analysis/` | **Pipeline completo L1+L2+L3** — carga crudos, aplica interpolacion, modelos H-H, missForest, hard rule | 12 KB | **Produccion** |
| **imputation_system_v3.py** | `src/analysis/` | Version anterior (evolucion del sistema) | 22 KB | Legacy |

**Para el jefe:** `imputation_system_v4_3.py` es el corazon del sistema. Contiene:
- Funcion `load_data()` — carga crudos IDEAM
- Funcion `train_hh_model()` — entrena curvas H-H cuadraticas
- Funcion `apply_l1_interpolation()` — interpolacion local
- Funcion `apply_l2_hh()` — imputacion H-H
- Funcion `apply_l3_missforest()` — Random Forest multivariado
- Funcion `apply_hard_rule()` — validacion de rangos

### B. Verificacion y calidad (valida v4.3)

| Archivo | Ruta | Que hace | Estado |
|---------|------|----------|--------|
| **verificacion_v4_3.py** | `src/analysis/` | 9 checks de calidad: inmutabilidad, hard rule, orientacion H-H, data leakage, cobertura, saltos bruscos, autocorrelacion | **Produccion** |

Checks que ejecuta:
1. Inmutabilidad de datos originales vs crudos IDEAM
2. Hard rule (ningun valor fuera del rango original)
3. Orientacion H-H correcta (independiente aguas arriba)
4. Coherencia fisica de valores imputados
5. Data leakage en entrenamiento H-H (solo originales concurrentes)
6. Cobertura 100% en estaciones no descartadas
7. Comparacion estadistica v4.2 vs v4.3
8. Continuidad de serie (deteccion de saltos bruscos)
9. Autocorrelacion de residuos de imputacion

### C. Generacion de cartillas (visualizaciones)

| Archivo | Ruta | Que hace | Estado |
|---------|------|----------|--------|
| **generar_cartillas_v4_3.py** | `src/analysis/` | Genera 5 figuras por estacion (90 figuras totales) | **Produccion** |
| **generar_cartillas_v4_4_calamar.py** | `cartillas_estaciones/` | Regenera 5 figuras de CALAMAR con v4.4 | **Produccion** |
| **generar_stacked_bars_imputacion_v4_3.py** | `src/analysis/` | Grafico de barras apiladas: composicion % de imputacion por estacion | **Produccion** |
| **generar_heatmap_datos_nulos_v3.py** | `src/analysis/` | Heatmap de cobertura temporal (estaciones vs anos) | **Produccion** |
| **generar_fuente_verdad_long.py** | `src/analysis/` | Genera formato long a partir de wide (preprocesamiento) | **Produccion** |

### D. Parche v4.4 (correccion CALAMAR)

| Archivo | Ruta | Que hace | Estado |
|---------|------|----------|--------|
| **parche_calamar_climatologia_v4_4.py** | `src/analysis/` | Reemplaza 61 dias de missForest constante por climatologia estacional | **Produccion** |
| **imputation_multivariate_hh_v4_4.py** | `src/analysis/` | H-H Multivariado (multiple donantes simultaneas) — desarrollado, no ejecutado | Desarrollo |

### E. Alternativas evaluadas y descartadas

| Archivo | Ruta | Que es | Estado |
|---------|------|--------|--------|
| imputation_saits_v4_4.py | `src/analysis/` | SAITS transformer (entrenamiento base) | Descartado |
| imputation_saits_v4_4_chunks.py | `src/analysis/` | SAITS por chunks (optimizacion memoria) | Descartado |
| imputation_saits_v4_4_fast.py | `src/analysis/` | SAITS rapido (batch processing) | Descartado |
| imputation_saits_v4_4_finalize.py | `src/analysis/` | SAITS finalizacion y guardado | Descartado |
| imputation_saits_v4_4_inference.py | `src/analysis/` | SAITS inferencia (prediccion) | Descartado |
| saits_v4_4_train_and_infer.py | `src/analysis/` | SAITS completo entrenamiento + inferencia | Descartado |

**Nota:** Estos 6 scripts demuestran que se evaluo una alternativa de deep learning (SAITS transformer) y se descarto por limitacion estructural: los bloques missForest (100-365 dias) exceden la ventana de contexto del modelo (90 dias), provocando colapso a valores constantes.

---

## 3. DATASETS - QUE ARCHIVO ES CUAL

### Ubicacion base
`C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\backend\data\processed\imputation\`

### Archivos principales

| Archivo | Tamano | Descripcion | Cuando usar |
|---------|--------|-------------|-------------|
| **Datos_Imputados_v4_4_ClimatologyPatch.csv** | ~14 MB | **DATASET FINAL v4.4** — v4.3 + parche CALAMAR | **SIEMPRE** — este es el producto final |
| Datos_Imputados_v4_3_Corrected.csv | ~14 MB | Dataset v4.3 (contiene artefacto CALAMAR 1969) | Referencia historica |
| Datos_Imputados_v4_2_Complete.csv | ~16 MB | Dataset v4.2 base | Referencia historica |
| Datos_Imputados_v4_4_SAITS.csv | ~14 MB | Dataset con SAITS (descartado, valores constantes) | No usar |
| detalle_parche_calamar_v4_4.csv | ~3 KB | Auditoria dia a dia del parche | Auditoria / transparencia |
| Tabla_Modelos_HH_v4_3.csv | ~1 KB | Tabla de modelos H-H aceptados (R2, ecuaciones, n) | Referencia metodologica |

### Estructura del dataset final (columnas)

```
CodigoEstacion     — Codigo IDEAM
NombreEstacion     — Nombre de la estacion
Fecha              — Fecha (YYYY-MM-DD)
Cota               — Nivel en m.s.n.m. (original o imputado)
Nivel_Imputacion   — Nivel jerarquico (1, 2, 3, 4)
Metodo             — Metodo especifico (Original, L1_Interpolacion, L2_HH_X_quadratic, L3_missForest, L4_Climatologia_Estacional)
```

---

## 4. CARTILLAS DE ESTACIONES - FIGURAS GENERADAS

### A. Version v4.3 (90 figuras, 18 estaciones × 5 figuras)

**Ubicacion:** `cartillas_estaciones/v4_3/`

| Estacion | Figuras | Ruta |
|----------|---------|------|
| ARMENIA | 5 | `v4_3/ARMENIA/` |
| BARBOSA | 5 | `v4_3/BARBOSA/` |
| CALAMAR | 5 | `v4_3/CALAMAR/` |
| COYONGAL | 5 | `v4_3/COYONGAL/` |
| EL_BANCO | 5 | `v4_3/EL_BANCO/` |
| EL_CONTENTO | 5 | `v4_3/EL_CONTENTO/` |
| GAMARRA_AUT | 5 | `v4_3/GAMARRA_AUT/` |
| LAS_AGUADAS | 5 | `v4_3/LAS_AGUADAS/` |
| LAS_PALOMAS | 5 | `v4_3/LAS_PALOMAS/` |
| LA_GLORIA | 5 | `v4_3/LA_GLORIA/` |
| MAGANGUE | 5 | `v4_3/MAGANGUE/` |
| PENONCITO | 5 | `v4_3/PENONCITO/` |
| PLATO | 5 | `v4_3/PLATO/` |
| PUERTO_WILCHES | 5 | `v4_3/PUERTO_WILCHES/` |
| RIO_NUEVO | 5 | `v4_3/RIO_NUEVO/` |
| SAN_PEDRITO | 5 | `v4_3/SAN_PEDRITO/` |
| SITIO_NUEVO | 5 | `v4_3/SITIO_NUEVO/` |
| TENERIFE | 5 | `v4_3/TENERIFE/` |

**5 figuras por estacion:**
1. `Fig1_SerieTiempo_*.png` — Serie temporal completa (linea negra)
2. `Fig2_ViolinMensual_*.png` — Distribucion mensual (violin plots)
3. `Fig3_CurvaDuracion_*.png` — Curva de duracion con P50/P90/P95/P100
4. `Fig4_PercentilesDiarios_*.png` — Percentiles climatologicos diarios (P5-P95, mediana)
5. `Fig5_Distribuciones_*.png` — Ajuste de 6 distribuciones estadisticas

**IMPORTANTE:** Los percentiles de Fig4 se calculan EXCLUSIVAMENTE con datos originales (`Metodo == 'Original'`), nunca con imputados. Esto garantiza que los percentiles climatologicos no esten contaminados.

### B. Version v4.4 (5 figuras, solo CALAMAR actualizado)

**Ubicacion:** `cartillas_estaciones/v4_4_CALAMAR/`

| Figura | Descripcion | Diferencia vs v4.3 |
|--------|-------------|-------------------|
| `Fig1_SerieTiempo_CALAMAR_v4_4.png` | Serie temporal | **No hay linea plana en 1969-1970** (artefacto eliminado) |
| `Fig2_ViolinMensual_CALAMAR_v4_4.png` | Violin mensual | Identico (usa solo originales) |
| `Fig3_CurvaDuracion_CALAMAR_v4_4.png` | Curva de duracion | Ligera mejora en cola inferior |
| `Fig4_PercentilesDiarios_CALAMAR_v4_4.png` | Percentiles diarios | Identico (usa solo originales) |
| `Fig5_Distribuciones_CALAMAR_v4_4.png` | Distribuciones | Ligera mejora en ajuste |

**Nota:** Las otras 17 estaciones NO cambian entre v4.3 y v4.4 (solo CALAMAR fue modificado). Las cartillas v4.3 de las otras 17 estaciones siguen siendo validas.

---

## 5. DOCUMENTOS DE REDACCION - QUE COPIAR AL INFORME

### Documentos principales (entregar)

| Documento | Ruta | Que copiar |
|-----------|------|------------|
| **REDACTION_IMPUTACION_v4_4_FINAL.md** | `docs/` | **TODO** — Metodologia completa L0-L4, tablas de resumen, modelos H-H, parche climatologico |
| **REPORTE_VERIFICACION_v4_4.md** | `docs/` | **Resumen** — Checks PASS/WARN, conclusion de aprobacion |
| **GUIA_ENTREGA_JEFE_v4_4.md** | `docs/` | Para ti — checklist y respuestas a preguntas esperadas |
| **GUIA_NAVEGACION_COMPLETA_v4_4.md** | `docs/` | Este documento — mapa completo del ecosistema |

### Documentos de referencia (no copiar, solo mencionar)

| Documento | Ruta | Uso |
|-----------|------|-----|
| REDACTION_IMPUTACION_v4_3_FINAL.md | `docs/` | Version anterior (mencionar como evolucion) |
| REPORTE_VERIFICACION_v4_3.md | `docs/` | Verificacion v4.3 (referencia) |
| PLAN_VERIFICACION_v4_3.md | `docs/` | Plan de pruebas (referencia) |
| REGLAS_IMPUTACION_V3.md | raiz | Reglas del sistema (referencia tecnica) |
| MAESTRO_PROYECTO.md | raiz | Vision general del proyecto |

---

## 6. CHECKLIST DE ENTREGA UNIFICADA AL JEFE

### Paquete 1: Dataset final
- [ ] `Datos_Imputados_v4_4_ClimatologyPatch.csv`
- [ ] `detalle_parche_calamar_v4_4.csv` (auditoria)

### Paquete 2: Codigos fuente (carpeta `src/analysis/`)
- [ ] `imputation_system_v4_3.py` (**sistema principal**)
- [ ] `verificacion_v4_3.py` (**verificacion de calidad**)
- [ ] `parche_calamar_climatologia_v4_4.py` (**parche v4.4**)
- [ ] `generar_cartillas_v4_3.py` (generador de figuras)
- [ ] `generar_stacked_bars_imputacion_v4_3.py` (grafico de composicion)
- [ ] `generar_heatmap_datos_nulos_v3.py` (heatmap de cobertura)
- [ ] `imputation_multivariate_hh_v4_4.py` (desarrollo futuro — mencionar)

### Paquete 3: Cartillas (carpeta `cartillas_estaciones/`)
- [ ] `v4_3/` — **90 figuras de 18 estaciones** (5 figuras cada una)
- [ ] `v4_4_CALAMAR/` — **5 figuras actualizadas de CALAMAR**

### Paquete 4: Documentos (carpeta `docs/`)
- [ ] `REDACTION_IMPUTACION_v4_4_FINAL.md` (texto para el informe)
- [ ] `REPORTE_VERIFICACION_v4_4.md` (verificacion de calidad)

---

## 7. NARRATIVA PARA LA PRESENTACION (10 minutos)

### Diapositiva 1: Problema
> "Teniamos datos faltantes en 18 estaciones del Rio Magdalena (1967-2025). Necesitabamos completar las series sin contaminar los analisis de frecuencia."

### Diapositiva 2: Solucion — Cascada jerarquica
> "Implementamos un sistema de 4 niveles:
> - L0: Datos originales (86 %)
> - L1: Interpolacion local (1 %)
> - L2: Curvas altura-altura cuadraticas (7.5 %)
> - L3: missForest multivariado (5.5 %)
> - L4: Climatologia estacional (parche, 0.02 %)"

### Diapositiva 3: Control de calidad
> "El sistema tiene 9 verificaciones automaticas:
> - Inmutabilidad de originales
> - Hard rule (nunca fuera del rango historico)
> - Orientacion hidrologica correcta
> - Sin data leakage
> - Cobertura 100% en 14 estaciones homogeneas"

### Diapositiva 4: Artefacto detectado y corregido
> "En revision de calidad detectamos 61 dias de CALAMAR (1969-1970) imputados como una linea constante por missForest. Evaluamos SAITS (deep learning) y H-H Multivariado, pero el parche climatologico fue la solucion mas eficiente. Ahora la serie tiene variabilidad estacional real."

### Diapositiva 5: Producto final
> "Dataset v4.4: 308,364 registros, 18 estaciones, 100% cobertura en 14 estaciones homogeneas. Listo para analisis de frecuencia y diseno hidraulico. Las cartillas de las 18 estaciones estan generadas y validadas."

---

## 8. PROXIMOS PASOS (para discutir con el jefe)

1. **Aprobacion del dataset v4.4** para entregar al equipo de analisis de frecuencia
2. **Decision sobre H-H Multivariado** — si se requiere reemplazar mas bloques missForest en el futuro
3. **Evaluacion de modelos de deep learning** con ventanas > 365 dias (cuando haya datos suficientes)
4. **Publicacion de metodologia** — el sistema de cascada jerarquica con hard rule es reproducible
