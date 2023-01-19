const prodouane = require('./common_prodouane.js');
const fs = require('fs');


(async () => {
  try {
    page = await prodouane.openpage_and_login();

    await page.click("input[value='Stock']");
    await page.waitForSelector('#formDeclaration');

    console.log("Click sur Stock OK");
    console.log("===================");


    //LISTER TOUS LES CVIS EN SORTIE STANDARD

    if(!process.env.CVI){

      if(! process.env.PRODOUANE_ANNEE){
        await prodouane.close();
        throw "Initialisez la variable d'environnement PRODOUANE_ANNEE avec l'année ";
      }

      if(process.env.DEBUG){
        console.log("LISTER TOUS LES CVIS");
        console.log("===================");
      }

      page.select('#formFiltre select',(parseInt(process.env.PRODOUANE_ANNEE) - 2000 - 5).toString());

      const departements = await page.evaluate(() =>
        Array.from(document.querySelectorAll('#formFiltre\\:selectDepartement option')).map(element=>element.value)
      );

      await page.waitForTimeout(250);

      for(var departement of departements){
        if(process.env.DEBUG){
          console.log("DEPARTEMENT : "+ departement+"\n");
        }

        await page.select('select#formFiltre\\:selectDepartement', departement);

        await page.waitForTimeout(250);

        const communes = await page.evaluate(() =>
          Array.from(document.querySelectorAll('#formFiltre\\:selectCommune option')).map(element=>element.value)
        );

        await page.waitForTimeout(250);

        for(var commune of communes){
          if(process.env.DEBUG){
            console.log("COMMUNE : "+ commune+"\n");
          }
          await page.select('select#formFiltre\\:selectCommune', commune);
          await page.click('input[value="Filtrer par EVV"]');
          await page.waitForSelector("#formDeclaration\\:listeDeclaration\\:th");

          var results = (await page.$('#formDeclaration\\:listeDeclaration\\:tf')) || false;

          if(!results){
            if(process.env.DEBUG){
              console.log('Aucun résultat');
            }
            continue;
          }

          var multiplePage = (await page.$("#formDeclaration\\:listeDeclaration\\:scrollerId_ds_f")) || false;

          if(multiplePage){
            if(process.env.DEBUG){
              console.log('PAGE MULTIPLE');
            }
            lastPage = false;
            while( !lastPage ){
              if(process.env.DEBUG){
                console.log('PARCOURS DES PAGES');
              }
              const cvis = await page.evaluate(() =>
                Array.from(document.querySelectorAll("td[id$='j_idt161']")).map(element=>element.innerText)
              );

              await page.waitForTimeout(250);

              for(var cvi of cvis){
                  console.log(cvi);
              }
              //Regarde si nous sommes à la dernière page
              const nextbtn = await page.evaluate(() => {
                  return document.getElementById("formDeclaration:listeDeclaration:scrollerId_ds_next").className;
              });

              if(nextbtn.match("rf-ds-dis")){
                lastPage = true;
              }
              else{
                await page.click('#formDeclaration\\:listeDeclaration\\:scrollerId_ds_next');
                await page.waitForTimeout(250);
              }
            }
          continue;
          }

          const cvis = await page.evaluate(() =>
            Array.from(document.querySelectorAll("td[id$='j_idt161']")).map(element=>element.innerText)
          );

          await page.waitForTimeout(250);

          if(process.env.DEBUG){
            console.log("NB CVIS : "+cvis.length);
          }

          for(var cvi of cvis){
              console.log(cvi);
          }

        }

      }

      if(process.env.DEBUG){
        console.log("FIN LISTING DES CVIS");
        console.log("===================");
      }

     await prodouane.close();
     return;
    }


    if(process.env.PRODOUANE_ANNEE){
      page.select('#formFiltre select',(parseInt(process.env.PRODOUANE_ANNEE) - 2000 - 5).toString());
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
