#!/usr/bin/env python3
"""
dc_sdk_ws.py - Nodo DC-PASILLO-04 (pasillo frio / contencion) alimentado por el SDK
azure-iot-device con **MQTT sobre WebSockets (TLS 443)** - transporte distinto al del
nodo DC-RACKC-03 (MQTT/TLS 8883). Aprovisionamiento DPS con clave simetrica.

Origen de envio: "Python SDK azure-iot-device (MQTT sobre WebSockets 443)" | Intervalo: 60 s

Nota tecnica: azure-iot-device 2.x soporta MQTT y MQTT/WebSockets; AMQP fue retirado del
SDK de dispositivo (solo queda en el SDK de servicio), por eso el segundo camino Python
se distingue por el transporte WebSocket (443), que ademas atraviesa proxies corporativos.
"""
from __future__ import annotations

import json
import signal
import sys
import time
from datetime import datetime, timezone

from azure.iot.device import IoTHubDeviceClient, Message, MethodResponse, ProvisioningDeviceClient

import dc_comun as C

DEVICE_ID = "DC-PASILLO-04"
ZONA = "Pasillo frio / contencion"
UBIC = "Sala blanca - pasillo entre filas A y C"
ORIGEN = "Python SDK azure-iot-device (MQTT sobre WebSockets 443)"
FAB, MODELO, VERSION = "Dell Edge Gateway 3200 + Sensirion SDP810", "Nodo-Py-WS/1.0", "1.2.0"
INTERVALO = 60
TRANSPORTE = "mqtt"
WEBSOCKETS = True

bit = C.Bitacora(DEVICE_ID)
parar = {"v": False}
estado = {"umbralHumedad": 60.0, "modo": "Normal"}


def on_method(request):
    payload = request.payload
    if isinstance(payload, (bytes, bytearray)):
        payload = payload.decode(errors="ignore")
    if isinstance(payload, str):
        try:
            payload = json.loads(payload)
        except Exception:
            pass
    ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
    nombre = request.name
    if nombre == "reiniciar":
        resp = {"resultado": "reinicio simulado aceptado (nodo pasillo)", "ts": ts}
    elif nombre == "acuseAlarma":
        alarma = payload.get("alarma", "?") if isinstance(payload, dict) else "?"
        resp = {"acuse": f"{alarma} acusada", "ts": ts}
    elif nombre == "setAlerta":
        on = payload.get("enabled", False) if isinstance(payload, dict) else bool(payload)
        resp = {"baliza": "encendida" if on else "apagada", "ts": ts}
    else:
        resp = {"resultado": f"{nombre} no soportado", "ts": ts}
    bit.info(f"CMD {nombre} -> {resp}")
    return MethodResponse.create_from_method_request(request, 200, resp)


def on_desired(patch):
    bit.info(f"TWIN desired: {patch}")
    if "umbralHumedad" in patch:
        estado["umbralHumedad"] = float(patch["umbralHumedad"])
    if "modoOperacion" in patch:
        estado["modo"] = str(patch["modoOperacion"])
    return True


def main():
    creds = C.cargar_credenciales(DEVICE_ID)
    if not creds["primary_key"]:
        bit.error("sin credenciales (.secrets/env). Aborto.")
        return 1
    bit.info(f"DPS (MQTT) id_scope={creds['id_scope']} registration_id={DEVICE_ID} "
             f"| hub por MQTT/WebSockets={WEBSOCKETS}")

    prov = ProvisioningDeviceClient.create_from_symmetric_key(
        provisioning_host=C.DPS_HOST, registration_id=DEVICE_ID,
        id_scope=creds["id_scope"], symmetric_key=creds["primary_key"])
    t0 = time.time()
    resultado = prov.register()
    rs = resultado.registration_state
    hub = (getattr(rs, "assigned_hub", "") or "").replace("https://", "").strip("/")
    C.guardar_hub(DEVICE_ID, hub)
    bit.info(f"DPS OK en {time.time()-t0:.1f} s -> hub {hub} | estado={getattr(resultado, 'status', '?')} | {rs}")

    cliente = IoTHubDeviceClient.create_from_symmetric_key(
        symmetric_key=creds["primary_key"], hostname=hub, device_id=DEVICE_ID,
        websockets=WEBSOCKETS, keep_alive=60)
    cliente.on_method_request_received = on_method
    cliente.on_twin_desired_properties_patch_received = on_desired
    cliente.connect()
    bit.info("MQTT sobre WebSockets (443) conectado a IoT Central")

    props = C.propiedades(DEVICE_ID, ZONA, UBIC, ORIGEN, FAB, MODELO, VERSION, INTERVALO)
    cliente.patch_twin_reported_properties(props)
    bit.info(f"propiedades reportadas: {props}")

    def _salir(*_):
        parar["v"] = True
    signal.signal(signal.SIGINT, _salir)
    signal.signal(signal.SIGTERM, _salir)

    while not parar["v"]:
        if C.en_pausa(DEVICE_ID):
            bit.info("PAUSA documentada: sin telemetria")
            time.sleep(5)
            continue
        datos = C.pasillo(C.hora_actual())
        datos["tsDispositivo"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        cliente.send_message(Message(json.dumps(datos)))
        bit.telemetria(datos, ORIGEN)
        time.sleep(INTERVALO)

    bit.info("cerrando cliente...")
    cliente.shutdown()
    return 0


if __name__ == "__main__":
    sys.exit(main())
