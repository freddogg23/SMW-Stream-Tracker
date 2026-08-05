SMW STREAM TRACKER - GUIDE COMPLET DE CONFIGURATION
Version 1.1.2

LANGUES
English : README.en.txt
Australian : README.au.txt
Español : README.es.txt
Français : README.fr.txt
Deutsch : README.de.txt
Português (Brasil) : README.pt-BR.txt

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

1. Lancez SMWStreamTracker_Setup_1.1.2.exe.
2. Choisissez une langue sur le premier écran.
3. Lisez l'avis sur les logiciels facultatifs et les ROMs.
4. Choisissez FXPAK Pro ou RetroArch comme plateforme initiale.
5. Cochez les outils facultatifs à installer.
6. Choisissez les dossiers des ROMs et de sortie OBS, ou laissez-les vides pour
   les configurer ultérieurement.
7. Terminez l'installation et ouvrez ce guide.

Les réglages existants sont conservés pendant l'installation et les mises à jour.

3. CHOISIR LES LOGICIELS FACULTATIFS

SNI est vivement recommandé pour la connexion en direct. QUsb2Snes est une
passerelle facultative, avancée et ancienne, surtout destinée aux utilisateurs
de FXPAK Pro et SD2SNES. RetroArch est facultatif : ignorez-le s'il est déjà
installé ou si vous utilisez uniquement FXPAK Pro. Si vous le sélectionnez,
l'assistant télécharge également le cœur bsnes-mercury Performance Libretro.

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
résultat et cliquez sur Jouer. Le jeu aléatoire choisit dans la bibliothèque.
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
8. Répétez si besoin avec hack_name.txt, author.txt ou exits.txt.

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
* RetroArch ne suit pas : activez les commandes réseau sur le port 55355.
* Le jeu ne démarre pas : vérifiez ROM, exécutable, cœur et chemins.
* Catalogue lent : laissez les nouvelles tentatives espacées se terminer.

Les chemins et données du tracker sont traités localement. Les fonctions de
catalogue, dépendances, mise à jour et synchronisation se connectent uniquement
lorsqu'elles sont utilisées. Consultez PRIVACY.txt et THIRD_PARTY_NOTICE.txt.
