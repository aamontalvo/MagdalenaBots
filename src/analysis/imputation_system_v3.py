"""
Sistema de Imputación de Datos Faltantes - Río Magdalena v3.0
Estrategia: 
  - Nivel 1: Interpolación local ponderada (gaps <=3 días)
  - Nivel 2: Curvas H-H (lineal vs cuadratico) - seleccion por R2 >= 0.75
  - Nivel 3: Múltiples donantes para casos difíciles
Cambios v3.0:
  - Comparación lineal vs cuadrático, selección del mejor modelo
  - Criterio estricto: R2 >= 0.75 para aceptar imputacion
  - Modelos con R2 < 0.75 se reportan pero no se usan para imputar
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')

# Orden geográfico (aguas abajo -> aguas arriba)
GEOGRAPHIC_ORDER = [
    'SAN_PEDRITO', 'CALAMAR', 'TENERIFE', 'PLATO', 'MAGANGUE', 'BARBOSA', 'COYONGAL',
    'ARMENIA', 'RIO_NUEVO', 'LAS_PALOMAS', 'LAS_AGUADAS', 'EL_BANCO', 'PENONCITO',
    'LA_GLORIA', 'GAMARRA_AUT', 'EL_CONTENTO', 'SITIO_NUEVO', 'PUERTO_WILCHES',
]

# Criterios de calidad
MIN_R2_FOR_IMPUTATION = 0.75  # R2 minimo para usar modelo en imputacion
MIN_CORRELATION = 0.85        # Correlación mínima para considerar par

plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['axes.grid'] = True


def load_data_long(data_dir):
    """Carga datos en formato long."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from ideam_levels_analysis import load_all_stations
    return load_all_stations(data_dir)


def create_full_date_range(df):
    """Crea rango completo de fechas para cada estación desde su primer año con datos."""
    stations_info = []
    
    for station in df['station'].unique():
        station_data = df[df['station'] == station]
        
        # Solo considerar años con al menos 50 datos válidos
        yearly_counts = station_data[station_data['level'].notna()].groupby('year').size()
        valid_years = yearly_counts[yearly_counts >= 50].index
        
        if len(valid_years) == 0:
            first_year = int(station_data['year'].min())
            last_year = int(station_data['year'].max())
        else:
            first_year = int(valid_years.min())
            last_year = int(valid_years.max())
        
        # Extender hasta 2025
        if last_year < 2025:
            last_year = 2025
        
        start_date = pd.Timestamp(f"{first_year}-01-01")
        end_date = pd.Timestamp(f"{last_year}-12-31")
        full_dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        stations_info.append({
            'station': station,
            'first_year': first_year,
            'last_year': last_year,
            'full_dates': full_dates,
            'expected_days': len(full_dates)
        })
    
    return pd.DataFrame(stations_info)


def expand_to_full_dates(df, station_info_df):
    """Expande cada estación a su rango completo de fechas."""
    expanded = []
    
    for _, row in station_info_df.iterrows():
        station = row['station']
        station_original = df[df['station'] == station].copy()
        
        full_df = pd.DataFrame({'date': row['full_dates']})
        full_df['year'] = full_df['date'].dt.year
        full_df['month'] = full_df['date'].dt.month
        full_df['day'] = full_df['date'].dt.day
        full_df['station'] = station
        
        station_original['date'] = pd.to_datetime(station_original['date'])
        full_df = full_df.merge(
            station_original[['date', 'level']], 
            on='date', 
            how='left'
        )
        
        full_df['data_source'] = full_df['level'].apply(lambda x: 'original' if pd.notna(x) else 'missing')
        
        expanded.append(full_df)
    
    return pd.concat(expanded, ignore_index=True)


def local_interpolation_weighted(df_station, max_gap=3):
    """Interpolación local con media móvil ponderada de 5 puntos para gaps <= max_gap."""
    df = df_station.copy().sort_values('date').reset_index(drop=True)
    df['level_original'] = df['level'].copy()
    df['imputed_local'] = False
    
    df['is_null'] = df['level'].isnull()
    df['gap_id'] = (df['is_null'] != df['is_null'].shift()).cumsum()
    
    imputed_count = 0
    
    for gap_id in df[df['is_null']]['gap_id'].unique():
        gap_data = df[df['gap_id'] == gap_id]
        gap_size = len(gap_data)
        
        if gap_size > max_gap:
            continue
        
        gap_indices = gap_data.index.tolist()
        
        for idx in gap_indices:
            pos = idx
            
            # Buscar 2 valores válidos anteriores
            prev_vals = []
            prev_weights = []
            for i in range(pos-1, max(0, pos-10), -1):
                if pd.notna(df.iloc[i]['level_original']) or df.iloc[i]['imputed_local']:
                    val = df.iloc[i]['level'] if pd.notna(df.iloc[i]['level']) else df.iloc[i]['level_original']
                    if pd.notna(val):
                        prev_vals.append(val)
                        dist = pos - i
                        weight = 2.0 if dist == 1 else 1.0 / (dist - 0.5)
                        prev_weights.append(weight)
                        if len(prev_vals) == 2:
                            break
            
            # Buscar 2 valores válidos posteriores
            next_vals = []
            next_weights = []
            for i in range(pos+1, min(len(df), pos+10)):
                if pd.notna(df.iloc[i]['level_original']) or df.iloc[i]['imputed_local']:
                    val = df.iloc[i]['level'] if pd.notna(df.iloc[i]['level']) else df.iloc[i]['level_original']
                    if pd.notna(val):
                        next_vals.append(val)
                        dist = i - pos
                        weight = 2.0 if dist == 1 else 1.0 / (dist - 0.5)
                        next_weights.append(weight)
                        if len(next_vals) == 2:
                            break
            
            all_vals = prev_vals + next_vals
            all_weights = prev_weights + next_weights
            
            if len(all_vals) >= 2:
                weighted_mean = np.average(all_vals, weights=all_weights)
                df.loc[idx, 'level'] = weighted_mean
                df.loc[idx, 'imputed_local'] = True
                df.loc[idx, 'data_source'] = 'imputed_local'
                imputed_count += 1
    
    return df, imputed_count


def fit_linear_model(X, y):
    """Ajusta modelo lineal: y = mx + b"""
    X_reshaped = X.reshape(-1, 1)
    model = LinearRegression()
    model.fit(X_reshaped, y)
    y_pred = model.predict(X_reshaped)
    
    r2 = r2_score(y, y_pred)
    rmse = np.sqrt(mean_squared_error(y, y_pred))
    m = model.coef_[0]
    b = model.intercept_
    
    return {
        'type': 'linear',
        'model': model,
        'r2': r2,
        'rmse': rmse,
        'equation': f"H_target = {m:.4f}·H_donor + {b:.4f}",
        'params': {'m': m, 'b': b}
    }


def fit_quadratic_model(X, y):
    """Ajusta modelo cuadratico: y = ax^2 + bx + c"""
    X_poly = np.column_stack([X, X**2])
    model = LinearRegression()
    model.fit(X_poly, y)
    y_pred = model.predict(X_poly)
    
    r2 = r2_score(y, y_pred)
    rmse = np.sqrt(mean_squared_error(y, y_pred))
    a = model.coef_[1]
    b = model.coef_[0]
    c = model.intercept_
    
    return {
        'type': 'quadratic',
        'model': model,
        'r2': r2,
        'rmse': rmse,
        'equation': f"H_target = {a:.6f}*H^2 + {b:.4f}*H + {c:.4f}",
        'params': {'a': a, 'b': b, 'c': c}
    }


def select_best_model(pair_data):
    """
    Compara modelos lineal y cuadratico, selecciona el mejor por R2.
    Retorna None si ninguno alcanza R2 >= MIN_R2_FOR_IMPUTATION.
    """
    X = pair_data['donor'].values
    y = pair_data['target'].values
    
    # Ajustar ambos modelos
    linear = fit_linear_model(X, y)
    quadratic = fit_quadratic_model(X, y)
    
    # Seleccionar el mejor
    if quadratic['r2'] >= linear['r2']:
        best = quadratic
        other = linear
    else:
        best = linear
        other = quadratic
    
    # Verificar si el mejor modelo cumple criterio mínimo
    best['acceptable'] = best['r2'] >= MIN_R2_FOR_IMPUTATION
    best['r2_other'] = other['r2']
    best['type_other'] = other['type']
    best['n_samples'] = len(y)
    
    return best, other


def plot_hh_model(pair_data, best_model, other_model, target_station, donor_station, output_path):
    """Genera figura de Curva H-H con el modelo seleccionado."""
    
    X = pair_data['donor'].values
    y = pair_data['target'].values
    
    # Crear figura con dos paneles
    fig, axes = plt.subplots(2, 1, figsize=(10, 12), gridspec_kw={'height_ratios': [2, 1]})
    
    # Calcular predicciones del mejor modelo
    if best_model['type'] == 'linear':
        m, b = best_model['params']['m'], best_model['params']['b']
        y_pred = m * X + b
        x_range = np.linspace(X.min() * 0.98, X.max() * 1.02, 500)
        y_range = m * x_range + b
        model_label = f"Lineal: y = {m:.4f}x + {b:.4f}"
    else:
        a, b, c = best_model['params']['a'], best_model['params']['b'], best_model['params']['c']
        y_pred = a * X**2 + b * X + c
        x_range = np.linspace(X.min() * 0.98, X.max() * 1.02, 500)
        y_range = a * x_range**2 + b * x_range + c
        model_label = f"Cuadratico: y = {a:.4f}x^2 + {b:.4f}x + {c:.4f}"
    
    residuals = y - y_pred
    
    # Panel superior: Dispersión y modelo
    ax_main = axes[0]
    ax_main.scatter(X, y, alpha=0.3, s=8, color='steelblue', edgecolors='none',
                   label=f'Datos concurrentes (n={len(y):,})')
    ax_main.plot(x_range, y_range, 'r-', linewidth=2, label=model_label)
    
    # Línea 1:1
    min_val = min(X.min(), y.min())
    max_val = max(X.max(), y.max())
    ax_main.plot([min_val, max_val], [min_val, max_val], 'k--', linewidth=1, alpha=0.5, label='1:1')
    
    # Texto de métricas
    status = "ACEPTADO" if best_model['acceptable'] else "RECHAZADO (R2 < 0.75)"
    metrics_text = (f"R2 = {best_model['r2']:.4f}\n"
                   f"RMSE = {best_model['rmse']:.3f} m\n"
                   f"Modelo alternativo ({other_model['type']}): R2 = {other_model['r2']:.4f}\n"
                   f"Estado: {status}")
    
    ax_main.text(0.05, 0.95, metrics_text,
                transform=ax_main.transAxes, fontsize=10,
                verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    target_clean = target_station.replace('_', ' ')
    donor_clean = donor_station.replace('_', ' ')
    
    title_suffix = f" ({best_model['type'].title()})"
    ax_main.set_title(f"{target_clean} vs {donor_clean}{title_suffix}",
                     fontsize=13, fontweight='bold', pad=10)
    ax_main.set_xlabel(f'{donor_clean} (m.s.n.m.)', fontsize=11)
    ax_main.set_ylabel(f'{target_clean} (m.s.n.m.)', fontsize=11)
    ax_main.legend(loc='lower right', fontsize=9)
    ax_main.grid(True, alpha=0.3)
    
    # Panel inferior: Residuos
    ax_res = axes[1]
    ax_res.scatter(y_pred, residuals, alpha=0.3, s=8, color='steelblue', edgecolors='none')
    ax_res.axhline(y=0, color='red', linewidth=1.5, label='Media = 0')
    ax_res.axhline(y=0.5, color='gray', linestyle='--', alpha=0.4)
    ax_res.axhline(y=-0.5, color='gray', linestyle='--', alpha=0.4)
    
    ax_res.set_xlabel('Valores predichos (m.s.n.m.)', fontsize=11)
    ax_res.set_ylabel('Residuos (m)', fontsize=11)
    ax_res.set_title(f'Residuos - {best_model["type"].title()}\nMedia residuos: {residuals.mean():.4f} m',
                    fontsize=11)
    ax_res.legend(loc='upper right')
    ax_res.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()


def apply_imputation(df_target, df_donor, model_info):
    """Aplica imputación usando el modelo seleccionado."""
    
    df_result = df_target.copy()
    
    donor_subset = df_donor[['date', 'level']].rename(columns={'level': 'donor_level'})
    df_result = df_result.merge(donor_subset, on='date', how='left')
    
    mask_missing = df_result['level'].isnull() & df_result['donor_level'].notnull()
    
    if mask_missing.sum() == 0:
        return df_result, 0
    
    X_missing = df_result.loc[mask_missing, 'donor_level'].values
    
    if model_info['type'] == 'linear':
        m, b = model_info['params']['m'], model_info['params']['b']
        y_imputed = m * X_missing + b
    else:
        a, b, c = model_info['params']['a'], model_info['params']['b'], model_info['params']['c']
        y_imputed = a * X_missing**2 + b * X_missing + c
    
    df_result.loc[mask_missing, 'level'] = y_imputed
    df_result.loc[mask_missing, 'data_source'] = 'imputed_hh'
    df_result.loc[mask_missing, 'donor_station'] = df_donor['station'].iloc[0]
    
    n_imputed = mask_missing.sum()
    df_result = df_result.drop(columns=['donor_level'])
    
    return df_result, n_imputed


def find_best_donor(df_all, target_station, imputed_data, min_correlation=0.85):
    """Encuentra la mejor estación donante con correlación suficiente."""
    
    candidates = []
    
    for donor in GEOGRAPHIC_ORDER:
        if donor == target_station or donor not in df_all['station'].values:
            continue
        
        # Preparar datos
        if target_station in imputed_data:
            target_df = imputed_data[target_station][['date', 'level']].rename(columns={'level': 'target'})
        else:
            target_df = df_all[df_all['station'] == target_station][['date', 'level']].rename(columns={'level': 'target'})
        
        if donor in imputed_data:
            donor_df = imputed_data[donor][['date', 'level']].rename(columns={'level': 'donor'})
        else:
            donor_df = df_all[df_all['station'] == donor][['date', 'level']].rename(columns={'level': 'donor'})
        
        merged = pd.merge(target_df, donor_df, on='date').dropna()
        
        if len(merged) < 100:
            continue
        
        corr = merged['target'].corr(merged['donor'])
        
        if corr >= min_correlation:
            candidates.append({
                'donor': donor,
                'correlation': corr,
                'pair_data': merged
            })
    
    if not candidates:
        return None, None
    
    # Seleccionar el mejor
    best = max(candidates, key=lambda x: x['correlation'])
    return best['donor'], best['pair_data']


def main():
    """Ejecuta el sistema completo de imputación v3.0."""
    
    print("=" * 75)
    print("SISTEMA DE IMPUTACION DE DATOS v3.0 - RIO MAGDALENA")
    print("Estrategia: Local + H-H (Lineal vs Cuadratico, R2 >= 0.75)")
    print("=" * 75)
    
    data_dir = r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\backend\data\raw\RawData\SERIE NIVELES IDEAM A 2026'
    output_dir = Path(r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\informes\imputacion')
    output_dir.mkdir(exist_ok=True)
    
    # 1. Cargar datos
    print("\n[1/5] Cargando datos...")
    df = load_data_long(data_dir)
    print(f"  Datos originales: {len(df):,} registros")
    
    # 2. Crear rangos completos
    print("\n[2/5] Creando rangos de fechas completos...")
    station_info = create_full_date_range(df)
    df_expanded = expand_to_full_dates(df, station_info)
    
    total_expected = len(df_expanded)
    total_original = (df_expanded['data_source'] == 'original').sum()
    print(f"  Total esperado: {total_expected:,} registros")
    print(f"  Datos originales: {total_original:,} ({total_original/total_expected*100:.1f}%)")
    
    # 3. Imputación local
    print("\n[3/5] Aplicando interpolación local (gaps <= 3)...")
    imputed_data = {}
    total_local = 0
    
    for station in GEOGRAPHIC_ORDER:
        station_df = df_expanded[df_expanded['station'] == station].copy()
        station_imputed, n_local = local_interpolation_weighted(station_df, max_gap=3)
        imputed_data[station] = station_imputed
        total_local += n_local
    
    print(f"  Total imputado localmente: {total_local:,}")
    
    # 4. Imputación H-H con selección de modelo
    print("\n[4/5] Aplicando curvas H-H (comparando lineal vs cuadratico)...")
    print(f"  Criterio de aceptacion: R2 >= {MIN_R2_FOR_IMPUTATION}")
    
    hh_results = []
    models_accepted = 0
    models_rejected = 0
    
    for station in GEOGRAPHIC_ORDER:
        if station not in imputed_data:
            continue
        
        station_df = imputed_data[station]
        remaining_missing = station_df['level'].isnull().sum()
        
        if remaining_missing == 0:
            continue
        
        # Encontrar mejor donante
        donor, pair_data = find_best_donor(df_expanded, station, imputed_data)
        
        if donor is None:
            continue
        
        # Comparar modelos
        best_model, other_model = select_best_model(pair_data)
        
        status = "ACEPTADO" if best_model['acceptable'] else "RECHAZADO"
        print(f"  {station} <- {donor}: {best_model['type']} R2={best_model['r2']:.3f} ({status})")
        
        # Generar figura
        fig_path = output_dir / f"Figura_HH_{station}_{donor}_{best_model['type']}.png"
        plot_hh_model(pair_data, best_model, other_model, station, donor, fig_path)
        
        # Aplicar imputación solo si el modelo es aceptable
        n_imputed = 0
        if best_model['acceptable']:
            donor_df = imputed_data[donor]
            station_imputed, n_imputed = apply_imputation(station_df, donor_df, best_model)
            imputed_data[station] = station_imputed
            models_accepted += 1
        else:
            models_rejected += 1
        
        hh_results.append({
            'target': station,
            'donor': donor,
            'model_type': best_model['type'],
            'r2': best_model['r2'],
            'r2_alternative': other_model['r2'],
            'rmse': best_model['rmse'],
            'equation': best_model['equation'],
            'acceptable': best_model['acceptable'],
            'n_training': best_model['n_samples'],
            'n_imputed': n_imputed
        })
    
    print(f"\n  Modelos aceptados (R2 >= {MIN_R2_FOR_IMPUTATION}): {models_accepted}")
    print(f"  Modelos rechazados (R2 < {MIN_R2_FOR_IMPUTATION}): {models_rejected}")
    
    # 5. Consolidar resultados
    print("\n[5/5] Consolidando resultados...")
    
    all_imputed = []
    summary = []
    
    for station in GEOGRAPHIC_ORDER:
        if station not in imputed_data:
            continue
        
        station_df = imputed_data[station]
        
        total_days = len(station_df)
        original = (station_df['data_source'] == 'original').sum()
        local = (station_df['data_source'] == 'imputed_local').sum()
        hh = (station_df['data_source'] == 'imputed_hh').sum()
        still_missing = station_df['level'].isnull().sum()
        
        final_coverage = ((total_days - still_missing) / total_days) * 100
        
        summary.append({
            'station': station,
            'total_days': total_days,
            'original_data': original,
            'local_imputed': local,
            'hh_imputed': hh,
            'still_missing': still_missing,
            'final_coverage_pct': final_coverage
        })
        
        all_imputed.append(station_df)
    
    summary_df = pd.DataFrame(summary)
    
    # Guardar resultados
    final_df = pd.concat(all_imputed, ignore_index=True)
    final_df.to_csv(output_dir / 'Datos_Imputados_v3.csv', index=False, encoding='utf-8-sig')
    summary_df.to_csv(output_dir / 'Tabla_I1_Resumen_Imputacion_v3.csv', index=False, encoding='utf-8-sig')
    
    if hh_results:
        hh_df = pd.DataFrame(hh_results)
        hh_df.to_csv(output_dir / 'Tabla_I2_Modelos_HH_v3.csv', index=False, encoding='utf-8-sig')
    
    # Reporte final
    print("\n" + "=" * 75)
    print("RESUMEN FINAL DE IMPUTACION v3.0")
    print("=" * 75)
    print(f"\nEstaciones procesadas: {len(summary_df)}")
    print(f"Cobertura promedio final: {summary_df['final_coverage_pct'].mean():.2f}%")
    print(f"Total imputado local: {summary_df['local_imputed'].sum():,}")
    print(f"Total imputado H-H: {summary_df['hh_imputed'].sum():,}")
    
    # Estaciones con problemas
    rejected_stations = [r for r in hh_results if not r['acceptable']]
    if rejected_stations:
        print("\nEstaciones con modelos rechazados (R2 < 0.75):")
        for r in rejected_stations:
            print(f"  - {r['target']} <- {r['donor']}: R2 = {r['r2']:.3f}")
    
    high_missing = summary_df[summary_df['still_missing'] > 1000]
    if len(high_missing) > 0:
        print("\nEstaciones con >1,000 días faltantes:")
        for _, row in high_missing.iterrows():
            print(f"  - {row['station']}: {row['still_missing']:,} días ({row['final_coverage_pct']:.1f}%)")
    
    return final_df, summary_df, hh_results


if __name__ == '__main__':
    final_df, summary_df, hh_results = main()
