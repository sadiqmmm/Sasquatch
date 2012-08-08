Services = {
	todos: {},
	addTodo: function(todo_name, callback) {
		var todo = Services.createNewTodo(todo_name); //create new todo list and add to todo object
		callback(todo); // return newly created todo
	},
	createNewTodo: function(name) {
		Services.todos[name] = {
			tasks: []
		};
		return Services.todos[name];
	},
	getTodo: function(todo_name, callback) {
		var todo = Services.todos[todo_name]; //find todo
		callback(todo ? todo.tasks : []); //return todo tasks if found, else return empty list
	},
	addTask: function(todo, task, callback) {
		Services.todos[todo].tasks.push(task); //add task to todo list
		callback({success:true, pos:Services.todos[todo].tasks.length - 1}); //return successful and position task was added in list
	},
	listTodos: function(callback) {
		callback(Services.todos); //return todo object
	},
	completeTask: function(todo, task, callback) {
		Services.todos[todo].tasks.splice(task, 1); // remove task from list of task
		callback({success:true}); //return successful
	}
}