#!/usr/bin/env python3
"""
dc_supervisor.py - mantiene viva la flota scriptada del DC-ANDES-1 durante la ventana
de 4 dias (24-27 sep 2026): arranca cada nodo y lo reinicia si se cae.

Uso:
  .venv/Scripts/python.exe dispositivos/python/dc_supervisor.py            # primer plano
  .venv/Scripts/python.exe dispositivos/python/dc_supervisor.py --estado   # resumen

Cada nodo escribe su log en logs/<nodo>.out (stdout/stderr) y su telemetria en
logs/<device>.log + datos/<device>.csv.
"""
from __future__ import annotations

import json
import pathlib
import signal
import subprocess
import sys
import time
from datetime import datetime

RAIZ = pathlib.Path(__file__).resolve().parents[2]
PY = RAIZ / ".venv" / "Scripts" / "python.exe"
PYDIR = RAIZ / "dispositivos" / "python"
LOGS = RAIZ / "logs"
ESTADO = RAIZ / "logs" / "supervisor_estado.json"
PIDFILE = RAIZ / "logs" / "supervisor.pid"

NODOS = [
    ("sdk_mqtt", "dc_sdk_mqtt.py"),
    ("sdk_ws", "dc_sdk_ws.py"),
    ("paho", "dc_paho.py"),
    ("api_openmeteo", "dc_api_openmeteo.py"),
    ("api_aire", "dc_api_aire.py"),
    ("csv_replay", "dc_csv_replay.py"),
    ("http_bridge", "dc_http_bridge.py"),
    ("acceso_campo", "dc_acceso_sim.py"),
]

parar = {"v": False}


def log(texto: str) -> None:
    linea = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {texto}"
    print(linea, flush=True)
    with (LOGS / "supervisor.log").open("a", encoding="utf-8") as fh:
        fh.write(linea + "\n")


def estado(procs: dict) -> None:
    datos = {}
    for nombre, (p, arranques, ultimo) in procs.items():
        datos[nombre] = {"pid": p.pid if p and p.poll() is None else None,
                         "arranques": arranques, "ultimo_arranque": ultimo}
    ESTADO.write_text(json.dumps(datos, indent=1), encoding="utf-8")


def pid_vivo(pid: int) -> bool:
    salida = subprocess.run(["tasklist", "/FI", f"PID eq {pid}", "/NH"],
                            capture_output=True, text=True).stdout
    return str(pid) in salida


def supervisores_ajenos() -> list[int]:
    """Pids de OTROS supervisores vivos (proceso python con dc_supervisor.py)."""
    import os
    ps = ("Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | "
          "Where-Object { $_.CommandLine -like '*dc_supervisor.py*' } | "
          "Select-Object -ExpandProperty ProcessId")
    out = subprocess.run(["powershell", "-NoProfile", "-Command", ps],
                         capture_output=True, text=True, timeout=90).stdout
    pids = []
    for linea in out.split():
        try:
            p = int(linea)
        except ValueError:
            continue
        if p != os.getpid():
            pids.append(p)
    return pids


def tomar_testigo() -> bool:
    """Escribe el pid propio de forma atomica y desempata por antiguedad.

    Dos lanzadores pueden coincidir (el cronjob de Hermes y reanudar_flota.ps1):
    sin desempate, ambos arrancan sus ocho nodos y la telemetria se duplica.
    Regla: gana el supervisor con el pid mas bajo (el que arranco antes); el otro
    sale sin arrancar nodos. Se comprueba tras una ventana de gracia para que la
    otra instancia alcance a aparecer.
    """
    import os

    with PIDFILE.open("w", encoding="utf-8") as fh:
        fh.write(f"{os.getpid()}\n")
    time.sleep(7)  # ventana de gracia: deja aparecer a un lanzador simultaneo
    otros = supervisores_ajenos()
    if otros and min(otros) < os.getpid():
        log(f"otra instancia anterior sigue viva (pid {min(otros)}); esta sale sin arrancar nodos")
        return False
    if otros:
        log(f"hay otra instancia mas reciente (pid {max(otros)}); se ignora")
    return True


def main() -> int:
    if "--estado" in sys.argv:
        print(ESTADO.read_text(encoding="utf-8") if ESTADO.exists() else "sin estado")
        return 0

    LOGS.mkdir(parents=True, exist_ok=True)
    if not tomar_testigo():
        return 0
    log(f"supervisor iniciado (pid {__import__('os').getpid()}); {len(NODOS)} nodos")
    procs: dict[str, tuple] = {}

    def _salir(*_):
        parar["v"] = True
    signal.signal(signal.SIGINT, _salir)
    signal.signal(signal.SIGTERM, _salir)

    for nombre, script in NODOS:
        salida = (LOGS / f"{nombre}.out").open("a", encoding="utf-8")
        p = subprocess.Popen([str(PY), str(PYDIR / script)], cwd=str(PYDIR),
                             stdout=salida, stderr=subprocess.STDOUT)
        procs[nombre] = (p, 1, datetime.now().isoformat(timespec="seconds"))
        log(f"  arrancado {nombre} (pid {p.pid})")
        time.sleep(2)  # evita rafagas de DPS

    estado(procs)
    espera = {n: 10 for n, _ in NODOS}
    while not parar["v"]:
        time.sleep(15)
        for nombre, script in NODOS:
            p, arranques, _ = procs[nombre]
            if p.poll() is not None:
                log(f"  {nombre} termino (codigo {p.returncode}); reinicio #{arranques + 1} en "
                    f"{espera[nombre]} s")
                time.sleep(espera[nombre])
                espera[nombre] = min(60, espera[nombre] * 2)
                salida = (LOGS / f"{nombre}.out").open("a", encoding="utf-8")
                np_ = subprocess.Popen([str(PY), str(PYDIR / script)], cwd=str(PYDIR),
                                       stdout=salida, stderr=subprocess.STDOUT)
                procs[nombre] = (np_, arranques + 1, datetime.now().isoformat(timespec="seconds"))
                log(f"  {nombre} reiniciado (pid {np_.pid})")
            else:
                espera[nombre] = 10
        estado(procs)

    log("deteniendo nodos...")
    for nombre, (p, _, _) in procs.items():
        if p.poll() is None:
            p.terminate()
    time.sleep(5)
    for nombre, (p, _, _) in procs.items():
        if p.poll() is None:
            p.kill()
    log("supervisor detenido")
    PIDFILE.unlink(missing_ok=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
