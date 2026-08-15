# Previsões automáticas de fase com Streamer.bot

O SMW Stream Tracker acrescenta eventos ao arquivo `streamerbot_level_events.txt` na pasta escolhida para textos do OBS / transmissão. O tracker não se conecta diretamente ao Twitch nem ao Streamer.bot.

- A primeira fase pergunta: `Vou vencer esta fase em até 100 vidas?`
- Depois da primeira fase concluída, o limite passa a ser a média arredondada de vidas usadas por fase na sessão atual do Streamer.bot.
- `Sim` vence se a fase for concluída antes da perda da vida limite. `Não` vence quando essa vida é perdida sem concluir a fase.
- Trocar a ROM, voltar ao título, escolher outra fase ou fechar o tracker cancela a previsão e devolve os pontos.

## Configuração

1. Escolha uma pasta de **saída de texto do OBS / transmissão** no tracker. Não é preciso adicionar esse arquivo ao OBS.
2. Conecte a conta do transmissor da Twitch no Streamer.bot.
3. Em **Services > File Tails**, crie e ative um File Tail para `streamerbot_level_events.txt`.
4. Crie a ação **SMW Tracker - Automatic Level Predictions**.
5. Adicione o gatilho **Core > File I/O > File Tail > Changed** e selecione o File Tail.
6. Adicione **Core > C# > Execute C# Code**, cole `SMW_Level_Predictions.cs`, compile e salve.
7. Abaixo, adicione **Core > Logic > Switch** com entrada `%smwCommand%` e três casos:
   - `start`: **Twitch > Predictions > Create Prediction**, título `%smwPredictionTitle%`, respostas `%smwYesOutcome%` e `%smwNoOutcome%`, janela de 60 segundos.
   - `resolve`: **Twitch > Predictions > Resolve Last Prediction**, Winning Index `%smwWinningIndex%` (`0` = Sim, `1` = Não).
   - `cancel`: **Twitch > Predictions > Cancel Active Prediction**.
8. Inicie o Streamer.bot antes da primeira fase jogável e mantenha só uma previsão ativa.

A média é reiniciada quando o Streamer.bot reinicia. Resolver a previsão distribui automaticamente os Pontos do Canal. As previsões da Twitch estão disponíveis apenas para Afiliados e Parceiros.
