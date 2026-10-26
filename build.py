"""Gera os pacotes de distribuicao do OmniStrip: docs/download/OmniStrip.zip e OmniStrip-Setup.exe.

Le o plugin direto da pasta de efeitos do REAPER (a copia em uso), guarda um
backup do fonte em src/ (fora do git) e monta uma versao de distribuicao sem
comentarios e sem indentacao, com aviso de licenca.

JSFX e sempre texto: isso dificulta a leitura, mas nao esconde o codigo.
O instalador para Windows (Inno Setup 6, installer/OmniStrip.iss) leva essa mesma versao.

Uso: python build.py
"""
import hashlib
import io
import os
import re
import shutil
import subprocess
import zipfile

VERSION = "1.2"
# o que mudou nesta versao (aparece no versao.txt lido pelo atualizador)
NOVIDADES = "Compressor desligado ao inserir o plugin (neutro); parametro Drive com nome novo"
ROOT = os.path.dirname(os.path.abspath(__file__))
LIVE = os.path.join(os.environ.get("APPDATA", ""), "REAPER", "Effects", "OmniStrip", "OmniStrip.jsfx")
SRC = os.path.join(ROOT, "src", "OmniStrip.jsfx")
OUT = os.path.join(ROOT, "docs", "download", "OmniStrip.zip")
SETUP = os.path.join(ROOT, "docs", "download", "OmniStrip-Setup.exe")
# lidos pelo atualizador (installer/OmniStrip_atualizador.lua) em www.helicleiton.com/omnistrip
JSFX_PUB = os.path.join(ROOT, "docs", "download", "OmniStrip.jsfx")
VERSAO_TXT = os.path.join(ROOT, "docs", "versao.txt")
URL_JSFX = "https://www.helicleiton.com/omnistrip/download/OmniStrip.jsfx"
DIST = os.path.join(ROOT, "build", "OmniStrip.jsfx")
ISCC = [os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Inno Setup 6", "ISCC.exe"),
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"]

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
    # Se o instalador foi rodado nesta maquina, o arquivo do REAPER e a versao de distribuicao
    # (sem comentarios): nao copia por cima do fonte em src/ e gera a partir de src/.
    if src == LIVE and "Proibido redistribuir" in io.open(LIVE, encoding="utf-8").read(4000):
        print("AVISO: o OmniStrip do REAPER e a versao instalada (sem comentarios); usando src/")
        src = SRC
    if src == LIVE:
        os.makedirs(os.path.dirname(SRC), exist_ok=True)
        shutil.copyfile(LIVE, SRC)
    code = io.open(src, encoding="utf-8").read()
    dist = strip(code)
    # o numero de versao dentro do plugin (om_versao = 1.1 -> 101) precisa bater com VERSION
    m = re.search(r"om_versao\s*=\s*(\d+);", code)
    maj, mi = (int(x) for x in VERSION.split("."))
    assert m and int(m.group(1)) == maj * 100 + mi, "om_versao no plugin (%s) difere de VERSION %s" % (m and m.group(1), VERSION)
    assert "options:gmem=OmniStrip" in dist
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("OmniStrip/OmniStrip.jsfx", dist)
        z.writestr("LEIA-ME.txt", README.replace("\n", "\r\n"))
    # plugin solto + versao.txt, para o atualizador
    io.open(JSFX_PUB, "w", encoding="utf-8", newline="").write(dist)
    sha = hashlib.sha256(dist.encode("utf-8")).hexdigest()
    io.open(VERSAO_TXT, "w", encoding="utf-8", newline="\n").write(
        "versao=%s\narquivo=%s\nsha256=%s\nnovidades=%s\n" % (VERSION, URL_JSFX, sha, NOVIDADES))
    # numero da versao mostrado na pagina
    pag = os.path.join(ROOT, "docs", "index.html")
    html = io.open(pag, encoding="utf-8").read()
    io.open(pag, "w", encoding="utf-8").write(re.sub(r"Versão \d+\.\d+", "Versão " + VERSION, html))
    # instalador para Windows
    os.makedirs(os.path.dirname(DIST), exist_ok=True)
    io.open(DIST, "w", encoding="utf-8", newline="").write(dist)
    iscc = next((p for p in ISCC if os.path.isfile(p)), None)
    if iscc:
        iss = os.path.join(ROOT, "installer", "OmniStrip.iss")
        subprocess.run([iscc, "/Q", "/DAppVersion=" + VERSION, iss], check=True)
        shutil.copyfile(os.path.join(ROOT, "installer", "Output", "OmniStrip-Setup-%s.exe" % VERSION), SETUP)
    else:
        print("AVISO: Inno Setup 6 nao encontrado; instalador nao gerado")
    print("fonte:", src)
    print("linhas: %d -> %d" % (len(code.splitlines()), len(dist.splitlines())))
    print("pacote:", OUT, "(%d KB)" % (os.path.getsize(OUT) // 1024))
    print("versao.txt:", VERSION, sha[:16] + "...")
    if iscc:
        print("instalador:", SETUP, "(%d KB)" % (os.path.getsize(SETUP) // 1024))


if __name__ == "__main__":
    main()
