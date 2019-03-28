# -*- coding: utf-8 -*-

""" Parse le site des douanes pour l'extraction des parcellaires """

import os

import scrapy
from scrapy.exporters import JsonItemExporter
from prodouane.items import CviItem, ExploitationItem, ExploitantItem
from prodouane.items import ParcellaireItem


class ParcellaireSpider(scrapy.Spider):
    """ Spider pour les parcellaires """

    custom_settings = {'COOKIES_DEBUG': True, 'DUPEFILTER_DEBUG': True,
                       'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter'}

    name = 'parcellaire'
    domain = 'https://pro.douane.gouv.fr/'
    url_login = 'https://pro.douane.gouv.fr/WDsession.asp'
    url_menu = 'https://pro.douane.gouv.fr/wdactuapplif.asp?wdAppli=118'
    url_appli = 'https://pro.douane.gouv.fr/wdroute.asp?btn=118&rap=3&cat=3'
    url_cvi = 'https://pro.douane.gouv.fr/ncvi_intervenant/prodouane/' \
        'portailNcviProdouane?sid=%s&app=118&code_teleservice=PORTAIL_VITI'
    url_connexion_prodouane = 'https://pro.douane.gouv.fr/ncvi_foncier/' \
        'prodouane/connexionProdouane?direct=fdc&sid=%s&app=118'

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

        departements = response.css(
            r'#formFdc\:selectDepartement option::attr(value)').getall()

        communes = response.css(
            r'#formFdc\:selectCommune option::attr(value)').getall()

        selected_commune = response.css(
            r'#formFdc\:selectCommune option[selected]::attr(value)').get()

        return scrapy.FormRequest.from_response(
            response,
            formname='formFdc',
            callback=self.get_total_page,
            meta={'commune': str(selected_commune)}
        )

    def get_total_page(self, response):
        """ Récupère le nombre de page de la commune """
        total_pages = len(response.css(r'#formFdc\:dttListeEvvOA\:scrollerId '
                                       '.rf-ds-nmb-btn').getall())
        for page in range(1, total_pages+1):
            response_copy = response.copy()
            yield scrapy.FormRequest.from_response(
                response_copy,
                formname='formFdc',
                formdata={'javax.faces.source':
                          'formFdc:dttListeEvvOA:scrollerId',
                          'javax.faces.partial.event':
                          'rich:datascroller:onscroll',
                          'javax.faces.partial.execute':
                          'formFdc:dttListeEvvOA:scrollerId @component',
                          'javax.faces.partial.render': '@component',
                          'formFdc:dttListeEvvOA:scrollerId:page': str(page),
                          'org.richfaces.ajax.component':
                          'formFdc:dttListeEvvOA:scrollerId',
                          'formFdc:dttListeEvvOA:scrollerId':
                          'formFdc:dttListeEvvOA:scrollerId',
                          'AJAX:EVENTS_COUNT': '1',
                          'rfExt': 'null',
                          },
                callback=self.get_liste_cvi,
                meta={'page': str(page), 'commune': response.meta['commune']}
            )

    def get_liste_cvi(self, response):
        """ Récupère le nombre de CVI sur la page """
        self.export_html(response.meta['commune'] + '-page-' +
                         response.meta['page'], 'list', response.text)
        numero_cvi = response.css(
            r'table#formFdc\:dttListeEvvOA td[id$=j_idt231]::text').get()

        cvi = CviItem()
        cvi['cvi'] = numero_cvi
        cvi['libelle'] = (
            response.css(
                r'table#formFdc\:dttListeEvvOA td[id$=j_idt233]::text'
            ).get()
        )
        cvi['commune'] = response.meta['commune']
        cvi['categorie'] = response.css(
            r'table#formFdc\:dttListeEvvOA td[id$=j_idt235]::text').get()
        cvi['activite'] = response.css(
            r'table#formFdc\:dttListeEvvOA td[id$=j_idt237]::text').get()

        yield scrapy.FormRequest.from_response(
            response,
            formname='formFdc',
            formdata={'formFdc:dttListeEvvOA:0:j_idt242':
                      'formFdc:dttListeEvvOA:0:j_idt242'},
            callback=self.fiche_accueil,
            meta={'cvi': cvi}
        )

    def fiche_accueil(self, response):
        """ Parse la page d'accueil de la fiche CVI """
        table_exploitation = response.css(
            r'div[id=formFdcConsultation\:j_idt172\:j_idt173] table tr '
            'td.fdcCoordonneCol2')

        exploitation = ExploitationItem()
        exploitation['cvi'] = table_exploitation[0].css('::text').get()
        exploitation['siret'] = table_exploitation[1].css('::text').get()
        exploitation['nom'] = table_exploitation[2].css('::text').get().strip()
        exploitation['categorie'] = table_exploitation[3].css('::text').get()
        exploitation['type'] = table_exploitation[4].css('::text').get()
        exploitation['commune'] = table_exploitation[5].css('::text').get()
        exploitation['date_debut'] = table_exploitation[6].css('::text').get()
        exploitation['statut'] = table_exploitation[7].css('::text').get()

        table_exploitant = response.css(
            r'div[id=formFdcConsultation\:j_idt172\:j_idt173]'
            ' table:nth-child(2) td.fdcCoordonneCol2')

        exploitant = ExploitantItem()
        exploitant['cvi'] = table_exploitant[0].css('::text').get()
        exploitant['siren'] = table_exploitant[1].css('::text').get()
        exploitant['civilite'] = table_exploitant[2].css('::text').get()
        exploitant['nom'] = table_exploitant[3].css('::text').get()
        exploitant['prenom'] = table_exploitant[4].css('::text').get()
        exploitant['statut_juridique'] = \
            table_exploitant[5].css('::text').get()
        exploitant['date_naissance'] = table_exploitant[6].css('::text').get()
        exploitant['adresse'] = table_exploitant[7].css('::text').get()
        exploitant['cp'] = table_exploitant[8].css('::text').get()
        exploitant['tel'] = table_exploitant[9].css('::text').get()
        exploitant['qualite'] = table_exploitant[10].css('::text').get()
        exploitant['email'] = table_exploitant[11].css('::text').get()
        exploitant['last_updated'] = table_exploitant[12].css('::text').get()

        cvi = response.meta['cvi']
        cvi['exploitation'] = exploitation
        cvi['exploitant'] = exploitant

        tables = response.css(
            r'div[id=formFdcConsultation\:j_idt172\:j_idt173] table'
        ).getall()
        self.export_html(cvi['cvi'], 'accueil', tables[0:2])

        file = open('/tmp/%s.json' % cvi['cvi'], 'a')
        try:
            JsonItemExporter(file).export_item(cvi)
        finally:
            file.close()

        return scrapy.FormRequest.from_response(
            response,
            formname='formFdcConsultation',
            formdata={'javax.faces.partial.ajax': 'true',
                      'javax.faces.source': 'formFdcConsultation:j_idt172',
                      'javax.faces.partial.execute':
                      'formFdcConsultation:j_idt172',
                      'javax.faces.partial.render':
                      '+formFdcConsultation:j_idt172',
                      'javax.faces.behavior.event': 'tabChange',
                      'javax.faces.partial.event': 'tabChange',
                      'formFdcConsultation:j_idt172_contentLoad': 'true',
                      'formFdcConsultation:j_idt172_newTab':
                      'formFdcConsultation:j_idt172:j_idt457',
                      'formFdcConsultation:j_idt172_tabindex': '3',
                      'formFdcConsultation:j_idt172_activeIndex': '3'},
            callback=self.fiche_parcellaire_plante,
            meta={'cvi': cvi},
        )

    def fiche_parcellaire_plante(self, response):
        """ Parse l'onglet parcellaire planté """
        cvi = response.meta['cvi']
        return scrapy.Request(response.url, meta={'cvi': cvi})

    def parse(self, response):
        """ Méthode par défaut de parsage de page """
        cvi = response.meta['cvi']
        self.export_html(cvi['cvi'], 'parcellaire',
                         response.text)

    @staticmethod
    def export_html(cvi, name, contents):
        """ Permet de sauvegarder le HTML en cas de coupure """
        file = open('/tmp/%s-%s.html' % (cvi, name), 'w')
        try:
            for content in contents:
                file.write(content.encode('utf-8'))
        finally:
            file.close()
