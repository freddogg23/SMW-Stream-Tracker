#define AppName "SMW Stream Tracker"
#define AppVersion "2.1.0"
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
DisableDirPage=yes
DisableProgramGroupPage=yes
UsePreviousAppDir=no
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
OutputDir={#SetupOutputDir}
OutputBaseFilename={#SetupOutputBaseFilename}
SetupIconFile=..\app_assets\smw_stream_tracker_icon.ico
WizardImageFile=
WizardSmallImageFile=
WizardStyle=modern dark polar includetitlebar hidebevels
WizardBackColor=#0D1216
WizardSizePercent=150
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
english.LaunchApp=Launch SMW Stream Tracker
english.DesktopShortcut=Create a &desktop shortcut
english.ShortcutGroup=Shortcuts:
english.PlatformTitle=Choose Your Platform
english.PlatformSubtitle=Which platform should SMW Stream Tracker use first?
english.PlatformDescription=You can switch between FXPAK Pro, RetroArch, and MiSTer later from the File menu.
english.FXPAKOption=FXPAK Pro (hardware cartridge)
english.RetroArchOption=RetroArch (Windows emulator)
english.MiSTerOption=MiSTer FPGA (network hardware)
english.DependencyTitle=Optional Dependencies
english.DependencySubtitle=Select any combination of the tools you want Setup to install.
english.DependencyDescription=SNI is required for RetroArch and MiSTer live tracking. MiSTer also continues with the app's one-click network setup on first launch.
english.SNIOption=Install SNI v0.0.103 (needed for RetroArch and MiSTer setup)
english.QUsbOption=Install QUsb2Snes 2025-10-20 (recommended for FXPAK Pro and SD2SNES users)
english.RetroArchInstallOption=Install portable RetroArch 1.22.2 and the bsnes-mercury Performance core (select if you only want a new/clean install)
english.MiSTerSetupOption=Set up MiSTer on first launch (requires MiSTer to be connected to your local network)
english.FolderTitle=Choose Your Tracker Folders
english.FolderSubtitle=Create new folders, or use folders you already have.
english.FolderDescription=Select new or existing folders below. You may leave OBS / stream text output blank and continue without it.
english.ROMLibrary=Patched ROM library (new or existing folder):
english.OBSFolder=OBS / stream text output (optional):
english.OBSFolderNote=OBS stream text files automatically update hack titles, creators, exits, and death counters in OBS or Streamlabs.
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
english.RetroFinalTitle=Portable RetroArch Setup
english.RetroFinalSubtitle=This blue Setup handles the RetroArch preparation automatically:
english.RetroStep1=1. RetroArch's faster background installer places the portable build in its standard RetroArch-Win64 folder.
english.RetroStep2=2. The recommended bsnes-mercury Performance core is installed automatically.
english.RetroStep3=3. Network Commands are enabled automatically on port 55355.
english.RetroStep4=4. After installation, launch an SMW ROM and select File > RetroArch. No separate RetroArch setup wizard is required.
english.ExistingTitle=Existing Settings Found
english.ExistingSubtitle=Your current tracker settings will be preserved.
english.ExistingDescription=Setup found SMWStreamTrackerConfig.json in your user profile. It will not overwrite that file. New tools are still installed, and their paths can be selected later from Settings.
english.ErrorService=The selected connection-service executable was not found.
english.ErrorRetroExe=The selected RetroArch executable was not found. Select a valid retroarch.exe or clear the field to configure it later.
english.ErrorRetroCore=The selected SNES core was not found. Select a valid Libretro core or clear the field to configure it later.
english.RetroInstallProgress=Installing RetroArch with its faster background installer...
english.ErrorRetroInstall=RetroArch could not be installed. Check your internet connection and try Setup again.
english.QUsbInstallProgress=Installing QUsb2Snes with the faster Windows archive engine...
english.ErrorQUsbInstall=QUsb2Snes could not be installed. Check your internet connection and try Setup again.
english.ReadySNI=SNI v0.0.103 (strongly recommended)
english.ReadyQUsb=QUsb2Snes 2025-10-20
english.ReadyRetro=Portable RetroArch 1.22.2 and the bsnes-mercury Performance core
english.ReadyMiSTer=One-click MiSTer discovery and setup on first launch
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
english.ExistingInstallActionTitle=Existing Installation Found
english.ExistingInstallActionSubtitle=Only one copy of SMW Stream Tracker can be installed for this Windows account.
english.ExistingInstallActionDescription=Choose what Setup should do. RetroArch, SNI, QUsb2Snes, and all ROM files will be preserved.
english.ExistingInstallFreshOption=Uninstall the current copy and continue with a fresh installation
english.ExistingInstallRemoveOption=Completely uninstall SMW Stream Tracker and exit Setup
english.ExistingInstallRemovalFailed=Setup could not completely remove the existing tracker. Close SMW Stream Tracker and try again.
english.ExistingInstallRemovalComplete=SMW Stream Tracker was completely uninstalled. RetroArch, SNI, QUsb2Snes, and ROM files were preserved.

australian.GuideName=Fair Dinkum Setup Guide
australian.MarkdownGuideName=Complete Setup README
australian.OpenGuide=Open the setup yarn
australian.LaunchApp=Fire up SMW Stream Tracker
australian.DesktopShortcut=Pop a shortcut on the &desktop
australian.ShortcutGroup=Handy shortcuts:
australian.PlatformTitle=Pick Your Gear
australian.PlatformSubtitle=What are we running first, mate?
australian.PlatformDescription=No dramas—you can swap between FXPAK Pro, RetroArch, and MiSTer later from the File menu.
australian.FXPAKOption=FXPAK Pro (the hardware cart, you beauty)
australian.RetroArchOption=RetroArch (emulator on the Windows box)
australian.MiSTerOption=MiSTer FPGA (the network hardware, mate)
australian.DependencyTitle=Optional Bits and Bobs
australian.DependencySubtitle=Pick any combination of tools you want Setup to chuck in.
australian.DependencyDescription=SNI is needed for RetroArch and MiSTer live tracking. Tick MiSTer and the app will find and sort out the hardware on first launch—too easy, mate.
australian.SNIOption=Install SNI v0.0.103 (needed for RetroArch and MiSTer setup)
australian.QUsbOption=Install QUsb2Snes 2025-10-20 (recommended for FXPAK Pro and SD2SNES mates)
australian.RetroArchInstallOption=Install portable RetroArch 1.22.2 and the bsnes-mercury Performance core (tick this only for a fresh/clean install, mate)
australian.MiSTerSetupOption=Set up MiSTer on first launch (requires MiSTer to be connected to your local network, mate)
australian.FolderTitle=Choose Where the Good Stuff Lives
australian.FolderSubtitle=Create new folders, or use folders you already have, mate.
australian.FolderDescription=Pick new or existing folders below. OBS / stream text output is optional, mate, so leave it blank and carry on if you do not need it.
australian.ROMLibrary=Patched ROM library (new or existing folder):
australian.OBSFolder=OBS / stream text output (optional, mate):
australian.OBSFolderNote=OBS stream text files keep hack titles, creators, exits, and death counters updated automatically in OBS or Streamlabs. Too easy.
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
australian.RetroFinalTitle=Portable RetroArch—All Sorted
australian.RetroFinalSubtitle=This blue Setup handles the RetroArch hard yakka automatically:
australian.RetroStep1=1. RetroArch's faster background installer chucks the portable build into its usual RetroArch-Win64 folder.
australian.RetroStep2=2. The recommended bsnes-mercury Performance core is chucked in automatically.
australian.RetroStep3=3. Network Commands are switched on automatically at port 55355.
australian.RetroStep4=4. After installation, launch an SMW ROM and select File > RetroArch. No second setup wizard, mate—too easy.
australian.ExistingTitle=Found Your Existing Settings
australian.ExistingSubtitle=Your current tracker settings are staying right where they are.
australian.ExistingDescription=Setup found SMWStreamTrackerConfig.json in your user profile. It will not stomp on that file. New tools still get installed, and you can pick their paths later in Settings.
australian.ErrorService=Could not find that connection-service executable, mate.
australian.ErrorRetroExe=Could not find that RetroArch executable. Pick a valid retroarch.exe or clear the field and sort it later.
australian.ErrorRetroCore=Could not find that SNES core. Pick a valid Libretro core or clear the field and sort it later.
australian.RetroInstallProgress=Installing RetroArch with its faster background installer, mate...
australian.ErrorRetroInstall=Crikey, RetroArch could not be installed. Check the internet connection and give Setup another burl.
australian.QUsbInstallProgress=Installing QUsb2Snes with the faster Windows archive engine, mate...
australian.ErrorQUsbInstall=Crikey, QUsb2Snes could not be installed. Check the internet connection and give Setup another burl.
australian.ReadySNI=SNI v0.0.103 (strongly recommended)
australian.ReadyQUsb=QUsb2Snes 2025-10-20
australian.ReadyRetro=Portable RetroArch 1.22.2 and the bsnes-mercury Performance core
australian.ReadyMiSTer=One-click MiSTer discovery and setup on first launch, mate
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
australian.ExistingInstallActionTitle=Crikey! Found Another Tracker
australian.ExistingInstallActionSubtitle=Only one SMW Stream Tracker copy can live on this Windows account, mate.
australian.ExistingInstallActionDescription=Pick what Setup should do. RetroArch, SNI, QUsb2Snes, and every ROM stay safe and sound.
australian.ExistingInstallFreshOption=Uninstall the old copy and crack on with a fresh install
australian.ExistingInstallRemoveOption=Completely uninstall SMW Stream Tracker and call it a day
australian.ExistingInstallRemovalFailed=Crikey! Setup could not clear the old tracker. Close SMW Stream Tracker and have another go, mate.
australian.ExistingInstallRemovalComplete=Done and dusted! The tracker is completely uninstalled. RetroArch, SNI, QUsb2Snes, and your ROMs are still right where you left them.

spanish.GuideName=Guía completa de configuración
spanish.MarkdownGuideName=README completo de configuración
spanish.OpenGuide=Abrir la guía completa de configuración
spanish.LaunchApp=Iniciar SMW Stream Tracker
spanish.DesktopShortcut=Crear un acceso directo en el &escritorio
spanish.ShortcutGroup=Accesos directos:
spanish.PlatformTitle=Elija su plataforma
spanish.PlatformSubtitle=¿Qué plataforma debe usar primero SMW Stream Tracker?
spanish.PlatformDescription=Puede cambiar entre FXPAK Pro, RetroArch y MiSTer más tarde desde el menú Archivo.
spanish.FXPAKOption=FXPAK Pro (cartucho físico)
spanish.RetroArchOption=RetroArch (emulador de Windows)
spanish.MiSTerOption=MiSTer FPGA (hardware de red)
spanish.DependencyTitle=Dependencias opcionales
spanish.DependencySubtitle=Seleccione cualquier combinación de herramientas que desee instalar.
spanish.DependencyDescription=SNI es necesario para el seguimiento en vivo de RetroArch y MiSTer. MiSTer también continúa con la configuración automática de red en el primer inicio.
spanish.SNIOption=Instalar SNI v0.0.103 (necesario para configurar RetroArch y MiSTer)
spanish.QUsbOption=Instalar QUsb2Snes 2025-10-20 (recomendado para FXPAK Pro y SD2SNES)
spanish.RetroArchInstallOption=Instalar RetroArch portátil 1.22.2 y el núcleo bsnes-mercury Performance (seleccione solo si desea una instalación nueva/limpia)
spanish.MiSTerSetupOption=Configurar MiSTer en el primer inicio (requiere que MiSTer esté conectado a su red local)
spanish.FolderTitle=Elija las carpetas del rastreador
spanish.FolderSubtitle=Cree carpetas nuevas o use las carpetas que ya tiene.
spanish.FolderDescription=Seleccione carpetas nuevas o existentes. Puede dejar vacía la salida de texto para OBS / streaming y continuar sin ella.
spanish.ROMLibrary=Biblioteca de ROM parcheadas (carpeta nueva o existente):
spanish.OBSFolder=Salida de texto para OBS / streaming (opcional):
spanish.OBSFolderNote=Los archivos de texto para OBS actualizan automáticamente los títulos de los hacks, los creadores, las salidas y los contadores de muertes en OBS o Streamlabs.
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
spanish.RetroFinalTitle=Configuración de RetroArch portátil
spanish.RetroFinalSubtitle=Este instalador azul prepara RetroArch automáticamente:
spanish.RetroStep1=1. El instalador rápido en segundo plano de RetroArch coloca la versión portátil en su carpeta estándar RetroArch-Win64.
spanish.RetroStep2=2. El núcleo recomendado bsnes-mercury Performance se instala automáticamente.
spanish.RetroStep3=3. Los Comandos de red se activan automáticamente en el puerto 55355.
spanish.RetroStep4=4. Después de instalar, inicie una ROM de SMW y seleccione Archivo > RetroArch. No se necesita otro asistente de instalación.
spanish.ExistingTitle=Se encontró una configuración existente
spanish.ExistingSubtitle=Se conservará la configuración actual del rastreador.
spanish.ExistingDescription=El instalador encontró SMWStreamTrackerConfig.json en su perfil y no lo sobrescribirá. Puede seleccionar las rutas de las nuevas herramientas más tarde.
spanish.ErrorService=No se encontró el ejecutable del servicio de conexión seleccionado.
spanish.ErrorRetroExe=No se encontró el ejecutable de RetroArch. Seleccione un retroarch.exe válido o borre el campo.
spanish.ErrorRetroCore=No se encontró el núcleo SNES. Seleccione un núcleo Libretro válido o borre el campo.
spanish.RetroInstallProgress=Instalando RetroArch con su instalador rápido en segundo plano...
spanish.ErrorRetroInstall=No se pudo instalar RetroArch. Compruebe la conexión a Internet y vuelva a ejecutar el instalador.
spanish.QUsbInstallProgress=Instalando QUsb2Snes con el motor rápido de archivos de Windows...
spanish.ErrorQUsbInstall=No se pudo instalar QUsb2Snes. Compruebe la conexión a Internet y vuelva a ejecutar el instalador.
spanish.ReadySNI=SNI v0.0.103 (muy recomendado)
spanish.ReadyQUsb=QUsb2Snes 2025-10-20
spanish.ReadyRetro=RetroArch portátil 1.22.2 y el núcleo bsnes-mercury Performance
spanish.ReadyMiSTer=Detección y configuración automática de MiSTer en el primer inicio
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
spanish.ExistingInstallActionTitle=Se encontró una instalación existente
spanish.ExistingInstallActionSubtitle=Solo se puede instalar una copia de SMW Stream Tracker en esta cuenta de Windows.
spanish.ExistingInstallActionDescription=Elija qué debe hacer el instalador. Se conservarán RetroArch, SNI, QUsb2Snes y todos los archivos ROM.
spanish.ExistingInstallFreshOption=Desinstalar la copia actual y continuar con una instalación nueva
spanish.ExistingInstallRemoveOption=Desinstalar completamente SMW Stream Tracker y salir del instalador
spanish.ExistingInstallRemovalFailed=El instalador no pudo eliminar completamente el tracker existente. Cierre SMW Stream Tracker e inténtelo de nuevo.
spanish.ExistingInstallRemovalComplete=SMW Stream Tracker se desinstaló completamente. Se conservaron RetroArch, SNI, QUsb2Snes y los archivos ROM.

french.GuideName=Guide complet de configuration
french.MarkdownGuideName=README complet de configuration
french.OpenGuide=Ouvrir le guide complet de configuration
french.LaunchApp=Lancer SMW Stream Tracker
french.DesktopShortcut=Créer un raccourci sur le &Bureau
french.ShortcutGroup=Raccourcis :
french.PlatformTitle=Choisissez votre plateforme
french.PlatformSubtitle=Quelle plateforme SMW Stream Tracker doit-il utiliser en premier ?
french.PlatformDescription=Vous pourrez basculer entre FXPAK Pro, RetroArch et MiSTer plus tard depuis le menu Fichier.
french.FXPAKOption=FXPAK Pro (cartouche matérielle)
french.RetroArchOption=RetroArch (émulateur Windows)
french.MiSTerOption=MiSTer FPGA (matériel réseau)
french.DependencyTitle=Dépendances facultatives
french.DependencySubtitle=Sélectionnez les outils que le programme d'installation doit installer.
french.DependencyDescription=SNI est requis pour le suivi en direct de RetroArch et MiSTer. MiSTer poursuit aussi la configuration réseau automatique au premier lancement.
french.SNIOption=Installer SNI v0.0.103 (requis pour configurer RetroArch et MiSTer)
french.QUsbOption=Installer QUsb2Snes 2025-10-20 (recommandé pour FXPAK Pro et SD2SNES)
french.RetroArchInstallOption=Installer RetroArch portable 1.22.2 et le cœur bsnes-mercury Performance (sélectionnez uniquement pour une nouvelle installation propre)
french.MiSTerSetupOption=Configurer MiSTer au premier lancement (nécessite que MiSTer soit connecté à votre réseau local)
french.FolderTitle=Choisissez les dossiers du tracker
french.FolderSubtitle=Créez de nouveaux dossiers ou utilisez les dossiers que vous possédez déjà.
french.FolderDescription=Sélectionnez des dossiers nouveaux ou existants. Vous pouvez laisser la sortie texte OBS / stream vide et continuer sans elle.
french.ROMLibrary=Bibliothèque de ROM patchées (dossier nouveau ou existant) :
french.OBSFolder=Sortie texte OBS / stream (facultative) :
french.OBSFolderNote=Les fichiers texte OBS mettent automatiquement à jour les titres des hacks, les créateurs, les sorties et les compteurs de morts dans OBS ou Streamlabs.
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
french.RetroFinalTitle=Configuration de RetroArch portable
french.RetroFinalSubtitle=Ce programme d'installation bleu prépare RetroArch automatiquement :
french.RetroStep1=1. Le programme d'installation rapide en arrière-plan de RetroArch place la version portable dans son dossier standard RetroArch-Win64.
french.RetroStep2=2. Le cœur bsnes-mercury Performance recommandé est installé automatiquement.
french.RetroStep3=3. Les commandes réseau sont activées automatiquement sur le port 55355.
french.RetroStep4=4. Après l'installation, lancez une ROM SMW et choisissez Fichier > RetroArch. Aucun autre assistant d'installation n'est nécessaire.
french.ExistingTitle=Paramètres existants détectés
french.ExistingSubtitle=Vos paramètres actuels seront conservés.
french.ExistingDescription=Le programme a trouvé SMWStreamTrackerConfig.json dans votre profil et ne l'écrasera pas. Les chemins des nouveaux outils pourront être choisis plus tard.
french.ErrorService=L'exécutable du service de connexion sélectionné est introuvable.
french.ErrorRetroExe=L'exécutable RetroArch est introuvable. Sélectionnez un retroarch.exe valide ou videz le champ.
french.ErrorRetroCore=Le cœur SNES est introuvable. Sélectionnez un cœur Libretro valide ou videz le champ.
french.RetroInstallProgress=Installation de RetroArch avec son programme rapide en arrière-plan...
french.ErrorRetroInstall=RetroArch n'a pas pu être installé. Vérifiez la connexion Internet et relancez l'installation.
french.QUsbInstallProgress=Installation de QUsb2Snes avec le moteur d'archive rapide de Windows...
french.ErrorQUsbInstall=QUsb2Snes n'a pas pu être installé. Vérifiez la connexion Internet et relancez l'installation.
french.ReadySNI=SNI v0.0.103 (fortement recommandé)
french.ReadyQUsb=QUsb2Snes 2025-10-20
french.ReadyRetro=RetroArch portable 1.22.2 et le cœur bsnes-mercury Performance
french.ReadyMiSTer=Détection et configuration automatiques de MiSTer au premier lancement
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
french.ExistingInstallActionTitle=Installation existante détectée
french.ExistingInstallActionSubtitle=Une seule copie de SMW Stream Tracker peut être installée pour ce compte Windows.
french.ExistingInstallActionDescription=Choisissez l'action du programme d'installation. RetroArch, SNI, QUsb2Snes et tous les fichiers ROM seront conservés.
french.ExistingInstallFreshOption=Désinstaller la copie actuelle et poursuivre avec une nouvelle installation
french.ExistingInstallRemoveOption=Désinstaller complètement SMW Stream Tracker et quitter l'installation
french.ExistingInstallRemovalFailed=Le programme n'a pas pu supprimer complètement le tracker existant. Fermez SMW Stream Tracker et réessayez.
french.ExistingInstallRemovalComplete=SMW Stream Tracker a été complètement désinstallé. RetroArch, SNI, QUsb2Snes et les fichiers ROM ont été conservés.

german.GuideName=Vollständige Einrichtungsanleitung
german.MarkdownGuideName=Vollständige Setup-README
german.OpenGuide=Vollständige Einrichtungsanleitung öffnen
german.LaunchApp=SMW Stream Tracker starten
german.DesktopShortcut=&Desktop-Verknüpfung erstellen
german.ShortcutGroup=Verknüpfungen:
german.PlatformTitle=Plattform auswählen
german.PlatformSubtitle=Welche Plattform soll SMW Stream Tracker zuerst verwenden?
german.PlatformDescription=Sie können später im Datei-Menü zwischen FXPAK Pro, RetroArch und MiSTer wechseln.
german.FXPAKOption=FXPAK Pro (Hardware-Modul)
german.RetroArchOption=RetroArch (Windows-Emulator)
german.MiSTerOption=MiSTer FPGA (Netzwerk-Hardware)
german.DependencyTitle=Optionale Abhängigkeiten
german.DependencySubtitle=Wählen Sie beliebige Tools aus, die Setup installieren soll.
german.DependencyDescription=SNI wird für das Live-Tracking mit RetroArch und MiSTer benötigt. MiSTer fährt beim ersten App-Start außerdem mit der automatischen Netzwerkeinrichtung fort.
german.SNIOption=SNI v0.0.103 installieren (für die Einrichtung von RetroArch und MiSTer erforderlich)
german.QUsbOption=QUsb2Snes 2025-10-20 installieren (für FXPAK Pro und SD2SNES empfohlen)
german.RetroArchInstallOption=Portables RetroArch 1.22.2 und bsnes-mercury Performance-Core installieren (nur für eine neue/saubere Installation auswählen)
german.MiSTerSetupOption=MiSTer beim ersten Start einrichten (MiSTer muss mit Ihrem lokalen Netzwerk verbunden sein)
german.FolderTitle=Tracker-Ordner auswählen
german.FolderSubtitle=Erstellen Sie neue Ordner oder verwenden Sie bereits vorhandene Ordner.
german.FolderDescription=Wählen Sie unten neue oder vorhandene Ordner. Die OBS-/Stream-Textausgabe darf leer bleiben; Sie können ohne sie fortfahren.
german.ROMLibrary=Bibliothek gepatchter ROMs (neuer oder vorhandener Ordner):
german.OBSFolder=OBS-/Stream-Textausgabe (optional):
german.OBSFolderNote=OBS-Textdateien aktualisieren Hack-Titel, Ersteller, Ausgänge und Todeszähler in OBS oder Streamlabs automatisch.
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
german.RetroFinalTitle=Einrichtung des portablen RetroArch
german.RetroFinalSubtitle=Dieses blaue Setup bereitet RetroArch automatisch vor:
german.RetroStep1=1. Das schnellere Hintergrund-Installationsprogramm von RetroArch legt die portable Version im standardmäßigen Ordner RetroArch-Win64 ab.
german.RetroStep2=2. Der empfohlene bsnes-mercury Performance-Core wird automatisch installiert.
german.RetroStep3=3. Netzwerkbefehle werden automatisch auf Port 55355 aktiviert.
german.RetroStep4=4. Starten Sie nach der Installation ein SMW-ROM und wählen Sie Datei > RetroArch. Ein zweiter Installationsassistent ist nicht erforderlich.
german.ExistingTitle=Vorhandene Einstellungen gefunden
german.ExistingSubtitle=Ihre aktuellen Tracker-Einstellungen bleiben erhalten.
german.ExistingDescription=Setup hat SMWStreamTrackerConfig.json in Ihrem Benutzerprofil gefunden und überschreibt die Datei nicht. Neue Tool-Pfade können später ausgewählt werden.
german.ErrorService=Die ausgewählte Programmdatei des Verbindungsdienstes wurde nicht gefunden.
german.ErrorRetroExe=Die ausgewählte RetroArch-Programmdatei wurde nicht gefunden. Wählen Sie eine gültige retroarch.exe oder leeren Sie das Feld.
german.ErrorRetroCore=Der SNES-Core wurde nicht gefunden. Wählen Sie einen gültigen Libretro-Core oder leeren Sie das Feld.
german.RetroInstallProgress=RetroArch wird mit dem schnelleren Hintergrund-Installationsprogramm installiert...
german.ErrorRetroInstall=RetroArch konnte nicht installiert werden. Prüfen Sie die Internetverbindung und starten Sie Setup erneut.
german.QUsbInstallProgress=QUsb2Snes wird mit der schnelleren Windows-Archiv-Engine installiert...
german.ErrorQUsbInstall=QUsb2Snes konnte nicht installiert werden. Prüfen Sie die Internetverbindung und starten Sie Setup erneut.
german.ReadySNI=SNI v0.0.103 (dringend empfohlen)
german.ReadyQUsb=QUsb2Snes 2025-10-20
german.ReadyRetro=Portables RetroArch 1.22.2 und bsnes-mercury Performance-Core
german.ReadyMiSTer=Automatische MiSTer-Suche und -Einrichtung beim ersten Start
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
german.ExistingInstallActionTitle=Vorhandene Installation gefunden
german.ExistingInstallActionSubtitle=Für dieses Windows-Konto kann nur eine Kopie von SMW Stream Tracker installiert werden.
german.ExistingInstallActionDescription=Wählen Sie die gewünschte Aktion. RetroArch, SNI, QUsb2Snes und alle ROM-Dateien bleiben erhalten.
german.ExistingInstallFreshOption=Die aktuelle Kopie deinstallieren und mit einer Neuinstallation fortfahren
german.ExistingInstallRemoveOption=SMW Stream Tracker vollständig deinstallieren und Setup beenden
german.ExistingInstallRemovalFailed=Setup konnte den vorhandenen Tracker nicht vollständig entfernen. Schließen Sie SMW Stream Tracker und versuchen Sie es erneut.
german.ExistingInstallRemovalComplete=SMW Stream Tracker wurde vollständig deinstalliert. RetroArch, SNI, QUsb2Snes und ROM-Dateien blieben erhalten.

brazilianportuguese.GuideName=Guia completo de configuração
brazilianportuguese.MarkdownGuideName=README completo de configuração
brazilianportuguese.OpenGuide=Abrir o guia completo de configuração
brazilianportuguese.LaunchApp=Iniciar o SMW Stream Tracker
brazilianportuguese.DesktopShortcut=Criar atalho na área de &trabalho
brazilianportuguese.ShortcutGroup=Atalhos:
brazilianportuguese.PlatformTitle=Escolha sua plataforma
brazilianportuguese.PlatformSubtitle=Qual plataforma o SMW Stream Tracker deve usar primeiro?
brazilianportuguese.PlatformDescription=Você poderá alternar entre FXPAK Pro, RetroArch e MiSTer mais tarde no menu Arquivo.
brazilianportuguese.FXPAKOption=FXPAK Pro (cartucho físico)
brazilianportuguese.RetroArchOption=RetroArch (emulador do Windows)
brazilianportuguese.MiSTerOption=MiSTer FPGA (hardware de rede)
brazilianportuguese.DependencyTitle=Dependências opcionais
brazilianportuguese.DependencySubtitle=Selecione qualquer combinação de ferramentas para instalar.
brazilianportuguese.DependencyDescription=SNI é necessário para o acompanhamento ao vivo do RetroArch e do MiSTer. O MiSTer também continua com a configuração automática de rede na primeira abertura.
brazilianportuguese.SNIOption=Instalar SNI v0.0.103 (necessário para configurar RetroArch e MiSTer)
brazilianportuguese.QUsbOption=Instalar QUsb2Snes 2025-10-20 (recomendado para FXPAK Pro e SD2SNES)
brazilianportuguese.RetroArchInstallOption=Instalar RetroArch portátil 1.22.2 e o núcleo bsnes-mercury Performance (selecione somente para uma instalação nova/limpa)
brazilianportuguese.MiSTerSetupOption=Configurar o MiSTer na primeira abertura (requer que o MiSTer esteja conectado à sua rede local)
brazilianportuguese.FolderTitle=Escolha as pastas do tracker
brazilianportuguese.FolderSubtitle=Crie novas pastas ou use as pastas que você já tem.
brazilianportuguese.FolderDescription=Selecione pastas novas ou existentes. Você pode deixar a saída de texto do OBS / transmissão em branco e continuar sem ela.
brazilianportuguese.ROMLibrary=Biblioteca de ROMs com patch (pasta nova ou existente):
brazilianportuguese.OBSFolder=Saída de texto do OBS / transmissão (opcional):
brazilianportuguese.OBSFolderNote=Os arquivos de texto do OBS atualizam automaticamente os títulos dos hacks, criadores, saídas e contadores de mortes no OBS ou Streamlabs.
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
brazilianportuguese.RetroFinalTitle=Configuração do RetroArch portátil
brazilianportuguese.RetroFinalSubtitle=Este instalador azul prepara o RetroArch automaticamente:
brazilianportuguese.RetroStep1=1. O instalador rápido em segundo plano do RetroArch coloca a versão portátil na pasta padrão RetroArch-Win64.
brazilianportuguese.RetroStep2=2. O núcleo recomendado bsnes-mercury Performance é instalado automaticamente.
brazilianportuguese.RetroStep3=3. Os Comandos de Rede são ativados automaticamente na porta 55355.
brazilianportuguese.RetroStep4=4. Depois da instalação, inicie uma ROM do SMW e selecione Arquivo > RetroArch. Nenhum outro assistente de instalação é necessário.
brazilianportuguese.ExistingTitle=Configurações existentes encontradas
brazilianportuguese.ExistingSubtitle=Suas configurações atuais serão preservadas.
brazilianportuguese.ExistingDescription=O instalador encontrou SMWStreamTrackerConfig.json no seu perfil e não substituirá o arquivo. Os caminhos das novas ferramentas podem ser escolhidos depois.
brazilianportuguese.ErrorService=O executável do serviço de conexão selecionado não foi encontrado.
brazilianportuguese.ErrorRetroExe=O executável do RetroArch não foi encontrado. Selecione um retroarch.exe válido ou limpe o campo.
brazilianportuguese.ErrorRetroCore=O núcleo SNES não foi encontrado. Selecione um núcleo Libretro válido ou limpe o campo.
brazilianportuguese.RetroInstallProgress=Instalando o RetroArch com seu instalador rápido em segundo plano...
brazilianportuguese.ErrorRetroInstall=Não foi possível instalar o RetroArch. Verifique a conexão com a Internet e execute o instalador novamente.
brazilianportuguese.QUsbInstallProgress=Instalando o QUsb2Snes com o mecanismo rápido de arquivos do Windows...
brazilianportuguese.ErrorQUsbInstall=Não foi possível instalar o QUsb2Snes. Verifique a conexão com a Internet e execute o instalador novamente.
brazilianportuguese.ReadySNI=SNI v0.0.103 (altamente recomendado)
brazilianportuguese.ReadyQUsb=QUsb2Snes 2025-10-20
brazilianportuguese.ReadyRetro=RetroArch portátil 1.22.2 e o núcleo bsnes-mercury Performance
brazilianportuguese.ReadyMiSTer=Detecção e configuração automáticas do MiSTer na primeira abertura
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
brazilianportuguese.ExistingInstallActionTitle=Instalação existente encontrada
brazilianportuguese.ExistingInstallActionSubtitle=Apenas uma cópia do SMW Stream Tracker pode ser instalada nesta conta do Windows.
brazilianportuguese.ExistingInstallActionDescription=Escolha o que o instalador deve fazer. RetroArch, SNI, QUsb2Snes e todos os arquivos de ROM serão preservados.
brazilianportuguese.ExistingInstallFreshOption=Desinstalar a cópia atual e continuar com uma instalação nova
brazilianportuguese.ExistingInstallRemoveOption=Desinstalar completamente o SMW Stream Tracker e sair do instalador
brazilianportuguese.ExistingInstallRemovalFailed=O instalador não conseguiu remover completamente o tracker existente. Feche o SMW Stream Tracker e tente novamente.
brazilianportuguese.ExistingInstallRemovalComplete=O SMW Stream Tracker foi completamente desinstalado. RetroArch, SNI, QUsb2Snes e os arquivos de ROM foram preservados.

[Files]
; The installer keeps this full-width SMW banner visible above every wizard
; page. It is extracted only for the installer's interface and is not copied
; into the installed application folder.
Source: "smw_installer_banner.png"; Flags: dontcopy noencryption
Source: "{#AppExeSource}"; DestDir: "{app}"; DestName: "{#AppExeName}"; Flags: ignoreversion
; Keep Tcl/Tk scripts outside the one-file temporary extraction directory as a
; stable fallback for systems whose security software interrupts _MEI startup.
Source: "..\dist\runtime\tcl\*"; DestDir: "{app}\runtime\tcl"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\dist\runtime\tk\*"; DestDir: "{app}\runtime\tk"; Flags: ignoreversion recursesubdirs createallsubdirs
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

; Recommended live-tracking bridge. Fixed release URLs and official SHA-256
; values keep dependency installs repeatable and reject corrupted downloads.
Source: "https://github.com/alttpo/sni/releases/download/v0.0.103/sni-v0.0.103-windows-amd64.zip"; \
  DestName: "sni-v0.0.103-windows-amd64.zip"; DestDir: "{app}\Tools\SNI"; \
  Hash: "4c0885769518c8b6ed7db038a29fdbdaf28b64c3b54689a5b2e0d6dd33074f87"; \
  ExternalSize: 13307359; Flags: external download extractarchive recursesubdirs ignoreversion uninsneveruninstall; \
  Check: ShouldInstallSNI

; Advanced legacy bridge alternative. Download the verified package first,
; then let Windows' native archive engine unpack its many small files in one
; fast pass during post-install. This avoids Inno's slow per-file extraction.
Source: "https://github.com/usb2snes/usb2snes/releases/download/2025-10-20/QUsb2Snes-bundle-2025-10-20.7z"; \
  DestName: "QUsb2Snes-bundle-2025-10-20.7z"; DestDir: "{tmp}"; \
  Hash: "104c4a01454d4a5e46998b0ddecf3f95ece71853c614e9e906c287f77de9806f"; \
  ExternalSize: 70505572; Flags: external download ignoreversion deleteafterinstall; \
  Check: ShouldInstallQUsb

; Keep the entire RetroArch experience inside this blue installer, but let
; RetroArch's native silent extractor handle its thousands of small assets.
; This avoids the long per-file extraction delay of Inno's archive handler
; without displaying a second setup wizard or launching RetroArch.
Source: "https://buildbot.libretro.com/stable/1.22.2/windows/x86_64/RetroArch-Win64-setup.exe"; \
  DestName: "RetroArch-Win64-setup.exe"; DestDir: "{tmp}"; \
  Hash: "bb2b95329542d98d951bb381c0dd57e803d846242878895f12d374b87201c1c9"; \
  ExternalSize: 209037907; Flags: external download ignoreversion deleteafterinstall; \
  Check: ShouldInstallRetroArch

; The official current bsnes-mercury Performance core is small enough to install directly, which
; removes the most common missing-core first-run error.
Source: "https://buildbot.libretro.com/nightly/windows/x86_64/latest/bsnes_mercury_performance_libretro.dll.zip"; \
  DestName: "bsnes_mercury_performance_libretro.dll.zip"; DestDir: "{tmp}"; \
  ExternalSize: 956416; Flags: external download ignoreversion deleteafterinstall; \
  Check: ShouldInstallRetroArchCore

; A full uninstall removes only tracker-owned state. The user's ROM library and
; OBS output are user-selected external locations and are intentionally never
; referenced here. Optional SNI, QUsb2Snes, and RetroArch files are protected
; above and their in-app-download equivalents below are left in place.
[UninstallDelete]
Type: files; Name: "{%USERPROFILE}\SMWStreamTrackerConfig.json"
Type: files; Name: "{%USERPROFILE}\SMWStreamTrackerTimes.json"
Type: files; Name: "{%USERPROFILE}\SMWStreamTrackerDeaths.json"
Type: files; Name: "{%USERPROFILE}\SMWStreamTrackerLevelProgress.json"
Type: files; Name: "{localappdata}\SMWStreamTracker\SMWStreamTracker.db"
Type: filesandordirs; Name: "{localappdata}\SMWStreamTracker\Backups"
Type: filesandordirs; Name: "{localappdata}\SMWStreamTracker\AutomaticBackups"
Type: filesandordirs; Name: "{localappdata}\SMWStreamTracker\Rollback"
Type: filesandordirs; Name: "{localappdata}\SMWStreamTracker\Updates"
Type: filesandordirs; Name: "{localappdata}\SMWStreamTracker\Logs"
Type: filesandordirs; Name: "{localappdata}\SMWStreamTracker\DependencyDownloads"
Type: filesandordirs; Name: "{localappdata}\SMWStreamTracker\Tools\LiveSplitGameTimer"
Type: filesandordirs; Name: "{localappdata}\SMWStreamTracker\Tools\LiveSplitLevelTimer"
Type: files; Name: "{localappdata}\SMWStreamTracker\UninstallObsOutputPath.txt"

[Icons]
Name: "{group}\SMW Stream Tracker"; Filename: "{app}\{#AppExeName}"
Name: "{group}\RetroArch"; Filename: "{sd}\RetroArch-Win64\retroarch.exe"; Check: ShouldInstallRetroArch
Name: "{group}\{cm:GuideName}"; Filename: "{app}\README.txt"
Name: "{group}\{cm:MarkdownGuideName}"; Filename: "{app}\README.md"
Name: "{autodesktop}\SMW Stream Tracker"; Filename: "{app}\{#AppExeName}"; Check: ShouldCreateDesktopShortcut

[Tasks]
Name: "desktopicon"; Description: "{cm:DesktopShortcut}"; GroupDescription: "{cm:ShortcutGroup}"; Flags: unchecked

[Code]
var
  InstallerBanner: TBitmapImage;
  PlatformPage: TInputOptionWizardPage;
  DependencyPage: TInputOptionWizardPage;
  FolderPage: TInputDirWizardPage;
  FolderOBSLabel: TNewStaticText;
  FolderOBSEdit: TNewEdit;
  FolderOBSBrowseButton: TNewButton;
  FolderOBSNote: TNewStaticText;
  ExistingInterfacePage: TInputFileWizardPage;
  RetroArchPage: TInputFileWizardPage;
  FXPAKStepsPage: TOutputMsgWizardPage;
  RetroArchStepsPage: TOutputMsgWizardPage;
  ExistingConfigPage: TOutputMsgWizardPage;
  ExistingInstallActionPage: TInputOptionWizardPage;
  ExistingInstallationDetected: Boolean;
  ExistingInstallationRemoved: Boolean;
  ExitAfterCompleteUninstall: Boolean;
  ExistingInstallDirectory: String;
  DependencyOptionRows: array[0..3] of TPanel;
  DependencyOptionBoxes: array[0..3] of TBitmapImage;
  DependencyOptionTicks: array[0..3] of TNewStaticText;
  DependencyOptionLabels: array[0..3] of TNewStaticText;
  DesktopShortcutRow: TPanel;
  DesktopShortcutBox: TBitmapImage;
  DesktopShortcutTick: TNewStaticText;
  DesktopShortcutLabel: TNewStaticText;
  FinishOptionRows: array[0..1] of TPanel;
  FinishOptionBoxes: array[0..1] of TBitmapImage;
  FinishOptionTicks: array[0..1] of TNewStaticText;
  FinishOptionLabels: array[0..1] of TNewStaticText;
  DesktopShortcutSelected: Boolean;
  FinishGuideSelected: Boolean;
  FinishAppSelected: Boolean;

function StreamDeskBackground: TColor;
begin
  Result := StrToColor('#0D1216');
end;

function StreamDeskSurface: TColor;
begin
  Result := StrToColor('#11171C');
end;

function StreamDeskSurfaceRaised: TColor;
begin
  Result := StrToColor('#182229');
end;

function StreamDeskSurfaceSelected: TColor;
begin
  Result := StrToColor('#26323B');
end;

function StreamDeskText: TColor;
begin
  Result := StrToColor('#F2F6F8');
end;

function StreamDeskMutedText: TColor;
begin
  Result := StrToColor('#9AA7B0');
end;

function StreamDeskGreen: TColor;
begin
  Result := StrToColor('#68D996');
end;

procedure StyleInstallerMemo(Memo: TNewMemo);
begin
  Memo.Color := StreamDeskSurface;
  Memo.Font.Color := StreamDeskText;
end;

procedure StyleInstallerEdit(Edit: TNewEdit);
begin
  Edit.Color := StreamDeskSurfaceRaised;
  Edit.Font.Color := StreamDeskText;
end;

procedure StyleInputOptionPage(Page: TInputOptionWizardPage);
begin
  if Page = nil then
    Exit;
  Page.Surface.Color := StreamDeskBackground;
  Page.CheckListBox.Color := StreamDeskSurface;
  Page.CheckListBox.Font.Color := StreamDeskText;
end;

procedure StyleInputDirPage(Page: TInputDirWizardPage; EditCount: Integer);
var
  I: Integer;
begin
  Page.Surface.Color := StreamDeskBackground;
  for I := 0 to EditCount - 1 do
  begin
    Page.Edits[I].Color := StreamDeskSurfaceRaised;
    Page.Edits[I].Font.Color := StreamDeskText;
  end;
end;

procedure StyleInputFilePage(Page: TInputFileWizardPage; EditCount: Integer);
var
  I: Integer;
begin
  Page.Surface.Color := StreamDeskBackground;
  for I := 0 to EditCount - 1 do
  begin
    Page.Edits[I].Color := StreamDeskSurfaceRaised;
    Page.Edits[I].Font.Color := StreamDeskText;
  end;
end;

procedure StyleOutputMessagePage(Page: TOutputMsgWizardPage);
begin
  Page.Surface.Color := StreamDeskBackground;
  Page.MsgLabel.Font.Color := StreamDeskText;
end;

procedure ConfigureInstallerTheme;
var
  BannerFile: String;
  BannerWidth: Integer;
  BannerHeight: Integer;
  MaximumBannerWidth: Integer;
  ContentTop: Integer;
  ContentBottom: Integer;
begin
  { Match the app's Stream Desk shell instead of the former blue setup UI. }
  WizardForm.Color := StreamDeskBackground;
  WizardForm.MainPanel.Color := StreamDeskSurface;
  WizardForm.WelcomePage.Color := StreamDeskBackground;
  WizardForm.LicensePage.Color := StreamDeskBackground;
  WizardForm.InfoBeforePage.Color := StreamDeskBackground;
  WizardForm.SelectDirPage.Color := StreamDeskBackground;
  WizardForm.SelectProgramGroupPage.Color := StreamDeskBackground;
  WizardForm.SelectTasksPage.Color := StreamDeskBackground;
  WizardForm.ReadyPage.Color := StreamDeskBackground;
  WizardForm.PreparingPage.Color := StreamDeskBackground;
  WizardForm.InstallingPage.Color := StreamDeskBackground;
  WizardForm.InfoAfterPage.Color := StreamDeskBackground;
  WizardForm.FinishedPage.Color := StreamDeskBackground;
  WizardForm.PageNameLabel.Font.Color := StreamDeskText;
  WizardForm.PageDescriptionLabel.Font.Color := StreamDeskMutedText;
  WizardForm.WelcomeLabel1.Font.Color := StreamDeskText;
  WizardForm.WelcomeLabel2.Font.Color := StreamDeskMutedText;
  WizardForm.FinishedHeadingLabel.Font.Color := StreamDeskText;
  WizardForm.FinishedLabel.Font.Color := StreamDeskMutedText;
  WizardForm.LicenseMemo.Color := StreamDeskSurface;
  WizardForm.LicenseMemo.Font.Color := StreamDeskText;
  WizardForm.InfoBeforeMemo.Color := StreamDeskSurface;
  WizardForm.InfoBeforeMemo.Font.Color := StreamDeskText;
  WizardForm.InfoAfterMemo.Color := StreamDeskSurface;
  WizardForm.InfoAfterMemo.Font.Color := StreamDeskText;
  WizardForm.ReadyMemo.Color := StreamDeskSurface;
  WizardForm.ReadyMemo.Font.Color := StreamDeskText;
  WizardForm.PreparingLabel.Font.Color := StreamDeskText;
  WizardForm.StatusLabel.Font.Color := StreamDeskText;
  WizardForm.FileNameLabel.Font.Color := StreamDeskMutedText;
  WizardForm.NextButton.Font.Style := [fsBold];
  WizardForm.BackButton.Font.Style := [fsBold];
  WizardForm.CancelButton.Font.Style := [fsBold];

  BannerFile := ExpandConstant('{tmp}\smw_installer_banner.png');
  ExtractTemporaryFile(ExtractFileName(BannerFile));

  InstallerBanner := TBitmapImage.Create(WizardForm);
  InstallerBanner.Parent := WizardForm;
  InstallerBanner.BackColor := StreamDeskBackground;
  InstallerBanner.Center := True;
  InstallerBanner.Stretch := True;
  InstallerBanner.PngImage.LoadFromFile(BannerFile);

  BannerHeight := ScaleY(150);
  BannerWidth := MulDiv(BannerHeight, 1039, 292);
  MaximumBannerWidth := WizardForm.ClientWidth - ScaleX(24);
  if BannerWidth > MaximumBannerWidth then
  begin
    BannerWidth := MaximumBannerWidth;
    BannerHeight := MulDiv(BannerWidth, 292, 1039);
  end;

  InstallerBanner.Left := (WizardForm.ClientWidth - BannerWidth) div 2;
  InstallerBanner.Top := ScaleY(10);
  InstallerBanner.Width := BannerWidth;
  InstallerBanner.Height := BannerHeight;

  ContentTop := InstallerBanner.Top + InstallerBanner.Height + ScaleY(10);
  ContentBottom := WizardForm.NextButton.Top - ScaleY(10);
  WizardForm.OuterNotebook.Left := ScaleX(12);
  WizardForm.OuterNotebook.Top := ContentTop;
  WizardForm.OuterNotebook.Width := WizardForm.ClientWidth - ScaleX(24);
  WizardForm.OuterNotebook.Height := ContentBottom - ContentTop;

  WizardForm.WizardBitmapImage.Visible := False;
  WizardForm.WizardSmallBitmapImage.Visible := False;

  WizardForm.WelcomeLabel1.AutoSize := False;
  WizardForm.WelcomeLabel1.Alignment := taCenter;
  WizardForm.WelcomeLabel1.Left := ScaleX(24);
  WizardForm.WelcomeLabel1.Width :=
    WizardForm.WelcomePage.ClientWidth - ScaleX(48);
  WizardForm.WelcomeLabel1.AdjustHeight;
  WizardForm.WelcomeLabel2.AutoSize := False;
  WizardForm.WelcomeLabel2.Alignment := taCenter;
  WizardForm.WelcomeLabel2.Left := ScaleX(24);
  WizardForm.WelcomeLabel2.Width :=
    WizardForm.WelcomePage.ClientWidth - ScaleX(48);

  WizardForm.FinishedHeadingLabel.AutoSize := False;
  WizardForm.FinishedHeadingLabel.Alignment := taCenter;
  WizardForm.FinishedHeadingLabel.Left := ScaleX(24);
  WizardForm.FinishedHeadingLabel.Width :=
    WizardForm.FinishedPage.ClientWidth - ScaleX(48);
  WizardForm.FinishedHeadingLabel.AdjustHeight;
  WizardForm.FinishedLabel.AutoSize := False;
  WizardForm.FinishedLabel.Alignment := taCenter;
  WizardForm.FinishedLabel.Left := ScaleX(24);
  WizardForm.FinishedLabel.Width :=
    WizardForm.FinishedPage.ClientWidth - ScaleX(48);
end;

procedure PaintGreenCheckbox(Box: TBitmapImage; IsChecked: Boolean);
var
  BoxWidth: Integer;
  BoxHeight: Integer;
begin
  BoxWidth := Box.Width;
  BoxHeight := Box.Height;
  Box.Bitmap.Width := BoxWidth;
  Box.Bitmap.Height := BoxHeight;

  if IsChecked then
  begin
    Box.Bitmap.Canvas.Brush.Color := StreamDeskGreen;
    Box.Bitmap.Canvas.Pen.Color := StreamDeskGreen;
  end
  else
  begin
    Box.Bitmap.Canvas.Brush.Color := StreamDeskSurfaceRaised;
    Box.Bitmap.Canvas.Pen.Color := StreamDeskMutedText;
  end;
  Box.Bitmap.Canvas.Pen.Width := 1;
  Box.Bitmap.Canvas.Rectangle(0, 0, BoxWidth, BoxHeight);

  if IsChecked then
  begin
    { Draw the app-style white check directly onto the green square. }
    Box.Bitmap.Canvas.Pen.Color := StreamDeskText;
    Box.Bitmap.Canvas.Pen.Width := BoxWidth div 6;
    if Box.Bitmap.Canvas.Pen.Width < 2 then
      Box.Bitmap.Canvas.Pen.Width := 2;
    Box.Bitmap.Canvas.MoveTo(BoxWidth div 5, BoxHeight div 2);
    Box.Bitmap.Canvas.LineTo((BoxWidth * 2) div 5, (BoxHeight * 3) div 4);
    Box.Bitmap.Canvas.LineTo((BoxWidth * 4) div 5, BoxHeight div 4);
  end;
  Box.Repaint;
end;

procedure SetGreenCheckboxAppearance(
  Row: TPanel;
  Box: TBitmapImage;
  Tick: TNewStaticText;
  LabelControl: TNewStaticText;
  IsChecked: Boolean);
begin
  if IsChecked then
  begin
    Row.Color := StreamDeskSurfaceSelected;
    Tick.Visible := False;
    LabelControl.Font.Color := StreamDeskText;
  end
  else
  begin
    Row.Color := StreamDeskSurface;
    Tick.Visible := False;
    LabelControl.Font.Color := StreamDeskMutedText;
  end;
  PaintGreenCheckbox(Box, IsChecked);
  Row.Repaint;
  Tick.Repaint;
  LabelControl.Repaint;
end;

procedure CreateGreenCheckboxRow(
  OwnerComponent: TComponent;
  ParentControl: TWinControl;
  var Row: TPanel;
  var Box: TBitmapImage;
  var Tick: TNewStaticText;
  var LabelControl: TNewStaticText;
  RowLeft, RowTop, RowWidth, RowHeight: Integer;
  RowCaption: String;
  ClickHandler: TNotifyEvent);
begin
  Row := TPanel.Create(OwnerComponent);
  Row.Parent := ParentControl;
  Row.Left := RowLeft;
  Row.Top := RowTop;
  Row.Width := RowWidth;
  Row.Height := RowHeight;
  Row.Caption := '';
  Row.BevelOuter := bvNone;
  Row.ParentBackground := False;
  Row.ParentColor := False;
  Row.Color := StreamDeskSurface;
  Row.OnClick := ClickHandler;

  Box := TBitmapImage.Create(OwnerComponent);
  Box.Parent := Row;
  Box.Left := ScaleX(12);
  Box.Top := (Row.Height - ScaleY(14)) div 2;
  Box.Width := ScaleX(14);
  Box.Height := ScaleY(14);
  Box.AutoSize := False;
  Box.Stretch := False;
  Box.Center := False;
  Box.OnClick := ClickHandler;

  Tick := TNewStaticText.Create(OwnerComponent);
  Tick.Parent := Row;
  Tick.Left := Box.Left;
  Tick.Top := Box.Top;
  Tick.Width := Box.Width;
  Tick.Height := Box.Height;
  Tick.AutoSize := False;
  Tick.Alignment := taCenter;
  Tick.ParentColor := False;
  Tick.Color := StreamDeskSurfaceRaised;
  Tick.Font.Color := StreamDeskBackground;
  Tick.Font.Size := 8;
  Tick.Font.Style := [fsBold];
  Tick.Visible := False;
  Tick.OnClick := ClickHandler;

  PaintGreenCheckbox(Box, False);

  LabelControl := TNewStaticText.Create(OwnerComponent);
  LabelControl.Parent := Row;
  LabelControl.Left := ScaleX(36);
  LabelControl.Top := (Row.Height - ScaleY(34)) div 2;
  LabelControl.Width := Row.Width - LabelControl.Left - ScaleX(12);
  LabelControl.Height := ScaleY(34);
  LabelControl.AutoSize := False;
  LabelControl.WordWrap := True;
  LabelControl.Caption := RowCaption;
  LabelControl.Font.Color := StreamDeskMutedText;
  LabelControl.Font.Style := [fsBold];
  LabelControl.OnClick := ClickHandler;
end;

procedure RefreshDependencyOptionRows;
var
  I: Integer;
begin
  for I := 0 to 3 do
    SetGreenCheckboxAppearance(
      DependencyOptionRows[I],
      DependencyOptionBoxes[I],
      DependencyOptionTicks[I],
      DependencyOptionLabels[I],
      DependencyPage.Values[I]);
end;

procedure ToggleDependencyOption(Index: Integer);
begin
  DependencyPage.Values[Index] := not DependencyPage.Values[Index];
  RefreshDependencyOptionRows;
end;

procedure ToggleDependencyOption0(Sender: TObject);
begin
  ToggleDependencyOption(0);
end;

procedure ToggleDependencyOption1(Sender: TObject);
begin
  ToggleDependencyOption(1);
end;

procedure ToggleDependencyOption2(Sender: TObject);
begin
  ToggleDependencyOption(2);
end;

procedure ToggleDependencyOption3(Sender: TObject);
begin
  ToggleDependencyOption(3);
end;

procedure CreateDependencyOptionRows;
var
  RowHeight: Integer;
  RowGap: Integer;
  RowTop: Integer;
begin
  RowGap := ScaleY(6);
  { The native checklist can report a height extending below the visible }
  { wizard surface at large DPI settings. Compact fixed rows keep all four }
  { dependency choices above the navigation buttons on every supported size. }
  RowHeight := ScaleY(44);
  RowTop := DependencyPage.CheckListBox.Top;

  CreateGreenCheckboxRow(
    DependencyPage, DependencyPage.Surface,
    DependencyOptionRows[0], DependencyOptionBoxes[0],
    DependencyOptionTicks[0], DependencyOptionLabels[0],
    DependencyPage.CheckListBox.Left, RowTop,
    DependencyPage.CheckListBox.Width, RowHeight,
    ExpandConstant('{cm:SNIOption}'), @ToggleDependencyOption0);
  RowTop := RowTop + RowHeight + RowGap;
  CreateGreenCheckboxRow(
    DependencyPage, DependencyPage.Surface,
    DependencyOptionRows[1], DependencyOptionBoxes[1],
    DependencyOptionTicks[1], DependencyOptionLabels[1],
    DependencyPage.CheckListBox.Left, RowTop,
    DependencyPage.CheckListBox.Width, RowHeight,
    ExpandConstant('{cm:QUsbOption}'), @ToggleDependencyOption1);
  RowTop := RowTop + RowHeight + RowGap;
  CreateGreenCheckboxRow(
    DependencyPage, DependencyPage.Surface,
    DependencyOptionRows[2], DependencyOptionBoxes[2],
    DependencyOptionTicks[2], DependencyOptionLabels[2],
    DependencyPage.CheckListBox.Left, RowTop,
    DependencyPage.CheckListBox.Width, RowHeight,
    ExpandConstant('{cm:RetroArchInstallOption}'), @ToggleDependencyOption2);
  RowTop := RowTop + RowHeight + RowGap;
  CreateGreenCheckboxRow(
    DependencyPage, DependencyPage.Surface,
    DependencyOptionRows[3], DependencyOptionBoxes[3],
    DependencyOptionTicks[3], DependencyOptionLabels[3],
    DependencyPage.CheckListBox.Left, RowTop,
    DependencyPage.CheckListBox.Width, RowHeight,
    ExpandConstant('{cm:MiSTerSetupOption}'), @ToggleDependencyOption3);

  DependencyPage.CheckListBox.Visible := False;
  RefreshDependencyOptionRows;
end;

procedure RefreshDesktopShortcutRow;
begin
  SetGreenCheckboxAppearance(
    DesktopShortcutRow,
    DesktopShortcutBox,
    DesktopShortcutTick,
    DesktopShortcutLabel,
    DesktopShortcutSelected);
end;

procedure ToggleDesktopShortcut(Sender: TObject);
begin
  DesktopShortcutSelected := not DesktopShortcutSelected;
  if WizardForm.TasksList.Items.Count > 0 then
    WizardForm.TasksList.Checked[0] := DesktopShortcutSelected;
  RefreshDesktopShortcutRow;
end;

procedure CreateDesktopShortcutRow;
begin
  WizardForm.SelectTasksPage.Color := StreamDeskBackground;
  CreateGreenCheckboxRow(
    WizardForm, WizardForm.SelectTasksPage,
    DesktopShortcutRow, DesktopShortcutBox,
    DesktopShortcutTick, DesktopShortcutLabel,
    WizardForm.TasksList.Left, WizardForm.TasksList.Top,
    WizardForm.TasksList.Width, ScaleY(58),
    ExpandConstant('{cm:DesktopShortcut}'), @ToggleDesktopShortcut);
  WizardForm.TasksList.Visible := False;
  RefreshDesktopShortcutRow;
end;

procedure RefreshFinishOptionRows;
begin
  SetGreenCheckboxAppearance(
    FinishOptionRows[0],
    FinishOptionBoxes[0],
    FinishOptionTicks[0],
    FinishOptionLabels[0],
    FinishGuideSelected);
  SetGreenCheckboxAppearance(
    FinishOptionRows[1],
    FinishOptionBoxes[1],
    FinishOptionTicks[1],
    FinishOptionLabels[1],
    FinishAppSelected);
end;

procedure SyncFinishOptionList;
begin
  { Finish actions are owned by the themed rows.  Keeping [Run] empty avoids }
  { Inno repainting a second checkbox list over this finished-page layout. }
end;

procedure ToggleFinishGuide(Sender: TObject);
begin
  FinishGuideSelected := not FinishGuideSelected;
  RefreshFinishOptionRows;
end;

procedure ToggleFinishApp(Sender: TObject);
begin
  FinishAppSelected := not FinishAppSelected;
  RefreshFinishOptionRows;
end;

procedure HideNativeFinishRunList;
begin
  { The installer deliberately has no postinstall [Run] entries.  Hide the }
  { unused native host so the themed rows are the only finish-page controls. }
  WizardForm.RunList.Visible := False;
  WizardForm.RunList.Enabled := False;
  WizardForm.RunList.Left := -WizardForm.RunList.Width - ScaleX(64);
  WizardForm.RunList.Top := -WizardForm.RunList.Height - ScaleY(64);
end;

procedure CreateFinishOptionRows;
var
  RowTop: Integer;
  RowLeft: Integer;
  RowWidth: Integer;
begin
  RowTop := WizardForm.RunList.Top;
  RowLeft := WizardForm.RunList.Left;
  RowWidth := WizardForm.RunList.Width;
  CreateGreenCheckboxRow(
    WizardForm, WizardForm.FinishedPage,
    FinishOptionRows[0], FinishOptionBoxes[0],
    FinishOptionTicks[0], FinishOptionLabels[0],
    RowLeft, RowTop,
    RowWidth, ScaleY(54),
    ExpandConstant('{cm:OpenGuide}'), @ToggleFinishGuide);
  RowTop := RowTop + ScaleY(62);
  CreateGreenCheckboxRow(
    WizardForm, WizardForm.FinishedPage,
    FinishOptionRows[1], FinishOptionBoxes[1],
    FinishOptionTicks[1], FinishOptionLabels[1],
    RowLeft, RowTop,
    RowWidth, ScaleY(54),
    ExpandConstant('{cm:LaunchApp}'), @ToggleFinishApp);
  HideNativeFinishRunList;
  RefreshFinishOptionRows;
end;

procedure ApplyCustomInstallerPageTheme;
begin
  StyleInputOptionPage(ExistingInstallActionPage);
  StyleInputOptionPage(PlatformPage);
  StyleInputOptionPage(DependencyPage);
  StyleInputDirPage(FolderPage, 1);
  StyleInstallerEdit(FolderOBSEdit);
  FolderOBSLabel.Font.Color := StreamDeskText;
  FolderOBSNote.Font.Color := StreamDeskMutedText;
  StyleInputFilePage(ExistingInterfacePage, 1);
  StyleInputFilePage(RetroArchPage, 2);
  StyleOutputMessagePage(FXPAKStepsPage);
  StyleOutputMessagePage(RetroArchStepsPage);
  StyleOutputMessagePage(ExistingConfigPage);
end;

function ConfigFilePath: String;
begin
  Result := ExpandConstant('{%USERPROFILE}\SMWStreamTrackerConfig.json');
end;

function UninstallObsPathFile: String;
begin
  Result := ExpandConstant(
    '{localappdata}\SMWStreamTracker\UninstallObsOutputPath.txt'
  );
end;

procedure DeleteTrackerObsOutputFiles;
var
  OutputFolder: String;
  OutputFolderLines: TArrayOfString;
begin
  if not LoadStringsFromFile(UninstallObsPathFile(), OutputFolderLines) then
    Exit;
  if GetArrayLength(OutputFolderLines) = 0 then
    Exit;

  OutputFolder := OutputFolderLines[0];
  OutputFolder := Trim(OutputFolder);
  if (OutputFolder = '') or (Length(OutputFolder) < 4) or
     (not DirExists(OutputFolder)) then
    Exit;

  { Delete only filenames owned by SMW Stream Tracker. Never delete the
    selected OBS folder itself unless it is empty, and never recurse through
    an external user folder. }
  DeleteFile(AddBackslash(OutputFolder) + 'author.txt');
  DeleteFile(AddBackslash(OutputFolder) + 'exits.txt');
  DeleteFile(AddBackslash(OutputFolder) + 'level_deaths.txt');
  DeleteFile(AddBackslash(OutputFolder) + 'death_counter.txt');
  DeleteFile(AddBackslash(OutputFolder) + 'total_deaths.txt');
  DeleteFile(AddBackslash(OutputFolder) + 'hack_name.txt');
  DeleteFile(AddBackslash(OutputFolder) + 'level_timer.txt');
  DeleteFile(AddBackslash(OutputFolder) + 'game_timer.txt');
  DeleteFile(AddBackslash(OutputFolder) + 'SMWTracker.log');
  RemoveDir(OutputFolder);
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  { usUninstall is reached only after the user confirms removal. Merely opening
    the uninstaller and cancelling it must never delete OBS output files. }
  if CurUninstallStep = usUninstall then
    DeleteTrackerObsOutputFiles;
end;

function DefaultTrackerInstallDirectory: String;
begin
  Result := ExpandConstant('{localappdata}\Programs\SMW Stream Tracker');
end;

function ExistingUninstallRegistryKey: String;
begin
  Result :=
    'Software\Microsoft\Windows\CurrentVersion\Uninstall\' +
    '{E7C2CB0B-73BC-4DEA-8D78-90B9A3BA9CB6}_is1';
end;

function RegistryContainsExistingTracker(
  RootKey: Integer;
  var InstallDirectory: String
): Boolean;
var
  UninstallCommand: String;
begin
  Result := RegQueryStringValue(
    RootKey,
    ExistingUninstallRegistryKey(),
    'UninstallString',
    UninstallCommand
  );
  if Result then
  begin
    if not RegQueryStringValue(
      RootKey,
      ExistingUninstallRegistryKey(),
      'InstallLocation',
      InstallDirectory
    ) then
      InstallDirectory := '';
  end;
end;

function FindExistingTrackerInstallation(
  var InstallDirectory: String
): Boolean;
begin
  InstallDirectory := '';
  Result := RegistryContainsExistingTracker(HKCU, InstallDirectory);
  if (not Result) and IsWin64 then
    Result := RegistryContainsExistingTracker(HKLM64, InstallDirectory);
  if not Result then
    Result := RegistryContainsExistingTracker(HKLM32, InstallDirectory);

  if Trim(InstallDirectory) = '' then
    InstallDirectory := DefaultTrackerInstallDirectory();

  if FileExists(
    AddBackslash(InstallDirectory) + '{#AppExeName}'
  ) then
    Result := True;
end;

procedure DeleteTrackerOwnedState;
var
  DataDirectory: String;
begin
  DeleteTrackerObsOutputFiles;

  DeleteFile(ConfigFilePath());
  DeleteFile(ExpandConstant('{%USERPROFILE}\SMWStreamTrackerTimes.json'));
  DeleteFile(ExpandConstant('{%USERPROFILE}\SMWStreamTrackerDeaths.json'));
  DeleteFile(ExpandConstant(
    '{%USERPROFILE}\SMWStreamTrackerLevelProgress.json'
  ));

  DataDirectory := ExpandConstant('{localappdata}\SMWStreamTracker');
  DeleteFile(AddBackslash(DataDirectory) + 'SMWStreamTracker.db');
  DeleteFile(AddBackslash(DataDirectory) + 'UninstallObsOutputPath.txt');
  DelTree(AddBackslash(DataDirectory) + 'Backups', True, True, True);
  DelTree(AddBackslash(DataDirectory) + 'AutomaticBackups', True, True, True);
  DelTree(AddBackslash(DataDirectory) + 'Rollback', True, True, True);
  DelTree(AddBackslash(DataDirectory) + 'Updates', True, True, True);
  DelTree(AddBackslash(DataDirectory) + 'Logs', True, True, True);
  DelTree(AddBackslash(DataDirectory) + 'DependencyDownloads', True, True, True);
  DelTree(
    AddBackslash(DataDirectory) + 'Tools\LiveSplit Game Timer',
    True,
    True,
    True
  );
  DelTree(
    AddBackslash(DataDirectory) + 'Tools\LiveSplit Level Timer',
    True,
    True,
    True
  );
  DelTree(
    AddBackslash(DataDirectory) + 'Tools\LiveSplitGameTimer',
    True,
    True,
    True
  );
  DelTree(
    AddBackslash(DataDirectory) + 'Tools\LiveSplitLevelTimer',
    True,
    True,
    True
  );
end;

procedure DeleteKnownTrackerApplicationFiles(InstallDirectory: String);
begin
  if Trim(InstallDirectory) = '' then
    InstallDirectory := DefaultTrackerInstallDirectory();

  DeleteFile(AddBackslash(InstallDirectory) + '{#AppExeName}');
  DelTree(AddBackslash(InstallDirectory) + 'runtime', True, True, True);
  DelTree(AddBackslash(InstallDirectory) + 'Documentation', True, True, True);
  DeleteFile(AddBackslash(InstallDirectory) + 'README.md');
  DeleteFile(AddBackslash(InstallDirectory) + 'README.txt');
  DeleteFile(AddBackslash(InstallDirectory) + 'rollback_update.ps1');
  DeleteFile(AddBackslash(InstallDirectory) + 'PRIVACY.txt');
  DeleteFile(AddBackslash(InstallDirectory) + 'LICENSE.txt');
  DeleteFile(AddBackslash(InstallDirectory) + 'THIRD_PARTY_NOTICE.txt');
  DeleteFile(AddBackslash(InstallDirectory) + 'unins000.exe');
  DeleteFile(AddBackslash(InstallDirectory) + 'unins000.dat');

  DeleteFile(ExpandConstant('{userdesktop}\SMW Stream Tracker.lnk'));
  DeleteFile(ExpandConstant('{commondesktop}\SMW Stream Tracker.lnk'));
  DelTree(
    ExpandConstant('{userprograms}\SMW Stream Tracker'),
    True,
    True,
    True
  );
end;

function RemoveExistingTrackerInstallation: Boolean;
begin
  DeleteTrackerOwnedState;
  DeleteKnownTrackerApplicationFiles(ExistingInstallDirectory);

  RegDeleteKeyIncludingSubkeys(HKCU, ExistingUninstallRegistryKey());
  if IsWin64 then
    RegDeleteKeyIncludingSubkeys(HKLM64, ExistingUninstallRegistryKey());
  RegDeleteKeyIncludingSubkeys(HKLM32, ExistingUninstallRegistryKey());

  Result := not FileExists(
    AddBackslash(ExistingInstallDirectory) + '{#AppExeName}'
  );
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
  SelectedDirectory := FolderOBSEdit.Text;
  if Trim(SelectedDirectory) = '' then
    SelectedDirectory := ExpandConstant('{userdocs}');
  if BrowseForFolder(
       ExpandConstant('{cm:OBSFolder}'),
       SelectedDirectory,
       True) then
    FolderOBSEdit.Text := SelectedDirectory;
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
var
  PlatformPreviousPageID: Integer;
begin
  ConfigureInstallerTheme;

  { The native TasksList and RunList receive their entries later in the }
  { wizard lifecycle. Keep the custom rows safe and deterministic until then. }
  DesktopShortcutSelected := False;
  FinishGuideSelected := False;
  FinishAppSelected := True;

  ExistingInstallationDetected := FindExistingTrackerInstallation(
    ExistingInstallDirectory
  );
  ExistingInstallationRemoved := False;
  ExitAfterCompleteUninstall := False;
  PlatformPreviousPageID := wpSelectDir;

  if ExistingInstallationDetected then
  begin
    ExistingInstallActionPage := CreateInputOptionPage(
      wpWelcome,
      ExpandConstant('{cm:ExistingInstallActionTitle}'),
      ExpandConstant('{cm:ExistingInstallActionSubtitle}'),
      ExpandConstant('{cm:ExistingInstallActionDescription}'),
      True,
      False
    );
    ExistingInstallActionPage.Add(
      ExpandConstant('{cm:ExistingInstallFreshOption}')
    );
    ExistingInstallActionPage.Add(
      ExpandConstant('{cm:ExistingInstallRemoveOption}')
    );
    ExistingInstallActionPage.SelectedValueIndex := 0;
    PlatformPreviousPageID := ExistingInstallActionPage.ID;
  end;

  PlatformPage := CreateInputOptionPage(
    PlatformPreviousPageID,
    ExpandConstant('{cm:PlatformTitle}'),
    ExpandConstant('{cm:PlatformSubtitle}'),
    ExpandConstant('{cm:PlatformDescription}'),
    True,
    False);
  PlatformPage.Add(ExpandConstant('{cm:FXPAKOption}'));
  PlatformPage.Add(ExpandConstant('{cm:RetroArchOption}'));
  PlatformPage.Add(ExpandConstant('{cm:MiSTerOption}'));
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
  DependencyPage.Add(ExpandConstant('{cm:MiSTerSetupOption}'));
  DependencyPage.Values[0] := True;
  DependencyPage.Values[1] := False;
  DependencyPage.Values[2] := False;
  DependencyPage.Values[3] := False;

  FolderPage := CreateInputDirPage(
    DependencyPage.ID,
    ExpandConstant('{cm:FolderTitle}'),
    ExpandConstant('{cm:FolderSubtitle}'),
    ExpandConstant('{cm:FolderDescription}'),
    False,
    SetupMessage(msgNewFolderName));
  FolderPage.Add(ExpandConstant('{cm:ROMLibrary}'));
  FolderPage.Values[0] := '';
  FolderPage.Buttons[0].OnClick := @BrowseForRomLibrary;

  { TInputDirWizardPage requires every field added with Add(). Keep the }
  { OBS path outside that required list so the user can leave it blank. }
  FolderOBSLabel := TNewStaticText.Create(FolderPage);
  FolderOBSLabel.Parent := FolderPage.Surface;
  FolderOBSLabel.Caption := ExpandConstant('{cm:OBSFolder}');
  FolderOBSLabel.AutoSize := True;
  FolderOBSLabel.Left := FolderPage.Edits[0].Left;
  FolderOBSLabel.Top :=
    FolderPage.Edits[0].Top + FolderPage.Edits[0].Height + ScaleY(18);

  FolderOBSEdit := TNewEdit.Create(FolderPage);
  FolderOBSEdit.Parent := FolderPage.Surface;
  FolderOBSEdit.Left := FolderPage.Edits[0].Left;
  FolderOBSEdit.Top :=
    FolderOBSLabel.Top + FolderOBSLabel.Height + ScaleY(4);
  FolderOBSEdit.Width := FolderPage.Edits[0].Width;
  FolderOBSEdit.Height := FolderPage.Edits[0].Height;
  FolderOBSEdit.Text := '';
  FolderOBSEdit.TabOrder := FolderPage.Edits[0].TabOrder + 1;

  FolderOBSBrowseButton := TNewButton.Create(FolderPage);
  FolderOBSBrowseButton.Parent := FolderPage.Surface;
  FolderOBSBrowseButton.Caption := FolderPage.Buttons[0].Caption;
  FolderOBSBrowseButton.Left := FolderPage.Buttons[0].Left;
  FolderOBSBrowseButton.Top := FolderOBSEdit.Top;
  FolderOBSBrowseButton.Width := FolderPage.Buttons[0].Width;
  FolderOBSBrowseButton.Height := FolderPage.Buttons[0].Height;
  FolderOBSBrowseButton.TabOrder := FolderOBSEdit.TabOrder + 1;
  FolderOBSBrowseButton.OnClick := @BrowseForObsFolder;

  FolderOBSNote := TNewStaticText.Create(FolderPage);
  FolderOBSNote.Parent := FolderPage.Surface;
  FolderOBSNote.Caption := ExpandConstant('{cm:OBSFolderNote}');
  FolderOBSNote.AutoSize := False;
  FolderOBSNote.WordWrap := True;
  FolderOBSNote.Left := FolderOBSEdit.Left;
  FolderOBSNote.Top :=
    FolderOBSEdit.Top + FolderOBSEdit.Height + ScaleY(12);
  FolderOBSNote.Width :=
    FolderOBSBrowseButton.Left + FolderOBSBrowseButton.Width -
    FolderOBSNote.Left;
  FolderOBSNote.Height := ScaleY(54);

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

  { Apply the Stream Desk palette after every custom page exists, then }
  { replace Inno Setup's native checkbox lists with the app-style rows. }
  ApplyCustomInstallerPageTheme;
  CreateDependencyOptionRows;
  CreateDesktopShortcutRow;
  CreateFinishOptionRows;
end;

procedure CurPageChanged(CurPageID: Integer);
begin
  if CurPageID = wpSelectTasks then
  begin
    if WizardForm.TasksList.Items.Count > 0 then
      WizardForm.TasksList.Checked[0] := DesktopShortcutSelected;
    RefreshDesktopShortcutRow;
  end;

  if CurPageID = wpFinished then
  begin
    HideNativeFinishRunList;
    FinishOptionRows[0].BringToFront;
    FinishOptionRows[1].BringToFront;
    RefreshFinishOptionRows;
  end;
end;

function ShouldInstallSNI: Boolean;
begin
  Result := DependencyPage.Values[0];
end;

function ShouldCreateDesktopShortcut: Boolean;
begin
  { The themed checkbox is authoritative during interactive setup. Keep
    /TASKS=desktopicon working for silent and managed installations too. }
  Result := DesktopShortcutSelected or WizardIsTaskSelected('desktopicon');
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

function ShouldSetUpMiSTer: Boolean;
begin
  Result := (PlatformPage.SelectedValueIndex = 2) or DependencyPage.Values[3];
end;

function RetroArchCoreDirectory(Param: String): String;
begin
  Result := ExpandConstant('{sd}\RetroArch-Win64\cores');
end;

function ShouldSkipPage(PageID: Integer): Boolean;
var
  WantsRetroArch: Boolean;
begin
  WantsRetroArch :=
    (PlatformPage.SelectedValueIndex = 1) or
    DependencyPage.Values[2];

  if PageID = ExistingInterfacePage.ID then
    Result := DependencyPage.Values[0] or DependencyPage.Values[1] or
      ShouldSetUpMiSTer()
  else if PageID = RetroArchPage.ID then
    Result := (not WantsRetroArch) or DependencyPage.Values[2]
  else if PageID = FXPAKStepsPage.ID then
    Result := (PlatformPage.SelectedValueIndex <> 0) or ShouldSetUpMiSTer()
  else if PageID = RetroArchStepsPage.ID then
    Result := not WantsRetroArch
  else if PageID = ExistingConfigPage.ID then
    Result := not FileExists(ConfigFilePath)
  else
    Result := False;
end;

procedure RunSelectedFinishOptions;
var
  ResultCode: Integer;
begin
  ResultCode := -1;
  if FinishGuideSelected then
    ShellExec(
      'open',
      ExpandConstant('{app}\README.txt'),
      '',
      ExpandConstant('{app}'),
      SW_SHOWNORMAL,
      ewNoWait,
      ResultCode
    );
  if FinishAppSelected then
    Exec(
      ExpandConstant('{app}\{#AppExeName}'),
      '',
      ExpandConstant('{app}'),
      SW_SHOWNORMAL,
      ewNoWait,
      ResultCode
    );
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;

  if CurPageID = wpFinished then
  begin
    RunSelectedFinishOptions;
    Exit;
  end;

  if ExistingInstallationDetected then
  begin
    if (not ExistingInstallationRemoved) and
       (CurPageID = ExistingInstallActionPage.ID) then
    begin
      if not RemoveExistingTrackerInstallation() then
      begin
        MsgBox(
          ExpandConstant('{cm:ExistingInstallRemovalFailed}'),
          mbError,
          MB_OK
        );
        Result := False;
      end
      else
      begin
        ExistingInstallationRemoved := True;
        if ExistingInstallActionPage.SelectedValueIndex = 1 then
        begin
          MsgBox(
            ExpandConstant('{cm:ExistingInstallRemovalComplete}'),
            mbInformation,
            MB_OK
          );
          ExitAfterCompleteUninstall := True;
          Result := False;
          WizardForm.Close;
        end;
      end;
      Exit;
    end;
  end;

  if CurPageID = PlatformPage.ID then
  begin
    if PlatformPage.SelectedValueIndex = 1 then
    begin
      DependencyPage.Values[0] := True;
      DependencyPage.Values[2] := True;
      DependencyPage.Values[3] := False;
    end
    else if PlatformPage.SelectedValueIndex = 2 then
    begin
      DependencyPage.Values[0] := True;
      DependencyPage.Values[1] := False;
      DependencyPage.Values[2] := False;
      DependencyPage.Values[3] := True;
    end;
    RefreshDependencyOptionRows;
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

function JsonBoolean(Value: Boolean): String;
begin
  if Value then
    Result := 'true'
  else
    Result := 'false';
end;

function SelectedPlatformName: String;
begin
  if ShouldSetUpMiSTer() then
    Result := 'MiSTer'
  else if PlatformPage.SelectedValueIndex = 1 then
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
    Result := ExpandConstant('{sd}\RetroArch-Win64\cores\bsnes_mercury_performance_libretro.dll')
  else
    Result := RetroArchPage.Values[1];
end;

function SelectedRetroArchExecutablePath: String;
begin
  if DependencyPage.Values[2] then
    Result := ExpandConstant('{sd}\RetroArch-Win64\retroarch.exe')
  else
    Result := RetroArchPage.Values[0];
end;

procedure SetRetroArchSetting(
  Settings: TStringList;
  SettingName, SettingValue: String);
var
  I: Integer;
  EqualsPosition: Integer;
  CurrentLine: String;
  CurrentName: String;
  Found: Boolean;
begin
  Found := False;
  for I := Settings.Count - 1 downto 0 do
  begin
    CurrentLine := Trim(Settings[I]);
    EqualsPosition := Pos('=', CurrentLine);
    if EqualsPosition > 0 then
      CurrentName := Trim(Copy(CurrentLine, 1, EqualsPosition - 1))
    else
      CurrentName := '';

    if CompareText(CurrentName, SettingName) = 0 then
    begin
      if not Found then
      begin
        Settings[I] := SettingName + ' = ' + SettingValue;
        Found := True;
      end
      else
        Settings.Delete(I);
    end;
  end;

  if not Found then
    Settings.Add(SettingName + ' = ' + SettingValue);
end;

procedure InstallPortableRetroArch;
var
  InstallerPath: String;
  InstallDirectory: String;
  CoreArchivePath: String;
  CoreDirectory: String;
  ResultCode: Integer;
begin
  if not ShouldInstallRetroArch then
    Exit;

  InstallerPath := ExpandConstant('{tmp}\RetroArch-Win64-setup.exe');
  InstallDirectory := ExpandConstant('{sd}\RetroArch-Win64');
  CoreArchivePath := ExpandConstant(
    '{tmp}\bsnes_mercury_performance_libretro.dll.zip');
  CoreDirectory := InstallDirectory + '\cores';
  WizardForm.StatusLabel.Caption :=
    ExpandConstant('{cm:RetroInstallProgress}');

  { RetroArch's package is an elevated NSIS self-extractor. /S keeps it }
  { inside the blue setup flow and uses its standard portable directory. }
  if not FileExists(InstallerPath) then
    RaiseException(ExpandConstant('{cm:ErrorRetroInstall}'));

  if not ShellExec(
    'runas',
    InstallerPath,
    '/S',
    '',
    SW_HIDE,
    ewWaitUntilTerminated,
    ResultCode) then
    RaiseException(ExpandConstant('{cm:ErrorRetroInstall}'));

  if (ResultCode <> 0) or
     (not FileExists(InstallDirectory + '\retroarch.exe')) then
    RaiseException(ExpandConstant('{cm:ErrorRetroInstall}'));

  ForceDirectories(CoreDirectory);
  if not FileExists(CoreArchivePath) then
    RaiseException(ExpandConstant('{cm:ErrorRetroInstall}'));
  ExtractArchive(CoreArchivePath, CoreDirectory, '', True, nil);
  if not FileExists(
    CoreDirectory + '\bsnes_mercury_performance_libretro.dll') then
    RaiseException(ExpandConstant('{cm:ErrorRetroInstall}'));
end;

procedure InstallQUsb2Snes;
var
  ArchivePath: String;
  InstallDirectory: String;
  TarPath: String;
  Parameters: String;
  ResultCode: Integer;
begin
  if not ShouldInstallQUsb then
    Exit;

  ArchivePath := ExpandConstant(
    '{tmp}\QUsb2Snes-bundle-2025-10-20.7z');
  InstallDirectory := ExpandConstant('{app}\Tools\QUsb2Snes');
  TarPath := ExpandConstant('{sys}\tar.exe');
  WizardForm.StatusLabel.Caption :=
    ExpandConstant('{cm:QUsbInstallProgress}');

  { Windows 10 includes bsdtar/libarchive. Let it unpack the complete 7z }
  { bundle in one native pass instead of making Inno process every file. }
  { The release has one QUsb2Snes-bundle wrapper directory, so remove that }
  { first path component to preserve the install layout used by the app. }
  if (not FileExists(ArchivePath)) or (not FileExists(TarPath)) then
    RaiseException(ExpandConstant('{cm:ErrorQUsbInstall}'));

  ForceDirectories(InstallDirectory);
  Parameters := '-xf "' + ArchivePath + '" -C "' +
    InstallDirectory + '" --strip-components 1';
  if not Exec(
    TarPath,
    Parameters,
    '',
    SW_HIDE,
    ewWaitUntilTerminated,
    ResultCode) then
    RaiseException(ExpandConstant('{cm:ErrorQUsbInstall}'));

  if (ResultCode <> 0) or
     (not FileExists(InstallDirectory + '\QUsb2Snes.exe')) then
    RaiseException(ExpandConstant('{cm:ErrorQUsbInstall}'));
end;

procedure ConfigurePortableRetroArch;
var
  ConfigPath: String;
  Settings: TStringList;
begin
  if not ShouldInstallRetroArch then
    Exit;

  ConfigPath := ExpandConstant('{sd}\RetroArch-Win64\retroarch.cfg');
  ForceDirectories(ExtractFileDir(ConfigPath));
  Settings := TStringList.Create;
  try
    if FileExists(ConfigPath) then
      Settings.LoadFromFile(ConfigPath);
    SetRetroArchSetting(Settings, 'network_cmd_enable', '"true"');
    SetRetroArchSetting(Settings, 'network_cmd_port', '"55355"');
    SetRetroArchSetting(Settings, 'quit_press_twice', '"false"');
    SetRetroArchSetting(Settings, 'config_save_on_exit', '"true"');
    Settings.SaveToFile(ConfigPath);
  finally
    Settings.Free;
  end;
end;

procedure CancelButtonClick(
  CurPageID: Integer;
  var Cancel: Boolean;
  var Confirm: Boolean
);
begin
  if ExitAfterCompleteUninstall then
  begin
    Cancel := True;
    Confirm := False;
  end;
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
  if Trim(FolderOBSEdit.Text) <> '' then
    ForceDirectories(FolderOBSEdit.Text);
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
    '  "output_folder": "' + JsonEscape(FolderOBSEdit.Text) + '",'#13#10 +
    '  "retroarch_executable_path": "' + JsonEscape(SelectedRetroArchExecutablePath) + '",'#13#10 +
    '  "retroarch_core_path": "' + JsonEscape(SelectedRetroArchCorePath) + '",'#13#10 +
    '  "retroarch_host": "127.0.0.1",'#13#10 +
    '  "retroarch_port": 55355,'#13#10 +
    '  "first_launch_mister_setup_requested": ' +
      JsonBoolean(ShouldSetUpMiSTer()) + ','#13#10 +
    '  "ui_theme": "dark",'#13#10 +
    '  "first_launch_welcome_completed": false'#13#10 +
    '}'#13#10;

  if not SaveStringToFile(ConfigFilePath, ConfigText, False) then
    RaiseException(ExpandConstant('{cm:ConfigWriteError}') + ' ' + ConfigFilePath);
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    InstallQUsb2Snes;
    InstallPortableRetroArch;
    ConfigurePortableRetroArch;
    WriteInitialConfiguration;
  end;
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
  if ShouldSetUpMiSTer() then
    DependencyList := DependencyList + Space + ExpandConstant('{cm:ReadyMiSTer}') + NewLine;
  if DependencyList = '' then
    DependencyList := Space + ExpandConstant('{cm:ReadyNone}') + NewLine;

  Result := MemoDirInfo + NewLine + NewLine +
    ExpandConstant('{cm:ReadyPlatform}') + NewLine + Space + SelectedPlatformName + NewLine + NewLine +
    ExpandConstant('{cm:ReadyDependencies}') + NewLine + DependencyList + NewLine +
    ExpandConstant('{cm:ReadyROMLibrary}') + NewLine + Space + FolderPage.Values[0] + NewLine + NewLine +
    ExpandConstant('{cm:ReadyOBS}') + NewLine + Space + FolderOBSEdit.Text + NewLine;

  if MemoTasksInfo <> '' then
    Result := Result + NewLine + MemoTasksInfo;
end;
