#!/bin/bash

. "$(dirname "$0")/common.inc"

if test "$PRODOUANE_DOUANE"; then
	mkdir -p debug
fi

if ! test "$PRODOUANE_USER" || ! test "$PRODOUANE_PASS" ; then
	echo "Authentification non configurée dans le config.inc"
	exit 1;
fi

type=$1
annee=$2
cvi=$3

if ! test "$cvi" ; then
	echo "3 arguments attendus : [dr|sv1|sv2] <campagne> <cvi>"
	exit 2;
fi

if test "$type" = "dr" ; then
  rm ./documents/dr-"$annee"*"$cvi"*
  PRODOUANE_USER="$PRODOUANE_USER" PRODOUANE_PASS="$PRODOUANE_PASS" CVI="$cvi" PRODOUANE_ANNEE="$annee" scrapy crawl "$type"
elif test "$type" = "sv11" && test $annee -lt 2022 ; then
  PRODOUANE_USER="$PRODOUANE_USER" PRODOUANE_PASS="$PRODOUANE_PASS" CVI="$cvi" PRODOUANE_ANNEE="$annee" scrapy crawl "$type"
elif test "$type" = "sv12" && test $annee -lt 2022 ; then
  PRODOUANE_USER="$PRODOUANE_USER" PRODOUANE_PASS="$PRODOUANE_PASS" CVI="$cvi" PRODOUANE_ANNEE="$annee" scrapy crawl "$type"
else
  PRODOUANE_USER="$PRODOUANE_USER" PRODOUANE_PASS="$PRODOUANE_PASS" CVI="$cvi" PRODOUANE_ANNEE="$annee" node puppeteer_scrapping/prodouane_vendanges.js
fi
