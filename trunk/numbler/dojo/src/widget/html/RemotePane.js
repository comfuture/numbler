dojo.provide("dojo.widget.RemotePane");
dojo.provide("dojo.widget.html.RemotePane");

//
// a div that loads from a URL.  (Similar to an iframe, but
// it's in the same environment as the main window)
//

dojo.require("dojo.widget.RemotePane");
dojo.require("dojo.widget.*");
dojo.require("dojo.event.*");
dojo.require("dojo.io.*");
dojo.require("dojo.widget.Container");
dojo.require("dojo.html");
dojo.require("dojo.style");
dojo.require("dojo.dom");
dojo.require("dojo.string");


dojo.widget.html.RemotePane = function(){
	dojo.widget.html.Container.call(this);
}

dojo.inherits(dojo.widget.html.RemotePane, dojo.widget.html.Container);

dojo.lang.extend(dojo.widget.html.RemotePane, {
	widgetType: "RemotePane",

	href: "about:blank",
	extractContent: true,
	parseContent: true,
	cacheContent: true,
	
	// To generate pane content from a java function
	handler: "none",

	// I'm using a template because the user may specify the input as
	// <a href="foo.html">label</a>, in which case we need to get rid of the
	// <a> because we don't want a link.
	templateString: '<div class="dojoRemotePane"></div>',

	fillInTemplate: function(args, frag){
		var source = this.getFragNodeRef(frag);

		// If user has specified node contents, they become the label
		// (markup in the link is not handled correctly, so don't use it)
		this.label += source.innerHTML;

		// Copy style info from input node to output node
		this.domNode.style.cssText = source.style.cssText;
		this.domNode["class"] = source["class"];
	},

	postCreate: function(args, frag, parentComp){
		if ( this.handler != "none" ){
			this.setHandler(this.handler);
		}
		if ( this.isVisible() ){
			this.loadContents();
		}
	},

	// If the pane contents are external then load them
	loadContents: function() {
		if ( this.isLoaded ){
			return;
		}
		if ( dojo.lang.isFunction(this.handler)) {
			this._runHandler();
		} else if ( this.href != "about:blank" ) {
			this._downloadExternalContent(this.href, this.cacheContent);
		}
		this.isLoaded=true;
	},

	// Reset the (external defined) content of this pane
	setUrl: function(url) {
		this.href = url;
		this.isLoaded = false;
		if ( this.isVisible() ){
			this.loadContents();
		}
	},

	_downloadExternalContent: function(url, useCache) {
		//dojo.debug(this.widgetId + " downloading " + url);
		var node = this.containerNode || this.domNode;
		node.innerHTML = "Loading...";

		var extract = this.extractContent;
		var parse = this.parseContent;
		var self = this;

		dojo.io.bind({
			url: url,
			useCache: useCache,
			mimetype: "text/html",
			handler: function(type, data, e) {
				if(type == "load") {
					if(extract) {
						var matches = data.match(/<body[^>]*>\s*([\s\S]+)\s*<\/body>/im);
						if(matches) { data = matches[1]; }
					}
					node.innerHTML = data;
					if(parse) {
						var parser = new dojo.xml.Parse();
						var frag = parser.parseElement(node, null, true);
						dojo.widget.getParser().createComponents(frag);
					}
					self.onResized();
				} else {
					node.innerHTML = "Error loading '" + url + "' (" + e.status + " " + e.statusText + ")";
				}
			}
		});
	},

	// Generate pane content from given java function
	setHandler: function(handler) {
		var fcn = dojo.lang.isFunction(handler) ? handler : window[handler];
		if(!dojo.lang.isFunction(fcn)) {
			throw new Error("Unable to set handler, '" + handler + "' not a function.");
			return;
		}
		this.handler = function() {
			return fcn.apply(this, arguments);
		}
	},

	_runHandler: function() {
		if(dojo.lang.isFunction(this.handler)) {
			this.handler(this, this.domNode);
			return false;
		}
		return true;
	}
});
