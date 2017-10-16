# Export des documents du portail prodouane

## Dépendance

    python-scrapy catdoc

## Lancer le téléchargement des documents

Les paramètres lié au compte utilisé et à la campagne viticole sont à passer en variable d'environnement.

Ainsi pour télécharger les DR mise à dispoition du compte `login` (dont le mot de passe est `pass`) pour la campagne `2016-2017`, il faut lancer la ligne de commande suivante :

    PRODOUANE_CAMPAGNE=2016-2017 PRODOUANE_USER='login' PRODOUANE_PASS='pass' scrapy crawl dr

Il est possible de remplacer `dr` par `sv11` ou `sv12` pour télécharger respectivement les SV11 et SV12.

Les documents au format html et xls sont mis à dispoition dans le répertoire `documents/`

Une commande générique permet de télécharger l'un des trois types de documents pour un CVI et une campagne données :

    bash bin/download_douane.sh dr 2014-2015 UN_CVI

Les identifiants et mot de passe doivent avant été indiqué dans le fichier `bin/config.inc`.

## Formatage des xls en csv

La conversion de xls en csv se fait à l'aide de xls2csv disponible dans le paquet debian catdoc

### DR

Pour formater les xls des déclarations en csv exploitable

    bash posttraitement/dr_xls2csv.sh chemin_vers_le_fichier_xls campagne
