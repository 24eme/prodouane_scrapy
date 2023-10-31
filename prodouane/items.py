# -*- coding: utf-8 -*-

"""
Objets extraits de pro.douane.gouv.fr
"""

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ExploitationItem(scrapy.Item):
    nom = scrapy.Field()
    cvi = scrapy.Field()
    siret = scrapy.Field()
    categorie = scrapy.Field()
    type = scrapy.Field()
    commune = scrapy.Field()
    date_debut = scrapy.Field()
    statut = scrapy.Field()

class ExploitantItem(scrapy.Item):
    cvi = scrapy.Field()
    siren = scrapy.Field()
    civilite = scrapy.Field()
    nom = scrapy.Field()
    prenom = scrapy.Field()
    statut_juridique = scrapy.Field()
    date_naissance = scrapy.Field()
    adresse = scrapy.Field()
    cp = scrapy.Field()
    tel = scrapy.Field()
    qualite = scrapy.Field()
    email = scrapy.Field()
    last_updated = scrapy.Field()

class ParcellaireItem(scrapy.Item):
    commune = scrapy.Field()
    lieu_dit = scrapy.Field()
    reference_cadastrale = scrapy.Field()
    produit_revendique = scrapy.Field()
    cepage = scrapy.Field()
    superficie = scrapy.Field()
    campagne = scrapy.Field()
    porte_greffe = scrapy.Field()
    ecart_pied = scrapy.Field()
    ecart_rang = scrapy.Field()
    etat = scrapy.Field()
    mode_faire_valoir = scrapy.Field()
    total = scrapy.Field()

class CviItem(scrapy.Item):
    cvi = scrapy.Field()
    libelle = scrapy.Field()
    commune = scrapy.Field()
    departement = scrapy.Field()
    categorie = scrapy.Field()
    activite = scrapy.Field()
    exploitation = scrapy.Field()
    exploitant = scrapy.Field()
    parcellaire = scrapy.Field()
