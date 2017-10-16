var system = require('system');
var id = system.args[2];
var fs = require('fs');

var page = require('webpage').create();
id = 100;

console.log("begin at "+id);

page.onLoadStarted = function () {console.log("page started");} ;

function downloadIdentite(id) {
    page.open("http://"+system.args[1]+"/identitydetails3.aspx?site=IVS&code_ident_site="+id, function(status) {
	console.log("status: "+status);
	if (status != "success") {
	    phantom.exit();	
	}
	var html = page.evaluate(function () {
	    return document.all[0].outerHTML+"";
	});
	console.log("html: "+html.length);

	consol.log("length OK");
	ret = 0;
	fs.write("html/"+id+".html", html, 'w');
	consol.log("ret: "+ret);
	if (!ret) {
	    phantom.exit();	
	}
	console.log("http://"+system.args[1]+"/identitydetails3.aspx?site=IVS&code_ident_site="+id+" DONE");
	if (id > 2600) {
	    phantom.exit();
	}
	id++;
	setTimeout(function() {downloadIdentite(id);}, 200);
    });
}

downloadIdentite(id);

