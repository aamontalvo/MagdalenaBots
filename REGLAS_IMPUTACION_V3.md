# REGLAS DE IMPUTACIÓN - Sistema v3.0
## HARD RULE: Nunca imputar fuera del rango original de cada estación

**Fuente oficial de datos:** `Resumen_LongFormat_NotProcessedNotImputation.csv`

---

## RANGOS VÁLIDOS POR ESTACIÓN (Hard Limits)

| Estación | Código | Inicio (dd-mm-yyyy) | Fin (dd-mm-yyyy) | Años |
|----------|--------|---------------------|------------------|------|
| **Puerto Wilches** | 23187010 | 07-05-2003 | 11-09-2025 | 23 |
| **Sitio Nuevo** | 23187280 | 01-03-1979 | 18-01-2026 | 48 |
| **El Contento** | 23217030 | 01-09-1974 | 17-01-2026 | 53 |
| **La Gloria** | 23217060 | 21-04-1991 | 18-01-2026 | 36 |
| **Gamarra Aut** | 23217080 | 01-01-2013 | 18-01-2026 | 14 |
| **El Banco** | 25027020 | 01-10-1972 | 09-02-2026 | 55 |
| **Peñoncito** | 25027330 | 01-10-1972 | 30-06-2025 | 54 |
| **Armenia** | 25027360 | 01-02-1973 | 15-10-2025 | 53 |
| **Las Palomas** | 25027390 | 01-08-1973 | 30-06-2025 | 53 |
| **Plato** | 25027450 | 01-06-1976 | 31-12-2019 | 44 |
| **Las Aguadas** | 25027490 | 01-04-1973 | 31-08-2025 | 53 |
| **Barbosa** | 25027530 | 01-10-1973 | 20-12-2024 | 52 |
| **Rio Nuevo** | 25027630 | 01-10-1974 | 23-10-2025 | 52 |
| **Magangue** | 25027680 | 01-04-1973 | 30-12-2025 | 53 |
| **Coyongal** | 25027930 | 01-03-1975 | 09-02-2026 | 52 |
| **Tenerife** | 29017010 | 01-10-1973 | 09-02-2026 | 54 |
| **Calamar** | 29037020 | 01-02-1967 | 09-02-2026 | 60 |
| **San Pedrito** | 29047070 | 01-01-1979 | 31-12-2019 | 41 |

> **⚠️ HARD RULE:** Nunca imputar datos antes de la fecha de inicio ni después de la fecha fin de cada estación.

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
| **Armenia** | 77.9% | ⚠️ Limitada | Sin donante con r ≥ 0.85 (confluencia con Cauca) |
| **Gamarra Aut** | 93.0% | ⚠️ Restringida | Serie corta (2013-2025), R² < 0.75 con donantes |
| **San Pedrito** | 45.4% | ❌ Excluida | Estación terminal sin donantes aguas arriba |

### Razones de exclusión:
1. **Armenia:** Ubicada en zona de confluencia con el río Cauca, comportamiento hidrológico diferente al resto del Magdalena
2. **Gamarra Aut:** Serie temporal muy corta (solo 14 años), insuficiente para establecer correlaciones robustas
3. **San Pedrito:** Estación terminal del sistema, no tiene estaciones donantes aguas arriba con correlación aceptable

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
