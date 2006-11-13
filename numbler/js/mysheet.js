/* Copyright 2006 Numbler LLC */

// this is an import statment: don't touch!
// import Nevow.Athena


Number = {};

Numbler.ManageSheet = Nevow.Athena.Widget.subclass('Numbler.ManageSheet');


Numbler.ManageSheet.method(
 'changeName',
 function(self,name) {
   self.callRemote('changeName',name);
 }
 );


