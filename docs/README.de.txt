SMW STREAM TRACKER - VOLLSTÄNDIGE EINRICHTUNGSANLEITUNG
Version 1.0.2

SPRACHEN
English: README.en.txt
Australian: README.au.txt
Español: README.es.txt
Français: README.fr.txt
Deutsch: README.de.txt
Português (Brasil): README.pt-BR.txt

INHALTSVERZEICHNIS
1. Voraussetzungen
2. Programm installieren
3. Optionale Software auswählen
4. FXPAK Pro einrichten
5. RetroArch einrichten
6. Ordner und Dateien auswählen
7. Katalog aktualisieren
8. Hacks herunterladen und erstellen
9. ROMs auf eine SD-Karte kopieren
10. Einen Hack spielen und verfolgen
11. Timer, Mein Tracker und Statistiken
12. LiveSplit, OBS Studio und Streamlabs Desktop
13. Updates, Sicherung und Rollback
14. Fehlerbehebung und Datenschutz

1. VORAUSSETZUNGEN

* Ein 64-Bit-PC mit Windows 10 oder Windows 11.
* Ein Ordner für gepatchte ROMs.
* Internet für Katalogaktualisierungen und optionale Downloads.
* Ein FXPAK Pro/SD2SNES oder RetroArch unter Windows.
* Ihr eigenes rechtmäßig erworbenes, sauberes Super-Mario-World-ROM, wenn Sie
  aus moderierten Patches spielbare ROMs erstellen möchten.

SMW Stream Tracker enthält und lädt kein kommerzielles Basis-ROM herunter.

2. PROGRAMM INSTALLIEREN

1. Starten Sie SMWStreamTracker_Setup_1.0.2.exe.
2. Wählen Sie auf dem ersten Bildschirm eine Sprache.
3. Lesen Sie den Hinweis zu optionaler Software und ROMs.
4. Wählen Sie FXPAK Pro oder RetroArch als erste Plattform.
5. Markieren Sie die optionalen Werkzeuge, die installiert werden sollen.
6. Wählen Sie ROM- und OBS-Ordner oder lassen Sie die Felder leer, um sie später
   einzurichten.
7. Beenden Sie die Installation und öffnen Sie diese Anleitung.

Vorhandene Tracker-Einstellungen bleiben bei Installation und Updates erhalten.

3. OPTIONALE SOFTWARE AUSWÄHLEN

SNI wird für die Live-Verbindung dringend empfohlen. QUsb2Snes ist eine
optionale ältere/fortgeschrittene Brücke, hauptsächlich für FXPAK-Pro- und
SD2SNES-Benutzer. RetroArch ist optional. Überspringen Sie es, wenn es bereits
installiert ist oder Sie nur FXPAK Pro verwenden. Bei Auswahl lädt Setup auch
den bsnes-mercury Performance-Libretro-Core herunter.

4. FXPAK PRO EINRICHTEN

1. Verbinden Sie den USB-Port des FXPAK Pro mit dem PC und schalten Sie die
   Konsole ein.
2. Starten Sie SNI oder QUsb2Snes und warten Sie auf das Gerät.
3. Öffnen Sie SMW Stream Tracker und wählen Sie Datei > FXPAK Pro.
4. Klicken Sie auf Aktualisieren, falls sich der Status nicht ändert.
5. Prüfen Sie in Einstellungen die Dienstdatei und WebSocket-Adresse. Üblich
   ist ws://localhost:23074.

Falls das Gerät fehlt, prüfen Sie USB-Kabel, kompatible Firmware, Windows-Treiber
und ob ein anderes Programm die Verbindung verwendet.

5. RETROARCH EINRICHTEN

1. Installieren Sie RetroArch oder wählen Sie retroarch.exe in Einstellungen.
2. Installieren Sie Nintendo - SNES / SFC (bsnes-mercury Performance) über Online Updater > Core
   Downloader.
3. Öffnen Sie Einstellungen > Netzwerk in RetroArch.
4. Aktivieren Sie Netzwerkbefehle und behalten Sie Port 55355 bei.
5. Wählen Sie in SMW Stream Tracker Datei > RetroArch.
6. Wählen Sie retroarch.exe und bsnes_mercury_performance_libretro.dll, falls sie nicht erkannt
   wurden.
7. Verwenden Sie Spielen. Beim Wechsel speichert der Tracker den Zustand,
   schließt den aktuellen Inhalt und startet den gewählten Hack.

6. ORDNER UND DATEIEN AUSWÄHLEN

Öffnen Sie Datei > Einstellungen und prüfen Sie:

* Bibliothek für gepatchte ROMs.
* OBS-Textausgabeordner.
* Sauberes Basis-ROM zum Anwenden moderierter Patches.
* SNI/QUsb2Snes-Datei für FXPAK Pro.
* RetroArch-Datei und bsnes-mercury Performance-Core.

Führen Sie nach Pfadänderungen die Zustandsprüfung aus.

7. KATALOG AKTUALISIEREN

1. Öffnen Sie Downloads.
2. Wählen Sie Moderierte Hacks von SMW Central aktualisieren.
3. Warten Sie; Anfragen werden zur Vermeidung von Limits zeitlich verteilt.
4. Öffnen Sie Gesamten Katalog anzeigen zum Suchen, Filtern und Sortieren.
5. Klicken Sie einmal auf Hinzugefügt am für neueste und erneut für älteste.

Nur die Zelle Schwierigkeit verwendet die konfigurierte Schwierigkeitsfarbe.

8. HACKS HERUNTERLADEN UND ERSTELLEN

1. Öffnen Sie Downloads > Fehlende SMW-Hacks herunterladen.
2. Wählen Sie Ihr sauberes, rechtmäßiges Super-Mario-World-ROM.
3. Wählen Sie den gepatchten ROM-Bibliotheksordner.
4. Filtern Sie bei Bedarf, prüfen Sie die Vorschau und wählen Sie Moderierte
   Hacks herunterladen.

Das Werkzeug lädt moderierte Patches und wendet sie lokal an. Es lädt nie ein
Basis-ROM herunter und überspringt vorhandene Spiele.

9. ROMS AUF EINE SD-KARTE KOPIEREN

Wählen Sie das SD-Ziel in Einstellungen und aktivieren Sie das Kopieren beim
Download. Prüfen Sie das Laufwerk genau. FXPAK Pro stellt seine SD-Karte über
die Tracking-USB-Verbindung normalerweise nicht als Windows-Laufwerk bereit;
für dauerhaftes Massenkopieren wird meist ein Kartenleser benötigt.

10. EINEN HACK SPIELEN UND VERFOLGEN

Geben Sie Text in Hack suchen oder auswählen ein, wählen Sie ein Ergebnis und
klicken Sie auf Spielen. Zufälliger Hack wählt aus der Bibliothek. Zu Mein
Tracker hinzufügen erstellt einen Eintrag und Hack abschließen speichert den
Abschluss. Ein Klick außerhalb schließt die Liste.

11. TIMER, MEIN TRACKER UND STATISTIKEN

Steuern Sie Spiel- und Level-Timer auf der Hauptseite. Mein Tracker bietet
Suche, Filter, editierbare Felder, Schwierigkeitsfarben, Bewertungs- und
Fortschrittsbalken sowie CSV/XLSX-Export. Statistiken fassen Fortschritt,
Bewertungen, Spielzeit, Aktivität und Schwierigkeit zusammen.

12. LIVESPLIT, OBS STUDIO UND STREAMLABS DESKTOP

Sie können LiveSplit-Fenster aufnehmen, die Textdateien des Trackers verwenden
oder beide Methoden kombinieren. Die Textdateien sind einfacher und benötigen
kein LiveSplit.

DEN LIVESPLIT-SPIELTIMER VERBINDEN

1. Laden Sie LiveSplit von https://livesplit.org/downloads/ herunter und
   entpacken Sie es.
2. Starten Sie LiveSplit.exe. Der Server ist integriert; die alte separate
   LiveSplit-Server-Komponente wird nicht benötigt.
3. Klicken Sie LiveSplit mit der rechten Maustaste an, öffnen Sie Einstellungen
   und setzen Sie Server Port auf 16834.
4. Bei nur einem Timer ist der automatische TCP-Start optional. Bei zwei
   Fenstern starten Sie jeden Server nach der Portprüfung manuell mit
   Control > Start TCP/WS Server.
5. Öffnen Sie in SMW Stream Tracker Datei > Einstellungen, setzen Sie Game
   LiveSplit port auf 16834, speichern Sie und testen Sie den Spieltimer.

EINEN SEPARATEN LIVESPLIT-LEVELTIMER VERBINDEN

1. Lassen Sie das erste LiveSplit-Fenster offen und starten Sie LiveSplit.exe
   ein zweites Mal.
2. Setzen Sie im zweiten Fenster Server Port auf 16835 und starten Sie den
   TCP-Server.
3. Lassen Sie Level LiveSplit port im Tracker auf 16835.
4. Testen Sie Start, gemeinsamen Start und Zurücksetzen des Leveltimers.

Beide Fenster müssen unterschiedliche Ports verwenden. Prüfen Sie bei späteren
Starts zuerst 16834 im ersten und 16835 im zweiten Fenster. Die Verbindung
bleibt lokal auf 127.0.0.1.

LIVESPLIT IN OBS STUDIO ANZEIGEN

1. Lassen Sie die LiveSplit-Fenster geöffnet und nicht minimiert.
2. Wählen Sie in Quellen + > Fensteraufnahme.
3. Wählen, positionieren und skalieren Sie das Spieltimer-Fenster.
4. Fügen Sie eine zweite Fensteraufnahme für den Leveltimer hinzu.
5. Erstellen Sie eine kurze Testaufnahme.

LIVESPLIT IN STREAMLABS DESKTOP ANZEIGEN

1. Lassen Sie die LiveSplit-Fenster geöffnet und nicht minimiert.
2. Wählen Sie in Quellen + > Bildschirmaufnahme. Falls Fensteraufnahme als
   eigene Option erscheint, verwenden Sie diese.
3. Wählen, positionieren und skalieren Sie beide LiveSplit-Fenster.
4. Erstellen Sie vor dem Stream eine kurze Testaufnahme.

TIMER-TEXTDATEIEN IN OBS ODER STREAMLABS VERWENDEN

1. Wählen Sie unter Datei > Einstellungen einen OBS-Ausgabeordner und speichern
   Sie.
2. Wählen oder starten Sie einen Hack und bedienen Sie beide Timer einmal.
3. Öffnen Sie den Ordner mit Datei > OBS-Textordner öffnen.
4. Fügen Sie in OBS oder Streamlabs eine Text-(GDI+)-Quelle hinzu.
5. Aktivieren Sie Aus Datei lesen und wählen Sie game_timer.txt.
6. Fügen Sie eine zweite Textquelle mit level_timer.txt hinzu.
7. Stellen Sie Schriftart, Farbe, Kontur, Ausrichtung und Größe ein.
8. Wiederholen Sie dies bei Bedarf für hack_name.txt, author.txt, exits.txt, level_deaths.txt oder total_deaths.txt.

Level-Tode bleiben bei Wiederholungsversuchen erhalten und werden beim Start
eines anderen Levels zurückgesetzt. Gesamttode werden für jedes ROM und jeden
Spielstand Mario A, B oder C separat gespeichert. Beide Beschriftungen können
unter Datei > OBS-Einstellungen geändert werden. death_counter.txt spiegelt
weiterhin level_deaths.txt für vorhandene Szenen.

SMW Stream Tracker muss geöffnet bleiben, damit die Dateien aktualisiert
werden. Bei einer leeren oder alten Anzeige prüfen Sie den Ordner und bedienen
Sie den Timer erneut.

Offizielle Hilfe:
LiveSplit-Server: https://github.com/LiveSplit/LiveSplit#the-livesplit-server
OBS-Textquellen: https://obsproject.com/kb/text-sources
Streamlabs-Aufnahme: https://streamlabs.com/content-hub/post/how-to-capture-your-screen-in-streamlabs-desktop

13. UPDATES, SICHERUNG UND ROLLBACK

Verwenden Sie SMWStreamTracker_Update_VERSION.exe für kleine Versionen, nachdem
einmal vollständig installiert wurde. Der Updater bewahrt die vorherige Datei
für einen Rollback. Sichern Sie Datenbank, Konfiguration und ROM-Bibliothek vor
größeren System- oder Speicheränderungen.

14. FEHLERBEHEBUNG UND DATENSCHUTZ

* FXPAK getrennt: SNI/QUsb2Snes, USB, Firmware und Port 23074 prüfen.
* RetroArch verfolgt nicht: Netzwerkbefehle auf Port 55355 aktivieren.
* Spiel startet nicht: ROM, Programmdatei, Core und Pfade prüfen.
* Langsamer Katalog: zeitlich verteilte Wiederholungen abwarten.

Tracker-Daten und Pfade werden lokal verarbeitet. Katalog-, Abhängigkeits-,
Update- und Synchronisierungsfunktionen verbinden sich nur bei Verwendung.
Lesen Sie PRIVACY.txt und THIRD_PARTY_NOTICE.txt für vollständige Hinweise.
