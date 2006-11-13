/*****
 *
 *   RedBlackTree.js
 *
 *   copyright 2004, Kevin Lindsey
 *   licensing info available at: http://www.kevlindev.com/license.txt
 *
 *
 * Modifications made to support atLeast, atMost functions as well 
 * as searching using alternate compare functions.
 *****/

/*****
 *
 *   class variables
 *
 *****/

RedBlackTree.VERSION = 1.0;


/*****
 *
 *   constructor
 *
 *****/
function RedBlackTree() {
  this._root      = null;
  this._cursor    = null;
  this._ancestors = [];
  this.defcompare = false;
  this.defaultCompare();
}

RedBlackTree.prototype.defaultCompare = function() {
  if(!this.defcompare) {
    this.compare = "compare";
    this.lt = "lt";
    this.gt = "gt";
    this.key = "key";
    this.defcompare = true;
  }
};

RedBlackTree.prototype.alternateCompare = function() {
  if(this.defcompare) {
    this.compare = "acompare";
    this.lt = "alt";
    this.gt = "agt";
    this.key = "akey";
    this.defcompare = false;
  }
};

/*****  private methods *****/

/*****
 *
 *   _findNode
 *
 *****/
RedBlackTree.prototype._findNode = function(value, saveAncestors) {
  if ( saveAncestors == null ) saveAncestors = false;

  var result = this._root;

  if ( saveAncestors ) {
    this._ancestors = [];
  }
    
  while ( result != null ) {
    var relation = value[this.compare](result._value);

    if ( relation != 0 ) {
      if ( saveAncestors ) {
	this._ancestors.push(result);
      }
      if ( relation < 0 ) {
	result = result._left;
      } else {
	result = result._right;
      }
    } else {
      break;
    }
  }

  return result;
};

// find the first node that is "at least" as big as the value.
// if nothing is at Least as big as the value then atLeast returns null
// to use atLeast and atMost the class in the tree must implement 
// gt,lt,compare, and key
// (samples for Number)
//
// Number.prototype.gt = function(that) { return this > that; }
// Number.prototype.lt = function(that) { return this < that; }
// Number.prototype.key = function() { return this; }
// Number.prototype.compare = function(that) { return this - that; }

RedBlackTree.prototype.atLeast = function(value) {
  var result = this._root;

  var lastGreatest =  null;
  if(result != null) {
    lastGreatest = result._value;
  }

  while ( result != null ) {
    var relation = value[this.compare](result._value);
		
    if ( relation != 0 ) {
      if ( relation < 0 ) {
	result = result._left;
      } else {
	result = result._right;
      }
      //print(result);
      if(result && result._value[this.gt](value)) {
	lastGreatest = result._value;
      }
    } else {
      break;
    }
  }
  if(result == null) {
    if(lastGreatest == null) {
      return null;
    }
    if(lastGreatest[this.lt](value)) {
      return null;
    }
    else {
      return lastGreatest;
    }
  }
  else {
    return result._value;
  }
};

// find the value in the tree that is "at most" as large as the
// than the specified value.  if the value is smaller than anything in
// in the tree the result is null.
RedBlackTree.prototype.atMost = function(value) {
  var result = this._root;
	
  var lastSmallest = null;
  if(result != null) {
    var seedrelation = value[this.compare](result._value);
    if(seedrelation < 0) {
      lastSmallest = {}
      lastSmallest[this.key] = function() { return -1; }
      lastSmallest[this.gt] = Number.prototype.gt;
    }
    else {
      lastSmallest = result._value;
    }
  }

  while ( result != null ) {
    var relation = value[this.compare](result._value);
		
    if ( relation != 0 ) {
      if ( relation < 0 ) {
	result = result._left;
      } else {
	result = result._right;
      }
      //print(result,lastSmallest);
      if(result && result._value[this.lt](value)) {
	lastSmallest = result._value[this.key]() > lastSmallest[this.key]() ? result._value : lastSmallest;
      }
    } else {
      break;
    }
  }
  if(result == null) {
    if(lastSmallest == null) {
      return null;
    }
    else if(lastSmallest[this.key]() == -1 || lastSmallest[this.gt](value)) {
      return null;
    }
    else {
      return lastSmallest;
    }
  }
  else {
    return result._value;
  }
};



/*****
 *
 *   _maxNode
 *
 *****/
RedBlackTree.prototype._maxNode = function(node, saveAncestors) {
  if ( node == null ) node = this._root;
  if ( saveAncestors == null ) saveAncestors = false;

  if ( node != null ) {
    while ( node._right != null ) {
      if ( saveAncestors ) {
	this._ancestors.push(node);
      }
      node = node._right;
    }
  }

  return node;
};


/*****
 *
 *   _minNode
 *
 *****/
RedBlackTree.prototype._minNode = function(node, saveAncestors) {
  if ( node == null ) node = this._root;
  if ( saveAncestors == null ) saveAncestors = false;

  if ( node != null ) {
    while ( node._left != null ) {
      if ( saveAncestors ) {
	this._ancestors.push(node);
      }
      node = node._left;
    }
  }

  return node;
};


/*****
 *
 *   _nextNode
 *
 *****/
RedBlackTree.prototype._nextNode = function(node) {
  if ( node != null ) {
    if ( node._right != null ) {
      this._ancestors.push(node);
      node = this._minNode(node._right, true);
    } else {
      var ancestors = this._ancestors;
      parent = ancestors.pop();
            
      while ( parent != null && parent._right === node ) {
	node = parent;
	parent = ancestors.pop();
      }

      node = parent;
    }
  } else {
    this._ancestors = [];
    node = this._minNode(this._root, true);
  }

  return node;
};


/*****
 *
 *   _previousNode
 *
 *****/
RedBlackTree.prototype._previousNode = function(node) {
  if ( node != null ) {
    if ( node._left != null ) {
      this._ancestors.push(node);
      node = this._maxNode(node._left, true);
    } else {
      var ancestors = this._ancestors;
      parent = ancestors.pop();
            
      while ( parent != null && parent._left === node ) {
	node = parent;
	parent = ancestors.pop();
      }

      node = parent;
    }
  } else {
    this._ancestors = [];
    node = this._maxNode(this._root, true);
  }

  return node;
};


/*****  public methods  *****/

/*****
 *
 *   add
 *
 *****/
RedBlackTree.prototype.add = function(value) {
  var result;
    
  if ( this._root == null ) {
    result = this._root = new RedBlackNode(value);
  } else {
    var addResult = this._root.add(value);

    this._root = addResult[0];
    result = addResult[1];
  }

  return result;
};


/*****
 *
 *   find
 *
 *****/
RedBlackTree.prototype.find = function(value) {
  var node = this._findNode(value);
    
  return ( node != null ) ? node._value : null;
};


/*****
 *
 *   findNext
 *
 *****/
RedBlackTree.prototype.findNext = function(value) {
  var current = this._findNode(value, true);

  current = this._nextNode(current);

  return (current != null ) ? current._value : null;
};


/*****
 *
 *   findPrevious
 *
 *****/
RedBlackTree.prototype.findPrevious = function(value) {
  var current = this._findNode(value, true);

  current = this._previousNode(current);

  return (current != null ) ? current._value : null;
};


/*****
 *
 *   max
 *
 *****/
RedBlackTree.prototype.max = function() {
  var result = this._maxNode();

  return ( result != null ) ? result._value : null;
};


/*****
 *
 *   min
 *
 *****/
RedBlackTree.prototype.min = function() {
  var result = this._minNode();

  return ( result != null ) ? result._value : null;
};


/*****
 *
 *   next
 *
 *****/

RedBlackTree.prototype.next = function() {
  this._cursor = this._nextNode(this._cursor);

  return ( this._cursor ) ? this._cursor._value : null;
};


/*****
 *
 *   previous
 *
 *****/
RedBlackTree.prototype.previous = function() {
  this._cursor = this._previousNode(this._cursor);

  return ( this._cursor ) ? this._cursor._value : null;
};


/*****
 *
 *   remove
 *
 *****/
RedBlackTree.prototype.remove = function(value) {
  var result;

  if ( this._root != null ) {
    var remResult = this._root.remove(value);

    this._root = remResult[0];
    result = remResult[1];
  } else {
    result = null;
  }

  return result;
};


/*****
 *
 *   traverse
 *
 *****/
RedBlackTree.prototype.traverse = function(func) {
  if ( this._root != null ) {
    this._root.traverse(func);
  }
};


/*****
 *
 *   toString
 *
 *****/
RedBlackTree.prototype.toString = function() {
  var lines = [];

  if ( this._root != null ) {
    var indentText = "  ";
    var stack = [[this._root, 0, "^"]];

    while ( stack.length > 0 ) {
      var current = stack.pop();
      var node    = current[0];
      var indent  = current[1];
      var line    = "";

      for ( var i = 0; i < indent; i++ ) {
	line += indentText;
      }
            
      line += current[2] + "(" + node.toString() + ")";
      lines.push(line);

      if ( node._right != null ) stack.push([node._right, indent+1, "R"]);
      if ( node._left  != null ) stack.push([node._left,  indent+1, "L"]);
    }
  }
    
  return lines.join("\n");
};
