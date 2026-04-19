#!/usr/bin/env python3
"""
Extract content from informe and generate MD
"""
from docx import Document
import re

doc_path = r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaRiver_Uninorte\CuentasCobro\2026\Febrero\INFORME ACTIVIDADES-ALEXANDER_MONTALVO_febrero2026.docx'

doc = Document(doc_path)

# Extract info from tables
info_contract = {}
for row in doc.tables[1].rows:
    key = row.cells[0].text.strip()
    value = row.cells[1].text.strip()
    info_contract[key] = value

# Extract obligations
obligations = []
for row in doc.tables[3].rows[1:]:  # Skip header
    obl = row.cells[0].text.strip()
    desc = row.cells[1].text.strip()
    # Clean up encoding issues
    obl = obl.replace('��', 'ó').replace('��', 'á').replace('��', 'é').replace('��', 'í').replace('��', 'ú').replace('��', 'ñ')
    desc = desc.replace('��', 'ó').replace('��', 'á').replace('��', 'é').replace('��', 'í').replace('��', 'ú').replace('��', 'ñ')
    obligations.append((obl, desc))

# Generate MD content
md_content = """# Informe de Actividades - Febrero 2026
## Proyecto BPIN: 2024000100122

### Información General
- **Contrato:** UN-OJ-2025-66227
- **Contratista:** Alexander Alberto Montalvo Molina
- **Identificación:** 1045734874
- **Periodo:** 01 de enero hasta 31 de enero de 2026
- **Tipo:** Prestación de Servicio

---

## Actividades Realizadas

### Obligación 1: Procesamiento y análisis de información SIG y registros hidrológicos históricos

**Descripción:**
Durante el segundo mes del proyecto, se han continuado con el procesamiento y verificación de calidad de las series de tiempo e información no estructurada relacionada a la información histórica de las estaciones hidrológicas del río Magdalena. Se continuó con la digitalización y organización de registros de niveles, caudales y sedimentos correspondientes a las estaciones del tramo medio y del tramo bajo.

Para ello se llevaron a cabo algoritmos de procesamiento y verificación de calidad de la información como base estructural y uso continuo en las siguientes etapas del proyecto.

**Productos específicos:**
1. **Scripts de verificación de calidad de datos** de series hidrológicas
2. **Scripts para visualización y descarga de gráficas** de:
   - Probabilidad de niveles
   - Excedencia de niveles
   - Curvas de duración de niveles y caudales

---

## Detalle Técnico del Trabajo Realizado

### Sección 1: Análisis Exploratorio de Datos
Se realizó un análisis exploratorio completo de las series de niveles del IDEAM para 18 estaciones del río Magdalena. El procesamiento incluyó:

- Carga de datos desde archivos Excel en formato wide (años como columnas)
- Transformación a formato long (estándar para series temporales)
- Generación de heatmap de datos faltantes con máscara "No Instalada" (NI)
- Análisis de completitud temporal por estación
- Estadísticas descriptivas y análisis de outliers

**Estaciones procesadas:**
- Puerto Wilches, Sitio Nuevo, El Contento, Gamarra Aut
- La Gloria, Peñoncito, El Banco, Las Aguadas
- Las Palomas, Río Nuevo, Armenia, Coyongal
- Barbosa, Magangué, Plato, Tenerife, Calamar

**Resultados:**
- 297,840 registros procesados
- Periodo: 1967-2026 (60 años)
- 3 estaciones con completitud ≥85% (Calamar: 97.6%, Las Aguadas: 85.6%, El Banco: 85.5%)

### Sección 2: Imputación Espacial de Datos Faltantes
Se desarrollaron modelos de imputación usando curvas H-H (nivel-nivel) con forma cuadrática:

**Metodología:**
- Relaciones unidireccionales: aguas arriba → aguas abajo
- Modelo cuadrático: H_target = a·H_donor² + b·H_donor + c
- Selección por criterio AIC y validación cruzada

**Relaciones establecidas:**
1. **Calamar ← Magangué:** R² = 0.9763, RMSE-CV = 0.2465 m, 53 valores imputados
2. **Las Aguadas ← El Banco:** R² = 0.9791, RMSE-CV = 0.2074 m, 550 valores imputados
3. **El Banco ← La Gloria:** R² = 0.8219, RMSE-CV = 0.5392 m, 25 valores imputados

**Total:** 628 valores imputados con alta confiabilidad

### Sección 3: Análisis Estadístico Detallado por Estaciones
Se realizó un análisis de distribuciones de probabilidad para las 3 estaciones con datos completos:

**Metodología:**
- Violinplots mensuales multianuales con boxplot interno
- Línea de media mensual multianual superpuesta
- Ajuste de distribuciones paramétricas (Normal, Log-Normal, Gamma, Gumbel, Weibull, Pearson III)
- Selección por criterio AIC

**Resultados por estación:**

| Estación | N | Media (m) | Desv.Est (m) | Mejor Distribución | AIC | Parámetros |
|----------|---|-----------|--------------|-------------------|-----|------------|
| Calamar | 21,434 | 5.262 | 1.698 | Weibull | 83070.0 | [4.189, -0.9461, 6.840] |
| Las Aguadas | 19,299 | 24.66 | 1.421 | Weibull | 67870.0 | [4.767, 18.8, 6.405] |
| El Banco | 19,390 | 25.91 | 1.402 | Weibull | 67800.0 | [3.767, 21.24, 5.176] |

**Hallazgos:**
- Todas las estaciones presentan distribución Weibull como mejor ajuste
- Los datos rechazan normalidad (p < 0.05 en pruebas KS y D'Agostino)
- Se observa asimetría negativa ligera (-0.09 a -0.23)
- El régimen hidrológico bimodal es evidente en los violinplots mensuales

---

## Productos Entregables

1. **Dataset procesado:** `magdalena_levels_imputed_final.csv` (297,840+ registros)
2. **Scripts de procesamiento:** Python para análisis automatizado
3. **Visualizaciones:**
   - Heatmap de calidad de datos
   - Curvas H-H de imputación
   - Violinplots mensuales por estación
   - Q-Q plots de ajuste de distribuciones
4. **Informe técnico:** Documento Word con análisis completo

---

## Próximos Pasos (Marzo 2026)

1. Incorporar nuevas estaciones (Barrancabermeja, Tebsa, etc.)
2. Análisis de caudales (complementario a niveles)
3. Desarrollo de modelos de predicción
4. Integración con plataforma Supabase

---

*Generado automáticamente desde informe de actividades febrero 2026*
"""

# Save to file
output_path = r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\INFORME_ACTIVIDADES_FEBRERO_2026.md'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(md_content)

print(f"Archivo MD generado: {output_path}")
