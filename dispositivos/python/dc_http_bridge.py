#!/usr/bin/env python3
"""
dc_http_bridge.py - **Puente HTTP/REST** del nodo DC-ACCESO-10 (puerta / control de acceso).

Arquitectura del origen:
  [sensor de campo] --HTTP POST localhost:8098/telemetria--> [puente] --MQTT/TLS 8883--> IoT Central

El puente escucha en 127.0.0.1:8098, valida el JSON del dispositivo de campo, lo reenvia a
IoT Central con el SDK y responde 202 Accepted. Los eventos que recibe quedan en
datos/DC-ACCESO-10.csv con la marca de tiempo de ingesta.

Origen de envio: "Puente HTTP/REST (sensor de campo -> Central)" | Intervalo: 120 s (lado campo)
"""
from __future__ import annotations

import json
import signal
import sys
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from azure.iot.device import IoTHubDeviceClient, Message, MethodResponse, ProvisioningDeviceClient

import dc_comun as C

DEVICE_ID = "DC-ACCESO-10"
ZONA = "Puerta / control de acceso"
UBIC = "Acceso principal - lector HID iCLASS SE R40"
ORIGEN = "Puente HTTP/REST (sensor de campo -> Central)"
FAB, MODELO, VERSION = "HID iCLASS SE R40 + controladora Mercury LP1502", "Puente-HTTP/1.0", "1.1.4"
INTERVALO = 120
PUERTO = 8098

bit = C.Bitacora(DEVICE_ID)
parar = {"v": False}
ctx = {"cliente": None, "ultimo": None, "recibidos": 0, "reenviados": 0, "puerta_hasta": 0.0}


class Manejador(BaseHTTPRequestHandler):
    def log_message(self, *a):  # silencio en stdout; el log lo lleva la bitacora
        pass

    def _responder(self, codigo: int, cuerpo: dict):
        datos = json.dumps(cuerpo).encode()
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(datos)))
        self.end_headers()
        self.wfile.write(datos)

    def do_GET(self):
        if self.path == "/salud":
            self._responder(200, {"puente": "ok", "recibidos": ctx["recibidos"],
                                  "reenviados": ctx["reenviados"], "device": DEVICE_ID})
        else:
            self._responder(404, {"error": "ruta no soportada"})

    def do_POST(self):
        if self.path != "/telemetria":
            self._responder(404, {"error": "ruta no soportada"})
            return
        n = int(self.headers.get("Content-Length", 0))
        try:
            datos = json.loads(self.rfile.read(n).decode() or "{}")
        except Exception:
            self._responder(400, {"error": "JSON invalido"})
            return
        ctx["recibidos"] += 1
        ctx["ultimo"] = datos
        datos["tsDispositivo"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        try:
            cliente = ctx["cliente"]
            if cliente is not None:
                cliente.send_message(Message(json.dumps(datos)))
                ctx["reenviados"] += 1
                bit.telemetria(datos, ORIGEN)
                self._responder(202, {"aceptado": True, "reenviado_a": "IoT Central"})
            else:
                self._responder(503, {"error": "puente sin conexion a Central"})
        except Exception as e:
            bit.error(f"fallo reenviando: {type(e).__name__}: {e}")
            self._responder(502, {"error": str(e)[:120]})


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
    if request.name == "abrirPuerta":
        segundos = int(payload.get("segundos", 5)) if isinstance(payload, dict) else 5
        ctx["puerta_hasta"] = time.time() + segundos
        resp = {"acceso": f"puerta abierta {segundos} s por comando remoto", "ts": ts}
    elif request.name == "acuseAlarma":
        alarma = payload.get("alarma", "?") if isinstance(payload, dict) else "?"
        resp = {"acuse": f"{alarma} acusada", "ts": ts}
    else:
        resp = {"resultado": f"{request.name} no soportado", "ts": ts}
    bit.info(f"CMD {request.name} -> {resp}")
    return MethodResponse.create_from_method_request(request, 200, resp)


def hilo_puerta():
    """Publica el estado de la puerta cada INTERVALO s, incluida la apertura remota."""
    while not parar["v"]:
        try:
            if C.en_pausa(DEVICE_ID):
                bit.info("PAUSA documentada")
                time.sleep(5)
                continue
            abierta_remota = time.time() < ctx["puerta_hasta"]
            hora = C.hora_actual()
            datos_base = C.acceso(hora, ctx["eventos"] if "eventos" in ctx else 0)
            ctx["eventos"] = datos_base["eventosAcceso"]
            if abierta_remota:
                datos_base["puertaAbierta"] = True
            datos_base["tsDispositivo"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
            cliente = ctx["cliente"]
            if cliente is not None:
                cliente.send_message(Message(json.dumps(datos_base)))
                bit.telemetria(datos_base, ORIGEN)
        except Exception as e:
            bit.error(f"hilo_puerta: {type(e).__name__}: {e}")
        time.sleep(INTERVALO)


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
    cliente.on_method_request_received = on_method
    cliente.connect()
    ctx["cliente"] = cliente
    props = C.propiedades(DEVICE_ID, ZONA, UBIC, ORIGEN, FAB, MODELO, VERSION, INTERVALO)
    cliente.patch_twin_reported_properties(props)
    bit.info(f"puente conectado y publicando el ciclo de la puerta cada {INTERVALO} s")

    def _salir(*_):
        parar["v"] = True
    signal.signal(signal.SIGINT, _salir)
    signal.signal(signal.SIGTERM, _salir)

    servidor = ThreadingHTTPServer(("127.0.0.1", PUERTO), Manejador)
    hilo = threading.Thread(target=servidor.serve_forever, daemon=True)
    hilo.start()
    bit.info(f"puente HTTP escuchando en http://127.0.0.1:{PUERTO}/telemetria (sensor de campo)")

    hilo_d = threading.Thread(target=hilo_puerta, daemon=True)
    hilo_d.start()

    while not parar["v"]:
        time.sleep(1)

    servidor.shutdown()
    cliente.shutdown()
    return 0


if __name__ == "__main__":
    sys.exit(main())
