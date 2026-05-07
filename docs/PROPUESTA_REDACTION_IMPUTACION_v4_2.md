# PROPUESTA DE REDACCIÓN — Sección: Imputación de Datos Faltantes (v4.2)
## Diagnóstico técnico + Texto condensado (~60% del original)

> Fecha: 07 de mayo de 2026
> Base: Datos reales de `Datos_Imputados_v4_2_Complete.csv` (306,623 registros)

---

## 🔴 CAMBIOS TÉCNICOS QUE INVALIDAN EL TEXTO ACTUAL

### 1. San Pedrito — de "caso extremo de exclusión" a "estrella de la imputación"

**El texto actual dice:**
> "San Pedrito representa el caso extremo de imposibilidad de imputación... 45.4% cobertura... 17,127 días faltantes... no apta para análisis estadísticos."

**La realidad v4.2 (post-corrección 06-mayo-2026):**
- Parser corregido: pandas renombraba columnas 2020-2026 como `Unnamed: XX`, truncando la serie en 2019.
- Con datos completos (1979-2025): correlación excepcional con Calamar **r = 0.996, R² = 0.993**.
- Imputación: 16,409 originales (95.7%) + 35 L1 + 711 L2 (H-H con Calamar) = **17,155 registros, 100% cobertura**.
- **San Pedrito es ahora una estación completamente viable** y debe aparecer como ejemplo positivo, no de exclusión.

### 2. NO existe "Regresión Lineal Multivariable" (L3 multi-donante)

**El texto actual tiene una subsección:**
> "Nivel L2: Regresión Lineal Multivariable... combinación ponderada utilizando múltiples estaciones donantes..."

**La realidad v4.2:**
- **NUNCA se usó multi-donante.** Todos los modelos H-H del sistema v4.2 usan **UNA sola estación donante** con ecuación cuadrática.
- La subsección entera debe eliminarse. El intento con San Pedrito usando múltiples donantes generó R² = 0.29, pero eso fue exploratorio y **no forma parte del sistema final**.

### 3. Estructura real del sistema: 4 niveles, no 3

| Nivel | Método | R² Umbral | Valores Imputados | % del total |
|-------|--------|-----------|-------------------|-------------|
| **L1** | Interpolación local ponderada | N/A | 1,003 | 0.33% |
| **L2** | H-H Cuadrática (Alta confianza) | **R² ≥ 0.95** | 8,938 | 2.91% |
| **L3** | H-H Cuadrática (Media confianza) | **0.75 ≤ R² < 0.95** | 17,793 | 5.80% |
| **L4** | missForest / Extrapolación | N/A | 5,363 | 1.75% |
| | **Total imputados** | | **33,097** | **10.6%** |

**Nota crítica:** L2 y L3 usan el **MISMO método matemático** (ecuación cuadrática con una donante). La diferencia es puramente de **clasificación por calidad de correlación**. No ameritan secciones metodológicas separadas.

### 4. Coberturas reales vs. las del texto anterior

**El texto dice:** "Cinco estaciones alcanzan cobertura del 100%: Plato, Coyongal, La Gloria, además de Magangue (99.8%) y Las Aguadas (99.6%)"

**La realidad (conteo de NaN en el dataset maestro):**

| Estación | Cobertura real | Faltantes (NaN) | Estado |
|----------|---------------|-----------------|--------|
| **San Pedrito** | **100.0%** | 0 | ✅ Completa |
| **Plato** | **100.0%** | 0 | ✅ Completa |
| **Puerto Wilches** | **100.0%** | 0 | ✅ Completa |
| Magangue | 99.79% | 41 | Casi completa |
| Tenerife | 99.78% | 42 | Casi completa |
| Barbosa | 99.83% | 31 | Casi completa |
| Coyongal | 99.57% | 80 | Casi completa |
| Río Nuevo | 99.01% | 185 | Casi completa |
| Las Palomas | 99.17% | 158 | Casi completa |
| Peñoncito | 98.59% | 272 | Casi completa |
| Las Aguadas | 98.09% | 366 | Casi completa |
| El Banco | 96.35% | 711 | Alta |
| Sitio Nuevo | 95.84% | 712 | Alta |
| El Contento | 92.73% | 1,364 | Media |
| Gamarra Aut | 93.08% | 330 | Media (serie corta) |
| La Gloria | 88.22% | 1,495 | Media |
| **Armenia** | **78.32%** | **4,173** | ⚠️ Limitada |

**Cobertura global ponderada:** ~96.7% (no 95.5% ni 97.9%).

### 5. Armenia y Gamarra Aut siguen siendo los casos problemáticos
- **Armenia**: Sin donante con r ≥ 0.85 (confluencia con Cauca). Cobertura 78.3%. Esto sigue siendo correcto en el texto.
- **Gamarra Aut**: Serie corta (2013-2025), sin modelo H-H aceptado. Cobertura 93.1%. Esto sigue siendo correcto.

---

## 📝 TEXTO PROPUESTO (versión condensada)

A continuación la redacción propuesta (~60% del original). Se eliminan:
- El párrafo introductorio excesivamente largo (de ~5 párrafos a 1).
- La subsección de multi-donante (no se usó).
- Las descripciones detalladas de cada par estación-donante (se resumen por zona).
- Las repeticiones de conceptos (L2 y L3 se fusionan).
- Los números desactualizados de cobertura.

---

```markdown
# Imputación de datos faltantes

La imputación de datos faltantes garantiza la continuidad temporal requerida para análisis de frecuencia y tendencias de largo plazo. El sistema implementado opera mediante una cascada jerárquica de cuatro niveles, donde la selección del método depende de la magnitud del gap, la disponibilidad de estaciones donantes correlacionadas y la calidad estadística de las relaciones altura–altura (H–H) establecidas. El flujograma de ejecución y los porcentajes de aporte por nivel se resumen en la Figura 10 [AM9.1].

El criterio de aceptación para modelos H–H se fija en R² ≥ 0.75, umbral que asegura la explicación de al menos el 75 % de la varianza. Los modelos por debajo de este valor se documentan con fines diagnósticos pero no se utilizan para imputación efectiva.

## Resumen de resultados

El proceso imputó 33,097 valores (10.6 % del total de 306,623 registros), distribuidos en cuatro niveles. La cobertura global ponderada alcanza el 96.7 %, con tres estaciones al 100 % (San Pedrito, Plato y Puerto Wilches) y Armenia como único caso con cobertura inferior al 90 % (78.3 %).

| Estación | Original | L1 | L2 | L3 | L4 | NaN | Cobertura |
|----------|----------|----|----|----|----|-----|-----------|
| San Pedrito | 16,409 | 35 | 711 | — | — | 0 | **100.0 %** |
| Plato | 14,145 | 57 | — | 1,717 | — | 0 | **100.0 %** |
| Puerto Wilches | 7,806 | 42 | — | — | 316 | 0 | **100.0 %** |
| Magangue | 15,840 | 59 | 3,368 | — | — | 41 | 99.8 % |
| Tenerife | 14,221 | 45 | 4,859 | — | — | 42 | 99.8 % |
| Barbosa | 14,381 | 35 | — | 4,293 | — | 31 | 99.8 % |
| Coyongal | 15,806 | 54 | — | 2,749 | — | 80 | 99.6 % |
| Río Nuevo | 14,394 | 92 | — | 4,165 | — | 185 | 99.0 % |
| Las Palomas | 15,846 | 84 | — | 3,032 | — | 158 | 99.2 % |
| Peñoncito | 17,369 | 60 | — | 1,837 | — | 272 | 98.6 % |
| Las Aguadas | 19,115 | 31 | — | 384 | — | 366 | 98.1 % |
| El Banco | 19,455 | 35 | — | 646 | — | 711 | 96.4 % |
| Sitio Nuevo | 15,816 | 101 | — | — | 1,209 | 712 | 95.8 % |
| El Contento | 14,811 | 118 | — | — | 3,838 | 1,364 | 92.7 % |
| Gamarra Aut | 4,745 | 21 | — | — | — | 330 | 93.1 % |
| La Gloria | 12,651 | 41 | — | — | — | 1,495 | 88.2 % |
| **Armenia** | **19,193** | **57** | **—** | **—** | **—** | **4,173** | **78.3 %** |

*Nota: L2 = H-H alta confianza (R² ≥ 0.95); L3 = H-H media confianza (0.75 ≤ R² < 0.95); L4 = missForest/extrapolación. El guión largo (—) indica que el nivel no aplica para esa estación.*

## Nivel L1: Interpolación local ponderada

Períodos con gaps ≤ 3 días se completan mediante media móvil ponderada de cinco puntos con kernel [0.1, 0.2, 0.4, 0.2, 0.1]. Se requiere al menos dos valores vecinos válidos; no se aplica al inicio o final de serie. Este nivel imputó 1,003 valores (0.33 % del total), distribuidos en 16 estaciones.

## Niveles L2 y L3: Curvas altura–altura (H–H)

Para gaps > 3 días se establecen relaciones estadísticas entre estaciones cercanas mediante regresión cuadrática de una sola variable (una estación donante). La comparación lineal vs. cuadrática se realiza para cada par, seleccionándose la forma que maximice R². El modelo adopta la forma H_obj = a·H_don² + b·H_don + c, donde la donante se elige como la estación con mayor correlación de Pearson (r ≥ 0.85) con el objetivo.

**Clasificación por confianza:** ambos niveles comparten el mismo método matemático; la distinción responde únicamente a la calidad del ajuste:

- **L2 — Alta confianza (R² ≥ 0.95):** 8,938 valores imputados. Aplica a Tenerife (donante Calamar, 4,859 valores), Magangue (donante Calamar, 3,368 valores) y San Pedrito (donante Calamar, 711 valores).
- **L3 — Media confianza (0.75 ≤ R² < 0.95):** 17,793 valores imputados. Aplica a Barbosa (Magangue, R² = 0.898), Río Nuevo (Las Aguadas, R² = 0.917), Las Palomas (Las Aguadas, R² = 0.921), Coyongal (Barbosa, R² = 0.876), Peñoncito (El Banco, R² = 0.814) y Plato (Tenerife, R² = 0.782).

Las mejores correlaciones se concentran en la Zona Baja: El Banco–Las Aguadas (R² = 0.980), Calamar–Magangue (R² = 0.976) y Tenerife–Calamar (R² = 0.961). La Zona Media presenta relaciones mixtas, coherentes con la mayor complejidad geomorfológica del tramo.

### Casos con limitaciones

**Armenia** no dispone de donante con r ≥ 0.85. Su ubicación en la confluencia con el Río Cauca introduce variabilidad no capturada por modelos bivariados simples, resultando en 4,173 días faltantes (21.7 % del rango). Su cobertura del 78.3 % es aceptable para tendencias de largo plazo, pero insuficiente para análisis de frecuencia de eventos extremos sin sensibilidad adicional.

**Gamarra Aut** (serie 2013-2025) no alcanza el umbral mínimo con ninguna donante por su corta longitud de registro. Se clasifica como estación de uso restringido a análisis de variabilidad reciente.

## Nivel L4: Imputación no paramétrica (missForest / extrapolación)

Cuando no existe donante con R² ≥ 0.75, se aplica missForest o extrapolación local para completar gaps extensos. Este nivel imputó 5,363 valores: El Contento (3,838), Sitio Nuevo (1,209) y Puerto Wilches (316). Los valores imputados por este método se marcan explícitamente y requieren análisis de sensibilidad en aplicaciones de diseño.

## Recomendaciones de uso de las series completadas

Para **análisis de frecuencia y diseño hidráulico** se recomiendan las 15 estaciones con cobertura ≥ 90 %, excluyendo únicamente a Armenia. Las estaciones con cobertura ≥ 98 % (San Pedrito, Plato, Puerto Wilches, Magangue, Tenerife, Barbosa, Coyongal, Río Nuevo, Las Palomas) pueden usarse sin restricciones. Las de cobertura 90–98 % (Peñoncito, Las Aguadas, El Banco, Sitio Nuevo, El Contento, Gamarra Aut, La Gloria) requieren verificar que los gaps no correspondan a eventos extremos que afecten cuantiles altos.

Para **análisis de tendencias**, todas las estaciones con cobertura ≥ 90 % son utilizables, con la advertencia de excluir sub-períodos donde la proporción de datos imputados supere el 20 % anual.
```

---

## 📊 Comparación de extensión

| Componente | Texto actual (líneas aprox.) | Propuesta (líneas aprox.) | Reducción |
|------------|------------------------------|---------------------------|-----------|
| Introducción + criterio R² | 25 | 8 | 68 % |
| Resumen de resultados | 30 | 22 | 27 % |
| L1: Interpolación | 20 | 6 | 70 % |
| L2: H-H (incluye subsecciones) | 80 | 25 | 69 % |
| L2 multivariable (multi-donante) | 20 | **0 (eliminado)** | 100 % |
| Casos particulares | 30 | 12 | 60 % |
| L3: Miss Forest | 5 | **Integrado en L4** | — |
| Recomendaciones | 25 | 10 | 60 % |
| **TOTAL** | **~235** | **~83** | **~65 %** |

---

## ⚠️ Decisiones pendientes para el usuario

1. **¿Incluir ecuaciones específicas de cada modelo H-H?** El texto original incluye la ecuación completa de Calamar–Magangue, etc. En la propuesta se omiten por brevedad, pero pueden agregarse en una tabla anexa si el director lo requiere.

2. **¿Mencionar explícitamente que L2 y L3 son el mismo método?** La propuesta lo aclara ("ambos niveles comparten el mismo método matemático"). Si se prefiere una terminología más simple, podría renombrarse como "L2-Alta" y "L2-Media" en lugar de L2/L3.

3. **¿Nivel de detalle de la tabla de cobertura?** La propuesta incluye tabla completa por estación. Si se prefiere aún más brevedad, puede resumirse en 3 categorías (100 %, 90–99 %, < 90 %).

4. **¿San Pedrito en recomendaciones?** Ahora que tiene 100 % cobertura y R² = 0.993, pasa a la categoría de "uso sin restricciones". Esto es un cambio radical respecto al texto anterior.
