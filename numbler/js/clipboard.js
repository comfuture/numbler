/* Copyright (C) 2006 Numbler LLC */
/* See LICENSE for details. */

if(typeof(DocUtils) == 'undefined') {
  var DocUtils = {};
 };

if(typeof(LiveSheet) == 'undefined') {
  LiveSheet = {};
 };

////////////////////////////////////////////////////////////////////////////////
// generic clipboard class
//
// right now this is little more than an array wrapper.  I wanted to wrap
// the interface because it might be interesting to sync this off to the server
//
////////////////////////////////////////////////////////////////////////////////


DocUtils.Clipboard = function(clipboardLength) {
  // default to 10 I suppose for now
  this.maxcount=  clipboardLength || 10;
  this.items = new Array();

  this.length = function() {
    return this.items.length;
  }

  this.empty = function() {
    return (this.items.length == 0) ? true : false;
  }
  this.clear = function() {
    this.items = new Array();
  }

  this.last = function() {
    if(this.items.length> 0) {
      return this.items[this.items.length-1];
    }
    return null;
  }
        
  this.pop = function() {
    return this.items.pop();
  }

  this.push = function(val) {
    if(this.items.length == this.maxcount) {
      this.items.shift(); // forget the oldest item
    }
    this.items.push(val);
  }

};

LiveSheet.CutUndo = function(startcell,endcell,sheet) {
  LiveSheet.UndoObject.call(this);
  this.startcell = LiveSheet.copyCell(startcell);
  this.endcell = LiveSheet.copyCell(endcell);
  this.sheet = sheet;
  this.copiedcells = null;
}


dojo.inherits(LiveSheet.CutUndo,LiveSheet.UndoObject);


dojo.lang.extend(LiveSheet.CutUndo, {
                //LiveSheet.CutUndo.prototype = {
  onSuccess:function(args) {
        undoManager.add(this);
  },
  undo:function() {
        // undo the cut operation by pasting the cells back.
        return sheetServer.callRemote('onPasteCellBuffer',this.copiedcells,this.startcell);
  },
  redo:function() {
        this.copiedcells = this.sheet.copyCells(this.startcell,this.endcell,true,true);
        this.clipitem = new LiveSheet.clipboardItem(this.copiedcells,
                                                    this.startcell,this.endcell,true);
        return sheetServer.callRemote('onCutCells',this.clipitem);
  },
  doAction:function() {
        this.redo().addCallback(bind(this.onSuccess,this));
        this.sheet.clipboard.push(this.clipitem);
  },
  valid:function() {
        for(var i=0;i<this.copiedcells.length;i++) {
          var existing = this.copiedcells[i];
          var c = this.sheet.cCache.getCellByAttr(existing.col,existing.row);
          if(c && c.formula != '') {
            return false;
          }
        }
        return true;
  },
  userString:function() {
        return "cut cells";
  }
});

// extension to cut for drag and drop operations
LiveSheet.MoveUndo = function(startcell,endcell,destcell,sheet) {
  LiveSheet.UndoObject.call(this);
  // TODO: make sure that startcell is really tl and endcell is br
  this.startcell = LiveSheet.copyCell(startcell);
  this.endcell = LiveSheet.copyCell(endcell);
  this.destcell = LiveSheet.copyCell(destcell);
  this.sheet = sheet;
};

dojo.inherits(LiveSheet.MoveUndo,LiveSheet.UndoObject);

dojo.lang.extend(LiveSheet.MoveUndo, {
//LiveSheet.MoveUndo.prototype = {
  onSuccess:function(args) {
    undoManager.add(this);
  },
  undo:function() {
    return sheetServer.callRemoteWithCalc('onMoveUndo',this.startcell,this.copiedcells,this.destcell,this.targetcells);
  },
  redo:function() {
    return sheetServer.callRemoteWithCalc('onMoveCells',this.startcell,this.endcell,this.destcell);
  },
  doAction:function() {
    this.copiedcells = this.sheet.copyCells(this.startcell,this.endcell,false,true); // no purge
    var destbotrow = this.destcell.row + (this.endcell.row - this.startcell.row);
    var destrightcol = this.destcell.col + (this.endcell.col - this.startcell.col);
    var destbotcell = new LiveSheet.Cell(destrightcol,destbotrow);
    this.targetcells = this.sheet.copyCells(this.destcell,destbotcell,false,true); // no purge
    var d = this.redo();
    d.addCallback(bind(this.onSuccess,this));
    return d;
  },
  valid:function() {
    // implement this
    return true;
  },
  userString:function() {
    return "moved cell" + ((this.startcell.key == this.endcell.key) ? '' : 's');
  }
});



LiveSheet.PasteUndo = function(clipboardItem,targetCell) {
  LiveSheet.UndoObject.call(this);
  this.clipitem = clipboardItem;
  this.target = LiveSheet.copyCell(targetCell);
  this.undobuffer = null;
}


dojo.inherits(LiveSheet.PasteUndo,LiveSheet.UndoObject);


dojo.lang.extend(LiveSheet.PasteUndo, {
//LiveSheet.PasteUndo.prototype = {
  onSuccess:function(args) {
        undoManager.add(this);
  },
  undo:function() {
        for(var i=0;i<this.undobuffer.length;i++) {
          var old = this.undobuffer[i];
          var c = currentsheet.cCache.getCellByAttr(old.col,old.row);
          if(c) {
                c.copyConstruct(old);
          }
        }
        return sheetServer.callRemote('onPasteCellBuffer',this.undobuffer,this.target);
  },
  redo:function() {
        var d;
    if(this.clipitem.destructive) {
      d = sheetServer.callRemote('onPasteCellBuffer',this.clipitem.source,this.target);
    }
    else {
          var s = this.clipitem.startcell;
          var e = this.clipitem.endcell;
      var rect = new DocUtils.geometry.rect(s.col,s.row,e.col,e.row);
      d = sheetServer.callRemote('onPasteCells',rect,this.target);
    }
        return d;
  },
  doAction:function() {
        // grab a snapshot of the paste region. Start from the target cell
                // and go the length and width of the paste region
        var s = this.clipitem.startcell,e=this.clipitem.endcell;
        
        var endcell = new LiveSheet.Cell(this.target.col + (e.col - s.col),
                                                                         this.target.row + (e.row - s.row));
        this.undobuffer = currentsheet.copyCells(this.target,endcell,false,true);
        this.redo().addCallback(bind(this.onSuccess,this));
  },
  valid:function() {
//      var source = this.clipitem.source;
//      var s = this.clipitem.startcell;
//      var e = this.clipitem.endcell;
        
//      for(var i=0;i<source.length;i++) {
//        var orig = source[i];
//        var cell = currentsheet.cCache.getCellByAttr((this.target.col + (orig.col - s.col)),
//                                                                                                 (this.target.row  + (orig.row - s.row)));
//        if((!cell && orig.formula != "") || (cell && cell.formula != orig.formula)) {
//              return false;
//        }
//      }
        return true;
  },
  userString:function() {
                return 'paste cells';
  }
});


//template

LiveSheet.ClearUndo = function(startcell,endcell) {
  LiveSheet.UndoObject.call(this);
  this.startcell = startcell;
  this.endcell = endcell;
}


dojo.inherits(LiveSheet.ClearUndo,LiveSheet.UndoObject);


dojo.lang.extend(LiveSheet.ClearUndo, {
        //LiveSheet.ClearUndo.prototype = {
  onSuccess:function(args) {
        undoManager.add(this);
  },
  undo:function() {
        return sheetServer.callRemote('onPasteCellBuffer',this.undobuffer,this.startcell);
  },
  redo:function() {
        currentsheet.clearCells(this.startcell,this.endcell);
        return sheetServer.callRemote('onClearCells',this.startcell,this.endcell);
  },
  doAction:function() {
        // grab the cells from the clear area.  Technically I could use copyCells 
        // to clear the cells but I want to reuse the redo implementation
        this.undobuffer = currentsheet.copyCells(this.startcell,this.endcell,false,true);
        this.redo().addCallback(bind(this.onSuccess,this));
  },
  valid:function() {
        for(var i=this.startcell.col;i<=this.endcell.col;i++) {
          for(var j=this.startcell.row;j<=this.endcell.row;j++) {
                var cell = currentsheet.cCache.getCellByAttr(i,j);
                if(cell && cell.formula != "") {
                  return false;
                }
          }
        }
        return true;
  },
  userString:function() {
        return "clear cells";
  }
});


LiveSheet.ColRowModUndo = function() {
  LiveSheet.UndoObject.call(this);
};

dojo.inherits(LiveSheet.ColRowModUndo,LiveSheet.UndoObject);

dojo.lang.extend(LiveSheet.ColRowModUndo, {
  onSuccess:function(args) {
    undoManager.add(this);
  },
  onFailure:function(failure) {
    if(/^ExpansionOverflow/.test(failure.error.message)) {
      var errb = new DocUtils.Widgets.errorBox(currentsheet.parentdiv,
                                               'Numbler cannot shift nonblank cells from the sheet.',
                                               'errorbox');
      errb.show(5);
    }
    if(/^LockRegionOverlap/.test(failure.error.message)) {
      var errb = new DocUtils.Widgets.errorBox(currentsheet.parentdiv,
                                               'You cannot modify a row or column that is inside a locked region of cells.',
                                               'errorbox');
      errb.show(5);
    }
    return failure;
  },
  doAction:function() {
    return this.redo().addCallback(bind(this.onSuccess,this));
  }
  });



LiveSheet.InsertRowUndo = function(row1,row2) {
  LiveSheet.ColRowModUndo.call(this);
  this.row = Math.min(row1,row2);
  this.delta = Math.max(row1,row2) - this.row + 1;
};

dojo.inherits(LiveSheet.InsertRowUndo,LiveSheet.ColRowModUndo);

dojo.lang.extend(LiveSheet.InsertRowUndo, {
    //LiveSheet.InsertRowUndo.prototype = {
  undo:function() {
    return sheetServer.callRemote('onRowDelete',this.row+this.delta,-this.delta);    
  },
  redo:function() {
    var d= sheetServer.callRemote('onRowInsert',this.row,this.delta);
    d.addErrback(bind(this.onFailure,this));
    return d;
  },
  valid:function() {
    return !currentsheet.cCache.cellsExistInRange(1,this.row,256,this.row+this.delta-1);
  },
  userString:function() {
    return "insert rows" 
  }
  });

LiveSheet.DeleteRowUndo = function(row1,row2) {
  LiveSheet.ColRowModUndo.call(this);
  // note: row should be the bottom most extent and delta should be negative.
  this.row = Math.max(row1,row2);
  this.delta = Math.min(row1,row2) - this.row - 1;
};

dojo.inherits(LiveSheet.DeleteRowUndo,LiveSheet.ColRowModUndo);

dojo.lang.extend(LiveSheet.DeleteRowUndo, {
    //LiveSheet.InsertRowUndo.prototype = {
  undo:function() {
    return sheetServer.callRemote('onRowDeleteUndo',
                                  Math.max(1,this.row+this.delta+1),-this.delta,
                                  this.copiedcells,this.copiedstyles);
  },
  redo:function() {
    var d = sheetServer.callRemote('onRowDelete',this.row,this.delta);
    d.addErrback(bind(this.onFailure,this));
    return d;
  },
  doAction:function() {
    // copy any cells
    this.copiedcells = currentsheet.copyCellsInRange(1,this.row+this.delta+1,LiveSheet.maxCol,this.row);
    this.copiedstyles = currentsheet.sCache.getRowStylesInRange(this.row+this.delta+1,this.row);
    return this.redo().addCallback(bind(this.onSuccess,this));
  },
  valid:function() {
    // hmm.. don't really know what to do here.
    return true;
  },
  userString:function() {
    return "delete rows" 
  }
  });


LiveSheet.InsertColUndo = function(col1,col2) {
  LiveSheet.ColRowModUndo.call(this);
  this.col = Math.min(col1,col2);
  this.delta = Math.max(col1,col2) - this.col + 1;
};

dojo.inherits(LiveSheet.InsertColUndo,LiveSheet.ColRowModUndo);

dojo.lang.extend(LiveSheet.InsertColUndo, {
    //LiveSheet.InsertColUndo.prototype = {
  undo:function() {
    return sheetServer.callRemote('onColDelete',this.col+this.delta,-this.delta);    
  },
  redo:function() {
    var d = sheetServer.callRemote('onColInsert',this.col,this.delta);
    d.addErrback(bind(this.onFailure,this));
    return d;
  },
  doAction:function() {
    return this.redo().addCallback(bind(this.onSuccess,this));
  },
  valid:function() {
    return !currentsheet.cCache.cellsExistInRange(this.col,1,this.col+this.delta-1,LiveSheet.maxRow);
  },
  userString:function() {
    return "insert columns" 
  }
  });


LiveSheet.DeleteColUndo = function(col1,col2) {
  LiveSheet.ColRowModUndo.call(this);
  // note: row should be the bottom most extent and delta should be negative.
  this.col = Math.max(col1,col2);
  this.delta = Math.min(col1,col2) - this.col - 1;
};

dojo.inherits(LiveSheet.DeleteColUndo,LiveSheet.ColRowModUndo);

dojo.lang.extend(LiveSheet.DeleteColUndo, {
//LiveSheet.InsertColUndo.prototype = {
  undo:function() {
    return sheetServer.callRemote('onColDeleteUndo',Math.max(1,this.col+this.delta+1),-this.delta,
                               this.copiedcells,this.copiedstyles);
  },
  redo:function() {
    var d = sheetServer.callRemote('onColDelete',this.col,this.delta);
    d.addErrback(bind(this.onFailure,this));
    return d;
  },
  doAction:function() {
    // copy any cells
    this.copiedcells = currentsheet.copyCellsInRange(this.col+this.delta+1,1,this.col,LiveSheet.maxRow);
    this.copiedstyles = currentsheet.sCache.getColStylesInRange(this.col+this.delta+1,this.col);
    return this.redo().addCallback(bind(this.onSuccess,this));
  },
  valid:function() {
    // hmm.. don't really know what to do here.
    return true;
  },
  userString:function() {
    return "delete columns" 
  }
  });
