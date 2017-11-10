#!/bin/bash

. scripts/config.inc

ID=$1

if ! test "$ID" ; then
  ID=1;
fi

while test $ID -lt 45600 ; do
  mycookie=$(QT_QPA_FONTDIR=/usr/share/fonts QT_QPA_PLATFORM=offscreen phantomjs scripts/login.js $domain $utilisateur_identite $motdepasse_identite | sed 's/ASP.NET_SessionId=//' ) ;
  echo $mycookie
  QT_QPA_FONTDIR=/usr/share/fonts QT_QPA_PLATFORM=offscreen phantomjs scripts/identitesSGV.js $domain $ID $mycookie;
  QT_QPA_FONTDIR=/usr/share/fonts QT_QPA_PLATFORM=offscreen phantomjs scripts/exit.js $domain $mycookie
  ID=$(ls -1rt identites/ | tail -n 1 | sed 's/.html//')
done
