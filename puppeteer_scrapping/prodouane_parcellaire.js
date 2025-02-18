const prodouane = require('./common_prodouane.js');
const fs = require('fs');

(async () => {
  try {

    page = await prodouane.openpage_and_login();

    await page.click("input[value='Fiche de compte']")
              .then(prodouane.log("Click sur Fiche de compte OK"));

    await page.waitForSelector('.btn-primary');
    await page.$$("#formFdc\\:inputNumeroCvi");

    if(!process.env.CVI){
      prodouane.log("LISTER TOUS LES CVIS");

      const departements = await page.evaluate(() =>
        Array.from(document.querySelectorAll('#formFdc\\:selectDepartement option')).map(element=>element.value)
      );

      for(var departement of departements) {

        await page.select('select#formFdc\\:selectDepartement', departement);
        await page.click('input[value="Rechercher"]');
        await page.waitForSelector('#formFdc\\:dttListeEvvOA\\:th')

        var lastPage = (await page.$("#formFdc\\:dttListeEvvOA\\:scrollerId_ds_ff")) || true;
        var changeDepartment = false;

        do {
          const cvis = await page.evaluate(() =>
            Array.from(document.querySelectorAll('tbody#formFdc\\:dttListeEvvOA\\:tb td:nth-child(2)')).map(element=>element.innerText)
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

      prodouane.log("FIN LISTING DES CVIS");

      await prodouane.close();
      return;
    }

    await page.click("#formFdc\\:inputNumeroCvi");
    await page.type('#formFdc\\:inputNumeroCvi', process.env.CVI);

    await page.click('input[value="Rechercher"]')
              .then(() => prodouane.log("Input CVI OK"));

    await page.waitForTimeout(500);

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
    await page.click("#formFdc\\:dttListeEvvOA\\:tb tr:nth-child(1) td a:nth-child(1)")
              .then(() => prodouane.log("Click sur l'oeil OK"));

    await page.waitForSelector('.fdcCoordonneCol1');

    const html = await page.content();
    fs.writeFileSync("documents/parcellaire-"+process.env.CVI+"-accueil.html","<?xml version='1.0' encoding='UTF-8' ?>"+html);
    prodouane.log("Enregistre la page HTML des coordonnées de l'opérateur OK");

    try {
        await page.click('a[href="#formFdcConsultation:j_idt159:j_idt448"]')
              .then(() => prodouane.log("Click sur Mon parcellaire planté OK"));
    } catch (Error) {
        await page.click('a[href="#formFdcConsultation:j_idt159:j_idt444"]')
              .then(() => prodouane.log("Click sur Mon parcellaire planté OK"));
    }


    await page.waitForSelector('#formFdcConsultation\\:j_idt159\\:pnlDttListeSpcvPlante ',{timeout: 150000});
    fs.writeFileSync("documents/parcellaire-"+process.env.CVI+"-parcellaire.html",await page.content());
    prodouane.log("Enregistre la page HTML des parcellaire plante de l'opérateur OK");

    await page.click('#formFdcConsultation\\:j_idt157')
              .then(() => prodouane.log("Click sur première imprimante OK"));

    await page.waitForSelector('#waitPopup_container', {hidden: false});
    await page.waitForSelector('#waitPopup_container', {hidden: true});

    await page.waitForSelector('#popupReleveParcellaire_container', {hidden: false})
              .then(() => prodouane.log("Wait popup OK"));
    await page.waitForTimeout(750);

    await page.waitForSelector('#j_idt43');
    await page.click('#j_idt43')
              .then(() => prodouane.log("Click sur le bouton imprimante de la popup OK"));

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

    await page.waitForTimeout(250);
    await page.waitForSelector('#waitPollImpressionPdf_container', {hidden: false})
              .then(() => prodouane.log("Popup generation OK"));

    await page.waitForSelector('#formGetFdc\\:linkGetPdfFicheDeCompte')
              .then(() => prodouane.log("Lien de téléchargement trouvé"))
    await page.click('#formGetFdc\\:linkGetPdfFicheDeCompte')
              .then(() => prodouane.log("Click sur le lien téléchargement"))

    var pdf_filename = '';
    await page.waitForResponse((response) => {
        if (response.status() === 200) {
            pdf_filename = response.headers()['content-disposition'];

            if (!pdf_filename) {
                return false;
            }

            pdf_filename = pdf_filename.replace('attachment; filename=', '');
            prodouane.log("Nom PDF : "+pdf_filename);

            if (pdf_filename.match('pdf')) {
                return true;
            }
        }
        return false;
    });

    await page.waitForTimeout(400);
    await fs.rename('documents/Fiches_de_compte_'+process.env.CVI+'.pdf', 'documents/parcellaire-'+process.env.CVI+'-parcellaire.pdf', (err) => { return 'ERR'; });
    if (!fs.existsSync('documents/parcellaire-'+process.env.CVI+'-parcellaire.pdf')) {
        await fs.rename('documents/Fiches_de_compte_'+process.env.CVI+'.pdf.crdownload', 'documents/parcellaire-'+process.env.CVI+'-parcellaire.pdf', (err) => { return 'ERR'; });
    }
    await prodouane.close();

    prodouane.log("FINI POUR LE CVI "+process.env.CVI);

  } catch (e) {
    console.log("");
    console.log('FAILED !!');
    console.log(e);
    await prodouane.close();
    process.exit(255);
  }
})();
