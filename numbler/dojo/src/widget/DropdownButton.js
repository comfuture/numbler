dojo.provide("dojo.widget.DropdownButton");

// Draws a button with a down arrow;
// when you press the down arrow something appears (usually a menu)

dojo.require("dojo.widget.*");

dojo.widget.tags.addParseTreeHandler("dojo:dropdownbutton");

dojo.widget.DropdownButton = function(){
	dojo.widget.Widget.call(this);

	this.widgetType = "DropdownButton";
}
dojo.inherits(dojo.widget.DropdownButton, dojo.widget.Widget);

dojo.requireAfterIf("html", "dojo.widget.html.DropdownButton");
