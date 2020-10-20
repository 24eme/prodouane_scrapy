# -*- coding: utf-8 -*-

""" Parse le site des douanes pour l'extraction des parcellaires """

import scrapy
import os
import re

from prodouane.items import CviItem

class ParcellaireSpider(scrapy.Spider):
    """ Spider pour les parcellaires """
    name = 'parcellaire'

    custom_settings = {'COOKIES_DEBUG': True, 'DUPEFILTER_DEBUG': True,
                       'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
                       'CONCURRENT_REQUESTS': 1}

    starter = {'departement': 0, 'commune': 0, 'page': 1, 'index_cvi': 0}

    storage_directory = './documents/'

    def start_requests(self):
        return [scrapy.Request(url='https://www.douane.gouv.fr/', callback=self.prelogin)]

    def prelogin(self, response):
        yield scrapy.Request(url="https://www.douane.gouv.fr/saml_login", callback=self.login)

    def login(self, response):
        formdata={"user":os.environ['PRODOUANE_USER'],"password":os.environ['PRODOUANE_PASS']}
        formdata['token'] = response.xpath('//*[@name="token"]/@value')[0].extract()
        formdata['url'] = response.xpath('//*[@name="url"]/@value')[0].extract()
        yield scrapy.FormRequest.from_response(response, formdata=formdata, callback=self.postlogin)

    def postlogin(self, response):
        self.log('postlogin')
        if os.getenv('PRODOUANE_DEBUG', None):
            with open("debug/parcellaire-0010_postlogin.html", 'wb') as f:
                f.write(response.body)
        action = response.xpath('//*[@id="form"]/@action')[0].extract()
        formdata={}
        formdata['RelayState'] = response.xpath('//*[@name="RelayState"]/@value')[0].extract()
        formdata['SAMLResponse'] = response.xpath('//*[@name="SAMLResponse"]/@value')[0].extract()
        yield scrapy.FormRequest(url=action, formdata=formdata, callback=self.redirectsaml, dont_filter = True)

    def redirectsaml(self, response):
        self.log('redirectsaml')
        if os.getenv('PRODOUANE_DEBUG', None):
            with open("debug/parcellaire-0020_redirectsaml.html", 'wb') as f:
                f.write(response.body)
        yield scrapy.Request(url='https://www.douane.gouv.fr/service-en-ligne/redirection/PORTAIL_VITI',  callback=self.multiservice)

    def multiservice(self, response):
        self.log('multiservice')
        if os.getenv('PRODOUANE_DEBUG', None):
            with open("debug/parcellaire-0030_multiservice.html", 'wb') as f:
                f.write(response.body)

        sid = ''
        for redir in response.request.meta.get('redirect_urls'):
            if re.search('sid=', redir):
                sid = re.sub(r'&.*', '', re.sub(r'.*sid=', '', redir))
                break

        self.starter['sid'] = sid

        yield scrapy.Request(url='https://www.douane.gouv.fr/ncvi-web-intervenant-prodouane/portailNcviProdouane?sid=%s&app=118&code_teleservice=PORTAIL_VITI' % sid, callback=self.accueil_intervenant, meta=self.starter)

    def accueil_intervenant(self, response):
        yield scrapy.Request(url='https://www.douane.gouv.fr/ncvi-web-foncier-prodouane/connexionProdouane?direct=fdc&sid=%s&app=118' % response.meta['sid'], callback=self.accueil_fdc, meta=response.meta)


    def accueil_fdc(self, response):
        """ Page d'accueil où l'on récupère les départements et les communes
        autorisés
        Si un CVI est passé en variable d'environnement, on télécharge les
        informations, sinon, on liste la liste des CVI par départements et par
        communes
        """

        self.log('accueil_fdc')
        if os.getenv('PRODOUANE_DEBUG', None):
            with open("debug/parcellaire-0040_accueil_fdc.html", 'wb') as f:
                f.write(response.body)

        meta = response.meta

        if os.getenv('CVI', None):
            cvi = os.getenv('CVI')
            meta['numero_cvi'] = cvi
            return scrapy.FormRequest.from_response(
                response,
                formname='formFdc',
                formdata={'formFdc:inputNumeroCvi': cvi},
                callback=self.get_un_cvi,
                meta=meta
            )

        meta['departements'] = response.css('#formFdc\:selectDepartement')[0].css('option::attr(value)').extract()
        meta['nb_departements'] = len(meta['departements'])
        meta['communes'] = response.css('#formFdc\:selectCommune')[0].css('option::attr(value)').extract()
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

        meta['noms_communes'] = response.css('#formFdc\:selectCommune')[0].css('option::attr(value)').extract()
        meta['nom_commune'] = meta['noms_communes'][meta['commune']]

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

    def update_communes(self, response):
        """ Mise à jour des communes en fonction du département
        Fonction appellée lorsque la dernière commune d'un département est
        finie
        """

        self.log('update_communes')
        if os.getenv('PRODOUANE_DEBUG', None):
            with open("debug/parcellaire-0050_update_communes.html", 'wb') as f:
                f.write(response.body)

        return scrapy.Request('https://www.douane.gouv.fr/ncvi-web-foncier-prodouane/pages/fdc/accueil.xhtml', callback=self.accueil_fdc,
                              meta=response.meta)

    def get_total_page(self, response):
        """ Récupère le nombre de page de la commune, et on requetes chacune
        d'elle pour avoir la liste de CVI
        Si on arrive à la dernière page, on change de commune """

        self.log('get_total_page')
        if os.getenv('PRODOUANE_DEBUG', None):
            with open("debug/parcellaire-0060_get_total_page.html", 'wb') as f:
                f.write(response.body)

        response.meta['total_pages'] = len(response.css('#formFdc\:dttListeEvvOA\:scrollerId')[0].css('.rf-ds-nmb-btn').extract())
        if response.meta['total_pages'] == 0:
            response.meta['total_pages'] = 1

        self.log('total_pages %s' % response.meta['total_pages'])

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

        self.log('get_liste_cvi')
        if os.getenv('PRODOUANE_DEBUG', None):
            with open("debug/parcellaire-0070_get_liste_cvi.html", 'wb') as f:
                f.write(response.body)

        numeros_cvi = re.findall(r'(\d+)</td>', response.body)

        for numero_cvi in numeros_cvi:
            print(numero_cvi)

        response.meta['page'] = response.meta['page'] + 1

        return scrapy.Request('https://www.douane.gouv.fr/ncvi-web-foncier-prodouane/pages/fdc/accueil.xhtml', meta=response.meta,
                              callback=self.get_total_page, dont_filter = True)

    def get_un_cvi(self, response):
        """ On sélectionne le CVI recherché """

        self.log('get_un_cvi')
        if os.getenv('PRODOUANE_DEBUG', None):
            with open("debug/parcellaire-0080_get_un_cvi.html", 'wb') as f:
                f.write(response.body)

        cssid = int(response.css('td.fdcAccueilEvvColCode').xpath('@id').re_first(r'.*_idt([0-9]*)'))

        cvi = CviItem()
        cvi['cvi'] = response.meta['numero_cvi']
        cvi['libelle']   = response.css('td[id$=j_idt' + str(cssid + 2) +']::text').extract()
        cvi['commune']   = response.css('td[id$=j_idt' + str(cssid + 4) +']::text').extract()
        cvi['categorie'] = response.css('td[id$=j_idt' + str(cssid + 6) +']::text').extract()
        cvi['activite']  = response.css('td[id$=j_idt' + str(cssid + 8) +']::text').extract()

        self.log(cvi)

        response.meta['cvi'] = cvi

        args={}
        args['formFdc']='formFdc'
        args['formFdc:inputNumeroCvi']=cvi['cvi']
        args['javax.faces.ViewState']=response.xpath('//*[@name="javax.faces.ViewState"]/@value')[0].extract()
        args['formFdc:dttListeEvvOA:0:j_idt' + str(cssid + 11)]='formFdc:dttListeEvvOA:0:j_idt' + str(cssid + 11)

        self.log(args)
        return scrapy.FormRequest(url='https://www.douane.gouv.fr/ncvi-web-foncier-prodouane/pages/fdc/accueil.xhtml', formdata=args,
                                 callback=self.fiche_accueil, meta=response.meta)

    def fiche_accueil(self, response):
        """ Parse la page d'accueil de la fiche CVI et on clique sur l'onglet
        des parcellaires """

        self.log('fiche_accueil')
        if os.getenv('PRODOUANE_DEBUG', None):
            with open("debug/parcellaire-0090_fiche_accueil.html", 'wb') as f:
                f.write(response.body)

        cvi = response.meta['cvi']
        identifiant = '-'.join(['parcellaire', cvi['cvi']])
        response.meta['identifiant'] = identifiant

        self.export_html(self.storage_directory, identifiant + '-accueil',
                         response.body)

        return scrapy.FormRequest.from_response(
            response,
            formname='formFdcConsultation',
            formdata={'javax.faces.partial.ajax': 'true',
                      'javax.faces.source': 'formFdcConsultation:j_idt174',
                      'javax.faces.partial.execute':
                          'formFdcConsultation:j_idt174',
                      'javax.faces.partial.render':
                          '+formFdcConsultation:j_idt174',
                      'javax.faces.behavior.event': 'tabChange',
                      'javax.faces.partial.event': 'tabChange',
                      'formFdcConsultation:j_idt174_contentLoad': 'true',
                      'formFdcConsultation:j_idt174_newTab':
                          'formFdcConsultation:j_idt174:j_idt459',
                      'formFdcConsultation:j_idt174_tabindex': '3',
                      'formFdcConsultation:j_idt174_activeIndex': '3'},
            callback=self.fiche_parcellaire_plante,
            meta=response.meta
        )

    def fiche_parcellaire_plante(self, response):
        """ Une fois que les données parcellaires sont en session, on
        recharge la page de consultation """

        self.log('fiche_parcellaire_plante')
        if os.getenv('PRODOUANE_DEBUG', None):
            with open("debug/parcellaire-0100_fiche_parcellaire_plante.html", 'wb') as f:
                f.write(response.body)

        return scrapy.Request('https://www.douane.gouv.fr/ncvi-web-foncier-prodouane/pages/fdc/consultation.xhtml', meta=response.meta)

    def parse(self, response):
        """ On récupère les informations de parcellaire """

        self.log('parse')

        self.export_html(self.storage_directory,
                         response.meta['identifiant'] + '-parcellaire',
                         response.body)

    @staticmethod
    def export_html(directory, name, content):
        """ Permet de sauvegarder le HTML en cas de coupure """

        if not os.path.isdir(directory):
            os.makedirs(directory, 0o764)

        file = open(directory + '%s.html' % name, 'wb')
        try:
            file.write(content)
        finally:
            file.close()
