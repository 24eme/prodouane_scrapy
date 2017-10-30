#!/bin/bash

. scripts/config.inc

rgrep -B 1 -A 1 viewDocument identites/ | sed 's/href="/>/' | sed 's/\&amp;*/\&/g' | sed 's/\&lt;/</g' | sed 's/\&nbsp;/ /g' | sed 's/;//g' | sed 's/" target=/;</' | sed 's/<[^>]*>/;/g' | sed 's/identites.//' | sed 's/.html./;/' | sed 's/;\s*/;/' | tr '\n' ';' | sed 's/--/\n/g' | sed 's/^;//' | awk -F ';' 'BEGIN{print "identifiant;nom fichier;lien;date;codification"} {print $1";"$3";"$8";"$15";"$17}' | sed 's|../DocumentsOperateur|http://'$domain'/DocumentsOperateur|' > data/documents.csv


mycookie=$(QT_QPA_FONTDIR=/usr/share/fonts QT_QPA_PLATFORM=offscreen phantomjs scripts/login.js $domain $1 $2 | sed 's/ASP.NET_SessionId=//' )
echo "cookie: $mycookie"
if ! test "$mycookie" ; then
exit;
fi

awk -F ';' '{print $3}' data/documents.csv | while read url ; do
id=$(echo $url | sed 's/.*id=//')
curl -s $url -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8' -H 'Accept-Language: fr,en;q=0.7,en-US;q=0.3' --compressed -H 'Cookie: ASP.NET_SessionId='$mycookie -H 'DNT: 1' -H 'Upgrade-Insecure-Requests: 1' > documents/$id.pdf
done

QT_QPA_FONTDIR=/usr/share/fonts QT_QPA_PLATFORM=offscreen phantomjs scripts/exit.js $domain $mycookie
