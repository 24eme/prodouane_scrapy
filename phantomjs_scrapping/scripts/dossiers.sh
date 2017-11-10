#!/bin/bash

rgrep -A 5000 "Etat du dossier d'identification" identites/  | grep -B 5000 '</table>' | sed 's/<[^>]*>//g'  | tail -n +32 | sed 's/identites\///' | sed 's/\.html./;/' | tr '\n' ';' | sed 's/popupIdentite.aspx./\n/g'  | grep --color 'WebServices/$' | awk -F ';' '{print $3";"$36";"$58";"$130}'  | sed 's/; */;/g'  | grep -i '[a-z]' > data/dossiers.csv
