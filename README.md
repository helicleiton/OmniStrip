# OmniStrip

Channel strip gratuita para o REAPER (JSFX): preamp com saturação de console ou fita de rolo, gate, equalizador de 4 bandas, compressor, chorus, delay, reverb e seção de saída, com painel vintage e presets por módulo.

- `docs/` — landing page (GitHub Pages) e o pacote de download em `docs/download/OmniStrip.zip`.
- `build.py` — gera o pacote a partir do plugin instalado no REAPER. Rode `python build.py` depois de cada mudança no plugin.
- `src/` — backup do fonte, fora do git.
- `installer/` — instalador para Windows (Inno Setup 6): `OmniStrip.iss`, arte (`arte.py`) e o atualizador `OmniStrip_atualizador.lua`.

## Atualizações

O instalador põe o `OmniStrip_atualizador.lua` em `Scripts/OmniStrip` do REAPER e acrescenta uma linha ao `Scripts/__startup.lua`. Ao abrir o REAPER, ele consulta `www.helicleiton.com/omnistrip/versao.txt` (no máximo uma vez por dia). Se houver versão nova, o plugin mostra "NOVA VERSÃO DISPONÍVEL – ATUALIZAR"; o clique baixa o `download/OmniStrip.jsfx`, confere o SHA-256, guarda a versão anterior em `Scripts/OmniStrip/backup` e recria as instâncias abertas com os mesmos ajustes, sem fechar o REAPER.

Para lançar uma versão: aumente `VERSION` no `build.py` e `om_versao` no plugin (1.2 = 102), atualize `NOVIDADES`, rode `python build.py` e publique (`git push`). O `versao.txt` é gerado pelo build.

## Antes de publicar

1. Crie um Google Forms com uma única pergunta de e-mail e preencha `FORM_ACTION` e `FORM_FIELD` no fim de `docs/index.html`.
2. Salve uma captura do plugin em `docs/screenshot.png`.

Desenvolvido por @helicleiton.
