
exports.loadData = function(data, callback){
	Services.getTodo(data.name, function(tasks) {
		callback({
			name: data.name,
			tasks: tasks
		});
	});
};

exports.onReady = function(){
	$('#new_task').when('submit', function(e) {
		e.preventDefault();
		var todo = $('.todo_name').val();
		var task = $('.task').val();
		Services.addTask(todo, task, function(result) {
			console.log(result)
			var partial = $.partial('task', {task:task});
			$('.task_list').append(partial);
		});
		$('#new_task input.task').val('');
		return false;
	});
};

exports.onFinished = function(){
    console.log("view exiting:todo");
};

