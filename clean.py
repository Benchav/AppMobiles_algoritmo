#!/usr/bin/env python3
"""Limpieza segura de archivos generados.

Uso:
  python clean.py        # interactivo: muestra archivos y pide confirmación
  python clean.py -y     # no interactivo: procede sin preguntar

El script elimina todos los archivos .csv, .xlsx y .png dentro de la carpeta
`datos/` (OUTPUT_DIR) y además elimina el CSV de datos limpios ubicado en
`data/datos_limpios.csv` (CLEANED_FILE). Solo actúa sobre esas rutas para
minimizar riesgo de borrados accidentales.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from src.config import OUTPUT_DIR, CLEANED_FILE
except Exception:
    # Intentar importar aun si se ejecuta desde otra ruta; si falla, informar y salir
    print("[ERROR] No se pudo importar src.config. Asegúrate de ejecutar el script desde la raíz del proyecto.")
    sys.exit(2)


def find_output_files(output_dir: Path) -> list[Path]:
    if not output_dir.exists() or not output_dir.is_dir():
        return []
    files: list[Path] = []
    for pattern in ("*.csv", "*.xlsx", "*.png"):
        files.extend(sorted(output_dir.glob(pattern)))
    return files


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Limpia archivos generados en datos/ y el CSV limpio en data/")
    parser.add_argument("-y", "--yes", action="store_true", help="Proceder sin pedir confirmación")
    args = parser.parse_args(argv)

    out_dir = Path(OUTPUT_DIR)
    cleaned = Path(CLEANED_FILE)

    to_delete = find_output_files(out_dir)
    if cleaned.exists():
        to_delete.append(cleaned)

    if not to_delete:
        print("No se encontraron archivos para eliminar en las rutas configuradas.")
        return 0

    print("Se han identificado los siguientes archivos para eliminar:")
    for p in to_delete:
        print(f"  - {p}")

    if not args.yes:
        try:
            resp = input("¿Desea eliminar estos archivos? [s/N]: ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print("\nOperacion cancelada por el usuario.")
            return 1
        if resp not in ("s", "si", "y", "yes"):
            print("Operacion cancelada. No se eliminaron archivos.")
            return 0

    errors = 0
    for p in to_delete:
        try:
            p.unlink()
            print(f"Eliminado: {p}")
        except Exception as exc:
            errors += 1
            print(f"Error al eliminar {p}: {exc}")

    if errors:
        print(f"Proceso finalizado con {errors} errores.")
        return 2

    print("Limpieza completada correctamente.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
