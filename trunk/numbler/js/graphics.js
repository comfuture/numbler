/* Copyright (C) 2006 Numbler LLC */
/* See LICENSE for details. */

dojo.require("dojo.graphics.*");

if(typeof(DocUtils) == 'undefined') {
  DocUtils = {};
 };

DocUtils.graphics = {};

DocUtils.graphics.startglow = function(el,aStartOpac,aEndOpac,aTimer) {
  var fadingIn = false;
  //var el = document.getElementById('fadeElm');
  var startopac = aStartOpac ||1;
  var endopac = aEndOpac || 0.5;
  var timer = aTimer || 1500;
  var anim = null;

  var switchfade = function() {
    !fadingIn ? fadein() : fadeout();
  };
        
  this.stop = function() {
    if(anim) {
      anim.stop();
    }
  }
        
  var fadeout = function() {
    anim = dojo.graphics.htmlEffects.fade(el,timer,startopac,endopac,switchfade);
    fadingIn = false;
  };
        
  var fadein = function() {
    anim = dojo.graphics.htmlEffects.fade(el,timer,endopac,startopac,switchfade);
    fadingIn = true;
  };
        
  fadeout();
        
};              
