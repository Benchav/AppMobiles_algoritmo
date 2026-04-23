import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.config import INPUT_FILE, OUTPUT_DIR
from src.data_loader import load_and_clean_data
from src.team_builder import build_teams
from src.exporter import export_counts, export_teams

def main():
    print("Iniciando algoritmo de conformación de equipos...")
    
    if not os.path.exists(INPUT_FILE):
        print(f"Error: No se encontró el archivo de datos en la ruta esperada:\n{INPUT_FILE}")
        return
        
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    print("Cargando y limpiando datos (eliminando duplicados)...")
    df = load_and_clean_data(INPUT_FILE)
    print(f"Datos cargados. Total estudiantes únicos: {len(df)}")
    
    print("Exportando conteos y generando gráfico de áreas...")
    export_counts(df)
    
    print("Generando equipos aleatorios con reglas establecidas...")
    teams_df = build_teams(df)
    
    print("Exportando equipos a Excel...")
    export_teams(teams_df)
    
    print("¡Proceso finalizado exitosamente!")

if __name__ == "__main__":
    main()
