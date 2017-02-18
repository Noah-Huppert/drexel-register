//Default tempalte js
//Store custom client js in /js/custom.js, and import to template.
function showCourse(domobj, which) {
	if (typeof coursebubblewidth == "undefined") {
		if(typeof bubblewidth == "undefined")
			var coursebubblewidth = 400;
		else
			var coursebubblewidth = bubblewidth;
	}
	function showCourseReady(req) {
		if($(req).find("course").length) {
			var html = $(req).find("course").text();
		} else {
			var html = "<p>Course information cannot be found. This course may " +
				"no longer be offered. If you believe there is an error or " +
				"require more information, please contact the course " +
				"department.</p>";
		}
		lfjs.bubble(domobj, html, {width:coursebubblewidth});
	}
	function showCourseError(req) {
		var html = "<p>An error occurred trying to load course information.  Please try your request again later. (" + req.status + " - " + req.statusText + ")</p>";
		lfjs.bubble(domobj, html, {
			width: coursebubblewidth
		});
	}
	domobj.blur();
	if(typeof ribbiturl == "undefined" || window.location.host.indexOf(".leepfrog.com") >= 0)
		ribbiturl = "/ribbit/index.cgi";
	var gcurl = ribbiturl + "?page=getcourse.rjs&code=" + encodeURIComponent(which);
	//if there is an edition var defined, use that in the getCourse call
	if(typeof edition == "string" && edition.length) {
		gcurl += "&edition=" + encodeURIComponent(edition);
	}
	$.ajax({
		url:gcurl,
		success:showCourseReady,
		error:showCourseError
	});
	lfjs.bubble(domobj, "Loading course description...", {width:coursebubblewidth});
	return false;
}

function showCourseEco(domobj, which) {
	if (typeof ecobubblewidth == "undefined") {
		if(typeof bubblewidth == "undefined")
			var ecobubblewidth = 600;
		else
			var ecobubblewidth = bubblewidth;
	}
	function showCourseEcoReady(req) {
		if($(req).find("courseeco").length) {
			var html = $(req).find("courseref").text();
		} else {
			var html = "<p>Unable to load course ecosystem.</p>";
		}
		lfjs.bubble(domobj, html, {width:ecobubblewidth});
	}
	function showCourseEcoError(req) {
		var html = "<p>An error occurred trying to load the course ecosystem." +
				"  ( " + req.status + " - " + req.statusText + ")</p>";
		lfjs.bubble(domobj, html, {
			width: ecobubblewidth
		});
	}
	domobj.blur();
	if(typeof ribbiturl == "undefined" || window.location.host.indexOf(".leepfrog.com") >= 0)
		ribbiturl = "/ribbit/index.cgi";
	$.ajax({
		url:ribbiturl + "?page=getcourseeco.rjs&code=" + encodeURIComponent(which),
		success:showCourseEcoReady,
		error:showCourseEcoError
	});
	lfjs.bubble(domobj, "Loading course ecosystem...", {width:ecobubblewidth});
	return false;
}

function printParent(el, removeel) {
	if (typeof removeel == "undefined")
		removeel = true;
	var html = $(el).parents("div:first").html();
	//strip out el
	if (removeel) {
		var outhtml = $("<p>").append($(el).clone()).html();
		html = html.replace(outhtml, "");
	}
	var new_win = window.open("","ppwin","resizable,height=300,width=450,scrollbars");
	new_win.document.write('<html><head><title>Course Detail</title></head><body>' +
		html + '</body></html>');
	new_win.document.close();
	$("link").each(function() {
		if(this.rel == "stylesheet") {
			$(new_win.document).find("head").append($(this).clone());
			$(new_win.document).find("body").css({"background-image": "none", "background-color": "white", "padding": "5px"});
		}
	})
	new_win.focus();
	new_win.print();
	new_win.close();
}

function showGenedCourselist(aEl) {
	var par = $(aEl).parents("table:first");
	if(!par.length)
		return;
	var head = $(aEl).attr("id").replace(/link$/, "");
	if (par.find('#' + head + 'courselist').length) {
		par.find('#' + head + 'courselist').slideToggle()
	} else {
		$(aEl).append('<div id="' + head + '" class="hiddencourselist">No Courses Defined For This Area</div>').slideDown();
	}
	$(aEl).parent("td").toggleClass("expanded");
	return false;
}

function escXML(str) {
	if(typeof str == "undefined")
		return "";
	var newStr = str.replace(/\&/g,'&amp;');
	newStr = newStr.replace(/\"/g,'&quot;');
	newStr = newStr.replace(/\</g,'&lt;');
	newStr = newStr.replace(/\>/g,'&gt;');

	return newStr;
}

//Tabs
$(function() {
	$(".tab_content").each(function() {
		var name = this.id.replace(/container$/, "")
		$(this).find("a[name='" + name + "']").remove();
	})
	if(typeof defshow != 'undefined')
		updateTabs(defshow);
	var page = window.location.href.replace(/\#.*$/, "").replace(/\/[^\/]*$/, "/");
	if(typeof bodycontainer == 'undefined')
		var bodycontainer = '#content';
	if(typeof validhashes == 'undefined')
		var validhashes = '';
	$(bodycontainer).find("a").each(function() {
		var href = $(this).attr("href")
		if(href) {
			var cleanhref = href.replace(page, "").replace(/^\#/, "");
			$(this).data("cleanhref", cleanhref);
			if(href.indexOf("#") == 0 && validhashes.indexOf("," + cleanhref + ",") != -1) {
				$(this).click(function(event) {
					showSection($(this).data("cleanhref"));
				})
			}
		}
	})
});
window.onhashchange = function() {
	var dest = window.location.hash.replace(/^\#/, "");
	if($("#" + dest + "container").length && $("#" + dest + "container").hasClass("tab_content") &&
			$("#" + dest + "container").is(":hidden")) {
		showSection(dest);
	}
}
function cleanHash(str) {
	return str.replace(/^\#/, "").replace(/([^\_]*)\_.*/, "$1");
}
function showSection(section) {
	$("#" + section + "tab").find("a").blur();

	$("#" + section + "tab").find("a").attr("target", "")
	if($("#" + section + "tab").hasClass("active"))
		return false;

	$(".tab_content").not("#" + section + "container").hide();
	$("#" + section + "container").show();
	updateTabs(section)
	var loc = window.location.href.replace(/\#[^\#]*$/, "") + "#" + section;
	//window.location.hash = section;
	window.location.replace(loc);
	return false;
}
function updateTabs(section) {
	//alert('******** Current Section: ' + section + ' ***********');
	$("#tabs li").not("#" + section + "tab").removeClass("active");
	$("#" + section + "tab").addClass("active");
}

function showPrintDialog() {
	if($("#print-dialog").length)
		$('#print-dialog')[0].activate();
}

function hidePrintDialog() {
	if($("#print-dialog").length)
		$('#print-dialog')[0].deactivate();
}

//Bubble width
var bubblewidth = 450;
