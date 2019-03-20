# -*- coding: utf-8 -*-
import scrapy
import os
import time
import random


class ParcellaireSpider(scrapy.Spider):

    custom_settings = { 'COOKIES_DEBUG': True }

    name = 'parcellaire'
    domain = 'https://pro.douane.gouv.fr/'
    url_login = 'https://pro.douane.gouv.fr/WDsession.asp'
    url_menu = 'https://pro.douane.gouv.fr/wdactuapplif.asp?wdAppli=118'
    url_appli = 'https://pro.douane.gouv.fr/wdroute.asp?btn=118&rap=3&cat=3'
    url_cvi = 'https://pro.douane.gouv.fr/ncvi_intervenant/prodouane/portailNcviProdouane?sid=%s&app=118&code_teleservice=PORTAIL_VITI'
    url_connexion_prodouane = 'https://pro.douane.gouv.fr/ncvi_foncier/prodouane/connexionProdouane?direct=fdc&sid=%s&app=118'
    url = 'https://pro.douane.gouv.fr/ncvi_foncier/prodouane/pages/fdc/accueil.xhtml'

    communes = {}

    def start_requests(self):
        return [scrapy.Request(url = self.domain, callback = self.login)]

    def login(self, response):
        return scrapy.FormRequest(
            url = self.url_login,
            formdata = {
                "login": os.environ['PRODOUANE_USER'],
                "pass": os.environ['PRODOUANE_PASS']
            },
            callback = self.menu
        )

    def menu(self, response):
        return scrapy.Request(url = self.url_menu, callback = self.appli)

    def appli(self, response):
        return scrapy.Request(url = self.url_appli, callback = self.choix_cvi)

    def choix_cvi(self, response):
        self.log('Extraction du sid')
        sid = response.css('#wdformAppli input[name=sessionidT]').attrib['value']

        self.log('Valeur trouvée : %s' % sid)
        self.log('Requete vers: %s' % self.url_cvi)

        return scrapy.Request(url = self.url_cvi % sid, callback = self.connexion_prodouane, meta = {'sid': sid})

    def connexion_prodouane(self, response):
        return scrapy.Request(url = self.url_connexion_prodouane % response.meta['sid'], callback = self.accueil_fdc)

    def accueil_fdc(self, response):
        data = {
            'javax.faces.source': 'formFdc:selectDepartement',
            'javax.faces.partial.event': 'change',
            'javax.faces.partial.execute': 'formFdc:selectDepartement @component',
            'javax.faces.partial.render': '@component',
            'javax.faces.behavior.event': 'change',
            'org.richfaces.ajax.component': 'formFdc:selectDepartement',
            'rfExt': 'null',
            'AJAX:EVENTS_COUNT': '1',
            'javax.faces.partial.ajax': 'true'
        }

        departements = response.css('#formFdc\:selectDepartement option::attr(value)').getall()
        r = response.copy()

        for i in departements:
            data.update({'formFdc:selectDepartement': i})

            yield scrapy.FormRequest.from_response(
                r,
                formname = 'formFdc',
                formdata = data,
                callback = self.get_communes_by_departement,
                meta = {'departement': i}
            )

    def get_communes_by_departement(self, response):
        time.sleep(random.randint(1,5))
        self.communes.update(
            {response.meta['departement']: response.css('update#formFdc\:selectCommune').re(r'value="(\d+)"')})
        print self.communes

    def parse(self, response):
        print response.body
        return None

