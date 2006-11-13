/* Copyright (C) 2006 Numbler LLC */
/* See LICENSE for details. */


LiveSheet.emailInvite = function() {
  this.invitelink = getElement('invitelink');
  this.inviteButton = getElement('invitebutton');
  this.inputForm = getElement('invitetext');

  if(this.invitelink) {
    dojo.event.connect(this.invitelink,'onclick',this,'openInvite');
  }

  this.dlg = dojo.widget.manager.getWidgetById('invitedlg');
  this.dlg.setCloseControl(getElement('canceldlg'));
  dojo.event.connect(this.inputForm,'onclick',this,'clearInvite');
  dojo.event.connect(this.inviteButton,'onclick',this,'onInvite');
  dojo.event.connect(getElement('inviteform'),'onsubmit',this,'onFormInvite');

};

LiveSheet.emailInvite.prototype = {
  openInvite:function(ev) {
    var errordiv = $('badinvitediv');
    errordiv.style.backgroundColor = '';
    errordiv.innerHTML = '&nbsp;';
    this.inputForm.value = 'enter email address'
    this.dlg.show();
    dojo.event.browser.stopEvent(ev);
    return false;
  },
  clearInvite:function() {
    this.inputForm.value = '';
  },
  onInvite:function() {
    var d = sheetServer.callRemote('sendEmailInvite',this.inputForm.value);
    d.addCallback(bind(this.afterInvite,this));
    d.addErrback(bind(this.inviteError,this));
  },
  showError:function(msg) {
    var errbox = $('badinvitediv');
    errbox.style.backgroundColor = '#ecf2a7';
    errbox.innerHTML = msg;
  },
  afterInvite:function(args) {
    if(args.error == 'badaddress') {
      this.showError('bad email address');
    }
    else if(args.error == 'selfinvite') {
      this.showError('you are already a member!');
    }
    else if(args.error == 'duplicate') {
      this.showError('already a member');
    }
    else {
      this.dlg.hide();
    }
  },
  inviteError:function(error) {
    this.dlg.hide();
  },
  onFormInvite:function(ev) {
    this.onInvite();
    dojo.event.browser.stopEvent(ev);    
    return false;
  }
};
