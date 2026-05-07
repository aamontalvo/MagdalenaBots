# Plan de Verificacion Anti Data-Leakage - Imputacion v4.3

## Fecha: 07 de mayo de 2026
## Version: v4.3 (orientacion H-H corregida)

---

## 1. OBJETIVO

Verificar que la regeneracion del sistema de imputacion v4.3:
1. No introdujo data leakage (imputacion usando informacion futura o fuera de rango)
2. No altero los valores originales medidos
3. Mantuvo la coherencia hidrologica entre estaciones vecinas
4. Respeto el hard rule de no imputar fuera del rango original de cada estacion

---

## 2. VERIFICACIONES OBLIGATORIAS

### 2.1 Inmutabilidad de datos originales (Check #1)

**Proposito:** Asegurar que los valores originales medidos por el IDEAM no fueron modificados.

**Metodo:**
```python
import pandas as pd

orig = pd.read_csv('backend/data/processed/Resumen_Crudos_IDEAM_2026.csv')
v43  = pd.read_csv('backend/data/processed/imputation/Datos_Imputados_v4_3_Corrected.csv')

# Merge por estacion y fecha
merged = orig.merge(v43, left_on=['station','date'], right_on=['NombreEstacion','Fecha'], how='inner')

# Verificar que todos los valores originales coinciden exactamente
mismatches = merged[abs(merged['level'] - merged['Cota']) > 1e-6]
assert len(mismatches) == 0, f"ERROR: {len(mismatches)} valores originales fueron modificados"
```

**Criterio de aceptacion:** 0 discrepancias entre valores originales y v4.3.

---

### 2.2 Hard rule: No imputacion fuera de rango (Check #2)

**Proposito:** Verificar que no existen registros imputados fuera del rango temporal original de cada estacion.

**Metodo:**
```python
# Para cada estacion, obtener rango original
rangos = orig.groupby('station')['date'].agg(['min','max'])

# Verificar que v43 no tiene registros fuera de estos rangos
for est in v43['NombreEstacion'].unique():
    subset = v43[v43['NombreEstacion'] == est]
    rmin, rmax = rangos.loc[est]
    fuera_rango = subset[(subset['Fecha'] < rmin) | (subset['Fecha'] > rmax)]
    assert len(fuera_rango) == 0, f"ERROR: {est} tiene {len(fuera_rango)} registros fuera de rango"
```

**Criterio de aceptacion:** 0 registros fuera del rango original por estacion.

---

### 2.3 Orientacion H-H correcta (Check #3)

**Proposito:** Confirmar que todos los modelos H-H usan variables independientes aguas arriba.

**Metodo:**
```python
# Orden geografico: numero mayor = mas aguas arriba
geo_order = {
    'San Pedrito': 0, 'Calamar': 1, 'Tenerife': 2, 'Plato': 3, 'Magangue': 4,
    'Barbosa': 5, 'Coyongal': 6, 'Armenia': 7, 'Rio Nuevo': 8, 'Las Palomas': 9,
    'Las Aguadas': 10, 'El Banco': 11, 'Penoncito': 12, 'La Gloria': 13,
    'Gamarra Aut': 14, 'El Contento': 15, 'Sitio Nuevo': 16, 'Puerto Wilches': 17,
}

models = pd.read_csv('backend/data/processed/imputation/Tabla_Modelos_HH_v4_3.csv')
for _, row in models.iterrows():
    dep = row['Recipiente']
    ind = row['Independiente']
    assert geo_order[ind] > geo_order[dep], f"ERROR: {dep} <- {ind} viola orientacion"
```

**Criterio de aceptacion:** Todos los modelos cumplen orientacion hidrologica.

---

### 2.4 Coherencia de valores imputados (Check #4)

**Proposito:** Verificar que los valores imputados caen dentro de rangos fisicamente razonables.

**Metodo:**
```python
# Calcular percentiles 1% y 99% de datos originales por estacion
pct_orig = orig.groupby('station')['level'].quantile([0.01, 0.99]).unstack()

# Verificar que imputados no exceden estos percentiles ampliados en > 20%
for est in v43['NombreEstacion'].unique():
    if est not in pct_orig.index:
        continue
    p01, p99 = pct_orig.loc[est]
    margin = (p99 - p01) * 0.2
    subset = v43[(v43['NombreEstacion'] == est) & (v43['Nivel_Imputacion'] > 0)]
    outliers = subset[(subset['Cota'] < p01 - margin) | (subset['Cota'] > p99 + margin)]
    if len(outliers) > 0:
        print(f"ALERTA: {est} tiene {len(outliers)} imputados fuera de rango esperado")
```

**Criterio de aceptacion:** < 1 % de valores imputados fuera del rango esperado.

---

### 2.5 Ausencia de data leakage en entrenamiento (Check #5)

**Proposito:** Confirmar que los modelos H-H fueron entrenados SOLO con datos originales concurrentes, sin usar valores imputados.

**Metodo:**
```python
# Para cada modelo, verificar que el numero de puntos de entrenamiento coincide
# con el numero de datos originales concurrentes (no imputados)
for _, model in models.iterrows():
    dep = model['Recipiente']
    ind = model['Independiente']
    n_train = model['N_Entrenamiento']
    
    # Contar datos originales concurrentes
    orig_dep = orig[orig['station'] == dep].dropna()
    orig_ind = orig[orig['station'] == ind].dropna()
    concurrentes = orig_dep.merge(orig_ind, on='date', how='inner')
    n_concurrentes = len(concurrentes)
    
    assert n_train <= n_concurrentes, f"ERROR: {dep} <- {ind} usa {n_train} puntos pero solo hay {n_concurrentes} originales"
```

**Criterio de aceptacion:** n_train <= n_datos_originales_concurrentes para todos los modelos.

---

### 2.6 Cobertura 100% en estaciones no descartadas (Check #6)

**Proposito:** Verificar que las 14 estaciones no descartadas tienen 0 NaN.

**Metodo:**
```python
descartadas = ['Armenia', 'Tenerife', 'Barbosa', 'Sitio Nuevo']
for est in v43['NombreEstacion'].unique():
    if est in descartadas:
        continue
    n_nan = v43[v43['NombreEstacion'] == est]['Cota'].isna().sum()
    assert n_nan == 0, f"ERROR: {est} tiene {n_nan} NaN"
```

**Criterio de aceptacion:** 0 NaN en las 14 estaciones no descartadas.

---

### 2.7 Comparacion v4.2 vs v4.3 (Check #7)

**Proposito:** Identificar cambios significativos entre versiones.

**Metodo:**
```python
v42 = pd.read_csv('backend/data/processed/imputation/Datos_Imputados_v4_2_Complete.csv')
v43 = pd.read_csv('backend/data/processed/imputation/Datos_Imputados_v4_3_Corrected.csv')

# Comparar estadisticas descriptivas por estacion
stats_42 = v42.groupby('NombreEstacion')['Cota'].agg(['mean','std','min','max'])
stats_43 = v43.groupby('NombreEstacion')['Cota'].agg(['mean','std','min','max'])

# Calcular diferencia porcentual en media
diff = ((stats_43['mean'] - stats_42['mean']) / stats_42['mean'] * 100).abs()
for est, d in diff.items():
    print(f"{est}: cambio en media = {d:.2f}%")
    assert d < 5.0, f"ALERTA: {est} cambio > 5% en media"
```

**Criterio de aceptacion:** Cambio < 5% en media por estacion.

---

## 3. EJECUCION DEL PLAN

### Paso 1: Ejecutar checks 1-6 (automatizados)
```bash
cd "C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot"
uv run --with pandas --with scipy python src/analysis/verificacion_v4_3.py
```

### Paso 2: Revision manual de figuras (check visual)
- Generar cartillas actualizadas para 18 estaciones
- Verificar que Fig1 (serie tiempo) no muestra saltos bruscos en fechas de imputacion
- Verificar que Fig3 (curva duracion) mantiene forma suave

### Paso 3: Documentar resultados
- Guardar reporte de verificacion en `docs/VERIFICACION_v4_3.md`
- Incluir tablas de checks pasados/fallidos
- Incluir figuras comparativas v4.2 vs v4.3 si aplica

---

## 4. CRONOGRAMA SUGERIDO

| Paso | Duracion estimada | Responsable |
|------|-------------------|-------------|
| Checks 1-6 (scripts) | 30 min | Kimi / Alex |
| Revision visual figuras | 2-3 horas | Alex |
| Documentacion | 1 hora | Kimi / Alex |
| **Total** | **~4 horas** | |

---

## 5. NOTAS IMPORTANTES

1. **Data leakage mas critico a verificar**: El cambio de orientacion H-H (v4.2 -> v4.3) es una correccion estructural, no un error. Sin embargo, se debe verificar que los nuevos modelos NO usan informacion futura.

2. **San Pedrito**: Es la estacion mas aguas abajo. Su imputacion con Calamar (R² = 0.993) es robusta pero requiere verificacion visual adicional.

3. **Estaciones descartadas**: Aunque Armenia, Tenerife, Barbosa y Sitio Nuevo fueron completadas, su estado de "descartadas por homogeneidad" debe propagarse a todos los analisis posteriores.
