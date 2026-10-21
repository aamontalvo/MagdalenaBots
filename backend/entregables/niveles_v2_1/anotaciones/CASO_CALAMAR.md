# Anotación: caso CALAMAR

## Resumen

`CALAMAR` es la única estación del dataset final que no alcanza el umbral de cobertura del 95 % dentro de su rango oficial. Su cobertura final es **93.34 %**, con **1,431 días sin dato** concentrados al inicio de su registro.

## Datos clave

| Campo | Valor |
|---|---|
| Estación | CALAMAR |
| Rango oficial | 1967-02-01 a 2025-12-31 |
| Días en rango | 21,500 |
| NaN restantes | 1,431 |
| Cobertura final | 93.34 % |
| Periodo sin datos | **1967-02-01 a 1973-01-31** |
| Imputados L1 | 13 |
| Imputados L2 | 86 |
| Imputados L3 | 83 |

## ¿Por qué no se imputó el bloque inicial?

Durante el periodo 1967–1973 ninguna otra estación del dataset tiene datos concurrentes que cumplan los criterios de correlación para ser donante H-H:

- La estación con mayor superposición temporal, **Puerto Salgar**, sí tiene datos disponibles en 1,603 de los 1,613 días faltantes, pero su correlación con CALAMAR es muy baja:
  - Pearson r = 0.4508
  - R² = 0.2033
  - Umbral requerido para L3: r ≥ 0.80 y R² ≥ 0.65
- Por tanto, Puerto Salgar no es un donante viable.
- La mejor donante disponible para CALAMAR fue **EL_BANCO** (R² = 0.7831, r = 0.8835), pero solo pudo cubrir 83 días adicionales porque la mayoría de los NaN de CALAMAR en 1967–1973 no tienen datos concurrentes en EL_BANCO tampoco.

## Decisión adoptada

Se dejan los 1,431 NaN como tales en el dataset final. No se aplicó imputación por climatología, media histórica ni extrapolación para no introducir información artificial en un periodo sin soporte empírico.

## Implicaciones

- CALAMAR aparece marcada como `INCOMPLETA` en `Resumen_Imputacion.csv`.
- El agente de validación genera una alerta de cobertura baja, que es esperada y documentada.
- Cualquier análisis que use la serie de CALAMAR debe considerar el periodo 1967–1973 como sin datos.

## Recomendación

Si en el futuro se consiguen datos de estaciones cercanas a CALAMAR para el periodo 1967–1973 (por ejemplo, registros históricos no digitalizados o bases de datos regionales), se podría reevaluar la posibilidad de imputar ese bloque con un modelo H-H adicional.

---

*Anotación generada el 25 de junio de 2026.*
