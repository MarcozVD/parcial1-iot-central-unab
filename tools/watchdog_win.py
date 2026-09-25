#!/usr/bin/env python3
"""Watchdog independiente de Hermes para la flota DC-ANDES-1.

Se ejecuta como proceso desprendido y cada `--cada` segundos:
  1. comprueba que el supervisor siga vivo (logs/supervisor_estado.json + pid en ejecucion);
  2. comprueba la frescura de los CSV locales (si todos estan viejos, el supervisor esta muerto);
  3. relanza el supervisor con start_supervisor.cmd cuando hace falta;
  4. deja constancia en logs/watchdog_win.log.

Uso:
    .venv/Scripts/python.exe tools/watchdog_win.py            # bucle (proceso desprendido)
    .venv/Scripts/python.exe tools/watchdog_win.py --una-vez  # una sola pasada (para probar)
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import subprocess
import time

RAIZ = pathlib.Path(__file__).resolve().parents[1]
ESTADO = RAIZ / "logs" / "supervisor_estado.json"
LOG = RAIZ / "logs" / "watchdog_win.log"
ARRANQUE = RAIZ / "tools" / "start_supervisor.cmd"
PY = RAIZ / ".venv" / "Scripts" / "python.exe"
PAUSA = RAIZ / "logs" / "PAUSA_FLOTA"


def log(msg: str) -> None:
    linea = f"{dt.datetime.now():%Y-%m-%d %H:%M:%S} {msg}"
    print(linea, flush=True)
    with LOG.open("a", encoding="utf-8") as fh:
        fh.write(linea + "\n")


def pid_vivo(pid: int) -> bool:
    salida = subprocess.run(
        ["tasklist", "/FI", f"PID eq {pid}", "/NH"],
        capture_output=True, text=True, shell=False,
    ).stdout
    return str(pid) in salida


def supervisor_vivo() -> tuple[bool, str]:
    if not ESTADO.exists():
        return False, "sin logs/supervisor_estado.json"
    try:
        datos = json.loads(ESTADO.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        return False, f"estado ilegible: {exc}"
    vivos = 0
    for nombre, info in datos.items():
        if isinstance(info, dict) and info.get("pid") and pid_vivo(int(info["pid"])):
            vivos += 1
    if vivos >= 5:
        return True, f"{vivos}/{len(datos)} nodos vivos"
    return False, f"solo {vivos}/{len(datos)} nodos vivos"


def csv_frescos(minutos: int = 30) -> tuple[bool, str]:
    csvs = sorted((RAIZ / "datos").glob("DC-*.csv"))
    csvs = [c for c in csvs if "campo" not in c.name and "historico" not in c.name]
    if not csvs:
        return False, "sin CSV locales"
    limite = time.time() - minutos * 60
    frescos = [c.name for c in csvs if c.stat().st_mtime >= limite]
    return len(frescos) >= 2, f"{len(frescos)}/{len(csvs)} CSV actualizados en {minutos} min"


def relanzar() -> None:
    log("supervisor caido -> relanzando")
    subprocess.Popen(
        ["cmd", "/c", "start", "", "/min", str(ARRANQUE)],
        cwd=str(RAIZ), shell=False,
    )


def supervisor_por_proceso() -> bool:
    """True si hay algun proceso dc_supervisor.py vivo (aunque el estado sea viejo)."""
    ps = ("Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | "
          "Where-Object { $_.CommandLine -like '*dc_supervisor.py*' } | Measure-Object | "
          "Select-Object -ExpandProperty Count")
    try:
        out = subprocess.run(["powershell", "-NoProfile", "-Command", ps],
                             capture_output=True, text=True, timeout=90).stdout.strip()
        return int(out.splitlines()[-1]) > 0
    except Exception:  # noqa: BLE001
        return False


def pasada() -> None:
    if PAUSA.exists():
        log("pausa activa (logs/PAUSA_FLOTA): sin vigilancia ni relanzado")
        return
    ok_sup, detalle_sup = supervisor_vivo()
    ok_csv, detalle_csv = csv_frescos()
    if not ok_sup and supervisor_por_proceso():
        # el supervisor acaba de arrancar y aun no reescribio el estado: no es una caida
        log(f"supervisor en arranque ({detalle_csv}); se espera al siguiente ciclo")
        return
    if ok_sup and ok_csv:
        log(f"ok: {detalle_sup}; {detalle_csv}")
        return
    log(f"alerta: {detalle_sup}; {detalle_csv}")
    if not ok_sup and not ok_csv:
        relanzar()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cada", type=int, default=600, help="segundos entre pasadas")
    ap.add_argument("--una-vez", action="store_true")
    args = ap.parse_args()
    if args.una_vez:
        pasada()
        return 0
    log(f"watchdog iniciado (cada {args.cada}s)")
    while True:
        try:
            pasada()
        except Exception as exc:  # noqa: BLE001
            log(f"error en la pasada: {exc}")
        time.sleep(args.cada)


if __name__ == "__main__":
    raise SystemExit(main())
