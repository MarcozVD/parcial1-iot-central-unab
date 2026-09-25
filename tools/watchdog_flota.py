#!/usr/bin/env python3
"""
watchdog_flota.py - vigila que el supervisor de la flota DC-ANDES-1 siga vivo.

- Si el supervisor NO esta corriendo, lo arranca de nuevo (proceso desprendido).
- Imprime SOLO cuando hace algo (patron watchdog: stdout vacio = todo bien).

Lo usa el cronjob de Hermes "Flota DC-ANDES-1 (watchdog)" cada 10 minutos.
"""
from __future__ import annotations

import pathlib
import subprocess
import sys

RAIZ = pathlib.Path(r"C:\Users\mvale\Documents\Parcial1_IoT_Central")
PY = RAIZ / ".venv" / "Scripts" / "python.exe"
DIR = RAIZ / "dispositivos" / "python"
PAUSA = RAIZ / "logs" / "PAUSA_FLOTA"

PS_CONTAR = (
    "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | "
    "Where-Object { $_.CommandLine -like '*dc_supervisor.py*' } | Measure-Object | "
    "Select-Object -ExpandProperty Count"
)


def supervisores_vivos() -> int:
    p = subprocess.run(["powershell", "-NoProfile", "-Command", PS_CONTAR],
                       capture_output=True, text=True, timeout=90)
    salida = (p.stdout or "").strip().splitlines()
    try:
        return int(salida[-1]) if salida else 0
    except ValueError:
        return 0


def arrancar() -> None:
    subprocess.run(["powershell", "-NoProfile", "-Command",
                    f"Start-Process -FilePath '{PY}' -ArgumentList 'dc_supervisor.py' "
                    f"-WorkingDirectory '{DIR}' -WindowStyle Hidden"],
                   capture_output=True, text=True, timeout=90)


def main():
    # pausa explicita (maquina apagada o ventana cerrada a proposito): no resucitar nada
    if PAUSA.exists():
        return 0
    n = supervisores_vivos()
    if n > 0:
        return 0
    arrancar()
    print(f"WATCHDOG: el supervisor de la flota DC-ANDES-1 no estaba corriendo; "
          f"se reinicio a las {__import__('datetime').datetime.now():%Y-%m-%d %H:%M:%S}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
