import pathlib

for w in ("rackb", "agua"):
    p = pathlib.Path(f"dispositivos/wokwi/{w}/sketch.ino")
    t = p.read_text(encoding="utf-8")
    lineas = t.split("\n")
    malas = [(n, l[:95]) for n, l in enumerate(lineas, 1) if l.count('"') % 2 == 1]
    print(f"{w}: lineas={len(lineas)} bytes={len(t)} | comillas impares={len(malas)}")
    for n, l in malas[:8]:
        print("   ", n, l)
    # verifica el patron exacto esperado
    print("   patron correcto (literal \\n):", "state=%d\\n\"" in t, "| patron roto:", "state=%d\n\"" in t)
