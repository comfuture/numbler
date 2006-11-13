/********************************************************************************
 ** (C) Numbler LLC 2006
 ********************************************************************************/

// drop down widget for displaying current undo actions

dojo.provide("LiveSheet.undodropdown");
dojo.require("dojo.widget.*");

LiveSheet.undodropdown = function() {
  dojo.widget.html.ToolbarDialog.call(this); // call superclass constructor
  for (var method in this.constructor.prototype) {
    this[method] = this.constructor.prototype[method];
  }
};

dojo.inherits(LiveSheet.undodropdown,dojo.widget.html.ToolbarDialog);

// isn't this just LiveSheet.undodropdown.prototype = ??
dojo.lang.extend(LiveSheet.undodropdown, {
//LiveSheet.undodropdown.prototype = {
  widgetType:'undodropdown',
  fillInTemplate: function (args, frag) {
	LiveSheet.undodropdown.superclass.fillInTemplate.call(this, args, frag);
	this.dialog = dojo.widget.createWidget("VariableDropDown",{actionstr:args.actionstr});
	this.dialog.domNode.style.position = "absolute";
	dojo.event.connect(this.dialog,'onSelect',this,'_onMultUndo');
  },
  _onMultUndo:function(count) {
	this._fireEvent("onMultipleUndo",count);
	this.deselect(true); // I think true is required because if count = size of list 
	// the widget could be disabled elsewhere.
  },
  showDialog: function(e) {
	LiveSheet.undodropdown.superclass.showDialog.call(this,e);
	var x = dojo.html.getAbsoluteX(this.domNode) - 32; // FIXME
	var y = dojo.html.getAbsoluteY(this.domNode) + dojo.html.getInnerHeight(this.domNode);
	this.dialog.showAt(x,y);
  },
  hideDialog: function(e) {
	LiveSheet.undodropdown.superclass.hideDialog.call(this,e);
	this.dialog.hide();
  },
  addUndo: function(obj) {
	this.dialog.push(obj);										 
  },
  removeUndo: function(count) {
	this.dialog.pop(count);
  },
  shiftUndo:function() {
	this.dialog.shift();
  }
});

dojo.widget.tags.addParseTreeHandler("dojo:undodropdown");


dojo.widget.tags.addParseTreeHandler("dojo:variabledropdown");

LiveSheet.VariableDropDown = function() {
  dojo.widget.HtmlWidget.call(this);
  this.count = 0;
};

dojo.inherits(LiveSheet.VariableDropDown,dojo.widget.HtmlWidget);

dojo.lang.extend(LiveSheet.VariableDropDown, {
//LiveSheet.VariableDropDown.prototype = {
	
  widgetType:"VariableDropDown",
  buildRendering: function() {
	this.domNode = DIV({'class':'variabledrop'},null);
	this.evCount = DIV({'id':'variablecount'});
	this.domNode.appendChild(this.evCount);
  },
  push:function(item) {
	var el = DIV(null,item.userString ? item.userString() : item.toString());
	dojo.event.connect(el,'onmouseover',this,'onmouseover');
	dojo.event.connect(el,'onmousedown',this,'click');
	el.dropindex = this.count++;
	this.domNode.insertBefore(el,this.domNode.childNodes[0]);
  },
  pop:function(count) {
	count = count || 1;
	if(this.count > 0) {
	  for(var i=Math.min(count,this.count)-1;i>=0;i--) {
		this.domNode.removeChild(this.domNode.childNodes[i]);
		--this.count;
	  }
	  return this.count;
	};
	return 0;
  },
  // remove the oldest item
  shift:function() {
	--this.count;
	this.domNode.removeChild(this.domNode.childNodes[this.count]);
	for(var i=0;i<this.count;i++) {
	  this.domNode.childNodes[i].dropindex--;
	}

  },
  hide:function() {
	if(this.domNode.parentNode) {
	  this.domNode.parentNode.removeChild(this.domNode);
	}
  },
  showAt:function(x,y) {
	this.evCount.innerHTML = "Cancel";
	this.drawhighlighted(this.count);
	with(this.domNode.style) {
	  top = y + "px"; left = x + "px";
	  zIndex = 999;
	}
	dojo.html.body().appendChild(this.domNode);
  },
  onmouseover:function(e) {
	this.drawhighlighted(e.currentTarget.dropindex);
  },
  drawhighlighted:function(index) {
	var hcount = 0;
	var midp = this.count - index;
	for(var i=0; i < midp;i++) {
	  hcount++;
	  var s = this.domNode.childNodes[i].style;
	  s.backgroundColor = "#316ac5";
	  s.color = "white";
	}
	for(i=midp;i<this.count;i++) {
	  var s = this.domNode.childNodes[i].style;
	  s.backgroundColor = "white";
	  s.color = "";
	}
	if(hcount > 0) {
	  this.evCount.innerHTML = [this.actionstr,hcount,' action',hcount == 1 ? '' : 's'].join('');
	}
  },
  click:function(e) {
	this.onSelect(this.count - e.currentTarget.dropindex);
  },
  onSelect:function(count) {}
		
});

