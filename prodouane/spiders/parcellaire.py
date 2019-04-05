# -*- coding: utf-8 -*-

""" Parse le site des douanes pour l'extraction des parcellaires """

import os
import re

import scrapy
from prodouane.items import CviItem


class ParcellaireSpider(scrapy.Spider):
    """ Spider pour les parcellaires """

    custom_settings = {'COOKIES_DEBUG': True, 'DUPEFILTER_DEBUG': True,
                       'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
                       'CONCURRENT_REQUESTS': 1}

    name = 'parcellaire'
    domain = 'https://pro.douane.gouv.fr/'
    url_login = 'https://pro.douane.gouv.fr/WDsession.asp'
    url_menu = 'https://pro.douane.gouv.fr/wdactuapplif.asp?wdAppli=118'
    url_appli = 'https://pro.douane.gouv.fr/wdroute.asp?btn=118&rap=3&cat=3'
    url_cvi = 'https://pro.douane.gouv.fr/ncvi_intervenant/prodouane/' \
        'portailNcviProdouane?sid=%s&app=118&code_teleservice=PORTAIL_VITI'
    url_connexion_prodouane = 'https://pro.douane.gouv.fr/ncvi_foncier/' \
        'prodouane/connexionProdouane?direct=fdc&sid=%s&app=118'
    url_accueil = 'https://pro.douane.gouv.fr/ncvi_foncier/prodouane/pages/' \
        'fdc/accueil.xhtml'
    url_consultation = 'https://pro.douane.gouv.fr/ncvi_foncier/prodouane/' \
        'pages/fdc/consultation.xhtml'

    starter = {'departement': 0, 'commune': 0, 'page': 1, 'index_cvi': 0}

    storage_directory = './documents/'

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
        """ On se re-connecte (?) à prodouane avec notre sid et on GET la
        page d'accueil de la liste des CVI en initialisant les compteurs de
        communes / départements """
        return scrapy.Request(
            url=self.url_connexion_prodouane % response.meta['sid'],
            callback=self.accueil_fdc,
            meta=self.starter)

    def accueil_fdc(self, response):
        """ Page d'accueil où l'on récupère les départements et les communes
        autorisés
        Si un CVI est passé en variable d'environnement, on télécharge les
        informations, sinon, on liste la liste des CVI par départements et par
        communes
        """
        meta = response.meta

        if os.getenv('CVI', None) is None:
            meta['departements'] = response.css(
                r'#formFdc\:selectDepartement option::attr(value)').getall()
            meta['nb_departements'] = len(meta['departements'])

            meta['communes'] = response.css(
                r'#formFdc\:selectCommune option::attr(value)').getall()
            meta['nb_communes'] = len(meta['communes'])

            if meta['commune'] is meta['nb_communes']:
                meta['commune'] = 0
                meta['departement'] = meta['departement'] + 1

                if meta['departement'] is meta['nb_departements']:
                    return False

                return scrapy.FormRequest.from_response(
                    response, formname='formFdc',
                    callback=self.update_communes,
                    meta=meta,
                    formdata={
                        'formFdc:selectDepartement':
                            meta['departements'][meta['departement']],
                        'javax.faces.source': 'formFdc:selectDepartement',
                        'javax.faces.partial.event': 'change',
                        'javax.faces.partial.execute':
                            'formFdc:selectDepartement @component',
                        'javax.faces.partial.render': '@component',
                        'javax.faces.behavior.event': 'change',
                        'org.richfaces.ajax.component':
                            'formFdc:selectDepartement',
                        'rfExt': 'null',
                        'AJAX:EVENTS_COUNT': '1',
                        'javax.faces.partial.ajax': 'true'
                    }
                )

            meta['noms_communes'] = response.css(
                r'#formFdc\:selectCommune option::text').getall()
            meta['nom_commune'] = \
                meta['noms_communes'][meta['commune']]

            return scrapy.FormRequest.from_response(
                response,
                formname='formFdc',
                formdata={
                    'formFdc:selectDepartement':
                    meta['departements'][meta['departement']],
                    'formFdc:selectCommune':
                        meta['communes'][meta['commune']]
                    },
                callback=self.get_total_page,
                meta=meta
            )
        else:
            cvi = os.getenv('CVI')
            meta['numero_cvi'] = cvi
            return scrapy.FormRequest.from_response(
                response,
                formname='formFdc',
                formdata={'formFdc:inputNumeroCvi': cvi},
                callback=self.get_un_cvi,
                meta=meta
            )

    def update_communes(self, response):
        """ Mise à jour des communes en fonction du département
        Fonction appellée lorsque la dernière commune d'un département est
        finie
        """
        return scrapy.Request(self.url_accueil, callback=self.accueil_fdc,
                              meta=response.meta)

    def get_total_page(self, response):
        """ Récupère le nombre de page de la commune, et on requetes chacune
        d'elle pour avoir la liste de CVI
        Si on arrive à la dernière page, on change de commune """
        response.meta['total_pages'] = len(response.css(
            r'#formFdc\:dttListeEvvOA\:scrollerId '
            '.rf-ds-nmb-btn').getall())

        if response.meta['total_pages'] == 0:
            response.meta['total_pages'] = 1

        if response.meta['page'] > response.meta['total_pages']:
            response.meta['page'] = 1
            response.meta['commune'] = response.meta['commune'] + 1
            return scrapy.FormRequest.from_response(
                response,
                formname='formFdc',
                callback=self.accueil_fdc,
                meta=response.meta
            )

        return scrapy.FormRequest.from_response(
            response,
            formname='formFdc',
            formdata={'javax.faces.source':
                      'formFdc:dttListeEvvOA:scrollerId',
                      'javax.faces.partial.event':
                          'rich:datascroller:onscroll',
                      'javax.faces.partial.execute':
                          'formFdc:dttListeEvvOA:scrollerId @component',
                      'javax.faces.partial.render': '@component',
                      'formFdc:dttListeEvvOA:scrollerId:page':
                          str(response.meta['page']),
                      'org.richfaces.ajax.component':
                          'formFdc:dttListeEvvOA:scrollerId',
                      'formFdc:dttListeEvvOA:scrollerId':
                          'formFdc:dttListeEvvOA:scrollerId',
                      'AJAX:EVENTS_COUNT': '1',
                      'rfExt': 'null',
                      },
            callback=self.get_liste_cvi,
            meta=response.meta
        )

    def get_liste_cvi(self, response):
        """ Récupère le nombre de CVI sur la page et on affiche sur STDIN
        les CVI un par un et on incremente la page
        """
        numeros_cvi = re.findall(r'(\d+)</td>', response.text)

        for numero_cvi in numeros_cvi:
            print(numero_cvi)

        response.meta['page'] = response.meta['page'] + 1

        return scrapy.Request(self.url_accueil, meta=response.meta,
                              callback=self.get_total_page)

    def get_un_cvi(self, response):
        """ On sélectionne le CVI recherché """
        cvi = CviItem()
        cvi['cvi'] = response.meta['numero_cvi']
        cvi['libelle'] = response.css('td[id$=j_idt233]::text').get()
        cvi['commune'] = response.css('td[id$=j_idt235]::text').get()
        cvi['categorie'] = response.css(
            'td[id$=j_idt237]::text').get()
        cvi['activite'] = response.css(
            'td[id$=j_idt239]::text').get()

        response.meta['cvi'] = cvi

        return scrapy.FormRequest.from_response(
            response,
            formname='formFdc',
            formdata={'formFdc:dttListeEvvOA:0:j_idt242':
                      'formFdc:dttListeEvvOA:0:j_idt242'},
            callback=self.fiche_accueil,
            meta=response.meta
        )

    def fiche_accueil(self, response):
        """ Parse la page d'accueil de la fiche CVI et on clique sur l'onglet
        des parcellaires """
        cvi = response.meta['cvi']
        identifiant = '-'.join(['parcellaire', cvi['cvi']])
        response.meta['identifiant'] = identifiant

        self.export_html(self.storage_directory, identifiant + '-accueil',
                         response.text)

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
            meta=response.meta
        )

    def fiche_parcellaire_plante(self, response):
        """ Une fois que les données parcellaires sont en session, on
        recharge la page de consultation """
        return scrapy.Request(self.url_consultation, meta=response.meta)

    def parse(self, response):
        """ On récupère les informations de parcellaire """
        self.export_html(self.storage_directory,
                         response.meta['identifiant'] + '-parcellaire',
                         response.text)

    @staticmethod
    def export_html(directory, name, content):
        """ Permet de sauvegarder le HTML en cas de coupure """
        if not os.path.isdir(directory):
            os.makedirs(directory, 0o764)

        file = open(directory + '%s.html' % name, 'w')
        try:
            file.write(content.encode('utf-8'))
        finally:
            file.close()
