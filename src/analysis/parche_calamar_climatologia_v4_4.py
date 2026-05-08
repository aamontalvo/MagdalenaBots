"""
Parche v4.4: Reemplazar bloque CALAMAR 1969-12-01 -> 1970-01-30 (61 dias)
de missForest constante (2.617m) con patron climatologico estacional ajustado.
"""
import pandas as pd
import numpy as np

INPUT_FILE = r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\backend\data\processed\imputation\Datos_Imputados_v4_3_Corrected.csv'
OUTPUT_FILE = r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\backend\data\processed\imputation\Datos_Imputados_v4_4_ClimatologyPatch.csv'

print("=" * 70)
print("PARCHE v4.4 - CALAMAR Climatologia Estacional")
print("=" * 70)

# 1. Cargar datos
df = pd.read_csv(INPUT_FILE, parse_dates=['Fecha'])
print(f"\nDataset cargado: {len(df):,} registros")

# 2. Identificar bloque a reemplazar
bloque_ini = pd.Timestamp('1969-12-01')
bloque_fin = pd.Timestamp('1970-01-30')
mask_bloque = (df['NombreEstacion'] == 'CALAMAR') & (df['Fecha'] >= bloque_ini) & (df['Fecha'] <= bloque_fin) & (df['Metodo'] == 'L3_missForest')

bloque_actual = df[mask_bloque].copy().sort_values('Fecha')
n_bloque = len(bloque_actual)
print(f"Bloque missForest CALAMAR: {n_bloque} dias ({bloque_ini.strftime('%Y-%m-%d')} a {bloque_fin.strftime('%Y-%m-%d')})")
print(f"  missForest actual: mean={bloque_actual['Cota'].mean():.3f}m, std={bloque_actual['Cota'].std():.6f}m")

# 3. Calcular climatologia diaria de CALAMAR (solo originales)
cal_orig = df[(df['NombreEstacion'] == 'CALAMAR') & (df['Metodo'] == 'Original')].copy()
cal_orig['mes_dia'] = cal_orig['Fecha'].dt.strftime('%m-%d')

# Excluir 29-feb para climatologia consistente
cal_orig = cal_orig[cal_orig['mes_dia'] != '02-29']

climatologia = cal_orig.groupby('mes_dia')['Cota'].agg(['mean', 'std', 'min', 'max', 'count']).reset_index()
climatologia = climatologia.rename(columns={'mean': 'cota_media', 'std': 'cota_std', 'min': 'cota_min', 'max': 'cota_max'})
print(f"\nClimatologia calculada: {len(climatologia)} dias (excluyendo 29-feb)")
print(f"  n original CALAMAR: {len(cal_orig):,}")

# 4. Generar valores climatologicos para el bloque
bloque_fechas = bloque_actual['Fecha'].values
mes_dias = pd.to_datetime(bloque_fechas).strftime('%m-%d')

valores_clima = []
for md in mes_dias:
    row = climatologia[climatologia['mes_dia'] == md]
    if len(row) > 0:
        valores_clima.append(row['cota_media'].values[0])
    else:
        # Fallback para 29-feb (no deberia pasar en dic-ene)
        valores_clima.append(np.nan)

valores_clima = np.array(valores_clima)
media_clima_bloque = np.mean(valores_clima)
media_missforest = bloque_actual['Cota'].mean()

# Ajustar: centrar climatologia en la media de missForest para preservar
# la señal de nivel medio de ese periodo, pero con variabilidad estacional
ajuste = media_missforest - media_clima_bloque
valores_finales = valores_clima + ajuste

# Hard rule: clip al rango historico original de CALAMAR
rango_min = cal_orig['Cota'].min()
rango_max = cal_orig['Cota'].max()
valores_finales = np.clip(valores_finales, rango_min, rango_max)

print(f"\nAjuste climatologico:")
print(f"  Media climatologia en bloque: {media_clima_bloque:.3f}m")
print(f"  Media missForest:             {media_missforest:.3f}m")
print(f"  Ajuste aplicado:              {ajuste:+.3f}m")
print(f"  Media final:                  {np.mean(valores_finales):.3f}m")
print(f"  STD final:                    {np.std(valores_finales):.3f}m")
print(f"  Rango final:                  [{np.min(valores_finales):.3f}, {np.max(valores_finales):.3f}]m")
print(f"  Rango historico original:     [{rango_min:.3f}, {rango_max:.3f}]m")

# 5. Verificar que los valores finales esten dentro del rango historico
assert np.min(valores_finales) >= rango_min, "Hard rule violada: valor por debajo del minimo historico"
assert np.max(valores_finales) <= rango_max, "Hard rule violada: valor por encima del maximo historico"
print(f"\n[PASS] Hard rule verificada: todos los valores dentro del rango historico")

# 6. Aplicar reemplazo
df_v44 = df.copy()
for i, fecha in enumerate(bloque_fechas):
    mask = (df_v44['NombreEstacion'] == 'CALAMAR') & (df_v44['Fecha'] == fecha) & (df_v44['Metodo'] == 'L3_missForest')
    if mask.sum() > 0:
        df_v44.loc[mask, 'Cota'] = valores_finales[i]
        df_v44.loc[mask, 'Metodo'] = 'L4_Climatologia_Estacional'
        df_v44.loc[mask, 'Nivel_Imputacion'] = 4

# 7. Verificacion final
bloque_nuevo = df_v44[(df_v44['NombreEstacion'] == 'CALAMAR') & (df_v44['Fecha'] >= bloque_ini) & (df_v44['Fecha'] <= bloque_fin)]
print(f"\nVerificacion post-parche:")
print(f"  Metodos en bloque: {bloque_nuevo['Metodo'].unique().tolist()}")
print(f"  Valores: mean={bloque_nuevo['Cota'].mean():.3f}, std={bloque_nuevo['Cota'].std():.3f}, min={bloque_nuevo['Cota'].min():.3f}, max={bloque_nuevo['Cota'].max():.3f}")

# 8. Guardar
df_v44.to_csv(OUTPUT_FILE, index=False)
print(f"\n[OK] Dataset v4.4 guardado: Datos_Imputados_v4_4_ClimatologyPatch.csv")

# 9. Resumen de metodos en v4.4
print(f"\nResumen de metodos en v4.4:")
print(df_v44['Metodo'].value_counts().to_string())

# 10. Guardar detalle del parche
parche_df = pd.DataFrame({
    'Fecha': bloque_fechas,
    'mes_dia': mes_dias,
    'missForest': bloque_actual['Cota'].values,
    'climatologia_media': valores_clima,
    'ajuste': ajuste,
    'v4_4_final': valores_finales
})
parche_df.to_csv(r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\backend\data\processed\imputation\detalle_parche_calamar_v4_4.csv', index=False)
print(f"\n[OK] Detalle del parche guardado: detalle_parche_calamar_v4_4.csv")

print("\n" + "=" * 70)
print("PARCHE v4.4 COMPLETADO")
print("=" * 70)
