$(document).ready(function() {
	$('pre.javascript').snippet('javascript', {style:"emacs"});
	$('pre.html').snippet('html', {style:"emacs"});
	$('pre.no-num').snippet('html', {style:"emacs", showNum:false});
});