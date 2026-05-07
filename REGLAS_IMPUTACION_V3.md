# REGLAS DE IMPUTACION - Sistema v3.0
## HARD RULE: Nunca imputar fuera del rango original de cada estacion

**Fuentes oficiales de datos:**
- Fuente primaria (verdad absoluta): `Resumen_Crudos_IDEAM_2026.csv` / `.xlsx`
- Fuente historica: `Resumen_LongFormat_NotProcessedNotImputation.csv`

---

## ACTUALIZACION - 06 de Mayo 2026 (Hallazgos del dia)

### Hallazgo 1: Correccion del parser de San Pedrito
Se descubrio que pandas `pd.read_excel()` con `header=0` renombraba las columnas de anos 2020-2026 como `Unnamed: 42`, `Unnamed: 43`, etc., porque la fila 0 (header) tenia NaN en esas columnas. Esto causo que San Pedrito se truncara artificialmente en 2019, perdiendo 6 anos de datos.

**Solucion aplicada:** Leer los datos sin header y detectar las columnas de ano por posicion/valor numerico.

### Hallazgo 2: San Pedrito ya NO esta excluida
Con los datos completos (1979-2025), San Pedrito muestra correlaciones excepcionales:
- vs Calamar: **r = 0.996** (R2 = 0.993, cuadratico)
- vs Magangue: r = 0.985
- vs Tenerife: r = 0.983

**Resultado:** San Pedrito es ahora una estacion completamente viable para imputacion via H-H.

### Hallazgo 3: Cobertura de San Pedrito despues de imputacion
- Datos originales: 16,409 (95.7%)
- Imputados L1 (interpolacion local): 35 (0.2%)
- Imputados L2 (H-H con Calamar): 711 (4.1%)
- **Cobertura final: 100.0%** (17,155 registros, 0 faltantes)

### Archivos actualizados hoy
- `Resumen_Crudos_IDEAM_2026.csv` / `.xlsx` - Fuente de la verdad LONG
- `Datos_Imputados_v4_2_Complete.csv` - San Pedrito regenerado quirurgicamente
- Curvas H-H oficiales de San Pedrito en `Informes/imputacion/Curvas_HH_v4_2/`
- Cartillas Fig1-5 de San Pedrito en `cartillas_estaciones/v4_2/SAN_PEDRITO/`

---

**Reglas de construccion del dataset maestro:**
1. Formato LONG unico. No se usan formatos wide.
2. Cada estacion tiene su propio rango temporal: desde su **PRIMERA fecha con dato real** (no NaN) hasta su **ULTIMA fecha con dato real**, con **corte maximo al 31-12-2025**.
3. **NO se extrapola/imputa fuera del rango real de datos de cada estacion.** Si una estacion inicia el 01-09-1974, no existen filas antes de esa fecha.
4. Dentro del rango real, los dias faltantes se crean con valor en blanco (NaN) para posterior imputacion.
5. **NO se incluye el 29 de febrero** en ninguna estacion, independientemente de si el ano es bisiesto.
6. La columna `date` es tipo datetime (en Excel) o string `dd-mm-yyyy` (en CSV).
7. Fuente unica de datos crudos: `backend/data/raw/SERIE NIVELES IDEAM A 2026`

---

## RANGOS VALIDOS POR ESTACION (Hard Limits)

Datos actualizados: Mayo 2026. Corte: 31-12-2025.

| Estacion | Codigo | Inicio (dd-mm-yyyy) | Fin (dd-mm-yyyy) | Dias totales | Validos | Faltantes | Cobertura |
|----------|--------|---------------------|------------------|--------------|---------|-----------|-----------|
| **Armenia** | 25027360 | 01-02-1973 | 15-10-2025 | 19,237 | 15,020 | 4,217 | 78.1% |
| **Barbosa** | 25027530 | 01-10-1973 | 20-12-2024 | 18,696 | 14,350 | 4,346 | 76.8% |
| **Calamar** | 29037020 | 01-02-1967 | 31-12-2025 | 21,504 | 21,341 | 163 | 99.2% |
| **Coyongal** | 25027930 | 01-03-1975 | 31-12-2025 | 18,556 | 15,691 | 2,865 | 84.6% |
| **El Banco** | 25027020 | 01-10-1972 | 31-12-2025 | 19,437 | 18,706 | 731 | 96.2% |
| **El Contento** | 23217030 | 01-09-1974 | 31-12-2025 | 18,737 | 13,430 | 5,307 | 71.7% |
| **Gamarra Aut** | 23217080 | 01-01-2013 | 31-12-2025 | 4,745 | 4,397 | 348 | 92.7% |
| **La Gloria** | 23217060 | 21-04-1991 | 31-12-2025 | 12,665 | 11,140 | 1,525 | 88.0% |
| **Las Aguadas** | 25027490 | 01-04-1973 | 31-08-2025 | 19,133 | 18,749 | 384 | 98.0% |
| **Las Palomas** | 25027390 | 01-08-1973 | 30-06-2025 | 18,949 | 15,688 | 3,261 | 82.8% |
| **Magangue** | 25027680 | 01-04-1973 | 30-12-2025 | 19,254 | 15,799 | 3,455 | 82.1% |
| **Penoncito** | 25027330 | 01-10-1972 | 30-06-2025 | 19,253 | 17,097 | 2,156 | 88.8% |
| **Plato** | 25027450 | 01-06-1976 | 11-12-2025 | 18,079 | 16,142 | 1,937 | 89.3% |
| **Puerto Wilches** | 23187010 | 07-05-2003 | 11-09-2025 | 8,158 | 7,806 | 352 | 95.7% |
| **Rio Nuevo** | 25027630 | 01-10-1974 | 23-10-2025 | 18,638 | 14,209 | 4,429 | 76.2% |
| **San Pedrito** | 29047070 | 01-01-1979 | 31-12-2025 | 17,155 | 16,409 | 746 | 95.7% |
| **Sitio Nuevo** | 23187280 | 01-03-1979 | 31-12-2025 | 17,096 | 15,086 | 2,010 | 88.2% |
| **Tenerife** | 29017010 | 01-10-1973 | 31-12-2025 | 19,072 | 14,171 | 4,901 | 74.3% |

> **HARD RULE:** Nunca imputar datos antes de la fecha de inicio ni despues de la fecha fin de cada estacion.
> 
> **HARD RULE:** La fecha de corte global es el 31-12-2025. Si una estacion tiene datos reales hasta despues de esa fecha, se trunca al 31-12-2025. Si termina antes, su fin es su ultima fecha real.

---

## NIVELES DE IMPUTACIÓN

### NIVEL 1: Interpolación Local Ponderada
**Aplicación:** Gaps de datos faltantes ≤ 3 días consecutivos

**Método:** Media móvil ponderada con kernel [0.1, 0.2, 0.4, 0.2, 0.1]

**Criterio de aceptación:** 
- No aplica R²
- Solo se requiere que existan datos válidos alrededor del gap

**Hallazgos anteriores:**
- 970 valores imputados con este método
- Representa el ~0.37% de los datos totales
- Método más conservador, mínima introducción de sesgo

---

### NIVEL 2: Curvas Altura-Altura (H-H)
**Aplicación:** Gaps de datos faltantes > 3 días consecutivos

**Método:** 
- Regresión lineal: `h_objetivo = a + b × h_donante`
- Regresión cuadrática: `h_objetivo = a + b × h_donante + c × h_donante²`
- Selección del mejor modelo basado en R²

**Criterio de aceptación:**
- **R² ≥ 0.75** (requisito mínimo)
- Comparación explícita lineal vs cuadrático
- Análisis de residuos para validación

**Hallazgos anteriores:**
- 15 modelos H-H aceptados con R² ≥ 0.75
- 38,641 valores imputados con este método
- Mejores correlaciones en estaciones cercanas hidráulicamente

**Modelos aceptados (R² ≥ 0.75):**

| Estación Objetivo | Estación Donante | Modelo | R² | Valores Imputados |
|-------------------|------------------|--------|-----|-------------------|
| Calamar | Magangue | Cuadrático | 0.976 | 53 |
| Tenerife | Calamar | Cuadrático | 0.960 | 890 |
| Plato | Tenerife | Cuadrático | 0.795 | 0 (completa) |
| Magangue | Calamar | Cuadrático | 0.976 | 0 (completa) |
| Barbosa | Magangue | Pearson III | 0.910 | 38 |
| Coyongal | Barbosa | Cuadrático | 0.883 | 0 (completa) |
| Río Nuevo | Las Aguadas | Cuadrático | 0.917 | 326 |
| Las Palomas | Las Aguadas | Cuadrático | 0.921 | 506 |
| Las Aguadas | El Banco | Cuadrático | 0.979 | 0 (completa) |
| El Banco | Las Aguadas | Cuadrático | 0.981 | 550 |
| Peñoncito | El Banco | Cuadrático | 0.809 | 381 |
| La Gloria | Puerto Wilches | Cuadrático | 0.824 | 0 (completa) |
| El Contento | Sitio Nuevo | Cuadrático | 0.763 | 1,605 |
| Sitio Nuevo | El Contento | Cuadrático | 0.828 | 784 |
| Puerto Wilches | Sitio Nuevo | Cuadrático | 0.814 | 330 |

---

### NIVEL 3: Multi-donante Ponderado
**Aplicación:** Casos especiales donde Nivel 2 no es suficiente

**Método:** 
- Combinación de múltiples estaciones donantes
- Pesos basados en correlación (r) con estación objetivo
- Fórmula: `h_imputado = Σ(wi × hi) / Σ(wi)` donde `wi = ri²`

**Criterio de aceptación:**
- **R² efectivo ≥ 0.75**
- Al menos 2 estaciones donantes con r ≥ 0.70

**Hallazgos anteriores:**
- Aplicado en casos de estaciones con comportamiento anómalo
- Útil cuando una sola estación donante no captura la variabilidad

---

## CASOS ESPECIALES Y EXCLUSIONES

### Estaciones con limitaciones:

| Estación | Cobertura | Estado | Observación |
|----------|-----------|--------|-------------|
| **Armenia** | 77.9% | ⚠️ Limitada | Sin donante con r >= 0.85 (confluencia con Cauca) |
| **Gamarra Aut** | 93.0% | ⚠️ Restringida | Serie corta (2013-2025), R2 < 0.75 con donantes |

### Razones de exclusion:
1. **Armenia:** Ubicada en zona de confluencia con el rio Cauca, comportamiento hidrologico diferente al resto del Magdalena
2. **Gamarra Aut:** Serie temporal muy corta (solo 14 anos), insuficiente para establecer correlaciones robustas

### HALLAZGO IMPORTANTE - San Pedrito (Actualizacion Mayo 2026)

**San Pedrito YA NO esta excluida.** Tras la correccion del parser que leia mal las columnas 2020-2026 (renombradas como `Unnamed: XX` por pandas), se descubrio que:

- **Rango completo corregido:** 01-01-1979 a 31-12-2025 (17,155 dias, 95.7% cobertura)
- **Correlacion con Calamar:** r = 0.996 (n = 14,139 dias concurrentes)
- **Correlacion con Magangue:** r = 0.985 (n = 12,402 dias concurrentes)
- **Correlacion con Tenerife:** r = 0.983 (n = 10,680 dias concurrentes)

San Pedrito es ahora una estacion **completamente viable** para imputacion via curvas H-H usando Calamar como donante principal (o Magangue/Tenerife como secundarios).

**Nota:** La baja cobertura anterior (45.4%) y la exclusion se debian a un error tecnico del parser de Excel, no a una limitacion hidrologica real.

---

## RESUMEN DE IMPUTACIÓN (Marzo 2026)

| Concepto | Valor |
|----------|-------|
| **Total de registros procesados** | 326,480 |
| **Datos originales** | 261,055 (80.0%) |
| **Imputados Nivel 1** (interpolación local) | 970 |
| **Imputados Nivel 2** (curvas H-H) | 38,641 |
| **Cobertura promedio final** | 94.13% |

---

## VERIFICACIÓN POST-IMPUTACIÓN

### Checks obligatorios:
1. ✅ Todos los valores imputados dentro del rango válido de la estación
2. ✅ R² ≥ 0.75 para todos los modelos H-H utilizados
3. ✅ Análisis de residuos sin patrones sistemáticos
4. ✅ Coherencia hidrológica entre estaciones vecinas
5. ✅ Sin extrapolación fuera del rango de calibración

---

## ACTUALIZACIÓN CON HARD RULE

A partir de ahora, cualquier imputación debe verificar:

```python
# Pseudocódigo de validación
def validar_rango_imputacion(estacion, fecha):
    rango = RANGOS_ESTACIONES[estacion]
    if fecha < rango['inicio'] or fecha > rango['fin']:
        return False  # NO imputar - fuera de rango válido
    return True  # Dentro del rango, proceder con imputación
```

**Consecuencia del Hard Rule:**
- Si una estación donante tiene datos en 1967-2026
- Y la estación objetivo solo tiene datos en 1991-2026
- **Solo se pueden imputar datos en el periodo 1991-2026**
- Los datos de 1967-1990 de la estación donante se usan solo para calibrar el modelo, NO para imputar en el objetivo

---

*Documento generado: Abril 2026*
*Sistema de Imputación v3.0 - Proyecto Río Magdalena*
