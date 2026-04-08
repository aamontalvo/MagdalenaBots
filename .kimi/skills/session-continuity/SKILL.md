# Session Continuity - MagdalenaBot Project

## Estado Actual del Proyecto (Marzo 2026)

### Resumen de Actividades Realizadas

Este skill documenta el estado completo del proyecto de análisis hidrológico del Río Magdalena para permitir la continuación del trabajo en sesiones futuras sin pérdida de contexto.

---

## 1. ESTRUCTURA DE DIRECTORIOS

```
MagdalenaBot/
├── backend/
│   ├── data/
│   │   ├── raw/RawData/SERIE NIVELES IDEAM A 2026/    # Datos originales Excel
│   │   └── processed/imputation/                       # Datos imputados CSV
│   │       ├── Datos_Imputados_v3.csv                  # Serie completa (23.7 MB)
│   │       ├── Tabla_I1_Resumen_Imputacion_v3.csv      # Resumen por estación
│   │       └── Tabla_I2_Modelos_HH_v3.csv              # Modelos H-H aplicados
│   └── scripts/
├── docs/
│   ├── contenido-informe.md                            # Informe técnico principal
│   └── informe_cuenta_cobro_marzo_2026.md              # Resumen para cobro
├── informes/
│   ├── imputacion/                                     # Figuras H-H y esquemas
│   │   ├── Figura_5_1_Esquema_Imputacion.png
│   │   ├── Figura_HH_*_quadratic.png                   # 15 figuras H-H
│   │   └── Tablas CSV de resultados
│   └── estaciones/                                     # Figuras por estación
│       ├── CALAMAR/                                    # 5 figuras
│       └── BARBOSA/                                    # 5 figuras
└── src/analysis/
    ├── imputation_system_v3.py                         # Sistema de imputación
    ├── generate_station_figures.py                     # Generador de figuras
    └── generate_diagram.py                             # Generador de flujogramas
```

---

## 2. DATOS CLAVE DEL PROYECTO

### 2.1 Estaciones Procesadas (18 total)

| Estación | Zona | Cobertura | Estado | Mejor Modelo H-H |
|----------|------|-----------|--------|------------------|
| CALAMAR | Baja | 99.4% | ✅ Aprobada | Weibull (R²=0.976) |
| BARBOSA | Baja | 99.8% | ✅ Aprobada | Pearson III (R²=0.910) |
| TENERIFE | Baja | 99.9% | ✅ Aprobada | Weibull (R²=0.960) |
| PLATO | Baja | 100.0% | ✅ Aprobada | Weibull (R²=0.795) |
| MAGANGUE | Baja | 99.8% | ✅ Aprobada | Weibull (R²=0.976) |
| COYONGAL | Baja | 100.0% | ✅ Aprobada | Weibull (R²=0.883) |
| RIO NUEVO | Media | 98.7% | ✅ Aprobada | Weibull (R²=0.917) |
| LAS PALOMAS | Media | 98.1% | ✅ Aprobada | Weibull (R²=0.921) |
| LAS AGUADAS | Media | 99.6% | ✅ Aprobada | Weibull (R²=0.979) |
| EL BANCO | Media | 98.2% | ✅ Aprobada | Weibull (R²=0.981) |
| PEÑONCITO | Media | 98.4% | ✅ Aprobada | Weibull (R²=0.809) |
| LA GLORIA | Alta | 100.0% | ✅ Aprobada | Weibull (R²=0.824) |
| EL CONTENTO | Alta | 91.5% | ✅ Aprobada | Weibull (R²=0.763) |
| SITIO NUEVO | Alta | 95.4% | ✅ Aprobada | Weibull (R²=0.828) |
| PUERTO WILCHES | Alta | 99.2% | ✅ Aprobada | Weibull (R²=0.814) |
| ARMENIA | Media | 77.9% | ⚠️ Marginal | Sin modelo (sin donante) |
| GAMARRA_AUT | Alta | 93.0% | ❌ Excluida | Serie corta (2011-2023) |
| SAN PEDRITO | Baja | 45.4% | ❌ Excluida | Estación terminal |

### 2.2 Resultados de Imputación

- **Total registros procesados**: 326,480
- **Datos originales**: 261,055 (80.0%)
- **Imputados Nivel 1**: 970 valores
- **Imputados Nivel 2**: 38,641 valores
- **Cobertura promedio**: 94.13%

---

## 3. SCRIPTS Y FUNCIONALIDADES

### 3.1 imputation_system_v3.py
**Propósito**: Sistema completo de imputación de 3 niveles

**Características**:
- Nivel 1: Interpolación local para gaps ≤ 3 días
- Nivel 2: Curvas H-H comparando lineal vs cuadrático (R² ≥ 0.75)
- Nivel 3: Multi-donante para casos especiales
- Selección automática del mejor modelo por AIC

**Uso**:
```bash
cd src/analysis
py imputation_system_v3.py
```

**Salidas**: `backend/data/processed/imputation/`

### 3.2 generate_station_figures.py
**Propósito**: Generar figuras de análisis por estación

**Figuras generadas por estación**:
1. Fig1: Serie de tiempo de cotas (línea negra, grid secundario)
2. Fig2: Distribución mensual multianual (violinplot + boxplot + media)
3. Fig3: Curva de duración (percentiles vs cotas)
4. Fig4: Curvas de frecuencias de cotas excedidas (max/min gris, P50 punteado, 2025 azul)
5. Fig5: Ajuste de distribuciones PDF (top 3 por AIC + Q-Q plot)

**Distribuciones probadas**: Weibull, Log-Normal, Gamma, Gumbel, Pearson III, Normal

**Uso**:
```python
# En el script, modificar la lista de estaciones en main()
stations = ['CALAMAR', 'BARBOSA']  # Agregar más estaciones según necesidad

py generate_station_figures.py
```

**Salidas**: `informes/estaciones/[ESTACION]/`

### 3.3 generate_diagram.py
**Propósito**: Generar flujograma del sistema de imputación

**Uso**:
```bash
py generate_diagram.py
```

**Salida**: `informes/imputacion/Figura_5_1_Esquema_Imputacion.png`

---

## 4. DOCUMENTACIÓN TÉCNICA

### 4.1 Informe Principal
**Archivo**: `docs/contenido-informe.md`

**Secciones completadas**:
- Sección 5: Imputación de datos faltantes (3 niveles, metodología, resultados)
- Sección 6: Análisis por estación (Calamar y Barbosa con 5 figuras cada una)

### 4.2 Informe para Cobro
**Archivo**: `docs/informe_cuenta_cobro_marzo_2026.md`

**Contenido**: Resumen ejecutivo, detalle de actividades, estadísticas consolidadas

---

## 5. TAREAS PENDIENTES / PRÓXIMOS PASOS

### Prioridad Alta
1. **Generar figuras para estaciones restantes**
   - Actualmente solo Calamar y Barbosa tienen figuras completas
   - 16 estaciones adicionales necesitan generación de figuras
   - Modificar `generate_station_figures.py` lista de estaciones

2. **Validación de modelos H-H con R² < 0.75**
   - Revisar si hay estaciones que necesiten modelos alternativos
   - Considerar relajación de umbral para casos especiales

### Prioridad Media
3. **Análisis de tendencias**
   - Aplicar pruebas de Mann-Kendall a series completadas
   - Identificar puntos de cambio (Pettitt)
   - Generar figuras de tendencias por estación

4. **Análisis de frecuencia**
   - Calcular curvas de recurrencia para eventos extremos
   - Ajustar distribuciones Gumbel/Weibull para máximos anuales
   - Estimar niveles de diseño (Q5, Q10, Q50, Q100 años)

### Prioridad Baja
5. **Mejoras visuales**
   - Estandarizar colores entre figuras
   - Agregar mapa de ubicación de estaciones
   - Crear figuras comparativas entre zonas

---

## 6. PARÁMETROS TÉCNICOS IMPORTANTES

### Criterios de Calidad
- **R² mínimo para H-H**: 0.75
- **Correlación mínima donante**: r ≥ 0.85
- **Máximo gap Nivel 1**: 3 días
- **Mínimo años para análisis**: 30 años

### Configuración de Figuras
- **Colores serie tiempo**: Negro (único)
- **Colores violinplot**: Gris claro (#E0E0E0) con boxplot negro
- **Colores curvas excedidos**: Max/Min gris sólido, P50 gris punteado, 2025 azul (#0D47A1)
- **Distribuciones a probar**: Weibull, Log-Normal, Gamma, Gumbel, Pearson III, Normal
- **Criterio selección distribución**: Mínimo AIC

### Rutas Críticas
```python
# Datos procesados
DATA_PATH = 'backend/data/processed/imputation/Datos_Imputados_v3.csv'

# Figuras por estación
OUTPUT_FIGURES = 'informes/estaciones/[ESTACION]/'

# Datos raw
RAW_DATA = 'backend/data/raw/RawData/SERIE NIVELES IDEAM A 2026/'
```

---

## 7. COMANDOS RÁPIDOS

### Regenerar figuras para todas las estaciones
```bash
cd src/analysis
# Editar generate_station_figures.py -> stations = ['ESTACION1', 'ESTACION2', ...]
py generate_station_figures.py
```

### Verificar datos imputados
```python
import pandas as pd
df = pd.read_csv('backend/data/processed/imputation/Datos_Imputados_v3.csv')
print(df.groupby('station')['level'].count())
```

### Listar figuras generadas
```powershell
cd informes/estaciones
Get-ChildItem -Recurse *.png
```

---

## 8. NOTAS ADICIONALES

### Cambios Recientes Importantes
- ✅ Figura 1 (serie tiempo): Cambiada a línea negra única sin leyenda de colores
- ✅ Figura 4 (curvas excedidos): Max/Min en gris sólido, P50 punteado, solo 2025 en azul
- ✅ Todos los ejes Y cambiados de "Nivel" a "Cota (m.s.n.m.)"
- ✅ Grid secundario agregado a Figura 1

### Estaciones Requieren Atención Especial
- **Armenia**: Cobertura 77.9%, sin modelo H-H aceptable
- **San Pedrito**: Cobertura 45.4%, estación terminal sin donantes
- **Gamarra Aut**: Serie corta (2011-2023), excluida de análisis histórico

### Mejor Ajuste por Estación (Procesadas)
- **Calamar**: Weibull (AIC=83,050.49)
- **Barbosa**: Pearson III (AIC=75,233.45)
- **Mayoría**: Weibull es el mejor ajuste (13 de 15 estaciones)

---

## 9. CONTACTO Y REFERENCIAS

**Fecha de última actualización**: Marzo 2026
**Responsable**: Sistema de Análisis Hidrológico MagdalenaBot
**Versión del sistema**: v3.0

Para continuar el trabajo:
1. Verificar estado actual con `git status` o listando archivos
2. Revisar este skill para contexto completo
3. Ejecutar scripts según necesidad (ver sección 6)
