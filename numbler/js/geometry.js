/* Copyright (C) 2006 Numbler LLC */
/* See LICENSE for details. */

if(typeof(DocUtils) == 'undefined') {
  DocUtils = {};
 };

DocUtils.geometry = {};

// fully defined rectangle: left,top,right,bottom (no width or height)
DocUtils.geometry.rect = function(l,t,r,b) {
  this.l = Math.min(l,r);
  this.r = Math.max(l,r);
  this.t = Math.min(t,b);
  this.b = Math.max(t,b);
  this.w = this.r - this.l;
  this.h = this.b - this.t;
};
DocUtils.geometry.rect.prototype = {
  toString:function() {
    return [this.l,' ',this.t,' ',this.r, ' ',this.b].join('');
  },
  json:function() {
    return {
      'l':this.l,
      'r':this.r,
      't':this.t,
      'b':this.b
    }
    //return simpleJSON(this,['l','t','r','b']);
  },
  pointInRect:function(x,y) {
        return x >= this.l && x <= this.r && y >= this.t && y <= this.b;
  },
  clip:function(b) {
    var l,t,r,b;
    var a = this;
    var done = false;
    do {
      // left
      if((a.l >= b.l) && (a.l <= b.r)) 
        l = a.l;
      else if((b.l >= a.l) && (b.l <= a.r))
        l = b.l;
      else break;
      // right
      if((a.r >= b.l) && (a.r <= b.r))
        r = a.r;
      else if((b.r >= a.l) && (b.r <= a.r))
        r = b.r;
      else break;
      // top
      if((a.t >= b.t) && (a.t <= b.b))
        t = a.t;
      else if((b.t >= a.t) && (b.t <= a.b))
        t = b.t;
      else break;
      // bottom
      if((a.b >= b.t) && (a.b <= b.b))
        b = a.b;
      else if((b.b >= a.t) && (b.b <= a.b))
        b = b.b;
      else break;
      done = true;
    } while(false);

    if(!done) {
      return null;
    }
    return new DocUtils.geometry.rect(l,t,r,b);
  },
  evalregion:function(cb) {
    for(var i=this.l;i<=this.r;i++)
      for(var j=this.t;j<=this.b;j++)
        cb(i,j);
  },
  equal:function(t) {
    return this.l == t.l && this.r == t.r && this.t == t.t && this.b == t.b;
  }
};

// specific for cells meaning that any shared edge is an overlap (while normally
// a shared edge is adjacent)
DocUtils.geometry.doRectsIntersect = function(a,b) {
  return ((a.l >= b.l && a.l <= b.r) ||
          (b.l >= a.l && b.l <= a.r)) && 
  ((a.t >= b.t && a.t <= b.b) ||
   (b.t >= a.t && b.t <= a.b));
};

