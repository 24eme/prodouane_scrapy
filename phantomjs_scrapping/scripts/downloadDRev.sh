#!/bin/bash

. scripts/config.inc

if ! test $1 ; then
	awk -F ';' '{print $1}'  data/ppm.csv data/cvi.csv  | sort -u > /tmp/cvi_ppm_$$.list
else
	echo $* | sed 's/ /\n/g' | grep '.' > /tmp/cvi_ppm_$$.list
fi

cat /tmp/cvi_ppm_$$.list | while read id ; do
  mycookie=$(QT_QPA_FONTDIR=/usr/share/fonts QT_QPA_PLATFORM=offscreen phantomjs scripts/login.js $domain $utilisateur_drev $motdepasse_drev | sed 's/ASP.NET_SessionId=//' ) ;
  echo $mycookie
  QT_QPA_FONTDIR=/usr/share/fonts QT_QPA_PLATFORM=offscreen phantomjs scripts/drev.js $domain $id $mycookie ;
  QT_QPA_FONTDIR=/usr/share/fonts QT_QPA_PLATFORM=offscreen phantomjs scripts/exit.js $domain $mycookie
done

rm /tmp/cvi_ppm_$$.list
