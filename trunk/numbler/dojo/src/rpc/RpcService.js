dojo.provide("dojo.rpc.RpcService");
dojo.require("dojo.io.*");
dojo.require("dojo.json");
dojo.require("dojo.lang");
dojo.require("dojo.rpc.Deferred");

dojo.rpc.RpcService = function(url){
	if(url){
		this.connect(url);
	}
}

dojo.lang.extend(dojo.rpc.RpcService, {

	serviceURL: "",

	parseResults: function(object) {
		return object;
	},

	errorCallback: function (deferredRequestHandler) {
		var self = this;
		return function(type, object, e) {
			deferredRequestHandler.errback(e);
		}
	},

	resultCallback: function(deferredRequestHandler) {
		var self = this;
		return function(type, object, e) {
			var results = self.parseResults(object);
			deferredRequestHandler.callback(results); 
		};
	},


	generateMethod: function(method,parameters) {
		return function() {

			var deferredRequestHandler = new dojo.rpc.Deferred();

			if(parameters){
				var numberExpectedParameters = parameters.length;
			}else{
				var numberExpectedParameters = 0;
			}

			if(arguments.length != numberExpectedParameters){
				dojo.raise("Invalid number of parameters for remote method.");
				// put error stuff here, no enough params
			} else {
				this.bind(method,arguments,deferredRequestHandler);
			}

			return deferredRequestHandler;
		};
	},

	processSMD: function (type, object, e) {
		dojo.debug("RpcService: Processing returned SMD.");
		for(var n = 0; n < object.methods.length; n++){
			dojo.debug("RpcService: Creating Method: this." + object.methods[n].name + "()");
  			this[object.methods[n].name] = this.generateMethod(object.methods[n].name,object.methods[n].parameters);
			if (dojo.lang.isFunction(this[object.methods[n].name])) {
				dojo.debug("RpcService: Successfully created " + object.methods[n].name + "()");
			} else {
				dojo.debug("RpcService: Failed to create " + object.methods[n].name + "()");
			}
		}

		this.serviceURL = object.serviceURL;
		dojo.debug("RpcService: Dojo RpcService is ready for use.");
	},

	connect: function(smdURL){
		dojo.debug("RpcService: Attempting to load SMD document from " + smdURL);
		dojo.io.bind({
			url: smdURL,
			mimetype: "text/json",
			load: dojo.lang.hitch(this, function(type, object, e){ return this.processSMD(type,object,e) }),
			sync: true
		});		
	}
});
