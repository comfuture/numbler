/* Copyright (C) 2006 Numbler LLC */
/* See LICENSE for details. */

if(typeof(DocUtils) == 'undefined') {
  DocUtils = {};
 };


DocUtils.fixupTable = {187:null,219:null,221:null,220:null,186:null,
                                           222:null,188:null,190:null,191:null,192:null
                       //                                          45:null// insert
};

// 
// still need 187 220 186 192
DocUtils.revfixupTable = {46:null,44:null,47:null,39:null,91:null,93:null}


DocUtils.modclipTable = {86:null,/*V*/88:null,/*X*/89:null,/*Y*/90:null/*Z*/};
DocUtils.clipTable = {67:null,/*C*/86:null,/*V*/88:null,/*X*/89:null,/*Y*/90:null/*Z*/};

DocUtils.mozNavIgnore = {37:null,38:null,39:null,40:null,9:null};


DocUtils.eventchar = function(ev) {
  var code;
  if(!ev) ev = window.event;
  if(ev.keyCode) code = ev.keyCode;
  else if(ev.which) code = ev.which;
  
  return {'code':code,
          'val':String.fromCharCode(code)[ev.shiftKey ? 'toUpperCase' : 'toLocaleLowerCase'](),
          'shift':ev.shiftKey,
          'metakeys':ev.ctrlKey || ev.altKey,
          'ignore':code == ev.KEY_CTRL 
          || code == ev.KEY_ALT || 
          code == ev.KEY_SHIFT,
          'toString':function() {
          return this.code + ',' + this.val + ',' + this.shift;
        }};
};


DocUtils.managecursor = function(inputel) {
  this.supported = false;
  this.atend = true;
  this.curpos = 0;
  this.textSelected = false;
  this.inputel = inputel;

  if(inputel.createTextRange) {
    // IE specific support for text range.  IE sucks so much.
    this.supported = true;
          var selrange = document.selection.createRange();
        if(inputel.tagName == "TEXTAREA") {
          // from http://the-stickman.com/web-development/javascript/finding-selection-cursor-position-in-a-textarea-in-internet-explorer/
          // We'll use this as a 'dummy'
          var stored_range = selrange.duplicate();
          // Select all text
          stored_range.moveToElementText(inputel);
          // Now move 'dummy' end point to end point of original range
          stored_range.setEndPoint( 'EndToEnd', selrange);
          // Now we can calculate start and end points

          var selstart = stored_range.text.length - selrange.text.length;
          var selend = selstart + selrange.text.length; 
          this.textSelected = (selstart != selend);
          this.curpos = selstart;
          this.atend = (stored_range.text.length == inputel.value.length);
        }
        else {
          var elrange = inputel.createTextRange();
          var newrange = elrange.duplicate();
          newrange.setEndPoint("EndToStart",selrange);
          this.atend = newrange.text.length == elrange.text.length;
          this.curpos = newrange.text.length;
          this.textSelected = selrange.text.length != elrange.text.length;
        }
  }
  else if(inputel.setSelectionRange) {
    this.supported = true;
    this.atend = inputel.value.length == inputel.selectionStart;
        this.curpos = inputel.selectionStart;
        this.textSelected = (inputel.selectionStart != inputel.selectionEnd);
  }
};

DocUtils.managecursor.prototype = {

  insertat:function(targetel,value) {
    if(this.supported && !this.atend) {
      targetel.value = targetel.value.slice(0,this.curpos) + value + 
      targetel.value.slice(this.curpos,targetel.value.length);
    }
    else {
      targetel.value += value;
    }
  },
  backspace:function(targetel) {
    if(this.curpos <= 0) return;
    if(this.supported && !this.atend) {
      targetel.value = targetel.value.slice(0,this.curpos-1) + targetel.value.slice(this.curpos,
                                                                                   targetel.value.length);
    }
    else {
      targetel.value = targetel.value.slice(0,targetel.value.length-1);
    };
  },
  dodelete:function(targetel) {
        if(this.textSelected) {
          var s = this.inputel;
          setTimeout(function() { targetel.value = s.value},1);
        }
        else if(!this.atend) {
          targetel.value = targetel.value.slice(0,this.curpos) + targetel.value.slice(this.curpos+1);
        }
  }
};




function setScrollHeight(el,newvalue) {
  if(typeof(el.scrollTop) != 'undefined') {
    el.scrollTop = newvalue;
  }
  else if(typeof(el.scrollY) != 'undefined') {
    el.scrollY = newvalue;
  }
}
function setScrollWidth(el,newvalue) {

  if(typeof(el.scrollLeft) != 'undefined') {
    el.scrollLeft = newvalue;
  }
  else if(typeof(el.scrollX) != 'undefined') {
    el.scrollX = newvalue;
  };
};

function findPosX(obj)
{
  var curleft = 0;
  if (obj.offsetParent)
    {
      while (obj.offsetParent)
        {
          curleft += obj.offsetLeft
            obj = obj.offsetParent;
        }
    }
  else if (obj.x)
    curleft += obj.x;
  return curleft;
}

function findPosY(obj)
{
  var curtop = 0;
  if (obj.offsetParent)
    {
      while (obj.offsetParent)
        {
          curtop += obj.offsetTop
            obj = obj.offsetParent;
        }
    }
  else if (obj.y)
    curtop += obj.y;
  return curtop;
}

DocUtils.bindprotos = function(source,target) {
  forEach(keys(source.prototype),function(val) { target[val] = source.prototype[val];});
};

DocUtils.deepcopy = function(self, obj) {
  if (self == null) {
    self = {};
  }
  for (var k in obj) {
    var v = obj[k];
    if(v && typeof(v) == 'object' && ! v.parentNode) { // ignore DOM nodes
      if(self[k]) {
        arguments.callee(self[k],v);
      }
      else {
        self[k] = arguments.callee(null,v);
      }
    }
    else {
      self[k] = v;
    }
  }
  return self;
};

DocUtils.bitarray = function() {
  this.bitArray = [];
};

DocUtils.bitarray.prototype = {
  bitmasks:[1,2,4,8,16,32,64,128,256,512,1024,2048,4096,8192,16384,32768,
            65536,131072,262144,524288,1048576,2097152,4194304,8388608,
            16777216,33554432,67108864,134217728,268435456,536870912,
            1073741824,2147483648],

  set:function(index) {
    this.bitArray[index >> 5] |= this.bitmasks[index % 32];
  },
  get:function(index) {
    var t = this.bitmasks[index % 32];
    return (this.bitArray[index >> 5] & t) == t;
  },
  toString:function() {
    var ret = [];
    for(var item in this.bitArray) {
      var base = item << 5;
      for(var i=0;i<32;i++) {
        if(this.get(base+i)) {
          ret.push(base+i);
        }
      }
    }
    return ret.join(',');
  }
}

DocUtils.athenaWrapper = function() {
  this.globalcb = null;
  this.globaleb = null;

  this.calcCallback = function(args) {
    currentsheet.onCellCalc(args[0],args[1]);
    return args;
  };
  this.logClientError = function(res) {
    server.callRemote('logClientError',res);
  };
};
DocUtils.athenaWrapper.prototype = {
  setGlobalCallback:function(cb) {
        this.globalcb = cb;
  },
  setGlobalErrback:function(eb) {
        this.globaleb = eb;
  },
  callRemote:function() {
        var d = server.callRemote.apply(server,arguments);
        if(this.globalcb) {
          d.addCallback(this.globalcb);
        }
        if(this.globaleb) {
          d.addErrback(this.globaleb);
        }
        return d;
  },
  callRemoteWithCalc:function() {
    /* useful when you want to direct the return value from the server to onCellCalc */
    var d = this.callRemote.apply(this,arguments);
    d.addCallback(this.calcCallback);
    d.addErrback(this.logClientError);
    return d;
  }
};

// create a global object for use by everone
sheetServer = new DocUtils.athenaWrapper();
