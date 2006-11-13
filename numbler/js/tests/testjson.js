

if(load) {
	load("../../mochikit/Base.js");
	load("../../mochikit/Iter.js");
	load("../simplejson.js");
 }

if(!assertequal) {
	var assertequal = function(a,b) {
		if(a != b) {
			throw "assertion error: " + a + " not equal to " + b
		}
		print('success:',a);
	};
 };

var basictest = {'foo':1,"bar":2};
var recursiveObj = {'obj1':basictest,'obj2':{'testobject':null,'testattr':43}};
var helperTestObj = function() {
	this.val1 = 'this is value 1'
	this.val2 = 'this is value 2'
	this.val3 = 'this is value 3'

	this.keys = ['val1','val2']
	this.toJSON = function() {
		return simpleJSON(this,this.keys);
	}

};

var embeddedObjects = {'basic':basictest,'withhelper':new helperTestObj()};
var embeddedArray = {'basic':basictest,arrObj:[1,2,3,4,new helperTestObj()]}

assertequal(simpleJSON(basictest),'{"foo":1,"bar":2}');
assertequal(simpleJSON(embeddedObjects),'{"basic":{"foo":1,"bar":2},"withhelper":{"val1":"this is value 1","val2":"this is value 2"}}');
assertequal(simpleJSON(embeddedArray),'{"basic":{"foo":1,"bar":2},"arrObj":[1,2,3,4,{"val1":"this is value 1","val2":"this is value 2"}]}');
