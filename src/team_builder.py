"""
team_builder.py
---------------
Capa de logica de negocio: conformacion de equipos multidisciplinarios.

Reglas obligatorias por equipo (6 integrantes ideales):
  • 2 de Ingenieria en Sistemas de Informacion (4to o 5to año)
  • 1 de Otra Ingenieria (Industrial o Telematica)
  • 1 de Ciencias Economicas
  • 1 de Ciencias Humanidades y Educacion
  • 1 integrante adicional (filler) elegido para completar el equipo
    procurando balance entre areas y carreras.

Prioridad de formacion:
  - Equipos COMPLETOS (6 integrantes) primero.
  - Si alguna area se agota, se forman equipos parciales con los disponibles.
  - Los 3 roles OBLIGATORIOS son: 2xSistemas + 1xOtraIngenieria.
    Sin esos 3, no se forma equipo.

Aleatoriedad garantizada:
  - Cada ejecucion mezcla los pools con semilla de tiempo (no fija),
    asegurando combinaciones siempre distintas entre corridas.
"""

import random
import time

import pandas as pd
from src.config import AREA_SISTEMAS, AREA_INGENIERIA, AREA_ECONOMICAS, AREA_HUMANIDADES

# Tamaño objetivo de cada equipo (6 integrantes según nueva regla)
TEAM_SIZE = 6


def build_teams(df: pd.DataFrame) -> pd.DataFrame:
    """
    Genera equipos de hasta TEAM_SIZE integrantes siguiendo las reglas multidisciplinarias.
    Prioriza equipos COMPLETOS. Los 3 roles base (2xSistemas + 1xIngenieria)
    son obligatorios para que se forme un equipo.

    Retorna DataFrame con todos los equipos y sus integrantes.
    """

    nombre_col = df.attrs.get('nombre_col', 'Nombre')
    carnet_col  = df.attrs.get('carnet_col', 'Carnet')

    # ── Semilla aleatoria basada en tiempo → garantiza variacion entre corridas
    seed = int(time.time() * 1000) % (2**32)
    random.seed(seed)

    # ── Pools por area (4to y 5to anno para Sistemas; todos los annos para el resto)
    pool_sis = (
        df[(df['Area'] == AREA_SISTEMAS) & (df['Año_Num'].isin([4, 5]))]
        .copy()
        .sample(frac=1, random_state=seed % (2**31))
        .reset_index(drop=True)
    )
    pool_ing = (
        df[df['Area'] == AREA_INGENIERIA]
        .copy()
        .sample(frac=1, random_state=(seed + 1) % (2**31))
        .reset_index(drop=True)
    )
    pool_eco = (
        df[df['Area'] == AREA_ECONOMICAS]
        .copy()
        .sample(frac=1, random_state=(seed + 2) % (2**31))
        .reset_index(drop=True)
    )
    pool_hum = (
        df[df['Area'] == AREA_HUMANIDADES]
        .copy()
        .sample(frac=1, random_state=(seed + 3) % (2**31))
        .reset_index(drop=True)
    )

    n_sis = len(pool_sis)
    n_ing = len(pool_ing)
    n_eco = len(pool_eco)
    n_hum = len(pool_hum)

    total_available = n_sis + n_ing + n_eco + n_hum

    # Equipos completos posibles considerando los roles obligatorios y el tamaño
    equipos_completos_posibles = min(n_sis // 2, n_ing, n_eco, n_hum, total_available // TEAM_SIZE)
    equipos_base_posibles = min(n_sis // 2, n_ing)

    print(f"\n  Disponibles por area:")
    print(f"    - Sistemas de Informacion (4to/5to año): {n_sis}")
    print(f"    - Otra Ingenieria:                        {n_ing}")
    print(f"    - Ciencias Economicas:                    {n_eco}")
    print(f"    - Humanidades y Educacion:                {n_hum}")
    print(f"\n  Equipos completos ({TEAM_SIZE} integrantes) posibles: {equipos_completos_posibles}")
    print(f"  Equipos base   (min 3 integrantes) posibles: {equipos_base_posibles}")

    # ── Formacion de equipos ──────────────────────────────────────────────────
    equipos_list = []
    idx_sis = 0
    idx_ing = 0
    idx_eco = 0
    idx_hum = 0

    while idx_sis + 1 < len(pool_sis) and idx_ing < len(pool_ing):

        # ── 3 roles OBLIGATORIOS ─────────────────────────────────────────────
        candidatos = [
            (pool_sis, idx_sis),
            (pool_sis, idx_sis + 1),
            (pool_ing, idx_ing),
        ]
        idx_sis += 2
        idx_ing += 1

        # ── Rol Economicas (opcional pero prioritario)
        if idx_eco < len(pool_eco):
            candidatos.append((pool_eco, idx_eco))
            idx_eco += 1

        # ── Rol Humanidades (opcional) ────────────────────────────────────────
        if idx_hum < len(pool_hum):
            candidatos.append((pool_hum, idx_hum))
            idx_hum += 1

        # Rellenar hasta TEAM_SIZE el equipo eligiendo de la pool con más remanente
        while len(candidatos) < TEAM_SIZE:
            remain = {
                'sis': len(pool_sis) - idx_sis,
                'ing': len(pool_ing) - idx_ing,
                'eco': len(pool_eco) - idx_eco,
                'hum': len(pool_hum) - idx_hum,
            }
            # seleccionar la area con mayor remanente
            area_choice, area_count = max(remain.items(), key=lambda kv: kv[1])
            if area_count <= 0:
                break
            if area_choice == 'sis':
                candidatos.append((pool_sis, idx_sis))
                idx_sis += 1
            elif area_choice == 'ing':
                candidatos.append((pool_ing, idx_ing))
                idx_ing += 1
            elif area_choice == 'eco':
                candidatos.append((pool_eco, idx_eco))
                idx_eco += 1
            else:
                candidatos.append((pool_hum, idx_hum))
                idx_hum += 1

        equipos_list.append(candidatos)

    # Recolectar a los estudiantes sobrantes
    leftovers = []
    while idx_sis < len(pool_sis):
        leftovers.append((pool_sis, idx_sis))
        idx_sis += 1
    while idx_ing < len(pool_ing):
        leftovers.append((pool_ing, idx_ing))
        idx_ing += 1
    while idx_eco < len(pool_eco):
        leftovers.append((pool_eco, idx_eco))
        idx_eco += 1
    while idx_hum < len(pool_hum):
        leftovers.append((pool_hum, idx_hum))
        idx_hum += 1

    def get_val(pool: pd.DataFrame, idx: int, col: str):
        try:
            return pool.at[idx, col]
        except (KeyError, IndexError):
            return ''

    # Agrupar sobrantes por carrera para distribuirlos de forma balanceada
    from collections import defaultdict
    import math

    leftovers_by_career = defaultdict(list)
    for p, idx in leftovers:
        carrera = get_val(p, idx, 'Carrera_Normalizada')
        leftovers_by_career[carrera].append((p, idx))

    # Ordenar carreras por cantidad (descendente) para distribuir las mas comunes primero
    sorted_careers = sorted(leftovers_by_career.keys(), key=lambda c: len(leftovers_by_career[c]), reverse=True)

    # Calcular cuantos equipos nuevos necesitamos
    total_leftovers = len(leftovers)
    slots_in_base = sum(TEAM_SIZE - len(eq) for eq in equipos_list)
    if total_leftovers > slots_in_base:
        remaining = total_leftovers - slots_in_base
        new_teams_count = math.ceil(remaining / TEAM_SIZE)
        for _ in range(new_teams_count):
            equipos_list.append([])

    # Distribuir estudiantes buscando maxima diversidad
    for carrera in sorted_careers:
        students = leftovers_by_career[carrera]
        for student in students:
            valid_teams = [eq for eq in equipos_list if len(eq) < TEAM_SIZE]
            if not valid_teams:
                # Fallback por si acaso (no deberia pasar con el math.ceil)
                equipos_list[-1].append(student)
                continue
                
            # Buscar equipos ideales (sin esta carrera, o < 2 si es Sistemas)
            best_candidates = []
            for eq in valid_teams:
                count_career = sum(1 for (p, i) in eq if get_val(p, i, 'Carrera_Normalizada') == carrera)
                area = get_val(student[0], student[1], 'Area')
                
                if area == AREA_SISTEMAS:
                    if count_career < 2:
                        best_candidates.append(eq)
                else:
                    if count_career == 0:
                        best_candidates.append(eq)
                        
            if best_candidates:
                # De los ideales, elegir el que tenga menos integrantes
                best_team = min(best_candidates, key=len)
                best_team.append(student)
            else:
                # Si es matematicamente imposible evitar repetir carrera, distribuir equitativamente
                best_team = min(valid_teams, key=len)
                best_team.append(student)

    registros = []
    for i, eq in enumerate(equipos_list, start=1):
        nombre_equipo = f"Equipo {i}"
        for miembro_num, (pool, pidx) in enumerate(eq, start=1):
            registros.append({
                'Equipo':  nombre_equipo,
                '#':       miembro_num,
                'Nombre':  get_val(pool, pidx, nombre_col),
                'Carnet':  get_val(pool, pidx, carnet_col),
                'Carrera': get_val(pool, pidx, 'Carrera_Normalizada'),
                'Area':    get_val(pool, pidx, 'Area'),
                'Año':     get_val(pool, pidx, 'Año'),
            })

    equipo_num = len(equipos_list) + 1

    # ── Reporte final ─────────────────────────────────────────────────────────
    total_equipos    = equipo_num - 1
    total_asignados  = len(registros)
    completos = sum(
        1 for eq in pd.DataFrame(registros).groupby('Equipo').size()
        if eq == TEAM_SIZE
    ) if registros else 0
    parciales = total_equipos - completos

    print(f"\n  Resultado:")
    print(f"    Equipos conformados:   {total_equipos}")
    print(f"    Equipos completos ({TEAM_SIZE}): {completos}")
    print(f"    Equipos parciales:     {parciales}")
    print(f"    Estudiantes asignados: {total_asignados}")

    if n_eco == 0:
        print("\n  [AVISO] No hay inscritos de Ciencias Economicas.")
        print(f"          Para equipos completos de {TEAM_SIZE}, se requieren estudiantes de esa area.")
    if n_hum < total_equipos:
        print(f"\n  [AVISO] Humanidades ({n_hum}) no alcanza para todos los equipos ({total_equipos}).")

    return pd.DataFrame(registros)
