# MagdalenaBot v3.0 - Índice Maestro del Proyecto

**Proyecto:** Análisis Hidrológico Río Magdalena  
**Contrato:** UN-OJ-2025-66227 | BPIN: 2024000100122  
**Responsable:** Alexander Alberto Montalvo Molina  
**Fecha de actualización:** Marzo 2026

---

## 🗺️ Estructura del Proyecto (Reorganizada)

```
MagdalenaBot/
│
├── 📁 .kimi/                          # Configuración Kimi
│   ├── skills/
│   │   ├── informes-mensuales/        # Skill para informes mensuales
│   │   ├── hydrological-processing/   # Procesamiento hidrológico
│   │   ├── scientific-writing/        # Escritura técnica
│   │   └── session-continuity/        # Continuidad de sesiones
│   └── settings.json
│
├── 📁 database/                       # Base de datos y modelos
│   ├── schema.sql                     # Esquema PostgreSQL
│   └── models.py                      # Modelos Python (Station, Measurement, etc.)
│
├── 📁 cartillas_estaciones/           # Generación de cartillas
│   ├── funciones/
│   │   ├── graficador.py              # Funciones de visualización
│   │   ├── validate_imputation.py     # Validación de imputación
│   │   └── validate_all_stations_light.py  # Validación ligera
│   ├── generar_cartilla.ipynb         # Notebook individual
│   ├── generar_cartilla_todas_estaciones.ipynb  # Notebook batch
│   ├── VALIDACION_VISUAL_COMPLETA.ipynb         # Validación visual
│   ├── validar_estaciones_problema.ipynb        # Validación problemas
│   ├── validar_todas_estaciones_light.py        # Script validación ligera
│   ├── generar_todas_estaciones_no_problematicas.py  # Script batch
│   └── resultados/                    # Subcarpetas por estación
│
├── 📁 workflows/                      # Workflows de integración
│   ├── integration_pipeline.py        # Pipeline completo
│   ├── magdalenabot_agent.json        # Configuración agente
│   └── magdalenabot_email_sender.json # Configuración email
│
├── 📁 docs/                           # Documentación
│   ├── informe_cuenta_cobro_marzo_2026_FUSIONADO.md
│   ├── DIAGNOSTICO_COMPLETO_SISTEMA_v3.md
│   ├── INFORME_TECNICO_VALIDACION_ESTACIONES.md
│   ├── architecture/
│   │   └── overview.md
│   ├── decisions/
│   │   └── ADR-001-zonificacion-estaciones.md
│   └── runbooks/
│       └── generacion-informes.md
│
├── 📁 backend/                        # Backend de procesamiento
│   ├── src/
│   │   ├── data_processing/
│   │   ├── models/
│   │   ├── config/
│   │   └── tests/
│   ├── scripts/                       # Scripts de procesamiento
│   └── data/
│       ├── raw/
│       └── processed/
│
├── 📁 src/                            # Código fuente principal
│   └── analysis/
│       ├── imputation_system_v3.py    # Sistema de imputación actual
│       ├── generate_station_figures.py
│       ├── generate_hh_figures.py
│       ├── generate_diagram.py
│       ├── hydrological_analyzer.py
│       ├── homogeneity_analysis.py
│       └── ZONIFICACION_ESTACIONES.md
│
├── 📁 database/                       # Esquema de base de datos
│   ├── schema.sql
│   └── models.py
│
├── 📁 Data/                           # Datos del proyecto
│   └── Niveles/
│
├── 📁 mcp/                            # MCP Server para n8n
│   └── n8n-magdalenaBot/
│
└── 📁 tools/                          # Herramientas auxiliares
    ├── prompts/
    └── scripts/
```

---

## 📊 Estado de Estaciones (Clasificación Final)

### ✅ EXCELLENT (4 estaciones) - Usar sin restricciones
- **CALAMAR** (Zona Baja) - 99.4% cobertura
- **BARBOSA** (Zona Baja) - 99.8% cobertura  
- **MAGANGUE** (Zona Baja) - 99.8% cobertura
- **EL_BANCO** (Zona Media) - 98.2% cobertura

### ⚠️ USABLE WITH CAUTION (8 estaciones) - Usar con precauciones
- **TENERIFE** - Excluir 2010-2012
- **LA GLORIA** - Excluir 2010-2012
- **SITIO NUEVO** - Excluir 2010-2012 + remanso
- **PUERTO_WILCHES** - Solo post-2003
- **PLATO** - Excluir primeros 2-3 años
- **LAS AGUADAS** - Excluir primeros 2 años
- **PEÑONCITO** - Excluir primeros 2 años
- **EL CONTENTO** - Excluir primeros 3 años

### ❌ EXCLUDE (6 estaciones) - No usar para análisis formal
- **ARMENIA** - Sin donante confiable
- **GAMARRA_AUT** - Serie corta (2013-2025)
- **SAN PEDRITO** - Terminal, imputación inviable
- **RIO NUEVO** - Extrapolación fuera de rango
- **LAS PALOMAS** - Dependencia crítica de donante
- **COYONGAL** - Saltos estructurales

---

## 🔄 Workflows Principales

### 1. Generación de Cartillas
```bash
cd cartillas_estaciones
python generar_todas_estaciones_no_problematicas.py
```
Genera figuras para 13 estaciones NO problemáticas en subcarpetas individuales.

### 2. Validación Visual
```bash
jupyter notebook cartillas_estaciones/VALIDACION_VISUAL_COMPLETA.ipynb
```
Validación visual interactiva de todas las estaciones.

### 3. Pipeline de Integración
```bash
python workflows/integration_pipeline.py
```
Pipeline completo: Validación → Imputación → Cartillas → Reporte

### 4. Validación Ligera (Todas las estaciones)
```bash
python cartillas_estaciones/validar_todas_estaciones_light.py
```
Detección automática de problemas visuales.

---

## 📄 Documentos Clave

| Documento | Ubicación | Descripción |
|-----------|-----------|-------------|
| **Informe Marzo 2026** | `docs/informe_cuenta_cobro_marzo_2026_FUSIONADO.md` | Informe técnico completo |
| **Diagnóstico Sistema** | `docs/DIAGNOSTICO_COMPLETO_SISTEMA_v3.md` | Clasificación estaciones |
| **Informe Técnico Validación** | `docs/INFORME_TECNICO_VALIDACION_ESTACIONES.md` | Análisis validación visual |
| **Guía Validación** | `cartillas_estaciones/README_VALIDACION.md` | Guía del sistema de validación |
| **Guía Generación Cartillas** | `cartillas_estaciones/GUIA_GENERAR_TODAS.md` | Guía generación masiva |
| **Guía Ejecución** | `cartillas_estaciones/GUIA_EJECUCION.md` | Guía de ejecución validación |

---

## 🗄️ Esquema de Base de Datos

### Tablas principales:
- `water_level_measurements` - Mediciones de nivel
- `stations` - Catálogo de estaciones con estado de calidad
- `imputation_models` - Modelos H-H calibrados
- `validation_results` - Resultados de validación automática

### Vistas:
- `station_summary` - Resumen por estación
- `station_quality_overview` - Vista de calidad

### Modelos Python:
- `Station` - Clase para estaciones
- `WaterLevelMeasurement` - Clase para mediciones
- `ImputationModel` - Clase para modelos H-H
- `ValidationResult` - Clase para validaciones

---

## 🎯 Próximos Pasos Prioritarios

### Inmediato (antes de abril 2026)
1. [ ] Verificar datos originales 2010-2012 en Tenerife, La Gloria, Sitio Nuevo, Puerto Wilches
2. [ ] Revisar primeros años de Plato, Las Aguadas, Peñoncito, El Contento
3. [ ] Actualizar metadatos de estaciones con exclusiones temporales

### Corto Plazo (abril-mayo 2026)
4. [ ] Implementar validación automática en pipeline
5. [ ] Re-imputar Río Nuevo con modelo lineal limitado
6. [ ] Generar cartillas faltantes de estaciones validadas

### Mediano Plazo (junio 2026)
7. [ ] Re-imputación de Coyongal con modelo diferente
8. [ ] Evaluar donantes alternativos para Las Palomas
9. [ ] Acumular datos Gamarra (meta: 20 años en 2033)

---

## 📞 Contacto

**Responsable:** Alexander Alberto Montalvo Molina  
**Proyecto:** Río Magdalena - IDEAM  
**Contrato:** UN-OJ-2025-66227
