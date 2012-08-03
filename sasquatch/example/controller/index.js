exports.loadData = function(data, callback){
  console.log("view ready:index");
  callback({
		heading: "This is a sample title",
		message: "Hey, here is a cool message"
	});
};

exports.onReady = function(){
  console.log("view ready:index");
	$('h2').when('click', function() {
		$.go('second', {heading: "This is another page"});
	});
};

exports.onFinished = function(){
  console.log("view exiting:index");
};
