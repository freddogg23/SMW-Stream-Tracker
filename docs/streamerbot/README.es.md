# Predicciones automáticas de nivel con Streamer.bot

SMW Stream Tracker agrega eventos a `streamerbot_level_events.txt` dentro de la carpeta elegida para textos de OBS / transmisión. El tracker no se conecta directamente a Twitch ni a Streamer.bot.

- El primer nivel pregunta: `¿Superaré este nivel en 100 vidas?`
- Después del primer nivel superado, el límite es el promedio redondeado de vidas usadas por nivel durante la sesión actual de Streamer.bot.
- `Sí` gana si completas el nivel antes de perder la vida límite. `No` gana cuando se pierde esa vida sin completar el nivel.
- Cambiar de ROM, volver al título, elegir otro nivel o cerrar el tracker cancela una predicción pendiente y devuelve los puntos.

## Configuración

1. Elige una carpeta de **salida de texto de OBS / transmisión** en el tracker. No tienes que añadir este archivo a OBS.
2. Conecta la cuenta de transmisor de Twitch en Streamer.bot.
3. En **Services > File Tails**, crea y activa un File Tail para `streamerbot_level_events.txt`.
4. Crea la acción **SMW Tracker - Automatic Level Predictions**.
5. Añade el disparador **Core > File I/O > File Tail > Changed** y selecciona el File Tail.
6. Añade **Core > C# > Execute C# Code**, pega `SMW_Level_Predictions.cs`, compila y guarda.
7. Debajo, añade **Core > Logic > Switch** con entrada `%smwCommand%` y tres casos:
   - `start`: **Twitch > Predictions > Create Prediction**, título `%smwPredictionTitle%`, respuestas `%smwYesOutcome%` y `%smwNoOutcome%`, y una ventana de 60 segundos.
   - `resolve`: **Twitch > Predictions > Resolve Last Prediction**, Winning Index `%smwWinningIndex%` (`0` = Sí, `1` = No).
   - `cancel`: **Twitch > Predictions > Cancel Active Prediction**.
8. Inicia Streamer.bot antes de entrar al primer nivel jugable y mantén solo una predicción activa.

El promedio se reinicia al reiniciar Streamer.bot. Resolver la predicción reparte automáticamente los puntos del canal. Las predicciones de Twitch solo están disponibles para Afiliados y Socios.
