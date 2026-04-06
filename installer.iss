; Inno Setup Script for Window Hider
; Requires Inno Setup: https://jrsoftware.org/isinfo.php

#define MyAppName "Window Hider"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Jojosstudio"
#define MyAppURL "https://jojosstudio.github.io/windowhider/"
#define MyAppExeName "Window Hider.exe"

[Setup]
AppId={{A1B2C3D4-E5F6-7890-1234-567890ABCDEF}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes
OutputDir=installer
OutputBaseFilename=WindowHider-Setup
SetupIconFile=icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin

[Languages]
Name: "german"; MessagesFile: "compiler:Languages\German.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\WindowHider.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "hider.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "icon.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\WindowHider.exe"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\WindowHider.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\WindowHider.exe"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}\*"
