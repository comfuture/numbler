/********************************************************************************
 ** (C) Numbler LLC 2006
 ********************************************************************************/

if(typeof(DocUtils) == 'undefined') {
  DocUtils = {};
 };

if(typeof(DocUtils.locking) == 'undefined') {
  DocUtils.locking = {};
 };

/*

LockManager takes a lockUiInterface that is expected to have a number
of functions

onFailure(): when a lock request fails
onLock(): when the server indicates a new lock has been taken out
onUnlock(): when the server releases a lock


*/


DocUtils.locking.lockManager = function(lockUI) {
  this.locklist = {};
  this.lockrequestlist = [];
  this.lastLockID = 0;
  this.lockUI = lockUI;
};


// responsible for basic lock management and iteraction
// with the server.  should be generic

DocUtils.locking.lockManager.prototype = {
	
  load: function(locks) {
    for(var i=0;i<locks.length;i++) {
      this.addlock(locks[i]);
      // locks are loaded before the cells are created so don't draw at this time
      //this.lockUI.onLock(locks[i]);
    }
  },
  redrawlocks: function() {
    for(var lockitem in this.locklist) {
      this.lockUI.onLock(this.locklist[lockitem]);
    }
  },
  addlockremote:function(args) {
    return this.addlock(args[0])
  },
  addlock: function(thelock) {
    if(!(thelock instanceof DocUtils.locking.lockregion)) {
      DocUtils.bindprotos(DocUtils.locking.lockregion,thelock);
    }
    this.locklist[thelock.lockuid] = thelock;
    return thelock;
  },

  releaseLock: function(lock) {
    // this should call back to the client.
    if(!lock) return;
    //var lockUID = lock instanceof DocUtils.locking.lockregion ? lock.lockuid : lock;
    var lockUID = lock.lockuid || lock;
    // TODO: should I used the deferred here?
    sheetServer.callRemote('releaseLock',lockUID);
  },
  onUpdateLocks:function(locklist) {
    for(var i=0;i<locklist.length;i++) {
      var cLock = locklist[i];
      try {
	if(cLock.lockuid in this.locklist) {
	  //var existing = this.locklist[cLocak.lockuid];
	  // remove the old lock.
	  var cowner = this.locklist[cLock.lockuid].owner;
	  this.onReleaseLock(cLock.lockuid);
	  // draw the new one and set the ownership flag. yes this is insecure.
	  cLock.owner = cowner;
	  this.onLockRegion(cLock);
	}
      }
      catch(err) {
	// do nothing
      }
    }
  },
  getLock: function(lockUID) {
    if(lockUID in this.locklist) {
      return this.locklist[lockUID];
    }
    else {
      throw (lockUID + " not found");
    };
  },

  requestLock : function (thelock) {
    var id = this.lastLockID;
    this.lockrequestlist.push(this.lastLockID++)
    //d.callback(thelock);
    d = sheetServer.callRemote('requestLock',thelock,id);
    d.addCallback(bind(this.addlockremote,this));
    d.addCallback(bind(this.lockUI.onLock,this.lockUI));
    d.addErrback(bind(this.lockUI.onFailure,this.lockUI),thelock);
    log('requested lock from server');
  },

  onReleaseLock : function (lockUID) {
    // when the lock is released by the server or a remote user
    if(lockUID in this.locklist) {
      this.lockUI.onUnlock(this.locklist[lockUID])
      delete this.locklist[lockUID];
    }
  },

  // NO LONGER USED
  onRequest : function(lock,id) {
    // after receiving a lock response from the server
    log('onRequest: ',lock)
    var theid = parseInt(id);
    if(theid in this.lockrequestlist) {
      var d = this.lockrequestlist[theid];
      thelock.locked ? d.callback(lock) : d.errback(null,lock);
      // TODO: cleanup the array at some point 
    }
  },
  onLockRegion: function(lock) {
    // called when a region is locked by a remote user.
    this.lockUI.onLock(this.addlock(lock));
  },
  overlapLockedRegion:function(rect) {
    // note: this is an inefficent algorithm that needs to be replaced 
    // with a stabbing query solution, IBS tree, interval skip list, etc.
    // this *will* fall over with large number of locks
    for(var lockitem in this.locklist) {
      var item = this.locklist[lockitem];
      if(!item.owner && DocUtils.geometry.doRectsIntersect(rect,item.rect)) {
	return true;
      }
    }
    return false;
  }
};


DocUtils.locking.locktypes = ['temp','perm'];

DocUtils.locking.lockregion = function() {
  this.topleft = {'col':0,'row':0};
  this.bottomright = {'col':0,'row':0};
  this.type = "temp";
  this.timerequested = toISOTimestamp(new Date())
  this.lockduration = 0;
  this.lockend = ''
  this.locked = false;
  this.lockuid = '';
  this.owner = false; // set by the server if you are the owner
  this.user = ''; // set by the server for the remote user who has the lock
};

DocUtils.locking.lockregion.prototype = {
  setRegion : function(topleft,bottomright) {
    this.topleft.col = topleft.col;this.topleft.row = topleft.row;
    this.bottomright.col = bottomright.col;this.bottomright.row = bottomright.row;
    this.rect = new DocUtils.geometry.rect(topleft.col,topleft.row,bottomright.col,bottomright.row);
  },
  setRegionRow: function(row) {
    this.topleft.col = 1; this.bottomright.col = LiveSheet.maxcol;
    this.topleft.row = row; this.bottomright.row = row;
    this.rect = new DocUtils.geometry.rect(1,row,LiveSheet.maxcol,row);
  },
  setRegionCol: function(col) {
    this.topleft.row = 1; this.bottomright.row = LiveSheet.maxrow;
    this.topleft.col = col; this.bottomright.col = col;
    this.rect = new DocUtils.geometry.rect(col,1,col,LiveSheet.maxrow);
  },
  showowner:function() {
    if(!this.tooltip) {
	  var x = parseInt(this.floater.style.top.slice(0,-2));
	  var y = parseInt(this.floater.style.left.slice(0,-2));
	  this.tooltip = DIV({'class':'locktt','style':
						   {'position':'absolute','top':((x+10) + 'px'),
							   'left':((y+10) + 'px')}},'locked by ' + this.user);
      this.floater.parentNode.appendChild(this.tooltip);
    }
  },
  hideowner:function() {
    if(this.tooltip) {
      this.floater.parentNode.removeChild(this.tooltip);
      delete this.tooltip;
    }
  },
  ownervisible:function() {
	return typeof(this.tooltip) == 'undefined';
  }
};


DocUtils.locking.lockUI = function(parent,sheet) {
  this.parent = parent;
  this.sheet = sheet;
  this.domobj = MochiKit.DOM;
};

DocUtils.locking.lockUI.prototype = {
	
  onFailure: function(error,lock) {
    log('onFailure called');
    var errbox = new DocUtils.Widgets.errorBox(document.body,
					       'Unable to lock the range of cells.',
					       'errorbox');
    errbox.fadein(5);

  },
  onLock: function(lock) {
    // note: this gets called as part of the deferred callback chain

    var intersect = this.sheet.drawrect.clip(lock.rect);
	if(intersect) {
	  intersect.evalregion(function(col,row) {
				 new LiveSheet.Cell(col,row).setLocked(lock);
			       });
	  
	  lock.owner ? this.drawUserLockedRegion(lock) : this.drawLockedRegion(lock);
	}
  },
  onUnlock: function(lock) {
    var intersect = this.sheet.drawrect.clip(lock.rect);
	if(!intersect) { 
	  lock.box = null;
	  return;
	}
	
    intersect.evalregion(function(col,row) {
			   new LiveSheet.Cell(col,row).clearLocked();
			 });

    if(lock.box) {
      // this can fail if the box exists but was removed from 
      // the parent by a scrolling event.
      try {
		this.parent.removeChild(lock.box);
      }
      catch(e) {
      }
    }
  },
  drawLockedRegion: function(lock) {
    // draw a region that is currently locked by another user
    // set the opacity on all of the cells from the top left to the bottom right
		
    // get the intersecting rectange based on the current view area.
    var intersect = this.sheet.drawrect.clip(lock.rect);
    if(!intersect) {
      // let's go home!
      lock.box = null;
      return;
    }
		
    // get the real cells from the intersection
    var topleft = new LiveSheet.Cell(intersect.l,intersect.t);
    var bottomright = new LiveSheet.Cell(intersect.r,intersect.b);
		
    var l = topleft.left();
    var r = bottomright.right();
    var t = topleft.top();
    var b = bottomright.bottom();
		
    lock.box = this.domobj.DIV(null);
    lock.floater = this.domobj.DIV({'class':'lockrange',
				       'style':{'height':(b-t)+'px','top':t + 'px',
					 'bottom':b + 'px',
					 'width':(r-l)+'px','left':l + 'px','right':r + 'px'}});
	
	dojo.event.connect(lock.floater,'oncontextmenu',this,'oncontextmenu');
	dojo.event.connect(lock.floater,'onmouseover',bind(partial(this.onmouseover,lock),this));
	dojo.event.connect(lock.floater,'onmouseout',bind(partial(this.onmouseout,lock),this));
	dojo.event.connect(lock.floater,'onmousedown',dojo.event.browser,'stopEvent');
	dojo.event.connect(lock.floater,'onmousemove',dojo.event.browser,'stopEvent');
	dojo.event.connect(lock.floater,'onmouseup',dojo.event.browser,'stopEvent');


    lock.box.appendChild(lock.floater);

    this.parent.appendChild(lock.box);
    this.drawUserLockedRegion(lock,true);
  },
  onmouseover:function(lock,ev) {
	lock.deftooltip = callLater(0.5,bind(lock.showowner,lock));
  },
  onmouseout:function(lock,ev) {
	lock.deftooltip.cancel();
	lock.hideowner();
  },
  oncontextmenu:function(ev) {
	dojo.event.browser.stopEvent(ev);
  },
  drawUserLockedRegion: function(lock,fromLockedRegion) {
    //draw a region that is locked by the user
    // get the *real* cells
    var intersect = this.sheet.drawrect.clip(lock.rect);
    if(!intersect) {
      lock.box = null;
      return;
    }

    var topleft = new LiveSheet.Cell(intersect.l,intersect.t);
    var bottomright = new LiveSheet.Cell(intersect.r,intersect.b);
		
    var l = topleft.left();
    var r = bottomright.right();
    var t = topleft.top();
    var b = bottomright.bottom();
		
    var hprops = {'class':'lockH','style':{'height':(b-t)+'px','top':t + 'px','bottom':b + 'px'}};
    var vprops = {'class':'lockV','style':{'width':(r-l)+'px','left':l + 'px','right':r + 'px'}};
		
    if(!fromLockedRegion) {
      lock.box = this.domobj.DIV(null);
      this.parent.appendChild(lock.box);
    }
    appendChildNodes(lock.box,
		     updateNodeAttributes(this.domobj.DIV(hprops),{'style':{'left':(l)+'px','right':(l+2) + 'px'}}),
		     updateNodeAttributes(this.domobj.DIV(hprops),{'style':{'left':(r)+'px','right':(r+2) + 'px'}}),
		     updateNodeAttributes(this.domobj.DIV(vprops),{'style':{'bottom':(t+2)+'px','top':(t) + 'px'}}),
		     updateNodeAttributes(this.domobj.DIV(vprops),{'style':{'bottom':(b+2)+'px','top':b + 'px'}}));
  }
};
