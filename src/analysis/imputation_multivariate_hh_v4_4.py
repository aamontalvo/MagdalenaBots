"""
H-H Multivariado v4.4 - Version optimizada con lookups
"""
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

INPUT_FILE = r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\backend\data\processed\imputation\Datos_Imputados_v4_3_Corrected.csv'
OUTPUT_DIR = r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\backend\data\processed\imputation'

ESTACIONES = [
    'SAN_PEDRITO', 'CALAMAR', 'TENERIFE', 'PLATO', 'MAGANGUE', 'BARBOSA',
    'COYONGAL', 'ARMENIA', 'RIO_NUEVO', 'LAS_PALOMAS', 'LAS_AGUADAS',
    'EL_BANCO', 'PENONCITO', 'LA_GLORIA', 'GAMARRA_AUT', 'EL_CONTENTO',
    'SITIO_NUEVO', 'PUERTO_WILCHES'
]

R2_UMBRAL = 0.75
MIN_N = 30

print("=" * 70)
print("H-H MULTIVARIADO v4.4")
print("=" * 70)

# 1. Cargar datos
print("\n[1/5] Cargando datos...")
df = pd.read_csv(INPUT_FILE, parse_dates=['Fecha'])
print(f"  Total: {len(df):,} | missForest: {(df['Metodo'] == 'L3_missForest').sum():,}")

df_orig = df[df['Metodo'] == 'Original'].copy()

# Pivot wide de originales
orig_wide = df_orig.pivot_table(index='Fecha', columns='NombreEstacion', values='Cota', aggfunc='first')
orig_wide = orig_wide.reindex(columns=ESTACIONES)

# Rango historico por estacion
rangos = {est: (df_orig[df_orig['NombreEstacion'] == est]['Cota'].min(),
                df_orig[df_orig['NombreEstacion'] == est]['Cota'].max())
          for est in ESTACIONES}

# 2. Lookup rapido: (fecha, estacion) -> cota (todos los datos, no solo originales)
print("\n[2/5] Creando lookup de datos disponibles...")
all_wide = df.pivot_table(index='Fecha', columns='NombreEstacion', values='Cota', aggfunc='first')
all_wide = all_wide.reindex(columns=ESTACIONES)

# 3. Pre-calcular modelos H-H
print("\n[3/5] Pre-calculando modelos H-H ({} pares)...".format(len(ESTACIONES) * (len(ESTACIONES)-1)))
modelos_hh = {}

for objetivo in ESTACIONES:
    for donante in ESTACIONES:
        if objetivo == donante:
            continue
        concurrent = orig_wide[[objetivo, donante]].dropna()
        if len(concurrent) < MIN_N:
            continue
        y = concurrent[objetivo].values
        x = concurrent[donante].values
        X = np.column_stack([x**2, x, np.ones(len(x))])
        try:
            coefs, *_ = np.linalg.lstsq(X, y, rcond=None)
            y_pred = coefs[0]*x**2 + coefs[1]*x + coefs[2]
            ss_res = ((y - y_pred)**2).sum()
            ss_tot = ((y - y.mean())**2).sum()
            r2 = 1 - ss_res/ss_tot if ss_tot > 0 else 0
            if R2_UMBRAL <= r2 <= 1.0:
                modelos_hh[(objetivo, donante)] = {'a': coefs[0], 'b': coefs[1], 'c': coefs[2], 'r2': r2}
        except:
            continue

print(f"  Modelos validos: {len(modelos_hh)}")
print("  Top 10:")
for (obj, don), m in sorted(modelos_hh.items(), key=lambda x: -x[1]['r2'])[:10]:
    print(f"    {obj:15s} <- {don:15s}: R2={m['r2']:.3f}")

# 4. Vectorizar imputacion
print("\n[4/5] Imputando missForest (vectorizado)...")

# Identificar filas missForest
mf_rows = df[df['Metodo'] == 'L3_missForest'].copy()
n_total = len(mf_rows)
print(f"  Total missForest a imputar: {n_total:,}")

# Para cada estacion, pre-computar que donantes tiene disponibles
donantes_por_estacion = {est: [d for (o, d), m in modelos_hh.items() if o == est] for est in ESTACIONES}

# Imputacion vectorizada
imputaciones = {}
n_multihh = 0
n_fallback = 0

for est in ESTACIONES:
    donantes = donantes_por_estacion[est]
    if not donantes:
        continue

    est_mf = mf_rows[mf_rows['NombreEstacion'] == est]
    if len(est_mf) == 0:
        continue

    fechas_mf = est_mf['Fecha'].values

    for donante in donantes:
        modelo = modelos_hh[(est, donante)]
        # Valores del donante en las fechas missForest
        vals_donante = all_wide.loc[pd.DatetimeIndex(fechas_mf), donante].values
        mask_valid = ~np.isnan(vals_donante)

        if mask_valid.sum() == 0:
            continue

        x = vals_donante[mask_valid]
        pred = modelo['a'] * x**2 + modelo['b'] * x + modelo['c']

        # Hard rule
        r_min, r_max = rangos[est]
        pred = np.clip(pred, r_min, r_max)

        fechas_valid = fechas_mf[mask_valid]
        for i, fecha in enumerate(fechas_valid):
            key = (est, fecha)
            if key not in imputaciones:
                imputaciones[key] = {'preds': [], 'pesos': []}
            imputaciones[key]['preds'].append(pred[i])
            imputaciones[key]['pesos'].append(modelo['r2'])

# Aplicar imputaciones al DataFrame
df_mhh = df.copy()
for (est, fecha), data in imputaciones.items():
    if len(data['preds']) > 0:
        final = np.average(data['preds'], weights=data['pesos'])
        mask = (df_mhh['NombreEstacion'] == est) & (df_mhh['Fecha'] == fecha) & (df_mhh['Metodo'] == 'L3_missForest')
        if mask.sum() > 0:
            df_mhh.loc[mask, 'Cota'] = final
            df_mhh.loc[mask, 'Metodo'] = 'L4_Multivariate_HH'
            df_mhh.loc[mask, 'Nivel_Imputacion'] = 4
            n_multihh += mask.sum()

# Contar fallbacks (missForest que no se pudieron imputar)
n_fallback = (df_mhh['Metodo'] == 'L3_missForest').sum()

print(f"\n  Multivariate HH: {n_multihh:,} ({n_multihh/n_total*100:.1f}%)")
print(f"  Fallback:        {n_fallback:,} ({n_fallback/n_total*100:.1f}%)")

# 5. Comparar
print("\n[5/5] Comparando missForest vs Multivariate HH...")
print("=" * 70)

comps = []
for est in ESTACIONES:
    est_mf = df[(df['NombreEstacion'] == est) & (df['Metodo'] == 'L3_missForest')]['Cota'].values
    est_mhh = df_mhh[(df_mhh['NombreEstacion'] == est) & (df_mhh['Metodo'] == 'L4_Multivariate_HH')]['Cota'].values

    n_mf = len(est_mf)
    n_mhh = len(est_mhh)
    if n_mf == 0:
        continue

    stats = {
        'estacion': est, 'n_missforest': n_mf, 'n_multihh': n_mhh,
        'missforest_mean': est_mf.mean(), 'missforest_std': est_mf.std(),
        'missforest_min': est_mf.min(), 'missforest_max': est_mf.max(),
        'mhh_mean': est_mhh.mean() if n_mhh > 0 else np.nan,
        'mhh_std': est_mhh.std() if n_mhh > 0 else np.nan,
        'mhh_min': est_mhh.min() if n_mhh > 0 else np.nan,
        'mhh_max': est_mhh.max() if n_mhh > 0 else np.nan,
    }
    stats['diff_mean'] = stats['mhh_mean'] - stats['missforest_mean'] if n_mhh > 0 else np.nan
    stats['diff_std'] = stats['mhh_std'] - stats['missforest_std'] if n_mhh > 0 else np.nan
    comps.append(stats)

    print(f"\n{est}:")
    print(f"  missForest:     mean={stats['missforest_mean']:.3f}, std={stats['missforest_std']:.3f}, range=[{stats['missforest_min']:.3f}, {stats['missforest_max']:.3f}] ({n_mf})")
    print(f"  MultivariateHH: mean={stats['mhh_mean']:.3f}, std={stats['mhh_std']:.3f}, range=[{stats['mhh_min']:.3f}, {stats['mhh_max']:.3f}] ({n_mhh})")
    print(f"  Dif:            mean={stats['diff_mean']:+.3f}, std={stats['diff_std']:+.3f}")

pd.DataFrame(comps).to_csv(f'{OUTPUT_DIR}/comparacion_missForest_vs_MultivariateHH.csv', index=False)
print(f"\n  Guardado: comparacion_missForest_vs_MultivariateHH.csv")

# Guardar modelos
modelos_df = [{'objetivo': k[0], 'donante': k[1], 'R2': v['r2'], 'a': v['a'], 'b': v['b'], 'c': v['c']}
              for k, v in modelos_hh.items()]
pd.DataFrame(modelos_df).to_csv(f'{OUTPUT_DIR}/tabla_modelos_multivariate_hh.csv', index=False)
print(f"  Guardado: tabla_modelos_multivariate_hh.csv")

# Guardar dataset
df_mhh.to_csv(f'{OUTPUT_DIR}/Datos_Imputados_v4_4_Multivariate_HH.csv', index=False)
print(f"  Guardado: Datos_Imputados_v4_4_Multivariate_HH.csv")

print("\n" + "=" * 70)
print("H-H MULTIVARIADO v4.4 COMPLETADO")
print("=" * 70)
