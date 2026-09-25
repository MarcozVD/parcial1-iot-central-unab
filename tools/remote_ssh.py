#!/usr/bin/env python3
"""
remote_ssh.py - Ejecutar comandos remotos SSH con credenciales de la carpeta Downloads.

Uso:
    python3 tools/remote_ssh.py <usuario>@<host> <comando>
    python3 tools/remote_ssh.py ubuntu@52.252.133.127 "ls -la /home/ubuntu"
    python3 tools/remote_ssh.py ubuntu@52.252.133.127 "cd ~/Parcial1_IoT_Central && python3 dispositivos/python/dc_supervisor.py"

Si ~/.ssh/id_rsa no existe, intenta cargar la llave de Downloads/<archivo>.pem.
"""
from __future__ import annotations

import argparse
import pathlib
import subprocess
import sys


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("remote", help="usuario@host")
    ap.add_argument("comando", help="comando a ejecutar")
    ap.add_argument("--puerto", "-p", type=int, default=22)
    ap.add_argument("--llave", "-i", help="ruta a la llave privada (.pem); si no, busca en Downloads")
    args = ap.parse_args()

    # Buscar la llave privada
    llave = None
    if args.llave:
        llave = pathlib.Path(args.llave)
    else:
        # Intentar ~/.ssh/id_rsa
        default_ssh = pathlib.Path.home() / ".ssh" / "id_rsa"
        if default_ssh.exists():
            llave = default_ssh
        else:
            # Buscar en Downloads (primer .pem que encuentre)
            downloads = pathlib.Path.home() / "Downloads"
            pems = list(downloads.glob("*.pem"))
            if pems:
                llave = pems[0]
                print(f"Usando llave de Downloads: {llave}")

    if not llave or not llave.exists():
        print(f"ERROR: no se encontró llave privada (.ssh/id_rsa o *.pem en Downloads)")
        return 1

    # Preparar comando SSH
    cmd = [
        "ssh",
        "-p", str(args.puerto),
        "-i", str(llave),
        args.remote,
        args.comando
    ]

    print(f"Ejecutando: {' '.join(cmd[:4])}... {args.comando[:50]}")
    result = subprocess.run(cmd)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
