---
name: scientific-writing
description: Technical and scientific writing standards for hydrological and engineering reports. Use when drafting formal reports, documenting methodologies, describing data sources, presenting results, or writing technical interpretations. Ensures academic tone, proper formatting of numbers and units, structured sections, and professional figure/table captions.
---

# Scientific Writing for Technical Reports

Guidelines for producing formal technical-scientific documents in the hydrological and environmental engineering domain.

## Writing Tone and Style

### Voice
- Use **impersonal third person**: "Se analizaron los datos..." not "Analicé los datos..."
- **Passive voice acceptable** for scientific objectivity: "Los datos fueron procesados..."
- **Avoid colloquialisms** and informal expressions

### Tense
- **Past tense**: For describing work done ("Se recolectaron datos...")
- **Present tense**: For established facts and general truths ("Los niveles varían...")

## Number and Unit Formatting

### Significant Figures
- **Maximum 3 decimal places** for hydrological data: 4.334, 0.599, 12.3
- **Consistent precision** throughout tables and text

### Units
- Always specify units on first mention: "cotas (msnm)"
- Use standard abbreviations: msnm (metros sobre el nivel del mar), m³/s

### Large Numbers
- Use thousands separator: 1,250.450
- Scientific notation for very large/small: 1.25 × 10⁶

## Section Structure

### Section 2: Data Sources (Fuentes de Información)
```
2.1 Descripción de la base de datos
    - Tabla resumen: estaciones, códigos, periodo, n datos
    
2.2 Análisis de datos faltantes
    - Figura: Heatmap estación × año
    - Interpretación de patrones de cobertura
```

### Section 3: General Characteristics (Generalidades)
```
3.1 Estadísticas descriptivas
    - Tabla: n, media, mediana, desv. std, min, max, percentiles
    
3.2 Análisis de valores extremos
    - Figura: Boxplot por estación
    - Identificación de outliers potenciales
```

## Figure Guidelines

### Caption Format
```
Figura X. [Título descriptivo]. [Breve interpretación o nota metodológica relevante].
```

Example:
```
Figura 2. Mapa de calor de cobertura de datos por estación y año. 
El color azul indica porcentaje de datos faltantes; las celdas en gris 
corresponden a años anteriores al inicio de operación de cada estación.
```

### Figure Standards
- **Resolution**: 300 DPI minimum for print
- **Font size**: Readable when printed (minimum 8pt)
- **Color palette**: Accessible (consider colorblind users)
- **Axes labels**: Include units

## Table Guidelines

### Table Caption Format
```
Tabla X. [Título descriptivo].
```

### Column Alignment
- Text: Left-aligned
- Numbers: Right-aligned, decimal-aligned

### Example Structure
```
Tabla 1. Estadísticas descriptivas de cotas por estación.

| Estación | n    | Media | Mediana | Desv. Std | Mín.  | Máx.  |
|----------|------|-------|---------|-----------|-------|-------|
| Calamar  | 1523 | 5.234 | 5.150   | 1.234     | 2.100 | 8.900 |
```

## Common Phrases (Spanish)

### Describing Data
- "La serie de datos comprende el periodo..."
- "La estación cuenta con un registro de X años..."
- "Se observa una cobertura del X% para el año..."

### Statistical Descriptions
- "El valor promedio anual fue de X msnm..."
- "Los percentiles 10 y 90 evidencian..."
- "Se identificaron valores atípicos en..."

### Geographic References
- "Aguas abajo de la confluencia con el río Cauca..."
- "La estación se ubica en el tramo bajo/medio/alto..."

## References to Document Sections

- "Como se presenta en la sección X..."
- "Los resultados (Figura X) indican..."
- "De acuerdo con lo expuesto en la Tabla X..."

## Abbreviations

Define on first use:
- **msnm**: metros sobre el nivel del mar
- **IDEAM**: Instituto de Hidrología, Meteorología y Estudios Ambientales
- **P10, P90**: percentil 10, percentil 90

See [references/abbreviations.md](references/abbreviations.md) for complete list.
