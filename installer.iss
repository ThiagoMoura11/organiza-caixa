; Inno Setup Script para Organiza Caixa
; https://jrsoftware.org/isinfo.php

#define MyAppName "Organiza Caixa"
#define MyAppVersion "1.0"
#define MyAppPublisher "Organiza Caixa"
#define MyAppURL "https://organizacaixa.com.br"
#define MyAppExeName "OrganizaCaixa.exe"

[Setup]
AppId={{A7B8C9D0-E1F2-3456-7890-ABCDEF123456}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=
OutputDir=Output
OutputBaseFilename=OrganizaCaixa_Instalador
SetupIconFile=
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "src\*"; DestDir: "{app}\src"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "data\*"; DestDir: "{app}\data"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "requirements.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "app.py"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Desinstalar {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
function InitializeSetup(): Boolean;
var
  ResultCode: Integer;
begin
  Result := True;
  
  // Verificar se Python está instalado
  if not FileExists(ExpandConstant('{pf}\Python312\python.exe')) and 
     not FileExists(ExpandConstant('{pf}\Python311\python.exe')) and
     not FileExists(ExpandConstant('{pf}\Python310\python.exe')) and
     not FileExists(ExpandConstant('{pf}\Python39\python.exe')) then
  begin
    if MsgBox('Python não encontrado. Deseja continuar mesmo assim?', mbConfirmation, MB_YESNO) = IDNO then
    begin
      Result := False;
    end;
  end;
end;
