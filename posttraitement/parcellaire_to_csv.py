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

    code_dep = code_communes[0:2]
    code_fincommune = code_communes[-3:]

    return "%s%s000%s%s" % (code_dep, code_fincommune, section, code_parc)


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

# Premier onglet
with open(directory + filename % 'accueil', 'rb') as html_file:
    tables = SoupStrainer('table')

    soup = BeautifulSoup(html_file, 'lxml', parse_only=tables)
    tds = soup.select('td.fdcCoordonneCol2')
    parcellaire['CVI Operateur'] = tds[0].string

    if tds[1].string:
        parcellaire['Siret Operateur'] = tds[1].string
    else:
        parcellaire['Siret Operateur'] = ""
    parcellaire['Nom Operateur'] = tds[2].string.strip()
    parcellaire['Nom Operateur'] = parcellaire['Nom Operateur'].replace('&amp;', '&')

    if tds[15].string:
        parcellaire['Adresse Operateur'] = tds[15].string
    else:
        parcellaire['Adresse Operateur'] = ""

    parcellaire['CP Operateur'] = tds[16].string.split(' ', 1)[0]
    parcellaire['Commune Operateur'] = tds[16].string.strip().split(' ', 1)[1]
    parcellaire['Email Operateur'] = tds[19].stripped_string

    date_maj = tds[20].string or '00/00/0000'

    # Deuxième onglet
    with open(directory + filename % 'parcellaire', 'rb') as html_file:
        tables = SoupStrainer('table')

        soup = BeautifulSoup(html_file, 'lxml', parse_only=tables)
        trs = soup.find_all('tr', class_='rf-cst-r')
        for tr in trs:
            infos_parcelles = []
            infos_parcelles.append(tr.td.string)
            for td in tr.td.next_siblings:
                infos_parcelles.append(td.string)

            parcellaire['Commune'] = infos_parcelles[0]

            if infos_parcelles[1]:
                parcellaire['Lieu dit'] = re.sub(r' *\* *', '', infos_parcelles[1].string)
            else:
                parcellaire['Lieu dit'] = ""

            #vérifie que la 3ème colonne est bien un IDU sinon c'est sans doute une Superficies de programme d'arrachage
            try:
                int(infos_parcelles[2][0:1])
            except ValueError:
                continue
            except TypeError:
                continue

            match = re.search(r'(\d{2})(\d{,4}) *([A-Z0-9]+)(\d{4})', infos_parcelles[2])
            CommuneId = match.group(1) + '%03d' % int(match.group(2))
            parcellaire['Section'] = match.group(3)
            parcellaire['Numero parcelle'] = match.group(4).lstrip('0')
            parcellaire['IDU'] = generate_idu(
                    CommuneId,
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
                        re.sub('AOC Alsace blanc.*', 'AOC Alsace Blanc',
                        re.sub('AOC Alsace Grand Cru.*', 'AOC Alsace Grand Cru',
                        re.sub('AOC Crémant d\'Alsace.*', 'AOC Crémant d\'Alsace',
                        infos_parcelles[3] \
                            .replace('Ctes ', 'Côtes ') \
                            .replace(' Ste-', ' Sainte ') \
                            .replace(' rs', ' rosé') \
                            .replace(' rg', ' rouge') \
                            .replace(' RG', ' rouge') \
                            .replace(' / lie', ' sur lie') \
                            .replace('Cx Loire', 'Coteaux de la Loire ')
                            .replace('ctes Grandlieu', 'côtes de Grand lieu')
                            .replace('  ANCENIS', 'Coteaux d\'Ancenis')
                            .replace('Muscadet sur lie', 'Muscadet AC sur lie')
                            .replace('Côtes Provence', 'Côtes de Provence')
                            .replace('BOUCHES-RHONE', 'Bouches-du-Rhône')
                            .replace('Edelzwicker', '')
                            .replace('Alsace blanc', 'AOC Alsace blanc')
                            .replace('ALSACE BLANC', 'AOC Alsace blanc')
                            .replace('Alsace Pinot Blanc', 'AOC Alsace blanc')
                            .replace('Alsace Pinot Gris', 'AOC Alsace blanc')
                            .replace('AGC', 'AOC Alsace Grand Cru')
                            .replace('Alsace rosé (Pinot Noir)', 'AOC Alsace Pinot Noir Rosé')
                            .replace('Crémant Alsace bl', "AOC Crémant d'Alsace")
                            .replace('CDRV', 'Côtes du Rhône Villages')
                        , flags=re.I), flags=re.I), flags=re.I), flags=re.I), flags=re.I), flags=re.I) ))).replace('  ', ' ')

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
                        infos_parcelles[11]
                else:
                    parcellaire['Mode savoir faire'] = ""
            except IndexError:
                parcellaire['Mode savoir faire'] = ""

            try:
                parcellaire['Statut'] = infos_parcelles[10]
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
