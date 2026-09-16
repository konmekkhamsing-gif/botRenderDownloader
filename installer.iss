#define MyAppName "MapleXD Downloader"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "MapleXD"
#define MyAppExeName "MapleXDDownloader.exe"

[Setup]
AppId={{A2D6A1F2-7BB6-4B45-9FD8-9C0B7A4F5D12}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\MapleXD Downloader
DefaultGroupName={#MyAppName}
OutputDir=installer
OutputBaseFilename=MapleXDDownloader-Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\{#MyAppExeName}
SetupIconFile=MapleXD.ico

[Files]
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "MapleXD.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\MapleXD.ico"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\MapleXD.ico"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "สร้างไอคอนบน Desktop"; GroupDescription: "ตัวเลือกเพิ่มเติม:"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "เปิด {#MyAppName}"; Flags: postinstall nowait skipifsilent
