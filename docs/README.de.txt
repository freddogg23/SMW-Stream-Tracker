SMW STREAM TRACKER - VOLLSTÄNDIGE EINRICHTUNGSANLEITUNG
Version 1.1.1

SPRACHEN
English: README.en.txt
Australian: README.au.txt
Español: README.es.txt
Français: README.fr.txt
Deutsch: README.de.txt
Português (Brasil): README.pt-BR.txt

MACOS-UNTERSTÜTZUNG

SMW Stream Tracker verwendet jetzt native Mac-Pfade und bietet Builds für
Apple Silicon (arm64) und Intel (x86_64). Lade das passende DMG herunter und
ziehe die App in den Ordner Programme. Die Tracker-Daten bleiben in:
~/Library/Application Support/SMWStreamTracker

Verbindungs- und Emulator-Einrichtung lädt die offiziellen Mac-Versionen von
SNI, QUsb2Snes und RetroArch einschließlich des richtigen bsnes-mercury-Cores.
Das klassische LiveSplit läuft nur unter Windows. Deshalb stellt die Mac-App
synchronisierte Fenster für Spiel- und Level-Timer sowie game_timer.txt und
level_timer.txt für OBS bereit. Katalog, Patchen, FXPAK-Emoji-Aliase,
Datenbank, Arbeitsmappen und OBS-Texte funktionieren unter Windows und Mac
gleich.

NEU IN VERSION 1.1.1

* SMW Central hat jetzt eine integrierte Startseite mit Live-Inhaltskarten,
  ausführlicheren Hack-Details, Tag-Suche, Screenshots sowie Konto- und
  Kommentarwerkzeugen.
* SMW Central Radio und die SPC-Wiedergabe besitzen einen kompakten Player, der
  verschoben, skaliert, minimiert und neben dem Tracker geöffnet bleiben kann.
* Der optionale OBS-Aufnahmemodus hält blaue Tracker-Fenster im Hauptfenster,
  damit eine einzige OBS-Fensteraufnahme sie erfassen kann.
* Der normale Windows-Build ergänzt kompatibilitätsgeprüfte MiSTer-Speicherstände
  5–11 mit exakt wiederherstellbarer Sicherung. Native Plätze 1–4 bleiben
  unverändert und F12 öffnet weiterhin das MiSTer-Menü.
* Einrichtungs-, Anwendungs-, OBS- und LiveSplit-Menüs wurden neu geordnet, ohne
  den Assistenten zu stören. Spielmodi kehrt nach dem Start zum Dashboard zurück.
* Veraltete MiSTer-Verbindungsdaten beeinflussen RetroArch nicht mehr; außerdem
  wurden Fenstergrößenänderungen und das Schließen von Google Sheets verbessert.
* Jeder neue Text ist in alle sechs Sprachen übersetzt und wird durch eine
  umfassendere automatische Übersetzungsprüfung abgesichert.

NEU IN VERSION 1.1.0

* MiSTer FPGA ist jetzt eine vollständige Spielplattform. Die Ein-Klick-Einrichtung
  findet die Konsole im lokalen Netzwerk, richtet Fernstart und Live-Tracking ein
  und funktioniert mit MiSTer sowie MiSTer Multisystem².
* Spielmodi enthält Zufälligen Hack spielen, Hack-Draft, Schwierigkeitsleiter,
  Creator Spotlight, Zeitkapsel und Hall-of-Fame-Tour mit übersetzten blauen
  Fenstern und Beschreibungen beim Darüberfahren.
* Tabellenkalkulations-Einstellungen bietet einen intelligenten Excel-Import.
  Google Sheets synchronisiert in beide Richtungen, und bei jedem ordentlichen
  Beenden wird eine neue Tracker-/Datenbank-Wiederherstellungskopie gespeichert.
* Mein Tracker hat kompakte Hinzufügen-/Entfernen-Schaltflächen, Mehrfachlöschung,
  automatische Hack-#-Neunummerierung und übersichtlichere Tabellen-Untermenüs.
* Menüs und Einstellungen blenden Optionen aus, die nicht zur ausgewählten
  Plattform FXPAK Pro, RetroArch oder MiSTer gehören.
* Die optionale RetroArch-Einrichtung unter Windows ist schneller; RetroArch
  bleibt geschlossen, bis ein Spiel gestartet wird.
* Streamer.bot-Levelereignisse und übersetzte Anleitungen ermöglichen eine
  optionale Automatisierung von Twitch-Vorhersagen.
* Alle neuen Menüs, Schaltflächen, Statusanzeigen, Meldungen und
  Einrichtungsanweisungen sind in allen sechs Sprachen übersetzt.

* Das native Verhalten unter Windows und macOS umfasst reproduzierbare Builds
  für Apple Silicon und Intel sowie die plattformgerechte Einrichtung von SNI,
  QUsb2Snes und RetroArch.
* Fensterbewegungen und das Scrollen in Mein Tracker sind flüssiger; das Banner
  wird zwischengespeichert, Tabellenrahmen bleiben ausgerichtet und ein kleineres
  Hauptfenster kann bis zu den unteren Bedienelementen gescrollt werden.
* Ein übersetztes blaues Zu Tracker hinzufügen-Formular übernimmt vollständige
  Hack- und Fortschrittsdaten. Eigene unmoderierte Hacks bleiben neben dem
  Katalog und können gepatcht und auf den FXPAK Pro übertragen werden.
* Aktualisieren kann eine laufende FXPAK-Pro-Sitzung vor dem Neuverbinden sicher
  zurücksetzen; Aus Mein Tracker entfernen verwendet nun den blauen Dialog.
* Ein neuer Assistent für den ersten Start lässt alle erforderlichen Schritte
  für Downloads, Verbindung, Katalog, Aktualisierung, Patchen, FXPAK und OBS
  nacheinander blinken.
* Nach der Auswahl von SNI oder RetroArch hören QUsb2Snes und die gewählte
  Option auf zu blinken; nur die andere erforderliche Option bleibt markiert.
* SMW-Central-Katalog und Hack-Downloader verwenden blaue Auswahllistenpfeile,
  gelbe Bildlaufleisten, breitere Typfelder und hellblaue Zellrahmen.
* Bei FXPAK-Pro-Übertragungen wird jedes Emoji im ROM-Dateinamen durch seinen
  lesbaren Unicode-Namen ersetzt, auch bei zukünftigen Hacks. Katalog, Tracker
  und aktuelle Spielanzeige behalten den Originaltitel; die gespeicherte
  Zuordnung ruft die umbenannte ROM bei der Auswahl wieder auf.
* Wenn der USB-Upload aktiviert ist, werden vorhandene lokale ROMs mit Emojis
  ebenfalls automatisch übertragen und zugeordnet. Frühere Downloads werden so
  repariert, ohne sie erneut herunterzuladen oder zu patchen.
* Beim Start eines Hacks mit Emojis findet der Tracker dessen lesbaren FXPAK-Alias
  oder lädt den fehlenden Alias automatisch hoch. Die dauerhafte Verknüpfung nutzt
  die SMW-Central-ID, damit im Tracker immer der Originaltitel angezeigt wird.
* Während einer FXPAK-Übertragung wird die aktive SNI/QUsb2Snes-Verbindung des
  Trackers vorübergehend angehalten und danach automatisch wiederhergestellt,
  damit sie den Upload mit dem sicheren Namen ohne Emojis nicht blockiert.
* Die OBS-Seite erklärt die Wiederverwendung vorhandener Textquellen. Zwei
  Schaltflächen laden getrennte Spiel- und Level-LiveSplit-Kopien herunter und
  richten sie automatisch auf den Ports 16834 und 16835 ein.
* Die Statistikseite verwendet das neue zweispaltige Layout, größere Diagramme
  und eine kompakte Fortschritt-nach-Schwierigkeit-Tabelle.
* Alle Meldungen, Menüs, Bedienelemente, Statuszeilen, Dateiauswahlen und
  Einrichtungsseiten sind in allen verfügbaren Sprachen übersetzt.
* Info und Updates enthält eine Discord-beitreten-Schaltfläche für Hilfe oder
  den Kontakt zu FredDOGG23: https://discord.gg/fHkTRgqjcr

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

* Ein 64-Bit-PC mit Windows 10/11 oder ein unterstützter Intel-/Apple-Silicon-Mac.
* Ein Ordner für gepatchte ROMs.
* Internet für Katalogaktualisierungen und optionale Downloads.
* Ein FXPAK Pro/SD2SNES, RetroArch oder ein MiSTer FPGA im lokalen Netzwerk.
* Ihr eigenes rechtmäßig erworbenes, sauberes Super-Mario-World-ROM, wenn Sie
  aus moderierten Patches spielbare ROMs erstellen möchten.

SMW Stream Tracker enthält und lädt kein kommerzielles Basis-ROM herunter.

2. PROGRAMM INSTALLIEREN

1. Starten Sie SMWStreamTracker_Setup_1.1.1.exe.
2. Wählen Sie auf dem ersten Bildschirm eine Sprache.
3. Lesen Sie den Hinweis zu optionaler Software und ROMs.
4. Wählen Sie FXPAK Pro, RetroArch oder MiSTer als erste Plattform.
5. Markieren Sie die optionalen Werkzeuge, die installiert werden sollen.
6. Wählen Sie ROM- und OBS-Ordner oder lassen Sie die Felder leer, um sie später
   einzurichten.
7. Beenden Sie die Installation und öffnen Sie diese Anleitung.

Vorhandene Tracker-Einstellungen bleiben bei Installation und Updates erhalten.
Eine vollständige Deinstallation entfernt Tracker-Einstellungen und -Daten,
LiveSplit-Kopien sowie die vom Tracker erstellten OBS-Textdateien. RetroArch,
SNI, QUsb2Snes und alle ROM-Dateien und ROM-Ordner bleiben erhalten. Bei einer
späteren Neuinstallation erscheint der Willkommens- und Einrichtungsbildschirm
erneut.
Für das aktuelle Windows-Konto kann nur eine Kopie installiert werden. Beim
erneuten Start des vollständigen Installers können Sie die aktuelle Kopie
entfernen und mit einer Neuinstallation fortfahren oder den Tracker vollständig
deinstallieren und Setup beenden. Beide Optionen erhalten RetroArch, SNI,
QUsb2Snes und alle ROM-Dateien.
Die Sprache kann jederzeit über Datei > Sprache geändert werden. Die
Hauptoberfläche wird sofort neu aufgebaut, ohne Beschriftungen der vorherigen
Sprache beizubehalten.

3. OPTIONALE SOFTWARE AUSWÄHLEN

Für FXPAK Pro oder SD2SNES wird nur QUsb2Snes benötigt. SNI ist für FXPAK Pro
nicht erforderlich. Für RetroArch werden RetroArch und SNI benötigt; SNI
stellt die Live-Speicherverbindung bereit. In der Anleitung mit blinkenden
Schaltflächen kann QUsb2Snes allein fortfahren. Wird SNI oder RetroArch gewählt,
bleibt der Verbindungsschritt aktiv, bis beide abgeschlossen sind. Bei Auswahl
von RetroArch lädt und
entpackt das blaue Setup die offizielle portable Version in seinen Tools-Ordner,
installiert den bsnes-mercury Performance-Core, aktiviert Netzwerkbefehle auf
Port 55355 und speichert beide Pfade. Ein zweiter RetroArch-Assistent öffnet
sich nicht.

Wenn Sie ein Werkzeug bei der Installation überspringen, öffnen Sie später
Downloads > Verbindungs- und Emulator-Einrichtung. Die App kann eine vorhandene
SNI-, QUsb2Snes- oder RetroArch-Installation finden oder sie in Ihrem
Benutzerprofil installieren. Bei RetroArch installiert sie außerdem den
empfohlenen Core, aktiviert Netzwerkbefehle auf Port 55355 und speichert beide
Dateipfade in den Tracker-Einstellungen.
Wenn eine Kopie gefunden wird, können Sie sie in einem übersetzten blauen
Bestätigungsfenster automatisch verwenden oder einen neuen Download auswählen.

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

Mit Katalog zurücksetzen am unteren Rand werden alle lokal gespeicherten
moderierten und wartenden Einträge entfernt. Zuerst wird eine
Wiederherstellungssicherung erstellt. Fortschritt, Bewertungen, Notizen, eigene
Hacks, ROM-Zuordnungen und ROM-Dateien bleiben erhalten.

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
klicken Sie auf Spielen. Spielmodi auf der Hauptseite öffnet eine Vollbildseite
mit einer Startseite-Schaltfläche. Wählen Sie Zufälligen Hack spielen für ein
zufällig ausgewähltes heruntergeladenes Spiel mit den gewählten Filtern.
Zu Mein Tracker hinzufügen
erstellt einen Eintrag und Hack abschließen speichert den Abschluss. Ein Klick
außerhalb schließt die Liste.

11. TIMER, MEIN TRACKER UND STATISTIKEN

Steuern Sie Spiel- und Level-Timer auf der Hauptseite. Mein Tracker bietet
Suche, Filter, editierbare Felder, Schwierigkeitsfarben, Bewertungs- und
Fortschrittsbalken sowie CSV/XLSX-Export. Statistiken fassen Fortschritt,
Bewertungen, Spielzeit, Aktivität und Schwierigkeit zusammen.

12. LIVESPLIT, OBS STUDIO UND STREAMLABS DESKTOP

Sie können LiveSplit-Fenster aufnehmen, die Textdateien des Trackers verwenden
oder beide Methoden kombinieren. Die Textdateien sind einfacher und benötigen
kein LiveSplit.

AUTOMATISCHE EINRICHTUNG VON ZWEI KOPIEN (EMPFOHLEN)

1. Öffnen Sie Hilfe > Einrichtung > LiveSplit-Timer einrichten.
2. Wählen Sie Spiel-LiveSplit (16834). Der Tracker lädt die aktuelle offizielle
   Version herunter, erstellt einen eigenen Ordner, richtet Port 16834 und den
   automatischen TCP-Serverstart ein und öffnet LiveSplit.
3. Wählen Sie Level-LiveSplit (16835). Der Tracker erstellt eine zweite Kopie,
   richtet Port 16835 und TCP-Autostart ein und öffnet sie.
4. Sobald beide Schaltflächen grün sind, wählen Sie Fertig und speichern.
5. Lassen Sie beide Fenster mit Tracker oder OBS geöffnet und nicht minimiert.
   Spätere Klicks öffnen die eingerichteten Kopien erneut.

MANUELLE EINRICHTUNG (ERSATZLÖSUNG)

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

IMPORT, GOOGLE SHEETS UND DAUERHAFTE EXCEL-SICHERUNG

Statistik > Vorhandene Tabelle importieren stellt aktuelle Mein-Tracker-Exporte
mit Fortschritt, Spielzeit, Toden, Bewertungen, Daten und Notizen wieder her.
Für den direkten Import öffnen Sie Mein Tracker > Aus Google Sheets
synchronisieren, fügen den normalen Freigabelink ein und wählen Jetzt
importieren. Geben Sie die Tabelle als Betrachter für Jeden mit dem Link frei;
sie muss ein Blatt Tracker oder My Tracker enthalten. Apps Script bleibt für
die automatische Synchronisierung verfügbar. Documents > SMW Stream Tracker Backups >
SMW_Stream_Tracker_Automatic_Backup.xlsx bleibt bei der Deinstallation erhalten.

13. UPDATES, SICHERUNG UND ROLLBACK

Verwenden Sie SMWStreamTracker_Update_VERSION.exe für kleine Versionen, nachdem
einmal vollständig installiert wurde. Der Updater bewahrt die vorherige Datei
für einen Rollback. Sichern Sie Datenbank, Konfiguration und ROM-Bibliothek vor
größeren System- oder Speicheränderungen.

14. FEHLERBEHEBUNG UND DATENSCHUTZ

* FXPAK getrennt: SNI/QUsb2Snes, USB, Firmware und Port 23074 prüfen.
* Aktueller Hack erkennt nach einem Update in der App keine Spiele mehr:
  Öffnen Sie Downloads > Verbindungs- und Emulator-Einrichtung > SNI
  installieren oder suchen (dringend empfohlen). Lassen Sie den Tracker SNI
  finden oder neu installieren, starten Sie SNI neu und wählen Sie Aktualisieren.
* RetroArch verfolgt nicht: Netzwerkbefehle auf Port 55355 aktivieren.
* Spiel startet nicht: ROM, Programmdatei, Core und Pfade prüfen.
* Langsamer Katalog: zeitlich verteilte Wiederholungen abwarten.

Tracker-Daten und Pfade werden lokal verarbeitet. Katalog-, Abhängigkeits-,
Update- und Synchronisierungsfunktionen verbinden sich nur bei Verwendung.
Lesen Sie PRIVACY.txt und THIRD_PARTY_NOTICE.txt für vollständige Hinweise.

MISTER-SCHNELLEINRICHTUNG

Wählen Sie bei einer neuen Windows-Installation MiSTer FPGA und lassen Sie
MiSTer beim ersten Start einrichten aktiviert. Der blinkende Assistent führt
Sie zur automatischen Einrichtungsschaltfläche.

Verbinden Sie MiSTer und diesen Computer mit demselben Router und öffnen Sie
Downloads > Verbindung und Emulator > MiSTer einrichten. Wählen Sie MiSTer
suchen und einrichten. Der Tracker findet und prüft das Gerät, installiert oder
repariert die Live-Verfolgung, erstellt die Spieleordner, wählt MiSTer aus,
richtet eine eigene automatische App-Anmeldung ein und testet die Verbindung.
Falls gefragt, lautet die SSH-Werksanmeldung root, Port 22, Passwort 1; das
Passwort wird nie gespeichert. Hacks werden unter sicheren Dateinamen kopiert,
während ihre echten Katalogtitel erhalten bleiben.

Der normale Windows-Build installiert die MiSTer-Speicherstände 5–11 automatisch,
wenn MiSTer suchen und einrichten oder Virtuelle Speicherplätze installieren
ausgeführt wird. Alt+F5 bis Alt+F11 speichern, F5 bis F11 laden die Stände 5–11,
F12 öffnet weiterhin das MiSTer-Menü und die
nativen Plätze 1–4 bleiben unverändert. Tracker-Updates behalten diese Funktion und
dürfen eine zuvor vom Tracker installierte Version sicher ersetzen. Wird MiSTer
Main unabhängig aktualisiert, überschreibt der Tracker die unbekannte Datei
nicht und führt kein Downgrade durch. Verwenden Sie vorher Vorherige
MiSTer-Version wiederherstellen und danach einen Build für die neue Main-Version.
