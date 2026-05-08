"""
SAITS v4.4 - ENTRENAMIENTO + INFERENCIA COMPLETO
=================================================
Modelo grande: d_model=128, n_layers=2, n_heads=4, 50 epochs
Este script entrena SAITS e inmediatamente hace inferencia y guarda resultados.

INSTRUCCIONES DE EJECUCION:
1. Abrir Visual Studio Code
2. Abrir terminal integrada (Ctrl+`) 
3. Asegurarse de estar en el entorno Python correcto (ver abajo)
4. Ejecutar: python src/analysis/saits_v4_4_train_and_infer.py
5. Esperar ~10-15 minutos (entrenamiento 50 epochs en CPU + inferencia)
6. Revisar resultados en backend/data/processed/imputation/

VERIFICACION DEL ENTORNO:
  python -c "import pypots; print(pypots.__version__)"
  Debe mostrar: 1.5 (o similar)
  
Si pypots no esta instalado:
  pip install pypots
"""

import pandas as pd
import numpy as np
import warnings
import os
import time
warnings.filterwarnings('ignore')

import torch
from pypots.imputation import SAITS

# ---------------------------------------------------------------------------
# CONFIGURACION
# ---------------------------------------------------------------------------
INPUT_FILE = r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\backend\data\processed\imputation\Datos_Imputados_v4_3_Corrected.csv'
OUTPUT_DIR = r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\backend\data\processed\imputation'
MODEL_SAVE_DIR = f'{OUTPUT_DIR}/saits_model_v44'

ESTACIONES = [
    'SAN_PEDRITO', 'CALAMAR', 'TENERIFE', 'PLATO', 'MAGANGUE', 'BARBOSA',
    'COYONGAL', 'ARMENIA', 'RIO_NUEVO', 'LAS_PALOMAS', 'LAS_AGUADAS',
    'EL_BANCO', 'PENONCITO', 'LA_GLORIA', 'GAMARRA_AUT', 'EL_CONTENTO',
    'SITIO_NUEVO', 'PUERTO_WILCHES'
]

# Hiperparametros MODELO GRANDE (para evitar colapso a constantes)
WINDOW_SIZE = 90
STRIDE = 30
D_MODEL = 128
N_LAYERS = 2
N_HEADS = 4
D_K = 32
D_V = 32
D_FFN = 256
DROPOUT = 0.1
EPOCHS = 50
BATCH_SIZE = 32
CHUNK_SIZE = 50  # ventanas por chunk durante inferencia

# ---------------------------------------------------------------------------
# FUNCIONES AUXILIARES
# ---------------------------------------------------------------------------
def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

# ---------------------------------------------------------------------------
# 1. PREPARAR DATOS
# ---------------------------------------------------------------------------
log("=" * 70)
log("SAITS v4.4 - ENTRENAMIENTO + INFERENCIA COMPLETO")
log("=" * 70)

log("Paso 1/8: Cargando datos v4.3...")
df = pd.read_csv(INPUT_FILE, parse_dates=['Fecha'])
log(f"  Total registros: {len(df):,}")
log(f"  missForest (L3): {(df['Metodo'] == 'L3_missForest').sum():,}")

# Pivot wide
df_pivot = df.copy()
df_pivot.loc[df_pivot['Metodo'] == 'L3_missForest', 'Cota'] = np.nan
wide_df = df_pivot.pivot_table(index='Fecha', columns='NombreEstacion', values='Cota', aggfunc='first')
wide_df = wide_df.reindex(columns=ESTACIONES)

mf_df = df[df['Metodo'] == 'L3_missForest'].pivot_table(
    index='Fecha', columns='NombreEstacion', values='Metodo', aggfunc='count'
)
mf_df = mf_df.reindex(columns=ESTACIONES).fillna(0)
mf_df = (mf_df > 0).astype(int)

fechas = np.sort(df['Fecha'].unique())
wide_df = wide_df.reindex(pd.DatetimeIndex(fechas))
mf_df = mf_df.reindex(pd.DatetimeIndex(fechas)).fillna(0).astype(int)

n_days = len(wide_df)
n_features = len(ESTACIONES)
log(f"  Dias: {n_days}, Estaciones: {n_features}")

# ---------------------------------------------------------------------------
# 2. CREAR VENTANAS
# ---------------------------------------------------------------------------
log("Paso 2/8: Creando ventanas deslizantes...")
values = wide_df.values
mask_missing = (~np.isnan(values)).astype(int)

windows = []
masks = []
window_dates = []
for start in range(0, n_days - WINDOW_SIZE + 1, STRIDE):
    end = start + WINDOW_SIZE
    window = values[start:end, :]
    mask = mask_missing[start:end, :]
    if np.isnan(window).sum() < WINDOW_SIZE * n_features * 0.95:
        windows.append(window)
        masks.append(mask)
        window_dates.append((start, end))

X = np.array(windows)
missing_mask = np.array(masks)
n_samples = X.shape[0]
log(f"  Ventanas: {n_samples}, Formato: {X.shape}")

# Normalizar (z-score por feature)
log("  Normalizando (z-score)...")
feature_means = []
feature_stds = []
for f in range(n_features):
    valid = X[:, :, f][~np.isnan(X[:, :, f])]
    mu = valid.mean() if len(valid) > 0 else 0
    sigma = valid.std() if len(valid) > 0 and valid.std() > 0 else 1.0
    feature_means.append(mu)
    feature_stds.append(sigma)
    X[:, :, f] = (X[:, :, f] - mu) / sigma

feature_means = np.array(feature_means)
feature_stds = np.array(feature_stds)
X_filled = np.nan_to_num(X, nan=0.0)

dataset_for_training = {
    'X': X_filled,
    'missing_mask': missing_mask
}

# ---------------------------------------------------------------------------
# 3. VERIFICAR SI EXISTE MODELO PREVIO GRANDE
# ---------------------------------------------------------------------------
log("Paso 3/8: Verificando modelo previo...")
model_path = None
if os.path.exists(MODEL_SAVE_DIR):
    pypots_files = []
    for root, dirs, files in os.walk(MODEL_SAVE_DIR):
        for f in files:
            if f.endswith('.pypots'):
                pypots_files.append(os.path.join(root, f))
    if pypots_files:
        model_path = sorted(pypots_files)[-1]
        log(f"  Modelo previo encontrado: {model_path}")

# ---------------------------------------------------------------------------
# 4. ENTRENAR O CARGAR MODELO
# ---------------------------------------------------------------------------
log("Paso 4/8: Inicializando SAITS...")
saits = SAITS(
    n_steps=WINDOW_SIZE,
    n_features=n_features,
    n_layers=N_LAYERS,
    d_model=D_MODEL,
    n_heads=N_HEADS,
    d_k=D_K,
    d_v=D_V,
    d_ffn=D_FFN,
    dropout=DROPOUT,
    epochs=EPOCHS,
    batch_size=BATCH_SIZE,
    patience=10,
    device='cuda' if torch.cuda.is_available() else 'cpu',
    saving_path=MODEL_SAVE_DIR,
    model_saving_strategy='best',
    verbose=True,
)
log(f"  Parametros: {sum(p.numel() for p in saits.model.parameters()):,}")
log(f"  Device: {saits.device}")

if model_path and os.path.exists(model_path):
    log("  Cargando modelo previo...")
    saits.load(model_path)
    log("  Modelo cargado.")
else:
    log(f"  Entrenando {EPOCHS} epochs... (~5-8 min en CPU)")
    t0 = time.time()
    saits.fit(dataset_for_training)
    log(f"  Entrenamiento completado en {time.time()-t0:.0f} segundos")

# ---------------------------------------------------------------------------
# 5. IMPUTAR POR CHUNKS
# ---------------------------------------------------------------------------
log("Paso 5/8: Imputando por chunks...")
t0 = time.time()
n_chunks = (n_samples + CHUNK_SIZE - 1) // CHUNK_SIZE
X_imputed_all = np.zeros((n_samples, WINDOW_SIZE, n_features), dtype=np.float32)

for ci in range(n_chunks):
    chunk_start = ci * CHUNK_SIZE
    chunk_end = min(chunk_start + CHUNK_SIZE, n_samples)
    log(f"  Chunk {ci+1}/{n_chunks} ({chunk_start}-{chunk_end})...")
    chunk_data = {
        'X': X_filled[chunk_start:chunk_end],
        'missing_mask': missing_mask[chunk_start:chunk_end]
    }
    chunk_imputed = saits.impute(chunk_data)
    X_imputed_all[chunk_start:chunk_end] = chunk_imputed

log(f"  Inferencia completada en {time.time()-t0:.0f} segundos")

# ---------------------------------------------------------------------------
# 6. DESNORMALIZAR Y RECONSTRUIR SERIE
# ---------------------------------------------------------------------------
log("Paso 6/8: Reconstruyendo serie...")
for f in range(n_features):
    X_imputed_all[:, :, f] = X_imputed_all[:, :, f] * feature_stds[f] + feature_means[f]

# Vectorizado con np.add.at
reconstructed_sum = np.zeros((n_days, n_features))
reconstructed_cnt = np.zeros((n_days, n_features))
day_indices = np.zeros((n_samples, WINDOW_SIZE), dtype=int)
for i, (start, _) in enumerate(window_dates):
    day_indices[i] = np.arange(start, start + WINDOW_SIZE)

for f in range(n_features):
    vals = X_imputed_all[:, :, f]
    days = day_indices
    np.add.at(reconstructed_sum[:, f], days.ravel(), vals.ravel())
    np.add.at(reconstructed_cnt[:, f], days.ravel(), np.ones_like(vals.ravel()))

mask = reconstructed_cnt > 0
reconstructed = np.full((n_days, n_features), np.nan)
reconstructed[mask] = reconstructed_sum[mask] / reconstructed_cnt[mask]

for f in range(n_features):
    s = pd.Series(reconstructed[:, f], index=wide_df.index)
    s = s.interpolate(method='linear', limit_direction='both')
    reconstructed[:, f] = s.values

log(f"  Serie reconstruida: {reconstructed.shape}")

# ---------------------------------------------------------------------------
# 7. COMPARAR missForest vs SAITS
# ---------------------------------------------------------------------------
log("Paso 7/8: Comparando missForest vs SAITS...")
print("=" * 70)

comparaciones = []
for i, est in enumerate(ESTACIONES):
    mf_idx = mf_df[est].values == 1
    n_mf = mf_idx.sum()
    if n_mf == 0:
        continue
    df_est = df[df['NombreEstacion'] == est].sort_values('Fecha').reset_index(drop=True)
    mf_orig = df_est.loc[df_est['Metodo'] == 'L3_missForest', 'Cota'].values
    saits_vals = reconstructed[:, i][mf_idx]
    
    stats = {
        'estacion': est, 'n_missforest': n_mf,
        'missforest_mean': mf_orig.mean(), 'missforest_std': mf_orig.std(),
        'missforest_min': mf_orig.min(), 'missforest_max': mf_orig.max(),
        'saits_mean': saits_vals.mean(), 'saits_std': saits_vals.std(),
        'saits_min': saits_vals.min(), 'saits_max': saits_vals.max(),
        'diff_mean': saits_vals.mean() - mf_orig.mean(),
        'diff_std': saits_vals.std() - mf_orig.std(),
    }
    comparaciones.append(stats)
    
    print(f"\n{est}:")
    print(f"  missForest: mean={stats['missforest_mean']:.3f}, std={stats['missforest_std']:.3f}, range=[{stats['missforest_min']:.3f}, {stats['missforest_max']:.3f}]")
    print(f"  SAITS:      mean={stats['saits_mean']:.3f}, std={stats['saits_std']:.3f}, range=[{stats['saits_min']:.3f}, {stats['saits_max']:.3f}]")
    print(f"  Dif:        mean={stats['diff_mean']:+.3f}, std={stats['diff_std']:+.3f}")

comp_df = pd.DataFrame(comparaciones)
comp_df.to_csv(f'{OUTPUT_DIR}/comparacion_missForest_vs_SAITS_v44.csv', index=False)
log(f"Guardado: comparacion_missForest_vs_SAITS_v44.csv")

# ---------------------------------------------------------------------------
# 8. GUARDAR DATASET v4.4
# ---------------------------------------------------------------------------
log("Paso 8/8: Generando Datos_Imputados_v4_4_SAITS.csv...")

# Crear lookup rapido: (estacion, fecha) -> valor
fecha_to_pos = {d: i for i, d in enumerate(wide_df.index)}
saits_lookup = {}
for i, est in enumerate(ESTACIONES):
    saits_lookup[est] = {d: reconstructed[p, i] for d, p in fecha_to_pos.items()}

# Usar map en lugar de apply para velocidad
df_saits = df.copy()
df_saits['saits_cota'] = df_saits.set_index(['NombreEstacion', 'Fecha']).index.map(
    lambda x: saits_lookup.get(x[0], {}).get(x[1], np.nan)
)

mask_mf = df_saits['Metodo'] == 'L3_missForest'
df_saits.loc[mask_mf, 'Cota'] = df_saits.loc[mask_mf, 'saits_cota']
df_saits.loc[mask_mf, 'Metodo'] = 'L4_SAITS'
df_saits.loc[mask_mf, 'Nivel_Imputacion'] = 4
df_saits = df_saits.drop(columns=['saits_cota'])

counts = df_saits['Metodo'].value_counts()
print(counts.to_string())

df_saits.to_csv(f'{OUTPUT_DIR}/Datos_Imputados_v4_4_SAITS.csv', index=False)
log("Guardado: Datos_Imputados_v4_4_SAITS.csv")

log("=" * 70)
log("SAITS v4.4 COMPLETADO - Resultados listos para revision")
log("=" * 70)
log("Archivos generados:")
log(f"  - {OUTPUT_DIR}/comparacion_missForest_vs_SAITS_v44.csv")
log(f"  - {OUTPUT_DIR}/Datos_Imputados_v4_4_SAITS.csv")
log(f"  - {MODEL_SAVE_DIR}/ (modelo entrenado)")
