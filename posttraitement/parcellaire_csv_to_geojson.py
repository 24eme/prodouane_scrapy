#! /usr/bin/python
# -*- coding: utf-8 -*-

""" Transforme les .html en csv """

import sys
import os
import re
import csv
import wget
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
    
def get_geoJson_commune(directory, cvi, idu):
    #https://cadastre.data.gouv.fr/data/etalab-cadastre/2019-10-01/geojson/communes/13/13002/cadastre-13002-parcelles.json.gz

    url = 'https://cadastre.data.gouv.fr/data/etalab-cadastre/latest/geojson/communes/%s/%s/cadastre-%s-parcelles.json.gz';
    dept = idu[0:2];
    num_commune = idu[0:5];

    outputfile = 'cadastre-' + num_commune + '-parcelles.json.gz';
    if(not my_cache_download(directory, outputfile)):
        #file doesn't exist
        wget.download(url%(dept, num_commune, num_commune), directory + outputfile);
    return outputfile;

def get_geoJson_parcelle(directory, parcelle):
    num_commune = parcellaire['CVI Operateur'];
    idu = parcellaire['IDU'];
    file_geojson_name = get_geoJson_commune(directory, num_commune, idu);
    
    with gzip.open(directory + file_geojson_name, 'rb') as f:
        list_geojson = json.load(f);
        
        for parcelle in list_geojson["features"]:
            if(parcelle['properties']['id'] == idu):
                
                parcelle['properties']['parcellaires'] = parcellaire;

                return parcelle;
    
def my_cache_download(directory, file):

    return os.path.isfile(directory + file);

parcellaire = {}

liste_parcellaire = []


numero_cvi = sys.argv[1];
directory = os.path.dirname(os.path.realpath(__file__)) + '/../documents/';
tmp_dir = '/tmp/';
inputfile = get_file_parcellaire(numero_cvi, directory);

if(inputfile != -1):
    with open(directory+inputfile, 'r') as csv_file:

        parcellaires = parse_csv_to_array(csv_file);
        list_geojson_idu = {};
        obj = [];
        list_geojson_idu = {'type': 'FeatureCollection', 'features': obj};
        
        
        outputfile = 'cadastre-' + parcellaires[0]['CVI Operateur'] + '-parcelles.json';
        if(not os.path.isfile(directory + outputfile)):
            open(directory + outputfile, 'a').close();

        with open(directory + outputfile, 'w') as outfile:
            for parcellaire in parcellaires:
                
                geojson = get_geoJson_parcelle(tmp_dir, parcellaire);
                if(geojson):
                    obj.append(geojson);
            if(bool(list_geojson_idu['features'])):
                json.dump(list_geojson_idu, outfile);
            else:
                os.remove(directory + outputfile);

