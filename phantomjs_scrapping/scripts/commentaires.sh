#!/bin/bash

ls identites/*.html | while read file ; do
echo -n $file | sed 's/^identites.//' | sed 's/.html$/;/'
grep -A 1500 "Observations sur" $file  | tail -n +2 | grep -B 1500 'ContentPlaceHolder1$ButtonModifyObservations' | sed 's/<[^>]*>/\n/g' | sed 's/ "/ «/g' | sed 's/" /» /g' | grep -i '[a-z]' | sed 's/;/-/g' | tr '\n' '#' | sed 's/#/ <br>/g'
echo
done | grep -v ';$' | sed 's/; */;/' > data/commentaires.csv
