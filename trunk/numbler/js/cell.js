/* Copyright (C) 2006 Numbler LLC */
/* See LICENSE for details. */

/////////////////////////////////////////////////////////////////////////////////
//
// Cell object
//
////////////////////////////////////////////////////////////////////////////////

if(typeof(LiveSheet) == 'undefined') {
  LiveSheet = {};
 };

LiveSheet.cellkey = function(col,row) {
  return 'k' + ((col-1) << 16 | (row-1));
};
LiveSheet.rowkey = function(row) {
  return 'r' + row;
};
LiveSheet.colkey = function(col) {
  return 'c' + col;
};

LiveSheet.maxRow = 65536;
LiveSheet.maxCol = 256;

LiveSheet.urlmatch = new RegExp(/^http:\/\/.*/);
LiveSheet.wwwmatch = new RegExp(/^www\..*/);
LiveSheet.imgmatch = new RegExp(/.jpg$|.jpeg$|.gif$|.png$/i);
// check if the text is number like
LiveSheet.nummatch = new RegExp(/^(\$?)([\+\-]{0,1})((\d+)|([\d,]+)*)(\.\d+)?([eE][\+\-]\d+)?(%?)$/)
// check if the user is entering cell reference mode
LiveSheet.refmatch = new RegExp(/(^=$)|(^=.+[\(,\^\+\<\>\-\=\/&\*]+$)/);

if(dojo.render.html.mozilla) { LiveSheet.disableSelect = "-moz-user-select:none;"; }
 else if(dojo.render.html.safari) { LiveSheet.disableSelect = "-khtml-user-select::none;"; }
// damn IE... always has to be different.
// else if (dojo.render.html.ie) { LiveSheet.disableSelect = "unselectable:on;"; } 
 else { LiveSheet.disableSelect = "user-select:none"; };


LiveSheet.decomposeKey = function(rawkey) {
  var key = parseInt(rawkey.slice(1));
  return {
    'col':(key >> 16)+1,
      'row':(key & 0xFFFF)+1
      };
};

var idkeyval = function(id) {
  return parseInt(id.slice(0));
};

LiveSheet.CellCache = function(args) {
  this.cache = {};
  this.maxCol = 1;
  this.maxRow = 1;
  this.onExtentChange = null;

};

LiveSheet.CellCache.prototype = {
  exists: function(key) {
    return key in this.cache;
  },
  getCellByAttr: function(col,row) {
    return this.getCell(LiveSheet.cellkey(col,row));
  },
  getCell: function(key) {
    return key in this.cache ? this.cache[key] : null;
  },
  // these two methods may be ineficient with large #'s of cells
  // they return an iterable
  getCellsByCol:function(col) {
    var cache = this.cache;
    var _this = this;
    return map(function(arg) { return _this.getCellByAttr(arg[0],arg[1]); },
               filter(function(arg) { 
                        var cell = _this.getCell(LiveSheet.cellkey(arg[0],arg[1]));
                        if(cell) {
                          return cell.formula || cell.text;
                        }
                        return false;
                      },
                      zip(repeat(col,this.maxRow),range(1,this.maxRow+1))));
  },
  getCellsByRow:function(row) {
    var cache = this.cache;
    var _this = this;
    return map(function(arg) { return _this.getCellByAttr(arg[0],arg[1]); },
               filter(function(arg) { 
                        var cell = _this.getCell(LiveSheet.cellkey(arg[0],arg[1]));
                        if(cell) {
                          return cell.formula || cell.text;
                        }
                        return false;
                      },
                      zip(repeat(this.maxCol,row),range(1,this.maxCol+1))));

  },
  cellsExistInRange:function(c1,r1,c2,r2) {
    for(key in this.cache) {
      cell = this.cache[key]
      if(cell.col >= c1 && cell.col <= c2 
         && cell.row >= r1 && cell.row <= r2) {
        contents = cell.formula ||  cell.text;
        if(contents) { return true; };
      }
    }
    return false;
  },
  getCellsInRange:function(c1,r1,c2,r2) {
    ret = []
    for(key in this.cache) {
      cell = this.cache[key]
      if(cell.col >= c1 && cell.col <= c2 
         && cell.row >= r1 && cell.row <= r2) {
        ret.push(cell);
      }
    }
    return ret;
  },
  createOnWrite: function(col,row,copy,nocache) {
    var key = LiveSheet.cellkey(col,row);
    var cell = this.getCell(key);
    if(!cell) {
      cell = new LiveSheet.Cell(col,row,key);
          if(!nocache) {
                this.putCell(cell);
          }
    }
    if(copy) {
      cell.copyConstruct(copy);
    }
    return cell;
  },
  putCell: function(cell) {
    this.cache[cell.key] = cell;
        
    var change = false;
    if(cell.col > this.maxCol) {
      change = true;
      this.maxCol = cell.col;
    }
    if(cell.row > this.maxRow) {
      change = true;
      this.maxRow = cell.row;
    }
    if(change && this.onExtentChange) {
      this.onExtentChange(cell);
    }
  },
  registerExtentChangeCallback:function(cb) {
    this.onExtentChange = cb;
  },
  repr: function() {
    return [keys(this.cache).length,'item(s) the Cell cache'].join(' ')
  }
};

// the overflow dictionary keeps track of cells that overflow
// into adjacent cells.  If an cell that was previously empty has content added 
// to it the cell checks the overflow list.  If a cell is found then 
// the new cell must go back and tell the overflowing cell to redraw
// to the next left-most cell.

LiveSheet.overflow = new LiveSheet.Cache();
LiveSheet.wouldOverflow = new LiveSheet.Cache();

LiveSheet.clearOverflow = function() {
  LiveSheet.overflow.purge();
  LiveSheet.wouldOverflow.purge();
};

LiveSheet.measurecache = new LiveSheet.Cache();

LiveSheet._typeTracker = function() {
  this.ruler = getElement('ruler1');

  var defaultmeasure = [];
  // add the default measurement array
  LiveSheet.measurecache.add('default',this.createmeasure());
};

LiveSheet._typeTracker.prototype = {
  createmeasure:function() {
    var measure = [];
    var generator = function(index) {
      this.ruler.innerHTML = String.fromCharCode(index);
      measure[index] = this.ruler.offsetWidth;
    }
    forEach(range(1,255),bind(generator,this));
    // special case for space
    this.ruler.innerHTML = '&nbsp;'
    measure[32] = this.ruler.offsetWidth;
    return measure;
  },
  getOrCreateMeasure:function(styleobj) {
    var declaration;
    if(!styleobj) {
      declaration = 'default';
    }
    else {
      declaration = styleobj.declaration();
    }
    var measure = LiveSheet.measurecache.get(declaration);
    if(!measure) {
      this.ruler.style.cssText = declaration; // should never be default
      measure = this.createmeasure();
      LiveSheet.measurecache.add(declaration,measure);
    }
    return measure;
  },
  init:function(initlen,styleInfo,endcol,endwidth) {
    // initlen is the current length of the text = 0 if no current text
    // styleInfo is the style cache object
    // endcol is the current end column
    
    this.endcol = endcol;
    this.endwidth = endwidth;
    this.textwidth = initlen;
    this.currentmeasure = this.getOrCreateMeasure(styleInfo);
  },
  addChar:function(keyval) {
    this.textwidth += this.currentmeasure[keyval.code];
    
    if(this.textwidth > this.endwidth) {
      this.endcol++;
      this.endwidth += currentsheet.dimManager.coldims(this.endcol).val;
    }
    return this.endwidth;
  },
  measure:function() {
    return this.textwidth + 5;
  },
  measureText:function(textvalue,styleInfo) {
    var m = this.getOrCreateMeasure(styleInfo);
    return sum(map(function(x) { return m[textvalue.charCodeAt(x)]; },range(0,textvalue.length)));
  }
};


LiveSheet.typeTracker = null; // create on sheet load

LiveSheet.createColHeader = function(col,container,dim) {
  var cssClass = (col == currentsheet.maxwidth) ? "endcolumn" : 
  ((col == 1) ? "startcolumn" : "column");

  var stringval;
  var columnID = (col -1);

  if(columnID >= 26) { // end of the alphabet
    var first = Math.floor(columnID/26);
    stringval = String.fromCharCode(65 + (Math.floor(columnID/26)-1)) + 
      String.fromCharCode(65 + (columnID % 26));
                
  }
  else {
    stringval = String.fromCharCode(65 +columnID);
  }
  var start = col == 1 ? dim.startval : dim.startval + 5;
  var width = col ==1 ? dim.val : dim.val - 5;
  var c = container;
  if(col != 1) {
    c.push('<div class="cmoverL" style="');
    c.push('left:');c.push(dim.startval);
    c.push('px;right:');c.push(start);
    c.push('px" id="cm');
    c.push(col);
    c.push('">');
    c.push('</div>');
  };
  c.push('<div class="');
  c.push(cssClass);
  c.push('" style="width:');
  c.push(width);
  c.push('px;left:');
  c.push(start);
  c.push('px;right:');
  c.push(dim.end());
  c.push('px;');
  if(dojo.render.html.ie) {
    c.push('" unselectable="on"'); // " ends the style block
  }
  else {
    c.push(LiveSheet.disableSelect);
    c.push('"');
  }
  c.push(' columnid="');
  c.push(col);
  c.push('" key="');
  c.push(LiveSheet.cellkey(col,0));
  c.push('" onclick="currentsheet.oncolumnclick(this) " ');
  c.push('oncontextmenu="currentsheet.oncolumncontext(event,this)"');
  c.push('>');c.push(stringval);c.push('</div>');
};

LiveSheet.createRowHeader = function(row,container,dim) {

  var cssClass = row == currentsheet.maxcells ? "rowheaderend" : 
  ((row == 1) ? "startrowheader " : "rowheader");
  var c = container;

  var top = row == 1? dim.startval : dim.startval + 5;
  var height = row == 1 ? dim.val : dim.val -5;

  if(row != 1) {
    c.push('<div class="rmoverT" style="');
    c.push('top:');c.push(dim.startval);
    c.push('px;bottom:');c.push(top);
    c.push('px" id="rm');
    c.push(row);
    c.push('">');
    c.push('</div>');
  }

  c.push('<div class="');
  c.push(cssClass);
  c.push('" rowid=');
  c.push(row);
  c.push(' id="');
  c.push(LiveSheet.cellkey(0,row));
  c.push('" style="height:');
  c.push(height);
  c.push('px;top:');
  c.push(top);
  c.push('px;bottom:');
  c.push(dim.end());
  c.push('px;');
  if(dojo.render.html.ie) {
    c.push('" unselectable="on"'); // " ends the style block
  }
  else {
    c.push(LiveSheet.disableSelect);
    c.push('"');
  }  
  c.push(' onclick="currentsheet.onrowclick(this)" ');
  c.push('oncontextmenu="currentsheet.onrowcontext(event,this)" ');
  c.push('>');
  c.push(row);
  c.push('</div>');
};



LiveSheet.createCell = function(col,row,container,key,cell,rowdim,coldims,nextNormalCol) {
  var c = container;

  var coldim = coldims[col];

  // the -3 is for the right padding offset
  var width = coldim.val-3;
  var right=coldim.end();
  // the return value indicates the next column to process normally
  var ret;
  
  if(col == nextNormalCol) {
    ret = col+1;
    if(cell) {
      var kwargs = {'width':width,'right':right};
      ret = cell.adjustForOverflow(coldim.startval,kwargs,ret,coldims);
      width = kwargs.width;
      right = kwargs.right;
    }
  }
  else {
        ret = nextNormalCol;
  }
  // generate the background div (if necessary)
  var bg = null;
  var bg_key = "_bg";
  
  if(cell && cell.customStyle) {
    bg = cell.customStyle.get('background-color');
  }
  if(!bg) {
    var colS = currentsheet.sCache.colstyle(col);
    if(colS) {
      bg = colS.get('background-color');
      bg_key = "_bg_ih"; // inherited column
    }
    if(!bg) {
      var rowS = currentsheet.sCache.rowstyle(row);
      if(rowS) {
        bg = rowS.get('background-color');
        bg_key = "_bg_ih";
      }
    }
  }
  
  if(bg) {
    c.push('<div id="');c.push(key);c.push(bg_key);c.push('" class="cellbg" style="');
    c.push('left:');c.push(coldim.startval);
    c.push('px;top:');c.push(rowdim.startval);
    c.push('px;right:');c.push(coldim.end());
    c.push('px;bottom:');c.push(rowdim.end());
    c.push('px;width:');c.push(coldim.val);
    c.push('px;height:');c.push(rowdim.val);
    c.push('px;background-color:');
    c.push(bg);c.push('"></div>');
  }
  
  c.push('<div class="');
  currentsheet.getCellStyle(col,row,c,nextNormalCol);
  if(bg) {
    c.push(' cellnoborder');
  }
  c.push('" id="');
  c.push(key);
  c.push('" style="width:');
  c.push(width);
  c.push('px;height:');
  c.push(rowdim.val);
  c.push('px;left:');
  c.push(coldim.startval);
  c.push('px;right:');
  c.push(right);
  c.push('px;top:');
  c.push(rowdim.startval);
  c.push('px;bottom:');
  c.push(rowdim.end());
  c.push('px;');
  if(cell && cell.customStyle) {
    cell.customStyle.declaration(c);
  }
  // clickstate=0
  if(dojo.render.html.ie) {
    c.push('" unselectable="on"'); // " ends the style block
  }
  else {
    c.push(LiveSheet.disableSelect);
    c.push('"');
  }  
  c.push(' onclick="currentsheet.clickercb(this,null,event)">');
  if(cell) {
        // store away the real with for later use by cell.width()
        cell._width = coldim.val;
        // get dispValue writes out the trailing <div>
        cell.getDispValue(c);
  }
  c.push('</div>');     
  return ret;
};


LiveSheet.CellException = function(key) {
  this.name = 'CellException';
  this.message = 'Cell element not found for ' + (key || 'unknown key');
};
LiveSheet.CellException.prototype = new Error();

////////////////////////////////////////////////////////////
// Cell methods that operate on a cell but are not part of a cell
////////////////////////////////////////////////////////////

LiveSheet.copyCell = function(s) {
  var retval = new LiveSheet.Cell(s.col,s.row);
  retval.text = s.text;
  retval.formula = s.formula;
  retval.setStyles(s);
  return retval;
};

LiveSheet.rangeRefCell = function(cell1,cell2) {
  return LiveSheet.rangeRef(cell1.col,cell1.row,cell2.col,cell2.row);
};

LiveSheet.rangeRef = function(col1,row1,col2,row2) {
  // assumes that either cell1 or cell2 is the topleft or bottom right of a region
  return [LiveSheet.cellref(Math.min(col1,col2),Math.min(row1,row2)),
          LiveSheet.cellref(Math.max(col1,col2),Math.max(row1,row2))].join(':');
};

LiveSheet.cellref = function(col,row) {
  var ret;
  col = col-1;

  if(col >= 26) { // end of the alphabet
    var first = Math.floor(col/26);
    ret = String.fromCharCode(65 + (Math.floor(col/26)-1)) + 
      String.fromCharCode(65 + (col % 26));
  }
  else {
    ret = String.fromCharCode(65 +col);
  }
  ret += row;
  return ret;
};

////////////////////////////////////////////////////////////
// Cell object - responsible for any cell specific operations
////////////////////////////////////////////////////////////

LiveSheet.Cell = function(column,row,key,el) {
  this.col = column; 
  this.row = row;       
  this.text = '';
  this.formula = '';
  this.createelfunc = null;
  this.fxerror = false;
  // only used for capturing the original values when gaining focus
  this.origtext = '';
  this.origformula = '';
  this.key = key || LiveSheet.cellkey(this.col,this.row);
  //this.cellElement = el || getElement(this.key); // may be null
  this.clickstate = 0;
  this.customStyle = null;
};

LiveSheet.Cell.prototype.getRef = function() {
  return LiveSheet.cellref(this.col,this.row);
}

LiveSheet.Cell.prototype.cellElement = function(nothrow) {
  var ret = getElement(this.key);
  if(!ret && !nothrow) {
    throw new LiveSheet.CellException(this.key);
  }
  return ret;
};

LiveSheet.Cell.prototype.copyConstruct = function(copycell) {
  // copyConstruct *modifies* the sheet in view.  if you only want
  // to use the cell as an object create the object call copyCell

  var el = this.cellElement(true); // could be null
  this.clear();

  if(copycell.error) {
    this.shorterror = copycell.error[0];
    this.fxerror = copycell.error[1];
  }
  // necessary in case the cell contents change while the cell is focused
  this.origtext = copycell.text;
  this.origformula = copycell.formula;
  this.formula = copycell.formula;
  this.text = copycell.text;

  var oldstyle = this.customStyle;
  this.setStyles(copycell);

  if('disp' in copycell) {
    this.disp = copycell.disp;
  }

  if(el) { // if the element exists
    this.maybeAdjustWidth();
    
    // adjust other cells if necessary
    if(this.formula.charAt(0)) {
      var overflow = LiveSheet.overflow.get(this.key);
      if(overflow) {
        currentsheet.cCache.getCell(overflow).ReduceOverflow(this.col);
      }
    }
    else {
      // check the would overflow list.
      var wouldoverflow = LiveSheet.wouldOverflow.get(this.key);
      if(wouldoverflow) {
        var pending = currentsheet.cCache.getCell(wouldoverflow);
        // only make this cell overflow if they are right against this cell or there overflow
        // is right next to this cell.  Otherwise we could be asking a cell to overflow an 
        // adjacent cell which has valid data.
        if((pending.row == (this.row -1)) || (pending.overflow && 
                                              (pending.overflow.slice(-1) == (this.row -1)))) {
          pending.ExpandOverflow(this.col);
        }
      }
    }
    if(this.customStyle || (oldstyle && !this.customstyle)) {
      el.style.cssText = this.genCustomStyles(null,false,true);
    }

    el.innerHTML = this.getDispValue();
    var bg = (this.customStyle && this.customStyle.get('background-color')) || null;
    if(bg) {
      this.setBackground(bg);
    }
    else {
      // clear any existing bg
      this.removeBackground();
    }
  }
};

LiveSheet.Cell.prototype.setStyles = function(source) {
  if(source.customStyle && source.customStyle.cache) {
    this.customStyle = new LiveSheet.styleBuilder('.cell',source.customStyle.cache)
  }
  else if(source.format) { // format string from server
    this.customStyle = new LiveSheet.styleBuilder('.cell',source.format);
  }
  else {
    // necessary for undo
    this.customStyle = null;
  }
};


LiveSheet.Cell.prototype.getTextValue = function() {
  if(this.fxerror) {
    return this.shorterror;
  }
  if(typeof(this.text) != 'undefined') {
        return this.text;
  }
  return this.formula;
};

LiveSheet.Cell.prototype.getDispValue = function(outbuff) {
  var b = outbuff || [];

  if(this.fxerror) {
    b.push(this.shorterror);
  }
  else if(typeof(this.disp) != 'undefined' && 'url' in this.disp) {
    b.push('<a href="'),b.push(this.disp['url']),b.push('" target="numblerwin">');b.push(this.text);b.push('</a>');
  }
  else if(typeof(this.text) != 'undefined') {
        if(LiveSheet.urlmatch.exec(this.text)) {
          if(this.text.match(LiveSheet.imgmatch)) {
                b.push('<img src="');b.push(this.text);b.push('">');
          }
          else {
                b.push('<a href="');b.push(this.text);b.push('" target="numblerwin">');b.push(this.text);b.push('</a>');
          }
        }
        else if(LiveSheet.wwwmatch.exec(this.text)) {
          if(this.text.match(LiveSheet.imgmatch)) {
                b.push('<img src="');b.push(this.text);b.push('">');
          }
          else {
                b.push('<a href="http://');b.push(this.text);b.push('" target="numblerwin">');b.push(this.text);b.push('</a>');
          }
        }
        else {
          b.push(this.text);
        }
  }
  else {
        b.push(this.formula);
  }
  if(!outbuff) {
        return b.join('');
  }
};


LiveSheet.Cell.prototype.equals = function(cellobj) {
  return (this.col == cellobj.col && this.row == cellobj.row);
};

LiveSheet.Cell.prototype.toString = function() {
  return 'Row: ' + this.row + ' Column: ' + this.col;
};

// return true if the cell is editable by the user
LiveSheet.Cell.prototype.UserCell = function() {
  return this.col != 0 && this.row != 0;
};

LiveSheet.Cell.prototype.left = function() {
  return parseInt(this.cellElement().style.left.slice(0,-2));
  //return this.cellElement.offsetLeft;
};
LiveSheet.Cell.prototype.top = function() {
  return parseInt(this.cellElement().style.top.slice(0,-2));
};

LiveSheet.Cell.prototype.height = function() {
  return parseInt(this.cellElement().style.height.slice(0,-2));
  //return this.cellElement.clientHeight;
};

LiveSheet.Cell.prototype.width = function() {
  // the +3 is to account for the padding
  return this._width ? this._width : parseInt(this.cellElement().style.width.slice(0,-2))+3;
};

LiveSheet.Cell.prototype.expandedwidth = function() {
  // always returns the "true" width of the cell contents (when the text is expanded)
  // usually you don't want this value but instead want width.
  return parseInt(this.cellElement().style.width.slice(0,-2));
}

LiveSheet.Cell.prototype.AdjustWidth = function(widthOffset) {
  this.cellElement().style.width = (this.width() + widthOffset) + "px";
};

LiveSheet.Cell.prototype.AdjustHeight = function(heightOffset) {
  this.cellElement().style.height = (this.height() + heightOffset) + "px";
};

LiveSheet.Cell.prototype.inCellX = function(x) {
  // TODO: should this be [) instead of [] for the set inclusivity?
  return ((x >= this.left()) && (x <= this.right()));
};

LiveSheet.Cell.prototype.inCellY = function(y) {
  // TODO: should this be [) instead of [] for the set inclusivity?
  return ((y >= this.top()) && (y <= this.bottom()));
};

LiveSheet.Cell.prototype.inCell = function(x,y) {
  return this.inCellX(x) && this.inCellY(y);
};

LiveSheet.Cell.prototype.right = function() {
  return this.left() + this.width();
};
LiveSheet.Cell.prototype.bottom = function() {
  return this.top() + this.height();
};

LiveSheet.Cell.prototype.inCellRange = function(endcell,x,y) {
        
  var l = Math.min(this.left(),endcell.left());
  var t = Math.min(this.top(),endcell.top());
  var r = Math.max(this.right(),endcell.right());
  var b = Math.max(this.bottom(),endcell.bottom());

  return ((x >= l) && (x <= r) && (y >= t) && (y <= b));
};


var cellKeys = ['col','row','formula','customStyle']

  LiveSheet.Cell.prototype.json = function() {
  var retval =  {
    'col':this.col,
    'row':this.row,
    'formula':this.formula,
    'customStyle':this.customStyle
  };
  return retval;
};

LiveSheet.Cell.prototype.textarea = function() {
  var cn = this.cellElement().childNodes;
  if(cn && cn.length > 0) {
    return cn[0].data;
  }
  return '';
};

LiveSheet.Cell.prototype.refresh = function() {
  this.text = this.textarea();
};

LiveSheet.Cell.prototype.setTextValue = function(val) {
  var el = this.cellElement(true);
  if(el) {
    el.innerHTML = val;
  }
};

// LiveSheet.Cell.prototype.set = function(val) {
//   if(typeof(val) == 'object') {
//     this.setTextValue(val.text);
//   }
//   else {
//     this.setTextValue(val);
//   }
// };

LiveSheet.Cell.prototype.clear = function() {
  this.formula = '';
  this.text = '';
  this.fxerror = false;
  var el = this.cellElement(true);
  if(el) {
        el.innerHTML = '';
        //el.style.color = '';
  }
  this.relAllOverflow();
  // clear out any overflow entries
};

LiveSheet.Cell.prototype.blankCell = function() {
  // remove everything from the cell; formula, computed value, and styling
  this.clear();
  delete this.customStyle;
  this.customStyle = null;
  var el = this.cellElement(true);
  if(el) {
    el.style.cssText = this.genCustomStyles();
  }
  // see if there are any cells that would like to draw over this cell.
  var wouldoverflow = LiveSheet.wouldOverflow.get(this.key);
  if(wouldoverflow) {
        currentsheet.cCache.getCell(wouldoverflow).ExpandOverflow(this.col);
  }
  this.removeBackground();
}


LiveSheet.Cell.prototype.getformulavalue = function() {
  if(this.formula) {
    return this.formula;
  }
  else {
    return this.text;
  }
};

// called whenever a user leaves a cell.
LiveSheet.Cell.prototype.onchange = function() {
  var currentinput = this.textarea();

  // check if 1) the current text is a formula and not the same as the original formula OR
  // 2) if the current text is not a formula but it not the same as the origal text
  if(currentinput.charAt(0) == '=') {
        return currentinput != this.origformula;
  }
  else if(currentinput) {
        if(currentinput == this.origformula) {
          return false;
        }
        return currentinput != this.origtext;
  }
  else {
        return  (!currentinput && (this.origtext || this.origformula));
  }
  //  return (currentinput.charAt(0) == '=' && currentinput != this.origformula) || 
  //(currentinput != this.origtext) || 

};

LiveSheet.Cell.prototype.onShowFormula = function() {
  if(this.formula) {
    this.setTextValue(this.formula);
  }
};

LiveSheet.Cell.prototype.showErrorHint = function() {
  if(this.fxerror) {
    //this.cellElement.
    currentsheet.parentdiv.appendChild(DIV({'style':
                                             {'position':'absolute','top':(this.bottom() + 10) + 'px',
                                                 'left':this.left() + 'px','z-index':'100'},
                                               'id':'errorhint'},'formula error: ' + this.fxerror));
  }
};
LiveSheet.Cell.prototype.hideErrorHint = function(parent) {
  var hintdiv =getElement('errorhint');
  if(hintdiv) {
    //this.cellElement.
    currentsheet.parentdiv.removeChild(hintdiv);
  }
};

LiveSheet.Cell.prototype.onCalc = function() {
  var s = this.cellElement().style;
  s.backgroundColor= '#FFFFE1';
};

// TODO: eventually wired this into a mockikit deferred?
LiveSheet.Cell.prototype.afterCalc = function() {
  var bg = '';
  //if(this.customStyle) {
        //bg = this.customStyle.get('background-color');
        //if(bg == null) {
        //  bg = '';
        //}
  //}

  this.cellElement().style.backgroundColor = bg;
};


LiveSheet.Cell.prototype.doChange = function() {
  // once a change is made here is where it takes action.
  if(this.formula.charAt(0) == '=') {
          this.onCalc();
  }
  return sheetServer.callRemoteWithCalc('onCellChange',[this])
};

LiveSheet.Cell.prototype.setStateAfterDrag = function() {
  this.clickstate = 0;
}

LiveSheet.Cell.prototype.setNormal = function(inputel) {
  if(this.clickstate == 0) return;

  // enable the default undo behavior.
  undoManager.adjusttoolbar();

  var el = this.cellElement();

  // cellLeave and hiding the error hint fire in both highlighted
  // and focused states
  this.hideErrorHint(currentsheet.parentdiv);
  //sheetServer.callRemote('onCellLeave',this);

  if(this.focusedState() && inputel) {
    el.innerHTML = inputel.value;

    if(this.onchange()) {
      //this.clear();
      this.formula = inputel.value;
      // add the cell to the undo list.
      var undo = new LiveSheet.CellUndo(this);
      undoManager.add(undo);
      undo.doAction(); // update the server
    }
    else {
          el.innerHTML = this.getDispValue();
    }
  }
  this.clickstate = 0;  
};

LiveSheet.Cell.prototype.inputInCell = function(inputel) {
  return inputel.crow == this.row && inputel.ccol == this.col;
};

// genCustomStyles is used to reapply the style information and also
// to set the style information for the focus input
LiveSheet.Cell.prototype.genCustomStyles = function(stylebuf,focusDim,fullWidth) {
  var buff = stylebuf || [];
  var rs = currentsheet.sCache.rowstyle(this.row);
  if(rs) {
    rs.declaration(buff);
  }
  var cs = currentsheet.sCache.colstyle(this.col);
  if(cs) {
    cs.declaration(buff);
  };
  if(this.customStyle) {
    this.customStyle.declaration(buff);
  }

  buff.push('left:');   buff.push(this.left()+ (focusDim ? 1 : 0));
  buff.push("px;right:");buff.push(this.right()- (focusDim ? 1 : 0));
  buff.push("px;bottom:");buff.push(this.bottom()- (focusDim ? 1 : 0));
  buff.push("px;top:");buff.push(this.top()+ (focusDim ? 1 : 0));
  buff.push("px;width:");buff.push((focusDim || fullWidth) ? this.expandedwidth() : (this.width()-3)); // was this.width()-2
  buff.push("px;height:");buff.push(this.height()- (focusDim ? 2 : 0));
  buff.push("px;");
        
  if(!stylebuf) {
    return buff.join('');
  }
};

LiveSheet.Cell.prototype.setHighlighted = function(inputel) {
  this.clickstate = 1;
  // save off the current row & column for that the input is using
  inputel.crow = this.row;
  inputel.ccol = this.col;

  var s = inputel.style;
  // see if we have any custom styles in the row or column style cache.
  var buff = ['display:none;']
  this.genCustomStyles(buff,true); // true = set borders
  s.cssText = buff.join('');
  this.showErrorHint();

  LiveSheet.typeTracker.init(this.textlen || 0, // textlen is set when measureing the text
                             this.customStyle,
                             ((this.overflow && this.overflow[this.overflow.length-1]) || this.col),
                             this.expandedwidth());
  
  // update the toolbar with state of the cell's custom styles.
  LiveSheet.Sheetbar.updateState(this.customStyle);


};
LiveSheet.Cell.prototype.setFocused = function(inputel,nofocus,ev) {
  log('setFocused: cell ' + this.col + ' ' + this.row + ' is now being edited');
  log('setFocused: old text: ' + this.text + ' formula:' + this.formula);
  this.clickstate = 2;
  this.origformula = this.formula;
  LiveSheet.Sheetbar.disableUndo();
  
  inputel.style.display = "block";
  inputel.value = this.getformulavalue();

  if(!nofocus) {
    inputel.focus();
//     var x = ev.pageX;
//     var y = ev.pageY;
//     callLater(0,function(pageX,pageY,clientX,clientY,targetel) {
//              var ev = document.createEvent("MouseEvents");
//              ev.initMouseEvent("click",true,true,window,1,pageX,pageY,clientX,clientY,
//                                false,false,false,false,0,targetel);
//              inputel.dispatchEvent(ev);
//            },ev.screenX,ev.screenY,ev.clientX,ev.clientY,inputel);
    
  }
  this.setTextValue("");
  currentsheet.focusOutline(2);
};

////////////////////////////////////////////////////////////
// Cell reference methods
////////////////////////////////////////////////////////////

LiveSheet.Cell.prototype.notifyonkey = function(inputel,cellinput,keyval) {
  // set the clickstate to 3 (cellref) or 2 (focused) based on 
  // if based on teh current input the user is enter cell reference mode
  this.clickstate = LiveSheet.refmatch.test(inputel.value) ? 3 : 2;

  var targetwidth = LiveSheet.typeTracker.addChar(keyval);
  if(parseInt(cellinput.style.width.slice(0,-2)) != targetwidth) {
    cellinput.style.width = (targetwidth-1) + "px";
  }
};

LiveSheet.Cell.prototype.afterRef = function() {
  this.clickstate = 2; // focused
}

LiveSheet.Cell.prototype.normalState= function() {
    return this.clickstate == 0;
  };

LiveSheet.Cell.prototype.highlightedState= function() {
  return this.clickstate == 1;
};

LiveSheet.Cell.prototype.focusedState= function() {
  // note: this used to be a simple check if the state was 
  // identical.  however, focusedState is widespread and is 
  // often identical to the cellRefState.  So, cellRefState is *still* in
  // in the focusedState so for more checks focusedState is adequate.
  return this.clickstate >= 2;
};

LiveSheet.Cell.prototype.cellRefState = function() {
  return this.clickstate == 3;
}

LiveSheet.Cell.prototype.currentState = function() {
  return this.clickstate;
};

LiveSheet.Cell.prototype.setOpacity = function(percentage) {
  dojo.style.setOpacity(this.cellElement(),percentage);
};

LiveSheet.Cell.prototype.setLocked = function(lock) {
  this.cellElement().lockref = lock;
};

LiveSheet.Cell.prototype.clearLocked = function(lockUID) {
  // delete works in FF but not IE, probably because the IE objects
  // aren't implemented in javascript.
  // delete this.cellElement().lockref;
  var el = this.cellElement();
  if(dojo.render.html.ie) {
    el.attributes.removeNamedItem('lockref');
    return;
  }
  delete el.lockref;

};

// somewhat backwards logic but works with the context menu stuff
LiveSheet.Cell.prototype.locked = function() {
  return this.getLocked() == null;
};

LiveSheet.Cell.prototype.getLocked = function() {
  var a= this.cellElement().lockref;
  return typeof(a) != 'undefined' ? a : null;
};

LiveSheet.Cell.prototype.lockedremote = function(fromremote) {
  var el = this.cellElement(true);
  if(!el) { return false; }

  // check if a remote side tried to do something but this user has the lock.
  // the other side should blcok this anyway

  // check if we are trying to do something to a lock region
  // which we don not own.  This will let by commands that come from 
  // another client.

  return   (fromremote && el.lockref && el.lockref.owner) ? true : 
  ((el.lockref && !el.lockref.owner && !fromremote) ? true : false);

};

LiveSheet.Cell.prototype.stylePropExists = function(prop) {
  if(!this.customStyle) {
    return false;
  }
  return this.customStyle.exists(prop);
};

LiveSheet.Cell.prototype.setInheritedBackground = function(value) {
  // set the background color only if one does not exist
  if(this.customStyle && this.customStyle.get('background-color')) {
    return;
  }
  this.setBackground(value);
};

LiveSheet.Cell.prototype.setBackground = function(value,inheritedExt) {
  if(!value ||  (value  && value.match(/#[fF]{6}/))) {
        this.removeBackground(inheritedExt);
        return;
  }
  var cellel = this.cellElement();
  
  var bgkey = inheritedExt ? (this.key + "_bg_ih") : (this.key + '_bg');
  var el = getElement(bgkey);
  if(el) {
        el.style.backgroundColor = value;
  }
  else {
        var bg = DIV({'class':'cellbg',
                                         'id':bgkey,
                                         'style':{'left':this.left() + "px",
                                           'top':this.top() + "px",
                                           'right':this.right() + "px",
                                           'bottom':this.bottom()+'px',
                                           'width':this.width()+'px','height':this.height()+'px',
                                           'backgroundColor':value}});
        cellel.parentNode.appendChild(bg);
  }
  addElementClass(cellel,'cellnoborder');

};

LiveSheet.Cell.prototype._setCustomStyle = function(prop,value) {

  if(!this.customStyle) {
    this.customStyle = new LiveSheet.styleBuilder(".cell");
  }
  //value ? this.customStyle.update(prop,value) : this.customStyle.remove(prop);
  var pval = (value == null) ? "" : value;
  this.customStyle.update(prop,pval);

  if(/^__/.test(prop)) { // bypass hidden styles.
        return; 
  }
  var cellel = this.cellElement(true); // nothrow
  if(!cellel) {
        return;
  }

  if(prop == 'background-color') {
        this.setBackground(value);
        return; 
  }
  

  // to camelcase translates font-style to fontStyle
  var prop = dojo.style.toCamelCase(prop);
  cellel.style[prop] = pval;
  if(!pval && dojo.render.html.ie && prop == 'border') {
        var s = this.cellElement().style;
        s.borderLeft = "1px solid #C0C0C0";s.borderTop="1px solid #C0C0C0";
  }

  // apply to the input if this cell is currently focused.
  if(this.key == currentsheet.focusCell.key && currentsheet.focusCell.focusedState()) {
        currentsheet.inputcell.style[prop] = pval;
  }
};

LiveSheet.Cell.prototype.clearAndApplyStyles = function(ul,fromremote) {
  if(this.lockedremote(fromremote)) return;
  
  var cellel = this.cellElement(true); // nothrow
  if(!cellel) {
        return;
  }
  if(!ul.length && this.customStyle) {
        // this means that we need to get rid of our custom styles
        this.removeCustomStyleList(this.customStyle.proplist());
  }

  this.setCustomStyleList(ul,fromremote);
};

LiveSheet.Cell.prototype.setCustomStyleList = function(ul,fromremote) {
  if(this.lockedremote(fromremote)) return;
  for(var i=0;i<ul.length;i+=2) {
    this._setCustomStyle(ul[i],ul[i+1]);
  }
};

LiveSheet.Cell.prototype.removeBackground = function(inherited) {
  // this doesn't check if 
  var bgkey = inherited? (this.key+'_bg_ih') : (this.key + "_bg");
  var bg = getElement(bgkey);
  if(bg) {
    bg.parentNode.removeChild(bg);
    // note: this used to be outside the if statement.  was that necessary?
    removeElementClass(this.cellElement(),'cellnoborder');
  }
};

LiveSheet.Cell.prototype._removeCustomStyle = function(prop) {
  if(this.customStyle) {
        this.customStyle.remove(prop);
  }
  var cellel = this.cellElement(true); // nothrow
  if(!cellel) {
        return;
  }
  if(prop == 'background-color') {
        this.removeBackground();
        return;
  }

  var prop = dojo.style.toCamelCase(prop);
  cellel.style[prop] = "";
  if(dojo.render.html.ie && prop == 'border') {
    // craptastic hack - if you remove a style IE doesn't 
    // doesn't chain back up to class.
    var s = cellel.style;
    s.borderLeft = "1px solid #C0C0C0";s.borderTop="1px solid #C0C0C0";
  }

  // apply to the input if this cell is currently focused.
  if(this.key == currentsheet.focusCell.key && currentsheet.focusCell.focusedState()) {
        currentsheet.inputcell.style[prop] = "";
  }
};

LiveSheet.Cell.prototype.removeCustomStyleList = function(rl,fromremote) {
  if(this.lockedremote(fromremote)) return;

  forEach(rl,this._removeCustomStyle,this);

};

LiveSheet.Cell.prototype.reApplyCustomStyle = function(prop) {
  if(this.lockedremote()) return;

  if(this.customStyle) {
        var val = this.customStyle.get(prop);
        if(val) {
          this.cellElement().style[dojo.style.toCamelCase(prop)] = val;
        }
  }
};

LiveSheet.Cell.prototype.handleCollision = function(sheet) {

  var parent = this.cellElement().parentNode;
  var collide = new DocUtils.Widgets.editCollision(this.getformulavalue());
  collide.onaccept = bind(this.acceptCollision,this);
  //colide.onignore = bind(this.ignoreCollision,this);
        
  var st = getElement('rightscroller').scrollTop;
  var sl = getElement('bottomscroller').scrollLeft;

  var cw = sheet.sc.clientWidth;
  var ch = sheet.sc.clientHeight;

  // must test each of the four corners to see which side to draw on.
  var l = this.left();
  var r = this.right();
  var t = this.top();
  var b = this.bottom();
  var x=r,y=b; // defaults
  if((r - sl + 200) > cw) {
    x = l-200;
  }
  if((b -st + 200) > ch) {
    y = t-75;
  }
  collide.show(sheet.parentdiv,x,y);            
};

LiveSheet.Cell.prototype.acceptCollision = function() {
  // move the cell away from the highlighted state.
  this.setNormal(null);
  currentsheet.clickercb();
};

LiveSheet.Cell.prototype.revertToNormal = function() {
  this.text = this.origtext;
  this.formula = this.origformula;
  var el = this.cellElement();
  if(el) {
    el.innerHTML = this.getDispValue();
  }
  this.setNormal(null);
};

LiveSheet.Cell.prototype.maybeAdjustWidth = function() {

  if(this.stylePropExists('__sht')) {
    return;
  }

  var disp = this.getTextValue()
  this.textlen = LiveSheet.typeTracker.measureText(disp,this.customStyle);
  var rw = this.textlen;
  var width = this.expandedwidth();

  // step 1: see if there is shrinkage and that the real width is greater
  // then the column width.
  if(rw < width && (this._width && this._width <= width) && this.overflow) {
    // step 2: see in which column the new end point is located.
    var celldims = currentsheet.dimManager.celldims(this.left() + rw,this.top());
    
    // step 3: see if we need to shrink our overflow
    if(celldims.col < this.overflow[this.overflow.length-1]) {
      
      var coldim = currentsheet.dimManager.coldims(celldims.col);
      
      // step 4: adjust our width and the overflow cells          
      this.ReduceOverflow(celldims.col+1,coldim);
    }
  }
  // step 5: expansion
  else if(rw > width) {
    var celldims = currentsheet.dimManager.celldims(this.left()+rw,this.top());
    // make sure targetwidth is the entire column
    this.targetwidth = celldims.r - this.left();
    if(!this._width || (this._width && this._width == width) || !this.overflow) {
      // step 6: in this case the cell is growing beyond its bounds for the first time.
      this.ExpandOverflow(this.col+1);
    }
    else {
      // step 7: need to start the expandsion from the proper column
      var lastoverflowcol = this.overflow[this.overflow.length-1];
      if(celldims.col > lastoverflowcol) {
        // step 8: start expanding to the right from the last known expansion point
        this.ExpandOverflow(lastoverflowcol+1); 
      }
    }
  }
};


LiveSheet.Cell.prototype.adjustForOverflow = function(left,kwargs,nextNormalCell,coldims) {
  // determine the width of the text and see if it will overflow
  var disp = this.getTextValue();
  
  if(disp && !this.stylePropExists('__sht')) {
    this.textlen = LiveSheet.typeTracker.measureText(disp,this.customStyle);
    var rw = this.textlen;
    if(rw > kwargs.width) {
      // ok.  so our cell contents overflow the cell.  We now
      // need to check to see how many cells we are going to overwrite
      // and return that list (for later processing)
      kwargs.width = rw;
      kwargs.right = left + kwargs.width;
      // iterate through our cell cache looking for any valid keys.
      // if we find any we stop and adjust the width and right values.
      this.resetOverflow();
      var endcol = coldims ? coldims.length : LiveSheet.maxcol;
      for(var i=this.col+1;i<endcol;i++) {
        var coldim;
        if(coldims) {
          coldim = coldims[i];
        }
        else {
          coldim = currentsheet.dimManager.coldims(i);
        }
                
        var tkey = LiveSheet.cellkey(i,this.row);
        var overcell = currentsheet.cCache.getCell(tkey);
        if(overcell && overcell.formula) {
          this.regWouldOverflow(tkey);
          kwargs.right = coldim.startval;
          kwargs.width = kwargs.right - left;
          // since we haven't found the optimal end for our cell we
          // need to look it up.
          this.targetwidth = currentsheet.dimManager.celldimX(left+rw).end - left;
          break;
        }
        else {
          // increase our return value - this indicates that we want to skip this 
          // adjacent cell
          this.addOverflow(i);
          LiveSheet.overflow.update(tkey,this.key);
          nextNormalCell++;
          if(kwargs.right < coldim.end()) {
            // ensure that target width points to an entire cell width
            kwargs.right = coldim.end();
            kwargs.width = kwargs.right - left;
            this.targetwidth = kwargs.width;

            // ok. the length of our text is less then the end
            // of the current cell. done.
            break;
          }
        }
      }
    }
  }
  return nextNormalCell;
};

LiveSheet.Cell.prototype.addOverflow = function(col) {
  if(!this.overflow) {
        this.overflow = [];
  }
  this.overflow.push(col);
};
LiveSheet.Cell.prototype.doesOverflow = function() {
  return this.overflow != null && this.overflow.length > 0;
}

LiveSheet.Cell.prototype.resetOverflow = function() {
  if(this.overflow) { this.overflow = []; }
};

LiveSheet.Cell.prototype.regWouldOverflow = function(tkey) {
  if(!this.wouldoverflow) {
        this.wouldoverflow = {};
  }
  this.wouldoverflow[tkey] = true;
  LiveSheet.wouldOverflow.update(tkey,this.key);
};

LiveSheet.Cell.prototype.relWouldOverflow = function(tkey) {
  if(this.wouldoverflow) {
        delete this.wouldoverflow[tkey];
  }
  LiveSheet.wouldOverflow.removeIf(tkey,this.key);
};

LiveSheet.Cell.prototype.relAllOverflow = function() {
  if(this.wouldoverflow) {
        for(key in this.wouldoverflow) {
          LiveSheet.wouldOverflow.removeIf(key,this.key);
        }
  }
}

LiveSheet.Cell.prototype.ReduceOverflow = function(col,coldim) {
  // this function reduces the current cells overflow to the column argument.

  // step 1: remove the current overflow key.  There may be overflow keys to the right
  // of this column but they don't get cleaned up in this step.
  if(!coldim) {
        coldim = currentsheet.dimManager.coldims(col-1);
  }

  //var cwidth = this.expandedwidth();

  // step 2: check that our width wasn't already less than the width from the targetcell.
  // this can happen if we have orphaned overflow keys.
  //if(cwidth < coldim.val) {
  //    return;
  //}

  // step 3: adjust our cell element width and right style aspects.
  var cellel = this.cellElement();
  cellel.style.right = coldim.end() + "px";
  var width = coldim.end() - this.left();
  cellel.style.width = width + "px";

  // step 4: check if we _width set (indicating the column width rather than
  // the overflow width. if this value is now equal to the column width then
  // we can remove the property
  if(width == this._width) {
        delete this._width;
  }

  // step 5: iterate through the list of overflow cells and reset the
  // cell styles.
  var i;
  for(var i=0;i<this.overflow.length;i++) {
        if(this.overflow[i] == col) break;
  }
  var cleanup = i;
  for(;i<this.overflow.length;i++) {
        var cleancol = this.overflow[i];
        var tkey = LiveSheet.cellkey(cleancol,this.row);
        var buff = [];
        // only remove if it the entry belongs to me.
        LiveSheet.overflow.removeIf(tkey,this.key);
        this.regWouldOverflow(tkey);
        //currentsheet.getCellStyle(cleancol,this.row,buff,cleancol);
        removeElementClass(tkey,'celloverflow');
        //getElement(tkey).className = buff.join('');
  }

  this.overflow = this.overflow.slice(0,cleanup);

};


LiveSheet.Cell.prototype.ExpandOverflow = function(col) {

  // step 1: keep around the column width (if it is not there currently)
  if(!this._width) {
        this._width = this.width();
  }
  var left = this.left();
  var width = this.targetwidth;
  var right = left + width;

  // step 2: iterate to the right looking for cells to overflow
  for(var i=col;i<=LiveSheet.maxcol;i++) {
        coldim = currentsheet.dimManager.coldims(i);
        var tkey = LiveSheet.cellkey(i,this.row);
        var overcell = currentsheet.cCache.getCell(tkey);
        if(overcell && overcell.formula) {
          this.regWouldOverflow(tkey);
          right = coldim.startval;
          width = right - left;
          break;
        }
        else {
          this.relWouldOverflow(tkey);
          this.addOverflow(i);
          LiveSheet.overflow.update(tkey,this.key);
          //var buff = [];
          // i+1 to because we want to force the celloverflow style
          addElementClass(tkey,'celloverflow');
          //currentsheet.getCellStyle(i,this.row,buff,i+1); 
          //getElement(tkey).className = buff.join('');
          if(right <= coldim.end()) {
                break;
          }
        }
  }
  // step 3: get our cell element and extend outwards
  var cellel = this.cellElement();
  cellel.style.right = right + "px";
  cellel.style.width = width + "px";
};


// CellUndo is only concerned with the cell formula, not 
// any other attributes



LiveSheet.CellUndo = function(cell) {
  LiveSheet.UndoObject.call(this); // call base constructor
  this.oldformula = cell.origformula;
  this.formula = cell.formula;
  this.key = cell.key;
  this.cell = cell;
};

dojo.inherits(LiveSheet.CellUndo,LiveSheet.UndoObject);


dojo.lang.extend(LiveSheet.CellUndo, {
    //LiveSheet.CellUndo.prototype = {
  onSuccess:function(args) {
    // set the formula in case it was modified by the server
    var cells = args[0];
    for(var i=0;i<cells.length;i++) {
      if(cells[i].row == this.cell.row && cells[i].col == this.cell.col) {
        this.formula = cells[i].formula;
      }
    }
  },
  undo:function() {
        var current = currentsheet.cCache.getCell(this.key);
        current.formula = this.oldformula;
        return current.doChange();
  },
  redo:function() {
        var current = currentsheet.cCache.getCell(this.key);
        current.formula = this.formula;
        return current.doChange();
  },
  doAction:function() {
    this.cell.doChange().addCallback(bind(this.onSuccess,this));
  },
  valid:function() {
    var current = currentsheet.cCache.getCell(this.key);
    if(current) {
      return current.formula == this.formula;
    }
    return false; //
  },
  userString:function() {
        return 'typing: ' + this.formula;
  }
});

LiveSheet.ExcelPasteUndo = function(source,startcell) {
  // handle a paste from excel.  Excel "plain text" clipboard
  // events are seperated by \n for new lines and \t to seperate
  // cells.  The formula results are part of the paste, not the 
  // actually formula itself.  for that the user must use excel import

  LiveSheet.UndoObject.call(this);
  this.source = source;
  this.startcell = startcell;
  this.celllist = [];
  this.undocells = null;
};

dojo.inherits(LiveSheet.ExcelPasteUndo,LiveSheet.UndoObject);

dojo.lang.extend(LiveSheet.ExcelPasteUndo, {
        //LiveSheet.ExcelPasteUndo.prototype = {
  onSuccess:function(args) {
        undoManager.add(this);
  },
  undo:function() {
        return sheetServer.callRemote('onPasteCellBuffer',this.undocells,this.startcell);
  },
  redo:function() {
    var changelist = [];
        for(var i=0;i<this.celllist.length;i++) {
          var obj = this.celllist[i];
          var cell = currentsheet.cCache.createOnWrite(obj.col,obj.row);
          var oldfx = cell.formula;
          cell.formula = obj.formula;
          if(oldfx != cell.formula) {
                changelist.push(cell);
          }
        }
        return sheetServer.callRemoteWithCalc('onCellChange',changelist);       
  },
  doAction:function() {
        var maxR = this.startcell.row;
        var maxC = this.startcell.col;
        for(var i=0;i<this.source.length;i++) {
          var targetrow = this.startcell.row + i;
          if(!this.source[i].length) {
                continue;
          }
          var datarow = this.source[i].split('\t');
          for(var j = 0;j<datarow.length;j++) {
                if(datarow[j].length) {
                  var c = this.startcell.col + j;
                  maxR = Math.max(maxR,targetrow); maxC = Math.max(maxC,c);
                  this.celllist.push({'col':c,'row':targetrow,'formula':datarow[j]});
                }
          }
        }
        var endcell = currentsheet.cCache.createOnWrite(maxC,maxR);
        this.undocells = currentsheet.copyCells(this.startcell,endcell,false,true);
        this.redo().addCallback(bind(this.onSuccess,this));
  },
  valid:function() {
        for(var i=0;i<this.celllist.length;i++) {
          var obj = this.celllist[i];
          var cell = currentsheet.cCache.getCellByAttr(obj.col,obj.row);
          if(!cell || (cell && cell.formula != obj.formula)) {
                return false;
          }
        }
        return true;
  },
  userString:function() {
        return 'external paste';
  }
});



LiveSheet.FormGenUndo = function(start,end,formula) {
  LiveSheet.UndoObject.call(this);
  // we need to copy the cells because we need their state to be constant
  this.startcell = LiveSheet.copyCell(start);
  this.endcell = LiveSheet.copyCell(end);
  this.formula = formula;

}

dojo.inherits(LiveSheet.FormGenUndo,LiveSheet.UndoObject);


dojo.lang.extend(LiveSheet.FormGenUndo, {
//LiveSheet.FormGenUndo.prototype = {
  onSuccess:function(args) {
    // this is called on a succesful result from the server
    this.cells = args[0];
    this.checkformulas = args[1];
    this.strRange = args[2];
    
    undoManager.add(this);
  },

  undo:function() {
        changelist = [];
    for(var i=0;i<this.cells.length;i++) {
      var ucell = this.cells[i];
      var cell = currentsheet.cCache.getCellByAttr(ucell.col,ucell.row);
      if(cell) {
                cell.formula = ucell.formula;
                changelist.push(cell);
      }
    }
    return sheetServer.callRemoteWithCalc('onCellChange',changelist);
  },
  redo:function() {
      return sheetServer.callRemote('genFormula',this.formula,this.startcell,this.endcell);
  },
  doAction:function() {
    this.redo().addCallback(bind(this.onSuccess,this));
  },
  valid:function() {
    for(var i=0;i<this.cells.length;i++) {
      var ucell = this.cells[i];
      var cell = currentsheet.cCache.getCellByAttr(ucell.col,ucell.row);
      // the formula generation algorithm always puts formula's in empty
      // cells - so we can assume that if the cell is not empty it has been changed.
      if(cell && cell.formula != this.checkformulas[i]) {
                return false;
      }
    }
    return true;
  },
  userString:function() {
    return 'typing: ' + this.strRange
  }
});


LiveSheet.SortUndo = function(startcell,endcell,sortType) {
  LiveSheet.UndoObject.call(this);
  this.startcell = startcell;
  this.endcell = endcell;
  this.sortType = sortType; // should be a string
  if(this.sortType != 'asc' && this.sortType != 'desc') {
        throw new Error('sort type invalid');
  }
};

dojo.inherits(LiveSheet.SortUndo,LiveSheet.UndoObject);

dojo.lang.extend(LiveSheet.SortUndo, {
        //LiveSheet.SortUndo.prototype = {
   onSuccess:function(args) {
     this.changeCells = args;
         undoManager.add(this);
   },
   undo:function() {
     return sheetServer.callRemoteWithCalc('onPasteCellBag',this.cells);
   },
   redo:function() {
     return sheetServer.callRemote('sortCells',this.sortType,this.startcell,this.endcell);
   },
   doAction:function() {
         this.cells = currentsheet.copyCells(this.startcell,this.endcell,false,true);
         this.redo().addCallback(bind(this.onSuccess,this));
   },
   valid:function() {
        for(var i=0;i<this.changeCells.length;i++) {
          var changecell = this.changeCells[i];
          var cell = currentsheet.cCache.getCellByAttr(changecell.col,changecell.row);
          if(cell && changecell.formula != cell.formula) {
                return false;
          }
        }
        return true;
   },
   userString:function() {
     return 'sorted ' + (this.sortType == 'asc' ? 'ascending' : 'descending')
   }
  });


LiveSheet.ColSortUndo = function(col,sortType) {
  LiveSheet.UndoObject.call(this);
  this.col = col;
  this.sortType = sortType;
  if(this.sortType != 'asc' && this.sortType != 'desc') {
        throw new Error('sort type invalid');
  }
}


dojo.inherits(LiveSheet.ColSortUndo,LiveSheet.UndoObject);


dojo.lang.extend(LiveSheet.ColSortUndo, {
        //LiveSheet.ColSortUndo.prototype = {
  onSuccess:function(args) {
        this.changeData = args;
        undoManager.add(this);
  },
  undo:function() {
   return sheetServer.callRemote('undoColSort',this.col,this.cells);
  },
  redo:function() {
        return sheetServer.callRemote('sortCol',this.col,this.sortType);
  },
  doAction:function() {
        this.cells = currentsheet.copyCol(this.col);
        this.redo().addCallback(bind(this.onSuccess,this));
  },
  valid:function() {
        var count = 0;
        var col = this.col;
        var cd = this.changeData;
        for(var i=0;i<this.changeData.length;i++) {
          var changecell = this.changeData[i];
          var cell = currentsheet.cCache.getCellByAttr(changecell.col,changecell.row);
          if((cell && cell.formula != changecell.formula) || !cell) {
                return false;
          }
        }
        return true;
  },
  userString:function() {
        return 'sorting column';
  }
});
