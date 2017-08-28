#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import csv
import sys
import re

annee_recolte = sys.argv[2];

print "type de document;campagne;cvi;raison_sociale;libelle produit;code_douane;numéro de la colonne produit;type_ligne;numero_ligne;volume ou superficie"

with open(sys.argv[1], 'rb') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    rows = list(reader)
    cvi = rows[1][1].strip(" ")
    raison_sociale = rows[1][2].strip(" ")
    raison_sociale = re.sub("[ ]+", " ", raison_sociale)

    produits = []
    for row in rows:
        if len(row) < 2:
            continue

        if row[1].strip(" ") != "Libelle produit" and row[1].strip(" ") != "Code produit":
            continue
        for i in range(3, len(row)-1):
            if i % 2 == 0:
                continue
            num_produit = i - 3 - ((i-3)/2)

            if len(produits) <= num_produit:
                produits.append([])

            produits[num_produit].extend([row[i].strip(" ")])

    for row in rows:
        if len(row) < 2:
            #print row
            continue

        libelle = row[1].strip(" ")
        num = row[0].strip(" ")

        if libelle == "Libelle produit":
            #print row
            continue
        if num == "DNR":
            #print row
            continue
        if num == "Identification de la déclaration":
            #print row
            continue

        for i in range(3, len(row)-1):
            if i % 2 == 0:
                continue

            volume = row[i]
            if not re.match("^[0-9]+.?[0-9]*$", volume):
                continue
            num_produit = i - 3 - ((i-3)/2)
            produit = produits[num_produit]
            produit_code_douane = produit[0]
            produit_libelle = produit[1]
            print("DR;%s;%s;%s;%s;%s;%s;%s;%s;%s" % (annee_recolte, cvi, raison_sociale, produit_libelle, produit_code_douane, num_produit, libelle, num, volume))
