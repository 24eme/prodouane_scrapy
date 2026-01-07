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
       console.log("Entrée dans Vendanges");
       console.log("===================");
     }
     const has_ovnis = await page.$$('.table-title');

     if (has_ovnis.length) {
         if(process.env.DEBUG){
           console.log("Selection d'un OVNIS");
           console.log("===================");
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
        return true;
    });

    prodouane.close();

 }catch (e) {
  console.log("");
  console.log('FAILED !!');
  console.log(e);
  if(process.env.DEBUG){
    await page.screenshot({ path: '/tmp/screenshot_vendanges_error.png'})
    console.log('screenshot in /tmp/screenshot_vendanges_error.png')
  }
  await prodouane.close();
}
})();
