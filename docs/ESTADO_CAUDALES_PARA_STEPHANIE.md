# Estado actual del analisis de caudales y niveles

> **Para:** Stefany Anaya (Proyectos HYCEN) / revision tecnica.
> **Corte de datos:** 24-ago-2026. **Generado:** 19-oct-2026.
> **Objetivo:** dejar claro que se trabajo, que esta cerrado, que falta y que decisiones siguen abiertas antes de actualizar el informe.

---

## 1. Resumen en una pagina

| Tema | Niveles | Caudales |
|---|---|---|
| Estaciones en la fuente | 24 | 25 |
| Estaciones en el dataset final | 24 | 14 comunes con niveles |
| Registros finales | 394.772 | 299.239 |
| Datos originales validos | 335.501 (85,0%) | 262.425 (87,7%) |
| Imputados | 54.835 (13,9%) | 28.981 (9,7%) |
| NaN documentados | 4.436 (1,1%) | 7.833 (2,6%) |
| Cobertura media | 98,87% | 97,74% |
| Cartillas | 24 | 14 |
| Figuras vigentes | 150 | 101 |
| Estaciones en el informe | 24/24 | 11/14 |

**Mensaje principal:** los datos y las figuras de caudales ya estan al nivel de detalle de niveles, pero el **informe de caudales quedo desactualizado**: cubre 11 estaciones, no tiene seccion de imputacion y no incluye las figuras Fig3 (duracion) ni Fig6 (N-C). El informe de niveles tambien debe incorporar Fig5 y Fig6, que ya estan generadas en las cartillas.

---

## 2. Que se cerro

### 2.1 Niveles v2.1

- Pipeline L1 -> L2 -> L3 con reglas duras de rango oficial.
- 23 modelos H-H L2 y 10 modelos H-H L3; 552 parejas evaluadas.
- 0 violaciones de rango, 0 saltos anomalos, 1 alerta de cobertura (Calamar).
- 24 cartillas y 150 figuras vigentes.
- Informe de julio con 24 estaciones y 105 imagenes; usa 4 figuras por estacion.

### 2.2 Caudales v1

- Base unificada sub-diaria (205.722 filas, 25 estaciones) y promedio diario.
- Imputacion L1 + L2: 349 + 28.632 valores; 7.833 NaN documentados.
- 14 curvas N-C con 222.993 pares; R2 0,6734-0,9676; 13 L2 aceptados.
- 14 curvas de duracion (Fig3) generadas para alinear el set con niveles.
- 14 cartillas y 101 figuras vigentes.
- 9 checks de integridad: 6 PASS, 0 FAIL, 2 INFO; todos los checks criticos pasaron.

---

## 3. Que falta o esta incompleto

| # | Brecha | Evidencia | Accion |
|---|---|---|---|
| 1 | El informe de caudales cubre 11 de 14 estaciones | Faltan San Pablo, Puerto Berrio y Puerto Salgar | Agregar las 3 secciones |
| 2 | La seccion "Imputacion de datos" esta vacia | Solo existe el titulo | Reutilizar la estructura de niveles y adaptar las cifras |
| 3 | La seccion "Anexos" esta vacia | Solo existe el titulo | Agregar tablas, figuras y trazabilidad |
| 4 | 20 imagenes de extremos sin leyenda | 57 imagenes, 37 leyendas | Agregar captions y numeracion |
| 5 | No incluye Fig3 ni Fig6 | El borrador usa Fig1, Fig2, Fig4, Fig5 max/min | Insertar Fig3 (duracion) y Fig6 (N-C) |
| 6 | El informe de niveles no incluye Fig5 ni Fig6 | Usa 4 figuras por estacion | Insertar Fig5 (24) y Fig6 (23; Puerto Salgar no tiene H-H) |
| 7 | Cifra de originales de niveles inconsistentes | El texto dice ~82,0%; el dataset da 84,99% | Corregir el resumen ejecutivo |
| 8 | Barbosa sin L2 | R2 N-C = 0,6734 < 0,75 | Evaluar L3 Q-Q o curva N-C segmentada |
| 9 | Puerto Salgar 1937-1960 sin niveles | No hay soporte para N-C | Mantener NaN documentado |
| 10 | Fig6 de Puerto Salgar en niveles | No hay modelo H-H | Nota de no aplicabilidad |

---

## 4. Alineacion de figuras: caudales replica niveles

La decision es que **caudales replique la estructura de niveles**, no al contrario.

| Tipo | Niveles | Caudales | Estado |
|---|---|---|---|
| Fig1 Serie de tiempo | Si (24) | Si (14) | Completo |
| Fig2 Violin mensual | Si (24) | Si (14) | Completo |
| Fig3 Curva de duracion | Si (24) | Si (14) | **Nueva en caudales** |
| Fig4 Curvas de excedidos | Si (24) | Si (14) | Completo |
| Fig5 Ajuste de extremos/distribuciones | Si (24) | Si (14 max + 14 min) | Completo |
| Fig6 Relacion H-H / N-C | Si (23) | Si (14) | Completo; falta Fig6 de Puerto Salgar en niveles |
| Figuras globales | 7 | 3 | Completas |

**En los informes:**

- Niveles: 96 figuras de estacion insertadas (24 x 4); faltan 47 (Fig5 y Fig6).
- Caudales: 53 imagenes de estacion insertadas; faltan 45 (22 de Fig3/Fig6 en las 11 incluidas + 21 de las 3 estaciones faltantes + 2 extremos sin insertar).

---

## 5. Cifras que deben usarse en el informe

### Niveles

- Registros: 394.772.
- L0 validos: 335.501 (84,99%).
- L1: 1.222 (0,31%); L2: 36.758 (9,31%); L3: 16.855 (4,27%).
- Total imputado: 54.835 (13,89%); NaN: 4.436 (1,12%).
- Cobertura media: 98,87%; sin Calamar: 99,11%.
- 12 estaciones al 100%; 23 >95%; 1 <95% (Calamar 93,34%).
- 4 estaciones inhomogeneas: Armenia, Barbosa, Sitio Nuevo, Tenerife.

### Caudales

- Registros: 299.239.
- L0 validos: 262.425 (87,7%).
- L1: 349 (0,12%); L2: 28.632 (9,57%).
- Total imputado: 28.981 (9,68%); NaN: 7.833 (2,62%).
- Cobertura media: 97,74%.
- 7 estaciones al 100%; 12 >95%; 2 <95% (Barbosa 83,22%, Puerto Salgar 87,67%).
- N-C: 14 modelos, 222.993 pares, R2 0,6734-0,9676; 13 L2 aceptados.

---

## 6. Preguntas abiertas para la revision

1. **Barbosa:** se deja sin L2 y se documenta, o se intenta L3 Q-Q / curva N-C segmentada?
2. **Puerto Salgar 1937-1960:** se mantiene como NaN documentado o se busca una donante fuera de niveles?
3. **Estaciones nuevas en el informe de caudales:** se agregan San Pablo, Puerto Berrio y Puerto Salgar con las 7 figuras disponibles?
4. **Fig6 de Puerto Salgar en niveles:** se omite con nota o se genera una figura sustituta?
5. **Fig5/Fig6 en niveles:** se insertan las 47 figuras disponibles o solo una seleccion?
6. **Numeracion de figuras:** se renombra todo el informe de niveles para evitar el reinicio en la seccion de imputacion?
7. **Cifras del resumen ejecutivo:** se reemplazan por las de este documento?
8. **Versionado:** el informe final se entrega en DOCX, PDF o ambos?

---

## 7. Archivos de referencia

- `docs/METRICAS_CAUDALES_NIVELES.md` - tablero completo de cifras.
- `docs/CONTEXTO_MAESTRO_CAUDALES.md` - contexto y linaje.
- `docs/INVENTARIO_ENTREGABLES.md` - inventario de archivos.
- `docs/RESPUESTAS_COMENTARIOS_STEFANY.md` - comentarios y respuestas.
- `backend/entregables/caudales_v1/Consolidado_Caudales_Niveles.xlsx` - resumen en Excel.
- `cartillas_estaciones/Caudales/` - 101 figuras de caudales.
- `backend/entregables/niveles_v2_1/07_cartillas/` - 143 figuras de niveles.
