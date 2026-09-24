#!/usr/bin/env python3
"""
dc_acceso_sim.py - "sensor de campo" del acceso principal: publica por **HTTP** al puente
local (dc_http_bridge.py), que es quien habla con IoT Central.

Es la mitad de campo del origen "Puente HTTP/REST": el dispositivo de acceso no conoce
MQTT ni Azure; solo hace POST JSON a http://127.0.0.1:8098/telemetria cada 120 s.
"""
from __future__ import annotations

import json
import signal
import sys
import time
import urllib.error
import urllib.request

import dc_comun as C

PUERTO = 8098
URL = f"http://127.0.0.1:{PUERTO}/telemetria"
INTERVALO = 120
bit = C.Bitacora("DC-ACCESO-10-campo")
parar = {"v": False}
eventos = 0


def main():
    bit.info(f"sensor de campo iniciado; destino {URL}")
    def _salir(*_):
        parar["v"] = True
    signal.signal(signal.SIGINT, _salir)
    signal.signal(signal.SIGTERM, _salir)

    global eventos
    while not parar["v"]:
        datos = C.acceso(C.hora_actual(), eventos)
        eventos = datos["eventosAcceso"]
        try:
            req = urllib.request.Request(URL, data=json.dumps(datos).encode(),
                                         method="POST", headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=15) as r:
                bit.info(f"HTTP {r.status} puente acepto {datos}")
        except urllib.error.URLError as e:
            bit.error(f"puente no disponible ({e}); se reintenta")
        time.sleep(INTERVALO)
    return 0


if __name__ == "__main__":
    sys.exit(main())
