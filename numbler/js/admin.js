/* Copyright (C) 2006 Numbler LLC */
/* See LICENSE for details. */

function checkcreateform() {
  var f = document.forms.createsheet;
  if(f.sheetname.value == '') {
    alert('you must provide a description of your spreadsheet');
    return false;
  }
  return checkname();
};

function checkname() {
  var sheetuser = document.getElementById('sheetusernick');
  if(sheetuser.value == '') {
    alert('you must provide your name or nick name (like in instant messaging)');
    return false;
  };
  return true;
};
