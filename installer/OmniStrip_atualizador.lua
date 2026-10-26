-- OmniStrip: avisa quando ha versao nova e atualiza o plugin sem fechar o REAPER.
-- Desenvolvido por @helicleiton - helicleiton.com
--
-- Instalado pelo OmniStrip-Setup.exe em <REAPER>/Scripts/OmniStrip e iniciado pelo __startup.lua.
-- Conversa com o plugin pela memoria compartilhada (gmem) "OmniStrip":
--   [0] versao mais nova no site (1.2 = 102)   [1] estado: 2 baixando, 3 atualizado, 4 falhou
--   [2] pedido do plugin (1 = atualizar agora)  [3] atualizador ativo (1)
-- A versao nova e conferida (SHA-256 e conteudo) antes de substituir o arquivo, a anterior vai
-- para Scripts/OmniStrip/backup, e as instancias abertas sao recriadas com os mesmos ajustes.

local cfg = OMNISTRIP_TESTE or {}   -- substituicoes usadas so nos testes
local URL = cfg.url or "https://www.helicleiton.com/omnistrip/versao.txt"
local SECAO = cfg.secao or "OmniStrip"
local INTERVALO = cfg.intervalo or 24 * 3600   -- consulta o site no maximo uma vez por dia
local ESPERA = cfg.espera or 20                -- segundos depois de o REAPER abrir

local SEP = package.config:sub(1, 1)
local AQUI = debug.getinfo(1, "S").source:match("^@(.*)[\\/]")
local RES = reaper.GetResourcePath()
local SYS = os.getenv("SystemRoot") or "C:\\Windows"
local CURL = SYS .. "\\System32\\curl.exe"
local CERTUTIL = SYS .. "\\System32\\certutil.exe"
local TMP = (os.getenv("TEMP") or AQUI) .. "\\OmniStrip-atualizador"

local function ler(p) local f = io.open(p, "rb"); if not f then return nil end; local s = f:read("*a"); f:close(); return s end
local function gravar(p, s) local f = io.open(p, "wb"); if not f then return false end; f:write(s); f:close(); return true end
local function existe(p) local f = io.open(p, "rb"); if f then f:close(); return true end; return false end
local function barra(p) return (p:gsub("\\", "/")) end
local function log(msg)
  local f = io.open(AQUI .. "/atualizador.log", "a")
  if f then f:write(os.date("%Y-%m-%d %H:%M:%S  ") .. msg .. "\n"); f:close() end
end

-- onde esta o plugin: o instalador grava a pasta em pasta.txt
local PASTA = cfg.pasta or ((ler(AQUI .. "/pasta.txt") or ""):match("^%s*(.-)%s*$"))
if not PASTA or PASTA == "" then PASTA = RES .. "/Effects/OmniStrip" end
local ARQ = barra(PASTA) .. "/OmniStrip.jsfx"
local EFFECTS = barra(RES) .. "/Effects/"
-- caminho como aparece nos projetos, relativo a Effects ("OmniStrip/OmniStrip.jsfx")
local REL = ARQ:lower():sub(1, #EFFECTS) == EFFECTS:lower() and ARQ:sub(#EFFECTS + 1) or nil

local function codigo(v)   -- "1.2" -> 102
  local a, b = tostring(v or ""):match("^%s*(%d+)%.(%d+)")
  return a and tonumber(a) * 100 + tonumber(b) or 0
end

local function executar(cmd, ms)   -- devolve codigo de saida e texto
  local r = reaper.ExecProcess(cmd, ms) or ""
  local cod, saida = r:match("^(%-?%d+)\n?(.*)$")
  return tonumber(cod) or -1, saida or ""
end

-- ---------------------------------------------------------------- consulta de versao
local info = {}

local function verificar()
  reaper.SetExtState(SECAO, "ultima_verificacao", tostring(os.time()), true)
  if not existe(CURL) then return end
  local cod, txt = executar('"' .. CURL .. '" -fsSL --connect-timeout 5 --max-time 8 "' .. URL .. '"', 10000)
  if cod ~= 0 then log("consulta falhou (curl " .. cod .. ")"); return end
  local t = {}
  for k, v in txt:gmatch("([%w_]+)%s*=%s*([^\r\n]*)") do t[k] = v end
  if codigo(t.versao) == 0 or not t.arquivo or not t.sha256 then log("versao.txt invalido"); return end
  info = t
  for _, k in ipairs({"versao", "arquivo", "sha256"}) do reaper.SetExtState(SECAO, k, t[k], true) end
  reaper.gmem_write(0, codigo(t.versao))
end

-- ---------------------------------------------------------------- recarga das instancias
local function escapar(s) return (s:gsub("%p", "%%%0")) end

-- Recria as instancias abertas: o REAPER so le o arquivo de novo quando a instancia e criada, e
-- reaproveita a instancia se o trecho da pista nao mudar. Trocar "/" por "\" no caminho do efeito
-- faz ele criar outra instancia, com o codigo novo e os mesmos ajustes, automacoes e presets.
local function recarregar()
  if not REL then return 0 end
  local a, b = REL:gsub("\\", "/"), REL:gsub("/", "\\")
  local n, p = 0, 0
  while true do
    local proj = reaper.EnumProjects(p); if not proj then break end
    local pistas = { reaper.GetMasterTrack(proj) }
    for i = 0, reaper.CountTracks(proj) - 1 do pistas[#pistas + 1] = reaper.GetTrack(proj, i) end
    local mexeu = false
    for _, tr in ipairs(pistas) do
      local ok, ch = reaper.GetTrackStateChunk(tr, "", false)
      if ok and (ch:find("<JS " .. a, 1, true) or ch:find("<JS " .. b, 1, true)
                 or ch:find('<JS "' .. a, 1, true) or ch:find('<JS "' .. b, 1, true)) then
        -- janelas abertas antes, para reabrir depois
        local janelas = {}
        for fx = 0, reaper.TrackFX_GetCount(tr) - 1 do
          if reaper.TrackFX_GetFloatingWindow(tr, fx) then janelas[#janelas + 1] = { fx, 3 } end
        end
        local cadeia = reaper.TrackFX_GetChainVisible(tr)
        local c, k1, k2, k3, k4
        c, k1 = ch:gsub("<JS " .. escapar(a), "<JS \1")
        c, k2 = c:gsub("<JS " .. escapar(b), "<JS " .. a:gsub("%%", "%%%%"))
        c = c:gsub("<JS \1", "<JS " .. b:gsub("%%", "%%%%"))
        c, k3 = c:gsub('<JS "' .. escapar(a), '<JS "\1')
        c, k4 = c:gsub('<JS "' .. escapar(b), '<JS "' .. a:gsub("%%", "%%%%"))
        c = c:gsub('<JS "\1', '<JS "' .. b:gsub("%%", "%%%%"))
        if not mexeu then reaper.Undo_BeginBlock2(proj); mexeu = true end
        reaper.SetTrackStateChunk(tr, c, false)
        for _, j in ipairs(janelas) do reaper.TrackFX_Show(tr, j[1], j[2]) end
        if cadeia >= 0 then reaper.TrackFX_Show(tr, cadeia, 1) end
        n = n + k1 + k2 + k3 + k4
      end
    end
    if mexeu then reaper.Undo_EndBlock2(proj, "Atualizar OmniStrip", -1) end
    p = p + 1
  end
  return n
end

-- ---------------------------------------------------------------- atualizacao
local function falhou(msg) log("atualizacao: " .. msg); reaper.gmem_write(1, 4) end

local function atualizar()
  reaper.gmem_write(1, 2)
  local versao = info.versao or reaper.GetExtState(SECAO, "versao")
  local url = info.arquivo or reaper.GetExtState(SECAO, "arquivo")
  local sha = (info.sha256 or reaper.GetExtState(SECAO, "sha256")):lower()
  if codigo(versao) == 0 or url == "" or sha == "" then return falhou("sem dados da versao nova") end
  if not existe(CURL) then return falhou("curl.exe nao encontrado") end

  local atual = ler(ARQ)
  -- protecao: nunca troca uma copia de desenvolvimento (com comentarios) do plugin
  if atual and not atual:find("Proibido redistribuir", 1, true) then return falhou("copia de desenvolvimento; nada alterado") end

  reaper.RecursiveCreateDirectory(TMP, 0)
  local novo_arq = TMP .. "\\OmniStrip.jsfx"
  os.remove(novo_arq)
  local cod = executar('"' .. CURL .. '" -fsSL --connect-timeout 5 --max-time 30 -o "' .. novo_arq .. '" "' .. url .. '"', 35000)
  if cod ~= 0 or not existe(novo_arq) then return falhou("download falhou (curl " .. cod .. ")") end
  local _, h = executar('"' .. CERTUTIL .. '" -hashfile "' .. novo_arq .. '" SHA256', 10000)
  local hash = (h:match("\n%s*([%x ]+)%s*\r?\n") or ""):gsub("%s", ""):lower()
  if hash ~= sha then return falhou("SHA-256 nao confere (" .. hash .. ")") end
  local novo = ler(novo_arq)
  local ver_arq = tonumber(novo and novo:match("om_versao%s*=%s*(%d+)") or "")
  if not novo or not novo:find("^desc: OmniStrip") or ver_arq ~= codigo(versao) then return falhou("arquivo baixado nao e o OmniStrip " .. versao) end

  if atual then
    reaper.RecursiveCreateDirectory(AQUI .. "/backup", 0)
    local antiga = atual:match("om_versao%s*=%s*(%d+)") or "antiga"
    gravar(AQUI .. "/backup/OmniStrip-" .. antiga .. ".jsfx", atual)
  end
  reaper.RecursiveCreateDirectory(barra(PASTA), 0)
  if not gravar(ARQ, novo) then return falhou("sem permissao para gravar " .. ARQ) end
  os.remove(novo_arq)

  local n = recarregar()
  reaper.SetExtState(SECAO, "instalada", versao, true)
  reaper.gmem_write(1, 3)
  log("atualizado para " .. versao .. "; instancias recriadas: " .. n)
end

-- ---------------------------------------------------------------- laco principal
reaper.gmem_attach("OmniStrip")
reaper.gmem_write(3, 1)
reaper.gmem_write(2, 0)
reaper.gmem_write(1, 0)
reaper.gmem_write(0, codigo(reaper.GetExtState(SECAO, "versao")))   -- ultimo resultado conhecido

local inicio = reaper.time_precise()
local proxima = 0
local function laco()
  local agora = reaper.time_precise()
  if agora - inicio >= ESPERA and agora >= proxima then
    proxima = agora + 3600   -- reavalia a cada hora; consulta o site so se passou o intervalo
    local ultima = tonumber(reaper.GetExtState(SECAO, "ultima_verificacao")) or 0
    if os.time() - ultima >= INTERVALO then verificar() end
  end
  if reaper.gmem_read(2) == 1 then
    reaper.gmem_write(2, 0)
    local ok, err = pcall(atualizar)
    if not ok then falhou(tostring(err)) end
  end
  reaper.defer(laco)
end
laco()
