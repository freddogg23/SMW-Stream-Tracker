# Automatic level predictions with Streamer.bot

SMW Stream Tracker writes `streamerbot_level_events.txt` into the selected OBS / stream text output folder. It appends one machine-readable line when a playable level starts, a death is recorded, the level is cleared, or the level is abandoned. The tracker does not connect to Twitch or Streamer.bot.

Streamer.bot owns the prediction rules:

- The first level asks: `Will I beat this level within 100 lives?`
- After the first cleared level, the next target is the rounded average number of lives used per cleared level during the current Streamer.bot session.
- `Yes` wins when the level is cleared before the target life is lost.
- `No` wins as soon as the target life is lost without a clear.
- A ROM change, return to the title screen, different level selection, or tracker shutdown cancels an unresolved prediction and refunds the points.

## Streamer.bot setup

1. In SMW Stream Tracker, select an **OBS / stream text output** folder. The tracker creates `streamerbot_level_events.txt` there. You do not need to add this file to OBS.
2. In Streamer.bot, connect the Twitch broadcaster account.
3. Open **Services > File Tails**, add a File Tail for `streamerbot_level_events.txt`, and enable it.
4. Create an action named **SMW Tracker - Automatic Level Predictions**.
5. Add the trigger **Core > File I/O > File Tail > Changed** and select the File Tail from step 3.
6. Add **Core > C# > Execute C# Code**, paste the contents of `SMW_Level_Predictions.cs`, then compile and save it.
7. Directly below the C# sub-action, add **Core > Logic > Switch** with input `%smwCommand%` and these three cases:
   - `start`: add **Twitch > Predictions > Create Prediction**. Use `%smwPredictionTitle%` for the title, `%smwYesOutcome%` and `%smwNoOutcome%` for the two outcomes, and a prediction window such as 60 seconds.
   - `resolve`: add **Twitch > Predictions > Resolve Last Prediction** and use `%smwWinningIndex%` as the Winning Index. Index `0` is Yes and index `1` is No.
   - `cancel`: add **Twitch > Predictions > Cancel Active Prediction**.
8. Start Streamer.bot before entering the first playable level. Keep only one Twitch prediction active at a time.

The running average is intentionally stored as a non-persisted Streamer.bot global, so restarting Streamer.bot begins a new prediction session at 100 lives.

Twitch Predictions are available only to Twitch Affiliates and Partners. Resolving the prediction through Streamer.bot automatically distributes the winning Channel Points; no separate payout action is needed.
