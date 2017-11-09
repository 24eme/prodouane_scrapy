
echo "id;cvi" > data/drevCVI.csv
rgrep -nE "<td>[0-9]+</td><td>[0-9]{4}</td>" html/breforedrev_* | sed 's/<td>//g' | sed 's|</td>|;|g' | sed -r 's/[ \t]*//g' | sed 's/;$//' | sed 's|html/breforedrev_||' | sed -r 's/\.html:[0-9]+:/;/' | grep ";2016$" >> data/drevCVI.csv
