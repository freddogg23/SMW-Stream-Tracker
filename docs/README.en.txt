SMW STREAM TRACKER - COMPLETE SETUP GUIDE
Version 1.0.4

LANGUAGES
English: README.en.txt
Australian: README.au.txt
Español: README.es.txt
Français: README.fr.txt
Deutsch: README.de.txt
Português (Brasil): README.pt-BR.txt

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

* A 64-bit Windows 10 or Windows 11 computer.
* A folder for patched ROMs.
* Internet access for catalog updates and optional downloads.
* Either an FXPAK Pro/SD2SNES or RetroArch on Windows.
* Your own legally obtained clean Super Mario World ROM if you want to build
  playable ROMs from moderated patch files.

SMW Stream Tracker does not include or download a commercial base ROM.

2. INSTALL THE PROGRAM

1. Start SMWStreamTracker_Setup_1.0.4.exe.
2. Select a language on the first screen.
3. Read the optional-software and ROM notice.
4. Choose FXPAK Pro or RetroArch as the initial platform.
5. Select any optional tools you want Setup to install.
6. Choose a patched-ROM folder and an OBS output folder, or leave either field
   blank and configure it later.
7. Finish Setup and open this guide.

Existing tracker settings are preserved during installation and updates.
Change the interface language at any time from File > Language. The main
interface updates immediately without leaving labels from the old language.

3. CHOOSE OPTIONAL SOFTWARE

SNI is strongly recommended. It provides the live connection used by the
tracker and works with supported hardware and emulator workflows.

QUsb2Snes is an optional legacy/advanced bridge recommended mainly for FXPAK
Pro and SD2SNES users who already use it.

RetroArch is optional. Skip it if RetroArch is already installed or if you use
only FXPAK Pro. When selected, Setup also downloads the bsnes-mercury Performance Libretro core.

If you skip a tool during Setup, open Downloads > Connection & Emulator Setup
later. The app can find an existing SNI, QUsb2Snes, or RetroArch installation,
or install it in your user profile. RetroArch setup also installs the
recommended core, enables Network Commands on port 55355, and saves both file
locations in the tracker settings.

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
* Play Random Hack chooses only from hacks that are already downloaded and
  launchable on the currently selected platform. Catalog-only entries are
  never selected.
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
