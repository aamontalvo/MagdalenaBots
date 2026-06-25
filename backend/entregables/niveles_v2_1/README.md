# Entrega final - Imputación de niveles IDEAM v2.1

## 1. Objetivo

Este paquete contiene el dataset final de cotas diarias del IDEAM para la cuenca del Magdalena, con un proceso de imputación estructurado en tres niveles (L1, L2, L3). Toda la imputación se restringe al rango oficial de cada estación, y los valores faltantes que no pudieron ser imputados se conservan como `NaN` para transparentar la cobertura real.

---

## 2. Resumen del proceso

El pipeline parte del dataset crudo `Resumen_Crudos_IDEAM_2026_v2_1.csv`, aplica las siguientes reglas de negocio y genera `Datos_Imputados.csv`:

- **Corte temporal:** 31 de diciembre de 2025.
- **Eliminación de 29 de febrero** de todos los años.
- **Rango oficial por estación:** primera y última fecha con dato válido en el crudo. No se imputa ni se reporta fuera de este rango.
- **Sin restricción geográfica** para estaciones donantes en las curvas Nivel-Nivel (H-H).
- **Niveles de imputación:**
  - **L0 – Original:** dato medido reportado por el IDEAM.
  - **L1 – Interpolación local:** huecos de 3 días o menos rodeados de valores válidos.
  - **L2 – Curva H-H principal:** modelo cuadrático con la mejor estación donante (`R² ≥ 0.75`).
  - **L3 – Segunda donante H-H complementaria:** aplicada automáticamente cuando la cobertura tras L2 es inferior al 95 %. Se selecciona la donante que maximiza la cobertura de `NaN` restantes, con `R² ≥ 0.65` y `r ≥ 0.80`. L3 nunca reemplaza L0, L1 ni L2.
- **Hard rules:** clip defensivo al rango histórico observado como verificación numérica.

---

## 3. Resultados globales

| Métrica | Valor |
|---|---|
| Estaciones | 24 |
| Registros totales | 394,772 |
| Datos originales (L0) | ~82.0 % |
| Imputados L1 | 1,222 |
| Imputados L2 | 36,758 |
| Imputados L3 | 16,855 |
| **Total imputados** | **54,835** |
| Estaciones con cobertura 100 % | 12 |
| Estaciones con cobertura > 95 % | 11 |
| Estaciones con cobertura < 95 % | 1 (CALAMAR, ver Anotaciones) |

**Validaciones automáticas:**
- Registros fuera del rango oficial: **0**
- Violaciones del rango histórico de cota: **0**
- Saltos temporales anomalos: **0**
- Alertas del agente de validación: **1** (CALAMAR, cobertura baja, justificada)

---

## 4. Estructura del paquete

```
backend/entregables/niveles_v2_1/
├── 01_datos_originales/          # Datos crudos y rangos oficiales
├── 02_datos_imputados/           # Dataset final, backup sin L3 y descripción de columnas
│   ├── Datos_Imputados.csv
│   ├── Datos_Imputados_sin_L3.csv  # Backup con L0/L1/L2 (antes de aplicar L3)
│   └── README_columnas.txt
├── 03_modelos/                   # Tablas de modelos H-H L2 y L3
├── 04_scripts/                   # Scripts reproducibles del pipeline
│   └── imputation_pipeline_v2_1/ # Paquete reutilizable
├── 05_validacion_y_auditoria/    # Reportes de validación y auditoría
├── 06_figuras/                   # Figuras globales del proceso
├── 07_cartillas/                 # Cartillas por estación (5 figuras × 24 estaciones)
├── anotaciones/                  # Notas y casos especiales
└── README.md                     # Este archivo
```

---

## 5. Archivos principales

| Ruta | Descripción |
|---|---|
| `01_datos_originales/Resumen_Crudos_IDEAM_2026_v2_1.csv` | Dataset crudo preparado (sin imputar). |
| `01_datos_originales/resumen_rangos_estaciones.csv` | Rango oficial usado por estación. |
| `02_datos_imputados/Datos_Imputados.csv` | Dataset final long con nivel de imputación y método. |
| `02_datos_imputados/Datos_Imputados_sin_L3.csv` | Dataset de backup con solo L0/L1/L2 (antes de L3). |
| `03_modelos/Tabla_Modelos_HH_Seleccionados.csv` | Modelos H-H usados en L2. |
| `03_modelos/Tabla_Modelos_L3.csv` | Modelos H-H usados en L3. |
| `05_validacion_y_auditoria/Resumen_Imputacion.csv` | Cobertura final por estación. |
| `05_validacion_y_auditoria/auditoria_todas_estaciones.md` | Auditoría detallada de las 24 estaciones con figuras. |
| `05_validacion_y_auditoria/validacion_post_imputacion.md` | Reporte de validación post-imputación. |
| `05_validacion_y_auditoria/agente_validacion_reporte.md` | Reporte del agente de validación automática. |

---

## 6. Cómo ejecutar el pipeline

Desde la raíz del repositorio:

```bash
# 1. Preparar dataset
py backend/scripts/imputation_v2_1/02_prepare_dataset.py

# 2. Descubrir modelos H-H
py backend/scripts/imputation_v2_1/03_hh_discovery.py

# 3. Ejecutar imputación L1 -> L2 -> L3
py backend/scripts/imputation_v2_1/04_run_imputation.py

# 4. Validación y reportes
py backend/scripts/imputation_v2_1/05_validate_and_report.py

# 5. Auditoría de 12 estaciones representativas
py backend/scripts/imputation_v2_1/06_auditoria_12_estaciones.py

# 6. Auditoría de las 24 estaciones
py backend/scripts/imputation_v2_1/07_auditoria_todas_estaciones.py

# 7. Agente de validación independiente
py backend/scripts/imputation_v2_1/13_agente_validacion.py
```

---

## 7. Notas para auditores externos

- El dataset final está en **formato long**: `Fecha, NombreEstacion, Cota, Nivel_Imputacion, Metodo`.
- `Nivel_Imputacion` indica el nivel de confianza: 0 = original, 1 = interpolación local, 2 = H-H principal, 3 = H-H complementaria.
- Los `NaN` dentro del rango oficial corresponden a huecos que no pudieron ser imputados por falta de donantes concurrentes.
- Todos los valores fueron verificados contra el rango temporal oficial y el rango histórico de cota de cada estación.
- Las cartillas por estación se regeneran a partir de `Datos_Imputados.csv` y se encuentran en `07_cartillas/`.

---

## 8. Anotaciones importantes

Ver el archivo `anotaciones/CASO_CALAMAR.md` para el único caso de cobertura inferior al 95 %.

---

*Generado el 25 de junio de 2026. Para dudas técnicas revisar `INFORME_ENTREGA_v2_1.md` en `backend/scripts/imputation_v2_1/`.*
