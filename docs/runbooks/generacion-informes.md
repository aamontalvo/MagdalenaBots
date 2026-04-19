# Runbook: Generación de Informes Técnicos

## Objetivo
Generar el informe técnico completo con análisis de niveles del Río Magdalena.

## Pre-requisitos

1. Datos Excel del IDEAM en: `data/raw/SERIE NIVELES IDEAM A 2026/`
2. Python 3.12+ instalado
3. Dependencias instaladas: `pip install -r requirements.txt`

## Procedimiento

### Paso 1: Verificar Datos de Entrada

```bash
# Verificar que existen los 18 archivos Excel
ls "data/raw/SERIE NIVELES IDEAM A 2026/"
```

Deben existir:
- ARMENIA_25027360.xlsx
- BARBOSA_25027530.xlsx
- CALAMAR_29037020.xlsx
- ... (18 archivos en total)

### Paso 2: Ejecutar Análisis Completo

```bash
python src/analysis/ideam_levels_analysis.py
```

**Salida esperada:**
```
======================================================================
ANALISIS DE NIVELES IDEAM - RIO MAGDALENA
======================================================================

[1/5] Cargando datos...
[2/5] Calculando cobertura...
[3/5] Generando heatmap...
[4/5] Generando boxplot...
[5/5] Generando tablas...
[6/6] Actualizando documento Word...

======================================================================
PROCESO COMPLETADO
======================================================================
```

### Paso 3: Verificar Salidas Generadas

#### Figuras
- `informes/figuras/Figura_2_1_Heatmap_Cobertura.png`
- `informes/figuras/Figura_3_1_Boxplot_Estaciones.png`

#### Tablas
- `informes/tablas/Tabla_2_1_Cobertura_Estaciones.csv`
- `informes/tablas/Tabla_3_1_Estadisticas_Estaciones.csv`

#### Documento Word
- `informes/INFORME_NIVELES_IDEAM_2026.docx` ← **Actualizado automáticamente**

### Paso 4: Revisión Manual

1. Abrir `informes/INFORME_NIVELES_IDEAM_2026.docx`
2. Verificar que las figuras se insertaron correctamente
3. Revisar que las tablas estén completas
4. Comprobar formato de números (3 decimales)

## Solución de Problemas

### Error: "No se encontraron archivos Excel"
**Causa:** Los datos no están en la ruta esperada.
**Solución:** Verificar que los archivos están en `data/raw/SERIE NIVELES IDEAM A 2026/`

### Error: "python-docx no encontrado"
**Causa:** Falta instalar dependencias.
**Solución:** Ejecutar `pip install python-docx`

### Las figuras no se actualizan
**Causa:** El script no está sobrescribiendo los archivos.
**Solución:** Verificar permisos de escritura en `informes/figuras/`

## Notas Importantes

⚠️ **NO MODIFICAR** `informes/INFORME_NIVELES_IDEAM_2026.docx` manualmente sin consultar, ya que el script lo sobrescribe.

## Verificación de Calidad

### Checklist Post-Ejecución

- [ ] Heatmap muestra las 18 estaciones
- [ ] Boxplot tiene 18 cajas en orden correcto
- [ ] Zonificación visible (líneas discontinuas)
- [ ] Tablas tienen formato UTF-8 correcto
- [ ] Documento Word abre sin errores
- [ ] Figuras están en alta resolución (300 DPI)

## Referencias

- Código de análisis: `src/analysis/ideam_levels_analysis.py`
- Zonificación: `src/analysis/ZONIFICACION_ESTACIONES.md`
- Documento principal: `informes/INFORME_NIVELES_IDEAM_2026.docx`
