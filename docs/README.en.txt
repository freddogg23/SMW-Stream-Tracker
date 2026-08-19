SMW STREAM TRACKER - COMPLETE SETUP GUIDE
Version 2.0.0

LANGUAGES
English: README.en.txt
Australian: README.au.txt
Español: README.es.txt
Français: README.fr.txt
Deutsch: README.de.txt
Português (Brasil): README.pt-BR.txt

MACOS SUPPORT

SMW Stream Tracker now has native Mac paths and a Mac build workflow for both
Apple Silicon (arm64) and Intel (x86_64). Install the matching DMG and drag the
app to Applications. Tracker data stays in:
~/Library/Application Support/SMWStreamTracker

Connection & Emulator Setup downloads the official Mac versions of SNI,
QUsb2Snes, and RetroArch, including the correct Mac bsnes-mercury core. Classic
desktop LiveSplit is Windows-only, so the Mac app provides synchronized Game
Timer and Level Timer windows plus game_timer.txt and level_timer.txt for OBS.
All catalog, patching, FXPAK, emoji-alias, database, workbook, and OBS text
features use the same data and behavior on Windows and Mac.

NEW IN VERSION 2.0.0

* The Stream Desk redesign now covers the dashboard, settings, libraries,
  game modes, setup tools, dialogs, popups, and the Windows installer.
* Hot Potato and Mario Kaizo Challenge add new ways to play, including curated
  playlists, automatic next-hack queues, filters, and dashboard controls.
* Guided RetroAchievements setup, compatible-core launching, and trophy markers
  identify supported hacks without changing normal tracker behavior.
* Advanced filters now support title, creator, difficulty, type, release state,
  Hall of Fame, waiting moderation, and RetroAchievements across the app.
* Catalog loading, My Tracker, settings, patching, and setup work have been
  tightened so the interface stays responsive and avoids legacy-color flashes.
* RetroArch launch normalization, installer/updater reliability, faster
  QUsb2Snes setup, and every shipped translation have been polished for release.

NEW IN VERSION 1.1.1

* SMW Central now has an integrated home experience with live content cards,
  richer hack details, tag search, screenshots, and account/comment tools.
* SMW Central Radio and SPC playback include a compact player that can be
  moved, resized, minimized, and left open while using the tracker.
* Optional OBS Capture Mode keeps blue tracker popups inside the main window so
  one OBS Window Capture source can include them.
* The normal Windows build adds compatibility-checked MiSTer save states 5–11,
  preserves an exact restorable backup and native slots 1–4, and keeps F12 for
  the MiSTer menu.
* Setup, application, OBS, and LiveSplit menus are reorganized without breaking
  guided setup. Game Modes return to the dashboard after launching a hack.
* Stale MiSTer connection data no longer affects RetroArch, and window resizing
  and Google Sheets settings close more reliably.
* Every new phrase is translated in all six supported languages and checked by
  a deeper automatic translation audit.

NEW IN VERSION 1.1.0

* MiSTer FPGA is now a complete playable platform. One-click setup discovers
  the console on the local network, prepares remote launching and live tracking,
  and works with standard MiSTer and MiSTer Multisystem² consoles.
* Game Modes now includes Play Random Hack, Hack Draft, Difficulty Ladder,
  Creator Spotlight, Time Capsule, and Hall of Fame Tour, with translated blue
  windows and hover descriptions.
* Spreadsheet Settings now includes smart Excel import. Google Sheets can sync
  in either direction, and a new tracker/database recovery backup is saved on
  every clean exit.
* My Tracker has compact add/remove controls, multi-row removal, automatic Hack #
  renumbering, and cleaner Spreadsheet and Google Sheets submenus.
* Menus and settings now hide options that do not apply to the selected FXPAK
  Pro, RetroArch, or MiSTer platform.
* Optional Windows RetroArch setup is faster, and RetroArch stays closed until
  the user launches a game.
* Streamer.bot level-event output and translated guides support optional Twitch
  prediction automation.
* Every new menu, button, status, popup, and setup instruction is translated in
  English, Australian, Spanish, French, German, and Brazilian Portuguese.

* Native Windows and macOS behavior now includes reproducible Apple Silicon
  and Intel builds and platform-correct SNI, QUsb2Snes, and RetroArch setup.
* Window movement and My Tracker scrolling are smoother, the banner is cached,
  table borders remain aligned while scrolling, and a shorter main window can
  scroll vertically to reach the bottom controls.
* A translated blue Add to Tracker form accepts complete hack and progress
  details. Custom unmoderated hacks remain beside the catalog and can be patched
  and uploaded through Download & Patch Missing Hacks.
* The main Refresh button can safely reset a running FXPAK Pro session before
  reconnecting, and Remove from My Tracker now uses the translated blue dialog.
* A guided first-run setup now flashes each required Downloads, connection,
  catalog, refresh, download, patch, FXPAK, and OBS step in order.
* After SNI or RetroArch is chosen, QUsb2Snes and the chosen option stop
  flashing; only the other required SNI/RetroArch option remains highlighted.
* The SMW Central catalog and hack downloader use blue drop-down arrows,
  yellow scrollbars, wider type fields, and light-blue cell borders.
* FXPAK Pro transfers replace every emoji with its readable Unicode name in
  the ROM filename. This also applies to future hacks; the catalog, tracker,
  and current-game display keep the original title, and the saved mapping
  recalls the renamed ROM when selected.
* When USB upload is enabled, existing local ROMs with emoji titles are also
  transferred and mapped automatically. This repairs earlier downloads without
  downloading or patching them again.
* Playing an emoji-titled hack now finds its readable FXPAK-only filename or
  uploads the missing alias automatically. The permanent link uses the SMW
  Central ID, so the tracker always restores and displays the original title.
* FXPAK file transfers temporarily pause the live SNI/QUsb2Snes tracker
  connection and reconnect it automatically afterward, so live tracking cannot
  block an emoji-safe upload.
* The OBS setup page explains how to reuse existing text sources, and two
  buttons can download and configure separate Game and Level LiveSplit copies
  automatically on ports 16834 and 16835.
* Statistics uses the revised two-column layout with larger difficulty and
  tracker-status charts and a compact Progress by Difficulty table.
* Message popups, menus, controls, status text, file pickers, and setup screens
  share complete translations. Australian English includes playful local
  wording throughout.
* About now includes a Join Discord button for help and contact:
  https://discord.gg/fHkTRgqjcr

TABLE OF CONTENTS
1. What you need
2. Install the program
3. Choose optional software
4. Set up FXPAK Pro
5. Set up RetroArch
6. Choose folders and files
7. Refresh the catalog
8. Download and build hacks
9. Copy ROMs to an SD card
10. Play and track a hack
11. Timers, My Tracker, and statistics
12. LiveSplit, OBS Studio, and Streamlabs Desktop
13. Updates, backup, and rollback
14. Troubleshooting and privacy

1. WHAT YOU NEED

* A 64-bit Windows 10/11 computer or a supported Intel/Apple Silicon Mac.
* A folder for patched ROMs.
* Internet access for catalog updates and optional downloads.
* An FXPAK Pro/SD2SNES, RetroArch, or a network-connected MiSTer FPGA.
* Your own legally obtained clean Super Mario World ROM if you want to build
  playable ROMs from moderated patch files.

SMW Stream Tracker does not include or download a commercial base ROM.

2. INSTALL THE PROGRAM

1. Start SMWStreamTracker_Setup_2.0.0.exe.
2. Select a language on the first screen.
3. Read the optional-software and ROM notice.
4. Choose FXPAK Pro, RetroArch, or MiSTer as the initial platform.
5. Select any optional tools you want Setup to install.
6. Choose a patched-ROM folder and an OBS output folder, or leave either field
   blank and configure it later.
7. Finish Setup and open this guide.

Existing tracker settings are preserved during installation and updates.
A full uninstall removes tracker settings, data, LiveSplit copies, and the
tracker-created OBS text files. It keeps RetroArch, SNI, QUsb2Snes, and all ROM
files and ROM-library folders. A later fresh install shows the branded welcome
and setup splash again.
Only one copy can be installed for the current Windows account. Running the
complete installer again asks whether to remove the current copy and continue
with a fresh installation, or completely uninstall the tracker and exit Setup.
Both choices preserve RetroArch, SNI, QUsb2Snes, and every ROM file.
Change the interface language at any time from File > Language. The main
interface updates immediately without leaving labels from the old language.

3. CHOOSE OPTIONAL SOFTWARE

FXPAK Pro and SD2SNES setups require QUsb2Snes only. SNI is not required for
the FXPAK Pro workflow.

RetroArch setups require both RetroArch and SNI. SNI provides the live-memory
connection that lets the tracker detect the running game and gameplay state.
In the flashing setup guide, QUsb2Snes may advance by itself. Selecting SNI or
RetroArch keeps the connection step active until both have been completed.

RetroArch is optional. Skip it if RetroArch is already installed or if you use
only FXPAK Pro. When selected, the blue Setup downloads and extracts the
official portable RetroArch build into its Tools folder, installs the
bsnes-mercury Performance Libretro core, enables Network Commands on port
55355, and saves both paths. No separate RetroArch setup wizard opens.

If you skip a tool during Setup, open Downloads > Connection & Emulator Setup
later. The app can find an existing SNI, QUsb2Snes, or RetroArch installation,
or install it in your user profile. RetroArch setup also installs the
recommended core, enables Network Commands on port 55355, and saves both file
locations in the tracker settings.
When a copy is found, a localized blue confirmation box lets you use it
automatically or choose a fresh download instead.

4. SET UP FXPAK PRO

1. Connect the FXPAK Pro USB port to the PC.
2. Power on the console.
3. Start SNI or QUsb2Snes and wait for the device to appear.
4. Open SMW Stream Tracker.
5. Select File > FXPAK Pro.
6. Click Refresh if the status does not update automatically.
7. In Settings, verify the service executable and WebSocket address. The usual
   address is ws://localhost:23074.

If the device is missing, check the USB cable, compatible firmware, Windows
driver, and whether another program is already using the connection.

5. SET UP RETROARCH

1. Install RetroArch or select your existing retroarch.exe in Settings.
2. Install Nintendo - SNES / SFC (bsnes-mercury Performance) from Online Updater > Core Downloader.
3. Open Settings > Network in RetroArch.
4. Enable Network Commands and keep the port at 55355.
5. In SMW Stream Tracker, select File > RetroArch.
6. Select retroarch.exe and bsnes_mercury_performance_libretro.dll if they were not detected.
7. Use Play in the tracker. When changing games, the tracker saves state,
   closes the current content, and starts the selected hack.

6. CHOOSE FOLDERS AND FILES

Open File > Settings and review:

* Patched ROM library: where finished .smc or .sfc files are stored.
* OBS output: where current-hack and timer text files are written.
* Clean base ROM: used only when applying moderated patch files.
* SNI/QUsb2Snes executable: needed for FXPAK Pro live tracking.
* RetroArch executable and bsnes-mercury Performance core: needed for RetroArch launching.

Use the health check after changing paths. Fix any item marked missing before
downloading or launching games.

7. REFRESH THE CATALOG

1. Open Downloads.
2. Select Refresh Moderated Hacks from SMW Central.
3. Wait for the refresh to finish. Requests are paced to avoid rate limits.
4. Select View Complete Catalog to search, filter, and sort the results.
5. Click Added Date once for newest first and again for oldest first.

Use Reset Catalog at the bottom to remove every locally stored moderated and
waiting entry. A recovery backup is created first. Tracker progress, ratings,
notes, custom hacks, ROM mappings, and ROM files are preserved.

Only the Difficulty cell uses your configured difficulty color. Other cells
use the selected light/dark theme and alternating row colors.

8. DOWNLOAD AND BUILD HACKS

1. Open Downloads > Download Missing SMW Hacks.
2. Select your legally obtained clean Super Mario World ROM.
3. Select the patched-ROM library folder.
4. Filter by type, difficulty, rating, or date if desired.
5. Review the preview.
6. Select Download Moderated Hacks.

The tool downloads moderated patch ZIPs, applies them locally, and never
downloads a base ROM. Existing mapped or local games are skipped.

9. COPY ROMS TO AN SD CARD

For a removable SD card, select the SD destination in Settings and enable the
copy option during the download workflow. Confirm the destination carefully.

An FXPAK Pro does not normally expose its SD card as a Windows drive over its
USB tracking connection. Remote upload may be available through SNI/QUsb2Snes,
but permanent bulk copying usually requires an SD-card reader.

10. PLAY AND TRACK A HACK

* Type in Search or select a hack, choose a result, and press Play.
* Game Modes on the main screen opens a full-screen page with a Home button.
  Choose Play Random Hack for one filtered random downloaded game.
* Add to My Tracker creates a tracked entry.
* Complete Hack records completion data.
* Clicking away closes the search list. The placeholder remains until a hack
  is selected.

11. TIMERS, MY TRACKER, AND STATISTICS

Start, pause, reset, and override game and level timers from the main screen.
If an older hack returns to the overworld after a death, the level timer keeps
counting for the configured Overworld timer grace period. It pauses only after
that grace expires and resumes when the same level is entered. A confirmed
clear stops it, the overworld return resets it, and the next level starts it.
My Tracker supports search, filters, editable fields, difficulty colors,
rating and completion data bars, and CSV/XLSX export. Right-click supported
areas to change solid or gradient colors. Statistics summarizes progress,
ratings, playtime, recent activity, and completion by difficulty.

12. LIVESPLIT, OBS STUDIO, AND STREAMLABS DESKTOP

You can capture LiveSplit windows, use the tracker's text files, or use both.
The text-file method is simpler and does not require LiveSplit.

AUTOMATIC TWO-COPY SETUP (RECOMMENDED)

1. Open Help > Setup > LiveSplit Timer Setup.
2. Select Game LiveSplit (16834). The tracker downloads the current official
   LiveSplit release, creates a separate game-timer folder, configures port
   16834 and automatic TCP server startup, and opens LiveSplit.
3. Select Level LiveSplit (16835). The tracker creates a separate level-timer
   copy, configures port 16835 and automatic TCP server startup, and opens it.
4. When both buttons are green, select Done and Save Settings.
5. Keep both LiveSplit windows open and not minimized while using the tracker
   or OBS. Later button clicks reopen the configured copies.

MANUAL SETUP (FALLBACK)

CONNECT THE FULL-GAME LIVESPLIT TIMER

1. Download and extract LiveSplit from https://livesplit.org/downloads/.
2. Open LiveSplit.exe. The server is built in; do not install the old separate
   LiveSplit Server component.
3. Right-click LiveSplit, open Settings, and set Server Port to 16834.
4. If this is your only LiveSplit timer, automatic TCP startup is optional. If
   you use two windows, manual startup is safer so you can check both ports.
   Right-click LiveSplit and select Control > Start TCP/WS Server.
5. In SMW Stream Tracker, open File > Settings, set Game LiveSplit port to
   16834, and save.
6. Select Start Game Timer and confirm LiveSplit follows the tracker.

CONNECT A SEPARATE LEVEL LIVESPLIT TIMER

1. Leave the game-timer LiveSplit open and start LiveSplit.exe a second time.
2. In the second window, set Server Port to 16835 and start its TCP server.
3. In the tracker, leave Level LiveSplit port set to 16835.
4. Select Start Level Timer or Start Timers and test Reset Level Timer.

The two LiveSplit windows must use different ports. On later launches, verify
16834 in the first window and 16835 in the second before starting each server.
The tracker connects only to this computer at 127.0.0.1. Save separate game
and level layouts if desired.

CAPTURE LIVESPLIT IN OBS STUDIO

1. Keep each LiveSplit window open and not minimized.
2. In OBS Sources, select + > Window Capture.
3. Select the full-game LiveSplit window, then position and resize it.
4. Add a second Window Capture source for the level LiveSplit window.
5. Make a short test recording and operate both tracker timers.

CAPTURE LIVESPLIT IN STREAMLABS DESKTOP

1. Keep each LiveSplit window open and not minimized.
2. In Streamlabs Sources, select + > Screen Capture. If your version lists it
   separately, select Window Capture.
3. Select, position, and resize the full-game LiveSplit window.
4. Repeat for the level LiveSplit window, then make a test recording.

USE THE TIMER TEXT FILES IN OBS OR STREAMLABS

1. Choose an OBS output folder in File > Settings and save.
2. Select or start a hack and operate both timers once to create the files.
3. Use File > Open OBS Text Folder to open the configured folder.
4. In OBS or Streamlabs, add a Text (GDI+) source.
5. Enable Read from file and select game_timer.txt.
6. Add another Text source and select level_timer.txt.
7. Set the font, color, outline, alignment, and size you want.
8. Repeat for hack_name.txt, author.txt, exits.txt, level_deaths.txt, or total_deaths.txt if desired.

Level Deaths survives ordinary retries and resets when a different level starts.
Total Deaths is saved separately for every ROM and Mario A, B, or C save file.
Both labels can be changed in File > OBS Settings. death_counter.txt remains a
compatibility mirror of level_deaths.txt for existing OBS scenes.

SMW Stream Tracker must remain running for the files to update. If a source is
blank or stale, verify it uses the same folder selected in the tracker and
operate that timer once more.

Official help:
LiveSplit server: https://github.com/LiveSplit/LiveSplit#the-livesplit-server
OBS text sources: https://obsproject.com/kb/text-sources
Streamlabs capture: https://streamlabs.com/content-hub/post/how-to-capture-your-screen-in-streamlabs-desktop

IMPORT, GOOGLE SHEETS, AND PERMANENT EXCEL BACKUP

Stats > Import Existing Spreadsheet restores current My Tracker Excel exports,
including progress, playtime, deaths, ratings, dates, and notes. Google Sheets
can also be imported directly: open My Tracker > Sync from Google Sheets, paste
the normal sharing link, and select Import Now. Share the sheet as Viewer with
Anyone with the link first; it must contain a Tracker or My Tracker tab. Apps
Script remains available in Google Sheets Settings for automatic two-way sync.
The tracker also maintains Documents > SMW Stream Tracker Backups >
SMW_Stream_Tracker_Automatic_Backup.xlsx outside the data removed by uninstall.

13. UPDATES, BACKUP, AND ROLLBACK

Use SMWStreamTracker_Update_VERSION.exe for small releases after the complete
installer has been used once. The updater preserves the previous executable
for rollback. Back up the tracker database, configuration, and patched-ROM
library before major Windows or storage changes.

14. TROUBLESHOOTING AND PRIVACY

* Disconnected FXPAK Pro: verify SNI/QUsb2Snes, USB, firmware, and port 23074.
* Current Hack no longer detects games after an in-app update: open Downloads
  > Connection & Emulator Setup > Install or Find SNI (Strongly Recommended).
  Let the tracker find or reinstall SNI, restart SNI, and select Refresh.
* RetroArch launches but does not track: enable Network Commands on port 55355.
  With SNI, launch games with bsnes-mercury Performance. With QUsb2Snes,
  enable its RetroArch virtual device from the Devices menu.
* Game does not launch: verify the ROM, executable, core, and library paths.
* Catalog refresh is slow: allow paced retries; repeatedly restarting can make
  a rate limit last longer.
* Theme does not update: close and reopen the affected window if necessary.

The application processes local ROM paths, tracker data, and stream text on
your computer. Optional catalog, dependency, update, and sync features connect
only when used. Read PRIVACY.txt and THIRD_PARTY_NOTICE.txt in the installation
folder for the complete notices.

MISTER QUICK SETUP

On a fresh Windows install, choose MiSTer FPGA and keep Set up MiSTer on first
launch selected. The flashing setup guide will lead you to the one-click button.

Connect MiSTer and this computer to the same router, then open Downloads >
Connection & Emulator Setup > Set Up MiSTer, then select Find & Set Up MiSTer.
The tracker finds and verifies the unit, installs or repairs live tracking,
creates its game folders, selects MiSTer, sets up an app-only automatic login,
and tests the finished connection. If prompted, the factory SSH login is root,
port 22, password 1; the password is never saved. Launching a hack copies it
with a hardware-safe filename and starts it automatically while its real
catalog title remains unchanged.

The normal Windows build installs MiSTer save states 5–11 automatically when
Find & Set Up MiSTer or Install Virtual Save State Slots is run. Alt+F5 through Alt+F11
save; F5 through F11 load states 5–11; F12 still
opens the MiSTer menu; native slots 1–4 stay intact. Tracker updates keep the
feature and may safely replace a version previously installed by the tracker.
If MiSTer Main is updated separately, the tracker refuses to overwrite or
downgrade the unknown file. Use Restore Previous MiSTer Version before updating
MiSTer Main, then use a tracker build made for that newer Main version.
