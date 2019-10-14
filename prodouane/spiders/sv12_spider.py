# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
import os
import re

class QuotesSpider(scrapy.Spider):
    name = "sv12"

#    custom_settings = {
#                       'COOKIES_DEBUG': True,
#                       }

    def start_requests(self):
        yield scrapy.Request(url="https://www.douane.gouv.fr/", callback=self.prelogin)

    def prelogin(self, response):
        yield scrapy.Request(url="https://www.douane.gouv.fr/saml_login", callback=self.login)

    def login(self, response):
        formdata={"user":os.environ['PRODOUANE_USER'],"password":os.environ['PRODOUANE_PASS']}
        formdata['token'] = response.xpath('//*[@name="token"]/@value')[0].extract()
        formdata['url'] = response.xpath('//*[@name="url"]/@value')[0].extract()
        yield scrapy.FormRequest.from_response(response, formdata=formdata, callback=self.postlogin)

    def postlogin(self, response):
        self.log('postlogin')
#        with open("quotes-postlogin.html", 'wb') as f:
#            f.write(response.body)
        action = response.xpath('//*[@id="form"]/@action')[0].extract()
        formdata={}
        formdata['RelayState'] = response.xpath('//*[@name="RelayState"]/@value')[0].extract()
        formdata['SAMLResponse'] = response.xpath('//*[@name="SAMLResponse"]/@value')[0].extract()
        yield scrapy.FormRequest(url=action, formdata=formdata, callback=self.redirectsaml, dont_filter = True)

    def redirectsaml(self, response):
        self.log('redirectsaml')
#        with open("quotes-redirectsaml.html", 'wb') as f:
#            f.write(response.body)
        yield scrapy.Request(url='https://www.douane.gouv.fr/service-en-ligne/redirection/PORTAIL_VITI',  callback=self.multiservice)

    def multiservice(self, response):
        self.log('multiservice')
#        with open("quotes-multiservice.html", 'wb') as f:
#            f.write(response.body)

        sid = ''
        for redir in response.request.meta.get('redirect_urls'):
            if re.search('sid=', redir):
                sid = re.sub(r'&.*', '', re.sub(r'.*sid=', '', redir))
                break

        cvi = ''
        if 'CVI' in os.environ:
            cvi = os.environ['CVI']

        yield scrapy.Request(url='https://www.douane.gouv.fr/ncvi-web-sv12-prodouane/connexionProdouane?sid=%s&app=118' % sid, callback=self.sv12_accueil, meta={'departement': 0, 'commune': 0, 'annee': os.environ['PRODOUANE_ANNEE'], "cvi": cvi, "sid": sid})

    def get_input_args(self, response, cssid):
        args = {}
        for i in (response.css('%s input' % cssid)):
            if (i.xpath('@name') and i.xpath('@value')):
                args[i.xpath('@name')[0].extract()] = i.xpath('@value')[0].extract()
        return args

    def sv12_accueil(self, response):
        self.log('sv12_accueil')
#        with open("quotes-sv12-connexion.html", 'wb') as f:
#            f.write(response.body)

        departements = response.css('#formFiltre tr')[1].css('td')[1].css('option::attr(value)').extract();
        inputs = self.get_input_args(response, '#formFiltre')

        response.meta['javaxViewState'] = inputs['javax.faces.ViewState']
        response.meta['nb_departements']  = len(departements)

        campagnes = {}
        for option in response.css('#formFiltre tr')[0].css('td')[1].css('option'):
            campagnes[option.xpath('text()')[0].extract()] = option.xpath('@value')[0].extract()
        campagne_name = response.css('#formFiltre tr')[0].css('td')[1].css('select::attr(name)')[0].extract();

        departements = response.css('#formFiltre tr')[1].css('td')[1].css('option::attr(value)').extract();
        communes = response.css('#formFiltre tr')[2].css('td')[1].css('option::attr(value)').extract();

        response.meta['departement_selected'] = departements[response.meta['departement']]
        response.meta['campagne_name'] = campagne_name
        response.meta['campagne_selected'] = campagnes["%s-%d" % (response.meta['annee'], int(response.meta['annee']) + 1)]

        args = {}
        args['AJAXREQUEST'] = "_viewRoot"
        args['formFiltre:selectDepartement'] = departements[response.meta['departement']]
        args['formFiltre:selectCommune'] = communes[0]
        args[response.meta['campagne_name']] = response.meta['campagne_selected']
        args['formFiltre_SUBMIT']="1"
        args['javax.faces.ViewState'] = inputs['javax.faces.ViewState']
        args["formFiltre:_idJsp14"] = "formFiltre:_idJsp14"

        yield scrapy.FormRequest(url='https://www.douane.gouv.fr/ncvi-web-sv12-prodouane/jsp/accueilOrganisme.jsf?javax.portlet.faces.DirectLink=true', formdata=args, callback=self.sv12_communes, meta=response.meta)

    def sv12_communes(self, response):
        meta = response.meta
        response = HtmlResponse(url=response.url, body=response.body)
        self.log('sv12_communes')
#       with open("quotes-sv12-commune.html", 'wb') as f:
#          f.write(response.body)

        communes = response.css('option::attr(value)').extract()
        inputs = self.get_input_args(response, '')

        args = {}
        args['formFiltre_SUBMIT']="1"
        args['javax.faces.ViewState'] = inputs['javax.faces.ViewState']
        args[meta['campagne_name']] = meta['campagne_selected']
        args['formFiltre:selectDepartement'] = str(meta['departement_selected'])
        args['formFiltre:selectCommune'] = communes[meta['commune']]
        args['formFiltre:inputNumeroCvi'] = meta['cvi']
        args['formFiltre:_idJsp19'] = "Rechercher"
        args['autoScroll'] = "0,0"
        args['formFiltre:_idcl'] = ""
        args['formFiltre:_link_hidden_'] = ""

        meta['id'] = 0
        meta['page'] = 0
        meta['javaxViewState'] = inputs['javax.faces.ViewState']
        meta['nb_communes']  = len(communes)

        self.log('cvi: %s' % meta['cvi'])
        
        yield scrapy.FormRequest(url='https://www.douane.gouv.fr/ncvi-web-sv12-prodouane/jsp/accueilOrganisme.jsf', formdata=args, callback=self.sv12_page_1, meta=meta)

    def sv12_page_1(self, response):
        self.log('sv12_page_1')
#        with open("quotes-sv12-page1.html", 'wb') as f:
#            f.write(response.body)
        args = self.get_input_args(response, '#formFiltre')
        response.meta['javaxViewState'] = args['javax.faces.ViewState']
        args = {
                'javax.faces.ViewState' : response.meta['javaxViewState'],
                'formDeclaration:_link_hidden_':'',
                'formDeclaration:listeDeclaration:scrollerId': '%d' % (response.meta['page'] + 1),
                'formDeclaration_SUBMIT':"1",
                'autoScroll':"0,0",
                }
        yield scrapy.FormRequest(url='https://www.douane.gouv.fr/ncvi-web-sv12-prodouane/jsp/accueilOrganisme.jsf', formdata=args, callback=self.sv12_tableau_cvi, meta=response.meta)

    def sv12_tableau_cvi(self, response):
        self.log('sv12_tableau_cvi')

#       with open("quotes-sv12.html", 'wb') as f:
#           f.write(response.body)

        info = []
        nb_docs = 0
        if (response.css('.dr-table-headercell')):
            nb_docs = int(response.css('.dr-table-headercell').re(r'\((\d+)\)')[0])

        if (nb_docs):
            for tr in response.css('#formDeclaration tbody tr'):
                if (tr.css('td')[3].css('a::attr(id)')):
                    idhtml = tr.css('td')[3].css('a::attr(id)')[0].extract()
                    cvi = tr.css('td::text')[1].extract()
                    date = 'XXXX'
                    if (len(tr.css('td::text')[2].extract().split('/')) > 1):
                        date = tr.css('td::text')[2].extract().split('/')[2]
                    #telechargement que si CVI specifie
                    self.log("new line : {date: %s, cvi: %s, idhtml: %s}"% (date, cvi, idhtml))
                    info.append({'date': date, 'cvi': cvi, 'idhtml': idhtml})
                    if (not len(response.meta['cvi'])):
                        print("new cvi found : sv12 "+cvi)

        args = self.get_input_args(response, '#formFiltre')

        id = response.meta['id']

        if (not len(response.meta['cvi'])) :
            self.log('id %s : %d (%d)' % ('NO MORE CVI', id, len(info)) )
            if (len(info) == 30) and (nb_docs > (30 * (response.meta['page'] + 1))) :
                response.meta['page'] = response.meta['page'] + 1
                myargs = {
                        'javax.faces.ViewState' : args['javax.faces.ViewState'],
                        'formDeclaration:_link_hidden_':'',
                        'formDeclaration:listeDeclaration:scrollerId': '%d' % (response.meta['page'] + 1),
                        'formDeclaration_SUBMIT':"1",
                        'autoScroll':"0,0",
                        }
                response.meta['id'] = 0
                yield scrapy.FormRequest(url='https://www.douane.gouv.fr/ncvi-web-sv12-prodouane/jsp/accueilOrganisme.jsf', formdata=myargs, callback=self.sv12_tableau_cvi, meta=response.meta)
            else:
                response.meta['page'] = 0
                response.meta['id'] = 0
                response.meta['commune'] = response.meta['commune'] + 1
                if (response.meta['nb_communes'] <= response.meta['commune']):
                    response.meta['departement'] = response.meta['departement'] + 1
                    response.meta['commune'] = 0
                if (response.meta['nb_departements'] > response.meta['departement']):
                    yield scrapy.FormRequest(url='https://www.douane.gouv.fr/ncvi-web-sv12-prodouane/jsp/accueilOrganisme.jsf?commune=%d&dep=%d' % (response.meta['commune'], response.meta['departement']), callback=self.sv12_accueil, meta=response.meta)
        elif (len(info) > id):
            self.log('id %s : %d (%d)' % (info[id]['cvi'], id, len(info)) )
            i = info[id]
            myargs = {
                    'javax.faces.ViewState' : args['javax.faces.ViewState'],
                    'formDeclaration:_link_hidden_':'',
                    'formDeclaration:_idcl': i['idhtml'],
                    'formDeclaration_SUBMIT':"1",
                    'autoScroll':"0,0",
                    }

            response.meta['id'] = id
            response.meta['info'] = info

            yield scrapy.FormRequest(url='https://www.douane.gouv.fr/ncvi-web-sv12-prodouane/jsp/accueilOrganisme.jsf', formdata=myargs, callback=self.sv12_html_sv12, meta=response.meta)
        else:
            self.log('no document found for %s' % response.meta['cvi'])

    def sv12_html_sv12(self, response):
        self.log('sv12_html_sv12')
        filename = 'documents/sv12-%s-%s.html' % (response.meta['annee'], response.meta['info'][response.meta['id']]['cvi'])
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)

        inputs = self.get_input_args(response, '')
        args = {
               'javax.faces.ViewState': inputs['javax.faces.ViewState'],
               'form1:_idcl': "form1:_idJsp47",
               'form1:_idcl': "form1:_idJsp50",
               'form1:_idJsp40': "_idJsp41",
               'form1:_idJsp42': "_idJsp43",
               'form1:_idJsp43': "_idJsp44",
               'form1:_idJsp45': "_idJsp46",
               'form1_SUBMIT': "1",
               'form1:_link_hidden_': "",
        }

        response.meta['javaxViewState'] = inputs['javax.faces.ViewState']
        yield scrapy.FormRequest(url='https://www.douane.gouv.fr/ncvi-web-sv12-prodouane/jsp/recapApporteur.jsf?total', formdata=args, callback=self.sv12_pdf_sv12, meta=response.meta)

    def sv12_pdf_sv12(self, response):
        self.log('sv12_pdf_sv12')
        filename = 'documents/sv12-%s-%s.pdf' % (response.meta['annee'], response.meta['info'][response.meta['id']]['cvi'])
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)

        args = {
               'javax.faces.ViewState': response.meta['javaxViewState'],
               'form1:_idcl':"form1:_idJsp50",
               'form1:_idcl':"form1:_idJsp53",
               'form1:_idJsp40':"_idJsp41",
               'form1:_idJsp42':"_idJsp43",
               'form1_SUBMIT':"1",
               'form1:_link_hidden_':"",
        }

        yield scrapy.FormRequest(url='https://www.douane.gouv.fr/ncvi-web-sv12-prodouane/jsp/recapApporteur.jsf?total', formdata=args, callback=self.sv12_tableur_sv12, meta=response.meta)


    def sv12_tableur_sv12(self, response):
        self.log('sv12_tableur_sv12_total')
        filename = 'documents/sv12-%s-%s.xls' % (response.meta['annee'], response.meta['info'][response.meta['id']]['cvi'])
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)

        response.meta['id'] = response.meta['id'] + 1
        if (not len(response.meta['cvi'])):
            yield scrapy.FormRequest(url='https://www.douane.gouv.fr/ncvi-web-sv12-prodouane/jsp/accueilOrganisme.jsf?%d,%d,%d,%d' % (response.meta['departement'], response.meta['commune'], response.meta['page'], response.meta['id']), callback=self.sv12_page_1, meta=response.meta)
