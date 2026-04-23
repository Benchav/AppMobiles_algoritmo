import pandas as pd
import matplotlib.pyplot as plt
import os
from src.config import OUTPUT_TEAMS_FILE, OUTPUT_COUNTS_FILE, OUTPUT_DIR

def export_counts(df):
    conteo = df.groupby(['Area', 'Carrera_Normalizada', 'Año']).size().reset_index(name='Cantidad')
    conteo.to_csv(OUTPUT_COUNTS_FILE, index=False, encoding='utf-8-sig')
    print(f"Conteo exportado exitosamente a: {OUTPUT_COUNTS_FILE}")
    
    plt.figure(figsize=(10, 6))
    area_counts = df['Area'].value_counts()
    area_counts.plot(kind='bar', color=['skyblue', 'lightgreen', 'salmon', 'gold'])
    plt.title('Conteo de Estudiantes por Área')
    plt.xlabel('Área')
    plt.ylabel('Cantidad de Estudiantes')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    img_path = os.path.join(OUTPUT_DIR, 'conteo_areas.png')
    plt.savefig(img_path)
    print(f"Imagen del conteo exportada a: {img_path}")

def export_teams(teams_df):
    if teams_df.empty:
        print("No se pudieron formar equipos. El archivo Excel estará vacío.")
        
    teams_df.to_excel(OUTPUT_TEAMS_FILE, index=False)
    print(f"Equipos exportados exitosamente a: {OUTPUT_TEAMS_FILE}")
