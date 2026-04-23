"""
team_builder.py
---------------
Capa de lógica de negocio: conformación de equipos multidisciplinarios.

Reglas obligatorias por equipo (5 integrantes):
  • 2 de Ingeniería en Sistemas de Información (4to o 5to año)
  • 1 de Otra Ingeniería (Industrial o Telemática)
  • 1 de Ciencias Económicas
  • 1 de Ciencias Humanidades y Educación

Aleatoriedad garantizada: cada ejecución mezcla los pools antes de asignar,
asegurando composición diferente en cada corrida.
"""

import pandas as pd
from src.config import AREA_SISTEMAS, AREA_INGENIERIA, AREA_ECONOMICAS, AREA_HUMANIDADES


def build_teams(df: pd.DataFrame) -> pd.DataFrame:
    """
    Genera equipos completos de 5 integrantes siguiendo las reglas multidisciplinarias.
    Los tres primeros roles (2×Sistemas + 1×OtraIng) son obligatorios para formar equipo.
    Económicas y Humanidades se agregan si hay disponibles.

    Retorna un DataFrame con todos los equipos y sus integrantes.
    """

    nombre_col = df.attrs.get('nombre_col', 'Nombre')
    carnet_col  = df.attrs.get('carnet_col', 'Carnet')

    # ── Pools por área (aleatorizado) ────────────────────────────────────────
    pool_sis = (
        df[(df['Area'] == AREA_SISTEMAS) & (df['Año_Num'].isin([4, 5]))]
        .copy().sample(frac=1).reset_index(drop=True)
    )
    pool_ing = (
        df[df['Area'] == AREA_INGENIERIA]
        .copy().sample(frac=1).reset_index(drop=True)
    )
    pool_eco = (
        df[df['Area'] == AREA_ECONOMICAS]
        .copy().sample(frac=1).reset_index(drop=True)
    )
    pool_hum = (
        df[df['Area'] == AREA_HUMANIDADES]
        .copy().sample(frac=1).reset_index(drop=True)
    )

    print(f"\n  [INFO] Disponibles por area:")
    print(f"     - Sistemas de Informacion (4to/5to): {len(pool_sis)}")
    print(f"     - Otra Ingenieria:                   {len(pool_ing)}")
    print(f"     - Ciencias Economicas:               {len(pool_eco)}")
    print(f"     - Humanidades y Educacion:           {len(pool_hum)}")

    # ── Iteración por filas con índice entero ────────────────────────────────
    idx_sis = 0
    idx_ing = 0
    idx_eco = 0
    idx_hum = 0

    registros = []
    equipo_num = 1

    def get_val(pool, idx, col):
        """Lee un valor de forma segura, retorna '' si columna no existe."""
        try:
            return pool.at[idx, col]
        except (KeyError, IndexError):
            return ''

    while idx_sis + 1 < len(pool_sis) and idx_ing < len(pool_ing):
        # Los tres roles obligatorios
        candidatos = [
            (pool_sis, idx_sis),
            (pool_sis, idx_sis + 1),
            (pool_ing, idx_ing),
        ]
        idx_sis += 2
        idx_ing += 1

        # Roles opcionales (pero deseables)
        if idx_eco < len(pool_eco):
            candidatos.append((pool_eco, idx_eco))
            idx_eco += 1

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
                'Área':    get_val(pool, pidx, 'Area'),
                'Año':     get_val(pool, pidx, 'Año'),
            })

        equipo_num += 1

    total_equipos  = equipo_num - 1
    total_asignados = len(registros)
    print(f"\n  [OK] Equipos conformados: {total_equipos}  |  Estudiantes asignados: {total_asignados}")

    if len(pool_eco) == 0:
        print("  [WARN] Sin estudiantes de Ciencias Economicas — equipos con 4 integrantes base.")
    elif idx_eco < total_equipos:
        print(f"  [WARN] Economicas cubrieron {idx_eco}/{total_equipos} equipos.")

    if len(pool_hum) == 0:
        print("  [WARN] Sin estudiantes de Humanidades — equipos sin ese rol.")
    elif idx_hum < total_equipos:
        print(f"  [WARN] Humanidades cubrieron {idx_hum}/{total_equipos} equipos.")

    return pd.DataFrame(registros)
