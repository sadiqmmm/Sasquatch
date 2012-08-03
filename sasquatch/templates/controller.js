{% autoescape off %}
//**************************************
//  START CONTROLLER SECTION
//**************************************
{% for view in views %}
//**************************************
// START CONTROLLER >> {{view.name}}
//**************************************
	jQuery.registerView("{{view.name}}", 
	//start internal func
	function(exports){
		{{view.controller}}
	}
	//end internal func
	, "{{view.template|escapejs}}");
//**************************************
// END CONTROLLER >> {{view.name}}
//**************************************
{% endfor %}
//**************************************
// END CONTROLLER SECTION
//**************************************
{% endautoescape %}