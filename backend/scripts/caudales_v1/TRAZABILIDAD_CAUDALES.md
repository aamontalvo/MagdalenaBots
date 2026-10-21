# Trazabilidad de decisiones y resultados — Procesamiento de caudales

> Documento vivo. Se actualiza a medida que avanza el trabajo de caudales.
> Base oficial: `backend/data/processed/caudales_unificados.csv` (sin outliers).
> Scripts: `backend/scripts/caudales_v1/`.

---

## A. Base de datos y resolución de la discrepancia de homogeneidad

### A1. Adopción de `caudales_unificados.csv` como base oficial
- **Contexto**: el equipo entregó `Resultados_Pruebas_Homogeneidad.csv` (25 estaciones) con resultados que no coincidían con los análisis internos previos.
- **Causa identificada**: los análisis anteriores usaron todos los caudales sin eliminar outliers; los del equipo, sobre la serie depurada.
- **Evidencia de compatibilidad**: sobre la base unificada, Armenia reproduce exactamente los resultados del equipo — quiebre de Pettitt en 2011-01-14 (índice 11.479, posición 0-based en la serie válida) y Mann-Kendall tau = 0,0141, p = 0,0104. La base unificada es la misma serie que usó el equipo.
- **Archivo**: formato ancho, 25 estaciones, 1936-01-01 → 2026-03-14.

### A2. Agregación sub-diaria a promedio diario
- **Hallazgo**: el archivo contiene 205.722 filas para ~32.923 días calendario; las estaciones automáticas (p. ej. El Banco, 132.506 registros) tienen varias lecturas por día.
- **Consecuencia si no se corrige**: porcentajes de faltantes inflados y mezcla de frecuencias en distribuciones.
- **Implementación**: `groupby(fecha).mean()` por estación antes de cualquier figura o estadístico.

### A3. Reproducibilidad parcial de la batería del equipo
- Estaciones diarias (como Armenia): reproducción exacta.
- Estaciones sub-diarias: El Banco no reproduce (equipo tau = −0,0293; crudo = −0,1125; diario = −0,0611) y su índice de quiebre (13.814) no corresponde a su fecha de quiebre (2012-06-24) en ninguna versión disponible → probable versión de datos distinta en el lado del equipo para esas estaciones.
- La columna "Estadístico Cramer" no pudo replicarse con ninguna convención estándar probada (t de Welch/Student, Cramér-von Mises 2 muestras, z de Mann-Whitney, Brunner-Munzel, KS signado; sobre datos crudos, diarios, mensuales y anuales). **Acción pendiente**: solicitar al equipo la fórmula o el código de esa columna.

---

## B. Presentación y figuras

### B1. Nomenclatura
Solo el nombre de la estación en las figuras (sin código, sin guiones bajos), con el mismo criterio de display names de niveles.

### B2. Estaciones de trabajo
Las 14 comunes entre niveles y caudales (Calamar, Magangué, Barbosa, Armenia, Río Nuevo, Las Palomas, Las Aguadas, El Banco, Peñoncito, El Contento, Sitio Nuevo, San Pablo, Puerto Berrío, Puerto Salgar), en orden geográfico aguas abajo → aguas arriba heredado de niveles. Las 11 estaciones del unificado sin niveles quedan en standby.

### B3. Figuras generales regeneradas (`cartillas_estaciones/Caudales/`)
- `figura_boxplot_caudales_estaciones.png` — zonas Baja (Calamar→Barbosa), Media (Armenia→Peñoncito), Alta (El Contento→Puerto Salgar), escala logarítmica.
- `figura_matriz_correlacion_caudales.png` — azul→rojo, mínimo 150 días concurrentes. **Resultado relevante**: las correlaciones Q-Q son más débiles que las H-H de niveles (máximo 0,97 Calamar–Magangué; Puerto Salgar 0,34–0,77).
- `figura_heatmap_cobertura_anual_caudales.png` — % faltantes por año con "X" fuera del periodo oficial. Los vacíos antiguos de Puerto Salgar (1939–1945, 1958, 1980) son reales.

### B4. Cartillas sobrescritas (nueva base + formato)
Fig1 (serie de tiempo), Fig2 (violín mensual), Fig4 (curvas de frecuencia excedidos) y Fig5 (ajuste de extremos máximos/mínimos: Gumbel, Log-Pearson III, GEV; selección por Anderson-Darling A2; periodos de retorno T = 2–100).
- **Incidencia técnica resuelta**: un bug de closures de Python hacía que las tres distribuciones evaluaran con los parámetros de la última ajustada (GEV); corregido con binding por defecto en las lambdas. Tras el fix, Calamar máximos: mejor ajuste Log-Pearson III (A2 = 0,4462 vs. Gumbel 0,9850 y GEV 59,0280), Q(T=100) = 16.049 m³/s.

---

## C. Curvas Nivel-Caudal

### C1. Variables y datos
Variable independiente = niveles de la serie aceptada v2.1 (`Datos_Imputados.csv`); dependiente = caudales de la base oficial (diario); solo pares originales concurrentes.

### C2. Modelos
Polinomios de orden 2 y 3 por estación; se reportan ambos y se selecciona por mayor R².

### C3. Resultados (222.993 pares concurrentes)

| Estación | n pares | r | R² orden 2 | R² orden 3 |
|---|---|---|---|---|
| Calamar | 19.997 | 0,970 | 0,9580 | 0,9580 |
| Magangué | 16.753 | 0,915 | 0,8342 | 0,8363 |
| Barbosa | 15.011 | 0,820 | 0,6734 | 0,6758 |
| Armenia | 14.717 | 0,881 | 0,7752 | 0,7753 |
| Río Nuevo | 15.339 | 0,928 | 0,8610 | 0,8615 |
| Las Palomas | 15.162 | 0,941 | 0,8846 | 0,8847 |
| Las Aguadas | 18.775 | 0,984 | 0,9676 | 0,9689 |
| El Banco | 18.888 | 0,942 | 0,8880 | 0,8880 |
| Peñoncito | 17.980 | 0,917 | 0,8398 | 0,8408 |
| El Contento | 14.306 | 0,937 | 0,8773 | 0,8774 |
| Sitio Nuevo | 15.551 | 0,939 | 0,8809 | 0,8811 |
| San Pablo | 6.969 | 0,913 | 0,8339 | 0,8342 |
| Puerto Berrío | 10.330 | 0,927 | 0,8595 | 0,8597 |
| Puerto Salgar | 23.215 | 0,940 | 0,8832 | 0,8832 |

**Conclusión**: el orden 3 mejora marginalmente (ΔR² < 0,003) → el orden 2 es suficiente operativamente. Barbosa (0,673) y Armenia (0,775, límite) muestran ramas paralelas en la nube de puntos (posibles cambios de régimen; candidatas a curvas segmentadas por periodo).

---

## D. Plan de imputación de caudales (diseño)

- **Nivel 1 — Interpolación local**: vacíos ≤ 3 días con observaciones a ambos lados, kernel de cinco puntos (0,1; 0,2; 0,4; 0,2; 0,1), igual que en niveles.
- **Nivel 2 — Curva Nivel-Caudal propia**: Q = f(H) con la serie de niveles aceptada como variable independiente, entrenada solo con pares originales concurrentes. Umbral: R² ≥ 0,75.
- **Nivel 3 — Relación Q-Q entre estaciones** (pendiente de diseño detallado): solo para vacíos restantes, umbrales R² ≥ 0,65 y r ≥ 0,80 (espejo del L3 de niveles).
- **Reglas duras**: nada fuera del periodo oficial, nada sin soporte empírico, vacíos documentados como NaN, trazabilidad por nivel en cada registro.

---

## E. Ejecución de la imputación L1 + L2 (resultados)

Script: `backend/scripts/caudales_v1/04_imputacion_caudales.py`.
Salidas: `backend/data/work/caudales_v1/output/Datos_Imputados_Caudales.csv` y `Resumen_Imputacion_Caudales.csv`.

**Globales**: 299.239 registros; L1 = 349 valores; L2 = 28.632 valores; NaN restantes = 7.833.

| Estación | Cobertura final | L1 | L2 | NaN restantes | Nota |
|---|---|---|---|---|---|
| Calamar | 98,7 % | 14 | 58 | 419 | Vacíos sin niveles concurrentes |
| Magangué | 99,8 % | 6 | 2.495 | 39 | |
| Barbosa | 83,2 % | 21 | 0 | 3.137 | **N-C rechazada (R² = 0,673 < 0,75)** |
| Armenia | 100 % | 8 | 2.371 | 0 | R² = 0,775 aceptada (límite) |
| Río Nuevo | 100 % | 58 | 3.241 | 0 | |
| Las Palomas | 100 % | 39 | 2.107 | 0 | |
| Las Aguadas | 100 % | 9 | 106 | 0 | |
| El Banco | 99,6 % | 15 | 450 | 84 | |
| Peñoncito | 99,7 % | 26 | 1.196 | 51 | |
| El Contento | 100 % | 62 | 4.216 | 0 | |
| Sitio Nuevo | 100 % | 52 | 1.493 | 0 | |
| San Pablo | 100 % | 9 | 10.695 | 0 | Mayor aporte de L2 del sistema |
| Puerto Berrío | 99,7 % | 21 | 203 | 88 | |
| Puerto Salgar | 87,7 % | 9 | 1 | 4.015 | Caudal desde 1937; niveles aceptados desde 1960 → sin soporte 1937–1960 |

**Hallazgos de la ejecución**:
1. **Barbosa** quedó sin L2 porque su curva N-C no supera el umbral → candidata principal al Nivel 3 (Q-Q entre estaciones).
2. **Puerto Salgar** no tiene niveles aceptados antes de 1960, por lo que su periodo 1937–1960 no es imputable con N-C; se mantiene documentado como NaN.
3. **San Pablo** recibió el mayor volumen de L2 (10.695 valores), coherente con su baja cobertura original (54 %) en niveles.

---

## F. Pendientes abiertos

1. ~~Solicitar al equipo la definición del estadístico "Cramer"~~ → **Descartado**: no se procederá con la reproducción idéntica de la batería de homogeneidad.
2. Nivel 3 (Q-Q entre estaciones) para Barbosa y cualquier estación < 95 % → **Standby**, pregunta abierta sujeta a cambios.
3. Curvas N-C segmentadas por periodo para Barbosa y Armenia → **Standby**.
4. Estaciones del unificado sin niveles (11) → **Fuera de alcance por ahora**: el análisis se limita a las estaciones con nivel y caudal.
5. Regeneración de figuras de auditoría de niveles (scripts 06/07): standby.

---

## G. Cierre de agosto 2026: alineación con niveles y métricas

### G1. Figura 3 - Curva de duración de caudales
- Se generó `05_curva_duracion_caudales.py` para las 14 estaciones.
- Replica la estructura de la Fig3 de niveles: serie ordenada descendente, P50, P90, P95 y P100.
- Salidas: `cartillas_estaciones/Caudales/<ESTACION>/Fig3_Curva_Duracion_<ESTACION>.png` y `curvas_duracion_caudales_resumen.csv`.

### G2. Set de figuras alineado
- Niveles: Fig1 serie, Fig2 violín, Fig3 duración, Fig4 excedidos, Fig5 ajuste de distribuciones, Fig6 relación H-H.
- Caudales: Fig1 serie, Fig2 violín, Fig3 duración, Fig4 excedidos, Fig5 máximos/mínimos, Fig6 curva N-C.
- Totales vigentes: 150 PNG de niveles (143 de cartillas + 7 globales) y 101 PNG de caudales (98 de cartillas + 3 globales).

### G3. Métricas consolidadas
- `06_metricas_consolidadas.py` recalcula las cifras desde las fuentes y genera `docs/METRICAS_CAUDALES_NIVELES.md` y `docs/metricas_caudales_niveles.json`.
- Cifras clave: niveles 394.772 registros (335.501 L0, 54.835 imputados, 4.436 NaN); caudales 299.239 registros (262.425 L0, 28.981 imputados, 7.833 NaN).
- Cobertura media: 98,87% en niveles y 97,74% en caudales.

### G4. Brechas que permanecen
- El informe de caudales sigue en 11 estaciones; faltan San Pablo, Puerto Berrío y Puerto Salgar.
- La sección de imputación del informe de caudales sigue vacía.
- Barbosa sin L2 (R² N-C = 0,6734); Puerto Salgar 1937-1960 sin niveles.
- Fig6 de Puerto Salgar en niveles no existe (sin modelo H-H).
- Datos y figuras siguen fuera de git; se recomienda release/ZIP con manifiesto.
