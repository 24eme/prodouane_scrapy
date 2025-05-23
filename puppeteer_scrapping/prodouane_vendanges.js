const prodouane = require('./common_prodouane.js');
const fs = require('fs');

(async () => {
  page = null;
  try {

    page = await prodouane.openpage_and_login();

    await page.click("input[value='VENDANGES']");

    await page.waitForSelector('#accueil');
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

    await page.click('#choix-statut-etat_BV_option_0')

    await page.waitForTimeout(250);

    await page.type('#inputNumeroCvi', process.env.CVI);
    await page.keyboard.press('Enter');

    await page.waitForSelector('#input-live-feedback');

    if(process.env.DEBUG){
      console.log("Saisie des infos CVI et Capagne");
      console.log("===================");
    }
    await page.waitForSelector('#inputNumeroCvi.is-valid');

    await page.waitForTimeout(250);
    await page.click('#btnRechercheDeclaration');
    if(process.env.DEBUG){
      console.log("Click sur la recherche");
      console.log("===================");
    }
    
    await page.waitForSelector('#inputNumeroCvi.is-valid');
    await page.waitForSelector('#tableau-declarations tbody tr');
    await page.waitForTimeout(250);
    const h2_result = await page.$$('#tableau-declarations tbody tr .btn-primary');
    
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

    await page.waitForSelector('#tableau-declarations tbody tr:first-child .btn-primary');

    await page.click('#tableau-declarations tbody tr:first-child .btn-primary');
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
    await page.click("#tableau-recap-resume button:first-child");
    if(process.env.DEBUG){
      console.log("Téléchargement CSV demandé");
      console.log("===================");
    }
    var csv_filename = '';
    await page.waitForResponse((response) => {
        if (response.status() === 200) {
            csv_filename = response.headers()['content-disposition'];
            csv_filename = csv_filename.replace('attachment;filename=', '');
            if (csv_filename.match('csv')) {
                return true;
            }
        }
        return false;
    });
    await page.waitForTimeout(1000);
    session_id = csv_filename.match('déclaration_production_([^_]+)_([^_]+)_([^\.]+)\.csv');
    await fs.rename('documents/'+csv_filename, 'documents/production-'+process.env.PRODOUANE_ANNEE+'-'+session_id[1]+'.csv', (err) => {if (err) throw err;});


    if(process.env.DEBUG){
      console.log("Téléchargement CSV OK");
      console.log('documents/'+csv_filename+' => documents/production-'+process.env.PRODOUANE_ANNEE+'-'+session_id[1]+'.csv');
      console.log("===================");
    }

    await page.click('.toggle-switch li:last-child label');
    await page.waitForSelector('#tableau-recap-resume', {hidden: true});
    await page.waitForSelector('#btnTeleChargement');
    if(process.env.DEBUG){
      console.log("Page par apporteur");
      console.log("===================");
    }
    await page.waitForTimeout(250);

    await page.click("#btnTeleChargement");
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

    await page.click('#buttonLogin');
    await page.waitForSelector('.logout');
    await page.click('.logout');

    await page.waitForSelector('.erreur-authentification')
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