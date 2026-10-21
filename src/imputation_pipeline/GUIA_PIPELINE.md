# Guia del Pipeline de Imputacion H-H (2 Pasos)

## Version
**v2.0** — Pipeline L1 + L2 (sin missForest)

---

## Que hace este pipeline?

Recibe datos crudos de niveles hidrometricos en **formato long** (`station, level, date`) y:

1. **Descubre automaticamente** todas las curvas Altura-Altura (H-H) posibles entre estaciones.
2. **Selecciona la mejor donante** para cada estacion objetivo (mayor R2 >= 0.75).
3. **Imputa** los datos faltantes en cascada:
   - **L1**: Interpolacion local ponderada (gaps <= 3 dias)
   - **L2**: Regresion cuadratica H-H usando la mejor donante aguas arriba
4. **Aplica hard rules**: ningun valor imputado puede salirse del rango historico original.
5. **Genera tracking**: cada valor sabemos si es original, L1 o L2.
6. **Exporta** el dataset final con todos los metadatos.

**NO usa missForest (L3)**. El pipeline es rapido (ambos pasos < 15 segundos).

---

## Estructura de archivos

```
src/imputation_pipeline/
|-- config.py              # Constantes y orden geografico
|-- loaders.py             # Carga CSV crudo -> DataFrame long/wide
|-- hh_selector.py         # Descubre y selecciona modelos H-H
|-- imputers.py            # L1 (interpolacion) y L2 (H-H cuadratica)
|-- hard_rules.py          # Restricciones de rango historico
|-- tracker.py             # Rastrea metodo de cada valor imputado
|-- pipeline.py            # Orquestador completo (opcional, para usar como libreria)
|-- run_hh_discovery.py    # PASO 1: Descubre modelos H-H
|-- run_imputation.py      # PASO 2: Aplica L1 + L2 y exporta
|-- GUIA_PIPELINE.md       # Este documento
```

---

## Formato de entrada

CSV con columnas (nombres configurables en `config.py`):

```csv
station,level,date
SAN_PEDRITO,8.523,01-01-1960
SAN_PEDRITO,8.512,02-01-1960
CALAMAR,6.891,01-01-1960
...
```

- `station`  : nombre de la estacion (string)
- `level`    : cota en metros (float)
- `date`     : fecha en formato `%d-%m-%Y`

---

## Paso 1: Descubrimiento de modelos H-H

### Para que sirve?
Genera automaticamente todas las parejas posibles donde una estacion "donante" esta **aguas arriba** de una estacion "objetivo", entrena una regresion cuadratica para cada pareja, calcula R2, y selecciona la **mejor donante** por estacion (si supera R2 >= 0.75).

### Como ejecutar?

```bash
py -m src.imputation_pipeline.run_hh_discovery
```

### Antes de ejecutar
Edita estas dos lineas al inicio del script:

```python
DATA_PATH  = r"C:\ruta\a\Resumen_Crudos_IDEAM_2026.csv"
OUTPUT_DIR = r"C:\ruta\a\pipeline_output"
```

### Salidas generadas

| Archivo | Descripcion |
|---------|-------------|
| `Tabla_Modelos_HH.csv` | Todas las parejas evaluadas (153 parejas para 18 estaciones) |
| `Tabla_Modelos_HH_Seleccionados.csv` | Solo las mejores (tipicamente 10-12 modelos) |

### Ejemplo de salida

```
[HH] Modelos seleccionados: 12
     [OK] BARBOSA      <- COYONGAL      : R2=0.8768, n=12148
     [OK] CALAMAR      <- MAGANGUE      : R2=0.9763, n=15746
     [OK] COYONGAL     <- LAS_AGUADAS   : R2=0.8790, n=15316
     [OK] EL_BANCO     <- PENONCITO     : R2=0.8390, n=16638
     [OK] EL_CONTENTO  <- PUERTO_WILCHES: R2=0.7641, n=6572
     [OK] LAS_AGUADAS  <- EL_BANCO      : R2=0.9791, n=18103
     [OK] LAS_PALOMAS  <- EL_BANCO      : R2=0.9258, n=15278
     [OK] MAGANGUE     <- BARBOSA       : R2=0.8987, n=12726
     [OK] RIO_NUEVO    <- LAS_AGUADAS   : R2=0.9165, n=13959
     [OK] SAN_PEDRITO  <- CALAMAR       : R2=0.9930, n=16310
     [OK] SITIO_NUEVO  <- PUERTO_WILCHES: R2=0.8134, n=6918
     [OK] TENERIFE     <- MAGANGUE      : R2=0.9606, n=12384
[HH] Estaciones SIN modelo H-H viable: ARMENIA, GAMARRA_AUT, LA_GLORIA, PENONCITO, PLATO, PUERTO_WILCHES
```

**Importante**: Revisa `Tabla_Modelos_HH_Seleccionados.csv` antes de continuar. Si alguna estacion critica no tiene modelo, puede ser porque no tiene donantes aguas arriba con datos concurrentes suficientes.

---

## Paso 2: Imputacion (L1 -> L2)

### Para que sirve?
Aplica la imputacion usando los modelos H-H ya descubiertos. Solo dos niveles:

- **L1**: Rellena gaps pequenos (<= 3 dias) con interpolacion local ponderada.
- **L2**: Rellena gaps grandes usando la curva H-H cuadratica con la mejor donante.

### Como ejecutar?

```bash
py -m src.imputation_pipeline.run_imputation
```

### Antes de ejecutar
Edita las mismas rutas que en el Paso 1. `OUTPUT_DIR` **debe ser el mismo** para que encuentre `Tabla_Modelos_HH_Seleccionados.csv`.

### Salidas generadas

| Archivo | Descripcion |
|---------|-------------|
| `Datos_Imputados.csv` | Dataset long final con tracking de metodo |
| `Resumen_Imputacion.csv` | Estadisticas por estacion (L1, L2, cobertura) |
| `log_imputacion.txt` | Log completo de la ejecucion |

### Columnas de `Datos_Imputados.csv`

```csv
Fecha,NombreEstacion,Cota,Nivel_Imputacion,Metodo
1960-01-01,SAN_PEDRITO,8.523,0,Original
1960-01-02,SAN_PEDRITO,8.512,0,Original
1960-01-03,SAN_PEDRITO,8.534,1,L1_Interpolacion
1960-01-10,SAN_PEDRITO,8.621,2,L2_HH_SAN_PEDRITO_quadratic
```

- `Nivel_Imputacion`:
  - `0` = Dato original (no imputado)
  - `1` = Imputado por L1 (interpolacion)
  - `2` = Imputado por L2 (curva H-H)
- `Metodo`: etiqueta legible del metodo usado

---

## Resumen del flujo de trabajo

```
Datos crudos (.csv)
       |
       v
+---------------------------+
| Paso 1: run_hh_discovery  |
|   Descubre modelos H-H    |
|   Genera CSVs de modelos  |
+---------------------------+
       |
       v
  Revisa modelos seleccionados
       |
       v
+---------------------------+
| Paso 2: run_imputation    |
|   L1: Interpolacion local |
|   L2: Curvas H-H          |
|   Hard rules              |
|   Tracking + exporta      |
+---------------------------+
       |
       v
Dataset final con tracking
```

---

## Customizacion

### Cambiar nombres de columnas de entrada

Edita `config.py`:

```python
INPUT_COL_STATION = 'station'   # o 'NombreEstacion', etc.
INPUT_COL_LEVEL   = 'level'     # o 'Cota', etc.
INPUT_COL_DATE    = 'date'      # o 'Fecha', etc.
INPUT_DATE_FORMAT = '%d-%m-%Y'  # o '%Y-%m-%d', etc.
```

### Cambiar umbrales

```python
R2_UMBRAL   = 0.75   # R2 minimo para aceptar modelo H-H
MIN_N_TRAIN = 50     # Minimo de puntos concurrentes para entrenar
L1_MAX_GAP  = 3      # Maximo gap en dias para interpolacion local
```

### Agregar/eliminar estaciones

Edita `GEO_ORDER` en `config.py`. La regla es:
- **Numero mas bajo** = mas aguas **abajo**
- **Numero mas alto** = mas aguas **arriba**

La donante debe estar aguas arriba del objetivo: `GEO_ORDER[donante] > GEO_ORDER[objetivo]`

### Estaciones descartadas

Las estaciones en `DESCARTADAS` se imputan pero no se exige cobertura 100%:

```python
DESCARTADAS = ['ARMENIA', 'TENERIFE', 'BARBOSA', 'SITIO_NUEVO']
```

---

## Uso como libreria (Python)

```python
from imputation_pipeline.pipeline import run_pipeline

# Ejecuta todo en una sola llamada
df_final, df_resumen = run_pipeline(
    data_path="datos.csv",
    output_dir="resultados/",
    date_format="%d-%m-%Y"
)
```

O en dos pasos separados (recomendado):

```python
from imputation_pipeline.loaders import load_raw_data
from imputation_pipeline.hh_selector import run_hh_discovery
from imputation_pipeline.imputers import apply_l1_interpolation, apply_l2_hh_imputation

# Paso 1: descubrir modelos
df_long = load_raw_data("datos.csv")
modelos, df_todas = run_hh_discovery(df_long)

# Revisar modelos...
# ...luego paso 2 con modelos validados
```

---

## Solucion de problemas

### "No se encontro Tabla_Modelos_HH_Seleccionados.csv"
Ejecuta primero `run_hh_discovery.py` o verifica que `OUTPUT_DIR` sea la misma carpeta en ambos scripts.

### "Estaciones SIN modelo H-H viable"
Normal para estaciones aguas arriba (como PUERTO_WILCHES) o con poca correlacion. Estas estaciones dependeran solo de L1 (interpolacion). Si una estacion critica no tiene modelo, revisa si tiene donantes con datos concurrentes.

### Timeout / tarda mucho
Con L3 (missForest) eliminado, ambos pasos deberian completarse en segundos. Si aun hay lentitud, revisa que no haya bucles infinitos en `apply_l1_interpolation` (verificar `L1_MAX_GAP` no sea excesivo).

### Valores fuera de rango
El pipeline aplica hard rules automaticamente (clip al rango historico). Si ves violaciones en el log, revisa los modelos H-H con R2 bajo cercano al umbral.

---

## Changelog

| Version | Cambios |
|---------|---------|
| v1.0    | Pipeline con L1 + L2 + L3 (missForest). Timeout frecuente. |
| v2.0    | Eliminado L3. Solo L1 + L2. Mas rapido, mas interpretable. |
