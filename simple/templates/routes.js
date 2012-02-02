{% autoescape off %}
//**************************************
//  START ROUTES SECTION
//**************************************
(function(){

//setup crossroads
$.routes = [];
crossroads.shouldTypecast = true;
crossroads.normalizeFn = function(request, vals){
    //will dispatch a single parameter (Object) with all the values
    return [vals];
};
	
{% for route in routes %}
//**************************************
// START ROUTE >> {{route.pattern}}
//**************************************

// {{route.priority}}
// {{route.params}}
// {{route.controller}}
var r = crossroads.addRoute("{{route.pattern}}", function(params){
	var controller = {% if route.controller %}"{{route.controller}}"{% else %}params.controller{% endif %};
	$.applyView(controller, params);
});
$.routes.push(r);

//**************************************
// END ROUTE >> {{route.pattern}}
//**************************************
{% endfor %}

//setup hasher
hasher.initialized.add(function(request){
	if(request == ""){
		arguments[0] = "/"
	}
	crossroads.parse.apply(crossroads, arguments);
}, crossroads);
hasher.changed.add(crossroads.parse, crossroads);

$(function(){
	hasher.init();
});


})();

//**************************************
// END ROUTE SECTION
//**************************************
{% endautoescape %}
