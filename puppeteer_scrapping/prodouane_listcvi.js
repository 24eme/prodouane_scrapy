const prodouane = require('./common_prodouane.js');
const fs = require('fs');

(async () => {
  try {

    page = await prodouane.openpage_and_login();

    await page.click("input[value='Fiche de compte']");
    await page.waitForSelector('.btn-primary');
    await page.waitForSelector('#formFdc\\:selectDepartement');

    await page.waitForTimeout(250);

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

        const cvis = await page.evaluate( () =>
          Array.from(document.querySelectorAll("tr[class='rf-dt-r']")).map(element=>Array.from(element.querySelectorAll("td")).map(element=>element.innerText))
        );

        for(var cvi of cvis){
            type = 'dr';
            if (cvi[4] == 'Cave coopérative') {
                type = 'sv11';
            } else if (cvi[4] == 'Négociant vinificateur') {
                type = 'sv12';
            }
            console.log(type+" "+cvi[1]);
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

    await prodouane.close();

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
