#!/bin/bash

. $(dirname $0)/common.inc

if ! type scrapy > /dev/null 2>&1; then
	echo "Le binaire scrapy n'existe pas"
	exit 1
fi

if ! test "$PRODOUANE_USER" || ! test "$PRODOUANE_PASS"; then
	echo "Authentification mal configurée dans le fichier de config"
	exit 1
fi

tmpfile=$(mktemp /tmp/$(basename $0).XXXXXX)

PRODOUANE_USER="$PRODOUANE_USER" PRODOUANE_PASS="$PRODOUANE_PASS" node puppeteer_scrapping/prodouane_parcellaire.js > $tmpfile

cat $tmpfile | while read cvi; do
	echo "Téléchargement CVI $cvi"
	CVI="$cvi" PRODOUANE_USER="$PRODOUANE_USER" PRODOUANE_PASS="$PRODOUANE_PASS" node puppeteer_scrapping/prodouane_parcellaire.js

	if test -f "./documents/parcellaire-${cvi}-parcellaire.html"; then
		sed -i '/^<?xml /id' "./documents/parcellaire-${cvi}-accueil.html"
		sed -i '/^<?xml /id' "./documents/parcellaire-${cvi}-parcellaire.html"
		python3 posttraitement/parcellaire_html_to_csv.py "$cvi" 2>&1
		python3 posttraitement/parcellaire_csv_to_geojson.py "$cvi" 2>&1
	fi
done

rm $tmpfile
