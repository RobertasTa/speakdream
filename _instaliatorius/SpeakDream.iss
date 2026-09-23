; SpeakDream - Inno Setup instaliatorius (2026-09-21).
;
; STATYTI PER POWERSHELL, ne per Git Bash (MSYS argumenta "/O..." pavercia keliu):
;   & "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe" "/O$env:TEMP\speakdream_setup" SpeakDream.iss
;   Move-Item "$env:TEMP\speakdream_setup\SpeakDream-1.0.0-setup.exe" ..\dist\
; ⛔ Inno Setup i D: diska rasyti NEGALI ("output file appears to be in use (32)") -
;   seimos pamoka 2026-09-19, receptas `DIKTUOKLE programa\_darbal\daryk_setup_C.bat`.
;
; SPRENDIMAI (paveldeta is Diktuokle.iss ir PhotoHome.iss, dviracio neieskom):
;  - ONEDIR aplankas dist\SpeakDream\ (exe + _internal), ~4,7 GB: torch su CUDA
;    (11 DLL) - butent tai daro programa savarankiska (Roberto sprendimas 09-19).
;  - PrivilegesRequired=lowest -> vartotojo profilis ({localappdata}\Programs\SpeakDream),
;    JOKIO UAC lango. Del to Stenogramos\ SALIA programos yra rasomas katalogas
;    (Program Files be admin butu neleides, ir programa kristu i AppData).
;  - [Dirs] Stenogramos - Roberto sprendimas 09-18: kataloga kuria INSTALIATORIUS,
;    "kad net tuscia galima butu atidaryti". Salinant programa jis NETRINAMAS, jei
;    jame yra failu - stenogramos yra zmogaus dokumentai.
;  - MODELIU PAKETE NERA (Paprika, Whisper, Marian, Piper balsai) - programa juos
;    randa HuggingFace kese arba parsisiuncia pati pirma karta.
;  - PORTABLE VERSIJOS NERA (Roberto sprendimas 09-18: "kad gerai veiktu GPU").
;  - Kalbos LT/EN/RU/DE - TIKSLIAI programos sasajos kalbos (guard Rule 6; FOTO namu
;    pamoka 08-30). Lithuanian.isl - musu pats (296 raktai), kopija is Diktuokles.
;  - AppId GUID FIKSUOTAS - NIEKADA nekeisti (kitaip senos versijos liks salia).
;  - Compression lzma2/ultra64 + LZMANumBlockThreads=2 - PAMATUOTA 2026-09-21:
;    4,9 GB -> 1,895 GiB per ~6 min. Su lzma2/normal + 4 gijos buvo 2,12 GiB per 105 s,
;    bet GitHub Release priima failus TIK iki 2 GiB - todel ultra, ne greitis.
;  - CloseApplications=force (Diktuokles pamoka 09-11): perleidziant setup'a ant
;    veikiancios programos garso gija mandagiai neuzsidaro.

#define AppName      "SpeakDream"
#define AppVersion   "1.0.0"
#define AppExeName   "SpeakDream.exe"
#define AppUrl       "https://github.com/RobertasTa/speakdream"

[Setup]
AppId={{5D2E7C41-9B3F-4A86-8E1D-3C7A2F9B6D14}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher=Robertas & Claude (AI)
AppPublisherURL={#AppUrl}
AppSupportURL={#AppUrl}/issues
AppUpdatesURL={#AppUrl}/releases
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
; OutputDir perrasomas komandines eilutes /O (i D: rasyti negalima, zr. virsuje).
OutputDir=..\dist
OutputBaseFilename={#AppName}-{#AppVersion}-setup
SetupIconFile=..\vertejas\SpeakDream.ico
UninstallDisplayIcon={app}\{#AppExeName}
Compression=lzma2/ultra64
SolidCompression=yes
LZMAUseSeparateProcess=yes
LZMANumBlockThreads=2
WizardStyle=modern
CloseApplications=force

[Languages]
; LIETUVIU PIRMA - tai lietuviska dovana.
Name: "lt"; MessagesFile: "Lithuanian.isl"
Name: "en"; MessagesFile: "compiler:Default.isl"
Name: "ru"; MessagesFile: "compiler:Languages\Russian.isl"
Name: "de"; MessagesFile: "compiler:Languages\German.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Dirs]
; Stenogramos salia programos - kuria instaliatorius (Roberto sprendimas 09-18).
Name: "{app}\Stenogramos"

[Files]
; Visas onedir aplankas: SpeakDream.exe + _internal\ (rekursyviai).
Source: "..\dist\SpeakDream\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExeName}"; Description: "{cm:LaunchProgram,{#AppName}}"; Flags: nowait postinstall skipifsilent

; PASTABA salinant programa: %LOCALAPPDATA%\SpeakDream (nustatymai.json, vertejas.log)
; ir {app}\Stenogramos su failais NETRINAMI - tai zmogaus nustatymai ir dokumentai.
; HuggingFace kesas (modeliai, keli GB) irgi lieka - perdiegus nereikes siustis is naujo.
