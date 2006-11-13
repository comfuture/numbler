dojo.provide("dojo.rpc.JsonService");
dojo.require("dojo.rpc.RpcService");
dojo.require("dojo.io.*");
dojo.require("dojo.json");
dojo.require("dojo.lang");

dojo.rpc.JsonService = function(url){
	if(url){
		this.connect(url);
	}
}

dojo.inherits(dojo.rpc.JsonService, dojo.rpc.RpcService);

dojo.lang.extend(dojo.rpc.JsonService, {

	lastSubmissionId:0,

	bind: function(method,parameters,deferredRequestHandler) {
		dojo.io.bind({
			url: this.serviceURL,
			postContent: this.createRequest(method,parameters),
			method: "POST",
			mimetype: "text/json",
			load: this.resultCallback(deferredRequestHandler) 
		});
	},

	createRequest: function(method,params){
		var req = { "params": params, "method": method, "id": this.lastSubmissionId++ };
		data = dojo.json.serialize(req);
		dojo.debug("JsonService: JSON-RPC Request: " + data);
		return data;
	},

	parseResults: function(object){
		return object.result;
	}
});
