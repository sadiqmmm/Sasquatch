exports.loadData = function(data, callback){
  console.log("view ready:index");
  callback({
		heading: data.heading,
		message: "Hey, here is a different message"
	});
};

exports.onReady = function(){
  console.log("view ready:index");
};

exports.onFinished = function(){
  console.log("view exiting:index");
};
