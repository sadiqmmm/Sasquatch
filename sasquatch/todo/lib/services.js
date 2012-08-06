Services = {
	todos: {},
	addTodo: function(todo_name, callback) {
		var todo = Services.createNewTodo(todo_name);
		callback(todo);
	},
	createNewTodo: function(name) {
		Services.todos[name] = {
			tasks: []
		};
		return Services.todos[name];
	},
	getTodo: function(todo_name, callback) {
		var todo = Services.todos[todo_name];
		callback(todo ? todo.tasks : []);
	},
	addTask: function(todo, task, callback) {
		Services.todos[todo].tasks.push(task);
		callback({success:true});
	}
}