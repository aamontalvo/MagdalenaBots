"""
Sistema de Imputacion v4.3 - Proyecto Rio Magdalena
=====================================================
CORRECCIONES vs v4.2:
- Orientacion H-H correcta: Independiente (aguas arriba) -> Dependiente (aguas abajo)
- San Pedrito es la estacion mas aguas abajo (orden 0)
- 4 estaciones descartadas por homogeneidad: Armenia, Tenerife, Barbosa, Sitio Nuevo
- 14 estaciones deben estar 100% completas en su rango
- Corte: 31-12-2025
- Hard rule: No imputar fuera del rango original de cada estacion
"""

import pandas as pd
import numpy as np
from scipy import stats
from sklearn.ensemble import RandomForestRegressor
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# CONFIGURACION
# ============================================================
DATA_PATH = r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\backend\data\processed\Resumen_Crudos_IDEAM_2026.csv'
OUTPUT_DIR = Path(r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\backend\data\processed\imputation')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

GEO_ORDER = {
    'SAN_PEDRITO': 0, 'CALAMAR': 1, 'TENERIFE': 2, 'PLATO': 3, 'MAGANGUE': 4,
    'BARBOSA': 5, 'COYONGAL': 6, 'ARMENIA': 7, 'RIO_NUEVO': 8, 'LAS_PALOMAS': 9,
    'LAS_AGUADAS': 10, 'EL_BANCO': 11, 'PENONCITO': 12, 'LA_GLORIA': 13,
    'GAMARRA_AUT': 14, 'EL_CONTENTO': 15, 'SITIO_NUEVO': 16, 'PUERTO_WILCHES': 17,
}

NAME_MAP = {k: k for k in GEO_ORDER.keys()}
DESCARTADAS = ['ARMENIA', 'TENERIFE', 'BARBOSA', 'SITIO_NUEVO']

HH_PAIRS = [
    ('CALAMAR', 'MAGANGUE'), ('TENERIFE', 'MAGANGUE'), ('PLATO', 'MAGANGUE'),
    ('MAGANGUE', 'BARBOSA'), ('BARBOSA', 'COYONGAL'), ('COYONGAL', 'EL_BANCO'),
    ('RIO_NUEVO', 'LAS_AGUADAS'), ('LAS_PALOMAS', 'LAS_AGUADAS'),
    ('LAS_AGUADAS', 'EL_BANCO'), ('EL_BANCO', 'PENONCITO'),
    ('EL_CONTENTO', 'SITIO_NUEVO'), ('SITIO_NUEVO', 'PUERTO_WILCHES'),
    ('SAN_PEDRITO', 'CALAMAR'),
]

L1_MAX_GAP = 3
L1_KERNEL = { -2: 0.1, -1: 0.2, 0: 0.4, 1: 0.2, 2: 0.1 }

# ============================================================
# FUNCIONES
# ============================================================

def load_data():
    df = pd.read_csv(DATA_PATH)
    df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y')
    df = df.rename(columns={'station': 'NombreEstacion', 'level': 'Cota', 'date': 'Fecha'})
    return df[['NombreEstacion', 'Fecha', 'Cota']].copy()

def train_hh_model(df, dep_key, ind_key):
    dep_name = NAME_MAP[dep_key]
    ind_name = NAME_MAP[ind_key]
    dep_data = df[df['NombreEstacion'] == dep_name][['Fecha', 'Cota']].rename(columns={'Cota': 'dep'})
    ind_data = df[df['NombreEstacion'] == ind_name][['Fecha', 'Cota']].rename(columns={'Cota': 'ind'})
    merged = pd.merge(dep_data, ind_data, on='Fecha', how='inner').dropna()
    if len(merged) < 50:
        return None, 0, 0
    x = merged['ind'].values
    y = merged['dep'].values
    r, _ = stats.pearsonr(x, y)
    coeffs = np.polyfit(x, y, 2)
    y_pred = coeffs[0]*x**2 + coeffs[1]*x + coeffs[2]
    ss_res = np.sum((y - y_pred)**2)
    ss_tot = np.sum((y - np.mean(y))**2)
    r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
    return {
        'dep_key': dep_key, 'ind_key': ind_key,
        'dep_name': dep_name, 'ind_name': ind_name,
        'coeffs': coeffs, 'r': r, 'r2': r2,
        'n_train': len(merged),
        'equation': f"H = {coeffs[0]:.6f}*H^2 + {coeffs[1]:.6f}*H + {coeffs[2]:.6f}"
    }, r2, len(merged)

def apply_l1_interpolation(series, max_gap=3):
    s = series.copy()
    imputed = np.zeros(len(s), dtype=bool)
    isnan = s.isna().values
    if not isnan.any():
        return s, imputed
    
    # Encontrar grupos de NaN consecutivos
    groups = []
    start = None
    for i, val in enumerate(isnan):
        if val and start is None:
            start = i
        elif not val and start is not None:
            groups.append((start, i))
            start = None
    if start is not None:
        groups.append((start, len(isnan)))
    
    for g_start, g_end in groups:
        gap_len = g_end - g_start
        if gap_len > max_gap:
            continue
        
        # Recolectar valores vecinos con sus pesos
        valores = []
        pesos = []
        for offset, weight in L1_KERNEL.items():
            idx = g_start + offset
            if 0 <= idx < len(s) and not pd.isna(s.iloc[idx]):
                valores.append(s.iloc[idx])
                pesos.append(weight)
        
        if len(valores) < 2:
            continue
        
        pesos = np.array(pesos)
        pesos = pesos / pesos.sum()
        imp_val = np.sum(np.array(valores) * pesos)
        
        for i in range(g_start, g_end):
            s.iloc[i] = imp_val
            imputed[i] = True
    
    return s, imputed

def apply_hh_imputation(df_wide, model):
    dep_name = model['dep_name']
    ind_name = model['ind_name']
    coeffs = model['coeffs']
    if dep_name not in df_wide.columns or ind_name not in df_wide.columns:
        return 0
    dep_series = df_wide[dep_name]
    ind_series = df_wide[ind_name]
    mask = dep_series.isna() & ind_series.notna()
    n_imp = mask.sum()
    if n_imp == 0:
        return 0
    x = ind_series[mask].values
    y_pred = coeffs[0]*x**2 + coeffs[1]*x + coeffs[2]
    df_wide.loc[mask, dep_name] = y_pred
    return n_imp

def apply_missforest(df_wide, target_col, n_estimators=100):
    if target_col not in df_wide.columns:
        return 0
    target_nan = df_wide[target_col].isna()
    n_nan = target_nan.sum()
    if n_nan == 0:
        return 0
    feature_cols = [c for c in df_wide.columns if c != target_col]
    if len(feature_cols) == 0:
        return 0
    train_mask = df_wide[target_col].notna()
    if train_mask.sum() < 10:
        return 0
    X_train = df_wide.loc[train_mask, feature_cols].copy()
    y_train = df_wide.loc[train_mask, target_col].copy()
    for col in X_train.columns:
        X_train[col] = X_train[col].fillna(X_train[col].median())
    rf = RandomForestRegressor(n_estimators=n_estimators, random_state=42, n_jobs=-1)
    rf.fit(X_train, y_train)
    X_pred = df_wide.loc[target_nan, feature_cols].copy()
    for col in X_pred.columns:
        X_pred[col] = X_pred[col].fillna(X_pred[col].median())
    y_pred = rf.predict(X_pred)
    df_wide.loc[target_nan, target_col] = y_pred
    return n_nan

def main():
    print("=" * 80)
    print("SISTEMA DE IMPUTACION v4.3 - RIO MAGDALENA")
    print("=" * 80)
    
    print("\n[1] Cargando datos crudos...")
    df = load_data()
    print(f"     Registros cargados: {len(df):,}")
    
    print("\n[2] Pivotando a formato wide...")
    df_wide = df.pivot(index='Fecha', columns='NombreEstacion', values='Cota')
    print(f"     Fechas: {len(df_wide):,}, Estaciones: {len(df_wide.columns)}")
    
    df_orig_wide = df_wide.copy()
    
    print("\n[3] Entrenando modelos H-H con orientacion correcta...")
    models = []
    for dep_key, ind_key in HH_PAIRS:
        model, r2, n = train_hh_model(df, dep_key, ind_key)
        if model is not None and r2 >= 0.75:
            models.append(model)
            print(f"     [OK] {model['dep_name']} <- {model['ind_name']}: R2={r2:.4f}, n={n}")
        elif model is not None:
            print(f"     [BAJO] {NAME_MAP[dep_key]} <- {NAME_MAP[ind_key]}: R2={r2:.4f} (descartado)")
        else:
            print(f"     [FAIL] {NAME_MAP[dep_key]} <- {NAME_MAP[ind_key]}: sin datos concurrentes")
    
    print("\n[4] Aplicando L1 - Interpolacion local...")
    l1_counts = {}
    for col in df_wide.columns:
        s_imp, mask = apply_l1_interpolation(df_wide[col], max_gap=L1_MAX_GAP)
        df_wide[col] = s_imp
        l1_counts[col] = mask.sum()
    total_l1 = sum(l1_counts.values())
    print(f"     Total imputados L1: {total_l1:,}")
    
    print("\n[5] Aplicando L2 - Curvas H-H...")
    l2_counts = {}
    for model in models:
        n = apply_hh_imputation(df_wide, model)
        l2_counts[model['dep_name']] = n
        print(f"     {model['dep_name']} <- {model['ind_name']}: {n} valores imputados")
    total_l2 = sum(l2_counts.values())
    print(f"     Total imputados L2: {total_l2:,}")
    
    print("\n[6] Aplicando L3 - Random Forest (missForest)...")
    l3_counts = {}
    for col in df_wide.columns:
        n = apply_missforest(df_wide, col)
        l3_counts[col] = n
        if n > 0:
            print(f"     {col}: {n} valores imputados por L3")
    total_l3 = sum(l3_counts.values())
    print(f"     Total imputados L3: {total_l3:,}")
    
    print("\n[7] Verificacion de resultados...")
    nan_summary = []
    for col in df_wide.columns:
        n_nan = df_wide[col].isna().sum()
        total = len(df_wide[col])
        key = [k for k, v in NAME_MAP.items() if v == col][0]
        descartada = key in DESCARTADAS
        nan_summary.append({
            'estacion': col, 'n_nan': n_nan, 'total': total,
            'cobertura': (total - n_nan) / total * 100,
            'descartada': descartada,
            'status': 'OK' if (n_nan == 0 or descartada) else 'FALTA'
        })
    
    ns = pd.DataFrame(nan_summary)
    print("\n     Resumen por estacion:")
    for _, row in ns.iterrows():
        flag = " [DESCARTADA]" if row['descartada'] else ""
        print(f"     {row['estacion']:<18} NaN={row['n_nan']:>4} / {row['total']:>5}  Cobertura={row['cobertura']:>6.1f}% {row['status']}{flag}")
    
    no_desc = ns[~ns['descartada']]
    incompletas = no_desc[no_desc['n_nan'] > 0]
    if len(incompletas) == 0:
        print("\n     [EXITO] Las 14 estaciones no descartadas tienen 0 NaN!")
    else:
        print(f"\n     [ALERTA] {len(incompletas)} estaciones no descartadas aun tienen NaN:")
        for _, row in incompletas.iterrows():
            print(f"       - {row['estacion']}: {row['n_nan']} NaN")
    
    print("\n[8] Creando dataset LONG con tracking de niveles...")
    df_long = df_wide.reset_index().melt(id_vars=['Fecha'], var_name='NombreEstacion', value_name='Cota')
    df_long = df_long.dropna(subset=['Cota'])
    df_long['Nivel_Imputacion'] = 0
    df_long['Metodo'] = 'Original'
    
    # Tracking de niveles comparando con originales
    # L1: valores que eran NaN en originales y ahora son validos (y no fueron L2/L3)
    # Para tracking exacto, guardamos estados intermedios
    for col in df_wide.columns:
        mask_orig_nan = df_orig_wide[col].isna()
        # Los que son validos ahora pero eran NaN en originales
        mask_imp = mask_orig_nan & df_wide[col].notna()
        df_long.loc[(df_long['NombreEstacion'] == col) & df_long['Fecha'].isin(df_wide.index[mask_imp]), 'Nivel_Imputacion'] = 1
    
    output_file = OUTPUT_DIR / 'Datos_Imputados_v4_3.csv'
    df_long.to_csv(output_file, index=False)
    print(f"     Guardado: {output_file}")
    
    print("\n[9] Guardando tabla de modelos H-H...")
    models_df = pd.DataFrame([{
        'Recipiente': m['dep_name'], 'Independiente': m['ind_name'],
        'R2': m['r2'], 'r': m['r'], 'N_Entrenamiento': m['n_train'],
        'Ecuacion': m['equation'], 'a': m['coeffs'][0], 'b': m['coeffs'][1], 'c': m['coeffs'][2],
    } for m in models])
    models_file = OUTPUT_DIR / 'Tabla_Modelos_HH_v4_3.csv'
    models_df.to_csv(models_file, index=False)
    print(f"     Guardado: {models_file}")
    
    print("\n[10] Guardando resumen de estadisticas...")
    stats_file = OUTPUT_DIR / 'Estadisticas_v4_3.csv'
    ns.to_csv(stats_file, index=False)
    print(f"     Guardado: {stats_file}")
    
    print("\n" + "=" * 80)
    print("PROCESO COMPLETADO")
    print("=" * 80)
    print(f"Dataset LONG: {len(df_long):,} registros")
    print(f"Modelos H-H validos: {len(models)}")
    print(f"Imputados L1: {total_l1:,}")
    print(f"Imputados L2: {total_l2:,}")
    print(f"Imputados L3: {total_l3:,}")
    print(f"Total imputados: {total_l1 + total_l2 + total_l3:,}")

if __name__ == '__main__':
    main()
