# Guía: Generar Cartillas para Todas las Estaciones NO Problemáticas

## ¿Qué hace esto?

Genera automáticamente las 5 figuras técnicas para las **13 estaciones NO problemáticas**, guardándolas en subcarpetas individuales.

## Estaciones que se generan (13):

### Zona Baja (6):
- CALAMAR ✅
- BARBOSA ✅
- TENERIFE ✅
- PLATO ✅
- MAGANGUE ✅
- SAN_PEDRITO ✅

### Zona Media (3):
- LAS_AGUADAS ✅
- EL_BANCO ✅
- PENONCITO ✅

### Zona Alta (4):
- LA_GLORIA ✅
- EL_CONTENTO ✅
- SITIO_NUEVO ✅
- PUERTO_WILCHES ✅

## Estaciones EXCLUIDAS (5 problemáticas):
- ❌ COYONGAL
- ❌ RIO_NUEVO
- ❌ LAS_PALOMAS
- ❌ ARMENIA
- ❌ GAMARRA_AUT

---

## Métodos de Ejecución

### Opción 1: Doble Click (Windows) 🖱️

1. Abre la carpeta `cartillas_estaciones`
2. Haz **doble click** en: **`GENERAR_TODAS_ESTACIONES.bat`**
3. Espera ~10-15 minutos
4. Revisa la carpeta `resultados/`

---

### Opción 2: Script Python 💻

```bash
cd cartillas_estaciones
python generar_todas_estaciones_no_problematicas.py
```

---

### Opción 3: Jupyter Notebook 📓

```bash
cd cartillas_estaciones
jupyter notebook generar_cartilla_todas_estaciones.ipynb
```

Luego: **Cell** → **Run All**

---

## Estructura de Resultados

```
resultados/
├── CALAMAR/
│   ├── Fig1_Serie_Tiempo_CALAMAR.png
│   ├── Fig2_Comportamiento_Mensual_CALAMAR.png
│   ├── Fig3_Curva_Duracion_CALAMAR.png
│   ├── Fig4_Curvas_Excedidos_CALAMAR.png
│   └── Fig5_Distribucion_Probabilidad_CALAMAR.png
├── BARBOSA/
│   └── ...
├── TENERIFE/
│   └── ...
├── PLATO/
│   └── ...
├── MAGANGUE/
│   └── ...
├── SAN_PEDRITO/
│   └── ...
├── LAS_AGUADAS/
│   └── ...
├── EL_BANCO/
│   └── ...
├── PENONCITO/
│   └── ...
├── LA_GLORIA/
│   └── ...
├── EL_CONTENTO/
│   └── ...
├── SITIO_NUEVO/
│   └── ...
└── PUERTO_WILCHES/
    └── ...
```

**Total: 13 carpetas × 5 figuras = 65 imágenes**

---

## Qué revisar en cada estación

### Figura 1 (Serie de tiempo):
- ✅ Sin picos/valles artificiales
- ✅ Sin saltos bruscos
- ✅ Continuidad razonable

### Figura 2 (Violinplots mensuales):
- ✅ Patrón estacional consistente
- ✅ Sin meses con rangos anómalos

### Figura 3 (Curva de duración):
- ✅ Curva suave sin saltos
- ✅ Sin picos en extremos (como el de Armenia)

### Figura 4 (Curvas excedidas):
- ✅ Líneas de percentiles coherentes
- ✅ Sin cruces extraños entre percentiles

### Figura 5 (Distribución + Q-Q plot):
- ✅ Q-Q plot cercano a línea 1:1
- ✅ Histograma con forma lógica

---

## Tiempo Estimado

- **Por estación:** ~1 minuto
- **Total (13 estaciones):** ~10-15 minutos

---

## Si encuentras problemas

Si alguna de estas estaciones "NO problemáticas" muestra errores visuales:

1. Revisa primero con el validador:
   ```bash
   python validar_todas_estaciones_light.py
   ```

2. Agrega la estación a la lista de problemáticas

3. Documenta el problema encontrado

---

**Fecha:** Marzo 2026
