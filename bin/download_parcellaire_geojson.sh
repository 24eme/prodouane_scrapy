#!/bin/bash

if [ $# -ne 1 ]; then
	echo "Il manque un paramètre"
	exit 1
fi

cvi=$1

. $(dirname $0)/common.inc

if [ ! -f "./documents/parcellaire-${cvi}.csv" ]; then
	echo "Document inexistant"
	exit 2
fi

python posttraitement/parcellaire_csv_to_geojson.py $cvi
