const puppeteer = require('puppeteer');
const fs = require('fs');

(async () => {
  
  const browser = await puppeteer.launch(
  {
    headless: false,
    defaultViewport: {width: 1920, height: 1080},
  }
  );
  try {
    
    if(!process.env.PRODOUANE_USER){
      await browser.close();
      throw "Initialisez la variable d'environnement PRODOUANE_USER avec le login";
    }
    if(!process.env.PRODOUANE_PASS){
      await browser.close();
      throw "Initialisez la variable d'environnement PRODOUANE_PASS avec le mot de passe";
    }
    if(!process.env.CVI){
      await browser.close();
      throw "Initialisez la variable d'environnement CVI avec le numéro de CVI";
    }
    
    console.log("===================");
    
    const page = await browser.newPage();
    const baseURL = 'https://www.douane.gouv.fr'
    
    await page.goto(baseURL+"/mon-espace-personnel");
    
    console.log("Home page: OK");
    console.log("===================");

    await page.click('#loginIdentifiant');    
    await page.waitForSelector('#loginIdentifiant');
    
    console.log("Login page: OK");
    console.log("===================");
    
    await page.type('#loginIdentifiant', process.env.PRODOUANE_USER); 
    await page.type('#loginMotdepasse', process.env.PRODOUANE_PASS);
    await page.keyboard.press('Enter');
    
    console.log("Login: OK");
    console.log("===================");
    
    await page.waitForSelector('#timer');
    await page.click('button.positive');

    console.log("Click sur CONTINUER OK");
    console.log("===================");

    await page.goto(baseURL+"/service-en-ligne/redirection/PORTAIL_VITI");
    
    console.log("Redirection OK");
    console.log("===================");
    
    await page.waitForTimeout(5000);
    
    await page.click("input[value='Fiche de compte']");
        
    console.log("Click sur Fiche de compte OK");
    console.log("===================");
    
    await page.waitForTimeout(1000);
    await page.$$("#formFdc\\:inputNumeroCvi");

    await page.click("#formFdc\\:inputNumeroCvi");    
    await page.type('#formFdc\\:inputNumeroCvi', process.env.CVI);    
    
    await page.click('input[value="Rechercher"]');
    
    console.log("Input CVI OK");
    console.log("===================");
    
    await page.waitForSelector("#formFdc\\:dttListeEvvOA\\:0\\:j_idt268");
    await page.click("#formFdc\\:dttListeEvvOA\\:0\\:j_idt268");    
    
    console.log("Click sur l'oeil OK");
    console.log("===================");

    await page.waitForTimeout(2000);

    const html = await page.content();
    fs.writeFileSync("documents/parcellaire-"+process.env.CVI+"-accueil.html","<?xml version='1.0' encoding='UTF-8' ?>"+html);
  	
    console.log("Enregistre la page HTML des coordonnées de l'opérateur OK");
    console.log("===================");
    
    
    await page.click('a[href="#formFdcConsultation:j_idt195:j_idt480"]'); 
    
    console.log("Click sur Mon parcellaire planté OK");
    console.log("===================");

    await page.waitForSelector('#formFdcConsultation\\:j_idt195\\:pnlDttListeSpcvPlante ');       
    fs.writeFileSync("documents/parcellaire-"+process.env.CVI+"-parcellaire.html",await page.content());

    console.log("Enregistre la page HTML des parcellaire plante de l'opérateur OK");
    console.log("===================");

    await page.click('#formFdcConsultation\\:j_idt193'); 
    
    console.log("Click sur première imprimante OK");
    console.log("===================");
    
    client = await page.target().createCDPSession()
    await client.send('Page.setDownloadBehavior', {
    behavior: 'allow',
    downloadPath: "documents",
    });
    
    await page.waitForTimeout(2000);
    await page.click('#releveForm\\:j_idt80');
    await page.waitForTimeout(10000);

    console.log("Click sur deuxième imprimante OK");
    console.log("===================");
    
    fs.rename('documents/Fiches_de_compte_'+process.env.CVI+'.pdf', 'documents/parcellaire-'+process.env.CVI+'-parcellaire.pdf', (err) => {
        if (err) throw err;
        console.log('Rename OK!');
        console.log("===================");
    });
    
    await browser.close();

    console.log("FINI POUR LE CVI "+process.env.CVI);  
    console.log("===================");

    }catch (e) {
				console.log("");
				console.log('FAILED !!');
				console.log(e);
			}
		})();