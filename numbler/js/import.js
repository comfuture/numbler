/* Copyright (C) 2006 Numbler LLC */
/* See LICENSE for details. */

NumblerImport = {};

NumblerImport.importTools = function() {
  this.state = 0;
  this.sc =getElement('statuscontainer');
};

NumblerImport.importTools.prototype = {
  onStartServerImport:function() {
        document.body.style.cursor = 'wait';
  },
  onEndServerImport:function() {
        Nevow.Athena.sendClose();
        document.body.style.cursor = '';
  },
  addMsg:function(text) {
        getElement('statuscontainer').appendChild(DIV({'class':'importstatus'},text));
  },
  addMsgFailure:function(text) {
        getElement('statuscontainer').appendChild(DIV({'class':'importfailure'},text));
        this.onEndServerImport();
  },
  startParse:function() {
        this.onStartServerImport();
        this.addMsg('parsing file...');
  },
  endParse:function(success) {
        if(success) {
          this.addMsg('file loaded.');
        }
        else {
          this.addMsgFailure('Numbler was unable to read the file.');
        }
        document.body.style.cursor = '';   
  },
  addWarnings:function(warnlist) {
        var sc = getElement('statuscontainer');
        this.addMsg('Numbler encountered some warnings while importing your spreadsheet:');
        var wh = UL({'id':'importwarnheader'});
        for(var i=0;i<warnlist.length;i++) {
          wh.appendChild(LI({'class':'importwarn'},warnlist[i]));
        }
        sc.appendChild(wh);
  },
  newSheet:function(URL,sheetname,moresheets) {
        getElement('statuscontainer').appendChild(DIV({'id':'gensuccess'},
                                                        'Your new spreadsheet ',
                                                        A({'href':URL},sheetname),
                                                      ' is now ready.',
                                                      P(null,'You can manage your sheet permissions from your account page.')));
        if(document.body.clientHeight) {
          document.body.style.height = (document.body.clientHeight) + "px";
        }
        else if(window.innerHeight) {
          document.body.style.height = window.innerHeight + "px";
        }
        if(!moresheets) {
          this.onEndServerImport();
        }
  },
  newSheetName:function(suggestedName) {
        var askform = FORM({'action':''},INPUT({'type':'text','id':'sheetnameinput','value':suggestedName}),
                                           SPAN({'style':{'paddingLeft':'10px'}},
                                                        INPUT({'type':'submit','name':'asksubmit','value':'continue'})));
    getElement('statuscontainer').appendChild(DIV({'id':'multisheets'},
                                                                                                  P(null,'Please enter the name of the spreadsheet:'),
                                                                                                  askform));
        askform.onsubmit = bind(this.onsheetnamesubmit,this);
        this.namedeferred = new MochiKit.Async.Deferred();
        this.askform = askform;
        return this.namedeferred;
  },
  onsheetnamesubmit:function() {
        this.namedeferred.callback(getElement('sheetnameinput').value);
        this.askform.onsubmit = null;
        getElement('sheetnameinput').disabled = true;
        this.namedeferred = null;
        return false;
  },
  multiSheets:function(sheetNames) {
        var cont = DIV({'id':'multisheets'});
        var askform = FORM({'action':''},DIV(null,'Your file contains multiple spreadsheets.  Which ones would you like to import?'));
        cont.appendChild(askform);
        forEach(sheetNames,function(sheetname) {
                          askform.appendChild(DIV(null,INPUT({'type':'checkbox','name':'sheetcheck','value':sheetname,
                                                                                                         'class':'sheetcheck','checked':'1'}),
                                                                          SPAN(null,sheetname)));
                        });
        askform.appendChild(DIV({'style':{'marginTop':'10px'}},
                                                        INPUT({'type':'submit','value':'continue'})));
        askform.onsubmit = bind(this.onmultisheetask,this);
        this.askform = askform;
        getElement('statuscontainer').appendChild(cont);
        this.multisheetdef = new MochiKit.Async.Deferred();
        return this.multisheetdef;
  },
  onmultisheetask:function() {
        if(this.multisheetdef) {
          var contents = getElementsByTagAndClassName('input','sheetcheck',this.askform);
          var results = [];
          for(var i=0;i<contents.length;i++) {
                contents[i].disabled = true;
                results.push([contents[i].value,contents[i].checked]);
          }
          this.multisheetdef.callback(results);
          this.multisheetdef = null;
          if(results.length) {
                this.onStartServerImport();
          }
        }
        return false;
  },
  noSheetsSelected:function() {
        getElement('statuscontainer').appendChild(DIV(null,'No spreadsheets selected.  here is a link to the ',
                                                                                                  A({'href':"/"},'home page.')));
        this.onEndServerImport();
  }
};

importTools = new NumblerImport.importTools();
