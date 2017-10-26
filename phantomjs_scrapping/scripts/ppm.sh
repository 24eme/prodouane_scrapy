#!/bin/bash

rgrep -A 2 donnees.identite.NUMERO_PPM identites  | grep ChampFicheIdentiteFormulaire | grep -v '><' | sed 's/<[^>]*>//g'  | sed 's/identites.//'  | sed 's/.html-\s*/;/' > data/ppm.csv
