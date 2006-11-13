/* Copyright (C) 2006 Numbler LLC */
/* See LICENSE for details. */

if(typeof(Numbler) == 'undefined') {
  Numbler = {};
 }

Numbler.funcdoc = {};

Numbler.funcdoc.loadTree = function(str) {
  var thetree = eval(str);

  Numbler.funcdoc.tree = new YAHOO.widget.TreeView("treediv");
  
  function createTree(node,treenode) {
    for(var i=0;i<node.length;i++) {
      var cnode = node[i];
  
      var detail = {label:cnode[0],link:cnode[1]};
      var newtreenode = new YAHOO.widget.TextNode(detail,treenode,false);
      var oldtoggle = newtreenode.toggle;
      newtreenode.toggle = partial(Numbler.funcdoc.ontoggle,oldtoggle,cnode[1]);
      if(cnode.length == 3) {
        var flist = cnode[2];
        for(var j=0;j<flist.length;j++) {
          var func = flist[j];
          var detail = {label:func,link:cnode[1]};
          var funcitem = new YAHOO.widget.TextNode(detail,newtreenode,false);
          var oldtoggle = funcitem.toggle;
          funcitem.toggle = partial(Numbler.funcdoc.ontoggle,oldtoggle,cnode[1]);         
        }
      }
    }
  }

  createTree(thetree,Numbler.funcdoc.tree.getRoot());
  Numbler.funcdoc.tree.draw();
};

Numbler.funcdoc.ontoggle = function(oldtoggle,nodelink) {
  oldtoggle.apply(this,arguments);
  Numbler.funcdoc.fetchsection('/functiondoc/sections/' + nodelink);
};

Numbler.funcdoc.fetchsection = function(url) {
  var req = getXMLHttpRequest();
  req.open('GET',url, true);  
  var d = sendXMLHttpRequest(req);
  document.body.style.cursor = 'wait';
  d.addCallback(Numbler.funcdoc.onGetDoc);
  d.addErrback(Numbler.funcdoc.onFailedDoc);
  d.addBoth(Numbler.funcdoc.restoreCursor);
}

Numbler.funcdoc.restoreCursor = function() {
  document.body.style.cursor = '';
}

Numbler.funcdoc.onGetDoc = function(arg) {
  $('funccontent').innerHTML = arg.responseText;
}

Numbler.funcdoc.onFailedDoc = function(arg) {
  $('funccontent').innerHTML = DIV(null,P(null,"Oops.  This section of documentation is currently missing.")).innerHTML;
}

