dojo.provide("dojo.widget.TabSet");
dojo.provide("dojo.widget.html.TabSet");
dojo.provide("dojo.widget.Tab");
dojo.provide("dojo.widget.html.Tab");

dojo.require("dojo.widget.*");
dojo.require("dojo.widget.LayoutPane");
dojo.require("dojo.event.*");
dojo.require("dojo.html");
dojo.require("dojo.style");

//////////////////////////////////////////
// TabSet -- a set of Tabs
//////////////////////////////////////////
dojo.widget.html.TabSet = function() {
	dojo.widget.html.LayoutPane.call(this);
}
dojo.inherits(dojo.widget.html.TabSet, dojo.widget.html.LayoutPane);

dojo.lang.extend(dojo.widget.html.TabSet, {
	widgetType: "TabSet",

	// Constructor arguments
	labelPosition: "top",
	useVisibility: false,		// true-->use visibility:hidden instead of display:none


	templateCssPath: dojo.uri.dojoUri("src/widget/templates/HtmlTabSet.css"),

	selectedTab: "",		// initially selected tab (widgetId)

	fillInTemplate: function(args, frag) {
		dojo.widget.html.TabSet.superclass.fillInTemplate.call(this, args, frag);
		
		dojo.style.insertCssFile(this.templateCssPath, null, true);
		dojo.html.prependClass(this.domNode, "dojoTabSet");
	},

	postCreate: function(args, frag) {
		// Create <ul> with special formatting to store all the tab labels
		// TODO: set "bottom" css tag if label is on bottom
		this.ul = document.createElement("ul");
		dojo.html.addClass(this.ul, "tabs");
		dojo.html.addClass(this.ul, this.labelPosition);

		// Load all the tabs, creating a label for each one
		for(var i=0; i<this.children.length; i++){
			this._setupTab(this.children[i]);
		}
		dojo.widget.html.TabSet.superclass.postCreate.call(this, args, frag);

		// Put tab labels in a panel on the top (or bottom)
		this.filterAllowed(this, 'labelPosition', ['top', 'bottom']);
		this.labelPanel = dojo.widget.createWidget("LayoutPane", {layoutAlign: this.labelPosition});
		this.labelPanel.domNode.appendChild(this.ul);
		dojo.widget.html.TabSet.superclass.addChild.call(this, this.labelPanel);
	},

	addChild: function(child){
		this._setupTab(child);
		dojo.widget.html.TabSet.superclass.addChild.call(this,child);
	},

	_setupTab: function(tab){
		tab.layoutAlign = "client";
		tab.domNode.style.display="none";
		dojo.html.prependClass(tab.domNode, "dojoTabPanel");

		// Create label
		tab.li = document.createElement("li");
		var span = document.createElement("span");
		span.innerHTML = tab.label;
		dojo.html.disableSelection(span);
		tab.li.appendChild(span);
		this.ul.appendChild(tab.li);
		
		var self = this;
		dojo.event.connect(tab.li, "onclick", function(){ self.selectTab(tab); });
		
		if(!this.selectedTabWidget || this.selectedTab==tab.widgetId || tab.selected){
			this.selectedTabWidget=tab;
		}
	},

	selectTab: function(tab) {
		// Deselect old tab and select new one
		if (this.selectedTabWidget) {
			this._hideTab(this.selectedTabWidget);
		}
		this.selectedTabWidget = tab;
		this._showTab(tab);
	},
	
	_showTab: function(tab) {
		dojo.html.addClass(tab.li, "current");
		tab.selected=true;
		if ( this.useVisibility && !dojo.render.html.ie ) {
			tab.domNode.style.visibility="visible";
		} else {
			tab.show();
		}
	},

	_hideTab: function(tab) {
		dojo.html.removeClass(tab.li, "current");
		tab.selected=false;
		if( this.useVisibility ){
			tab.domNode.style.visibility="hidden";
		}else{
			tab.hide();
		}
	},

	onResized: function() {
		// Display the selected tab
		if(this.selectedTabWidget){
			this.selectTab(this.selectedTabWidget);
		}
		dojo.widget.html.TabSet.superclass.onResized.call(this);
	}
});
dojo.widget.tags.addParseTreeHandler("dojo:TabSet");

// These arguments can be specified for the children of a TabSet.
// Since any widget can be specified as a TabSet child, mix them
// into the base widget class.  (This is a hack, but it's effective.)
dojo.lang.extend(dojo.widget.Widget, {
	label: "",
	selected: false	// is this tab currently selected?
});

// Deprecated class.  Tabset can take any widget as input.
// Use BasicPane, LayoutPane, etc.
dojo.widget.html.Tab = function() {
	dojo.widget.html.LayoutPane.call(this);
}
dojo.inherits(dojo.widget.html.Tab, dojo.widget.html.LayoutPane);
dojo.lang.extend(dojo.widget.html.Tab, {
	widgetType: "Tab"
});
dojo.widget.tags.addParseTreeHandler("dojo:Tab");

