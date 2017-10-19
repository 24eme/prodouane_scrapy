ls identites/*html | while read identite ; do
grep -r -A 1410 lblCodeExtra $identite | sed 's/identites\/[0-9]*.html.//' | tr '\n' ' ' | sed 's/<\/td>/<\/td>\n/ig'  | sed 's/<.tr>/\n@@@@@/ig' | sed 's/<[^>]*>//g' | sed 's/^\s*//' | sed 's/\s*$//g' | sed 's/&amp;/\&/g' | tr '\n' ';' | sed 's/@@@@@/\n/g' | sed 's/--/\n/g' | sed 's/^\s*//' | grep '^[0-9][0-9]*;'
done  > /tmp/habilitation_sansidentite.unsorted.csv
sort -t ';' -k 1,1  /tmp/habilitation_sansidentite.unsorted.csv  > /tmp/habilitation_sansidentite.csv
grep '00_lblCodeExtra">' identites/*.html | sed 's/.html.*eExtra">/;/' | sed 's/<.*//' | sed 's/<.*//' | sed 's/identites\///' | sort -t ';' -k 2,2 > /tmp/extraid2identite.csv
join -t ';' -1 2 -2 1 /tmp/extraid2identite.csv /tmp/habilitation_sansidentite.csv > data/habilitations.csv
echo "id extravitis;id identite;syndicat;nom opérateur;commune;code postal;siren;cvi;produit;type habilitation;Statut;date;Fin suspension;Historique" > data/habilitation.csv
cat data/habilitations.csv | sed 's/[ \t]*$/;/' | awk -F ';' '{
    split($11,date,"/"); if ($10) print $1";"$2";"$3";"$4";"$5";"$6";"$7";"$8";"$9";producteur de raisin;"$10";"date[3]"-"date[2]"-"date[1]";"$12";"$13 ;
    split($15,date,"/"); if ($14) print $1";"$2";"$3";"$4";"$5";"$6";"$7";"$8";"$9";vinificateur;"        $14";"date[3]"-"date[2]"-"date[1]";"$16";"$17 ;
    split($19,date,"/"); if ($18) print $1";"$2";"$3";"$4";"$5";"$6";"$7";"$8";"$9";conditionneur;"       $18";"date[3]"-"date[2]"-"date[1]";"$20";"$21 ;
    split($23,date,"/"); if ($22) print $1";"$2";"$3";"$4";"$5";"$6";"$7";"$8";"$9";eleveur;"             $22";"date[3]"-"date[2]"-"date[1]";"$24";"$25 ;
    split($27,date,"/"); if ($26) print $1";"$2";"$3";"$4";"$5";"$6";"$7";"$8";"$9";achat et vente;"      $26";"date[3]"-"date[2]"-"date[1]";"$28";"$29 ;
    split($31,date,"/"); if ($30) print $1";"$2";"$3";"$4";"$5";"$6";"$7";"$8";"$9";elaborateur;"         $30";"date[3]"-"date[2]"-"date[1]";"$32";"$33 ;
    split($35,date,"/"); if ($34) print $1";"$2";"$3";"$4";"$5";"$6";"$7";"$8";"$9";vente tireuse;"       $34";"date[3]"-"date[2]"-"date[1]";"$36";"$37 ;
}' | sed 's/;--;/;9999-99-99;/' | sort -t ';' -k 12,12 | sed 's/;9999-99-99;/;;/' >> data/habilitation.csv
rm /tmp/extraid2identite.csv /tmp/habilitation_sansidentite.csv /tmp/habilitation_sansidentite.unsorted.csv data/habilitations.csv
