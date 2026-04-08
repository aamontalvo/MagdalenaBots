# MagdalenaBot v2.0 - Sistema de Análisis Hidrológico

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

> Sistema de análisis de niveles hidrométricos del Río Magdalena para generación de informes técnicos.

## 📋 Descripción

MagdalenaBot es una herramienta de análisis de datos hidrológicos que procesa series temporales de niveles del IDEAM (Instituto de Hidrología, Meteorología y Estudios Ambientales) y genera:

- **Análisis de calidad de datos:** Cobertura temporal, datos faltantes, valores atípicos
- **Estadísticas descriptivas:** Por estación y zonas geográficas
- **Visualizaciones:** Boxplots, heatmaps, curvas de duración
- **Informes técnicos:** Documentos Word con formato científico

## 🏗️ Estructura del Proyecto

```
MagdalenaBot/
├── CLAUDE.md                    # Contexto del proyecto para asistentes AI
├── README.md                    # Este archivo
├── requirements.txt             # Dependencias de Python
│
├── .claude/                     # Configuración de Claude Code
│   ├── settings.json           # Configuración de entorno
│   ├── hooks/                  # Automatizaciones y validaciones
│   └── skills/                 # Skills reutilizables
│       ├── data-analysis/
│       ├── scientific-writing/
│       └── hydrological-processing/
│
├── docs/                        # Documentación técnica
│   ├── architecture/           # Decisiones de arquitectura
│   ├── decisions/              # Registro de decisiones (ADR)
│   └── runbooks/               # Guías operacionales
│
├── src/                         # Código fuente
│   ├── analysis/               # Módulos de análisis
│   │   ├── ideam_levels_analysis.py
│   │   └── ZONIFICACION_ESTACIONES.md
│   ├── chat_engine/            # Motor de chat (legacy)
│   ├── data_connectors/        # Conectores de datos
│   └── utils/                  # Utilidades
│
├── tools/                       # Herramientas y scripts
│   ├── scripts/                # Scripts auxiliares
│   └── prompts/                # Prompts para análisis
│
├── data/                        # Datos del proyecto
│   ├── raw/                    # Datos crudos IDEAM
│   ├── processed/              # Datos procesados
│   └── figures/                # Figuras históricas
│
├── informes/                    # Documentos técnicos
│   ├── figuras/                # Figuras generadas
│   ├── tablas/                 # Tablas CSV
│   ├── INFORME_NIVELES_IDEAM_2026.docx
│   └── ESTRUCTURA INFORME.docx
│
└── archive/                     # Archivos históricos
    └── old_versions/           # Versiones antiguas de código
```

## 🚀 Instalación

### Requisitos
- Python 3.12 o superior
- Microsoft Word (para generación de informes)

### Instalación de dependencias

```bash
pip install -r requirements.txt
```

### Dependencias principales
```
pandas>=2.0.0
numpy>=1.24.0
matplotlib>=3.7.0
seaborn>=0.12.0
openpyxl>=3.1.0
python-docx>=0.8.11
```

## 📊 Uso

### Análisis Completo

Ejecutar el análisis completo de niveles IDEAM:

```bash
python src/analysis/ideam_levels_analysis.py
```

Este comando genera:
- Heatmap de cobertura de datos (`informes/figuras/Figura_2_1_Heatmap_Cobertura.png`)
- Boxplot por estación (`informes/figuras/Figura_3_1_Boxplot_Estaciones.png`)
- Tablas de estadísticas (`informes/tablas/`)
- Actualiza el documento Word del informe

### Estructura de Datos de Entrada

Los datos deben estar en:
```
data/raw/SERIE NIVELES IDEAM A 2026/
├── ARMENIA_25027360.xlsx
├── BARBOSA_25027530.xlsx
├── CALAMAR_29037020.xlsx
└── ... (18 archivos Excel)
```

Formato Excel: Wide format (filas=días, columnas=años)

## 🗺️ Zonificación de Estaciones

Las 18 estaciones se organizan geográficamente de aguas abajo hacia aguas arriba:

| Zona | Estaciones | # |
|------|-----------|---|
| **Baja** | San Pedrito, Calamar, Tenerife, Plato, Magangue, Barbosa, Coyongal | 7 |
| **Media** | Armenia, Rio Nuevo, Las Palomas, Las Aguadas, El Banco, Penoncito | 6 |
| **Alta** | La Gloria, Gamarra Aut, El Contento, Sitio Nuevo, Puerto Wilches | 5 |

Ver documentación detallada en: `src/analysis/ZONIFICACION_ESTACIONES.md`

## 📈 Salidas Generadas

### Figuras
- **Figura 2.1:** Mapa de calor de cobertura de datos (estación × año)
- **Figura 3.1:** Diagrama de cajas de cotas por estación (escala de grises)

### Tablas
- **Tabla 2.1:** Cobertura de datos por estación (% completitud)
- **Tabla 3.1:** Estadísticas descriptivas (n, media, std, min, max, percentiles)

### Informe Técnico
- **INFORME_NIVELES_IDEAM_2026.docx** - Documento principal con análisis completo

## 🛠️ Desarrollo

### Convenciones de Código
- Python 3.12+ con type hints
- Formato: 3 cifras decimales para cotas
- Orden geográfico obligatorio en visualizaciones
- Documentación en español

### Decisiones de Arquitectura
Ver: `docs/decisions/`

### Skills Disponibles
- **data-analysis:** Análisis de series temporales hidrológicas
- **scientific-writing:** Escritura técnica para informes
- **hydrological-processing:** Procesamiento de datos IDEAM

## 📝 Notas

- Los datos de Sitio Nuevo presentan una cota anómala (~50.67 msnm) por su ubicación en zona de remanso
- La estación Gamarra Aut es la única estación automática disponible
- Calamar es la estación con el registro más antiguo (desde 1967)

## 📄 Licencia

MIT License - Ver archivo LICENSE

## 👥 Contacto

Para consultas técnicas sobre el proyecto, revisar:
- `CLAUDE.md` - Contexto completo para asistentes AI
- `docs/architecture/` - Documentación de arquitectura
- `docs/runbooks/` - Guías operacionales
