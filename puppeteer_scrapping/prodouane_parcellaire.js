const prodouane = require('./common_prodouane.js');
const fs = require('fs');

(async () => {
  try {

    page = await prodouane.openpage_and_login();

    await page.click("input[value='Fiche de compte']");
    
    if(process.env.DEBUG){
      console.log("Click sur Fiche de compte OK");
      console.log("===================");
    }
    

    await page.waitForSelector('.btn-primary');
    await page.$$("#formFdc\\:inputNumeroCvi");


    if(!process.env.CVI){
      if(process.env.DEBUG){
        console.log("LISTER TOUS LES CVIS");
        console.log("===================");
      }

      const departements = await page.evaluate(() =>
        Array.from(document.querySelectorAll('#formFdc\\:selectDepartement option')).map(element=>element.value)
      );

      for(var departement of departements){

        await page.select('select#formFdc\\:selectDepartement', departement);

        await page.click('input[value="Rechercher"]');
        
        await page.waitForSelector('#formFdc\\:dttListeEvvOA\\:th')
        
        var lastPage = (await page.$("#formFdc\\:dttListeEvvOA\\:scrollerId_ds_ff")) || true;
        
        var changeDepartment = false;
        
        do {
            
          const cvis = await page.evaluate(() =>
            Array.from(document.querySelectorAll("td[id$='idt260']")).map(element=>element.innerText)
          );
          
          for(var cvi of cvis){
              console.log(cvi);
          }
          
          var multiplePage = (await page.$("#formFdc\\:dttListeEvvOA\\:scrollerId_ds_next")) || false;
          
          if(multiplePage){
            await page.click("#formFdc\\:dttListeEvvOA\\:scrollerId_ds_next");
          }
          
          await page.waitForTimeout(250);
          
          if(lastPage==true){
            changeDepartment=true;
          }
          
          lastPage = (await page.$("#formFdc\\:dttListeEvvOA\\:scrollerId_ds_ff")) || true;
          
        } while(!changeDepartment);
        
      }
      
      if(process.env.DEBUG){
        console.log("FIN LISTING DES CVIS");
        console.log("===================");
      }
      
      await prodouane.close();
      return;
    }
    await page.click("#formFdc\\:inputNumeroCvi");    
    await page.type('#formFdc\\:inputNumeroCvi', process.env.CVI);    
    
    await page.click('input[value="Rechercher"]');
    
    if(process.env.DEBUG){
      console.log("Input CVI OK");
      console.log("===================");
    }
    
    await page.waitForTimeout(250);
    
    const tableLines = await page.evaluate(() =>
      Array.from(document.querySelectorAll("td[class='rf-dt-nd-c']")).map(element=>element.innerText)
    ); 
        
    var hasCVIError = (await page.$("#erreur\\:j_idt112")) || false;
        
    if(hasCVIError || tableLines.includes("aucune")){
      console.log("");
      console.log('FAILED !! ERREUR DE CVI');
      await prodouane.close();
      return;
    }    
    
    var hasError = (await page.$("#erreur\\:jsfErrorId")) || false;
    
    if(hasError){
      console.log("");
      console.log('FAILED !! IL Y A UNE ERREUR DANS LA RECHERCHE');
      await prodouane.close();
      return;
    }

    await page.waitForSelector("#formFdc\\:dttListeEvvOA\\:tb tr:nth-child(1) td a:nth-child(1)");
    await page.click("#formFdc\\:dttListeEvvOA\\:tb tr:nth-child(1) td a:nth-child(1)");

    if(process.env.DEBUG){
      console.log("Click sur l'oeil OK");
      console.log("===================");
    }

    await page.waitForSelector('.fdcCoordonneCol1');

    const html = await page.content();
    fs.writeFileSync("documents/parcellaire-"+process.env.CVI+"-accueil.html","<?xml version='1.0' encoding='UTF-8' ?>"+html);

    if(process.env.DEBUG){
      console.log("Enregistre la page HTML des coordonnées de l'opérateur OK");
      console.log("===================");
    }

    await page.click('a[href="#formFdcConsultation:j_idt195:j_idt480"]');

    if(process.env.DEBUG){
      console.log("Click sur Mon parcellaire planté OK");
      console.log("===================");
    }

    await page.waitForSelector('#formFdcConsultation\\:j_idt195\\:pnlDttListeSpcvPlante ');
    fs.writeFileSync("documents/parcellaire-"+process.env.CVI+"-parcellaire.html",await page.content());

    if(process.env.DEBUG){
      console.log("Enregistre la page HTML des parcellaire plante de l'opérateur OK");
      console.log("===================");
    }

    await page.click('#formFdcConsultation\\:j_idt193');

    if(process.env.DEBUG){
      console.log("Click sur première imprimante OK");
      console.log("===================");
    }

    await page.waitForSelector('#waitPopup_content', {hidden: false});
    await page.waitForSelector('#waitPopup_content', {hidden: true});

    if(process.env.DEBUG){
      console.log("Wait popup OK");
      console.log("=============");
    }

    await page.waitForSelector('#j_idt80');
    await page.waitForTimeout(750);

    await page.click('#j_idt80');
    if(process.env.DEBUG){
        console.log("Click sur le bouton imprimante de la popup OK");
        console.log("===================");
    }

    try {
      fs.unlinkSync('documents/Fiches_de_compte_'+process.env.CVI+'.pdf', {force: true});
    } catch (Error) { }

    try {
      fs.unlinkSync('documents/Fiches_de_compte_'+process.env.CVI+'.pdf.crdownload', {force: true});
    } catch (Error) { }

    try {
      fs.unlinkSync('documents/parcellaire-'+process.env.CVI+'-parcellaire.pdf', {force: true});
    } catch (Error) { }

    client = await page.target().createCDPSession()
    await client.send('Page.setDownloadBehavior', {
    behavior: 'allow',
    downloadPath: "documents",
    });

    var pdf_filename = '';
    await page.waitForSelector('#formGetFdc\\:linkGetPdfFicheDeCompte');
    await page.waitForTimeout(750);
    await page.click('#formGetFdc\\:linkGetPdfFicheDeCompte')
    await page.waitForResponse((response) => {
        if (response.status() === 200) {
            pdf_filename = response.headers()['content-disposition'];
            if (!pdf_filename) {
                return false;
            }
            pdf_filename = pdf_filename.replace('attachment; filename=', '');
            if(process.env.DEBUG){
              console.log("Nom PDF : "+pdf_filename);
              console.log("===================");
            }
            if (pdf_filename.match('pdf')) {
                return true;
            }
        }
        return false;
    });


    if(process.env.DEBUG){
      console.log("Click sur le lien téléchargement");
      console.log("===================");
    }

    await page.waitForTimeout(400);
    await fs.rename('documents/Fiches_de_compte_'+process.env.CVI+'.pdf', 'documents/parcellaire-'+process.env.CVI+'-parcellaire.pdf', (err) => { return 'ERR'; });
    if (!fs.existsSync('documents/parcellaire-'+process.env.CVI+'-parcellaire.pdf')) {
        await fs.rename('documents/Fiches_de_compte_'+process.env.CVI+'.pdf.crdownload', 'documents/parcellaire-'+process.env.CVI+'-parcellaire.pdf', (err) => { return 'ERR'; });
    }
    await prodouane.close();

    if(process.env.DEBUG){
      console.log("FINI POUR LE CVI "+process.env.CVI);  
      console.log("===================");
    }
    
  }catch (e) {
    console.log("");
    console.log('FAILED !!');
    console.log(e);
    await prodouane.close();
    process.exit(255);
  }
})();
