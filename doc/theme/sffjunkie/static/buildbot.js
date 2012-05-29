/** http://www.quirksmode.org/js/cookies.html */
function createCookie(name,value,days) {
	if (days) {
		var date = new Date();
		date.setTime(date.getTime()+(days*24*60*60*1000));
		var expires = "; expires="+date.toGMTString();
	}
	else var expires = "";
	document.cookie = name+"="+value+expires+"; path=/";
}

function readCookie(name) {
	var nameEQ = name + "=";
	var ca = document.cookie.split(';');
	for(var i=0;i < ca.length;i++) {
		var c = ca[i];
		while (c.charAt(0)==' ') c = c.substring(1,c.length);
		if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
	}
	return null;
}

function eraseCookie(name) {
	createCookie(name,"",-1);
}

$(document).ready(function(){
    var skip_hide = '<a class="class-hide" href="#"><img title="Hide Class Details" src="_static/minus.png" alt=""/></a>';
    $("dl.class").prepend(skip_hide)
    
/*    if (show_skip == '1') {
        $("#skip-links").show();
        $("#skip-hide").css("display", "block");
    }
    else {
        $("#skip-links").hide();
        $("#skip-show").css("display", "block");
    }
  
    $("#skip-hide").click(function() {
        $("#skip-links").hide();
        $("#skip-show").css("display", "block");
        $("#skip-hide").css("display", "none");
        createCookie("show_skip", "0", 31)
        return false;
    });
  
    $("#skip-show").click(function() {
        $("#skip-links").show();
        $("#skip-show").css("display", "none");
        $("#skip-hide").css("display", "block");
        createCookie("show_skip", "1", 31)
        return false;
    });
*/
});
