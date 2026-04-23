"""
team_builder.py
---------------
Capa de logica de negocio: conformacion de equipos multidisciplinarios.

Reglas obligatorias por equipo (5 integrantes ideales):
  • 2 de Ingenieria en Sistemas de Informacion (4to o 5to anno)
  • 1 de Otra Ingenieria (Industrial o Telematica)
  • 1 de Ciencias Economicas
  • 1 de Ciencias Humanidades y Educacion

Prioridad de formacion:
  - Equipos COMPLETOS (5 integrantes) primero.
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


def build_teams(df: pd.DataFrame) -> pd.DataFrame:
    """
    Genera equipos de hasta 5 integrantes siguiendo las reglas multidisciplinarias.
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

    # Equipos completos posibles con los 4 roles
    equipos_completos_posibles = min(n_sis // 2, n_ing, n_eco, n_hum)
    equipos_base_posibles      = min(n_sis // 2, n_ing)

    print(f"\n  Disponibles por area:")
    print(f"    - Sistemas de Informacion (4to/5to anno): {n_sis}")
    print(f"    - Otra Ingenieria:                        {n_ing}")
    print(f"    - Ciencias Economicas:                    {n_eco}")
    print(f"    - Humanidades y Educacion:                {n_hum}")
    print(f"\n  Equipos completos (5 integrantes) posibles: {equipos_completos_posibles}")
    print(f"  Equipos base   (min 3 integrantes) posibles: {equipos_base_posibles}")

    # ── Formacion de equipos ──────────────────────────────────────────────────
    registros   = []
    equipo_num  = 1
    idx_sis = 0
    idx_ing = 0
    idx_eco = 0
    idx_hum = 0

    def get_val(pool: pd.DataFrame, idx: int, col: str):
        try:
            return pool.at[idx, col]
        except (KeyError, IndexError):
            return ''

    while idx_sis + 1 < len(pool_sis) and idx_ing < len(pool_ing):

        # ── 3 roles OBLIGATORIOS ─────────────────────────────────────────────
        candidatos = [
            (pool_sis, idx_sis),
            (pool_sis, idx_sis + 1),
            (pool_ing, idx_ing),
        ]
        idx_sis += 2
        idx_ing += 1

        # ── Rol Economicas (opcional pero prioritario para llegar a 5) ───────
        if idx_eco < len(pool_eco):
            candidatos.append((pool_eco, idx_eco))
            idx_eco += 1

        # ── Rol Humanidades (opcional) ────────────────────────────────────────
        if idx_hum < len(pool_hum):
            candidatos.append((pool_hum, idx_hum))
            idx_hum += 1

        nombre_equipo = f"Equipo {equipo_num}"

        for miembro_num, (pool, pidx) in enumerate(candidatos, start=1):
            registros.append({
                'Equipo':  nombre_equipo,
                '#':       miembro_num,
                'Nombre':  get_val(pool, pidx, nombre_col),
                'Carnet':  get_val(pool, pidx, carnet_col),
                'Carrera': get_val(pool, pidx, 'Carrera_Normalizada'),
                'Area':    get_val(pool, pidx, 'Area'),
                'Año':     get_val(pool, pidx, 'Año'),
            })

        equipo_num += 1

    # ── Reporte final ─────────────────────────────────────────────────────────
    total_equipos    = equipo_num - 1
    total_asignados  = len(registros)
    completos = sum(
        1 for eq in pd.DataFrame(registros).groupby('Equipo').size()
        if eq == 5
    ) if registros else 0
    parciales = total_equipos - completos

    print(f"\n  Resultado:")
    print(f"    Equipos conformados:   {total_equipos}")
    print(f"    Equipos completos (5): {completos}")
    print(f"    Equipos parciales:     {parciales}")
    print(f"    Estudiantes asignados: {total_asignados}")

    if n_eco == 0:
        print("\n  [AVISO] No hay inscritos de Ciencias Economicas.")
        print("          Para equipos completos de 5, se requieren estudiantes de esa area.")
    if n_hum < total_equipos:
        print(f"\n  [AVISO] Humanidades ({n_hum}) no alcanza para todos los equipos ({total_equipos}).")

    return pd.DataFrame(registros)
