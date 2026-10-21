# Comentarios de Stefany y respuestas tecnicas

> **Fuente:** comentarios embebidos en los borradores de julio 2026.
> **Objetivo:** dejar trazabilidad de cada observacion y su estado, para que la actualizacion del informe no reabra decisiones ya cerradas.
> **Regla:** cuando no hay evidencia suficiente, el estado queda como "Pendiente de decision editorial"; no se inventa una respuesta.

## 1. Informe de caudales (11 comentarios)

| ID | Autor | Fecha | Comentario | Respuesta / estado | Evidencia |
|---:|---|---|---|---|---|
| 3 | Alexander | 2026-06-20 | Corregir ortografia. Notar problemas en la serie antigua de Calamar y en faltantes de Magangue, Barbosa, Rio Nuevo, El Banco y El Contento. | **Resuelto en datos; pendiente editorial.** Calamar inicia en 1940 en caudales y 1967 en niveles. Los faltantes estan en la tabla de cobertura. | `Resumen_Imputacion_Caudales.csv`; `Resumen_Imputacion.csv` |
| 4 | Alexander | 2026-06-20 | Resuelto. | **Cerrado.** | - |
| 11 | Proyectos HYCEN | 2026-07-24 | Mis pruebas no coinciden con estos resultados. | **Resuelto.** Alex: las pruebas estaban bien; se estaban usando valores con outliers. La base oficial ya los excluye. | `TRAZABILIDAD_CAUDALES.md`, A1-A3 |
| 12 | Alexander | 2026-08-24 | Tus pruebas estan bien Stefy; estaba tomando los valores con outliers y ya se corrige. | **Cerrado.** | `TRAZABILIDAD_CAUDALES.md` |
| 26 | Alexander | 2026-06-20 | Cambios para imputacion de mayor nivel tecnico. | **Resuelto.** Se implemento L1 + L2 con reglas duras y trazabilidad. | `04_imputacion_caudales.py` |
| 34 | Proyectos HYCEN | 2026-07-23 | Este evento si sucedio o es un error? | **Evento real con outlier.** El pico de Barbosa de mediados de los 70 es un extremo documentado. | `Outliers_Caudales.csv`; `Eventos_Abruptos_Caudales.csv` |
| 35 | Alexander | 2026-06-20 | Valor extremo basico con claro outlier en datos originales al inicio de la serie. | **Cerrado.** | `Outliers_Caudales.csv` |
| 42 | Alexander | 2026-06-20 | Cambio de picos claro alrededor de 2015. | **Documentado.** | Serie Armenia; `Eventos_Abruptos_Caudales.csv` |
| 58 | Alexander | 2026-06-20 | La serie esta cortada hasta el 2020. | **Correcto.** Las Palomas cierra su periodo oficial en 2020-12-31. | `Resumen_Imputacion_Caudales.csv` |
| 73 | Proyectos HYCEN | 2026-07-23 | Es un evento real o un error? Maximiza los maxs despues. | **Serie con problemas de maximos.** Se reporta como outlier; no se usa para imputar. | `Outliers_Caudales.csv` |
| 78 | Alexander | 2026-06-20 | Serie con claros problemas de maximos en outliers. | **Cerrado.** | `Outliers_Caudales.csv` |

## 2. Informe de niveles (19 comentarios)

| ID | Autor | Fecha | Comentario | Respuesta / estado | Evidencia |
|---:|---|---|---|---|---|
| 8 | Stefany Anaya | 2026-07-16 | No se si San Pablo va mas aguas arriba; en el mapa aparecia entre Sitio Nuevo y Puerto Wilches. | **Resuelto.** Alex marco "Resuelto". | - |
| 9 | Alexander | 2026-07-16 | Resuelto. | **Cerrado.** | - |
| 14 | Alexander | 2026-05-06 | Hay que escribir en que consiste cada prueba o no? | **Pendiente editorial.** Se sugiere una linea por prueba. | `Resultados_Pruebas_Homogeneidad.csv` |
| 20 | Stefany Anaya | 2026-07-16 | Esto lo hare yo. | **Asignado a Stefany.** | - |
| 23 | Alexander | 2026-04-10 | Colocar la explicacion de los niveles de imputacion. | **Existe en niveles; falta en caudales.** | `docs/CONTEXTO_MAESTRO_CAUDALES.md` |
| 24 | Alexander | 2026-07-21 | La numeracion de las figuras se reinicio y no encontre forma de corregirlo. | **Pendiente.** Renumerar la seccion de imputacion. | Borrador de niveles |
| 30 | Stefany Anaya | 2026-07-15 | Revisar la explicacion de este nivel. | **Pendiente editorial.** | - |
| 31 | Alexander | 2026-07-21 | Actualizar referencia cuando sea necesario. | **Pendiente editorial.** | - |
| 33 | Alexander | 2026-07-21 | Se deberia colocar esto o no, dado que Calamar siempre es estacion de referencia; sus faltantes (~7%) son del inicio. | **Documentar.** Calamar tiene 93,34% de cobertura; sus NaN se concentran en 1967-1973. | `Resumen_Imputacion.csv`; `anotaciones/CASO_CALAMAR.md` |
| 34 | Stefany Anaya | 2026-07-15 | Este parrafo se puede quitar porque no aplicaria; hay correlaciones con R2 mayor a 80%. | **Pendiente editorial.** Revisar contra la tabla de modelos. | `Tabla_Modelos_HH_Seleccionados.csv` |
| 36 | Stefany Anaya | 2026-07-15 | Revisar toda esta seccion y decidir que colocar. | **Pendiente editorial.** | - |
| 37 | Alexander | 2026-07-21 | Hecho; cuidado si incluir o no esta subseccion, a mi parecer si porque es auditado. | **Cerrado.** | - |
| 39 | Stefany Anaya | 2026-07-15 | Mejorar esta seccion. | **Pendiente editorial.** | - |
| 41 | Alexander | 2026-04-10 | Los ajustes de distribucion no estan terminados; son diarios, no para periodo de retorno porque no se han sacado max/min anual. | **Resuelto en v2.1.** Se genero Fig5 de ajuste de distribuciones; en caudales se genero Fig5 max/min. | `14_generar_cartillas_v2_1.py`; `02_cartillas_caudales_resto.py` |
| 63 | Stefany Anaya | 2026-04-15 | Colocar la serie hasta 2025. | **Correcto.** El corte global es 2025-12-31; algunas estaciones terminan antes por su ultimo dato valido. | `Resumen_Imputacion.csv` |
| 89 | Stefany Anaya | 2026-04-15 | Esta serie antes tenia hasta 2025; ahora aparece hasta 2024, se debe a algo? | **No es error.** Barbosa termina 2024-12-20; Las Palomas 2025-06-30; cada estacion respeta su ultimo dato valido. | `Resumen_Imputacion.csv` |
| 128 | Stefany Anaya | 2026-04-15 | La informacion de datos originales e imputados vario en un 10%. Revisar. | **Revisar en la version final.** Cifras vigentes: L0 84,99%; imputados 13,89%; NaN 1,12%. | `Datos_Imputados.csv`; `Resumen_Imputacion.csv` |
| 160 | Stefany Anaya | 2026-04-15 | Mejorar leyendas. | **Pendiente editorial.** | - |
| 215 | Alexander | 2026-03-06 | Analizar donde colocarlas. | **Pendiente editorial.** | - |

## 3. Prioridad de revision

1. **Cerrar la seccion de imputacion de caudales** (comentario 23).
2. **Renumerar figuras de niveles** (comentario 24).
3. **Agregar captions a las 20 imagenes de extremos** de caudales.
4. **Revisar la variacion del 10%** en niveles (comentario 128) contra el dataset final.
5. **Decidir que parrafos se mantienen** en las secciones marcadas por Stefany (34, 36, 39).
6. **Actualizar referencias y leyendas** (31, 160, 215).

## 4. Nota sobre el intercambio de pruebas

El comentario 11 de Stefany ("mis pruebas no coinciden") y la respuesta 12 de Alex son la clave del cruce de resultados:

- Las pruebas de Stefany estaban bien calculadas.
- La diferencia venia de usar la serie cruda con outliers.
- La base oficial de caudales excluye outliers; por eso los estadisticos cambian.
- En Armenia la reproduccion es exacta sobre la base unificada (Pettitt 2011-01-14, indice 11.479; Mann-Kendall tau 0,0141, p 0,0104).
- En El Banco no se reproduce: el equipo reporta tau -0,0293; el crudo -0,1125; el diario -0,0611. Probablemente el equipo uso otra version de datos para esa estacion.
- El estadistico "Cramer" no se pudo reproducir con ninguna convencion estandar y se descarto.

Ver `backend/scripts/caudales_v1/TRAZABILIDAD_CAUDALES.md`, secciones A y F.
