exports.loadData = function(data, callback){
	Services.listTodos(function(todos) {
		callback({
			heading: "My Simple Todo App",
			todos: todos
		});
	});
};

exports.onReady = function(){
  console.log("view ready:index");
};

exports.onFinished = function(){
  console.log("view exiting:index");
};
