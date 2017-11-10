var system = require('system');
var id = system.args[2];
var cookie = system.args[3];
var fs = require('fs');

var page = require('webpage').create();

console.log("begin at "+id);

//page.settings.userAgent = "Mozilla/5.0 (X11; Linux x86_64; rv:43.0) Gecko/20100101 Firefox/43.0 Iceweasel/43.0.4";

phantom.addCookie({
    'name':     'ASP.NET_SessionId',        /* required property */
    'value':    cookie, /* required property */
    'domain':   system.args[1],           /* required property */
    'path':     '/',
    'httponly': true,
    'secure':   false,
    'expires':  (new Date()).getTime() + (1000 * 60 * 60 * 240)   /* <-- expires in 24 hour */
});


page.onLoadStarted = function () {console.log("page started");} ;
//page.onLoadFinished = function() {console.log("page ended");};

nb = 0;

function downloadExtravitis(id) {
    page.open("http://"+system.args[1]+"/FicheIdentite/IdentityDetails.aspx?site=SGV&code_ident_site="+id, function(status) {
      console.log("status: "+status);
      if (status != "success") {
            page.open("http://"+system.args[1]+"/default.aspx?AbandonSession=1", function(statuts) {
		    phantom.exit();
	    });
      }else {
          setTimeout(function() {
          console.log("rendering...");
  	  var html = page.evaluate(function () {
	    return document.all[0].outerHTML+"";
	  });
	  console.log("html: "+html.length);
	  console.log("length OK");
	  if (id > 45555 || html.length == 13912 || nb++ > 1000) {
            console.log('fin');
            page.open("http://"+system.args[1]+"/default.aspx?AbandonSession=1", function(statuts) {
                    phantom.exit();
            });
	  }else {
	          fs.write("identites/"+id+".html", html, 'w');
	          console.log("http://"+system.args[1]+"/FicheIdentite/IdentityDetails.aspx?site=SGV&code_ident_site="+id+" DONE");

		  id++;
		  setTimeout(function() {downloadExtravitis(id);}, 200);
	  }
	}, 5000);
      }
    });
}

downloadExtravitis(id);
