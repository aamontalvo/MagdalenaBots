# Arquitectura del Sistema MagdalenaBot

## Visión General

MagdalenaBot es un sistema de procesamiento de datos hidrológicos con las siguientes capas:

```
┌─────────────────────────────────────────────────────────────┐
│                    CAPA DE PRESENTACIÓN                     │
│              (Informes Word, Figuras, Tablas)               │
└─────────────────────────────────────────────────────────────┘
                              ↑
┌─────────────────────────────────────────────────────────────┐
│                   CAPA DE ANÁLISIS                          │
│  (Estadísticas, Visualizaciones, Detección de outliers)     │
└─────────────────────────────────────────────────────────────┘
                              ↑
┌─────────────────────────────────────────────────────────────┐
│                   CAPA DE PROCESAMIENTO                     │
│     (Transformación Wide→Long, Limpieza, Validación)        │
└─────────────────────────────────────────────────────────────┘
                              ↑
┌─────────────────────────────────────────────────────────────┐
│                    CAPA DE DATOS                            │
│            (Archivos Excel IDEAM - Raw Data)                │
└─────────────────────────────────────────────────────────────┘
```

## Componentes Principales

### 1. Módulo de Procesamiento de Datos

**Archivo:** `src/analysis/ideam_levels_analysis.py`

**Funciones:**
- Carga de archivos Excel en formato wide
- Transformación a formato long
- Cálculo de cobertura de datos
- Generación de estadísticas descriptivas

**Flujo de datos:**
```
Excel (wide: filas=días, cols=años) 
    ↓
DataFrame long (fecha | estación | cota | año | mes | día)
    ↓
Análisis estadístico
```

### 2. Módulo de Visualización

**Funciones:**
- `create_coverage_heatmap()` - Mapa de calor de cobertura
- `create_boxplot_by_station()` - Diagramas de caja por estación

**Convenciones visuales:**
- **Boxplots:** Escala de grises (sin colores)
- **Heatmap:** Blues_r (azul oscuro = mejor cobertura)
- **Líneas de zona:** Discontinuas negras verticales

### 3. Módulo de Generación de Informes

**Integración con python-docx:**
- Inserción de figuras en documentos Word
- Creación de tablas formateadas
- Mantenimiento de estilos consistentes

## Flujo de Datos

```mermaid
Input (Excel IDEAM)
    ↓
[Load] → Validación de formato
    ↓
[Transform] → Wide a Long
    ↓
[Process] → Cálculo de estadísticas
    ↓
[Visualize] → Generación de figuras
    ↓
[Report] → Documento Word
```

## Convenciones de Datos

### Formato de Entrada (Excel)
- **Filas:** Días del año (1-366)
- **Columnas:** Años (1967-2026)
- **Primera columna:** Fecha de referencia
- **Últimas columnas:** Estadísticas (Max, Prom, Min, percentiles)

### Formato de Procesamiento (Long)
```
date        | station    | level | year | month | day
2023-01-01  | CALAMAR    | 5.23  | 2023 | 1     | 1
2023-01-01  | TENERIFE   | 8.94  | 2023 | 1     | 1
```

## Zonificación

La zonificación sigue criterios hidrológicos:

| Zona | Criterio | Estaciones |
|------|----------|------------|
| Baja | Aguas abajo del Cauca | 7 estaciones |
| Media | Aguas arriba del Cauca | 6 estaciones |
| Alta | Tramo alto del Magdalena | 5 estaciones |

## Dependencias

### Python
- pandas: Manipulación de datos
- matplotlib/seaborn: Visualización
- openpyxl: Lectura de Excel
- python-docx: Generación de informes

### Datos
- IDEAM Series de Niveles 1967-2026
- 18 estaciones hidrométricas

## Consideraciones de Diseño

1. **Formato único de análisis:** Se mantiene un solo archivo de análisis (`ideam_levels_analysis.py`) con versiones antiguas archivadas
2. **No duplicación de datos:** Los datos raw no se modifican, se procesan en memoria
3. **Separación de concerns:** Análisis, visualización y generación de informes son módulos independientes
4. **Documentación viva:** La zonificación se documenta tanto en código como en Markdown
