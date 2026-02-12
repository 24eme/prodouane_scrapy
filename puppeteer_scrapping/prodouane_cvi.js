const prodouane = require('./common_prodouane.js');
const fs = require('fs');

var page;
var browser;

(async () => {
 try {
     page = await prodouane.openpage_and_login();

     await page.click("input[value='VENDANGES']");

     await page.waitForSelector('.fr-col');
     if(process.env.DEBUG){
       prodouane.log("Entrée dans Vendanges");
     }
     await page.waitForTimeout(500);

     const has_ovnis = await page.url().includes('/ovnis');

     if (has_ovnis) {
         if(process.env.DEBUG){
           prodouane.log("Has OVNIS");
         }
         await page.waitForSelector('#blocSelectionIntervenant')

         const ovnis = await page.$$('#blocSelectionIntervenant tbody tr td:first-child');
         for (tr_ovnis of ovnis) {
             const name = await tr_ovnis.$("div div span");
             const o = await page.evaluate(name => name.innerText, name);
             if (o == process.env.PRODOUANE_OVNI) {
                if(process.env.DEBUG){
                    console.log("ovnis: ", o);
                }
             }
         }
         os = await tr_ovnis.$x('..');
         await page.evaluate(name => name.click('.material-icons'), os[0]);
         if(process.env.DEBUG){
           prodouane.log("OVNIS sélectionné");
         }
     }

     await page.waitForSelector('.btnMenu');

     await page.click('.btnMenu');
     await page.waitForSelector('#inputNumeroCvi');

    await page.type('#inputNumeroCvi', process.env.CVI);
    await page.keyboard.press('Enter');


    await page.waitForResponse(async (response) => {
        if (response.status() != 200 && response.status() != 404) {
            return false;
        }
        if (!response.url().match('rest/evvs')) {
            return false;
        }
        r = await response.text();
        console.log(r);
        prodouane.log('');
        return true;
    });

    await prodouane.saveCookie(page);
    await prodouane.close();

 }catch (e) {
  console.log("");
  console.log('FAILED !!');
  console.log(e);
  if(process.env.DEBUG){
    if (!page) {
        page = prodouane.page;
    }
    await page.screenshot({ path: '/tmp/screenshot_vendanges_error.png'})
    console.log('screenshot in /tmp/screenshot_vendanges_error.png')
  }
  await prodouane.close();
}
})();
