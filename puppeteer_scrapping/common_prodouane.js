const puppeteer = require('puppeteer');
const fs = require('fs');

var browser;

const baseURL = 'https://www.douane.gouv.fr';
exports.baseURL = baseURL;
exports.page = null;

exports.close = async function() {
    await this.saveCookie(this.page);
    return await browser.close();
}

exports.log = function (message) {
    if (process.env.DEBUG) {
        console.log(message + "\n===================")
    }
}

exports.openpage = async function () {
    if (!process.env.DEBUG && (process.env.DEBUG_WITH_BROWSER != undefined)) {
        process.env.DEBUG = 1;
    }

    browser = await puppeteer.launch({
      headless: !(process.env.DEBUG_WITH_BROWSER),  //mettre à false pour debug
      defaultViewport: {width: 1920, height: 1080},
      ignoreDefaultArgs: ['--disable-extensions'],
      args: ['--no-sandbox', '--disable-setuid-sandbox'],
    });

    this.log('');

    const page = await browser.newPage();
    this.page = page;
    return page

}

exports.openpage_and_login = async function () {

    const page = await this.openpage();
    this.page = page;

    if(!process.env.PRODOUANE_USER){
      await browser.close();
      throw "Initialisez la variable d'environnement PRODOUANE_USER avec le login";
    }
    if(!process.env.PRODOUANE_PASS){
      await browser.close();
      throw "Initialisez la variable d'environnement PRODOUANE_PASS avec le mot de passe";
    }

    if (exports.loadCookie(page)) {
        var logged_OK = false;
        this.log("PORTAIL_VITI cookie connexion");
        page.goto(baseURL+"/service-en-ligne/redirection/PORTAIL_VITI");
        await page.waitForResponse( async (response) => {
            if (response.status() == 403) {
                if (response.url().match('redirection/PORTAIL_VITI')) {
                    logged_OK = true;
                    return true;
                }
            }
            if (response.status() == 200) {
                if (response.url().match('connexion.douane.gouv.fr')) {
                    return true;
                }
                if (response.url().match('portail.xhtml')) {
                    logged_OK = true;
                    return true;
                }
            }
            return false;
        });
        if (logged_OK) {
            this.log("Cookie loaded: OK");
            await page.waitForTimeout(250);
            await page.goto(baseURL+"/service-en-ligne/redirection/PORTAIL_VITI");
            this.log("Redirect PORTAIL_VITI");
            await page.waitForSelector('.btn-primary');
            await page.waitForSelector("form");
            this.log("Portail VITI: OK");
            return page;
        }
        this.log("Cookie: outdated");
    }
    await page.goto("https://connexion.douane.gouv.fr/")

    await page.click('#loginIdentifiant');
    await page.waitForSelector('#loginIdentifiant')
              .then(() => this.log("Login page: OK"));

    await page.type('#loginIdentifiant', process.env.PRODOUANE_USER);
    await page.type('#loginMotdepasse', process.env.PRODOUANE_PASS);
    await page.waitForTimeout(50);
    await page.keyboard.press('Enter')
                       .then(() => this.log("Login: OK"));

    await page.waitForSelector('body');
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

    exports.saveCookie(page);
    return page;
}


exports.saveCookie = async (page) => {
    const cookies = await page.cookies();
    const cookieJson = JSON.stringify(cookies, null, 2);
    await fs.writeFile('/tmp/prodouane_cookies.'+process.env.PRODOUANE_USER+'.json', cookieJson,  err => { if (err) { console.error('ERROR: saveCookie: '+ err); } } );
    this.log("saveCookie in "+'/tmp/prodouane_cookies.'+process.env.PRODOUANE_USER+'.json');
}

//load cookie function
exports.loadCookie = async (page) => {
    if (!fs.existsSync('/tmp/prodouane_cookies.'+process.env.PRODOUANE_USER+'.json')) {
        this.log('loadCookie: no file');
        return false;
    }
    return await fs.readFile('/tmp/prodouane_cookies.'+process.env.PRODOUANE_USER+'.json', (err, data) => {
        if (err) {
            console.error('ERROR: loadCookie: '+ err);
        }
        const cookieJson = data.toString();
        if (! cookieJson) {
            this.log('loadCookie: no json');
            return false;
        }
        const cookies = JSON.parse(cookieJson);
        page.setCookie(...cookies);
        this.log("cookies loaded");
        return true;
    } );
}
