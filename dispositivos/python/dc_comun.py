#!/usr/bin/env python3
"""
dc_comun.py - utilidades comunes de la flota DC-ANDES-1 (Parcial 1, UNAB).

- Lectura de credenciales desde .secrets/env/<device>.env  (nunca en el repo)
- Registro de telemetria en CSV local (datos/<device>.csv) para el analisis de los 4 dias
- Modelos de datos por zona (con patron diurno documentado en docs/datasheets.md)
- Ventana de pausa programada (desconexion documentada)
"""
from __future__ import annotations

import base64
import csv
import hashlib
import hmac
import json
import math
import os
import pathlib
import random
import time
from datetime import datetime, timedelta, timezone

RAIZ = pathlib.Path(__file__).resolve().parents[2]
SECRETS = RAIZ / ".secrets" / "env"
DATOS = RAIZ / "datos"
LOGS = RAIZ / "logs"
for _d in (DATOS, LOGS):
    _d.mkdir(parents=True, exist_ok=True)

TZ_LOCAL = timezone(timedelta(hours=-5))  # America/Bogota (UTC-05, sin DST)
DPS_HOST = "global.azure-devices-provisioning.net"

# --------------------------------------------------------------------------- #
# credenciales
# --------------------------------------------------------------------------- #


def cargar_credenciales(device_id: str) -> dict:
    """Lee ID_SCOPE / PRIMARY_KEY del entorno o de .secrets/env/<device_id>.env."""
    env = os.environ
    if not env.get("PRIMARY_KEY"):
        f = SECRETS / f"{device_id}.env"
        if f.exists():
            for linea in f.read_text(encoding="utf-8").splitlines():
                linea = linea.strip()
                if linea.startswith("export "):
                    k, _, v = linea[7:].partition("=")
                    env[k.strip()] = v.strip().strip('"')
    return {
        "id_scope": env.get("ID_SCOPE", ""),
        "device_id": env.get("DEVICE_ID", device_id),
        "primary_key": env.get("PRIMARY_KEY", ""),
    }


def hub_de_creds(device_id: str) -> str:
    """Hostname del IoT Hub (se resuelve en el primer registro DPS y se cachea)."""
    f = DATOS / f"hub_{device_id}.txt"
    if f.exists():
        return f.read_text(encoding="utf-8").strip()
    return ""


def guardar_hub(device_id: str, hub: str) -> None:
    (DATOS / f"hub_{device_id}.txt").write_text(hub, encoding="utf-8")


def generar_sas(recurso: str, clave_b64: str, ttl: int = 3600, firmar_codificado: bool = True) -> str:
    """SAS = HMAC-SHA256(clave, <recurso>\\n expiración) en base64 URL-safe.

    El token siempre lleva el recurso percent-encoded una sola vez (patrón del SDK).
    `firmar_codificado` elige QUE cadena se firma:
      - True  (por defecto, igual que azure-iot-device sastoken.py): se firma el
        recurso YA codificado -> es lo que aceptan Hub y DPS.
      - False: se firma el recurso en claro (compatibilidad con clientes que firman
        el URI crudo, p.ej. algunos ejemplos de paho).
    """
    from urllib.parse import quote
    se = int(time.time()) + ttl
    sr_codificado = quote(recurso, safe="")
    mensaje = (sr_codificado if firmar_codificado else recurso) + "\n" + str(se)
    firma = base64.b64encode(
        hmac.new(base64.b64decode(clave_b64), mensaje.encode(), hashlib.sha256).digest()
    )
    return f"SharedAccessSignature sr={sr_codificado}&sig={quote(firma.decode(), safe='')}&se={se}"


# --------------------------------------------------------------------------- #
# registro local de telemetria
# --------------------------------------------------------------------------- #


class Bitacora:
    """Escribe cada lote de telemetria en datos/<device>.csv y logs/<device>.log."""

    def __init__(self, device_id: str):
        self.device_id = device_id
        self.csv_path = DATOS / f"{device_id}.csv"
        self.log_path = LOGS / f"{device_id}.log"

    def _log(self, texto: str) -> None:
        linea = f"[{datetime.now(TZ_LOCAL).strftime('%Y-%m-%d %H:%M:%S')}] {texto}"
        with self.log_path.open("a", encoding="utf-8") as fh:
            fh.write(linea + "\n")
        print(linea, flush=True)

    def info(self, texto: str) -> None:
        self._log("INFO  " + texto)

    def error(self, texto: str) -> None:
        self._log("ERROR " + texto)

    def telemetria(self, datos: dict, origen: str) -> None:
        ts_local = datetime.now(TZ_LOCAL).isoformat(timespec="seconds")
        ts_utc = datetime.now(timezone.utc).isoformat(timespec="seconds")
        fila = {"ts_local": ts_local, "ts_utc": ts_utc, "origen": origen, "device_id": self.device_id}
        fila.update({k: v for k, v in datos.items()})
        nuevo = not self.csv_path.exists() or self.csv_path.stat().st_size <= len(
            "ts_local,ts_utc,origen,device_id\n")
        with self.csv_path.open("a", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(fila.keys()))
            if nuevo:
                w.writeheader()
            w.writerow(fila)
        self._log(f"TX {origen} -> {json.dumps(datos, ensure_ascii=False)}")


# --------------------------------------------------------------------------- #
# ventana de pausa (desconexion documentada)
# --------------------------------------------------------------------------- #


def en_pausa(device_id: str, ahora: datetime | None = None) -> bool:
    """Si existe datos/pausa_<device>.json con {"desde": iso, "hasta": iso}, la respeta."""
    f = DATOS / f"pausa_{device_id}.json"
    if not f.exists():
        return False
    try:
        v = json.loads(f.read_text(encoding="utf-8"))
        ahora = ahora or datetime.now(TZ_LOCAL)
        desde = datetime.fromisoformat(v["desde"])
        hasta = datetime.fromisoformat(v["hasta"])
        return desde <= ahora <= hasta
    except Exception:
        return False


# --------------------------------------------------------------------------- #
# modelos de datos por zona (el "que se mide"; ver docs/datasheets.md)
# --------------------------------------------------------------------------- #


def _ruido(amplitud: float) -> float:
    return random.uniform(-amplitud, amplitud)


def _diurno(hora: float, pico: float = 15.0, amplitud: float = 1.0) -> float:
    """Curva diurna suave: maximo cerca de `pico` (hora local), minimo 12 h antes."""
    return amplitud * math.cos((hora - pico) * math.pi / 12.0)


def carga_it(hora: float) -> float:
    """Perfil de carga IT 0..1 del centro de datos (valle 03:00, pico 15:00)."""
    return round(0.42 + 0.30 * (1 + math.cos((hora - 15.0) * math.pi / 12.0)) / 2 + _ruido(0.02), 3)


def rack(zona: str, hora: float) -> dict:
    carga = carga_it(hora)
    intake = 21.0 + 1.5 * carga + _ruido(0.35)
    exhaust = intake + 8.0 + 4.5 * carga + _ruido(0.6)
    hr = 47.0 + 6.0 * math.sin((hora - 4.0) * math.pi / 12.0) + _ruido(1.2)
    return {
        "tempIntake": round(intake, 2),
        "tempExhaust": round(exhaust, 2),
        "humedadRack": round(min(62.0, max(38.0, hr)), 2),
    }


def pasillo(hora: float) -> dict:
    carga = carga_it(hora)
    return {
        "tempPasillo": round(19.4 + 1.2 * carga + _ruido(0.3), 2),
        "humedadPasillo": round(min(58.0, max(40.0, 50.0 + 4.0 * math.sin((hora - 5.0) * math.pi / 12.0) + _ruido(1.0))), 2),
        "deltaPresionPa": round(max(3.0, 14.0 + 8.0 * carga + _ruido(2.5)), 1),
    }


def agua(hora: float, indice: int) -> dict:
    """Prueba funcional de fuga programada: 2 muestras alrededor de las 15:00."""
    prueba = (15 <= hora < 15.05) and (indice % 3 == 0)
    return {
        "fugaAgua": bool(prueba),
        "humedadPiso": round(min(99.0, max(30.0, 36.0 + 2.0 * math.sin(hora * math.pi / 12.0) + (45.0 if prueba else 0.0) + _ruido(1.5))), 1),
    }


def humo(hora: float) -> dict:
    """Prueba funcional de humo programada a las 10:00 (indice %obs/m)."""
    prueba = 10 <= hora < 10.05
    base = 0.021 + 0.004 * math.sin(hora * math.pi / 12.0) + abs(_ruido(0.004))
    return {
        "humo": round(0.09 + _ruido(0.02) if prueba else base, 3),
        "tempTecho": round(24.5 + 2.5 * math.cos((hora - 15.0) * math.pi / 12.0) + _ruido(0.4), 2),
    }


def energia(hora: float) -> dict:
    carga = carga_it(hora)
    kw = 4.1 + 3.4 * carga + _ruido(0.25)
    pf = min(0.995, max(0.90, 0.965 + _ruido(0.012)))
    corriente = kw * 1000.0 / (230.0 * pf)   # PDU monofasica 230 V (32 A)
    return {
        "potenciaKw": round(kw, 2),
        "corrienteA": round(corriente, 2),
        "factorPotencia": round(pf, 3),
    }


def acceso(hora: float, eventos: int) -> dict:
    abierta = (7.5 <= hora <= 18.5) and (random.random() < 0.12)
    if abierta:
        eventos += 1
    return {
        "puertaAbierta": bool(abierta),
        "eventosAcceso": eventos,
        "tempPuerta": round(22.4 + 1.6 * math.cos((hora - 15.0) * math.pi / 12.0) + _ruido(0.4), 2),
    }


def propiedades(device_id: str, zona: str, ubicacion: str, origen: str, fabricante: str,
                modelo: str, version: str, intervalo: int) -> dict:
    return {
        "zona": zona, "ubicacion": ubicacion, "origenEnvio": origen, "fabricante": fabricante,
        "modelo": modelo, "versionFirmware": version, "intervaloMuestreo": intervalo,
    }


def hora_actual() -> float:
    n = datetime.now(TZ_LOCAL)
    return n.hour + n.minute / 60.0 + n.second / 3600.0
