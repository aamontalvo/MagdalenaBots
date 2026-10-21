# Importación a Softr - Magdalena SGR

Database: `Magdalena SGR`
ID: `cdc45f86-e02c-4c19-8e65-5854d6e8a816`

## Orden de importación

1. `estaciones.csv` -> tabla `Estaciones` (35 filas).
2. `datasets.csv` -> tabla `Datasets` (11 filas).
3. `resumen_niveles.csv` -> tabla `Resumen_Niveles` (24 filas).
4. `resumen_caudales.csv` -> tabla `Resumen_Caudales` (14 filas).
5. `metricas.csv` -> tabla `Metricas` (42 filas).
6. `niveles_diarios/part_01.csv` ... `part_08.csv` -> tabla `Niveles` (394.772 filas).
7. `caudales_diarios/part_01.csv` ... `part_06.csv` -> tabla `Caudales` (299.239 filas).
8. `figuras.csv` -> tabla `Figuras` (251 filas).

## Notas de importación

- Codificación: UTF-8.
- Fechas: `YYYY-MM-DD`.
- Booleanos: `TRUE` / `FALSE`.
- El campo primario de `Niveles` y `Caudales` es `Name`; el valor es `station_code|date` y es único.
- `data_source` toma `Original`, `Imputado` o `Faltante`.
- Los 3 registros vacíos que ya existen en `Niveles` y `Caudales` se dejan; Alex los borrará después.
- Si el importador rechaza una parte por tamaño, dividirla en dos.
- `figuras.csv` quedó actualizado por `10_publish_figures_repo.py` con URLs raw de GitHub en `cartillas_estaciones/figuras_publicas/`. El repo debe ser público para que Softr cargue las imágenes.
- Las tablas creadas contienen campos genéricos (`official_start`, `records`, etc.) que se dejan vacíos; los valores específicos están en `levels_*` y `caudales_*`.
