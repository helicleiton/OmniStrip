; Instalador do OmniStrip (efeito JSFX para REAPER) para Windows
; Compilar com Inno Setup 6:  ISCC.exe /DAppVersion=1.1 installer\OmniStrip.iss
; (o build.py faz isso e copia o resultado para docs\download\OmniStrip-Setup.exe)
;
; Instala na pasta de efeitos do REAPER do usuario, sem pedir administrador:
;   %APPDATA%\REAPER\Effects\OmniStrip\OmniStrip.jsfx
; Quem usa o REAPER portatil escolhe a pasta Effects dele na tela de destino.
; O desinstalador e o icone ficam fora do REAPER, em %LOCALAPPDATA%\Programs\OmniStrip.

#ifndef AppVersion
  #define AppVersion "1.1"
#endif
#define AppName "OmniStrip"
#define AppPublisher "Helicleiton"
#define Dist "..\build"

[Setup]
AppId={{E3044676-44B7-4169-ACB4-3972353DD277}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
VersionInfoVersion={#AppVersion}
VersionInfoDescription=Instalador do OmniStrip para REAPER
AppPublisher={#AppPublisher}
AppPublisherURL=https://www.helicleiton.com
AppSupportURL=https://www.helicleiton.com/omnistrip
AppUpdatesURL=https://www.helicleiton.com/omnistrip
AppCopyright=Copyright (c) 2026 Helicleiton
DefaultDirName={userappdata}\REAPER\Effects\OmniStrip
AppendDefaultDirName=no
DirExistsWarning=no
UsePreviousAppDir=yes
DisableProgramGroupPage=yes
CreateAppDir=yes
OutputDir=Output
OutputBaseFilename=OmniStrip-Setup-{#AppVersion}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
SetupIconFile=OmniStrip.ico
UninstallFilesDir={localappdata}\Programs\OmniStrip
UninstallDisplayIcon={localappdata}\Programs\OmniStrip\OmniStrip.ico
UninstallDisplayName={#AppName} (REAPER)
WizardImageFile=lateral.bmp,lateral@2x.bmp
WizardSmallImageFile=pequena.bmp,pequena@2x.bmp
WizardImageStretch=no
WizardImageBackColor=$786E5F

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "{#Dist}\OmniStrip.jsfx"; DestDir: "{app}"; Flags: ignoreversion
Source: "OmniStrip.ico"; DestDir: "{localappdata}\Programs\OmniStrip"; Flags: ignoreversion

[Run]
Filename: "https://www.helicleiton.com/omnistrip"; Description: "Visitar helicleiton.com"; Flags: shellexec postinstall skipifsilent nowait unchecked

[UninstallDelete]
Type: dirifempty; Name: "{app}"
Type: filesandordirs; Name: "{localappdata}\Programs\OmniStrip"

[Messages]
brazilianportuguese.WelcomeLabel2=Este assistente vai instalar o OmniStrip [ver] no REAPER.%n%nO OmniStrip é uma channel strip gratuita: preamp com saturação de console ou de fita de rolo, gate, equalizador, compressor, chorus, delay e reverb.%n%nDesenvolvido por @helicleiton%nhelicleiton.com
brazilianportuguese.SelectDirLabel3=O OmniStrip vai para a pasta de efeitos (Effects) do REAPER.
brazilianportuguese.SelectDirBrowseLabel=Se você usa o REAPER portátil, clique em Procurar e escolha a pasta Effects dele. Senão, apenas clique em Avançar.
brazilianportuguese.FinishedHeadingLabel=OmniStrip instalado
brazilianportuguese.FinishedLabelNoIcons=No REAPER, abra a janela de efeitos (FX) de uma pista, aperte F5 para atualizar a lista e procure por OmniStrip.%n%nO OmniStrip é gratuito. Se ele ajuda a sua música, considere fazer uma doação espontânea via Pix: o QR code está aqui ao lado e também no botão SOBRE do plugin.%n%nDesenvolvido por @helicleiton - helicleiton.com
english.WelcomeLabel2=This will install OmniStrip [ver] into REAPER.%n%nOmniStrip is a free channel strip: preamp with console or tape saturation, gate, EQ, compressor, chorus, delay and reverb.%n%nDeveloped by @helicleiton%nhelicleiton.com
english.FinishedLabelNoIcons=In REAPER, open a track's FX window, press F5 to refresh the list and search for OmniStrip.%n%nOmniStrip is free. If it helps your music, consider a voluntary Pix donation: the QR code is shown here and in the plugin's SOBRE (about) button.%n%nDeveloped by @helicleiton - helicleiton.com

[Code]
// Avisa se a pasta escolhida nao fica dentro de uma pasta Effects do REAPER existente.
function NextButtonClick(CurPageID: Integer): Boolean;
var
  Effects: String;
begin
  Result := True;
  if CurPageID = wpSelectDir then
  begin
    Effects := ExtractFileDir(RemoveBackslashUnlessRoot(WizardDirValue));
    if not DirExists(Effects) then
      Result := MsgBox('Não encontrei a pasta de efeitos do REAPER:' + #13#10 + Effects + #13#10#13#10 +
        'O REAPER está instalado? Se você usa o REAPER portátil, volte e escolha a pasta Effects dele.' + #13#10#13#10 +
        'Instalar mesmo assim?', mbConfirmation, MB_YESNO) = IDYES;
  end;
end;
