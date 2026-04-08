# Cartillas de Estaciones - Skill

Generación de cartillas hidrológicas para estaciones de monitoreo del Río Magdalena.

## Estructura de Cartillas v4.2

Cada estación tiene 5 figuras:

### Fig1 - Serie de Tiempo
- **Datos**: Imputados v4.2 (completos)
- **Formato**: Línea negra continua (sin categorizar)
- **Anotación**: Período, total observaciones, % originales, % imputados

### Fig2 - Violin Mensual
- **Datos**: Originales IDEAM (sin imputar)
- **Formato**: Violin plot gris con líneas de referencia
- **Leyenda**: Media (rojo), Mediana (negro)

### Fig3 - Curva de Duración
- **Datos**: Imputados v4.2
- **Línea principal**: Azul
- **Línea Q95**: Negro dashed (zona baja, 95% excedido)
- **Línea P50**: Gris dotted

### Fig4 - Curvas de Frecuencia de Niveles Excedidos
- **Datos**: Imputados v4.2
- **Colores**:
  - MAX/MIN: Negro
  - 5%: Rojo oscuro (#8B0000)
  - 25%: Verde (#6B8E23)
  - 50%: Negro grueso
  - 75%: Azul (#5DADE2)
  - 95%: Naranja (#D35400)
- **Etiquetas**: FUERA del box (a la derecha)

### Fig5 - Ajuste de Distribuciones
- **Datos**: Originales IDEAM
- **Histograma**: Gris claro con borde gris
- **Curvas**:
  - Normal: Negro sólido
  - Pearson III: Negro dashed
  - Weibull: Negro dotted
- **Q-Q Plot**: Grises

## Datos Imputados

**Ruta**: `Informes/imputacion/Datos_Imputados_v3.csv`

**Columnas relevantes**:
- `date`: Fecha
- `station`: Nombre de estación
- `level`: Nivel imputado (si aplica)
- `data_source`: Tipo de dato
  - `original`: Dato medido
  - `imputed_hh`: Imputado por curvas H-H
  - `imputed_local`: Imputado por interpolación local
  - `missing`: Sin dato
- `donor_station`: Estación donante (para imputados H-H)

## Comandos

Generar cartillas:
```bash
cd cartillas_estaciones
python generar_cartillas_v4_2_corregido.py
```

## Cobertura por Estación

| Estación | Cobertura | Estado |
|----------|-----------|--------|
| CALAMAR | 99.4% | Completa |
| TENERIFE | 99.9% | Completa |
| MAGANGUE | 99.8% | Completa |
| BARBOSA | 99.8% | Completa |
| LAS_AGUADAS | 99.6% | Completa |
| PUERTO_WILCHES | 99.2% | Completa |
| SITIO_NUEVO | 95.4% | Completa |
| COYONGAL | 100% | Completa |
| LA_GLORIA | 100% | Completa |
| RIO_NUEVO | 98.7% | Completa |
| EL_BANCO | 98.2% | Completa |
| LAS_PALOMAS | 98.1% | Completa |
| PENONCITO | 98.4% | Completa |
| GAMARRA_AUT | 93.0% | Restringida |
| EL_CONTENTO | 91.5% | Completa |
| ARMENIA | 77.9% | Limitada |
| SAN_PEDRITO | 45.4% | Excluida |
