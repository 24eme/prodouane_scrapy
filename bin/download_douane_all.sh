#!/bin/bash

. $(dirname $0)/common.inc

if ! test "$PRODOUANE_USER" || ! test "$PRODOUANE_PASS" ; then
        echo "Authentification non configurée dans le config.inc"
        exit 1;
fi

annee=$1
types=$2

if ! test "$annee" ; then
	annee=$(date '+%Y')
fi
if ! test "$types" ; then
types="dr sv11 sv12";
fi


PRODOUANE_USER="$PRODOUANE_USER" PRODOUANE_PASS="$PRODOUANE_PASS" PRODOUANE_ANNEE="$annee" node puppeteer_scrapping/prodouane_listcvi.js > /tmp/$$.cvi.tmp

for type in $(echo $types) ; do
cat /tmp/$$.cvi.tmp | grep "$type" | while read type cvi ; do
    bash bin/download_douane.sh $type $annee $cvi
done
done

file documents/*$annee*.pdf | grep HTML | sed 's/:.*//' | sed 's/.pdf//' | while read file ; do
	rm $file*;
done
#rm /tmp/$$.cvi.tmp
