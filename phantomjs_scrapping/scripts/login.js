var system = require('system');
var page = require('webpage').create();

page.open("http://"+system.args[1], function(status) {
  setTimeout(function() {
    page.sendEvent('keypress', page.event.key['Tab']);
    page.sendEvent('keypress', system.args[2]);
    page.sendEvent('keypress', page.event.key['Tab']);
    page.sendEvent('keypress', system.args[3]);
    page.sendEvent('keypress', page.event.key['Tab']);
    page.sendEvent('keypress', page.event.key['Enter']);
  }, 1000);
  setTimeout(function() {
    //    page.render('page01.png');
    var cookies = page.cookies;
    for(var i in cookies) {
      console.log(cookies[i].name + '=' + cookies[i].value);
    } 
    phantom.exit();
  }, 5000);
});
