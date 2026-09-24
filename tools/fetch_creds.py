#!/usr/bin/env python3
"""Obtiene ID Scope + claves de los 10 dispositivos y las guarda en .secrets/.

No imprime claves. Genera:
  .secrets/creds.json          -> {device_id: {idScope, primaryKey, secondaryKey}}
  .secrets/env/<device>.env    -> export ID_SCOPE/DEVICE_ID/PRIMARY_KEY
"""
import json
import os
import pathlib
import subprocess

ROOT = pathlib.Path(r"C:\Users\mvale\Documents\Parcial1_IoT_Central")
SEC = ROOT / ".secrets"
APP = "dcandes1unab"
DEVS = ["DC-RACKA-01", "DC-RACKB-02", "DC-RACKC-03", "DC-PASILLO-04", "DC-CLIMA-05",
        "DC-AIRE-06", "DC-AGUA-07", "DC-HUMO-08", "DC-ENERGIA-09", "DC-ACCESO-10"]
AZ = r'"C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd"'


AZ_DIR = r"C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin"
ENV = dict(os.environ, PATH=AZ_DIR + ";" + os.environ.get("PATH", ""))


def run_az(args: str) -> str:
    p = subprocess.run("az " + args, capture_output=True, text=True, shell=True,
                       timeout=180, env=ENV)
    out = (p.stdout or "") + (p.stderr or "")
    if p.returncode != 0:
        raise RuntimeError(f"az fallo: {out[:300]}")
    return out


def main():
    (SEC / "env").mkdir(parents=True, exist_ok=True)
    creds = {}
    for d in DEVS:
        try:
            txt = run_az(f"iot central device show-credentials --app-id {APP} -d {d} -o json")
        except RuntimeError as e:
            print(f"  -- {d}: sin credenciales (dispositivo simulado nativo)")
            continue
        i = txt.find("{")
        j = txt.rfind("}")
        data = json.loads(txt[i:j + 1])
        creds[d] = {
            "idScope": data["idScope"],
            "primaryKey": data["symmetricKey"]["primaryKey"],
            "secondaryKey": data["symmetricKey"]["secondaryKey"],
        }
        env = SEC / "env" / f"{d}.env"
        env.write_text(
            f'export ID_SCOPE="{creds[d]["idScope"]}"\n'
            f'export DEVICE_ID="{d}"\n'
            f'export PRIMARY_KEY="{creds[d]["primaryKey"]}"\n',
            encoding="utf-8", newline="\n")
        print(f"  ok {d} (idScope {creds[d]['idScope']})")
    (SEC / "creds.json").write_text(json.dumps(creds, indent=1), encoding="utf-8")
    print("guardado en", SEC / "creds.json")


if __name__ == "__main__":
    main()
