
function athenahelper(func) {
	return function() {
		var args = [arguments[arguments.length > 0 ? arguments.length-1 : 0]];
		for(var i=0;i<arguments.length-1;i++) {
			args.push(arguments[i]);
		}
		func.apply(this,args);
	}
};

function tester() {
	var dump = [];
	for(var i=0;i<arguments.length;i++) {
		dump.push(arguments[i]);
	}
	print(dump.join(','));
}
