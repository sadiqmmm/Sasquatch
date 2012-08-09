$(function() {
	var top = $('.submenu').offset().top - parseFloat($('.submenu').css('margin-top').replace(/auto/, 0));
	$(window).scroll(function (event) {
	  // what the y position of the scroll is
	  var y = $(this).scrollTop();

	  // whether that's below
	  if (y >= top) {
		// if so, ad the fixed class
		$('.submenu').addClass('fixed');
	  } else {
		// otherwise remove it
		$('.submenu').removeClass('fixed');
	  }
	});
});