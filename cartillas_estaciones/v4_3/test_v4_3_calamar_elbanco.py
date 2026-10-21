"""
Script de prueba para generar cartillas v4.3 solo para CALAMAR y EL_BANCO.
"""

import sys
sys.path.insert(0, r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\cartillas_estaciones')

from generar_cartillas_v4_3 import (
    load_data, get_station_data,
    plot_serie_tiempo, plot_violin_mensual, plot_curva_duracion,
    plot_curvas_excedidos, plot_ajuste_distribuciones,
    OUTPUT_DIR
)

ESTACIONES_TEST = ['CALAMAR', 'EL_BANCO']

print("=" * 70)
print("PRUEBA v4.3 - CALAMAR y EL_BANCO")
print("=" * 70)

df = load_data()
print(f"\nDatos cargados: {len(df):,} registros")

for station in ESTACIONES_TEST:
    print(f"\n{'-'*60}")
    print(f"Procesando: {station}")
    print(f"{'-'*60}")

    station_dir = OUTPUT_DIR / station
    station_dir.mkdir(exist_ok=True, parents=True)

    station_df = get_station_data(df, station)
    print(f"  Registros: {len(station_df):,}")
    print(f"  Periodo: {station_df['year'].min():.0f}-{station_df['year'].max():.0f}")

    original_count = (station_df['data_source'] == 'original').sum()
    print(f"  Originales: {original_count:,} ({original_count/len(station_df)*100:.1f}%)")

    figs = []

    try:
        output = station_dir / f"Fig1_Serie_Tiempo_{station}.png"
        plot_serie_tiempo(station_df, station, output)
        print(f"  [OK] Fig1")
        figs.append('Fig1')
    except Exception as e:
        print(f"  [ERROR] Fig1: {e}")

    try:
        output = station_dir / f"Fig2_Violin_Mensual_{station}.png"
        plot_violin_mensual(station_df, station, output)
        print(f"  [OK] Fig2")
        figs.append('Fig2')
    except Exception as e:
        print(f"  [ERROR] Fig2: {e}")

    try:
        output = station_dir / f"Fig3_Curva_Duracion_{station}.png"
        plot_curva_duracion(station_df, station, output)
        print(f"  [OK] Fig3")
        figs.append('Fig3')
    except Exception as e:
        print(f"  [ERROR] Fig3: {e}")

    try:
        output = station_dir / f"Fig4_Curvas_Excedidos_{station}.png"
        plot_curvas_excedidos(station_df, station, output)
        print(f"  [OK] Fig4")
        figs.append('Fig4')
    except Exception as e:
        print(f"  [ERROR] Fig4: {e}")

    try:
        output = station_dir / f"Fig5_Ajuste_Distribuciones_{station}.png"
        plot_ajuste_distribuciones(station_df, station, output)
        print(f"  [OK] Fig5")
        figs.append('Fig5')
    except Exception as e:
        print(f"  [ERROR] Fig5: {e}")

    print(f"\n  Figuras generadas: {len(figs)}/5 -> {figs}")

print("\n" + "=" * 70)
print("PRUEBA COMPLETADA")
print("=" * 70)
print(f"\nRevisa: {OUTPUT_DIR}")
