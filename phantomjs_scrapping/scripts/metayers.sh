#!/bin/bash

grep -A 120 EVV_ligne_explt_LabelNumero identites/*.html  | grep -v 'ajaxPopup_url = ' | sed 's/identites\/[0-9]*.html-//' | sed 's/<[^>]*>//g' | sed 's/;//g'  | tr '\n' ';' | sed 's/identites\//\n/g'  | sed 's/.html:/;/'  | sed 's/;[ \t]*/;/g'  > /tmp/metayers.csv
grep -A 120 UC_EVV_ligne_bailleur_LabelNumero identites/*.html  | grep -v 'ajaxPopup_url = ' | sed 's/identites\/[0-9]*.html-//' | sed 's/<[^>]*>//g' | sed 's/;//g'  | tr '\n' ';' | sed 's/identites\//\n/g'  | sed 's/.html:/;/'  | sed 's/;[ \t]*/;/g' > /tmp/bailleurs.csv
echo "id;numero;MFV;ratio;id co partageant;nom co partageant;MFV;ratio;cvi" > data/metayers.csv
cat /tmp/metayers.csv | awk -F ';' '{print $1";"$2";"$7";"$20";"$54";"$66";"$76}' | sed 's/:/;/' >> data/metayers.csv
cat /tmp/bailleurs.csv | awk -F ';' '{print $1";"$2";"$3";"$12";"$42";"$58";"$71";"$102}' | sed 's/:/;/' >> data/metayers.csv

rm /tmp/metayers.csv /tmp/bailleurs.csv
