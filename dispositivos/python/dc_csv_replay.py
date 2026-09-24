#!/usr/bin/env python3
"""
dc_csv_replay.py - Nodo DC-ENERGIA-09 (PDU / energia de fila) alimentado por
**replay de un CSV historico** (datos/historico_pdu_fila.csv), sin sensor fisico.

Origen de envio: "Replay de CSV historico (PDU fila C)" | Intervalo: 120 s
El CSV se genero con tools/generar_csv_pdu.py a partir del modelo de carga documentado
en docs/datasheets.md (perfil de un dia tipico, 120 s de resolucion).
"""
from __future__ import annotations

import csv
import json
import signal
import sys
import time
from datetime import datetime, timezone

from azure.iot.device import IoTHubDeviceClient, Message, ProvisioningDeviceClient

import dc_comun as C

DEVICE_ID = "DC-ENERGIA-09"
ZONA = "PDU / energia de fila"
UBIC = "Sala blanca - tablero de fila C (PDU monofasica 32 A)"
ORIGEN = "Replay de CSV historico (PDU fila C)"
FAB, MODELO, VERSION = "Raritan PX3-5488 + shunt 100 A", "Replay-CSV/1.0", "1.0.3"
INTERVALO = 120
CSV_HIST = C.DATOS / "historico_pdu_fila.csv"

bit = C.Bitacora(DEVICE_ID)
parar = {"v": False}


def leer_historico() -> list[dict]:
    with CSV_HIST.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def main():
    creds = C.cargar_credenciales(DEVICE_ID)
    if not creds["primary_key"]:
        bit.error("sin credenciales (.secrets/env). Aborto.")
        return 1
    if not CSV_HIST.exists():
        bit.error(f"falta {CSV_HIST}; genere el historico con tools/generar_csv_pdu.py")
        return 1

    filas = leer_historico()
    bit.info(f"historico cargado: {len(filas)} muestras de {CSV_HIST.name}")

    prov = ProvisioningDeviceClient.create_from_symmetric_key(
        provisioning_host=C.DPS_HOST, registration_id=DEVICE_ID,
        id_scope=creds["id_scope"], symmetric_key=creds["primary_key"])
    res = prov.register()
    hub = (getattr(res.registration_state, "assigned_hub", "") or "").replace("https://", "").strip("/")
    C.guardar_hub(DEVICE_ID, hub)
    bit.info(f"DPS OK -> hub {hub}")

    cliente = IoTHubDeviceClient.create_from_symmetric_key(
        symmetric_key=creds["primary_key"], hostname=hub, device_id=DEVICE_ID, keep_alive=60)
    cliente.connect()
    props = C.propiedades(DEVICE_ID, ZONA, UBIC, ORIGEN, FAB, MODELO, VERSION, INTERVALO)
    cliente.patch_twin_reported_properties(props)
    bit.info(f"replay conectado; propiedades: {props}")

    def _salir(*_):
        parar["v"] = True
    signal.signal(signal.SIGINT, _salir)
    signal.signal(signal.SIGTERM, _salir)

    i = 0
    while not parar["v"]:
        if C.en_pausa(DEVICE_ID):
            bit.info("PAUSA documentada")
            time.sleep(5)
            continue
        fila = filas[i % len(filas)]
        vuelta = i // len(filas) + 1
        i += 1
        datos = {
            "tsFuente": f"{fila['ts_origen']} (historico PDU, vuelta {vuelta})",
            "potenciaKw": float(fila["potenciaKw"]),
            "corrienteA": float(fila["corrienteA"]),
            "factorPotencia": float(fila["factorPotencia"]),
            "tsDispositivo": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }
        cliente.send_message(Message(json.dumps(datos)))
        bit.telemetria(datos, ORIGEN)
        time.sleep(INTERVALO)

    cliente.shutdown()
    return 0


if __name__ == "__main__":
    sys.exit(main())
