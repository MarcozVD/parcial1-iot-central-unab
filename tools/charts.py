"""charts.py - graficos PIL con los datos medidos del Lab 3."""
from PIL import Image, ImageDraw, ImageFont

F = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 22)
FS = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 19)
FB = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 26)
NAVY, BLUE, GREEN, RED, GREY, LIGHT = (11, 42, 74), (31, 95, 168), (30, 132, 73), (192, 57, 43), (110, 118, 128), (226, 232, 240)


def latency():
    lat = [98, 105, 92, 99, 110, 111]
    W, H = 1500, 620
    im = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(im)
    d.text((60, 22), "Latencia publish → PUBACK por mensaje (QoS 1, intervalo 3 s)", font=FB, fill=NAVY)
    x0, y0, x1, y1 = 130, 110, W - 60, H - 90
    vmax = 140
    for v in range(0, vmax + 1, 20):
        y = y1 - (y1 - y0) * v / vmax
        d.line([x0, y, x1, y], fill=LIGHT, width=2)
        d.text((x0 - 60, y - 13), f"{v}", font=FS, fill=GREY)
    d.text((20, y0 - 45), "ms", font=FS, fill=GREY)
    n = len(lat); slot = (x1 - x0) / n; bw = slot * 0.55
    for i, v in enumerate(lat):
        cx = x0 + slot * (i + 0.5); top = y1 - (y1 - y0) * v / vmax
        d.rounded_rectangle([cx - bw / 2, top, cx + bw / 2, y1], radius=8, fill=BLUE)
        t = f"{v} ms"; d.text((cx - d.textlength(t, font=F) / 2, top - 34), t, font=F, fill=NAVY)
        l = f"TX #{i}"; d.text((cx - d.textlength(l, font=FS) / 2, y1 + 14), l, font=FS, fill=GREY)
    avg = sum(lat) / n; ya = y1 - (y1 - y0) * avg / vmax
    for x in range(int(x0), int(x1), 22):
        d.line([x, ya, x + 12, ya], fill=RED, width=3)
    d.text((x1 - 330, ya - 34), f"promedio {avg:.0f} ms", font=F, fill=RED)
    d.text((x0, H - 42), "Payload constante de 62 bytes · intervalo observado 3.11 s (configurado 3.0 s)", font=FS, fill=GREY)
    im.save("evidencias/chart_latencia.png")


def timeline():
    W, H = 1500, 520
    im = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(im)
    d.text((60, 22), "Corte de red real de 15 s con el cliente MQTT explícito (QoS 1)", font=FB, fill=NAVY)
    x0, x1 = 90, W - 70; t0, t1 = 31, 61  # segundos 05:06:31 -> 05:07:01
    def X(s): return x0 + (x1 - x0) * (s - t0) / (t1 - t0)
    ytx, yack = 190, 330
    d.text((x0, ytx - 72), "Publicaciones (TX)", font=F, fill=NAVY)
    d.text((x0, yack + 34), "Acuses del hub (PUBACK)", font=F, fill=NAVY)
    d.rectangle([X(40), 110, X(55), 420], fill=(253, 236, 234))
    d.text((X(40) + 12, 118), "sin conexión al hub (blackhole 15 s)", font=FS, fill=RED)
    d.line([x0, ytx, x1, ytx], fill=LIGHT, width=4); d.line([x0, yack, x1, yack], fill=LIGHT, width=4)
    tx = {4: 34, 5: 37, 6: 40, 7: 43, 8: 46, 9: 49, 10: 52, 11: 55, 12: 58}
    ack = {4: 34, 5: 37, 12: 58}
    for m, s in tx.items():
        c = RED if 40 <= s < 55 else BLUE
        d.ellipse([X(s) - 11, ytx - 11, X(s) + 11, ytx + 11], fill=c)
        d.text((X(s) - 12, ytx + 18), f"#{m}", font=FS, fill=GREY)
    for m, s in ack.items():
        d.ellipse([X(s) - 11, yack - 11, X(s) + 11, yack + 11], fill=GREEN)
        d.line([X(s), ytx + 12, X(s), yack - 12], fill=GREEN, width=2)
    # rafaga de 6 PUBACK a los 55 s
    for k in range(6):
        cx = X(55) + (k - 2.5) * 16
        d.ellipse([cx - 9, yack - 9, cx + 9, yack + 9], fill=GREEN)
    d.text((X(55) - 150, yack - 60), "6 PUBACK en ráfaga (mid 6–11)", font=FS, fill=GREEN)
    for s in range(31, 62, 5):
        d.text((X(s) - 30, 440), f"05:06:{s:02d}" if s < 60 else f"05:07:{s-60:02d}", font=FS, fill=GREY)
    d.text((x0, 478), "Resultado: los mensajes se encolaron durante el corte y el hub los acusó todos al restaurar → 0 pérdidas.", font=FS, fill=NAVY)
    im.save("evidencias/chart_corte.png")


if __name__ == "__main__":
    latency(); timeline(); print("charts ok")
