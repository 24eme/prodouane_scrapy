# Export des documents du portail prodouane

## Dépendances

    python-scrapy catdoc
    beautifulsoup lxml # pour les parcellaires
    python-wget # pour télécharger les geojson depuis cadastre

## Lancer le téléchargement des documents

Les paramètres lié au compte utilisé et à la campagne viticole sont à passer en variable d'environnement.

Ainsi pour télécharger les DR mise à disposition du compte `login` (dont le mot de passe est `pass`) pour l'année `2016`, il faut lancer la ligne de commande suivante :

    PRODOUANE_ANNEE=2016 PRODOUANE_USER='login' PRODOUANE_PASS='pass' scrapy crawl dr

Il est possible de remplacer `dr` par `sv11`, `sv12` ou `parcellaire` pour télécharger respectivement les SV11, SV12 et Parcellaires.

Les documents au format pdf, html et xls sont mis à disposition dans le répertoire `documents/`

Une commande générique permet de télécharger l'un des trois types de documents pour un CVI et une année donnée :

    bash bin/download_douane.sh DOCUMENT ANNÉE CVI

Soit pour la dr de 2015 du CVI 1234512345 :

    bash bin/download_douane.sh dr 2015 1234512345

Les identifiants et mot de passe doivent avant été indiqué dans le fichier `bin/config.inc`.

Pour télécharger les parcellaires, le script est :

    bash bin/download_parcellaire.sh

## Formatage des xls en csv

La conversion de xls en csv se fait à l'aide de xls2csv disponible dans le paquet debian catdoc

### DR

Pour formater les xls des déclarations en csv exploitable

    bash posttraitement/dr_xls2csv.sh chemin_vers_le_fichier_xls campagne

### Parcellaire

Pour formater le HTML en csv il faut lancer le script

    python posttraitement/parcellaire_to_csv.py <numero_cvi>

## GeoJson cadastre

Pour télécharger les geojson des parcellaire dépuis le site web https://cadastre.data.gouv.fr/

!! vérifier le droit d'accès www sur le fichier bin/download_parcellaire_geojson.sh

	sh bin/download_parcellaire_geojson.sh cvi?

## Délimitation du parcellaire

Pour télécharger la délimitation parcellaire des AOC (https://www.data.gouv.fr/fr/datasets/ ) puis les parse par commune, il existe un script pour le faire.

Il faut avant tout indiquer l'identifiant de l'appellation dans le ficheir `bin/config.inc` via la variable de configuration `APP_ID`.

La liste des appellations est disponible dans le fichier [inao_id_app.csv](inao_id_app.csv).

Puis il faut executer le script suivant :
	
	bash bin/get_delimination_aoc.sh

!! si ne fonctionne pas vérifier l'url du téléchargement qui peut avoir changé sur data.gouv.fr
