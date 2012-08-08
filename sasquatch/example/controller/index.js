exports.loadData = function(data, callback){
  console.log("view ready:index");
  callback({
		heading: "This is a sample title",
		message: "Hey, here is a cool message"
	});
};

exports.onReady = function(){
  console.log("view ready:index");
	$('a.second-page').when('click', function() {
		$.go('second', {heading: "This is another page"});
		return false;
	});
	$('a.second-page-reaplce').when('click', function() {
		$.goReplace('second', {heading: "This is another page and replaced the previous hash"});
		return false;
	});
};

exports.onFinished = function(){
  console.log("view exiting:index");
};
