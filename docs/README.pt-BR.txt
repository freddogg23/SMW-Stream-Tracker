SMW STREAM TRACKER - GUIA COMPLETO DE CONFIGURAÇÃO
Versão 1.0.11

IDIOMAS
English: README.en.txt
Australian: README.au.txt
Español: README.es.txt
Français: README.fr.txt
Deutsch: README.de.txt
Português (Brasil): README.pt-BR.txt

SUPORTE AO MACOS

O SMW Stream Tracker agora usa caminhos nativos do Mac e possui builds para
Apple Silicon (arm64) e Intel (x86_64). Baixe o DMG correspondente e arraste o
aplicativo para Aplicativos. Os dados do tracker ficam preservados em:
~/Library/Application Support/SMWStreamTracker

Configuração de conexão e emulador baixa as versões oficiais para Mac do SNI,
QUsb2Snes e RetroArch, incluindo o núcleo bsnes-mercury correto. O LiveSplit
clássico funciona somente no Windows; por isso o aplicativo para Mac fornece
janelas sincronizadas para os cronômetros de jogo e fase, além de
game_timer.txt e level_timer.txt para o OBS. Catálogo, patches, aliases de
emojis no FXPAK, banco de dados, planilhas e textos do OBS mantêm o mesmo
funcionamento no Windows e no Mac.

NOVIDADES DA VERSÃO 1.0.11

* O funcionamento nativo no Windows e macOS inclui compilações reproduzíveis
  para Apple Silicon e Intel e a configuração correta de SNI, QUsb2Snes e
  RetroArch para cada plataforma.
* Mover a janela e rolar Meu Tracker ficou mais suave; o banner é reutilizado,
  as bordas das tabelas permanecem alinhadas e uma janela principal menor pode
  rolar verticalmente até os controles inferiores.
* Um formulário azul e traduzido Adicionar ao tracker aceita todos os detalhes
  do hack e do progresso. Hacks personalizados não moderados permanecem com o
  catálogo e podem ser corrigidos e enviados ao FXPAK Pro.
* Atualizar pode reiniciar com segurança uma sessão ativa do FXPAK Pro antes de
  reconectar; Remover do Meu Tracker agora usa a caixa azul traduzida.
* Um novo guia de primeira execução faz cada etapa necessária de Downloads,
  conexão, catálogo, atualização, aplicação de patches, FXPAK e OBS piscar em
  ordem.
* Depois de escolher SNI ou RetroArch, o QUsb2Snes e a opção escolhida param de
  piscar; somente a outra opção obrigatória entre SNI e RetroArch fica destacada.
* O catálogo do SMW Central e o baixador usam setas azuis, barras de rolagem
  amarelas, campos de tipo mais largos e bordas de células em azul-claro.
* As transferências para o FXPAK Pro substituem cada emoji pelo nome Unicode
  legível no arquivo da ROM, inclusive em hacks futuros. O catálogo, o tracker
  e a exibição do jogo mantêm o título original, e o mapeamento salvo recupera
  a ROM renomeada quando ela é selecionada.
* Quando o envio por USB está ativado, ROMs locais existentes com emojis também
  são transferidas e mapeadas automaticamente. Isso corrige downloads anteriores
  sem baixar nem aplicar o patch novamente.
* Ao iniciar um hack com emojis, o tracker encontra o alias legível no FXPAK ou
  envia automaticamente o alias que estiver faltando. O vínculo permanente usa
  o ID do SMW Central, mantendo o título original na exibição do tracker.
* Durante uma transferência para o FXPAK, a conexão ativa do tracker com
  SNI/QUsb2Snes é pausada e reconectada automaticamente depois, impedindo que
  ela bloqueie o envio com o nome seguro sem emojis.
* A página do OBS explica como reutilizar fontes de texto existentes. Dois
  botões baixam e configuram cópias separadas do LiveSplit para jogo e fase nas
  portas 16834 e 16835.
* As estatísticas usam o novo layout de duas colunas, gráficos maiores e uma
  tabela compacta de Progresso por dificuldade.
* Todas as mensagens, menus, controles, estados, seletores e telas de
  configuração estão traduzidos em todos os idiomas disponíveis.
* Sobre e atualizações inclui um botão Entrar no Discord para obter ajuda ou
  falar com FredDOGG23: https://discord.gg/fHkTRgqjcr

ÍNDICE
1. O que você precisa
2. Instalar o programa
3. Escolher software opcional
4. Configurar o FXPAK Pro
5. Configurar o RetroArch
6. Escolher pastas e arquivos
7. Atualizar o catálogo
8. Baixar e criar hacks
9. Copiar ROMs para um cartão SD
10. Jogar e acompanhar um hack
11. Cronômetros, Meu Tracker e estatísticas
12. LiveSplit, OBS Studio e Streamlabs Desktop
13. Atualizações, backup e reversão
14. Solução de problemas e privacidade

1. O QUE VOCÊ PRECISA

* Um PC de 64 bits com Windows 10 ou Windows 11.
* Uma pasta para ROMs com patch.
* Internet para o catálogo e downloads opcionais.
* Um FXPAK Pro/SD2SNES ou RetroArch no Windows.
* Sua própria ROM limpa de Super Mario World obtida legalmente para criar ROMs
  jogáveis com patches moderados.

O SMW Stream Tracker não inclui nem baixa uma ROM-base comercial.

2. INSTALAR O PROGRAMA

1. Execute SMWStreamTracker_Setup_1.0.11.exe.
2. Escolha um idioma na primeira tela.
3. Leia o aviso sobre software opcional e ROMs.
4. Escolha FXPAK Pro ou RetroArch como plataforma inicial.
5. Marque as ferramentas opcionais que deseja instalar.
6. Escolha as pastas de ROMs e saída do OBS, ou deixe os campos vazios para
   configurar depois.
7. Conclua a instalação e abra este guia.

As configurações existentes são preservadas em instalações e atualizações.
Uma desinstalação completa remove configurações e dados do tracker, as cópias
do LiveSplit e os arquivos de texto do OBS criados pelo tracker. RetroArch,
SNI, QUsb2Snes e todos os arquivos e pastas de ROM são preservados. Uma nova
instalação posterior mostra novamente a tela de boas-vindas e configuração.
Apenas uma cópia pode ser instalada na conta atual do Windows. Ao executar o
instalador completo novamente, você pode remover a cópia atual e continuar com
uma instalação nova, ou desinstalar completamente o tracker e sair. As duas
opções preservam RetroArch, SNI, QUsb2Snes e todos os arquivos de ROM.
Você pode alterar o idioma a qualquer momento em Arquivo > Idioma. A interface
principal é reconstruída imediatamente, sem manter textos do idioma anterior.

3. ESCOLHER SOFTWARE OPCIONAL

A configuração do FXPAK Pro ou SD2SNES requer apenas o QUsb2Snes. O SNI não é
necessário para o FXPAK Pro. A configuração do RetroArch requer RetroArch e
SNI; o SNI fornece a conexão de memória ao vivo. No guia de botões piscantes,
o QUsb2Snes pode avançar sozinho. Se SNI ou RetroArch for selecionado, a etapa
de conexão continua ativa até que ambos sejam concluídos. Quando o RetroArch é
selecionado, o instalador azul baixa e extrai a versão portátil oficial na
pasta Tools, instala o núcleo bsnes-mercury Performance, ativa os Comandos de
Rede na porta 55355 e salva os dois caminhos. Nenhum outro assistente de
instalação do RetroArch é aberto.

Se você ignorar uma ferramenta durante a instalação, abra depois Downloads >
Configuração de conexão e emulador. O aplicativo pode localizar uma instalação
existente do SNI, QUsb2Snes ou RetroArch, ou instalá-la no seu perfil de
usuário. Ao configurar o RetroArch, ele também instala o núcleo recomendado,
ativa os Comandos de Rede na porta 55355 e salva os dois caminhos nas
configurações do tracker.
Quando uma cópia é encontrada, uma caixa de confirmação azul traduzida permite
usá-la automaticamente ou escolher um novo download.

4. CONFIGURAR O FXPAK PRO

1. Conecte a porta USB do FXPAK Pro ao PC e ligue o console.
2. Inicie o SNI ou QUsb2Snes e espere o dispositivo aparecer.
3. Abra o SMW Stream Tracker e selecione Arquivo > FXPAK Pro.
4. Clique em Atualizar se o status não mudar automaticamente.
5. Em Configurações, confira o executável do serviço e o endereço WebSocket. O
   endereço comum é ws://localhost:23074.

Se o dispositivo não aparecer, confira o cabo USB, firmware compatível, driver
do Windows e se outro programa está usando a conexão.

5. CONFIGURAR O RETROARCH

1. Instale o RetroArch ou selecione retroarch.exe em Configurações.
2. Instale Nintendo - SNES / SFC (bsnes-mercury Performance) em Atualizador Online > Baixador de
   Núcleos.
3. Abra Configurações > Rede no RetroArch.
4. Ative Comandos de Rede e mantenha a porta 55355.
5. No SMW Stream Tracker, selecione Arquivo > RetroArch.
6. Selecione retroarch.exe e bsnes_mercury_performance_libretro.dll se não forem detectados.
7. Use Jogar. Ao trocar de jogo, o tracker salva o estado, fecha o conteúdo
   atual e inicia o hack selecionado.

6. ESCOLHER PASTAS E ARQUIVOS

Abra Arquivo > Configurações e confira:

* Biblioteca de ROMs com patch.
* Pasta de saída de texto para o OBS.
* ROM-base limpa para aplicar patches moderados.
* Executável do SNI/QUsb2Snes para o FXPAK Pro.
* Executável do RetroArch e núcleo bsnes-mercury Performance.

Execute a verificação de integridade depois de alterar caminhos.

7. ATUALIZAR O CATÁLOGO

1. Abra Downloads.
2. Selecione Atualizar hacks moderados do SMW Central.
3. Aguarde; as solicitações são espaçadas para evitar limites do site.
4. Abra Ver catálogo completo para pesquisar, filtrar e ordenar.
5. Clique uma vez em Data adicionada para os mais novos e novamente para os
   mais antigos.

Use Redefinir catálogo na parte inferior para remover todas as entradas
moderadas e em espera armazenadas localmente. Primeiro é criado um backup de
recuperação. O progresso, as avaliações, as notas, os hacks personalizados, os
mapeamentos de ROM e os arquivos ROM são preservados.

Somente a célula Dificuldade usa a cor configurada para aquela dificuldade.

8. BAIXAR E CRIAR HACKS

1. Abra Downloads > Baixar hacks SMW ausentes.
2. Selecione sua ROM limpa e legal de Super Mario World.
3. Selecione a pasta da biblioteca com patches.
4. Filtre se quiser, confira a visualização e clique em Baixar hacks moderados.

A ferramenta baixa patches moderados e os aplica localmente. Ela nunca baixa
uma ROM-base e ignora jogos existentes.

9. COPIAR ROMS PARA UM CARTÃO SD

Escolha o destino SD em Configurações e ative a cópia durante o download.
Confirme a unidade com cuidado. Normalmente o FXPAK Pro não expõe o cartão SD
como unidade do Windows pela conexão USB de rastreamento; para uma cópia
permanente em massa geralmente é necessário um leitor de cartões.

10. JOGAR E ACOMPANHAR UM HACK

Digite em Pesquisar ou selecionar um hack, escolha um resultado e clique em
Jogar. Jogar hack aleatório escolhe somente hacks já baixados que podem ser
abertos na plataforma selecionada; itens que existem apenas no catálogo nunca
são escolhidos. Adicionar ao Meu Tracker cria
uma entrada e Concluir hack registra a conclusão. Clicar fora fecha a lista.

11. CRONÔMETROS, MEU TRACKER E ESTATÍSTICAS

Controle os cronômetros de jogo e fase na tela principal. Meu Tracker oferece
pesquisa, filtros, campos editáveis, cores por dificuldade, barras de nota e
progresso e exportação CSV/XLSX. As estatísticas resumem progresso, notas,
tempo, atividade e dificuldade.

12. LIVESPLIT, OBS STUDIO E STREAMLABS DESKTOP

Você pode capturar as janelas do LiveSplit, usar os arquivos de texto do
tracker ou combinar os dois métodos. Os arquivos de texto são mais simples e
não exigem o LiveSplit.

CONFIGURAÇÃO AUTOMÁTICA DE DUAS CÓPIAS (RECOMENDADA)

1. Abra Ajuda > Configuração > Configurar cronômetros LiveSplit.
2. Selecione LiveSplit de jogo (16834). O tracker baixa a versão oficial
   atual, cria uma pasta separada, configura a porta 16834 e a inicialização
   automática do servidor TCP e abre o LiveSplit.
3. Selecione LiveSplit de fase (16835). O tracker cria outra cópia, configura
   a porta 16835 e a inicialização automática TCP e abre essa cópia.
4. Quando os dois botões estiverem verdes, selecione Concluído e salve.
5. Mantenha as duas janelas abertas e não minimizadas com o tracker ou OBS.
   Cliques futuros nos botões reabrem as cópias já configuradas.

CONFIGURAÇÃO MANUAL (ALTERNATIVA)

CONECTAR O CRONÔMETRO DE JOGO DO LIVESPLIT

1. Baixe e extraia o LiveSplit de https://livesplit.org/downloads/.
2. Abra LiveSplit.exe. O servidor já está integrado; não instale o antigo
   componente LiveSplit Server separado.
3. Clique com o botão direito no LiveSplit, abra Configurações e defina Server
   Port como 16834.
4. Com apenas um cronômetro, a inicialização automática é opcional. Com duas
   janelas, inicie cada servidor manualmente depois de conferir a porta usando
   Control > Start TCP/WS Server.
5. No SMW Stream Tracker, abra Arquivo > Configurações, defina Game LiveSplit
   port como 16834, salve e teste o cronômetro de jogo.

CONECTAR UM CRONÔMETRO DE FASE SEPARADO

1. Deixe a primeira janela aberta e execute LiveSplit.exe novamente.
2. Na segunda janela, defina Server Port como 16835 e inicie o servidor TCP.
3. Deixe Level LiveSplit port como 16835 no tracker.
4. Teste iniciar, iniciar os dois e redefinir o cronômetro de fase.

As duas janelas precisam usar portas diferentes. Nas próximas execuções,
confira 16834 na primeira e 16835 na segunda antes de iniciar cada servidor. A
conexão fica local em 127.0.0.1.

MOSTRAR O LIVESPLIT NO OBS STUDIO

1. Mantenha as janelas do LiveSplit abertas e não minimizadas.
2. Em Fontes, selecione + > Captura de janela.
3. Selecione, posicione e redimensione a janela do cronômetro de jogo.
4. Adicione outra Captura de janela para o cronômetro de fase.
5. Faça uma gravação curta de teste.

MOSTRAR O LIVESPLIT NO STREAMLABS DESKTOP

1. Mantenha as janelas do LiveSplit abertas e não minimizadas.
2. Em Fontes, selecione + > Captura de tela. Se Captura de janela aparecer
   separadamente na sua versão, use essa opção.
3. Selecione, posicione e redimensione cada janela do LiveSplit.
4. Faça uma gravação curta antes de transmitir.

USAR OS ARQUIVOS DOS CRONÔMETROS NO OBS OU STREAMLABS

1. Escolha uma pasta de saída OBS em Arquivo > Configurações e salve.
2. Selecione ou inicie um hack e opere cada cronômetro uma vez.
3. Abra a pasta com Arquivo > Abrir pasta de texto OBS.
4. No OBS ou Streamlabs, adicione uma fonte Texto (GDI+).
5. Ative Ler do arquivo e escolha game_timer.txt.
6. Adicione outra fonte Texto e escolha level_timer.txt.
7. Configure fonte, cor, contorno, alinhamento e tamanho.
8. Repita, se desejar, para hack_name.txt, author.txt, exits.txt, level_deaths.txt ou total_deaths.txt.

Mortes no nível mantém as tentativas e zera quando outro nível começa. Mortes
totais é salvo separadamente para cada ROM e arquivo Mario A, B ou C. Altere os
dois textos em Arquivo > Configurações do OBS. death_counter.txt continua como
espelho de level_deaths.txt para cenas existentes.

O SMW Stream Tracker precisa ficar aberto para atualizar os arquivos. Se uma
fonte estiver vazia ou desatualizada, confira a pasta e opere o cronômetro
novamente.

Ajuda oficial:
Servidor LiveSplit: https://github.com/LiveSplit/LiveSplit#the-livesplit-server
Texto no OBS: https://obsproject.com/kb/text-sources
Captura no Streamlabs: https://streamlabs.com/content-hub/post/how-to-capture-your-screen-in-streamlabs-desktop

13. ATUALIZAÇÕES, BACKUP E REVERSÃO

Use SMWStreamTracker_Update_VERSION.exe para versões pequenas depois de uma
instalação completa. O atualizador preserva o executável anterior para reversão.
Faça backup do banco de dados, configuração e biblioteca antes de mudanças
importantes no Windows ou armazenamento.

14. SOLUÇÃO DE PROBLEMAS E PRIVACIDADE

* FXPAK desconectado: confira SNI/QUsb2Snes, USB, firmware e porta 23074.
* Hack atual para de detectar jogos depois de uma atualização pelo aplicativo:
  abra Downloads > Configuração de conexão e emulador > Instalar ou encontrar
  SNI (altamente recomendado). Deixe o tracker encontrar ou reinstalar o SNI,
  reinicie o SNI e selecione Atualizar.
* RetroArch não acompanha: ative Comandos de Rede na porta 55355.
* Jogo não inicia: confira ROM, executável, núcleo e caminhos.
* Catálogo lento: deixe as novas tentativas espaçadas terminarem.

Os dados e caminhos do tracker são processados localmente. Catálogo,
dependências, atualizações e sincronização só se conectam quando usados. Leia
PRIVACY.txt e THIRD_PARTY_NOTICE.txt para os avisos completos.
