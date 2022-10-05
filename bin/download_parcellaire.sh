#!/bin/bash

. "$(dirname "$0")"/common.inc

if ! type scrapy > /dev/null 2>&1; then
	echo "Le binaire scrapy n'existe pas"
	exit 1
fi

if [ $# -ne 1 ]; then
	echo "Il manque un paramètre : CVI attendu"
	exit 2
fi

cvi=$1

if ! test "$PRODOUANE_USER" || ! test "$PRODOUANE_PASS"; then
	echo "Authentification mal configurée dans le fichier de config"
	exit 3
fi

CVI="$cvi" PRODOUANE_USER="$PRODOUANE_USER" PRODOUANE_PASS="$PRODOUANE_PASS" node puppeteer_scrapping/scriptGetHTMLSAndPDFByCVI.js

if [ ! -f "./documents/parcellaire-${cvi}-parcellaire.html" ]; then
	echo "Échec du scraping"
	exit 4
fi

sed -i '/^<?xml /id' "./documents/parcellaire-${cvi}-accueil.html"
sed -i '/^<?xml /id' "./documents/parcellaire-${cvi}-parcellaire.html"

python3 posttraitement/parcellaire_to_csv.py "$cvi" 2>&1
