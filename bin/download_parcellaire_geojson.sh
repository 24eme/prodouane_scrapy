#!/bin/bash

if ! type scrapy > /dev/null 2>&1; then
	echo "Le binaire scrapy n'existe pas"
	exit 1
fi

if [ $# -ne 1 ]; then
	echo "Il manque un paramètre"
	exit 2
fi

cvi=$1


. $(dirname $0)/config.inc
cd $(dirname $0)/../ > /dev/null 2>&1

if ! test "$PRODOUANE_USER" || ! test "$PRODOUANE_PASS"; then
	echo "Authentification mal configurée dans le fichier de config"
	exit 3
fi

CVI="$cvi" PRODOUANE_USER="$PRODOUANE_USER" PRODOUANE_PASS="$PRODOUANE_PASS" scrapy crawl parcellaire

if [ ! -f "./documents/parcellaire-${cvi}.csv" ]; then
	echo "Échec du scraping"
	exit 1
fi

python posttraitement/parcellaire_csv_to_geojson.py $cvi
