var system = require('system');
var id = system.args[2];
var cookie = system.args[3];
var fs = require('fs');

var page = require('webpage').create();
var annee = '2016'

//page.settings.userAgent = "Mozilla/5.0 (X11; Linux x86_64; rv:43.0) Gecko/20100101 Firefox/43.0 Iceweasel/43.0.4";

phantom.addCookie({
  'name':     'ASP.NET_SessionId',
  'value':    cookie,
  'domain':   system.args[1],
  'path':     '/',
  'httponly': true,
  'secure':   false,
  'expires':  (new Date()).getTime() + (1000 * 60 * 60 * 240)   /* <-- expires in 24 hour */
});



function downloadBeforeDrev(id) {
  page.open("http://"+system.args[1]+"/DREV/DREV2/BeforeDrev2.aspx?site=SGV&code_ident_site="+id, function(status) {
    // page.render('beforedev.png');
    if (status != "success") {
      page.open("http://"+system.args[1]+"/default.aspx?AbandonSession=1", function(statuts) {
        phantom.exit();
      });
    }else {
      setTimeout(function() {
        var html = page.evaluate(function () {
          return document.all[0].outerHTML+"";
        });
        if (html.length == 13912) {
          console.log('ERROR: Unexpected login page for '+id+' :()');
          page.open("http://"+system.args[1]+"/default.aspx?AbandonSession=1", function(statuts) {
            phantom.exit();
          });
        } else {
          fs.write("html/breforedrev_"+id+".html", html, 'w');
          var cle_evvs = page.evaluate(function() {
              var evvs = [];
              for (drevChildIndex in document.getElementById("ctl00_ContentPlaceHolder1_ddEVV").children) {
                  drevChild = document.getElementById("ctl00_ContentPlaceHolder1_ddEVV").children[drevChildIndex];
                  if(drevChild.value) {
                      evvs.push(drevChild.value);
                  }
              }

              return evvs;
          });
          for(cle_evv_index in cle_evvs) {
              downloadDrev(id, cle_evvs[cle_evv_index], annee);
          }
        }
      }, 2000);
    }
  });
}

function downloadDrev(id, cle_evv, campagne) {
  page.open("http://"+system.args[1]+"/DREV/DREV2/drev.aspx?code_ident_site="+id+"&site=SGV&cle_evv="+cle_evv+"&mill="+campagne, function(status) {
    setTimeout(function() {
      // page.render('drev.png');
      var html = page.evaluate(function () {
        return document.all[0].outerHTML+"";
      });
      fs.write("html/drev_"+id+"_"+annee+".html", html, 'w');
      console.log("DRev "+annee+" of "+id+" saved");
      phantom.exit();
    }, 2000);
  });
}

downloadBeforeDrev(id);
