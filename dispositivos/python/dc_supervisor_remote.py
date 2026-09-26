#!/usr/bin/env python3
"""
dc_supervisor_remote.py - Supervisor de la flota DC-ANDES-1 para la maquina Ubuntu.

Mismo diseno que el supervisor local (una entrada por SCRIPT, no por dispositivo):
cada script de dispositivos/python/ tiene su propio DEVICE_ID fijo en el codigo, asi que
pasarle un id por argumento no hace nada (error detectado el 26-sep: los procesos
publicaban todos el mismo dispositivo y peleaban por la conexion del hub).

Vigila cada proceso, lo relanza si muere y respeta la bandera de pausa logs/PAUSA_FLOTA.
"""
from __future__ import annotations

import os
import pathlib
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone

RAIZ = pathlib.Path(__file__).resolve().parents[2]
PYDIR = RAIZ / "dispositivos" / "python"
LOGS = RAIZ / "logs"
LOGS.mkdir(parents=True, exist_ok=True)

PAUSA = LOGS / "PAUSA_FLOTA"
TZ_LOCAL = timezone(timedelta(hours=-5))

# (nombre para el registro, script) - el dispositivo lo fija cada script
NODOS = [
    ("sdk_mqtt", "dc_sdk_mqtt.py"),            # DC-RACKC-03   (SDK MQTT/TLS)
    ("sdk_ws", "dc_sdk_ws.py"),                # DC-PASILLO-04 (SDK WebSocket)
    ("paho", "dc_paho.py"),                    # DC-HUMO-08    (paho, SAS manual)
    ("api_openmeteo", "dc_api_openmeteo.py"),  # DC-CLIMA-05
    ("api_aire", "dc_api_aire.py"),            # DC-AIRE-06
    ("csv_replay", "dc_csv_replay.py"),        # DC-ENERGIA-09
    ("http_bridge", "dc_http_bridge.py"),      # DC-ACCESO-10
    ("acceso_campo", "dc_acceso_sim.py"),      # simulador de campo (alimenta al puente)
]

PY = RAIZ.parent / "venv_parcial" / "bin" / "python3"
if not PY.exists():
    PY = pathlib.Path(sys.executable)


def log(texto: str) -> None:
    marca = datetime.now(tz=TZ_LOCAL).strftime("%Y-%m-%d %H:%M:%S")
    linea = f"[{marca}] {texto}"
    print(linea, flush=True)
    with (LOGS / "supervisor.log").open("a", encoding="utf-8") as f:
        f.write(linea + "\n")


def arrancar(nombre: str, script: str) -> subprocess.Popen:
    salida = (LOGS / f"{nombre}.out").open("a", encoding="utf-8")
    env = dict(os.environ)
    env["PYTHONPATH"] = str(PYDIR)
    env["PYTHONUNBUFFERED"] = "1"
    return subprocess.Popen([str(PY), str(PYDIR / script)], cwd=str(PYDIR),
                            stdout=salida, stderr=subprocess.STDOUT, env=env)


def estado(procs: dict) -> None:
    vivos = sum(1 for p, _, _ in procs.values() if p.poll() is None)
    log(f"nodos vivos: {vivos}/{len(procs)}")


def main() -> int:
    if PAUSA.exists():
        log(f"pausa activa ({PAUSA.name}); el supervisor no arranca")
        return 0

    log(f"supervisor iniciado (Ubuntu, {len(NODOS)} nodos) - python {PY}")
    procs: dict[str, tuple[subprocess.Popen, int, str]] = {}
    for nombre, script in NODOS:
        p = arrancar(nombre, script)
        procs[nombre] = (p, 1, datetime.now(tz=TZ_LOCAL).isoformat(timespec="seconds"))
        log(f"  arrancado {nombre} (pid {p.pid})")
        time.sleep(2)  # evita rafagas de DPS

    estado(procs)
    espera = {n: 10 for n, _ in NODOS}
    while True:
        time.sleep(15)
        if PAUSA.exists():
            log("pausa activa: deteniendo los nodos")
            for p, _, _ in procs.values():
                if p.poll() is None:
                    p.terminate()
            return 0
        for nombre, script in NODOS:
            p, arranques, _ = procs[nombre]
            if p.poll() is None:
                espera[nombre] = 10
            else:
                log(f"  {nombre} murio (codigo {p.returncode}); relanzando en {espera[nombre]} s")
                time.sleep(espera[nombre])
                espera[nombre] = min(60, espera[nombre] * 2)
                nuevo = arrancar(nombre, script)
                procs[nombre] = (nuevo, arranques + 1, datetime.now(tz=TZ_LOCAL).isoformat(timespec="seconds"))
                log(f"  {nombre} reiniciado (pid {nuevo.pid})")
        estado(procs)


if __name__ == "__main__":
    raise SystemExit(main())
