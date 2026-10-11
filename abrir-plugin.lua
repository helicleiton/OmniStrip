-- Abre o OmniStrip numa pista nova, em janela flutuante.
-- Uso: reaper.exe -newinst -new abrir-plugin.lua
reaper.InsertTrackAtIndex(0, true)
local track = reaper.GetTrack(0, 0)
reaper.GetSetMediaTrackInfo_String(track, "P_NAME", "OmniStrip", true)

local names = {
  "JS: OmniStrip/OmniStrip.jsfx",
  "JS:OmniStrip/OmniStrip.jsfx",
  "OmniStrip/OmniStrip.jsfx",
  "JS: OmniStrip JSFX - Ultimate Channel Strip",
  "OmniStrip",
}
local fx = -1
for _, name in ipairs(names) do
  fx = reaper.TrackFX_AddByName(track, name, false, -1)
  if fx >= 0 then break end
end

if fx >= 0 then
  reaper.TrackFX_Show(track, fx, 3)
else
  reaper.ShowMessageBox("Nao encontrei o OmniStrip na pasta Effects do REAPER.", "OmniStrip", 0)
end
