#!/bin/bash

grep Repreneur_Repreneur_Repris_TheLabel identites/*.html | sed 's/<[^>]*>//g' | grep -v ':$' | sed 's/identites\///' | sed 's/.html:/;/' | sed 's/:/;/' > /tmp/repreneur.list
grep Repris_Repreneur_Repris_TheLabel identites/*.html    | sed 's/<[^>]*>//g' | grep -v ':$' | sed 's/identites\///' | sed 's/.html:/;/' | sed 's/:/;/' > /tmp/repris.list
awk -F ';' '{print $1";"$2}' /tmp/repreneur.list  > /tmp/repreneur.csv
awk -F ';' '{print $2";"$1}' /tmp/repris.list  > /tmp/repris.csv
echo "id repris;id repreneur" > data/reprise_repreneur.csv
cat /tmp/repreneur.csv /tmp/repris.csv | sort -u >> data/reprise_repreneur.csv

rm /tmp/repreneur.list /tmp/repris.list /tmp/repris.csv /tmp/repreneur.csv
