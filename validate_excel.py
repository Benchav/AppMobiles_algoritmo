#!/usr/bin/env python3
"""Valida los contenidos de 'equipos_conformados.xlsx'.

Comprueba que en la hoja 'Estadísticas' los valores de 'Cantidad' y
'Porcentaje (%)' sean consistentes con los datos listados en la hoja
'Equipos Conformados'. También verifica que las carreras listadas en
Estadísticas coincidan con las presentes entre los integrantes asignados.

Salida: imprime un resumen y las discrepancias si las hay.
"""

from pathlib import Path
import sys

import pandas as pd


def find_col(cols, keywords):
    for c in cols:
        lc = str(c).lower()
        for k in keywords:
            if k in lc:
                return c
    return None


def main():
    xlsx = Path('datos') / 'equipos_conformados.xlsx'
    if not xlsx.exists():
        print(f"ERROR: no se encontró el archivo: {xlsx}")
        return 2

    try:
        # El archivo generado tiene una fila de título arriba, y los encabezados reales
        # están en la segunda fila (índice 1). Leemos con header=1 para capturar los
        # nombres de columna correctos.
        df_stats = pd.read_excel(xlsx, sheet_name='Estadísticas', header=1)
    except Exception as e:
        print('ERROR leyendo la hoja Estadísticas:', e)
        return 3

    try:
        df_teams = pd.read_excel(xlsx, sheet_name='Equipos Conformados', header=1)
    except Exception as e:
        print('ERROR leyendo la hoja Equipos Conformados:', e)
        return 4

    # Detectar columnas relevantes en la hoja de equipos
    area_col_teams = find_col(df_teams.columns, ['area', 'área'])
    career_col_teams = find_col(df_teams.columns, ['carr', 'carrera'])
    year_col_teams = find_col(df_teams.columns, ['año', 'ano', 'year'])
    name_col_teams = find_col(df_teams.columns, ['nombre'])

    if None in (area_col_teams, career_col_teams, year_col_teams, name_col_teams):
        print('ERROR: no se pudieron localizar todas las columnas esperadas en Equipos Conformados')
        print('Columnas detectadas:', list(df_teams.columns))
        return 5

    # Normalizar y tomar solo columnas necesarias
    df_teams = df_teams[[area_col_teams, career_col_teams, year_col_teams, name_col_teams]].copy()
    df_teams.columns = ['Area', 'Carrera', 'Año', 'Nombre']
    df_teams['Año'] = df_teams['Año'].astype(str).str.strip()

    # Agrupar y contar
    group_counts = (
        df_teams.groupby(['Area', 'Carrera', 'Año'])
                .size()
                .reset_index(name='Cantidad_calc')
    )
    total_est = df_teams['Nombre'].nunique()
    group_counts['Porcentaje_calc'] = (group_counts['Cantidad_calc'] / total_est * 100).round(2)

    # Normalizar tabla de estadísticas leída del Excel
    area_col_stats = find_col(df_stats.columns, ['area', 'área'])
    career_col_stats = find_col(df_stats.columns, ['carr', 'carrera'])
    year_col_stats = find_col(df_stats.columns, ['año', 'ano', 'year'])
    cantidad_col_stats = find_col(df_stats.columns, ['cant', 'cantidad'])
    pct_col_stats = find_col(df_stats.columns, ['porcentaje', '%'])

    if None in (area_col_stats, career_col_stats, year_col_stats, cantidad_col_stats, pct_col_stats):
        print('ERROR: no se pudieron localizar todas las columnas esperadas en Estadísticas')
        print('Columnas detectadas:', list(df_stats.columns))
        return 6

    df_stats = df_stats[[area_col_stats, career_col_stats, year_col_stats, cantidad_col_stats, pct_col_stats]].copy()
    df_stats.columns = ['Area', 'Carrera', 'Año', 'Cantidad', 'Porcentaje']
    df_stats['Año'] = df_stats['Año'].astype(str).str.strip()
    df_stats['Cantidad'] = pd.to_numeric(df_stats['Cantidad'], errors='coerce').fillna(0).astype(int)
    # El porcentaje en el Excel puede estar como número (5.32) o como string '5.32%'
    df_stats['Porcentaje'] = pd.to_numeric(df_stats['Porcentaje'].astype(str).str.replace('%', '').str.replace(',', '.'), errors='coerce')

    # Merge para comparar
    merged = pd.merge(group_counts, df_stats, on=['Area', 'Carrera', 'Año'], how='outer', indicator=True)

    both = merged[merged['_merge'] == 'both'].copy()
    both['Cantidad_match'] = both['Cantidad'] == both['Cantidad_calc']
    both['Porcentaje_match'] = (both['Porcentaje'].round(2) == both['Porcentaje_calc'].round(2))

    left_only = merged[merged['_merge'] == 'left_only']
    right_only = merged[merged['_merge'] == 'right_only']

    print('\nResumen de validación:')
    print('  Total estudiantes asignados (nombres únicos):', total_est)
    print('  Total reportado en Estadísticas (suma Cantidad):', int(df_stats['Cantidad'].sum()))
    print('  Grupos concordantes (tanto Cantidad como Porcentaje):', both[(both['Cantidad_match']) & (both['Porcentaje_match'])].shape[0])
    print('  Grupos con discrepancias (mismatched cantidad/porcentaje):', both.shape[0] - both[(both['Cantidad_match']) & (both['Porcentaje_match'])].shape[0])
    print('  Grupos presentes en equipos pero NO en estadisticas:', left_only.shape[0])
    print('  Grupos presentes en estadisticas pero NO en equipos:', right_only.shape[0])

    if not left_only.empty:
        print('\nGrupos en equipos (no en estadisticas):')
        print(left_only[['Area', 'Carrera', 'Año', 'Cantidad_calc']].to_string(index=False))

    if not right_only.empty:
        print('\nGrupos en estadisticas (no en equipos):')
        print(right_only[['Area', 'Carrera', 'Año', 'Cantidad']].to_string(index=False))

    mismatches = both[~(both['Cantidad_match'] & both['Porcentaje_match'])]
    if not mismatches.empty:
        print('\nDiscrepancias encontradas:')
        print(mismatches[['Area', 'Carrera', 'Año', 'Cantidad_calc', 'Cantidad', 'Porcentaje_calc', 'Porcentaje']].to_string(index=False))
        return 10

    print('\nOK: todas las filas de Estadísticas coinciden con los datos de Equipos Conformados.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
