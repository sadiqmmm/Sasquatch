exports.loadData = function(data, callback){
  callback({
		heading: "My Simple Todo App"
	});
};

exports.onReady = function(){
  console.log("view ready:index");
};

exports.onFinished = function(){
  console.log("view exiting:index");
};
