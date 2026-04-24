"""
main.py
-------
Punto de entrada del algoritmo de conformacion de equipos multidisciplinarios.

Flujo de ejecucion:
  1. data_cleaner  → normaliza nombres de carreras y elimina duplicados en data/
  2. data_loader   → carga el CSV limpio y clasifica por area academica
  3. exporter      → genera graficos y CSV de conteo en datos/
  4. team_builder  → conforma equipos aleatorios siguiendo las reglas
  5. exporter      → exporta equipos a Excel profesional en datos/
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.data_cleaner import run_cleaner
from src.data_loader import load_and_clean_data
from src.team_builder import build_teams
from src.exporter import export_counts, export_teams
from src.config import OUTPUT_DIR, INPUT_FILE
from src.tutors import maybe_generate_tutors_if_missing, read_tutors, generate_tutors
from src.config import TUTORS_FILE, TUTOR_CARNET_START


def main():
    print("Iniciando algoritmo de conformacion de equipos...")

    # Verificar existencia de archivo de entrada antes de comenzar
    if not INPUT_FILE or not os.path.exists(INPUT_FILE):
        print("\n[ERROR] No se encontró el archivo de inscripciones en la carpeta data/.\n"
              "Por favor coloca el CSV de inscripciones dentro de data/ y asegúrate de que no sea 'datos_limpios.csv'.\n")
        sys.exit(1)

    # ── Paso 1: Limpieza y normalizacion de carreras ─────────────────────────
    cleaned_path = run_cleaner()

    # ── Paso 2: Carga del CSV limpio ─────────────────────────────────────────
    print("Cargando datos limpios...")
    df = load_and_clean_data(cleaned_path)
    print(f"  Total estudiantes unicos cargados: {len(df)}")

    # ── Paso 3: Graficos y CSV de conteo ─────────────────────────────────────
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    print("\nExportando conteos y graficos...")
    export_counts(df)

    # ── Paso 4: Conformacion de equipos ──────────────────────────────────────
    print("\nGenerando equipos aleatorios con reglas establecidas...")
    teams_df = build_teams(df)

    # ── Asignar tutores a cada equipo (solo si hay equipos)
    if teams_df is not None and not teams_df.empty:
        n_teams = teams_df['Equipo'].nunique()
        # generar archivo de tutores solo si NO existe
        maybe_generate_tutors_if_missing(n_teams)

        tutors_df = read_tutors()
        # si el archivo existe pero está vacío, generamos n_teams tutores para poder asignar
        if tutors_df.empty:
            tutors_df = generate_tutors(n_teams, start=TUTOR_CARNET_START, path=TUTORS_FILE)

        # asignación aleatoria: si hay menos tutores que equipos permitimos reemplazo
        replace = len(tutors_df) < n_teams
        chosen = tutors_df.sample(n=n_teams, replace=replace).reset_index(drop=True)

        # mapear cada equipo (en orden de aparición) a un tutor
        equipos_orden = list(dict.fromkeys(teams_df['Equipo'].tolist()))
        mapping_name = dict(zip(equipos_orden, chosen['Nombre'].astype(str)))
        mapping_carnet = dict(zip(equipos_orden, chosen['Carnet'].astype(str)))
        teams_df['Tutor'] = teams_df['Equipo'].map(mapping_name)
        teams_df['Tutor_Carnet'] = teams_df['Equipo'].map(mapping_carnet)

    # ── Paso 5: Exportar Excel ────────────────────────────────────────────────
    print("\nExportando equipos a Excel...")
    export_teams(teams_df)

    print("\nProceso finalizado exitosamente.")


if __name__ == "__main__":
    main()
