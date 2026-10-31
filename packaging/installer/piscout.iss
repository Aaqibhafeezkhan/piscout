; Inno Setup script for the piscout installer.
; Build:  python packaging/installer/build_installer.py --version 0.1.8   (needs the dist\piscout folder from build.bat)
; Installs per user (no administrator rights needed), adds a Start menu entry and an optional desktop shortcut,
; and registers an uninstaller under Settings > Apps. Saved logins live in %LOCALAPPDATA%\piscout and are kept.

#ifndef MyAppVersion
  #define MyAppVersion "0.0.0"
#endif
#ifndef SourceDir
  #define SourceDir "..\..\dist\piscout"
#endif

[Setup]
AppId={{6F0B8E52-3C1A-4D8E-9A47-5D2E7B1C94A3}
AppName=piscout
AppVersion={#MyAppVersion}
AppVerName=piscout {#MyAppVersion}
AppPublisher=MilkteaTW1
AppPublisherURL=https://github.com/MilkteaTW1/piscout
AppSupportURL=https://github.com/MilkteaTW1/piscout/issues
AppUpdatesURL=https://github.com/MilkteaTW1/piscout/releases
DefaultDirName={autopf}\piscout
DisableProgramGroupPage=yes
DisableDirPage=auto
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
OutputDir=..\..\dist
OutputBaseFilename=piscout-setup
SetupIconFile=piscout.ico
UninstallDisplayIcon={app}\piscout.exe
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
CloseApplications=yes
RestartApplications=no

; The languages come from piscout\static\locales\*.json (see build_installer.py, which writes generated\languages.iss).
; Setup shows its UI in the language of the user's Windows and falls back to English.
[Languages]
#ifexist "generated\languages.iss"
  #include "generated\languages.iss"
#else
Name: "english"; MessagesFile: "compiler:Default.isl"
#endif

[CustomMessages]
TaskDesktop=Create a &desktop shortcut
TaskGroup=Shortcuts:
RunApp=Start piscout

[Tasks]
Name: "desktopicon"; Description: "{cm:TaskDesktop}"; GroupDescription: "{cm:TaskGroup}"

[Files]
Source: "{#SourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\piscout"; Filename: "{app}\piscout.exe"
Name: "{autodesktop}\piscout"; Filename: "{app}\piscout.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\piscout.exe"; Description: "{cm:RunApp}"; Flags: nowait postinstall skipifsilent
; Started by the in-app updater (it passes /update=1 to the silent installer): reopen the app afterwards.
Filename: "{app}\piscout.exe"; Flags: nowait runasoriginaluser; Check: IsUpdate

[Code]
function IsUpdate: Boolean;
begin
  Result := ExpandConstant('{param:update|0}') = '1';
end;
