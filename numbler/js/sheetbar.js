/* Copyright (C) 2006 Numbler LLC */
/* See LICENSE for details. */

if(typeof(LiveSheet) == 'undefined') {
  LiveSheet = {};
 };

dojo.hostenv.setModulePrefix('LiveSheet','../LiveSheet');
dojo.widget.manager.registerWidgetPackage('LiveSheet');
dojo.require('LiveSheet.undodropdown');


LiveSheet.Sheetbar = {};

function img(name) {
  return ("img/buttons/" + name + ".gif").toString();
}

function imgPNG(name) {
  return ("img/buttons/" + name + ".png").toString();
}

LiveSheet.Sheetbar.tb = null;
LiveSheet.Sheetbar.chat = null;

LiveSheet.Sheetbar.create = function(parent) {
  tc = dojo.widget.createWidget("ToolbarContainer");
  parent.appendChild(tc.domNode);
  tb = dojo.widget.createWidget("Toolbar");
  LiveSheet.Sheetbar.tb = tb;
  tc.addChild(tb);

  var bg = dojo.widget.createWidget("ToolbarButtonGroup", {
    name: "justify",
                                      defaultButton: "justifyleft",
                                      preventDeselect: true
                                      });

  LiveSheet.Sheetbar.bg = bg;
  var jl = new Image();
  jl.src = img("justifyleft");

  bg.addChild(jl);
  bg.addChild(img("justifycenter"));
  bg.addChild(img("justifyright"));
  bg.addChild(img("justifyfull"));

  var expand = new Image();
  expand.src = img("expand");
  var backcolor = new Image();
  backcolor.src = img("backcolor");
  var forecolor = new Image();
  forecolor.src = img("forecolor");

  var items = [img("bold"), 
               img("italic"), 
               img("underline"),
               "|", 
               dojo.widget.createWidget("ToolbarColorDialog", 
                                                                        {toggleItem: true, icon: new dojo.widget.Icon(backcolor)}), 
               dojo.widget.createWidget("ToolbarColorDialog", 
                                                                        {toggleItem: true, icon: new dojo.widget.Icon(forecolor)}),
               "|", bg, 
               //"|", img("createlink"), img("insertimage"),
               //"|", img("indent"), img("outdent"),
               //img("insertorderedlist"), img("insertunorderedlist"),
               "|", 
               img("undo"), 
               dojo.widget.createWidget("undodropdown",
                                      {toggleItem:true,name:'undodrop',actionstr:"Undo ",
                                                  icon:new dojo.widget.Icon(expand,expand,expand,expand)}),
               img("redo"),
               dojo.widget.createWidget("undodropdown",
                                      {toggleItem:true,name:'redodrop',actionstr:"Redo ",
                                                  icon:new dojo.widget.Icon(expand,expand,expand,expand)}),
                   "|",
                   img("dollar"),
                   img("percent"),
                   img("comma"),
                   "|",
                   img("cigma"), 
                   img("sortup"),
                   img("sortdown"),
                   "|",
                   img("chat"),img("chat_bubble")
               ];
  for(var i = 0; i < items.length; i++) {
    tb.addChild(items[i], null, {toggleItem:i<3});
  }
  tb.getItem('chat').setToggleItem(true);
  var bubble = tb.getItem('chat_bubble');
  LiveSheet.Sheetbar.chat = bubble;
  bubble._onmouseover = bubble._onmouseout = bubble._onmouseout = bubble._onmousedown = bubble._onmouseup = null;
  LiveSheet.Sheetbar.disableChatBubble();
};

LiveSheet.Sheetbar.disableChatBubble = function() {
  LiveSheet.Sheetbar.chat.domNode.style.display = "none";
};
LiveSheet.Sheetbar.enableChatBubble = function() {
  LiveSheet.Sheetbar.chat.domNode.style.display = "block";
}


LiveSheet.Sheetbar.wireHandlers = function(sheet,undoManager) {

  var bg = LiveSheet.Sheetbar.bg;
  var tb =   LiveSheet.Sheetbar.tb;

  // add titles to all of the images to enable tooltip support.
  bgtooltip = [{'tb':'justifyleft','tt':'justify left'},
        {'tb':'justifycenter','tt':'justify center'},
        {'tb':'justifyright','tt':'justify right'},
        {'tb':'justifyfull','tt':'justify full'}
                           ];

  tbtooltip = [{'tb':'backcolor','tt':'background color'},
        {'tb':'forecolor','tt':'foreground color'},
        {'tb':'bold','tt':'bold'},
        {'tb':'italic','tt':'italics'},
        {'tb':'underline','tt':'underline'},
        {'tb':'undo','tt':'undo'},
        {'tb':'redo','tt':'redo'},
        {'tb':'dollar','tt':'format as currency'},
        {'tb':'percent','tt':'format as percent'},
        {'tb':'comma','tt':'Comma style'},
        {'tb':'sortup','tt':'Sort Ascending'},
        {'tb':'sortdown','tt':'Sort Descending'},
        {'tb':'chat_bubble','tt':'new message'},
        {'tb':'cigma','tt':'auto-sum'},
                           ]

  setTitle = function(currentbar,item) {
        currentbar.getItem(item.tb).getIcon().getNode().title = item.tt;
  }
  forEach(bgtooltip,partial(setTitle,bg));
  forEach(tbtooltip,partial(setTitle,tb));


  // wire up the event handlers
  dojo.event.connect(tb.getItem('bold'),'onSelect',bind(partial(sheet.onBold,true),sheet));
  dojo.event.connect(tb.getItem('bold'),'onDeselect',bind(partial(sheet.onBold,false),sheet));
  dojo.event.connect(tb.getItem('italic'),'onSelect',bind(partial(sheet.onItalic,true),sheet));
  dojo.event.connect(tb.getItem('italic'),'onDeselect',bind(partial(sheet.onItalic,false),sheet));
  dojo.event.connect(tb.getItem('underline'),'onSelect',bind(partial(sheet.onUnderline,true),sheet));
  dojo.event.connect(tb.getItem('underline'),'onDeselect',bind(partial(sheet.onUnderline,false),sheet));
  dojo.event.connect(bg,'onSelect',bind(sheet.onJustify,sheet));
  dojo.event.connect(tb.getItem('backcolor'),'onSetValue',bind(sheet.onBgColor,sheet));
  dojo.event.connect(tb.getItem('forecolor'),'onSetValue',bind(sheet.onFontColor,sheet));
  dojo.event.connect(tb.getItem('dollar'),'onClick',bind(partial(sheet.onCurrencyStyle,'$'),sheet));
  dojo.event.connect(tb.getItem('percent'),'onClick',bind(partial(sheet.onCurrencyStyle,'%'),sheet));
  dojo.event.connect(tb.getItem('comma'),'onClick',bind(partial(sheet.onCurrencyStyle,','),sheet));
  dojo.event.connect(tb.getItem('sortup'),'onClick',bind(partial(sheet.doSort,'asc'),sheet));
  dojo.event.connect(tb.getItem('sortdown'),'onClick',bind(partial(sheet.doSort,'desc'),sheet));

  dojo.event.connect(tb.getItem('cigma'),'onClick',function() {
                                           var fl = currentsheet.mousetrack.floater;
                                           if(fl && fl.visible) {
                                                 fl.doFormulaGen('Sum');
                                           }
                                         });

        
  //undo support
  dojo.event.connect(tb.getItem('undo'),'onClick',bind(partial(undoManager.undo,1),undoManager));
  dojo.event.connect(tb.getItem('redo'),'onClick',bind(partial(undoManager.redo,1),undoManager));

  dojo.event.connect(undoManager,'pushundo',tb.getItem('undodrop'),'addUndo');
  dojo.event.connect(undoManager,'popundo',tb.getItem('undodrop'),'removeUndo');
  dojo.event.connect(undoManager,'shiftundo',tb.getItem('undodrop'),'shiftUndo');
  dojo.event.connect(undoManager,'pushredo',tb.getItem('redodrop'),'addUndo');
  dojo.event.connect(undoManager,'popredo',tb.getItem('redodrop'),'removeUndo');

  dojo.event.connect(tb.getItem('undodrop'),'onMultipleUndo',function(widget,count) {
                       undoManager.undo(count);
                     });
  dojo.event.connect(tb.getItem('redodrop'),'onMultipleUndo',function(widget,count) {
                       undoManager.redo(count);
                     });

  // for each toolbar dialog object hook the showdialog and hideDialog to do the right thing with the 
  // mouse.  the Dojo toolbar functionality registers a mousedown handler with the document
  // whenever a dialog is open so that a mousedown will close the dialog.  However, because we
  // intercept these events in the sheet we need to manually register our mouse events with 
  // each dialog.
  var tbdialogs = ['backcolor','forecolor','undodrop','redodrop'];
  var divlist = ['mainbody','colcontainer','rowcontainer'];
  for(var i=0;i<tbdialogs.length;i++) {
    var func = partial(function(reglist,dialogname) {
                         var dialog = LiveSheet.Sheetbar.tb.getItem(dialogname);
                         for(var i =0;i<reglist.length;i++) {
                           dojo.event.connect(getElement(reglist[i]),'onmousedown',dialog,'deselect');
                         }
                       },divlist,tbdialogs[i]);
                
    var disfunc = partial(function(reglist,dialogname) {
                            var dialog = LiveSheet.Sheetbar.tb.getItem(dialogname);
                            for(var i =0;i<reglist.length;i++) {
                              dojo.event.disconnect(getElement(reglist[i]),'onmousedown',dialog,'deselect');
                            }
                          },divlist,tbdialogs[i]);
    dojo.event.connect(tb.getItem(tbdialogs[i]),'onSelect',func);
    dojo.event.connect(tb.getItem(tbdialogs[i]),'onDeselect',disfunc);
  }
  // chat support
  var tbchat = tb.getItem('chat');
  dojo.event.connect(tbchat,'onSelect',sheet,'toggleContainer');
  dojo.event.connect(tbchat,'onDeselect',sheet,'toggleContainer');
  dojo.event.connect(tb.getItem('chat_bubble'),'onClick',function() {
                                           tbchat.select();  // passthrough to the chat icon event
                                         });
};

LiveSheet.Sheetbar.updateState = function(sb) {
  // sb = styleBuilder.  Note that we don't fire the event in these cases to avoid firing 
  // our own handlers.
  var tb = LiveSheet.Sheetbar.tb;
  tb.getItem('bold').setSelected((sb && sb.exists('font-weight')) || false,false,true);
  tb.getItem('italic').setSelected((sb && sb.exists('font-style')) || false,false,true);
  tb.getItem('underline').setSelected((sb && sb.exists('text-decoration')) || false,false,true);

  var bg = tb.getItem('justify');
  if(sb) {
    var value = sb.getTextAlign();
    switch(value) {
    case 'left': bg.select('justifyleft',false,true); break;
    case 'right':bg.select('justifyright',false,true); break;
    case 'center':bg.select('justifycenter',false,true); break;
    case 'justify':bg.select('justifyfull',false,true); break;
    };
  }
  else {
    bg.select(bg.defaultButton,false,true);
  }
};
LiveSheet.Sheetbar.setUndoCount = function(val) {
  var command = val ? 'enable' : 'disable';
  tb.getItem('undo')[command]();
  tb.getItem('undodrop')[command]();
};
LiveSheet.Sheetbar.setRedoCount = function(val) {
  var command = val ? 'enable' : 'disable';
  tb.getItem('redo')[command]();
  tb.getItem('redodrop')[command]();
};
LiveSheet.Sheetbar.disableUndo = function() {
  with(LiveSheet.Sheetbar) {
    setUndoCount(0); setRedoCount(0); 
  }
};

