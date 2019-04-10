# -*- coding: utf-8 -*-

""" Transforme les .html en csv """

import sys
import re
import csv
from bs4 import BeautifulSoup, SoupStrainer

parcellaire = {}
liste_parcellaire = []

headers = [
    'CVI Operateur', 'Siret Operateur', 'Nom Operateur', 'Adresse Operateur',
    'CP Operateur', 'Commune Operateur', 'Email Operateur', 'Commune',
    'Lieu dit', 'Section', 'Numero parcelle', 'Produit', 'Cepage',
    'Superficie', 'Campage', 'Ecart pied', 'Ecart rang']

numero_cvi = sys.argv[1]
directory = './documents/'
file = 'parcellaire-' + numero_cvi + '-%s.html'

# Premier onglet
with open(directory + file % 'accueil', 'rb') as html_file:
    tables = SoupStrainer('table')

    soup = BeautifulSoup(html_file, 'lxml', parse_only=tables)
    tds = soup.select('td.fdcCoordonneCol2')
    parcellaire['CVI Operateur'] = tds[0].string
    parcellaire['Siret Operateur'] = tds[1].string
    parcellaire['Nom Operateur'] = tds[2].string.strip()
    parcellaire['Adresse Operateur'] = tds[15].string
    parcellaire['CP Operateur'] = tds[16].string.split(' ', 1)[0]
    parcellaire['Commune Operateur'] = tds[16].string.split(' ', 1)[1]
    parcellaire['Email Operateur'] = tds[19].stripped_string

# Deuxième onglet
with open(directory + file % 'parcellaire', 'rb') as html_file:
    tables = SoupStrainer('table')

    soup = BeautifulSoup(html_file, 'lxml', parse_only=tables)
    trs = soup.find_all('tr', class_='rf-cst-r')
    for tr in trs:
        infos_parcelles = []
        infos_parcelles.append(tr.td.string)
        for td in tr.td.next_siblings:
            infos_parcelles.append(td.string)

        parcellaire['Commune'] = infos_parcelles[0]
        parcellaire['Lieu dit'] = infos_parcelles[1]

        match = re.search(r'([A-Z]+)(\d+)', infos_parcelles[2])
        parcellaire['Section'] = match.group(1)
        parcellaire['Numero parcelle'] = match.group(2).lstrip('0')

        parcellaire['Produit'] = infos_parcelles[3].encode('utf-8')
        parcellaire['Cepage'] = infos_parcelles[4]

        superficie = re.search(r'(\d+)Ha (\d+)Ar (\d+)Ca', infos_parcelles[5])
        parcellaire['Superficie'] = '{},{}{}'.format(superficie.group(1),
                                                     superficie.group(2),
                                                     superficie.group(3)
                                                     ).rstrip('0')
        parcellaire['Campage'] = infos_parcelles[6]
        parcellaire['Ecart pied'] = infos_parcelles[8]
        parcellaire['Ecart rang'] = infos_parcelles[9]

        liste_parcellaire.append(parcellaire.copy())

if len(liste_parcellaire):
    with open(directory + numero_cvi + '.csv', 'w') as f:
        w = csv.DictWriter(f, headers)
        w.writeheader()
        w.writerows(liste_parcellaire)
