
exports.loadData = function(data, callback){
	Services.getTodo(data.name, function(tasks) { //Call services layer to see if there is a todo by that name
		callback({ //local vars
			name: data.name,
			tasks: tasks
		});
	});
};

exports.onReady = function(){
	$('#new_task').when('submit', function(e) { //event for adding a new event
		e.preventDefault();
		var todo = $('.todo_name').val(); //get todo list name
		var task = $('.task').val(); //get new task

		Services.addTask(todo, task, function(result) { //submit new task and add it to todo in service layer
			console.log(result)
			var partial = $.partial('task', {task:task, pos:result.pos}); //use partial to insert new task on page
			$('.task_list').append(partial);
		});
		$('#new_task input.task').val(''); //reset new task input
		return false;
	});

	$('.task_list').when('click', 'li', function() {
		var self = this;
		var task = $(this).attr('index'); //get task name we are removing
		var todo = $(this).closest('ul').attr('todo'); //get the todo list the task is in
		Services.completeTask(todo, task, function(result) { //call service layer to remove task from todo lisr
			$(self).remove(); //remove from dom
			$('.task_list li').each(function(i, v) {
				$(this).attr('index', i); //renumber index attributes to be the same as todo task array
			});
		});
	});
};

exports.onFinished = function(){
    console.log("view exiting:todo");
};

