#!/bin/bash

. "$(dirname "$0")/common.inc"

if test "$PRODOUANE_DOUANE"; then
	mkdir -p debug
fi

if ! test "$PRODOUANE_USER" || ! test "$PRODOUANE_PASS" ; then
	echo "Authentification non configurée dans le config.inc"
	exit 1;
fi

cvi=$1

if ! test "$cvi" ; then
	echo "1 argument attendu : <cvi>"
	exit 2;
fi

PRODOUANE_USER="$PRODOUANE_USER" PRODOUANE_PASS="$PRODOUANE_PASS" CVI="$cvi" PRODOUANE_OVNI="$PRODOUANE_OVNI" node puppeteer_scrapping/prodouane_cvi.js
