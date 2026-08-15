# Automatic level predictions with Streamer.bot — Aussie edition

SMW Stream Tracker chucks events into `streamerbot_level_events.txt` in your chosen OBS / stream text folder. The tracker leaves Twitch and Streamer.bot to do their own thing, mate.

- First cab off the rank asks: `Will I beat this level within 100 lives?`
- After the first clear, the limit becomes the rounded average lives used per cleared level for this Streamer.bot session.
- `Yes` wins if you clear it before the target life goes walkabout. `No` wins when that life is lost without a clear. Crikey.
- Changing ROMs, heading to the title screen, picking another level, or closing the tracker cancels the prediction and gives the points back. Fair go.

## Setup

1. Pick an **OBS / stream text output** folder in the tracker. You don't need to whack this file into OBS.
2. Connect your Twitch broadcaster account in Streamer.bot.
3. Under **Services > File Tails**, create and enable a File Tail for `streamerbot_level_events.txt`.
4. Create an action named **SMW Tracker - Automatic Level Predictions**.
5. Add **Core > File I/O > File Tail > Changed** as the trigger and select that File Tail.
6. Add **Core > C# > Execute C# Code**, paste in `SMW_Level_Predictions.cs`, then compile and save it.
7. Under it, add **Core > Logic > Switch** with `%smwCommand%` and three cases:
   - `start`: **Twitch > Predictions > Create Prediction**, title `%smwPredictionTitle%`, outcomes `%smwYesOutcome%` and `%smwNoOutcome%`, 60-second window.
   - `resolve`: **Twitch > Predictions > Resolve Last Prediction**, Winning Index `%smwWinningIndex%` (`0` = Yes, `1` = No).
   - `cancel`: **Twitch > Predictions > Cancel Active Prediction**.
8. Fire up Streamer.bot before the first playable level and keep only one prediction active at a time. Too easy.

The average resets when Streamer.bot restarts. Resolving the prediction pays out the Channel Points automatically. Twitch Predictions are for Affiliates and Partners only, mate.
