# -*- coding: utf-8 -*-

""" Parse le site des douanes pour l'extraction des parcellaires """

import os
import time
import random
import scrapy


class ParcellaireSpider(scrapy.Spider):
    """ Spider pour les parcellaires """

    custom_settings = {'COOKIES_DEBUG': True}

    name = 'parcellaire'
    domain = 'https://pro.douane.gouv.fr/'
    url_login = 'https://pro.douane.gouv.fr/WDsession.asp'
    url_menu = 'https://pro.douane.gouv.fr/wdactuapplif.asp?wdAppli=118'
    url_appli = 'https://pro.douane.gouv.fr/wdroute.asp?btn=118&rap=3&cat=3'
    url_cvi = 'https://pro.douane.gouv.fr/ncvi_intervenant/prodouane/' \
        'portailNcviProdouane?sid=%s&app=118&code_teleservice=PORTAIL_VITI'
    url_connexion_prodouane = 'https://pro.douane.gouv.fr/ncvi_foncier/' \
        'prodouane/connexionProdouane?direct=fdc&sid=%s&app=118'
    url = 'https://pro.douane.gouv.fr/ncvi_foncier/' \
        'prodouane/pages/fdc/accueil.xhtml'

    communes = {}

    def start_requests(self):
        """ Requête appellée en premier pour le scraping """
        return [scrapy.Request(url=self.domain, callback=self.login)]

    def login(self, response):
        """ Envoi des informations de session pour se loguer """
        return scrapy.FormRequest(
            url=self.url_login,
            formdata={
                "login": os.environ['PRODOUANE_USER'],
                "pass": os.environ['PRODOUANE_PASS']
            },
            callback=self.menu
        )

    def menu(self, response):
        """ On clique sur le bouton pour acceder au portail viticole """
        return scrapy.Request(url=self.url_menu, callback=self.appli)

    def appli(self, response):
        """ On clique sur le bouton « Entrer » du portail """
        return scrapy.Request(url=self.url_appli, callback=self.get_sid)

    def get_sid(self, response):
        """ On récupère le sid """
        self.log('Extraction du sid')
        sid = response.css(
            '#wdformAppli input[name=sessionidT]'
        ).attrib['value']

        self.log('Valeur trouvée : %s' % sid)
        self.log('Requete vers: %s' % self.url_cvi)

        return scrapy.Request(
            url=self.url_cvi % sid,
            callback=self.connexion_prodouane, meta={'sid': sid}
        )

    def connexion_prodouane(self, response):
        """ On se re-connecte (?) à prodouane avec notre sid """
        return scrapy.Request(
            url=self.url_connexion_prodouane % response.meta['sid'],
            callback=self.accueil_fdc)

    def accueil_fdc(self, response):
        """ Page d'accueil où l'on récupère les départements autorisés """

        data = {
            'javax.faces.source': 'formFdc:selectDepartement',
            'javax.faces.partial.event': 'change',
            'javax.faces.partial.execute':
                'formFdc:selectDepartement @component',
            'javax.faces.partial.render': '@component',
            'javax.faces.behavior.event': 'change',
            'org.richfaces.ajax.component': 'formFdc:selectDepartement',
            'rfExt': 'null',
            'AJAX:EVENTS_COUNT': '1',
            'javax.faces.partial.ajax': 'true'
        }

        departements = response.css(
            u'#formFdc:selectDepartement option::attr(value)').getall()

        initial_response = response.copy()

        for i in departements:
            data.update({'formFdc:selectDepartement': i})

            yield scrapy.FormRequest.from_response(
                initial_response,
                formname='formFdc',
                formdata=data,
                callback=self.get_communes_by_departement,
                meta={'departement': i}
            )

    def get_communes_by_departement(self, response):
        """ On récupère la liste des communes du département """
        time.sleep(random.randint(1, 5))
        self.communes.update(
            {
                response.meta['departement']:
                    response.css(
                        u'update#formFdc:selectCommune'
                    ).re(r'value="(\d+)"')
            }
        )
        print(self.communes)

    def parse(self, response):
        """ Méthode par défaut de parsage de page """
        print(response.body)
        return None
