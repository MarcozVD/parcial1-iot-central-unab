#!/usr/bin/env python3
"""
dc_supervisor_remote.py - Supervisor de flota para ejecución remota en Linux/Ubuntu.

Idéntico a dc_supervisor.py pero sin llamadas a PowerShell; usa ps/grep en su lugar.
Lanza los 8 nodos Python y supervisa que no mueran.
"""
from __future__ import annotations

import pathlib
import subprocess
import sys
import time
from datetime import datetime, timezone, timedelta

RAIZ = pathlib.Path(__file__).resolve().parents[2]
LOGS = RAIZ / "logs"
LOGS.mkdir(parents=True, exist_ok=True)

NODOS = [
    ("DC-RACKC-03", 30),    # Rack C, 30 s
    ("DC-HUMO-08", 45),     # Humo, 45 s
    ("DC-PASILLO-04", 60),  # Pasillo, 60 s
    ("DC-CLIMA-05", 900),   # Clima, 15 min
    ("DC-AIRE-06", 900),    # Aire, 15 min
    ("DC-ENERGIA-09", 120), # Energía, 2 min
    ("DC-ACCESO-10", 120),  # Acceso, 2 min
    ("DC-AGUA-07", 30),     # Agua, 30 s
]

TZ_LOCAL = timezone(timedelta(hours=-5))


def log(msg: str) -> None:
    """Escribir en el log con timestamp."""
    ts = datetime.now(tz=TZ_LOCAL).strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}")
    with open(LOGS / "supervisor.log", "a", encoding="utf-8") as f:
        f.write(f"[{ts}] {msg}\n")


def pids_de_nodo(device_id: str) -> list[int]:
    """Encontrar PIDs de procesos Python que corran este nodo."""
    try:
        out = subprocess.run(
            ["pgrep", "-f", f"dc_paho.py.*{device_id}"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return [int(line.strip()) for line in out.stdout.splitlines() if line.strip()]
    except Exception as e:
        log(f"error al buscar PID para {device_id}: {e}")
        return []


def lanzar_nodo(device_id: str, intervalo: int) -> bool:
    """Lanzar un nodo con dc_paho.py dentro de la venv."""
    try:
        # Usar python de la venv
        python_exe = RAIZ.parent / "venv_parcial" / "bin" / "python3"
        if not python_exe.exists():
            python_exe = sys.executable  # fallback
        
        cmd = [
            str(python_exe),
            str(RAIZ / "dispositivos" / "python" / "dc_paho.py"),
            device_id,
            str(intervalo)
        ]
        env = {
            "PYTHONPATH": str(RAIZ / "dispositivos" / "python"),
            "PATH": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
        }
        import os
        env.update(os.environ)
        
        # Capturar output en log del nodo (no DEVNULL, para diagnosticar si falla)
        nodo_log = LOGS / f"{device_id}.log"
        with open(nodo_log, "w") as logf:
            subprocess.Popen(cmd, env=env, stdout=logf, stderr=subprocess.STDOUT)
        
        log(f"lanzado {device_id} (intervalo {intervalo} s) -> {nodo_log}")
        return True
    except Exception as e:
        log(f"ERROR: no se pudo lanzar {device_id}: {e}")
        return False


def main() -> int:
    """Ciclo principal de supervisión."""
    log("supervisor iniciado (remoto Linux)")
    
    # Lanzar todos los nodos
    for device_id, intervalo in NODOS:
        lanzar_nodo(device_id, intervalo)
    
    log(f"flota de 8 nodos iniciada")
    
    # Vigilancia: cada 30 s verificar que sigan vivos
    try:
        while True:
            time.sleep(30)
            muertos = []
            for device_id, _ in NODOS:
                if not pids_de_nodo(device_id):
                    muertos.append(device_id)
            
            if muertos:
                log(f"ALERTA: nodos muertos: {', '.join(muertos)}")
                for device_id, intervalo in NODOS:
                    if device_id in muertos:
                        lanzar_nodo(device_id, intervalo)
            else:
                log(f"vigilancia OK: 8/8 nodos vivos")
    except KeyboardInterrupt:
        log("supervisor detenido por usuario")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
