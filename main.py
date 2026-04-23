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
from src.config import OUTPUT_DIR


def main():
    print("Iniciando algoritmo de conformacion de equipos...")

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

    # ── Paso 5: Exportar Excel ────────────────────────────────────────────────
    print("\nExportando equipos a Excel...")
    export_teams(teams_df)

    print("\nProceso finalizado exitosamente.")


if __name__ == "__main__":
    main()
