#!/bin/bash

. scripts/config.inc

echo "trying with $1/$2..."
mycookie=$(QT_QPA_FONTDIR=/usr/share/fonts QT_QPA_PLATFORM=offscreen phantomjs scripts/login.js $domain $1 $2 | sed 's/ASP.NET_SessionId=//' )
if ! text "$mycookie"; then
	echo Pas de cookie trouvé
	exit;
fi
nextid=$(echo $(ls -1rt identites/*html | tail -n 1 | sed 's/.html//') + 1 | bc )
echo $mycookie
QT_QPA_FONTDIR=/usr/share/fonts QT_QPA_PLATFORM=offscreen phantomjs scripts/identiesSGV.js $domain $nextid $mycookie
echo $mycookie
QT_QPA_FONTDIR=/usr/share/fonts QT_QPA_PLATFORM=offscreen phantomjs scripts/exit.js $domain $mycookie

