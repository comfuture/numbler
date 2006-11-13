/* Copyright (C) 2006 Numbler LLC */
/* See LICENSE for details. */

if(typeof(LiveSheet) == 'undefined') {
  LiveSheet = {};
 };

LiveSheet.Cache = function() {
  this.AddException = new MochiKit.Base.NamedError("CacheAddException");
  this.cache = {}
};

LiveSheet.Cache.prototype = {
  exists: function(key) {
    return key in this.cache;
  },
  get: function(key) {
    return key in this.cache ? this.cache[key] : null;
  },
  add: function(key,value) {
    if(!this.exists(key)) {
      this.cache[key] = value;
    }
    else {
      throw this.AddException;
    }
  },
  update:function(key,value) {
    var oldvalue = this.get(key);
    this.cache[key] = value;
    return oldvalue;

  },
  updateList:function(ul) {
    for(var i=0;i<ul.length;i+=2) {
      this.update(ul[i],ul[i+1]);
    }
  },
  remove:function(key) {
    var oldvalue = this.get(key);
    delete this.cache[key];
    return oldvalue;
  },
  removeIf:function(key,value) {
        // remove only if the key and value match
        var oldvalue = this.get(key);
        if(oldvalue && (oldvalue == value)) {
          delete this.cache[key];
        }
  },
  removeList:function(rl) {
    forEach(rl,this.remove,this);
  },
  empty:function() {
    // no way to get the number of items in the dictionary (that I know of)
    // if there is *anything* then return false
    for(var item in this.cache) {
      return false;
    }
    return true;
  },
  compare:function(props) {
    // properties is expect to be an array of keys
    for(var i=0;i<props.length;i+=2) {
      var c = this.get(props[i]);
      if(c != props[i+1]) {
        return false;
      }
    }
    return true;
  },
  comparenull:function(props) {
    for(var i=0;i<props.length;i++) {
      // the property can be there but it should not contain anything
      if(props[i] in this.cache && this.cache[props[i]]) {
        return false;
      }
    }
    return true;
  },
  proplist:function(akeylist) {
    var keylist = akeylist || keys(this.cache);
    var ret = [];
    for(var i=0;i<keylist.length;i++) {
      ret.push(keylist[i]);
      ret.push(this.get(keylist[i]));
    }
    return ret;
  },
  json:function() {
    return {
      'cache':this.cache
    }
    //return simpleJSON(this,['cache']);
  },
  purge:function() {
        this.cache = {}
  }
};
