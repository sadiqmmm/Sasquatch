$(function() {
	var top = $('.submenu, .submenu-top').offset().top - parseFloat($('.submenu, .submenu-top').css('margin-top').replace(/auto/, 0));
	$(window).scroll(function (event) {
	  // what the y position of the scroll is
	  var y = $(this).scrollTop();

	  // whether that's below
	  if (y >= top) {
		// if so, ad the fixed class
		$('.submenu, .submenu-top').addClass('fixed');
	  } else {
		// otherwise remove it
		$('.submenu, .submenu-top').removeClass('fixed');
	  }
	});
});