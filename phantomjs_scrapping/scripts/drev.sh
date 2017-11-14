#!/bin/bash

#echo "id;produit;Surface Ha;Surface a;Surface ca;volume hl;volume l;volume année hl;volume année l;vci année-1 hl;vci année-1 l;VCI rafraichi hl;VCI rafraichi l;VCI complément hl;VCI complément l;vci détruit hl;vci détruit l" > data/drev.csv
echo "id;annee;produit;Surface;volume;volume année;vci année-1;VCI rafraichi;VCI complément;vci détruit" > data/drevSansCVI.csv
grep -A 1005 'LibelleVin' html/drev_*.html   | sed 's/html\/drev_[0-9_]*.html-//' | sed 's/<[^>]*>//g' | tr '\n' ';' | sed 's/html\/drev_\([0-9]*\)_\([0-9]*\)[0-9_]*.html:/\n\1@@\2;/g'  | sed 's/;\s*/;/g' | grep '[0-9]' | awk -F ';' '{ Volume = ($189 * 100 + $240) /100.0 ; VolAnnee = ($291 * 100 + $342) / 100.0 ; VCI = ($393 * 100 + $444) / 100.0 ; if (VCI == 0) VolAnnee = Volume ; print $1";"$2";"($36 * 10000 + $87 * 100 + $138) / 10000.0";" Volume ";" VolAnnee ";" VCI ";" ($648 * 100 + $699) / 100.0";" ($750 * 100 + $801) / 100.0";"($954 * 100 + $1005) / 100.0}' | sed 's/@@/;/' | sort -t ";" -k 1,1 >> data/drevSansCVI.csv
#grep -A 1005 'LibelleVin' html/drev_*.html   | sed 's/html\/drev_[0-9]*.html-//' | sed 's/<[^>]*>//g' | tr '\n' ';' | sed 's/html\/drev_\([0-9]*\).html:/\n\1;/g'  | sed 's/;\s*/;/g' | grep '[0-9]' >> data/drev.csv
echo "id;cvi" > data/drevIdentifiantCVI.csv
rgrep -nE "<td>[0-9]+</td><td>[0-9]{4}</td>" html/breforedrev_* | sed 's/<td>//g' | sed 's|</td>|;|g' | sed -r 's/[ \t]*//g' | sed 's/;$//' | sed 's|html/breforedrev_||' | sed -r 's/\.html:[0-9]+:/;/' | grep ";2016$" | cut -d ";" -f 1,2 | sort | uniq | sort -t ";" -k 1,1 >> data/drevIdentifiantCVI.csv

join -a 1 --header -t ";" data/drevSansCVI.csv data/drevIdentifiantCVI.csv > data/drev.csv

rm data/drevSansCVI.csv data/drevIdentifiantCVI.csv
