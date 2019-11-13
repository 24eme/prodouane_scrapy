#!/bin/bash

if [ $# -ne 1 ]; then
	echo "Il manque un paramètre"
	exit 2
fi

cvi=$1

cd $(dirname $0)/../ > /dev/null 2>&1

if [ ! -f "./documents/parcellaire-${cvi}.csv" ]; then
	echo "Document inexistant"
	exit 4
fi

python posttraitement/parcellaire_csv_to_geojson.py $cvi