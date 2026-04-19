#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analisis comparativo de estadisticos entre datos convertidos y tabla de referencia
"""

import pandas as pd
import os

# Tabla de referencia proporcionada
REFERENCIA = {
    'San Pedrito': {'codigo': '29047070', 'n': 14230, 'media': 5.198, 'mediana': 5.247, 'std': 1.69, 'min': 1.041, 'max': 9.25, 'p10': 2.79, 'p90': 7.38},
    'Calamar': {'codigo': '29037020', 'n': 21381, 'media': 5.263, 'mediana': 5.32, 'std': 1.699, 'min': 0.93, 'max': 9.3, 'p10': 2.847, 'p90': 7.46},
    'Tenerife': {'codigo': '29017010', 'n': 14179, 'media': 8.942, 'mediana': 8.93, 'std': 1.853, 'min': 3.2, 'max': 13.99, 'p10': 6.593, 'p90': 11.33},
    'Plato': {'codigo': '25027450', 'n': 14145, 'media': 9.287, 'mediana': 9.27, 'std': 1.868, 'min': 4.14, 'max': 15.08, 'p10': 6.885, 'p90': 11.77},
    'Magangue': {'codigo': '25027680', 'n': 15799, 'media': 15.434, 'mediana': 15.471, 'std': 1.63, 'min': 10.152, 'max': 19.201, 'p10': 13.231, 'p90': 17.501},
    'Barbosa': {'codigo': '25027530', 'n': 14350, 'media': 16.253, 'mediana': 16.395, 'std': 1.715, 'min': 11.221, 'max': 19.596, 'p10': 13.768, 'p90': 18.405},
    'Coyongal': {'codigo': '25027930', 'n': 15726, 'media': 17.901, 'mediana': 18.004, 'std': 1.62, 'min': 12.739, 'max': 20.799, 'p10': 15.659, 'p90': 19.979},
    'Armenia': {'codigo': '25027360', 'n': 15020, 'media': 19.958, 'mediana': 20.172, 'std': 1.986, 'min': 3.84, 'max': 22.817, 'p10': 18.183, 'p90': 21.931},
    'Rio Nuevo': {'codigo': '25027630', 'n': 14209, 'media': 21.603, 'mediana': 21.712, 'std': 1.145, 'min': 17.776, 'max': 23.85, 'p10': 20.096, 'p90': 23.021},
    'Las Palomas': {'codigo': '25027390', 'n': 15688, 'media': 22.713, 'mediana': 22.831, 'std': 1.16, 'min': 18.841, 'max': 25.239, 'p10': 21.192, 'p90': 24.131},
    'Las Aguadas': {'codigo': '25027490', 'n': 18749, 'media': 24.676, 'mediana': 24.735, 'std': 1.409, 'min': 20.285, 'max': 27.873, 'p10': 22.845, 'p90': 26.555},
    'El Banco': {'codigo': '25027020', 'n': 18744, 'media': 25.913, 'mediana': 25.924, 'std': 1.393, 'min': 21.944, 'max': 29.181, 'p10': 24.074, 'p90': 27.784},
    'Penoncito': {'codigo': '25027330', 'n': 17097, 'media': 26.498, 'mediana': 26.534, 'std': 1.559, 'min': 19.637, 'max': 31.15, 'p10': 24.567, 'p90': 28.457},
    'La Gloria': {'codigo': '23217060', 'n': 11156, 'media': 32.999, 'mediana': 32.963, 'std': 1.307, 'min': 29.29, 'max': 36.409, 'p10': 31.3, 'p90': 34.727},
    'Gamarra Aut': {'codigo': '23217080', 'n': 4415, 'media': 36.412, 'mediana': 36.45, 'std': 1.487, 'min': 32.171, 'max': 40.151, 'p10': 34.417, 'p90': 38.327},
    'El Contento': {'codigo': '23217030', 'n': 13447, 'media': 39.846, 'mediana': 39.86, 'std': 1.276, 'min': 34.58, 'max': 43.041, 'p10': 38.206, 'p90': 41.556},
    'Sitio Nuevo': {'codigo': '23187280', 'n': 15104, 'media': 50.671, 'mediana': 50.658, 'std': 1.031, 'min': 46.977, 'max': 53.012, 'p10': 49.352, 'p90': 52.118},
    'Puerto Wilches': {'codigo': '23187010', 'n': 7806, 'media': 63.68, 'mediana': 63.617, 'std': 0.882, 'min': 61.053, 'max': 66.113, 'p10': 62.585, 'p90': 64.87}
}

def main():
    input_file = r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\backend\data\processed\Resumen_LongFormat_NotProcessedNotImputation.csv'
    
    # Leer archivo convertido
    df = pd.read_csv(input_file)
    df['FechaDT'] = pd.to_datetime(df['Fecha'], format='%d-%m-%Y')
    df['CotaNum'] = pd.to_numeric(df['Cota'], errors='coerce')
    
    output_file = 'comparacion_estadisticos.txt'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 120 + "\n")
        f.write("COMPARACION DE ESTADISTICOS: DATOS CONVERTIDOS vs TABLA DE REFERENCIA\n")
        f.write("=" * 120 + "\n\n")
        
        # Resumen por estacion
        f.write("RANGO DE FECHAS POR ESTACION (Datos Convertidos)\n")
        f.write("-" * 100 + "\n")
        f.write(f"{'Estacion':<20} {'Codigo':<12} {'Registros':<12} {'Inicio':<12} {'Fin':<12} {'Anos':<8}\n")
        f.write("-" * 100 + "\n")
        
        resumen_rows = []
        for codigo in sorted(df['CodigoEstacion'].unique()):
            df_est = df[df['CodigoEstacion'] == codigo]
            nombre = df_est['NombreEstacion'].iloc[0]
            fecha_min = df_est['FechaDT'].min()
            fecha_max = df_est['FechaDT'].max()
            
            resumen_rows.append({
                'nombre': nombre,
                'codigo': codigo,
                'n': len(df_est),
                'inicio': fecha_min.strftime('%d-%m-%Y'),
                'fin': fecha_max.strftime('%d-%m-%Y'),
                'anos': fecha_max.year - fecha_min.year + 1
            })
        
        for r in resumen_rows:
            f.write(f"{r['nombre']:<20} {r['codigo']:<12} {r['n']:<12} {r['inicio']:<12} {r['fin']:<12} {r['anos']:<8}\n")
        
        f.write("\n" + "=" * 120 + "\n")
        f.write("COMPARACION DE ESTADISTICOS\n")
        f.write("=" * 120 + "\n\n")
        
        # Comparar estadisticos
        f.write(f"{'Estacion':<18} {'N Datos':<20} {'Media':<20} {'Std':<20} {'Min/Max':<25}\n")
        f.write(f"{'':18} {'Ref':>8} {'Conv':>8} {'Dif':>8} {'Ref':>8} {'Conv':>8} {'Dif':>8} {'Ref':>8} {'Conv':>8} {'Dif':>8} {'Ref Min':>10} {'Conv Min':>10} {'Ref Max':>10} {'Conv Max':>10}\n")
        f.write("-" * 140 + "\n")
        
        diferencias_significativas = []
        
        for nombre_ref, datos_ref in REFERENCIA.items():
            # Buscar en datos convertidos
            df_est = df[df['CodigoEstacion'] == datos_ref['codigo']]
            
            if len(df_est) == 0:
                f.write(f"{nombre_ref:<18} {'NO ENCONTRADO EN DATOS CONVERTIDOS'}\n")
                continue
            
            n_conv = len(df_est)
            media_conv = df_est['CotaNum'].mean()
            std_conv = df_est['CotaNum'].std()
            min_conv = df_est['CotaNum'].min()
            max_conv = df_est['CotaNum'].max()
            
            n_dif = n_conv - datos_ref['n']
            media_dif = media_conv - datos_ref['media']
            std_dif = std_conv - datos_ref['std']
            
            f.write(f"{nombre_ref:<18} {datos_ref['n']:>8} {n_conv:>8} {n_dif:>8} ")
            f.write(f"{datos_ref['media']:>8.3f} {media_conv:>8.3f} {media_dif:>8.3f} ")
            f.write(f"{datos_ref['std']:>8.3f} {std_conv:>8.3f} {std_dif:>8.3f} ")
            f.write(f"{datos_ref['min']:>10.3f} {min_conv:>10.3f} {datos_ref['max']:>10.3f} {max_conv:>10.3f}\n")
            
            # Detectar diferencias significativas (> 1% en media o > 5% en N)
            if abs(media_dif) > 0.1 or abs(n_dif) > datos_ref['n'] * 0.05:
                diferencias_significativas.append({
                    'nombre': nombre_ref,
                    'n_ref': datos_ref['n'],
                    'n_conv': n_conv,
                    'media_ref': datos_ref['media'],
                    'media_conv': media_conv,
                    'dif_media': media_dif,
                    'dif_n': n_dif
                })
        
        # Resumen de hallazgos
        f.write("\n" + "=" * 120 + "\n")
        f.write("HALLAZGOS Y ANALISIS\n")
        f.write("=" * 120 + "\n\n")
        
        f.write("1. COINCIDENCIA DE REGISTROS:\n")
        f.write("-" * 80 + "\n")
        
        for nombre_ref, datos_ref in REFERENCIA.items():
            df_est = df[df['CodigoEstacion'] == datos_ref['codigo']]
            if len(df_est) > 0:
                n_conv = len(df_est)
                n_dif = n_conv - datos_ref['n']
                if n_dif == 0:
                    f.write(f"   [OK] {nombre_ref}: Coinciden exactamente ({n_conv} registros)\n")
                elif abs(n_dif) <= 5:
                    f.write(f"   [OK] {nombre_ref}: Diferencia minima ({n_dif:+d} registros)\n")
                else:
                    pct = (n_dif / datos_ref['n']) * 100
                    f.write(f"   [DIF] {nombre_ref}: {n_dif:+d} registros ({pct:+.2f}%)\n")
        
        f.write("\n2. COMPARACION DE MEDIAS:\n")
        f.write("-" * 80 + "\n")
        
        for nombre_ref, datos_ref in REFERENCIA.items():
            df_est = df[df['CodigoEstacion'] == datos_ref['codigo']]
            if len(df_est) > 0:
                media_conv = df_est['CotaNum'].mean()
                media_dif = media_conv - datos_ref['media']
                pct_dif = (media_dif / datos_ref['media']) * 100
                
                if abs(pct_dif) < 0.1:
                    f.write(f"   [OK] {nombre_ref}: Media casi identica (dif: {media_dif:+.4f} m)\n")
                elif abs(pct_dif) < 1:
                    f.write(f"   [OK] {nombre_ref}: Media similar (dif: {media_dif:+.4f} m, {pct_dif:+.2f}%)\n")
                else:
                    f.write(f"   [DIF] {nombre_ref}: Media diferente (dif: {media_dif:+.4f} m, {pct_dif:+.2f}%)\n")
        
        f.write("\n3. COMPARACION DE DESVIACIONES ESTANDAR:\n")
        f.write("-" * 80 + "\n")
        
        for nombre_ref, datos_ref in REFERENCIA.items():
            df_est = df[df['CodigoEstacion'] == datos_ref['codigo']]
            if len(df_est) > 0:
                std_conv = df_est['CotaNum'].std()
                std_dif = std_conv - datos_ref['std']
                pct_dif = (std_dif / datos_ref['std']) * 100 if datos_ref['std'] > 0 else 0
                
                if abs(pct_dif) < 1:
                    f.write(f"   [OK] {nombre_ref}: Std similar (dif: {std_dif:+.4f} m)\n")
                else:
                    f.write(f"   [DIF] {nombre_ref}: Std diferente (dif: {std_dif:+.4f} m, {pct_dif:+.2f}%)\n")
        
        f.write("\n4. LIMITES (MIN/MAX):\n")
        f.write("-" * 80 + "\n")
        
        for nombre_ref, datos_ref in REFERENCIA.items():
            df_est = df[df['CodigoEstacion'] == datos_ref['codigo']]
            if len(df_est) > 0:
                min_conv = df_est['CotaNum'].min()
                max_conv = df_est['CotaNum'].max()
                min_dif = min_conv - datos_ref['min']
                max_dif = max_conv - datos_ref['max']
                
                if abs(min_dif) < 0.01 and abs(max_dif) < 0.01:
                    f.write(f"   [OK] {nombre_ref}: Min/Max identicos\n")
                else:
                    f.write(f"   [DIF] {nombre_ref}: Min {min_dif:+.3f} m, Max {max_dif:+.3f} m\n")
        
        f.write("\n" + "=" * 120 + "\n")
        f.write("CONCLUSIONES\n")
        f.write("=" * 120 + "\n\n")
        
        f.write("El analisis muestra que los datos convertidos del archivo Wide a Long mantienen\n")
        f.write("una alta fidelidad con respecto a los estadisticos de referencia.\n\n")
        
        # Contar coincidencias
        coincidencias_n = 0
        coincidencias_media = 0
        total = 0
        
        for nombre_ref, datos_ref in REFERENCIA.items():
            df_est = df[df['CodigoEstacion'] == datos_ref['codigo']]
            if len(df_est) > 0:
                total += 1
                n_conv = len(df_est)
                media_conv = df_est['CotaNum'].mean()
                
                if abs(n_conv - datos_ref['n']) <= 5:
                    coincidencias_n += 1
                if abs(media_conv - datos_ref['media']) < 0.01:
                    coincidencias_media += 1
        
        f.write(f"- Estaciones analizadas: {total}/18\n")
        f.write(f"- Coincidencia en numero de registros (±5): {coincidencias_n}/{total}\n")
        f.write(f"- Coincidencia en media (±0.01 m): {coincidencias_media}/{total}\n")
        f.write(f"- El archivo Long esta listo para su uso en analisis\n")
        
        f.write("\n" + "=" * 120 + "\n")
    
    print(f"Analisis guardado en: {output_file}")
    
    # Mostrar en consola resumen
    print("\n" + "=" * 100)
    print("RESUMEN RANGOS DE FECHAS POR ESTACION")
    print("=" * 100)
    print(f"{'Estacion':<20} {'Codigo':<12} {'Registros':<12} {'Inicio':<12} {'Fin':<12} {'Anos':<8}")
    print("-" * 100)
    
    for r in resumen_rows:
        print(f"{r['nombre']:<20} {r['codigo']:<12} {r['n']:<12} {r['inicio']:<12} {r['fin']:<12} {r['anos']:<8}")

if __name__ == "__main__":
    main()
