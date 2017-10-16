ls ivso/*.html | while read file ; do
id=''
tva=''
compta=''
id=$(echo $file | sed 's/ivso.//' | sed 's/.html//')
compta=$(cat $file | grep ContentPlaceHolder1_uc_Interpro_txtCpteGen | sed 's/.*value="//' | sed 's/".*//' )
tva=$(cat $file | grep ctl00_ContentPlaceHolder1_Uc_IdentityPanel_DbLayer_ppm_numSn_TheLabel | sed 's/.*ctl00_ContentPlaceHolder1_Uc_IdentityPanel_DbLayer_ppm_numSn_TheLabel".//' | sed 's/<.*//')
echo $id";"$compta";"$tva";";
done | sed 's/;0;/;;/' | grep -v ';;;'

