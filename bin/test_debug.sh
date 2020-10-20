#!/bin/bash

. bin/config.inc

rm debug/*

PRODOUANE_DEBUG=true bash bin/download_douane.sh dr 2019 $PRODOUANE_DEBUG_DR
PRODOUANE_DEBUG=true bash bin/download_douane.sh sv11 2019 $PRODOUANE_DEBUG_SV11
PRODOUANE_DEBUG=true bash bin/download_douane.sh sv12 2019 $PRODOUANE_DEBUG_SV12
PRODOUANE_DEBUG=true bash bin/download_parcellaire.sh $PRODOUANE_DEBUG_PARCELLAIRE

sed -i 's/value="[^"]*="/value="CLEANED"/g' debug/*
sed -i 's/value="[0-9-][0-9]*:[0-9-]*"/value="CLEANED"/g' debug/*
sed -i 's/CDATA\[[0-9-][0-9]*:[0-9-]*\]/CDATA[CLEANED]/g' debug/*
sed -i 's/token=[^ "]*[ "]/token=CLEANED/g' debug/*
sed -i 's/views*_dom_id[":]*[^"]*"/view_dom_id:CLEANED/g' debug/*
sed -i 's/RichFaces.panelTabs.*//' debug/*
sed -i 's/permissionsHash":"[^"]*"/permissionsHash":"CLEANED"/' debug/*
sed -i 's/javax.faces.ViewState" value="[^"]*"/javax.faces.ViewState" value="CLEANED"/' debug/*

cd debug

git status -s | grep -v redirectsaml || echo TOUT EST OK
