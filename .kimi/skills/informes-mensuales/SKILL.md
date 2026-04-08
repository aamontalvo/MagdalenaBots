# Skill: Informes Mensuales - Ejecución Contractual

Este skill estandariza la creación de informes mensuales para el proyecto BPIN 2024000100122 (Contrato UN-OJ-2025-66227).

## Tipos de Informes a Generar

Cada mes se deben generar **DOS documentos**:

1. **Informe Detallado de Actividades** (`docs/informe_cuenta_cobro_[MES]_[AÑO].md`)
   - Documento técnico completo
   - Metodología, resultados, tablas
   - Público: Equipo técnico

2. **Resumen de Ejecución Contractual** (`docs/resumen_ejecucion_contractual_[MES]_[AÑO].md`)
   - Máximo 3 párrafos
   - Sección 4 del formato oficial
   - Público: Administrativo/Contractual

## Estructura Obligatoria

Todo informe debe seguir esta estructura:

```markdown
# Informe de Actividades - [MES] [AÑO]

**Proyecto BPIN:** 2024000100122  
**Contrato:** UN-OJ-2025-66227  
**Contratista:** Alexander Alberto Montalvo Molina  
**Periodo:** [01] de [mes] hasta [28/30/31] de [mes] de [año]

---

## Actividades Realizadas

### Obligación [N]: [Título de la obligación del contrato]

**Descripción:**

[Descripción detallada de actividades realizadas, incluyendo contexto y alcance]

> **📝 Notas de seguimiento:** [Opcional - anotaciones sobre revisión futura, feedback pendiente, etc.]

**Productos específicos:**

1. [Producto 1]
2. [Producto 2]
3. [Producto 3]

---

## Detalle Técnico del Trabajo Realizado

### Sección [N]: [Título de la sección técnica]

[Contenido técnico con tablas, metodología, resultados]

---

## Productos Entregables

### Código Fuente
- `[ruta/al/script.py]` ([X] líneas) - [Descripción]

### Datos Procesados
- `[ruta/al/archivo.csv]` ([X] registros) - [Descripción]

### Figuras
- `[ruta/figura.png]` - [Descripción]

### Documentación
- `[ruta/documento.md]` - [Descripción]

---

## Resumen Estadístico

| Categoría | Cantidad |
|-----------|----------|
| [Métrica 1] | [Valor] |
| [Métrica 2] | [Valor] |

---

## Notas y Observaciones

1. [Nota relevante]
2. [Actualización metodológica si aplica]
3. [Limitaciones identificadas]
4. [Próximos pasos]

---

**Fecha de elaboración:** [Mes] [Año]  
**Responsable:** Alexander Alberto Montalvo Molina  
**Proyecto:** Análisis Hidrológico Río Magdalena - IDEAM
```

## Convenciones

### Encabezado
- Siempre incluir BPIN, Contrato, Contratista y Periodo
- Formato de fecha: "01 de [mes] hasta [día] de [mes] de [año]"
- Nombres en mayúsculas para campos fijos

### Obligaciones
- Numerar según contrato (Obligación 1, 2, 3...)
- Usar títulos exactos del contrato cuando sea posible
- Incluir notas de seguimiento cuando haya feedback pendiente

### Secciones Técnicas
- Usar tablas Markdown para resultados comparativos
- Incluir unidades de medida (m, m³/s, %, etc.)
- Referenciar figuras con formato: `Figura X.Y`
- Referenciar tablas con formato: `Tabla X.Y`

### Notas de Seguimiento
Usar bloque destacado para notas importantes:

```markdown
> **📝 Nota para seguimiento:** [Texto de la nota]

> **📝 Nota importante:** [Texto de la nota]
```

### Resumen Estadístico
Incluir siempre métricas clave:
- Estaciones procesadas
- Registros/valores procesados
- Scripts desarrollados
- Figuras generadas
- Coberturas alcanzadas

### Productos Entregables
Clasificar en categorías:
- Código Fuente
- Datos Procesados
- Figuras
- Documentación

## Metodología de Imputación (Referencia)

Cuando se reporte imputación de datos, usar esta estructura:

| Nivel | Método | Criterio |
|-------|--------|----------|
| Nivel 1 | Interpolación local | Gaps ≤ 3 días |
| Nivel 2 | Curvas H-H | R² ≥ 0.75 |
| Nivel 3 | Multi-donante | Casos especiales |

## Estados de Estaciones

Usar iconos para clasificación:

| Icono | Estado | Descripción |
|-------|--------|-------------|
| ✅ | Aprobada | Cobertura ≥ 90%, R² ≥ 0.75 |
| ⚠️ | Limitada | Cobertura 75-90%, o problemas menores |
| ❌ | Excluida | Cobertura < 75%, o imposible imputar |

## Ejemplo de Tabla de Resultados

```markdown
| Estación | N | Media (m) | Desv.Est (m) | Mejor Distribución | R² | Estado |
|----------|---|-----------|--------------|-------------------|-----|--------|
| Calamar | 21,434 | 5.263 | 1.698 | Weibull | 0.976 | ✅ |
```

## Ubicación de Archivos

Guardar informes en: `docs/informe_cuenta_cobro_[MES]_[AÑO].md`

Ejemplos:
- `docs/informe_cuenta_cobro_febrero_2026.md`
- `docs/informe_cuenta_cobro_marzo_2026.md`
- `docs/informe_cuenta_cobro_abril_2026.md`

## Sección 4: Ejecución Contractual (Resumen Corto)

Además del informe detallado, se debe generar una **versión resumida** de máximo 3 párrafos para la sección "4. Ejecución Contractual" del documento de cuenta de cobro.

### Formato de la Sección 4:

```markdown
# 4. Ejecución Contractual

Se relaciona a continuación las actividades realizadas por el contratista durante el plazo de la ejecución del contrato

| Obligación contractual | Descripción |
|------------------------|-------------|
| 1. Procesamiento y análisis de información SIG y registros hidrológicos históricos asociado a la cuenca del río Magdalena | [Párrafo 1: Descripción general del trabajo realizado durante el mes, incluyendo el objetivo principal y alcance general. Mencionar metodología o sistema desarrollado si aplica.] |
| | [Párrafo 2: Detalle cuantitativo del trabajo: registros procesados, figuras generadas, estaciones trabajadas, métricas clave. Describir los entregables técnicos principales.] |
| | [Párrafo 3: Productos entregables específicos (scripts, archivos, documentación), su propósito y cómo contribuyen a las siguientes etapas del proyecto.] |
```

### Ejemplo (Marzo 2026):

> Durante el tercer mes del proyecto, se desarrolló e implementó el Sistema de Imputación de Datos Faltantes v3.0 para las 18 estaciones hidrométricas del río Magdalena, representando una actualización metodológica significativa respecto al sistema utilizado en el mes anterior. El nuevo sistema implementa una estrategia de tres niveles jerárquicos que permitió imputar 39,611 valores faltantes con alta confiabilidad, alcanzando una cobertura promedio del 94.13% en las series procesadas.

> Para ello se procesaron 326,480 registros históricos correspondientes al periodo 1967-2026, generando 26 figuras técnicas distribuidas en 15 curvas altura-altura individuales, 10 figuras de análisis por estación y un esquema del sistema de imputación. Se establecieron 15 modelos aceptados bajo el criterio de calidad R² ≥ 0.75, validando la robustez de la metodología implementada.

> Los entregables del mes incluyen el código fuente de tres scripts automatizados, archivos CSV con datos imputados completos y tablas resumen, así como la documentación técnica correspondiente a las secciones 5 y 6 del informe principal, sentando las bases para análisis hidrológicos de frecuencia y tendencias en las etapas siguientes del proyecto.

### Ubicación de Archivos:

- Informe detallado: `docs/informe_cuenta_cobro_[MES]_[AÑO].md`
- Resumen ejecución contractual: `docs/resumen_ejecucion_contractual_[MES]_[AÑO].md`

## Checklist Pre-entrega

Antes de finalizar un informe, verificar:

- [ ] Datos contractuales correctos (BPIN, contrato, contratista)
- [ ] Periodo especificado correctamente
- [ ] Todas las obligaciones del mes incluidas
- [ ] **Sección 4: Ejecución Contractual generada (3 párrafos máximo)**
- [ ] Tablas con encabezados claros
- [ ] Unidades de medida especificadas
- [ ] Rutas de archivos correctas
- [ ] Fechas de elaboración actualizadas
- [ ] Notas de seguimiento incluidas si aplica
- [ ] Resumen estadístico completo
- [ ] Próximos pasos identificados

## Referencias

- Contrato: UN-OJ-2025-66227
- BPIN: 2024000100122
- Informe modelo: `docs/informe_cuenta_cobro_marzo_2026_FUSIONADO.md`
