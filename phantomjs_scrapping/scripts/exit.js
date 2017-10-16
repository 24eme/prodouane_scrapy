var system = require('system');
var cookie = system.args[2];
var fs = require('fs');

var page = require('webpage').create();

phantom.addCookie({
    'name':     'ASP.NET_SessionId',        /* required property */
    'value':    cookie, /* required property */
    'domain':   system.args[1],           /* required property */
    'path':     '/',
    'httponly': true,
    'secure':   false,
    'expires':  (new Date()).getTime() + (1000 * 60 * 60 * 24)   /* <-- expires in 1 hour */
});


page.open("http://"+system.args[1]+"/default.aspx?AbandonSession=1", function(statuts) {
                    phantom.exit();
});

