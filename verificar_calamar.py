import pandas as pd

file = r'backend/data/raw/RawData/SERIE NIVELES IDEAM A 2026/CALAMAR_29037020.xlsx'
df = pd.read_excel(file, sheet_name='Crudos')
df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
df['cota'] = pd.to_numeric(df['cota nivel (m.s.n.m)'], errors='coerce')

# Filtrar datos validos
df_valid = df.dropna(subset=['fecha', 'cota'])

print('=== VERIFICACION CALAMAR ===')
print()
print(f'Total filas en hoja Crudos: {len(df)}')
print(f'Filas con datos validos: {len(df_valid)}')
print()
print('PRIMER dato valido:')
print(df_valid.head(1)[['fecha', 'cota']].to_string(index=False))
print()
print('ULTIMO dato valido:')
print(df_valid.tail(1)[['fecha', 'cota']].to_string(index=False))
print()
print('Rango completo:')
inicio = df_valid['fecha'].min()
fin = df_valid['fecha'].max()
print(f'  Inicio: {inicio}')
print(f'  Fin: {fin}')
print()

# Ver primeros 20 datos validos
print('Primeros 20 datos validos:')
print(df_valid.head(20)[['fecha', 'cota']].to_string(index=False))
