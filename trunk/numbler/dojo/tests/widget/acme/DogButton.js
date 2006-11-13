//
// User defined button widget
// that extends dojo's button widget by setting custom images
//
// In java terminology, this file defines
// a class called acme.DogButton that extends dojo.widget.Button2
//

dojo.provide("acme.DogButton");
dojo.require("dojo.widget.Button2");

// define DogButton's constructor
acme.DogButton = function(){
	// call superclass's constructor
	dojo.widget.html.Button2.call(this);
}

// set DogButton's superclass to Button2
dojo.inherits(acme.DogButton, dojo.widget.html.Button2);

// define DogButton's functions and variables
dojo.lang.extend(acme.DogButton, {
	widgetType: "DogButton",
	
	// override icons
	inactiveImg: "tests/widget/acme/dog-",
	activeImg: "tests/widget/acme/dogwag-",
	pressedImg: "tests/widget/acme/dogred-",
	disabledImg: "tests/widget/acme/dog-",
	width2height: 1.3
});

// setup 
dojo.widget.tags.addParseTreeHandler("dojo:dogbutton");