$(function() {
	if ($('.qugcourses').length == 0) {
		return;
	}
	var listCol1 = $('<div id="listCol1"></div>')
   var listCol2 = $('<div id="listCol2"></div>')
   var col1Height = 0;
   var col2Height = 0;
   $('#textcontainer').after(listCol2);
   $('#textcontainer').after(listCol1);
   $('.qugcourses').each(function() {
      $(this).removeClass('qugcourses');
      if (col1Height <= col2Height) {
         $(this).detach().appendTo('#listCol1');
         col1Height += $(this).height();
      }
      else {
         $(this).detach().appendTo('#listCol2');
         col2Height += $(this).height();
      }
   });
   listCol1.addClass('qugcourses');
   listCol2.addClass('qugcourses');
});
