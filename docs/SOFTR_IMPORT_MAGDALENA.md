# Importación a Softr - Magdalena SGR

> **Estado:** tablas y campos creados. CSV de importación generados. Falta que Alex importe los CSV y defina el dominio público de las figuras.
> **Database Softr:** `Magdalena SGR`
> **ID:** `cdc45f86-e02c-4c19-8e65-5854d6e8a816`

## 1. Tablas creadas

| Tabla | ID | Rol | Filas a importar |
|---|---|---|---:|
| `Estaciones` | `p41nC54YeYb1xx` | Dimensión de 35 estaciones únicas | 35 |
| `Datasets` | `WHH130rI4R4TFc` | Linaje de datasets | 11 |
| `Metricas` | `KNnvfCOHVI2tm5` | Métricas cerradas | 42 |
| `Figuras` | `R3GZljNc81puzj` | Catálogo de 251 figuras | 251 |
| `Resumen_Niveles` | `PUETb4vvJHpzCZ` | Resumen por estación de niveles | 24 |
| `Resumen_Caudales` | `CbCKsHSztv701Q` | Resumen por estación de caudales | 14 |
| `Niveles` | `i3Tb4oVMxOrwUE` | Serie diaria de niveles | 394.772 |
| `Caudales` | `bscYMyyyPGRQ71` | Serie diaria de caudales | 299.239 |

Las tablas `Niveles` y `Caudales` ya existían; se les agregaron los campos de datos diarios. Conservan 3 registros vacíos cada una; Alex los borrará después.

## 2. Campos agregados a Niveles y Caudales

### Niveles
`Name` (primario), `station_code`, `station_name`, `date`, `value_m`, `data_source`, `method`, `dataset_id`.

### Caudales
`Name` (primario), `station_code`, `station_name`, `date`, `value_m3s`, `data_source`, `method`, `dataset_id`.

`Name` tiene el formato `station_code|date` y es único.
`data_source` toma `Original`, `Imputado` o `Faltante`.
El campo `AI Summary` existente no debería ejecutarse porque `Description` va vacío; si se activa, desactivarlo antes de importar las series diarias.

## 3. Paquete de importación

Carpeta:
`backend/entregables/softr_import/`

| Archivo | Tabla | Filas |
|---|---|---:|
| `estaciones.csv` | `Estaciones` | 35 |
| `datasets.csv` | `Datasets` | 11 |
| `resumen_niveles.csv` | `Resumen_Niveles` | 24 |
| `resumen_caudales.csv` | `Resumen_Caudales` | 14 |
| `metricas.csv` | `Metricas` | 42 |
| `figuras.csv` | `Figuras` | 251 |
| `niveles_diarios/part_01.csv` ... `part_08.csv` | `Niveles` | 394.772 |
| `caudales_diarios/part_01.csv` ... `part_06.csv` | `Caudales` | 299.239 |

Orden recomendado:
1. `Estaciones`
2. `Datasets`
3. `Resumen_Niveles`
4. `Resumen_Caudales`
5. `Metricas`
6. `Niveles` (8 partes)
7. `Caudales` (6 partes)
8. `Figuras`

## 4. Relaciones

- `Estaciones` 1:N `Resumen_Niveles` por `station_code`.
- `Estaciones` 1:N `Resumen_Caudales` por `station_code`.
- `Estaciones` 1:N `Niveles` por `station_code`.
- `Estaciones` 1:N `Caudales` por `station_code`.
- `Estaciones` 1:N `Figuras` por `station_code` (las figuras globales no tienen estación).
- `Datasets` 1:N `Niveles`, `Caudales` y `Figuras` por `dataset_id`.

Softr puede crear los vínculos nativos (`LINKED_RECORD`) después de importar, usando `station_code` como llave. El CSV ya incluye la llave en todas las tablas.

## 5. Figuras

- `figuras.csv` tiene 251 filas: 150 de niveles y 101 de caudales.
- La carpeta pública está en `backend/entregables/softr_import/figures_public/figures/`.
- El ZIP está en `backend/entregables/softr_import/figures_public.zip` (72,41 MB).
- `image_url` usa la base `https://PENDING_HOST`. Para activar las URLs:
  1. Subir `figures_public/figures/` a un dominio público.
  2. Definir `SOFTR_FIGURE_BASE_URL=https://tudominio.com`.
  3. Ejecutar:
     `py backend/scripts/caudales_v1/09_pack_figures_softr.py`
  4. Reimportar o actualizar `figuras.csv` en Softr.

Opciones de host:
- Dominio propio / Hostinger.
- Repo público solo de figuras (requiere autorización).
- ImgBB / UploadToURL (requiere conectar la app).

## 6. Scripts

- `backend/scripts/caudales_v1/08_export_softr_csvs.py` — genera todos los CSV.
- `backend/scripts/caudales_v1/09_pack_figures_softr.py` — empaqueta figuras y actualiza URLs/hashes.

## 7. Lo que falta

1. Importar los CSV en Softr en el orden indicado.
2. Definir el dominio público de las figuras y regenerar `figuras.csv`.
3. Verificar conteos en Softr:
   - `Estaciones` 35.
   - `Resumen_Niveles` 24.
   - `Resumen_Caudales` 14.
   - `Metricas` 42.
   - `Figuras` 251.
   - `Niveles` 394.772.
   - `Caudales` 299.239.
4. Borrar los 3 registros vacíos de `Niveles` y `Caudales`.
5. Opcional: crear los `LINKED_RECORD` nativos entre tablas.
