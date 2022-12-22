const prodouane = require('./common_prodouane.js');
const fs = require('fs');


(async () => {
  try {
    page = await prodouane.openpage_and_login();
    
    await page.click("input[value='Stock']");
    await page.waitForSelector('#formDeclaration');
    
    console.log("Click sur Stock OK");
    console.log("===================");
  
    if(!process.env.CVI){
      if(process.env.DEBUG){
        console.log("LISTER TOUS LES CVIS");
        console.log("===================");
      }
       
       //LISTER TOUS LES CVIS EN SORTIE STANDARD
     await prodouane.close();
     return;
    }
    
    
    await page.click("#formFiltre\\:inputNumeroCvi");
    await page.type('#formFiltre\\:inputNumeroCvi', process.env.CVI);    
    
    await page.click('input[value="Filtrer par EVV"]');
    
    console.log("Input CVI OK");
    console.log("===================");
    
    //verifier que le CVI existe 
    var hasError = (await page.$("#erreur\\:j_idt113")) || false;
    
    console.log(hasError);
    // 
    // if(hasError){
    //   console.log("");
    //   console.log('FAILED !! IL Y A UNE ERREUR CVI inconnu');
    //   await prodouane.close();
    //   return;
    // }    
    // 
                     
  }catch (e) {
    console.log("");
    console.log('FAILED !!');
    console.log(e);
    await prodouane.close();
  }
  
})();