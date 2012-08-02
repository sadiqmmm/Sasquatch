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

	$.parallel = function(){
		var _callback,
		_results = [],
		_finished = 0,
		_jobs = [],
		_started = false,
		_errored=false,
		_error;

		// strips the first argument
		function cut(list){
			var len = list.length;
			var result = [];
			for(var x=1; x<len; x++){
				result.push(list[x]);
			}
			return result;
		}

		function start_job(index){
			var job = _jobs[index];
			var func = job[0];
			var inner_callback = function(err, result){
				if(_errored){ return console.log("errored out."); }
				if(err){ console.log("error on callback"); _errored = true; return _error(err); }

				_results[index] = result;
				_finished += 1;
				if(_finished >= _jobs.length){
					_callback.apply(this, _results);
				}
			};
			var args = job[1].concat([inner_callback]);
			func.apply(this, args);
		}

		function check(){
			if( _started ) { throw Error("Already started."); }
		}
		return {
			add : function(func){
				check();
				_jobs.push([func, cut(arguments)]);
				return this;
			},
			response : function(func){
				check();
				_callback = func;
				return this;
			},
			error : function(func){
				check();
				_error = func;
				return this;
			},
			go : function(){
				for(var x=0; x<_jobs.length; x++){
					start_job(x)
				}

				_started = true;
			}
		};
	}

})(jQuery);

