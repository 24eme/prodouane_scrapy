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
types="dr";
fi


for type in $(echo $types) ; do
PRODOUANE_USER="$PRODOUANE_USER" PRODOUANE_PASS="$PRODOUANE_PASS" PRODOUANE_ANNEE="$annee" scrapy crawl $type
done > /tmp/$$.cvi.tmp

cat /tmp/$$.cvi.tmp | grep "new cvi found" | sed 's/new cvi found : //' | while read type cvi ; do
PRODOUANE_USER="$PRODOUANE_USER" PRODOUANE_PASS="$PRODOUANE_PASS" PRODOUANE_ANNEE="$annee" CVI="$cvi" scrapy crawl $type
done

file documents/*$annee*.pdf | grep HTML | sed 's/:.*//' | sed 's/.pdf//' | while read file ; do
	rm $file*;
done
rm /tmp/$$.cvi.tmp
