/* Copyright (C) 2006 Numbler LLC */
/* See LICENSE for details. */

DocUtils.DelayedLoader = function() {

  var delay = 100; // ms
  var queuelist = [];
  var unroll = 4;
  var running = false;

  this.enqueue = function(parent,func,args) {
    //var args = clone(arguments);
    //var args = arguments;
    //alert(arguments + ' ' + args);
    var f = function() {
      func.apply(parent,args);
      for(var i=0;i<unroll && i<queuelist.length;i++) {
        queuelist.shift()();
      }
      if(queuelist.length > 0) {
        setTimeout(queuelist.shift(),delay);
      }
      else {
        running = false;
      }
    }
    queuelist.push(f);
  }
  this.start = function() {
    if(!running) {
      var result = queuelist.shift();
      if(result) { 
        running = true;
        result(); 
      }
    }
  }
};

DocUtils.binsearch = function(source,target) {
  var max = source.length -1;

  var remainder = Math.round(max / 2);
  var pivot = remainder;
  var found = false;
  //print('target:'+target);
  while(!found) {
    remainder = Math.round(remainder / 2);
    //print('pivot:'+pivot);
    //if(isNaN(pivot)) { return -1; }
    if(target >= source[pivot]) {
      if(pivot == max || 
         (pivot+1 < source.length && target < source[pivot+1])) {
        found = true;
      }
      else {
        pivot = Math.min(pivot + remainder,max);
      }
    }
    else if(target < source[pivot]) {
      if(pivot == 0 || 
         (pivot-1 > 0 && target > source[pivot-1])) {
        pivot -= 1;
        found = true;
      }
      else {
        if(pivot == 1) { 
          pivot = 0;
          found = true;
        }
        pivot -= remainder;
      }
    };
  };
  return pivot;
};

DocUtils.framehelper = function(framename) {

  this.document = function() { return window.frames[framename].document; }

  var createElement = function() {
    var newelargs = arguments;

    return withWindow(window.frames[framename],function() {
                        return MochiKit.DOM.createDOM.apply(this,newelargs);
                      });
  };
                
  this.createDOM = function() {
    return MochiKit.Base.partial.apply(
                                       this,
                                       MochiKit.Base.extend([createElement], arguments)
                                       );
  };

  this.DIV = this.createDOM('DIV');
  this.INPUT = this.createDOM('INPUT');
  this.P = this.createDOM('P');
  this.HR = this.createDOM('HR');
  this.FORM = this.createDOM('FORM');

  this.addListener = function(obj,event,handler,bubbling) {
    // add the handler using the dojo fixup stuff.
    dojo.event.browser.addListener(obj,event,handler,bubbling);
    if(dojo.render.html.ie) {
      // go back and fixup the handlers to pass in right event
      // because of the iframe.  eeck.
      var eventname = 'on'+event;
      var oldhandler = obj[eventname];
                        
      obj[eventname] = function(ev) {
        if(!ev) {
          ev = window.frames[framename].event;
        }
        oldhandler(ev);
      }
    }
  };
};

////////////////////////////////////////////////////////////////////////////////
// contextmenu
////////////////////////////////////////////////////////////////////////////////

LiveSheet.contextMenu = function(sheet,currentTarget,elements) {
  this.x = null;
  this.y = null;
  this.sheet = sheet;
  this.currentTarget = currentTarget;
  // elements should be a dictionary in the form of
  // {'name of menu':action,'name of menu2':action}
  this.elements = elements;
  this.menuname = 'contextmenu';
  this.themenu = null;
};

LiveSheet.contextMenu.prototype.cleanup = function() {

  this.themenu= getElement(this.menuname);
  if(this.themenu) {
    this.themenu.parentNode.removeChild(this.themenu);
  }
};

LiveSheet.contextMenu.prototype.showme = function(x,y,parent) {
  this.x = x;
  this.y = y;

  this.cleanup();
  var myp = P(null);
  if(dojo.render.html.ie) {
    this.themenu = DIV({'id':this.menuname},
                       DIV({'class':'p-menu'},myp));
  }
  else {
    this.themenu = DIV({'id':this.menuname},
                       DIV({'class':'p-shadow'},DIV(null,myp)));
  }
  var me = this;


  var mapfunc = function(key) {
    if(key == '_override') {
      return me.elements[key].eval;
    }
    if(me.elements[key]._test) {
      if(me.elements[key]._test()) {
        return null;
      }
    }

    var menudiv =  DIV({'class':'contextmenuitem',
                           'onmouseover':function() { 
                           //this.style.backgroundColor = '#FFEEC2'; 
                           this.style.border = '1px solid black';
                         },
                           'onmouseout':function() { this.style.backgroundColor = '';this.style.border=''; }
                                                                 
                       },key);


    // note: we use mousedown and mouse up here instead of click
    // because the main document uses these events.  Because of the event bubbling
    // architecture we need to intercept the exact events on the context menu and
    // then make sure they don't propagate upwards.
    dojo.event.browser.addListener(menudiv,'mousedown',function(ev){ev.stopPropagation()},false);
    dojo.event.browser.addListener(menudiv,'mousemove',function(ev){ev.stopPropagation()},false);
    dojo.event.browser.addListener(menudiv,'click',function(ev) {
                                     ev.stopPropagation();
                                     me.elements[key]['eval'](ev);
                                     setTimeout(function() { hideElement(me.themenu)},100);

                                   },
                                   false); // use event bubbling!!
    return menudiv;
                
  }

  appendChildNodes(myp,map(mapfunc,keys(me.elements)));


  var el = this.themenu;
  el.style.left = x + 'px';
  el.style.top = y + 'px';
  parent.appendChild(el);
                                        
};
