; Inno Setup script for the piscout installer.
; Build:  iscc /DMyAppVersion=0.1.8 packaging\installer\piscout.iss   (needs dist\piscout.exe)
; Installs per user (no administrator rights needed), adds a Start menu entry and an optional desktop shortcut,
; and registers an uninstaller under Settings > Apps. Saved logins live in %LOCALAPPDATA%\piscout and are kept.

#ifndef MyAppVersion
  #define MyAppVersion "0.0.0"
#endif
#ifndef SourceExe
  #define SourceExe "..\..\dist\piscout.exe"
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

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Shortcuts:"

[Files]
Source: "{#SourceExe}"; DestDir: "{app}"; DestName: "piscout.exe"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\piscout"; Filename: "{app}\piscout.exe"
Name: "{autodesktop}\piscout"; Filename: "{app}\piscout.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\piscout.exe"; Description: "Start piscout"; Flags: nowait postinstall skipifsilent
