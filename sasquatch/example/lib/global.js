$.noop();//required by prod compiler!

(function($){

	$.ad = null;
	$.currentView = null;
	$.lastState = null;

// create data structure to hold views/templates
$._views = {};

$.registerView = function(name, fn, templ){
    $._views[name] = {
        "fn" : fn,
        "template" : _.template(templ)
    };
};

$.getView = function(name){
	var view = $._views[name];
	if(view == undefined){
		throw new Error("View is not defined: '" + name + "'");
	}
	return view;
};

$.activeView = function(){
    return $("#view");
};

$.applyView = function(name, data){
	if($.currentView){
		$.currentView.onFinished();
	}
	var view = $.getView(name);
    $.currentView = {};
    view.fn($.currentView);

    var renderTemplate = function(data){
      console.log("renderTemplate", data)
      var html = view.template(data);//TODO
      $($.config.rootElement).html(html);
			$(window).trigger('pageChange');
      $.currentView.onReady();
    }
    if("loadData" in $.currentView){
        return $.currentView.loadData(data, renderTemplate);
    }
    renderTemplate(data);
};

$.partial = function(name, data){
	var view = $.getView(name);
	var html = view.template(data);
	return html;
};

$.link = function(controller, opts){
	//_paramsIds
	var len = $.routes.length;
	for(var x=0; x<len; x++){
		var route = $.routes[x];
		if(!route.controller || route.controller == controller){
			var route_url = route._pattern;
			route_url = route_url.replace("{controller}", controller);
			if(opts){
				for(var prop in opts){
					route_url = route_url.replace("{"+prop+"}", opts[prop].toString());
					route_url = route_url.replace(":"+prop+":", opts[prop].toString());
				}
			}
			return route_url;
		}
	}
	throw new Error("Cannot match controller + params to a route.")
};

	$.go = function(controller, opts){
		var link = $.link(controller, opts);
		hasher.setHash(link);
	};

	$.goReplace = function(controller, opts, isQuiet){
		var link = $.link(controller, opts);
		if(isQuiet) {
			hasher.changed.active = false; //disable changed signal
			hasher.replaceHash(link); //set hash without dispatching changed signal
			hasher.changed.active = true; //re-enable signal
			return true;
		}
		hasher.replaceHash(link);
	};

	var offArr = [];

	$(window).on('pageChange', function() {
		_.each(offArr, function(ele, i) {
			$.fn.off(ele[0], ele[1], ele[2]);
		});
		offArr = [];
	});

	$.fn.when = function(types, selector, data, fn, one) {
		offArr.push([types, selector, fn]);
		$(this).on(types, selector, data, fn, one);
	}


})(jQuery);

