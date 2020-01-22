#! /usr/bin/python
# -*- coding: utf-8 -*-
import sys,os,wget,gzip

from zipfile import ZipFile

from itertools import islice

def my_cache_download(directory, file):

    return os.path.isfile(directory + file);

directory = os.path.dirname(os.path.realpath(__file__)) + '/../documents/';

tmp_dir = '/tmp/';

url = "https://www.data.gouv.fr/fr/datasets/r/ad6e471e-8b53-4151-b37e-7ce5a8fe868f";

outputfile = "delimitation_parcellaire_aoc_viticoles.zip";

file_name = "delimitation_parcellaire_aoc_viticoles.json";

if(not my_cache_download(tmp_dir, file_name)):
	
	wget.download(url, tmp_dir + outputfile);


with ZipFile(tmp_dir + outputfile, 'r') as fs:
	fs.extractall(tmp_dir);

	with open(tmp_dir + file_name, "r") as f:

		data = "";
		header = '{"type": "FeatureCollection","name": "provence_geojson","crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:EPSG::2154" } },"features": [{';
		footer = "]}"
		substr = '"new_insee" : "';
		for line in islice(f,4, None):

			line = line.replace('\n', '');
			line = line.replace('\r', '');
			line = line.replace('\t', '');

			if((data[-2:] == "}," and line == "{") or(data[-2:] == "}" and line == "]")):

				commune = data[(data.find(substr)+len(substr)):(data.find(substr)+len(substr)+5)];
				outputfile = 'delimitation-' + commune + '.json';

				with open(directory + outputfile, 'w') as outfile:

					if(data[-2:] == "},"):

						data = data[:-1];
					outfile.write(header + data + footer);
				data = "";
			else:

				data = data + line;

os.remove(tmp_dir + file_name);