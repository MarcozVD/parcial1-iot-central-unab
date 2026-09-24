#!/usr/bin/env python3
"""
dc_api_openmeteo.py - Nodo DC-CLIMA-05: **puente de API publica meteorologica**.
Consulta Open-Meteo (feed meteorologico abierto, equivalente a Atlas Weather) para la
ubicacion urbana del DC-ANDES-1 (7.1193, -73.1227, Bucaramanga) y reenvia las variables
de free-cooling a IoT Central con el SDK (MQTT/TLS 8883).

Origen de envio: "API publica Open-Meteo (puente HTTP -> IoT Central)" | Intervalo: 900 s
Se publican las marcas de tiempo de la FUENTE (tsFuente) y de INGESTION (tsDispositivo).
"""
from __future__ import annotations

import json
import signal
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone

from azure.iot.device import IoTHubDeviceClient, Message, ProvisioningDeviceClient

import dc_comun as C

DEVICE_ID = "DC-CLIMA-05"
ZONA = "Clima exterior (free-cooling)"
UBIC = "Cubierta tecnica - estacion meteorologica del predio"
ORIGEN = "API publica Open-Meteo (puente HTTP -> IoT Central)"
FAB, MODELO, VERSION = "Davis Vantage Pro2 (referencia) / feed Open-Meteo", "Puente-API-Meteo/1.0", "1.3.0"
INTERVALO = 900
LAT, LON = 7.1193, -73.1227
URL = ("https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
       "&current=temperature_2m,relative_humidity_2m,precipitation,rain,wind_speed_10m,"
       "shortwave_radiation&timezone=America%2FBogota")

bit = C.Bitacora(DEVICE_ID)
parar = {"v": False}


def consultar_fuente() -> dict:
    """Devuelve las variables del escenario a partir del feed publico."""
    with urllib.request.urlopen(URL.format(lat=LAT, lon=LON), timeout=25) as r:
        j = json.load(r)
    cur = j["current"]
    return {
        "tsFuente": cur["time"] + " (America/Bogota, Open-Meteo)",
        "tempExterior": float(cur["temperature_2m"]),
        "humedadExterior": float(cur["relative_humidity_2m"]),
        "lluviaMm": float(cur["precipitation"]),
        "vientoKmh": float(cur["wind_speed_10m"]),
        "radiacionSolar": float(cur["shortwave_radiation"]),
    }


def main():
    creds = C.cargar_credenciales(DEVICE_ID)
    if not creds["primary_key"]:
        bit.error("sin credenciales (.secrets/env). Aborto.")
        return 1

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
    bit.info(f"puente conectado; propiedades: {props}")

    def _salir(*_):
        parar["v"] = True
    signal.signal(signal.SIGINT, _salir)
    signal.signal(signal.SIGTERM, _salir)

    while not parar["v"]:
        if C.en_pausa(DEVICE_ID):
            bit.info("PAUSA documentada")
            time.sleep(5)
            continue
        try:
            datos = consultar_fuente()
            datos["tsDispositivo"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
            cliente.send_message(Message(json.dumps(datos)))
            bit.telemetria(datos, ORIGEN)
        except Exception as e:  # red o cuota de la API publica
            bit.error(f"fallo consultando la API publica: {type(e).__name__}: {e}")
        time.sleep(INTERVALO)

    cliente.shutdown()
    return 0


if __name__ == "__main__":
    sys.exit(main())
