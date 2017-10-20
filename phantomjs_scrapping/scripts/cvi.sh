#!/bin/bash

echo "id extravitis;type;cvi" > data/cvi.csv
grep evv_TheLabel identites/*html | sed 's/.html:.* id="ctl[0-9]*_ContentPlaceHolder1_Uc_/;/' | sed 's/"[^>]*>/;/' | sed 's/ctl[0-9]*//g' | sed 's/<[^>]*>//g' | sed 's/_Panel_RepeaterEVV_CHAIS2*__Uc_EVV_CHAIS_Panel_/;/' | sed 's/Panel_RepeaterEVV_/;/' | sed 's/_DbLayer_evv_nr_evv_TheLabel//' | sed 's/ligne_bailleur__UC_EVV_ligne_bailleur/bailleur/' | sed 's/explt__UC_EVV_Panel_explt/exploitation/' | sed 's/DbLayer_evv_nr_evv_TheLabel/exploitation/' | sed 's/identites.//'  | awk -F ';' '{print $1";"$3";"$4}' | sort -u >> data/cvi.csv
