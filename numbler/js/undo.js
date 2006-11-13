/* Copyright (C) 2006 Numbler LLC */
/* See LICENSE for details. */

if(typeof(LiveSheet) == 'undefined') {
  LiveSheet = {};
 };


LiveSheet.implException = function(method) {
  this.name = 'undoException';
  this.message = method + ' not implemented';
};
LiveSheet.implException = new Error();

LiveSheet.UndoObject = function() {
  this.bypassvalid = false;
};

LiveSheet.UndoObject.prototype = {
  // all UndoObjects must implement these methods.
  bypass:function() {
        var ret = this.bypassvalid;
        this.bypassvalid = false;
        return ret;
  },
  setBypass:function() {
        this.bypassvalid = true;
  },
  undo:function() {
        // undo's the action.  the undo manager is responsible
        // for placing the undo object on the redo stack.
        throw new LiveSheet.implException('undo');
  },
  redo:function() {
        // applies the action.  Redo should be the same
        // as applying the action to begin with.
        throw new LiveSheet.implException('redo');
  },
  doAction:function() { this.redo(); },
  valid:function() {
        // if the undo valid action is still valid - it may not be
        // do to changes by remote users.
        throw new LiveSheet.implException('valid');
  },
  userString:function() {
        // returns a format for displaying to the user in the undo /redo buffer.
        throw new LiveSheet.implException('userString');
  }
};


LiveSheet.undoManager = function() {
  this.undostack = [];
  this.redostack = [];
  this.undolength = 20;
};

LiveSheet.undoManager.prototype = {
  pushundo:function(obj) {
    this.undostack.push(obj);
  },
  popundo:function() {
    return this.undostack.pop();
  },
  shiftundo:function() {
        return this.undostack.shift();
  },
  pushredo:function(obj) {
    this.redostack.push(obj);
  },
  popredo:function(count) {
    if(count == this.redostack.length) {
      this.redostack = [];
      return null;
    }
    else {
      return this.redostack.pop();
    }
  },
  add:function(obj) {
    // add to the undo stack.  Any adds will clear out the redostack.
        if(this.undostack.length == this.undolength) {
          var last = this.shiftundo();
          delete last;
        }

    this.pushundo(obj);

    if(this.redostack.length) {
      this.popredo(this.redostack.length);
    }
    this.adjusttoolbar();
  },
  continueUndo:function(countLeft) {

  },
  undo:function(itemnumber) {
    if(this.undostack.length) {
      // undo the last n item(s) on the stack.
      var count = itemnumber ? Math.min(this.undostack.length,itemnumber) : 1;
      log('*** undo: at item ' + count + ' ****');
      var obj = this.undostack.slice(-1)[0];
          if(!obj.valid()) {
                if(!obj.bypass()) {
                  this.onInvalidUndo(obj,count);
                  return;
                }
          }
          var error = false;
          var d;
          try {
                d = obj.undo();
          }
          catch(e) {
                log('exception occured in undoManager.undo ',e);
                error = true;
          }
          var old = this.popundo();
          if(error) {
            this.onUndoException(obj);
            // we throw away the broken undo.  is this the right thing to do?
          }
          else {
            if(count > 1) {
              log('registering for callback');
              d.addCallback(bind(partial(this.undo,count - 1),this));
            }
            this.pushredo(old);
          }
        }
        // reset the toolbar here
        this.adjusttoolbar();
  },
  redo:function(itemnumber) {
    if(this.redostack.length) {
      var count = itemnumber ? Math.min(this.redostack.length,itemnumber) : 1;
          log('*** redo: at item ' + count + ' ****');
          var obj = this.redostack.slice(-1)[0];
          var error = false;
          var d;
          try {
                d = obj.redo();
          }
          catch(e) {
                log('exception occurred in undoManager.redo ',e);
                error = true;
          }
          var old = this.popredo();
          if(error) {
                this.onRedoException(obj);
          }
          else {
                if(count > 1) {
                  d.addCallback(bind(partial(this.redo,count-1),this));
                }
                this.pushundo(old);
          }
        }
        this.adjusttoolbar();
  },
  adjusttoolbar:function() {
    // adjust toolbars to reflect the current reality
    LiveSheet.Sheetbar.setUndoCount(this.undostack.length);
    LiveSheet.Sheetbar.setRedoCount(this.redostack.length);
  },
  onUndoException:function(object) {
    // called when an error ocurs with the undo object.
  },
  onRedoException:function(object) {

  },
  onInvalidUndo:function(object,count) {
    // called when an undo is potentially unsafe so we can ask the user
    // what action to take.
    var msg = ['The undo event "',object.userString(),
                           '" was modified by another user.  Click OK to overwrite the change'].join('');
    var mb = new DocUtils.Widgets.messageBox(msg);
    dojo.event.connect(mb,'onOK',bind(partial(this.acceptInvalidChange,count,object),this));
    dojo.event.connect(mb,'onCancel',this,'rejectInvalidChange');
    mb.show();
    return true;
  },
  acceptInvalidChange:function(count,obj) {
    obj.setBypass(); // bypass next change
    this.undo(count); // restart the undo
  },
  rejectInvalidChange:function() {
    this.popundo(); // forget about the change - it is lost!
  }
};








