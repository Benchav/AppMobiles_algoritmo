import os
import unicodedata

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
OUTPUT_DIR = os.path.join(BASE_DIR, 'datos')

INPUT_FILE = os.path.join(DATA_DIR, 'InscripciónConcurso Multidisciplinario de Aplicaciones Móviles 2026(1-89).csv')
OUTPUT_TEAMS_FILE = os.path.join(OUTPUT_DIR, 'equipos_conformados.xlsx')
OUTPUT_COUNTS_FILE = os.path.join(OUTPUT_DIR, 'conteo_estudiantes.csv')

# Reglas de equipos
AREA_SISTEMAS = "Sistemas de Información"
AREA_INGENIERIA = "Otra Ingeniería"
AREA_ECONOMICAS = "Ciencias Económicas"
AREA_HUMANIDADES = "Ciencias Humanidades y Educación"

def normalize_string(s):
    if not isinstance(s, str):
        return ""
    s = s.lower().strip()
    s = unicodedata.normalize('NFKD', s).encode('ASCII', 'ignore').decode('utf-8')
    return s

def get_area_from_major(major_raw):
    major = normalize_string(major_raw)
    
    # Humanidades y Educación
    if 'psicologia' in major or 'educacion' in major or 'educativa' in major or 'fisica matematica' in major:
        return AREA_HUMANIDADES
        
    # Sistemas de información
    if 'sistema' in major or 'informatica' in major:
        return AREA_SISTEMAS
    
    # Otra Ingeniería
    if 'industrial' in major or 'telematica' in major or 'telecomunicacion' in major:
        return AREA_INGENIERIA
        
    # Ciencias Económicas
    if 'economia' in major or 'administracion' in major or 'contaduria' in major or 'finanzas' in major or 'mercadeo' in major or 'marketing' in major or 'contabilidad' in major or 'banca' in major:
        return AREA_ECONOMICAS
        
    return "Otra"
