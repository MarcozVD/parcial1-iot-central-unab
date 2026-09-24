#!/usr/bin/env python3
"""
resolver_hub.py - resuelve y cachea (datos/hub_<device>.txt) el IoT Hub asignado por DPS
a cada dispositivo de la flota, para los nodos que NO usan el SDK (HTTPS/REST, CSV, etc.).

Uso:  python tools/resolver_hub.py [DEVICE_ID ...]     (sin argumentos = toda la flota)
"""
from __future__ import annotations

import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "dispositivos" / "python"))

import dc_comun as C  # noqa: E402
from azure.iot.device import ProvisioningDeviceClient  # noqa: E402

FLOTA = ["DC-RACKB-02", "DC-RACKC-03", "DC-PASILLO-04", "DC-CLIMA-05", "DC-AIRE-06",
         "DC-AGUA-07", "DC-HUMO-08", "DC-ENERGIA-09", "DC-ACCESO-10"]


def resolver(device_id: str) -> str:
    creds = C.cargar_credenciales(device_id)
    if not creds["primary_key"]:
        raise RuntimeError(f"{device_id}: sin credenciales")
    prov = ProvisioningDeviceClient.create_from_symmetric_key(
        provisioning_host=C.DPS_HOST, registration_id=device_id,
        id_scope=creds["id_scope"], symmetric_key=creds["primary_key"])
    res = prov.register()
    hub = (getattr(res.registration_state, "assigned_hub", "") or "").replace("https://", "").strip("/")
    C.guardar_hub(device_id, hub)
    return hub


def main():
    ids = sys.argv[1:] or FLOTA
    for d in ids:
        try:
            hub = resolver(d)
            print(f"{d:16s} -> {hub}")
        except Exception as e:
            print(f"{d:16s} -> ERROR {type(e).__name__}: {e}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
