#!/usr/bin/env python3
"""
Script rapido para validar TODAS las estaciones
Uso: python validar_todas_estaciones_light.py
"""

import sys
sys.path.append('./funciones')

from validate_all_stations_light import LightValidator

def main():
    print("="*70)
    print("VALIDACION LIGHT - TODAS LAS ESTACIONES")
    print("Detectando: outliers, saltos en curvas, problemas de distribucion")
    print("="*70)
    
    validator = LightValidator()
    results = validator.validate_all()
    
    # Generar reporte
    report_file = validator.generate_report(results)
    
    # Resumen
    critical = [r for r in results if r['overall_status'] == 'CRITICAL']
    warning = [r for r in results if r['overall_status'] == 'WARNING']
    ok = [r for r in results if r['overall_status'] == 'OK']
    
    print("\n" + "="*70)
    print("RESUMEN FINAL")
    print("="*70)
    print(f"\nCRITICAL ({len(critical)} estaciones):")
    for r in critical:
        print(f"  - {r['station']}: {r['n_critical']} checks criticos")
    
    print(f"\nWARNING ({len(warning)} estaciones):")
    for r in warning:
        print(f"  - {r['station']}: {r['n_warning']} checks de advertencia")
    
    print(f"\nOK ({len(ok)} estaciones)")
    
    print("\n" + "="*70)
    print(f"Reporte completo: {report_file}")
    print("="*70)
    
    # Alertas especificas
    print("\n⚠️  ALERTAS IMPORTANTES:")
    
    # Estaciones con problemas de curva de duracion (como Armenia)
    duration_problems = [r for r in results 
                        if r['checks'].get('duration_jumps', {}).get('status') == 'CRITICAL']
    if duration_problems:
        print(f"\nProblemas en curva de duracion (saltos/valles artificiales):")
        for r in duration_problems:
            jumps = r['checks']['duration_jumps']
            print(f"  - {r['station']}: {jumps['jumps_lower_pct']} saltos en extremos inferiores")
    
    # Estaciones con problemas de distribucion
    dist_problems = [r for r in results 
                    if r['checks'].get('distribution', {}).get('status') in ['CRITICAL', 'WARNING']]
    if dist_problems:
        print(f"\nProblemas de ajuste de distribucion (Q-Q plots desviados):")
        for r in dist_problems:
            dist = r['checks']['distribution']
            print(f"  - {r['station']}: QQ corr={dist['qq_correlation']:.3f}")
    
    # Estaciones con outliers
    outlier_problems = [r for r in results 
                       if r['checks'].get('outliers', {}).get('n_severe', 0) > 5]
    if outlier_problems:
        print(f"\nOutliers severos detectados:")
        for r in outlier_problems:
            out = r['checks']['outliers']
            print(f"  - {r['station']}: {out['n_severe']} valores extremos")

if __name__ == '__main__':
    main()
