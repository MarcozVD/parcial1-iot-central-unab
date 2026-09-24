#!/usr/bin/env python3
"""Estado de la flota DC-ANDES-1 consultado a la API de datos de IoT Central.

Uso:
    python tools/estado_flota_api.py            # tabla resumen
    python tools/estado_flota_api.py --json     # salida json
"""
from __future__ import annotations

import json
import pathlib
import shutil
import subprocess
import sys
import urllib.request

RAIZ = pathlib.Path(__file__).resolve().parents[1]
APP = "dcandes1unab"
AUTH = pathlib.Path.home() / ".azure" / "accessTokens.json"
LOTE = RAIZ / "datos" / "estado_flota.json"


def token() -> str:
    exe = shutil.which("az") or r"C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd"
    cmd = [
        exe, "account", "get-access-token",
        "--resource", "https://apps.azureiotcentral.com",
        "--query", "accessToken", "-o", "tsv",
    ]
    usar_shell = exe.lower().endswith((".cmd", ".bat"))
    r = subprocess.run(" ".join(f'"{c}"' for c in cmd) if usar_shell else cmd,
                       capture_output=True, text=True, shell=usar_shell)
    if r.returncode != 0:
        raise SystemExit("No se pudo obtener token: " + (r.stderr or "")[:300])
    return r.stdout.strip()


def api(tk: str, ruta: str) -> dict:
    url = f"https://{APP}.azureiotcentral.com/api/{ruta}"
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + tk})
    with urllib.request.urlopen(req, timeout=40) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main() -> int:
    tk = token()
    datos = api(tk, "devices?api-version=2022-06-30-preview")
    filas = []
    for d in datos.get("value", []):
        did = d.get("id")
        # el listado no trae connectionState: se consulta el detalle
        det = {}
        try:
            det = api(tk, f"devices/{did}?api-version=2022-06-30-preview")
        except Exception as exc:  # noqa: BLE001
            det = {"error": str(exc)[:80]}
        filas.append({
            "id": did,
            "nombre": d.get("displayName"),
            "plantilla": d.get("template"),
            "estado": "provisioned" if d.get("provisioned") else "registered",
            "conexion": det.get("connectionState", "?"),
            "simulado": d.get("simulated", False),
        })
    filas.sort(key=lambda f: f["id"] or "")
    conectados = sum(1 for f in filas if f["conexion"] == "connected")
    resumen = {
        "app": APP,
        "dispositivos": len(filas),
        "conectados": conectados,
        "filas": filas,
    }
    LOTE.parent.mkdir(parents=True, exist_ok=True)
    LOTE.write_text(json.dumps(resumen, indent=2, ensure_ascii=False), encoding="utf-8")
    if "--json" in sys.argv:
        print(json.dumps(resumen, indent=2, ensure_ascii=False))
    else:
        print(f"{'id':<16}{'estado':<12}{'conexion':<12}{'simulado':<9}nombre")
        for f in filas:
            print(f"{f['id']:<16}{f['estado']:<12}{f['conexion']:<12}{str(f['simulado']):<9}{f['nombre']}")
        print(f"\ntotal: {len(filas)} dispositivos, conectados: {conectados}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
