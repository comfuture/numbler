/* Copyright (C) 2006 Numbler LLC */
/* See LICENSE for details. */

if(typeof(LiveSheet) == 'undefined') {
  LiveSheet = {};
 };

// getElement = function(id) {
//      var ret = MochiKit.DOM.getElement(id);
//      if(ret) { return ret; }

//      return window.frames['scrollcontainer'].document.getElementById(id);

// };

if(typeof(DocUtils) == 'undefined') {
  throw('LiveSheet requires docUtils');
 };

if(typeof(DocUtils.Clipboard) == 'undefined') {
  throw('LiveSheet requires DocUtils.Clipboard');
 };


function removeChildren(parent,elList) {
  var f = function(val) { return getElement(val); }
  var me = parent;
  var r  = function(val) { if(val) { return me.removeChild(val);} }
  forEach(map(f,elList),r);
}

////////////////////////////////////////////////////////////////////////////////
// clipboardItem
////////////////////////////////////////////////////////////////////////////////

LiveSheet.clipboardItem = function(sourceCells,startcell,endcell,destructive) {
  if(arguments.length == 0) {
    return;
  }
  // if we only have a single cell
  if(!isArrayLike(sourceCells)) {
    sourceCells.refresh(); 
    this.source = LiveSheet.copyCell(sourceCells);
    this.startcell = this.source;
    this.endcell = this.source;
    this.destructive = destructive || false;
  }
  else {
    this.startcell = startcell;
    this.endcell = endcell;
    this.source = sourceCells;
    this.destructive = destructive;
  }
};

LiveSheet.clipboardItem.prototype.copyConstruct = function(copy) {
  this.startcell = LiveSheet.copyCell(copy.startcell);
  this.endcell = LiveSheet.copyCell(copy.endcell);
  this.source = clone(copy.source);
};

var clipKeys = ['source','startcell','endcell'];

LiveSheet.clipboardItem.prototype.json = function() {
  return {
    'source':this.source,
    'startcell':this.startcell,
    'endcell':this.endcell
  }
};


////////////////////////////////////////////////////////////////////////////////
// selectionFloater class - used for overlays
////////////////////////////////////////////////////////////////////////////////

LiveSheet.floaterIds = ['floater','__fl1','__fl2','__fl3','__fl4'];

LiveSheet.selectionFloater = function(sheet,startcell,selType) {
  this.sheet = sheet;
  this.selectionEl = getElement('floater');
  if(this.selectionEl) {
    this.dragtop = $('__fl1');this.dragbot = $('__fl2');
    this.dragleft = $('__fl3');this.dragright = $('__fl4');

    this.unbindhandlers();
    this.bindhandlers();
  };
  this.startcell = startcell;
  this.endcell = null;
  this.contextmenu = null;
  this.visible = false;
  this.selType = (typeof(selType) == 'undefined') ? 'region' : selType;
};

LiveSheet.selectionFloater.prototype.active = function() {
  return this.selectionEl != null;
};

LiveSheet.selectionFloater.prototype.onFinal = function() {
  // called when the floater is finalized
};

LiveSheet.selectionFloater.prototype.create = function() {
  this.selectionEl = DIV({'id':'floater'},null);
  var p = this.sheet.parentdiv;
  this.bindhandlers();
  p.appendChild(this.selectionEl);
  this.dragtop = DIV({'class':'floaterH','id':'__fl1'},null);
  p.appendChild(this.dragtop);
  this.dragbot = DIV({'class':'floaterH','id':'__fl2'},null);
  p.appendChild(this.dragbot);
  this.dragleft = DIV({'class':'floaterV','id':'__fl3'},null);
  p.appendChild(this.dragleft);
  this.dragright = DIV({'class':'floaterV','id':'__fl4'},null);
  p.appendChild(this.dragright);

  this.sheet.regdragger = new LiveSheet.regiondrag(this.sheet,this.dragtop,this.dragbot,
                                                   this.dragleft,this.dragright);

};

LiveSheet.selectionFloater.prototype.unbindhandlers = function() {
  this.selectionEl.oncontextmenu = null;
};
LiveSheet.selectionFloater.prototype.bindhandlers = function() {
  dojo.event.browser.addListener(this.selectionEl,'contextmenu',bind(this.oncontextmenu,this),false);
};

LiveSheet.selectionFloater.prototype.onhide = function(el) {
  var me = this;
  el.stopPropagation();
  setTimeout(function() { me.cleanup(); },100);
};

LiveSheet.selectionFloater.prototype.oncontextmenu = function(ev) {

  var sortOps = this.sheet.ctxSortMenu;
  
  sortOps.desc.setDisabled(this.selType == 'row');
  sortOps.asc.setDisabled(this.selType == 'row');

  this.sheet.deleteSubRows.setDisabled(this.selType == 'col');
  this.sheet.deleteSubCols.setDisabled(this.selType == 'row');
  this.sheet.insertSubRows.setDisabled(this.selType == 'col');
  this.sheet.insertSubCols.setDisabled(this.selType == 'row');

  this.sheet.autoformulaentry.setDisabled(this.selType != 'region');
  this.sheet.fmenu.onOpen(ev);
  dojo.event.browser.stopEvent(ev);
};

LiveSheet.selectionFloater.prototype.adjustFocus = function() {
  if(this.startcell.key != this.sheet.focusCell.key) {
    this.sheet.focusCell = this.startcell;
    this.sheet.clickercb();
  }
};

LiveSheet.selectionFloater.prototype.move = function(currentcell) {
        
  //bench = new DocUtils.benchmark();
  //bench.mark();

  this.endcell = currentcell;
  if(!this.active()) {
    this.create();
  }

  if(!currentcell.UserCell()) {
    return;
  }
  //log('move:',this.startcell.col,this.startcell.row,currentcell.col,currentcell.row);

  var el = this.selectionEl;
  this.visible = true;
  forEach(LiveSheet.floaterIds,showElement);
  //bench.mark();

  var l = Math.max(this.sheet.leftoffset(),Math.min(this.startcell.left(),currentcell.left()));
  var t = Math.max(this.sheet.topoffset(),Math.min(this.startcell.top(),currentcell.top()));
  var r = Math.max(this.startcell.right(),currentcell.right()) -2;
  var b = Math.max(this.startcell.bottom(),currentcell.bottom()) -2;

  el.style.left = l + "px";
  el.style.top = t + "px";
  el.style.right = r + "px";
  el.style.bottom = b + "px";
  el.style.height = (b - t) + "px";
  el.style.width = (r -l) + "px";

  var w = r - l;
  var h = b - t;

  var style = this.dragtop.style;
  style.left = l + 'px';style.right = r + 'px';
  style.top = t + 'px';style.bottom = (t+1)+'px';style.width = w + 'px';
  
  style = this.dragbot.style;
  style.left=l+'px';style.right=r+'px';style.top = b + 'px';
  style.bottom=(b+2)+'px';style.width=(w+1)+'px';
  
  style = this.dragleft.style;
  style.left=l+'px';style.right=(l+1)+'px';style.top=t+'px';style.bottom=b+'px';
  style.height=h+'px';
  
  style=this.dragright.style;
  style.left=r+'px';style.right=(r+1)+'px';style.top=t+'px';style.bottom=b+'px';
  style.height=(h+2)+'px';

  //bench.mark();
  //bench.report();

};

LiveSheet.selectionFloater.prototype.cleanup = function() {
  forEach(LiveSheet.floaterIds,hideElement);
  this.sheet.fmenu.close();
  this.visible = false;
};


LiveSheet.selectionFloater.prototype.pointInSelection = function(ev) {

  var curEvent = this.sheet.normalize(ev);
  try {
    if(this.endcell) {
      return this.startcell.inCellRange(this.endcell,curEvent.x,curEvent.y);
    }
    else {
      return this.startcell.inCell(curEvent.x,curEvent.y); 
    }
  }
  catch(e) {
    // we can get a cellexception error if the selection is no longer visible
    if(!(e instanceof LiveSheet.CellException)) {
      throw e;
    }
  }
  return false;
};

LiveSheet.selectionFloater.prototype.copySel = function() {
  this.onSelOperation(false);
  sheetServer.callRemote('onCopyCells',this.sheet.clipboard.last());
};

LiveSheet.selectionFloater.prototype.cutSel = function() {
  var normal = this.sheet.normalizeCells(this.startcell,this.endcell);
  var undo = new LiveSheet.CutUndo(normal.start,normal.end,this.sheet);
  undo.doAction();
};

LiveSheet.selectionFloater.prototype.clearSel = function() {
  var normal = this.sheet.normalizeCells(this.startcell,this.endcell);
  var undo = new LiveSheet.ClearUndo(normal.start,normal.end);
  undo.doAction();
};

LiveSheet.selectionFloater.prototype.onSelOperation = function(purge) {
  var copiedcells = this.sheet.copyCells(this.startcell,this.endcell,purge);
  var clipitem = new LiveSheet.clipboardItem(copiedcells,this.startcell,this.endcell,purge);
  this.sheet.clipboard.push(clipitem);
};

LiveSheet.selectionFloater.prototype.doFormulaGen = function(formula) {
  var undo = new LiveSheet.FormGenUndo(this.startcell,this.endcell,formula);
  undo.doAction();
};

LiveSheet.selectionFloater.prototype.insertRows = function() {
  var undo = new LiveSheet.InsertRowUndo(this.startcell.row,this.endcell.row);
  return undo.doAction();
};

LiveSheet.selectionFloater.prototype.deleteRows = function() {
  var undo = new LiveSheet.DeleteRowUndo(this.startcell.row,this.endcell.row);
  return undo.doAction();
};

LiveSheet.selectionFloater.prototype.insertColumns = function() {
  var undo = new LiveSheet.InsertColUndo(this.startcell.col,this.endcell.col);
  return undo.doAction();
};

LiveSheet.selectionFloater.prototype.deleteColumns = function() {
  var undo = new LiveSheet.DeleteColUndo(this.startcell.col,this.endcell.col);
  return undo.doAction();
};


LiveSheet.selectionFloater.prototype.lockregion = function() {
  var reg = new DocUtils.locking.lockregion();
  switch(this.selType) {
  case 'region':
    reg.setRegion(this.startcell,this.endcell); break;
  case 'row':
    reg.setRegionRow(this.startcell.row); break;
  case 'col':
    reg.setRegionCol(this.startcell.col); break;
  };

  this.sheet.lockmanager.requestLock(reg);
};

LiveSheet.selectionFloater.prototype.testalign = function() {
  // only for columns right now
  var col = this.startcell.col;
  var style = this.sheet.sCache.colstyle(col);
  if(!style) {
    style = this.sheet.sCache.newcolstyle(col);
  }
  style.update('text-align',['left','center','right'][Math.floor(Math.random()*3)]);
  style.save();


  var setstyle = function() {
    var startrow = currentsheet.cArea.startrow,endrow=currentsheet.cArea.endrow;
    for(var i=startrow;i<=endrow;i++) {
      var el = getElement(LiveSheet.cellkey(col,i));
      el.className = style.className;
    };
  };

  benchContainer(setstyle,'testalign:setstyle');        

};

////////////////////////////////////////////////////////////////////////////////
// Mousetracker
//
// Mousetracker is generally responsible for tracking sheet wide mouse events
// when those mouse events can't be properly handled by the containing element.
////////////////////////////////////////////////////////////////////////////////


LiveSheet.mousetracker = function(sheet) {
  this.sheet = sheet;
  this.tracking = false; // not tracking mouse movments (but still getting events)
  this.floatertracking = false; // tracking events inside an existing floater
  this.floater = null;
  this.glowHandler = null;
};

// setup the mouse tracker with the first event

LiveSheet.mousetracker.prototype.init = function(ev) {
        
  if(DocUtils.Widgets.modalVisible()) {
    this.floatertracking = false; this.tracking = false;
    return;
  }

  if(this.floater && this.floater.pointInSelection(ev) && ev.button == 2) {
    ev.stopPropagation();
    this.floatertracking = true;
  }
  else {
    this.initState(ev);
    ev.stopPropagation();
  };
};

LiveSheet.mousetracker.prototype.initState = function(ev) {
        
  var curEvent = this.sheet.normalize(ev);
  //log('event Y position:',ev.pageY || ev.y);
  //log('event X position:',ev.pageX || ev.x);
  log('event position',curEvent.x,curEvent.y);

  this.startcell = this.sheet.cellfrompos(curEvent.x,curEvent.y,true);
  this.endcell = null;
  this.colselected = false;
  this.rowselected =false;

  //alert(this.startcell.toString());
  // the overlay that highlights the selected region
  if(this.sheet.focusCell.cellRefState()) {
    this.floater = new LiveSheet.refarea(this.sheet,this.startcell);
  }
  else {
    this.floater = new LiveSheet.selectionFloater(this.sheet,this.startcell);
  }
  this.floater.cleanup();
  if(this.glowHandler) {
    //alert('stopping glow...');
    this.glowHandler.stop();
    this.glowHandler = null;
    getElement('floater').style.opacity = "0.5";
  }
  this.tracking = true;
};

LiveSheet.mousetracker.prototype.update = function(ev,isfinal) {

  if(this.tracking) {
    var _this = this;
    this.updateSelection(ev,isfinal);
  }
  else if(this.floatertracking) {
    this.updateFloater(ev,isfinal);
  }
  ev.stopPropagation();
};

LiveSheet.mousetracker.prototype.updateFloater = function(ev,isfinal) {
  if(isfinal && ev.button == 2) {// button == 2 is the right mouse
    //alert('right click');
    ev.stopPropagation();
  }
};


// handle event updates when doing a selection (not a floater click)
LiveSheet.mousetracker.prototype.updateSelection = function(ev,isfinal) {
  if(!this.tracking) { return; }

  var curEvent = this.sheet.normalize(ev);
  //var _this = this;
  // benchContainer(function() { _this.endcell = _this.sheet.cellfrompos(curEvent.x,curEvent.y); },'cellfrompos');
  this.endcell = this.sheet.cellfrompos(curEvent.x,curEvent.y,true); // use the cache

  if(isfinal) {
    this.floater.onFinal(ev);
    this.tracking = false;
  }

  if(!this.startcell) {
    log('updateSelection: startcell not defined!');
    return;
  }

  if(this.startcell.UserCell()) {
    if(this.endcell && !this.endcell.equals(this.startcell)) {
      var f = this.floater;
      f.adjustFocus();
      var c = this.endcell;
      f.move(c);
    }
  }
};

// LiveSheet.mousetracker.prototype.toString = function() {
//   return (this.startX + ' ' + this.startY + ' ' + this.endX + ' ' + this.endY);
// };

LiveSheet.mousetracker.prototype.selectColumn = function(column) {
  this.colselected = true;
  this.rowselected = false;
  var top = this.sheet.cCache.getCellByAttr(column,this.sheet.visiblerows.start);
  if(!top) {
    top = new LiveSheet.Cell(column,this.sheet.visiblerows.start);
  }
  var bottom = this.sheet.cCache.getCellByAttr(column,this.sheet.visiblerows.end);
  if(!bottom) {
    bottom = new LiveSheet.Cell(column,this.sheet.visiblerows.end);
  }
  this.doSelect(top,bottom,'col');
};

LiveSheet.mousetracker.prototype.selectRow = function(row) {
  this.rowselected = true;
  this.colselected = false;
  var left = this.sheet.cCache.getCellByAttr(this.sheet.visiblecols.start,row);
  if(!left) {
    left = new LiveSheet.Cell(this.sheet.visiblecols.start,row);
  }
  var right = this.sheet.cCache.getCellByAttr(this.sheet.visiblecols.end,row);
  if(!right) {
    right = new LiveSheet.Cell(this.sheet.visiblecols.end,row);
  }
  this.doSelect(left,right,'row');
};

LiveSheet.mousetracker.prototype.doSelect = function(startcell,endcell,seltype) {
  if(this.floater) {
    this.floater.cleanup();
  }
  this.floater = new LiveSheet.selectionFloater(this.sheet,startcell,seltype);
  this.floater.move(endcell);
};

////////////////////////////////////////////////////////////////////////////////
// cell helper functions
////////////////////////////////////////////////////////////////////////////////

var fromJSON = function(source) {
  return eval('(' + source + ')');
};


////////////////////////////////////////////////////////////////////////////////
// class for manipulating the spreadsheet
////////////////////////////////////////////////////////////////////////////////

LiveSheet.mainsheet = function() {};

LiveSheet.mainsheet.prototype.construct = function(dimensions) {

  this.dimManager = new LiveSheet.dimManager();
  this.dimManager.loadFromServer(dimensions);
  this.rowmarkerwidth = 20; // 20 pixels for the row markers
  this.stylestr = "2px solid red";
  this.normalborder = "1px solid #C0C0C0";
  this.parentdiv = getElement('mainbody');
  this.mousetrack = new LiveSheet.mousetracker(this);
  this.focusCell = null; // indicates the current cell in focus
  this.inputselect = '';
  this.fxselect = '';
  this.oldfocus = null; // previous cell in focus
  this.clipboard = new DocUtils.Clipboard();

  this.cCache = new LiveSheet.CellCache();
  this.cCache.registerExtentChangeCallback(bind(this.onExtentChange,this));

  this.formulainput = getElement('formulainput');
  dojo.event.browser.addListener(this.formulainput,'keypress',bind(this.onformulakeypress,this),false);
  dojo.event.browser.addListener(this.formulainput,'keydown',bind(this.onformulakeydown,this),false);
  dojo.event.browser.addListener(this.formulainput,'focus',bind(this.onformulafocus,this),false);
  dojo.event.browser.addListener(this.formulainput,'click',bind(this.onformulaclick,this),false);
  //dojo.event.browser.addListener(this.formulainput,'click',bind(this.onformulaclick,this),false);
        

  this.remoteupdate = false; // flag for keeping track of the update widget
  this.updatetimer = null;

  this.visiblecols = null; // contains dict of begin,end for visible cols
  this.visiblerows = null; // contains dict of begin,end for visible rows

  this.containerenabled = false;
  this.sc = getElement('scrollcontainer');
  this.formulaclicked = false;

  this.lockUI = new DocUtils.locking.lockUI(this.parentdiv,this);
  this.lockmanager = new DocUtils.locking.lockManager(this.lockUI);
  this.lockmanager.load(dimensions.locks); // load in an existing locks from the server

  this.cArea = {'startcol':0,'startrow':0,'endcol':0,'endrow':0};
  this.drawrect = new DocUtils.geometry.rect(1,1,1,1);
  this.viewArea = {'leftcol':1,'leftpos':0,'toprow':1,'toppos':0,'scrollY':0,'scrollX':0}
  this.viewrect = new DocUtils.geometry.rect(1,1,1,1);
  this.scrollYtimer = null;
  this.scrollXtimer = null;
  this.lastXscroll = null;
  this.lastYscroll = null;

  // exceptions
  this.elToCellConversion = new MochiKit.Base.NamedError("ElToCellConversion");

  // column changing
  this.colChanger = new LiveSheet.colChanger();
  // row changing
  this.rowChanger = new LiveSheet.rowChanger();
  //style manager
  this.sCache = new LiveSheet.styleCache();
  this.sCache.loadFromServer(dimensions.cols,dimensions.rows);

  this.conLostDlg = dojo.widget.manager.getWidgetById("lostconnection");

  this.cmenu = dojo.widget.manager.getWidgetById('cellpopup');
  // wire up event handlers
  dojo.event.connect(this.cmenu.findChild('copy'),'onClick',this,this.copySel);
  dojo.event.connect(this.cmenu.findChild('cut'),'onClick',this,this.cutSel);
  dojo.event.connect(this.cmenu.findChild('paste'),'onClick',this,this.pasteSel);
  dojo.event.connect(this.cmenu.findChild('lock'),'onClick',this,this.lockcell);
  dojo.event.connect(this.cmenu.findChild('unlock'),'onClick',this,this.unlockRegion);
  dojo.event.connect(this.cmenu.findChild('enable overflow'),'onClick',this,this.toggleOverflow);
  //short cuts
  this.cmenu._lock = this.cmenu.findChild('lock');
  this.cmenu._unlock = this.cmenu.findChild('unlock');
  this.cmenu._paste = this.cmenu.findChild('paste');
  this.cmenu._toggleoverflow = this.cmenu.findChild('enable overflow');


  this.fmenu = dojo.widget.manager.getWidgetById('floaterpop');
  dojo.event.connect(this.fmenu.findChild('copy'),'onClick',function() {
                       currentsheet.mousetrack.floater.copySel();
                     });
  dojo.event.connect(this.fmenu.findChild('cut'),'onClick',function() {
                       currentsheet.mousetrack.floater.cutSel();
                     });
  dojo.event.connect(this.fmenu.findChild('clear'),'onClick',function() {
                       currentsheet.mousetrack.floater.clearSel();
                     });

  this.autoformulaentry = this.fmenu.findChild('Auto Formula');
  this.autoformula = dojo.widget.manager.getWidgetById('autoformula');
  dojo.event.connect(this.autoformula.findChild('SUM'),'onClick',function() {
                       currentsheet.mousetrack.floater.doFormulaGen('sum');
                     });
  dojo.event.connect(this.autoformula.findChild('AVG'),'onClick',function() {
                       currentsheet.mousetrack.floater.doFormulaGen('avg');
                     });
  dojo.event.connect(this.autoformula.findChild('Count'),'onClick',function() {
                       currentsheet.mousetrack.floater.doFormulaGen('count');
                     });
  dojo.event.connect(this.autoformula.findChild('Max'),'onClick',function() {
                       currentsheet.mousetrack.floater.doFormulaGen('Max');
                     });
  dojo.event.connect(this.autoformula.findChild('Min'),'onClick',function() {
                       currentsheet.mousetrack.floater.doFormulaGen('Min');
                     });

  this.ctxSortMenu = {}
  this.ctxSortMenu.desc = this.fmenu.findChild('sort descending');

  dojo.event.connect(this.ctxSortMenu.desc,'onClick',function() {
                       currentsheet.doSort('desc');
                     });

  this.ctxSortMenu.asc = this.fmenu.findChild('sort ascending');

  dojo.event.connect(this.ctxSortMenu.asc,'onClick',function() {
                       currentsheet.doSort('asc');
                     });
  dojo.event.connect(this.fmenu.findChild('lock region'),'onClick',function() {
                       currentsheet.mousetrack.floater.lockregion();
                     });

  this.insertSub = dojo.widget.manager.getWidgetById('insertSub');
  this.insertSubRows = this.insertSub.findChild('insert rows');
  this.insertSubCols = this.insertSub.findChild('insert columns');

  dojo.event.connect(this.insertSubRows,'onClick',function() {
                       currentsheet.mousetrack.floater.insertRows();
                     });
  dojo.event.connect(this.insertSubCols,'onClick',function() {
                       currentsheet.mousetrack.floater.insertColumns();
                     });

  this.deleteSub = dojo.widget.manager.getWidgetById('deleteSub');
  this.deleteSubRows = this.deleteSub.findChild('delete rows');
  this.deleteSubCols = this.deleteSub.findChild('delete columns');

  dojo.event.connect(this.deleteSubRows,'onClick',function() {
                       currentsheet.mousetrack.floater.deleteRows();
                     });
  dojo.event.connect(this.deleteSubCols,'onClick',function() {
                       currentsheet.mousetrack.floater.deleteColumns();
                     });


  this.formatSub = dojo.widget.manager.getWidgetById('formatSub');
  dojo.event.connect(this.formatSub.findChild('none'),'onClick',function() {
                       currentsheet.setCurrencyStyle('');
                     });
  dojo.event.connect(this.formatSub.findChild('currency'),'onClick',function() {
                       currentsheet.setCurrencyStyle('$');
                     });
  dojo.event.connect(this.formatSub.findChild('percentage'),'onClick',function() {
                       currentsheet.setCurrencyStyle('%');
                     });
  dojo.event.connect(this.formatSub.findChild('comma style'),'onClick',function() {
                       currentsheet.setCurrencyStyle(',');
                     });

  var datesub = dojo.widget.manager.getWidgetById('fmtDateSub');
  dojo.event.connect(datesub.findChild('Date and time (combined)'),'onClick',function() {
                       currentsheet.setCurrencyStyle('dt');
                     });
  dojo.event.connect(datesub.findChild('Long date format'),'onClick',function() {
                       currentsheet.setCurrencyStyle('ld');
                     });
  dojo.event.connect(datesub.findChild('Medium date format'),'onClick',function() {
                       currentsheet.setCurrencyStyle('md');
                     });
  dojo.event.connect(datesub.findChild('Short date format'),'onClick',function() {
                       currentsheet.setCurrencyStyle('sd');
                     });

  var timeSub = dojo.widget.manager.getWidgetById('fmtTimeSub');
  dojo.event.connect(timeSub.findChild('time (minutes and hours)'),'onClick',function() {
                       currentsheet.setCurrencyStyle('mt');
                     });
  dojo.event.connect(timeSub.findChild('time (with seconds)'),'onClick',function() {
                       currentsheet.setCurrencyStyle('lt');
                     });

  this.rs = getElement('rightscroller');
  this.rsinsert = getElement('rightscrollinsert');
  this.bs = getElement('bottomscroller');
  this.bsinsert = getElement('bottominsert');

  this.helpwindow = null;
  getElement('faqlink').onclick = function() {
    if(currentsheet.helpwindow && !currentsheet.helpwindow.closed) {
      currentsheet.helpwindow.focus();
    }
    else {
      currentsheet.helpwindow = window.open("/support","Numbler Support",
                                            "width=800,height=600,scrollbars=yes");
    }
                       return false;
  };
  getElement('feedbacklink').onclick = function() {
    if(currentsheet.helpwindow && !currentsheet.helpwindow.closed) {
      currentsheet.helpwindow.focus();
    }
    else {
      currentsheet.helpwindow = window.open("/feedback","Contact Numbler",
                                            "width=800,height=600,scrollbars=yes");
    }
    return false;
  };                   

  this.inviteHandler = new LiveSheet.emailInvite();
};

LiveSheet.mainsheet.prototype.normalizeCells = function(cell1,cell2) {
  var rect = new DocUtils.geometry.rect(cell1.col,cell1.row,cell2.col,cell2.row);
  
  return {
    'start':this.cCache.createOnWrite(rect.l,rect.t,false,true), // false no copy, true no cache
      'end':this.cCache.createOnWrite(rect.r,rect.b,false,true)
      };
};
        
LiveSheet.mainsheet.prototype.normalize = function(ev) {
  if(dojo.render.html.ie) {
    return {'x':ev.x,
            'y':ev.y};
  }
  var xval = ev.pageX; 
  var yval = ev.pageY; 

  return {'x':(this.viewArea.leftpos + (xval - findPosX(this.parentdiv))),
      'y':(this.viewArea.toppos + (yval - findPosY(this.parentdiv)))}

};

LiveSheet.mainsheet.prototype.ignoreEvent = function(keyval,ev) {
  return (keyval.code == ev.KEY_TAB || keyval.code == ev.KEY_ENTER || 
          /*(keyval.code >= ev.KEY_LEFT_ARROW && keyval.code <= ev.KEY_DOWN_ARROW)  || */
          keyval.code == ev.KEY_ESCAPE);
  //&& !keyval.shift; // ignore events with the shift key
};

LiveSheet.mainsheet.prototype.processNonDirectional = function(ev) {
  var row = this.focusCell.row;
  var column =this.focusCell.col;
  var retval = false;
  if(ev.keyCode == ev.KEY_TAB) {
    this.changeSel(row,column+1,ev.keyCode);
  }
  else if(ev.keyCode == ev.KEY_ENTER) {
    this.changeSel(row+1,column,ev.keyCode);
  }
  else {
    retval = true;
  }
  return retval;
};


LiveSheet.mainsheet.prototype.processControlEvent = function(ev) {
  var row = this.focusCell.row;
  var column =this.focusCell.col;
  var retval = false;

  if(this.focusCell.focusedState()) {
    switch(ev.keyCode) {
    case ev.KEY_ESCAPE:
      // revert to highlighted state
      this.focusCell.revertToNormal();
      this.formulainput.value = this.focusCell.getformulavalue();
      this.clickercb();
      break;
    default:
      // only process tab and enter if we are focused.
      retval = this.processNonDirectional(ev);
    }
  }
  else if(this.focusCell.highlightedState()) {
    if(ev.shiftKey) {
      var f = this.mousetrack.floater;
      var t = (f && f.visible) ? f.endcell : this.focusCell;
      var col =t.col;
      var row = t.row;
      switch(ev.keyCode) {
      case ev.KEY_DOWN_ARROW:
        row = Math.min(LiveSheet.maxrow,row+1);break;
      case ev.KEY_RIGHT_ARROW:
        col= Math.min(LiveSheet.maxcol,col+1);break;
      case ev.KEY_UP_ARROW:
        row = Math.max(1,row-1);break;
      case ev.KEY_LEFT_ARROW:
        col = Math.max(1,col-1);break;
      default:
        retval= true;
      }
      if(!retval) {
        this.ignorenextkeypress = true;
        var dc = this.cellfrom(row,col);
        if(f && f.visible) {
          f.move(dc);
        }
        else {
          this.mousetrack.doSelect(this.focusCell,dc,'');
        }
      }
    }
    else if(ev.ctrlKey) {
      switch(ev.keyCode) {
        case ev.KEY_DOWN_ARROW:
        {
          var rows = {};
          rows.end = LiveSheet.maxrow;
          var dims = this.dimManager.rowdims(LiveSheet.maxrow);
          rows.start = this.dimManager.findRowRange(dims.end() - this.sc.clientHeight,0,0,dims.end()).start;
          this.adjustRowScroll(LiveSheet.maxrow);
          setScrollHeight(this.rs,(rows.start-1)*this.dimManager.defheight);
          this.lastYscroll = true;
          this.doscrollYinternal(rows);
        }
        break;
        case ev.KEY_RIGHT_ARROW:
        {
          var cols = {};
          cols.end = LiveSheet.maxcol;
          var dims = this.dimManager.coldims(LiveSheet.maxcol);
          cols.start = this.dimManager.findColRange(dims.end() - this.sc.clientWidth,0,0,dims.end()).start;
          this.adjustColScroll(LiveSheet.maxcol);
          setScrollWidth(this.bs,(cols.start-1)*this.dimManager.defwidth);
          this.lastXscroll = true;
          this.doscrollXinternal(cols);
        }
        break;
        case ev.KEY_UP_ARROW:
        {
          var rows = this.addPaddingRows(this.getVisibleRows(0,this.sc.clientHeight));
          this.lastYscroll = true;
          setScrollHeight(this.rs,0);
          this.doscrollYinternal(rows);
        }
        break;
        case ev.KEY_LEFT_ARROW:
        {
          var cols = this.addPaddingCols(this.getVisibleCols(0,this.sc.clientWidth));
          this.lastXscroll = true;
          setScrollWidth(this.bs,0);
          this.doscrollXinternal(cols);
        }
        break;
        case ev.KEY_END:
        this.changeSel(this.cCache.maxRow,this.cCache.maxCol,ev.keyCode);
        break;
        case ev.KEY_HOME:
        this.changeSel(1,1);
        break;
        default:
        retval= true;
      }
    }
    else {
      switch(ev.keyCode) {
        case ev.KEY_ENTER:
        case ev.KEY_DOWN_ARROW: // VK_DOWN
        this.changeSel(row+1,column,ev.keyCode);
        break;
        case ev.KEY_TAB: // tab
        case ev.KEY_RIGHT_ARROW: // VK_RIGHT
        // pass in the keycode so we can do special tab handling
        this.changeSel(row,column+1,ev.keyCode); 
        break;
        case ev.KEY_UP_ARROW: // VK_UP
        this.changeSel(row-1,column,ev.keyCode);
        break;
        case ev.KEY_LEFT_ARROW: // VK_LEFT
        this.changeSel(row,column-1,ev.keyCode);
        break;
        case ev.KEY_ESCAPE: // do nothing - just break
        break;
        case ev.KEY_PAGE_DOWN:
        var st = this.viewArea.toppos + this.sc.clientHeight;
        var rowrange = this.dimManager.findRowRange(st,0,0,st+this.sc.clientHeight);
        log('paging to',st,st+this.sc.clientHeight);
        this.lastYscroll = true;
        this.adjustRowScroll(rowrange.end);
        setScrollHeight(this.rs,st);
        this.doscrollYinternal(rowrange);
        break;
        case ev.KEY_PAGE_UP:
        if(this.viewArea.toppos == 0) { break; }
        var st = Math.max(0,this.viewArea.toppos - this.sc.clientHeight);
        var rowrange = this.dimManager.findRowRange(st,0,0,st+this.sc.clientHeight);
        log('paging to',st,st+this.sc.clientHeight);
        this.lastYscroll = true;
        this.adjustRowScroll(rowrange.end);
        setScrollHeight(this.rs,st);
        this.doscrollYinternal(rowrange);
        break;
        default:
        retval = true;
      }
    }
  }

  if(!retval) {
    log('processControlEvent: stopping event');
    dojo.event.browser.stopEvent(ev);
  }
  return retval;
};

LiveSheet.mainsheet.prototype.highlightedToFocused = function(ev,keyval,setInput) {
  this.clickercb();
  if(keyval.code != ev.KEY_BACKSPACE) {
    // keydown events come through with caps.
    if(dojo.render.html.ie || (dojo.render.html.mozilla && keyval.code in DocUtils.revfixupTable)) {
      this.inputcell.value = keyval.val;
      this.focusCell.notifyonkey(this.inputcell,this.inputcell,keyval);
    }
    else {
      this.inputcell.value = '';
    }
    if(setInput) {
      this.formulainput.value = keyval.val;
    }
    else {
      this.formulainput.value = '';
    }
  }
  else {
    log('stopping the goddamn backspace event');
    dojo.event.browser.stopEvent(ev);
    retval = true;
  }
};


LiveSheet.mainsheet.prototype.onformulakeydown = function(ev) {
  var keyval = DocUtils.eventchar(ev);
  this.keydowncode = keyval.code;
  log('onformulakeydown',keyval.code,keyval.val);
  if((!ev.shiftKey && keyval.code in DocUtils.fixupTable) 
     || (dojo.render.html.ie && ev.shiftKey && (ev.keyCode < ev.KEY_LEFT_ARROW || ev.keyCode > ev.KEY_DOWN_ARROW))) {
    log('onformulakeydown: ignoring key');
    return;
  }


  if(this.formulaclicked) {
    if(dojo.render.html.ie) {
      if(!this.processClipboardEvent(ev,this.formulainput,this.inputcell)) {
        return;
      }
    }
    if(dojo.render.html.mozilla && ev.keyCode >= ev.KEY_LEFT_ARROW && ev.keyCode <= ev.KEY_DOWN_ARROW) {
      this.ignorenextkeypress = true;
      return;
    }


    if(this.processNonDirectional(ev)) { // true retval value means not processed
      if(keyval.code == ev.KEY_BACKSPACE) {
        new DocUtils.managecursor(this.formulainput).backspace(this.inputcell);
      }
      else if(keyval.code == ev.KEY_DELETE) {
        new DocUtils.managecursor(this.formulainput).dodelete(this.inputcell);          
      }
    }
    else {
      dojo.event.browser.stopEvent(ev);
    };
    return;
  }

  var retval = false;

  // two steps:
  // 1) handle keyboard events for navigation.
  // 2) handle other keyboard events

  if(!this.processControlEvent(ev)) {
    if(dojo.render.html.mozilla) {
      log('ignoring next key press');
      this.ignorenextkeypress = true;
    }   
    return false;
  }

  // step 2
  if(this.focusCell.highlightedState()) {
    if(!keyval.ignore) { // cases like the shift,alt or ctrl keys
      if(!this.highlightedClipEvent(ev)) {
        if(dojo.render.html.mozilla) {
          this.ignorenextkeypress = true;
        }
        return false;
      }
      log('onformulakeydown: handling higlighted cell');
      this.highlightedToFocused(ev,keyval,dojo.render.html.ie); // true to set the formula input
    }
  }
  else if(keyval.code == ev.KEY_BACKSPACE) {
    new DocUtils.managecursor(this.formulainput).backspace(this.inputcell);
    //this.inputcell.value = this.inputcell.value.slice(0,this.inputcell.value.length-1);
    retval = true;
  }

  return retval;
};

LiveSheet.mainsheet.prototype.onformulakeypress = function(ev) {
  var keyval = DocUtils.eventchar(ev);
  //var input = this.focusCell.textarea();
  log('onformulakeypress',keyval.code,keyval.val,this.ignorenextkeypress);
  if(dojo.render.html.mozilla) {
    if(this.ignorenextkeypress) {
      this.ignorenextkeypress = false;
      return false;
    }
    // mozilla / firefox generates repeated events for navigation keys
    if(keyval.code in DocUtils.mozNavIgnore) {
      this.processControlEvent(ev);
      return false;
    }
  }
  if(! this.formulaclicked) {
    // this only seems to be necessary for FF as IE doesn't get these events
    if(this.focusCell.focusedState()) {
      if(!this.processControlEvent(ev)) {
        return false;
      }
    }
    if(this.ignoreEvent(keyval,ev)) {
      log('onformulakeypress: ignoring event');
      dojo.event.browser.stopEvent(ev);         
      return false;
    }
  }
  if(keyval.code == ev.KEY_ESCAPE) {
    if(!this.processControlEvent(ev)) {
      return false;
    }
  }
  if(keyval.code != ev.KEY_BACKSPACE && !this.ignoreEvent(keyval,ev)) {
    if(this.focusCell.highlightedState()) {
      log('onformulakeypress: higlightedToFocused');
      this.highlightedToFocused(ev,keyval,dojo.render.html.ie); // if IE set key into the formula bar
      //if(dojo.render.html.ie) {
      //        this.formulainput.
      //}
      return false; // for IE
    }
    else {
      if(!this.processClipboardEvent(ev,this.formulainput,this.inputcell)) {
        return;
      }

      var cursor = new DocUtils.managecursor(this.formulainput);
      if(keyval.code == ev.KEY_DELETE && this.keydowncode == ev.KEY_DELETE) {
        cursor.dodelete(this.inputcell);
      }
      else {
        cursor.insertat(this.inputcell,keyval.val);
        this.focusCell.notifyonkey(this.inputcell,this.inputcell,keyval);
      }
    }
  };
  return true;
};

LiveSheet.mainsheet.prototype.onformulafocus = function() {
  // if(this.focusCell && this.focusCell.focusedState()) {
  //            this.focusCell.onShowFormula();
  //    }
};

//LiveSheet.mainsheet.prototype.onformulablur = function(ev,targetCell) {
//  log('onformulablur', ev ? ev : "null");
//  var target = targetCell || this.focusCell;
//};

LiveSheet.mainsheet.prototype.onformulaclick = function(ev) {
  log('onformulaclick');
  this.formulaclicked = true;
  if(this.focusCell.highlightedState()) {
    this.focusCell.setFocused(this.inputcell,true);
  }
};

LiveSheet.mainsheet.prototype.calcmaxwidth = function() {
  return this.sc.clientWidth;
};

LiveSheet.mainsheet.prototype.calcmaxheight = function() {
  return this.sc.clientHeight;
};

LiveSheet.mainsheet.prototype.getRowHeight = function(i) {
  var retval = this.rowheights[i];
  // make sure we have a positive row height!! (this should be caught elsewhere as well)
  return Math.max(retval,20);
};

LiveSheet.mainsheet.prototype.getVisibleCols = function(left,right,padding) {

  var colrange = this.dimManager.findColRange(left,0,0,right);
  log('getVisibleCols',colrange.start,colrange.end);
  if(padding) {
    return this.addPaddingCols(colrange);
  }
  return colrange;
};

LiveSheet.mainsheet.prototype.addPaddingCols = function(colrange,scrolldir) {
  var padstart = 7;
  var padend = 7;
  if(scrolldir) {
    if(scrolldir == 'left') {
      padstart = 12; padend = 2;
    }
    else if(scrolldir == 'right') {
      padstart = 2; padend = 12;
    }
  }
  return {'start':Math.max(1,colrange.start-padstart),
          'end':Math.min(LiveSheet.maxcol,colrange.end+padend)};
};


LiveSheet.mainsheet.prototype.getVisibleRows = function(toprow,bottom,padding) {
        
  var rowrange = this.dimManager.findRowRange(toprow,0,0,bottom);
  log('getVisibleRows:',rowrange.start,rowrange.end);
  if(padding) {
    return this.addPaddingRows(rowrange);
  }
  return rowrange;

};

LiveSheet.mainsheet.prototype.addPaddingRows = function(rowrange,scrolldir) {
  var padstart = 7;
  var padend = 7;
  if(scrolldir) {
    if(scrolldir == 'up') {
      padstart = 12;
      padend = 2;
    }
    else if(scrolldir == 'down') {
      padstart = 2;
      padend = 12;
    }
  }
  return {'start':Math.max(1,rowrange.start-padstart),
          'end':Math.min(LiveSheet.maxrow,rowrange.end+padend)};
};

LiveSheet.mainsheet.prototype.topoffset =function() {
  return 0;
  //return this.parentdiv.offsetTop;
};

LiveSheet.mainsheet.prototype.leftoffset = function() {
  return 0;
  //return this.parentdiv.offsetLeft;
};

LiveSheet.mainsheet.prototype.atright = function(index) {
  return index == this.maxwidth;
};


LiveSheet.mainsheet.prototype.atbottom = function(index) {
  return index == this.maxcells;
};

LiveSheet.mainsheet.prototype.getCellStyle = function(indexleft,indextop,container,nextNormal) {

  var r = indexleft == this.maxwidth; // inlined
  var b = indextop == this.maxcells; // inlined
        
  container.push("cell ");
  if(indexleft != nextNormal) {
    container.push('celloverflow ')
      }
  else {
    if(r && b) {
      container.push('cellcorner ');
    }
    else if(r) {
      container.push('cellright ');
    }
    else if(b) {
      container.push('cellbottom ');
    }
  }
  if(this.sCache.rowexists(indextop)) {
    container.push('r');container.push(indextop);container.push(' ');
  }
  if(this.sCache.colexists(indexleft)) {
    container.push('c');container.push(indexleft);container.push(' ');
  }
};

LiveSheet.mainsheet.prototype.cellfrom = function(row,column) {
        
  var el = this.getCellElement(row,column);
  if(el) {
    return this.cellFromEl(el,true); // no cache
  }
  return null;
};

LiveSheet.mainsheet.prototype.getCellElement = function(row,column) {
  return getElement(LiveSheet.cellkey(column,row));
};


// LiveSheet.mainsheet.prototype.cellfromEvent = function(ev) {
        
//   var el;

//   if(dojo.render.html.mozilla) {
//     //el = ev.explicitOriginalTarget;
//     el = ev.originalTarget;
//   }
//   else {
//     el = ev.srcElement;
//   }
//   return this.cellFromEl(el);
// };

// var sumhelper = function(source) {
//   target = [0];
//   for(var i=0;i<source.length;i++) {
//     target.push(target[target.length-1]+parseInt(source[i]));
//   }
//   return target;
// };

// LiveSheet.mainsheet.prototype.recalcwidths = function() {
//   this.__maxwidth = sum(this.colwidths);
//   this.computedwidths = sumhelper(this.colwidths);
// };

LiveSheet.mainsheet.prototype.AdjustColumnWidth = function(columnID,newwidth) {

  this.dimManager.addColumnWidth(columnID,newwidth);
  if(columnID >= this.visiblecols.start && columnID <= this.visiblecols.end) {
    this.repaint();
  }
};

LiveSheet.mainsheet.prototype.repaint = function() {
  this.createViewArea();
  // check if we have a focusCell and if it is in the viewport
  if(this.focusCell && this.focusCell.cellElement(true)) {
    if(!chatwindow.focused) {
      this.clickercb();
    }
  }
  else {
    if(!chatwindow.focused) {
      window.focus();
    }
  }
};

LiveSheet.mainsheet.prototype.copyCol = function(col) {
  // processes the iterable of valid cells and copies them.
  return map(function(origCell) {
               return LiveSheet.copyCell(origCell);
             },this.cCache.getCellsByCol(col));
};
LiveSheet.mainsheet.prototype.copyRow = function(row) {
  return map(function(origCell) {
               return LiveSheet.copyCell(origCell);
             },this.cCache.getCellsByRow(row));
};
LiveSheet.mainsheet.prototype.copyCellsInRange = function(c1,r1,c2,r2) {
  return map(function(origCell) {
               return LiveSheet.copyCell(origCell);
             },this.cCache.getCellsInRange(c1,r1,c2,r2));
};


LiveSheet.mainsheet.prototype.copyCells = function(startCell,endCell,purge,full) {
  // check for inversion and fixup
  if(startCell.col > endCell.col || startCell.row > endCell.row) {
    var temp = endCell;
    endCell = startCell;
    startCell = temp;
  }

  var retCells = new Array();

  for(var i=startCell.col;i<=endCell.col;i++) {
    for(var j=startCell.row;j<=endCell.row;j++) {
      var c = this.cCache.getCellByAttr(i,j);
      if(c) {
        //c.refresh();
        retCells.push(LiveSheet.copyCell(c));
        if(purge) { c.blankCell(); }
      }
      else if(full){
        retCells.push(new LiveSheet.Cell(i,j));
      }
    }
  }
  return retCells;
};

LiveSheet.mainsheet.prototype.clearCells = function(startCell,endCell) {
  if(startCell.col > endCell.col || startCell.row > endCell.row) {
    var temp = endCell;
    endCell = startCell;
    startCell = temp;
  }
  for(var i=startCell.col;i<=endCell.col;i++) {
    for(var j=startCell.row;j<=endCell.row;j++) {
      var cell = this.cCache.getCellByAttr(i,j);
      if(cell) {
        cell.blankCell();
      }
    }
  }
};

LiveSheet.mainsheet.prototype.AdjustRowHeight = function(rowID,newheight) {

  this.dimManager.addRowHeight(rowID,newheight);
  if(rowID >= this.visiblerows.start && rowID <= this.visiblerows.end) {
    this.repaint();
  }
};
LiveSheet.mainsheet.prototype.cellfromEventPos = function(ev) {
  var x = ev.pageX || ev.clientX + document.body.scrollLeft;
  var y = ev.pageY || ev.clientY + document.body.scrollTop;
  x = currentsheet.viewArea.leftpos + (x - this.sc.offsetLeft);
  y = currentsheet.viewArea.toppos + (y - this.sc.offsetTop);
  return this.cellfrompos(x,y);
};

LiveSheet.mainsheet.prototype.cellfrompos = function(x,y,useCache) {
  // get a cell based on normalized coordinates
  var celldims = this.dimManager.celldims(x,y);
  var cell = null;
  if(useCache) {
    cell = this.cCache.getCell(LiveSheet.cellkey(celldims.col,celldims.row));
  }
  if(!cell) {
    return new LiveSheet.Cell(celldims.col,celldims.row);       
  }
  return cell;
};


LiveSheet.mainsheet.prototype.cellFromEl = function(el,nocache) {

  var keyfrom = el.id || el;
  var cell = this.cCache.getCell(keyfrom);
  if(!cell) {
    if(!keyfrom) {
      log('no keyfrom.slice!');
    };

    var key = LiveSheet.decomposeKey(keyfrom);
    if(keyfrom.slice(0,1) != 'k' || isNaN(key.col) || isNaN(key.row)) {
      //throw this.elToCellConversion;
      return null;
    }

    cell = new LiveSheet.Cell(key.col,key.row,keyfrom,el);
    if(typeof(nocache) == 'undefined' || nocache == false) {
      this.cCache.putCell(cell);
    }
  }
  return cell;
};

// LiveSheet.mainsheet.prototype.afterFocus = function(handler) {
//   this.deffocushandler = handler;
// };
// LiveSheet.mainsheet.prototype.procDefFocus = function() {
//   if(this.deffocushandler) {
//     this.deffocushandler();
//     this.deffocushandler = null;
//   }
// };

LiveSheet.mainsheet.prototype.inputcellclick = function(ev) {
  // this is necessary because in some browsers the click comes to the input
  // when in the highlighted case rather than to the div.  a bubbling thing?
  log('inputcellclick');
  this.formulaclicked = false;
  if(this.focusCell.highlightedState()) {
    this.focusCell.setFocused(this.inputcell,false,ev); 
  }
};

LiveSheet.mainsheet.prototype.clickercb = function(el,keycode,ev) {
  this.formulaclicked = false;

  if(el) {
    if(dojo.render.html.ie && window.event && !keycode) {
      // true = lookup from the cache first.
      var tempcell = this.cellfrompos(window.event.x,window.event.y,true);
      if(!this.focusCell || (this.focusCell && tempcell.key != this.focusCell.key)) {
        this.focusCell = tempcell;
      }
      el = this.focusCell.cellElement();
    }
    else if(!(this.focusCell && this.focusCell.key == el.id)) {
      this.focusCell = this.cellFromEl(el,true);
    }
  }
  else {
    el = this.focusCell.cellElement();
  }
  // double check that if we have a mouse event AND we are using firefox that 
  // we didn't get a bogus click event.
  if(dojo.render.html.mozilla && ev) {
    var coords = this.normalize(ev);
    if(!this.focusCell.inCell(coords.x,coords.y)) {
      log('bogus click event, skipping');
      return;
    }
  }

  log('clickercb: on cell ' + this.focusCell.col + ' ' + this.focusCell.row,this.focusCell.currentState());

  if(this.focusCell.normalState()) {
    log('clickercb: cell ' + this.focusCell.col + ' ' + this.focusCell.row + ' is now highlighted');

    if(this.oldfocus) {
      this.oldfocus.setNormal(this.inputcell);
    }

    // focus the formula input so it gets key events

    this.formulainput.focus();
    this.focusCell.setHighlighted(this.inputcell);
    this.formulainput.value = this.focusCell.getformulavalue();

    this.oldfocus = this.focusCell;
    this.focusOutline(3);
  }
  else if(this.focusCell.highlightedState()) {
    this.focusCell.setFocused(this.inputcell,false,ev);
    this.inputcell.focus();
  }
  else if(this.focusCell.focusedState()) {
    this.inputcell.focus();
  };

  // FIXME: does this matter anymore?
  if(keycode && keycode == 9 /* tab */) {
    return;
  }
};


LiveSheet.mainsheet.prototype.focusOutline = function(offset) {
        
  // copy from the cell object
  if(!this.spacertop) {
    var parent = this.parentdiv;
    this.spacertop = DIV({'class':'hspacer','id':'__hs1'},null);
    parent.appendChild(this.spacertop);
    this.spacerbottom = DIV({'class':'hspacer','id':'__hs2'},null);
    parent.appendChild(this.spacerbottom);
    this.spacerleft = DIV({'class':'vspacer','id':'__vs1'},null);
    parent.appendChild(this.spacerleft);
    this.spacerright = DIV({'class':'vspacer','id':'__vs2'},null);
    parent.appendChild(this.spacerright);
    this.celldragger = new LiveSheet.celldrag(this,this.spacertop,this.spacerbottom,this.spacerleft,this.spacerright);
  }
        
  offset = offset || 3;
  if(offset == 2) {
    this.spacertop.className = 'hspacer';this.spacerbottom.className='hspacer';
    this.spacerleft.className='vspacer';this.spacerright.className='vspacer';
  }
  else if(offset == 3) {
    this.spacertop.className = 'hspacer3';this.spacerbottom.className='hspacer3';
    this.spacerleft.className='vspacer3';this.spacerright.className='vspacer3';
                
  }
  var adj = offset-1;


  var left = this.focusCell.left();
  var right = this.focusCell.right();
  var top = this.focusCell.top();
  var bottom = this.focusCell.bottom();
  var width = this.focusCell.width();
  var height = this.focusCell.height();
        
  var style = this.spacertop.style;
  style.left = left + 'px';
  style.right = right + 'px';
  style.top = top + 'px';
  style.bottom = (top+adj)+'px';
  style.width = width + 'px';

  style = this.spacerbottom.style;
  style.left=left+'px';style.right=right+'px';style.top = bottom+'px';
  style.bottom=(bottom+adj)+'px';style.width=width+'px';
        
  style = this.spacerleft.style;
  style.left=left+'px';style.right=(left+adj)+'px';style.top=top+'px';style.bottom=bottom+'px';
  style.height=height+'px';
        
  style=this.spacerright.style;
  style.left=right+'px';style.right=(right+adj)+'px';style.top=top+'px';style.bottom=bottom+'px';
  style.height=(height+adj+1)+'px';


};


LiveSheet.mainsheet.prototype.onmousedown = function(ev) {
  if(!ev) return;
  if(this.cmenu.isShowing) {
    this.cmenu.close();
  }
  // mouse events to the spacers bubble out
  if(ev.target.id.slice(0,2) == '__') {
    return;
  }

  this.mousetrack.init(ev);
  if(!this.focusCell.focusedState()) {
    dojo.event.browser.stopEvent(ev);
  }
  return false;
};

LiveSheet.mainsheet.prototype.onmousemove = function(ev) {

  if(!ev) return;
        

  this.mousetrack.update(ev);
  if(!this.focusCell.focusedState()) {
    dojo.event.browser.stopEvent(ev);
  }
  return false;
};

LiveSheet.mainsheet.prototype.onmouseup = function(ev) {
  if(!ev) return;
        
  this.mousetrack.update(ev,true);
  if(!this.focusCell.focusedState()) {
    dojo.event.browser.stopEvent(ev);
  }
  return false;
};


LiveSheet.mainsheet.prototype.copySel = function() {
  var cell = this.cCache.createOnWrite(this.focusCell.col,this.focusCell.row);
  this.clipboard.push(new LiveSheet.clipboardItem(cell));
  sheetServer.callRemote('onCopyCells',this.clipboard.last());
};

LiveSheet.mainsheet.prototype.cutSel = function() {
  var undo = new LiveSheet.CutUndo(this.focusCell,this.focusCell,this);
  undo.doAction();
};

LiveSheet.mainsheet.prototype.pasteSel = function(ev) {
  if(this.clipboard.length() > 0) {
    var undo = new LiveSheet.PasteUndo(this.clipboard.last(),this.focusCell);
    undo.doAction();
  }
};

LiveSheet.mainsheet.prototype.toggleOverflow = function() {
  if(this.focusCell.stylePropExists('overflow')) {
    this.applyStyle(['overflow',''],true);
  }
  else {
    this.applyStyle(['overflow','visible']);
  }
};

LiveSheet.mainsheet.prototype.applyPaste = function(cell,clipboardItem) {

  startrow = Math.min(clipboardItem.startcell.row,clipboardItem.endcell.row)
  startcol = Math.min(clipboardItem.startcell.col,clipboardItem.endcell.col)
  var source = clipboardItem.source;
  if(isArrayLike(source)) {
    for(var i=0;i<source.length;i++) {
      var pastecell = source[i];
      var targetrow = cell.row + (pastecell.row - startrow);
      var targetcol = cell.col + (pastecell.col - startcol);
      this.cCache.createOnWrite(targetcol,targetrow,pastecell);
    }
  }
  else {
    this.cCache.createOnWrite(cell.col,cell.row,source);
  }
};

LiveSheet.mainsheet.prototype.changeSel = function(row,column,keycode) {
  if(row >= 1 && column >= 1 && row <= LiveSheet.maxrow && column <= LiveSheet.maxcol) {
    var cell = new LiveSheet.Cell(column,row);
    this.maybeScroll(cell);
    var el = cell.cellElement();
    if(el.lockref && !el.lockref.owner) {
      return;
    }
    this.clickercb(el,keycode);
  }
};

LiveSheet.mainsheet.prototype.doSelectInternal = function(target,savedval,ev) {
  if(document.selection) { // IE
    // IE seems to fire this event multiple times while the user is selecting.
    this[savedval] = document.selection.createRange().text;
  }
  else {
    var i = target;
    this[savedval] = i.value.slice(i.selectionStart,i.selectionEnd);
  }
  log('doSelectionIternal',this[savedval]);
};

LiveSheet.mainsheet.prototype.doRemotePaste = function(target,source) {

  // the *real* target is always focusCell
  var sourceln = source.value.length;
  var multirows = source.value.split('\n');
  if(multirows.length != sourceln) {
    // multiplerows.  see how many cells.
  }
  else if(source.value.match(/\t/)) {
    multirows = [source.value];
  }
  else {
    target.value = source.value;
    return;
  }
  var undo = new LiveSheet.ExcelPasteUndo(multirows,this.focusCell);
  undo.doAction();
  this.focusCell.revertToNormal();
  this.formulainput.value = this.focusCell.getformulavalue();
  this.clickercb();

};


LiveSheet.mainsheet.prototype.processClipboardEvent = function(ev,source,target) {
  // process a clipboard event like ctrl-c,ctrl-x,ctrl-v.  No
  // idea how this will work on the mac.  This is only if the cell is focused!

  // make sure that the event value is uppercase.
  var key = ev.keyCode || ev.which;
  // force lowercase
  var val = String.fromCharCode(key).toUpperCase();
  var retval = true;

  if(ev.ctrlKey) {
    if(val.charCodeAt(0) in DocUtils.modclipTable) {
      // paste
      setTimeout(function() { 
                   currentsheet.doRemotePaste(target,source);
                 },1);
      retval = false;
    }
    if(val == 'C' ||val == 'X') {
      // get the selection and put in the clipboard 
    }
    retval = false;
  }
  return retval;
};

LiveSheet.mainsheet.prototype.highlightedClipEvent = function(ev) {
  var key = ev.keyCode || ev.which;
  var val = String.fromCharCode(key).toUpperCase();
  var retval = true;  
  var ccode = val.charCodeAt(0);
  if(ev.ctrlKey && ccode in DocUtils.clipTable) {
    retval = false;
    var f = this.mousetrack.floater;
    switch(ccode) {
    case 67: // C
      (f && f.visible) ? f.copySel() : this.copySel();
        break;
    case 86: // V
      // paste what is in the clipboard to the focusCell
      this.pasteSel();
      break;
    case 88: // X
      // cut the current focuscell or selection
      (f && f.visible) ? f.cutSel() : this.cutSel();
        break;
    case 89: // Y
      undoManager.redo();
      // redo
      break;
    case 90: // Z
      // undo
      undoManager.undo();
      break;
    default:
      retval = true; // should never get here
    }

  }
  if(!retval) {
    dojo.event.browser.stopEvent(ev);
  }
  return retval;
};

LiveSheet.mainsheet.prototype.onkeypress = function(ev) {
  var keyval = DocUtils.eventchar(ev);
  log('input onkeypress: ',keyval.code,ev.ctrlKey);
  
  if(dojo.render.html.mozilla && this.ignorenextkeypress) {
    this.ignorenextkeypress = false;
    return;
  }
  if((this.focusCell.focusedState() && this.ignoreEvent(keyval,ev))
     || (!ev.shiftKey && keyval.code in DocUtils.fixupTable)) { 
    log('onkeypress: ignoring event');
    return;
  }
  // check if we have any of clipboard events
  //if(!this.processClipboardEvent(ev,this.inputcell,this.formulainput)) {
  //return false;
  //}

  // backspace handled in onkeydown
  if(keyval.code != ev.KEY_BACKSPACE && !(keyval.code == ev.KEY_DELETE && this.keydowncode == ev.KEY_DELETE)) {
    var cursor = new DocUtils.managecursor(this.inputcell);
    cursor.insertat(this.formulainput,keyval.val);
    this.focusCell.notifyonkey(this.formulainput,this.inputcell,keyval);
  }

};

LiveSheet.mainsheet.prototype.onkeydown = function(ev) {
  this.keydowncode = ev.keyCode;
  var row = this.focusCell.row;
  var column =this.focusCell.col;
  log('input onkeydown: ',ev.keyCode);

  // proces key commands (arrow, tab, return, etc)

  if(dojo.render.html.ie) {
    if(this.focusCell.highlightedState() && 
       !this.processClipboardEvent(ev,this.inputcell,this.formulainput)) {
      return;
    }
  }
  if(dojo.render.html.mozilla && ev.keyCode >= ev.KEY_LEFT_ARROW && ev.keyCode <= ev.KEY_DOWN_ARROW) {
    this.ignorenextkeypress = true;
    return;
  }
  
  if(!this.processControlEvent(ev)) {
    // ignore tab key it was from the input box and you are moving to the next cell -
    // onformulakeypress will get a tab event and we don't want it to day anything.
    if(ev.keyCode == ev.KEY_TAB && dojo.render.html.mozilla) {
      this.ignorenextkeypress = true;
      return;
    }
  }
  

  if(ev.keyCode == ev.KEY_BACKSPACE) {
    new DocUtils.managecursor(this.inputcell).backspace(this.formulainput);
  }
  else if(ev.keyCode == ev.KEY_DELETE) {
    new DocUtils.managecursor(this.inputcell).dodelete(this.formulainput);
  }
  //return false;
};

LiveSheet.mainsheet.prototype.oncontextmenu = function(ev) {
        
  var cell = this.cellfromEventPos(ev);
  if(this.focusCell) {
    if(cell.key != this.focusCell.key) {
      this.focusCell = cell;
      this.clickercb();
    }
  }
  else {
    this.focusCell = cell;
    this.clickercb();
    // put the cell in the highlighted state
  }

  var lk = this.focusCell.locked();
  this.cmenu._lock.setDisabled(!lk);
  this.cmenu._unlock.setDisabled(lk);
  this.cmenu._paste.setDisabled(this.clipboard.empty());
  this.cmenu.onOpen(ev);
  dojo.event.browser.stopEvent(ev);
};

LiveSheet.mainsheet.prototype.testcollide = function() {
  this.focusCell.refresh();
  var collide = new DocUtils.Widgets.editCollision(this.focusCell.getformulavalue());
  collide.show(this.parentdiv,this.focusCell.right(),this.focusCell.bottom());
};

LiveSheet.mainsheet.prototype.lockcell = function() {
  // lock a single cell
  var reg = new DocUtils.locking.lockregion();
  reg.setRegion(this.focusCell,this.focusCell);
  this.lockmanager.requestLock(reg);  
}

  LiveSheet.mainsheet.prototype.unlockRegion = function() {
    this.lockmanager.releaseLock(this.focusCell.getLocked())
  };

LiveSheet.mainsheet.prototype.onerror = function() {
  var errb = new DocUtils.Widgets.errorBox(this.parentdiv,'The copy area is larger than the paste area.','errorbox');
  errb.show(5);
};


LiveSheet.mainsheet.prototype.onresize = function(ev) {
  var colcont = getElement('colcontainer');
  var rowcont = getElement('rowcontainer');
  var sc = getElement('scrollcontainer');

  var colwidth = dojo.html.getViewportWidth() -50; //20 is fudge factor for scrollbar (and we have two of them potentially)
  var height = dojo.html.getViewportHeight() - findPosY(rowcont) -30; // fudge factor for scrollbar
  if(this.containerenabled) {
    colwidth *= 0.80;
  }

  colcont.style.width = (colwidth - findPosX(colcont)) + "px";
  rowcont.style.height = height + "px";
  sc.style.width = (colcont.style.width.slice(0,-2) - rowcont.style.width.slice(0,-2)) + "px";
  sc.style.height = (height - colcont.style.height.slice(0,-2)) + "px";

  this.rs.style.height = height + "px";
  this.bs.style.width = colwidth + "px";

  if(this.containerenabled) {
    var el = getElement('chatcontainer');
    el.style.width = (dojo.html.getViewportWidth() - findPosX(this.rs) - 
                      this.rs.style.width.slice(0,-2) - 50) + "px";
    el.style.height = this.sc.style.height;
    showElement(el);
    getElement('chatarea').style.height = (el.style.height.slice(0,-2) * .9) + "px";
    LiveSheet.Sheetbar.disableChatBubble();
    chatwindow.visible = true;
  }
  else {
    hideElement('chatcontainer');
    chatwindow.visible = false;
  }

};

LiveSheet.mainsheet.prototype.docmousemove = function(ev) {
  if(this.scrollYinprog && dojo.render.html.ie) {
    this.scrollYinprog = null;
  }
  if(this.scrollXinprog && dojo.render.html.ie) {
    this.scrollXinprog = null;
  }
};


LiveSheet.mainsheet.prototype.docmouseup = function(ev) {
  if(this.scrollYinprog) {
    this.scrollYinprog = null;
  }
    if(this.scrollXinprog) {
      this.scrollXinprog = null;
    }
  
  //log('docmouseup',ev.pageY||ev.y);
};

LiveSheet.mainsheet.prototype.docmousedown = function(ev) {
  log('docmousedown',ev.pageY||ev.y);
  if(this.rs == ev.target) {
    if(this.visiblerows.end == LiveSheet.maxrow) {
      return;
    }
    var t = ev.target;
    var clicky = (ev.pageY||ev.y);
    var height = findPosY(t) + t.offsetHeight;
    if(clicky >= height -13 && clicky <= height && 
       // check that the scrolling is at the bottom
       t.offsetHeight + t.scrollTop == t.scrollHeight) {
      // scrolll down by one row
      var rowrange = {'start':this.viewrect.t + 1,'end':this.viewrect.b+1};
      var rng = this.dimManager.rowdims(rowrange.start);
      this.generatedYscroll = true;
      this.generatedYRange = rowrange;
      this.movescrollY(rowrange.end);
      setScrollHeight(this.rs,(rowrange.start-1) * this.dimManager.defheight);
      
    }
  }
  else if(this.bs == ev.target) {
    if(this.visiblecols.end == LiveSheet.maxcol) {
      return;
    }
    var t = ev.target;
    var clickx = (ev.pageX||ev.x);
    
    // TODO: fix this (I don't really understand why I need 
    // to special case here
    var width = dojo.render.html.ie ? t.offsetWidth : (findPosX(t) + t.offsetWidth);
    if(clickx >= width - 13 && clickx <= width && 
       (dojo.render.html.ie ? t.clientWidth : t.offsetWidth) + t.scrollLeft == t.scrollWidth) {
      // XXX: fix this: should be just this.viewrect.r + 1
      var colrange = {'start':this.viewrect.l + 1,'end':this.viewrect.r+2};
      var rng = this.dimManager.coldims(colrange.start);
      this.generatedXscroll = true;
      this.generatedXRange = colrange;
      this.movescrollX(colrange.end);
      setScrollWidth(this.bs,(colrange.start-1) * this.dimManager.defwidth);
    }
  }
};

LiveSheet.mainsheet.prototype.movescrollY = function(bottomrow) {
  var s = this.rsinsert.style;
  var crow = parseInt(s.height.slice(0,-2)) / this.dimManager.defheight;
  if(crow < bottomrow) {
    s.height = (bottomrow * this.dimManager.defheight) + "px";
  }
};

LiveSheet.mainsheet.prototype.movescrollX = function(rightcol) {
  var s = getElement('bottominsert').style;
  var ccol = parseInt(s.width.slice(0,-2)) / this.dimManager.defwidth;
  if(ccol < rightcol) {
    s.width = (rightcol * this.dimManager.defwidth) + "px";
  }
};

LiveSheet.mainsheet.prototype.onmousewheel = function(ev) {
  var delta = 0;
  // normalize the mouse delta.
  if(ev.wheelDelta) {
    delta = ev.wheelDelta/120;
  }
  else if(ev.detail) {
    delta = -ev.detail/3;
  }
  log('onmousewheel: delta is ' + delta)
  if(delta) {
    var row = this.focusCell.row;
    var rowrange = null;
    if(delta > 0 && this.viewrect.t > 1) {
      rowrange = {'start':this.viewrect.t -1 ,'end':this.viewrect.b-1};
    }
    else if(delta < 0) {
      rowrange = {'start':this.viewrect.t + 1,'end':this.viewrect.b+1};
    }
    if(rowrange) {
      var rng = this.dimManager.rowdims(rowrange.start);
      this.generatedYscroll = true;
      this.generatedYRange = rowrange;
      this.movescrollY(rowrange.end);
      setScrollHeight(this.rs,(rowrange.start-1) * this.dimManager.defheight);
    }
  }
};

LiveSheet.mainsheet.prototype.createsheet = function() {

  var _this = this;

  var obj = this.parentdiv;

  dojo.event.connect(document,'onmousedown',this,'docmousedown');
  dojo.event.connect(document,'onmouseup',this,'docmouseup');
  dojo.event.connect(document,'onmousemove',this,'docmousemove');
  dojo.event.connect(obj,'onmousedown',this,'onmousedown');
  dojo.event.connect(obj,'onmousemove',this,'onmousemove');
  dojo.event.connect(obj,'onmouseup',this,'onmouseup');
  dojo.event.connect(obj,'oncontextmenu',this,'oncontextmenu');
  // onmousehwell for IE/Opera, DOMMouseScroll for Mozilla/firefox
  if(obj.addEventListener) {
    obj.addEventListener('DOMMouseScroll',bind(this.onmousewheel,this),false);
  }
  else {
    dojo.event.connect(document,'onmousewheel',this,'onmousewheel');
  }
  dojo.event.browser.addListener(window,'resize',bind(this.onresize,this),false);

  this.inputcell = INPUT({'class':'cellinput'});
  //this.inputcell = TEXTAREA({'class':'celltextarea'});

  //this.parentdiv.appendChild(this.inputcell);
  //this.sc.appendChild(this.inputcell);
  dojo.event.browser.addListener(this.inputcell,'keypress',bind(this.onkeypress,this),false);
  dojo.event.browser.addListener(this.inputcell,'keydown',bind(this.onkeydown,this),false);
  dojo.event.browser.addListener(this.inputcell,'click',bind(this.inputcellclick,this),false);
  dojo.event.browser.addListener(this.inputcell,'contextmenu',bind(this.oncontextmenu,this),false);
  dojo.event.browser.addListener(getElement('rightscroller'),'scroll',bind(this.doscrollY,this),false);
  dojo.event.browser.addListener(getElement('bottomscroller'),'scroll',bind(this.doscrollX,this),false);

  dojo.event.connect(this.inputcell,'onselect',bind(partial(this.doSelectInternal,
                                                            this.inputcell,'inputselect'),this));
  dojo.event.connect(this.formulainput,'onselect',bind(partial(this.doSelectInternal,
                                                               this.formulainput,'fxselect'),this));

  this.generatesheet();

  this.clickercb(this.getCellElement(1,1));
  this.formulainput.focus();
};

LiveSheet.mainsheet.prototype.onExtentChange = function(cell) {
  //this.maxDataRow = Math.max(this.maxDataRow,cell.row);
  //this.maxDataCol = Math.max(this.maxDataCol,cell.col);

};

LiveSheet.mainsheet.prototype.doscrollY = function(ev) {
  var t = ev.currentTarget;
  var viewY = typeof(t.scrollTop) != 'undefined' ? t.scrollTop : 
  (typeof(t.scrollY) != 'undefined' ? t.scrollY : 0);
  //log('doscrollY',viewY);
  if(this.lastYscroll) {
    this.lastYscroll = null;
    return;
  }

  var targetrow = parseInt(viewY / this.dimManager.defheight) + 1;

  if(this.generatedYscroll) {
    var rowrange = this.generatedYRange;
    this.generatedYscroll = false;this.generatedYrange = null;
    this.doscrollYinternal(rowrange);
  }
  else {
    var rowrange = this.dimManager.findEndRow(targetrow,this.sc.clientHeight);

    // what is the *current* scroll state - is this because someone
    // is waggling aroudn the scrollbar?
    var inprog = this.scrollYinprog;
    this.scrollYinprog = {'lastY':viewY,'rrange':rowrange};
    log('asking for scroll to',rowrange);
    currentsheet.doscrollYinternal(rowrange,inprog);
  }
};

LiveSheet.mainsheet.prototype.doscrollYinternal = function(rowrange,inprog) {

  // search from the current 
  var oldend = this.viewrect.b;
  this.viewArea.toprow = rowrange.start;
  this.viewrect.t = rowrange.start; this.viewrect.b = rowrange.end;
  this.viewArea.toppos = this.dimManager.rowdims(rowrange.start).startval;
  var oldscrollY = this.viewArea.scrollY;
  this.viewArea.scrollY = this.viewArea.toppos;

  // scrolldirY is used to indicate the scroll direction.  if inprog is set this means
  // that scrolling is still in progress so don't make any assumptions about the user.
  // if inprog is false the scroll event could have come from click or arrow key.

  var scrolldirY = !inprog ? ((oldscrollY < this.viewArea.scrollY) ? 'down' : 'up') : null;

  log('doscrollYinternal',this.cCache.maxRow,oldend,this.viewArea.scrollY,oldscrollY);
  if(this.viewArea.scrollY < oldscrollY && this.cCache.maxRow < oldend) {
    // adjust the possible size of the scroll bar
    this.adjustRowScroll(this.viewrect.b);
  }

  this.maybeCreateCells(this.visiblecols,rowrange,scrolldirY);
  setScrollHeight(getElement('scrollcontainer'),this.viewArea.toppos);
  setScrollHeight(getElement('rowcontainer'),this.viewArea.toppos);
};

LiveSheet.mainsheet.prototype.doscrollX = function(ev) {

  var t = ev.currentTarget;
  var viewX = typeof(t.scrollLeft) != 'undefined' ? t.scrollLeft : 
  (typeof(t.scrollX) != 'undefined' ? t.scrollX : 0);
  //log('doscrollX: scroll value is now',viewX);

  // flag to avoid entering - used when we want to avoid continous scroll events
  // or if a scroll is already in progress.
  if(this.lastXscroll) {
    this.lastXscroll = null;
    return;
  };

  var targetcol = parseInt(viewX / this.dimManager.defwidth) + 1;
  

  var colrange = this.dimManager.findColRange(viewX,
                                              this.viewArea.scrollX,
                                              this.viewArea.leftcol,
                                              viewX + this.sc.clientWidth);

  if(this.generatedXscroll) {
    this.doscrollXinternal(this.generatedXRange);
    this.generatedXscroll = false;this.generatedXRange = null;

  }
  else {
    var colrange = this.dimManager.findEndCol(targetcol,this.sc.clientWidth);

    // inprogress is used if the scroll is still happening
    var inprog = this.scrollXinprog;
    this.scrollXinprog = {'lastX':viewX,'crange':colrange};
    this.doscrollXinternal(colrange);
  }
};

LiveSheet.mainsheet.prototype.doscrollXinternal = function(colrange,inprog) {

  var oldright = this.viewrect.r;
  this.viewArea.leftcol = colrange.start;
  this.viewArea.leftpos = this.dimManager.coldims(colrange.start).startval;
  var oldscrollX = this.viewArea.scrollX;
  this.viewArea.scrollX = this.viewArea.leftpos;
  this.viewrect.l = colrange.start;this.viewrect.r = colrange.end;

  var scrolldirX = !inprog ? ((oldscrollX < this.viewArea.scrollX) ? 'right' : 'left') : null;

  if(this.viewArea.scrollX < oldscrollX && this.cCache.maxCol < oldright) {
    this.adjustColScroll(this.viewrect.r);
  }

  log('setting the scrollbar to ',this.viewArea.leftpos);
  this.maybeCreateCells(colrange,this.visiblerows,null,scrolldirX);
  setScrollWidth(getElement('scrollcontainer'),this.viewArea.leftpos);
  setScrollWidth(getElement('colcontainer'),this.viewArea.leftpos);

};

LiveSheet.mainsheet.prototype.maybeScroll = function(cell) {
  // used when the user wants to focus a new cell and we might need to bring it into view.
  var col = cell.col,row = cell.row;
  var v = this.viewrect;
  var range;
  if(col < v.l) {
    // scroll left
    // +1 to avoid boundary issues and be inside the next cell
    range = this.dimManager.findEndCol(col,this.sc.clientWidth);
    this.doscrollXinternal(range);
    setScrollWidth(this.bs,(col-1) * this.dimManager.defwidth);
    this.lastXscroll = true;
  }
  else if(col >= v.r) {
    // scroll right
    var right = this.dimManager.coldims(col).end();
    var left = right - this.sc.clientWidth;
    range = this.dimManager.findColRange(left,this.viewArea.scrollX,this.viewArea.leftcol,
                                         right,true);
    this.movescrollX(range.end);
    this.doscrollXinternal(range);
    setScrollWidth(this.bs,(range.start-1) * this.dimManager.defwidth);
    this.lastXscroll = true;
  }
  
  if(row < v.t) {
    // scroll up
    range = this.dimManager.findEndRow(row,this.sc.clientHeight)
    this.doscrollYinternal(range);
    setScrollHeight(this.rs,(row-1) * this.dimManager.defheight);
    this.lastYscroll = true;
  }
  else if(row >= v.b) {
    // scroll down
    var bottom = this.dimManager.rowdims(row).end();
    var top = bottom - this.sc.clientHeight;
    range = this.dimManager.findRowRange(top,this.viewArea.scrollY,this.viewArea.toprow,
                                         bottom,true);
    this.movescrollY(range.end);
    this.doscrollYinternal(range);
    setScrollHeight(this.rs,(range.start-1) * this.dimManager.defheight);
    this.lastYscroll = true;
  }
};

LiveSheet.mainsheet.prototype.maybeCreateCells = function(colrange,rowrange,scrolldirY,scrolldirX) {
  // maybeCreateCells is called from a scroll event.  It is responsible for checking 
  // whether a paint event is required.

  var c = this.cArea;
  if(colrange.start >= c.startcol && colrange.end <= c.endcol && 
     rowrange.start >= c.startrow && rowrange.end <= c.endrow) {
    return; // nothing to do
  }
  else {
    var fcol = this.focusCell.col;
    var frow = this.focusCell.row;
    if(fcol < colrange.start || fcol > colrange.end) {
      fcol = colrange.start;
    }
    if(frow < rowrange.start || frow > rowrange.end) {
      frow = rowrange.start;
    }

    if(colrange != this.visiblecols) {
      this.visiblecols = this.addPaddingCols(colrange,scrolldirX);
    }
    if(rowrange != this.visiblerows) {
      this.visiblerows = this.addPaddingRows(rowrange,scrolldirY);
    }
    currentsheet.createViewArea();
    this.focusCell = this.cellfrom(frow,fcol);
    this.clickercb();
    this.formulainput.focus();
  }
};

LiveSheet.mainsheet.prototype.oncolumnclick = function(el) {
  var c= parseInt(el.attributes.columnid.value);
  LiveSheet.Sheetbar.updateState(this.sCache.getcolstyle(c));
  this.mousetrack.selectColumn(c);
};

LiveSheet.mainsheet.prototype.oncolumncontext = function(ev,el) {
  this.oncolumnclick(el);
  this.mousetrack.floater.oncontextmenu(ev);
};

LiveSheet.mainsheet.prototype.onrowclick = function(el) {
  var r = parseInt(el.attributes.rowid.value);
  LiveSheet.Sheetbar.updateState(this.sCache.getrowstyle(r));
  this.mousetrack.selectRow(r);
};

LiveSheet.mainsheet.prototype.onrowcontext = function(ev,el) {
  this.onrowclick(el);
  // pass the context event directly down to the floater.
  this.mousetrack.floater.oncontextmenu(ev);
};

LiveSheet.mainsheet.prototype.toggleContainer = function() {
  this.containerenabled = !this.containerenabled;
  this.onresize();
};

LiveSheet.mainsheet.prototype.containerWidth = function() {
  return getElement('spacercontainer').clientWidth;
};


LiveSheet.mainsheet.prototype.generatesheet = function() {
  // kick off the first drawing event.
  log('generating sheet...');

  undoManager = new LiveSheet.undoManager(); // global
  LiveSheet.Sheetbar.wireHandlers(this,undoManager);
  undoManager.adjusttoolbar();

  var colrange = this.dimManager.findColRange(0,0,0,this.sc.clientWidth);
  var rowrange = this.dimManager.findRowRange(0,0,0,this.sc.clientHeight);
  this.viewrect.l = colrange.start; this.viewrect.r = colrange.end;
  this.viewrect.t = rowrange.start; this.viewrect.b = rowrange.end;
  this.visiblerows=this.addPaddingRows(rowrange);
  this.visiblecols=this.addPaddingCols(colrange);
        
  if(dojo.render.html.ie) {
    getElement('spacer').style.marginRight = "-3px";
  }

  currentsheet.createViewArea();
};

LiveSheet.mainsheet.prototype.createViewArea = function() {

  var vr = this.visiblerows;vc =this.visiblecols;
  var startcol=vc.start,startrow=vr.start,endcol=vc.end,endrow=vr.end;
        
  log('CreateViewArea called: ',startcol,startrow,endcol,endrow);

  // clear out the overflow dictionaries
  LiveSheet.clearOverflow();

  var c = this.cArea;
  c.startcol=startcol;c.startrow=startrow;c.endcol=endcol;c.endrow=endrow;
  this.drawrect = new DocUtils.geometry.rect(startcol,startrow,endcol,endrow);

  mark = new DocUtils.benchmark();
  mark.mark();

  try {
    // before we blow away the contents deal with our last cell in focus
    if(this.oldfocus) {
      this.oldfocus.setNormal(this.inputcell);
      this.oldfocus = null;
    }
        
    // clear out spacers
    this.spacertop=null;this.spacerbottom=null;this.spacerleft=null;this.spcaerright=null;
        
    var count = 0;
    var p = this.parentdiv;
        
    // create the cells
    var content = []
      var rowcontent = [];
    var colcontent = [];
        
    var count = 0;
    var colDimArray = [];
    for(var i=startcol;i<=endcol;i++) {
      var dim = currentsheet.dimManager.coldims(i);
      LiveSheet.createColHeader(i,colcontent,dim);
      colDimArray[i] = dim;
    }
        
    for(var j=startrow;j<=endrow;j++) {
      var rowdim = currentsheet.dimManager.rowdims(j);
      LiveSheet.createRowHeader(j,rowcontent,rowdim);
      var nextNormalCol = startcol;
      for(var i=startcol;i<=endcol;i++) {
        var key = LiveSheet.cellkey(i,j);
        nextNormalCol = LiveSheet.createCell(i,j,content,key,this.cCache.getCell(key),rowdim,
                                             colDimArray,nextNormalCol);
        count++;
      }
    }
    var parentdiv = this.parentdiv;
    //log('createViewArea: created ' + count + ' cells');
        
    parentdiv.innerHTML = content.join('');
    getElement('rowinsert').innerHTML = rowcontent.join('');
    getElement('colinsert').innerHTML = colcontent.join('');
        
    // redraw any locks that should be visible.
    this.lockmanager.redrawlocks();
    // reappend the inputcell
    this.parentdiv.appendChild(this.inputcell);
  }
  // not really doing anything with this right now - this is 
  // here so that we always reset the cursor style.
  catch(e) {} 
  mark.mark();
  mark.report('createviewarea');
};

LiveSheet.mainsheet.prototype.setUpdating = function() {
  if(this.updatetimer) {
    this.remoteupdate = true;
  }
  else {
    // let it run for three cycles
    getElement('updatingbutton').style.display = "";
    this.updatetimer = setTimeout(bind(this.onUpdateCycle,this),1.8*3000);
  }
};

// toolbar handlers
LiveSheet.mainsheet.prototype.onBold = function(selected,value) {
  this.applyStyle(['font-weight','bold'],!selected);
};

LiveSheet.mainsheet.prototype.onItalic = function(selected,value) {
  this.applyStyle(['font-style','italic'],!selected);
};

LiveSheet.mainsheet.prototype.onUnderline = function(selected,value) {
  this.applyStyle(['text-decoration','underline'],!selected);
};

LiveSheet.mainsheet.prototype.onJustify = function(widgets,selected) {
  var justify;
  var remove=false;
  switch(selected) {
  case 'justifycenter': justify='center';break;
  case 'justifyright': justify='right';break;
  case 'justifyfull': justify='justify';break;
  case 'justifyleft':
  default:
    // left justify is the default - don't keep it around.
    // NOTE: we don't remove the style anymore because it screws up
    // if someone wants to override the default right align on a
    // an interpreted literal.
    //remove = true;
    justify = 'left';
  };
  this.applyStyle(['text-align',justify],remove);
};

LiveSheet.mainsheet.prototype.onBgColor = function(widget,value) {
  // value is a color
  log('onBgColor:',value);
  if(value == '#ffffff') { //white 
    log('reseting background color');
    this.applyStyle(['background-color',value],true); // ,'border',value],true);
  }
  else {
    this.applyStyle(['background-color',value]); // 'border','1px solid ' + value]);
  }
};

LiveSheet.mainsheet.prototype.onFontColor = function(widget,value) {
  this.applyStyle(['color',value]);
};

LiveSheet.mainsheet.prototype.onCurrencyStyle = function(currencyType,value) {
  this.setCurrencyStyle(currencyType);
};

LiveSheet.mainsheet.prototype.setCurrencyStyle = function(currencyType) {
  var floater = this.mousetrack.floater;
  var undo = null;
  if(floater && floater.visible) {
    if(this.mousetrack.rowselected) {
      undo = new LiveSheet.ColRowCurrencyUndo('r',floater.startcell.row,currencyType);
    }
    else if(this.mousetrack.colselected) {
      undo = new LiveSheet.ColRowCurrencyUndo('c',floater.startcell.col,currencyType);
    }
    else {
      var normal = this.normalizeCells(floater.startcell,floater.endcell);
      undo = new LiveSheet.CurrencyUndo(normal.start,normal.end,currencyType);
    }
  }
  else if(this.focusCell) {
    undo = new LiveSheet.CurrencyUndo(this.focusCell,this.focusCell,currencyType);
  }
  if(undo) {
    undo.doAction();
  }
};

LiveSheet.mainsheet.prototype.doSort = function(sortType) {
  
  var floater = this.mousetrack.floater;
  var undo = null;
  if(floater && floater.visible) {
    if(this.mousetrack.colselected) {
      undo = new LiveSheet.ColSortUndo(floater.startcell.col,sortType);
    }
    else if(this.mousetrack.rowselected) {
      // row sorting not supported
    }
    else {
      undo = new LiveSheet.SortUndo(floater.startcell,floater.endcell,sortType);
    }
  }
  undo.doAction();

};

LiveSheet.mainsheet.prototype.applyStyle = function(proplist,remove) {
  var rl = []; // remove list
  if(remove) {
    for(var i=0;i<proplist.length;i+=2) { rl.push(proplist[i]); }
  }

  // couple of cases: 1) selected column, selected row, selected region, or selected single cell
  var floater = this.mousetrack.floater;
  if(floater && floater.visible) {
    if(this.mousetrack.colselected) {
      var undo = new LiveSheet.ColStyleUndo(floater.startcell.col,proplist,remove);
      undo.doAction();
    }
    else if(this.mousetrack.rowselected) {
      var undo = new LiveSheet.RowStyleUndo(floater.startcell.row,proplist,remove);
      undo.doAction();
    }
    else {
      var r = new DocUtils.geometry.rect(floater.startcell.col,
                                         floater.startcell.row,
                                         floater.endcell.col,
                                         floater.endcell.row);
      var undo = new LiveSheet.StyleRangeUndo(r,proplist,this.cCache,remove);
      undo.doAction();
    }
  }
  else if(this.focusCell) {
    var cell = this.focusCell;
    var r = new DocUtils.geometry.rect(cell.col,cell.row,cell.col,cell.row);
    var undo = new LiveSheet.StyleRangeUndo(r,proplist,this.cCache,remove);
    undo.doAction();
  }
};

// remote style handlers

LiveSheet.mainsheet.prototype.onUpdateStyleClass = function(key,jsonstyle,props) {
  this.setUpdating();
  var cache = jsonstyle.cache;
  log('onUpdateStyleClass:',key);
  var ret = this.getUpdateStyleList(key);
  ret.style.cache = cache;
  ret.style.save();
  
  var func;
  var _this = this;
  if(props && props[0] == 'background-color') {
    func = function(x) {  _this.cellFromEl(x).setInheritedBackground(props[1]); }
  }
  else {
    func = function(x) { addElementClass(x,ret.style.className); };
  }
  forEach(ret.updatelist,func);
};
LiveSheet.mainsheet.prototype.onRemoveStyleClass = function(key,props) {
  this.setUpdating();
  var ret = this.getUpdateStyleList(key);
  
  var func;
  var _this = this;
  if(props[0] == 'background-color') {
    func = bind(this.removeInheritedbgColor,this);
  }
  else {
    func = function(x) { removeElementClass(x,ret.style.className); };
  }
  forEach(ret.updatelist,func);
  ret.style.removeRule();
  // remove from the style cache
  ret.remove();
};

LiveSheet.mainsheet.prototype.removeInheritedbgColor = function(cellkey) {
  var cell = this.cellFromEl(cellkey);
  // remove any inherited style
  cell.removeBackground(true);
  if(cell.customStyle  && cell.customStyle.get('background-color')) {
    cell.setBackground(cell.customStyle.get('background-color'));
  }
};

LiveSheet.mainsheet.prototype.getUpdateStyleList = function(key) {
  var updatelist;
  var style;
  var remove = null;

  if(key.charAt(0) == 'r') { // row
    var row = parseInt(key.slice(1));
    style = this.sCache.getrowstyle(row);
    remove = function() { currentsheet.sCache.removeRowStyle(row); }
    if(row >= this.drawrect.t && row <= this.drawrect.b) {
      updatelist = map (function(x) { return LiveSheet.cellkey(x,row); },
                        range(this.cArea.startcol,this.cArea.endcol+1));
    }
    else {
      updatelist = [];
    }
  }
  else { // column
    var col = parseInt(key.slice(1));
    style = this.sCache.getcolstyle(col);
    remove = function() { currentsheet.sCache.removeColStyle(col); }
    if(col >= this.drawrect.l && col <= this.drawrect.r) {
      updatelist = map(function(x) { return LiveSheet.cellkey(col,x); },
                       range(this.cArea.startrow,this.cArea.endrow+1));
    }
    else {
      updatelist = [];
    }
  }
  return {'updatelist':updatelist,'style':style,'remove':remove};
};


LiveSheet.mainsheet.prototype.processRemoteStyleReq = function(rect,cb) {
  this.setUpdating();
  for(var i=rect.l;i<=rect.r;i++) {
    for(var j=rect.t;j<=rect.b;j++) {
      if(i == this.focusCell.col && j == this.focusCell.row) {
        LiveSheet.Sheetbar.updateState(this.focusCell.customStyle);
      }
      cb.apply(this,[i,j]);
    }
  }
};

LiveSheet.mainsheet.prototype.onUpdateStyleRegion = function(rect,props) {
  this.processRemoteStyleReq(rect,function(i,j) {
                               var cell = this.cCache.createOnWrite(i,j);
                               cell.setCustomStyleList(props,true);
                             });
};

LiveSheet.mainsheet.prototype.onRemoveStyleRegion = function(rect,props) {
  this.processRemoteStyleReq(rect,function(i,j) {
                               var cell = this.cCache.getCellByAttr(i,j);
                               if(cell) {
                                 cell.removeCustomStyleList(props,true);
                               }
                             });
};

LiveSheet.mainsheet.prototype.onUpdateStyleCells = function(cells) {
  this.setUpdating();
  for(var i=0;i<cells.length;i++) {
    var cell = this.cCache.createOnWrite(cells[i].col,cells[i].row);
    // ugh. this is messy - is there a better way?
    var sb = new LiveSheet.styleBuilder('.cell',cells[i].customStyle.cache);
    cell.clearAndApplyStyles(sb.proplist(),true);
  }
};

LiveSheet.mainsheet.prototype.deleteStyleOnUpdate = function(removeobj) {
  var styleinfo = this.getUpdateStyleList(removeobj.key);
  if(!styleinfo.style) { return; }
  // if a background color exists clear it.
  if(styleinfo.style.exists('background-color')) {
    forEach(styleinfo.updatelist,bind(this.removeInheritedbgColor,this));
  }
  // remove the style from all cells in view.
  forEach(styleinfo.updatelist,function(x) { removeElementClass(x,styleinfo.style.className); });
  // remove the rule completely.
  styleinfo.style.removeRule();
  // remove from the cache
  styleinfo.remove();
};


LiveSheet.mainsheet.prototype.updateMultipleStyleClasses = function(updates,removals,
                                                                    colVal,colDelta,rowVal,rowDelta) {
  // currently called when we have a list of column or row styles to change
  // as result of a column or row insert / delete operation.
  //
  // Note: this also supports row heights and column widths in order to avoid the overhead
  // of another RPC
  var repaint = false;
  var coldims = [];
  var rowdims = [];
  mincol = null;
  minrow = null;
  
  // go through the removal list and remove the existing style.
  for(var i=0;i<removals.length;i++) {
    this.deleteStyleOnUpdate(removals[i]);
  }
  // go through the update list and apply all the styles.
  for(var i=0;i<updates.length;i++) {
    var updateobj = updates[i];
    if(keys(updateobj.format).length) {

      var styleinfo = this.getUpdateStyleList(updateobj.key);
      // set the new style info.
      styleinfo.style.cache = updateobj.format.cache;
      styleinfo.style.save();
    
      // if a background color exists apply to all existing cells.
      var bg = styleinfo.style.get('background-color');
      if(bg) {
        var _this = this;
        forEach(styleinfo.updatelist,function(x) { _this.cellFromEl(x).setInheritedBackground(bg); });
      }
      // apply the rest of the style.
      forEach(styleinfo.updatelist,function(x) { addElementClass(x,styleinfo.style.className); });
    }
    else {
      // treat the case of having style info but no formatting as a delete.
      this.deleteStyleOnUpdate(updateobj);
    }
    if(updateobj.val > 0) {
      if(updateobj.key.slice(0,1) == 'c') {
        mincol = mincol == null ? updateobj.id : Math.min(updateobj.id,mincol);
        coldims.push(updateobj);
        //this.dimManager.addColumnWidth(updateobj.id,updateobj.val);
      }
      if(updateobj.key.slice(0,1) == 'r') {
        minrow = (minrow == null) ? updateobj.id : Math.min(updateobj.id,minrow);
        rowdims.push(updateobj);
        //this.dimManager.addRowHeight(updateobj.id,updateobj.val);
      }
      repaint = true;
    }
  }

  var self = this;
  // adjust above max(val+delta,val) or adjust rows above max(val+delta,val)
  if(colVal != 0 && colDelta != 0) {
    currentsheet.dimManager.moveCols(colVal,colDelta);
    forEach(coldims,function(updateobj) { self.dimManager.addColumnWidth(updateobj.id,updateobj.val); });
    this.repaint();
  }
  else if(rowVal != 0 && rowDelta != 0) {
    currentsheet.dimManager.moveRows(rowVal,rowDelta);
    forEach(rowdims,function(updateobj) { self.dimManager.addRowHeight(updateobj.id,updateobj.val); });
    this.repaint();
  }
};

LiveSheet.mainsheet.prototype.onUpdateCycle = function() {
  if(this.remoteupdate) {
    this.remoteupdate = false;
    this.updatetimer = setTimeout(bind(this.onUpdateCycle,this),1.8*3000);
  }
  else {
    hideElement(getElement('updatingbutton'));
    this.updatetimer = null;
  }
};


// remote handlers
LiveSheet.mainsheet.prototype.onColumnWidthChange = function(columnID,newwidth) {
  this.setUpdating();
  this.AdjustColumnWidth(columnID,newwidth);
        
};

LiveSheet.mainsheet.prototype.onRowHeightChange = function(rowID,newheight) {
  this.setUpdating();
  this.AdjustRowHeight(rowID,newheight);
};

LiveSheet.mainsheet.prototype.onCellUpdate = function(cells,fromSelf) {
  //this.setUpdating();
  this.onCellCalc(cells,fromSelf);
};

LiveSheet.mainsheet.prototype.onCellCalc = function(cells,fromSelf) {
  // the main entry point for cell updates from the server

  log('*** onCellcalc called from server *** ')
  this.setUpdating();
  var updatelist = cells;
  var changelist = new Array();
  if(!updatelist) { return; }

  for(var i=updatelist.length-1;i>=0;i--) {
    var remotecell = updatelist[i];
    var cell = this.cCache.createOnWrite(remotecell.col,remotecell.row,remotecell);
    try { // if the cell is not visible then we will get an exception trying to change it
      cell.onCalc();
      changelist.push(cell);
      if(cell.key == this.focusCell.key && this.focusCell.focusedState() && !fromSelf) {
        cell.handleCollision(this);
      }
    }
    catch(e) {
      if(!(e instanceof LiveSheet.CellException)) {
        throw e;
      }
    }
  }
  setTimeout(function() {
               forEach(changelist,function(arg) {arg.afterCalc(); });
             },500);

  if(this.cCache.maxRow > this.maxDataRow) {
    this.setMinimumRowScroll(this.cCache.maxRow,fromSelf,10* this.dimManager.defheight);
  }
  if(this.cCache.maxCol > this.maxDataCol) {
    this.setMinimumColScroll(this.cCache.maxCol,fromSelf,4* this.dimManager.defwidth);
  }
};

LiveSheet.mainsheet.prototype.setMinimumRowScroll = function(row,fromSelf,padding) {
  //set the minimum acceptable scroll height
  if(row == this.maxDataRow) { return; }
  this.maxDataRow = row;
  //this.minscrollheight = this.dimManager.rowdims(this.maxDataRow).end() + (padding||0);
  this.minscrollheight = (this.maxDataRow * this.dimManager.defheight) + (padding||0);
  
  if(!fromSelf) {
    var cheight = parseInt(this.rsinsert.style.height.slice(0,-2));
    if(isNaN(cheight)) { cheight= 0; }
    if(this.minscrollheight > cheight) {
      // only adjust the height if the current height is less than the minimum
      this.rsinsert.style.height = (this.minscrollheight) + "px";
    }
  }
};

LiveSheet.mainsheet.prototype.adjustRowScroll = function(bottomrow) {
  // adjust the amount of scroll available for the height of the sheet
  var bot = bottomrow * this.dimManager.defheight;

  if(bot > this.minscrollheight) {
    this.rsinsert.style.height = (bot + "px");
  }
  else {
    //var rheight = parseInt(this.rsinsert.style.height.slice(0,-2));
    if(bot < this.minscrollheight) {
      this.rsinsert.style.height = (this.minscrollheight + "px");
    }
  }
};

LiveSheet.mainsheet.prototype.setMinimumColScroll = function(col,fromSelf,padding) {
  if(col == this.maxDataCol) { return; } // short circuit
  this.maxDataCol = col;

  this.minscrollwidth = (this.maxDataCol * this.dimManager.defwidth) + (padding||0);
  if(!fromSelf) {
    var cwidth = parseInt(this.bsinsert.style.width.slice(0,-2));
    if(isNaN(cwidth)) { cwidth = 0; }
    if(this.minscrollwidth > cwidth) {
      this.bsinsert.style.width = (this.minscrollwidth + "px");
    }
  }
};
  
LiveSheet.mainsheet.prototype.adjustColScroll = function(rightcol) {

  var right = rightcol * this.dimManager.defwidth;

  if(right > this.minscrollwidth) {
    this.bsinsert.style.width = (right + "px");
  }
  else {
    //var cwidth = parseInt(this.bsinsert.style.width.slice(0,-2));
    if(right < this.minscrollwidth) {
      this.bsinsert.style.width = (this.minscrollwidth + "px");
    }
  }
};
  
LiveSheet.mainsheet.prototype.onEditingCell = function(jSONcell) {
  // var jsoncell = fromJSON(jSONcell);
  //    var el = getElement(LiveSheet.cellkey(jsoncell.col,jsoncell.row));
  //    if(el) {
  //            // TODO: fix this, to messy and dangerous
  //            el.style.backgroundColor = 'silver';
  //    }
};

LiveSheet.mainsheet.prototype.onCellLeave = function(jSONcell) {
  //    var jsoncell = fromJSON(jSONcell);
  //    var key = LiveSheet.cellkey(jsoncell.col,jsoncell.row);
  //    var el = getElement(LiveSheet.cellkey(jsoncell.col,jsoncell.row));
  //    if(el) {
  //            var cell = this.cCache.getCell(key);
  //            if(cell) {
  //                    cell.reApplyCustomStyle('background-color');
  //            }
  //            else {
  //                    el.style.backgroundColor = '';
  //            }
  //    }
};

LiveSheet.mainsheet.prototype.onPasteCells = function(clipitem,targetCell) {
  this.setUpdating();
  this.applyPaste(targetCell,clipitem);
};

LiveSheet.mainsheet.prototype.onClearCells = function(startcell,endcell) {
  this.setUpdating();
  this.clearCells(startcell,endcell)
};

LiveSheet.mainsheet.prototype.onCutCells = function(clipItem) {
  this.clearCells(clipItem.startcell,clipItem.endcell);
  this._addclip(clipItem);
};

LiveSheet.mainsheet.prototype.onCopyCells = function(clipboard) {
  this._addclip(clipboard);
};

LiveSheet.mainsheet.prototype._addclip = function(clipItem) {
  var newitem = new LiveSheet.clipboardItem();
  newitem.copyConstruct(clipItem);
  this.clipboard.push(newitem);
};

LiveSheet.mainsheet.prototype.onEditingDone = function(jSONcell) {

};

LiveSheet.mainsheet.prototype.onSheetConstruct = function(jsonData) {
  log('onSheetConstruct');
  this.construct(jsonData[0]);
  this.onsheetload(jsonData[1]);

  // construct the visible display elements of the sheet
  this.createsheet();
  // seed initial maximums
  this.maxDataRow = 0; this.maxDataCol = 0;
  // adjust the scrollbars
  this.setMinimumRowScroll(Math.max(this.visiblerows.end,this.cCache.maxRow),
                           false, // force scroll bar adjustment
                           this.dimManager.defheight * 10);

  this.setMinimumColScroll(Math.max(this.visiblecols.end,this.cCache.maxCol),
                           false,
                           this.dimManager.defwidth * 4);

  this.onresize(null);

  // register a global disconnect notification
  Nevow.Athena.notifyOnDisconnect(function() { currentsheet.conLostDlg.show(); });

  sheetServer.setGlobalErrback(function(result) {
                                 //if(result instanceof Divmod.connectionError) {
                                 //  currentsheet.conLostDlg.show();
                                 //}
                                 // ensure that errbacks keep firing!  very important.
                                 return result;
                               });

  // make stuff visible.
  dojo.fx.html.fadeOut(getElement('loadingsheet'),250,function() {
                         hideElement('loadingsheet');
                       });

  var d = sheetServer.callRemote('getChatHistory')
  d.addCallback(bind(chatwindow.loadOld,chatwindow))

};

//LiveSheet.mainsheet.prototype.enablechat = function() {
//  showElement('chatcontainer');
// this.toggleContainer();
//};

// this is also used to page in cells
LiveSheet.mainsheet.prototype.onsheetload = function(cells) {
  log('loading sheet data....');
  this.setUpdating();
  for(var i=0;i<cells.length;i++) {
    cellitem = cells[i];
    if(cellitem.row >= 1 && cellitem.col >= 1) {
      var cell =new LiveSheet.Cell(cellitem.col,cellitem.row);
      cell.copyConstruct(cellitem);                     
      this.cCache.putCell(cell);
    }
  }
  //log(repr(this.cCache));
};


// globals


var currentsheet = null;
var undoManager = null; 

function doload() {
  LiveSheet.typeTracker = new LiveSheet._typeTracker();
  
  if(!currentsheet) {
    currentsheet = new LiveSheet.mainsheet();
    // create the sheet bar
    LiveSheet.Sheetbar.create(getElement('toolbar'));

     Nevow.Athena.notifyOnConnect().
       addCallback(function() {
                    var d = sheetServer.callRemote('onSheetLoad');
                    d.addCallback(bind(currentsheet.onSheetConstruct,currentsheet));
                    // todo: is this right?
                    d.addErrback(function(res) {
                                   var loading = $('loadingsheet');
                                   loading.childNodes[0].innerHTML = '';
                                   var failed = $('failedcon');
                                   showElement(failed);
                                   roundElement(failed);
                                   if(res instanceof Error) {
                                     server.callRemote('logClientError',res.message);
                                   }
                                   else {
                                     server.callRemote('logClientError',res);
                                   }
                                 });
                   });
  }
}


function getsheet() {
  return currentsheet;
}


MochiKit.DOM.addLoadEvent(function() {
                            var agt=navigator.userAgent.toLowerCase();
                            var el;
                            if(agt.indexOf('safari') != -1) {
                              el = 'safari';
                            }
                            else if(agt.indexOf('opera') != -1) {
                              el = 'opera';
                            }
                            else {
                              return true;
                            }
                            $('loadingsheet').childNodes[0].innerHTML = '';
                            showElement(el);
                            roundElement(el);
                            return false;
                          });
MochiKit.DOM.addLoadEvent(doload);

var chatwindow = null;
MochiKit.DOM.addLoadEvent(function() {
                            chatwindow = new LiveSheet.chat(); 
                          });
