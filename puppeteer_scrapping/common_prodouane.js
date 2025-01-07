const puppeteer = require('puppeteer');

var browser;

const baseURL = 'https://www.douane.gouv.fr';
exports.baseURL = baseURL;

exports.close = async function() {
    return await browser.close();
}

exports.log = function (message) {
    if (process.env.DEBUG) {
        console.log(message + "\n===================")
    }
}

exports.openpage_and_login = async function () {

    if (!process.env.DEBUG && (process.env.DEBUG_WITH_BROWSER != undefined)) {
        process.env.DEBUG = 1;
    }

    browser = await puppeteer.launch({
      headless: !(process.env.DEBUG_WITH_BROWSER),  //mettre à false pour debug
      defaultViewport: {width: 1920, height: 1080},
      ignoreDefaultArgs: ['--disable-extensions'],
      args: ['--no-sandbox', '--disable-setuid-sandbox'],
    });

    if(!process.env.PRODOUANE_USER){
      await browser.close();
      throw "Initialisez la variable d'environnement PRODOUANE_USER avec le login";
    }
    if(!process.env.PRODOUANE_PASS){
      await browser.close();
      throw "Initialisez la variable d'environnement PRODOUANE_PASS avec le mot de passe";
    }
    this.log('');

    const page = await browser.newPage();

    await page.goto("https://connexion.douane.gouv.fr/")

    await page.click('#loginIdentifiant');
    await page.waitForSelector('#loginIdentifiant')
              .then(() => this.log("Login page: OK"));

    await page.type('#loginIdentifiant', process.env.PRODOUANE_USER);
    await page.type('#loginMotdepasse', process.env.PRODOUANE_PASS);
    await page.keyboard.press('Enter')
                       .then(() => this.log("Login: OK"));

    await page.waitForSelector('.container');
    await page.waitForTimeout(250);

    const timer = await page.$$('#timer');
    if (timer.length) {
      await page.click('button.positive')
                .then(() => this.log("Click sur CONTINUER OK"));
    } else {
      this.log("Seule connexion, on peut aller directement au portail VITI");
    }

    await page.goto(baseURL+"/");
    await page.waitForSelector('.marqueDouane');

    const meteo = await page.$$('.descriptionMeteo');
    if (meteo.length) {
      this.log("Mode secours de la douane détecté");
      throw new Error('Portail de la douane inaccessible')
    }

    await page.goto(baseURL+"/service-en-ligne/redirection/PORTAIL_VITI");
    this.log("Redirection OK");

    await page.waitForSelector('.btn-primary');
    await page.waitForSelector("form");

    this.log("Portail VITI: OK");
    return page;
}
