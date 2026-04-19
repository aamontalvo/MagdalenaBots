#!/usr/bin/env python3
"""
Script standalone para validar estaciones con problemas de imputación
Uso: python validar_estaciones.py
"""

import sys
sys.path.append('./funciones')

from validate_imputation import ImputationValidator, generate_validation_report, STATION_NEIGHBORS

def main():
    print("="*70)
    print("SISTEMA DE VALIDACIÓN DE IMPUTACIÓN - RÍO MAGDALENA")
    print("="*70)
    
    # Inicializar validador
    validator = ImputationValidator(data_path='./datos/processed/')
    
    # Estaciones problemáticas
    problem_stations = ['COYONGAL', 'RIO_NUEVO', 'LAS_PALOMAS', 'ARMENIA', 'GAMARRA_AUT']
    
    print(f"\nEstaciones a validar: {', '.join(problem_stations)}")
    print("="*70)
    
    # Ejecutar validación
    results = []
    for station in problem_stations:
        neighbors = STATION_NEIGHBORS.get(station, [])
        result = validator.validate_station(station, neighbor_stations=neighbors)
        results.append(result)
    
    # Generar reporte
    print("\n" + "="*70)
    print("GENERANDO REPORTE...")
    print("="*70)
    
    report_file = generate_validation_report(results, output_path='./resultados/')
    
    print("\n" + "="*70)
    print("VALIDACIÓN COMPLETADA")
    print("="*70)
    print(f"\nArchivos generados:")
    print(f"  - {report_file}")
    print(f"\nResumen:")
    
    for r in results:
        print(f"  {r['station']}: {r['total_flags']} flags ({r['critical_flags']} CRITICAL, {r['warning_flags']} WARNING)")

if __name__ == '__main__':
    main()
