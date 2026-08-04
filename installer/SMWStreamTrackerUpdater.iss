#define AppName "SMW Stream Tracker"
#define AppVersion "1.0.4"
#define AppPublisher "FredDOGG23"
#define AppExeName "SMWStreamTracker.exe"
#ifndef AppExeSource
  #define AppExeSource "..\dist\SMWStreamTracker.exe"
#endif

[Setup]
AppId={{E7C2CB0B-73BC-4DEA-8D78-90B9A3BA9CB6}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} Update {#AppVersion}
AppPublisher={#AppPublisher}
VersionInfoVersion={#AppVersion}.0
VersionInfoCompany={#AppPublisher}
VersionInfoDescription={#AppName} Update
VersionInfoProductName={#AppName}
VersionInfoProductVersion={#AppVersion}
DefaultDirName={localappdata}\Programs\SMW Stream Tracker
UsePreviousAppDir=yes
DisableDirPage=yes
DisableProgramGroupPage=yes
DisableReadyPage=yes
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
OutputDir=..\dist
OutputBaseFilename=SMWStreamTracker_Update_{#AppVersion}
SetupIconFile=..\app_assets\smw_stream_tracker_icon.ico
WizardSmallImageFile=..\app_assets\smw_stream_tracker_icon.png
WizardSmallImageBackColor=#E02C26
WizardStyle=modern dynamic
DisableWelcomePage=no
Uninstallable=no
Compression=lzma2/ultra64
SolidCompression=yes
ArchiveExtraction=full
CloseApplications=yes
RestartApplications=no
MinVersion=10.0.17763
AppMutex=SMWStreamTrackerAppMutex

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "australian"; MessagesFile: "Australian.isl"
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"
Name: "french"; MessagesFile: "compiler:Languages\French.isl"
Name: "german"; MessagesFile: "compiler:Languages\German.isl"
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[CustomMessages]
english.LaunchApp=Launch SMW Stream Tracker
english.NotInstalled1=SMW Stream Tracker is not installed in the expected location.
english.NotInstalled2=Use the complete installer for the first installation, then use this updater for future releases.
english.RollbackFolderError=Setup could not create the rollback folder. The update was stopped safely.
english.RollbackCopyError=Setup could not preserve the current app for rollback. The update was stopped safely.
english.RollbackHashError=Setup could not verify the saved rollback copy. The update was stopped safely.
australian.LaunchApp=Fire up SMW Stream Tracker
australian.NotInstalled1=SMW Stream Tracker is not installed where we expected, mate.
australian.NotInstalled2=Use the complete installer for the first go, then use this updater next time. Too easy.
australian.RollbackFolderError=Could not make the rollback folder. The update pulled up safely.
australian.RollbackCopyError=Could not keep the current app for rollback. The update pulled up safely.
australian.RollbackHashError=Could not verify the saved rollback copy. The update pulled up safely.
spanish.LaunchApp=Iniciar SMW Stream Tracker
spanish.NotInstalled1=SMW Stream Tracker no está instalado en la ubicación esperada.
spanish.NotInstalled2=Usa el instalador completo para la primera instalación y después este actualizador.
spanish.RollbackFolderError=El instalador no pudo crear la carpeta de reversión. La actualización se detuvo de forma segura.
spanish.RollbackCopyError=El instalador no pudo conservar la aplicación actual para revertirla. La actualización se detuvo de forma segura.
spanish.RollbackHashError=El instalador no pudo verificar la copia guardada para la reversión. La actualización se detuvo de forma segura.
french.LaunchApp=Lancer SMW Stream Tracker
french.NotInstalled1=SMW Stream Tracker n'est pas installé à l'emplacement attendu.
french.NotInstalled2=Utilisez d'abord le programme d'installation complet, puis ce programme de mise à jour.
french.RollbackFolderError=Le programme n'a pas pu créer le dossier de restauration. La mise à jour a été arrêtée en toute sécurité.
french.RollbackCopyError=Le programme n'a pas pu conserver l'application actuelle pour la restauration. La mise à jour a été arrêtée en toute sécurité.
french.RollbackHashError=Le programme n'a pas pu vérifier la copie de restauration enregistrée. La mise à jour a été arrêtée en toute sécurité.
german.LaunchApp=SMW Stream Tracker starten
german.NotInstalled1=SMW Stream Tracker ist nicht am erwarteten Ort installiert.
german.NotInstalled2=Verwenden Sie zuerst das vollständige Installationsprogramm und danach diesen Updater.
german.RollbackFolderError=Der Rollback-Ordner konnte nicht erstellt werden. Das Update wurde sicher beendet.
german.RollbackCopyError=Die aktuelle App konnte nicht für den Rollback gesichert werden. Das Update wurde sicher beendet.
german.RollbackHashError=Die gespeicherte Rollback-Kopie konnte nicht überprüft werden. Das Update wurde sicher beendet.
brazilianportuguese.LaunchApp=Iniciar o SMW Stream Tracker
brazilianportuguese.NotInstalled1=O SMW Stream Tracker não está instalado no local esperado.
brazilianportuguese.NotInstalled2=Use o instalador completo na primeira instalação e depois este atualizador.
brazilianportuguese.RollbackFolderError=O instalador não conseguiu criar a pasta de reversão. A atualização foi interrompida com segurança.
brazilianportuguese.RollbackCopyError=O instalador não conseguiu preservar o aplicativo atual para reversão. A atualização foi interrompida com segurança.
brazilianportuguese.RollbackHashError=O instalador não conseguiu verificar a cópia salva para reversão. A atualização foi interrompida com segurança.

[Files]
Source: "{#AppExeSource}"; DestDir: "{app}"; DestName: "{#AppExeName}"; Flags: ignoreversion restartreplace
; Install the SNI-compatible RetroArch core when RetroArch support is used. The app
; automatically selects it only when RetroArch and SNI are the active pair.
Source: "https://buildbot.libretro.com/nightly/windows/x86_64/latest/bsnes_mercury_performance_libretro.dll.zip"; \
  DestName: "bsnes_mercury_performance_libretro.dll.zip"; DestDir: "{app}\Tools\RetroArch\cores"; \
  ExternalSize: 956416; Flags: external download extractarchive recursesubdirs ignoreversion
Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\docs\README.en.txt"; DestDir: "{app}"; DestName: "README.txt"; Flags: ignoreversion; Languages: english
Source: "..\docs\README.au.txt"; DestDir: "{app}"; DestName: "README.txt"; Flags: ignoreversion; Languages: australian
Source: "..\docs\README.es.txt"; DestDir: "{app}"; DestName: "README.txt"; Flags: ignoreversion; Languages: spanish
Source: "..\docs\README.fr.txt"; DestDir: "{app}"; DestName: "README.txt"; Flags: ignoreversion; Languages: french
Source: "..\docs\README.de.txt"; DestDir: "{app}"; DestName: "README.txt"; Flags: ignoreversion; Languages: german
Source: "..\docs\README.pt-BR.txt"; DestDir: "{app}"; DestName: "README.txt"; Flags: ignoreversion; Languages: brazilianportuguese
Source: "..\docs\README.en.txt"; DestDir: "{app}\Documentation"; Flags: ignoreversion
Source: "..\docs\README.au.txt"; DestDir: "{app}\Documentation"; Flags: ignoreversion
Source: "..\docs\README.es.txt"; DestDir: "{app}\Documentation"; Flags: ignoreversion
Source: "..\docs\README.fr.txt"; DestDir: "{app}\Documentation"; Flags: ignoreversion
Source: "..\docs\README.de.txt"; DestDir: "{app}\Documentation"; Flags: ignoreversion
Source: "..\docs\README.pt-BR.txt"; DestDir: "{app}\Documentation"; Flags: ignoreversion
Source: "..\release_tools\rollback_update.ps1"; DestDir: "{app}"; Flags: ignoreversion
Source: "PRIVACY.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "THIRD_PARTY_NOTICE.txt"; DestDir: "{app}"; Flags: ignoreversion

[Run]
Filename: "{app}\{#AppExeName}"; Description: "{cm:LaunchApp}"; \
  Flags: postinstall nowait skipifsilent

[Code]
function PrepareToInstall(var NeedsRestart: Boolean): String;
var
  CurrentExe: String;
  RollbackDir: String;
  PreviousExe: String;
  PreviousHash: String;
  CurrentHash: String;
begin
  Result := '';
  CurrentExe := ExpandConstant('{app}\{#AppExeName}');
  if not FileExists(CurrentExe) then
    Result := ExpandConstant('{cm:NotInstalled1}') + #13#10#13#10 +
      ExpandConstant('{cm:NotInstalled2}')
  else
  begin
    RollbackDir := ExpandConstant('{localappdata}\SMWStreamTracker\Rollback');
    PreviousExe := RollbackDir + '\SMWStreamTracker_previous.exe';
    PreviousHash := RollbackDir + '\SMWStreamTracker_previous.sha256';
    if not ForceDirectories(RollbackDir) then
      Result := ExpandConstant('{cm:RollbackFolderError}')
    else if not CopyFile(CurrentExe, PreviousExe, False) then
      Result := ExpandConstant('{cm:RollbackCopyError}')
    else
    begin
      CurrentHash := GetSHA256OfFile(PreviousExe);
      if (Length(CurrentHash) <> 64) or
         (not SaveStringToFile(PreviousHash, Lowercase(CurrentHash) + #13#10, False)) then
        Result := ExpandConstant('{cm:RollbackHashError}');
    end;
  end;
end;
