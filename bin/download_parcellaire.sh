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

CVI="$cvi" PRODOUANE_USER="$PRODOUANE_USER" PRODOUANE_PASS="$PRODOUANE_PASS" node puppeteer_scrapping/prodouane_parcellaire.js

if test -f "./documents/parcellaire-${cvi}-parcellaire.html"; then
	sed -i '/^<?xml /id' "./documents/parcellaire-${cvi}-accueil.html"
	sed -i '/^<?xml /id' "./documents/parcellaire-${cvi}-parcellaire.html"
	python3 posttraitement/parcellaire_html_to_csv.py "$cvi" 2>&1
fi

if ! test -f "documents/parcellaire-${cvi}.csv" && test -f "$INAO_FILE"; then
	echo -n "Origine;CVI Operateur;Siret Operateur;Nom Operateur;Adresse Operateur;CP Operateur;Commune Operateur;Email Operateur;IDU;Commune;Lieu dit;Section;" > "documents/parcellaire-${cvi}.csv"
	echo "Numero parcelle;Produit;Cepage;Superficie;Superficie cadastrale;Campagne;Ecart pied;Ecart rang;Mode savoir faire;Statut;Date MaJ" >> "documents/parcellaire-${cvi}.csv"
	grep "$cvi" $INAO_FILE | awk -F ';' '{idu=substr($4,1,2)substr($4,4,12); gsub(" ", "0", idu); print "INAO";$17";"$19";"$18";;;;;"idu";"$9";"$10";"$1";"$2";"$26" - "$25";"$28";"$36";"$5";"$35";"$37";"$38";"$33";;"$39}' >> "documents/parcellaire-${cvi}.csv"
fi

#Code transitoire
if ! test -f "$INAO_FILE" && test -f "documents/parcellaire-${cvi}.csv" ; then
	sed -i 's/^[^;]*;//' "documents/parcellaire-${cvi}.csv"
fi

if ! test -f "documents/parcellaire-${cvi}.csv"; then
	echo "Échec du scraping"
	exit 4
fi
