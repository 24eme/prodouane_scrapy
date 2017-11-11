#!/bin/bash

. scripts/config.inc

awk -F ';' '{print $1}'  data/ppm.csv data/cvi.csv  | sort -u > /tmp/cvi_ppm.list

cat /tmp/cvi_ppm.list | while read id ; do
  mycookie=$(QT_QPA_FONTDIR=/usr/share/fonts QT_QPA_PLATFORM=offscreen phantomjs scripts/login.js $domain $utilisateur_drev $motdepasse_drev | sed 's/ASP.NET_SessionId=//' ) ;
  echo $mycookie
  QT_QPA_FONTDIR=/usr/share/fonts QT_QPA_PLATFORM=offscreen phantomjs scripts/drev.js $domain $id $mycookie ;
  QT_QPA_FONTDIR=/usr/share/fonts QT_QPA_PLATFORM=offscreen phantomjs scripts/exit.js $domain $mycookie
done
