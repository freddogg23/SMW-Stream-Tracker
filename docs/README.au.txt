SMW STREAM TRACKER - THE FAIR DINKUM SETUP GUIDE
Version 1.0.0

G'day. This is the Australian guide: useful instructions, a few laughs, and no
drop bears anywhere in the installer. Probably.

LANGUAGES
English: README.en.txt
Australian: README.au.txt
Español: README.es.txt
Français: README.fr.txt
Deutsch: README.de.txt
Português (Brasil): README.pt-BR.txt

WHAT'S IN THIS YARN
1. What you need
2. Install the program
3. Pick the optional bits and bobs
4. Set up FXPAK Pro
5. Set up RetroArch
6. Choose folders and files
7. Refresh the catalogue
8. Download and build hacks
9. Copy ROMs to an SD card
10. Play and track a hack
11. Timers, My Tracker, and statistics
12. OBS text output
13. Updates, backup, and rollback
14. Troubleshooting and privacy

1. WHAT YOU NEED

* A 64-bit Windows 10 or Windows 11 computer.
* A folder where patched ROMs can bunk down.
* Internet for catalogue updates and optional downloads.
* Either an FXPAK Pro/SD2SNES or RetroArch on Windows.
* Your own legally obtained clean Super Mario World ROM if you want to build
  playable ROMs from moderated patch files.

SMW Stream Tracker does not include or download a commercial base ROM. That bit
is important, so do the right thing.

2. INSTALL THE PROGRAM

1. Fire up SMWStreamTracker_Setup_1.0.0.exe.
2. Select Australian on the first screen.
3. Read the optional-software and ROM notice.
4. Pick FXPAK Pro or RetroArch as your first cab off the rank.
5. Tick any optional tools you want Setup to chuck in.
6. Choose a patched-ROM folder and an OBS output folder, or leave either field
   blank and sort it out later.
7. Finish Setup and open this guide. Too easy.

Existing tracker settings are preserved during installation and updates, so
Setup will not stomp all over your current configuration.

3. PICK THE OPTIONAL BITS AND BOBS

SNI is strongly recommended. It provides the live connection used by the
tracker and works with supported hardware and emulator workflows.

QUsb2Snes is the optional legacy/advanced bridge, mainly for FXPAK Pro and
SD2SNES users who already know their way around it.

RetroArch is optional. Leave it unticked if it is already installed or if you
only use FXPAK Pro. If selected, Setup also grabs the bsnes-mercury Performance Libretro core.

4. SET UP FXPAK PRO

1. Connect the FXPAK Pro USB port to the PC.
2. Power on the console.
3. Start SNI or QUsb2Snes and wait for the device to show up.
4. Open SMW Stream Tracker.
5. Select File > FXPAK Pro.
6. Give Refresh a burl if the status does not update automatically.
7. In Settings, check the service executable and WebSocket address. The usual
   address is ws://localhost:23074.

If the device goes walkabout, check the USB cable, compatible firmware,
Windows driver, and whether another program has nicked the connection.

5. SET UP RETROARCH

1. Install RetroArch or select your existing retroarch.exe in Settings.
2. Install Nintendo - SNES / SFC (bsnes-mercury Performance) from Online Updater > Core Downloader.
3. Open Settings > Network in RetroArch.
4. Enable Network Commands and leave the port at 55355.
5. In SMW Stream Tracker, select File > RetroArch.
6. Select retroarch.exe and bsnes_mercury_performance_libretro.dll if they were not detected.
7. Use Play in the tracker. When changing games, the tracker saves state,
   closes the current content, and starts the selected hack.

6. CHOOSE FOLDERS AND FILES

Open File > Settings and have a squiz at:

* Patched ROM library: finished .smc or .sfc files live here.
* OBS output: current-hack and timer text files land here.
* Clean base ROM: used only when applying moderated patch files.
* SNI/QUsb2Snes executable: needed for FXPAK Pro live tracking.
* RetroArch executable and bsnes-mercury Performance core: needed for RetroArch launching.

Run the health check after changing paths. Sort out anything marked missing
before downloading or launching games.

7. REFRESH THE CATALOGUE

1. Open Downloads.
2. Select Refresh Moderated Hacks from SMW Central.
3. Let it finish. Requests are paced so the site does not tell us to rack off.
4. Select View Complete Catalog to search, filter, and sort everything.
5. Click Added Date once for newest first and again for oldest first.

Only the Difficulty cell uses your configured difficulty colour. The rest of
the table follows the light/dark theme and alternating row colours.

8. DOWNLOAD AND BUILD HACKS

1. Open Downloads > Download Missing SMW Hacks.
2. Select your legally obtained clean Super Mario World ROM.
3. Select the patched-ROM library folder.
4. Filter by type, difficulty, rating, or date if you fancy.
5. Check the preview.
6. Select Download Moderated Hacks.

The tool downloads moderated patch ZIPs and applies them locally. It never
downloads a base ROM, and existing mapped or local games are skipped.

9. COPY ROMS TO AN SD CARD

For a removable SD card, select the SD destination in Settings and enable copy
during the download workflow. Double-check the destination before letting it rip.

An FXPAK Pro does not normally expose its SD card as a Windows drive over the
USB tracking connection. Remote upload may work through SNI/QUsb2Snes, but
permanent bulk copying usually still needs an SD-card reader. No worries.

10. PLAY AND TRACK A HACK

* Type in Search or select a hack, choose a result, and press Play.
* Play Random Hack picks something from the available library.
* Add to My Tracker creates a tracked entry.
* Complete Hack records completion data.
* Clicking away closes the search list. The placeholder hangs around until a
  hack is actually selected.

11. TIMERS, MY TRACKER, AND STATISTICS

Start, pause, reset, and override game and level timers from the main screen.
My Tracker supports search, filters, editable fields, difficulty colours,
rating and completion bars, and CSV/XLSX export. Right-click supported areas to
change solid or gradient colours. Statistics wraps up progress, ratings,
playtime, recent activity, and completion by difficulty. Beauty.

12. OBS TEXT OUTPUT

1. Choose an OBS output folder in Settings.
2. Start or select a hack so the tracker writes its text files.
3. In OBS, add a Text source.
4. Enable Read from file and select the file you want.
5. Repeat for the title, creator, exits, timers, or other fields.

13. UPDATES, BACKUP, AND ROLLBACK

Use SMWStreamTracker_Update_VERSION.exe for small releases after using the
complete installer once. The updater keeps the previous executable for
rollback. Back up the tracker database, configuration, and patched-ROM library
before major Windows or storage changes. She'll be right, but backups help.

14. TROUBLESHOOTING AND PRIVACY

* FXPAK Pro disconnected: check SNI/QUsb2Snes, USB, firmware, and port 23074.
* RetroArch launches but does not track: enable Network Commands on port 55355.
  With SNI, launch games with bsnes-mercury Performance. With QUsb2Snes,
  enable its RetroArch virtual device from the Devices menu.
* Game does not launch: check the ROM, executable, core, and library paths.
* Catalogue refresh is slow: let the paced retries finish; restarting over and
  over can make a rate limit hang around longer.
* Theme does not update: close and reopen the affected window if needed.

The app processes local ROM paths, tracker data, and stream text on your PC.
Optional catalogue, dependency, update, and sync features connect only when
used. Read PRIVACY.txt and THIRD_PARTY_NOTICE.txt for the full serious yarn.

All done. Fire it up and have a ripper time.
