const prodouane = require('./common_prodouane.js');
const fs = require('fs');

(async () => {
  page = null;
  try {

    page = await prodouane.openpage_and_login();

    await page.click("input[value='VENDANGES']");

    await page.waitForSelector('.btnMenu');
    if(process.env.DEBUG){
      console.log("Entrée dans Vendanges");
      console.log("===================");
    }
    await page.waitForTimeout(250);

    const has_ovnis = await page.$$('.table-title');

    if (has_ovnis.length) {
        if(process.env.DEBUG){
          console.log("Selection d'un OVNIS");
          console.log("===================");
        }

        await page.type('input.champRecherche', process.env.PRODOUANE_OVNI);
        await page.click('.material-icons');
    }

    await page.waitForSelector('.btnMenu');

    await page.click('.btnMenu');
    await page.waitForSelector('#inputNumeroCvi');

    await page.waitForTimeout(250);

    await page.type('#selectCampagne',  process.env.PRODOUANE_ANNEE);
    await page.keyboard.press('Enter');

    await page.click('#statut_1')

    await page.waitForTimeout(250);

    await page.type('#inputNumeroCvi', process.env.CVI);
    await page.keyboard.press('Enter');

    await page.waitForSelector('.fr-input-group--valid');

    if(process.env.DEBUG){
      console.log("Saisie des infos CVI et Capagne");
      console.log("===================");
    }


    await page.waitForSelector('#bloc-form-recherche-dec-par-evv button.fr-icon-search-line');
    await page.waitForTimeout(250);

    await page.click('#statut_1')
    await page.waitForTimeout(250);

    await page.keyboard.press("Tab");
    await page.keyboard.press("Tab");
    await page.keyboard.press('Enter');

//    await page.click('#bloc-form-recherche-dec-par-evv button.fr-icon-search-line');
    if(process.env.DEBUG){
      console.log("Click sur la recherche");
      console.log("===================");
    }

    await page.waitForSelector('#tableau-declarations tbody tr');
    await page.waitForTimeout(250);
    const h2_result = await page.$$('#tableau-declarations tbody tr .fr-badge--success');

    if (h2_result.length < 1) {
        console.log("ERREUR: pas de résultat");
        if (process.env.DEBUG) {
            await page.waitForTimeout(500000);
        }
        return prodouane.close();
    }
    if (h2_result.length > 1) {
        console.log("ERREUR: plus d'un résultat");
        if (process.env.DEBUG) {
            await page.waitForTimeout(500000);
        }
        return prodouane.close();
    }
    if(process.env.DEBUG){
      console.log("Une déclaration trouvée");
      console.log("===================");
    }

    await page.waitForSelector('#tableau-declarations tbody tr:first-child .fr-icon-arrow-right-line');

    await page.click('#tableau-declarations tbody tr:first-child .fr-icon-arrow-right-line');
    await page.waitForSelector('#tableau-recap-resume');
    if(process.env.DEBUG){
      console.log("Page du document");
      console.log("===================");
    }

    client = await page.target().createCDPSession()
    await client.send('Page.setDownloadBehavior', {
    behavior: 'allow',
    downloadPath: "documents",
    });
    await page.waitForTimeout(250);
    await page.click("#accordeonRecapDec .fr-link--download:first-child");
    if(process.env.DEBUG){
      console.log("Téléchargement CSV demandé");
      console.log("===================");
    }
    var first_filename = '';
    await page.waitForResponse((response) => {
        if (response.status() === 200) {
            first_filename = response.headers()['content-disposition'];
            first_filename = first_filename.replace('attachment;filename=', '');
            if (first_filename.match('csv')) {
                return true;
            }
            if (first_filename.match('pdf')) {
                return true;
            }
        }
        return false;
    });
    await page.waitForTimeout(1000);

    is_production = first_filename.match('production.*\.csv');
    if (is_production) {
        await scrape_production(first_filename, page, process);
    } else {
        await scrape_recolte(first_filename, page, process);
    }

    await page.click('.id-user');
    await page.waitForSelector('.fr-icon-logout-box-r-line');
    await page.click('.fr-icon-logout-box-r-line');

    await page.waitForTimeout(1000);
    if(process.env.DEBUG){
      console.log("Déconnexion OK");
      console.log("===================");
    }

    await prodouane.close();

  }catch (e) {
    console.log("");
    console.log('FAILED !!');
    console.log(e);
    if(process.env.DEBUG && page){
        await page.screenshot({ path: '/tmp/screenshot_vendanges_error.png'})
        console.log('screenshot in /tmp/screenshot_vendanges_error.png')
    }
    await prodouane.close();
  }
})();

async function scrape_recolte(pdf_filename, page, process) {
    session_id = pdf_filename.match('([^_]+)_recolte_production_([^\.]+)\.pdf');
    await fs.rename('documents/'+pdf_filename, 'documents/recolte-'+process.env.PRODOUANE_ANNEE+'-'+session_id[1]+'.pdf', (err) => {if (err) throw err;});
    if(process.env.DEBUG){
      console.log("Téléchargement PDF OK");
      console.log('documents/'+pdf_filename+' => documents/recolte-'+process.env.PRODOUANE_ANNEE+'-'+session_id[1]+'.pdf');
      console.log("===================");
    }

    await page.click("#accordeonRecapDec .fr-link--download:nth-child(2)");
    if(process.env.DEBUG){
      console.log("Téléchargement JSON demandé");
      console.log("===================");
    }
    var json_filename = '';
    await page.waitForResponse((response) => {
        if (response.status() === 200) {
            json_filename = response.headers()['content-disposition'];
            json_filename = json_filename.replace('attachment;filename=', '');
            if (json_filename.match('json')) {
                return true;
            }
        }
        return false;
    });
    await page.waitForTimeout(1000);
    await fs.rename('documents/'+json_filename, 'documents/recolte-'+process.env.PRODOUANE_ANNEE+'-'+session_id[1]+'.json', (err) => {if (err) throw err;});
    if(process.env.DEBUG){
      console.log("Téléchargement JSON OK");
      console.log('documents/'+json_filename+' => documents/recolte-'+process.env.PRODOUANE_ANNEE+'-'+session_id[1]+'.json');
      console.log("===================");
    }

}

async function scrape_production(csv_filename, page, process) {
    session_id = csv_filename.match('([^_]+)_production_([^\.]+)\.csv');
    await fs.rename('documents/'+csv_filename, 'documents/production-'+process.env.PRODOUANE_ANNEE+'-'+session_id[1]+'.csv', (err) => {if (err) throw err;});

    if(process.env.DEBUG){
      console.log("Téléchargement CSV OK");
      console.log('documents/'+csv_filename+' => documents/production-'+process.env.PRODOUANE_ANNEE+'-'+session_id[1]+'.csv');
      console.log("===================");
    }

    await page.click("#accordeonRecapDec .fr-link--download:nth-child(3)");
    if(process.env.DEBUG){
      console.log("Téléchargement JSON demandé");
      console.log("===================");
    }
    var json_filename = '';
    await page.waitForResponse((response) => {
        if (response.status() === 200) {
            json_filename = response.headers()['content-disposition'];
            json_filename = json_filename.replace('attachment;filename=', '');
            if (json_filename.match('json')) {
                return true;
            }
        }
        return false;
    });
    await page.waitForTimeout(1000);
    await fs.rename('documents/'+json_filename, 'documents/production-'+process.env.PRODOUANE_ANNEE+'-'+session_id[1]+'.json', (err) => {if (err) throw err;});
    if(process.env.DEBUG){
      console.log("Téléchargement JSON OK");
      console.log('documents/'+json_filename+' => documents/production-'+process.env.PRODOUANE_ANNEE+'-'+session_id[1]+'.json');
      console.log("===================");
    }

    await page.click('#segmented-v-18');
    await page.waitForSelector('#tableau-recap-resume', {hidden: true});
    await page.waitForSelector('#tableau-recap-par-fournisseur-apporteur table');
    if(process.env.DEBUG){
      console.log("Page par apporteur");
      console.log("===================");
    }
    await page.waitForTimeout(250);

    await page.click(".fr-link--download");
    if(process.env.DEBUG){
      console.log("Téléchargement du PDF");
      console.log("===================");
    }
    var pdf_filename = '';
    await page.waitForResponse((response) => {
        if (response.status() === 200) {
            pdf_filename = response.headers()['content-disposition'];
            pdf_filename = pdf_filename.replace('attachment;filename=', '');
            if(process.env.DEBUG){
                console.log('pdf_filename: ' + pdf_filename);
            }
            if (pdf_filename.match('pdf')) {
                return true;
            }
        }
        return false;
    });
    await page.waitForTimeout(1000);
    document_filename = null
    if (!document_filename && fs.existsSync('documents/'+pdf_filename)) {
        document_filename = 'documents/'+pdf_filename;
    }
    if (!document_filename && fs.existsSync('documents/declaration_'+session_id[2]+'.pdf')) {
        document_filename = 'documents/declaration_'+session_id[2]+'.pdf';
    }
    if (!document_filename && fs.existsSync('documents/declaration_production-'+session_id[2]+'_recapitulatif_par_fournisseur.pdf')) {
        document_filename = 'documents/declaration_production-'+session_id[2]+'_recapitulatif_par_fournisseur.pdf';
    }
    if (!document_filename && fs.existsSync('documents/declaration_Production-'+session_id[2]+'_recapitulatif_par_fournisseur.pdf')) {
        document_filename = 'documents/declaration_Production-'+session_id[2]+'_recapitulatif_par_fournisseur.pdf';
    }
    if (!document_filename && fs.existsSync('documents/declaration_production-'+session_id[2]+'_recapitulatif_par_apporteur.pdf')) {
        document_filename = 'documents/declaration_production-'+session_id[2]+'_recapitulatif_par_apporteur.pdf';
    }
    if (!document_filename && fs.existsSync('documents/declaration_Production-'+session_id[2]+'_recapitulatif_par_apporteur.pdf')) {
        document_filename = 'documents/declaration_Production-'+session_id[2]+'_recapitulatif_par_apporteur.pdf';
    }

    if (document_filename) {
        await fs.rename(document_filename, 'documents/production-'+process.env.PRODOUANE_ANNEE+'-'+session_id[1]+'.pdf', (err) => {if (err) return 'ERR';});
        if(process.env.DEBUG){
            console.log("Téléchargement PDF OK");
            console.log('documents/'+document_filename+" => "+'documents/production-'+process.env.PRODOUANE_ANNEE+'-'+session_id[1]+'.pdf');
            console.log("===================");
        }
    }
}
