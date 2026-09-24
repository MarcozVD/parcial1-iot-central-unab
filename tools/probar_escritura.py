import pathlib, time

p = pathlib.Path(r"C:\Users\mvale\Documents\Parcial1_IoT_Central\dispositivos\wokwi\rackb\sketch.ino")
t = p.read_text(encoding="utf-8")
print("antes: bytes", len(t), "| canario:", "//CANARIO" in t)
t2 = "//CANARIO-ABC\n" + t
p.write_text(t2, encoding="utf-8")
time.sleep(1)
t3 = p.read_text(encoding="utf-8")
print("despues: bytes", len(t3), "| canario:", "//CANARIO-ABC" in t3)

# ahora el join y verificacion inmediata
lineas = t3.split("\n")
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
print("unidas:", n)
nuevo = "\n".join(out)
print("en memoria, patron roto:", 'state=%d\n"' in nuevo, "| correcto:", 'state=%d\\n"' in nuevo)
p.write_text(nuevo, encoding="utf-8")
time.sleep(1)
t4 = p.read_text(encoding="utf-8")
print("tras escribir: patron roto:", 'state=%d\n"' in t4, "| correcto:", 'state=%d\\n"' in t4, "| bytes", len(t4))
print("canario sigue:", "//CANARIO-ABC" in t4)
