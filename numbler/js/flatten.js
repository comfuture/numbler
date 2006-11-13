/* Copyright (C) 2006 Numbler LLC */
/* See LICENSE for details. */

flattener = {};

flattener.XHTML = function() {
  this.contents = [];

  this.DIV =  this.createDOM("DIV");
  this.contents.append = this.contents.push;
};

flattener.XHTML.prototype = {
  generate: function() {
    return this.contents.join('');
    //this.contents = [];
  },
  createEl:function(name,attrs/* children */) {
    var c = this.contents;
    c.append('<');c.append(name);
    if(attrs) {
      this.addAttributes(attrs);
    }
    c.append('>');
    ///if(arguments.length <= 2) return;
                
    for(var i=2;i<arguments.length;i++) {
      var t = typeof(arguments[i]);
      if(t == 'string') {
        c.append(arguments[i]);
        if(i+1 < arguments.length) {
          c.append(' ');
        }
      }
      else if(t == 'object') {
        // FIXME: not support
      }
    }

    c.append('</');c.append(name);c.append('>');
                
  },
  addAttributes: function(attrs) {
    var c = this.contents;
    for(var k in attrs) {
      var v = attrs[k];
      if(typeof(v) == 'object') {
        if(k == 'style') { // FIXME: lowercase
          c.append(' style="');
          for(var i in v) {
            var sattr = v[i];
            c.append(i);
            c.append(':');
            c.append(sattr);
            c.append(';');
          }
          c.append('"');
        }
      }
      else {
        c.append(' ');
        c.append(k);
        c.append('="');
        c.append(v);
        c.append('"');
      };
    }
  },
  createDOM: function() {
    return MochiKit.Base.partial.apply(
                                       this,
                                       MochiKit.Base.extend([this.createEl], arguments)
                                       )
  }
};
