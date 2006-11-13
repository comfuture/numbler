/* Copyright (C) 2006 Numbler LLC */
/* See LICENSE for details. */

LiveSheet.defstyles = {
  'text-align':'left',
  'background-color':'',
  'border':'', 
  'color':'', 
  'text-decoration':''
};


LiveSheet.styleCache = function() { 
  LiveSheet.Cache.call(this); // call base class constructor
};
LiveSheet.styleCache.prototype = new LiveSheet.Cache();

LiveSheet.styleCache.prototype.loadFromServer = function(cols,rows) {
  // load stored cell values from the server.  Since this is 
  // called before cells are rendered there is no need to apply
  // the styles to the cells.
  for(var i=0;i<cols.length;i++) {
    if(cols[i].format) {
      this.getcolstyle(cols[i].id,cols[i].format.cache).save();
    }
  }
  for(i=0;i<rows.length;i++) {
    if(rows[i].format) {
      this.getrowstyle(rows[i].id,rows[i].format.cache).save();
    }
  }
};

LiveSheet.styleCache.prototype.colstyle = function(col) {
  var colkey = (typeof(col) == 'number') ? LiveSheet.colkey(col) : col;
  return this.get(colkey);
};
        
LiveSheet.styleCache.prototype.rowstyle = function(row) {
  var rowkey = (typeof(row) == 'number') ? LiveSheet.rowkey(row) : row;
  return this.get(rowkey);
};

LiveSheet.styleCache.prototype.getcolstyle = function(col,copy) {
  var builder =this.colstyle(col);
  if(!builder) {
    builder = new LiveSheet.styleBuilder(".cell." + LiveSheet.colkey(col),copy);
        // overwrite the className for now
        builder.className = LiveSheet.colkey(col);
    this.add(LiveSheet.colkey(col),builder);
  }
  return builder;
};

LiveSheet.styleCache.prototype.getrowstyle = function(row,copy) {
  var builder = this.rowstyle(row);
  if(!builder) {
    builder = new LiveSheet.styleBuilder(".cell." + LiveSheet.rowkey(row),copy);
        builder.className = LiveSheet.rowkey(row);
    this.add(LiveSheet.rowkey(row),builder);
  }
  return builder;
};

LiveSheet.styleCache.prototype.colexists = function(col) {
  return this.exists(LiveSheet.colkey(col));
};
LiveSheet.styleCache.prototype.rowexists = function(row) {
  return this.exists(LiveSheet.rowkey(row));
};

LiveSheet.styleCache.prototype.removeColStyle = function(col) {
  var colkey = (typeof(col) == 'number') ? LiveSheet.colkey(col) : col;
  return this.remove(colkey);
};

LiveSheet.styleCache.prototype.removeRowStyle = function(row) {
  var rowkey = (typeof(row) == 'number') ? LiveSheet.rowkey(row) : row;
  return this.remove(rowkey);
};
LiveSheet.styleCache.prototype.getColStylesInRange = function(c1,c2) {
  var ret = [];
  for(var i=c1;i<=c2;i++) {
    var cstyle = this.colstyle(i);
    var dims = currentsheet.dimManager.findNonDefaultCol(i);
    if(cstyle || dims) {
      ret.push({'key':'c' + i,'id':i,
                   'val':dims != null ? dims.val : 0,
                   // merge should create a deep copy
                   'format':cstyle != null ? merge(cstyle) : {}});
    }
  }
  return ret;
};
LiveSheet.styleCache.prototype.getRowStylesInRange = function(r1,r2) {
  var ret = [];
  for(var i=r1;i<=r2;i++) {
    var cstyle = this.rowstyle(i);
    var dims = currentsheet.dimManager.findNonDefaultRow(i);
    if(cstyle || dims) {
      ret.push({'key':'r' + i,'id':i,
                   'val':dims != null ? dims.val : 0,
                   // merge should create a deep copy
                   'format':cstyle != null ? merge(cstyle) : {}});
    }
  }
  return ret;
};



LiveSheet.styleBuilder = function(selector,cache) {
  LiveSheet.Cache.call(this);
  this.selector = selector;
  this.className = this.selector.replace(/.*?\./,'').replace(/\./,' ');
  if(cache) {
    this.cache = cache;
  }
};
LiveSheet.styleBuilder.prototype = new LiveSheet.Cache();

LiveSheet.styleBuilder.prototype.fromString = function(val) {
  // strip out selector and {} and then split by seperators.  this 
  // probably misses some fancy CSS cases.
  var items = val.replace(/.*?\u007b/,'').replace(/\u007d.*?/,'').split(/:|;/);
  // ensure that we only do %2 items
  for(var i=0;i<items.length - (items.length%2);i += 2) {
    this.add(items[i],items[i+1]);
  }
};

LiveSheet.skipStyle = new RegExp(/^__|background-color/);

LiveSheet.styleBuilder.prototype.getTextAlign = function() {
  var ta = this.get('text-align');
  if(ta) {
    return ta;
  }
  else if('__sht' in this.cache) {
    return 'right';
  }
  return null;
};

LiveSheet.styleBuilder.prototype.declaration = function(fullstyle) {
  var retval = fullstyle || [];
  
  if('__sht' in this.cache && !('text-align' in this.cache)) {
    retval.push('text-align:right;');
  }

  for(var cacheitem in this.cache) {
    if(LiveSheet.skipStyle.test(cacheitem)) { // bypass hidden styles
      continue;
    }
    
    retval.push(cacheitem);
    retval.push(':');
    retval.push(this.cache[cacheitem]);
    retval.push(';');
  };
  if(!fullstyle) {
    return retval.join('');
  }
};

LiveSheet.styleBuilder.prototype.toString = function() {
  var retval = [];
  retval.push(this.selector);
  retval.push(' {');
  this.declaration(retval);
  retval.push('}');
  return retval.join('');

};

LiveSheet.styleBuilder.prototype.removeRule = function() {
  var index = dojo.style.findCssRule(this.selector);    
  if(index >= 0) {
    dojo.style.removeCssRule(index);
  }
};

LiveSheet.styleBuilder.prototype.save = function() {
  // write the rule to the DOM.  While the W3C does support
  // fine grained accessed to stylesheet properties this interface is 
  // not suported by IE6 (addPropertyValue,removeProperty, etc). so
  // we need to add the new rule and then remove the old one.
  var index = dojo.style.findCssRule(this.selector);
  var dec = this.declaration();
  if(dec) { // IE barfs on empty declarations (possible with our hidden style support
        dojo.style.insertCssRule(this.selector,this.declaration());
  }
  if(index >= 0) {
    dojo.style.removeCssRule(index);
  }
};

// dojo extension to find a stylesheet rule 

if(typeof(dojo.style.findCssRule) == 'undefined') {
  dojo.style.findCssRule = function(selector) {
    if (!dojo.style.styleSheet) {
      if (document.createStyleSheet) { // IE
                dojo.style.styleSheet = document.createStyleSheet();
      } else if (document.styleSheets[0]) { // rest
                // FIXME: should create a new style sheet here
                // fall back on an exsiting style sheet
                dojo.style.styleSheet = document.styleSheets[0];
      } else { return null; } // fail
    }
        
    var rules =dojo.style.styleSheet.cssRules;
    if(!rules) {
      rules = dojo.style.styleSheet.rules;
    }
    if(!rules) {
      return -1;
    }
                
    for(var i=0;i<rules.length;i++) {
      if(rules[i].selectorText == selector) {
                return i;
      }
    }
    return -1;
  };
 };



LiveSheet.StyleRangeUndo = function(rect,properties,cache,remove) {
  LiveSheet.UndoObject.call(this);
  this.rect = rect;
  this.properties = properties;
  this.remove = remove;
  this.cellcache = cache;
  this.prevstate = [];

  this.rl = [];
  for(var i=0;i<this.properties.length;i+=2) { 
    this.rl.push(this.properties[i]);
  }
};
dojo.inherits(LiveSheet.StyleRangeUndo,LiveSheet.UndoObject);

dojo.lang.extend(LiveSheet.StyleRangeUndo, {
//LiveSheet.StyleRangeUndo.prototype = {
  // LiveSheet.CellUndo required functions
  undo:function() {
    var count = 0;
    var updatelist = [];
    for(var i=this.rect.l;i<=this.rect.r;i++) {
      for(var j=this.rect.t;j<=this.rect.b;j++,count++) {
                var cell = this.cellcache.getCellByAttr(i,j);
                if(!cell) { continue; }
                
                // if we have nothing previously remove any applied styles.
                var styleState = this.prevstate[count];
                if(!styleState) {
                  cell.removeCustomStyleList(this.rl);
                }
                else {
                  // apply the styles in the snapshot to the current cell.
                  cell.setCustomStyleList(styleState.proplist(this.rl));
                }
                updatelist.push(cell);
      }
    }
    this.update();
    return sheetServer.callRemote('updateStyleCells',updatelist);
  },
  redo:function() {
    var d = this._applyStyle(false);
    this.update();
        return d;
  },
  update:function() {
    LiveSheet.Sheetbar.updateState(currentsheet.focusCell.customStyle);
  },
  valid:function() {
    var count = 0;
    var prop = this.properties[0];
    for(var i=this.rect.l;i<=this.rect.r;i++) {
      for(var j=this.rect.t;j<=this.rect.b;j++,count++) {
                var cell = this.cellcache.getCellByAttr(i,j);   
                if(!cell) {
                  // the cell should be in cache because it had a custom style on it
                  // if not then something has changed - this will need to be revisited
                  // when we go to a better range based style algorithm
                  return false;
                }
                // compare the style properties
                if(cell.customStyle) {
                  // we use the rl list here because it just contains the property names 
                  // we are going to compare
                  if(this.remove) {
                        // in the removal case we expect the properties to be non existant OR 
                        // be the defaults
                        if(!cell.customStyle.comparenull(this.rl)) {
                          return false;
                        }
                  }
                  else if(!cell.customStyle.compare(this.properties)) {
                        return false;
                  }
                }
                else if(this.prevstate[count] != null) {
                  return false;
                }
      }
    }
    return true;
  },
  userString:function() {
    // FIXME
    return 'applying style';
  },
  onSuccess:function(args) {
   undoManager.add(this);
  },
  doAction:function() { // this should be called by the user
   this._applyStyle(true).addCallback(bind(this.onSuccess,this));
  },
  recordOldState:function(count,cell) {
    this.prevstate[count] = cell.customStyle ? 
    DocUtils.deepcopy(null,cell.customStyle) : null;
  },
  _applyStyle:function(scan) {
    // perform the action.  Scan you only be specified once!
    var count=0;
    for(var i=this.rect.l;i<=this.rect.r;i++) {
      for(var j=this.rect.t;j<=this.rect.b;j++,count++) {
        if(!this.remove) {
          var cell = this.cellcache.createOnWrite(i,j);
          if(scan) {
            this.recordOldState(count,cell);
          }
          cell.setCustomStyleList(this.properties);
        }
        else {
          // don't force the cell into the cache because we are deleting
          var cell = this.cellcache.getCellByAttr(i,j);
          if(cell) {
            if(scan) {
              this.recordOldState(count,cell);
            }
            cell.removeCustomStyleList(this.rl);
          }
        }
      }
    }
    return sheetServer.callRemote(this.remove ? 'removeStyleRegion' : 'updateStyleRegion',this.rect,
                      this.remove ? this.rl : this.properties);
  }
});

LiveSheet.GenericStyleUndo = function(properties,remove) {
  LiveSheet.UndoObject.call(this);
  this.remove = remove;
  this.properties = properties;  

  if(this.remove) {
    this.rl = [];
    for(var i=0;i<this.properties.length;i+=2) { this.rl.push(properties[i]); }
  }
}

dojo.inherits(LiveSheet.GenericStyleUndo,LiveSheet.UndoObject);

dojo.lang.extend(LiveSheet.GenericStyleUndo, {
    //LiveSheet.GenericStyleUndo.prototype = {
  onSuccess:function(args) {
    undoManager.add(this);
  },
  getStyle:function() {
    throw new Error("must implement");
  },
  removeStyle:function() {
    throw new Error("must implement");
  },
   _updateCells:function(style,empty,redo) {
    throw new Error("must implement");
  },
  undo:function() {
    // remove the style
    var style = this.getStyle();
    var empty = this.prevstate.empty();
    if(empty) {
      this.removeStyle();
    }
    else {
      // if prevstate is not empty then we want to simply apply the old style
      style.updateList(this.prevstate.proplist());
      style.save();
    }
    // update any cells in view
    this._updateCells(style,empty,false);
    
    return empty ? sheetServer.callRemote('removeStyleClass',this.key,this.properties) : 
    sheetServer.callRemote('updateStyleClass',this.key,style,this.properties);
  },
  doAction:function() {
   // idealy this would be in the constructor but we don't know abou getStyle at that point
   this.prevstate = DocUtils.deepcopy(null,this.getStyle());
   this.redo().addCallback(bind(this.onSuccess,this));
  },
  redo:function() {
    // set the style
    var style = this.getStyle();
    this.remove ? style.removeList(this.rl) : style.updateList(this.properties);
    var empty = style.empty();
    empty ? style.removeRule() : style.save();
    // update any cells in view
    this._updateCells(style,empty,true);

    return empty ? sheetServer.callRemote('removeStyleClass',this.key,this.properties) : 
    sheetServer.callRemote('updateStyleClass',this.key,style,this.properties);
  },
  valid:function() {
    // get the style for the column
    var cStyle = this.getStyle();
    if(this.remove) {
      if(!cStyle.comparenull(this.rl)) {
        return false;
      }
    }
    else if(!cStyle.compare(this.properties)) {
      return false;
    }
    return true;
  },
 procCell:function(el,style,empty,redo) {
    if(this.properties[0] == 'background-color') {
      var cell = currentsheet.cellFromEl(el,true); // no cache
      var existingBG = cell.customStyle ? cell.customStyle.get('background-color') : null;
      if(!redo) {
        cell.removeBackground(true); // remove any inherited backgroudn
        if(existingBG) {
          cell.setBackground(existingBG);
        }
      }
      else {
        if(!existingBG) {
          cell.setBackground(this.properties[1],true); // inherited style
        }
      }
    }
    
    if(empty) { 
      removeElementClass(el,style.className) 
    } 
    else { 
      addElementClass(el,style.className); 
    }
  }
});


LiveSheet.ColStyleUndo = function(col,properties,remove) {
  this.col = col;
  this.key = LiveSheet.colkey(this.col);
      //el.className = empty ? el.className.replace(this.key,'') : style.className;

  LiveSheet.GenericStyleUndo.call(this,properties,remove);
};


dojo.inherits(LiveSheet.ColStyleUndo,LiveSheet.GenericStyleUndo);

dojo.lang.extend(LiveSheet.ColStyleUndo, {
    //LiveSheet.ColStyleUndo.prototype = {
  getStyle:function() {
    return currentsheet.sCache.getcolstyle(this.col);
  },
  removeStyle:function() {
    currentsheet.sCache.removeColStyle(this.col);
  },
 _updateCells:function(style,empty,redo) {
    var startrow = currentsheet.cArea.startrow,endrow=currentsheet.cArea.endrow;
    for(var i=startrow;i<=endrow;i++) {
      var el = getElement(LiveSheet.cellkey(this.col,i));
      // if empty remove the key (remember that the class may have multiple space
      // seperated selectors
          this.procCell(el,style,empty,redo);
    }
  },
  userString:function() {
    return 'formatting column';
  }
});



LiveSheet.RowStyleUndo = function(row,properties,remove) {
  this.row = row;
  this.key = LiveSheet.rowkey(this.row);
  LiveSheet.GenericStyleUndo.call(this,properties,remove);
}


dojo.inherits(LiveSheet.RowStyleUndo,LiveSheet.GenericStyleUndo);


dojo.lang.extend(LiveSheet.RowStyleUndo, {
    //LiveSheet.RowStyleUndo.prototype = {
  getStyle:function() {
    return currentsheet.sCache.getrowstyle(this.row);
  },
  removeStyle:function() {
    currentsheet.sCache.removeRowStyle(this.row);
  },
  _updateCells:function(style,empty,redo) {
    var startcol = currentsheet.cArea.startcol,endcol=currentsheet.cArea.endcol;
    for(var i=startcol;i<=endcol;i++) {
      var el = getElement(LiveSheet.cellkey(i,this.row));
          this.procCell(el,style,empty,redo);
    }
  },
  userString:function() {
    return 'formatting row';
  }
});


LiveSheet.CurrencyUndo = function(startcell,endcell,ctype) {
  LiveSheet.UndoObject.call(this);
  this.startcell = startcell;
  this.endcell = endcell;
  this.rect = new DocUtils.geometry.rect(this.startcell.col,
                                                                           this.startcell.row,
                                                                           this.endcell.col,
                                                                           this.endcell.row);  
  this.type = ctype;
};


dojo.inherits(LiveSheet.CurrencyUndo,LiveSheet.UndoObject);


dojo.lang.extend(LiveSheet.CurrencyUndo, {
//LiveSheet.CurrencyUndo.prototype = {
  onSuccess:function(args) {
        this.changecells = [];
        for(var i=0;i<args.length;i++) {
          this.changecells.push(LiveSheet.copyCell(args[i]));
    }
    undoManager.add(this);
  },
  undo:function() {
     return sheetServer.callRemote('onPasteCellBuffer',this.cells,this.startcell);
  },
  redo:function() {
         return sheetServer.callRemote('updateCurrencyRegion',this.rect,this.type);
  },
  doAction:function() {
         this.cells = currentsheet.copyCells(this.startcell,this.endcell,false,true);
         this.redo().addCallback(bind(this.onSuccess,this));
  },
  valid:function() {
         for(var i=0;i<this.changecells.length;i++) {
           var changeCell = this.changecells[i];
           var cell = currentsheet.cCache.getCellByAttr(changeCell.col,changeCell.row);
           if(cell) {
                 if(changeCell) {
                   currencyStyle = changeCell.customStyle.get('__sht');
                   if(currencyStyle) {
                         // check that it matches that on the current cell.
                         if(cell.customStyle && cell.customStyle.get('__sht') == currencyStyle) {
                           continue;
                         }
                         else {
                           return false;
                         }
                   }
                 }
                 else {
                   // else ensure that the currency style is not set.
                   if(!cell.customStyle) {
                         continue;
                   }
                   if(cell.customStyle.get('__sht')) {
                         return false;
                   }
                 }
           }
           else {
                 return false;
           }
         }
         return true;
  },
  userString:function() {
         return 'formatting currency';
  }
});


LiveSheet.ColRowCurrencyUndo = function(undoType,identifier,ctype) {
  LiveSheet.UndoObject.call(this);
  this.undoType = undoType;
  if(this.undoType != 'r' && this.undoType != 'c') {
        throw Error("LiveSheet.ColRowCurrencyUndo: invalid type");
  };
  this.val = identifier; // row or column value
  this.properties = ['__sht',ctype];
  this.ctype = ctype;
  this.undocells = null;
};


dojo.inherits(LiveSheet.ColRowCurrencyUndo,LiveSheet.UndoObject);


dojo.lang.extend(LiveSheet.ColRowCurrencyUndo, {
//LiveSheet.ColRowCurrencyUndo.prototype = {
  getStyle:function() {
        return this.undoType == 'r' ? 
        currentsheet.sCache.getrowstyle(this.val) : 
        currentsheet.sCache.getcolstyle(this.val);
  },
  onSuccess:function(args) {
        undoManager.add(this);
  },
  undo:function() {
        var s = this.getStyle();
        !this.oldval ? s.remove('__sht') : s.update('__sht',this.oldval);
    return sheetServer.callRemote('updateCurrencyClass',(this.undoType + this.val),s);
  },
  redo:function() {
        var s = this.getStyle();
        s.update('__sht',this.ctype);
    return sheetServer.callRemote('updateCurrencyClass',(this.undoType + this.val),s);
  },
  doAction:function() {
        // grab the cells for the column
        this.oldval = this.getStyle().get('__sht');
        this.redo().addCallback(bind(this.onSuccess,this));
  },
  valid:function() {
        return this.getStyle().compare(this.properties);
  },
  userString:function() {
    return 'formatting ' + (this.undoType == 'r' ? 'row' : 'column');
  }
});


// template

// LiveSheet.ColStyleUndo = function(start,end,formula) {
//   LiveSheet.UndoObject.call(this);
// }


// dojo.inherits(LiveSheet.ColStyleUndo,LiveSheet.UndoObject);


// //dojo.lang.extend(LiveSheet.ColStyleUndo, {
// LiveSheet.ColStyleUndo.prototype = {
//   onSuccess:function(args) {
//   },
//   undo:function() {
//   },
//   redo:function() {
//   },
//   doAction:function() {
//   },
//   valid:function() {
//   },
//   userString:function() {
//   }
// });
