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
        request.urlretrieve(url%(millesime,dept, num_commune, num_commune), outputfile)

    return outputfile

def get_geoJson_parcelle(directory, parcellaire):
    num_commune = parcellaire[0]['CVI Operateur'];
    idu = parcellaire[0]['IDU'];
    millesimes = ['2017-07-06', '2017-10-12',
                '2018-01-02', '2018-04-03','2018-06-29',
                '2018-10-01', '2019-01-01', '2019-04-01',
                '2019-07-01', 'latest'
                ];
    for millesime in millesimes[::-1]:
        file_geojson_path = get_geoJson_commune(directory, num_commune, idu, millesime);
        if file_geojson_path.find('.gz'):
          try:
            with gzip.open(file_geojson_path, 'rb') as f:
              list_geojson = json.loads(f.read().decode('utf-8'));
              
              for parcelle in list_geojson["features"]:
                if(parcelle['properties']['id'] == idu):
                    #check if parcelle contains more than one cepage
                    parcelle['properties']['parcellaires'] = parcellaire;
                    return parcelle;
          except: #Not a gz probably 404
            continue
          #parcelle doesn't found in that millesime downloaded
          #make new downloading and process
    
def my_cache_download(filepath):

    return os.path.isfile(filepath);

def create_array_assoc(parcellaires):
    assoc = {};
    cepages = [];
    for parcellaire in parcellaires:
        cepages.append(parcellaire);
        for p in parcellaires:
            if(parcellaire['IDU'] == p['IDU'] and parcellaire['Cepage'] != p['Cepage']):
                cepages.append(p);
        assoc[parcellaire['IDU']] = cepages;
        cepages = [];
    return assoc;

parcellaire = {}

liste_parcellaire = []


numero_cvi = sys.argv[1];
directory = os.path.dirname(os.path.realpath(__file__)) + '/../documents/';
tmp_dir = '/tmp/';
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

