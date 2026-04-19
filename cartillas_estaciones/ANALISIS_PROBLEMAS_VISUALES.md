# Analisis de Problemas Visuales en Estaciones

## Problemas Detectados en las Imagenes

### 1. Armenia - Curva de Frecuencias de Cotas Excedidas

**Problema:** Gran pico/valle artificial en el minimo (extremo izquierdo de la grafica)

**Causa probable:**
- Valores imputados incorrectamente en el rango bajo (niveles menores a ~10 msnm)
- La imputacion probablemente extrapolo hacia valores demasiado bajos
- El modelo H-H no capturo correctamente el comportamiento en estiaje

**Impacto:**
- Los percentiles P1-P5 estan completamente distorsionados
- La curva de duracion muestra un valle antinatural
- Cualquier analisis de frecuencia de minimos sera erroneo

**Solucion:**
- Revisar los valores imputados en el rango < 15 msnm para Armenia
- Posiblemente limitar el rango de imputacion o usar donante diferente

---

### 2. Armenia - Q-Q Plot Weibull

**Problema:** Desviacion masiva de la linea 1:1, especialmente en cuantiles bajos

**Causa probable:**
- Valores atipicos en el extremo inferior de la distribucion
- Los valores observados en los cuantiles teoricos bajos son mucho menores de lo esperado
- Confirma que hay valores erroneos/imputados mal en el rango de estiaje

**Impacto:**
- El ajuste Weibull es inapropiado (aunque el test KS no lo detecte)
- Los parametros de la distrib estan sesgados
- Los percentiles calculados (P10, P90) no son confiables

**Solucion:**
- Limpiar outliers antes de ajustar distribuciones
- Revisar metodologia de imputacion para esta estacion
- Considerar excluir periodos con datos imputados del ajuste de distribucion

---

## Plan de Validacion LIGHT Propuesto

Para detectar estos problemas en TODAS las estaciones sin ser tan pesado como el validador anterior:

### Check 1: Outliers por Percentiles (IQR)
- Detecta valores fuera de rango usando IQR x 3
- Identifica valores extremos que no deberian estar

### Check 2: Saltos en Curva de Duracion
- Calcula diferencias entre percentiles consecutivos
- Detecta saltos grandes (como el valle de Armenia)
- Enfocado especialmente en extremos (10% inferior y superior)

### Check 3: Calidad de Ajuste de Distribucion
- Test KS (Kolmogorov-Smirnov) para Weibull
- Correlacion en Q-Q plot
- Detecta desviaciones sistematicas

### Check 4: Rangos Mensuales
- Verifica que cada mes tenga comportamiento razonable
- Detecta meses con valores atipicos comparados con el patron historico

---

## Ejecucion

```bash
cd cartillas_estaciones
python validar_todas_estaciones_light.py
```

Genera:
- `resultados/validacion_light_todas_estaciones.md` - Reporte con todas las estaciones
- Resumen en consola con estaciones CRITICAL y WARNING

---

## Criterios de Clasificacion

| Estado | Significado | Accion |
|--------|-------------|--------|
| CRITICAL | Problemas graves detectados | Revisar imputacion, posible exclusion |
| WARNING | Problemas menores | Verificar, monitorear |
| OK | Sin problemas detectados | Usar normalmente |

---

## Estaciones que YA sabemos tienen problemas

Basado en el analisis anterior (validacion completa):

| Estacion | Problema Principal | Estado Esperado |
|----------|-------------------|-----------------|
| ARMENIA | Sin donante confiable | CRITICAL |
| GAMARRA_AUT | Serie corta + automatica | CRITICAL |
| RIO_NUEVO | Extrapolacion fuera de rango | WARNING |
| LAS_PALOMAS | Gaps en donante | WARNING |
| COYONGAL | Saltos menores | WARNING |

---

**Nota:** Este analisis light complementa (no reemplaza) la validacion completa anterior. Es mas rapido y enfocado en problemas visuales obvios.
