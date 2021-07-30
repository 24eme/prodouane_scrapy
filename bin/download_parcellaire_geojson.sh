#!/bin/bash

if [ $# -ne 1 ]; then
	echo "Il manque un paramètre"
	exit 10
fi

cvi=$1

. $(dirname $0)/common.inc

if [ ! -f "./documents/parcellaire-${cvi}.csv" ]; then
	echo "Document inexistant"
	exit 20
fi

python3 posttraitement/parcellaire_csv_to_geojson.py $cvi 2>&1
