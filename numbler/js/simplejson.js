/* Copyright (C) 2006 Numbler LLC */
/* See LICENSE for details. */

// simple helper function that converts object key values 
// into a JSON string.  


function simpleJSON(obj,attrs) {

  function nullHandler(val) {
    if(typeof(val) == "string") {
      return reprString(val);
      //return '"' + reprString(val) + '"';
    }
    else if(typeof(val) == 'function') {
      return null;
    }
    else if(typeof(val) == 'object') {
      if(!val) {
        return '"' + "null" + '"';
      }
      else {
        if(val.toJSON) {
          // if object supports a toJSON method use it
          return val.toJSON();
        }
        else {
          return simpleJSON(val);
        }
      }
    }
    return val;
  };
        
  if(!attrs) {
    attrs = keys(obj);
  }

  if(isArrayLike(obj)) {
    return '[' + concat(map(function(key) { return nullHandler(obj[key]) },
                            attrs)) + ']';
  }
  else if(typeof(obj) == 'object') {
    return '{' + concat(map(function(key) { return '"' + key + '":' + nullHandler(obj[key]) },
                            attrs)) + '}';
  }
};
