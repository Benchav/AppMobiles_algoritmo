"""
data_loader.py
--------------
Capa de carga y limpieza de datos.
Responsabilidades:
  - Leer el CSV con tolerancia de encoding.
  - Detectar y eliminar duplicados por Nombre Completo y Número de carnet.
  - Clasificar cada estudiante en su Área académica.
  - Normalizar el año universitario a valor numérico.
"""

import pandas as pd
from src.config import get_area_from_major, normalize_string


def load_and_clean_data(filepath: str) -> pd.DataFrame:
    """Carga el CSV, limpia duplicados y clasifica áreas. Retorna el DataFrame limpio."""

    # 1. Lectura con fallback de encoding
    try:
        df = pd.read_csv(filepath, sep=';', encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(filepath, sep=';', encoding='latin1')

    total_raw = len(df)

    # 2. Identificar columnas clave
    nombre_col = next(
        (col for col in df.columns if 'Nombre completo' in col),
        None
    )
    carnet_col = next(
        (col for col in df.columns if 'carnet' in col.lower()),
        None
    )

    # 3. Limpieza de duplicados
    #    Prioridad: duplicado exacto de Nombre Completo → se queda el último registro
    if nombre_col:
        # Normalizar el nombre para comparación sin importar tildes/espacios
        df['_nombre_norm'] = df[nombre_col].apply(normalize_string)
        antes = len(df)
        df = df.drop_duplicates(subset=['_nombre_norm'], keep='last')
        eliminados_nombre = antes - len(df)
        if eliminados_nombre > 0:
            print(f"  ⚠  Duplicados por nombre completo eliminados: {eliminados_nombre}")
        df = df.drop(columns=['_nombre_norm'])

    # 4. Limpieza adicional por carnet (si existe y no está vacío)
    if carnet_col:
        df['_carnet_norm'] = df[carnet_col].astype(str).str.strip().str.replace(r'[\s,\-]', '', regex=True).str.lower()
        df['_carnet_norm'] = df['_carnet_norm'].replace(['', 'nan', 'none'], pd.NA)
        antes = len(df)
        df_sinNA = df.dropna(subset=['_carnet_norm'])
        df_conNA = df[df['_carnet_norm'].isna()]
        df_sinNA = df_sinNA.drop_duplicates(subset=['_carnet_norm'], keep='last')
        df = pd.concat([df_sinNA, df_conNA], ignore_index=True)
        eliminados_carnet = antes - len(df)
        if eliminados_carnet > 0:
            print(f"  ⚠  Duplicados por número de carnet eliminados: {eliminados_carnet}")
        df = df.drop(columns=['_carnet_norm'])

    total_limpio = len(df)
    print(f"  ✔  Registros originales: {total_raw}  →  Registros únicos: {total_limpio}")

    # 5. Enriquecer datos
    df['Carrera_Normalizada'] = df['Carrera'].apply(
        lambda x: str(x).strip() if pd.notnull(x) else 'Desconocida'
    )
    df['Area'] = df['Carrera_Normalizada'].apply(get_area_from_major)
    df['Año_Num'] = df['Año'].apply(
        lambda x: 5 if '5' in str(x)
        else (4 if '4' in str(x)
              else (3 if '3' in str(x)
                    else 0))
    )

    # 6. Guardar referencias de columnas en el df para uso posterior
    df.attrs['nombre_col'] = nombre_col or 'Nombre'
    df.attrs['carnet_col'] = carnet_col or 'Carnet'

    return df.reset_index(drop=True)
