XLSFILE=$1

if ! test "$XLSFILE"; then
    echo "Le fichier xls est requis en premier paramètre"
    exit;
fi

CAMPAGNE=$2

if ! test "$CAMPAGNE"; then
    echo "La campagne est requise en deuxième parametre"
    exit;
fi

CSVFILE_NONFORMATE=$(echo $XLSFILE | sed 's/\.xls/.csv/')
CSVFILE_FORMATE=$(echo $XLSFILE | sed 's/\.xls/_formate.csv/')

xls2csv $XLSFILE > $CSVFILE_NONFORMATE

echo "Transformation du fichier xls en csv : $CSVFILE_NONFORMATE"

python posttraitement/dr_format_csv.py $CSVFILE_NONFORMATE $CAMPAGNE | sed 's/\&amp;/\&/' > $CSVFILE_FORMATE

echo "Formatage du csv : $CSVFILE_FORMATE"
