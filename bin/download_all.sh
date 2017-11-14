#!/bin/bash

. $(dirname $0)/config.inc

cd $(dirname $0)/../ > /dev/null 2>&1

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


for type in $(echo $types) ; do
PRODOUANE_USER="$PRODOUANE_USER" PRODOUANE_PASS="$PRODOUANE_PASS" PRODOUANE_ANNEE="$annee" scrapy crawl $type
done

file documents/*$annee*.pdf | grep HTML | sed 's/:.*//' | sed 's/.pdf//' | while read file ; do
	rm $file*;
done
