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

PRODOUANE_USER="$PRODOUANE_USER" PRODOUANE_PASS="$PRODOUANE_PASS" node puppeteer_scrapping/scriptGetHTMLSAndPDFByCVI.js > $tmpfile

cat $tmpfile | while read cvi; do
	CVI="$cvi" PRODOUANE_USER="$PRODOUANE_USER" PRODOUANE_PASS="$PRODOUANE_PASS" node puppeteer_scrapping/scriptGetHTMLSAndPDFByCVI.js
done
	
rm $tmpfile
