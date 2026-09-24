#!/usr/bin/env python3
"""
dc_sdk_mqtt.py - Nodo DC-RACKC-03 (Rack C) alimentado por el SDK azure-iot-device
sobre **MQTT (TLS 8883)** con aprovisionamiento DPS (clave simetrica).

Origen de envio: "Python SDK azure-iot-device (MQTT)"  |  Intervalo: 30 s
Destino: Azure IoT Central -> app dcandes1unab  (NO un broker local)

Ejecutar:  python dc_sdk_mqtt.py        (credenciales en .secrets/env/DC-RACKC-03.env)
"""
from __future__ import annotations

import json
import signal
import sys
import time
from datetime import datetime, timezone

from azure.iot.device import IoTHubDeviceClient, Message, MethodResponse, ProvisioningDeviceClient

import dc_comun as C

DEVICE_ID = "DC-RACKC-03"
ZONA = "Rack C"
UBIC = "Sala blanca - fila C (DC-ANDES-1)"
ORIGEN = "Python SDK azure-iot-device (MQTT 8883)"
FAB, MODELO, VERSION = "Raspberry Pi 4B + Sensorica SHT31", "Nodo-Py-MQTT/1.0", "1.4.0"
INTERVALO = 30
TRANSPORTE = "mqtt"

bit = C.Bitacora(DEVICE_ID)
parar = {"v": False}
estado = {"baliza": "apagada", "umbral": 27.0, "modo": "Normal"}


def on_method(request):
    """Comandos desde IoT Central: setAlerta, reiniciar, acuseAlarma."""
    nombre = request.name
    payload = request.payload
    if isinstance(payload, (bytes, bytearray)):
        payload = payload.decode(errors="ignore")
    if isinstance(payload, str):
        try:
            payload = json.loads(payload)
        except Exception:
            pass
    ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
    if nombre == "setAlerta":
        on = payload.get("enabled", payload) if isinstance(payload, dict) else bool(payload)
        estado["baliza"] = "encendida" if on else "apagada"
        resp = {"baliza": estado["baliza"], "ts": ts}
    elif nombre == "reiniciar":
        resp = {"resultado": "reinicio simulado aceptado", "ts": ts}
    elif nombre == "acuseAlarma":
        alarma = payload.get("alarma", "?") if isinstance(payload, dict) else "?"
        resp = {"acuse": f"{alarma} acusada por operador", "ts": ts}
    elif nombre == "abrirPuerta":
        resp = {"acceso": "no aplica a este nodo", "ts": ts}
    else:
        resp = {"resultado": f"comando {nombre} no soportado", "ts": ts}
    bit.info(f"CMD {nombre} payload={payload} -> {resp}")
    return MethodResponse.create_from_method_request(request, 200, resp)


def on_desired(patch):
    """Propiedades escribibles (nube -> dispositivo)."""
    bit.info(f"TWIN desired: {patch}")
    if "umbralTemperatura" in patch:
        estado["umbral"] = float(patch["umbralTemperatura"])
    if "modoOperacion" in patch:
        estado["modo"] = str(patch["modoOperacion"])
    return True


def main():
    creds = C.cargar_credenciales(DEVICE_ID)
    if not creds["primary_key"]:
        bit.error("sin credenciales (.secrets/env). Aborto.")
        return 1
    bit.info(f"DPS: id_scope={creds['id_scope']} registration_id={DEVICE_ID} transporte={TRANSPORTE}")

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
        keep_alive=60)
    cliente.on_method_request_received = on_method
    cliente.on_twin_desired_properties_patch_received = on_desired
    cliente.connect()
    bit.info("MQTT/TLS conectado a IoT Central")

    props = C.propiedades(DEVICE_ID, ZONA, UBIC, ORIGEN, FAB, MODELO, VERSION, INTERVALO)
    cliente.patch_twin_reported_properties(props)
    bit.info(f"propiedades reportadas: {props}")

    def _salir(*_):
        parar["v"] = True
    signal.signal(signal.SIGINT, _salir)
    signal.signal(signal.SIGTERM, _salir)

    n = 0
    while not parar["v"]:
        if C.en_pausa(DEVICE_ID):
            bit.info("PAUSA documentada: no se publica telemetria (ventana de mantenimiento)")
            time.sleep(5)
            continue
        n += 1
        datos = C.rack(ZONA, C.hora_actual())
        datos["tsDispositivo"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        msg = Message(json.dumps(datos))
        msg.content_encoding = "utf-8"
        msg.content_type = "application/json"
        cliente.send_message(msg)
        # valor de baliza en el log local (no es telemetria de la plantilla)
        if estado["baliza"] == "encendida":
            bit.info(f"baliza encendida; umbral={estado['umbral']}")
        bit.telemetria(datos, ORIGEN)
        time.sleep(INTERVALO)

    bit.info("cerrando cliente...")
    cliente.shutdown()
    return 0


if __name__ == "__main__":
    sys.exit(main())
