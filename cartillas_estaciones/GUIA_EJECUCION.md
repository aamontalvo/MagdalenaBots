# Guía de Ejecución - Sistema de Validación

## Método 1: Ejecutar con Doble Click (Windows) 🖱️

1. Abre la carpeta `cartillas_estaciones`
2. Haz **doble click** en el archivo: **`EJECUTAR_VALIDACION.bat`**
3. Espera ~3-5 minutos
4. Revisa los resultados en la carpeta `resultados/`

---

## Método 2: Línea de Comandos 💻

### Windows (PowerShell):
```powershell
cd cartillas_estaciones
python validar_estaciones.py
python generar_visualizacion_validacion.py
```

### Windows (CMD):
```cmd
cd cartillas_estaciones
python validar_estaciones.py
python generar_visualizacion_validacion.py
```

### Linux/Mac:
```bash
cd cartillas_estaciones
python3 validar_estaciones.py
python3 generar_visualizacion_validacion.py
```

---

## Método 3: Jupyter Notebook 📓

```bash
cd cartillas_estaciones
jupyter notebook validar_estaciones_problema.ipynb
```

Luego en el notebook:
1. Menú **Cell** → **Run All**
2. Espera ~3 minutos
3. Revisa las figuras que se muestran inline

---

## 📁 Archivos que se Generarán

### Reportes:
- `resultados/validacion_imputacion_problemas.md` - Reporte completo en Markdown
- `resultados/periodos_problematicos.csv` - Tabla con fechas de problemas

### Figuras:
- `resultados/Validacion_Resumen_Todas_Estaciones.png` - Todas las estaciones en una figura
- `resultados/Validacion_Detallada_COYONGAL.png` - Análisis detallado
- `resultados/Validacion_Detallada_RIO_NUEVO.png` - Análisis detallado
- `resultados/Validacion_Detallada_LAS_PALOMAS.png` - Análisis detallado
- `resultados/Validacion_Detallada_ARMENIA.png` - Análisis detallado
- `resultados/Validacion_Detallada_GAMARRA_AUT.png` - Análisis detallado

---

## 🔧 Requisitos

- Python 3.8 o superior
- Librerías: pandas, numpy, matplotlib, scipy

### Instalar librerías (solo una vez):
```bash
pip install pandas numpy matplotlib scipy
```

---

## ⚠️ Solución de Problemas

### "Python no está instalado"
→ Descarga Python desde https://python.org

### "No module named pandas"
→ Ejecuta: `pip install pandas numpy matplotlib scipy`

### "No se encuentra el archivo de datos"
→ Verifica que exista: `cartillas_estaciones/datos/processed/Datos_Imputados_v3.csv`

---

## 🎯 Qué Hace el Sistema

1. **Carga los datos** de las 5 estaciones problemáticas
2. **Aplica 3 filtros** de validación hidrológica
3. **Detecta anomalías** (picos, saltos, inconsistencias)
4. **Genera reporte** con tabla de periodos problemáticos
5. **Crea figuras** con los flags marcados en rojo/naranja

---

**Fecha:** Marzo 2026  
**Versión:** 1.0
