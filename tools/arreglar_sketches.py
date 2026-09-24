import pathlib

for w in ("rackb", "agua"):
    p = pathlib.Path(rf"C:\Users\mvale\Documents\Parcial1_IoT_Central\dispositivos\wokwi\{w}\sketch.ino")
    lineas = p.read_text(encoding="utf-8").split("\n")
    out = []
    i = 0
    n = 0
    while i < len(lineas):
        x = lineas[i]
        if "Serial.printf(" in x and not x.rstrip().endswith(");"):
            out.append(x.rstrip() + "\\n" + lineas[i + 1].lstrip())
            n += 1
            i += 2
            continue
        out.append(x)
        i += 1
    nuevo = "\n".join(out)
    p.write_text(nuevo, encoding="utf-8")
    t = p.read_text(encoding="utf-8")
    malas = sum(1 for l in t.split("\n") if l.count('"') % 2)
    print(f"{w}: unidas={n} bytes={len(t)} lineas_con_comillas_impares={malas}")
