# 📊 Cartillas de Estaciones - Río Magdalena

## Guía de Usuario Paso a Paso

---

## 🎯 ¿Qué es esto?

Este folder contiene todo lo necesario para **generar automáticamente 5 figuras técnicas** de cualquier estación hidrométrica del Río Magdalena.

**No necesitas saber programar.** Solo sigue estos pasos.

---

## 📁 Estructura del Folder

```
cartillas_estaciones/
├── 📖 generar_cartilla.ipynb    ← ABRE ESTE ARCHIVO (doble click)
├── 📂 datos/
│   └── processed/
│       └── Datos_Imputados_v3.csv    ← Datos de todas las estaciones
├── 📂 resultados/                 ← Aquí aparecerán tus figuras
├── 🔧 funciones/
│   └── graficador.py             ← Código (no lo abras)
└── 📄 README.md                  ← Este archivo
```

---

## 🚀 Instrucciones Rápidas (3 Pasos)

### PASO 1: Abrir el Notebook

1. Abre **Jupyter Notebook**
2. Navega a esta carpeta (`cartillas_estaciones`)
3. Haz **doble click** en `generar_cartilla.ipynb`

### PASO 2: Escribir el Nombre de la Estación

1. En la primera celda de código, verás esta línea:
   ```python
   NOMBRE_ESTACION = 'CALAMAR'
   ```

2. **Cambia** `'CALAMAR'` por el nombre de tu estación (mantén las comillas)
   
   ✅ Ejemplos válidos:
   - `'BARBOSA'`
   - `'RIO_NUEVO'`
   - `'LAS_AGUADAS'`
   - `'TENERIFE'`

   ⚠️ **Importante:** Escribe en MAYÚSCULAS y usa guión bajo `_` si tiene espacios.

### PASO 3: Ejecutar

1. Ve al menú **`Cell`** → **`Run All`**
2. Espera 1-2 minutos
3. ¡Listo! Revisa la carpeta `resultados/`

---

## 📋 Lista de Estaciones Disponibles

### Zona Baja
- CALAMAR
- BARBOSA
- TENERIFE
- PLATO
- MAGANGUE
- COYONGAL
- SAN_PEDRITO

### Zona Media
- RIO_NUEVO
- LAS_PALOMAS
- LAS_AGUADAS
- EL_BANCO
- PEÑONCITO
- ARMENIA

### Zona Alta
- LA_GLORIA
- EL_CONTENTO
- SITIO_NUEVO
- PUERTO_WILCHES
- GAMARRA_AUT

---

## 🖼️ Figuras que se Generan

| Figura | Descripción |
|--------|-------------|
| **Fig1** | Serie de tiempo de cotas (toda la historia) |
| **Fig2** | Comportamiento mensual multianual (violinplots) |
| **Fig3** | Curva de duración (frecuencia de niveles) |
| **Fig4** | Curvas de frecuencias de cotas excedidas |
| **Fig5** | Ajuste de distribuciones de probabilidad |

---

## ⚠️ Solución de Problemas

### "Estación no encontrada"
→ Verifica que escribiste el nombre **exactamente** igual (mayúsculas, guiones bajos)

### "No module named pandas"
→ Instala las librerías. En el notebook hay una celda para esto (última sección)

### No aparecen las figuras
→ Revisa que tengas permisos de escritura en la carpeta `resultados/`

---

## 💡 Consejos

- **Para otra estación:** Vuelve al Paso 2, cambia el nombre y ejecuta de nuevo
- **Las figuras no se borran:** Cada estación genera sus propios archivos
- **Calidad:** Todas las figuras se guardan en alta resolución (300 DPI)

---

## 🔍 Validación de Imputación (NUEVO)

Si detectas **picos o saltos extraños** en las series de tiempo, usa el sistema de validación:

### Ejecutar Validación

```bash
python validar_estaciones.py
```

O abre el notebook: **`validar_estaciones_problema.ipynb`**

### Estaciones con Problemas Conocidos

- **COYONGAL**: Saltos menores en fronteras de gaps
- **RIO_NUEVO**: Extrapolación fuera de rango de calibración
- **LAS_PALOMAS**: Discontinuidades propagadas desde donante
- **ARMENIA**: Sin donante confiable (confluencia con Cauca)
- **GAMARRA_AUT**: Serie corta, correlaciones bajas

### Filtros de Detección

1. **Velocidad de Cambio**: Detecta cambios diarios anómalos
2. **Coherencia Espacial**: Valida correlación con vecinas
3. **Continuidad de Fronteras**: Detecta saltos en límites de gaps

Ver documento completo: **`README_VALIDACION.md`**

Reporte de problemas: **`resultados/validacion_imputacion_problemas.md`**

---

## 🔍 Validación RÁPIDA - Todas las Estaciones (NUEVO)

Si sospechas que **varias estaciones** tienen problemas (outliers, saltos en curvas, Q-Q plots desviados):

### Ejecutar Validación LIGHT

```bash
python validar_todas_estaciones_light.py
```

### Qué detecta (en 4 checks):

1. **Outliers**: Valores fuera de rango usando IQR
2. **Saltos en Curvas**: Detecta picos/valles artificiales (como el de Armenia)
3. **Ajuste de Distribución**: Verifica Q-Q plots (Weibull)
4. **Rangos Mensuales**: Meses con comportamiento atípico

### Resultado:

Clasifica cada estación como:
- ✅ **OK**: Sin problemas detectados
- ⚠️ **WARNING**: Problemas menores, revisar
- 🔴 **CRITICAL**: Problemas graves, posible re-imputación

### Archivos generados:
- `resultados/validacion_light_todas_estaciones.md` - Reporte completo

Ver análisis de problemas visuales: **`ANALISIS_PROBLEMAS_VISUALES.md`**

---

## 📞 Soporte

Si tienes dudas, revisa el notebook `generar_cartilla.ipynb` que tiene instrucciones detalladas en cada sección.

**Versión:** Marzo 2026  
**Proyecto:** Río Magdalena - IDEAM

**Responsable:** Alexander Alberto Montalvo Molina  
**Contrato:** UN-OJ-2025-66227
