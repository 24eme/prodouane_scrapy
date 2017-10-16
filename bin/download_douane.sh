#!/bin/bash

. $(dirname $0)/config.inc

if ! test "$PRODOUANE_USER" || ! test "$PRODOUANE_PASS" ; then
	echo "Authentification non configurée dans le config.inc"
	exit 1;
fi

type=$1
campagne=$2
cvi=$3

if ! test "$cvi" ; then
	echo "3 arguments attendus : [dr|sv1|sv2] <campagne> <cvi>"
	exit 2;
fi

PRODOUANE_USER="$PRODOUANE_USER" PRODOUANE_PASS="$PRODOUANE_PASS" CVI="$cvi" PRODOUANE_CAMPAGNE="$campagne" scrapy crawl $type
