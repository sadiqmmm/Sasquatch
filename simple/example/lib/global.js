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
	
    $.activeView = function(){
        return $("#view");
    };
    
    var applyView = function(name, data){
        var view = $._views[name];
        var exports = { urlData : data };
        view.fn(exports);
        
        var renderTemplate = function(data){
            console.log("renderTemplate", data)
            var html = view.template(data);//TODO
            $($.config.rootElement).html(html);
            exports.onReady();
        }
        if("loadData" in exports){
            return exports.loadData(renderTemplate);
        }
        renderTemplate(data);
    };
	
	//************
	//	Query String to Javascript Object
	//************
	function qs2obj(qs){
		var qp = {};
		if(qs && qs.length > 0){
			var pairs = qs.split("&");
			var len = pairs.length;
			while(len--){
				var nv = pairs[len].split("=");
				if(nv.length == 2){
					qp[nv[0]] = nv[1];
				}
			}
		}
		return qp;
	}
	
	function stateChanged(){
		var state = $.History.getState();
		var parts = state.split("?");
		var view = parts[0];
		var qp = null;
		if(parts.length > 1){
			qp = qs2obj(parts[1]);
		}
		if(!qp) qp = {};
		applyView(view, qp);	
	}
	
	$.History.bind(function(state){
		if(state != $.lastState){
			console.log("state change >> " + state);
			stateChanged(state);
			$.lastState = state;
		}
	});
	
	if($.History.getHash() == ""){
		$.History.setHash($.config.defaultView);
	}
	
})(jQuery)

