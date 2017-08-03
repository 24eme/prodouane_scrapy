import scrapy
from scrapy.http import HtmlResponse
import os

class QuotesSpider(scrapy.Spider):
    name = "sv12"

#    custom_settings = {
#                       'COOKIES_DEBUG': True,
#                       }

    def start_requests(self):
        yield scrapy.Request(url="https://pro.douane.gouv.fr/", callback=self.login)

    def login(self, response):
        yield scrapy.FormRequest(url='https://pro.douane.gouv.fr/WDsession.asp', formdata={"login":os.environ['PRODOUANE_USER'],"pass":os.environ['PRODOUANE_PASS']}, callback=self.sv12_postlogin)

    def sv12_postlogin(self, response):
        yield scrapy.Request(url=response.urljoin('/wdactuapplif.asp?wdAppli=57'),  callback=self.sv12_postmenu)

    def sv12_postmenu(self, response):
        yield scrapy.Request(url=response.urljoin('/wdroute.asp?btn=57&rap=3&cat=3'),  callback=self.sv12_login, meta={'departement': 0, 'commune': 0, 'campagne': os.environ['PRODOUANE_CAMPAGNE']})

    def sv12_login(self, response):
        args = {}
        for i in response.css('#wdformAppli input'):
            args[i.xpath('@name')[0].extract()] = i.xpath('@value')[0].extract()
        args[response.css('#wdformAppli textarea').xpath('@name')[0].extract()] = response.css('#wdformAppli textarea::text').extract()

        yield scrapy.Request(url='https://pro.douane.gouv.fr/ncvi_sv12/prodouane/connexionProdouane?sid=%s&app=%s&code_teleservice=%s' % (args['sessionidT'], args['idappliT'], args['codeT']),  callback=self.sv12_connexion, meta=response.meta)

    def get_input_args(self, response, cssid):
        args = {}
        for i in (response.css('%s input' % cssid)):
            if (i.xpath('@name') and i.xpath('@value')):
                args[i.xpath('@name')[0].extract()] = i.xpath('@value')[0].extract()
        return args

    def sv12_connexion(self, response):
        self.log('sv12_connexion')
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
        response.meta['campagne_selected'] = campagnes[response.meta['campagne']]

        args = {}
        args['AJAXREQUEST'] = "_viewRoot"
        args['formFiltre:selectDepartement'] = departements[response.meta['departement']]
        args['formFiltre:selectCommune'] = communes[0]
        args[response.meta['campagne_name']] = response.meta['campagne_selected']
        args['formFiltre_SUBMIT']="1"
        args['javax.faces.ViewState'] = inputs['javax.faces.ViewState']
        args["formFiltre:_idJsp14"] = "formFiltre:_idJsp14"

        yield scrapy.FormRequest(url='https://pro.douane.gouv.fr/ncvi_sv12/prodouane/jsp/accueilOrganisme.jsf?javax.portlet.faces.DirectLink=true', formdata=args, callback=self.sv12_communes, meta=response.meta)

    def sv12_communes(self, response):
        meta = response.meta
        response = HtmlResponse(url=response.url, body=response.body)
        self.log('sv12_communes')
  #      with open("quotes-sv12-commune.html", 'wb') as f:
  #          f.write(response.body)

        communes = response.css('option::attr(value)').extract()
        inputs = self.get_input_args(response, '')

        args = {}
        args['formFiltre_SUBMIT']="1"
        args['javax.faces.ViewState'] = inputs['javax.faces.ViewState']
        args[meta['campagne_name']] = meta['campagne_selected']
        args['formFiltre:selectDepartement'] = str(meta['departement_selected'])
        args['formFiltre:selectCommune'] = communes[meta['commune']]
        args['formFiltre:inputNumeroCvi'] = ""
        args['formFiltre:_idJsp19'] = "Rechercher"
        args['autoScroll'] = "0,0"
        args['formFiltre:_idcl'] = ""
        args['formFiltre:_link_hidden_'] = ""

        meta['id'] = 0
        meta['page'] = 0
        meta['javaxViewState'] = inputs['javax.faces.ViewState']
        meta['nb_communes']  = len(communes)

        yield scrapy.FormRequest(url='https://pro.douane.gouv.fr/ncvi_sv12/prodouane/jsp/accueilOrganisme.jsf', formdata=args, callback=self.sv12_page_1, meta=meta)

    def sv12_page_1(self, response):
        self.log('dr_page_1')
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
        yield scrapy.FormRequest(url='https://pro.douane.gouv.fr/ncvi_sv12/prodouane/jsp/accueilOrganisme.jsf', formdata=args, callback=self.sv12_tableau_cvi, meta=response.meta)

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
                    info.append({'date': date, 'cvi': cvi, 'idhtml': idhtml})

        args = self.get_input_args(response, '#formFiltre')

        id = response.meta['id']

        if (len(info) > id):
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

            yield scrapy.FormRequest(url='https://pro.douane.gouv.fr/ncvi_sv12/prodouane/jsp/accueilOrganisme.jsf', formdata=myargs, callback=self.sv12_html_sv12, meta=response.meta)
        else:
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
                yield scrapy.FormRequest(url='https://pro.douane.gouv.fr/ncvi_sv12/prodouane/jsp/accueilOrganisme.jsf', formdata=myargs, callback=self.sv12_tableau_cvi, meta=response.meta)
            else:
                response.meta['page'] = 0
                response.meta['id'] = 0
                response.meta['commune'] = response.meta['commune'] + 1
                if (response.meta['nb_communes'] <= response.meta['commune']):
                    response.meta['departement'] = response.meta['departement'] + 1
                    response.meta['commune'] = 0
                if (response.meta['nb_departements'] > response.meta['departement']):
                    yield scrapy.FormRequest(url='https://pro.douane.gouv.fr/ncvi_sv12/prodouane/jsp/accueilOrganisme.jsf?commune=%d&dep=%d' % (response.meta['commune'], response.meta['departement']), callback=self.sv12_connexion, meta=response.meta)

    def sv12_html_sv12(self, response):
        self.log('sv12_html_sv12')
        filename = 'documents/SV12-%s-%s.html' % (response.meta['info'][response.meta['id']]['date'], response.meta['info'][response.meta['id']]['cvi'])
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)

        inputs = self.get_input_args(response, '')
        args = {
               'javax.faces.ViewState': inputs['javax.faces.ViewState'],
               'form1:_idcl':"form1:_idJsp50",
               'form1:_idJsp40':"_idJsp41",
               'form1:_idJsp42':"_idJsp43",
               'form1_SUBMIT':"1",
               'form1:_link_hidden_':"",
        }

        response.meta['javaxViewState'] = inputs['javax.faces.ViewState']
        yield scrapy.FormRequest(url='https://pro.douane.gouv.fr/ncvi_sv12/prodouane/jsp/recapApporteur.jsf?total', formdata=args, callback=self.sv12_tableur_sv12, meta=response.meta)


    def sv12_tableur_sv12(self, response):
        self.log('sv12_tableur_sv12_total')
        filename = 'documents/SV12-%s-%s.xls' % (response.meta['info'][response.meta['id']]['date'], response.meta['info'][response.meta['id']]['cvi'])
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)

        response.meta['id'] = response.meta['id'] + 1
        yield scrapy.FormRequest(url='https://pro.douane.gouv.fr/ncvi_sv12/prodouane/jsp/accueilOrganisme.jsf?%d,%d,%d,%d' % (response.meta['departement'], response.meta['commune'], response.meta['page'], response.meta['id']), callback=self.sv12_page_1, meta=response.meta)
