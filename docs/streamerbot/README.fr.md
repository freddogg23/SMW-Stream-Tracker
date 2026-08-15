# Prédictions automatiques de niveau avec Streamer.bot

SMW Stream Tracker ajoute des événements à `streamerbot_level_events.txt` dans le dossier de sortie texte OBS / diffusion choisi. Le tracker ne se connecte pas directement à Twitch ni à Streamer.bot.

- Le premier niveau demande : `Vais-je terminer ce niveau en moins de 100 vies ?`
- Après le premier niveau terminé, la limite devient la moyenne arrondie des vies utilisées par niveau pendant la session Streamer.bot actuelle.
- `Oui` gagne si le niveau est terminé avant la perte de la vie limite. `Non` gagne dès que cette vie est perdue sans réussite.
- Un changement de ROM, un retour au titre, un autre niveau ou la fermeture du tracker annule la prédiction et rembourse les points.

## Configuration

1. Choisissez un dossier **Sortie texte OBS / diffusion** dans le tracker. Il n'est pas nécessaire d'ajouter ce fichier à OBS.
2. Connectez le compte diffuseur Twitch dans Streamer.bot.
3. Dans **Services > File Tails**, créez et activez un File Tail pour `streamerbot_level_events.txt`.
4. Créez l'action **SMW Tracker - Automatic Level Predictions**.
5. Ajoutez le déclencheur **Core > File I/O > File Tail > Changed** et sélectionnez ce File Tail.
6. Ajoutez **Core > C# > Execute C# Code**, collez `SMW_Level_Predictions.cs`, compilez et enregistrez.
7. En dessous, ajoutez **Core > Logic > Switch** avec l'entrée `%smwCommand%` et trois cas :
   - `start` : **Twitch > Predictions > Create Prediction**, titre `%smwPredictionTitle%`, réponses `%smwYesOutcome%` et `%smwNoOutcome%`, fenêtre de 60 secondes.
   - `resolve` : **Twitch > Predictions > Resolve Last Prediction**, Winning Index `%smwWinningIndex%` (`0` = Oui, `1` = Non).
   - `cancel` : **Twitch > Predictions > Cancel Active Prediction**.
8. Lancez Streamer.bot avant le premier niveau jouable et ne gardez qu'une seule prédiction active.

La moyenne est réinitialisée au redémarrage de Streamer.bot. La résolution distribue automatiquement les points de chaîne. Les prédictions Twitch sont réservées aux affiliés et partenaires.
