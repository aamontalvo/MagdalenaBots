# Imputacion de datos faltantes

La imputacion de datos faltantes garantiza la continuidad temporal requerida para analisis de frecuencia y tendencias de largo plazo. El sistema implementado opera mediante una cascada jerarquica de cuatro niveles, donde la seleccion del metodo depende de la magnitud del gap, la disponibilidad de estaciones independientes correlacionadas y la calidad estadistica de las relaciones altura-altura (H-H) establecidas. El flujograma de ejecucion y los porcentajes de aporte por nivel se resumen en la Figura 10 [AM9.1].

El criterio de aceptacion para modelos H-H se fija en R² >= 0.75, umbral que asegura la explicacion de al menos el 75 % de la varianza. Los modelos por debajo de este valor se documentan con fines diagnosticos pero no se utilizan para imputacion efectiva.

Un principio hidrologico fundamental del sistema es la orientacion correcta de las relaciones H-H: la variable independiente (predictora) debe ubicarse siempre aguas arriba de la variable dependiente (objetivo), garantizando la coherencia con la direccion de flujo del rio. Esta restriccion descarta automaticamente cualquier modelo que use una estacion aguas abajo como predictora de una estacion aguas arriba.

## Resumen de resultados

El proceso imputo 43,133 valores (13.99 % del total de 308,364 registros), distribuidos en cuatro niveles. La cobertura global alcanza el 100.0 % en las 14 estaciones aprobadas para analisis, mientras que las 4 estaciones descartadas por inhomogeneidad temporal (Armenia, Tenerife, Barbosa, Sitio Nuevo) tambien fueron completadas para mantener la integridad del dataset maestro. El corte temporal para todos los analisis es el 31 de diciembre de 2025.

| Nivel | Metodo | Valores imputados | % del total |
|-------|--------|-------------------|-------------|
| **L0** | Datos originales medidos | 265,231 | 86.01 % |
| **L1** | Interpolacion local ponderada | 2,959 | 0.96 % |
| **L2** | H-H cuadratica (una independiente) | 22,970 | 7.45 % |
| **L3** | missForest / extrapolacion no parametrica | 17,143 | 5.56 % |
| **L4** | Climatologia estacional (correccion artefacto) | 61 | 0.02 % |
| | **Total** | **308,364** | **100.0 %** |

### Tabla desglosada por estacion

| Estacion | L0 Original | L1 Interpolacion | L2 H-H | L3 missForest | L4 Climatologia | Total | % Original | % Imputado |
|----------|-------------|------------------|--------|---------------|-----------------|-------|------------|------------|
| **San Pedrito** | 16,409 | 53 | 693 | 0 | 0 | 17,155 | 95.65 % | 4.35 % |
| **Calamar** | 21,341 | 31 | 33 | 38 | 61 | 21,504 | 99.24 % | 0.76 % |
| **Tenerife** | 14,171 | 287 | 3,155 | 1,459 | 0 | 19,072 | 74.30 % | 25.70 % |
| **Plato** | 16,142 | 185 | 0 | 1,752 | 0 | 18,079 | 89.29 % | 10.71 % |
| **Magangue** | 15,799 | 191 | 1,523 | 1,741 | 0 | 19,254 | 82.06 % | 17.94 % |
| **Barbosa** | 14,350 | 199 | 3,096 | 1,051 | 0 | 18,696 | 76.75 % | 23.25 % |
| **Coyongal** | 15,691 | 152 | 2,497 | 216 | 0 | 18,556 | 84.56 % | 15.44 % |
| **Armenia** | 15,020 | 233 | 0 | 3,984 | 0 | 19,237 | 78.08 % | 21.92 % |
| **Rio Nuevo** | 14,209 | 301 | 3,949 | 179 | 0 | 18,638 | 76.24 % | 23.76 % |
| **Las Palomas** | 15,688 | 234 | 2,872 | 155 | 0 | 18,949 | 82.79 % | 17.21 % |
| **Las Aguadas** | 18,749 | 59 | 325 | 0 | 0 | 19,133 | 97.99 % | 2.01 % |
| **El Banco** | 18,706 | 57 | 410 | 264 | 0 | 19,437 | 96.24 % | 3.76 % |
| **Penoncito** | 17,097 | 168 | 0 | 1,988 | 0 | 19,253 | 88.80 % | 11.20 % |
| **La Gloria** | 11,140 | 117 | 0 | 1,408 | 0 | 12,665 | 87.96 % | 12.04 % |
| **Gamarra Aut** | 4,397 | 50 | 0 | 298 | 0 | 4,745 | 92.67 % | 7.33 % |
| **El Contento** | 13,430 | 367 | 3,592 | 1,348 | 0 | 18,737 | 71.68 % | 28.32 % |
| **Sitio Nuevo** | 15,086 | 192 | 825 | 993 | 0 | 17,096 | 88.24 % | 11.76 % |
| **Puerto Wilches** | 7,806 | 83 | 0 | 269 | 0 | 8,158 | 95.69 % | 4.31 % |

*Nota: Estaciones en negrita son las 14 estaciones no descartadas (aptas para analisis). Las 4 estaciones descartadas por homogeneidad temporal (Armenia, Tenerife, Barbosa, Sitio Nuevo) se marcan con [DESCARTADA] en el dataset maestro.*

## Nivel L0: Datos originales medidos

Los datos originales provienen de los registros nivel-metricos del IDEAM, procesados a partir de las series horarias y diarias de cada estacion. Constituyen el 86.01 % del dataset (265,231 registros) y representan la fuente primaria de informacion. El procesamiento incluyo control de calidad basico, eliminacion de valores fisicamente imposibles y estandarizacion de unidades a metros sobre el nivel del mar (m.s.n.m.).

## Nivel L1: Interpolacion local ponderada

Periodos con gaps <= 3 dias se completan mediante interpolacion local ponderada de cinco puntos con kernel [0.1, 0.2, 0.4, 0.2, 0.1]. Se requiere al menos dos valores vecinos validos; no se aplica al inicio o final de serie. Este nivel imputo 2,959 valores (0.96 % del total), distribuidos en 18 estaciones. Los valores L1 se consideran de alta confianza debido a la continuidad hidrodinamica que caracteriza el flujo fluvial en escalas temporales reducidas.

## Nivel L2: Curvas altura-altura (H-H) cuadraticas

Para gaps > 3 dias se establecen relaciones estadisticas entre estaciones cercanas mediante regresion cuadratica de una sola variable independiente. La variable independiente se selecciona obligatoriamente entre estaciones ubicadas aguas arriba de la dependiente, conforme al orden geografico del rio. El modelo adopta la forma H_dep = a * H_ind^2 + b * H_ind + c.

Este nivel imputo 22,970 valores (7.45 %). Se entrenaron 12 modelos con R² >= 0.75. Las mejores correlaciones se concentran en la zona baja y media, donde la continuidad hidrologica entre estaciones contiguas es maxima.

### Tabla de modelos H-H aceptados

| Dependiente (aguas abajo) | Independiente (aguas arriba) | Ecuacion | R² | n |
|---------------------------|------------------------------|----------|-----|-----|
| **Calamar** | Magangue | H = 0.012905 * H^2 + 0.580837 * H - 6.585584 | 0.9763 | 15,746 |
| **Tenerife** | Magangue | H = 0.037600 * H^2 - 0.050777 * H + 0.603984 | 0.9606 | 12,384 |
| **Magangue** | Barbosa | H = 0.025700 * H^2 + 0.114267 * H + 6.677464 | 0.8987 | 12,726 |
| **Barbosa** | Coyongal | H = 0.016080 * H^2 + 0.416081 * H + 3.605543 | 0.8768 | 12,148 |
| **Coyongal** | El Banco | H = -0.073616 * H^2 + 4.928907 * H - 60.354840 | 0.8685 | 15,491 |
| **Rio Nuevo** | Las Aguadas | H = -0.023506 * H^2 + 1.943900 * H - 12.110109 | 0.9165 | 13,959 |
| **Las Palomas** | Las Aguadas | H = -0.032196 * H^2 + 2.407577 * H - 17.180649 | 0.9208 | 15,468 |
| **Las Aguadas** | El Banco | H = -0.020040 * H^2 + 2.036621 * H - 14.619214 | 0.9791 | 18,103 |
| **El Banco** | Penoncito | H = 0.057572 * H^2 - 2.224669 * H + 44.407922 | 0.8390 | 16,638 |
| **El Contento** | Sitio Nuevo | H = -0.011182 * H^2 + 2.239026 * H - 44.959042 | 0.7637 | 11,227 |
| **Sitio Nuevo** | Puerto Wilches | H = -0.014486 * H^2 + 2.851696 * H - 72.500660 | 0.8134 | 6,918 |
| **San Pedrito** | Calamar | H = 0.002688 * H^2 + 0.960705 * H + 0.066373 | 0.9930 | 16,310 |

*Nota: Todos los modelos cumplen con el criterio R² >= 0.75 y respetan la orientacion hidrologica (independiente aguas arriba, dependiente aguas abajo). La estacion Plato no cuenta con modelo H-H aceptado porque su mejor correlacion con Magangue alcanzo solo R² = 0.7437, por debajo del umbral.*

## Nivel L3: Imputacion no parametrica (missForest)

Cuando no existe una estacion independiente aguas arriba con R² >= 0.75, o cuando los gaps residuales persisten despues de aplicar L1 y L2, se emplea un algoritmo de Random Forest para imputacion multiple (missForest). Este metodo utiliza como predictores todas las demas estaciones del sistema, capturando relaciones no lineales complejas que los modelos bivariados no pueden representar.

Este nivel imputo 17,143 valores (5.56 %), concentrados principalmente en estaciones donde la geografia limita las opciones de modelos H-H validos: Puerto Wilches (estacion terminal aguas arriba del sistema), Gamarra Aut (serie corta), Armenia (influencia del Cauca) y La Gloria (aislamiento hidrologico relativo).

## Nivel L4: Correccion de artefacto missForest por climatologia estacional

Durante la revision de calidad del dataset v4.3 se detecto un artefacto grave en la estacion Calamar: el periodo 1 de diciembre de 1969 al 30 de enero de 1970 (61 dias consecutivos) fue imputado por missForest como una serie completamente constante con valor 2.617 m (desviacion estandar = 0.000 m). Este comportamiento indica un colapso del algoritmo missForest a la media global cuando ninguna estacion donante tenia datos observados en ese periodo.

### Diagnostico del artefacto

| Parametro | Valor |
|-----------|-------|
| Estacion | Calamar |
| Periodo | 1969-12-01 a 1970-01-30 |
| Duracion | 61 dias |
| Valor missForest | 2.617 m (constante) |
| Desviacion estandar missForest | 0.000 m |
| Estaciones donantes con datos en periodo | 0 (ninguna) |

El analisis revelo que en diciembre de 1969 ninguna de las 17 estaciones restantes tenia datos originales disponibles, por lo que missForest carecio de predictores y predijo la media historica como valor constante. Sin embargo, la climatologia historica de Calamar para diciembre-enero muestra un patron estacional descendente caracteristico del regimen hidrologico del Rio Magdalena, con medias diarias que varian desde ~7.0 m en diciembre hasta ~4.0 m en enero.

### Metodologia de correccion

La correccion emplea una climatologia estacional ajustada, calculada como sigue:

1. **Climatologia diaria**: Para cada mes-dia del calendario (excluyendo 29 de febrero), se calcula la cota media historica de Calamar utilizando unicamente datos originales medidos (n = 21,341 registros originales).

2. **Ajuste por nivel medio**: La serie climatologica del periodo se centra en la media del valor missForest original (2.617 m), preservando la senal de que 1969-1970 fue un ano con niveles relativamente bajos:

   ```
   valor_final = climatologia_diaria - (media_climatologia - media_missForest)
   ```

3. **Hard rule**: Los valores resultantes se limitan al rango historico original de Calamar [0.930 m, 9.300 m].

### Resultado de la correccion

| Metrica | missForest (v4.3) | L4 Climatologia (v4.4) |
|---------|-------------------|------------------------|
| Media | 2.617 m | 2.624 m |
| Desviacion estandar | 0.000 m | 0.999 m |
| Minimo | 2.617 m | 0.930 m |
| Maximo | 2.617 m | 3.795 m |
| Variabilidad | Ninguna | Estacional descendente |

La serie corregida reproduce el patron estacional esperado: inicia en ~3.8 m a principios de diciembre y desciende progresivamente hasta ~0.9 m a finales de enero, coherente con la hidrologia de estiaje del Rio Magdalena. La media se conserva practicamente identica (diferencia de +0.007 m), preservando la interpretacion de que el periodo correspondio a un ano de niveles bajos.

### Artefacto SITIO_NUEVO 1988 — Decision de no correccion

Durante la misma revision se detecto un segundo bloque con baja variabilidad en Sitio Nuevo (24 de enero a 28 de febrero de 1988, 36 dias, std = 0.045 m). Sin embargo, este bloque no fue corregido por las siguientes razones:

1. **Dispersion no nula**: A diferencia de Calamar (std = 0.000 m), Sitio Nuevo presenta una variabilidad residual pequena pero no nula, indicando que missForest no colapso completamente a la media.

2. **Donantes de baja calidad**: Las tres mejores estaciones donantes con datos originales en ese periodo (El Banco, R² = 0.528; Armenia, R² = 0.352; Penoncito, R² = 0.460) no alcanzan el umbral minimo de R² >= 0.75 requerido para imputacion H-H. Aplicar una correccion con donantes de tan baja calidad introduciria mas incertidumbre que el artefacto original.

3. **Impacto limitado**: Sitio Nuevo es una estacion descartada por inhomogeneidad temporal (quiebre en 2008, Pettitt p = 0.0009), por lo que sus datos no se utilizan en analisis de frecuencia ni tendencias.

## Homogeneidad temporal y estaciones descartadas

La verificacion de homogeneidad temporal constituye un requisito indispensable para garantizar la validez de analisis de tendencias. Se aplicaron tres pruebas estadisticas complementarias (Pettitt, SNHT y Mann-Kendall) a las 18 estaciones. Cuatro estaciones presentaron cambios de regimen estadisticamente significativos (p < 0.05) y fueron clasificadas como inhomogeneas:

- **Armenia**: Cambio en 1998 (Pettitt p = 0.0189)
- **Tenerife**: Tendencia creciente significativa (MK tau = 0.467, p = 0.0034) y quiebre en 2005
- **Barbosa**: Cambio en 2012 (Pettitt p = 0.0459)
- **Sitio Nuevo**: Cambio en 2008 (Pettitt p = 0.0009) y tendencia decreciente (MK tau = -0.386, p = 0.0017)

Estas cuatro estaciones se completaron mediante imputacion para mantener la integridad del dataset maestro, pero se excluyen explicitamente de analisis de frecuencia y tendencias de largo plazo. Las 14 estaciones restantes son homogeneas y estan 100 % completas en sus rangos temporales, cumpliendo con los estandares requeridos para analisis hidrologicos rigurosos.

## Recomendaciones de uso de las series completadas

Para **analisis de frecuencia y diseno hidraulico**, se recomienda utilizar exclusivamente las **14 estaciones homogeneas y completas**, excluyendo las 4 estaciones inhomogeneas identificadas. Dentro de este grupo, las estaciones con mayor proporcion de datos originales (Calamar 99.24 %, Las Aguadas 98.0 %, El Banco 96.2 %, San Pedrito 95.7 %, Puerto Wilches 95.7 %) pueden utilizarse sin restricciones adicionales.

Para **analisis de tendencias y cambio climatico**, las 14 estaciones aprobadas son potencialmente utilizables, con la advertencia de que los periodos con alta proporcion de datos imputados (> 20 % del registro anual) deben ser identificados y excluidos de sub-analisis especificos. Se recomienda realizar analisis comparativos entre series con y sin imputacion para verificar que las tendencias detectadas no sean artefactos del proceso de completitud.

San Pedrito, ahora con 100 % de cobertura y correlacion excepcional con Calamar (R² = 0.993), pasa a la categoria de estacion de **uso sin restricciones** para todos los analisis hidrologicos, incluyendo frecuencia de eventos extremos.
