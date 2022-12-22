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

    console.log("Input CVI OK");
    console.log("===================");


    await page.waitForSelector("#formDeclaration\\:listeDeclaration\\:j_idt140");
    var result = await page.$("#formDeclaration\\:listeDeclaration\\:0\\:j_idt172");

    if (result === null) {
      console.log('Aucun résultat pour le CVI donné');
      await prodouane.close();
    }

    await page.click("#formDeclaration\\:listeDeclaration\\:0\\:j_idt172 a");

    console.log("Click sur Consulter par installation");
    console.log("===================");

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

    // await page.$$('#j_idt172\\:j_idt178 a(title="Générer un fichier pdf pour impression")');
    
    // console.log(liens);
    // await page.click('a(title="Générer un fichier pdf pour impression")');
    
    
    
    // Download du PDF

    await page.click('#j_idt172\\:j_idt178:nth-child(1)');

    console.log("Click sur pdf");
    console.log("===================");

    var pdf_filename = '';
    
    await page.waitForResponse((response) => {
        console.log(pdf_filename);
        if (response.status() === 200) {
            pdf_filename = response.headers()['content-disposition'];
            pdf_filename = pdf_filename.replace('attachment; filename=', '');
            console.log(pdf_filename);
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

    

    // Download du XLS
    await page.click("a[title='Générer un tableur Excel ou Calc']");

    console.log("Click sur xls");
    console.log("===================");

    var xls_filename = '';
    await page.waitForResponse((response) => {
        if (response.status() === 200) {
            xls_filename = response.headers()['content-disposition'];
            xls_filename = xls_filename.replace('attachment; filename=', '');
            if (xls_filename.match('/xls$/')) {
                return true;
            }
        }
        return false;
    });
    xls_newfilename = xls_filename.replace('DeclarationStock', 'ds');
    xls_newfilename = xls_newfilename.replace('_RecapitulatifInstallation', '');
    xls_newfilename = xls_newfilename.replace('_', '-');
    
    await page.waitForTimeout(500);
    
    // console.log('documents/'+xls_filename+"\n");
    // console.log('documents/'+xls_newfilename+"\n");
    
    await fs.rename('documents/'+xls_filename, 'documents/'+xls_newfilename, (err) => {if (err) throw err;});
    
    
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
    await prodouane.close();
  }

})();
