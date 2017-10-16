echo "ID;type de chai;Chai de vinification;Elevage et vieillissement;Centre de conditionnement;Lieu de stockage;Prestataire de service;Intitulé;Type;Adresse;Adresse 2;Adresse 3;commune;code postal" > data/chais.csv
grep -A 250 LabelChai identites/*.html | sed 's/\&amp;*/\&/ig' | sed 's/;/ - /g' | sed 's/<[^>]*>//g' | sed 's/identites\/[0-9]*.html-//' | tr '\n' ';' | sed 's/identites\/\([0-9]*\).html:/\n\1;/g'  | awk -F ';' '{print $1";"$2";"$23";"$27";"$29";"$31";"$33";"$50";"$77";"$90";"$121";"$152";"$190";"$221}' | grep '[0-9]' | sed 's/; */;/g'  | sed 's/ *;/;/' >> data/chais.csv

