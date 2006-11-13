/* Copyright (C) 2006 Numbler LLC */
/* See LICENSE for details. */

if(typeof(LiveSheet) == 'undefined') {
  LiveSheet = {};
 };

LiveSheet.chat = function() {
  this.defshow = null;
  this.fh = null; // fadehandle
  this.th = null; // timerhandler for setTimeout1

  var ca = getElement('chattextarea');

  var pthis = this;
  this.focused = false;
  dojo.event.connect(ca,'onfocus',function() {
                       pthis.focused = true;
                     });
  dojo.event.connect(ca,'onblur',function() {
                       pthis.focused = false;
                     });
  this.visible = false;
  self.myusername = '';
};

LiveSheet.chat.prototype = {
  submitMessage:function() {
        var ca = getElement('chattextarea');
        sheetServer.callRemote('chatsubmit',ca.value).addCallback(bind(this.messageFromMe,this));
        ca.value = '';
        return false;
  },
  messageFromMe:function(args) {
        var tm = args[0];
        var val = args[1];
        var msg = DIV(null,
                                  DIV({'class':'useridself'},self.myusername),
                                  DIV({'class':'message'},val));
        getElement('chatarea').appendChild(msg);
    this.scrollchat();
  },
  addnew:function(timestamp,username,chatvalue) {
    var newmessage = DIV(null, // {'style':'Display:None;'},
                         DIV({'class':'userid'},username),
                         DIV({'class':'message'},chatvalue));
    getElement('chatarea').appendChild(newmessage);
  },
  newmessage:function(timestamp,username,chatvalue) {
    this.addnew(timestamp,username,chatvalue);
        if(!this.visible) {
          LiveSheet.Sheetbar.enableChatBubble();
        }
    this.scrollchat();
  },
  startFade:function() {
        if(this.fh) {
          this.fh.stop();
          this.fh = null;
        }
        if(this.th) {
          clearTimeout(this.th);
          this.th = null;
        }
        this.fh = dojo.fx.html.fade(getElement('statusupdate'),
                                    300,0,1,bind(this.waitFade,this));
  },
  waitFade:function(el) {
        this.fh = null;
        this.th = setTimeout(bind(this.stopFade,this),3000);
  },
  stopFade:function(el) {
        this.th = null;
        this.fh = dojo.fx.html.fade(getElement('statusupdate'),
                                    300,1,0,bind(this.onStopFade,this));
  },
  onStopFade:function() {
        this.fh = null;
  },
  onjoin:function(timestamp,username) {
    var newmessage = DIV(null, // {'style':'Display:None;'},
                         DIV({'class':'userjoin'},['*** ',username,' has joined'].join('')));
    getElement('chatarea').appendChild(newmessage);
    var el = getElement('statusupdate');
    el.innerHTML = username + ' joined';
    this.startFade(el);
  },
  onleave:function(timestamp,username) {
    getElement('chatarea').appendChild(DIV({'class':'userjoin'},
                                           ['*** ',username,' has left'].join('')));
    var el = getElement('statusupdate');
    el.innerHTML = username + ' left';
    this.startFade(el);
  },
  loadOld:function(args) {
    log('loading chat history')
    var history = args[0];
    log('items of history:',history.length)
    for(var i=0;i<history.length;i++) {
      var m = history[i];
      this.addnew(m.ts,m.u,m.c);
    }
        var current = args[1];
        if(current.length > 0) {
          getElement('chatarea').appendChild(DIV({'class':'userjoin'},
                                                 current.join(',') + ' currently connected'));
        }
    self.myusername = args[2];
    this.scrollchat();
  },
  scrollchat:function() {
    el = getElement('chatarea');
    el.scrollTop = el.scrollHeight - el.clientHeight;
  }
};
