

var loadutils = function() {
  if(load) {
    load('../benchmark.js');
    if(typeof(DocUtils) == "undefined") {
      load('http://hali:8080/js/benchmark.js');
    }		
    if(typeof(DocUtils) == "undefined") {
      print("can't find benchmark.js... try rerunning if under the IE shell");
      return;
    };
  };
};


var runtest = function() {

  loadutils();

  print('running "in" performance test');
  var cache = {};
	
  bench = new DocUtils.benchmark();

  print('creating cache....');
  bench.mark();
  for(var i=0;i<10000;i++) {
    cache[Math.floor(Math.random()*10000)] = i;
  }
	
  print('building lookup list...');
  bench.mark();
  var lookuplist = [];
  for(i=0;i<100000;i++) {
    lookuplist.push(Math.floor(Math.random()*10000));
  }
	
  bench.mark();
  print('testing lookup with array test');
  var foundlist = [];
  for(i=0;i<lookuplist.length;i++) {
    if(typeof(cache[lookuplist[i]]) != undefined) {
      foundlist.push(cache[lookuplist[i]]);
    }
  }
	
  bench.mark();
  print('testing lookup with in syntax');
  foundlist = [];
  for(i=0;i<lookuplist.length;i++) {
    if(lookuplist[i] in cache) {
      foundlist.push(cache[lookuplist[i]]);
    }
  }
  bench.mark();
  bench.report();
};

var keytest = function() {

  loadutils();
  bench = new DocUtils.benchmark();



  var randcols = [];
  var randrows = [];
	
  for(i=0;i<100000;i++) {
    randcols.push(Math.floor(Math.random() * 255));
    randrows.push(Math.floor(Math.random() * 65536));
  }
  print('computing key with standard formula');
  bench.mark();
  for(i=0;i<100000;i++) {
    var key = 'k' + (randrows[i]*256 + randcols[i]);
  }

  print('computing key with new formula');
  bench.mark();
  for(i=0;i<100000;i++) {
    var key = 'k' + (randcols[i] << 16 | randrows[i]);
  }

  bench.mark();
  bench.report();

};

var bitarraytest = function() {

  loadutils();
  bench = new DocUtils.benchmark();

  var bittesters = [1,2,4,8,16,32,64,128,256,512,1024,2048,4096,8192,16384,32768,
		    65536,131072,262144,524288,1048576,2097152,4194304,8388608,
		    16777216,33554432,67108864,134217728,268435456,536870912,
		    1073741824,2147483648];


  bench.mark();
  var bitArray = [];
  var val;
  print('creating bit array');
  for(var i = 0;i< 100000;i++) {
    val = Math.floor(Math.random() * 2);
    // 		if( i % 32 == 0) {
    // 			bitArray[i >> 5] = 0;
    // 		}
    if(val) {
      bitArray[i >> 5] |= bittesters[i % 32]; 
    }
  }
  //print(bitArray);
  bench.mark();
  var testarray = [];
  print('creating normal test array');
  for(var i=0;i<100000;i++) {
    testarray[i] = Math.floor(Math.random()*2) ? true : false;
  }
  bench.mark();

  var count = 0;
  var j;
  for(i=0,j=0;i<100000;i++) {
    var t = bittesters[i % 32];
    if((bitArray[j] & t) == t) {
      count++;
    }
    if((i+1) % 32 == 0) {
      j++;
    }
  }
  bench.mark();
  print(count + ' positive values in the bit array, length is ' + bitArray.length);
  var count = 0;
  for(i=0;i<100000;i++) {
    if(testarray[i]) {
      count++;
    }
  }

  bench.mark();
  print(count + ' positive values in the normal array');
  bench.report();

};

function mathtest() {

  loadutils();
  bench = new DocUtils.benchmark();

  var randomrow = [];
  var randomcol = [];
  for(var i=0;i<100000;i++) {
    randomrow.push(Math.floor(Math.random() * 65536));
    randomcol.push(Math.floor(Math.random() * 255));
  };
	
  var val;
  bench.mark();
  print('computing key with multiplication');
  for(var i=0;i<100000;i++) {
    val = randomrow[i] * 256 + randomcol[i];
  };
  bench.mark();
  print('computing key with shifts');
  for(var i=0;i<100000;i++) {
    val = randomrow[i] << 8 + randomcol[i];
  }

  bench.mark();
  bench.report();


};

function objectDerefTest() {
  loadutils();
  bench = new DocUtils.benchmark();

  parent = {};
  parent.bar = 'fringle';

  parent.parent = {}
  parent.parent.parent = {}
  parent.parent.parent.parent = {}
  parent.parent.parent.parent.parent = {}
  parent.parent.parent.parent.parent.parent = {}
  parent.parent.parent.parent.parent.parent.parent = {}
  parent.parent.parent.parent.parent.parent.parent.parent = {}
  parent.parent.parent.parent.parent.parent.parent.parent.parent = {}
  parent.parent.parent.parent.parent.parent.parent.parent.parent.parent = {}
  parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.bar = 'fringle';

  bench.mark();
  for(var i=0;i<100000;i++) {
    var bing = parent.bar;
  }
  bench.mark();
  for(var i=0;i<100000;i++) {
    var bing = parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.bar;
  }
  bench.mark();
  bench.report();

}



function deepclone(obj) {
  var me = arguments.callee;
  if (arguments.length == 1) {
    me.prototype = obj;
    var ret = new me();
    for(prop in obj){
      var t= obj[prop];
      if(typeof(t) == "object") {
	print('deepcloning ',prop);
	ret[prop] = deepclone(t);
      }
    }
    return ret;
  }
}


function deepcopy(self, obj) {
  if (self == null) {
    self = {};
  }
  for (var k in obj) {
    var v = obj[k];
    if(typeof(v) == 'object') {
      if(self[k]) {
	arguments.callee(self[k],v);
      }
      else {
	self[k] = arguments.callee(null,v);
      }
    }
    else {
      self[k] = v;
    }
  }
  return self;
}

Object.prototype.toString = function() { 
  var l = []; for(item in this) {
    l.push(this[item].toString());
  }
  return l.join(' ');
};



function bigkeys() {
  loadutils();
  load('../../mochikit/MochiKit/Base.js');
  load('../../mochikit/MochiKit/Iter.js');

  bench = new DocUtils.benchmark();

  var gen = function() {
	return String.fromCharCode(32+ Math.floor(Math.random()*100));
  }

  var testlen = 10000;
  var numlookups = 100000;

  var gendict = function(dict,keylist,keylen) {
	for(var i=0;i<testlen;i++) {
	  var key = map(gen,range(1,keylen)).join('')
	  keylist.push(key)
	  dict[key] = i
	}
  }
  var runlookup = function(dict,keylist) {
	results = [];
	for(var i=0;i<numlookups;i++) {
	  var key = keylist[Math.floor(Math.random()*testlen)]
		results.push(testdict[key]);
	}
	return results;
  }


  testdict = {};
  testkeys = [];
  // generate a large number of keys for a dictionary
  bench.mark();
  print('generating dict');
  gendict(testdict,testkeys,50);
  bench.mark();
  results = [];
  print('testing lookup...');
  runlookup(testdict,testkeys);
  bench.mark();

  smallkeydict = {};
  smalltestkeys = [];
  print('generating small key dict');
  gendict(smallkeydict,smalltestkeys,5);
  bench.mark();
  print('testing lookup...');
  runlookup(smallkeydict,smalltestkeys);
  bench.mark();
  bench.report();
};

