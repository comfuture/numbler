/* Copyright (C) 2006 Numbler LLC */
/* See LICENSE for details. */

if(typeof(LiveSheet) == 'undefined') {
  LiveSheet = {};
 };

LiveSheet.colChanger = function() {
  this.el = null;
  this.init();
  dojo.event.browser.addListener(getElement('colcontainer'),'mousedown',bind(this.onmousedown,this),false);
  dojo.event.browser.addListener(getElement('colcontainer'),'mousemove',bind(this.onmousemove,this),false);
  dojo.event.browser.addListener(getElement('colcontainer'),'mouseup',bind(this.onmouseup,this),false);
};

LiveSheet.colChanger.prototype.init = function() {
  this.mousedown = false;
  this.col = -1;
  this.tracking = false;
  this.el = null; // we don't need to remove this div because we have already redrawn the viewport
  this.startX = 0;
};

LiveSheet.colChanger.prototype.onmousedown = function(ev) {
  if(!this.mousedown) {
    this.mousedown = true;
    // grab the current column from the target element          
    var id = ev.target.id;
    if(id.slice(0,2) == "cm") {
      this.tracking = true;
      this.col = id.slice(2);
      this.col--; // we really are targeting the previous cell!

      this.el = DIV({'id':'columnmover','style':
                      {'height':(currentsheet.viewArea.toppos + currentsheet.calcmaxheight()) + "px"}});
      currentsheet.parentdiv.appendChild(this.el);
      this.move(ev);
      this.startX = ev.pageX || ev.clientX + document.body.scrollLeft;
    }
  };
  ev.stopPropagation();
};

LiveSheet.colChanger.prototype.move = function(ev) {
  var x = ev.pageX || ev.clientX + document.body.scrollLeft;
  x = currentsheet.viewArea.leftpos + (x - getElement('colcontainer').offsetLeft);

  this.el.style.left = x + "px";
  this.el.style.right = (x + 1) + "px";
};

LiveSheet.colChanger.prototype.onmousemove = function(ev) {
  if(this.tracking) {
    this.move(ev);
  }
  ev.stopPropagation();
};

LiveSheet.colChanger.prototype.onmouseup = function(ev) {
  if(this.tracking) {
    log('colChanger: onmouseup');
    // resize it
    var oldwidth = width = currentsheet.dimManager.coldims(this.col).val;
    var x = ev.pageX || ev.clientX + document.body.scrollLeft;
    width += (x - this.startX);

    var undo = new LiveSheet.ColWidthUndo(this.col,oldwidth,width);
    undo.doAction();
  }
  this.init();
  ev.stopPropagation();
};

LiveSheet.rowChanger = function() {
  this.el = null;
  this.init();
  dojo.event.browser.addListener(getElement('rowcontainer'),'mousedown',bind(this.onmousedown,this),false);
  dojo.event.browser.addListener(getElement('rowcontainer'),'mousemove',bind(this.onmousemove,this),false);
  dojo.event.browser.addListener(getElement('rowcontainer'),'mouseup',bind(this.onmouseup,this),false);
};

LiveSheet.rowChanger.prototype.init = function() {
  this.mousedown = false;
  this.row = -1;
  this.tracking = false;
  this.el = null;
  this.startY = 0;
};

LiveSheet.rowChanger.prototype.onmousedown = function(ev) {
  if(!this.mousedown) {
    this.mousedown = true;
    // grab the current column from the target element          
    var id = ev.target.id;
    if(id.slice(0,2) == "rm") {
      this.tracking = true;
      this.row = id.slice(2);
      this.row--; // we really are targeting the previous cell!

      this.el = DIV({'id':'rowmover','style':
                      {'width':(currentsheet.viewArea.leftpos + currentsheet.calcmaxwidth()) + "px"}});
      currentsheet.parentdiv.appendChild(this.el);
      this.move(ev);
      this.startY = ev.pageY || ev.clientY + document.body.scrollTop;
    }
  };
  ev.stopPropagation();
};

LiveSheet.rowChanger.prototype.move = function(ev) {
  var y = ev.pageY || ev.clientY + document.body.scrollTop;
  y = currentsheet.viewArea.toppos + (y - getElement('rowcontainer').offsetTop);
  this.el.style.top = y + "px";
  this.el.style.bottom = (y + 1) + "px";
};

LiveSheet.rowChanger.prototype.onmousemove = function(ev) {
  if(this.tracking) {
    this.move(ev);
  }
  ev.stopPropagation();
};

LiveSheet.rowChanger.prototype.onmouseup = function(ev) {
  if(this.tracking) {
    log('colChanger: onmouseup');
    // resize it
    var oldheight = height = currentsheet.dimManager.rowdims(this.row).val;
    var y = ev.pageY || ev.clientY + document.body.scrollTop;
    height += (y - this.startY);

    var undo = new LiveSheet.RowHeightUndo(this.row,oldheight,height);
    undo.doAction();
                
  }
  this.init();
  ev.stopPropagation();
};


LiveSheet.ColWidthUndo = function(col,oldwidth,width) {
  LiveSheet.UndoObject.call(this);
  this.col = col;
  this.oldwidth = oldwidth;
  this.width = width;
};

dojo.inherits(LiveSheet.ColWidthUndo,LiveSheet.UndoObject);

dojo.lang.extend(LiveSheet.ColWidthUndo, {
    //LiveSheet.ColWidthUndo.prototype = {
  onSuccess:function(args) {
    undoManager.add(this);
   },
  undo:function() {
    currentsheet.AdjustColumnWidth(this.col,this.oldwidth);
    return sheetServer.callRemote('onColumnWidthChange',this.col,this.oldwidth);  
  },
  redo:function() {
    currentsheet.AdjustColumnWidth(this.col,this.width);
    return sheetServer.callRemote('onColumnWidthChange',this.col,this.width);  
  },
  doAction:function() {
    this.redo().addCallback(bind(this.onSuccess,this));
  },
  valid:function() {
    var width = currentsheet.dimManager.coldims(this.col).val;
    return width == this.width;
  },
  userString:function() {
    return 'column width';
  }
  });


LiveSheet.RowHeightUndo = function(row,oldheight,height) {
  LiveSheet.UndoObject.call(this);
  this.row = row;
  this.oldheight = oldheight;
  this.height = height;
};

dojo.inherits(LiveSheet.RowHeightUndo,LiveSheet.UndoObject);

dojo.lang.extend(LiveSheet.RowHeightUndo, {
    //LiveSheet.RowHeightUndo.prototype = {
  onSuccess:function(args) {
    undoManager.add(this);
  },
  undo:function() {
    // TODO: we should have a call back handler here, right?
    currentsheet.AdjustRowHeight(this.row,this.oldheight);                  
    return sheetServer.callRemote('onRowHeightChange',this.row,this.oldheight);
  },
  redo:function() {
    currentsheet.AdjustRowHeight(this.row,height);
    return sheetServer.callRemote('onRowHeightChange',this.row,height);
  },
  doAction:function() {
    this.redo().addCallback(bind(this.onSuccess,this));
  },
  valid:function() {
    var height = currentsheet.dimManager.rowdims(this.row).val;
    return height == this.height;
  },
  userString:function() {
    return 'row height';
  }
});
