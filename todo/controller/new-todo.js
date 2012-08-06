
exports.loadData = function(data, callback){
    console.log("view ready:todo-new");
    callback({
			heading: "Create a New Todo List"
		});
};

exports.onReady = function(){
  console.log("view ready:todo-new");
	$('#new_todo').when('submit', function(e) {
		e.preventDefault();
		var todo_name = $('.todo_name').val()
		Services.addTodo(todo_name, function(result) {
			console.log(result);
			$.goReplace('todo', {name:todo_name});
		});
	});
};

exports.onFinished = function(){
    console.log("view exiting:todo-new");
};

