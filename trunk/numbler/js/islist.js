/********************************************************************************
 ** (C) Numbler LLC 2006
 ********************************************************************************/

// javascript implementation of an interval skip list
// algorithm derived from Hanson, E. and T. Johnson, "The Interval Skip List: 
// A Data structure for Finding All Intervals That Overlap a Point", 16 June 1992

function isList() {};

isList.P = 0.5;

isList.Node = function(searchKey,levels) {
  this.key = searchKey;
  this.forward = [];
  this.markers = [];
  this.eqmarkers = [];
  this.ownerCount;
  this.topLevel = levels;
};

isList.Node.prototype = {
  get_next:function() {
    return this.forward[0];
  },
  level:function() { return this.topLevel+1; },
  getValue:function() { return this.key; },
  isHeader:function() { return this.key == 0; },
  get_next:function() { return this.forward[0]; },
  toString:function() {
    ret = [];
    ret.push('isList.Node:\n');
    ret.push(this.key ? this.key.toString() : 'HEADER');
    ret.push('\n');
    ret.push('number of levels : ');ret.push(this.level());
    ret.push(' owning intervals: ownerCount = ');
    ret.push(this.ownerCount);
    ret.push('\nforward pointers:\n');
    for(var i=0;i<this.topLevel;i++) {
      ret.push('forward[' + i + '] = ');
      ret.push(this.forward[i] ? this.forward[i].key.toString() : "NULL");
      ret.push('\n');
    }
    ret.push('markers:\n');
    for(var i=0;i<this.topLevel;i++) {
      ret.push('markers[' + i + '] =');
      ret.push(this.markers[i] ? this.markers[i].toString() : "NULL");
      ret.push('\n');
    }
    ret.push('EQ markers: ');
    ret.push(eqMarkers.toString());
    ret.push('\n');
    return ret.join('');
  }
};

isList.Interval = function(left,right) {
  this.left = left;
  this.right = right;
	
};
isList.Interval.prototype = {
  // only support [left,right] semantics right now
  contains:function(value) { return value >= this.left && value <= this.right; },
  containsInterval:function(l,r) { return l > this.left && r < this.right; },
  toString:function() { return ['[',this.left,',',this.right,']'].join(''); }
};

isList.IntervalList = function() {
  this.header = null;
};

isList.IntervalList.prototype = {
  insert:function(interval) {
    var temp = new isList.IntervalListElt(interval);
    temp.next = header;
    this.header = temp;
  },
  remove:function(interval) {
    var x = this.header,last = null;
    while(x && x.getInterval() != interval) {
      last = x;
      x = x.next;
    }
    if(!x) return;
    else if(!last) {
      this.header = x.next;
      delete x;
    }
    else {
      last.next = x.next;
      delete x;
    }
  },
  removeAll:function(interval) {
    var x;
    for(x = interval.get_frst(); x; x= interval.get_next(x)) {
      this.remove(x.getInterval());
    }
  },
  get_first:function() {
    return this.header;
  },
  get_next:function(element) {
    return element.next;
  },
  toString:function() {
    var e = this.header;
    var ret = [];
    while(e) {
      ret.push(e.toString());
      e = e.get_next();
    }
    return ret.join('');
  }
};

isList.IntervalListElt = function(interval) {
  this.interval = interval;
  this.next = null;
};

isList.IntervalListElt.prototype = {
  toString:function() { return this.interval ? this.interval.toString() : ''; },
  set_next:function(next) { this.next = next; },
  get_next:function() { return this.next; },
  getInterval:function() { return this.interval; }
};



isList.IntervalSkipList = function() {
  this.maxLevel = 0;
  this.header = new isList.Node(null,48); // 48 is maximum number of forward pointers

};

isList.IntervalSkipList.prototype.toString = function() {
  var ret = [];
  var n = this.header.get_next();
  while(n) {
    ret.push(n.toString());
    n = n.get_next();
  }
};

isList.IntervalSkipList.prototype.randomLevel = function() {
  var levels = 0;
  while(isList.P < Math.random()) levels++;
  if(levels <= this.maxLevel) {
    return levels; 
  }
  else { 
    return this.maxLevel + 1; 
  }
};

isList.IntervalSkipList.prototype.placeMarkers = function(left,right,interval) {
  var x = left;
  if(interval.contains(x.key)) x.eqMarkers.insert(interval);
	
  var i=0; // start at level 0 and go up
  while(x.forward[i] && interval.containsInterval(x.key,x.forward[i].key)) {
    // find level to put mark on
    while(i != x.topLevel && x.forward[i+1] && interval.containsInterval(x.key,x.forward[i+1].key)) {
      i++;
    }
    // Mark current level i edge since it is the highest edge out of
    // x that contains I, except in the case where current level i edge
    // is null, in which case it should never be marked.
    if(x.foward[i]) {
      x.markers[i].insert(interval);
      x = x.forward[i];
      // Add interval to eqMarkers set on node unless currently at right endpoint
      // of interval and interval doesn't contain right endpoint.
      if(interval.contains(x.key)) x.eqMarkers.insert(interval);
    }
  }
  // mark non-ascending path
  while(x.key != right.key) {
    // find level to put mark on
    while(i!=0 && (x.forward[i] == null || 
		   !interval.containsInterval(x.key,x.forward[i].key))) {
      i--;
    }
    // At this point, we can assert that i=0 or x->forward[i]!=0 and I contains 
    // (x->key,x->forward[i]->key).  In addition, x is between left and 
    // right so i=0 implies I contains (x->key,x->forward[i]->key).
    // Hence, the interval must be marked.  Note that it is impossible
    // for us to be at the end of the list because x->key is not equal
    // to right->key.
    x.markers[i].insert(interval);
    x = x.forward[i];
    if(interval.contains(x.key)) { x.eqMarkers.insert(interval);
    }
  }
};

isList.IntervalSkipList.prototype.removeMarkers = function(left,interval) {
  // Remove markers for interval I, which has left as it's left
  // endpoint,  following a staircase pattern.
  // remove marks from ascending path	
  x = left;
  if(interval.contains(x.key)) x.eqMarkers.remove(interval);
  var i=0; // start at level 0 and go up
  while(x.forward[i] && interval.containsInterval(x.key,x.forward[i].key)) {
    // find level to take mark from
    while(i != x.topLevel && x.forward[i+1] && 
	  interval.containsInterval(x.key,x.forward[i+1].key)) {
      i++;
    }
    // Remove mark from current level i edge since it is the highest edge out 
    // of x that contains I, except in the case where current level i edge
    // is null, in which case there are no markers on it.
    if(x.forward[i]) {
      x.markers[i].remove(interval);
      x = x.forward[i];
      // remove I from eqMarkers set on node unless currently at right 
      // endpoint of I and I doesn't contain right endpoint.
      if(interval.contains(x.key)) x.eqMarkers.remove(interval);
    }
  }
  // remove marks from non-ascending path
  while(x.key != interval.right) {
    // find level to remove mark from
    while(i != 0 && (x.forward[i] == null ||
		     !interval.containsInterval(x.key,x.forward[i].key))) {
      i--;
    }
    // At this point, we can assert that i=0 or x->forward[i]!=0 and I contains 
    // (x->key,x->forward[i]->key).  In addition, x is between left and 
    // right so i=0 implies I contains (x->key,x->forward[i]->key).
    // Hence, the interval is marked and the mark must be removed.  
    // Note that it is impossible for us to be at the end of the list 
    // because x->key is not equal to right->key.
    x.markers[i].remove(interval);
    x = x.forward[i];
    if(interval.contains(x.key)) x.eqMarkers.remove(interval);
  };	
};


isList.IntervalSkipList.prototype.removeMarkFromLevel = function(interval,i,left,right) {
  var x;
  for(x=1;x != 0 && x != right; x = x.forward[i]) {
    x.markers[i].remove(interval);
    x.eqMarkers.remove(interval);
  }
  if(x!=0) x.eqMarkers.remove(m);
};

isList.IntervalSkipList.prototype.adjustMarkersOnInsert = function(x,update) {
	

};




