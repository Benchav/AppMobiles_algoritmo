"""
tutors.py
---------
Funciones para gestionar el archivo data/tutores.csv cuando no se dispone
de una lista real de tutores. Permite leer el archivo si existe, generarlo
con nombres "Tutor 1..N" y carnets secuenciales, y devolver un DataFrame.
"""
import os
from typing import Optional

import pandas as pd

from src.config import TUTORS_FILE, TUTOR_CARNET_START


def _read_csv(path: str) -> pd.DataFrame:
    try:
        return pd.read_csv(path, sep=';', encoding='utf-8')
    except UnicodeDecodeError:
        return pd.read_csv(path, sep=';', encoding='latin1')


def read_tutors(path: str = TUTORS_FILE) -> pd.DataFrame:
    """Lee el CSV de tutores y normaliza columnas a ['Nombre','Carnet'].
    Si no existe, retorna un DataFrame vacío con esas columnas.
    """
    if not os.path.exists(path):
        return pd.DataFrame(columns=['Nombre', 'Carnet'])

    df = _read_csv(path)
    # detectar columnas equivalentes
    name_col = next((c for c in df.columns if 'nombre' in c.lower()), None)
    carnet_col = next((c for c in df.columns if 'carnet' in c.lower()), None)
    if name_col and carnet_col:
        if name_col != 'Nombre' or carnet_col != 'Carnet':
            df = df.rename(columns={name_col: 'Nombre', carnet_col: 'Carnet'})

    # asegurar columnas
    if 'Nombre' not in df.columns:
        df['Nombre'] = ''
    if 'Carnet' not in df.columns:
        df['Carnet'] = ''

    return df[['Nombre', 'Carnet']]


def generate_tutors(n: int, start: int = TUTOR_CARNET_START, path: str = TUTORS_FILE) -> pd.DataFrame:
    """Genera n tutores con nombres Tutor 1..N y carnets secuenciales.
    Guarda el CSV en `path` con sep=';'. Retorna el DataFrame generado.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    rows = [{'Nombre': f'Tutor {i+1}', 'Carnet': str(start + i)} for i in range(n)]
    df = pd.DataFrame(rows, columns=['Nombre', 'Carnet'])
    df.to_csv(path, sep=';', index=False, encoding='utf-8-sig')
    return df


def maybe_generate_tutors_if_missing(n: int, path: str = TUTORS_FILE, start: int = TUTOR_CARNET_START) -> pd.DataFrame:
    """Genera el CSV con n tutores solo si NO existe. Si existe, lo lee y lo retorna.
    Esta funcion no sobrescribe un archivo existente.
    """
    if n <= 0:
        return pd.DataFrame(columns=['Nombre', 'Carnet'])
    if not os.path.exists(path):
        return generate_tutors(n, start=start, path=path)
    return read_tutors(path)
