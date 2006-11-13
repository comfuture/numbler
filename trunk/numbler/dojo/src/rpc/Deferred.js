dojo.provide("dojo.rpc.Deferred");
dojo.require("dojo.lang");

dojo.rpc.Deferred = function(){
	this._callbacks = [];
	this._errbacks = [];
	this.results = null;
	this.error = null;
};

dojo.lang.extend(dojo.rpc.Deferred, {
	
	getFunctionFromArgs: function(){
		var a = arguments;
		if((a[0])&&(!a[1])){
			if(dojo.lang.isFunction(a[0])){
				return a[0];
			}else if(dojo.lang.isString(a[0])){
				return dj_global[a[0]];
			}
		}else if((a[0])&&(a[1])){
			return dojo.lang.hitch(a[0], a[1]);
		}
		return null;
	},

	addCallback: function(cb, cbfn){
		var enclosed = this.getFunctionFromArgs(cb, cbfn)
		if(enclosed){
			this._callbacks.push(enclosed);
			if(this.results){
				enclosed(this.results);
			}
		}else{
			dojo.raise("Deferred: object supplied to addCallback is not a function");
		}
	},

	addErrback: function(eb, ebfn){
		var enclosed = this.getFunctionFromArgs(eb, ebfn)
		if(enclosed){
			this._errbacks.push(enclosed);
			if(this.error){
				enclosed(this.error);
			}	
		}else{
			dojo.raise("Deferred: object supplied to addErrback is not a function");
		}
	},

	addBoth: function(cb, eb){
		this.addCallback(cb);
		this.addErrback(eb);
	},

	callback: function(results){
		this.results = results;
		dojo.lang.forEach(this._callbacks, function(func){
			func(results);
		});
	},

	errback: function(error){
		this.error = error;
		dojo.lang.forEach(this._errbacks, function(func){
			func(error);
		});
	}

});
