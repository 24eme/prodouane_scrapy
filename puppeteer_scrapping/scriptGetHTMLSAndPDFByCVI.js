const puppeteer = require('puppeteer');
const fs = require('fs');

(async () => {
  
  const browser = await puppeteer.launch(
  {
    headless: true,  //mettre à false pour debug
    defaultViewport: {width: 1920, height: 1080},
    ignoreDefaultArgs: ['--disable-extensions'],
    args: ['--no-sandbox', '--disable-setuid-sandbox'], 
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
    if(process.env.DEBUG == "true"){
      console.log("===================");
    }
    const page = await browser.newPage();
    const baseURL = 'https://www.douane.gouv.fr'
    
    await page.goto(baseURL+"/mon-espace-personnel");
    
    if(process.env.DEBUG == "true"){
      console.log("Home page: OK");
      console.log("===================");
    }
    await page.click('#loginIdentifiant');    
    await page.waitForSelector('#loginIdentifiant');
    
    if(process.env.DEBUG == "true"){
      console.log("Login page: OK");
      console.log("===================");
    }
    
    await page.type('#loginIdentifiant', process.env.PRODOUANE_USER); 
    await page.type('#loginMotdepasse', process.env.PRODOUANE_PASS);
    await page.keyboard.press('Enter');
    
    if(process.env.DEBUG == "true"){
      console.log("Login: OK");
      console.log("===================");
    }
    
    await page.waitForSelector('#timer');
    await page.click('button.positive');

    if(process.env.DEBUG == "true"){
      console.log("Click sur CONTINUER OK");
      console.log("===================");
    }

    await page.goto(baseURL+"/service-en-ligne/redirection/PORTAIL_VITI");
    
    if(process.env.DEBUG == "true"){
      console.log("Redirection OK");
      console.log("===================");
    }
    await page.waitForTimeout(5000);
    
    await page.click("input[value='Fiche de compte']");
    
    if(process.env.DEBUG == "true"){
      console.log("Click sur Fiche de compte OK");
      console.log("===================");
    }
    
    await page.waitForTimeout(1000);
    await page.$$("#formFdc\\:inputNumeroCvi");

    await page.click("#formFdc\\:inputNumeroCvi");    
    await page.type('#formFdc\\:inputNumeroCvi', process.env.CVI);    
    
    await page.click('input[value="Rechercher"]');
    
    if(process.env.DEBUG == "true"){
      console.log("Input CVI OK");
      console.log("===================");
    }
    
    await page.waitForSelector("#formFdc\\:dttListeEvvOA\\:0\\:j_idt268");
    await page.click("#formFdc\\:dttListeEvvOA\\:0\\:j_idt268");    
    
    if(process.env.DEBUG == "true"){
      console.log("Click sur l'oeil OK");
      console.log("===================");
    }

    await page.waitForTimeout(2000);

    const html = await page.content();
    fs.writeFileSync("documents/parcellaire-"+process.env.CVI+"-accueil.html","<?xml version='1.0' encoding='UTF-8' ?>"+html);
  	
    if(process.env.DEBUG == "true"){
      console.log("Enregistre la page HTML des coordonnées de l'opérateur OK");
      console.log("===================");
    }
        
    await page.click('a[href="#formFdcConsultation:j_idt195:j_idt480"]'); 
    
    if(process.env.DEBUG == "true"){
      console.log("Click sur Mon parcellaire planté OK");
      console.log("===================");
    }
    
    await page.waitForSelector('#formFdcConsultation\\:j_idt195\\:pnlDttListeSpcvPlante ');       
    fs.writeFileSync("documents/parcellaire-"+process.env.CVI+"-parcellaire.html",await page.content());

    if(process.env.DEBUG == "true"){
      console.log("Enregistre la page HTML des parcellaire plante de l'opérateur OK");
      console.log("===================");
    }
    
    await page.click('#formFdcConsultation\\:j_idt193'); 
    
    if(process.env.DEBUG == "true"){
      console.log("Click sur première imprimante OK");
      console.log("===================");
    }
    
    client = await page.target().createCDPSession()
    await client.send('Page.setDownloadBehavior', {
    behavior: 'allow',
    downloadPath: "documents",
    });
    
    await page.waitForTimeout(2000);
    await page.click('#releveForm\\:j_idt80');
    await page.waitForTimeout(10000);

    if(process.env.DEBUG == "true"){
      console.log("Click sur deuxième imprimante OK");
      console.log("===================");
    }
    
    fs.rename('documents/Fiches_de_compte_'+process.env.CVI+'.pdf', 'documents/parcellaire-'+process.env.CVI+'-parcellaire.pdf', (err) => {
        if (err) throw err;
        if(process.env.DEBUG == "true"){
          console.log('Rename OK!');
          console.log("===================");
        }
    });
    
    await browser.close();

    if(process.env.DEBUG == "true"){
      console.log("FINI POUR LE CVI "+process.env.CVI);  
      console.log("===================");
    }
    
    }catch (e) {
				console.log("");
				console.log('FAILED !!');
				console.log(e);
        await browser.close();
			}
		})();