(function($){

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
}
	
$.activeView = function(){
    return $("#view");
};
    
$.applyView = function(name, data){
    console.log("apply view", name);
	var view = $.getView(name);
    var exports = {};
    view.fn(exports);
        
    var renderTemplate = function(data){
        console.log("renderTemplate", data)
        var html = view.template(data);//TODO
        $($.config.rootElement).html(html);
        exports.onReady();
    }
    if("loadData" in exports){
        return exports.loadData(data, renderTemplate);
    }
    renderTemplate(data);
};

$.partial = function(name, data){
	var view = $.getView(name);
	var html = view.template(data);
	return html;
}

	
})(jQuery)

