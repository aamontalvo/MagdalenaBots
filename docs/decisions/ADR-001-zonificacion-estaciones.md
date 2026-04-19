# ADR-001: Zonificación de Estaciones del Río Magdalena

## Estado
**Aceptado** - 2026-03-06

## Contexto

El proyecto requiere organizar 18 estaciones hidrométricas del IDEAM de manera que refleje la realidad geográfica e hidrológica del Río Magdalena. Se necesita una zonificación que:

1. Respete el orden hidrológico (aguas abajo → aguas arriba)
2. Considere la confluencia con el Río Cauca como punto de división
3. Permita análisis comparativos entre tramos del río

## Decisión

Se establece una zonificación en tres niveles:

### Zona Baja (7 estaciones)
**Criterio:** Estaciones ubicadas aguas abajo de la confluencia con el Río Cauca.

**Estaciones (orden hidrológico):**
1. San Pedrito
2. Calamar
3. Tenerife
4. Plato
5. Magangue
6. Barbosa
7. Coyongal

### Zona Media (6 estaciones)
**Criterio:** Estaciones ubicadas entre la primera aguas arriba de la confluencia con el Cauca y Peñoncito.

**Estaciones (orden hidrológico):**
1. Armenia
2. Rio Nuevo
3. Las Palomas
4. Las Aguadas
5. El Banco
6. Penoncito

### Zona Alta (5 estaciones)
**Criterio:** Estaciones del tramo alto del Río Magdalena.

**Estaciones (orden hidrológico):**
1. La Gloria
2. Gamarra Aut
3. El Contento
4. Sitio Nuevo
5. Puerto Wilches

## Consecuencias

### Positivas
- Orden lógico que refleja la realidad hidrológica
- Facilita comparaciones entre tramos del río
- Permite identificar gradientes de elevación (aguas abajo → aguas arriba)

### Negativas / Consideraciones
- **Sitio Nuevo** presenta una cota anómala (~50.67 msnm) para su ubicación en Zona Alta. Esto se debe a su ubicación en una zona de remanso y debe ser documentado en los análisis.

## Notas Especiales

### Estación Gamarra
- Solo existe **Gamarra Aut** (automática) en los datos
- Código: 23217080
- La estación Gamarra manual no está disponible en el dataset actual

### Estación San Pedrito
- Incluida en Zona Baja como primera estación del orden hidrológico
- Periodo de datos: 1979-2019

## Referencias

- Implementación: `src/analysis/ideam_levels_analysis.py`
- Documentación: `src/analysis/ZONIFICACION_ESTACIONES.md`
- Configuración: `.claude/settings.json`
