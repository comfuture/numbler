/* Copyright (C) 2006 Numbler LLC */
/* See LICENSE for details. */

if(typeof(LiveSheet) == 'undefined') {
  LiveSheet = {};
 };

LiveSheet.dragBase = function() {
  //public properties
  inprogress = false;
};

LiveSheet.dragBase.prototype = {
  // base methods
  construct:function() {
    this.sheet = arguments[0];
    for(var i=1;i<arguments.length;i++) {
      dojo.event.connect(arguments[i],'onmousedown',this,'onmousedown');
    }
    
    this.dragtop = DIV({'class':'hdrag'},null);
    this.sheet.parentdiv.appendChild(this.dragtop);
    this.dragbot = DIV({'class':'hdrag'},null);
    this.sheet.parentdiv.appendChild(this.dragbot);
    this.dragleft = DIV({'class':'vdrag'},null);
    this.sheet.parentdiv.appendChild(this.dragleft);
    this.dragright = DIV({'class':'vdrag'},null);
    this.sheet.parentdiv.appendChild(this.dragright);
  },
  onmousedown:function(ev) {
    // hook into the mouseevents before the sheet handlers
    dojo.event.connect("before",this.sheet,'onmousemove',this,'onmousemove');
    dojo.event.connect("before",this.sheet,'onmouseup',this,'onmouseup');
    this.setcontrolcell(ev);
    this.hidden = true;
  },
  onmousemove:function(ev) {
    var curEvent = this.sheet.normalize(ev);
    var target = this.sheet.cellfrompos(curEvent.x,curEvent.y,true);
    this.domousemove(target);
    dojo.event.browser.stopEvent(ev);
  },
  onmouseup:function(ev) {
    dojo.event.browser.stopEvent(ev);
    dojo.event.disconnect("before",this.sheet,'onmousemove',this,'onmousemove');
    dojo.event.disconnect("before",this.sheet,'onmouseup',this,'onmouseup');
    this.domouseup();
    hideElement(this.dragtop);hideElement(this.dragbot);
    hideElement(this.dragleft);hideElement(this.dragright);
  },
  drawoutline:function(ev) {
    if(this.hidden) {
      this.hidden = false;
      showElement(this.dragtop);showElement(this.dragbot);
      showElement(this.dragleft);showElement(this.dragright);
    }
    
    var rect = this.getdrawrect();
    var style = this.dragtop.style;
    style.left = rect.l + 'px';
    style.right = rect.r + 'px';
    style.top = rect.t + 'px';
    style.bottom = (rect.t+1)+'px';
    style.width = rect.w + 'px';
    
    style = this.dragbot.style;
    style.left=rect.l+'px';style.right=rect.r+'px';style.top = rect.b+'px';
    style.bottom=(rect.b+1)+'px';style.width=rect.w+'px';
    
    style = this.dragleft.style;
    style.left=rect.l+'px';style.right=(rect.l+1)+'px';style.top=rect.t+'px';style.bottom=rect.b+'px';
    style.height=rect.h+'px';
        
    style=this.dragright.style;
    style.left=rect.r+'px';style.right=(rect.r+1)+'px';style.top=rect.t+'px';style.bottom=rect.b+'px';
    style.height=(rect.h+2)+'px';
  },
  // methods that must be implemented
  setcontrolcell:function(ev) {
    // sets the control cell which is used to identify when a position change
    // has occured.  the control cell must be stored in this.cell
    throw new Error('not implemented');
  },
  domousemove:function(targetcell) {    
    // call when a mouse move event has occured and the target cell has been 
    // identified
    throw new Error('not implemented');
  },
  domouseup:function() {
    // called when the move is done
    throw new Error('not implemented');
  },
  getdrawrect:function() {
    // return the drawing rectanglehttp://hali:8080/qdJmX4whHczgFRrv?debugscripts=1 for showing the outline.
    throw new Error('not implemented');
  }
};
  
LiveSheet.celldrag = function() {
  LiveSheet.dragBase.call(this);
  this.construct.apply(this,arguments);
};

dojo.inherits(LiveSheet.celldrag,LiveSheet.dragBase);

dojo.lang.extend(LiveSheet.celldrag, {
//LiveSheet.celldrag.prototype = {
  setcontrolcell:function(ev) {
    this.cell = this.sheet.focusCell;
    this.origcell = this.cell;
  },
  domousemove:function(target) {
   if(target.key != this.cell.key && !target.getLocked()) {
      this.cell = target;
      this.drawoutline();
    }
  },
  domouseup:function() {
    if(this.cell.key != this.origcell.key) {
      this.moveCell();
    }
  },
  moveCell:function() {
    if(this.origcell.focusedState()) {
      this.origcell.setStateAfterDrag();
    }

    var undo = new LiveSheet.MoveUndo(this.origcell,this.origcell,this.cell,this.sheet);
    undo.doAction().addCallback(bind(this.afterMove,this));
  },
  afterMove:function() {
    this.sheet.focusCell = this.sheet.cCache.getCellByAttr(this.cell.col,this.cell.row);
    this.sheet.clickercb();
  },
  getdrawrect:function() {
    return new DocUtils.geometry.rect(this.cell.left(),this.cell.top(),this.cell.right(),this.cell.bottom());
  }
  });


LiveSheet.regiondrag = function() {
  LiveSheet.dragBase.call(this);
  this.construct.apply(this,arguments);
};

dojo.inherits(LiveSheet.regiondrag,LiveSheet.dragBase);

dojo.lang.extend(LiveSheet.regiondrag, {
    //LiveSheet.regiondrag.prototype = {
  setcontrolcell:function(ev) {
    var f = this.sheet.mousetrack.floater;
    this.regionrect = new DocUtils.geometry.rect(f.startcell.col,f.startcell.row,f.endcell.col,f.endcell.row);
    this.origstart = f.startcell;
    this.origend = f.endcell;

    var curEvent = this.sheet.normalize(ev);
    this.cell = this.sheet.cellfrompos(curEvent.x,curEvent.y,true);
    this.origcell = this.cell;
    this.drawrect = null;
    this.targetregion = null;
  },
  domousemove:function(target) {
    if(target.key != this.cell.key) {
      
      // compute the delta between the target and the tracking cell
      var rowdelta = target.row - this.origcell.row;
      var coldelta = target.col - this.origcell.col;
      
      var r = this.regionrect;
      var targetrect = new DocUtils.geometry.rect(r.l + coldelta,r.t + rowdelta,r.r + coldelta,r.b + rowdelta);
      if(targetrect.l < 1) {
        targetrect.l = 1;
        targetrect.r = targetrect.l + r.w;
        targetrect.w = r.w;
      }
      if(targetrect.t < 1) {
        targetrect.t = 1;
        targetrect.b = targetrect.t + r.h;
        targetrect.h = r.h;
      }
      if(targetrect.r > LiveSheet.maxcol) {
        targetrect.r = LiveSheet.maxcol;
        targetrect.l = targetrect.r - r.w;
        targetrect.w = r.w;
      }
      if(targetrect.b > LiveSheet.maxrow) {
        targetrect.b = LiveSheet.maxrow;
        targetrect.t = targetrect.b - r.h;
        targetrect.h = r.h;
      }

      // if the target rect is the same as previous do nothing.
      // if the targetrect overlaps a lock region (that we don't own)
      // do nothing
      if((this.targetregion && targetrect.equal(this.targetregion)) ||
         this.sheet.lockmanager.overlapLockedRegion(targetrect)) {
        return;
      }

      // get the top left and bottom based on the target rectangle to compute the 
      // drawing rectanlge
      var topleft = this.sheet.cellfrom(targetrect.t,targetrect.l);
      var botright = this.sheet.cellfrom(targetrect.b,targetrect.r);
      this.targetregion = targetrect;
      this.drawrect = new DocUtils.geometry.rect(topleft.left(),topleft.top(),botright.right(),botright.bottom());
      this.cell = target;
      this.drawoutline();
    }
  },
  domouseup:function() {
    if(this.targetregion && !this.targetregion.equal(this.regionrect)) {
      this.move(this.sheet.cellfrom(this.targetregion.t,this.targetregion.l));
    }
  },
  move:function(destleftcorner) {
    var undo = new LiveSheet.MoveUndo(this.origstart,this.origend,destleftcorner,this.sheet);
    undo.doAction();
    
    // move the floater to the new area.
    var f = this.sheet.mousetrack.floater;
    f.startcell = destleftcorner;
    f.move(this.sheet.cellfrom(f.startcell.row + this.regionrect.h,f.startcell.col + this.regionrect.w));
  },
  getdrawrect:function() {
    return this.drawrect;
  }
    //}
});

LiveSheet.refareaIds = ['__r1','__r2','__r3','__r4'];

LiveSheet.refarea = function(sheet,startcell) {
  this.sheet = sheet;
  this.startcell = startcell;

  var r = LiveSheet.refareaIds;
  if(!$(r[0])) {
    var p = this.sheet.parentdiv;
    this.dragtop = DIV({'class':'refH','id':r[0]},null);
    p.appendChild(this.dragtop);
    this.dragbot = DIV({'class':'refH','id':r[1]},null);
    p.appendChild(this.dragbot);
    this.dragleft = DIV({'class':'refV','id':r[2]},null);
    p.appendChild(this.dragleft);
    this.dragright = DIV({'class':'refV','id':r[3]},null);
    p.appendChild(this.dragright);
  }
  else {
    this.dragtop = $(r[0]);this.dragbot = $(r[1]);
    this.dragleft = $(r[2]);this.dragright=$(r[3]);
    forEach(r,showElement);
  }
  // always draw for the original cell
  this.move(startcell);

};


LiveSheet.refarea.prototype = {
  pointInSelection:function() {
    return false;
  },
  cleanup:function() {
    // hide everything - this is done in onFinal
  },
  adjustFocus:function() {
    // not implemented
  },
  dereg:function(invocation) {
    dojo.event.disconnect("around",this.sheet,'clickercb',this,'dereg');
    return;
  },
  onFinal:function(ev) {
    // generate the reference
    forEach(LiveSheet.refareaIds,hideElement);

    var range;
    if(this.startcell.key == this.endcell.key) {
      range = this.startcell.getRef();
      
      // in this case we need to some special event handling to avoid tripping the 
      // default click handler on the cell.
      dojo.event.connect("around",this.sheet,'clickercb',this,'dereg');
    }
    else {
      range = LiveSheet.rangeRefCell(this.startcell,this.endcell);
    }
   
    var cursor = new DocUtils.managecursor(this.sheet.inputcell);
    cursor.insertat(this.sheet.formulainput,range);
    cursor = new DocUtils.managecursor(this.sheet.inputcell);
    cursor.insertat(this.sheet.inputcell,range);
    
    if(this.sheet.formulalclicked) {
      this.sheet.formulainput.focus();
    }
    else {
      this.sheet.inputcell.focus();
    }
    this.sheet.focusCell.afterRef();
  },
  move:function(currentcell) {
    if(!currentcell.UserCell() || (this.endcell && this.endcell.key == currentcell.key)) {
      return;
    }

    this.endcell = currentcell;

    var l = Math.max(this.sheet.leftoffset(),Math.min(this.startcell.left(),currentcell.left()));
    var t = Math.max(this.sheet.topoffset(),Math.min(this.startcell.top(),currentcell.top()));
    var r = Math.max(this.startcell.right(),currentcell.right()) -1;
    var b = Math.max(this.startcell.bottom(),currentcell.bottom()) -1;
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
  }
};



