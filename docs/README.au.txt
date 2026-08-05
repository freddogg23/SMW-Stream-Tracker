SMW STREAM TRACKER - THE RIDGY-DIDGE SETUP YARN
Version 1.1.2

G'day, mate. You've found the Australian guide: all the useful setup details,
a healthy serve of local lingo, and absolutely no drop bears hiding in the
installer. Probably. Chuck the kettle on and we'll get this sorted.

LANGUAGES
English: README.en.txt
Australian: README.au.txt
Español: README.es.txt
Français: README.fr.txt
Deutsch: README.de.txt
Português (Brasil): README.pt-BR.txt

WHAT'S IN THIS YARN
1. The gear you'll need
2. Get the show on the road
3. Pick the optional bits and bobs
4. Set up FXPAK Pro
5. Set up RetroArch
6. Have a squiz at your folders and files
7. Freshen up the catalogue
8. Download and build some hacks
9. Bung ROMs onto an SD card
10. Pick a hack and have a crack
11. Timers, My Tracker, and statistics
12. LiveSplit, OBS Studio, and Streamlabs Desktop
13. Updates, backups, and winding back a version
14. When something spits the dummy

1. THE GEAR YOU'LL NEED

* A 64-bit Windows 10 or Windows 11 computer. Nothing too flash, just something
  that isn't held together with fencing wire.
* A folder where your patched ROMs can bunk down.
* Internet access for catalogue refreshes, updates, and optional downloads.
* Either an FXPAK Pro/SD2SNES or RetroArch on Windows.
* Your own legally obtained clean Super Mario World ROM if you want to turn
  moderated patch files into playable ROMs.

SMW Stream Tracker does not include, download, or sneak in a commercial base
ROM. Supply your own legally obtained clean copy and she'll be apples. Do the
right thing, mate.

2. GET THE SHOW ON THE ROAD

1. Give SMWStreamTracker_Setup_1.1.2.exe a double-click.
2. Select Australian on the first screen. Good choice, champion.
3. Read the optional-software information and the ROM notice.
4. Pick FXPAK Pro or RetroArch as your first cab off the rank.
5. Tick whichever optional tools you want Setup to chuck in.
6. Choose a patched-ROM folder and an OBS output folder, or leave either field
   blank and sort it out later. No dramas.
7. Finish Setup and launch SMW Stream Tracker. Too easy.

Existing tracker settings are preserved during installations and updates, so
Setup won't barge in and stomp all over your current configuration.

3. PICK THE OPTIONAL BITS AND BOBS

SNI is strongly recommended. Fair dinkum, this is the normal live connection
used by the tracker for supported hardware and emulator setups.

QUsb2Snes is recommended for FXPAK Pro and SD2SNES users, especially if you
want to upload ROMs over USB while the SD card stays tucked inside the cart.
It is also handy for older or more advanced setups.

RetroArch is optional. Leave it unticked if you already have it or if you're
an FXPAK Pro-only operator. If selected, Setup also grabs the bsnes-mercury
Performance Libretro core so you aren't left mucking about hunting for it.

4. SET UP FXPAK PRO

1. Connect the FXPAK Pro USB port to the PC with a proper USB data cable. A
   charge-only cable is about as useful here as a screen door on a submarine.
2. Power on the console.
3. Start SNI or QUsb2Snes and wait for the device to show up.
4. Open SMW Stream Tracker.
5. Select File > FXPAK Pro.
6. Give Refresh a burl if the status doesn't update automatically.
7. Open File > Settings and check the selected service executable and
   connection address. The usual WebSocket address is ws://localhost:23074.

If the device has gone walkabout, check the USB cable, compatible firmware,
Windows driver, console power, and whether another program has nicked the
connection. Then give Refresh another nudge.

5. SET UP RETROARCH

1. Install RetroArch, or select your existing retroarch.exe in File > Settings.
2. In RetroArch, open Online Updater > Core Downloader and install
   Nintendo - SNES / SFC (bsnes-mercury Performance) if Setup did not already
   provide it.
3. Open Settings > Network in RetroArch.
4. Enable Network Commands and leave the port at 55355.
5. Close and reopen RetroArch so the setting is properly saved.
6. In SMW Stream Tracker, select File > RetroArch.
7. Select retroarch.exe and bsnes_mercury_performance_libretro.dll in
   File > Settings if they weren't detected automatically.
8. Select File > Test Selected Platform and make sure everything is behaving.
9. Use Play in the tracker. When changing games, the tracker requests a save
   state, closes the current content/session, and launches the selected hack.

If that all checks out, you're off like a frog in a sock.

6. HAVE A SQUIZ AT YOUR FOLDERS AND FILES

Open File > Settings and cast your eye over these:

* Patched ROM library: your finished .smc or .sfc files live here.
* OBS output: current-hack and timer text files land here.
* Clean base ROM: used only when applying moderated patch files.
* SNI/QUsb2Snes executable: needed for FXPAK Pro live tracking.
* RetroArch executable: needed to launch RetroArch games.
* RetroArch core: normally bsnes_mercury_performance_libretro.dll.

Run File > Setup & Health Check after changing paths. Sort out anything marked
Missing before downloading or launching games; she'll be right is not a file
location.

7. FRESHEN UP THE CATALOGUE

1. Open Downloads.
2. Select Refresh Moderated Hacks from SMW Central.
3. Let the refresh finish. The requests are paced so SMW Central doesn't tell
   us to rack off. Don't hammer Refresh like a galah if it is already working.
4. Select View Complete Catalog to search, filter, and sort the whole lot.
5. Click Added Date once for newest first and again for oldest first.

Only the Difficulty cell wears your configured difficulty colour. The rest of
the table follows the selected light/dark theme and the alternating row colours.

8. DOWNLOAD AND BUILD SOME HACKS

1. Open Downloads > Download Missing SMW Hacks.
2. Select your legally obtained clean Super Mario World ROM.
3. Select the patched-ROM library folder.
4. Filter by type, difficulty, rating, or date if that tickles your fancy.
5. Have a stickybeak at the preview.
6. Select Download Moderated Hacks and let it do its thing.

The tool downloads moderated patch ZIPs and applies them locally. It never
downloads a base ROM. Existing mapped or local games are skipped, so it won't
needlessly double up the whole paddock.

9. BUNG ROMS ONTO AN SD CARD

METHOD A - THE SD CARD IS MOUNTED IN WINDOWS

1. Open Download Missing SMW Hacks.
2. Enable Copy new ROMs to a mounted SD folder.
3. Choose the correct All_Hacks folder on the SD card.
4. Double-check the destination before letting it rip.
5. Download the missing hacks. The app keeps the local-library copy and puts a
   second copy in the selected SD folder.

METHOD B - LEAVE THE SD CARD IN THE FXPAK PRO

1. Connect the FXPAK Pro to the PC with a USB data cable and power on the
   console.
2. Start QUsb2Snes and confirm it can see the cartridge.
3. Open Download Missing SMW Hacks.
4. Enable Upload new ROMs through FXPAK Pro USB.
5. Leave the remote folder as /All_Hacks, or choose another folder on the card.
6. Select Test USB before sending the whole mob across.
7. Download the missing hacks after the test succeeds.

The app won't overwrite an existing same-named card file. Measure twice, copy
once, and Bob's your uncle.

10. PICK A HACK AND HAVE A CRACK

* Type in Search or select a hack, choose a result, and press Play.
* Play Random Hack rolls the dice and picks something from the available library.
* Add to My Tracker creates a tracked entry.
* Complete Hack records your completion data. On ya.
* Clicking elsewhere closes the search list. The placeholder hangs about until
  a hack is actually selected.

11. TIMERS, MY TRACKER, AND STATISTICS

Start, pause, reset, and override the game and level timers from the main
screen. My Tracker supports searching, filters, editable fields, difficulty
colours, rating and completion bars, and CSV/XLSX export. Right-click supported
areas to change solid fills, gradients, or difficulty colours.

Statistics rounds up progress, ratings, playtime, recent activity, and
completion by difficulty. Everything in one spot, neat as a new pin. Beauty.

12. LIVESPLIT, OBS STUDIO, AND STREAMLABS DESKTOP

You've got two fair-dinkum options: capture the LiveSplit windows, or let OBS
or Streamlabs read the tracker's text files. Use both if that floats your boat.
The text-file method is the easier caper and doesn't need LiveSplit at all.

HOOK UP THE FULL-GAME LIVESPLIT TIMER

1. Grab and extract LiveSplit from https://livesplit.org/downloads/.
2. Open LiveSplit.exe. The server is already built in, so don't fossick around
   for the old separate LiveSplit Server component.
3. Right-click LiveSplit, open Settings, and set Server Port to 16834.
4. If this is your only LiveSplit timer, automatic TCP startup is optional. If
   you're using two windows, start them manually so you can check both ports.
   Choose Control > Start TCP/WS Server after checking the port.
5. In SMW Stream Tracker, open File > Settings, set Game LiveSplit port to
   16834, save, and give Start Game Timer a burl.

HOOK UP THE LEVEL LIVESPLIT TIMER

1. Leave the first LiveSplit running and open LiveSplit.exe again.
2. In this second window, set Server Port to 16835 and start its TCP server.
3. Leave Level LiveSplit port at 16835 in the tracker.
4. Try Start Level Timer, Start Timers, and Reset Level Timer.

The two windows need different ports or they'll carry on like two utes trying
to fit through one gate. On later launches, check 16834 in the first and 16835
in the second before starting each server. It all stays local on 127.0.0.1.
Save separate game and level layouts if you want each timer dressed differently.

PUT LIVESPLIT INTO OBS STUDIO

1. Keep the LiveSplit windows open and don't minimise them.
2. In OBS Sources, choose + > Window Capture.
3. Pick the full-game LiveSplit window, then position and resize it.
4. Add another Window Capture for the level LiveSplit window.
5. Make a quick test recording and work both tracker timers.

PUT LIVESPLIT INTO STREAMLABS DESKTOP

1. Keep the LiveSplit windows open and not minimised.
2. In Streamlabs Sources, choose + > Screen Capture. If your version has a
   separate Window Capture choice, use that.
3. Pick, position, and resize the full-game LiveSplit window.
4. Do the same for the level window and make a quick test recording.

USE THE TIMER TEXT FILES IN OBS OR STREAMLABS

1. Choose an OBS output folder in File > Settings and save it.
2. Pick or start a hack and operate both timers once to create the files.
3. Use File > Open OBS Text Folder to find the right paddock.
4. In OBS or Streamlabs, add a Text (GDI+) source.
5. Enable Read from file and choose game_timer.txt.
6. Add another Text source and choose level_timer.txt.
7. Set your font, colour, outline, alignment, and size.
8. Repeat for hack_name.txt, author.txt, or exits.txt if you fancy.

Keep SMW Stream Tracker running so the files stay fresh. If a source shows
yesterday's news, make sure it reads the same folder selected in the tracker,
then give that timer another nudge. Too easy.

Official help:
LiveSplit server: https://github.com/LiveSplit/LiveSplit#the-livesplit-server
OBS text sources: https://obsproject.com/kb/text-sources
Streamlabs capture: https://streamlabs.com/content-hub/post/how-to-capture-your-screen-in-streamlabs-desktop

13. UPDATES, BACKUPS, AND WINDING BACK A VERSION

Use File > Check for Updates inside SMW Stream Tracker. The app checks the
official update manifest and tells you when a newer version is available.
Review the version, release date, size, and notes, then select Download & Install.

The app downloads the updater helper automatically, checks its SHA-256 value
against the official HTTPS update manifest, and creates a recovery backup
before closing. The helper replaces the running program and keeps the previous
executable available for rollback. You do not need to hunt down or run the
updater helper yourself.

Use Stats > Create Recovery Backup Now whenever you want an extra backup. Use
File > Restore Previous App Version if an installed update goes pear-shaped.
Backups are like sunscreen: you might reckon you'll be right without them,
right up until you aren't.

14. WHEN SOMETHING SPITS THE DUMMY

* FXPAK Pro says Disconnected: check SNI/QUsb2Snes, the USB data cable,
  firmware, console power, and port 23074. Then select Refresh.
* RetroArch launches but doesn't track: enable Network Commands on port 55355
  and restart RetroArch. With SNI, use bsnes-mercury Performance. With
  QUsb2Snes, enable its RetroArch virtual device from the Devices menu.
* A game won't launch: check the ROM, executable, core, and library paths.
* Catalogue refresh is taking yonks: leave the paced retries running. Starting
  it over and over can keep a rate limit hanging around longer.
* A window has the wrong theme: close and reopen that window if it was already
  open when you changed appearance settings.
* Still cactus: open File > Diagnostics, copy the redacted report, and include
  it when asking for help.

The app processes local ROM paths, tracker data, and stream text on your own PC.
Optional catalogue, dependency, update, and sync features connect only when
used. The diagnostic report redacts personal paths and ROM details. Read
PRIVACY.txt and THIRD_PARTY_NOTICE.txt for the full serious yarn.

That's the lot, mate. Fire it up, pick a hack, and have an absolute ripper.
