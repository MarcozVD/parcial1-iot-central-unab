#!/usr/bin/env python3
"""Copia de seguridad del proyecto (repositorio + entregables) en un ZIP.

Excluye lo que no debe salir de la maquina o no aporta: .venv, .secrets (credenciales),
.playwright-cli, __pycache__ y los .pyc. Verifica al final que el ZIP no contenga secretos.

Uso:
    .venv/Scripts/python.exe tools/backup.py            # a OneDrive
    .venv/Scripts/python.exe tools/backup.py --destino <carpeta>
"""
from __future__ import annotations

import argparse
import datetime as dt
import pathlib
import zipfile

RAIZ = pathlib.Path(__file__).resolve().parents[1]
DESTINO_POR_DEFECTO = pathlib.Path.home() / "OneDrive" / "Parcial1_IoT_Central_backup"

EXCLUIR_DIRS = {".venv", ".secrets", ".playwright-cli", "__pycache__", "node_modules", ".mypy_cache"}
EXCLUIR_SUFIJOS = {".pyc", ".pyo"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--destino", default=str(DESTINO_POR_DEFECTO))
    args = ap.parse_args()

    destino = pathlib.Path(args.destino)
    destino.mkdir(parents=True, exist_ok=True)
    sello = dt.datetime.now().strftime("%Y%m%d_%H%M")
    zip_path = destino / f"Parcial1_IoT_Central_{sello}.zip"

    incluidos = 0
    bytes_totales = 0
    secretos = []
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for ruta in sorted(RAIZ.rglob("*")):
            rel = ruta.relative_to(RAIZ)
            if any(parte in EXCLUIR_DIRS for parte in rel.parts):
                continue
            if ruta.suffix in EXCLUIR_SUFIJOS:
                continue
            if ruta.is_dir():
                continue
            zf.write(ruta, rel.as_posix())
            incluidos += 1
            bytes_totales += ruta.stat().st_size
            if ".secrets" in rel.as_posix() or rel.name.endswith(".env"):
                secretos.append(rel.as_posix())

    tam = zip_path.stat().st_size
    print(f"zip: {zip_path}")
    print(f"archivos: {incluidos}  original: {bytes_totales/1e6:.1f} MB  comprimido: {tam/1e6:.1f} MB")
    print("secretos dentro del zip:", secretos or "ninguno")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
