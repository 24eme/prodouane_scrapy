const prodouane = require('./common_prodouane.js');
const fs = require('fs');


(async () => {
  try {
    page = await prodouane.openpage_and_login();

    await page.click("input[value='Stock']");
    await page.waitForSelector('#formDeclaration');

    console.log("Click sur Stock OK");
    console.log("===================");

    if(!process.env.CVI){
      if(process.env.DEBUG){
        console.log("LISTER TOUS LES CVIS");
        console.log("===================");
      }

       //LISTER TOUS LES CVIS EN SORTIE STANDARD
     await prodouane.close();
     return;
    }


    await page.click("#formFiltre\\:inputNumeroCvi");
    await page.type('#formFiltre\\:inputNumeroCvi', process.env.CVI);

    await page.click('input[value="Filtrer par EVV"]');

    if(process.env.DEBUG){
      console.log("Input CVI OK");
      console.log("===================");
    }


    await page.waitForSelector("#formDeclaration\\:listeDeclaration\\:j_idt140");
    var result = await page.$("#formDeclaration\\:listeDeclaration\\:0\\:j_idt172");

    if (result === null) {
      console.log('Aucun résultat pour le CVI donné');
      await prodouane.close();
    }

    await page.waitForSelector("#formDeclaration\\:listeDeclaration\\:0\\:j_idt172");

    await page.waitForTimeout(100);

    await page.click("#formDeclaration\\:listeDeclaration\\:0\\:j_idt172 a");

    if(process.env.DEBUG){
      console.log("Click sur Consulter par installation");
      console.log("===================");
    }

    await page.waitForSelector("#j_idt172\\:0");
    fs.writeFileSync("documents/ds-"+process.env.CVI+".html",await page.content());

    if(process.env.DEBUG){
      console.log("Enregistre la page HTML des stock de l'opérateur OK");
      console.log("===================");
    }

    // CONFIGURATION DU DOSSIER DE TELECHARGEMENT

    client = await page.target().createCDPSession()
    await client.send('Page.setDownloadBehavior', {
    behavior: 'allow',
    downloadPath: "documents",
    });

    // Download du PDF

    liens = await page.$$('#j_idt172\\:j_idt178 a');

    await liens[0].click();

    if(process.env.DEBUG){
      console.log("Click sur pdf");
      console.log("===================");
    }

    var pdf_filename = '';

    await page.waitForResponse((response) => {
        if (response.status() === 200) {
            pdf_filename = response.headers()['content-disposition'];
            pdf_filename = pdf_filename.replace('attachment; filename=', '');
            if (pdf_filename.match('.pdf')) {
                return true;
            }
        }
        return false;
    });

    await page.waitForTimeout(100);

    pdf_newfilename = pdf_filename.replace('DeclarationStock', 'ds');
    pdf_newfilename = pdf_newfilename.replace('_RecapitulatifInstallation', '');
    pdf_newfilename = pdf_newfilename.replace('_', '-');
    await fs.rename('documents/'+pdf_filename, 'documents/'+pdf_newfilename, (err) => {if (err) throw err;});

    if(process.env.DEBUG){
      console.log("Renommage de "+'documents/'+pdf_filename+"en"+'documents/'+pdf_newfilename+" OK");
      console.log("===================");
    }

    // Download du XLS

    await liens[1].click();

    if(process.env.DEBUG){
      console.log("Click sur xls");
      console.log("===================");
    }
    
    var xls_filename = '';
    await page.waitForResponse((response) => {
        if (response.status() === 200) {
            xls_filename = response.headers()['content-disposition'];
            xls_filename = xls_filename.replace('attachment; filename=', '');
            if (xls_filename.match(/.xls$/)) {
                return true;
            }
        }
        return false;
    });

    xls_newfilename = xls_filename.replace('DeclarationStock', 'ds');
    xls_newfilename = xls_newfilename.replace('_RecapitulatifInstallation', '');
    xls_newfilename = xls_newfilename.replace('_', '-');

    await page.waitForTimeout(5000); //attendre le téléchargement complet et non du fichier temporaire de chromium .crdownload

    await fs.rename('documents/'+xls_filename, 'documents/'+xls_newfilename, (err) => {if (err) throw err;});

    if(process.env.DEBUG){
      console.log("Renommage de "+'documents/'+xls_filename+"en"+'documents/'+xls_newfilename+" OK");
      console.log("===================");
    }
    await prodouane.close();

  }catch (e) {
    console.log("");
    console.log('FAILED !!');
    console.log(e);
    await prodouane.close();
  }

})();
