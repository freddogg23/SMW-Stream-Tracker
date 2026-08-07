#define AppName "SMW Stream Tracker"
#define AppVersion "1.0.5"
#define AppPublisher "FredDOGG23"
#define AppExeName "SMWStreamTracker.exe"
#ifndef AppExeSource
  #define AppExeSource "..\dist\SMWStreamTracker.exe"
#endif
#ifndef SetupOutputDir
  #define SetupOutputDir "..\dist"
#endif
#ifndef SetupOutputBaseFilename
  #define SetupOutputBaseFilename "SMWStreamTracker_Setup_" + AppVersion
#endif

[Setup]
AppId={{E7C2CB0B-73BC-4DEA-8D78-90B9A3BA9CB6}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher={#AppPublisher}
VersionInfoVersion={#AppVersion}.0
VersionInfoCompany={#AppPublisher}
VersionInfoDescription={#AppName} Setup
VersionInfoProductName={#AppName}
VersionInfoProductVersion={#AppVersion}
AppPublisherURL=https://github.com/freddogg23/SMW-Stream-Tracker
AppSupportURL=https://github.com/freddogg23/SMW-Stream-Tracker
AppUpdatesURL=https://github.com/freddogg23/SMW-Stream-Tracker
DefaultDirName={localappdata}\Programs\SMW Stream Tracker
DefaultGroupName=SMW Stream Tracker
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
OutputDir={#SetupOutputDir}
OutputBaseFilename={#SetupOutputBaseFilename}
SetupIconFile=..\app_assets\smw_stream_tracker_icon.ico
WizardSmallImageFile=..\app_assets\smw_stream_tracker_icon.png
WizardSmallImageBackColor=#E02C26
WizardStyle=modern dynamic
DisableWelcomePage=no
UninstallDisplayIcon={app}\{#AppExeName}
Compression=lzma2/ultra64
SolidCompression=yes
ArchiveExtraction=full
CloseApplications=yes
RestartApplications=no
MinVersion=10.0.17763
AppMutex=SMWStreamTrackerAppMutex

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"; InfoBeforeFile: "THIRD_PARTY_NOTICE.txt"
Name: "australian"; MessagesFile: "Australian.isl"; InfoBeforeFile: "THIRD_PARTY_NOTICE.au.txt"
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"; InfoBeforeFile: "THIRD_PARTY_NOTICE.es.txt"
Name: "french"; MessagesFile: "compiler:Languages\French.isl"; InfoBeforeFile: "THIRD_PARTY_NOTICE.fr.txt"
Name: "german"; MessagesFile: "compiler:Languages\German.isl"; InfoBeforeFile: "THIRD_PARTY_NOTICE.de.txt"
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"; InfoBeforeFile: "THIRD_PARTY_NOTICE.pt-BR.txt"

[CustomMessages]
english.GuideName=Complete Setup Guide
english.MarkdownGuideName=Complete Setup README
english.OpenGuide=Open the complete setup guide
english.InstallRetroArch=Install official RetroArch 1.22.2
english.LaunchApp=Launch SMW Stream Tracker
english.DesktopShortcut=Create a &desktop shortcut
english.ShortcutGroup=Shortcuts:
english.PlatformTitle=Choose Your Platform
english.PlatformSubtitle=Which platform should SMW Stream Tracker use first?
english.PlatformDescription=You can switch between FXPAK Pro and RetroArch later from the File menu.
english.FXPAKOption=FXPAK Pro (hardware cartridge)
english.RetroArchOption=RetroArch (Windows emulator)
english.DependencyTitle=Optional Dependencies
english.DependencySubtitle=Select any combination of the tools you want Setup to install.
english.DependencyDescription=SNI is strongly recommended. Leave RetroArch unchecked if it is already installed or you use FXPAK Pro.
english.SNIOption=Install SNI v0.0.103 (strongly recommended for live tracking)
english.QUsbOption=Install QUsb2Snes 2025-10-20 (recommended for FXPAK Pro and SD2SNES users)
english.RetroArchInstallOption=Install RetroArch 1.22.2 and the bsnes-mercury Performance core (skip if already installed or using FXPAK Pro)
english.FolderTitle=Choose Your Tracker Folders
english.FolderSubtitle=Where should ROM hacks and stream text files be stored?
english.FolderDescription=Choose folders now, or leave either field blank and configure it later in Settings.
english.ROMLibrary=Patched ROM library:
english.OBSFolder=OBS / stream text output:
english.ServiceTitle=Existing Connection Service
english.ServiceSubtitle=Select an existing SNI.exe or QUsb2Snes.exe.
english.ServiceDescription=Leave this blank only if you plan to configure the connection later.
english.ServiceExecutable=Connection service executable:
english.RetroLocationTitle=RetroArch Locations
english.RetroLocationSubtitle=Select an existing RetroArch installation, or configure it later.
english.RetroLocationDescription=Both fields intentionally start blank so Setup never displays another user's file locations.
english.RetroExecutable=RetroArch executable:
english.RetroCore=SNES core (optional until downloaded):
english.FXPAKFinalTitle=FXPAK Pro Final Steps
english.FinalSubtitle=Complete these steps after installation:
english.FXPAKStep1=1. Connect the FXPAK Pro USB port to this PC and power on the console.
english.FXPAKStep2=2. Let SNI or QUsb2Snes detect the FXPAK Pro device.
english.FXPAKStep3=3. In SMW Stream Tracker, select File > FXPAK Pro and click Refresh.
english.FXPAKStep4=If the device is not listed, verify its USB driver and USB-compatible firmware.
english.RetroFinalTitle=RetroArch Final Steps
english.RetroFinalSubtitle=Complete these steps in RetroArch after installation:
english.RetroStep1=1. Open Online Updater > Core Downloader and install Nintendo - SNES / SFC (bsnes-mercury Performance).
english.RetroStep2=2. Open Settings > Network and enable Network Commands.
english.RetroStep3=3. Keep the Network Command port at 55355.
english.RetroStep4=4. Launch an SMW ROM, then select File > RetroArch in SMW Stream Tracker.
english.ExistingTitle=Existing Settings Found
english.ExistingSubtitle=Your current tracker settings will be preserved.
english.ExistingDescription=Setup found SMWStreamTrackerConfig.json in your user profile. It will not overwrite that file. New tools are still installed, and their paths can be selected later from Settings.
english.ErrorService=The selected connection-service executable was not found.
english.ErrorRetroExe=The selected RetroArch executable was not found. Select a valid retroarch.exe or clear the field to configure it later.
english.ErrorRetroCore=The selected SNES core was not found. Select a valid Libretro core or clear the field to configure it later.
english.ReadySNI=SNI v0.0.103 (strongly recommended)
english.ReadyQUsb=QUsb2Snes 2025-10-20
english.ReadyRetro=RetroArch 1.22.2 and the bsnes-mercury Performance core
english.ReadyNone=None (configure dependencies later)
english.ReadyPlatform=Initial platform:
english.ReadyDependencies=Selected dependencies:
english.ReadyROMLibrary=Patched ROM library:
english.ReadyOBS=OBS output folder:
english.ExecutableFiles=Executable files
english.AllFiles=All files
english.RetroExecutableFilter=RetroArch executable
english.LibretroCores=Libretro cores
english.DLLFiles=DLL files
english.ConfigWriteError=Could not create the configuration file:

australian.GuideName=Fair Dinkum Setup Guide
australian.MarkdownGuideName=Complete Setup README
australian.OpenGuide=Open the setup yarn
australian.InstallRetroArch=Chuck in official RetroArch 1.22.2
australian.LaunchApp=Fire up SMW Stream Tracker
australian.DesktopShortcut=Pop a shortcut on the &desktop
australian.ShortcutGroup=Handy shortcuts:
australian.PlatformTitle=Pick Your Gear
australian.PlatformSubtitle=What are we running first, mate?
australian.PlatformDescription=No dramas—you can swap between FXPAK Pro and RetroArch later from the File menu.
australian.FXPAKOption=FXPAK Pro (the hardware cart, you beauty)
australian.RetroArchOption=RetroArch (emulator on the Windows box)
australian.DependencyTitle=Optional Bits and Bobs
australian.DependencySubtitle=Pick any combination of tools you want Setup to chuck in.
australian.DependencyDescription=SNI is strongly recommended. Leave RetroArch unticked if it is already installed or you use FXPAK Pro.
australian.SNIOption=Install SNI v0.0.103 (strongly recommended for live tracking)
australian.QUsbOption=Install QUsb2Snes 2025-10-20 (recommended for FXPAK Pro and SD2SNES mates)
australian.RetroArchInstallOption=Install RetroArch 1.22.2 and the bsnes-mercury Performance core (skip it if sorted already or using FXPAK Pro)
australian.FolderTitle=Choose Where the Good Stuff Lives
australian.FolderSubtitle=Where should ROM hacks and stream text files bunk down?
australian.FolderDescription=Choose folders now, or leave either field blank and sort it out later in Settings.
australian.ROMLibrary=Patched ROM library:
australian.OBSFolder=OBS / stream text output:
australian.ServiceTitle=Existing Connection Service
australian.ServiceSubtitle=Point us at an existing SNI.exe or QUsb2Snes.exe.
australian.ServiceDescription=Leave this blank only if you plan to sort out the connection later.
australian.ServiceExecutable=Connection service executable:
australian.RetroLocationTitle=Where RetroArch Lives
australian.RetroLocationSubtitle=Select an existing RetroArch install, or configure it later.
australian.RetroLocationDescription=Both fields start blank on purpose, so Setup never shows some other cobber's file locations.
australian.RetroExecutable=RetroArch executable:
australian.RetroCore=SNES core (optional until downloaded):
australian.FXPAKFinalTitle=FXPAK Pro—Nearly There
australian.FinalSubtitle=Knock over these steps after installation:
australian.FXPAKStep1=1. Connect the FXPAK Pro USB port to this PC and power on the console.
australian.FXPAKStep2=2. Let SNI or QUsb2Snes spot the FXPAK Pro device.
australian.FXPAKStep3=3. In SMW Stream Tracker, select File > FXPAK Pro and give Refresh a burl.
australian.FXPAKStep4=If the device goes walkabout, check its USB driver and USB-compatible firmware.
australian.RetroFinalTitle=RetroArch—Nearly There
australian.RetroFinalSubtitle=Knock over these steps in RetroArch after installation:
australian.RetroStep1=1. Open Online Updater > Core Downloader and install Nintendo - SNES / SFC (bsnes-mercury Performance).
australian.RetroStep2=2. Open Settings > Network and switch on Network Commands.
australian.RetroStep3=3. Leave the Network Command port at 55355.
australian.RetroStep4=4. Launch an SMW ROM, then select File > RetroArch in SMW Stream Tracker. Too easy.
australian.ExistingTitle=Found Your Existing Settings
australian.ExistingSubtitle=Your current tracker settings are staying right where they are.
australian.ExistingDescription=Setup found SMWStreamTrackerConfig.json in your user profile. It will not stomp on that file. New tools still get installed, and you can pick their paths later in Settings.
australian.ErrorService=Could not find that connection-service executable, mate.
australian.ErrorRetroExe=Could not find that RetroArch executable. Pick a valid retroarch.exe or clear the field and sort it later.
australian.ErrorRetroCore=Could not find that SNES core. Pick a valid Libretro core or clear the field and sort it later.
australian.ReadySNI=SNI v0.0.103 (strongly recommended)
australian.ReadyQUsb=QUsb2Snes 2025-10-20
australian.ReadyRetro=RetroArch 1.22.2 and the bsnes-mercury Performance core
australian.ReadyNone=None yet (sort out dependencies later)
australian.ReadyPlatform=First cab off the rank:
australian.ReadyDependencies=Selected bits and bobs:
australian.ReadyROMLibrary=Patched ROM library:
australian.ReadyOBS=OBS output folder:
australian.ExecutableFiles=Executable files
australian.AllFiles=All files
australian.RetroExecutableFilter=RetroArch executable
australian.LibretroCores=Libretro cores
australian.DLLFiles=DLL files
australian.ConfigWriteError=Could not create the configuration file:

spanish.GuideName=Guía completa de configuración
spanish.MarkdownGuideName=README completo de configuración
spanish.OpenGuide=Abrir la guía completa de configuración
spanish.InstallRetroArch=Instalar RetroArch 1.22.2 oficial
spanish.LaunchApp=Iniciar SMW Stream Tracker
spanish.DesktopShortcut=Crear un acceso directo en el &escritorio
spanish.ShortcutGroup=Accesos directos:
spanish.PlatformTitle=Elija su plataforma
spanish.PlatformSubtitle=¿Qué plataforma debe usar primero SMW Stream Tracker?
spanish.PlatformDescription=Puede cambiar entre FXPAK Pro y RetroArch más tarde desde el menú Archivo.
spanish.FXPAKOption=FXPAK Pro (cartucho físico)
spanish.RetroArchOption=RetroArch (emulador de Windows)
spanish.DependencyTitle=Dependencias opcionales
spanish.DependencySubtitle=Seleccione cualquier combinación de herramientas que desee instalar.
spanish.DependencyDescription=SNI es muy recomendado. No seleccione RetroArch si ya está instalado o si usa FXPAK Pro.
spanish.SNIOption=Instalar SNI v0.0.103 (muy recomendado para el seguimiento en vivo)
spanish.QUsbOption=Instalar QUsb2Snes 2025-10-20 (recomendado para FXPAK Pro y SD2SNES)
spanish.RetroArchInstallOption=Instalar RetroArch 1.22.2 y el núcleo bsnes-mercury Performance (omitir si ya está instalado o usa FXPAK Pro)
spanish.FolderTitle=Elija las carpetas del rastreador
spanish.FolderSubtitle=¿Dónde se guardarán los ROM hacks y los archivos de texto para streaming?
spanish.FolderDescription=Elija las carpetas ahora o deje los campos vacíos para configurarlos más tarde.
spanish.ROMLibrary=Biblioteca de ROM parcheadas:
spanish.OBSFolder=Salida de texto para OBS / streaming:
spanish.ServiceTitle=Servicio de conexión existente
spanish.ServiceSubtitle=Seleccione un SNI.exe o QUsb2Snes.exe existente.
spanish.ServiceDescription=Déjelo vacío solo si configurará la conexión más tarde.
spanish.ServiceExecutable=Ejecutable del servicio de conexión:
spanish.RetroLocationTitle=Ubicaciones de RetroArch
spanish.RetroLocationSubtitle=Seleccione una instalación de RetroArch existente o configúrela más tarde.
spanish.RetroLocationDescription=Los campos empiezan vacíos para no mostrar las rutas de archivos de otro usuario.
spanish.RetroExecutable=Ejecutable de RetroArch:
spanish.RetroCore=Núcleo SNES (opcional hasta descargarlo):
spanish.FXPAKFinalTitle=Pasos finales de FXPAK Pro
spanish.FinalSubtitle=Complete estos pasos después de la instalación:
spanish.FXPAKStep1=1. Conecte el puerto USB de FXPAK Pro a este PC y encienda la consola.
spanish.FXPAKStep2=2. Permita que SNI o QUsb2Snes detecte el dispositivo FXPAK Pro.
spanish.FXPAKStep3=3. En SMW Stream Tracker, seleccione Archivo > FXPAK Pro y pulse Actualizar.
spanish.FXPAKStep4=Si el dispositivo no aparece, compruebe el controlador USB y el firmware compatible.
spanish.RetroFinalTitle=Pasos finales de RetroArch
spanish.RetroFinalSubtitle=Complete estos pasos en RetroArch después de la instalación:
spanish.RetroStep1=1. Abra Actualizador en línea > Descargador de núcleos e instale Nintendo - SNES / SFC (bsnes-mercury Performance).
spanish.RetroStep2=2. Abra Ajustes > Red y active Comandos de red.
spanish.RetroStep3=3. Mantenga el puerto de comandos de red en 55355.
spanish.RetroStep4=4. Inicie una ROM de SMW y seleccione Archivo > RetroArch en SMW Stream Tracker.
spanish.ExistingTitle=Se encontró una configuración existente
spanish.ExistingSubtitle=Se conservará la configuración actual del rastreador.
spanish.ExistingDescription=El instalador encontró SMWStreamTrackerConfig.json en su perfil y no lo sobrescribirá. Puede seleccionar las rutas de las nuevas herramientas más tarde.
spanish.ErrorService=No se encontró el ejecutable del servicio de conexión seleccionado.
spanish.ErrorRetroExe=No se encontró el ejecutable de RetroArch. Seleccione un retroarch.exe válido o borre el campo.
spanish.ErrorRetroCore=No se encontró el núcleo SNES. Seleccione un núcleo Libretro válido o borre el campo.
spanish.ReadySNI=SNI v0.0.103 (muy recomendado)
spanish.ReadyQUsb=QUsb2Snes 2025-10-20
spanish.ReadyRetro=RetroArch 1.22.2 y el núcleo bsnes-mercury Performance
spanish.ReadyNone=Ninguna (configurar las dependencias más tarde)
spanish.ReadyPlatform=Plataforma inicial:
spanish.ReadyDependencies=Dependencias seleccionadas:
spanish.ReadyROMLibrary=Biblioteca de ROM parcheadas:
spanish.ReadyOBS=Carpeta de salida de OBS:
spanish.ExecutableFiles=Archivos ejecutables
spanish.AllFiles=Todos los archivos
spanish.RetroExecutableFilter=Ejecutable de RetroArch
spanish.LibretroCores=Núcleos Libretro
spanish.DLLFiles=Archivos DLL
spanish.ConfigWriteError=No se pudo crear el archivo de configuración:

french.GuideName=Guide complet de configuration
french.MarkdownGuideName=README complet de configuration
french.OpenGuide=Ouvrir le guide complet de configuration
french.InstallRetroArch=Installer RetroArch 1.22.2 officiel
french.LaunchApp=Lancer SMW Stream Tracker
french.DesktopShortcut=Créer un raccourci sur le &Bureau
french.ShortcutGroup=Raccourcis :
french.PlatformTitle=Choisissez votre plateforme
french.PlatformSubtitle=Quelle plateforme SMW Stream Tracker doit-il utiliser en premier ?
french.PlatformDescription=Vous pourrez basculer entre FXPAK Pro et RetroArch plus tard depuis le menu Fichier.
french.FXPAKOption=FXPAK Pro (cartouche matérielle)
french.RetroArchOption=RetroArch (émulateur Windows)
french.DependencyTitle=Dépendances facultatives
french.DependencySubtitle=Sélectionnez les outils que le programme d'installation doit installer.
french.DependencyDescription=SNI est fortement recommandé. Décochez RetroArch s'il est déjà installé ou si vous utilisez FXPAK Pro.
french.SNIOption=Installer SNI v0.0.103 (fortement recommandé pour le suivi en direct)
french.QUsbOption=Installer QUsb2Snes 2025-10-20 (recommandé pour FXPAK Pro et SD2SNES)
french.RetroArchInstallOption=Installer RetroArch 1.22.2 et le cœur bsnes-mercury Performance (ignorer s'il est déjà installé ou avec FXPAK Pro)
french.FolderTitle=Choisissez les dossiers du tracker
french.FolderSubtitle=Où stocker les ROM hacks et les fichiers texte du stream ?
french.FolderDescription=Choisissez les dossiers maintenant ou laissez les champs vides pour les configurer plus tard.
french.ROMLibrary=Bibliothèque de ROM patchées :
french.OBSFolder=Sortie texte OBS / stream :
french.ServiceTitle=Service de connexion existant
french.ServiceSubtitle=Sélectionnez un SNI.exe ou QUsb2Snes.exe existant.
french.ServiceDescription=Laissez ce champ vide uniquement si vous configurerez la connexion plus tard.
french.ServiceExecutable=Exécutable du service de connexion :
french.RetroLocationTitle=Emplacements RetroArch
french.RetroLocationSubtitle=Sélectionnez une installation RetroArch existante ou configurez-la plus tard.
french.RetroLocationDescription=Les champs sont vides afin de ne jamais afficher les chemins d'un autre utilisateur.
french.RetroExecutable=Exécutable RetroArch :
french.RetroCore=Cœur SNES (facultatif jusqu'au téléchargement) :
french.FXPAKFinalTitle=Étapes finales FXPAK Pro
french.FinalSubtitle=Effectuez ces étapes après l'installation :
french.FXPAKStep1=1. Connectez le port USB du FXPAK Pro à ce PC et allumez la console.
french.FXPAKStep2=2. Laissez SNI ou QUsb2Snes détecter le FXPAK Pro.
french.FXPAKStep3=3. Dans SMW Stream Tracker, choisissez Fichier > FXPAK Pro puis Actualiser.
french.FXPAKStep4=Si l'appareil n'apparaît pas, vérifiez le pilote USB et le micrologiciel compatible.
french.RetroFinalTitle=Étapes finales RetroArch
french.RetroFinalSubtitle=Effectuez ces étapes dans RetroArch après l'installation :
french.RetroStep1=1. Ouvrez Mise à jour en ligne > Téléchargeur de cœurs et installez Nintendo - SNES / SFC (bsnes-mercury Performance).
french.RetroStep2=2. Ouvrez Paramètres > Réseau et activez les commandes réseau.
french.RetroStep3=3. Conservez le port des commandes réseau sur 55355.
french.RetroStep4=4. Lancez une ROM SMW, puis choisissez Fichier > RetroArch dans SMW Stream Tracker.
french.ExistingTitle=Paramètres existants détectés
french.ExistingSubtitle=Vos paramètres actuels seront conservés.
french.ExistingDescription=Le programme a trouvé SMWStreamTrackerConfig.json dans votre profil et ne l'écrasera pas. Les chemins des nouveaux outils pourront être choisis plus tard.
french.ErrorService=L'exécutable du service de connexion sélectionné est introuvable.
french.ErrorRetroExe=L'exécutable RetroArch est introuvable. Sélectionnez un retroarch.exe valide ou videz le champ.
french.ErrorRetroCore=Le cœur SNES est introuvable. Sélectionnez un cœur Libretro valide ou videz le champ.
french.ReadySNI=SNI v0.0.103 (fortement recommandé)
french.ReadyQUsb=QUsb2Snes 2025-10-20
french.ReadyRetro=RetroArch 1.22.2 et le cœur bsnes-mercury Performance
french.ReadyNone=Aucune (configurer les dépendances plus tard)
french.ReadyPlatform=Plateforme initiale :
french.ReadyDependencies=Dépendances sélectionnées :
french.ReadyROMLibrary=Bibliothèque de ROM patchées :
french.ReadyOBS=Dossier de sortie OBS :
french.ExecutableFiles=Fichiers exécutables
french.AllFiles=Tous les fichiers
french.RetroExecutableFilter=Exécutable RetroArch
french.LibretroCores=Cœurs Libretro
french.DLLFiles=Fichiers DLL
french.ConfigWriteError=Impossible de créer le fichier de configuration :

german.GuideName=Vollständige Einrichtungsanleitung
german.MarkdownGuideName=Vollständige Setup-README
german.OpenGuide=Vollständige Einrichtungsanleitung öffnen
german.InstallRetroArch=Offizielles RetroArch 1.22.2 installieren
german.LaunchApp=SMW Stream Tracker starten
german.DesktopShortcut=&Desktop-Verknüpfung erstellen
german.ShortcutGroup=Verknüpfungen:
german.PlatformTitle=Plattform auswählen
german.PlatformSubtitle=Welche Plattform soll SMW Stream Tracker zuerst verwenden?
german.PlatformDescription=Sie können später im Datei-Menü zwischen FXPAK Pro und RetroArch wechseln.
german.FXPAKOption=FXPAK Pro (Hardware-Modul)
german.RetroArchOption=RetroArch (Windows-Emulator)
german.DependencyTitle=Optionale Abhängigkeiten
german.DependencySubtitle=Wählen Sie beliebige Tools aus, die Setup installieren soll.
german.DependencyDescription=SNI wird dringend empfohlen. Deaktivieren Sie RetroArch, wenn es bereits installiert ist oder Sie FXPAK Pro verwenden.
german.SNIOption=SNI v0.0.103 installieren (für Live-Tracking dringend empfohlen)
german.QUsbOption=QUsb2Snes 2025-10-20 installieren (für FXPAK Pro und SD2SNES empfohlen)
german.RetroArchInstallOption=RetroArch 1.22.2 und bsnes-mercury Performance-Core installieren (überspringen, wenn bereits installiert oder bei FXPAK Pro)
german.FolderTitle=Tracker-Ordner auswählen
german.FolderSubtitle=Wo sollen ROM-Hacks und Stream-Textdateien gespeichert werden?
german.FolderDescription=Wählen Sie jetzt Ordner oder lassen Sie Felder leer, um sie später zu konfigurieren.
german.ROMLibrary=Bibliothek gepatchter ROMs:
german.OBSFolder=OBS-/Stream-Textausgabe:
german.ServiceTitle=Vorhandener Verbindungsdienst
german.ServiceSubtitle=Wählen Sie eine vorhandene SNI.exe oder QUsb2Snes.exe.
german.ServiceDescription=Lassen Sie das Feld nur leer, wenn Sie die Verbindung später konfigurieren.
german.ServiceExecutable=Programmdatei des Verbindungsdienstes:
german.RetroLocationTitle=RetroArch-Speicherorte
german.RetroLocationSubtitle=Wählen Sie eine vorhandene RetroArch-Installation oder konfigurieren Sie sie später.
german.RetroLocationDescription=Die Felder sind absichtlich leer, damit niemals Dateipfade eines anderen Benutzers angezeigt werden.
german.RetroExecutable=RetroArch-Programmdatei:
german.RetroCore=SNES-Core (bis zum Download optional):
german.FXPAKFinalTitle=Letzte Schritte für FXPAK Pro
german.FinalSubtitle=Führen Sie nach der Installation diese Schritte aus:
german.FXPAKStep1=1. Verbinden Sie den USB-Port des FXPAK Pro mit diesem PC und schalten Sie die Konsole ein.
german.FXPAKStep2=2. Lassen Sie SNI oder QUsb2Snes das FXPAK-Pro-Gerät erkennen.
german.FXPAKStep3=3. Wählen Sie in SMW Stream Tracker Datei > FXPAK Pro und klicken Sie auf Aktualisieren.
german.FXPAKStep4=Wenn das Gerät nicht erscheint, prüfen Sie USB-Treiber und kompatible Firmware.
german.RetroFinalTitle=Letzte Schritte für RetroArch
german.RetroFinalSubtitle=Führen Sie nach der Installation diese Schritte in RetroArch aus:
german.RetroStep1=1. Öffnen Sie Online-Updater > Core-Downloader und installieren Sie Nintendo - SNES / SFC (bsnes-mercury Performance).
german.RetroStep2=2. Öffnen Sie Einstellungen > Netzwerk und aktivieren Sie Netzwerkbefehle.
german.RetroStep3=3. Behalten Sie für Netzwerkbefehle Port 55355 bei.
german.RetroStep4=4. Starten Sie ein SMW-ROM und wählen Sie Datei > RetroArch in SMW Stream Tracker.
german.ExistingTitle=Vorhandene Einstellungen gefunden
german.ExistingSubtitle=Ihre aktuellen Tracker-Einstellungen bleiben erhalten.
german.ExistingDescription=Setup hat SMWStreamTrackerConfig.json in Ihrem Benutzerprofil gefunden und überschreibt die Datei nicht. Neue Tool-Pfade können später ausgewählt werden.
german.ErrorService=Die ausgewählte Programmdatei des Verbindungsdienstes wurde nicht gefunden.
german.ErrorRetroExe=Die ausgewählte RetroArch-Programmdatei wurde nicht gefunden. Wählen Sie eine gültige retroarch.exe oder leeren Sie das Feld.
german.ErrorRetroCore=Der SNES-Core wurde nicht gefunden. Wählen Sie einen gültigen Libretro-Core oder leeren Sie das Feld.
german.ReadySNI=SNI v0.0.103 (dringend empfohlen)
german.ReadyQUsb=QUsb2Snes 2025-10-20
german.ReadyRetro=RetroArch 1.22.2 und bsnes-mercury Performance-Core
german.ReadyNone=Keine (Abhängigkeiten später konfigurieren)
german.ReadyPlatform=Anfängliche Plattform:
german.ReadyDependencies=Ausgewählte Abhängigkeiten:
german.ReadyROMLibrary=Bibliothek gepatchter ROMs:
german.ReadyOBS=OBS-Ausgabeordner:
german.ExecutableFiles=Ausführbare Dateien
german.AllFiles=Alle Dateien
german.RetroExecutableFilter=RetroArch-Programmdatei
german.LibretroCores=Libretro-Cores
german.DLLFiles=DLL-Dateien
german.ConfigWriteError=Die Konfigurationsdatei konnte nicht erstellt werden:

brazilianportuguese.GuideName=Guia completo de configuração
brazilianportuguese.MarkdownGuideName=README completo de configuração
brazilianportuguese.OpenGuide=Abrir o guia completo de configuração
brazilianportuguese.InstallRetroArch=Instalar o RetroArch 1.22.2 oficial
brazilianportuguese.LaunchApp=Iniciar o SMW Stream Tracker
brazilianportuguese.DesktopShortcut=Criar atalho na área de &trabalho
brazilianportuguese.ShortcutGroup=Atalhos:
brazilianportuguese.PlatformTitle=Escolha sua plataforma
brazilianportuguese.PlatformSubtitle=Qual plataforma o SMW Stream Tracker deve usar primeiro?
brazilianportuguese.PlatformDescription=Você poderá alternar entre FXPAK Pro e RetroArch mais tarde no menu Arquivo.
brazilianportuguese.FXPAKOption=FXPAK Pro (cartucho físico)
brazilianportuguese.RetroArchOption=RetroArch (emulador do Windows)
brazilianportuguese.DependencyTitle=Dependências opcionais
brazilianportuguese.DependencySubtitle=Selecione qualquer combinação de ferramentas para instalar.
brazilianportuguese.DependencyDescription=SNI é altamente recomendado. Desmarque RetroArch se ele já estiver instalado ou se você usa FXPAK Pro.
brazilianportuguese.SNIOption=Instalar SNI v0.0.103 (altamente recomendado para rastreamento ao vivo)
brazilianportuguese.QUsbOption=Instalar QUsb2Snes 2025-10-20 (recomendado para FXPAK Pro e SD2SNES)
brazilianportuguese.RetroArchInstallOption=Instalar RetroArch 1.22.2 e o núcleo bsnes-mercury Performance (ignore se já estiver instalado ou se usar FXPAK Pro)
brazilianportuguese.FolderTitle=Escolha as pastas do tracker
brazilianportuguese.FolderSubtitle=Onde os ROM hacks e arquivos de texto da transmissão serão armazenados?
brazilianportuguese.FolderDescription=Escolha as pastas agora ou deixe os campos vazios para configurar depois.
brazilianportuguese.ROMLibrary=Biblioteca de ROMs com patch:
brazilianportuguese.OBSFolder=Saída de texto do OBS / transmissão:
brazilianportuguese.ServiceTitle=Serviço de conexão existente
brazilianportuguese.ServiceSubtitle=Selecione um SNI.exe ou QUsb2Snes.exe existente.
brazilianportuguese.ServiceDescription=Deixe vazio somente se pretende configurar a conexão depois.
brazilianportuguese.ServiceExecutable=Executável do serviço de conexão:
brazilianportuguese.RetroLocationTitle=Locais do RetroArch
brazilianportuguese.RetroLocationSubtitle=Selecione uma instalação existente do RetroArch ou configure depois.
brazilianportuguese.RetroLocationDescription=Os campos começam vazios para nunca mostrar caminhos de arquivos de outro usuário.
brazilianportuguese.RetroExecutable=Executável do RetroArch:
brazilianportuguese.RetroCore=Núcleo SNES (opcional até ser baixado):
brazilianportuguese.FXPAKFinalTitle=Etapas finais do FXPAK Pro
brazilianportuguese.FinalSubtitle=Conclua estas etapas depois da instalação:
brazilianportuguese.FXPAKStep1=1. Conecte a porta USB do FXPAK Pro a este PC e ligue o console.
brazilianportuguese.FXPAKStep2=2. Deixe o SNI ou QUsb2Snes detectar o dispositivo FXPAK Pro.
brazilianportuguese.FXPAKStep3=3. No SMW Stream Tracker, selecione Arquivo > FXPAK Pro e clique em Atualizar.
brazilianportuguese.FXPAKStep4=Se o dispositivo não aparecer, verifique o driver USB e o firmware compatível.
brazilianportuguese.RetroFinalTitle=Etapas finais do RetroArch
brazilianportuguese.RetroFinalSubtitle=Conclua estas etapas no RetroArch depois da instalação:
brazilianportuguese.RetroStep1=1. Abra Atualizador Online > Baixador de Núcleos e instale Nintendo - SNES / SFC (bsnes-mercury Performance).
brazilianportuguese.RetroStep2=2. Abra Configurações > Rede e habilite Comandos de Rede.
brazilianportuguese.RetroStep3=3. Mantenha a porta de comandos de rede em 55355.
brazilianportuguese.RetroStep4=4. Inicie uma ROM do SMW e selecione Arquivo > RetroArch no SMW Stream Tracker.
brazilianportuguese.ExistingTitle=Configurações existentes encontradas
brazilianportuguese.ExistingSubtitle=Suas configurações atuais serão preservadas.
brazilianportuguese.ExistingDescription=O instalador encontrou SMWStreamTrackerConfig.json no seu perfil e não substituirá o arquivo. Os caminhos das novas ferramentas podem ser escolhidos depois.
brazilianportuguese.ErrorService=O executável do serviço de conexão selecionado não foi encontrado.
brazilianportuguese.ErrorRetroExe=O executável do RetroArch não foi encontrado. Selecione um retroarch.exe válido ou limpe o campo.
brazilianportuguese.ErrorRetroCore=O núcleo SNES não foi encontrado. Selecione um núcleo Libretro válido ou limpe o campo.
brazilianportuguese.ReadySNI=SNI v0.0.103 (altamente recomendado)
brazilianportuguese.ReadyQUsb=QUsb2Snes 2025-10-20
brazilianportuguese.ReadyRetro=RetroArch 1.22.2 e o núcleo bsnes-mercury Performance
brazilianportuguese.ReadyNone=Nenhuma (configurar dependências depois)
brazilianportuguese.ReadyPlatform=Plataforma inicial:
brazilianportuguese.ReadyDependencies=Dependências selecionadas:
brazilianportuguese.ReadyROMLibrary=Biblioteca de ROMs com patch:
brazilianportuguese.ReadyOBS=Pasta de saída do OBS:
brazilianportuguese.ExecutableFiles=Arquivos executáveis
brazilianportuguese.AllFiles=Todos os arquivos
brazilianportuguese.RetroExecutableFilter=Executável do RetroArch
brazilianportuguese.LibretroCores=Núcleos Libretro
brazilianportuguese.DLLFiles=Arquivos DLL
brazilianportuguese.ConfigWriteError=Não foi possível criar o arquivo de configuração:

[Files]
Source: "{#AppExeSource}"; DestDir: "{app}"; DestName: "{#AppExeName}"; Flags: ignoreversion
; Keep Tcl/Tk scripts outside the one-file temporary extraction directory as a
; stable fallback for systems whose security software interrupts _MEI startup.
Source: "..\dist\runtime\tcl\*"; DestDir: "{app}\runtime\tcl"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\dist\runtime\tk\*"; DestDir: "{app}\runtime\tk"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\docs\README.en.txt"; DestDir: "{app}"; DestName: "README.txt"; Flags: ignoreversion isreadme; Languages: english
Source: "..\docs\README.au.txt"; DestDir: "{app}"; DestName: "README.txt"; Flags: ignoreversion isreadme; Languages: australian
Source: "..\docs\README.es.txt"; DestDir: "{app}"; DestName: "README.txt"; Flags: ignoreversion isreadme; Languages: spanish
Source: "..\docs\README.fr.txt"; DestDir: "{app}"; DestName: "README.txt"; Flags: ignoreversion isreadme; Languages: french
Source: "..\docs\README.de.txt"; DestDir: "{app}"; DestName: "README.txt"; Flags: ignoreversion isreadme; Languages: german
Source: "..\docs\README.pt-BR.txt"; DestDir: "{app}"; DestName: "README.txt"; Flags: ignoreversion isreadme; Languages: brazilianportuguese
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

; Recommended live-tracking bridge. Fixed release URLs and official SHA-256
; values keep dependency installs repeatable and reject corrupted downloads.
Source: "https://github.com/alttpo/sni/releases/download/v0.0.103/sni-v0.0.103-windows-amd64.zip"; \
  DestName: "sni-v0.0.103-windows-amd64.zip"; DestDir: "{app}\Tools\SNI"; \
  Hash: "4c0885769518c8b6ed7db038a29fdbdaf28b64c3b54689a5b2e0d6dd33074f87"; \
  ExternalSize: 13307359; Flags: external download extractarchive recursesubdirs ignoreversion; \
  Check: ShouldInstallSNI

; Advanced legacy bridge alternative.
Source: "https://github.com/usb2snes/usb2snes/releases/download/2025-10-20/QUsb2Snes-bundle-2025-10-20.7z"; \
  DestName: "QUsb2Snes-bundle-2025-10-20.7z"; DestDir: "{app}\Tools\QUsb2Snes"; \
  Hash: "104c4a01454d4a5e46998b0ddecf3f95ece71853c614e9e906c287f77de9806f"; \
  ExternalSize: 70505572; Flags: external download extractarchive recursesubdirs ignoreversion; \
  Check: ShouldInstallQUsb

; The official RetroArch installer is downloaded only when selected. Its own
; installer remains visible so the user can review and accept its choices.
Source: "https://buildbot.libretro.com/stable/1.22.2/windows/x86_64/RetroArch-Win64-setup.exe"; \
  DestName: "RetroArch-Win64-setup.exe"; DestDir: "{tmp}"; ExternalSize: 209037907; \
  Flags: external download ignoreversion deleteafterinstall; Check: ShouldInstallRetroArch

; The official current bsnes-mercury Performance core is small enough to install directly, which
; removes the most common missing-core first-run error.
Source: "https://buildbot.libretro.com/nightly/windows/x86_64/latest/bsnes_mercury_performance_libretro.dll.zip"; \
  DestName: "bsnes_mercury_performance_libretro.dll.zip"; DestDir: "{code:RetroArchCoreDirectory}"; \
  ExternalSize: 956416; Flags: external download extractarchive recursesubdirs ignoreversion; \
  Check: ShouldInstallRetroArchCore

[Icons]
Name: "{group}\SMW Stream Tracker"; Filename: "{app}\{#AppExeName}"
Name: "{group}\{cm:GuideName}"; Filename: "{app}\README.txt"
Name: "{group}\{cm:MarkdownGuideName}"; Filename: "{app}\README.md"
Name: "{autodesktop}\SMW Stream Tracker"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "{cm:DesktopShortcut}"; GroupDescription: "{cm:ShortcutGroup}"; Flags: unchecked

[Run]
Filename: "{tmp}\RetroArch-Win64-setup.exe"; Description: "{cm:InstallRetroArch}"; \
  Verb: "runas"; Flags: shellexec waituntilterminated; Check: ShouldInstallRetroArch
Filename: "{app}\README.txt"; Description: "{cm:OpenGuide}"; \
  Flags: postinstall shellexec skipifsilent unchecked
Filename: "{app}\{#AppExeName}"; Description: "{cm:LaunchApp}"; \
  Flags: postinstall nowait skipifsilent

[Code]
var
  PlatformPage: TInputOptionWizardPage;
  DependencyPage: TInputOptionWizardPage;
  FolderPage: TInputDirWizardPage;
  ExistingInterfacePage: TInputFileWizardPage;
  RetroArchPage: TInputFileWizardPage;
  FXPAKStepsPage: TOutputMsgWizardPage;
  RetroArchStepsPage: TOutputMsgWizardPage;
  ExistingConfigPage: TOutputMsgWizardPage;

function ConfigFilePath: String;
begin
  Result := ExpandConstant('{%USERPROFILE}\SMWStreamTrackerConfig.json');
end;

function PickerInitialDirectory(CurrentValue: String): String;
begin
  Result := '';
  CurrentValue := Trim(CurrentValue);
  if CurrentValue <> '' then
  begin
    if DirExists(CurrentValue) then
      Result := CurrentValue
    else
      Result := ExtractFileDir(CurrentValue);
  end;
  if (Result = '') or (not DirExists(Result)) then
    Result := ExpandConstant('{userdocs}');
end;

procedure BrowseForRomLibrary(Sender: TObject);
var
  SelectedDirectory: String;
begin
  SelectedDirectory := FolderPage.Values[0];
  if Trim(SelectedDirectory) = '' then
    SelectedDirectory := ExpandConstant('{userdocs}');
  if BrowseForFolder(
       ExpandConstant('{cm:ROMLibrary}'),
       SelectedDirectory,
       True) then
    FolderPage.Values[0] := SelectedDirectory;
end;

procedure BrowseForObsFolder(Sender: TObject);
var
  SelectedDirectory: String;
begin
  SelectedDirectory := FolderPage.Values[1];
  if Trim(SelectedDirectory) = '' then
    SelectedDirectory := ExpandConstant('{userdocs}');
  if BrowseForFolder(
       ExpandConstant('{cm:OBSFolder}'),
       SelectedDirectory,
       True) then
    FolderPage.Values[1] := SelectedDirectory;
end;

procedure BrowseForConnectionService(Sender: TObject);
var
  SelectedFile: String;
begin
  SelectedFile := ExistingInterfacePage.Values[0];
  if GetOpenFileName(
       ExpandConstant('{cm:ServiceTitle}'),
       SelectedFile,
       PickerInitialDirectory(SelectedFile),
       ExpandConstant('{cm:ExecutableFiles}') + '|*.exe|' +
         ExpandConstant('{cm:AllFiles}') + '|*.*',
       '.exe') then
    ExistingInterfacePage.Values[0] := SelectedFile;
end;

procedure BrowseForRetroArch(Sender: TObject);
var
  SelectedFile: String;
begin
  SelectedFile := RetroArchPage.Values[0];
  if GetOpenFileName(
       ExpandConstant('{cm:RetroLocationTitle}'),
       SelectedFile,
       PickerInitialDirectory(SelectedFile),
       ExpandConstant('{cm:RetroExecutableFilter}') + '|retroarch.exe|' +
         ExpandConstant('{cm:ExecutableFiles}') + '|*.exe|' +
         ExpandConstant('{cm:AllFiles}') + '|*.*',
       '.exe') then
    RetroArchPage.Values[0] := SelectedFile;
end;

procedure BrowseForRetroArchCore(Sender: TObject);
var
  SelectedFile: String;
begin
  SelectedFile := RetroArchPage.Values[1];
  if GetOpenFileName(
       ExpandConstant('{cm:RetroCore}'),
       SelectedFile,
       PickerInitialDirectory(SelectedFile),
       ExpandConstant('{cm:LibretroCores}') + '|*_libretro.dll|' +
         ExpandConstant('{cm:DLLFiles}') + '|*.dll|' +
         ExpandConstant('{cm:AllFiles}') + '|*.*',
       '.dll') then
    RetroArchPage.Values[1] := SelectedFile;
end;

procedure InitializeWizard;
begin
  PlatformPage := CreateInputOptionPage(
    wpSelectDir,
    ExpandConstant('{cm:PlatformTitle}'),
    ExpandConstant('{cm:PlatformSubtitle}'),
    ExpandConstant('{cm:PlatformDescription}'),
    True,
    False);
  PlatformPage.Add(ExpandConstant('{cm:FXPAKOption}'));
  PlatformPage.Add(ExpandConstant('{cm:RetroArchOption}'));
  PlatformPage.SelectedValueIndex := 0;

  DependencyPage := CreateInputOptionPage(
    PlatformPage.ID,
    ExpandConstant('{cm:DependencyTitle}'),
    ExpandConstant('{cm:DependencySubtitle}'),
    ExpandConstant('{cm:DependencyDescription}'),
    False,
    False);
  DependencyPage.Add(ExpandConstant('{cm:SNIOption}'));
  DependencyPage.Add(ExpandConstant('{cm:QUsbOption}'));
  DependencyPage.Add(ExpandConstant('{cm:RetroArchInstallOption}'));
  DependencyPage.Values[0] := True;
  DependencyPage.Values[1] := False;
  DependencyPage.Values[2] := False;

  FolderPage := CreateInputDirPage(
    DependencyPage.ID,
    ExpandConstant('{cm:FolderTitle}'),
    ExpandConstant('{cm:FolderSubtitle}'),
    ExpandConstant('{cm:FolderDescription}'),
    False,
    SetupMessage(msgNewFolderName));
  FolderPage.Add(ExpandConstant('{cm:ROMLibrary}'));
  FolderPage.Add(ExpandConstant('{cm:OBSFolder}'));
  FolderPage.Values[0] := '';
  FolderPage.Values[1] := '';
  FolderPage.Buttons[0].OnClick := @BrowseForRomLibrary;
  FolderPage.Buttons[1].OnClick := @BrowseForObsFolder;

  ExistingInterfacePage := CreateInputFilePage(
    FolderPage.ID,
    ExpandConstant('{cm:ServiceTitle}'),
    ExpandConstant('{cm:ServiceSubtitle}'),
    ExpandConstant('{cm:ServiceDescription}'));
  ExistingInterfacePage.Add(
    ExpandConstant('{cm:ServiceExecutable}'),
    ExpandConstant('{cm:ExecutableFiles}') + '|*.exe|' +
      ExpandConstant('{cm:AllFiles}') + '|*.*',
    '.exe');
  ExistingInterfacePage.Values[0] := '';
  ExistingInterfacePage.Buttons[0].OnClick :=
    @BrowseForConnectionService;

  RetroArchPage := CreateInputFilePage(
    ExistingInterfacePage.ID,
    ExpandConstant('{cm:RetroLocationTitle}'),
    ExpandConstant('{cm:RetroLocationSubtitle}'),
    ExpandConstant('{cm:RetroLocationDescription}'));
  RetroArchPage.Add(
    ExpandConstant('{cm:RetroExecutable}'),
    ExpandConstant('{cm:RetroExecutableFilter}') + '|retroarch.exe|' +
      ExpandConstant('{cm:ExecutableFiles}') + '|*.exe|' +
      ExpandConstant('{cm:AllFiles}') + '|*.*',
    '.exe');
  RetroArchPage.Add(
    ExpandConstant('{cm:RetroCore}'),
    ExpandConstant('{cm:LibretroCores}') + '|*_libretro.dll|' +
      ExpandConstant('{cm:DLLFiles}') + '|*.dll|' +
      ExpandConstant('{cm:AllFiles}') + '|*.*',
    '.dll');
  RetroArchPage.Values[0] := '';
  RetroArchPage.Values[1] := '';
  RetroArchPage.Buttons[0].OnClick := @BrowseForRetroArch;
  RetroArchPage.Buttons[1].OnClick := @BrowseForRetroArchCore;

  FXPAKStepsPage := CreateOutputMsgPage(
    RetroArchPage.ID,
    ExpandConstant('{cm:FXPAKFinalTitle}'),
    ExpandConstant('{cm:FinalSubtitle}'),
    ExpandConstant('{cm:FXPAKStep1}') + #13#10#13#10 +
    ExpandConstant('{cm:FXPAKStep2}') + #13#10#13#10 +
    ExpandConstant('{cm:FXPAKStep3}') + #13#10#13#10 +
    ExpandConstant('{cm:FXPAKStep4}'));

  RetroArchStepsPage := CreateOutputMsgPage(
    FXPAKStepsPage.ID,
    ExpandConstant('{cm:RetroFinalTitle}'),
    ExpandConstant('{cm:RetroFinalSubtitle}'),
    ExpandConstant('{cm:RetroStep1}') + #13#10#13#10 +
    ExpandConstant('{cm:RetroStep2}') + #13#10#13#10 +
    ExpandConstant('{cm:RetroStep3}') + #13#10#13#10 +
    ExpandConstant('{cm:RetroStep4}'));

  ExistingConfigPage := CreateOutputMsgPage(
    RetroArchStepsPage.ID,
    ExpandConstant('{cm:ExistingTitle}'),
    ExpandConstant('{cm:ExistingSubtitle}'),
    ExpandConstant('{cm:ExistingDescription}'));
end;

function ShouldInstallSNI: Boolean;
begin
  Result := DependencyPage.Values[0];
end;

function ShouldInstallQUsb: Boolean;
begin
  Result := DependencyPage.Values[1];
end;

function ShouldInstallRetroArch: Boolean;
begin
  Result := DependencyPage.Values[2];
end;

function ShouldInstallRetroArchCore: Boolean;
begin
  Result := DependencyPage.Values[2];
end;

function RetroArchCoreDirectory(Param: String): String;
begin
  Result := ExpandConstant('{app}\Tools\RetroArch\cores');
end;

function ShouldSkipPage(PageID: Integer): Boolean;
var
  WantsRetroArch: Boolean;
begin
  WantsRetroArch :=
    (PlatformPage.SelectedValueIndex = 1) or
    DependencyPage.Values[2];

  if PageID = ExistingInterfacePage.ID then
    Result := DependencyPage.Values[0] or DependencyPage.Values[1]
  else if PageID = RetroArchPage.ID then
    Result := (not WantsRetroArch) or DependencyPage.Values[2]
  else if PageID = FXPAKStepsPage.ID then
    Result := PlatformPage.SelectedValueIndex <> 0
  else if PageID = RetroArchStepsPage.ID then
    Result := not WantsRetroArch
  else if PageID = ExistingConfigPage.ID then
    Result := not FileExists(ConfigFilePath)
  else
    Result := False;
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;

  if CurPageID = PlatformPage.ID then
  begin
    if PlatformPage.SelectedValueIndex = 1 then
    begin
      DependencyPage.Values[0] := True;
      DependencyPage.Values[2] := True;
    end;
  end
  else if CurPageID = ExistingInterfacePage.ID then
  begin
    if (Trim(ExistingInterfacePage.Values[0]) <> '') and
       (not FileExists(ExistingInterfacePage.Values[0])) then
    begin
      MsgBox(ExpandConstant('{cm:ErrorService}'), mbError, MB_OK);
      Result := False;
    end;
  end
  else if CurPageID = RetroArchPage.ID then
  begin
    if (Trim(RetroArchPage.Values[0]) <> '') and
       (not FileExists(RetroArchPage.Values[0])) then
    begin
      MsgBox(
        ExpandConstant('{cm:ErrorRetroExe}'),
        mbError,
        MB_OK);
      Result := False;
    end
    else if (Trim(RetroArchPage.Values[1]) <> '') and
            (not FileExists(RetroArchPage.Values[1])) then
    begin
      MsgBox(
        ExpandConstant('{cm:ErrorRetroCore}'),
        mbError,
        MB_OK);
      Result := False;
    end;
  end;
end;

function JsonEscape(Value: String): String;
begin
  Result := Value;
  StringChangeEx(Result, '\', '\\', True);
  StringChangeEx(Result, '"', '\"', True);
end;

function SelectedPlatformName: String;
begin
  if PlatformPage.SelectedValueIndex = 1 then
    Result := 'RetroArch'
  else
    Result := 'FXPAK Pro';
end;

function SelectedAppLanguage: String;
begin
  if ActiveLanguage = 'australian' then
    Result := 'au'
  else if ActiveLanguage = 'spanish' then
    Result := 'es'
  else if ActiveLanguage = 'french' then
    Result := 'fr'
  else if ActiveLanguage = 'german' then
    Result := 'de'
  else if ActiveLanguage = 'brazilianportuguese' then
    Result := 'pt-BR'
  else
    Result := 'en';
end;

function SelectedSNIPath: String;
begin
  if DependencyPage.Values[0] then
    Result := ExpandConstant('{app}\Tools\SNI\sni.exe')
  else if CompareText(ExtractFileName(ExistingInterfacePage.Values[0]), 'sni.exe') = 0 then
    Result := ExistingInterfacePage.Values[0]
  else
    Result := '';
end;

function SelectedQUsb2SnesPath: String;
begin
  if DependencyPage.Values[1] then
    Result := ExpandConstant('{app}\Tools\QUsb2Snes\QUsb2Snes.exe')
  else if CompareText(ExtractFileName(ExistingInterfacePage.Values[0]), 'QUsb2Snes.exe') = 0 then
    Result := ExistingInterfacePage.Values[0]
  else
    Result := '';
end;

function SelectedInterfacePath: String;
begin
  Result := SelectedSNIPath;
  if Result = '' then
    Result := SelectedQUsb2SnesPath;
end;

function SelectedRetroArchCorePath: String;
begin
  if DependencyPage.Values[2] then
    Result := ExpandConstant('{app}\Tools\RetroArch\cores\bsnes_mercury_performance_libretro.dll')
  else
    Result := RetroArchPage.Values[1];
end;

procedure WriteInitialConfiguration;
var
  ConfigText: String;
  InterfacePath: String;
  SNIPath: String;
  QUsb2SnesPath: String;
begin
  if FileExists(ConfigFilePath) then
  begin
    Log('Preserving existing tracker configuration: ' + ConfigFilePath);
    Exit;
  end;

  if Trim(FolderPage.Values[0]) <> '' then
    ForceDirectories(FolderPage.Values[0]);
  if Trim(FolderPage.Values[1]) <> '' then
    ForceDirectories(FolderPage.Values[1]);
  SNIPath := SelectedSNIPath;
  QUsb2SnesPath := SelectedQUsb2SnesPath;
  InterfacePath := SelectedInterfacePath;

  ConfigText := '{'#13#10 +
    '  "app_language": "' + SelectedAppLanguage + '",'#13#10 +
    '  "sni_path": "' + JsonEscape(SNIPath) + '",'#13#10 +
    '  "qusb2snes_path": "' + JsonEscape(QUsb2SnesPath) + '",'#13#10 +
    '  "connection_service_preference": "Automatic",'#13#10 +
    '  "platform_interface_path": "' + JsonEscape(InterfacePath) + '",'#13#10 +
    '  "platform_websocket_url": "ws://localhost:23074",'#13#10 +
    '  "fxpak_websocket_url": "ws://localhost:23074",'#13#10 +
    '  "selected_platform": "' + SelectedPlatformName + '",'#13#10 +
    '  "platform_rom_library_folder": "' + JsonEscape(FolderPage.Values[0]) + '",'#13#10 +
    '  "rom_builder_library_folder": "' + JsonEscape(FolderPage.Values[0]) + '",'#13#10 +
    '  "output_folder": "' + JsonEscape(FolderPage.Values[1]) + '",'#13#10 +
    '  "retroarch_executable_path": "' + JsonEscape(RetroArchPage.Values[0]) + '",'#13#10 +
    '  "retroarch_core_path": "' + JsonEscape(SelectedRetroArchCorePath) + '",'#13#10 +
    '  "retroarch_host": "127.0.0.1",'#13#10 +
    '  "retroarch_port": 55355,'#13#10 +
    '  "ui_theme": "dark"'#13#10 +
    '}'#13#10;

  if not SaveStringToFile(ConfigFilePath, ConfigText, False) then
    RaiseException(ExpandConstant('{cm:ConfigWriteError}') + ' ' + ConfigFilePath);
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
    WriteInitialConfiguration;
end;

function UpdateReadyMemo(
  Space, NewLine, MemoUserInfoInfo, MemoDirInfo, MemoTypeInfo,
  MemoComponentsInfo, MemoGroupInfo, MemoTasksInfo: String): String;
var
  DependencyList: String;
begin
  DependencyList := '';
  if DependencyPage.Values[0] then
    DependencyList := DependencyList + Space + ExpandConstant('{cm:ReadySNI}') + NewLine;
  if DependencyPage.Values[1] then
    DependencyList := DependencyList + Space + ExpandConstant('{cm:ReadyQUsb}') + NewLine;
  if DependencyPage.Values[2] then
    DependencyList := DependencyList + Space + ExpandConstant('{cm:ReadyRetro}') + NewLine;
  if DependencyList = '' then
    DependencyList := Space + ExpandConstant('{cm:ReadyNone}') + NewLine;

  Result := MemoDirInfo + NewLine + NewLine +
    ExpandConstant('{cm:ReadyPlatform}') + NewLine + Space + SelectedPlatformName + NewLine + NewLine +
    ExpandConstant('{cm:ReadyDependencies}') + NewLine + DependencyList + NewLine +
    ExpandConstant('{cm:ReadyROMLibrary}') + NewLine + Space + FolderPage.Values[0] + NewLine + NewLine +
    ExpandConstant('{cm:ReadyOBS}') + NewLine + Space + FolderPage.Values[1] + NewLine;

  if MemoTasksInfo <> '' then
    Result := Result + NewLine + MemoTasksInfo;
end;
