/* Copyright (C) 2006 Numbler LLC */
/* See LICENSE for details. */

// global handler for number comparison

if(typeof(LiveSheet) == 'undefined') {
  LiveSheet = {};
 };

if(typeof(log) == 'undefined') {
  log = function(){ print.apply(this,arguments); };
 };

LiveSheet.maxrow = 65536;
LiveSheet.maxcol = 256;

//
// enable for testing RB trees with numbers

// Number.prototype.compare = function(that) { retmurn this - that; };
Number.prototype.gt = function(that) { return this > that; };
Number.prototype.lt = function(that) { return this < that; };
Number.prototype.key = function() { return this; };

LiveSheet.dim = function(keyvalue,dimension,totaldim) {
  this.keyvalue = keyvalue;
  this.val = dimension;
  this.startval = totaldim;
};

LiveSheet.dim.prototype.inDim = function(test) {
  // [begin,end] semantics
  return test >= this.startval && test <= this.end();
};

LiveSheet.dim.prototype.toString = function() {
  return ['key:',this.keyvalue,'width:',this.val,'startval:',this.startval].join(' ');
};

LiveSheet.dim.prototype.compare = function(that) {
  return this.keyvalue - that.keyvalue;
};
LiveSheet.dim.prototype.gt = function(that) { return this.keyvalue > that.keyvalue; };
LiveSheet.dim.prototype.lt = function(that) { return this.keyvalue < that.keyvalue; };
LiveSheet.dim.prototype.key = function() { return this.keyvalue; };

// alternate comparison functions
LiveSheet.dim.prototype.acompare = function(that) { return this.startval - that.startval; }
  LiveSheet.dim.prototype.agt = function(that) { return this.startval > that.startval; };
LiveSheet.dim.prototype.alt = function(that) { return this.startval < that.startval; };
LiveSheet.dim.prototype.akey = function() { return this.startval; };


LiveSheet.dim.prototype.end = function() { return (this.startval + this.val); };

LiveSheet.dimManager = function(defaultRowHeight,defaultColWidth) {
  this.defheight= defaultRowHeight;
  this.defwidth = defaultColWidth;
  this.col_rbt = new RedBlackTree();
  this.row_rbt = new RedBlackTree();

  this.colBoundaryException = new MochiKit.Base.NamedError("ColumnBoundaryException");
  this.rowBoundaryException = new MochiKit.Base.NamedError("RowBoundaryException");
};

LiveSheet.dimManager.prototype.loadFromServer = function(specs) {
  this.defheight = specs.defheight;
  this.defwidth = specs.defwidth;

  this.lastdatacol = specs.maxColWithData;
  this.lastdatarow = specs.maxRowWithData;

  // format of each element is id, val
  for(var i=0;i<specs.rows.length;i++) {
    var row = specs.rows[i];
    this.addRowHeight(row.id,row.val);
  }
  for(i=0;i<specs.cols.length;i++) {
    var col = specs.cols[i];
    this.addColumnWidth(col.id,col.val);
  }
};

LiveSheet.dimManager.prototype.dumpCols = function() {
  var list = [];
  function handler(value) {
    list.push(value._value.keyvalue);
  };
  this.col_rbt.traverse(handler);
  return list;
};

// recalculate all of the nodes forward from the position of the node
LiveSheet.dimManager.prototype.recalc = function(tree,defaultValue,node) {
  if(!node) return;
        
  tree.defaultCompare(); // set the tree in default comparision mode

  // check if there are any nodes ahead of us.
  var totalsofar = 0;
  var lastnode;
        
  function traversalFunc(nodevalue) {
    var value = nodevalue._value;

    if(value.keyvalue < node.keyvalue) {
      totalsofar = value.end();
    }
    else {
      if(!totalsofar) {
        // looks like we were the first in the tree.
        node.startval = (value.keyvalue-1)*defaultValue;
        totalsofar = node.end();
        //log("setting the first node's start value: ",node.startval," totalsofar:",totalsofar,"Node val",node.val);
      }
      else {
        var delta = Math.max(0,(value.keyvalue - lastnode._value.keyvalue-1));
        value.startval = delta*defaultValue + totalsofar;
        totalsofar = delta*defaultValue + totalsofar + value.val;
      }
    }
    lastnode = nodevalue;
  }
  tree.traverse(traversalFunc);
};

LiveSheet.dimManager.prototype.addColumnWidth = function(col,width) {
  if(col < 1 || col > LiveSheet.maxcol) {
    throw this.colBoundaryException;
  }
  this.internalAdd(col,width,this.col_rbt,this.defwidth);
};
LiveSheet.dimManager.prototype.setDefaultColWidth = function(col) {
  this.addColumnWidth(col,this.defwidth);
};

LiveSheet.dimManager.prototype.addRowHeight = function(row,height) {
  if(row < 1 || row > LiveSheet.maxrow) {
    throw this.rowBoundaryException;
  }
  this.internalAdd(row,height,this.row_rbt,this.defheight);
};
LiveSheet.dimManager.prototype.setDefaultRowHeight = function(row) {
  this.addRowHeight(row,this.defheight);
};

LiveSheet.dimManager.prototype.internalAdd = function(key,val,rbt,defaultval) {
        
  rbt.defaultCompare(); // set the tree in default comparision mode
        
  var item = new LiveSheet.dim(key,val,0);
  var result = rbt.find(item);
  if(!result) {
    result = rbt.add(item)._value;
  }
  else {
    result.val = val;
  }
  this.recalc(rbt,defaultval,result);
};

LiveSheet.dimManager.prototype.findCol = function(col) {
  return this.col_rbt.find(new LiveSheet.dim(col,0,0));
};
LiveSheet.dimManager.prototype.findRow = function(row) {
  return this.row_rbt.find(new LiveSheet.dim(row,0,0));
};

LiveSheet.dimManager.prototype.getDims = function(searchval,rbt,defaultValue) {
  rbt.defaultCompare(); // set the tree in default comparision mode
        
  var query = new LiveSheet.dim(searchval,0,0);
  var result = rbt.atMost(query);
  if(result && result.keyvalue == searchval) {
    // very important to clone the result otherwise you can fuck up the tree later on!
    return clone(result);
  }
  query.val = defaultValue;
  if(!result) {
    query.startval = Math.max(0,(searchval-1)) * defaultValue
      }
  else {
    query.startval = (Math.max(0,(searchval - result.keyvalue - 1)) * defaultValue) + result.end();
  }
  // clone the query result so it doesn't get screwed up later on
  return query;
};

LiveSheet.dimManager.prototype.rowdims = function(row) {
  if(row < 1 || row > LiveSheet.maxrow) {
    throw this.rowBoundaryException;
  }
  return this.getDims(row,this.row_rbt,this.defheight);
};
LiveSheet.dimManager.prototype.findNonDefaultRow = function(row) {
  var res = this.rowdims(row);
  if(res.val != this.defheight) {
    return res;
  }
  return null;
}

LiveSheet.dimManager.prototype.coldims = function(col) {
  if(col < 1 || col > LiveSheet.maxcol) {
    throw this.colBoundaryException;
  }
  return this.getDims(col,this.col_rbt,this.defwidth);
};
LiveSheet.dimManager.prototype.findNonDefaultCol = function(col) {
  var res = this.coldims(col);
  if(res.val != this.defwidth) {
    return res;
  }
  return null;
};


LiveSheet.dimManager.prototype.moveCols = function(start,delta) {
  // move all of values for columns up from the starting point by delta.
  // return false if no work required, true if work occcurred.
  var newrbt = this.moveRbtValues(this.col_rbt,this.defwidth,start,delta);
  if(!newrbt) { return false; }
  this.col_rbt = newrbt;
  return true;
};

LiveSheet.dimManager.prototype.moveRows = function(start,delta) {
  // move all of values for columns up from the starting point by delta.
  // return false if no work required, true if work occcurred.
  var newrbt = this.moveRbtValues(this.row_rbt,this.defheight,start,delta);
  if(!newrbt) { return false; }
  this.row_rbt = newrbt;
  return true;
};



LiveSheet.dimManager.prototype.moveRbtValues = function(rbt,defaultval,start,delta) {

  var vlist = [];
  // copy all of the values out of the RBT
  rbt.traverse(function(x) { vlist.push(x._value); });
  if(!vlist.length) {
    return null;
  }

  var deletevals = delta < 0;
  // create new rbt
  var newrbt = new RedBlackTree();
  // append all the values into the new tree, modifying the ones >= start.
  for(var i=0;i<vlist.length;i++) {
    // dump ones that have the default width
    var entry = vlist[i];
    var key = entry.keyvalue;
    // skip default entries (if they exist) and values that are now deleted.
    if(entry.val == defaultval || (deletevals && key <= start && key >= (start + delta+1))) {
      continue; 
    }

    if(key >= start) {
      key += delta;
    }
    this.internalAdd(key,entry.val,newrbt,defaultval);
  };
  return newrbt;
};

LiveSheet.dimManager.prototype.findColRange = function(start,oldstart,oldval,end,forcenext) {
  var ret = this.findStartAndEnd(start,oldstart,oldval,end,this.col_rbt,this.defwidth,forcenext);
  ret.start = Math.max(1,ret.start);
  ret.end = Math.min(LiveSheet.maxcol,ret.end);
  return ret;
};

LiveSheet.dimManager.prototype.findRowRange = function(start,oldstart,oldval,end,forcenext) {
  var ret = this.findStartAndEnd(start,oldstart,oldval,end,this.row_rbt,this.defheight,forcenext);
  ret.start = Math.max(1,ret.start);
  ret.end = Math.min(LiveSheet.maxrow,ret.end);
  return ret;
};
        
LiveSheet.dimManager.prototype.findStartAndEnd = function(startoffset,oldstart,oldval,endoffset,rbt,defaultValue,
                                                          forcenext) {
  // search for the closest cell to the start.
  // Math.ceil( startoffset - results from atMostm
  var ret = {'start':0,'end':0,toString:function() {return [this.start,this.end].join(' ')} };
  rbt.alternateCompare();
        
  log('findStartAndEnd: called with',startoffset,oldstart,endoffset);
  //log('tree: ',rbt.toString())
        
  if(startoffset == 0) {
    ret.start = 1; // everything is one based
  }
  else {
    // indicates up or down movement


    var result = rbt.atMost(new LiveSheet.dim(0,0,startoffset));
    if(!result) {
      // nothing before us.  calculate what the closest value before startoffset
      // we pass down to the next check to see if amove is required.
      var key = Math.ceil(startoffset / defaultValue);
      result = new LiveSheet.dim(key,defaultValue,Math.max(0,key-1)*defaultValue);
    }
    if(result.inDim(startoffset)) {
      //log('atMost result is result',result.keyvalue);
      ret.start = result.keyvalue;
      //ret.start = Math.min(65535,Math.max(1,result.keyvalue + direction));
    }
    else {
      // calculate up from the result.
      //log('calculating up from the result');
      ret.start = result.keyvalue + Math.ceil((startoffset - result.end()) / defaultValue);
    }
    if(oldstart || oldval) {
      // we need to make sure that we move up or down in the direction indicated by the delta.
      var direction = startoffset >= oldstart ? 1 : -1;
      if(direction > 0) {
        ret.start = Math.max(oldval+1,ret.start);
      }
      else {
        ret.start = Math.min(oldval-1,ret.start);
      }
    }
    ret.start = Math.min(LiveSheet.maxrow,Math.max(1,ret.start));
  }
  rbt.defaultCompare();
        
  var startb = this.getDims(ret.start,rbt,defaultValue);
  if(forcenext && startb.startval < startoffset) {
    ret.start++;
    startb = this.getDims(ret.start,rbt,defaultValue);
  }
  var endt = startb.startval + (endoffset - startoffset);

  ret.end = this.findEndVal(startb,endt,rbt,defaultValue);

  log('findStartAndEnd: ',ret);
  // now to the end value.
  return ret;
};





LiveSheet.dimManager.prototype.findEndCol = function(startval,endOffset) {
  var cdim = this.coldims(startval);
  return {'start':startval,
          'end':this.findEndVal(cdim,cdim.startval + endOffset,this.col_rbt,this.defwidth)};
};

LiveSheet.dimManager.prototype.findEndRow = function(startval,endOffset) {
  var rdim = this.rowdims(startval);
  return {'start':startval,
          'end':this.findEndVal(rdim,rdim.startval + endOffset,this.row_rbt,this.defheight)};
};


LiveSheet.dimManager.prototype.findEndVal = function(searcher,endOffset,rbt,defaultValue) {

  rbt.defaultCompare();
  // startval is a single column or row.
  var result = rbt.atLeast(searcher);

  if(!result || (result && result.startval > endOffset)) {
    // the width is a simple calculation
    //log('no custom rows found, returning simple offset calculation');
    return searcher.keyvalue + Math.ceil((endOffset - searcher.end()) / defaultValue);
  }
  var endkey = result.keyvalue;
  var oldresult = result;

  while(result && (result.startval <= endOffset)) {
    oldresult = result;
    searcher.keyvalue = endkey+1;
    //log('looking for next biggest column at',searcher.keyvalue);
    result = rbt.atLeast(searcher);
    if(result) {
      //log('found',result.keyvalue,result.end());
      endkey = result.keyvalue;
    }
  };
  // oldresult should alway start before the end.
  //log('oldresult is',oldresult);
  endkey = oldresult.keyvalue;
  if(oldresult.end() <= endOffset) {
    //log(endkey,'is not quite big enough... padding out with extra data');
    endkey += Math.ceil((endOffset - oldresult.end()) / defaultValue);
  }
  return endkey;
};


LiveSheet.dimManager.prototype.findVal = function(val,rbt,defaultValue) {
  rbt.alternateCompare();
        
  var ret = {'begin':0,'end':0,'key':0};
        
  var result = rbt.atMost(new LiveSheet.dim(0,0,val));
  if(!result) {
    // beginning
    ret.begin = val - (val%defaultValue);
    ret.end = ret.begin+defaultValue;
    ret.key = Math.floor(ret.begin / defaultValue) + 1;
  }
  else if(val < result.end()) {
    ret.begin = result.startval;
    ret.end = result.end();
    ret.key = result.keyvalue;
  }
  else {
    // calculate up from the last found position
    var end = result.end();
    var diff = (val-end)%defaultValue;
    ret.begin = val - diff;
    ret.end = ret.begin + defaultValue;
    ret.key =((ret.begin - result.end()) / defaultValue) + result.keyvalue + 1;
  }
  return ret;
};

LiveSheet.dimManager.prototype.celldims = function(x,y) {
  var c = this.findVal(x,this.col_rbt,this.defwidth);
  var r = this.findVal(y,this.row_rbt,this.defheight);
  return {'l':c.begin,'t':r.begin,'r':c.end,'b':r.end,'row':r.key,'col':c.key,
      toString:function() { 
      return ['l:',this.l,'r:',this.r,'t:',this.t,'b:',this.b,
              'col:',this.col,'row:',this.row].join(' '); }};
};

LiveSheet.dimManager.prototype.celldimX = function(x) {
  return this.findVal(x,this.col_rbt,this.defwidth);
};


