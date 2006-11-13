/* Copyright (C) 2006 Numbler LLC */
/* See LICENSE for details. */

if(typeof(DocUtils) == 'undefined') {
  DocUtils = {};
 };

if(typeof(DocUtils.Widgets) == 'undefined') {
  DocUtils.Widgets = {};
 }

DocUtils.Widgets.modalCount = 0;

DocUtils.Widgets.modalVisible = function() {
  return DocUtils.Widgets.modalCount != 0;
};

DocUtils.Widgets.modalDialogBox = function() {};

DocUtils.Widgets.modalDialogBox.prototype.onShow = function() {
  DocUtils.Widgets.modalCount++;
};
DocUtils.Widgets.modalDialogBox.prototype.onClose = function() {
  DocUtils.Widgets.modalCount = Math.max(0,DocUtils.Widgets.modalCount - 1);
  log('onclose called, count is ',DocUtils.Widgets.modalCount)
};


DocUtils.Widgets.CenteredStyle = function(width,height) {

  // TODO: port to other browsers: see http://www.quirksmode.org/viewport/compatibility.html

  //    alert(window.innerHeight + ' ' + window.innerWidth + ' ' + window.pageXOffset + 
  //                            ' ' + window.pageYOffset + ' ' + 
  //                            window.screen.availWidth + ' ' + window.screen.availHeight);

  var xcenter = (window.innerWidth / 2)  + window.pageXOffset;
  var ycenter = (window.innerHeight / 2) + window.pageYOffset;

  return {'position':'absolute','left':(xcenter - (width/2)) + "px;",
      'top':(ycenter - (height/2)) + "px"};
};

DocUtils.Widgets.center = function(el) {
  // shamelesslessly stolen from dojo (replace all this cruft with dojo at some point)

  var dimel = el.parentNode; // get the dimension element from the parent
  var scrollTop = dimel.scrollTop;
  var scrollLeft = dimel.scrollLeft;
  var W = dimel.clientWidth || document.body.clientWidth || 0;
  var H = dimel.clientHeight || document.body.clientHeight || 0;
  el.style.display = "block";
  var w = 200;//el.offsetWidth;
  var h = 100; //el.offsetHeight;
  var L = scrollLeft + (W/2) - w; //(W - w)/2;
  var T = scrollTop + (H/2) - h;//(H - h)/2;
  with(el.style) {
    left = L + "px";
    top = T + "px";
  }

};


DocUtils.Widgets.errorBox = function(parentdiv,errtext,styleID,DOMObj) {
  this.errtext = errtext;
  this.styleID = styleID;
  this.parentdiv = parentdiv;
};

DocUtils.Widgets.errorBox.prototype = new DocUtils.Widgets.modalDialogBox(); // parent object

DocUtils.Widgets.errorBox.prototype.create = function() {
  var me = this;
        
  var buttonInput = INPUT({'class':'button',
                              'type':'submit',
                              value:'OK'
                              });
  dojo.event.browser.addListener(buttonInput,'click',bind(this.remove,this),false);
  
  var myp = P(null,
              DIV({'id':'errorboxtext'},this.errtext),
              FORM({'id':'errorboxform','method':'post','onsubmit':'return false;'},buttonInput));

  if(dojo.render.html.ie) {
    var boxel = DIV({'id':this.styleID,
                        'style':{'position':'absolute','width':'200px','height':'100px'}},
                    DIV({'class':'p-menu'},myp));
  }
  else {
    var boxel = DIV({'id':this.styleID,
                        'style':{'position':'absolute','width':'200px','height':'100px'}},
                    DIV({'class':'p-shadow'},
                        DIV(null,myp)));
  }
  
  this.parentdiv.parentNode.appendChild(boxel);
  DocUtils.Widgets.center(boxel);
  return boxel;
};

// ttl will indicate how long the message box should stay visible
DocUtils.Widgets.errorBox.prototype.show = function(ttl) {

  var boxel = this.create();
  if(ttl) {
    // I would like to use the mochikit deferred here but they didn't work for me.
    var me = this;
    this.deftimer = setTimeout(function() { me.remove(); },parseInt(ttl) * 1000);
  }
        
  this.onShow();
};

DocUtils.Widgets.errorBox.prototype.remove = function() {
  if(this.deftimer) {
    clearTimeout(this.deftimer);
  }
  var el = getElement(this.styleID);
  if(el) {
    el.parentNode.removeChild(el);
  }
  this.onClose();
};


DocUtils.Widgets.errorBox.prototype.fadein = function(ttl) {
  var el = this.create();
  dojo.graphics.htmlEffects.fade(el,250,0,bind(this.show,this));
  var me = this;
  if(ttl) {
    // I would like to use the mochikit deferred here but they didn't work for me.
    this.deftimer = setTimeout(function() { 
                                 me.fadeout();
                               },
                               parseInt(ttl) * 1000);
  }
};

DocUtils.Widgets.errorBox.prototype.fadeout = function() {
  dojo.graphics.htmlEffects.fade(getElement(this.styleID),250,1,0,bind(this.remove,this))
};


DocUtils.Widgets.editCollision = function(text) {
  this.text = text;
  this.onaccept = null;
  this.onignore = null;
  this.dialog = null;
};

DocUtils.Widgets.editCollision.prototype = {
  show:function(parent,x,y) {
    this.dialog = DIV(
                      {'class':'collision',
                          'style':
                        {'left':x + 'px','top':y + 'px'}},
                      FORM(null,
                           P(null,'Another user modified this cell.'),
                           P({'id':'newformula'},this.text),
                           INPUT({'type':'button','onclick':bind(this.onaccept_click,this),
                                     'value':'accept?'},null),
                           INPUT({'type':'button','onclick':bind(this.onignore_click,this),
                                     'value':'ignore'},null)));

    var b = dojo.event.browser;
    b.addListener(this.dialog,'mousedown',function(ev) { b.stopEvent(ev); return false; });
    b.addListener(this.dialog,'mousemove',function(ev) { b.stopEvent(ev); return false; });
    b.addListener(this.dialog,'mouseup',function(ev) { b.stopEvent(ev); return false; });
    b.addListener(this.dialog,'contextmenu',function(ev) { b.stopEvent(ev); return false; });
    parent.appendChild(this.dialog);
  },
  onaccept_click:function() {
    this.dialog.parentNode.removeChild(this.dialog);
    this.onaccept ? this.onaccept() : null;
  },
  onignore_click:function() {
    this.onignore ? this.onignore() : null;
    this.dialog.parentNode.removeChild(this.dialog);
  }
};


// ideally this would be a dojo widget... however the dojo
// infrastructure comes with a lot of baggage that I can't 
// quite fully comprehend right now.


DocUtils.Widgets.messageBox = function(query) {
  this.query = query;
};

DocUtils.Widgets.messageBox.prototype = {
  placeDialog:function() {
    dojo.widget.HtmlDialog.prototype.placeDialog.apply(this,arguments);
  },
  show:function(x,y) {
    this.butOK = INPUT({'type':'button','value':'OK'},null);
    this.butCancel = INPUT({'type':'button','value':'Cancel'},null);

    dojo.event.connect(this.butOK,'onclick',this,'onOK');
    dojo.event.connect(this.butCancel,'onclick',this,'onCancel');

    this.domNode = DIV({'class':'messageBox'},
                       P(null,this.query),
                       this.butOK,this.butCancel);

    this.domNode.style.display = "block";
    dojo.html.body().appendChild(this.domNode);

    if(x && y) {
      var s = this.domNode.style;
      s.left = x + "px";
      s.top = y + "px";
    }
    else {
      // needs to be called after it is appended into the DOM
      DocUtils.Widgets.center(this.domNode);
    }
    //dojo.fx.fade(this.domNode,250,0,1,function(node) {});
  },
  remove:function() {
    dojo.fx.fadeOut(this.domNode,250,function(node) {
                      node.parentNode.removeChild(node);
                    });
  },
  onOK:function() {
    this.remove();
  },
  onCancel:function() {
    this.remove();
  }
};

dojo.widget.PopupMenu2.prototype.findChild = function(caption) {
  for(var i=0;i<this.children.length;i++) {
        var child = this.children[i];
        if(child.caption == caption) {
          return child;
        }
  }
  return null;
};


