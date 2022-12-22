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
    
        
    await page.click('#j_idt172\\:j_idt178 a');  
    console.log("Click sur pdf");
    console.log("===================");
    

    var csv_filename = '';
    await page.waitForResponse((response) => {
        if (response.status() === 200) {
            csv_filename = response.headers()['content-disposition'];
            csv_filename = csv_filename.replace('attachment;filename=', '');
            console.log(csv_filename);
            if (csv_filename.match('pdf')) {
                return true;
            }
        }
        return false;
    });
    
    
    // session_id = csv_filename.match('DeclarationStock_([^_]+)_([^_]+)_([^\.]+)\.pdf');  DeclarationStock_6900703220_2122_RecapitulatifInstallation.pdf
    // await page.waitForTimeout(100);
    // await fs.rename('documents/'+csv_filename, 'documents/production-'+process.env.PRODOUANE_ANNEE+'-'+session_id[1]+'.csv', (err) => {if (err) throw err;});
    
    
    // await page.click('#j_idt172\\:j_idt178 a');
    
  }catch (e) {
    console.log("");
    console.log('FAILED !!');
    console.log(e);
    await prodouane.close();
  }

})();
