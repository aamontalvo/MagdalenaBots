#!/usr/bin/env python3
"""
Genera cartillas para TODAS las estaciones NO problemáticas
Guarda en subcarpetas individuales por estación
"""

import sys
import os
sys.path.append('./funciones')

from graficador import generar_cartilla_completa

# Lista de estaciones NO problemáticas (13 estaciones)
ESTACIONES_NO_PROBLEMATICAS = [
    # Zona Baja (6 estaciones)
    'CALAMAR',
    'BARBOSA', 
    'TENERIFE',
    'PLATO',
    'MAGANGUE',
    'SAN_PEDRITO',
    
    # Zona Media (3 estaciones - excluyendo RIO_NUEVO, LAS_PALOMAS, ARMENIA)
    'LAS_AGUADAS',
    'EL_BANCO',
    'PENONCITO',
    
    # Zona Alta (4 estaciones - excluyendo GAMARRA_AUT)
    'LA_GLORIA',
    'EL_CONTENTO',
    'SITIO_NUEVO',
    'PUERTO_WILCHES'
]

# Estaciones EXCLUIDAS (problemáticas):
# COYONGAL, RIO_NUEVO, LAS_PALOMAS, ARMENIA, GAMARRA_AUT


def generar_cartilla_con_subcarpeta(nombre_estacion, base_output_dir='./resultados/'):
    """
    Genera las 5 figuras para una estación y las guarda en subcarpeta propia.
    """
    # Crear subcarpeta para la estación
    estacion_dir = os.path.join(base_output_dir, nombre_estacion)
    os.makedirs(estacion_dir, exist_ok=True)
    
    print(f"\n{'='*60}")
    print(f"PROCESANDO: {nombre_estacion}")
    print(f"{'='*60}")
    
    try:
        # Generar figuras en la subcarpeta
        generar_cartilla_completa(nombre_estacion, output_dir=estacion_dir + '/')
        
        print(f"✓ Completado: {nombre_estacion}")
        print(f"  Guardado en: {estacion_dir}/")
        return True
        
    except Exception as e:
        print(f"✗ Error en {nombre_estacion}: {str(e)}")
        return False


def main():
    print("="*60)
    print("GENERADOR DE CARTILLAS - ESTACIONES NO PROBLEMÁTICAS")
    print("="*60)
    print(f"\nTotal de estaciones a procesar: {len(ESTACIONES_NO_PROBLEMATICAS)}")
    print("\nEstaciones EXCLUIDAS (problemáticas):")
    print("  - COYONGAL")
    print("  - RIO_NUEVO")
    print("  - LAS_PALOMAS")
    print("  - ARMENIA")
    print("  - GAMARRA_AUT")
    print("\n" + "="*60)
    
    # Procesar todas las estaciones
    exitosos = 0
    fallidos = 0
    
    for i, estacion in enumerate(ESTACIONES_NO_PROBLEMATICAS, 1):
        print(f"\n[{i}/{len(ESTACIONES_NO_PROBLEMATICAS)}] ", end="")
        
        if generar_cartilla_con_subcarpeta(estacion):
            exitosos += 1
        else:
            fallidos += 1
    
    # Resumen final
    print("\n" + "="*60)
    print("RESUMEN FINAL")
    print("="*60)
    print(f"✓ Exitosos: {exitosos}/{len(ESTACIONES_NO_PROBLEMATICAS)}")
    print(f"✗ Fallidos: {fallidos}/{len(ESTACIONES_NO_PROBLEMATICAS)}")
    print("\nArchivos generados en: ./resultados/")
    print("Estructura:")
    for estacion in ESTACIONES_NO_PROBLEMATICAS:
        print(f"  resultados/{estacion}/")
        print(f"    ├── Fig1_Serie_Tiempo_{estacion}.png")
        print(f"    ├── Fig2_Comportamiento_Mensual_{estacion}.png")
        print(f"    ├── Fig3_Curva_Duracion_{estacion}.png")
        print(f"    ├── Fig4_Curvas_Excedidos_{estacion}.png")
        print(f"    └── Fig5_Distribucion_Probabilidad_{estacion}.png")
    print("="*60)


if __name__ == '__main__':
    main()
