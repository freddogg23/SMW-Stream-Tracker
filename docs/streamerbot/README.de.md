# Automatische Level-Vorhersagen mit Streamer.bot

SMW Stream Tracker hängt Ereignisse an `streamerbot_level_events.txt` im gewählten OBS-/Stream-Textordner an. Der Tracker verbindet sich nicht direkt mit Twitch oder Streamer.bot.

- Das erste Level fragt: `Schaffe ich dieses Level innerhalb von 100 Leben?`
- Nach dem ersten abgeschlossenen Level wird der Grenzwert zum gerundeten Durchschnitt der pro Level verbrauchten Leben in der aktuellen Streamer.bot-Sitzung.
- `Ja` gewinnt, wenn das Level vor dem Verlust des Grenzlebens beendet wird. `Nein` gewinnt, sobald dieses Leben ohne Abschluss verloren geht.
- ROM-Wechsel, Titelseite, anderes Level oder Tracker-Ende bricht eine offene Vorhersage ab und erstattet die Punkte.

## Einrichtung

1. Wähle im Tracker einen Ordner für **OBS-/Stream-Textausgabe**. Die Datei muss nicht zu OBS hinzugefügt werden.
2. Verbinde in Streamer.bot das Twitch-Broadcaster-Konto.
3. Erstelle unter **Services > File Tails** einen aktiven File Tail für `streamerbot_level_events.txt`.
4. Erstelle die Aktion **SMW Tracker - Automatic Level Predictions**.
5. Füge **Core > File I/O > File Tail > Changed** als Trigger hinzu und wähle den File Tail.
6. Füge **Core > C# > Execute C# Code** hinzu, kopiere `SMW_Level_Predictions.cs` hinein, kompiliere und speichere.
7. Füge darunter **Core > Logic > Switch** mit `%smwCommand%` und drei Fällen hinzu:
   - `start`: **Twitch > Predictions > Create Prediction**, Titel `%smwPredictionTitle%`, Antworten `%smwYesOutcome%` und `%smwNoOutcome%`, 60 Sekunden.
   - `resolve`: **Twitch > Predictions > Resolve Last Prediction**, Winning Index `%smwWinningIndex%` (`0` = Ja, `1` = Nein).
   - `cancel`: **Twitch > Predictions > Cancel Active Prediction**.
8. Starte Streamer.bot vor dem ersten spielbaren Level und halte nur eine Vorhersage gleichzeitig aktiv.

Der Durchschnitt wird beim Neustart von Streamer.bot zurückgesetzt. Das Auflösen verteilt die Kanalpunkte automatisch. Twitch-Vorhersagen sind nur für Affiliates und Partner verfügbar.
