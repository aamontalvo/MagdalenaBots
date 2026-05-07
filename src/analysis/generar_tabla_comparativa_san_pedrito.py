"""
Generar tabla comparativa ANTES vs DESPUES de imputacion para San Pedrito.
Para inclusion en documento Word.
"""

import pandas as pd
from pathlib import Path

BACKUP_PATH = Path(r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\backend\data\processed\imputation\Datos_Imputados_v4_2_Complete_backup_pre_sanpedrito.csv')
NEW_PATH = Path(r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\backend\data\processed\imputation\Datos_Imputados_v4_2_Complete.csv')
OUTPUT_DIR = Path(r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\backend\data\processed\imputation')

# Leer datos
print("Generando tabla comparativa ANTES vs DESPUES - San Pedrito...")

# Backup (antes)
df_backup = pd.read_csv(BACKUP_PATH)
sp_before = df_backup[df_backup['NombreEstacion'] == 'San Pedrito'].copy()

# Nuevo (despues)
df_new = pd.read_csv(NEW_PATH)
sp_after = df_new[df_new['NombreEstacion'] == 'San Pedrito'].copy()

# Comparativa
print("\n" + "=" * 80)
print("COMPARATIVA SAN PEDRITO - ANTES vs DESPUES DE ACTUALIZACION")
print("=" * 80)

# Estadisticas antes
before_total = len(sp_before)
before_original = (sp_before['Nivel_Imputacion'] == 0).sum()
before_l1 = (sp_before['Nivel_Imputacion'] == 1).sum()
before_l2 = (sp_before['Nivel_Imputacion'] == 2).sum()
before_missing = sp_before['Cota'].isna().sum()
before_coverage = 100 * (before_total - before_missing) / before_total

# Estadisticas despues
after_total = len(sp_after)
after_original = (sp_after['Nivel_Imputacion'] == 0).sum()
after_l1 = (sp_after['Nivel_Imputacion'] == 1).sum()
after_l2 = (sp_after['Nivel_Imputacion'] == 2).sum()
after_missing = sp_after['Cota'].isna().sum()
after_coverage = 100 * (after_total - after_missing) / after_total

print(f"\n{'Metrica':<35} {'ANTES (v4.2 original)':>25} {'DESPUES (actualizado)':>25}")
print("-" * 90)
print(f"{'Rango temporal':<35} {'01-01-1979 a 31-12-2019':>25} {'01-01-1979 a 31-12-2025':>25}")
print(f"{'Total registros':<35} {before_total:>25,} {after_total:>25,}")
print(f"{'Datos originales':<35} {before_original:>25,} {after_original:>25,}")
print(f"{'Imputados L1 (interpolacion)':<35} {before_l1:>25,} {after_l1:>25,}")
print(f"{'Imputados L2 (H-H)':<35} {before_l2:>25,} {after_l2:>25,}")
print(f"{'Faltantes (sin imputar)':<35} {before_missing:>25,} {after_missing:>25,}")
print(f"{'Cobertura':<35} {before_coverage:>24.2f}% {after_coverage:>24.2f}%")

# Guardar como CSV
data = {
    'Metrica': [
        'Rango temporal',
        'Total registros',
        'Datos originales',
        'Imputados L1 (interpolacion)',
        'Imputados L2 (H-H)',
        'Faltantes (sin imputar)',
        'Cobertura (%)'
    ],
    'ANTES_v4_2_original': [
        '01-01-1979 a 31-12-2019',
        before_total,
        before_original,
        before_l1,
        before_l2,
        before_missing,
        round(before_coverage, 2)
    ],
    'DESPUES_actualizado': [
        '01-01-1979 a 31-12-2025',
        after_total,
        after_original,
        after_l1,
        after_l2,
        after_missing,
        round(after_coverage, 2)
    ]
}

df_comp = pd.DataFrame(data)
output_path = OUTPUT_DIR / 'Tabla_Comparativa_SanPedrito_Antes_Despues.csv'
df_comp.to_csv(output_path, index=False, encoding='utf-8-sig')
print(f"\nTabla guardada: {output_path}")

# Tambien guardar como texto formateado
text_path = OUTPUT_DIR / 'Tabla_Comparativa_SanPedrito_Antes_Despues.txt'
with open(text_path, 'w', encoding='utf-8') as f:
    f.write("=" * 90 + "\n")
    f.write("COMPARATIVA SAN PEDRITO - ANTES vs DESPUES DE ACTUALIZACION\n")
    f.write("=" * 90 + "\n\n")
    f.write(f"{'Metrica':<35} {'ANTES (v4.2 original)':>25} {'DESPUES (actualizado)':>25}\n")
    f.write("-" * 90 + "\n")
    f.write(f"{'Rango temporal':<35} {'01-01-1979 a 31-12-2019':>25} {'01-01-1979 a 31-12-2025':>25}\n")
    f.write(f"{'Total registros':<35} {before_total:>25,} {after_total:>25,}\n")
    f.write(f"{'Datos originales':<35} {before_original:>25,} {after_original:>25,}\n")
    f.write(f"{'Imputados L1 (interpolacion)':<35} {before_l1:>25,} {after_l1:>25,}\n")
    f.write(f"{'Imputados L2 (H-H)':<35} {before_l2:>25,} {after_l2:>25,}\n")
    f.write(f"{'Faltantes (sin imputar)':<35} {before_missing:>25,} {after_missing:>25,}\n")
    f.write(f"{'Cobertura (%)':<35} {before_coverage:>24.2f}% {after_coverage:>24.2f}%\n")
    f.write("\n" + "=" * 90 + "\n")
    f.write("NOTA: La actualizacion corrigio el parser de Excel que truncaba San Pedrito\n")
    f.write("en 2019. Ahora tiene datos hasta 2025 y se imputo al 100% usando Calamar\n")
    f.write("como estacion donante (R2 = 0.993, modelo cuadratico).\n")
    f.write("=" * 90 + "\n")

print(f"Texto formateado guardado: {text_path}")
print("\nPROCESO COMPLETADO")
