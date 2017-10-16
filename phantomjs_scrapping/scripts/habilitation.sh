ls identites/*html | while read identite ; do
grep -r -A 410 lblCodeExtra $identite | sed 's/identites\/[0-9]*.html.//' | tr '\n' ' ' | sed 's/<\/td>/<\/td>\n/ig'  | sed 's/<.tr>/\n@@@@@/ig' | sed 's/<[^>]*>//g' | sed 's/^\s*//' | sed 's/\s*$//g' | sed 's/&amp;/\&/g' | tr '\n' ';' | sed 's/@@@@@/\n/g' | sed 's/--/\n/g' | sed 's/^\s*//' | grep '^[0-9][0-9]*;' 
done  > /tmp/habilitation_sansidentite.unsorted.csv
sort -t ';' -k 1,1  /tmp/habilitation_sansidentite.unsorted.csv  > /tmp/habilitation_sansidentite.csv
grep '00_lblCodeExtra">' identites/*.html | sed 's/.html.*eExtra">/;/' | sed 's/<.*//' | sed 's/<.*//' | sed 's/identites\///' | sort -t ';' -k 2,2 > /tmp/extraid2identite.csv
echo "id extravitis;id identite;syndicat;nom opérateur;commune;code postal;siren;cvi;produit;Statut producteurs de raisins;date Producteurs de raisins;Fin suspension Producteurs de raisins;Historique Producteurs de raisins;Statut Vinificateur ;date Vinificateur;fin suspension Vinificateur;Historique Vinificateur;statut Conditionneur;date Conditionneur;fin suspension Conditionneur;historique Conditionneur;statut Eleveur;date Eleveur;fin suspension Eleveur;historique Eleveur;statut Achat et vente;date Achat et vente;fin suspension Achat et vente;historique Achat et vente;statut Elaborateur;date Elaborateur;fin suspension Elaborateur;historique Elaborateur;statut Vente tireuse;date Vente tireuse;fin suspention Vente tireuse;Historique Vente tireuse" > data/habilitation.csv
join -t ';' -1 2 -2 1 /tmp/extraid2identite.csv /tmp/habilitation_sansidentite.csv >> data/habilitation.csv
rm /tmp/extraid2identite.csv /tmp/habilitation_sansidentite.csv /tmp/habilitation_sansidentite.unsorted.csv

