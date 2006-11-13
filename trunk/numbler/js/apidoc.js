/* Copyright (C) 2006 Numbler LLC */
/* See LICENSE for details. */

if(typeof(LiveSheet) == 'undefined') {
  Numbler = {};
 };
Numbler.apidoc = {};

Numbler.apidoc.loadTree = function(str) {
  var thetree = eval(str);

  Numbler.apidoc.tree = new YAHOO.widget.TreeView("treediv");
  
  function createTree(node,treenode) {
    for(var i=0;i<node.length;i++) {
      var cnode = node[i];
  
      var detail = {label:cnode[0],link:cnode[1]};
      var newtreenode = new YAHOO.widget.TextNode(detail,treenode,false);
      var oldtoggle = newtreenode.toggle;
      newtreenode.toggle = partial(Numbler.apidoc.ontoggle,oldtoggle,cnode[1]);
      if(cnode.length == 3) {
        createTree(cnode[2],newtreenode);
      }
    }
  }
  createTree(thetree,Numbler.apidoc.tree.getRoot());
  Numbler.apidoc.tree.draw();
};


Numbler.apidoc.ontoggle = function(oldtoggle,nodelink) {
  oldtoggle.apply(this,arguments);
  Numbler.apidoc.fetchsection('/apidoc/' + nodelink);
};

Numbler.apidoc.fetchsection = function(url) {
  var req = getXMLHttpRequest();
  req.open('GET',url, true);  
  var d = sendXMLHttpRequest(req);
  document.body.style.cursor = 'wait';
  d.addCallback(Numbler.apidoc.onGetDoc);
  d.addErrback(Numbler.apidoc.onFailedDoc);
  d.addBoth(Numbler.apidoc.restoreCursor);
}

Numbler.apidoc.restoreCursor = function() {
  document.body.style.cursor = '';
}

Numbler.apidoc.onGetDoc = function(arg) {
  $('apicontent').innerHTML = arg.responseText;
  var nodes = getElementsByTagAndClassName("*","doclink",$('apicontent'))
  for(var i=0;i<nodes.length;i++) {
    var cnode = nodes[i];
    connect(nodes[i],'onclick',partial(function(node,ev) {
                                         Numbler.apidoc.fetchsection(node.href);
                                         ev.stop();
                                       },cnode));
  }
}

Numbler.apidoc.onFailedDoc = function(arg) {
  $('apicontent').innerHTML = DIV(null,P(null,"Oops.  This section of documentation is currently missing.")).innerHTML;
}
