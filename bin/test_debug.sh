#!/bin/bash

. bin/config.inc

. $(dirname $0)/common.inc

mkdir -p debug
rm debug/*
if ! test -d debug/.git ; then
	cd debug
	git init .
	echo "*log" > .gitignore
	git add .gitignore
	git commit -m "commit initial avec gitignore pour les log"
	cd -
fi

echo
echo "test DR"
echo "================"
rm -f "documents/dr-2019-"$PRODOUANE_DEBUG_DR""*
PRODOUANE_DEBUG=true bash bin/download_douane.sh dr 2019 $PRODOUANE_DEBUG_DR > debug/dr-2019.log 2>&1

if test -s documents/dr-2019-"$PRODOUANE_DEBUG_DR".pdf ;  then echo " PDF Présent :)";  else 	echo "Erreur pas de pdf dr";  fi
if test -s documents/dr-2019-"$PRODOUANE_DEBUG_DR".html ; then echo " HTML Présent :)"; else    echo "Erreur pas de HTML dr"; fi
if test -s documents/dr-2019-"$PRODOUANE_DEBUG_DR".xls ;  then echo " XLS Présent :)";  else    echo "Erreur pas de xls dr";  fi

echo
echo "test SV11"
echo "================"
rm -f "documents/sv11-2019-"$PRODOUANE_DEBUG_SV11""*
PRODOUANE_DEBUG=true bash bin/download_douane.sh sv11 2019 $PRODOUANE_DEBUG_SV11 > debug/sv11-2019.log 2>&1

if test -s documents/sv11-2019-"$PRODOUANE_DEBUG_SV11".pdf ;  then echo " PDF Présent :)" ;  else echo "Erreur pas de pdf sv11";  fi
if test -s documents/sv11-2019-"$PRODOUANE_DEBUG_SV11".html ; then echo " HTML Présent :)" ; else echo "Erreur pas de html sv11"; fi
if test -s documents/sv11-2019-"$PRODOUANE_DEBUG_SV11".xls ;  then echo " XLS Présent :)" ;  else echo "Erreur pas de xls sv11";  fi

echo
echo "test SV12"
echo "================"
rm -f "documents/sv12-2019-"$PRODOUANE_DEBUG_SV12""*
PRODOUANE_DEBUG=true bash bin/download_douane.sh sv12 2019 $PRODOUANE_DEBUG_SV12 > debug/sv12-2019.log 2>&1

if test -s documents/sv12-2019-"$PRODOUANE_DEBUG_SV12".pdf  ; then echo " PDF Présent :)";  else echo "Erreur pas de pdf dr";  fi
if test -s documents/sv12-2019-"$PRODOUANE_DEBUG_SV12".html ; then echo " HTML Présent :)"; else echo "Erreur pas de html dr"; fi
if test -s documents/sv12-2019-"$PRODOUANE_DEBUG_SV12".xls  ; then echo " XLS Présent :)";  else echo "Erreur pas de xls dr";  fi

echo
echo "test Parcellaire"
echo "================"
rm -f "documents/parcellaire-"$PRODOUANE_DEBUG_PARCELLAIRE""*
PRODOUANE_DEBUG=true bash bin/download_parcellaire.sh $PRODOUANE_DEBUG_PARCELLAIRE > debug/parcellaire.log 2>&1

if test -s documents/parcellaire-"$PRODOUANE_DEBUG_PARCELLAIRE"-parcellaire.html ; then echo " HTML Parcellaire Présent :)"; else echo "Erreur pas de HTML parcellaire"; fi
if test -s documents/parcellaire-"$PRODOUANE_DEBUG_PARCELLAIRE"-accueil.html ; then echo " HTML accueil Parcellaire Présent :)"; else echo "Erreur pas de HTML accueil Parcellaire"; fi
if test -s documents/parcellaire-"$PRODOUANE_DEBUG_PARCELLAIRE"-parcellaire.pdf ; then echo " PDF Parcellaire Présent :)"; else echo "Erreur pas de PDF Parcellaire"; fi
if test -s documents/parcellaire-"$PRODOUANE_DEBUG_PARCELLAIRE".csv && test 0$(wc -l documents/parcellaire-"$PRODOUANE_DEBUG_PARCELLAIRE".csv | sed 's/ .*//') -gt 1 ; then echo " CSV Parcellaire Présent :)"; else echo "Erreur pas de CSV Parcellaire"; fi

sed -i 's/value="[^"]*="/value="CLEANED"/g' debug/*
sed -i 's/value="[0-9-][0-9]*:[0-9-]*"/value="CLEANED"/g' debug/*
sed -i 's/CDATA\[[0-9-][0-9]*:[0-9-]*\]/CDATA[CLEANED]/g' debug/*
sed -i -r 's/token="[^">]*([">])/token="CLEANED\1/g' debug/*
sed -i -r 's/token=[^">]*([">])/token=CLEANED\1/g' debug/*
sed -i 's/name="token" value="[^"]*"/name="token" value="CLEANED"/g' debug/*
sed -i 's/views*_dom_id[":]*[^"]*"/view_dom_id:CLEANED/g' debug/*
sed -i 's/RichFaces.panelTabs.*//' debug/*
sed -i 's/permissionsHash":"[^"]*"/permissionsHash":"CLEANED"/' debug/*
sed -i 's/javax.faces.ViewState" value="[^"]*"/javax.faces.ViewState" value="CLEANED"/' debug/*
sed -i 's/javax.faces.ViewState" value="[^"]*"/javax.faces.ViewState" value="CLEANED"/' debug/*
sed -i 's/input type="hidden" name="token" value="[0-9_]*"/input type="hidden" name="token" value="CLEANED"/' debug/*
sed -i 's/SAMLResponse" value="[^"]*"/SAMLResponse" value="CLEANED"/' debug/*
sed -i -r 's/(class="localeDate" val=")[0-9]+(")/\1CLEANED\2/' debug/*

cd debug

echo
echo "Comparaison"
echo "================"
git status -s | grep -v redirectsaml || echo TOUT EST OK
