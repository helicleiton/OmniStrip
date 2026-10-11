"""Gera o pacote de distribuicao do OmniStrip (docs/download/OmniStrip.zip).

Le o plugin direto da pasta de efeitos do REAPER (a copia em uso), guarda um
backup do fonte em src/ (fora do git) e monta uma versao de distribuicao sem
comentarios e sem indentacao, com aviso de licenca.

JSFX e sempre texto: isso dificulta a leitura, mas nao esconde o codigo.

Uso: python build.py
"""
import io
import os
import re
import shutil
import zipfile

VERSION = "1.0"
ROOT = os.path.dirname(os.path.abspath(__file__))
LIVE = os.path.join(os.environ.get("APPDATA", ""), "REAPER", "Effects", "OmniStrip", "OmniStrip.jsfx")
SRC = os.path.join(ROOT, "src", "OmniStrip.jsfx")
OUT = os.path.join(ROOT, "docs", "download", "OmniStrip.zip")

LICENSE = """// OmniStrip {v} - Desenvolvido por @helicleiton
// Copyright (c) 2026 Helicleiton. Todos os direitos reservados.
// Uso gratuito, inclusive em trabalhos comerciais de audio.
// Proibido redistribuir, revender ou publicar este arquivo, modificado ou nao.
""".format(v=VERSION)

README = """OmniStrip {v} - Ultimate Channel Strip
Desenvolvido por @helicleiton

COMO INSTALAR (REAPER)
1. No REAPER, abra o menu Options > Show REAPER resource path in explorer/finder.
2. Entre na pasta "Effects".
3. Copie a pasta "OmniStrip" deste zip para dentro de "Effects".
4. Abra a janela de efeitos de uma pista (FX), aperte F5 para atualizar a
   lista e procure por "OmniStrip".

COMO USAR
- Arraste um knob para cima ou para baixo para ajustar.
- Segure Shift para ajuste fino. A roda do mouse tambem funciona.
- Duplo clique (ou Ctrl+clique) volta o knob ao valor padrao.
- O botao PRESETS de cada modulo abre a lista de ajustes prontos.
- No visor do delay: clique troca a figura de sync, clique direito volta.

LICENCA
Uso gratuito, inclusive em trabalhos comerciais de audio.
Proibido redistribuir, revender ou publicar o arquivo, modificado ou nao.
""".format(v=VERSION)


def strip(code):
    for line in code.splitlines():
        # garante que nenhum "//" esta dentro de uma string antes de cortar comentarios
        pos = line.find("//")
        assert pos < 0 or line[:pos].count('"') % 2 == 0, line
    code = re.sub(r"/\*.*?\*/", "", code, flags=re.S)
    out = []
    for line in code.splitlines():
        line = re.sub(r"//.*$", "", line).strip()
        if line:
            out.append(line)
    assert out[0].startswith("desc:"), out[0]
    return out[0] + "\n" + LICENSE + "\n".join(out[1:]) + "\n"


def main():
    src = LIVE if os.path.isfile(LIVE) else SRC
    if src == LIVE:
        os.makedirs(os.path.dirname(SRC), exist_ok=True)
        shutil.copyfile(LIVE, SRC)
    code = io.open(src, encoding="utf-8").read()
    dist = strip(code)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("OmniStrip/OmniStrip.jsfx", dist)
        z.writestr("LEIA-ME.txt", README.replace("\n", "\r\n"))
    print("fonte:", src)
    print("linhas: %d -> %d" % (len(code.splitlines()), len(dist.splitlines())))
    print("pacote:", OUT, "(%d KB)" % (os.path.getsize(OUT) // 1024))


if __name__ == "__main__":
    main()
