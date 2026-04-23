"""
data_cleaner.py
---------------
Capa de preprocesamiento: normalización de nombres de carreras.

Ejecuta ANTES de data_loader. Lee el CSV original, mapea todas las
variantes ortográficas y de escritura a un nombre canónico único por
carrera, y guarda el resultado como un CSV limpio en la misma carpeta
data/ con el sufijo _limpio.

Nombres canónicos definidos:
  Área Sistemas de Información:
    → "Ingenieria en Sistemas de Informacion"

  Área Otra Ingeniería:
    → "Ingenieria Industrial"
    → "Ingenieria en Telematica"

  Área Humanidades y Educación:
    → "Informatica Educativa"
    → "Psicologia"
    → "Fisica y Matematicas"

  Sin clasificar conocida:
    → "Otra" (se conserva el original pero se etiqueta)
"""

import os
import unicodedata

import pandas as pd

from src.config import INPUT_FILE, DATA_DIR


# ── Nombre del archivo limpio ────────────────────────────────────────────────
CLEANED_FILENAME = 'datos_limpios.csv'
CLEANED_FILE = os.path.join(DATA_DIR, CLEANED_FILENAME)

# ── Reglas de mapeo (orden importa: más específico primero) ──────────────────
# Cada entrada: (lista_de_palabras_clave, nombre_canonico)
# Se usa coincidencia sobre el texto normalizado (sin tildes, minúsculas).
MAPEO_CANONICO = [
    # ── Humanidades (verificar ANTES que "sistema" para "informatica educativa")
    (['informatica educativa', 'informaticaeducativa'],
     'Informatica Educativa'),

    (['psicolog'],
     'Psicologia'),

    (['fisica matematica', 'ciencias de la educacion', 'fisica y matematica',
      'matematica', 'fisica'],
     'Fisica y Matematicas'),

    # ── Sistemas de Información
    (['sistema', 'informatico', 'informatica'],
     'Ingenieria en Sistemas de Informacion'),

    # ── Otras Ingenierías
    (['industrial'],
     'Ingenieria Industrial'),

    (['telematica', 'telecomunicacion'],
     'Ingenieria en Telematica'),
]


def _normalize(text: str) -> str:
    """Minúsculas, sin tildes, sin espacios redundantes."""
    if not isinstance(text, str):
        return ''
    text = text.lower().strip()
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')
    return text


def _sanitize_unicode(val):
    """Elimina caracteres del bloque Unicode matemático cursivo (U+1D000–1D7FF)
    que algunos estudiantes introdujeron al copiar texto de otras fuentes."""
    if not isinstance(val, str):
        return val
    result = []
    for ch in val:
        cp = ord(ch)
        if 0x1D000 <= cp <= 0x1D7FF:
            # Intentar desglosar en ASCII equivalente
            cleaned = unicodedata.normalize('NFKD', ch).encode('ASCII', 'ignore').decode('utf-8')
            result.append(cleaned if cleaned else '')
        else:
            result.append(ch)
    return ''.join(result).strip()


def canonicalize_career(raw: str) -> str:
    """
    Recibe el nombre de carrera tal como está en el CSV (con variantes, errores
    ortográficos, mayúsculas mezcladas, tildes, etc.) y retorna el nombre
    canónico estandarizado.
    """
    norm = _normalize(raw)

    for keywords, canonical in MAPEO_CANONICO:
        for kw in keywords:
            if kw in norm:
                return canonical

    # No encontró regla → conservar limpio pero señalar
    return raw.strip()


def run_cleaner() -> str:
    """
    Lee el CSV original, limpia y normaliza nombres de carreras,
    elimina duplicados, y guarda el archivo limpio en data/.
    Retorna la ruta al archivo limpio.
    """
    print("\n" + "=" * 60)
    print("  [LIMPIEZA]  Normalizacion de datos de entrada")
    print("=" * 60)

    # 1. Cargar CSV original
    try:
        df = pd.read_csv(INPUT_FILE, sep=';', encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(INPUT_FILE, sep=';', encoding='latin1')

    print(f"  Registros originales leidos: {len(df)}")

    # 2. Sanitizar caracteres Unicode matemáticos en TODAS las columnas texto
    for col in df.select_dtypes(include='object').columns:
        df[col] = df[col].apply(_sanitize_unicode)

    # 3. Identificar columna Carrera
    carrera_col = next(
        (col for col in df.columns if col.strip().lower() == 'carrera'),
        None
    )
    if carrera_col is None:
        print("  [ERROR] No se encontro columna 'Carrera' en el CSV.")
        return INPUT_FILE

    # 4. Mostrar variantes antes de normalizar
    variantes_antes = df[carrera_col].dropna().unique()
    print(f"\n  Variantes de carrera encontradas ({len(variantes_antes)}):")
    for v in sorted(variantes_antes):
        canonical = canonicalize_career(v)
        marker = '  OK ' if v.strip() == canonical else '  -> '
        print(f"    {marker}  {repr(v.strip())}")
        if v.strip() != canonical:
            print(f"           => {repr(canonical)}")

    # 5. Aplicar normalización
    df[carrera_col] = df[carrera_col].apply(
        lambda x: canonicalize_career(x) if pd.notnull(x) else x
    )

    # 6. Eliminar duplicados por Nombre Completo (manteniendo el último)
    nombre_col = next(
        (col for col in df.columns if 'Nombre completo' in col),
        None
    )
    if nombre_col:
        df['_norm_nombre'] = df[nombre_col].apply(_normalize)
        antes = len(df)
        df = df.drop_duplicates(subset=['_norm_nombre'], keep='last')
        df = df.drop(columns=['_norm_nombre'])
        eliminados = antes - len(df)
        if eliminados:
            print(f"\n  [WARN] Duplicados de nombre eliminados: {eliminados}")

    # 7. Eliminar duplicados por Carnet
    carnet_col = next(
        (col for col in df.columns if 'carnet' in col.lower()),
        None
    )
    if carnet_col:
        df['_norm_carnet'] = (
            df[carnet_col].astype(str)
            .str.strip()
            .str.replace(r'[\s,\-\.]', '', regex=True)
            .str.lower()
            .replace(['', 'nan', 'none'], pd.NA)
        )
        df_con = df.dropna(subset=['_norm_carnet'])
        df_sin = df[df['_norm_carnet'].isna()]
        antes = len(df)
        df_con = df_con.drop_duplicates(subset=['_norm_carnet'], keep='last')
        df = pd.concat([df_con, df_sin], ignore_index=True)
        df = df.drop(columns=['_norm_carnet'])
        eliminados_c = antes - len(df)
        if eliminados_c:
            print(f"  [WARN] Duplicados de carnet eliminados: {eliminados_c}")

    # 8. Resumen de carreras canonizadas
    print(f"\n  Carreras canonicas resultantes:")
    for carrera, n in df[carrera_col].value_counts().items():
        print(f"    {n:3}  {carrera}")

    print(f"\n  Registros limpios finales: {len(df)}")

    # 9. Guardar CSV limpio
    df.to_csv(CLEANED_FILE, sep=';', index=False, encoding='utf-8-sig')
    print(f"\n  [OK] CSV limpio guardado en: {CLEANED_FILE}")
    print("=" * 60 + "\n")

    return CLEANED_FILE
