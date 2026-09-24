#!/usr/bin/env python3
"""
dc_paho.py - Nodo DC-HUMO-08 (deteccion de humo / incendio) publicado con un
**cliente MQTT explícito (paho-mqtt), SIN el SDK azure-iot-device**.

El DPS se resuelve a mano por MQTT ($dps/registrations/...), el SAS se firma con
HMAC-SHA256 y la telemetria va al topic del hub `devices/<id>/messages/events/`.
Origen de envio: "Cliente MQTT explicito (paho, SAS manual)" | Intervalo: 45 s
"""
from __future__ import annotations

import json
import signal
import ssl
import sys
import threading
import time
from datetime import datetime, timezone

import paho.mqtt.client as mqtt

import dc_comun as C

DEVICE_ID = "DC-HUMO-08"
ZONA = "Deteccion de humo / incendio (techo sala blanca)"
UBIC = "Sala blanca - losa superior, cerca del VESDA"
ORIGEN = "Cliente MQTT explicito (paho, SAS manual)"
FAB, MODELO, VERSION = "Siemens FDA241 + ESP32-WROOM", "Nodo-Paho-MQTT/1.0", "1.1.0"
INTERVALO = 45
DPS_API = "2021-06-01"
HUB_API = "2019-10-01"   # el endpoint MQTT del hub rechaza api-version >= 2020

bit = C.Bitacora(DEVICE_ID)
parar = {"v": False}
ctx = {"hub": "", "operacion": None, "asignado": threading.Event()}


# ----------------------------- DPS por MQTT ------------------------------- #
def on_connect_dps(cli, userdata, flags, rc):
    bit.info(f"[DPS] CONNECT rc={rc}")
    if rc == 0:
        cli.subscribe("$dps/registrations/res/#", qos=1)
        carga = json.dumps({"registrationId": DEVICE_ID})
        cli.publish("$dps/registrations/PUT/iotdps-register/?$rid=1", carga, qos=1)


def on_message_dps(cli, userdata, msg):
    try:
        cuerpo = json.loads(msg.payload.decode())
    except Exception:
        bit.info(f"[DPS] mensaje no JSON en {msg.topic}")
        return
    status = cuerpo.get("status")
    bit.info(f"[DPS] {msg.topic} -> status={status} keys={list(cuerpo.keys())}")
    if status == "assigning":
        op = cuerpo.get("operationId")
        if op:
            ctx["operacion"] = op
            cli.publish(
                f"$dps/registrations/GET/iotdps-get-operationstatus/?$rid=2&operationId={op}", "", qos=1)
    elif status == "assigned":
        rs = cuerpo.get("registrationState", {})
        ctx["hub"] = (rs.get("assignedHub") or "").strip()
        C.guardar_hub(DEVICE_ID, ctx["hub"])
        bit.info(f"[DPS] assigned -> hub={ctx['hub']} deviceId={rs.get('deviceId')}")
        ctx["asignado"].set()
    elif status in ("failed", "disabled", "unassigned"):
        bit.error(f"[DPS] estado {status}: {cuerpo.get('errorCode')} {cuerpo.get('errorMessage')}")
        ctx["asignado"].set()


def _poll(cli):
    """Reintenta el sondeo de estado de la operacion DPS mientras no haya asignacion."""
    for _ in range(20):
        if ctx["asignado"].is_set() or parar["v"]:
            return
        if ctx["operacion"]:
            cli.publish(
                f"$dps/registrations/GET/iotdps-get-operationstatus/?$rid=9&operationId={ctx['operacion']}", "", qos=1)
        time.sleep(2)


def registrar_dps(id_scope: str, clave: str) -> str:
    recurso = f"{id_scope}/registrations/{DEVICE_ID}"
    sas = C.generar_sas(recurso, clave, ttl=3600, firmar_codificado=True)
    cli = mqtt.Client(client_id=DEVICE_ID, protocol=mqtt.MQTTv311)
    cli.username_pw_set(f"{id_scope}/registrations/{DEVICE_ID}/api-version={DPS_API}", sas)
    cli.tls_set(cert_reqs=ssl.CERT_REQUIRED)
    cli.on_connect = on_connect_dps
    cli.on_message = on_message_dps
    cli.connect(C.DPS_HOST, 8883, keepalive=30)
    cli.loop_start()
    hilo = threading.Thread(target=_poll, args=(cli,), daemon=True)
    hilo.start()
    ok = ctx["asignado"].wait(timeout=60)
    cli.loop_stop()
    cli.disconnect()
    if not ok or not ctx["hub"]:
        raise RuntimeError("DPS no asigno hub en 60 s")
    return ctx["hub"]


# ----------------------------- Hub MQTT ---------------------------------- #
def on_connect_hub(cli, userdata, flags, rc):
    bit.info(f"[HUB] CONNECT rc={rc} (0=OK, 4=timeout de red, 5=no autorizado)")
    if rc == 0:
        cli.publish(f"$iothub/twin/GET/?$rid=1", "", qos=1)
        props = C.propiedades(DEVICE_ID, ZONA, UBIC, ORIGEN, FAB, MODELO, VERSION, INTERVALO)
        cli.publish(f"$iothub/twin/PATCH/properties/reported/?$rid=2",
                    json.dumps(props), qos=1)
        bit.info(f"propiedades reportadas: {props}")


def on_message_hub(cli, userdata, msg):
    t = msg.topic
    if t.startswith("$iothub/twin/PATCH/properties/desired"):
        try:
            datos = json.loads(msg.payload.decode())
            bit.info(f"[HUB] twin desired: {datos}")
        except Exception:
            pass
    elif "$iothub/methods/POST/" in t:
        nombre = t.split("$iothub/methods/POST/")[1].split("/")[0]
        rid = 0
        for parte in t.split("?"):
            if parte.startswith("$rid="):
                rid = parte[4:]
        try:
            payload = json.loads(msg.payload.decode() or "{}")
        except Exception:
            payload = {}
        resp = {"resultado": f"{nombre} atendido por nodo paho", "ts": datetime.now(timezone.utc).isoformat(timespec="seconds")}
        if nombre == "setAlerta":
            resp = {"baliza": "encendida" if payload.get("enabled") else "apagada",
                    "ts": resp["ts"]}
        cli.publish(f"$iothub/methods/res/200/?$rid={rid}", json.dumps(resp), qos=1)
        bit.info(f"[HUB] comando {nombre} payload={payload} -> {resp}")


def main():
    creds = C.cargar_credenciales(DEVICE_ID)
    if not creds["primary_key"]:
        bit.error("sin credenciales (.secrets/env). Aborto.")
        return 1

    hub = C.hub_de_creds(DEVICE_ID) or registrar_dps(creds["id_scope"], creds["primary_key"])
    bit.info(f"hub listo: {hub}")

    def conectar() -> mqtt.Client:
        """Conecta (o reconecta) al hub con un SAS nuevo: paho no renueva el token solo."""
        recurso = f"{hub}/devices/{DEVICE_ID}"
        sas = C.generar_sas(recurso, creds["primary_key"], ttl=3600)
        username = f"{hub}/{DEVICE_ID}/?api-version={HUB_API}&DeviceClientType=paho-mqtt"
        cli = mqtt.Client(client_id=DEVICE_ID, protocol=mqtt.MQTTv311)
        cli.username_pw_set(username, sas)
        cli.tls_set(cert_reqs=ssl.CERT_REQUIRED)
        cli.tls_insecure_set(False)
        cli.on_connect = on_connect_hub
        cli.on_message = on_message_hub
        cli.connect(hub, 8883, keepalive=60)
        cli.loop_start()
        bit.info(f"MQTT explicito conectado a {hub}:8883 (QoS 1, SAS nuevo, topic "
                 f"devices/{DEVICE_ID}/messages/events/)")
        return cli

    cli = conectar()
    t_conexion = time.time()

    def _salir(*_):
        parar["v"] = True
    signal.signal(signal.SIGINT, _salir)
    signal.signal(signal.SIGTERM, _salir)

    topic = f"devices/{DEVICE_ID}/messages/events/"
    fallos = 0
    while not parar["v"]:
        if C.en_pausa(DEVICE_ID):
            bit.info("PAUSA documentada: sin telemetria")
            time.sleep(5)
            continue
        # el SAS del hub dura 1 h: se renueva a los 45 min o si el cliente se cayo
        if time.time() - t_conexion > 2700 or not cli.is_connected():
            bit.info("renovando SAS / reconectando al hub")
            try:
                cli.loop_stop()
                cli.disconnect()
            except Exception:
                pass
            try:
                cli = conectar()
                t_conexion = time.time()
                fallos = 0
            except Exception as e:
                bit.error(f"reconexion fallida: {type(e).__name__}: {e}")
                time.sleep(10)
                continue
        datos = C.humo(C.hora_actual())
        datos["tsDispositivo"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        carga = json.dumps(datos)
        info = cli.publish(topic, carga, qos=1)
        bit.telemetria(datos, ORIGEN)
        if info.rc != 0:
            fallos += 1
            bit.error(f"publish rc={info.rc} (fallo {fallos})")
            if fallos >= 3:
                bit.info("tres fallos de publicacion: se fuerza la reconexion")
                t_conexion = 0
        else:
            fallos = 0
        time.sleep(INTERVALO)

    cli.loop_stop()
    cli.disconnect()
    return 0


if __name__ == "__main__":
    sys.exit(main())
