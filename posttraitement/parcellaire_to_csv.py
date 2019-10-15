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


parcellaire = {}
liste_parcellaire = []

headers = [
    'CVI Operateur', 'Siret Operateur', 'Nom Operateur', 'Adresse Operateur',
    'CP Operateur', 'Commune Operateur', 'Email Operateur', 'Commune',
    'Lieu dit', 'Section', 'Numero parcelle', 'Produit', 'Cepage',
    'Superficie', 'Superficie cadastrale', 'Campagne', 'Ecart pied',
    'Ecart rang', 'Mode savoir faire', 'Statut']

numero_cvi = sys.argv[1]
directory = os.path.dirname(os.path.realpath(__file__)) + '/../documents/'
file = 'parcellaire-' + numero_cvi + '-%s.html'

# Premier onglet
with open(directory + file % 'accueil', 'rb') as html_file:
    tables = SoupStrainer('table')

    soup = BeautifulSoup(html_file, 'lxml', parse_only=tables)
    tds = soup.select('td.fdcCoordonneCol2')
    parcellaire['CVI Operateur'] = tds[0].string
    parcellaire['Siret Operateur'] = tds[1].string
    parcellaire['Nom Operateur'] = tds[2].string.encode('utf-8').strip()

    if tds[15].string:
        parcellaire['Adresse Operateur'] = tds[15].string.encode('utf-8')
    else:
        parcellaire['Adresse Operateur'] = ''

    parcellaire['CP Operateur'] = tds[16].string \
                                         .encode('utf-8') \
                                         .split(' ', 1)[0]
    parcellaire['Commune Operateur'] = tds[16].string \
                                              .encode('utf-8') \
                                              .split(' ', 1)[1]
    parcellaire['Email Operateur'] = tds[19].stripped_string

    date_maj = tds[20].string or '00/00/0000'

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

            parcellaire['Commune'] = infos_parcelles[0].encode('utf-8')

            if infos_parcelles[1]:
                parcellaire['Lieu dit'] = infos_parcelles[1].encode('utf-8')
            else:
                parcellaire['Lieu dit'] = ''

            match = re.search(r'([A-Z]+)(\d+)', infos_parcelles[2])
            parcellaire['Section'] = match.group(1)
            parcellaire['Numero parcelle'] = match.group(2).lstrip('0')

            if infos_parcelles[3]:
                parcellaire['Superficie cadastrale'] = transform_superficie(
                    infos_parcelles[3].parent['title']
                )
                parcellaire['Produit'] = infos_parcelles[3].encode('utf-8').replace('Ctes ', 'Côtes de ').replace(' Ste-', ' Sainte ').replace(' rs', ' rosé').replace(' rg', ' rouge')
            else:
                parcellaire['Produit'] = ''
                parcellaire['Superficie cadastrale'] = ''

            parcellaire['Cepage'] = infos_parcelles[4].encode('utf-8')

            parcellaire['Superficie'] = transform_superficie(infos_parcelles[5])

            parcellaire['Campagne'] = infos_parcelles[6]
            parcellaire['Ecart pied'] = infos_parcelles[8]
            parcellaire['Ecart rang'] = infos_parcelles[9]

            try:
                if infos_parcelles[11]:
                    parcellaire['Mode savoir faire'] = \
                        infos_parcelles[11].encode('utf-8')
                else:
                    parcellaire['Mode savoir faire'] = ''
            except IndexError:
                    parcellaire['Mode savoir faire'] = ''

            parcellaire['Statut'] = infos_parcelles[10].encode('utf-8')

            liste_parcellaire.append(parcellaire.copy())

            if date_maj:
                date_transform = re.search(r'(\d+)/(\d+)/(\d+)', date_maj)
                date_maj = '{}{}{}'.format(date_transform.group(3),
                                           date_transform.group(2),
                                           date_transform.group(1))

                outputfile = 'parcellaire-' + numero_cvi + '-' + date_maj + '.csv'
                print(outputfile)
                with open(directory + outputfile, 'w') as f:
                    w = csv.DictWriter(f, headers, delimiter=';')
                    w.writeheader()
                    w.writerows(liste_parcellaire)
