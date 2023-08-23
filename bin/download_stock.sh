#!/bin/bash

. "$(dirname "$0")/common.inc"

if test "$PRODOUANE_DOUANE"; then
	mkdir -p debug
fi

if ! test "$PRODOUANE_USER" || ! test "$PRODOUANE_PASS" ; then
	echo "Authentification non configurée dans le config.inc"
	exit 1;
fi

annee=$1
cvi=$2

if ! test "$annee" ; then
	echo "1 arguments attendus : <annee>"
	exit 2;
fi

if ! test "$cvi" ; then
	echo "listes des CVI"
	PRODOUANE_USER="$PRODOUANE_USER" PRODOUANE_PASS="$PRODOUANE_PASS" PRODOUANE_ANNEE="$annee" node puppeteer_scrapping/prodouane_stock.js
else
	PRODOUANE_USER="$PRODOUANE_USER" PRODOUANE_PASS="$PRODOUANE_PASS" CVI="$cvi" PRODOUANE_ANNEE="$annee" node puppeteer_scrapping/prodouane_stock.js
fi