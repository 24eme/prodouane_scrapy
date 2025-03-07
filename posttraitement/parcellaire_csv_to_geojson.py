#! /usr/bin/python
# -*- coding: utf-8 -*-

""" Transforme les .html en csv """

import sys
import os
import re
import csv
import urllib
import gzip
import json
import time

cache_parcelles_commune_millesimes = {};
cache_parcelles = {};

def get_file_parcellaire(numero_cvi, directory):
    for file in os.listdir(directory):
        if(re.findall('parcellaire-'+numero_cvi+'.csv', file)):
            return file
    return -1;

def parse_csv_to_array(data):
    csv_reader = csv.DictReader(csv_file, delimiter=';')
    return [r for r in csv_reader];
    
def get_geoJson_commune(directory, cvi, idu, millesime):
    #https://cadastre.data.gouv.fr/data/etalab-cadastre/2019-10-01/geojson/communes/13/13002/cadastre-13002-parcelles.json.gz

    url = 'https://cadastre.data.gouv.fr/data/etalab-cadastre/%s/geojson/communes/%s/%s/cadastre-%s-parcelles.json.gz';
    dept = idu[0:2];
    num_commune = idu[0:5];

    outputfile = directory + 'cadastre-' + millesime +'-'+ num_commune + '-parcelles.json.gz';
    if(my_cache_download(outputfile)):
        return outputfile

    try:
        urllib.urlretrieve(url%(millesime,dept, num_commune, num_commune), outputfile)
    except AttributeError:
        from urllib import (parse, request)
        try:
            request.urlretrieve(url%(millesime,dept, num_commune, num_commune), outputfile)
        except urllib.error.HTTPError as e:
            return ""
        except urllib.error.URLError as e:
            return ""
    except urllib.error.HTTPError as e:
        return ""
    except urllib.error.URLError as e:
        return ""

    return outputfile

def get_geoJson_parcelle(directory, parcellaire):
    idu = parcellaire[0]['IDU'];
    millesimes = ['latest','2022-10-01','2022-07-01','2022-04-01','2022-01-01','2021-10-01','2021-07-01','2021-04-01','2021-02-01','2020-10-01','2020-07-01','2020-01-01','2019-10-01','2019-07-01','2019-04-01','2019-01-01']
    if not idu in cache_parcelles:
        for millesime in millesimes:
            if not idu[0:5] in cache_parcelles_commune_millesimes:
                cache_parcelles_commune_millesimes[idu[0:5]] = {}
            if not millesime in cache_parcelles_commune_millesimes[idu[0:5]]:
                cache_parcelles_commune_millesimes[idu[0:5]][millesime] = True
                file_geojson_path = get_geoJson_commune(directory, idu[0:5], idu, millesime);
                if not file_geojson_path:
                    continue
                if file_geojson_path.find('.gz'):
                    try:
                        with gzip.open(file_geojson_path, 'rb') as f:
                            list_geojson = json.loads(f.read().decode('utf-8'));
                        
                        for parcelle in list_geojson["features"]:
                            cache_parcelles[parcelle['properties']['id']] = parcelle
                    except: #Not a gz probably 404
                        continue
                if idu in cache_parcelles:
                    parcelle = cache_parcelles[idu]
                    parcelle['properties']['parcellaires'] = parcellaire;
                    return parcelle
    try:
        parcelle = cache_parcelles[idu]
        #check if parcelle contains more than one cepage
        parcelle['properties']['parcellaires'] = parcellaire;
        return parcelle
    except: #Not a gz probably 404
        return None
    return None

def my_cache_download(filepath):
    return os.path.isfile(filepath) and os.path.getmtime(filepath) > time.time() - 604800; #Si plus vieux qu'une semaine on ignore le cache

def convert_parcellaire(parcellaire):
    try:
        if parcellaire['IDU']:
            return parcellaire
    except KeyError:
        parcellaire['IDU'] = parcellaire['Code INSEE de la commune'] + parcellaire['Référence cadastrale de la parcelle'][6:].replace(' ', '0')
        parcellaire['Commune'] = parcellaire['Libellé de la commune']
        parcellaire['Section'] = parcellaire['Référence cadastrale de la parcelle'][-6:-4]
        parcellaire['Numero parcelle'] = parcellaire['Référence cadastrale de la parcelle'][-4:]
        parcellaire['Produit'] = parcellaire['Libellé du produit']
        parcellaire['Cepage'] = parcellaire['Libellé cépage']
        parcellaire['Campagne'] = parcellaire['Campagne de plantation']
        parcellaire['Ecart pied'] = parcellaire['Écart entre les pieds de vigne']
        parcellaire['Ecart rang'] = parcellaire['Écart entre les rangs de vigne']
        parcellaire['Superficie'] = parcellaire['Superficie de la plantation']
    return parcellaire

def create_array_assoc(parcellaires):
    assoc = {};
    cepages = [];
    for parcellaire in parcellaires:
        parcellaire = convert_parcellaire(parcellaire)
        if not assoc.get(parcellaire['IDU']):
            assoc[parcellaire['IDU']] = []
        assoc[parcellaire['IDU']].append(parcellaire);
    return assoc;

parcellaire = {}

liste_parcellaire = []


numero_cvi = sys.argv[1];
directory = os.path.dirname(os.path.realpath(__file__)) + '/../documents/';
tmp_dir = '/tmp/parcellaires/'
if not os.path.exists(tmp_dir):
    os.mkdir(tmp_dir)
inputfile = get_file_parcellaire(numero_cvi, directory);

if(inputfile != -1):
    with open(directory+inputfile, 'r') as csv_file:

        parcellaires = parse_csv_to_array(csv_file);
        parcellaires = create_array_assoc(parcellaires);
        
        list_geojson_idu = {};
        obj = [];
        list_geojson_idu = {'type': 'FeatureCollection', 'features': obj};
        
        
        outputfile = 'cadastre-' + numero_cvi + '-parcelles.json';
        if(not os.path.isfile(directory + outputfile)):
            open(directory + outputfile, 'a').close();
            
        with open(directory + outputfile, 'w') as outfile:
            for idu in parcellaires:
                geojson = get_geoJson_parcelle(tmp_dir, parcellaires[idu]);
            
                if(geojson):
                    obj.append(geojson);

            if(bool(list_geojson_idu['features'])):
                json.dump(list_geojson_idu, outfile);
            else:
                os.remove(directory + outputfile);

