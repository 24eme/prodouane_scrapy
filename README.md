# Export des documents du portail prodouane

## Dépendance 

    python-scrapy

## Lancer le téléchargement des documents

Les paramètres lié au compte utilisé et à la campagne viticole sont à passer en variable d'environnement.

Ainsi pour télécharger les DR mise à dispoition du compte `login` (dont le mot de passe est `pass`) pour la campagne `2016-2017`, il faut lancer la ligne de commande suivante :

    PRODOUANE_CAMPAGNE=2016-2017 PRODOUANE_USER='login' PRODOUANE_PASS='pass' scrapy crawl dr

Il est possible de remplacer `dr` par `sv11` ou `sv12` pour télécharger respectivement les SV11 et SV12.

Les documents au format html et xls sont mis à dispoition dans le répertoire `documents/`
