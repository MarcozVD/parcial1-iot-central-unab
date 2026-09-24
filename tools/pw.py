#!/usr/bin/env python3
"""Helper para playwright-cli (sesion 'iot') desde bash/MSYS.

Uso:
  python tools/pw.py eval "<js>"            -> imprime el valor (JSON)
  python tools/pw.py text [maxchars]        -> document.body.innerText
  python tools/pw.py goto <url>
  python tools/pw.py click <selector>
  python tools/pw.py fill <selector> <valor>
  python tools/pw.py shot <ruta.png>
  python tools/pw.py raw <comando...>       -> playwright-cli crudo

Nota Windows: el JS no debe contener comillas dobles; usar simples/backticks.
"""
import json
import subprocess
import sys

SESSION = "iot"
PROFILE = "C:/Users/mvale/AppData/Local/Temp/edgeprof"


def run(args, timeout=120):
    import shutil
    exe = shutil.which("playwright-cli") or "playwright-cli.cmd"
    if exe.lower().endswith(".cmd") or exe.lower().endswith(".bat"):
        cmd = f'"{exe}" -s={SESSION} ' + " ".join(f'"{a}"' for a in args)
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, shell=True)
    else:
        cmd = [exe, f"-s={SESSION}"] + args
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, shell=False)
    return p.stdout + p.stderr


def parse_value(out):
    """--raw eval: descarta lineas 'await ...' y toma la ultima como JSON."""
    lines = [l for l in out.splitlines() if l.strip() and not l.strip().startswith("await")]
    if not lines:
        return None
    last = lines[-1].strip()
    try:
        v = json.loads(last)
    except Exception:
        return last
    if isinstance(v, str):
        try:
            return json.loads(v)
        except Exception:
            return v
    return v


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    op = sys.argv[1]
    if op == "eval":
        out = run(["--raw", "eval", sys.argv[2]])
        v = parse_value(out)
        print(json.dumps(v, ensure_ascii=False, indent=1) if not isinstance(v, str) else v)
    elif op == "text":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 4000
        out = run(["--raw", "eval", "document.body.innerText"])
        v = parse_value(out) or ""
        print(v[:n])
    elif op == "js":
        # ejecuta un archivo JS con run-code (async (page) => {...})
        print(run(["run-code", "--filename", sys.argv[2]], timeout=150))
    elif op == "goto":
        print(run(["goto", sys.argv[2]], timeout=150))
    elif op == "click":
        print(run(["click", sys.argv[2]]))
    elif op == "fill":
        print(run(["fill", sys.argv[2], sys.argv[3]]))
    elif op == "shot":
        js = ("async (page) => { await page.setViewportSize({width:1500,height:950}); "
              "await page.waitForTimeout(1200); "
              f"await page.screenshot({{path: '{sys.argv[2]}'}}); return 'ok'; }}")
        out = run(["run-code", "--filename"], timeout=5)  # placeholder, se usa el archivo aparte
        print(out)
    else:
        print(run(sys.argv[1:], timeout=180))
    return 0


if __name__ == "__main__":
    sys.exit(main())
