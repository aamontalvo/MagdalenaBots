#!/usr/bin/env python3
"""
Genera visualizaciones de validación para estaciones problemáticas
Crea gráficos con los flags CRITICAL y WARNING marcados
"""

import sys
sys.path.append('./funciones')

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from validate_imputation import ImputationValidator, STATION_NEIGHBORS
import warnings
warnings.filterwarnings('ignore')

# Configuración de estilo
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12


def plot_validation_summary(results, output_dir='./resultados/'):
    """Genera figura resumen con todas las estaciones."""
    
    fig, axes = plt.subplots(5, 1, figsize=(16, 20))
    fig.suptitle('Validación de Imputación - Estaciones Problemáticas', 
                 fontsize=16, fontweight='bold', y=0.995)
    
    for idx, result in enumerate(results):
        ax = axes[idx]
        station = result['station']
        
        # Cargar datos de la estación
        validator = ImputationValidator(data_path='./datos/processed/')
        df_station = validator.df[validator.df['station'] == station].copy()
        df_station = df_station.sort_values('date')
        
        # Serie completa
        ax.plot(df_station['date'], df_station['level'], 
                color='black', linewidth=0.4, alpha=0.7, label='Serie temporal')
        
        # Marcar flags
        flags = result['all_flags']
        if len(flags) > 0:
            critical = flags[flags['severity'] == 'CRITICAL']
            warning = flags[flags['severity'] == 'WARNING']
            
            if len(critical) > 0:
                ax.scatter(critical['date'], critical['level'], 
                          color='red', s=60, zorder=5, marker='x', 
                          linewidths=2, label=f'CRITICAL ({len(critical)})')
            
            if len(warning) > 0:
                ax.scatter(warning['date'], warning['level'], 
                          color='orange', s=30, alpha=0.6, zorder=4, 
                          label=f'WARNING ({len(warning)})')
        
        # Configuración del eje
        ax.set_ylabel('Cota (m.s.n.m.)', fontsize=10)
        ax.set_title(f'{station} - {result["assessment"]}', 
                    fontsize=11, fontweight='bold', loc='left')
        ax.legend(loc='upper left', fontsize=8)
        ax.grid(True, alpha=0.3, linestyle='--')
        
        # Formato de fechas
        ax.xaxis.set_major_locator(mdates.YearLocator(10))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
        ax.xaxis.set_minor_locator(mdates.YearLocator(5))
        
        # Estadísticas
        stats = result['statistics']
        stats_text = (f"N: {stats['n_valid']:,} | "
                     f"Rango: {stats['min_level']:.1f}-{stats['max_level']:.1f}m | "
                     f"Flags: {result['total_flags']}")
        ax.text(0.02, 0.97, stats_text, transform=ax.transAxes, fontsize=8,
                verticalalignment='top', bbox=dict(boxstyle='round', 
                facecolor='wheat', alpha=0.8))
    
    plt.xlabel('Fecha', fontsize=11)
    plt.tight_layout()
    plt.savefig(f'{output_dir}Validacion_Resumen_Todas_Estaciones.png', 
                dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Figura guardada: {output_dir}Validacion_Resumen_Todas_Estaciones.png")


def plot_detailed_validation(station, result, output_dir='./resultados/'):
    """Genera figura detallada para una estación específica."""
    
    validator = ImputationValidator(data_path='./datos/processed/')
    df_station = validator.df[validator.df['station'] == station].copy()
    df_station = df_station.sort_values('date')
    
    # Crear figura con 2 paneles
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10), 
                                    gridspec_kw={'height_ratios': [3, 1]})
    
    # Panel superior: Serie temporal
    ax1.plot(df_station['date'], df_station['level'], 
             color='black', linewidth=0.5, alpha=0.8, label='Serie temporal')
    
    flags = result['all_flags']
    
    if len(flags) > 0:
        critical = flags[flags['severity'] == 'CRITICAL']
        warning = flags[flags['severity'] == 'WARNING']
        
        if len(critical) > 0:
            ax1.scatter(critical['date'], critical['level'], 
                       color='red', s=80, zorder=5, marker='x', 
                       linewidths=2.5, label=f'CRITICAL ({len(critical)})')
        
        if len(warning) > 0:
            ax1.scatter(warning['date'], warning['level'], 
                       color='orange', s=40, alpha=0.7, zorder=4, 
                       label=f'WARNING ({len(warning)})')
    
    ax1.set_ylabel('Cota (m.s.n.m.)', fontsize=11)
    ax1.set_title(f'Validación Detallada - {station}\n{result["assessment"]}', 
                 fontsize=13, fontweight='bold')
    ax1.legend(loc='best')
    ax1.grid(True, alpha=0.3)
    
    # Panel inferior: Velocidad de cambio
    df_station['daily_change'] = df_station['level'].diff().abs()
    
    ax2.plot(df_station['date'], df_station['daily_change'], 
             color='blue', linewidth=0.3, alpha=0.6, label='|Δnivel/día|')
    
    # Líneas de umbral
    stats = result['statistics']
    ax2.axhline(y=stats['p99_change'], color='orange', linestyle='--', 
                alpha=0.7, label=f'p99 = {stats["p99_change"]:.2f}m')
    ax2.axhline(y=stats['p995_change']*2, color='red', linestyle='--', 
                alpha=0.7, label=f'2×p99.5 = {stats["p995_change"]*2:.2f}m')
    
    # Marcar flags en velocidad
    velocity_flags = flags[flags['flag_type'] == 'VELOCITY'] if len(flags) > 0 else pd.DataFrame()
    if len(velocity_flags) > 0:
        ax2.scatter(velocity_flags['date'], velocity_flags['daily_change'], 
                   color='red', s=50, zorder=5, marker='x')
    
    ax2.set_ylabel('|Δ Nivel| (m/día)', fontsize=11)
    ax2.set_xlabel('Fecha', fontsize=11)
    ax2.legend(loc='best', fontsize=9)
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(0, None)
    
    # Formato de fechas
    for ax in [ax1, ax2]:
        ax.xaxis.set_major_locator(mdates.YearLocator(10))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
        ax.xaxis.set_minor_locator(mdates.YearLocator(5))
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}Validacion_Detallada_{station}.png', 
                dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Figura guardada: {output_dir}Validacion_Detallada_{station}.png")


def main():
    print("="*70)
    print("GENERANDO VISUALIZACIONES DE VALIDACIÓN")
    print("="*70)
    
    # Inicializar validador
    validator = ImputationValidator(data_path='./datos/processed/')
    
    # Estaciones a validar
    problem_stations = ['COYONGAL', 'RIO_NUEVO', 'LAS_PALOMAS', 'ARMENIA', 'GAMARRA_AUT']
    
    # Ejecutar validación
    results = []
    for station in problem_stations:
        neighbors = STATION_NEIGHBORS.get(station, [])
        result = validator.validate_station(station, neighbor_stations=neighbors)
        results.append(result)
    
    print("\n" + "="*70)
    print("GENERANDO FIGURAS")
    print("="*70)
    
    # Figura resumen con todas las estaciones
    print("\n[1/6] Generando figura resumen...")
    plot_validation_summary(results)
    
    # Figuras detalladas por estación
    for idx, result in enumerate(results, 2):
        station = result['station']
        print(f"\n[{idx}/6] Generando figura detallada para {station}...")
        plot_detailed_validation(station, result)
    
    print("\n" + "="*70)
    print("VISUALIZACIONES COMPLETADAS")
    print("="*70)
    print("\nArchivos generados en ./resultados/:")
    print("  - Validacion_Resumen_Todas_Estaciones.png")
    print("  - Validacion_Detallada_COYONGAL.png")
    print("  - Validacion_Detallada_RIO_NUEVO.png")
    print("  - Validacion_Detallada_LAS_PALOMAS.png")
    print("  - Validacion_Detallada_ARMENIA.png")
    print("  - Validacion_Detallada_GAMARRA_AUT.png")


if __name__ == '__main__':
    main()
