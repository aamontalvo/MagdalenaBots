Columnas de Datos_Imputados.csv
================================

Fecha               : Fecha del registro (YYYY-MM-DD).
NombreEstacion      : Nombre de la estación hidrométrica.
Cota                : Cota del nivel de agua en metros sobre el nivel del mar (m.s.n.m.).
                      Puede ser un valor original o imputado. Los valores faltantes se
                      representan como celda vacía (NaN).
Nivel_Imputacion    : Código numérico que indica el nivel de imputación:
                      0 = Dato original (L0)
                      1 = Interpolación local (L1)
                      2 = Curva Nivel-Nivel principal (L2)
                      3 = Segunda donante Nivel-Nivel complementaria (L3)
Metodo              : Descripción del método aplicado. Ejemplos:
                      Original
                      L1_Interpolacion
                      L2_HH_<ESTACION>_quadratic
                      L3_HH_<OBJETIVO>_vs_<DONANTE>

Notas
=====
- Cada estación solo tiene registros dentro de su rango oficial (primera y última fecha
  con dato en el crudo). Fuera de ese rango no hay filas.
- Los NaN dentro del rango oficial representan días sin dato original ni imputación viable.
- L3 solo se aplica a fechas que siguen siendo NaN después de L1 y L2, y nunca
  sobrescribe valores ya existentes.
