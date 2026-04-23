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


def _get_col(df: pd.DataFrame, attr: str, fallback: str) -> str:
    """Obtiene el nombre de columna guardado en attrs o usa el fallback."""
    return df.attrs.get(attr, fallback)


def build_teams(df: pd.DataFrame) -> pd.DataFrame:
    """
    Genera equipos completos de 5 integrantes siguiendo las reglas multidisciplinarias.
    Retorna un DataFrame con todos los equipos y sus integrantes.
    """

    nombre_col = _get_col(df, 'nombre_col', 'Nombre')
    carnet_col  = _get_col(df, 'carnet_col', 'Carnet')

    # ── Pools por área ──────────────────────────────────────────────────────────
    pool_sis = (
        df[(df['Area'] == AREA_SISTEMAS) & (df['Año_Num'].isin([4, 5]))]
        .copy()
        .sample(frac=1)          # aleatorizar
        .reset_index(drop=True)
    )
    pool_ing = (
        df[df['Area'] == AREA_INGENIERIA]
        .copy()
        .sample(frac=1)
        .reset_index(drop=True)
    )
    pool_eco = (
        df[df['Area'] == AREA_ECONOMICAS]
        .copy()
        .sample(frac=1)
        .reset_index(drop=True)
    )
    pool_hum = (
        df[df['Area'] == AREA_HUMANIDADES]
        .copy()
        .sample(frac=1)
        .reset_index(drop=True)
    )

    print(f"\n  📊 Disponibles por área:")
    print(f"     • Sistemas de Información (4to/5to): {len(pool_sis)}")
    print(f"     • Otra Ingeniería:                   {len(pool_ing)}")
    print(f"     • Ciencias Económicas:               {len(pool_eco)}")
    print(f"     • Humanidades y Educación:           {len(pool_hum)}")

    # ── Iteradores por área ─────────────────────────────────────────────────────
    it_sis = iter(pool_sis.itertuples(index=False))
    it_ing = iter(pool_ing.itertuples(index=False))
    it_eco = iter(pool_eco.itertuples(index=False))
    it_hum = iter(pool_hum.itertuples(index=False))

    def _next(it):
        try:
            return next(it)
        except StopIteration:
            return None

    # ── Formación de equipos ────────────────────────────────────────────────────
    registros = []
    equipo_num = 1

    while True:
        s1 = _next(it_sis)
        s2 = _next(it_sis)
        ing = _next(it_ing)

        # El equipo es válido solo si se cumplen los tres roles obligatorios
        if s1 is None or s2 is None or ing is None:
            break

        eco = _next(it_eco)
        hum = _next(it_hum)

        integrantes = [s1, s2, ing]
        if eco is not None:
            integrantes.append(eco)
        if hum is not None:
            integrantes.append(hum)

        nombre_equipo = f"Equipo {equipo_num}"

        for idx_miembro, row in enumerate(integrantes, start=1):
            registros.append({
                'Equipo':   nombre_equipo,
                '#':        idx_miembro,
                'Nombre':   getattr(row, nombre_col.replace(' ', '_'), getattr(row, '_7', '')),
                'Carnet':   getattr(row, carnet_col.replace(' ', '_'), getattr(row, '_6', '')),
                'Carrera':  row.Carrera_Normalizada,
                'Área':     row.Area,
                'Año':      row.Año,
            })

        equipo_num += 1

    total_equipos = equipo_num - 1
    total_asignados = sum(1 for r in registros)
    print(f"\n  ✅ Equipos conformados: {total_equipos}  |  Estudiantes asignados: {total_asignados}")

    # Advertencias si alguna área se agotó antes de terminar
    if _next(it_eco) is None and len(pool_eco) == 0:
        print("  ⚠  Sin estudiantes de Ciencias Económicas — equipos formados sin ese rol.")
    if _next(it_hum) is None and len(pool_hum) < total_equipos:
        print(f"  ⚠  Estudiantes de Humanidades insuficientes para todos los equipos.")

    return pd.DataFrame(registros)
