#!/usr/bin/env python3
"""Imprime conteos por carrera en datos_limpios.csv y en el Excel de equipos.
"""
import pandas as pd
from pathlib import Path
import sys

base = Path('.')
cleaned = base / 'data' / 'datos_limpios.csv'
excel = base / 'datos' / 'equipos_conformados.xlsx'

def read_cleaned():
    if not cleaned.exists():
        print('No existe', cleaned)
        return None
    try:
        df = pd.read_csv(cleaned, sep=';', encoding='utf-8-sig')
    except Exception:
        df = pd.read_csv(cleaned, sep=';', encoding='latin1')
    return df

def read_teams():
    if not excel.exists():
        print('No existe', excel)
        return None
    try:
        df = pd.read_excel(excel, sheet_name='Equipos Conformados', header=1)
    except Exception as e:
        print('Error leyendo excel:', e)
        return None
    return df

def main():
    dfc = read_cleaned()
    if dfc is None:
        return 1
    print('\nDatos limpios: total rows =', len(dfc))
    if 'Carrera' in dfc.columns:
        col = 'Carrera'
    else:
        # try common alternatives
        col = next((c for c in dfc.columns if 'carr' in c.lower()), None)
    print('Carrera col in cleaned:', col)
    if col:
        cnts = dfc[col].fillna('Desconocida').value_counts()
        print('\nTop carreras in datos_limpios:')
        print(cnts.head(20).to_string())
        print('\nCount for Mercadotecnia:', int(cnts.get('Mercadotecnia', 0)))

    dft = read_teams()
    if dft is None:
        return 0
    print('\nEquipos Conformados: total rows =', len(dft))
    # find career column
    career_col = next((c for c in dft.columns if 'carr' in str(c).lower()), None)
    print('Career col in teams sheet:', career_col)
    if career_col:
        cnts2 = dft[career_col].fillna('Desconocida').value_counts()
        print('\nTop carreras in equipos_conformados:')
        print(cnts2.head(30).to_string())
        print('\nCount for Mercadotecnia in teams:', int(cnts2.get('Mercadotecnia', 0)))

    # Detectar estudiantes en datos_limpios que NO estén en equipos_conformados
    # Preferir match por carnet si existe, sino por nombre normalizado
    carnet_col_cleaned = next((c for c in dfc.columns if 'carnet' in str(c).lower()), None)
    carnet_col_teams = next((c for c in dft.columns if 'carnet' in str(c).lower()), None)
    nombre_col_cleaned = next((c for c in dfc.columns if 'nombre' in str(c).lower()), None)
    nombre_col_teams = next((c for c in dft.columns if 'nombre' in str(c).lower()), None)

    def norm(s: str) -> str:
        return str(s).strip().lower()

    if carnet_col_cleaned and carnet_col_teams:
        set_teams = set(dft[carnet_col_teams].astype(str).str.strip().str.lower().replace({'nan': ''}))
        missing = dfc[~dfc[carnet_col_cleaned].astype(str).str.strip().str.lower().isin(set_teams)]
    elif nombre_col_cleaned and nombre_col_teams:
        set_teams = set(dft[nombre_col_teams].astype(str).str.strip().str.lower())
        missing = dfc[~dfc[nombre_col_cleaned].astype(str).str.strip().str.lower().isin(set_teams)]
    else:
        missing = pd.DataFrame()

    if not missing.empty:
        print('\nEstudiantes en datos_limpios.csv que NO aparecen en equipos_conformados.xlsx:')
        # mostrar columnas de interes
        show_cols = []
        for c in ('Nombre', 'Nombre completo', nombre_col_cleaned):
            if c and c in missing.columns and c not in show_cols:
                show_cols.append(c)
        if 'Carrera' in missing.columns:
            show_cols.append('Carrera')
        if carnet_col_cleaned and carnet_col_cleaned in missing.columns:
            show_cols.append(carnet_col_cleaned)
        print(missing[show_cols].to_string(index=False))
    else:
        print('\nTodos los estudiantes de datos_limpios están presentes en equipos_conformados (por carnet/nombre).')

if __name__ == '__main__':
    sys.exit(main())
