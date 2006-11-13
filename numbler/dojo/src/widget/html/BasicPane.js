dojo.provide("dojo.widget.html.BasicPane");

dojo.require("dojo.widget.*");
dojo.require("dojo.widget.Container");
dojo.require("dojo.widget.BasicPane");

dojo.widget.html.BasicPane = function(){
	dojo.widget.html.Container.call(this);
}
dojo.inherits(dojo.widget.html.BasicPane, dojo.widget.html.Container);

dojo.lang.extend(dojo.widget.html.BasicPane, {
	widgetType: "BasicPane"
});

dojo.widget.tags.addParseTreeHandler("dojo:BasicPane");
