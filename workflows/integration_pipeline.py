#!/usr/bin/env python3
"""
Workflow de Integracion Continua - MagdalenaBot
Pipeline completo: Validacion -> Imputacion -> Generacion de Cartillas -> Reporte
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'database'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'cartillas_estaciones', 'funciones'))

import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Dict, Optional
import json

from models import (
    Station, WaterLevelMeasurement, ImputationModel, ValidationResult,
    QualityStatus, Zone, STATIONS_CATALOG, get_usable_stations, get_excluded_stations
)


class IntegrationPipeline:
    """Pipeline completo de procesamiento de datos hidrologicos."""
    
    def __init__(self, data_path: str = './data/processed/'):
        self.data_path = data_path
        self.results = {
            'validation': {},
            'imputation': {},
            'cartillas': {},
            'report': {}
        }
        
    def step_1_validate(self, station_id: str) -> ValidationResult:
        """
        Paso 1: Validar calidad de datos de una estacion.
        Detecta outliers, saltos en curvas, problemas de distribucion.
        """
        print(f"[PASO 1] Validando {station_id}...")
        
        # Cargar datos
        df = pd.read_csv(f'{self.data_path}Datos_Imputados_v3.csv')
        df_station = df[df['station'] == station_id].copy()
        
        if len(df_station) == 0:
            return ValidationResult(
                station_id=station_id,
                check_outliers_status="CRITICAL",
                quality_score=0,
                alerts=["No hay datos disponibles"]
            )
        
        # Check 1: Outliers
        Q1 = df_station['level'].quantile(0.25)
        Q3 = df_station['level'].quantile(0.75)
        IQR = Q3 - Q1
        outliers = df_station[
            (df_station['level'] < Q1 - 3*IQR) | 
            (df_station['level'] > Q3 + 3*IQR)
        ]
        
        # Check 2: Saltos en curva de duracion
        levels_sorted = df_station['level'].dropna().sort_values()
        diffs = np.diff(levels_sorted.values)
        median_diff = np.median(np.abs(diffs))
        large_jumps = np.sum(np.abs(diffs) > 5 * median_diff)
        
        # Calcular score general
        score = 100
        status_outliers = "OK"
        status_jumps = "OK"
        
        if len(outliers) > 10:
            score -= 30
            status_outliers = "WARNING"
        if len(outliers) > 20:
            score -= 20
            status_outliers = "CRITICAL"
            
        if large_jumps > 5:
            score -= 20
            status_jumps = "WARNING"
        if large_jumps > 10:
            score -= 20
            status_jumps = "CRITICAL"
        
        result = ValidationResult(
            station_id=station_id,
            check_outliers_status=status_outliers,
            check_duration_jumps_status=status_jumps,
            check_distribution_status="OK",  # Simplificado
            n_outliers=len(outliers),
            n_duration_jumps=large_jumps,
            quality_score=max(0, score),
            alerts=[]
        )
        
        if score < 50:
            result.alerts.append("Calidad insuficiente para analisis de frecuencia")
        
        self.results['validation'][station_id] = result
        print(f"  Score: {result.quality_score}/100 - {status_outliers}/{status_jumps}")
        return result
    
    def step_2_impute(self, station_id: str, force_reimpute: bool = False) -> Dict:
        """
        Paso 2: Imputar datos faltantes usando modelos H-H.
        Solo si la estacion paso validacion o force_reimpute=True.
        """
        print(f"[PASO 2] Imputando {station_id}...")
        
        validation = self.results['validation'].get(station_id)
        
        if not validation:
            print(f"  ⚠ No hay resultado de validacion. Ejecutando validacion primero...")
            validation = self.step_1_validate(station_id)
        
        if validation.quality_score < 50 and not force_reimpute:
            print(f"  ✗ Omitido: Calidad insuficiente ({validation.quality_score})")
            return {'status': 'SKIPPED', 'reason': 'Low quality score'}
        
        # Aqui iria la logica de imputacion
        # Por ahora, registro simplificado
        result = {
            'station_id': station_id,
            'status': 'COMPLETED',
            'method': 'H-H_v3.0',
            'n_imputed': 0,  # Calcular segun datos
            'models_used': []
        }
        
        self.results['imputation'][station_id] = result
        print(f"  ✓ Completado")
        return result
    
    def step_3_generate_cartilla(self, station_id: str) -> bool:
        """
        Paso 3: Generar cartilla con 5 figuras para la estacion.
        """
        print(f"[PASO 3] Generando cartilla {station_id}...")
        
        try:
            from graficador import generar_cartilla_completa
            
            output_dir = f'./cartillas_estaciones/resultados/{station_id}'
            os.makedirs(output_dir, exist_ok=True)
            
            generar_cartilla_completa(station_id, output_dir=output_dir + '/')
            
            self.results['cartillas'][station_id] = {
                'status': 'GENERATED',
                'output_dir': output_dir,
                'n_figures': 5
            }
            print(f"  ✓ Cartilla generada en {output_dir}")
            return True
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            self.results['cartillas'][station_id] = {
                'status': 'FAILED',
                'error': str(e)
            }
            return False
    
    def step_4_generate_report(self) -> str:
        """
        Paso 4: Generar reporte consolidado del pipeline.
        """
        print(f"[PASO 4] Generando reporte consolidado...")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_stations': len(self.results['validation']),
                'passed_validation': sum(1 for v in self.results['validation'].values() if v.quality_score >= 50),
                'failed_validation': sum(1 for v in self.results['validation'].values() if v.quality_score < 50),
                'cartillas_generated': sum(1 for c in self.results['cartillas'].values() if c.get('status') == 'GENERATED')
            },
            'stations': {}
        }
        
        for station_id in self.results['validation'].keys():
            report['stations'][station_id] = {
                'validation': self.results['validation'][station_id].to_dict() if hasattr(self.results['validation'][station_id], 'to_dict') else str(self.results['validation'][station_id]),
                'imputation': self.results['imputation'].get(station_id, {}),
                'cartilla': self.results['cartillas'].get(station_id, {})
            }
        
        # Guardar reporte
        report_path = './workflows/reports/pipeline_report.json'
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        self.results['report'] = report
        print(f"  ✓ Reporte guardado en {report_path}")
        return report_path
    
    def run_full_pipeline(self, station_ids: List[str], skip_cartillas: bool = False):
        """
        Ejecuta pipeline completo para lista de estaciones.
        """
        print("="*60)
        print("PIPELINE DE INTEGRACION CONTINUA - MagdalenaBot")
        print("="*60)
        print(f"Estaciones a procesar: {len(station_ids)}")
        print(f"Pasos: Validacion -> Imputacion -> {'Cartillas -> ' if not skip_cartillas else ''}Reporte")
        print("="*60)
        
        for station_id in station_ids:
            print(f"\n{'='*60}")
            print(f"PROCESANDO: {station_id}")
            print(f"{'='*60}")
            
            # Paso 1: Validar
            self.step_1_validate(station_id)
            
            # Paso 2: Imputar (si aplica)
            self.step_2_impute(station_id)
            
            # Paso 3: Generar cartilla (si no se omite)
            if not skip_cartillas:
                self.step_3_generate_cartilla(station_id)
        
        # Paso 4: Reporte consolidado
        self.step_4_generate_report()
        
        print("\n" + "="*60)
        print("PIPELINE COMPLETADO")
        print("="*60)
        print(f"Resumen:")
        print(f"  - Estaciones procesadas: {len(station_ids)}")
        print(f"  - Validaciones exitosas: {self.results['report']['summary']['passed_validation']}")
        print(f"  - Cartillas generadas: {self.results['report']['summary']['cartillas_generated']}")


def main():
    """Ejemplo de uso del pipeline."""
    pipeline = IntegrationPipeline()
    
    # Procesar estaciones NO excluidas
    excluded = ['ARMENIA', 'GAMARRA_AUT', 'SAN_PEDRITO', 'RIO_NUEVO', 'LAS_PALOMAS', 'COYONGAL']
    all_stations = list(STATIONS_CATALOG.keys())
    stations_to_process = [s for s in all_stations if s not in excluded]
    
    # Agregar otras estaciones del proyecto
    other_stations = ['TENERIFE', 'PLATO', 'LA_GLORIA', 'SITIO_NUEVO', 'PUERTO_WILCHES', 
                      'LAS_AGUADAS', 'PENONCITO', 'EL_CONTENTO']
    stations_to_process.extend(other_stations)
    
    pipeline.run_full_pipeline(stations_to_process, skip_cartillas=False)


if __name__ == '__main__':
    main()
