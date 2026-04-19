# Sistema de Validación de Imputación - Guía de Uso

## Descripción

Sistema de detección de problemas en series temporales imputadas usando 3 filtros hidrológicos validados.

## Estructura de Archivos

```
cartillas_estaciones/
├── funciones/
│   ├── graficador.py              # Funciones de visualización (existente)
│   └── validate_imputation.py     # NUEVO: Sistema de validación
├── validar_estaciones.py          # NUEVO: Script standalone
├── validar_estaciones_problema.ipynb  # NUEVO: Notebook interactivo
├── resultados/
│   ├── validacion_imputacion_problemas.md  # NUEVO: Reporte generado
│   └── periodos_problematicos.csv          # NUEVO: Tabla de problemas
└── README_VALIDACION.md           # Este archivo
```

## Métodos de Uso

### Opción 1: Script Rápido (Recomendado)

```bash
cd cartillas_estaciones
python validar_estaciones.py
```

Genera automáticamente el reporte en `resultados/validacion_imputacion_problemas.md`

### Opción 2: Notebook Interactivo

```bash
jupyter notebook validar_estaciones_problema.ipynb
```

Permite:
- Visualizar series con flags marcados
- Explorar detalle por estación
- Exportar datos a CSV
- Generar gráficos personalizados

### Opción 3: Uso Programático

```python
from funciones.validate_imputation import ImputationValidator

# Crear validador
validator = ImputationValidator(data_path='./datos/processed/')

# Validar una estación
result = validator.validate_station(
    station='COYONGAL',
    neighbor_stations=['BARBOSA', 'MAGANGUE']
)

# Revisar flags
print(result['all_flags'])
print(result['problem_periods'])
```

## Los 3 Filtros de Validación

### 1. Velocidad de Cambio Hidrológica

**Detecta:** Cambios diarios anómalos comparados con histórico

**Umbral:**
- WARNING: > Percentil 99
- CRITICAL: > 2 × Percentil 99.5

**Fórmula:**
```
Δnivel/día = |nivel[t] - nivel[t-1]|
```

**Ejemplo de problema:**
- Estación típica varía 0.3 m/día
- Flag si cambia > 1.5 m en un día (CRITICAL)

---

### 2. Coherencia Espacial

**Detecta:** Inconsistencias con estaciones vecinas

**Umbral:**
- WARNING: Correlación < 0.7 en ventana ±3 días

**Método:**
- Ventana móvil de 7 días
- Correlación Pearson con estaciones vecinas
- Detecta cuando el patrón local no coincide

**Ejemplo de problema:**
- Coyongal sube mientras Magangué baja
- Correlación esperada: r > 0.9
- Flag si r < 0.7

---

### 3. Continuidad en Fronteras

**Detecta:** Saltos bruscos en límites de gaps imputados

**Umbral:**
- WARNING: Salto > 3 σ local
- CRITICAL: Salto > 5 σ local

**Fórmula:**
```
salto_relativo = |nivel[post] - nivel[pre]| / σ_local
```

**Ejemplo de problema:**
- Valor antes del gap: 15.0 m
- Primer valor imputado: 18.5 m
- σ local: 0.8 m
- Salto: 3.5 m = 4.4 σ → CRITICAL

---

## Evaluación de tu Propuesta (Porcentaje de Cambio)

### Tu Idea Original
```python
df['pct_change'] = df['level'].pct_change().abs()
# Flag si pct_change > umbral
```

### Problemas Identificados

| Problema | Ejemplo | Consecuencia |
|----------|---------|--------------|
| **Falsos positivos** | Creciente real: 5m → 10m (+100%) | Marcarías evento válido como error |
| **Dependencia nivel** | 0.5→1.0m (100%) vs 10→11m (10%) | Mismo cambio absoluto, diferente alerta |
| **No detecta forma** | Curva suave pero desplazada | Error sistemático pasa desapercibido |

### Mejora Sugerida (Velocidad Relativa al Rango)

```python
rango = nivel_max - nivel_min
velocidad_relativa = abs(Δnivel) / rango

# Ejemplo:
# Estación A: rango 10m, cambio 2m → 0.20 (20% del rango)
# Estación B: rango 50m, cambio 2m → 0.04 (4% del rango)
# → Estación A requiere más atención
```

**Ventajas:**
- Normalizado por dinámica de cada estación
- Comparable entre estaciones
- Detecta proporción del rango operativo

---

## Interpretación de Resultados

### Clasificación de Estaciones

| Evaluación | Flags | Acción |
|------------|-------|--------|
| ✓ SERIE VALIDA | 0 | Usar sin restricciones |
| ⚠ REVISION MENOR | < 0.1% datos | Revisar flags individuales |
| ⚠ SERIE DUDOSA | 0.1-5% datos | Revisar periodos marcados |
| ✗ SERIE CRITICA | > 5% datos | Revisión completa, posible exclusión |

### Estados de Severidad

| Severidad | Color | Significado | Acción |
|-----------|-------|-------------|--------|
| CRITICAL | 🔴 | Cambio excede 2×p99.5 o salto >5σ | Revisar inmediatamente |
| WARNING | 🟡 | Cambio excede p99 o correlación <0.7 | Verificar si es evento real |

---

## Estaciones Problemáticas Identificadas

### Prioridad 1 (Acción Inmediata)

#### ARMENIA
- **Problema:** Sin donante confiable (zona de confluencia con Cauca)
- **Cobertura:** 77.9% (4,280 días faltantes)
- **Recomendación:** NO imputar. Usar solo datos observados.
- **Impacto:** Excluir de análisis de frecuencia

#### GAMARRA_AUT
- **Problema:** Serie corta (2013-2025) + estación automática
- **Cobertura:** 93.0% de serie corta
- **Recomendación:** NO imputar. Uso restringido a análisis recientes.
- **Impacto:** Solo análisis 2013-2025

### Prioridad 2 (Ajuste Metodológico)

#### RIO_NUEVO
- **Problema:** Extrapolación cuadrática fuera de rango
- **Solución:** Limitar imputación a [21, 26] msnm
- **Impacto:** ~0.3% datos afectados

#### LAS_PALOMAS
- **Problema:** Gaps en donante (Las Aguadas) propagan errores
- **Solución:** Usar donante alternativo (El Banco) en periodos críticos
- **Impacto:** ~0.4% datos afectados

### Prioridad 3 (Optimización)

#### COYONGAL
- **Problema:** Saltos menores en fronteras
- **Solución:** Ajustar modelo cuadrático o considerar lineal
- **Impacto:** <0.1% datos afectados

---

## Próximos Pasos Sugeridos

1. **Revisar manualmente** periodos marcados como CRITICAL en ARMENIA y GAMARRA_AUT
2. **Comparar con aforos** de campo si están disponibles
3. **Ajustar modelo H-H** para RIO_NUEVO limitando rango de extrapolación
4. **Implementar sistema de donantes alternativos** para LAS_PALOMAS
5. **Documentar metadatos** de estaciones automáticas (GAMARRA_AUT)

---

## Contacto

**Responsable:** Alexander Alberto Montalvo Molina  
**Proyecto:** BPIN 2024000100122 - Contrato UN-OJ-2025-66227  
**Fecha:** Marzo 2026
