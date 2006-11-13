/* Copyright 2006 Numbler LLC */

// this is an import statment: don't touch!
// import Nevow.Athena


Numbler = {};

// Numbler.NumblerWidget = Nevow.Athena.Widget.subclass('Numbler.NumblerWidget');

// Numbler.NumblerWidget.oldCallRemote = Numbler.callRemote;
// Numbler.NumblerWidget.methods(
// //Numbler.NumblerWidget.prototype = {
//   function callRemote(self) {
//     var d= Numbler.NumblerWidget.oldCallRemote.apply(self,arguments);
//     d.addErrback(function(x) { alert(x); });
//     return d;
//   }
// );

//Numbler.MyAccount = Numbler.NumblerWidget.subclass('Numbler.MyAccount');


Numbler.MyAccount = Nevow.Athena.Widget.subclass('Numbler.MyAccount');

Numbler.yoursheetsStr = "Your Sheets:";
Numbler.nosheetsStr = "You do not have any sheets yet.";
Numbler.membersheetstr = "Sheets you are a member of:";
Numbler.nomembersheetsstr = "You have not been invited to any sheets.";


Numbler.mysheetcount = 0;
Numbler.mymembercount = 0;

function renderTitlesOnLoad() {
  
  var header = $('yoursheetsheader');
  var membersheets = $('yourmembersheets');
  if(header) {
    header.innerHTML = Numbler.mysheetcount >  0 ? Numbler.yoursheetsStr : Numbler.nosheetsStr;
  }
  if(membersheets) {
    membersheets.innerHTML = Numbler.mymembercount > 0 ? Numbler.membersheetstr : Numbler.nomembersheetsstr;
  }
}
       

MochiKit.DOM.addLoadEvent(renderTitlesOnLoad);


Numbler.MyAccount.methods(
//Numbler.MyAccount.prototype = {
 function addnewsheet(self) {
   var textinput = self.firstNodeByAttribute("class","newsheetname");
   if(textinput.value.length) {
     var d= self.callRemote('addnewsheet',textinput.value);
     d.addCallback(bind(self.addNewFragment,self));
     d.addCallback(renderTitlesOnLoad);

     textinput.value = '';
   }
 },
 function addNewFragment(self,args) {
   newfrag = args[0];
   id = args[1];
   Divmod.Runtime.theRuntime.appendNodeContent($('mysheets'),newfrag);
   Nevow.Athena.Widget._widgetNodeAdded(parseInt(id));
 }
);

// yet another style of writing JS courtesy of divmod ;)

Numbler.ManageSheet = Nevow.Athena.Widget.subclass('Numbler.ManageSheet');
// corresponds to managesheet.xml
Numbler.ManageSheet.methods(
//Numbler.ManageSheet.prototype = {
  function __init__(self,widgetNode) {
    Numbler.ManageSheet.upcall(self, "__init__",widgetNode);
    // gather together some stuff
    Numbler.mysheetcount += 1;

    self.mynode = self.nodeByAttribute("class","sheetdetails");
    self.showdetails = self.nodeByAttribute("class","expander");
    connect(self.showdetails,'onclick',self,'toggledetails');
    self.loadeduserlist = false;
    Nevow.Athena.notifyOnDisconnect(bind(self.ondisconnect,self));
  },
  function ondisconnect(self,failure) {
    alert('connection to the server lost.');
    history.go(0);
  },
  function bindEventsOnFirstLoad(self) {

    var handlers = {'invitetext':'inviteinput',
		    'currentmembers':'cmembers',
		    'sheetpublic':'publicsheet',
		    'sheetprivate':'privatesheet',
		    'sheetname':'sheetnameinput',
		    'deletetab':'deletetab',
		    'invitesum':'summary',
		    'applychanges':'applybut',
		    'updatecont':'updateserver'
    };

    var nodes = getElementsByTagAndClassName("*",null,self.node);
    for(var i=0;i<nodes.length;i++) {
      var nodname = nodes[i].className;
      if(nodname in handlers) {
	self[handlers[nodname]] = nodes[i];
	delete handlers[nodname];
      }
    }
    connect(self.inviteinput,'onkeypress',self,'oninvitekeypress');
    connect(self.inviteinput,'onclick',self,'oninviteclick');
    connect(self.deletetab,'onclick',self,'deletesheet');
    connect(self.applybut,'onclick',self,'applyChanges');
    self.fh = null;
    self.th = null;
  },
  function showUpdate(self) {
    if(self.fh) {
      self.fh.stop();
      self.fh = null;
    }
    if(self.th) {
      clearTimeout(self.th);
      self.th = null;
    }
    self.fh = dojo.fx.html.fadeIn(self.updateserver,250,bind(self.waitfade,self));
  },
  function waitfade(self) {
    self.fh = null;
    self.th = setTimeout(bind(self.stopUpdate,self),1000);
  },
  function stopUpdate(self) {
    self.th = null;
    self.fh = dojo.fx.html.fadeOut(self.updateserver,250);
  },
  function expandDetails(self) {
    self.showdetails.innerHTML = "-";
    self.showdetails.className = "expandopen";
    showElement(self.mynode);
    hideElement(self.summary);
    showElement(self.deletetab);
  },
  function hideDetails(self) {
    self.showdetails.innerHTML = "+";
    self.showdetails.className = "expander";
    hideElement(self.mynode);
    showElement(self.summary);
    hideElement(self.deletetab);
  },
  function afterload(self,args) {      
    self.expandDetails();
    self.sheetnameinput.value = args[0].name;
    if(args[0].type == 0) {
      self.publicsheet.checked = true;
    }
    else {
      self.privatesheet.checked = true;
    }

    var results = args[1];
    for(var i=0;i<results.length;i++) {
      self.addInviteLine(results[i]);
    }
    self.loadeduserlist = true;
  },
  function addInviteLine(self,data) {
    var removediv = DIV({'class':'removelink'},'[x]');
    var usernode;
    if(data.pending) {
      usernode = DIV({'class':'pending','title':'pending'},data.dispname);
    }
    else {
      usernode = DIV({'class':'member','title':data.username},data.dispname);
    }


    var node = DIV({'class':'sheetmember'},usernode,
		   removediv,DIV({'style':{'clear':'both'}},null));
      self.cmembers.appendChild(node);
      connect(removediv,'onclick',bind(partial(self.removeuser,node,data.username,data.pending),self));
  },
  function toggledetails(self,ev) {
    if(self.mynode.style.display == "block") {
      self.hideDetails();
    }
    else {
      if(!self.loadeduserlist) {
	self.bindEventsOnFirstLoad();
	self.callRemote('getDetails').addCallback(bind(self.afterload,self));
      }
      else {
	self.expandDetails();
      }
    }
    ev.stop();
  },
  function oninvitekeypress(self,ev) {
    if(ev.key().code == 13) {
      self.inviteInternal();
      ev.stop();
    }
  },
  function oninviteclick(self,ev) {
    if(self.inviteinput.value == 'enter an email address') {
      self.inviteinput.value = '';
    }
  },
  function changePendingCount(self,count) {
    var pendingel = self.nodeByAttribute("class","pendcount");
    pendingel.innerHTML = (parseInt(pendingel.innerHTML) + count);

  },
  function changeCurrentCount(self,count) {
    var countel = self.nodeByAttribute("class","nummembers");
    countel.innerHTML = (parseInt(countel.innerHTML) + count);
  },
  function inviteInternal(self) {
    if(self.inviteinput.value == 'enter an email address') {
      self.inviteinput.value = '';
    }
    if(self.inviteinput.value.length) {
      var invitelist;
      if(self.inviteinput.value.search(/,/) > 0) {
	invitelist = self.inviteinput.value.split(',');
      }
      else {
	invitelist = [self.inviteinput.value]
	  }
      var d = self.callRemote('addUsers',invitelist);
      self.showUpdate();
      d.addCallback(bind(self.afterInvite,self));
      self.inviteinput.value = '';
      return d;
    }
    return null;
  },
  function afterInvite(self,args) {
    var header = args;
    if(header.error == 'dupe') {
      alert(header.dupelist + ' is a duplicate email address');
    }
    else if (header.error == 'badaddrs') {
      alert(header.invalidusers + ' is not a valid email address');
    }
    else if(header.error == 'dnfailure') {
      alert(header.invaliddn + ' is not a registered internet domain');
    }
    else if(header.error == 'selfinvite') {
      alert("you don't need need to invite yourself to a sheet that you created.");
    }
    else {
      var pending = header.pending;
      var current = header.current;
      self.changeCurrentCount(current.length);
      self.changePendingCount(pending.length);
      forEach(pending,function(x) { self.addInviteLine({'username':x,'dispname':x,'pending':true}) });
      forEach(current,function(x) { self.addInviteLine({'username':x.username,'dispname':x.dispname,'pending':false}) });
    }
  },
  function removeuser(self,node,username,pending) {
    var d= self.callRemote('removeUsers',[username]);
    self.showUpdate();
    d.addCallback(bind(partial(self.afterRemove,node,pending),self));
  },
  function afterRemove(self,node,pending) {
    self.cmembers.removeChild(node);
    pending ? self.changePendingCount(-1) : self.changeCurrentCount(-1);
  },
  function deletesheet(self) {
    self.callRemote('beforeDeleteSheet').addCallback(bind(self.deletecb,self));
  },
  function deletecb(self,count) {
    dodelete = false;
    if(count > 0) {
      dodelete = confirm('There are users still connected to this spreadsheet. ' + 
			 'Deleting the spreadsheet will disconnect all users from the spreadsheet.  ' + 
			 'Also, we recommend exporting your spreadsheet first before deleting it.');
    }
    else {
      dodelete = confirm('do you really want to delete this spreadsheet? ' + 
			 'We strongly advise that you export your spreadsheet first before deleting it.');
    }
    if(dodelete) {
      self.hideDetails();
      self.summary.innerHTML = '';
      self.summary.appendChild(DIV({'class':'standout'},'Deleting...'));
      self.callRemote('deleteSheet').addBoth(bind(self.afterDelete,self));
    }
  },
  function afterDelete(self,arg) {
    self.node.parentNode.removeChild(self.node);
    Numbler.mysheetcount = Math.max(0,Numbler.mysheetcount -1);
    renderTitlesOnLoad();
  },
  function applyChanges(self,ev) {
    ev.stop();
    if(self.sheetnameinput.value.length == 0) {
      alert('a valid name is required');
    }
    // save the sheet type and spreadsheet name
    var type = -1;
    if(self.privatesheet.checked) {
      type = 1;
    }
    if(self.publicsheet.checked) {
      type = 0;
    }
    
    var d = self.callRemote("applyChanges",type,self.sheetnameinput.value);
    self.showUpdate();
    d.addCallback(bind(self.afterchange,self));
    self.inviteInternal();
  },
  function afterchange(self) {
    self.nodeByAttribute("class","sheetnamelink").innerHTML = self.sheetnameinput.value;
  }
  //}			  
);


Numbler.ManageMemberList = Nevow.Athena.Widget.subclass('Numbler.MyAccount');

Numbler.ManageMemberList.methods(
//Numbler.ManageMemberList.prototype = {
  function __init__(self,widgetNode) {
    Numbler.mymembercount += 1;
    Numbler.ManageMemberList.upcall(self,"__init__",widgetNode);
  },
  function dodelete(self) {
    self.callRemote('deleteMembership').addCallback(bind(self.afterdelete,self));
  },
  function afterdelete(self) {
    self.node.parentNode.removeChild(self.node);
    Numbler.mymembercount = Math.max(0,Numbler.mymembercount -1 );
    renderTitlesOnLoad();
  }
);


Numbler.CreateAccount = Nevow.Athena.Widget.subclass('Numbler.CreateAccount');

Numbler.CreateAccount.methods(
//Numbler.CreateAccount.prototype = {
  function __init__(self,widgetNode) {
    Numbler.CreateAccount.upcall(self, "__init__",widgetNode);
    
    connect($('emailinput'),'onblur',self,'checkemail');
    connect($('password2'),'onblur',self,'checkpasswd');
    connect($('processform'),'onclick',self,'processform');
    $('langselect').selectedIndex = 79; // en_US
    $('tzselect').selectedIndex = 8; // CST
    Nevow.Athena.notifyOnDisconnect(bind(self.ondisconnect,self));
  },
  function ondisconnect(self,failure) {
    alert('connection to the server lost.');
    history.go(0);
  },
  function checkemail(self) {
    var emailval = $('emailinput').value;
    if(emailval.length) {
      d = self.callRemote('validateEmail',emailval);
      d.addCallback(bind(self.aftermailcheck,self));
    }
  },
  function setErrorMsg(self,msg) {
    var el = $('error');
    el.style.backgroundColor = "#ecf2a7";
    el.innerHTML = msg;
  },
  function clearErrorMsg(self) {
    var el = $('error');
    el.style.backgroundColor = "white";
    el.innerHTML = '';
  },
  function aftermailcheck(self,args) {
    if(args['error'] == 'badaddr') {
      self.setErrorMsg('invalid email address');
    }
    else if(args['error'] == 'exists') {
      self.setErrorMsg('account already exists');
    }
    else if(args['error'] == 'dnfailure') {
      self.setErrorMsg(args['dn'] + ' does not exist');
    }
    else {
      self.clearErrorMsg();
    }
  },
  function checkpasswd(self) {
    if($('password1').value != $('password2').value) {
      self.setErrorMsg('passwords do not match');
      return false;
    }
    return true;
  },
  function formvalidation(self) {
    var email = $('emailinput');
    if(!email.value.length) {
      self.setErrorMsg('email address required');
      return false;
    }
    if(!$('password1').value.length) {
      self.setErrorMsg('password required');
      return false;
    }
    if(!self.checkpasswd()) {
      return false;
    }
    if(!$('nick').value.length) {
      self.setErrorMsg('user name required');
      return false;
    }
    return true;
  },

  function processform(self,ev) {
    ev.stop();
    if(!self.formvalidation()) {
      return false;
    }
    var d = self.callRemote('createAccount',$('emailinput').value,$('password1').value,$('nick').value,
			    $('langselect').value,$('tzselect').value);
    d.addCallback(bind(self.afterprocess,self));
    d.addErrback(bind(self.processerror,self));


    return false;
  },
  function afterprocess(self,result) {
    if(result.error == 'exists') {
      self.setErrorMsg('account already exists');
    }
    else if(result.error == 'oldsheets') {
      Nevow.Athena.sendClose();
      showElement($('aftercreate'));
      hideElement($('createaccount'));
      
      listdiv = UL(null,null);
      forEach(result.sheetlist,function(x) { listdiv.appendChild(LI(null,x)); });
      var pending = $('listpendingsheets');
      pending.appendChild(listdiv);
      showElement(pending);
    }
    else if(result.error == 'none') {
      Nevow.Athena.sendClose();
      showElement($('aftercreate'));
      hideElement($('createaccount'));
    }
  },
  function processerror(self,failure) {
    self.setErrorMsg('An error occurred creating your account.  please try later.');
  }
);


Numbler.ModifyAccount = Numbler.CreateAccount.subclass('Numbler.ModifyAccount');

Numbler.ModifyAccount.methods(
//Numbler.CreateAccount.prototype = {
  function __init__(self,widgetNode,email,dispname,boguspasswd,langIndex,tzIndex) {
    Numbler.ModifyAccount.upcall(self, "__init__",widgetNode);
    showElement($('modifyaccintro'));
    hideElement($('createaccintro'));
    $('emailinput').value = email;
    $('nick').value = dispname;
    $('password1').value = boguspasswd;
    $('password2').value = boguspasswd;
    $('langselect').selectedIndex = langIndex;
    $('tzselect').selectedIndex = tzIndex;
  },
  function processform(self,ev) {
    ev.stop();
    if(!self.formvalidation()) {
      return;
    }
    var d= self.callRemote('modifyAccount',$('emailinput').value,$('password1').value,
			   $('nick').value,$('langselect').value,$('tzselect').value)
    d.addCallback(bind(self.afterprocess,self));
    d.addErrback(bind(self.processerror,self));
  },
  function processerror(self,failure) {
    self.setErrorMsg('An error occurred while changing your account settings.  Please try again later.');
  },
  function afterprocess(self,result) {
    if(result.error == 'exists') {
      self.setErrorMsg('account already exists');
    }
    else if(result.error == 'emailchange') {
      Nevow.Athena.sendClose();
      hideElement($('createaccount'));
      showElement($('emailchanged'));
    }
    else if(result.error == 'none') {
      Nevow.Athena.sendClose();
      hideElement($('createaccount'));
      showElement($('accChanged'));
    }
  }
  );
