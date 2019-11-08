#! /usr/bin/python
# -*- coding: utf-8 -*-

""" Transforme les .html en csv """

import sys
import os
import re
import csv
from bs4 import BeautifulSoup, SoupStrainer


def transform_superficie(superficie):
    superficie = re.search(r'(\d+)Ha (\d+)Ar (\d+)Ca', superficie)
    return '{:01d}.{}{}'.format(
        int(superficie.group(1)),
        superficie.group(2),
        superficie.group(3)
    ).rstrip('0')

def generate_idu(code_communes, section, num_parc):
    code_parc = num_parc;
    length = len(num_parc);
    if(length == 1):
        code_parc = '000' + num_parc;
    if(length == 2):
        code_parc = '00' + num_parc;
    if(length == 3):
        code_parc = '0' + num_parc;
    return "%s0000%s%s"%(code_communes, section, code_parc);

def parse_csv_to_array(data):
    communes = {};

    for line in data:
        commune = line.split(';');
        communes[commune[1].rstrip()] = commune[0].rstrip();
    return communes;

parcellaire = {}
liste_parcellaire = []

headers = [
    'CVI Operateur', 'Siret Operateur', 'Nom Operateur', 'Adresse Operateur',
    'CP Operateur', 'Commune Operateur', 'Email Operateur', 'IDU', 'Commune',
    'Lieu dit', 'Section', 'Numero parcelle', 'Produit', 'Cepage',
    'Superficie', 'Superficie cadastrale', 'Campagne', 'Ecart pied',
    'Ecart rang', 'Mode savoir faire', 'Statut', 'Date MaJ']

numero_cvi = sys.argv[1]
directory = os.path.dirname(os.path.realpath(__file__)) + '/../documents/'
filename = 'parcellaire-' + numero_cvi + "-%s.html"

communesFile = 'communes.csv';
listCommunes = [];
with open(directory + communesFile, 'r') as communesfile:
    data = communesfile.readlines();
    listCommunes = parse_csv_to_array(data);

# Premier onglet
with open(directory + filename % 'accueil', 'rb') as html_file:
    tables = SoupStrainer('table')

    soup = BeautifulSoup(html_file, 'lxml', parse_only=tables)
    tds = soup.select('td.fdcCoordonneCol2')
    parcellaire['CVI Operateur'] = tds[0].string.encode('ascii', 'ignore')
    parcellaire['Siret Operateur'] = tds[1].string.encode('ascii', 'ignore')
    parcellaire['Nom Operateur'] = tds[2].string.encode('ascii', 'ignore').strip()
    
    if tds[15].string:
        parcellaire['Adresse Operateur'] = tds[15].string.encode('ascii', 'ignore')
    else:
        parcellaire['Adresse Operateur'] = ''

    parcellaire['CP Operateur'] = tds[16].string \
                                         .split(' ', 1)[0]
    parcellaire['Commune Operateur'] = tds[16].string.split(' ', 1)[1]
    parcellaire['Email Operateur'] = tds[19].stripped_string

    date_maj = tds[20].string or '00/00/0000'

    # Deuxième onglet
    with open(directory + filename % 'parcellaire', 'rb') as html_file:
        tables = SoupStrainer('table')

        soup = BeautifulSoup(html_file, 'lxml', parse_only=tables)
        trs = soup.find_all('tr', class_='rf-cst-r')
        for tr in trs:
            infos_parcelles = []
            infos_parcelles.append(tr.td.string.encode('ascii', 'ignore'))
            for td in tr.td.next_siblings:
                infos_parcelles.append(td.string)

            parcellaire['Commune'] = infos_parcelles[0].encode('ascii', 'ignore')

            if infos_parcelles[1]:
                parcellaire['Lieu dit'] = infos_parcelles[1].string.encode('ascii', 'ignore')
            else:
                parcellaire['Lieu dit'] = ''

            match = re.search(r'([A-Z]+)(\d+)', infos_parcelles[2])
            parcellaire['Section'] = match.group(1)
            parcellaire['Numero parcelle'] = match.group(2).lstrip('0')

            if(listCommunes[parcellaire['Commune']]):
                parcellaire['IDU'] = generate_idu(listCommunes[parcellaire['Commune']], parcellaire['Section'], parcellaire['Numero parcelle']);

            if infos_parcelles[3]:
                parcellaire['Superficie cadastrale'] = transform_superficie(
                    infos_parcelles[3].parent['title']
                )
                produit = infos_parcelles[3]

                parcellaire['Produit'] = infos_parcelles[3].encode('ascii', 'ignore').replace('Ctes ', u'Côtes de '.encode('ascii', 'ignore')).replace(' Ste-', ' Sainte '.encode('ascii', 'ignore')).replace(' rs', u' rosé'.encode('ascii', 'ignore')).replace(' rg', ' rouge')            
 
            else:
                parcellaire['Produit'] = ''
                parcellaire['Superficie cadastrale'] = ''

            parcellaire['Cepage'] = infos_parcelles[4]

            parcellaire['Superficie'] = transform_superficie(infos_parcelles[5])

            parcellaire['Campagne'] = infos_parcelles[6]
            parcellaire['Ecart pied'] = infos_parcelles[8]
            parcellaire['Ecart rang'] = infos_parcelles[9]

            try:
                if infos_parcelles[11]:
                    parcellaire['Mode savoir faire'] = \
                        infos_parcelles[11].encode('ascii', 'ignore')
                else:
                    parcellaire['Mode savoir faire'] = ''
            except IndexError:
                    parcellaire['Mode savoir faire'] = ''

            try:
                parcellaire['Statut'] = infos_parcelles[10].encode('ascii', 'ignore')
            except AttributeError:
                parcellaire['Statut'] = ''

            liste_parcellaire.append(parcellaire.copy())

        if date_maj:
            date_transform = re.search(r'(\d+)/(\d+)/(\d+)', date_maj)
            date_maj = '{}{}{}'.format(date_transform.group(3),
                                       date_transform.group(2),
                                       date_transform.group(1))
            parcellaire['Date MaJ'] = date_maj

            outputfile = 'parcellaire-' + numero_cvi + '.csv'

            with open(directory + outputfile, 'w') as f:
                w = csv.DictWriter(f, headers, delimiter=';')
                w.writeheader()
                w.writerows(liste_parcellaire)
