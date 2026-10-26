"""Gera a arte do instalador: icone (.ico), imagem lateral (com o QR do Pix) e imagem pequena.

Uso: python installer/arte.py   (le installer/pix-qrcode.png)
"""
import os
from PIL import Image, ImageDraw, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts")
CREAM, AMBER, PANEL, DARK = (237, 227, 189), (242, 179, 76), (95, 110, 120), (22, 23, 26)


def fonte(tam, negrito=True):
    return ImageFont.truetype(os.path.join(FONTS, "arialbd.ttf" if negrito else "arial.ttf"), tam)


def knob(d, cx, cy, r, cap, angulo):
    """Knob no estilo do painel: saia preta, tampa colorida e ponteiro branco."""
    import math
    d.ellipse([cx - r + 2, cy - r + 4, cx + r + 2, cy + r + 4], fill=(0, 0, 0, 110))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(14, 14, 16))
    d.ellipse([cx - r + 1, cy - r, cx + r - 1, cy + r - 2], fill=(46, 46, 50))
    d.ellipse([cx - r + 2, cy - r + 2, cx + r - 2, cy + r - 2], fill=(22, 22, 24))
    c = r * 0.66
    d.ellipse([cx - c, cy - c, cx + c, cy + c], fill=tuple(int(v * 0.55) for v in cap))
    c2 = r * 0.6
    d.ellipse([cx - c2, cy - c2 - 1, cx + c2, cy + c2 - 1], fill=cap)
    hl = r * 0.25
    d.ellipse([cx - r * 0.3 - hl, cy - r * 0.32 - hl, cx - r * 0.3 + hl, cy - r * 0.32 + hl], fill=tuple(min(255, v + 70) for v in cap))
    a = math.radians(angulo)
    d.line([cx + math.sin(a) * r * 0.15, cy - math.cos(a) * r * 0.15, cx + math.sin(a) * r * 0.95, cy - math.cos(a) * r * 0.95],
           fill=(250, 246, 232), width=max(2, int(r / 7)))


def qr_grade():
    """Le pix-qrcode.png e devolve a grade de modulos (amostrando o centro de cada um)."""
    im = Image.open(os.path.join(AQUI, "pix-qrcode.png")).convert("RGBA")
    fundo = Image.new("RGBA", im.size, "white"); fundo.alpha_composite(im)
    g = fundo.convert("L"); W, H = g.size; px = g.load()
    escuro = lambda x, y: px[x, y] < 128
    pts = [(x, y) for y in range(H) for x in range(W) if escuro(x, y)]
    x0 = min(p[0] for p in pts); x1 = max(p[0] for p in pts); y0 = min(p[1] for p in pts)
    corrida = 0
    while escuro(x0 + corrida, y0): corrida += 1
    n = round((x1 - x0 + 1) / (corrida / 7.0)); mod = (x1 - x0 + 1) / n
    return [[escuro(int(x0 + (c + 0.5) * mod), int(y0 + (r + 0.5) * mod)) for c in range(n)] for r in range(n)]


def icone():
    tamanhos = [16, 24, 32, 48, 64, 128, 256]
    base = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    d = ImageDraw.Draw(base)
    d.rounded_rectangle([8, 8, 248, 248], 44, fill=(70, 82, 90))
    d.rounded_rectangle([8, 8, 248, 248], 44, outline=(20, 20, 22), width=6)
    knob(d, 128, 128, 92, (184, 39, 31), -40)
    base.save(os.path.join(AQUI, "OmniStrip.ico"), sizes=[(s, s) for s in tamanhos])


def lateral(escala):
    """Imagem das telas de boas-vindas e de conclusao (164x314 em 100%)."""
    W, H = 164 * escala, 314 * escala
    im = Image.new("RGB", (W, H), DARK)
    d = ImageDraw.Draw(im, "RGBA")
    for y in range(H):  # chapa azul-acinzentada com leve degrade
        k = 1 - 0.18 * y / H
        d.line([(0, y), (W, y)], fill=tuple(int(v * k) for v in PANEL))
    madeira = 10 * escala
    for x in range(madeira):
        d.line([(x, 0), (x, H)], fill=(int(86 + 14 * ((x * 7) % 3)), 47, 20))
    s = escala
    d.rectangle([madeira, 0, W, 34 * s], fill=(14, 15, 18))
    d.text((madeira + 10 * s, 7 * s), "OMNISTRIP", font=fonte(17 * s), fill=CREAM)
    d.text((madeira + 11 * s, 25 * s), "CHANNEL STRIP", font=fonte(7 * s), fill=AMBER)
    for i, (cap, ang) in enumerate([((184, 39, 31), -50), ((46, 92, 158), 30), ((56, 133, 92), 110)]):
        knob(d, madeira + 26 * s + i * 42 * s, 64 * s, 15 * s, cap, ang)
    d.text((madeira + 10 * s, 92 * s), "Desenvolvido por", font=fonte(8 * s, False), fill=CREAM)
    d.text((madeira + 10 * s, 103 * s), "@helicleiton", font=fonte(12 * s), fill=CREAM)
    d.text((madeira + 10 * s, 119 * s), "helicleiton.com", font=fonte(10 * s), fill=AMBER)
    # QR do Pix sobre fundo branco, modulos inteiros
    grade = qr_grade()
    mod = (130 * s) // (len(grade) + 4)  # modulos de tamanho inteiro, com 2 de margem
    lado = mod * (len(grade) + 4)
    qr = Image.new("RGB", (lado, lado), "white"); dq = ImageDraw.Draw(qr)
    for r, linha in enumerate(grade):
        for c, v in enumerate(linha):
            if v: dq.rectangle([(c + 2) * mod, (r + 2) * mod, (c + 3) * mod - 1, (r + 3) * mod - 1], fill="black")
    qx, qy = madeira + (W - madeira - lado) // 2, 146 * s
    d.rectangle([qx + 2 * s, qy + 3 * s, qx + lado + 2 * s, qy + lado + 3 * s], fill=(0, 0, 0, 120))
    im.paste(qr, (qx, qy))
    cx = madeira + (W - madeira) // 2
    d.text((cx, qy + lado + 8 * s), "APOIE VIA PIX", font=fonte(9 * s), fill=CREAM, anchor="mt")
    d.text((cx, qy + lado + 21 * s), "doação espontânea", font=fonte(8 * s, False), fill=(214, 218, 221), anchor="mt")
    return im


def pequena(escala):
    W = 55 * escala
    im = Image.new("RGB", (W, W), (255, 255, 255))
    d = ImageDraw.Draw(im, "RGBA")
    knob(d, W // 2, W // 2, int(W * 0.42), (184, 39, 31), -40)
    return im


if __name__ == "__main__":
    icone()
    lateral(1).save(os.path.join(AQUI, "lateral.bmp"))
    lateral(2).save(os.path.join(AQUI, "lateral@2x.bmp"))
    pequena(1).save(os.path.join(AQUI, "pequena.bmp"))
    pequena(2).save(os.path.join(AQUI, "pequena@2x.bmp"))
    print("arte gerada em", AQUI)
