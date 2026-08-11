SMW STREAM TRACKER - GUIDE COMPLET DE CONFIGURATION
Version 1.0.11

LANGUES
English : README.en.txt
Australian : README.au.txt
Español : README.es.txt
Français : README.fr.txt
Deutsch : README.de.txt
Português (Brasil) : README.pt-BR.txt

PRISE EN CHARGE DE MACOS

SMW Stream Tracker utilise désormais les chemins natifs de Mac et propose des
compilations pour Apple Silicon (arm64) et Intel (x86_64). Téléchargez le DMG
correspondant et faites glisser l’application dans Applications. Les données du
tracker sont conservées dans :
~/Library/Application Support/SMWStreamTracker

La configuration de la connexion et de l’émulateur télécharge les versions Mac
officielles de SNI, QUsb2Snes et RetroArch, avec le bon cœur bsnes-mercury.
LiveSplit classique est réservé à Windows ; l’application Mac fournit donc des
fenêtres synchronisées pour les chronomètres de partie et de niveau, ainsi que
game_timer.txt et level_timer.txt pour OBS. Le catalogue, les correctifs, les
alias emoji FXPAK, la base de données, les classeurs et les textes OBS gardent
le même fonctionnement sous Windows et Mac.

NOUVEAUTÉS DE LA VERSION 1.0.11

* Le fonctionnement natif sous Windows et macOS comprend des versions
  reproductibles pour Apple Silicon et Intel ainsi que la configuration SNI,
  QUsb2Snes et RetroArch adaptée à chaque plateforme.
* Le déplacement de la fenêtre et le défilement de Mon Tracker sont plus
  fluides ; la bannière est mise en cache, les bordures des tableaux restent
  alignées et une fenêtre principale réduite peut défiler jusqu’en bas.
* Un formulaire bleu et traduit Ajouter au tracker accepte tous les détails du
  hack et de la progression. Les hacks personnalisés non modérés restent avec
  le catalogue et peuvent être patchés puis envoyés vers le FXPAK Pro.
* Actualiser peut réinitialiser en toute sécurité une session FXPAK Pro active
  avant la reconnexion, et Retirer de Mon Tracker utilise la boîte bleue.
* Un nouveau guide de premier démarrage fait clignoter dans l’ordre chaque
  étape requise : téléchargements, connexion, catalogue, actualisation,
  application des correctifs, FXPAK et OBS.
* Après avoir choisi SNI ou RetroArch, QUsb2Snes et l’option choisie cessent de
  clignoter ; seule l’autre option SNI/RetroArch requise reste mise en évidence.
* Le catalogue SMW Central et le téléchargeur utilisent des flèches bleues,
  des barres de défilement jaunes, des champs de type plus larges et des
  bordures de cellule bleu clair.
* Les transferts vers FXPAK Pro remplacent chaque emoji par son nom Unicode
  lisible dans le fichier ROM, y compris pour les futurs hacks. Le catalogue,
  le tracker et l’affichage du jeu conservent le titre original, et le mappage
  enregistré rappelle la ROM renommée lorsqu’elle est sélectionnée.
* Lorsque l’envoi USB est activé, les ROM locales existantes dont le titre
  contient des emojis sont aussi transférées et associées automatiquement. Les
  anciens téléchargements sont ainsi corrigés sans nouveau patch ni téléchargement.
* Au lancement d’un hack avec emojis, le tracker retrouve son alias lisible sur
  le FXPAK ou l’envoie automatiquement s’il manque. Le lien permanent utilise
  l’identifiant SMW Central afin de toujours rétablir et afficher le titre original.
* Pendant un transfert FXPAK, la connexion active du tracker à SNI/QUsb2Snes
  est suspendue puis rétablie automatiquement, afin qu’elle ne puisse pas
  bloquer l’envoi avec le nom sécurisé sans emoji.
* La page OBS explique comment réutiliser les sources de texte existantes. Deux
  boutons téléchargent et configurent des copies LiveSplit distinctes pour la
  partie et le niveau sur les ports 16834 et 16835.
* Les statistiques adoptent la nouvelle disposition à deux colonnes, des
  graphiques plus grands et un tableau compact de progression par difficulté.
* Tous les messages, menus, commandes, états, sélecteurs et écrans de
  configuration sont traduits dans toutes les langues disponibles.
* À propos et mises à jour contient un bouton Rejoindre Discord pour obtenir de
  l’aide ou contacter FredDOGG23 : https://discord.gg/fHkTRgqjcr

TABLE DES MATIÈRES
1. Prérequis
2. Installer le programme
3. Choisir les logiciels facultatifs
4. Configurer FXPAK Pro
5. Configurer RetroArch
6. Choisir les dossiers et fichiers
7. Actualiser le catalogue
8. Télécharger et créer des hacks
9. Copier les ROMs sur une carte SD
10. Jouer et suivre un hack
11. Minuteurs, Mon Tracker et statistiques
12. LiveSplit, OBS Studio et Streamlabs Desktop
13. Mises à jour, sauvegarde et restauration
14. Dépannage et confidentialité

1. PRÉREQUIS

* Un PC 64 bits sous Windows 10 ou Windows 11.
* Un dossier destiné aux ROMs corrigées.
* Internet pour le catalogue et les téléchargements facultatifs.
* Un FXPAK Pro/SD2SNES ou RetroArch sous Windows.
* Votre propre ROM propre de Super Mario World obtenue légalement pour créer
  des ROMs jouables à partir de correctifs modérés.

SMW Stream Tracker n'inclut et ne télécharge aucune ROM commerciale de base.

2. INSTALLER LE PROGRAMME

1. Lancez SMWStreamTracker_Setup_1.0.11.exe.
2. Choisissez une langue sur le premier écran.
3. Lisez l'avis sur les logiciels facultatifs et les ROMs.
4. Choisissez FXPAK Pro ou RetroArch comme plateforme initiale.
5. Cochez les outils facultatifs à installer.
6. Choisissez les dossiers des ROMs et de sortie OBS, ou laissez-les vides pour
   les configurer ultérieurement.
7. Terminez l'installation et ouvrez ce guide.

Les réglages existants sont conservés pendant l'installation et les mises à jour.
Une désinstallation complète supprime les réglages et données du tracker, les
copies LiveSplit et les fichiers texte OBS créés par le tracker. Elle conserve
RetroArch, SNI, QUsb2Snes ainsi que tous les fichiers et dossiers de ROM. Une
installation propre ultérieure affiche de nouveau l'écran d'accueil configuré.
Une seule copie peut être installée pour le compte Windows actuel. Si vous
relancez l'installateur complet, il propose de supprimer la copie actuelle et
de poursuivre avec une installation propre, ou de désinstaller complètement le
tracker et de quitter. Les deux choix conservent RetroArch, SNI, QUsb2Snes et les ROM.
Vous pouvez changer la langue à tout moment dans Fichier > Langue. L’interface
principale se reconstruit immédiatement sans conserver de texte de l’ancienne
langue.

3. CHOISIR LES LOGICIELS FACULTATIFS

La configuration FXPAK Pro ou SD2SNES nécessite uniquement QUsb2Snes. SNI
n'est pas requis pour FXPAK Pro. La configuration RetroArch nécessite à la
fois RetroArch et SNI ; SNI fournit la connexion mémoire en direct. Dans le
guide aux boutons clignotants, QUsb2Snes peut avancer seul. Si SNI ou RetroArch
est sélectionné, l'étape de connexion reste active jusqu'à ce que les deux
soient terminés. Si vous
sélectionnez RetroArch, l'installateur bleu télécharge et extrait la version
portable officielle dans son dossier Tools, installe le cœur bsnes-mercury
Performance, active les commandes réseau sur le port 55355 et mémorise les
deux chemins. Aucun autre assistant d'installation RetroArch ne s'ouvre.

Si vous ignorez un outil pendant l'installation, ouvrez plus tard
Téléchargements > Configuration de la connexion et de l’émulateur. L’application
peut retrouver une installation existante de SNI, QUsb2Snes ou RetroArch, ou
l’installer dans votre profil utilisateur. Pour RetroArch, elle installe aussi
le cœur recommandé, active les commandes réseau sur le port 55355 et mémorise
les deux chemins dans les paramètres du tracker.
Lorsqu'une copie est trouvée, une boîte de confirmation bleue traduite permet
de l'utiliser automatiquement ou de choisir un nouveau téléchargement.

4. CONFIGURER FXPAK PRO

1. Branchez le port USB du FXPAK Pro au PC et allumez la console.
2. Lancez SNI ou QUsb2Snes et attendez que l'appareil apparaisse.
3. Ouvrez SMW Stream Tracker et choisissez Fichier > FXPAK Pro.
4. Cliquez sur Actualiser si l'état ne change pas automatiquement.
5. Dans Paramètres, vérifiez l'exécutable du service et l'adresse WebSocket.
   L'adresse habituelle est ws://localhost:23074.

Si l'appareil manque, vérifiez le câble USB, le micrologiciel compatible, le
pilote Windows et qu'aucune autre application n'utilise la connexion.

5. CONFIGURER RETROARCH

1. Installez RetroArch ou sélectionnez retroarch.exe dans Paramètres.
2. Installez Nintendo - SNES / SFC (bsnes-mercury Performance) depuis Mise à jour en ligne >
   Téléchargeur de cœurs.
3. Ouvrez Paramètres > Réseau dans RetroArch.
4. Activez les commandes réseau et conservez le port 55355.
5. Dans SMW Stream Tracker, choisissez Fichier > RetroArch.
6. Sélectionnez retroarch.exe et bsnes_mercury_performance_libretro.dll s'ils ne sont pas détectés.
7. Utilisez Jouer. Lors d'un changement, le tracker sauvegarde l'état, ferme le
   contenu actuel et lance le hack choisi.

6. CHOISIR LES DOSSIERS ET FICHIERS

Ouvrez Fichier > Paramètres et vérifiez :

* Bibliothèque de ROMs corrigées.
* Dossier de sortie texte OBS.
* ROM propre de base pour appliquer les correctifs modérés.
* Exécutable SNI/QUsb2Snes pour FXPAK Pro.
* Exécutable RetroArch et cœur bsnes-mercury Performance.

Exécutez le contrôle d'intégrité après toute modification de chemin.

7. ACTUALISER LE CATALOGUE

1. Ouvrez Téléchargements.
2. Choisissez Actualiser les hacks modérés depuis SMW Central.
3. Attendez la fin; les requêtes sont espacées pour éviter les limitations.
4. Ouvrez Afficher le catalogue complet pour rechercher, filtrer et trier.
5. Cliquez une fois sur Date d'ajout pour le plus récent, puis une seconde fois
   pour le plus ancien.

Utilisez Réinitialiser le catalogue en bas de la page pour supprimer toutes les
entrées modérées et en attente enregistrées localement. Une sauvegarde de
récupération est d'abord créée. La progression, les notes, les commentaires,
les hacks personnalisés, les associations de ROM et les fichiers ROM sont
conservés.

Seule la cellule Difficulté utilise la couleur définie pour cette difficulté.

8. TÉLÉCHARGER ET CRÉER DES HACKS

1. Ouvrez Téléchargements > Télécharger les hacks SMW manquants.
2. Sélectionnez votre ROM propre et légale de Super Mario World.
3. Sélectionnez la bibliothèque de ROMs corrigées.
4. Filtrez si nécessaire, vérifiez l'aperçu, puis cliquez sur Télécharger les
   hacks modérés.

L'outil télécharge des correctifs modérés et les applique localement. Il ne
télécharge jamais de ROM de base et ignore les jeux déjà présents.

9. COPIER LES ROMS SUR UNE CARTE SD

Choisissez la destination SD dans Paramètres et activez la copie pendant le
téléchargement. Vérifiez soigneusement le lecteur. Le FXPAK Pro n'expose
généralement pas sa carte SD comme lecteur Windows via son USB de suivi; un
lecteur de cartes reste normalement nécessaire pour une copie permanente.

10. JOUER ET SUIVRE UN HACK

Saisissez du texte dans Rechercher ou sélectionner un hack, choisissez un
résultat et cliquez sur Jouer. Le jeu aléatoire choisit uniquement parmi les
hacks déjà téléchargés et utilisables avec la plateforme sélectionnée ; les
entrées présentes uniquement dans le catalogue sont exclues.
Ajouter à Mon Tracker crée une entrée et Terminer le hack enregistre la fin.
Un clic à l'extérieur ferme la liste.

11. MINUTEURS, MON TRACKER ET STATISTIQUES

Contrôlez les minuteurs de jeu et de niveau depuis l'écran principal. Mon
Tracker offre recherche, filtres, champs modifiables, couleurs de difficulté,
barres de note/progression et export CSV/XLSX. Les statistiques résument la
progression, les notes, le temps, l'activité et les difficultés.

12. LIVESPLIT, OBS STUDIO ET STREAMLABS DESKTOP

Vous pouvez capturer les fenêtres LiveSplit, utiliser les fichiers texte du
tracker, ou combiner les deux. Les fichiers texte sont la méthode la plus
simple et ne nécessitent pas LiveSplit.

CONFIGURATION AUTOMATIQUE DE DEUX COPIES (RECOMMANDÉE)

1. Ouvrez Aide > Configuration > Configurer les chronomètres LiveSplit.
2. Choisissez LiveSplit jeu (16834). Le tracker télécharge la version
   officielle actuelle, crée un dossier séparé, configure le port 16834 et le
   démarrage automatique du serveur TCP, puis ouvre LiveSplit.
3. Choisissez LiveSplit niveau (16835). Le tracker crée une seconde copie,
   configure le port 16835 et le démarrage automatique TCP, puis l'ouvre.
4. Quand les deux boutons sont verts, choisissez Terminé et enregistrez.
5. Gardez les deux fenêtres ouvertes et non réduites avec le tracker ou OBS.
   Les boutons rouvriront ensuite les copies déjà configurées.

CONFIGURATION MANUELLE (SOLUTION DE REPLI)

CONNECTER LE MINUTEUR DE JEU LIVESPLIT

1. Téléchargez et extrayez LiveSplit depuis https://livesplit.org/downloads/.
2. Ouvrez LiveSplit.exe. Le serveur est intégré; n'installez pas l'ancien
   composant LiveSplit Server séparé.
3. Faites un clic droit sur LiveSplit, ouvrez Paramètres et réglez Server Port
   sur 16834.
4. Pour un seul minuteur, le démarrage automatique est facultatif. Avec deux
   fenêtres, démarrez chaque serveur manuellement après avoir vérifié son port
   avec Control > Start TCP/WS Server.
5. Dans SMW Stream Tracker, ouvrez Fichier > Paramètres, réglez Game LiveSplit
   port sur 16834, enregistrez et testez le minuteur de jeu.

CONNECTER UN MINUTEUR DE NIVEAU SÉPARÉ

1. Laissez la première fenêtre ouverte et relancez LiveSplit.exe.
2. Dans la seconde fenêtre, réglez Server Port sur 16835 et démarrez le
   serveur TCP.
3. Laissez Level LiveSplit port sur 16835 dans le tracker.
4. Testez le démarrage, le contrôle simultané et la remise à zéro du
   minuteur de niveau.

Les deux fenêtres doivent utiliser des ports différents. Aux lancements
suivants, vérifiez 16834 dans la première et 16835 dans la seconde avant de
démarrer les serveurs. La connexion reste locale sur 127.0.0.1.

AFFICHER LIVESPLIT DANS OBS STUDIO

1. Gardez les fenêtres LiveSplit ouvertes et non réduites.
2. Dans Sources, choisissez + > Capture de fenêtre.
3. Sélectionnez, placez et redimensionnez le minuteur de jeu.
4. Ajoutez une seconde Capture de fenêtre pour le minuteur de niveau.
5. Effectuez un court enregistrement de test.

AFFICHER LIVESPLIT DANS STREAMLABS DESKTOP

1. Gardez les fenêtres LiveSplit ouvertes et non réduites.
2. Dans Sources, choisissez + > Capture d'écran; si Capture de fenêtre est
   proposée séparément, choisissez-la.
3. Sélectionnez, placez et redimensionnez chaque fenêtre LiveSplit.
4. Effectuez un court enregistrement avant la diffusion.

UTILISER LES FICHIERS DES MINUTEURS DANS OBS OU STREAMLABS

1. Choisissez un dossier de sortie OBS dans Fichier > Paramètres et enregistrez.
2. Sélectionnez ou lancez un hack et utilisez chaque minuteur une fois.
3. Ouvrez le dossier avec Fichier > Ouvrir le dossier texte OBS.
4. Dans OBS ou Streamlabs, ajoutez une source Texte (GDI+).
5. Activez Lire depuis un fichier et choisissez game_timer.txt.
6. Ajoutez une autre source Texte et choisissez level_timer.txt.
7. Réglez police, couleur, contour, alignement et taille.
8. Répétez si besoin avec hack_name.txt, author.txt, exits.txt, level_deaths.txt ou total_deaths.txt.

Morts du niveau conserve les tentatives et se réinitialise au début d'un autre
niveau. Total des morts est enregistré séparément pour chaque ROM et sauvegarde
Mario A, B ou C. Modifiez les deux libellés dans Fichier > Paramètres OBS.
death_counter.txt reste un miroir de level_deaths.txt pour les scènes existantes.

SMW Stream Tracker doit rester ouvert pour actualiser les fichiers. Si une
source est vide ou ancienne, vérifiez le dossier et actionnez à nouveau le
minuteur.

Aide officielle :
Serveur LiveSplit : https://github.com/LiveSplit/LiveSplit#the-livesplit-server
Texte OBS : https://obsproject.com/kb/text-sources
Capture Streamlabs : https://streamlabs.com/content-hub/post/how-to-capture-your-screen-in-streamlabs-desktop

13. MISES À JOUR, SAUVEGARDE ET RESTAURATION

Utilisez SMWStreamTracker_Update_VERSION.exe pour les petites versions après
une installation complète. Le programme conserve l'exécutable précédent pour
une restauration. Sauvegardez la base, la configuration et la bibliothèque
avant toute modification importante du système ou du stockage.

14. DÉPANNAGE ET CONFIDENTIALITÉ

* FXPAK déconnecté : vérifiez SNI/QUsb2Snes, USB, firmware et le port 23074.
* Hack actuel ne détecte plus les jeux après une mise à jour dans
  l’application : ouvrez Téléchargements > Configuration de la connexion et
  de l’émulateur > Installer ou trouver SNI (fortement recommandé). Laissez le
  tracker trouver ou réinstaller SNI, redémarrez SNI, puis choisissez Actualiser.
* RetroArch ne suit pas : activez les commandes réseau sur le port 55355.
* Le jeu ne démarre pas : vérifiez ROM, exécutable, cœur et chemins.
* Catalogue lent : laissez les nouvelles tentatives espacées se terminer.

Les chemins et données du tracker sont traités localement. Les fonctions de
catalogue, dépendances, mise à jour et synchronisation se connectent uniquement
lorsqu'elles sont utilisées. Consultez PRIVACY.txt et THIRD_PARTY_NOTICE.txt.
