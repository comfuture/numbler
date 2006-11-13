/* Copyright (C) 2006 Numbler LLC */
/* See LICENSE for details. */

if(typeof(DocUtils) == 'undefined') {
  DocUtils = {};
 };


DocUtils.benchmark = function() {

  var markers = []

  var dumper;
  if(typeof(log) != 'undefined') {
    dumper = log;
  }
  else if(typeof(print) != 'undefined') {
    dumper = print;
  }
  else if(typeof(alert) != 'undefined') {
    dumper = alert;
  }
  else {
    // I have no mouth and cannot scream.
  }

  this.mark = function() {
    markers.push(new Date().getTime());
  };
  this.getElapsed = function() {
    return (markers[markers.length-1] - markers[0])/1000;
  };
  this.elapsedSummary = function() {
    return this.getElapsed() + " seconds";
  };
  this.elapsedSpans = function() {
    var result = '';
    for(var i=1;i<markers.length;i++) {
      result += ((markers[i]-markers[i-1])/1000) + ' ';
    }
    result += "seconds";
    return result;
  };
  this.report = function(funcName) {
    if(markers.length == 2) {
      dumper((funcName || "") + this.elapsedSummary());
    }
    else if(markers.length > 2) {
      dumper((funcName || "") + this.elapsedSpans());
    }
  };
};

function benchContainer(func,name) {
  log('running ' + name);
  var bench = new DocUtils.benchmark();
  bench.mark();
  func();
  bench.mark();
  bench.report(name + ": ");
};

