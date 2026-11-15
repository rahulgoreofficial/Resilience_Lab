; =====================================================================
; RESILIENCE LAB - Inno Setup 7 Configuration Script
; Target: Standalone Single-File Windows Installer (x64)
; =====================================================================

#define MyAppName "RESILIENCE LAB"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "RESILIENCE LAB"
#define MyAppURL "https://github.com/resilience-lab"
#define MyAppExeName "RESILIENCE_LAB.exe"

[Setup]
; Unique application GUID for Windows Add/Remove Programs
AppId={{D37F8E24-5A19-4F91-95A2-1C2DE8BC6A39}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; Support both Per-User (no admin needed) and All-Users installations
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog commandline
DefaultDirName={autopf}\RESILIENCE LAB
DefaultGroupName={#MyAppName}
AllowNoIcons=yes

; Visual presentation
SetupIconFile=assets\app_icon.ico
WizardStyle=modern
WizardSizePercent=105

; Output destination
OutputDir=..\release
OutputBaseFilename=RESILIENCE_LAB_Setup

; Compression configuration for single-file deployment
Compression=lzma2/ultra64
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64compatible
ArchitecturesAllowed=x64compatible

; Uninstaller configuration
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}
CloseApplications=yes
CloseApplicationsFilter=*.exe

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
; Distributable application payload built by PyInstaller
Source: "..\dist\RESILIENCE_LAB\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; Companion execution scripts, main entry point, and readme
Source: "..\packaging\dist_extras\*"; DestDir: "{app}"; Flags: ignoreversion

; Official documentation manuals
Source: "..\release\INSTALLATION_GUIDE.pdf"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\release\USER_MANUAL.pdf"; DestDir: "{app}"; Flags: ignoreversion

; Application icon
Source: "assets\app_icon.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Desktop Shortcuts (Checked by default)
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\app_icon.ico"; Tasks: desktopicon; Comment: "Launch RESILIENCE LAB"
Name: "{autodesktop}\Run RESILIENCE LAB (Batch)"; Filename: "{app}\Run_Resilience_Lab.bat"; IconFilename: "{app}\app_icon.ico"; Tasks: desktopicon; Comment: "Run RESILIENCE LAB with Console Window"

; Start Menu Shortcuts
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\app_icon.ico"; Comment: "Launch RESILIENCE LAB Platform"
Name: "{group}\Run RESILIENCE LAB (Batch)"; Filename: "{app}\Run_Resilience_Lab.bat"; IconFilename: "{app}\app_icon.ico"; Comment: "Run with Visible Console Window"
Name: "{group}\Stop RESILIENCE LAB"; Filename: "{app}\Stop_Resilience_Lab.bat"; IconFilename: "{app}\app_icon.ico"; Comment: "Gracefully terminate running background instance"
Name: "{group}\User Manual (PDF)"; Filename: "{app}\USER_MANUAL.pdf"; Comment: "View Mathematical Resilience Analysis Guide"
Name: "{group}\Installation Guide (PDF)"; Filename: "{app}\INSTALLATION_GUIDE.pdf"; Comment: "View Installation Manual"
Name: "{group}\View Application Logs"; Filename: "{app}\{#MyAppExeName}"; Parameters: "--open-logs"; Comment: "Open application logs directory"
Name: "{group}\Open Database Storage"; Filename: "{app}\{#MyAppExeName}"; Parameters: "--open-data"; Comment: "Open SQLite database storage directory"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"

[Run]
; Launch options after setup finishes
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
Filename: "explorer.exe"; Parameters: """{app}"""; Description: "Open installation directory in File Explorer"; Flags: postinstall skipifsilent

[Code]
// User Data Safety & Retention Logic
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  DataDir: String;
  LogsDir: String;
begin
  if CurUninstallStep = usPostUninstall then
  begin
    DataDir := ExpandConstant('{localappdata}\RESILIENCE LAB\Data');
    LogsDir := ExpandConstant('{localappdata}\RESILIENCE LAB\Logs');

    // Prompt user with explicit choice: Keep or remove data
    if DirExists(DataDir) then
    begin
      if MsgBox('Do you want to delete your saved network databases and simulation history?' + #13#10 + #13#10 +
                '(Selecting "No" will safely preserve your data under: ' + DataDir + ')',
                mbConfirmation, MB_YESNO or MB_DEFBUTTON2) = IDYES then
      begin
        DelTree(DataDir, True, True, True);
        DelTree(LogsDir, True, True, True);
        RemoveDir(ExpandConstant('{localappdata}\RESILIENCE LAB'));
      end;
    end;
  end;
end;
