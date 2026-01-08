const prodouane = require('./common_prodouane.js');
const fs = require('fs');

var page;
var browser;

(async () => {
 try {
     page = await prodouane.openpage_and_login();

     await page.click("input[value='VENDANGES']");

     await page.waitForSelector('.btnMenu');
     if(process.env.DEBUG){
       prodouane.log("Entrée dans Vendanges");
     }
     const has_ovnis = await page.$$('.table-title');

     if (has_ovnis.length) {
         if(process.env.DEBUG){
           prodouane.log("Selection d'un OVNIS");
         }

         await page.type('input.champRecherche', process.env.PRODOUANE_OVNI);
         await page.click('.material-icons');
     }

     await page.waitForSelector('.btnMenu');

     await page.click('.btnMenu');
     await page.waitForSelector('#inputNumeroCvi');

    await page.type('#inputNumeroCvi', process.env.CVI);
    await page.keyboard.press('Enter');

    await page.waitForResponse(async (response) => {
        if (response.status() != 200) {
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
