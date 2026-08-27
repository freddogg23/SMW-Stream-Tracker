#define AppName "SMW Stream Tracker"
#define AppVersion "2.2.0"
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
WizardImageFile=
WizardSmallImageFile=
WizardStyle=modern dark polar includetitlebar hidebevels
WizardBackColor=#0D1216
WizardSizePercent=130
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
english.StartupCheckFailed=The updated app could not start its window system. Setup restored the previous working version automatically.
australian.LaunchApp=Fire up SMW Stream Tracker
australian.NotInstalled1=SMW Stream Tracker is not installed where we expected, mate.
australian.NotInstalled2=Use the complete installer for the first go, then use this updater next time. Too easy.
australian.RollbackFolderError=Could not make the rollback folder. The update pulled up safely.
australian.RollbackCopyError=Could not keep the current app for rollback. The update pulled up safely.
australian.RollbackHashError=Could not verify the saved rollback copy. The update pulled up safely.
australian.StartupCheckFailed=The updated app could not start its window system. Setup put the previous working version back automatically.
spanish.LaunchApp=Iniciar SMW Stream Tracker
spanish.NotInstalled1=SMW Stream Tracker no está instalado en la ubicación esperada.
spanish.NotInstalled2=Usa el instalador completo para la primera instalación y después este actualizador.
spanish.RollbackFolderError=El instalador no pudo crear la carpeta de reversión. La actualización se detuvo de forma segura.
spanish.RollbackCopyError=El instalador no pudo conservar la aplicación actual para revertirla. La actualización se detuvo de forma segura.
spanish.RollbackHashError=El instalador no pudo verificar la copia guardada para la reversión. La actualización se detuvo de forma segura.
spanish.StartupCheckFailed=La aplicación actualizada no pudo iniciar su sistema de ventanas. El instalador restauró automáticamente la versión anterior que funcionaba.
french.LaunchApp=Lancer SMW Stream Tracker
french.NotInstalled1=SMW Stream Tracker n'est pas installé à l'emplacement attendu.
french.NotInstalled2=Utilisez d'abord le programme d'installation complet, puis ce programme de mise à jour.
french.RollbackFolderError=Le programme n'a pas pu créer le dossier de restauration. La mise à jour a été arrêtée en toute sécurité.
french.RollbackCopyError=Le programme n'a pas pu conserver l'application actuelle pour la restauration. La mise à jour a été arrêtée en toute sécurité.
french.RollbackHashError=Le programme n'a pas pu vérifier la copie de restauration enregistrée. La mise à jour a été arrêtée en toute sécurité.
french.StartupCheckFailed=L'application mise à jour n'a pas pu démarrer son système de fenêtres. Le programme a automatiquement restauré la version précédente fonctionnelle.
german.LaunchApp=SMW Stream Tracker starten
german.NotInstalled1=SMW Stream Tracker ist nicht am erwarteten Ort installiert.
german.NotInstalled2=Verwenden Sie zuerst das vollständige Installationsprogramm und danach diesen Updater.
german.RollbackFolderError=Der Rollback-Ordner konnte nicht erstellt werden. Das Update wurde sicher beendet.
german.RollbackCopyError=Die aktuelle App konnte nicht für den Rollback gesichert werden. Das Update wurde sicher beendet.
german.RollbackHashError=Die gespeicherte Rollback-Kopie konnte nicht überprüft werden. Das Update wurde sicher beendet.
german.StartupCheckFailed=Die aktualisierte App konnte ihr Fenstersystem nicht starten. Das Setup hat die vorherige funktionierende Version automatisch wiederhergestellt.
brazilianportuguese.LaunchApp=Iniciar o SMW Stream Tracker
brazilianportuguese.NotInstalled1=O SMW Stream Tracker não está instalado no local esperado.
brazilianportuguese.NotInstalled2=Use o instalador completo na primeira instalação e depois este atualizador.
brazilianportuguese.RollbackFolderError=O instalador não conseguiu criar a pasta de reversão. A atualização foi interrompida com segurança.
brazilianportuguese.RollbackCopyError=O instalador não conseguiu preservar o aplicativo atual para reversão. A atualização foi interrompida com segurança.
brazilianportuguese.RollbackHashError=O instalador não conseguiu verificar a cópia salva para reversão. A atualização foi interrompida com segurança.
brazilianportuguese.StartupCheckFailed=O aplicativo atualizado não conseguiu iniciar o sistema de janelas. O instalador restaurou automaticamente a versão anterior que funcionava.

[Files]
Source: "smw_installer_banner.png"; Flags: dontcopy noencryption
Source: "{#AppExeSource}"; DestDir: "{app}"; DestName: "{#AppExeName}"; Flags: ignoreversion restartreplace
; Permanent Tcl/Tk fallback used when one-file temporary extraction is blocked.
Source: "..\dist\runtime\tcl\*"; DestDir: "{app}\runtime\tcl"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\dist\runtime\tk\*"; DestDir: "{app}\runtime\tk"; Flags: ignoreversion recursesubdirs createallsubdirs
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

[Code]
var
  UpdatedAppStartupCheckPassed: Boolean;
  UpdaterBanner: TBitmapImage;
  UpdaterFinishMask: TPanel;
  UpdaterFinishRow: TPanel;
  UpdaterFinishBox: TPanel;
  UpdaterFinishTick: TNewStaticText;
  UpdaterFinishLabel: TNewStaticText;
  LaunchUpdatedAppSelected: Boolean;

function UpdaterBackground: TColor;
begin
  Result := StrToColor('#0D1216');
end;

function UpdaterSurface: TColor;
begin
  Result := StrToColor('#11171C');
end;

function UpdaterSurfaceRaised: TColor;
begin
  Result := StrToColor('#182229');
end;

function UpdaterSurfaceSelected: TColor;
begin
  Result := StrToColor('#26323B');
end;

function UpdaterText: TColor;
begin
  Result := StrToColor('#F2F6F8');
end;

function UpdaterMutedText: TColor;
begin
  Result := StrToColor('#9AA7B0');
end;

function UpdaterGreen: TColor;
begin
  Result := StrToColor('#68D996');
end;

procedure ConfigureUpdaterTheme;
var
  BannerFile: String;
  BannerWidth: Integer;
  BannerHeight: Integer;
  MaximumBannerWidth: Integer;
  ContentTop: Integer;
  ContentBottom: Integer;
begin
  WizardForm.Color := UpdaterBackground;
  WizardForm.MainPanel.Color := UpdaterSurface;
  WizardForm.WelcomePage.Color := UpdaterBackground;
  WizardForm.LicensePage.Color := UpdaterBackground;
  WizardForm.InfoBeforePage.Color := UpdaterBackground;
  WizardForm.SelectDirPage.Color := UpdaterBackground;
  WizardForm.SelectProgramGroupPage.Color := UpdaterBackground;
  WizardForm.SelectTasksPage.Color := UpdaterBackground;
  WizardForm.ReadyPage.Color := UpdaterBackground;
  WizardForm.PreparingPage.Color := UpdaterBackground;
  WizardForm.InstallingPage.Color := UpdaterBackground;
  WizardForm.InfoAfterPage.Color := UpdaterBackground;
  WizardForm.FinishedPage.Color := UpdaterBackground;
  WizardForm.PageNameLabel.Font.Color := UpdaterText;
  WizardForm.PageDescriptionLabel.Font.Color := UpdaterMutedText;
  WizardForm.WelcomeLabel1.Font.Color := UpdaterText;
  WizardForm.WelcomeLabel2.Font.Color := UpdaterMutedText;
  WizardForm.FinishedHeadingLabel.Font.Color := UpdaterText;
  WizardForm.FinishedLabel.Font.Color := UpdaterMutedText;
  WizardForm.FinishedHeadingLabel.AutoSize := False;
  WizardForm.FinishedHeadingLabel.Alignment := taCenter;
  WizardForm.FinishedHeadingLabel.Left := ScaleX(24);
  WizardForm.FinishedHeadingLabel.Width :=
    WizardForm.FinishedPage.ClientWidth - ScaleX(48);
  WizardForm.FinishedHeadingLabel.Font.Size := 17;
  WizardForm.FinishedHeadingLabel.AdjustHeight;
  WizardForm.FinishedLabel.AutoSize := False;
  WizardForm.FinishedLabel.Alignment := taCenter;
  WizardForm.FinishedLabel.Left := ScaleX(24);
  WizardForm.FinishedLabel.Width :=
    WizardForm.FinishedPage.ClientWidth - ScaleX(48);
  WizardForm.LicenseMemo.Color := UpdaterSurface;
  WizardForm.LicenseMemo.Font.Color := UpdaterText;
  WizardForm.InfoBeforeMemo.Color := UpdaterSurface;
  WizardForm.InfoBeforeMemo.Font.Color := UpdaterText;
  WizardForm.InfoAfterMemo.Color := UpdaterSurface;
  WizardForm.InfoAfterMemo.Font.Color := UpdaterText;
  WizardForm.ReadyMemo.Color := UpdaterSurface;
  WizardForm.ReadyMemo.Font.Color := UpdaterText;
  WizardForm.PreparingLabel.Font.Color := UpdaterText;
  WizardForm.StatusLabel.Font.Color := UpdaterText;
  WizardForm.FileNameLabel.Font.Color := UpdaterMutedText;
  WizardForm.NextButton.Font.Style := [fsBold];
  WizardForm.BackButton.Font.Style := [fsBold];
  WizardForm.CancelButton.Font.Style := [fsBold];

  BannerFile := ExpandConstant('{tmp}\smw_installer_banner.png');
  ExtractTemporaryFile(ExtractFileName(BannerFile));
  UpdaterBanner := TBitmapImage.Create(WizardForm);
  UpdaterBanner.Parent := WizardForm;
  UpdaterBanner.BackColor := UpdaterBackground;
  UpdaterBanner.Center := True;
  UpdaterBanner.Stretch := True;
  UpdaterBanner.PngImage.LoadFromFile(BannerFile);

  BannerHeight := ScaleY(112);
  BannerWidth := MulDiv(BannerHeight, 1039, 292);
  MaximumBannerWidth := WizardForm.ClientWidth - ScaleX(24);
  if BannerWidth > MaximumBannerWidth then
  begin
    BannerWidth := MaximumBannerWidth;
    BannerHeight := MulDiv(BannerWidth, 292, 1039);
  end;
  UpdaterBanner.Left := (WizardForm.ClientWidth - BannerWidth) div 2;
  UpdaterBanner.Top := ScaleY(10);
  UpdaterBanner.Width := BannerWidth;
  UpdaterBanner.Height := BannerHeight;

  ContentTop := UpdaterBanner.Top + UpdaterBanner.Height + ScaleY(10);
  ContentBottom := WizardForm.NextButton.Top - ScaleY(10);
  WizardForm.OuterNotebook.Left := ScaleX(12);
  WizardForm.OuterNotebook.Top := ContentTop;
  WizardForm.OuterNotebook.Width := WizardForm.ClientWidth - ScaleX(24);
  WizardForm.OuterNotebook.Height := ContentBottom - ContentTop;
  WizardForm.WizardBitmapImage.Visible := False;
  WizardForm.WizardSmallBitmapImage.Visible := False;
end;

procedure RefreshUpdaterFinishRow;
begin
  if LaunchUpdatedAppSelected then
  begin
    UpdaterFinishRow.Color := UpdaterSurfaceSelected;
    UpdaterFinishBox.Color := UpdaterGreen;
    UpdaterFinishTick.Caption := '✓';
    UpdaterFinishLabel.Font.Color := UpdaterText;
  end
  else
  begin
    UpdaterFinishRow.Color := UpdaterSurface;
    UpdaterFinishBox.Color := UpdaterSurfaceRaised;
    UpdaterFinishTick.Caption := '';
    UpdaterFinishLabel.Font.Color := UpdaterMutedText;
  end;
end;

procedure ToggleUpdaterFinishRow(Sender: TObject);
begin
  LaunchUpdatedAppSelected := not LaunchUpdatedAppSelected;
  RefreshUpdaterFinishRow;
end;

procedure HideUpdaterNativeRunList;
begin
  { The updater deliberately has no postinstall [Run] entries.  Hide and }
  { park the unused native host so only the themed launch row can paint. }
  WizardForm.RunList.Visible := False;
  WizardForm.RunList.Enabled := False;
  WizardForm.RunList.Parent := WizardForm;
  WizardForm.RunList.Left := -WizardForm.RunList.Width - ScaleX(64);
  WizardForm.RunList.Top := -WizardForm.RunList.Height - ScaleY(64);
end;

procedure CreateUpdaterFinishRow;
var
  NativeRunLeft: Integer;
  NativeRunTop: Integer;
  NativeRunWidth: Integer;
begin
  NativeRunLeft := WizardForm.RunList.Left;
  NativeRunTop := WizardForm.RunList.Top;
  NativeRunWidth := WizardForm.RunList.Width;

  { Keep an opaque, bounded finish-row host so high-DPI text cannot bleed }
  { into the heading or the Finish button area. }
  UpdaterFinishMask := TPanel.Create(WizardForm);
  UpdaterFinishMask.Parent := WizardForm.FinishedPage;
  UpdaterFinishMask.Left := NativeRunLeft;
  UpdaterFinishMask.Top := NativeRunTop - ScaleY(4);
  UpdaterFinishMask.Width := NativeRunWidth;
  UpdaterFinishMask.Height := ScaleY(70);
  UpdaterFinishMask.Caption := '';
  UpdaterFinishMask.Color := UpdaterBackground;
  UpdaterFinishMask.BevelOuter := bvNone;

  UpdaterFinishRow := TPanel.Create(WizardForm);
  UpdaterFinishRow.Parent := UpdaterFinishMask;
  UpdaterFinishRow.Left := 0;
  UpdaterFinishRow.Top := ScaleY(4);
  UpdaterFinishRow.Width := UpdaterFinishMask.Width;
  UpdaterFinishRow.Height := ScaleY(58);
  UpdaterFinishRow.Caption := '';
  UpdaterFinishRow.BevelOuter := bvNone;
  UpdaterFinishRow.OnClick := @ToggleUpdaterFinishRow;

  UpdaterFinishBox := TPanel.Create(WizardForm);
  UpdaterFinishBox.Parent := UpdaterFinishRow;
  UpdaterFinishBox.Left := ScaleX(12);
  UpdaterFinishBox.Top := (UpdaterFinishRow.Height - ScaleY(26)) div 2;
  UpdaterFinishBox.Width := ScaleX(26);
  UpdaterFinishBox.Height := ScaleY(26);
  UpdaterFinishBox.Caption := '';
  UpdaterFinishBox.BevelOuter := bvNone;
  UpdaterFinishBox.OnClick := @ToggleUpdaterFinishRow;

  UpdaterFinishTick := TNewStaticText.Create(WizardForm);
  UpdaterFinishTick.Parent := UpdaterFinishBox;
  UpdaterFinishTick.Left := 0;
  UpdaterFinishTick.Top := 0;
  UpdaterFinishTick.Width := UpdaterFinishBox.Width;
  UpdaterFinishTick.Height := UpdaterFinishBox.Height;
  UpdaterFinishTick.AutoSize := False;
  UpdaterFinishTick.Alignment := taCenter;
  UpdaterFinishTick.Font.Color := UpdaterBackground;
  UpdaterFinishTick.Font.Style := [fsBold];
  UpdaterFinishTick.OnClick := @ToggleUpdaterFinishRow;

  UpdaterFinishLabel := TNewStaticText.Create(WizardForm);
  UpdaterFinishLabel.Parent := UpdaterFinishRow;
  UpdaterFinishLabel.Left := ScaleX(52);
  UpdaterFinishLabel.Top := (UpdaterFinishRow.Height - ScaleY(30)) div 2;
  UpdaterFinishLabel.Width := UpdaterFinishRow.Width - ScaleX(64);
  UpdaterFinishLabel.Height := ScaleY(30);
  UpdaterFinishLabel.AutoSize := False;
  UpdaterFinishLabel.Caption := ExpandConstant('{cm:LaunchApp}');
  UpdaterFinishLabel.Font.Style := [fsBold];
  UpdaterFinishLabel.OnClick := @ToggleUpdaterFinishRow;

  HideUpdaterNativeRunList;
  RefreshUpdaterFinishRow;
end;

procedure InitializeWizard;
begin
  LaunchUpdatedAppSelected := True;
  ConfigureUpdaterTheme;
  CreateUpdaterFinishRow;
end;

procedure CurPageChanged(CurPageID: Integer);
begin
  if CurPageID = wpFinished then
  begin
    if not UpdatedAppStartupCheckPassed then
      LaunchUpdatedAppSelected := False;
    HideUpdaterNativeRunList;
    UpdaterFinishMask.BringToFront;
    UpdaterFinishRow.BringToFront;
    RefreshUpdaterFinishRow;
  end;
end;

function NextButtonClick(CurPageID: Integer): Boolean;
var
  ResultCode: Integer;
begin
  Result := True;
  if (CurPageID = wpFinished) and
     UpdatedAppStartupCheckPassed and
     LaunchUpdatedAppSelected then
  begin
    ResultCode := -1;
    Exec(
      ExpandConstant('{app}\{#AppExeName}'),
      '',
      ExpandConstant('{app}'),
      SW_SHOWNORMAL,
      ewNoWait,
      ResultCode
    );
  end;
end;

function SetEnvironmentVariable(
  lpName: String;
  lpValue: String
): Boolean;
  external 'SetEnvironmentVariableW@kernel32.dll stdcall';

function InitializeSetup(): Boolean;
begin
  { The updater can be started by the PyInstaller one-file app and inherit
    its temporary _MEI extraction folder.  Force the newly installed app to
    start as an independent process so it never looks for the old python DLL
    after that temporary folder has been removed. }
  SetEnvironmentVariable('PYINSTALLER_RESET_ENVIRONMENT', '1');
  UpdatedAppStartupCheckPassed := False;
  Result := True;
end;

function UpdatedAppPassedStartupCheck(): Boolean;
begin
  Result := UpdatedAppStartupCheckPassed and LaunchUpdatedAppSelected;
end;

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

procedure CurStepChanged(CurStep: TSetupStep);
var
  AppExecutable: String;
  PreviousExecutable: String;
  ResultCode: Integer;
begin
  if CurStep <> ssPostInstall then
    Exit;

  AppExecutable := ExpandConstant('{app}\{#AppExeName}');
  PreviousExecutable := ExpandConstant(
    '{localappdata}\SMWStreamTracker\Rollback\SMWStreamTracker_previous.exe'
  );
  ResultCode := -1;
  UpdatedAppStartupCheckPassed := Exec(
    AppExecutable,
    '--startup-check',
    ExpandConstant('{app}'),
    SW_HIDE,
    ewWaitUntilTerminated,
    ResultCode
  ) and (ResultCode = 0);

  if not UpdatedAppStartupCheckPassed then
  begin
    if FileExists(PreviousExecutable) then
      CopyFile(PreviousExecutable, AppExecutable, False);
    MsgBox(ExpandConstant('{cm:StartupCheckFailed}'), mbError, MB_OK);
  end;
end;
