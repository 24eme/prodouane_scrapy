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
    code_parc = num_parc
    length = len(num_parc)
    zeros = ''

    if length == 1:
        code_parc = '000' + num_parc
    if length == 2:
        code_parc = '00' + num_parc
    if length == 3:
        code_parc = '0' + num_parc

    for zero in range(5-len(section)):
        zeros = zeros + '0'

    if len(section) == 1:
        section = '0' + section

    return "%s000%s%s" % (code_communes, section, code_parc)


def parse_csv_to_array(data):
    communes = {}

    for line in data:
        commune = line.split(';')
        communes[commune[1].rstrip()] = commune[0].rstrip()
    return communes


parcellaire = {}
liste_parcellaire = []

headers = [
    'CVI Operateur', 'Siret Operateur', 'Nom Operateur', 'Adresse Operateur',
    'CP Operateur', 'Commune Operateur', 'Email Operateur', 'IDU', 'Commune',
    'Lieu dit', 'Section', 'Numero parcelle', 'Produit', 'Cepage',
    'Superficie', 'Superficie cadastrale', 'Campagne', 'Ecart pied',
    'Ecart rang', 'Mode savoir faire', 'Statut', 'Date MaJ'
]

numero_cvi = sys.argv[1]
directory = os.path.dirname(os.path.realpath(__file__)) + '/../documents/'
filename = 'parcellaire-' + numero_cvi + "-%s.html"

communesFile = 'communes.csv'
listCommunes = []
with open(directory + communesFile, 'r') as communesfile:
    data = communesfile.readlines()
    listCommunes = parse_csv_to_array(data)

# Premier onglet
with open(directory + filename % 'accueil', 'rb') as html_file:
    tables = SoupStrainer('table')

    soup = BeautifulSoup(html_file, 'lxml', parse_only=tables)
    tds = soup.select('td.fdcCoordonneCol2')
    parcellaire['CVI Operateur'] = tds[0].string.encode('utf-8', 'replace')

    if tds[1].string:
        parcellaire['Siret Operateur'] = tds[1].string.encode('utf-8', 'replace')
    else:
        parcellaire['Siret Operateur'] = ""
    parcellaire['Nom Operateur'] = tds[2].string.encode('utf-8', 'replace').strip().replace('&amp;', '&').replace('&amp;', '&').replace('&amp;', '&')

    if tds[15].string:
        parcellaire['Adresse Operateur'] = tds[15].string.encode('utf8')
    else:
        parcellaire['Adresse Operateur'] = ""

    parcellaire['CP Operateur'] = tds[16].string.encode('utf8') \
                                         .split(' ', 1)[0]
    parcellaire['Commune Operateur'] = tds[16].string.encode('utf-8', 'replace').strip().split(' ', 1)[1]
    parcellaire['Email Operateur'] = tds[19].stripped_string

    date_maj = tds[20].string.encode('utf8') or '00/00/0000'

    # Deuxième onglet
    with open(directory + filename % 'parcellaire', 'rb') as html_file:
        tables = SoupStrainer('table')

        soup = BeautifulSoup(html_file, 'lxml', parse_only=tables)
        trs = soup.find_all('tr', class_='rf-cst-r')
        for tr in trs:
            infos_parcelles = []
            infos_parcelles.append(tr.td.string.encode('utf8'))
            for td in tr.td.next_siblings:
                infos_parcelles.append(td.string)

            parcellaire['Commune'] = infos_parcelles[0]

            if infos_parcelles[1]:
                parcellaire['Lieu dit'] = infos_parcelles[1].string.encode('utf8')
            else:
                parcellaire['Lieu dit'] = ""

            match = re.search(r'([A-Z]+)(\d+)', infos_parcelles[2])
            parcellaire['Section'] = match.group(1)
            parcellaire['Numero parcelle'] = match.group(2).lstrip('0')

            if parcellaire['Commune'] in listCommunes:
                parcellaire['IDU'] = generate_idu(
                    listCommunes[parcellaire['Commune']],
                    parcellaire['Section'],
                    parcellaire['Numero parcelle']
                )

            if infos_parcelles[3]:
                parcellaire['Superficie cadastrale'] = transform_superficie(
                    infos_parcelles[3].parent['title']
                )
                produit = infos_parcelles[3]

                parcellaire['Produit'] = re.sub('^  *', '', re.sub('  *$', '', re.sub(' ros($| )', ' rosé ',
                        re.sub(' bl($| )', ' blanc ',
                        re.sub('Muscadet$', 'Muscadet AC',
                        re.sub('cx ancenis', 'Coteaux d\'Ancenis',
                        infos_parcelles[3] \
                            .encode('utf8') \
                            .replace('Ctes ', 'Côtes ') \
                            .replace(' Ste-', ' Sainte ') \
                            .replace(' rs', ' rosé') \
                            .replace(' rg', ' rouge') \
                            .replace(' / lie', ' sur lie') \
                            .replace('Cx Loire', 'Coteaux de la Loire ')
                            .replace('ctes Grandlieu', 'côtes de Grand lieu')
                            .replace('  ANCENIS', 'Coteaux d\'Ancenis')
                            .replace('Muscadet sur lie', 'Muscadet AC sur lie')
                            .replace('Côtes Provence', 'Côtes de Provence')
                        , flags=re.I), flags=re.I), flags=re.I)))).replace('  ', ' ')

            else:
                parcellaire['Produit'] = ""
                parcellaire['Superficie cadastrale'] = ""

            parcellaire['Cepage'] = infos_parcelles[4]

            parcellaire['Superficie'] = transform_superficie(infos_parcelles[5])

            parcellaire['Campagne'] = infos_parcelles[6]
            parcellaire['Ecart pied'] = infos_parcelles[8]
            parcellaire['Ecart rang'] = infos_parcelles[9]

            try:
                if infos_parcelles[11]:
                    parcellaire['Mode savoir faire'] = \
                        infos_parcelles[11].encode('utf-8')
                else:
                    parcellaire['Mode savoir faire'] = ""
            except IndexError:
                parcellaire['Mode savoir faire'] = ""

            try:
                parcellaire['Statut'] = infos_parcelles[10].encode('utf8')
            except AttributeError:
                parcellaire['Statut'] = ""

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
