/*
	This is a compiled version of Dojo, built for deployment and not for
	development. To get an editable version, please visit:

		http://dojotoolkit.org

	for documentation and information on getting the source.
*/

var dj_global=this;
function dj_undef(_1,_2){
if(!_2){
_2=dj_global;
}
return (typeof _2[_1]=="undefined");
}
if(dj_undef("djConfig")){
var djConfig={};
}
var dojo;
if(dj_undef("dojo")){
dojo={};
}
dojo.version={major:0,minor:2,patch:1,flag:"+",revision:Number("$Rev: 2579 $".match(/[0-9]+/)[0]),toString:function(){
with(dojo.version){
return major+"."+minor+"."+patch+flag+" ("+revision+")";
}
}};
dojo.evalObjPath=function(_3,_4){
if(typeof _3!="string"){
return dj_global;
}
if(_3.indexOf(".")==-1){
if((dj_undef(_3,dj_global))&&(_4)){
dj_global[_3]={};
}
return dj_global[_3];
}
var _5=_3.split(/\./);
var _6=dj_global;
for(var i=0;i<_5.length;++i){
if(!_4){
_6=_6[_5[i]];
if((typeof _6=="undefined")||(!_6)){
return _6;
}
}else{
if(dj_undef(_5[i],_6)){
_6[_5[i]]={};
}
_6=_6[_5[i]];
}
}
return _6;
};
dojo.errorToString=function(_8){
return ((!dj_undef("message",_8))?_8.message:(dj_undef("description",_8)?_8:_8.description));
};
dojo.raise=function(_9,_a){
if(_a){
_9=_9+": "+dojo.errorToString(_a);
}
var he=dojo.hostenv;
if((!dj_undef("hostenv",dojo))&&(!dj_undef("println",dojo.hostenv))){
dojo.hostenv.println("FATAL: "+_9);
}
throw Error(_9);
};
dj_throw=dj_rethrow=function(m,e){
dojo.deprecated("dj_throw and dj_rethrow deprecated, use dojo.raise instead");
dojo.raise(m,e);
};
dojo.debug=function(){
if(!djConfig.isDebug){
return;
}
var _e=arguments;
if(dj_undef("println",dojo.hostenv)){
dojo.raise("dojo.debug not available (yet?)");
}
var _f=dj_global["jum"]&&!dj_global["jum"].isBrowser;
var s=[(_f?"":"DEBUG: ")];
for(var i=0;i<_e.length;++i){
if(!false&&_e[i] instanceof Error){
var msg="["+_e[i].name+": "+dojo.errorToString(_e[i])+(_e[i].fileName?", file: "+_e[i].fileName:"")+(_e[i].lineNumber?", line: "+_e[i].lineNumber:"")+"]";
}else{
try{
var msg=String(_e[i]);
}
catch(e){
if(dojo.render.html.ie){
var msg="[ActiveXObject]";
}else{
var msg="[unknown]";
}
}
}
s.push(msg);
}
if(_f){
jum.debug(s.join(" "));
}else{
dojo.hostenv.println(s.join(" "));
}
};
dojo.debugShallow=function(obj){
if(!djConfig.isDebug){
return;
}
dojo.debug("------------------------------------------------------------");
dojo.debug("Object: "+obj);
for(i in obj){
dojo.debug(i+": "+obj[i]);
}
dojo.debug("------------------------------------------------------------");
};
var dj_debug=dojo.debug;
function dj_eval(s){
return dj_global.eval?dj_global.eval(s):eval(s);
}
dj_unimplemented=dojo.unimplemented=function(_15,_16){
var _17="'"+_15+"' not implemented";
if((!dj_undef(_16))&&(_16)){
_17+=" "+_16;
}
dojo.raise(_17);
};
dj_deprecated=dojo.deprecated=function(_18,_19,_1a){
var _1b="DEPRECATED: "+_18;
if(_19){
_1b+=" "+_19;
}
if(_1a){
_1b+=" -- will be removed in version: "+_1a;
}
dojo.debug(_1b);
};
dojo.inherits=function(_1c,_1d){
if(typeof _1d!="function"){
dojo.raise("superclass: "+_1d+" borken");
}
_1c.prototype=new _1d();
_1c.prototype.constructor=_1c;
_1c.superclass=_1d.prototype;
_1c["super"]=_1d.prototype;
};
dj_inherits=function(_1e,_1f){
dojo.deprecated("dj_inherits deprecated, use dojo.inherits instead");
dojo.inherits(_1e,_1f);
};
dojo.render=(function(){
function vscaffold(_20,_21){
var tmp={capable:false,support:{builtin:false,plugin:false},prefixes:_20};
for(var x in _21){
tmp[x]=false;
}
return tmp;
}
return {name:"",ver:dojo.version,os:{win:false,linux:false,osx:false},html:vscaffold(["html"],["ie","opera","khtml","safari","moz"]),svg:vscaffold(["svg"],["corel","adobe","batik"]),vml:vscaffold(["vml"],["ie"]),swf:vscaffold(["Swf","Flash","Mm"],["mm"]),swt:vscaffold(["Swt"],["ibm"])};
})();
dojo.hostenv=(function(){
var _24={isDebug:false,allowQueryConfig:false,baseScriptUri:"",baseRelativePath:"",libraryScriptUri:"",iePreventClobber:false,ieClobberMinimal:true,preventBackButtonFix:true,searchIds:[],parseWidgets:true};
if(typeof djConfig=="undefined"){
djConfig=_24;
}else{
for(var _25 in _24){
if(typeof djConfig[_25]=="undefined"){
djConfig[_25]=_24[_25];
}
}
}
var djc=djConfig;
function _def(obj,_28,def){
return (dj_undef(_28,obj)?def:obj[_28]);
}
return {name_:"(unset)",version_:"(unset)",pkgFileName:"__package__",loading_modules_:{},loaded_modules_:{},addedToLoadingCount:[],removedFromLoadingCount:[],inFlightCount:0,modulePrefixes_:{dojo:{name:"dojo",value:"src"}},setModulePrefix:function(_2a,_2b){
this.modulePrefixes_[_2a]={name:_2a,value:_2b};
},getModulePrefix:function(_2c){
var mp=this.modulePrefixes_;
if((mp[_2c])&&(mp[_2c]["name"])){
return mp[_2c].value;
}
return _2c;
},getTextStack:[],loadUriStack:[],loadedUris:[],post_load_:false,modulesLoadedListeners:[],getName:function(){
return this.name_;
},getVersion:function(){
return this.version_;
},getText:function(uri){
dojo.unimplemented("getText","uri="+uri);
},getLibraryScriptUri:function(){
dojo.unimplemented("getLibraryScriptUri","");
}};
})();
dojo.hostenv.getBaseScriptUri=function(){
if(djConfig.baseScriptUri.length){
return djConfig.baseScriptUri;
}
var uri=new String(djConfig.libraryScriptUri||djConfig.baseRelativePath);
if(!uri){
dojo.raise("Nothing returned by getLibraryScriptUri(): "+uri);
}
var _30=uri.lastIndexOf("/");
djConfig.baseScriptUri=djConfig.baseRelativePath;
return djConfig.baseScriptUri;
};
dojo.hostenv.setBaseScriptUri=function(uri){
djConfig.baseScriptUri=uri;
};
dojo.hostenv.loadPath=function(_32,_33,cb){
if((_32.charAt(0)=="/")||(_32.match(/^\w+:/))){
dojo.raise("relpath '"+_32+"'; must be relative");
}
var uri=this.getBaseScriptUri()+_32;
if(djConfig.cacheBust&&dojo.render.html.capable){
uri+="?"+djConfig.cacheBust.replace(/\W+/g,"");
}
try{
return ((!_33)?this.loadUri(uri,cb):this.loadUriAndCheck(uri,_33,cb));
}
catch(e){
dojo.debug(e);
return false;
}
};
dojo.hostenv.loadUri=function(uri,cb){
if(dojo.hostenv.loadedUris[uri]){
return;
}
var _38=this.getText(uri,null,true);
if(_38==null){
return 0;
}
var _39=dj_eval(_38);
return 1;
};
dojo.hostenv.loadUriAndCheck=function(uri,_3b,cb){
var ok=true;
try{
ok=this.loadUri(uri,cb);
}
catch(e){
dojo.debug("failed loading ",uri," with error: ",e);
}
return ((ok)&&(this.findModule(_3b,false)))?true:false;
};
dojo.loaded=function(){
};
dojo.hostenv.loaded=function(){
this.post_load_=true;
var mll=this.modulesLoadedListeners;
for(var x=0;x<mll.length;x++){
mll[x]();
}
dojo.loaded();
};
dojo.addOnLoad=function(obj,_41){
if(arguments.length==1){
dojo.hostenv.modulesLoadedListeners.push(obj);
}else{
if(arguments.length>1){
dojo.hostenv.modulesLoadedListeners.push(function(){
obj[_41]();
});
}
}
};
dojo.hostenv.modulesLoaded=function(){
if(this.post_load_){
return;
}
if((this.loadUriStack.length==0)&&(this.getTextStack.length==0)){
if(this.inFlightCount>0){
dojo.debug("files still in flight!");
return;
}
if(typeof setTimeout=="object"){
setTimeout("dojo.hostenv.loaded();",0);
}else{
dojo.hostenv.loaded();
}
}
};
dojo.hostenv.moduleLoaded=function(_42){
var _43=dojo.evalObjPath((_42.split(".").slice(0,-1)).join("."));
this.loaded_modules_[(new String(_42)).toLowerCase()]=_43;
};
dojo.hostenv._global_omit_module_check=false;
dojo.hostenv.loadModule=function(_44,_45,_46){
_46=this._global_omit_module_check||_46;
var _47=this.findModule(_44,false);
if(_47){
return _47;
}
if(dj_undef(_44,this.loading_modules_)){
this.addedToLoadingCount.push(_44);
}
this.loading_modules_[_44]=1;
var _48=_44.replace(/\./g,"/")+".js";
var _49=_44.split(".");
var _4a=_44.split(".");
for(var i=_49.length-1;i>0;i--){
var _4c=_49.slice(0,i).join(".");
var _4d=this.getModulePrefix(_4c);
if(_4d!=_4c){
_49.splice(0,i,_4d);
break;
}
}
var _4e=_49[_49.length-1];
if(_4e=="*"){
_44=(_4a.slice(0,-1)).join(".");
while(_49.length){
_49.pop();
_49.push(this.pkgFileName);
_48=_49.join("/")+".js";
if(_48.charAt(0)=="/"){
_48=_48.slice(1);
}
ok=this.loadPath(_48,((!_46)?_44:null));
if(ok){
break;
}
_49.pop();
}
}else{
_48=_49.join("/")+".js";
_44=_4a.join(".");
var ok=this.loadPath(_48,((!_46)?_44:null));
if((!ok)&&(!_45)){
_49.pop();
while(_49.length){
_48=_49.join("/")+".js";
ok=this.loadPath(_48,((!_46)?_44:null));
if(ok){
break;
}
_49.pop();
_48=_49.join("/")+"/"+this.pkgFileName+".js";
if(_48.charAt(0)=="/"){
_48=_48.slice(1);
}
ok=this.loadPath(_48,((!_46)?_44:null));
if(ok){
break;
}
}
}
if((!ok)&&(!_46)){
dojo.raise("Could not load '"+_44+"'; last tried '"+_48+"'");
}
}
if(!_46){
_47=this.findModule(_44,false);
if(!_47){
dojo.raise("symbol '"+_44+"' is not defined after loading '"+_48+"'");
}
}
return _47;
};
dojo.hostenv.startPackage=function(_50){
var _51=_50.split(/\./);
if(_51[_51.length-1]=="*"){
_51.pop();
}
return dojo.evalObjPath(_51.join("."),true);
};
dojo.hostenv.findModule=function(_52,_53){
if(this.loaded_modules_[(new String(_52)).toLowerCase()]){
return this.loaded_modules_[_52];
}
var _54=dojo.evalObjPath(_52);
if((typeof _54!=="undefined")&&(_54)){
return _54;
}
if(_53){
dojo.raise("no loaded module named '"+_52+"'");
}
return null;
};
if(typeof window=="undefined"){
dojo.raise("no window object");
}
(function(){
if(djConfig.allowQueryConfig){
var _55=document.location.toString();
var _56=_55.split("?",2);
if(_56.length>1){
var _57=_56[1];
var _58=_57.split("&");
for(var x in _58){
var sp=_58[x].split("=");
if((sp[0].length>9)&&(sp[0].substr(0,9)=="djConfig.")){
var opt=sp[0].substr(9);
try{
djConfig[opt]=eval(sp[1]);
}
catch(e){
djConfig[opt]=sp[1];
}
}
}
}
}
if(((djConfig["baseScriptUri"]=="")||(djConfig["baseRelativePath"]==""))&&(document&&document.getElementsByTagName)){
var _5c=document.getElementsByTagName("script");
var _5d=/(__package__|dojo)\.js([\?\.]|$)/i;
for(var i=0;i<_5c.length;i++){
var src=_5c[i].getAttribute("src");
if(!src){
continue;
}
var m=src.match(_5d);
if(m){
root=src.substring(0,m.index);
if(!this["djConfig"]){
djConfig={};
}
if(djConfig["baseScriptUri"]==""){
djConfig["baseScriptUri"]=root;
}
if(djConfig["baseRelativePath"]==""){
djConfig["baseRelativePath"]=root;
}
break;
}
}
}
var dr=dojo.render;
var drh=dojo.render.html;
var dua=drh.UA=navigator.userAgent;
var dav=drh.AV=navigator.appVersion;
var t=true;
var f=false;
drh.capable=t;
drh.support.builtin=t;
dr.ver=parseFloat(drh.AV);
dr.os.mac=dav.indexOf("Macintosh")>=0;
dr.os.win=dav.indexOf("Windows")>=0;
dr.os.linux=dav.indexOf("X11")>=0;
drh.opera=dua.indexOf("Opera")>=0;
drh.khtml=(dav.indexOf("Konqueror")>=0)||(dav.indexOf("Safari")>=0);
drh.safari=dav.indexOf("Safari")>=0;
var _67=dua.indexOf("Gecko");
drh.mozilla=drh.moz=(_67>=0)&&(!drh.khtml);
if(drh.mozilla){
drh.geckoVersion=dua.substring(_67+6,_67+14);
}
drh.ie=(document.all)&&(!drh.opera);
drh.ie50=drh.ie&&dav.indexOf("MSIE 5.0")>=0;
drh.ie55=drh.ie&&dav.indexOf("MSIE 5.5")>=0;
drh.ie60=drh.ie&&dav.indexOf("MSIE 6.0")>=0;
dr.vml.capable=drh.ie;
dr.svg.capable=f;
dr.svg.support.plugin=f;
dr.svg.support.builtin=f;
dr.svg.adobe=f;
if(document.implementation&&document.implementation.hasFeature&&document.implementation.hasFeature("org.w3c.dom.svg","1.0")){
dr.svg.capable=t;
dr.svg.support.builtin=t;
dr.svg.support.plugin=f;
dr.svg.adobe=f;
}else{
if(navigator.mimeTypes&&navigator.mimeTypes.length>0){
var _68=navigator.mimeTypes["image/svg+xml"]||navigator.mimeTypes["image/svg"]||navigator.mimeTypes["image/svg-xml"];
if(_68){
dr.svg.adobe=_68&&_68.enabledPlugin&&_68.enabledPlugin.description&&(_68.enabledPlugin.description.indexOf("Adobe")>-1);
if(dr.svg.adobe){
dr.svg.capable=t;
dr.svg.support.plugin=t;
}
}
}else{
if(drh.ie&&dr.os.win){
var _68=f;
try{
var _69=new ActiveXObject("Adobe.SVGCtl");
_68=t;
}
catch(e){
}
if(_68){
dr.svg.capable=t;
dr.svg.support.plugin=t;
dr.svg.adobe=t;
}
}else{
dr.svg.capable=f;
dr.svg.support.plugin=f;
dr.svg.adobe=f;
}
}
}
})();
dojo.hostenv.startPackage("dojo.hostenv");
dojo.hostenv.name_="browser";
dojo.hostenv.searchIds=[];
var DJ_XMLHTTP_PROGIDS=["Msxml2.XMLHTTP","Microsoft.XMLHTTP","Msxml2.XMLHTTP.4.0"];
dojo.hostenv.getXmlhttpObject=function(){
var _6a=null;
var _6b=null;
try{
_6a=new XMLHttpRequest();
}
catch(e){
}
if(!_6a){
for(var i=0;i<3;++i){
var _6d=DJ_XMLHTTP_PROGIDS[i];
try{
_6a=new ActiveXObject(_6d);
}
catch(e){
_6b=e;
}
if(_6a){
DJ_XMLHTTP_PROGIDS=[_6d];
break;
}
}
}
if(!_6a){
return dojo.raise("XMLHTTP not available",_6b);
}
return _6a;
};
dojo.hostenv.getText=function(uri,_6f,_70){
var _71=this.getXmlhttpObject();
if(_6f){
_71.onreadystatechange=function(){
if((4==_71.readyState)&&(_71["status"])){
if(_71.status==200){
dojo.debug("LOADED URI: "+uri);
_6f(_71.responseText);
}
}
};
}
_71.open("GET",uri,_6f?true:false);
_71.send(null);
if(_6f){
return null;
}
return _71.responseText;
};
dojo.hostenv.defaultDebugContainerId="dojoDebug";
dojo.hostenv._println_buffer=[];
dojo.hostenv._println_safe=false;
dojo.hostenv.println=function(_72){
if(!dojo.hostenv._println_safe){
dojo.hostenv._println_buffer.push(_72);
}else{
try{
var _73=document.getElementById(djConfig.debugContainerId?djConfig.debugContainerId:dojo.hostenv.defaultDebugContainerId);
if(!_73){
_73=document.getElementsByTagName("body")[0]||document.body;
}
var div=document.createElement("div");
div.appendChild(document.createTextNode(_72));
_73.appendChild(div);
}
catch(e){
try{
document.write("<div>"+_72+"</div>");
}
catch(e2){
window.status=_72;
}
}
}
};
dojo.addOnLoad(function(){
dojo.hostenv._println_safe=true;
while(dojo.hostenv._println_buffer.length>0){
dojo.hostenv.println(dojo.hostenv._println_buffer.shift());
}
});
function dj_addNodeEvtHdlr(_75,_76,fp,_78){
var _79=_75["on"+_76]||function(){
};
_75["on"+_76]=function(){
fp.apply(_75,arguments);
_79.apply(_75,arguments);
};
return true;
}
dj_addNodeEvtHdlr(window,"load",function(){
if(dojo.render.html.ie){
dojo.hostenv.makeWidgets();
}
dojo.hostenv.modulesLoaded();
});
dojo.hostenv.makeWidgets=function(){
var _7a=[];
if(djConfig.searchIds&&djConfig.searchIds.length>0){
_7a=_7a.concat(djConfig.searchIds);
}
if(dojo.hostenv.searchIds&&dojo.hostenv.searchIds.length>0){
_7a=_7a.concat(dojo.hostenv.searchIds);
}
if((djConfig.parseWidgets)||(_7a.length>0)){
if(dojo.evalObjPath("dojo.widget.Parse")){
try{
var _7b=new dojo.xml.Parse();
if(_7a.length>0){
for(var x=0;x<_7a.length;x++){
var _7d=document.getElementById(_7a[x]);
if(!_7d){
continue;
}
var _7e=_7b.parseElement(_7d,null,true);
dojo.widget.getParser().createComponents(_7e);
}
}else{
if(djConfig.parseWidgets){
var _7e=_7b.parseElement(document.getElementsByTagName("body")[0]||document.body,null,true);
dojo.widget.getParser().createComponents(_7e);
}
}
}
catch(e){
dojo.debug("auto-build-widgets error:",e);
}
}
}
};
dojo.hostenv.modulesLoadedListeners.push(function(){
if(!dojo.render.html.ie){
dojo.hostenv.makeWidgets();
}
});
try{
if(dojo.render.html.ie){
document.write("<style>v:*{ behavior:url(#default#VML); }</style>");
document.write("<xml:namespace ns=\"urn:schemas-microsoft-com:vml\" prefix=\"v\"/>");
}
}
catch(e){
}
dojo.hostenv.writeIncludes=function(){
};
dojo.hostenv.byId=dojo.byId=function(id,doc){
if(typeof id=="string"||id instanceof String){
if(!doc){
doc=document;
}
return doc.getElementById(id);
}
return id;
};
dojo.hostenv.byIdArray=dojo.byIdArray=function(){
var ids=[];
for(var i=0;i<arguments.length;i++){
if((arguments[i] instanceof Array)||(typeof arguments[i]=="array")){
for(var j=0;j<arguments[i].length;j++){
ids=ids.concat(dojo.hostenv.byIdArray(arguments[i][j]));
}
}else{
ids.push(dojo.hostenv.byId(arguments[i]));
}
}
return ids;
};
dojo.hostenv.conditionalLoadModule=function(_84){
var _85=_84["common"]||[];
var _86=(_84[dojo.hostenv.name_])?_85.concat(_84[dojo.hostenv.name_]||[]):_85.concat(_84["default"]||[]);
for(var x=0;x<_86.length;x++){
var _88=_86[x];
if(_88.constructor==Array){
dojo.hostenv.loadModule.apply(dojo.hostenv,_88);
}else{
dojo.hostenv.loadModule(_88);
}
}
};
dojo.hostenv.require=dojo.hostenv.loadModule;
dojo.require=function(){
dojo.hostenv.loadModule.apply(dojo.hostenv,arguments);
};
dojo.requireAfter=dojo.require;
dojo.requireIf=function(){
if((arguments[0]===true)||(arguments[0]=="common")||(dojo.render[arguments[0]].capable)){
var _89=[];
for(var i=1;i<arguments.length;i++){
_89.push(arguments[i]);
}
dojo.require.apply(dojo,_89);
}
};
dojo.requireAfterIf=dojo.requireIf;
dojo.conditionalRequire=dojo.requireIf;
dojo.kwCompoundRequire=function(){
dojo.hostenv.conditionalLoadModule.apply(dojo.hostenv,arguments);
};
dojo.hostenv.provide=dojo.hostenv.startPackage;
dojo.provide=function(){
return dojo.hostenv.startPackage.apply(dojo.hostenv,arguments);
};
dojo.setModulePrefix=function(_8b,_8c){
return dojo.hostenv.setModulePrefix(_8b,_8c);
};
dojo.profile={start:function(){
},end:function(){
},dump:function(){
}};
dojo.exists=function(obj,_8e){
var p=_8e.split(".");
for(var i=0;i<p.length;i++){
if(!(obj[p[i]])){
return false;
}
obj=obj[p[i]];
}
return true;
};
dojo.provide("dojo.lang");
dojo.provide("dojo.AdapterRegistry");
dojo.provide("dojo.lang.Lang");
dojo.lang.mixin=function(obj,_92){
var _93={};
for(var x in _92){
if(typeof _93[x]=="undefined"||_93[x]!=_92[x]){
obj[x]=_92[x];
}
}
if(dojo.render.html.ie&&dojo.lang.isFunction(_92["toString"])&&_92["toString"]!=obj["toString"]){
obj.toString=_92.toString;
}
return obj;
};
dojo.lang.extend=function(_95,_96){
this.mixin(_95.prototype,_96);
};
dojo.lang.extendPrototype=function(obj,_98){
this.extend(obj.constructor,_98);
};
dojo.lang.anonCtr=0;
dojo.lang.anon={};
dojo.lang.nameAnonFunc=function(_99,_9a){
var nso=(_9a||dojo.lang.anon);
if((dj_global["djConfig"])&&(djConfig["slowAnonFuncLookups"]==true)){
for(var x in nso){
if(nso[x]===_99){
return x;
}
}
}
var ret="__"+dojo.lang.anonCtr++;
while(typeof nso[ret]!="undefined"){
ret="__"+dojo.lang.anonCtr++;
}
nso[ret]=_99;
return ret;
};
dojo.lang.hitch=function(_9e,_9f){
if(dojo.lang.isString(_9f)){
var fcn=_9e[_9f];
}else{
var fcn=_9f;
}
return function(){
return fcn.apply(_9e,arguments);
};
};
dojo.lang.setTimeout=function(_a1,_a2){
var _a3=window,argsStart=2;
if(!dojo.lang.isFunction(_a1)){
_a3=_a1;
_a1=_a2;
_a2=arguments[2];
argsStart++;
}
if(dojo.lang.isString(_a1)){
_a1=_a3[_a1];
}
var _a4=[];
for(var i=argsStart;i<arguments.length;i++){
_a4.push(arguments[i]);
}
return setTimeout(function(){
_a1.apply(_a3,_a4);
},_a2);
};
dojo.lang.isObject=function(wh){
return typeof wh=="object"||dojo.lang.isArray(wh)||dojo.lang.isFunction(wh);
};
dojo.lang.isArray=function(wh){
return (wh instanceof Array||typeof wh=="array");
};
dojo.lang.isArrayLike=function(wh){
if(dojo.lang.isString(wh)){
return false;
}
if(dojo.lang.isArray(wh)){
return true;
}
if(dojo.lang.isNumber(wh.length)&&isFinite(wh)){
return true;
}
return false;
};
dojo.lang.isFunction=function(wh){
return (wh instanceof Function||typeof wh=="function");
};
dojo.lang.isString=function(wh){
return (wh instanceof String||typeof wh=="string");
};
dojo.lang.isAlien=function(wh){
return !dojo.lang.isFunction()&&/\{\s*\[native code\]\s*\}/.test(String(wh));
};
dojo.lang.isBoolean=function(wh){
return (wh instanceof Boolean||typeof wh=="boolean");
};
dojo.lang.isNumber=function(wh){
return (wh instanceof Number||typeof wh=="number");
};
dojo.lang.isUndefined=function(wh){
return ((wh==undefined)&&(typeof wh=="undefined"));
};
dojo.lang.whatAmI=function(wh){
try{
if(dojo.lang.isArray(wh)){
return "array";
}
if(dojo.lang.isFunction(wh)){
return "function";
}
if(dojo.lang.isString(wh)){
return "string";
}
if(dojo.lang.isNumber(wh)){
return "number";
}
if(dojo.lang.isBoolean(wh)){
return "boolean";
}
if(dojo.lang.isAlien(wh)){
return "alien";
}
if(dojo.lang.isUndefined(wh)){
return "undefined";
}
for(var _b0 in dojo.lang.whatAmI.custom){
if(dojo.lang.whatAmI.custom[_b0](wh)){
return _b0;
}
}
if(dojo.lang.isObject(wh)){
return "object";
}
}
catch(E){
}
return "unknown";
};
dojo.lang.whatAmI.custom={};
dojo.lang.find=function(arr,val,_b3){
if(!dojo.lang.isArray(arr)&&dojo.lang.isArray(val)){
var a=arr;
arr=val;
val=a;
}
var _b5=dojo.lang.isString(arr);
if(_b5){
arr=arr.split("");
}
if(_b3){
for(var i=0;i<arr.length;++i){
if(arr[i]===val){
return i;
}
}
}else{
for(var i=0;i<arr.length;++i){
if(arr[i]==val){
return i;
}
}
}
return -1;
};
dojo.lang.indexOf=dojo.lang.find;
dojo.lang.findLast=function(arr,val,_b9){
if(!dojo.lang.isArray(arr)&&dojo.lang.isArray(val)){
var a=arr;
arr=val;
val=a;
}
var _bb=dojo.lang.isString(arr);
if(_bb){
arr=arr.split("");
}
if(_b9){
for(var i=arr.length-1;i>=0;i--){
if(arr[i]===val){
return i;
}
}
}else{
for(var i=arr.length-1;i>=0;i--){
if(arr[i]==val){
return i;
}
}
}
return -1;
};
dojo.lang.lastIndexOf=dojo.lang.findLast;
dojo.lang.inArray=function(arr,val){
return dojo.lang.find(arr,val)>-1;
};
dojo.lang.getNameInObj=function(ns,_c0){
if(!ns){
ns=dj_global;
}
for(var x in ns){
if(ns[x]===_c0){
return new String(x);
}
}
return null;
};
dojo.lang.has=function(obj,_c3){
return (typeof obj[_c3]!=="undefined");
};
dojo.lang.isEmpty=function(obj){
if(dojo.lang.isObject(obj)){
var tmp={};
var _c6=0;
for(var x in obj){
if(obj[x]&&(!tmp[x])){
_c6++;
break;
}
}
return (_c6==0);
}else{
if(dojo.lang.isArray(obj)||dojo.lang.isString(obj)){
return obj.length==0;
}
}
};
dojo.lang.forEach=function(arr,_c9,_ca){
var _cb=dojo.lang.isString(arr);
if(_cb){
arr=arr.split("");
}
var il=arr.length;
for(var i=0;i<((_ca)?il:arr.length);i++){
if(_c9(arr[i],i,arr)=="break"){
break;
}
}
};
dojo.lang.map=function(arr,obj,_d0){
var _d1=dojo.lang.isString(arr);
if(_d1){
arr=arr.split("");
}
if(dojo.lang.isFunction(obj)&&(!_d0)){
_d0=obj;
obj=dj_global;
}else{
if(dojo.lang.isFunction(obj)&&_d0){
var _d2=obj;
obj=_d0;
_d0=_d2;
}
}
if(Array.map){
var _d3=Array.map(arr,_d0,obj);
}else{
var _d3=[];
for(var i=0;i<arr.length;++i){
_d3.push(_d0.call(obj,arr[i]));
}
}
if(_d1){
return _d3.join("");
}else{
return _d3;
}
};
dojo.lang.tryThese=function(){
for(var x=0;x<arguments.length;x++){
try{
if(typeof arguments[x]=="function"){
var ret=(arguments[x]());
if(ret){
return ret;
}
}
}
catch(e){
dojo.debug(e);
}
}
};
dojo.lang.delayThese=function(_d7,cb,_d9,_da){
if(!_d7.length){
if(typeof _da=="function"){
_da();
}
return;
}
if((typeof _d9=="undefined")&&(typeof cb=="number")){
_d9=cb;
cb=function(){
};
}else{
if(!cb){
cb=function(){
};
if(!_d9){
_d9=0;
}
}
}
setTimeout(function(){
(_d7.shift())();
cb();
dojo.lang.delayThese(_d7,cb,_d9,_da);
},_d9);
};
dojo.lang.shallowCopy=function(obj){
var ret={},key;
for(key in obj){
if(dojo.lang.isUndefined(ret[key])){
ret[key]=obj[key];
}
}
return ret;
};
dojo.lang.every=function(arr,_de,_df){
var _e0=dojo.lang.isString(arr);
if(_e0){
arr=arr.split("");
}
if(Array.every){
return Array.every(arr,_de,_df);
}else{
if(!_df){
if(arguments.length>=3){
dojo.raise("thisObject doesn't exist!");
}
_df=dj_global;
}
for(var i=0;i<arr.length;i++){
if(!_de.call(_df,arr[i],i,arr)){
return false;
}
}
return true;
}
};
dojo.lang.some=function(arr,_e3,_e4){
var _e5=dojo.lang.isString(arr);
if(_e5){
arr=arr.split("");
}
if(Array.some){
return Array.some(arr,_e3,_e4);
}else{
if(!_e4){
if(arguments.length>=3){
dojo.raise("thisObject doesn't exist!");
}
_e4=dj_global;
}
for(var i=0;i<arr.length;i++){
if(_e3.call(_e4,arr[i],i,arr)){
return true;
}
}
return false;
}
};
dojo.lang.filter=function(arr,_e8,_e9){
var _ea=dojo.lang.isString(arr);
if(_ea){
arr=arr.split("");
}
if(Array.filter){
var _eb=Array.filter(arr,_e8,_e9);
}else{
if(!_e9){
if(arguments.length>=3){
dojo.raise("thisObject doesn't exist!");
}
_e9=dj_global;
}
var _eb=[];
for(var i=0;i<arr.length;i++){
if(_e8.call(_e9,arr[i],i,arr)){
_eb.push(arr[i]);
}
}
}
if(_ea){
return _eb.join("");
}else{
return _eb;
}
};
dojo.AdapterRegistry=function(){
this.pairs=[];
};
dojo.lang.extend(dojo.AdapterRegistry,{register:function(_ed,_ee,_ef,_f0){
if(_f0){
this.pairs.unshift([_ed,_ee,_ef]);
}else{
this.pairs.push([_ed,_ee,_ef]);
}
},match:function(){
for(var i=0;i<this.pairs.length;i++){
var _f2=this.pairs[i];
if(_f2[1].apply(this,arguments)){
return _f2[2].apply(this,arguments);
}
}
dojo.raise("No match found");
},unregister:function(_f3){
for(var i=0;i<this.pairs.length;i++){
var _f5=this.pairs[i];
if(_f5[0]==_f3){
this.pairs.splice(i,1);
return true;
}
}
return false;
}});
dojo.lang.reprRegistry=new dojo.AdapterRegistry();
dojo.lang.registerRepr=function(_f6,_f7,_f8,_f9){
dojo.lang.reprRegistry.register(_f6,_f7,_f8,_f9);
};
dojo.lang.repr=function(obj){
if(typeof (obj)=="undefined"){
return "undefined";
}else{
if(obj===null){
return "null";
}
}
try{
if(typeof (obj["__repr__"])=="function"){
return obj["__repr__"]();
}else{
if((typeof (obj["repr"])=="function")&&(obj.repr!=arguments.callee)){
return obj["repr"]();
}
}
return dojo.lang.reprRegistry.match(obj);
}
catch(e){
if(typeof (obj.NAME)=="string"&&(obj.toString==Function.prototype.toString||obj.toString==Object.prototype.toString)){
return o.NAME;
}
}
if(typeof (obj)=="function"){
obj=(obj+"").replace(/^\s+/,"");
var idx=obj.indexOf("{");
if(idx!=-1){
obj=obj.substr(0,idx)+"{...}";
}
}
return obj+"";
};
dojo.lang.reprArrayLike=function(arr){
try{
var na=dojo.lang.map(arr,dojo.lang.repr);
return "["+na.join(", ")+"]";
}
catch(e){
}
};
dojo.lang.reprString=function(str){
return ("\""+str.replace(/(["\\])/g,"\\$1")+"\"").replace(/[\f]/g,"\\f").replace(/[\b]/g,"\\b").replace(/[\n]/g,"\\n").replace(/[\t]/g,"\\t").replace(/[\r]/g,"\\r");
};
dojo.lang.reprNumber=function(num){
return num+"";
};
(function(){
var m=dojo.lang;
m.registerRepr("arrayLike",m.isArrayLike,m.reprArrayLike);
m.registerRepr("string",m.isString,m.reprString);
m.registerRepr("numbers",m.isNumber,m.reprNumber);
m.registerRepr("boolean",m.isBoolean,m.reprNumber);
})();
dojo.lang.unnest=function(){
var out=[];
for(var i=0;i<arguments.length;i++){
if(dojo.lang.isArrayLike(arguments[i])){
var add=dojo.lang.unnest.apply(this,arguments[i]);
out=out.concat(add);
}else{
out.push(arguments[i]);
}
}
return out;
};
dojo.require("dojo.lang");
dojo.provide("dojo.event");
dojo.event=new function(){
this.canTimeout=dojo.lang.isFunction(dj_global["setTimeout"])||dojo.lang.isAlien(dj_global["setTimeout"]);
function interpolateArgs(args){
var ao={srcObj:dj_global,srcFunc:null,adviceObj:dj_global,adviceFunc:null,aroundObj:null,aroundFunc:null,adviceType:(args.length>2)?args[0]:"after",precedence:"last",once:false,delay:null,rate:0,adviceMsg:false};
switch(args.length){
case 0:
return;
case 1:
return;
case 2:
ao.srcFunc=args[0];
ao.adviceFunc=args[1];
break;
case 3:
if((typeof args[0]=="object")&&(typeof args[1]=="string")&&(typeof args[2]=="string")){
ao.adviceType="after";
ao.srcObj=args[0];
ao.srcFunc=args[1];
ao.adviceFunc=args[2];
}else{
if((typeof args[1]=="string")&&(typeof args[2]=="string")){
ao.srcFunc=args[1];
ao.adviceFunc=args[2];
}else{
if((typeof args[0]=="object")&&(typeof args[1]=="string")&&(typeof args[2]=="function")){
ao.adviceType="after";
ao.srcObj=args[0];
ao.srcFunc=args[1];
var _106=dojo.lang.nameAnonFunc(args[2],ao.adviceObj);
ao.adviceObj[_106]=args[2];
ao.adviceFunc=_106;
}else{
if((typeof args[0]=="function")&&(typeof args[1]=="object")&&(typeof args[2]=="string")){
ao.adviceType="after";
ao.srcObj=dj_global;
var _106=dojo.lang.nameAnonFunc(args[0],ao.srcObj);
ao.srcObj[_106]=args[0];
ao.srcFunc=_106;
ao.adviceObj=args[1];
ao.adviceFunc=args[2];
}
}
}
}
break;
case 4:
if((typeof args[0]=="object")&&(typeof args[2]=="object")){
ao.adviceType="after";
ao.srcObj=args[0];
ao.srcFunc=args[1];
ao.adviceObj=args[2];
ao.adviceFunc=args[3];
}else{
if((typeof args[1]).toLowerCase()=="object"){
ao.srcObj=args[1];
ao.srcFunc=args[2];
ao.adviceObj=dj_global;
ao.adviceFunc=args[3];
}else{
if((typeof args[2]).toLowerCase()=="object"){
ao.srcObj=dj_global;
ao.srcFunc=args[1];
ao.adviceObj=args[2];
ao.adviceFunc=args[3];
}else{
ao.srcObj=ao.adviceObj=ao.aroundObj=dj_global;
ao.srcFunc=args[1];
ao.adviceFunc=args[2];
ao.aroundFunc=args[3];
}
}
}
break;
case 6:
ao.srcObj=args[1];
ao.srcFunc=args[2];
ao.adviceObj=args[3];
ao.adviceFunc=args[4];
ao.aroundFunc=args[5];
ao.aroundObj=dj_global;
break;
default:
ao.srcObj=args[1];
ao.srcFunc=args[2];
ao.adviceObj=args[3];
ao.adviceFunc=args[4];
ao.aroundObj=args[5];
ao.aroundFunc=args[6];
ao.once=args[7];
ao.delay=args[8];
ao.rate=args[9];
ao.adviceMsg=args[10];
break;
}
if((typeof ao.srcFunc).toLowerCase()!="string"){
ao.srcFunc=dojo.lang.getNameInObj(ao.srcObj,ao.srcFunc);
}
if((typeof ao.adviceFunc).toLowerCase()!="string"){
ao.adviceFunc=dojo.lang.getNameInObj(ao.adviceObj,ao.adviceFunc);
}
if((ao.aroundObj)&&((typeof ao.aroundFunc).toLowerCase()!="string")){
ao.aroundFunc=dojo.lang.getNameInObj(ao.aroundObj,ao.aroundFunc);
}
if(!ao.srcObj){
dojo.raise("bad srcObj for srcFunc: "+ao.srcFunc);
}
if(!ao.adviceObj){
dojo.raise("bad adviceObj for adviceFunc: "+ao.adviceFunc);
}
return ao;
}
this.connect=function(){
var ao=interpolateArgs(arguments);
var mjp=dojo.event.MethodJoinPoint.getForMethod(ao.srcObj,ao.srcFunc);
if(ao.adviceFunc){
var mjp2=dojo.event.MethodJoinPoint.getForMethod(ao.adviceObj,ao.adviceFunc);
}
mjp.kwAddAdvice(ao);
return mjp;
};
this.connectBefore=function(){
var args=["before"];
for(var i=0;i<arguments.length;i++){
args.push(arguments[i]);
}
return this.connect.apply(this,args);
};
this.connectAround=function(){
var args=["around"];
for(var i=0;i<arguments.length;i++){
args.push(arguments[i]);
}
return this.connect.apply(this,args);
};
this._kwConnectImpl=function(_10e,_10f){
var fn=(_10f)?"disconnect":"connect";
if(typeof _10e["srcFunc"]=="function"){
_10e.srcObj=_10e["srcObj"]||dj_global;
var _111=dojo.lang.nameAnonFunc(_10e.srcFunc,_10e.srcObj);
_10e.srcFunc=_111;
}
if(typeof _10e["adviceFunc"]=="function"){
_10e.adviceObj=_10e["adviceObj"]||dj_global;
var _111=dojo.lang.nameAnonFunc(_10e.adviceFunc,_10e.adviceObj);
_10e.adviceFunc=_111;
}
return dojo.event[fn]((_10e["type"]||_10e["adviceType"]||"after"),_10e["srcObj"]||dj_global,_10e["srcFunc"],_10e["adviceObj"]||_10e["targetObj"]||dj_global,_10e["adviceFunc"]||_10e["targetFunc"],_10e["aroundObj"],_10e["aroundFunc"],_10e["once"],_10e["delay"],_10e["rate"],_10e["adviceMsg"]||false);
};
this.kwConnect=function(_112){
return this._kwConnectImpl(_112,false);
};
this.disconnect=function(){
var ao=interpolateArgs(arguments);
if(!ao.adviceFunc){
return;
}
var mjp=dojo.event.MethodJoinPoint.getForMethod(ao.srcObj,ao.srcFunc);
return mjp.removeAdvice(ao.adviceObj,ao.adviceFunc,ao.adviceType,ao.once);
};
this.kwDisconnect=function(_115){
return this._kwConnectImpl(_115,true);
};
};
dojo.event.MethodInvocation=function(_116,obj,args){
this.jp_=_116;
this.object=obj;
this.args=[];
for(var x=0;x<args.length;x++){
this.args[x]=args[x];
}
this.around_index=-1;
};
dojo.event.MethodInvocation.prototype.proceed=function(){
this.around_index++;
if(this.around_index>=this.jp_.around.length){
return this.jp_.object[this.jp_.methodname].apply(this.jp_.object,this.args);
}else{
var ti=this.jp_.around[this.around_index];
var mobj=ti[0]||dj_global;
var meth=ti[1];
return mobj[meth].call(mobj,this);
}
};
dojo.event.MethodJoinPoint=function(obj,_11e){
this.object=obj||dj_global;
this.methodname=_11e;
this.methodfunc=this.object[_11e];
this.before=[];
this.after=[];
this.around=[];
};
dojo.event.MethodJoinPoint.getForMethod=function(obj,_120){
if(!obj){
obj=dj_global;
}
if(!obj[_120]){
obj[_120]=function(){
};
}else{
if((!dojo.lang.isFunction(obj[_120]))&&(!dojo.lang.isAlien(obj[_120]))){
return null;
}
}
var _121=_120+"$joinpoint";
var _122=_120+"$joinpoint$method";
var _123=obj[_121];
if(!_123){
var _124=false;
if(dojo.event["browser"]){
if((obj["attachEvent"])||(obj["nodeType"])||(obj["addEventListener"])){
_124=true;
dojo.event.browser.addClobberNodeAttrs(obj,[_121,_122,_120]);
}
}
obj[_122]=obj[_120];
_123=obj[_121]=new dojo.event.MethodJoinPoint(obj,_122);
obj[_120]=function(){
var args=[];
if((_124)&&(!arguments.length)&&(window.event)){
args.push(dojo.event.browser.fixEvent(window.event));
}else{
for(var x=0;x<arguments.length;x++){
if((x==0)&&(_124)&&(dojo.event.browser.isEvent(arguments[x]))){
args.push(dojo.event.browser.fixEvent(arguments[x]));
}else{
args.push(arguments[x]);
}
}
}
return _123.run.apply(_123,args);
};
}
return _123;
};
dojo.lang.extend(dojo.event.MethodJoinPoint,{unintercept:function(){
this.object[this.methodname]=this.methodfunc;
},run:function(){
var obj=this.object||dj_global;
var args=arguments;
var _129=[];
for(var x=0;x<args.length;x++){
_129[x]=args[x];
}
var _12b=function(marr){
if(!marr){
dojo.debug("Null argument to unrollAdvice()");
return;
}
var _12d=marr[0]||dj_global;
var _12e=marr[1];
if(!_12d[_12e]){
dojo.raise("function \""+_12e+"\" does not exist on \""+_12d+"\"");
}
var _12f=marr[2]||dj_global;
var _130=marr[3];
var msg=marr[6];
var _132;
var to={args:[],jp_:this,object:obj,proceed:function(){
return _12d[_12e].apply(_12d,to.args);
}};
to.args=_129;
var _134=parseInt(marr[4]);
var _135=((!isNaN(_134))&&(marr[4]!==null)&&(typeof marr[4]!="undefined"));
if(marr[5]){
var rate=parseInt(marr[5]);
var cur=new Date();
var _138=false;
if((marr["last"])&&((cur-marr.last)<=rate)){
if(dojo.event.canTimeout){
if(marr["delayTimer"]){
clearTimeout(marr.delayTimer);
}
var tod=parseInt(rate*2);
var mcpy=dojo.lang.shallowCopy(marr);
marr.delayTimer=setTimeout(function(){
mcpy[5]=0;
_12b(mcpy);
},tod);
}
return;
}else{
marr.last=cur;
}
}
if(_130){
_12f[_130].call(_12f,to);
}else{
if((_135)&&((dojo.render.html)||(dojo.render.svg))){
dj_global["setTimeout"](function(){
if(msg){
_12d[_12e].call(_12d,to);
}else{
_12d[_12e].apply(_12d,args);
}
},_134);
}else{
if(msg){
_12d[_12e].call(_12d,to);
}else{
_12d[_12e].apply(_12d,args);
}
}
}
};
if(this.before.length>0){
dojo.lang.forEach(this.before,_12b,true);
}
var _13b;
if(this.around.length>0){
var mi=new dojo.event.MethodInvocation(this,obj,args);
_13b=mi.proceed();
}else{
if(this.methodfunc){
_13b=this.object[this.methodname].apply(this.object,args);
}
}
if(this.after.length>0){
dojo.lang.forEach(this.after,_12b,true);
}
return (this.methodfunc)?_13b:null;
},getArr:function(kind){
var arr=this.after;
if((typeof kind=="string")&&(kind.indexOf("before")!=-1)){
arr=this.before;
}else{
if(kind=="around"){
arr=this.around;
}
}
return arr;
},kwAddAdvice:function(args){
this.addAdvice(args["adviceObj"],args["adviceFunc"],args["aroundObj"],args["aroundFunc"],args["adviceType"],args["precedence"],args["once"],args["delay"],args["rate"],args["adviceMsg"]);
},addAdvice:function(_140,_141,_142,_143,_144,_145,once,_147,rate,_149){
var arr=this.getArr(_144);
if(!arr){
dojo.raise("bad this: "+this);
}
var ao=[_140,_141,_142,_143,_147,rate,_149];
if(once){
if(this.hasAdvice(_140,_141,_144,arr)>=0){
return;
}
}
if(_145=="first"){
arr.unshift(ao);
}else{
arr.push(ao);
}
},hasAdvice:function(_14c,_14d,_14e,arr){
if(!arr){
arr=this.getArr(_14e);
}
var ind=-1;
for(var x=0;x<arr.length;x++){
if((arr[x][0]==_14c)&&(arr[x][1]==_14d)){
ind=x;
}
}
return ind;
},removeAdvice:function(_152,_153,_154,once){
var arr=this.getArr(_154);
var ind=this.hasAdvice(_152,_153,_154,arr);
if(ind==-1){
return false;
}
while(ind!=-1){
arr.splice(ind,1);
if(once){
break;
}
ind=this.hasAdvice(_152,_153,_154,arr);
}
return true;
}});
dojo.require("dojo.event");
dojo.provide("dojo.event.topic");
dojo.event.topic=new function(){
this.topics={};
this.getTopic=function(_158){
if(!this.topics[_158]){
this.topics[_158]=new this.TopicImpl(_158);
}
return this.topics[_158];
};
this.registerPublisher=function(_159,obj,_15b){
var _159=this.getTopic(_159);
_159.registerPublisher(obj,_15b);
};
this.subscribe=function(_15c,obj,_15e){
var _15c=this.getTopic(_15c);
_15c.subscribe(obj,_15e);
};
this.unsubscribe=function(_15f,obj,_161){
var _15f=this.getTopic(_15f);
_15f.unsubscribe(obj,_161);
};
this.publish=function(_162,_163){
var _162=this.getTopic(_162);
var args=[];
if((arguments.length==2)&&(_163.length)&&(typeof _163!="string")){
args=_163;
}else{
var args=[];
for(var x=1;x<arguments.length;x++){
args.push(arguments[x]);
}
}
_162.sendMessage.apply(_162,args);
};
};
dojo.event.topic.TopicImpl=function(_166){
this.topicName=_166;
var self=this;
self.subscribe=function(_168,_169){
var tf=_169||_168;
var to=(!_169)?dj_global:_168;
dojo.event.kwConnect({srcObj:self,srcFunc:"sendMessage",adviceObj:to,adviceFunc:tf});
};
self.unsubscribe=function(_16c,_16d){
var tf=(!_16d)?_16c:_16d;
var to=(!_16d)?null:_16c;
dojo.event.kwDisconnect({srcObj:self,srcFunc:"sendMessage",adviceObj:to,adviceFunc:tf});
};
self.registerPublisher=function(_170,_171){
dojo.event.connect(_170,_171,self,"sendMessage");
};
self.sendMessage=function(_172){
};
};
dojo.provide("dojo.event.browser");
dojo.require("dojo.event");
dojo_ie_clobber=new function(){
this.clobberNodes=[];
function nukeProp(node,prop){
try{
node[prop]=null;
}
catch(e){
}
try{
delete node[prop];
}
catch(e){
}
try{
node.removeAttribute(prop);
}
catch(e){
}
}
this.clobber=function(_175){
var na;
var tna;
if(_175){
tna=_175.getElementsByTagName("*");
na=[_175];
for(var x=0;x<tna.length;x++){
if(tna[x]["__doClobber__"]){
na.push(tna[x]);
}
}
}else{
try{
window.onload=null;
}
catch(e){
}
na=(this.clobberNodes.length)?this.clobberNodes:document.all;
}
tna=null;
var _179={};
for(var i=na.length-1;i>=0;i=i-1){
var el=na[i];
if(el["__clobberAttrs__"]){
for(var j=0;j<el.__clobberAttrs__.length;j++){
nukeProp(el,el.__clobberAttrs__[j]);
}
nukeProp(el,"__clobberAttrs__");
nukeProp(el,"__doClobber__");
}
}
na=null;
};
};
if(dojo.render.html.ie){
window.onunload=function(){
dojo_ie_clobber.clobber();
try{
if((dojo["widget"])&&(dojo.widget["manager"])){
dojo.widget.manager.destroyAll();
}
}
catch(e){
}
try{
window.onload=null;
}
catch(e){
}
try{
window.onunload=null;
}
catch(e){
}
dojo_ie_clobber.clobberNodes=[];
};
}
dojo.event.browser=new function(){
var _17d=0;
this.clean=function(node){
if(dojo.render.html.ie){
dojo_ie_clobber.clobber(node);
}
};
this.addClobberNode=function(node){
if(!node["__doClobber__"]){
node.__doClobber__=true;
dojo_ie_clobber.clobberNodes.push(node);
node.__clobberAttrs__=[];
}
};
this.addClobberNodeAttrs=function(node,_181){
this.addClobberNode(node);
for(var x=0;x<_181.length;x++){
node.__clobberAttrs__.push(_181[x]);
}
};
this.removeListener=function(node,_184,fp,_186){
if(!_186){
var _186=false;
}
_184=_184.toLowerCase();
if(_184.substr(0,2)=="on"){
_184=_184.substr(2);
}
if(node.removeEventListener){
node.removeEventListener(_184,fp,_186);
}
};
this.addListener=function(node,_188,fp,_18a,_18b){
if(!node){
return;
}
if(!_18a){
var _18a=false;
}
_188=_188.toLowerCase();
if(_188.substr(0,2)!="on"){
_188="on"+_188;
}
if(!_18b){
var _18c=function(evt){
if(!evt){
evt=window.event;
}
var ret=fp(dojo.event.browser.fixEvent(evt));
if(_18a){
dojo.event.browser.stopEvent(evt);
}
return ret;
};
}else{
_18c=fp;
}
if(node.addEventListener){
node.addEventListener(_188.substr(2),_18c,_18a);
return _18c;
}else{
if(typeof node[_188]=="function"){
var _18f=node[_188];
node[_188]=function(e){
_18f(e);
return _18c(e);
};
}else{
node[_188]=_18c;
}
if(dojo.render.html.ie){
this.addClobberNodeAttrs(node,[_188]);
}
return _18c;
}
};
this.isEvent=function(obj){
return (typeof obj!="undefined")&&(typeof Event!="undefined")&&(obj.eventPhase);
};
this.currentEvent=null;
this.callListener=function(_192,_193){
if(typeof _192!="function"){
dojo.raise("listener not a function: "+_192);
}
dojo.event.browser.currentEvent.currentTarget=_193;
return _192.call(_193,dojo.event.browser.currentEvent);
};
this.stopPropagation=function(){
dojo.event.browser.currentEvent.cancelBubble=true;
};
this.preventDefault=function(){
dojo.event.browser.currentEvent.returnValue=false;
};
this.keys={KEY_BACKSPACE:8,KEY_TAB:9,KEY_ENTER:13,KEY_SHIFT:16,KEY_CTRL:17,KEY_ALT:18,KEY_PAUSE:19,KEY_CAPS_LOCK:20,KEY_ESCAPE:27,KEY_SPACE:32,KEY_PAGE_UP:33,KEY_PAGE_DOWN:34,KEY_END:35,KEY_HOME:36,KEY_LEFT_ARROW:37,KEY_UP_ARROW:38,KEY_RIGHT_ARROW:39,KEY_DOWN_ARROW:40,KEY_INSERT:45,KEY_DELETE:46,KEY_LEFT_WINDOW:91,KEY_RIGHT_WINDOW:92,KEY_SELECT:93,KEY_F1:112,KEY_F2:113,KEY_F3:114,KEY_F4:115,KEY_F5:116,KEY_F6:117,KEY_F7:118,KEY_F8:119,KEY_F9:120,KEY_F10:121,KEY_F11:122,KEY_F12:123,KEY_NUM_LOCK:144,KEY_SCROLL_LOCK:145};
this.revKeys=[];
for(var key in this.keys){
this.revKeys[this.keys[key]]=key;
}
this.fixEvent=function(evt){
if((!evt)&&(window["event"])){
var evt=window.event;
}
if((evt["type"])&&(evt["type"].indexOf("key")==0)){
evt.keys=this.revKeys;
for(var key in this.keys){
evt[key]=this.keys[key];
}
if((dojo.render.html.ie)&&(evt["type"]=="keypress")){
evt.charCode=evt.keyCode;
}
}
if(dojo.render.html.ie){
if(!evt.target){
evt.target=evt.srcElement;
}
if(!evt.currentTarget){
evt.currentTarget=evt.srcElement;
}
if(!evt.layerX){
evt.layerX=evt.offsetX;
}
if(!evt.layerY){
evt.layerY=evt.offsetY;
}
if(evt.fromElement){
evt.relatedTarget=evt.fromElement;
}
if(evt.toElement){
evt.relatedTarget=evt.toElement;
}
this.currentEvent=evt;
evt.callListener=this.callListener;
evt.stopPropagation=this.stopPropagation;
evt.preventDefault=this.preventDefault;
}
return evt;
};
this.stopEvent=function(ev){
if(window.event){
ev.returnValue=false;
ev.cancelBubble=true;
}else{
ev.preventDefault();
ev.stopPropagation();
}
};
};
dojo.hostenv.conditionalLoadModule({common:["dojo.event","dojo.event.topic"],browser:["dojo.event.browser"]});
dojo.hostenv.moduleLoaded("dojo.event.*");
dojo.provide("dojo.dom");
dojo.require("dojo.lang");
dojo.dom.ELEMENT_NODE=1;
dojo.dom.ATTRIBUTE_NODE=2;
dojo.dom.TEXT_NODE=3;
dojo.dom.CDATA_SECTION_NODE=4;
dojo.dom.ENTITY_REFERENCE_NODE=5;
dojo.dom.ENTITY_NODE=6;
dojo.dom.PROCESSING_INSTRUCTION_NODE=7;
dojo.dom.COMMENT_NODE=8;
dojo.dom.DOCUMENT_NODE=9;
dojo.dom.DOCUMENT_TYPE_NODE=10;
dojo.dom.DOCUMENT_FRAGMENT_NODE=11;
dojo.dom.NOTATION_NODE=12;
dojo.dom.dojoml="http://www.dojotoolkit.org/2004/dojoml";
dojo.dom.xmlns={svg:"http://www.w3.org/2000/svg",smil:"http://www.w3.org/2001/SMIL20/",mml:"http://www.w3.org/1998/Math/MathML",cml:"http://www.xml-cml.org",xlink:"http://www.w3.org/1999/xlink",xhtml:"http://www.w3.org/1999/xhtml",xul:"http://www.mozilla.org/keymaster/gatekeeper/there.is.only.xul",xbl:"http://www.mozilla.org/xbl",fo:"http://www.w3.org/1999/XSL/Format",xsl:"http://www.w3.org/1999/XSL/Transform",xslt:"http://www.w3.org/1999/XSL/Transform",xi:"http://www.w3.org/2001/XInclude",xforms:"http://www.w3.org/2002/01/xforms",saxon:"http://icl.com/saxon",xalan:"http://xml.apache.org/xslt",xsd:"http://www.w3.org/2001/XMLSchema",dt:"http://www.w3.org/2001/XMLSchema-datatypes",xsi:"http://www.w3.org/2001/XMLSchema-instance",rdf:"http://www.w3.org/1999/02/22-rdf-syntax-ns#",rdfs:"http://www.w3.org/2000/01/rdf-schema#",dc:"http://purl.org/dc/elements/1.1/",dcq:"http://purl.org/dc/qualifiers/1.0","soap-env":"http://schemas.xmlsoap.org/soap/envelope/",wsdl:"http://schemas.xmlsoap.org/wsdl/",AdobeExtensions:"http://ns.adobe.com/AdobeSVGViewerExtensions/3.0/"};
dojo.dom.isNode=dojo.lang.isDomNode=function(wh){
if(typeof Element=="object"){
try{
return wh instanceof Element;
}
catch(E){
}
}else{
return wh&&!isNaN(wh.nodeType);
}
};
dojo.lang.whatAmI.custom["node"]=dojo.dom.isNode;
dojo.dom.getTagName=function(node){
var _19a=node.tagName;
if(_19a.substr(0,5).toLowerCase()!="dojo:"){
if(_19a.substr(0,4).toLowerCase()=="dojo"){
return "dojo:"+_19a.substring(4).toLowerCase();
}
var djt=node.getAttribute("dojoType")||node.getAttribute("dojotype");
if(djt){
return "dojo:"+djt.toLowerCase();
}
if((node.getAttributeNS)&&(node.getAttributeNS(this.dojoml,"type"))){
return "dojo:"+node.getAttributeNS(this.dojoml,"type").toLowerCase();
}
try{
djt=node.getAttribute("dojo:type");
}
catch(e){
}
if(djt){
return "dojo:"+djt.toLowerCase();
}
if((!dj_global["djConfig"])||(!djConfig["ignoreClassNames"])){
var _19c=node.className||node.getAttribute("class");
if((_19c)&&(_19c.indexOf)&&(_19c.indexOf("dojo-")!=-1)){
var _19d=_19c.split(" ");
for(var x=0;x<_19d.length;x++){
if((_19d[x].length>5)&&(_19d[x].indexOf("dojo-")>=0)){
return "dojo:"+_19d[x].substr(5).toLowerCase();
}
}
}
}
}
return _19a.toLowerCase();
};
dojo.dom.getUniqueId=function(){
do{
var id="dj_unique_"+(++arguments.callee._idIncrement);
}while(document.getElementById(id));
return id;
};
dojo.dom.getUniqueId._idIncrement=0;
dojo.dom.firstElement=dojo.dom.getFirstChildElement=function(_1a0,_1a1){
var node=_1a0.firstChild;
while(node&&node.nodeType!=dojo.dom.ELEMENT_NODE){
node=node.nextSibling;
}
if(_1a1&&node&&node.tagName&&node.tagName.toLowerCase()!=_1a1.toLowerCase()){
node=dojo.dom.nextElement(node,_1a1);
}
return node;
};
dojo.dom.lastElement=dojo.dom.getLastChildElement=function(_1a3,_1a4){
var node=_1a3.lastChild;
while(node&&node.nodeType!=dojo.dom.ELEMENT_NODE){
node=node.previousSibling;
}
if(_1a4&&node&&node.tagName&&node.tagName.toLowerCase()!=_1a4.toLowerCase()){
node=dojo.dom.prevElement(node,_1a4);
}
return node;
};
dojo.dom.nextElement=dojo.dom.getNextSiblingElement=function(node,_1a7){
if(!node){
return null;
}
do{
node=node.nextSibling;
}while(node&&node.nodeType!=dojo.dom.ELEMENT_NODE);
if(node&&_1a7&&_1a7.toLowerCase()!=node.tagName.toLowerCase()){
return dojo.dom.nextElement(node,_1a7);
}
return node;
};
dojo.dom.prevElement=dojo.dom.getPreviousSiblingElement=function(node,_1a9){
if(!node){
return null;
}
if(_1a9){
_1a9=_1a9.toLowerCase();
}
do{
node=node.previousSibling;
}while(node&&node.nodeType!=dojo.dom.ELEMENT_NODE);
if(node&&_1a9&&_1a9.toLowerCase()!=node.tagName.toLowerCase()){
return dojo.dom.prevElement(node,_1a9);
}
return node;
};
dojo.dom.moveChildren=function(_1aa,_1ab,trim){
var _1ad=0;
if(trim){
while(_1aa.hasChildNodes()&&_1aa.firstChild.nodeType==dojo.dom.TEXT_NODE){
_1aa.removeChild(_1aa.firstChild);
}
while(_1aa.hasChildNodes()&&_1aa.lastChild.nodeType==dojo.dom.TEXT_NODE){
_1aa.removeChild(_1aa.lastChild);
}
}
while(_1aa.hasChildNodes()){
_1ab.appendChild(_1aa.firstChild);
_1ad++;
}
return _1ad;
};
dojo.dom.copyChildren=function(_1ae,_1af,trim){
var _1b1=_1ae.cloneNode(true);
return this.moveChildren(_1b1,_1af,trim);
};
dojo.dom.removeChildren=function(node){
var _1b3=node.childNodes.length;
while(node.hasChildNodes()){
node.removeChild(node.firstChild);
}
return _1b3;
};
dojo.dom.replaceChildren=function(node,_1b5){
dojo.dom.removeChildren(node);
node.appendChild(_1b5);
};
dojo.dom.removeNode=function(node){
if(node&&node.parentNode){
return node.parentNode.removeChild(node);
}
};
dojo.dom.getAncestors=function(node,_1b8,_1b9){
var _1ba=[];
var _1bb=dojo.lang.isFunction(_1b8);
while(node){
if(!_1bb||_1b8(node)){
_1ba.push(node);
}
if(_1b9&&_1ba.length>0){
return _1ba[0];
}
node=node.parentNode;
}
if(_1b9){
return null;
}
return _1ba;
};
dojo.dom.getAncestorsByTag=function(node,tag,_1be){
tag=tag.toLowerCase();
return dojo.dom.getAncestors(node,function(el){
return ((el.tagName)&&(el.tagName.toLowerCase()==tag));
},_1be);
};
dojo.dom.getFirstAncestorByTag=function(node,tag){
return dojo.dom.getAncestorsByTag(node,tag,true);
};
dojo.dom.isDescendantOf=function(node,_1c3,_1c4){
if(_1c4&&node){
node=node.parentNode;
}
while(node){
if(node==_1c3){
return true;
}
node=node.parentNode;
}
return false;
};
dojo.dom.innerXML=function(node){
if(node.innerXML){
return node.innerXML;
}else{
if(typeof XMLSerializer!="undefined"){
return (new XMLSerializer()).serializeToString(node);
}
}
};
dojo.dom.createDocumentFromText=function(str,_1c7){
if(!_1c7){
_1c7="text/xml";
}
if(typeof DOMParser!="undefined"){
var _1c8=new DOMParser();
return _1c8.parseFromString(str,_1c7);
}else{
if(typeof ActiveXObject!="undefined"){
var _1c9=new ActiveXObject("Microsoft.XMLDOM");
if(_1c9){
_1c9.async=false;
_1c9.loadXML(str);
return _1c9;
}else{
dojo.debug("toXml didn't work?");
}
}else{
if(document.createElement){
var tmp=document.createElement("xml");
tmp.innerHTML=str;
if(document.implementation&&document.implementation.createDocument){
var _1cb=document.implementation.createDocument("foo","",null);
for(var i=0;i<tmp.childNodes.length;i++){
_1cb.importNode(tmp.childNodes.item(i),true);
}
return _1cb;
}
return tmp.document&&tmp.document.firstChild?tmp.document.firstChild:tmp;
}
}
}
return null;
};
dojo.dom.prependChild=function(node,_1ce){
if(_1ce.firstChild){
_1ce.insertBefore(node,_1ce.firstChild);
}else{
_1ce.appendChild(node);
}
return true;
};
dojo.dom.insertBefore=function(node,ref,_1d1){
if(_1d1!=true&&(node===ref||node.nextSibling===ref)){
return false;
}
var _1d2=ref.parentNode;
_1d2.insertBefore(node,ref);
return true;
};
dojo.dom.insertAfter=function(node,ref,_1d5){
var pn=ref.parentNode;
if(ref==pn.lastChild){
if((_1d5!=true)&&(node===ref)){
return false;
}
pn.appendChild(node);
}else{
return this.insertBefore(node,ref.nextSibling,_1d5);
}
return true;
};
dojo.dom.insertAtPosition=function(node,ref,_1d9){
if((!node)||(!ref)||(!_1d9)){
return false;
}
switch(_1d9.toLowerCase()){
case "before":
return dojo.dom.insertBefore(node,ref);
case "after":
return dojo.dom.insertAfter(node,ref);
case "first":
if(ref.firstChild){
return dojo.dom.insertBefore(node,ref.firstChild);
}else{
ref.appendChild(node);
return true;
}
break;
default:
ref.appendChild(node);
return true;
}
};
dojo.dom.insertAtIndex=function(node,_1db,_1dc){
var _1dd=_1db.childNodes;
if(!_1dd.length){
_1db.appendChild(node);
return true;
}
var _1de=null;
for(var i=0;i<_1dd.length;i++){
var _1e0=_1dd.item(i)["getAttribute"]?parseInt(_1dd.item(i).getAttribute("dojoinsertionindex")):-1;
if(_1e0<_1dc){
_1de=_1dd.item(i);
}
}
if(_1de){
return dojo.dom.insertAfter(node,_1de);
}else{
return dojo.dom.insertBefore(node,_1dd.item(0));
}
};
dojo.dom.textContent=function(node,text){
if(text){
dojo.dom.replaceChildren(node,document.createTextNode(text));
return text;
}else{
var _1e3="";
if(node==null){
return _1e3;
}
for(var i=0;i<node.childNodes.length;i++){
switch(node.childNodes[i].nodeType){
case 1:
case 5:
_1e3+=dojo.dom.textContent(node.childNodes[i]);
break;
case 3:
case 2:
case 4:
_1e3+=node.childNodes[i].nodeValue;
break;
default:
break;
}
}
return _1e3;
}
};
dojo.dom.collectionToArray=function(_1e5){
var _1e6=new Array(_1e5.length);
for(var i=0;i<_1e5.length;i++){
_1e6[i]=_1e5[i];
}
return _1e6;
};
dojo.provide("dojo.uri.Uri");
dojo.uri=new function(){
this.joinPath=function(){
var arr=[];
for(var i=0;i<arguments.length;i++){
arr.push(arguments[i]);
}
return arr.join("/").replace(/\/{2,}/g,"/").replace(/((https*|ftps*):)/i,"$1/");
};
this.dojoUri=function(uri){
return new dojo.uri.Uri(dojo.hostenv.getBaseScriptUri(),uri);
};
this.Uri=function(){
var uri=arguments[0];
for(var i=1;i<arguments.length;i++){
if(!arguments[i]){
continue;
}
var _1ed=new dojo.uri.Uri(arguments[i].toString());
var _1ee=new dojo.uri.Uri(uri.toString());
if(_1ed.path==""&&_1ed.scheme==null&&_1ed.authority==null&&_1ed.query==null){
if(_1ed.fragment!=null){
_1ee.fragment=_1ed.fragment;
}
_1ed=_1ee;
}else{
if(_1ed.scheme==null){
_1ed.scheme=_1ee.scheme;
if(_1ed.authority==null){
_1ed.authority=_1ee.authority;
if(_1ed.path.charAt(0)!="/"){
var path=_1ee.path.substring(0,_1ee.path.lastIndexOf("/")+1)+_1ed.path;
var segs=path.split("/");
for(var j=0;j<segs.length;j++){
if(segs[j]=="."){
if(j==segs.length-1){
segs[j]="";
}else{
segs.splice(j,1);
j--;
}
}else{
if(j>0&&!(j==1&&segs[0]=="")&&segs[j]==".."&&segs[j-1]!=".."){
if(j==segs.length-1){
segs.splice(j,1);
segs[j-1]="";
}else{
segs.splice(j-1,2);
j-=2;
}
}
}
}
_1ed.path=segs.join("/");
}
}
}
}
uri="";
if(_1ed.scheme!=null){
uri+=_1ed.scheme+":";
}
if(_1ed.authority!=null){
uri+="//"+_1ed.authority;
}
uri+=_1ed.path;
if(_1ed.query!=null){
uri+="?"+_1ed.query;
}
if(_1ed.fragment!=null){
uri+="#"+_1ed.fragment;
}
}
this.uri=uri.toString();
var _1f2="^(([^:/?#]+):)?(//([^/?#]*))?([^?#]*)(\\?([^#]*))?(#(.*))?$";
var r=this.uri.match(new RegExp(_1f2));
this.scheme=r[2]||(r[1]?"":null);
this.authority=r[4]||(r[3]?"":null);
this.path=r[5];
this.query=r[7]||(r[6]?"":null);
this.fragment=r[9]||(r[8]?"":null);
if(this.authority!=null){
_1f2="^((([^:]+:)?([^@]+))@)?([^:]*)(:([0-9]+))?$";
r=this.authority.match(new RegExp(_1f2));
this.user=r[3]||null;
this.password=r[4]||null;
this.host=r[5];
this.port=r[7]||null;
}
this.toString=function(){
return this.uri;
};
};
};
dojo.provide("dojo.string");
dojo.require("dojo.lang");
dojo.string.trim=function(str,wh){
if(!dojo.lang.isString(str)){
return str;
}
if(!str.length){
return str;
}
if(wh>0){
return str.replace(/^\s+/,"");
}else{
if(wh<0){
return str.replace(/\s+$/,"");
}else{
return str.replace(/^\s+|\s+$/g,"");
}
}
};
dojo.string.trimStart=function(str){
return dojo.string.trim(str,1);
};
dojo.string.trimEnd=function(str){
return dojo.string.trim(str,-1);
};
dojo.string.paramString=function(str,_1f9,_1fa){
for(var name in _1f9){
var re=new RegExp("\\%\\{"+name+"\\}","g");
str=str.replace(re,_1f9[name]);
}
if(_1fa){
str=str.replace(/%\{([^\}\s]+)\}/g,"");
}
return str;
};
dojo.string.capitalize=function(str){
if(!dojo.lang.isString(str)){
return "";
}
if(arguments.length==0){
str=this;
}
var _1fe=str.split(" ");
var _1ff="";
var len=_1fe.length;
for(var i=0;i<len;i++){
var word=_1fe[i];
word=word.charAt(0).toUpperCase()+word.substring(1,word.length);
_1ff+=word;
if(i<len-1){
_1ff+=" ";
}
}
return new String(_1ff);
};
dojo.string.isBlank=function(str){
if(!dojo.lang.isString(str)){
return true;
}
return (dojo.string.trim(str).length==0);
};
dojo.string.encodeAscii=function(str){
if(!dojo.lang.isString(str)){
return str;
}
var ret="";
var _206=escape(str);
var _207,re=/%u([0-9A-F]{4})/i;
while((_207=_206.match(re))){
var num=Number("0x"+_207[1]);
var _209=escape("&#"+num+";");
ret+=_206.substring(0,_207.index)+_209;
_206=_206.substring(_207.index+_207[0].length);
}
ret+=_206.replace(/\+/g,"%2B");
return ret;
};
dojo.string.summary=function(str,len){
if(!len||str.length<=len){
return str;
}else{
return str.substring(0,len).replace(/\.+$/,"")+"...";
}
};
dojo.string.escape=function(type,str){
switch(type.toLowerCase()){
case "xml":
case "html":
case "xhtml":
return dojo.string.escapeXml(str);
case "sql":
return dojo.string.escapeSql(str);
case "regexp":
case "regex":
return dojo.string.escapeRegExp(str);
case "javascript":
case "jscript":
case "js":
return dojo.string.escapeJavaScript(str);
case "ascii":
return dojo.string.encodeAscii(str);
default:
return str;
}
};
dojo.string.escapeXml=function(str){
return str.replace(/&/gm,"&amp;").replace(/</gm,"&lt;").replace(/>/gm,"&gt;").replace(/"/gm,"&quot;").replace(/'/gm,"&#39;");
};
dojo.string.escapeSql=function(str){
return str.replace(/'/gm,"''");
};
dojo.string.escapeRegExp=function(str){
return str.replace(/\\/gm,"\\\\").replace(/([\f\b\n\t\r])/gm,"\\$1");
};
dojo.string.escapeJavaScript=function(str){
return str.replace(/(["'\f\b\n\t\r])/gm,"\\$1");
};
dojo.string.repeat=function(str,_213,_214){
var out="";
for(var i=0;i<_213;i++){
out+=str;
if(_214&&i<_213-1){
out+=_214;
}
}
return out;
};
dojo.string.endsWith=function(str,end,_219){
if(_219){
str=str.toLowerCase();
end=end.toLowerCase();
}
return str.lastIndexOf(end)==str.length-end.length;
};
dojo.string.endsWithAny=function(str){
for(var i=1;i<arguments.length;i++){
if(dojo.string.endsWith(str,arguments[i])){
return true;
}
}
return false;
};
dojo.string.startsWith=function(str,_21d,_21e){
if(_21e){
str=str.toLowerCase();
_21d=_21d.toLowerCase();
}
return str.indexOf(_21d)==0;
};
dojo.string.startsWithAny=function(str){
for(var i=1;i<arguments.length;i++){
if(dojo.string.startsWith(str,arguments[i])){
return true;
}
}
return false;
};
dojo.string.has=function(str){
for(var i=1;i<arguments.length;i++){
if(str.indexOf(arguments[i]>-1)){
return true;
}
}
return false;
};
dojo.string.pad=function(str,len,c,dir){
var out=String(str);
if(!c){
c="0";
}
if(!dir){
dir=1;
}
while(out.length<len){
if(dir>0){
out=c+out;
}else{
out+=c;
}
}
return out;
};
dojo.string.padLeft=function(str,len,c){
return dojo.string.pad(str,len,c,1);
};
dojo.string.padRight=function(str,len,c){
return dojo.string.pad(str,len,c,-1);
};
dojo.string.addToPrototype=function(){
for(var _22e in dojo.string){
if(dojo.lang.isFunction(dojo.string[_22e])){
var func=(function(){
var meth=_22e;
switch(meth){
case "addToPrototype":
return null;
break;
case "escape":
return function(type){
return dojo.string.escape(type,this);
};
break;
default:
return function(){
var args=[this];
for(var i=0;i<arguments.length;i++){
args.push(arguments[i]);
}
dojo.debug(args);
return dojo.string[meth].apply(dojo.string,args);
};
}
})();
if(func){
String.prototype[_22e]=func;
}
}
}
};
dojo.provide("dojo.math");
dojo.math.degToRad=function(x){
return (x*Math.PI)/180;
};
dojo.math.radToDeg=function(x){
return (x*180)/Math.PI;
};
dojo.math.factorial=function(n){
if(n<1){
return 0;
}
var _237=1;
for(var i=1;i<=n;i++){
_237*=i;
}
return _237;
};
dojo.math.permutations=function(n,k){
if(n==0||k==0){
return 1;
}
return (dojo.math.factorial(n)/dojo.math.factorial(n-k));
};
dojo.math.combinations=function(n,r){
if(n==0||r==0){
return 1;
}
return (dojo.math.factorial(n)/(dojo.math.factorial(n-r)*dojo.math.factorial(r)));
};
dojo.math.bernstein=function(t,n,i){
return (dojo.math.combinations(n,i)*Math.pow(t,i)*Math.pow(1-t,n-i));
};
dojo.math.gaussianRandom=function(){
var k=2;
do{
var i=2*Math.random()-1;
var j=2*Math.random()-1;
k=i*i+j*j;
}while(k>=1);
k=Math.sqrt((-2*Math.log(k))/k);
return i*k;
};
dojo.math.mean=function(){
var _243=dojo.lang.isArray(arguments[0])?arguments[0]:arguments;
var mean=0;
for(var i=0;i<_243.length;i++){
mean+=_243[i];
}
return mean/_243.length;
};
dojo.math.round=function(_246,_247){
if(!_247){
var _248=1;
}else{
var _248=Math.pow(10,_247);
}
return Math.round(_246*_248)/_248;
};
dojo.math.sd=function(){
var _249=dojo.lang.isArray(arguments[0])?arguments[0]:arguments;
return Math.sqrt(dojo.math.variance(_249));
};
dojo.math.variance=function(){
var _24a=dojo.lang.isArray(arguments[0])?arguments[0]:arguments;
var mean=0,squares=0;
for(var i=0;i<_24a.length;i++){
mean+=_24a[i];
squares+=Math.pow(_24a[i],2);
}
return (squares/_24a.length)-Math.pow(mean/_24a.length,2);
};
dojo.provide("dojo.graphics.color");
dojo.require("dojo.lang");
dojo.require("dojo.string");
dojo.require("dojo.math");
dojo.graphics.color.Color=function(r,g,b,a){
if(dojo.lang.isArray(r)){
this.r=r[0];
this.g=r[1];
this.b=r[2];
this.a=r[3]||1;
}else{
if(dojo.lang.isString(r)){
var rgb=dojo.graphics.color.extractRGB(r);
this.r=rgb[0];
this.g=rgb[1];
this.b=rgb[2];
this.a=g||1;
}else{
if(r instanceof dojo.graphics.color.Color){
this.r=r.r;
this.b=r.b;
this.g=r.g;
this.a=r.a;
}else{
this.r=r;
this.g=g;
this.b=b;
this.a=a;
}
}
}
};
dojo.lang.extend(dojo.graphics.color.Color,{toRgb:function(_252){
if(_252){
return this.toRgba();
}else{
return [this.r,this.g,this.b];
}
},toRgba:function(){
return [this.r,this.g,this.b,this.a];
},toHex:function(){
return dojo.graphics.color.rgb2hex(this.toRgb());
},toCss:function(){
return "rgb("+this.toRgb().join()+")";
},toString:function(){
return this.toHex();
},toHsv:function(){
return dojo.graphics.color.rgb2hsv(this.toRgb());
},toHsl:function(){
return dojo.graphics.color.rgb2hsl(this.toRgb());
},blend:function(_253,_254){
return dojo.graphics.color.blend(this.toRgb(),new Color(_253).toRgb(),_254);
}});
dojo.graphics.color.named={white:[255,255,255],black:[0,0,0],red:[255,0,0],green:[0,255,0],blue:[0,0,255],navy:[0,0,128],gray:[128,128,128],silver:[192,192,192]};
dojo.graphics.color.blend=function(a,b,_257){
if(typeof a=="string"){
return dojo.graphics.color.blendHex(a,b,_257);
}
if(!_257){
_257=0;
}else{
if(_257>1){
_257=1;
}else{
if(_257<-1){
_257=-1;
}
}
}
var c=new Array(3);
for(var i=0;i<3;i++){
var half=Math.abs(a[i]-b[i])/2;
c[i]=Math.floor(Math.min(a[i],b[i])+half+(half*_257));
}
return c;
};
dojo.graphics.color.blendHex=function(a,b,_25d){
return dojo.graphics.color.rgb2hex(dojo.graphics.color.blend(dojo.graphics.color.hex2rgb(a),dojo.graphics.color.hex2rgb(b),_25d));
};
dojo.graphics.color.extractRGB=function(_25e){
var hex="0123456789abcdef";
_25e=_25e.toLowerCase();
if(_25e.indexOf("rgb")==0){
var _260=_25e.match(/rgba*\((\d+), *(\d+), *(\d+)/i);
var ret=_260.splice(1,3);
return ret;
}else{
var _262=dojo.graphics.color.hex2rgb(_25e);
if(_262){
return _262;
}else{
return dojo.graphics.color.named[_25e]||[255,255,255];
}
}
};
dojo.graphics.color.hex2rgb=function(hex){
var _264="0123456789ABCDEF";
var rgb=new Array(3);
if(hex.indexOf("#")==0){
hex=hex.substring(1);
}
hex=hex.toUpperCase();
if(hex.replace(new RegExp("["+_264+"]","g"),"")!=""){
return null;
}
if(hex.length==3){
rgb[0]=hex.charAt(0)+hex.charAt(0);
rgb[1]=hex.charAt(1)+hex.charAt(1);
rgb[2]=hex.charAt(2)+hex.charAt(2);
}else{
rgb[0]=hex.substring(0,2);
rgb[1]=hex.substring(2,4);
rgb[2]=hex.substring(4);
}
for(var i=0;i<rgb.length;i++){
rgb[i]=_264.indexOf(rgb[i].charAt(0))*16+_264.indexOf(rgb[i].charAt(1));
}
return rgb;
};
dojo.graphics.color.rgb2hex=function(r,g,b){
if(dojo.lang.isArray(r)){
g=r[1]||0;
b=r[2]||0;
r=r[0]||0;
}
return ["#",dojo.string.pad(r.toString(16),2),dojo.string.pad(g.toString(16),2),dojo.string.pad(b.toString(16),2)].join("");
};
dojo.graphics.color.rgb2hsv=function(r,g,b){
if(dojo.lang.isArray(r)){
b=r[2]||0;
g=r[1]||0;
r=r[0]||0;
}
var h=null;
var s=null;
var v=null;
var min=Math.min(r,g,b);
v=Math.max(r,g,b);
var _271=v-min;
s=(v==0)?0:_271/v;
if(s==0){
h=0;
}else{
if(r==v){
h=60*(g-b)/_271;
}else{
if(g==v){
h=120+60*(b-r)/_271;
}else{
if(b==v){
h=240+60*(r-g)/_271;
}
}
}
if(h<0){
h+=360;
}
}
h=(h==0)?360:Math.ceil((h/360)*255);
s=Math.ceil(s*255);
return [h,s,v];
};
dojo.graphics.color.hsv2rgb=function(h,s,v){
if(dojo.lang.isArray(h)){
v=h[2]||0;
s=h[1]||0;
h=h[0]||0;
}
h=(h/255)*360;
if(h==360){
h=0;
}
s=s/255;
v=v/255;
var r=null;
var g=null;
var b=null;
if(s==0){
r=v;
g=v;
b=v;
}else{
var _278=h/60;
var i=Math.floor(_278);
var f=_278-i;
var p=v*(1-s);
var q=v*(1-(s*f));
var t=v*(1-(s*(1-f)));
switch(i){
case 0:
r=v;
g=t;
b=p;
break;
case 1:
r=q;
g=v;
b=p;
break;
case 2:
r=p;
g=v;
b=t;
break;
case 3:
r=p;
g=q;
b=v;
break;
case 4:
r=t;
g=p;
b=v;
break;
case 5:
r=v;
g=p;
b=q;
break;
}
}
r=Math.ceil(r*255);
g=Math.ceil(g*255);
b=Math.ceil(b*255);
return [r,g,b];
};
dojo.graphics.color.rgb2hsl=function(r,g,b){
if(dojo.lang.isArray(r)){
b=r[2]||0;
g=r[1]||0;
r=r[0]||0;
}
r/=255;
g/=255;
b/=255;
var h=null;
var s=null;
var l=null;
var min=Math.min(r,g,b);
var max=Math.max(r,g,b);
var _286=max-min;
l=(min+max)/2;
s=0;
if((l>0)&&(l<1)){
s=_286/((l<0.5)?(2*l):(2-2*l));
}
h=0;
if(_286>0){
if((max==r)&&(max!=g)){
h+=(g-b)/_286;
}
if((max==g)&&(max!=b)){
h+=(2+(b-r)/_286);
}
if((max==b)&&(max!=r)){
h+=(4+(r-g)/_286);
}
h*=60;
}
h=(h==0)?360:Math.ceil((h/360)*255);
s=Math.ceil(s*255);
l=Math.ceil(l*255);
return [h,s,l];
};
dojo.graphics.color.hsl2rgb=function(h,s,l){
if(dojo.lang.isArray(h)){
l=h[2]||0;
s=h[1]||0;
h=h[0]||0;
}
h=(h/255)*360;
if(h==360){
h=0;
}
s=s/255;
l=l/255;
while(h<0){
h+=360;
}
while(h>360){
h-=360;
}
if(h<120){
r=(120-h)/60;
g=h/60;
b=0;
}else{
if(h<240){
r=0;
g=(240-h)/60;
b=(h-120)/60;
}else{
r=(h-240)/60;
g=0;
b=(360-h)/60;
}
}
r=Math.min(r,1);
g=Math.min(g,1);
b=Math.min(b,1);
r=2*s*r+(1-s);
g=2*s*g+(1-s);
b=2*s*b+(1-s);
if(l<0.5){
r=l*r;
g=l*g;
b=l*b;
}else{
r=(1-l)*r+2*l-1;
g=(1-l)*g+2*l-1;
b=(1-l)*b+2*l-1;
}
r=Math.ceil(r*255);
g=Math.ceil(g*255);
b=Math.ceil(b*255);
return [r,g,b];
};
dojo.graphics.color.hsl2hex=function(h,s,l){
var rgb=dojo.graphics.color.hsl2rgb(h,s,l);
return dojo.graphics.color.rgb2hex(rgb[0],rgb[1],rgb[2]);
};
dojo.graphics.color.hex2hsl=function(hex){
var rgb=dojo.graphics.color.hex2rgb(hex);
return dojo.graphics.color.rgb2hsl(rgb[0],rgb[1],rgb[2]);
};
dojo.provide("dojo.style");
dojo.require("dojo.dom");
dojo.require("dojo.uri.Uri");
dojo.require("dojo.graphics.color");
dojo.style.boxSizing={marginBox:"margin-box",borderBox:"border-box",paddingBox:"padding-box",contentBox:"content-box"};
dojo.style.getBoxSizing=function(node){
if(dojo.render.html.ie||dojo.render.html.opera){
var cm=document["compatMode"];
if(cm=="BackCompat"||cm=="QuirksMode"){
return dojo.style.boxSizing.borderBox;
}else{
return dojo.style.boxSizing.contentBox;
}
}else{
if(arguments.length==0){
node=document.documentElement;
}
var _292=dojo.style.getStyle(node,"-moz-box-sizing");
if(!_292){
_292=dojo.style.getStyle(node,"box-sizing");
}
return (_292?_292:dojo.style.boxSizing.contentBox);
}
};
dojo.style.isBorderBox=function(node){
return (dojo.style.getBoxSizing(node)==dojo.style.boxSizing.borderBox);
};
dojo.style.getUnitValue=function(_294,_295,_296){
var _297={value:0,units:"px"};
var s=dojo.style.getComputedStyle(_294,_295);
if(s==""||(s=="auto"&&_296)){
return _297;
}
if(dojo.lang.isUndefined(s)){
_297.value=NaN;
}else{
var _299=s.match(/([\d.]+)([a-z%]*)/i);
if(!_299){
_297.value=NaN;
}else{
_297.value=Number(_299[1]);
_297.units=_299[2].toLowerCase();
}
}
return _297;
};
dojo.style.getPixelValue=function(_29a,_29b,_29c){
var _29d=dojo.style.getUnitValue(_29a,_29b,_29c);
if(isNaN(_29d.value)){
return 0;
}
if((_29d.value)&&(_29d.units!="px")){
return NaN;
}
return _29d.value;
};
dojo.style.getNumericStyle=dojo.style.getPixelValue;
dojo.style.isPositionAbsolute=function(node){
return (dojo.style.getComputedStyle(node,"position")=="absolute");
};
dojo.style.getMarginWidth=function(node){
var _2a0=dojo.style.isPositionAbsolute(node);
var left=dojo.style.getPixelValue(node,"margin-left",_2a0);
var _2a2=dojo.style.getPixelValue(node,"margin-right",_2a0);
return left+_2a2;
};
dojo.style.getBorderWidth=function(node){
var left=(dojo.style.getStyle(node,"border-left-style")=="none"?0:dojo.style.getPixelValue(node,"border-left-width"));
var _2a5=(dojo.style.getStyle(node,"border-right-style")=="none"?0:dojo.style.getPixelValue(node,"border-right-width"));
return left+_2a5;
};
dojo.style.getPaddingWidth=function(node){
var left=dojo.style.getPixelValue(node,"padding-left",true);
var _2a8=dojo.style.getPixelValue(node,"padding-right",true);
return left+_2a8;
};
dojo.style.getContentWidth=function(node){
return node.offsetWidth-dojo.style.getPaddingWidth(node)-dojo.style.getBorderWidth(node);
};
dojo.style.getInnerWidth=function(node){
return node.offsetWidth;
};
dojo.style.getOuterWidth=function(node){
return dojo.style.getInnerWidth(node)+dojo.style.getMarginWidth(node);
};
dojo.style.setOuterWidth=function(node,_2ad){
if(!dojo.style.isBorderBox(node)){
_2ad-=dojo.style.getPaddingWidth(node)+dojo.style.getBorderWidth(node);
}
_2ad-=dojo.style.getMarginWidth(node);
if(!isNaN(_2ad)&&_2ad>0){
node.style.width=_2ad+"px";
return true;
}else{
return false;
}
};
dojo.style.getContentBoxWidth=dojo.style.getContentWidth;
dojo.style.getBorderBoxWidth=dojo.style.getInnerWidth;
dojo.style.getMarginBoxWidth=dojo.style.getOuterWidth;
dojo.style.setMarginBoxWidth=dojo.style.setOuterWidth;
dojo.style.getMarginHeight=function(node){
var _2af=dojo.style.isPositionAbsolute(node);
var top=dojo.style.getPixelValue(node,"margin-top",_2af);
var _2b1=dojo.style.getPixelValue(node,"margin-bottom",_2af);
return top+_2b1;
};
dojo.style.getBorderHeight=function(node){
var top=(dojo.style.getStyle(node,"border-top-style")=="none"?0:dojo.style.getPixelValue(node,"border-top-width"));
var _2b4=(dojo.style.getStyle(node,"border-bottom-style")=="none"?0:dojo.style.getPixelValue(node,"border-bottom-width"));
return top+_2b4;
};
dojo.style.getPaddingHeight=function(node){
var top=dojo.style.getPixelValue(node,"padding-top",true);
var _2b7=dojo.style.getPixelValue(node,"padding-bottom",true);
return top+_2b7;
};
dojo.style.getContentHeight=function(node){
return node.offsetHeight-dojo.style.getPaddingHeight(node)-dojo.style.getBorderHeight(node);
};
dojo.style.getInnerHeight=function(node){
return node.offsetHeight;
};
dojo.style.getOuterHeight=function(node){
return dojo.style.getInnerHeight(node)+dojo.style.getMarginHeight(node);
};
dojo.style.setOuterHeight=function(node,_2bc){
if(!dojo.style.isBorderBox(node)){
_2bc-=dojo.style.getPaddingHeight(node)+dojo.style.getBorderHeight(node);
}
_2bc-=dojo.style.getMarginHeight(node);
if(!isNaN(_2bc)&&_2bc>0){
node.style.height=_2bc+"px";
return true;
}else{
return false;
}
};
dojo.style.setContentWidth=function(node,_2be){
if(dojo.style.isBorderBox(node)){
_2be+=dojo.style.getPaddingWidth(node)+dojo.style.getBorderWidth(node);
}
if(!isNaN(_2be)&&_2be>0){
node.style.width=_2be+"px";
return true;
}else{
return false;
}
};
dojo.style.setContentHeight=function(node,_2c0){
if(dojo.style.isBorderBox(node)){
_2c0+=dojo.style.getPaddingHeight(node)+dojo.style.getBorderHeight(node);
}
if(!isNaN(_2c0)&&_2c0>0){
node.style.height=_2c0+"px";
return true;
}else{
return false;
}
};
dojo.style.getContentBoxHeight=dojo.style.getContentHeight;
dojo.style.getBorderBoxHeight=dojo.style.getInnerHeight;
dojo.style.getMarginBoxHeight=dojo.style.getOuterHeight;
dojo.style.setMarginBoxHeight=dojo.style.setOuterHeight;
dojo.style.getTotalOffset=function(node,type,_2c3){
var _2c4=(type=="top")?"offsetTop":"offsetLeft";
var _2c5=(type=="top")?"scrollTop":"scrollLeft";
var _2c6=(type=="top")?"y":"x";
var _2c7=0;
if(node["offsetParent"]){
if(dojo.render.html.safari&&node.style.getPropertyValue("position")=="absolute"&&node.parentNode==dojo.html.body()){
var _2c8=dojo.html.body();
}else{
var _2c8=dojo.html.body().parentNode;
}
if(_2c3&&node.parentNode!=document.body){
_2c7-=dojo.style.sumAncestorProperties(node,_2c5);
}
do{
_2c7+=node[_2c4];
node=node.offsetParent;
}while(node!=_2c8&&node!=null);
}else{
if(node[_2c6]){
_2c7+=node[_2c6];
}
}
return _2c7;
};
dojo.style.sumAncestorProperties=function(node,prop){
if(!node){
return 0;
}
var _2cb=0;
while(node){
var val=node[prop];
if(val){
_2cb+=val-0;
}
node=node.parentNode;
}
return _2cb;
};
dojo.style.totalOffsetLeft=function(node,_2ce){
return dojo.style.getTotalOffset(node,"left",_2ce);
};
dojo.style.getAbsoluteX=dojo.style.totalOffsetLeft;
dojo.style.totalOffsetTop=function(node,_2d0){
return dojo.style.getTotalOffset(node,"top",_2d0);
};
dojo.style.getAbsoluteY=dojo.style.totalOffsetTop;
dojo.style.getAbsolutePosition=function(node,_2d2){
var _2d3=[dojo.style.getAbsoluteX(node,_2d2),dojo.style.getAbsoluteY(node,_2d2)];
_2d3.x=_2d3[0];
_2d3.y=_2d3[1];
return _2d3;
};
dojo.style.styleSheet=null;
dojo.style.insertCssRule=function(_2d4,_2d5,_2d6){
if(!dojo.style.styleSheet){
if(document.createStyleSheet){
dojo.style.styleSheet=document.createStyleSheet();
}else{
if(document.styleSheets[0]){
dojo.style.styleSheet=document.styleSheets[0];
}else{
return null;
}
}
}
if(arguments.length<3){
if(dojo.style.styleSheet.cssRules){
_2d6=dojo.style.styleSheet.cssRules.length;
}else{
if(dojo.style.styleSheet.rules){
_2d6=dojo.style.styleSheet.rules.length;
}else{
return null;
}
}
}
if(dojo.style.styleSheet.insertRule){
var rule=_2d4+" { "+_2d5+" }";
return dojo.style.styleSheet.insertRule(rule,_2d6);
}else{
if(dojo.style.styleSheet.addRule){
return dojo.style.styleSheet.addRule(_2d4,_2d5,_2d6);
}else{
return null;
}
}
};
dojo.style.removeCssRule=function(_2d8){
if(!dojo.style.styleSheet){
dojo.debug("no stylesheet defined for removing rules");
return false;
}
if(dojo.render.html.ie){
if(!_2d8){
_2d8=dojo.style.styleSheet.rules.length;
dojo.style.styleSheet.removeRule(_2d8);
}
}else{
if(document.styleSheets[0]){
if(!_2d8){
_2d8=dojo.style.styleSheet.cssRules.length;
}
dojo.style.styleSheet.deleteRule(_2d8);
}
}
return true;
};
dojo.style.insertCssFile=function(URI,doc,_2db){
if(!URI){
return;
}
if(!doc){
doc=document;
}
if(doc.baseURI){
URI=new dojo.uri.Uri(doc.baseURI,URI);
}
if(_2db&&doc.styleSheets){
var loc=location.href.split("#")[0].substring(0,location.href.indexOf(location.pathname));
for(var i=0;i<doc.styleSheets.length;i++){
if(doc.styleSheets[i].href&&URI.toString()==new dojo.uri.Uri(doc.styleSheets[i].href.toString())){
return;
}
}
}
var file=doc.createElement("link");
file.setAttribute("type","text/css");
file.setAttribute("rel","stylesheet");
file.setAttribute("href",URI);
var head=doc.getElementsByTagName("head")[0];
if(head){
head.appendChild(file);
}
};
dojo.style.getBackgroundColor=function(node){
var _2e1;
do{
_2e1=dojo.style.getStyle(node,"background-color");
if(_2e1.toLowerCase()=="rgba(0, 0, 0, 0)"){
_2e1="transparent";
}
if(node==document.getElementsByTagName("body")[0]){
node=null;
break;
}
node=node.parentNode;
}while(node&&dojo.lang.inArray(_2e1,["transparent",""]));
if(_2e1=="transparent"){
_2e1=[255,255,255,0];
}else{
_2e1=dojo.graphics.color.extractRGB(_2e1);
}
return _2e1;
};
dojo.style.getComputedStyle=function(_2e2,_2e3,_2e4){
var _2e5=_2e4;
if(_2e2.style.getPropertyValue){
_2e5=_2e2.style.getPropertyValue(_2e3);
}
if(!_2e5){
if(document.defaultView){
_2e5=document.defaultView.getComputedStyle(_2e2,"").getPropertyValue(_2e3);
}else{
if(_2e2.currentStyle){
_2e5=_2e2.currentStyle[dojo.style.toCamelCase(_2e3)];
}
}
}
return _2e5;
};
dojo.style.getStyle=function(_2e6,_2e7){
var _2e8=dojo.style.toCamelCase(_2e7);
var _2e9=_2e6.style[_2e8];
return (_2e9?_2e9:dojo.style.getComputedStyle(_2e6,_2e7,_2e9));
};
dojo.style.toCamelCase=function(_2ea){
var arr=_2ea.split("-"),cc=arr[0];
for(var i=1;i<arr.length;i++){
cc+=arr[i].charAt(0).toUpperCase()+arr[i].substring(1);
}
return cc;
};
dojo.style.toSelectorCase=function(_2ed){
return _2ed.replace(/([A-Z])/g,"-$1").toLowerCase();
};
dojo.style.setOpacity=function setOpacity(node,_2ef,_2f0){
node=dojo.byId(node);
var h=dojo.render.html;
if(!_2f0){
if(_2ef>=1){
if(h.ie){
dojo.style.clearOpacity(node);
return;
}else{
_2ef=0.999999;
}
}else{
if(_2ef<0){
_2ef=0;
}
}
}
if(h.ie){
if(node.nodeName.toLowerCase()=="tr"){
var tds=node.getElementsByTagName("td");
for(var x=0;x<tds.length;x++){
tds[x].style.filter="Alpha(Opacity="+_2ef*100+")";
}
}
node.style.filter="Alpha(Opacity="+_2ef*100+")";
}else{
if(h.moz){
node.style.opacity=_2ef;
node.style.MozOpacity=_2ef;
}else{
if(h.safari){
node.style.opacity=_2ef;
node.style.KhtmlOpacity=_2ef;
}else{
node.style.opacity=_2ef;
}
}
}
};
dojo.style.getOpacity=function getOpacity(node){
if(dojo.render.html.ie){
var opac=(node.filters&&node.filters.alpha&&typeof node.filters.alpha.opacity=="number"?node.filters.alpha.opacity:100)/100;
}else{
var opac=node.style.opacity||node.style.MozOpacity||node.style.KhtmlOpacity||1;
}
return opac>=0.999999?1:Number(opac);
};
dojo.style.clearOpacity=function clearOpacity(node){
var h=dojo.render.html;
if(h.ie){
if(node.filters&&node.filters.alpha){
node.style.filter="";
}
}else{
if(h.moz){
node.style.opacity=1;
node.style.MozOpacity=1;
}else{
if(h.safari){
node.style.opacity=1;
node.style.KhtmlOpacity=1;
}else{
node.style.opacity=1;
}
}
}
};
dojo.provide("dojo.html");
dojo.require("dojo.dom");
dojo.require("dojo.style");
dojo.require("dojo.string");
dojo.lang.mixin(dojo.html,dojo.dom);
dojo.lang.mixin(dojo.html,dojo.style);
dojo.html.clearSelection=function(){
try{
if(window["getSelection"]){
if(dojo.render.html.safari){
window.getSelection().collapse();
}else{
window.getSelection().removeAllRanges();
}
}else{
if((document.selection)&&(document.selection.clear)){
document.selection.clear();
}
}
return true;
}
catch(e){
dojo.debug(e);
return false;
}
};
dojo.html.disableSelection=function(_2f8){
_2f8=_2f8||dojo.html.body();
var h=dojo.render.html;
if(h.mozilla){
_2f8.style.MozUserSelect="none";
}else{
if(h.safari){
_2f8.style.KhtmlUserSelect="none";
}else{
if(h.ie){
_2f8.unselectable="on";
}else{
return false;
}
}
}
return true;
};
dojo.html.enableSelection=function(_2fa){
_2fa=_2fa||dojo.html.body();
var h=dojo.render.html;
if(h.mozilla){
_2fa.style.MozUserSelect="";
}else{
if(h.safari){
_2fa.style.KhtmlUserSelect="";
}else{
if(h.ie){
_2fa.unselectable="off";
}else{
return false;
}
}
}
return true;
};
dojo.html.selectElement=function(_2fc){
if(document.selection&&dojo.html.body().createTextRange){
var _2fd=dojo.html.body().createTextRange();
_2fd.moveToElementText(_2fc);
_2fd.select();
}else{
if(window["getSelection"]){
var _2fe=window.getSelection();
if(_2fe["selectAllChildren"]){
_2fe.selectAllChildren(_2fc);
}
}
}
};
dojo.html.isSelectionCollapsed=function(){
if(document["selection"]){
return document.selection.createRange().text=="";
}else{
if(window["getSelection"]){
var _2ff=window.getSelection();
if(dojo.lang.isString(_2ff)){
return _2ff=="";
}else{
return _2ff.isCollapsed;
}
}
}
};
dojo.html.getEventTarget=function(evt){
if(!evt){
evt=window.event||{};
}
if(evt.srcElement){
return evt.srcElement;
}else{
if(evt.target){
return evt.target;
}
}
return null;
};
dojo.html.getScrollTop=function(){
return document.documentElement.scrollTop||dojo.html.body().scrollTop||0;
};
dojo.html.getScrollLeft=function(){
return document.documentElement.scrollLeft||dojo.html.body().scrollLeft||0;
};
dojo.html.getDocumentWidth=function(){
dojo.deprecated("dojo.html.getDocument* has been deprecated in favor of dojo.html.getViewport*");
return dojo.html.getViewportWidth();
};
dojo.html.getDocumentHeight=function(){
dojo.deprecated("dojo.html.getDocument* has been deprecated in favor of dojo.html.getViewport*");
return dojo.html.getViewportHeight();
};
dojo.html.getDocumentSize=function(){
dojo.deprecated("dojo.html.getDocument* has been deprecated in favor of dojo.html.getViewport*");
return dojo.html.getViewportSize();
};
dojo.html.getViewportWidth=function(){
var w=0;
if(window.innerWidth){
w=window.innerWidth;
}
if(dojo.exists(document,"documentElement.clientWidth")){
var w2=document.documentElement.clientWidth;
if(!w||w2&&w2<w){
w=w2;
}
return w;
}
if(document.body){
return document.body.clientWidth;
}
return 0;
};
dojo.html.getViewportHeight=function(){
if(window.innerHeight){
return window.innerHeight;
}
if(dojo.exists(document,"documentElement.clientHeight")){
return document.documentElement.clientHeight;
}
if(document.body){
return document.body.clientHeight;
}
return 0;
};
dojo.html.getViewportSize=function(){
var ret=[dojo.html.getViewportWidth(),dojo.html.getViewportHeight()];
ret.w=ret[0];
ret.h=ret[1];
return ret;
};
dojo.html.getScrollOffset=function(){
var ret=[0,0];
if(window.pageYOffset){
ret=[window.pageXOffset,window.pageYOffset];
}else{
if(dojo.exists(document,"documentElement.scrollTop")){
ret=[document.documentElement.scrollLeft,document.documentElement.scrollTop];
}else{
if(document.body){
ret=[document.body.scrollLeft,document.body.scrollTop];
}
}
}
ret.x=ret[0];
ret.y=ret[1];
return ret;
};
dojo.html.getParentOfType=function(node,type){
dojo.deprecated("dojo.html.getParentOfType has been deprecated in favor of dojo.html.getParentByType*");
return dojo.html.getParentByType(node,type);
};
dojo.html.getParentByType=function(node,type){
var _309=node;
type=type.toLowerCase();
while((_309)&&(_309.nodeName.toLowerCase()!=type)){
if(_309==(document["body"]||document["documentElement"])){
return null;
}
_309=_309.parentNode;
}
return _309;
};
dojo.html.getAttribute=function(node,attr){
if((!node)||(!node.getAttribute)){
return null;
}
var ta=typeof attr=="string"?attr:new String(attr);
var v=node.getAttribute(ta.toUpperCase());
if((v)&&(typeof v=="string")&&(v!="")){
return v;
}
if(v&&v.value){
return v.value;
}
if((node.getAttributeNode)&&(node.getAttributeNode(ta))){
return (node.getAttributeNode(ta)).value;
}else{
if(node.getAttribute(ta)){
return node.getAttribute(ta);
}else{
if(node.getAttribute(ta.toLowerCase())){
return node.getAttribute(ta.toLowerCase());
}
}
}
return null;
};
dojo.html.hasAttribute=function(node,attr){
return dojo.html.getAttribute(node,attr)?true:false;
};
dojo.html.getClass=function(node){
if(!node){
return "";
}
var cs="";
if(node.className){
cs=node.className;
}else{
if(dojo.html.hasAttribute(node,"class")){
cs=dojo.html.getAttribute(node,"class");
}
}
return dojo.string.trim(cs);
};
dojo.html.getClasses=function(node){
var c=dojo.html.getClass(node);
return (c=="")?[]:c.split(/\s+/g);
};
dojo.html.hasClass=function(node,_315){
return dojo.lang.inArray(dojo.html.getClasses(node),_315);
};
dojo.html.prependClass=function(node,_317){
if(!node){
return false;
}
_317+=" "+dojo.html.getClass(node);
return dojo.html.setClass(node,_317);
};
dojo.html.addClass=function(node,_319){
if(!node){
return false;
}
if(dojo.html.hasClass(node,_319)){
return false;
}
_319=dojo.string.trim(dojo.html.getClass(node)+" "+_319);
return dojo.html.setClass(node,_319);
};
dojo.html.setClass=function(node,_31b){
if(!node){
return false;
}
var cs=new String(_31b);
try{
if(typeof node.className=="string"){
node.className=cs;
}else{
if(node.setAttribute){
node.setAttribute("class",_31b);
node.className=cs;
}else{
return false;
}
}
}
catch(e){
dojo.debug("dojo.html.setClass() failed",e);
}
return true;
};
dojo.html.removeClass=function(node,_31e,_31f){
if(!node){
return false;
}
var _31e=dojo.string.trim(new String(_31e));
try{
var cs=dojo.html.getClasses(node);
var nca=[];
if(_31f){
for(var i=0;i<cs.length;i++){
if(cs[i].indexOf(_31e)==-1){
nca.push(cs[i]);
}
}
}else{
for(var i=0;i<cs.length;i++){
if(cs[i]!=_31e){
nca.push(cs[i]);
}
}
}
dojo.html.setClass(node,nca.join(" "));
}
catch(e){
dojo.debug("dojo.html.removeClass() failed",e);
}
return true;
};
dojo.html.replaceClass=function(node,_324,_325){
dojo.html.removeClass(node,_325);
dojo.html.addClass(node,_324);
};
dojo.html.classMatchType={ContainsAll:0,ContainsAny:1,IsOnly:2};
dojo.html.getElementsByClass=function(_326,_327,_328,_329){
if(!_327){
_327=document;
}
var _32a=_326.split(/\s+/g);
var _32b=[];
if(_329!=1&&_329!=2){
_329=0;
}
var _32c=new RegExp("(\\s|^)(("+_32a.join(")|(")+"))(\\s|$)");
if(!_328){
_328="*";
}
var _32d=_327.getElementsByTagName(_328);
outer:
for(var i=0;i<_32d.length;i++){
var node=_32d[i];
var _330=dojo.html.getClasses(node);
if(_330.length==0){
continue outer;
}
var _331=0;
for(var j=0;j<_330.length;j++){
if(_32c.test(_330[j])){
if(_329==dojo.html.classMatchType.ContainsAny){
_32b.push(node);
continue outer;
}else{
_331++;
}
}else{
if(_329==dojo.html.classMatchType.IsOnly){
continue outer;
}
}
}
if(_331==_32a.length){
if(_329==dojo.html.classMatchType.IsOnly&&_331==_330.length){
_32b.push(node);
}else{
if(_329==dojo.html.classMatchType.ContainsAll){
_32b.push(node);
}
}
}
}
return _32b;
};
dojo.html.getElementsByClassName=dojo.html.getElementsByClass;
dojo.html.gravity=function(node,e){
var _335=e.pageX||e.clientX+dojo.html.body().scrollLeft;
var _336=e.pageY||e.clientY+dojo.html.body().scrollTop;
with(dojo.html){
var _337=getAbsoluteX(node)+(getInnerWidth(node)/2);
var _338=getAbsoluteY(node)+(getInnerHeight(node)/2);
}
with(dojo.html.gravity){
return ((_335<_337?WEST:EAST)|(_336<_338?NORTH:SOUTH));
}
};
dojo.html.gravity.NORTH=1;
dojo.html.gravity.SOUTH=1<<1;
dojo.html.gravity.EAST=1<<2;
dojo.html.gravity.WEST=1<<3;
dojo.html.overElement=function(_339,e){
var _33b=e.pageX||e.clientX+dojo.html.body().scrollLeft;
var _33c=e.pageY||e.clientY+dojo.html.body().scrollTop;
with(dojo.html){
var top=getAbsoluteY(_339);
var _33e=top+getInnerHeight(_339);
var left=getAbsoluteX(_339);
var _340=left+getInnerWidth(_339);
}
return (_33b>=left&&_33b<=_340&&_33c>=top&&_33c<=_33e);
};
dojo.html.renderedTextContent=function(node){
var _342="";
if(node==null){
return _342;
}
for(var i=0;i<node.childNodes.length;i++){
switch(node.childNodes[i].nodeType){
case 1:
case 5:
var _344="unknown";
try{
_344=dojo.style.getStyle(node.childNodes[i],"display");
}
catch(E){
}
switch(_344){
case "block":
case "list-item":
case "run-in":
case "table":
case "table-row-group":
case "table-header-group":
case "table-footer-group":
case "table-row":
case "table-column-group":
case "table-column":
case "table-cell":
case "table-caption":
_342+="\n";
_342+=dojo.html.renderedTextContent(node.childNodes[i]);
_342+="\n";
break;
case "none":
break;
default:
if(node.childNodes[i].tagName&&node.childNodes[i].tagName.toLowerCase()=="br"){
_342+="\n";
}else{
_342+=dojo.html.renderedTextContent(node.childNodes[i]);
}
break;
}
break;
case 3:
case 2:
case 4:
var text=node.childNodes[i].nodeValue;
var _346="unknown";
try{
_346=dojo.style.getStyle(node,"text-transform");
}
catch(E){
}
switch(_346){
case "capitalize":
text=dojo.string.capitalize(text);
break;
case "uppercase":
text=text.toUpperCase();
break;
case "lowercase":
text=text.toLowerCase();
break;
default:
break;
}
switch(_346){
case "nowrap":
break;
case "pre-wrap":
break;
case "pre-line":
break;
case "pre":
break;
default:
text=text.replace(/\s+/," ");
if(/\s$/.test(_342)){
text.replace(/^\s/,"");
}
break;
}
_342+=text;
break;
default:
break;
}
}
return _342;
};
dojo.html.setActiveStyleSheet=function(_347){
var i,a,main;
for(i=0;(a=document.getElementsByTagName("link")[i]);i++){
if(a.getAttribute("rel").indexOf("style")!=-1&&a.getAttribute("title")){
a.disabled=true;
if(a.getAttribute("title")==_347){
a.disabled=false;
}
}
}
};
dojo.html.getActiveStyleSheet=function(){
var i,a;
for(i=0;(a=document.getElementsByTagName("link")[i]);i++){
if(a.getAttribute("rel").indexOf("style")!=-1&&a.getAttribute("title")&&!a.disabled){
return a.getAttribute("title");
}
}
return null;
};
dojo.html.getPreferredStyleSheet=function(){
var i,a;
for(i=0;(a=document.getElementsByTagName("link")[i]);i++){
if(a.getAttribute("rel").indexOf("style")!=-1&&a.getAttribute("rel").indexOf("alt")==-1&&a.getAttribute("title")){
return a.getAttribute("title");
}
}
return null;
};
dojo.html.body=function(){
return document.body||document.getElementsByTagName("body")[0];
};
dojo.html.createNodesFromText=function(txt,trim){
if(trim){
txt=dojo.string.trim(txt);
}
var tn=document.createElement("div");
tn.style.visibility="hidden";
document.body.appendChild(tn);
var _34e="none";
if((/^<t[dh][\s>]/mi).test(dojo.string.trimStart(txt))){
txt="<table><tbody><tr>"+txt+"</tr></tbody></table>";
_34e="cell";
}else{
if((/^<tr[\s>]/mi).test(dojo.string.trimStart(txt))){
txt="<table><tbody>"+txt+"</tbody></table>";
_34e="row";
}else{
if((/^<(thead|tbody|tfoot)[\s>]/mi).test(dojo.string.trimStart(txt))){
txt="<table>"+txt+"</table>";
_34e="section";
}
}
}
tn.innerHTML=txt;
tn.normalize();
var _34f=null;
switch(_34e){
case "cell":
_34f=tn.getElementsByTagName("tr")[0];
break;
case "row":
_34f=tn.getElementsByTagName("tbody")[0];
break;
case "section":
_34f=tn.getElementsByTagName("table")[0];
break;
default:
_34f=tn;
break;
}
var _350=[];
for(var x=0;x<_34f.childNodes.length;x++){
_350.push(_34f.childNodes[x].cloneNode(true));
}
tn.style.display="none";
document.body.removeChild(tn);
return _350;
};
if(!dojo.evalObjPath("dojo.dom.createNodesFromText")){
dojo.dom.createNodesFromText=function(){
dojo.deprecated("dojo.dom.createNodesFromText","use dojo.html.createNodesFromText instead");
return dojo.html.createNodesFromText.apply(dojo.html,arguments);
};
}
dojo.html.isVisible=function(node){
return dojo.style.getComputedStyle(node||this.domNode,"display")!="none";
};
dojo.html.show=function(node){
if(node.style){
node.style.display=dojo.lang.inArray(["tr","td","th"],node.tagName.toLowerCase())?"":"block";
}
};
dojo.html.hide=function(node){
if(node.style){
node.style.display="none";
}
};
dojo.html.toCoordinateArray=function(_355,_356){
if(dojo.lang.isArray(_355)){
while(_355.length<4){
_355.push(0);
}
while(_355.length>4){
_355.pop();
}
var ret=_355;
}else{
var node=dojo.byId(_355);
var ret=[dojo.html.getAbsoluteX(node,_356),dojo.html.getAbsoluteY(node,_356),dojo.html.getInnerWidth(node),dojo.html.getInnerHeight(node)];
}
ret.x=ret[0];
ret.y=ret[1];
ret.w=ret[2];
ret.h=ret[3];
return ret;
};
dojo.html.placeOnScreen=function(node,_35a,_35b,_35c,_35d){
if(dojo.lang.isArray(_35a)){
_35d=_35c;
_35c=_35b;
_35b=_35a[1];
_35a=_35a[0];
}
if(!isNaN(_35c)){
_35c=[Number(_35c),Number(_35c)];
}else{
if(!dojo.lang.isArray(_35c)){
_35c=[0,0];
}
}
var _35e=dojo.html.getScrollOffset();
var view=dojo.html.getViewportSize();
node=dojo.byId(node);
var w=node.offsetWidth+_35c[0];
var h=node.offsetHeight+_35c[1];
if(_35d){
_35a-=_35e.x;
_35b-=_35e.y;
}
var x=_35a+w;
if(x>view.w){
x=view.w-w;
}else{
x=_35a;
}
x=Math.max(_35c[0],x)+_35e.x;
var y=_35b+h;
if(y>view.h){
y=view.h-h;
}else{
y=_35b;
}
y=Math.max(_35c[1],y)+_35e.y;
node.style.left=x+"px";
node.style.top=y+"px";
var ret=[x,y];
ret.x=x;
ret.y=y;
return ret;
};
dojo.html.placeOnScreenPoint=function(node,_366,_367,_368,_369){
if(dojo.lang.isArray(_366)){
_369=_368;
_368=_367;
_367=_366[1];
_366=_366[0];
}
var _36a=dojo.html.getScrollOffset();
var view=dojo.html.getViewportSize();
node=dojo.byId(node);
var w=node.offsetWidth;
var h=node.offsetHeight;
if(_369){
_366-=_36a.x;
_367-=_36a.y;
}
var x=-1,y=-1;
if(_366+w<=view.w&&_367+h<=view.h){
x=_366;
y=_367;
}
if((x<0||y<0)&&_366<=view.w&&_367+h<=view.h){
x=_366-w;
y=_367;
}
if((x<0||y<0)&&_366+w<=view.w&&_367<=view.h){
x=_366;
y=_367-h;
}
if((x<0||y<0)&&_366<=view.w&&_367<=view.h){
x=_366-w;
y=_367-h;
}
if(x<0||y<0||(x+w>view.w)||(y+h>view.h)){
return dojo.html.placeOnScreen(node,_366,_367,_368,_369);
}
x+=_36a.x;
y+=_36a.y;
node.style.left=x+"px";
node.style.top=y+"px";
var ret=[x,y];
ret.x=x;
ret.y=y;
return ret;
};
dojo.html.BackgroundIframe=function(){
if(this.ie){
this.iframe=document.createElement("<iframe frameborder='0' src='about:blank'>");
var s=this.iframe.style;
s.position="absolute";
s.left=s.top="0px";
s.zIndex=2;
s.display="none";
dojo.style.setOpacity(this.iframe,0);
dojo.html.body().appendChild(this.iframe);
}else{
this.enabled=false;
}
};
dojo.lang.extend(dojo.html.BackgroundIframe,{ie:dojo.render.html.ie,enabled:true,visibile:false,iframe:null,sizeNode:null,sizeCoords:null,size:function(node){
if(!this.ie||!this.enabled){
return;
}
if(dojo.dom.isNode(node)){
this.sizeNode=node;
}else{
if(arguments.length>0){
this.sizeNode=null;
this.sizeCoords=node;
}
}
this.update();
},update:function(){
if(!this.ie||!this.enabled){
return;
}
if(this.sizeNode){
this.sizeCoords=dojo.html.toCoordinateArray(this.sizeNode,true);
}else{
if(this.sizeCoords){
this.sizeCoords=dojo.html.toCoordinateArray(this.sizeCoords,true);
}else{
return;
}
}
var s=this.iframe.style;
var dims=this.sizeCoords;
s.width=dims.w+"px";
s.height=dims.h+"px";
s.left=dims.x+"px";
s.top=dims.y+"px";
},setZIndex:function(node){
if(!this.ie||!this.enabled){
return;
}
if(dojo.dom.isNode(node)){
this.iframe.zIndex=dojo.html.getStyle(node,"z-index")-1;
}else{
if(!isNaN(node)){
this.iframe.zIndex=node;
}
}
},show:function(node){
if(!this.ie||!this.enabled){
return;
}
this.size(node);
this.iframe.style.display="block";
},hide:function(){
if(!this.ie){
return;
}
var s=this.iframe.style;
s.display="none";
s.width=s.height="1px";
},remove:function(){
dojo.dom.removeNode(this.iframe);
}});
dojo.provide("dojo.math.curves");
dojo.require("dojo.math");
dojo.math.curves={Line:function(_377,end){
this.start=_377;
this.end=end;
this.dimensions=_377.length;
for(var i=0;i<_377.length;i++){
_377[i]=Number(_377[i]);
}
for(var i=0;i<end.length;i++){
end[i]=Number(end[i]);
}
this.getValue=function(n){
var _37b=new Array(this.dimensions);
for(var i=0;i<this.dimensions;i++){
_37b[i]=((this.end[i]-this.start[i])*n)+this.start[i];
}
return _37b;
};
return this;
},Bezier:function(pnts){
this.getValue=function(step){
if(step>=1){
return this.p[this.p.length-1];
}
if(step<=0){
return this.p[0];
}
var _37f=new Array(this.p[0].length);
for(var k=0;j<this.p[0].length;k++){
_37f[k]=0;
}
for(var j=0;j<this.p[0].length;j++){
var C=0;
var D=0;
for(var i=0;i<this.p.length;i++){
C+=this.p[i][j]*this.p[this.p.length-1][0]*dojo.math.bernstein(step,this.p.length,i);
}
for(var l=0;l<this.p.length;l++){
D+=this.p[this.p.length-1][0]*dojo.math.bernstein(step,this.p.length,l);
}
_37f[j]=C/D;
}
return _37f;
};
this.p=pnts;
return this;
},CatmullRom:function(pnts,c){
this.getValue=function(step){
var _389=step*(this.p.length-1);
var node=Math.floor(_389);
var _38b=_389-node;
var i0=node-1;
if(i0<0){
i0=0;
}
var i=node;
var i1=node+1;
if(i1>=this.p.length){
i1=this.p.length-1;
}
var i2=node+2;
if(i2>=this.p.length){
i2=this.p.length-1;
}
var u=_38b;
var u2=_38b*_38b;
var u3=_38b*_38b*_38b;
var _393=new Array(this.p[0].length);
for(var k=0;k<this.p[0].length;k++){
var x1=(-this.c*this.p[i0][k])+((2-this.c)*this.p[i][k])+((this.c-2)*this.p[i1][k])+(this.c*this.p[i2][k]);
var x2=(2*this.c*this.p[i0][k])+((this.c-3)*this.p[i][k])+((3-2*this.c)*this.p[i1][k])+(-this.c*this.p[i2][k]);
var x3=(-this.c*this.p[i0][k])+(this.c*this.p[i1][k]);
var x4=this.p[i][k];
_393[k]=x1*u3+x2*u2+x3*u+x4;
}
return _393;
};
if(!c){
this.c=0.7;
}else{
this.c=c;
}
this.p=pnts;
return this;
},Arc:function(_399,end,ccw){
var _39c=dojo.math.points.midpoint(_399,end);
var _39d=dojo.math.points.translate(dojo.math.points.invert(_39c),_399);
var rad=Math.sqrt(Math.pow(_39d[0],2)+Math.pow(_39d[1],2));
var _39f=dojo.math.radToDeg(Math.atan(_39d[1]/_39d[0]));
if(_39d[0]<0){
_39f-=90;
}else{
_39f+=90;
}
dojo.math.curves.CenteredArc.call(this,_39c,rad,_39f,_39f+(ccw?-180:180));
},CenteredArc:function(_3a0,_3a1,_3a2,end){
this.center=_3a0;
this.radius=_3a1;
this.start=_3a2||0;
this.end=end;
this.getValue=function(n){
var _3a5=new Array(2);
var _3a6=dojo.math.degToRad(this.start+((this.end-this.start)*n));
_3a5[0]=this.center[0]+this.radius*Math.sin(_3a6);
_3a5[1]=this.center[1]-this.radius*Math.cos(_3a6);
return _3a5;
};
return this;
},Circle:function(_3a7,_3a8){
dojo.math.curves.CenteredArc.call(this,_3a7,_3a8,0,360);
return this;
},Path:function(){
var _3a9=[];
var _3aa=[];
var _3ab=[];
var _3ac=0;
this.add=function(_3ad,_3ae){
if(_3ae<0){
dojo.raise("dojo.math.curves.Path.add: weight cannot be less than 0");
}
_3a9.push(_3ad);
_3aa.push(_3ae);
_3ac+=_3ae;
computeRanges();
};
this.remove=function(_3af){
for(var i=0;i<_3a9.length;i++){
if(_3a9[i]==_3af){
_3a9.splice(i,1);
_3ac-=_3aa.splice(i,1)[0];
break;
}
}
computeRanges();
};
this.removeAll=function(){
_3a9=[];
_3aa=[];
_3ac=0;
};
this.getValue=function(n){
var _3b2=false,value=0;
for(var i=0;i<_3ab.length;i++){
var r=_3ab[i];
if(n>=r[0]&&n<r[1]){
var subN=(n-r[0])/r[2];
value=_3a9[i].getValue(subN);
_3b2=true;
break;
}
}
if(!_3b2){
value=_3a9[_3a9.length-1].getValue(1);
}
for(j=0;j<i;j++){
value=dojo.math.points.translate(value,_3a9[j].getValue(1));
}
return value;
};
function computeRanges(){
var _3b6=0;
for(var i=0;i<_3aa.length;i++){
var end=_3b6+_3aa[i]/_3ac;
var len=end-_3b6;
_3ab[i]=[_3b6,end,len];
_3b6=end;
}
}
return this;
}};
dojo.provide("dojo.animation");
dojo.provide("dojo.animation.Animation");
dojo.require("dojo.lang");
dojo.require("dojo.math");
dojo.require("dojo.math.curves");
dojo.animation.Animation=function(_3ba,_3bb,_3bc,_3bd,rate){
this.curve=_3ba;
this.duration=_3bb;
this.repeatCount=_3bd||0;
this.rate=rate||25;
if(_3bc){
if(dojo.lang.isFunction(_3bc.getValue)){
this.accel=_3bc;
}else{
var i=0.35*_3bc+0.5;
this.accel=new dojo.math.curves.CatmullRom([[0],[i],[1]],0.45);
}
}
};
dojo.lang.extend(dojo.animation.Animation,{curve:null,duration:0,repeatCount:0,accel:null,onBegin:null,onAnimate:null,onEnd:null,onPlay:null,onPause:null,onStop:null,handler:null,_animSequence:null,_startTime:null,_endTime:null,_lastFrame:null,_timer:null,_percent:0,_active:false,_paused:false,_startRepeatCount:0,play:function(_3c0){
if(_3c0){
clearTimeout(this._timer);
this._active=false;
this._paused=false;
this._percent=0;
}else{
if(this._active&&!this._paused){
return;
}
}
this._startTime=new Date().valueOf();
if(this._paused){
this._startTime-=(this.duration*this._percent/100);
}
this._endTime=this._startTime+this.duration;
this._lastFrame=this._startTime;
var e=new dojo.animation.AnimationEvent(this,null,this.curve.getValue(this._percent),this._startTime,this._startTime,this._endTime,this.duration,this._percent,0);
this._active=true;
this._paused=false;
if(this._percent==0){
if(!this._startRepeatCount){
this._startRepeatCount=this.repeatCount;
}
e.type="begin";
if(typeof this.handler=="function"){
this.handler(e);
}
if(typeof this.onBegin=="function"){
this.onBegin(e);
}
}
e.type="play";
if(typeof this.handler=="function"){
this.handler(e);
}
if(typeof this.onPlay=="function"){
this.onPlay(e);
}
if(this._animSequence){
this._animSequence._setCurrent(this);
}
this._cycle();
},pause:function(){
clearTimeout(this._timer);
if(!this._active){
return;
}
this._paused=true;
var e=new dojo.animation.AnimationEvent(this,"pause",this.curve.getValue(this._percent),this._startTime,new Date().valueOf(),this._endTime,this.duration,this._percent,0);
if(typeof this.handler=="function"){
this.handler(e);
}
if(typeof this.onPause=="function"){
this.onPause(e);
}
},playPause:function(){
if(!this._active||this._paused){
this.play();
}else{
this.pause();
}
},gotoPercent:function(pct,_3c4){
clearTimeout(this._timer);
this._active=true;
this._paused=true;
this._percent=pct;
if(_3c4){
this.play();
}
},stop:function(_3c5){
clearTimeout(this._timer);
var step=this._percent/100;
if(_3c5){
step=1;
}
var e=new dojo.animation.AnimationEvent(this,"stop",this.curve.getValue(step),this._startTime,new Date().valueOf(),this._endTime,this.duration,this._percent,Math.round(fps));
if(typeof this.handler=="function"){
this.handler(e);
}
if(typeof this.onStop=="function"){
this.onStop(e);
}
this._active=false;
this._paused=false;
},status:function(){
if(this._active){
return this._paused?"paused":"playing";
}else{
return "stopped";
}
},_cycle:function(){
clearTimeout(this._timer);
if(this._active){
var curr=new Date().valueOf();
var step=(curr-this._startTime)/(this._endTime-this._startTime);
fps=1000/(curr-this._lastFrame);
this._lastFrame=curr;
if(step>=1){
step=1;
this._percent=100;
}else{
this._percent=step*100;
}
if(this.accel&&this.accel.getValue){
step=this.accel.getValue(step);
}
var e=new dojo.animation.AnimationEvent(this,"animate",this.curve.getValue(step),this._startTime,curr,this._endTime,this.duration,this._percent,Math.round(fps));
if(typeof this.handler=="function"){
this.handler(e);
}
if(typeof this.onAnimate=="function"){
this.onAnimate(e);
}
if(step<1){
this._timer=setTimeout(dojo.lang.hitch(this,"_cycle"),this.rate);
}else{
e.type="end";
this._active=false;
if(typeof this.handler=="function"){
this.handler(e);
}
if(typeof this.onEnd=="function"){
this.onEnd(e);
}
if(this.repeatCount>0){
this.repeatCount--;
this.play(true);
}else{
if(this.repeatCount==-1){
this.play(true);
}else{
if(this._startRepeatCount){
this.repeatCount=this._startRepeatCount;
this._startRepeatCount=0;
}
if(this._animSequence){
this._animSequence._playNext();
}
}
}
}
}
}});
dojo.animation.AnimationEvent=function(anim,type,_3cd,_3ce,_3cf,_3d0,dur,pct,fps){
this.type=type;
this.animation=anim;
this.coords=_3cd;
this.x=_3cd[0];
this.y=_3cd[1];
this.z=_3cd[2];
this.startTime=_3ce;
this.currentTime=_3cf;
this.endTime=_3d0;
this.duration=dur;
this.percent=pct;
this.fps=fps;
};
dojo.lang.extend(dojo.animation.AnimationEvent,{coordsAsInts:function(){
var _3d4=new Array(this.coords.length);
for(var i=0;i<this.coords.length;i++){
_3d4[i]=Math.round(this.coords[i]);
}
return _3d4;
}});
dojo.animation.AnimationSequence=function(_3d6){
this.repeatCount=_3d6||0;
};
dojo.lang.extend(dojo.animation.AnimationSequence,{repeateCount:0,_anims:[],_currAnim:-1,onBegin:null,onEnd:null,onNext:null,handler:null,add:function(){
for(var i=0;i<arguments.length;i++){
this._anims.push(arguments[i]);
arguments[i]._animSequence=this;
}
},remove:function(anim){
for(var i=0;i<this._anims.length;i++){
if(this._anims[i]==anim){
this._anims[i]._animSequence=null;
this._anims.splice(i,1);
break;
}
}
},removeAll:function(){
for(var i=0;i<this._anims.length;i++){
this._anims[i]._animSequence=null;
}
this._anims=[];
this._currAnim=-1;
},clear:function(){
this.removeAll();
},play:function(_3db){
if(this._anims.length==0){
return;
}
if(_3db||!this._anims[this._currAnim]){
this._currAnim=0;
}
if(this._anims[this._currAnim]){
if(this._currAnim==0){
var e={type:"begin",animation:this._anims[this._currAnim]};
if(typeof this.handler=="function"){
this.handler(e);
}
if(typeof this.onBegin=="function"){
this.onBegin(e);
}
}
this._anims[this._currAnim].play(_3db);
}
},pause:function(){
if(this._anims[this._currAnim]){
this._anims[this._currAnim].pause();
}
},playPause:function(){
if(this._anims.length==0){
return;
}
if(this._currAnim==-1){
this._currAnim=0;
}
if(this._anims[this._currAnim]){
this._anims[this._currAnim].playPause();
}
},stop:function(){
if(this._anims[this._currAnim]){
this._anims[this._currAnim].stop();
}
},status:function(){
if(this._anims[this._currAnim]){
return this._anims[this._currAnim].status();
}else{
return "stopped";
}
},_setCurrent:function(anim){
for(var i=0;i<this._anims.length;i++){
if(this._anims[i]==anim){
this._currAnim=i;
break;
}
}
},_playNext:function(){
if(this._currAnim==-1||this._anims.length==0){
return;
}
this._currAnim++;
if(this._anims[this._currAnim]){
var e={type:"next",animation:this._anims[this._currAnim]};
if(typeof this.handler=="function"){
this.handler(e);
}
if(typeof this.onNext=="function"){
this.onNext(e);
}
this._anims[this._currAnim].play(true);
}else{
var e={type:"end",animation:this._anims[this._anims.length-1]};
if(typeof this.handler=="function"){
this.handler(e);
}
if(typeof this.onEnd=="function"){
this.onEnd(e);
}
if(this.repeatCount>0){
this._currAnim=0;
this.repeatCount--;
this._anims[this._currAnim].play(true);
}else{
if(this.repeatCount==-1){
this._currAnim=0;
this._anims[this._currAnim].play(true);
}else{
this._currAnim=-1;
}
}
}
}});
dojo.hostenv.conditionalLoadModule({common:["dojo.animation.Animation",false,false]});
dojo.hostenv.moduleLoaded("dojo.animation.*");
dojo.provide("dojo.fx.html");
dojo.require("dojo.html");
dojo.require("dojo.style");
dojo.require("dojo.lang");
dojo.require("dojo.animation.*");
dojo.require("dojo.event.*");
dojo.require("dojo.graphics.color");
dojo.fx.html._makeFadeable=function(node){
if(dojo.render.html.ie){
if((node.style.zoom.length==0)&&(dojo.style.getStyle(node,"zoom")=="normal")){
node.style.zoom="1";
}
if((node.style.width.length==0)&&(dojo.style.getStyle(node,"width")=="auto")){
node.style.width="auto";
}
}
};
dojo.fx.html.fadeOut=function(node,_3e2,_3e3,_3e4){
return dojo.fx.html.fade(node,_3e2,dojo.style.getOpacity(node),0,_3e3,_3e4);
};
dojo.fx.html.fadeIn=function(node,_3e6,_3e7,_3e8){
return dojo.fx.html.fade(node,_3e6,dojo.style.getOpacity(node),1,_3e7,_3e8);
};
dojo.fx.html.fadeHide=function(node,_3ea,_3eb,_3ec){
node=dojo.byId(node);
if(!_3ea){
_3ea=150;
}
return dojo.fx.html.fadeOut(node,_3ea,function(node){
node.style.display="none";
if(typeof _3eb=="function"){
_3eb(node);
}
});
};
dojo.fx.html.fadeShow=function(node,_3ef,_3f0,_3f1){
node=dojo.byId(node);
if(!_3ef){
_3ef=150;
}
node.style.display="block";
return dojo.fx.html.fade(node,_3ef,0,1,_3f0,_3f1);
};
dojo.fx.html.fade=function(node,_3f3,_3f4,_3f5,_3f6,_3f7){
node=dojo.byId(node);
dojo.fx.html._makeFadeable(node);
var anim=new dojo.animation.Animation(new dojo.math.curves.Line([_3f4],[_3f5]),_3f3,0);
dojo.event.connect(anim,"onAnimate",function(e){
dojo.style.setOpacity(node,e.x);
});
if(_3f6){
dojo.event.connect(anim,"onEnd",function(e){
_3f6(node,anim);
});
}
if(!_3f7){
anim.play(true);
}
return anim;
};
dojo.fx.html.slideTo=function(node,_3fc,_3fd,_3fe,_3ff){
if(!dojo.lang.isNumber(_3fc)){
var tmp=_3fc;
_3fc=_3fd;
_3fd=tmp;
}
node=dojo.byId(node);
var top=node.offsetTop;
var left=node.offsetLeft;
var pos=dojo.style.getComputedStyle(node,"position");
if(pos=="relative"||pos=="static"){
top=parseInt(dojo.style.getComputedStyle(node,"top"))||0;
left=parseInt(dojo.style.getComputedStyle(node,"left"))||0;
}
return dojo.fx.html.slide(node,_3fc,[left,top],_3fd,_3fe,_3ff);
};
dojo.fx.html.slideBy=function(node,_405,_406,_407,_408){
if(!dojo.lang.isNumber(_405)){
var tmp=_405;
_405=_406;
_406=tmp;
}
node=dojo.byId(node);
var top=node.offsetTop;
var left=node.offsetLeft;
var pos=dojo.style.getComputedStyle(node,"position");
if(pos=="relative"||pos=="static"){
top=parseInt(dojo.style.getComputedStyle(node,"top"))||0;
left=parseInt(dojo.style.getComputedStyle(node,"left"))||0;
}
return dojo.fx.html.slideTo(node,_405,[left+_406[0],top+_406[1]],_407,_408);
};
dojo.fx.html.slide=function(node,_40e,_40f,_410,_411,_412){
if(!dojo.lang.isNumber(_40e)){
var tmp=_40e;
_40e=_410;
_410=_40f;
_40f=tmp;
}
node=dojo.byId(node);
if(dojo.style.getComputedStyle(node,"position")=="static"){
node.style.position="relative";
}
var anim=new dojo.animation.Animation(new dojo.math.curves.Line(_40f,_410),_40e,0);
dojo.event.connect(anim,"onAnimate",function(e){
with(node.style){
left=e.x+"px";
top=e.y+"px";
}
});
if(_411){
dojo.event.connect(anim,"onEnd",function(e){
_411(node,anim);
});
}
if(!_412){
anim.play(true);
}
return anim;
};
dojo.fx.html.colorFadeIn=function(node,_418,_419,_41a,_41b,_41c){
if(!dojo.lang.isNumber(_418)){
var tmp=_418;
_418=_419;
_419=tmp;
}
node=dojo.byId(node);
var _41e=dojo.html.getBackgroundColor(node);
var bg=dojo.style.getStyle(node,"background-color").toLowerCase();
var _420=bg=="transparent"||bg=="rgba(0, 0, 0, 0)";
while(_41e.length>3){
_41e.pop();
}
var rgb=new dojo.graphics.color.Color(_419).toRgb();
var anim=dojo.fx.html.colorFade(node,_418,_419,_41e,_41b,true);
dojo.event.connect(anim,"onEnd",function(e){
if(_420){
node.style.backgroundColor="transparent";
}
});
if(_41a>0){
node.style.backgroundColor="rgb("+rgb.join(",")+")";
if(!_41c){
setTimeout(function(){
anim.play(true);
},_41a);
}
}else{
if(!_41c){
anim.play(true);
}
}
return anim;
};
dojo.fx.html.highlight=dojo.fx.html.colorFadeIn;
dojo.fx.html.colorFadeFrom=dojo.fx.html.colorFadeIn;
dojo.fx.html.colorFadeOut=function(node,_425,_426,_427,_428,_429){
if(!dojo.lang.isNumber(_425)){
var tmp=_425;
_425=_426;
_426=tmp;
}
node=dojo.byId(node);
var _42b=new dojo.graphics.color.Color(dojo.html.getBackgroundColor(node)).toRgb();
var rgb=new dojo.graphics.color.Color(_426).toRgb();
var anim=dojo.fx.html.colorFade(node,_425,_42b,rgb,_428,_427>0||_429);
if(_427>0){
node.style.backgroundColor="rgb("+_42b.join(",")+")";
if(!_429){
setTimeout(function(){
anim.play(true);
},_427);
}
}
return anim;
};
dojo.fx.html.unhighlight=dojo.fx.html.colorFadeOut;
dojo.fx.html.colorFadeTo=dojo.fx.html.colorFadeOut;
dojo.fx.html.colorFade=function(node,_42f,_430,_431,_432,_433){
if(!dojo.lang.isNumber(_42f)){
var tmp=_42f;
_42f=_431;
_431=_430;
_430=tmp;
}
node=dojo.byId(node);
var _435=new dojo.graphics.color.Color(_430).toRgb();
var _436=new dojo.graphics.color.Color(_431).toRgb();
var anim=new dojo.animation.Animation(new dojo.math.curves.Line(_435,_436),_42f,0);
dojo.event.connect(anim,"onAnimate",function(e){
node.style.backgroundColor="rgb("+e.coordsAsInts().join(",")+")";
});
if(_432){
dojo.event.connect(anim,"onEnd",function(e){
_432(node,anim);
});
}
if(!_433){
anim.play(true);
}
return anim;
};
dojo.fx.html.wipeIn=function(node,_43b,_43c,_43d){
node=dojo.byId(node);
var _43e=dojo.html.getStyle(node,"height");
var _43f=dojo.lang.inArray(node.tagName.toLowerCase(),["tr","td","th"])?"":"block";
node.style.display=_43f;
var _440=node.offsetHeight;
var anim=dojo.fx.html.wipeInToHeight(node,_43b,_440,function(e){
node.style.height=_43e||"auto";
if(_43c){
_43c(node,anim);
}
},_43d);
};
dojo.fx.html.wipeInToHeight=function(node,_444,_445,_446,_447){
node=dojo.byId(node);
var _448=dojo.html.getStyle(node,"overflow");
node.style.height="0px";
node.style.display="none";
if(_448=="visible"){
node.style.overflow="hidden";
}
var _449=dojo.lang.inArray(node.tagName.toLowerCase(),["tr","td","th"])?"":"block";
node.style.display=_449;
var anim=new dojo.animation.Animation(new dojo.math.curves.Line([0],[_445]),_444,0);
dojo.event.connect(anim,"onAnimate",function(e){
node.style.height=Math.round(e.x)+"px";
});
dojo.event.connect(anim,"onEnd",function(e){
if(_448!="visible"){
node.style.overflow=_448;
}
if(_446){
_446(node,anim);
}
});
if(!_447){
anim.play(true);
}
return anim;
};
dojo.fx.html.wipeOut=function(node,_44e,_44f,_450){
node=dojo.byId(node);
var _451=dojo.html.getStyle(node,"overflow");
var _452=dojo.html.getStyle(node,"height");
var _453=node.offsetHeight;
node.style.overflow="hidden";
var anim=new dojo.animation.Animation(new dojo.math.curves.Line([_453],[0]),_44e,0);
dojo.event.connect(anim,"onAnimate",function(e){
node.style.height=Math.round(e.x)+"px";
});
dojo.event.connect(anim,"onEnd",function(e){
node.style.display="none";
node.style.overflow=_451;
node.style.height=_452||"auto";
if(_44f){
_44f(node,anim);
}
});
if(!_450){
anim.play(true);
}
return anim;
};
dojo.fx.html.explode=function(_457,_458,_459,_45a,_45b){
var _45c=dojo.html.toCoordinateArray(_457);
var _45d=document.createElement("div");
with(_45d.style){
position="absolute";
border="1px solid black";
display="none";
}
dojo.html.body().appendChild(_45d);
_458=dojo.byId(_458);
with(_458.style){
visibility="hidden";
display="block";
}
var _45e=dojo.html.toCoordinateArray(_458);
with(_458.style){
display="none";
visibility="visible";
}
var anim=new dojo.animation.Animation(new dojo.math.curves.Line(_45c,_45e),_459,0);
dojo.event.connect(anim,"onBegin",function(e){
_45d.style.display="block";
});
dojo.event.connect(anim,"onAnimate",function(e){
with(_45d.style){
left=e.x+"px";
top=e.y+"px";
width=e.coords[2]+"px";
height=e.coords[3]+"px";
}
});
dojo.event.connect(anim,"onEnd",function(){
_458.style.display="block";
_45d.parentNode.removeChild(_45d);
if(_45a){
_45a(_458,anim);
}
});
if(!_45b){
anim.play();
}
return anim;
};
dojo.fx.html.implode=function(_462,end,_464,_465,_466){
var _467=dojo.html.toCoordinateArray(_462);
var _468=dojo.html.toCoordinateArray(end);
_462=dojo.byId(_462);
var _469=document.createElement("div");
with(_469.style){
position="absolute";
border="1px solid black";
display="none";
}
dojo.html.body().appendChild(_469);
var anim=new dojo.animation.Animation(new dojo.math.curves.Line(_467,_468),_464,0);
dojo.event.connect(anim,"onBegin",function(e){
_462.style.display="none";
_469.style.display="block";
});
dojo.event.connect(anim,"onAnimate",function(e){
with(_469.style){
left=e.x+"px";
top=e.y+"px";
width=e.coords[2]+"px";
height=e.coords[3]+"px";
}
});
dojo.event.connect(anim,"onEnd",function(){
_469.parentNode.removeChild(_469);
if(_465){
_465(_462,anim);
}
});
if(!_466){
anim.play();
}
return anim;
};
dojo.fx.html.Exploder=function(_46d,_46e){
_46d=dojo.byId(_46d);
_46e=dojo.byId(_46e);
var _46f=this;
this.waitToHide=500;
this.timeToShow=100;
this.waitToShow=200;
this.timeToHide=70;
this.autoShow=false;
this.autoHide=false;
var _470=null;
var _471=null;
var _472=null;
var _473=null;
var _474=null;
var _475=null;
this.showing=false;
this.onBeforeExplode=null;
this.onAfterExplode=null;
this.onBeforeImplode=null;
this.onAfterImplode=null;
this.onExploding=null;
this.onImploding=null;
this.timeShow=function(){
clearTimeout(_472);
_472=setTimeout(_46f.show,_46f.waitToShow);
};
this.show=function(){
clearTimeout(_472);
clearTimeout(_473);
if((_471&&_471.status()=="playing")||(_470&&_470.status()=="playing")||_46f.showing){
return;
}
if(typeof _46f.onBeforeExplode=="function"){
_46f.onBeforeExplode(_46d,_46e);
}
_470=dojo.fx.html.explode(_46d,_46e,_46f.timeToShow,function(e){
_46f.showing=true;
if(typeof _46f.onAfterExplode=="function"){
_46f.onAfterExplode(_46d,_46e);
}
});
if(typeof _46f.onExploding=="function"){
dojo.event.connect(_470,"onAnimate",this,"onExploding");
}
};
this.timeHide=function(){
clearTimeout(_472);
clearTimeout(_473);
if(_46f.showing){
_473=setTimeout(_46f.hide,_46f.waitToHide);
}
};
this.hide=function(){
clearTimeout(_472);
clearTimeout(_473);
if(_470&&_470.status()=="playing"){
return;
}
_46f.showing=false;
if(typeof _46f.onBeforeImplode=="function"){
_46f.onBeforeImplode(_46d,_46e);
}
_471=dojo.fx.html.implode(_46e,_46d,_46f.timeToHide,function(e){
if(typeof _46f.onAfterImplode=="function"){
_46f.onAfterImplode(_46d,_46e);
}
});
if(typeof _46f.onImploding=="function"){
dojo.event.connect(_471,"onAnimate",this,"onImploding");
}
};
dojo.event.connect(_46d,"onclick",function(e){
if(_46f.showing){
_46f.hide();
}else{
_46f.show();
}
});
dojo.event.connect(_46d,"onmouseover",function(e){
if(_46f.autoShow){
_46f.timeShow();
}
});
dojo.event.connect(_46d,"onmouseout",function(e){
if(_46f.autoHide){
_46f.timeHide();
}
});
dojo.event.connect(_46e,"onmouseover",function(e){
clearTimeout(_473);
});
dojo.event.connect(_46e,"onmouseout",function(e){
if(_46f.autoHide){
_46f.timeHide();
}
});
dojo.event.connect(document.documentElement||dojo.html.body(),"onclick",function(e){
if(_46f.autoHide&&_46f.showing&&!dojo.dom.isDescendantOf(e.target,_46e)&&!dojo.dom.isDescendantOf(e.target,_46d)){
_46f.hide();
}
});
return this;
};
dojo.lang.mixin(dojo.fx,dojo.fx.html);
dojo.hostenv.conditionalLoadModule({browser:["dojo.fx.html"]});
dojo.hostenv.moduleLoaded("dojo.fx.*");
dojo.provide("dojo.graphics.htmlEffects");
dojo.require("dojo.fx.*");
dj_deprecated("dojo.graphics.htmlEffects is deprecated, use dojo.fx.html instead");
dojo.graphics.htmlEffects=dojo.fx.html;
dojo.hostenv.conditionalLoadModule({browser:["dojo.graphics.htmlEffects"]});
dojo.hostenv.moduleLoaded("dojo.graphics.*");
dojo.provide("dojo.xml.Parse");
dojo.require("dojo.dom");
dojo.xml.Parse=function(){
this.parseFragment=function(_47e){
var _47f={};
var _480=dojo.dom.getTagName(_47e);
_47f[_480]=new Array(_47e.tagName);
var _481=this.parseAttributes(_47e);
for(var attr in _481){
if(!_47f[attr]){
_47f[attr]=[];
}
_47f[attr][_47f[attr].length]=_481[attr];
}
var _483=_47e.childNodes;
for(var _484 in _483){
switch(_483[_484].nodeType){
case dojo.dom.ELEMENT_NODE:
_47f[_480].push(this.parseElement(_483[_484]));
break;
case dojo.dom.TEXT_NODE:
if(_483.length==1){
if(!_47f[_47e.tagName]){
_47f[_480]=[];
}
_47f[_480].push({value:_483[0].nodeValue});
}
break;
}
}
return _47f;
};
this.parseElement=function(node,_486,_487,_488){
var _489={};
var _48a=dojo.dom.getTagName(node);
_489[_48a]=[];
if((!_487)||(_48a.substr(0,4).toLowerCase()=="dojo")){
var _48b=this.parseAttributes(node);
for(var attr in _48b){
if((!_489[_48a][attr])||(typeof _489[_48a][attr]!="array")){
_489[_48a][attr]=[];
}
_489[_48a][attr].push(_48b[attr]);
}
_489[_48a].nodeRef=node;
_489.tagName=_48a;
_489.index=_488||0;
}
var _48d=0;
for(var i=0;i<node.childNodes.length;i++){
var tcn=node.childNodes.item(i);
switch(tcn.nodeType){
case dojo.dom.ELEMENT_NODE:
_48d++;
var ctn=dojo.dom.getTagName(tcn);
if(!_489[ctn]){
_489[ctn]=[];
}
_489[ctn].push(this.parseElement(tcn,true,_487,_48d));
if((tcn.childNodes.length==1)&&(tcn.childNodes.item(0).nodeType==dojo.dom.TEXT_NODE)){
_489[ctn][_489[ctn].length-1].value=tcn.childNodes.item(0).nodeValue;
}
break;
case dojo.dom.TEXT_NODE:
if(node.childNodes.length==1){
_489[_48a].push({value:node.childNodes.item(0).nodeValue});
}
break;
default:
break;
}
}
return _489;
};
this.parseAttributes=function(node){
var _492={};
var atts=node.attributes;
for(var i=0;i<atts.length;i++){
var _495=atts.item(i);
if((dojo.render.html.capable)&&(dojo.render.html.ie)){
if(!_495){
continue;
}
if((typeof _495=="object")&&(typeof _495.nodeValue=="undefined")||(_495.nodeValue==null)||(_495.nodeValue=="")){
continue;
}
}
var nn=(_495.nodeName.indexOf("dojo:")==-1)?_495.nodeName:_495.nodeName.split("dojo:")[1];
_492[nn]={value:_495.nodeValue};
}
return _492;
};
};
dojo.provide("dojo.widget.Manager");
dojo.require("dojo.lang");
dojo.require("dojo.event.*");
dojo.widget.manager=new function(){
this.widgets=[];
this.widgetIds=[];
this.topWidgets={};
var _497={};
var _498=[];
this.getUniqueId=function(_499){
return _499+"_"+(_497[_499]!=undefined?++_497[_499]:_497[_499]=0);
};
this.add=function(_49a){
dojo.profile.start("dojo.widget.manager.add");
this.widgets.push(_49a);
if(_49a.widgetId==""){
if(_49a["id"]){
_49a.widgetId=_49a["id"];
}else{
if(_49a.extraArgs["id"]){
_49a.widgetId=_49a.extraArgs["id"];
}else{
_49a.widgetId=this.getUniqueId(_49a.widgetType);
}
}
}
if(this.widgetIds[_49a.widgetId]){
dojo.debug("widget ID collision on ID: "+_49a.widgetId);
}
this.widgetIds[_49a.widgetId]=_49a;
dojo.profile.end("dojo.widget.manager.add");
};
this.destroyAll=function(){
for(var x=this.widgets.length-1;x>=0;x--){
try{
this.widgets[x].destroy(true);
delete this.widgets[x];
}
catch(e){
}
}
};
this.remove=function(_49c){
var tw=this.widgets[_49c].widgetId;
delete this.widgetIds[tw];
this.widgets.splice(_49c,1);
};
this.removeById=function(id){
for(var i=0;i<this.widgets.length;i++){
if(this.widgets[i].widgetId==id){
this.remove(i);
break;
}
}
};
this.getWidgetById=function(id){
return this.widgetIds[id];
};
this.getWidgetsByType=function(type){
var lt=type.toLowerCase();
var ret=[];
dojo.lang.forEach(this.widgets,function(x){
if(x.widgetType.toLowerCase()==lt){
ret.push(x);
}
});
return ret;
};
this.getWidgetsOfType=function(id){
dj_deprecated("getWidgetsOfType is depecrecated, use getWidgetsByType");
return dojo.widget.manager.getWidgetsByType(id);
};
this.getWidgetsByFilter=function(_4a6){
var ret=[];
dojo.lang.forEach(this.widgets,function(x){
if(_4a6(x)){
ret.push(x);
}
});
return ret;
};
this.getAllWidgets=function(){
return this.widgets.concat();
};
this.byId=this.getWidgetById;
this.byType=this.getWidgetsByType;
this.byFilter=this.getWidgetsByFilter;
var _4a9={};
var _4aa=["dojo.widget","dojo.webui.widgets"];
for(var i=0;i<_4aa.length;i++){
_4aa[_4aa[i]]=true;
}
this.registerWidgetPackage=function(_4ac){
if(!_4aa[_4ac]){
_4aa[_4ac]=true;
_4aa.push(_4ac);
}
};
this.getWidgetPackageList=function(){
return dojo.lang.map(_4aa,function(elt){
return (elt!==true?elt:undefined);
});
};
this.getImplementation=function(_4ae,_4af,_4b0){
var impl=this.getImplementationName(_4ae);
if(impl){
var ret=new impl(_4af);
return ret;
}
};
this.getImplementationName=function(_4b3){
var _4b4=_4b3.toLowerCase();
var impl=_4a9[_4b4];
if(impl){
return impl;
}
if(!_498.length){
for(var _4b6 in dojo.render){
if(dojo.render[_4b6]["capable"]===true){
var _4b7=dojo.render[_4b6].prefixes;
for(var i=0;i<_4b7.length;i++){
_498.push(_4b7[i].toLowerCase());
}
}
}
_498.push("");
}
for(var i=0;i<_4aa.length;i++){
var _4b9=dojo.evalObjPath(_4aa[i]);
if(!_4b9){
continue;
}
for(var j=0;j<_498.length;j++){
if(!_4b9[_498[j]]){
continue;
}
for(var _4bb in _4b9[_498[j]]){
if(_4bb.toLowerCase()!=_4b4){
continue;
}
_4a9[_4b4]=_4b9[_498[j]][_4bb];
return _4a9[_4b4];
}
}
for(var j=0;j<_498.length;j++){
for(var _4bb in _4b9){
if(_4bb.toLowerCase()!=(_498[j]+_4b4)){
continue;
}
_4a9[_4b4]=_4b9[_4bb];
return _4a9[_4b4];
}
}
}
throw new Error("Could not locate \""+_4b3+"\" class");
};
this.resizing=false;
this.onResized=function(){
if(this.resizing){
return;
}
try{
this.resizing=true;
for(var id in this.topWidgets){
var _4bd=this.topWidgets[id];
if(_4bd.onResized){
_4bd.onResized();
}
}
}
finally{
this.resizing=false;
}
};
if(typeof window!="undefined"){
dojo.addOnLoad(this,"onResized");
dojo.event.connect(window,"onresize",this,"onResized");
}
};
dojo.widget.getUniqueId=function(){
return dojo.widget.manager.getUniqueId.apply(dojo.widget.manager,arguments);
};
dojo.widget.addWidget=function(){
return dojo.widget.manager.add.apply(dojo.widget.manager,arguments);
};
dojo.widget.destroyAllWidgets=function(){
return dojo.widget.manager.destroyAll.apply(dojo.widget.manager,arguments);
};
dojo.widget.removeWidget=function(){
return dojo.widget.manager.remove.apply(dojo.widget.manager,arguments);
};
dojo.widget.removeWidgetById=function(){
return dojo.widget.manager.removeById.apply(dojo.widget.manager,arguments);
};
dojo.widget.getWidgetById=function(){
return dojo.widget.manager.getWidgetById.apply(dojo.widget.manager,arguments);
};
dojo.widget.getWidgetsByType=function(){
return dojo.widget.manager.getWidgetsByType.apply(dojo.widget.manager,arguments);
};
dojo.widget.getWidgetsByFilter=function(){
return dojo.widget.manager.getWidgetsByFilter.apply(dojo.widget.manager,arguments);
};
dojo.widget.byId=function(){
return dojo.widget.manager.getWidgetById.apply(dojo.widget.manager,arguments);
};
dojo.widget.byType=function(){
return dojo.widget.manager.getWidgetsByType.apply(dojo.widget.manager,arguments);
};
dojo.widget.byFilter=function(){
return dojo.widget.manager.getWidgetsByFilter.apply(dojo.widget.manager,arguments);
};
dojo.widget.all=function(n){
var _4bf=dojo.widget.manager.getAllWidgets.apply(dojo.widget.manager,arguments);
if(arguments.length>0){
return _4bf[n];
}
return _4bf;
};
dojo.widget.registerWidgetPackage=function(){
return dojo.widget.manager.registerWidgetPackage.apply(dojo.widget.manager,arguments);
};
dojo.widget.getWidgetImplementation=function(){
return dojo.widget.manager.getImplementation.apply(dojo.widget.manager,arguments);
};
dojo.widget.getWidgetImplementationName=function(){
return dojo.widget.manager.getImplementationName.apply(dojo.widget.manager,arguments);
};
dojo.widget.widgets=dojo.widget.manager.widgets;
dojo.widget.widgetIds=dojo.widget.manager.widgetIds;
dojo.widget.root=dojo.widget.manager.root;
dojo.provide("dojo.widget.Widget");
dojo.provide("dojo.widget.tags");
dojo.require("dojo.lang");
dojo.require("dojo.widget.Manager");
dojo.require("dojo.event.*");
dojo.require("dojo.string");
dojo.widget.Widget=function(){
this.children=[];
this.extraArgs={};
};
dojo.lang.extend(dojo.widget.Widget,{parent:null,isTopLevel:false,isModal:false,isEnabled:true,isHidden:false,isContainer:false,widgetId:"",widgetType:"Widget",toString:function(){
return "[Widget "+this.widgetType+", "+(this.widgetId||"NO ID")+"]";
},repr:function(){
return this.toString();
},enable:function(){
this.isEnabled=true;
},disable:function(){
this.isEnabled=false;
},hide:function(){
this.isHidden=true;
},show:function(){
this.isHidden=false;
},create:function(args,_4c1,_4c2){
this.satisfyPropertySets(args,_4c1,_4c2);
this.mixInProperties(args,_4c1,_4c2);
this.postMixInProperties(args,_4c1,_4c2);
dojo.widget.manager.add(this);
this.buildRendering(args,_4c1,_4c2);
this.initialize(args,_4c1,_4c2);
this.postInitialize(args,_4c1,_4c2);
this.postCreate(args,_4c1,_4c2);
return this;
},destroy:function(_4c3){
this.uninitialize();
this.destroyRendering(_4c3);
dojo.widget.manager.removeById(this.widgetId);
},destroyChildren:function(_4c4){
_4c4=(!_4c4)?function(){
return true;
}:_4c4;
for(var x=0;x<this.children.length;x++){
var tc=this.children[x];
if((tc)&&(_4c4(tc))){
tc.destroy();
}
}
},destroyChildrenOfType:function(type){
type=type.toLowerCase();
this.destroyChildren(function(item){
if(item.widgetType.toLowerCase()==type){
return true;
}else{
return false;
}
});
},getChildrenOfType:function(type,_4ca){
var ret=[];
type=type.toLowerCase();
for(var x=0;x<this.children.length;x++){
if(this.children[x].widgetType.toLowerCase()==type){
ret.push(this.children[x]);
}
if(_4ca){
ret=ret.concat(this.children[x].getChildrenOfType(type,_4ca));
}
}
return ret;
},satisfyPropertySets:function(args){
return args;
},mixInProperties:function(args,frag){
if((args["fastMixIn"])||(frag["fastMixIn"])){
for(var x in args){
this[x]=args[x];
}
return;
}
var _4d1;
var _4d2=dojo.widget.lcArgsCache[this.widgetType];
if(_4d2==null){
_4d2={};
for(var y in this){
_4d2[((new String(y)).toLowerCase())]=y;
}
dojo.widget.lcArgsCache[this.widgetType]=_4d2;
}
var _4d4={};
for(var x in args){
if(!this[x]){
var y=_4d2[(new String(x)).toLowerCase()];
if(y){
args[y]=args[x];
x=y;
}
}
if(_4d4[x]){
continue;
}
_4d4[x]=true;
if((typeof this[x])!=(typeof _4d1)){
if(typeof args[x]!="string"){
this[x]=args[x];
}else{
if(dojo.lang.isString(this[x])){
this[x]=args[x];
}else{
if(dojo.lang.isNumber(this[x])){
this[x]=new Number(args[x]);
}else{
if(dojo.lang.isBoolean(this[x])){
this[x]=(args[x].toLowerCase()=="false")?false:true;
}else{
if(dojo.lang.isFunction(this[x])){
var tn=dojo.lang.nameAnonFunc(new Function(args[x]),this);
dojo.event.connect(this,x,this,tn);
}else{
if(dojo.lang.isArray(this[x])){
this[x]=args[x].split(";");
}else{
if(this[x] instanceof Date){
this[x]=new Date(Number(args[x]));
}else{
if(typeof this[x]=="object"){
var _4d6=args[x].split(";");
for(var y=0;y<_4d6.length;y++){
var si=_4d6[y].indexOf(":");
if((si!=-1)&&(_4d6[y].length>si)){
this[x][dojo.string.trim(_4d6[y].substr(0,si))]=_4d6[y].substr(si+1);
}
}
}else{
this[x]=args[x];
}
}
}
}
}
}
}
}
}else{
this.extraArgs[x]=args[x];
}
}
},postMixInProperties:function(){
},initialize:function(args,frag){
return false;
},postInitialize:function(args,frag){
return false;
},postCreate:function(args,frag){
return false;
},uninitialize:function(){
return false;
},buildRendering:function(){
dj_unimplemented("dojo.widget.Widget.buildRendering, on "+this.toString()+", ");
return false;
},destroyRendering:function(){
dj_unimplemented("dojo.widget.Widget.destroyRendering");
return false;
},cleanUp:function(){
dj_unimplemented("dojo.widget.Widget.cleanUp");
return false;
},addedTo:function(_4de){
},addChild:function(_4df){
dj_unimplemented("dojo.widget.Widget.addChild");
return false;
},addChildAtIndex:function(_4e0,_4e1){
dj_unimplemented("dojo.widget.Widget.addChildAtIndex");
return false;
},removeChild:function(_4e2){
dj_unimplemented("dojo.widget.Widget.removeChild");
return false;
},removeChildAtIndex:function(_4e3){
dj_unimplemented("dojo.widget.Widget.removeChildAtIndex");
return false;
},resize:function(_4e4,_4e5){
this.setWidth(_4e4);
this.setHeight(_4e5);
},setWidth:function(_4e6){
if((typeof _4e6=="string")&&(_4e6.substr(-1)=="%")){
this.setPercentageWidth(_4e6);
}else{
this.setNativeWidth(_4e6);
}
},setHeight:function(_4e7){
if((typeof _4e7=="string")&&(_4e7.substr(-1)=="%")){
this.setPercentageHeight(_4e7);
}else{
this.setNativeHeight(_4e7);
}
},setPercentageHeight:function(_4e8){
return false;
},setNativeHeight:function(_4e9){
return false;
},setPercentageWidth:function(_4ea){
return false;
},setNativeWidth:function(_4eb){
return false;
}});
dojo.widget.lcArgsCache={};
dojo.widget.tags={};
dojo.widget.tags.addParseTreeHandler=function(type){
var _4ed=type.toLowerCase();
this[_4ed]=function(_4ee,_4ef,_4f0,_4f1){
return dojo.widget.buildWidgetFromParseTree(_4ed,_4ee,_4ef,_4f0,_4f1);
};
};
dojo.widget.tags.addParseTreeHandler("dojo:widget");
dojo.widget.tags["dojo:propertyset"]=function(_4f2,_4f3,_4f4){
var _4f5=_4f3.parseProperties(_4f2["dojo:propertyset"]);
};
dojo.widget.tags["dojo:connect"]=function(_4f6,_4f7,_4f8){
var _4f9=_4f7.parseProperties(_4f6["dojo:connect"]);
};
dojo.widget.buildWidgetFromParseTree=function(type,frag,_4fc,_4fd,_4fe){
var _4ff={};
var _500=type.split(":");
_500=(_500.length==2)?_500[1]:type;
var _4ff=_4fc.parseProperties(frag["dojo:"+_500]);
var _501=dojo.widget.manager.getImplementation(_500);
if(!_501){
throw new Error("cannot find \""+_500+"\" widget");
}else{
if(!_501.create){
throw new Error("\""+_500+"\" widget object does not appear to implement *Widget");
}
}
_4ff["dojoinsertionindex"]=_4fe;
var ret=_501.create(_4ff,frag,_4fd);
return ret;
};
dojo.provide("dojo.widget.Parse");
dojo.require("dojo.widget.Manager");
dojo.require("dojo.string");
dojo.require("dojo.dom");
dojo.widget.Parse=function(_503){
this.propertySetsList=[];
this.fragment=_503;
this.createComponents=function(_504,_505){
var _506=dojo.widget.tags;
var _507=[];
for(var item in _504){
var _509=false;
try{
if(_504[item]&&(_504[item]["tagName"])&&(_504[item]!=_504["nodeRef"])){
var tn=new String(_504[item]["tagName"]);
var tna=tn.split(";");
for(var x=0;x<tna.length;x++){
var ltn=dojo.string.trim(tna[x]).toLowerCase();
if(_506[ltn]){
_509=true;
_504[item].tagName=ltn;
_507.push(_506[ltn](_504[item],this,_505,_504[item]["index"]));
}else{
if(ltn.substr(0,5)=="dojo:"){
dojo.debug("no tag handler registed for type: ",ltn);
}
}
}
}
}
catch(e){
dojo.debug(e);
}
if((!_509)&&(typeof _504[item]=="object")&&(_504[item]!=_504.nodeRef)&&(_504[item]!=_504["tagName"])){
_507.push(this.createComponents(_504[item],_505));
}
}
return _507;
};
this.parsePropertySets=function(_50e){
return [];
var _50f=[];
for(var item in _50e){
if((_50e[item]["tagName"]=="dojo:propertyset")){
_50f.push(_50e[item]);
}
}
this.propertySetsList.push(_50f);
return _50f;
};
this.parseProperties=function(_511){
var _512={};
for(var item in _511){
if((_511[item]==_511["tagName"])||(_511[item]==_511.nodeRef)){
}else{
if((_511[item]["tagName"])&&(dojo.widget.tags[_511[item].tagName.toLowerCase()])){
}else{
if((_511[item][0])&&(_511[item][0].value!="")){
try{
if(item.toLowerCase()=="dataprovider"){
var _514=this;
this.getDataProvider(_514,_511[item][0].value);
_512.dataProvider=this.dataProvider;
}
_512[item]=_511[item][0].value;
var _515=this.parseProperties(_511[item]);
for(var _516 in _515){
_512[_516]=_515[_516];
}
}
catch(e){
dj_debug(e);
}
}
}
}
}
return _512;
};
this.getDataProvider=function(_517,_518){
dojo.io.bind({url:_518,load:function(type,_51a){
if(type=="load"){
_517.dataProvider=_51a;
}
},mimetype:"text/javascript",sync:true});
};
this.getPropertySetById=function(_51b){
for(var x=0;x<this.propertySetsList.length;x++){
if(_51b==this.propertySetsList[x]["id"][0].value){
return this.propertySetsList[x];
}
}
return "";
};
this.getPropertySetsByType=function(_51d){
var _51e=[];
for(var x=0;x<this.propertySetsList.length;x++){
var cpl=this.propertySetsList[x];
var cpcc=cpl["componentClass"]||cpl["componentType"]||null;
if((cpcc)&&(propertySetId==cpcc[0].value)){
_51e.push(cpl);
}
}
return _51e;
};
this.getPropertySets=function(_522){
var ppl="dojo:propertyproviderlist";
var _524=[];
var _525=_522["tagName"];
if(_522[ppl]){
var _526=_522[ppl].value.split(" ");
for(propertySetId in _526){
if((propertySetId.indexOf("..")==-1)&&(propertySetId.indexOf("://")==-1)){
var _527=this.getPropertySetById(propertySetId);
if(_527!=""){
_524.push(_527);
}
}else{
}
}
}
return (this.getPropertySetsByType(_525)).concat(_524);
};
this.createComponentFromScript=function(_528,_529,_52a,_52b){
var frag={};
var _52d="dojo:"+_529.toLowerCase();
frag[_52d]={};
var bo={};
_52a.dojotype=_529;
for(var prop in _52a){
if(typeof bo[prop]=="undefined"){
frag[_52d][prop]=[{value:_52a[prop]}];
}
}
frag[_52d].nodeRef=_528;
frag.tagName=_52d;
var _530=[frag];
if(_52b){
_530[0].fastMixIn=true;
}
return this.createComponents(_530);
};
};
dojo.widget._parser_collection={"dojo":new dojo.widget.Parse()};
dojo.widget.getParser=function(name){
if(!name){
name="dojo";
}
if(!this._parser_collection[name]){
this._parser_collection[name]=new dojo.widget.Parse();
}
return this._parser_collection[name];
};
dojo.widget.createWidget=function(name,_533,_534,_535){
function fromScript(_536,name,_538){
var _539=name.toLowerCase();
var _53a="dojo:"+_539;
_538[_53a]={dojotype:[{value:_539}],nodeRef:_536,fastMixIn:true};
return dojo.widget.getParser().createComponentFromScript(_536,name,_538,true);
}
if(typeof name!="string"&&typeof _533=="string"){
dojo.deprecated("dojo.widget.createWidget","argument order is now of the form "+"dojo.widget.createWidget(NAME, [PROPERTIES, [REFERENCENODE, [POSITION]]])");
return fromScript(name,_533,_534);
}
_533=_533||{};
var _53b=false;
var tn=null;
var h=dojo.render.html.capable;
if(h){
tn=document.createElement("span");
}
if(!_534){
_53b=true;
_534=tn;
if(h){
dojo.html.body().appendChild(_534);
}
}else{
if(_535){
dojo.dom.insertAtPosition(tn,_534,_535);
}else{
tn=_534;
}
}
var _53e=fromScript(tn,name,_533);
if(!_53e[0]||typeof _53e[0].widgetType=="undefined"){
throw new Error("createWidget: Creation of \""+name+"\" widget failed.");
}
if(_53b){
if(_53e[0].domNode.parentNode){
_53e[0].domNode.parentNode.removeChild(_53e[0].domNode);
}
}
return _53e[0];
};
dojo.widget.fromScript=function(name,_540,_541,_542){
dojo.deprecated("dojo.widget.fromScript"," use "+"dojo.widget.createWidget instead");
return dojo.widget.createWidget(name,_540,_541,_542);
};
dojo.hostenv.conditionalLoadModule({common:["dojo.uri.Uri",false,false]});
dojo.hostenv.moduleLoaded("dojo.uri.*");
dojo.provide("dojo.widget.DomWidget");
dojo.require("dojo.event.*");
dojo.require("dojo.string");
dojo.require("dojo.widget.Widget");
dojo.require("dojo.dom");
dojo.require("dojo.xml.Parse");
dojo.require("dojo.uri.*");
dojo.widget._cssFiles={};
dojo.widget.defaultStrings={dojoRoot:dojo.hostenv.getBaseScriptUri(),baseScriptUri:dojo.hostenv.getBaseScriptUri()};
dojo.widget.buildFromTemplate=function(obj,_544,_545,_546){
var _547=_544||obj.templatePath;
var _548=_545||obj.templateCssPath;
if(!_548&&obj.templateCSSPath){
obj.templateCssPath=_548=obj.templateCSSPath;
obj.templateCSSPath=null;
dj_deprecated("templateCSSPath is deprecated, use templateCssPath");
}
if(_547&&!(_547 instanceof dojo.uri.Uri)){
_547=dojo.uri.dojoUri(_547);
dj_deprecated("templatePath should be of type dojo.uri.Uri");
}
if(_548&&!(_548 instanceof dojo.uri.Uri)){
_548=dojo.uri.dojoUri(_548);
dj_deprecated("templateCssPath should be of type dojo.uri.Uri");
}
var _549=dojo.widget.DomWidget.templates;
if(!obj["widgetType"]){
do{
var _54a="__dummyTemplate__"+dojo.widget.buildFromTemplate.dummyCount++;
}while(_549[_54a]);
obj.widgetType=_54a;
}
if((_548)&&(!dojo.widget._cssFiles[_548])){
dojo.html.insertCssFile(_548);
obj.templateCssPath=null;
dojo.widget._cssFiles[_548]=true;
}
var ts=_549[obj.widgetType];
if(!ts){
_549[obj.widgetType]={};
ts=_549[obj.widgetType];
}
if(!obj.templateString){
obj.templateString=_546||ts["string"];
}
if(!obj.templateNode){
obj.templateNode=ts["node"];
}
if((!obj.templateNode)&&(!obj.templateString)&&(_547)){
var _54c=dojo.hostenv.getText(_547);
if(_54c){
var _54d=_54c.match(/<body[^>]*>\s*([\s\S]+)\s*<\/body>/im);
if(_54d){
_54c=_54d[1];
}
}else{
_54c="";
}
obj.templateString=_54c;
ts.string=_54c;
}
if(!ts["string"]){
ts.string=obj.templateString;
}
};
dojo.widget.buildFromTemplate.dummyCount=0;
dojo.widget.attachProperties=["dojoAttachPoint","id"];
dojo.widget.eventAttachProperty="dojoAttachEvent";
dojo.widget.onBuildProperty="dojoOnBuild";
dojo.widget.attachTemplateNodes=function(_54e,_54f,_550){
var _551=dojo.dom.ELEMENT_NODE;
if(!_54e){
_54e=_54f.domNode;
}
if(_54e.nodeType!=_551){
return;
}
var _552=_54e.getElementsByTagName("*");
var _553=_54f;
for(var x=-1;x<_552.length;x++){
var _555=(x==-1)?_54e:_552[x];
var _556=[];
for(var y=0;y<this.attachProperties.length;y++){
var _558=_555.getAttribute(this.attachProperties[y]);
if(_558){
_556=_558.split(";");
for(var z=0;z<this.attachProperties.length;z++){
if((_54f[_556[z]])&&(dojo.lang.isArray(_54f[_556[z]]))){
_54f[_556[z]].push(_555);
}else{
_54f[_556[z]]=_555;
}
}
break;
}
}
var _55a=_555.getAttribute(this.templateProperty);
if(_55a){
_54f[_55a]=_555;
}
var _55b=_555.getAttribute(this.eventAttachProperty);
if(_55b){
var evts=_55b.split(";");
for(var y=0;y<evts.length;y++){
if((!evts[y])||(!evts[y].length)){
continue;
}
var _55d=null;
var tevt=dojo.string.trim(evts[y]);
if(evts[y].indexOf(":")>=0){
var _55f=tevt.split(":");
tevt=dojo.string.trim(_55f[0]);
_55d=dojo.string.trim(_55f[1]);
}
if(!_55d){
_55d=tevt;
}
var tf=function(){
var ntf=new String(_55d);
return function(evt){
if(_553[ntf]){
_553[ntf](dojo.event.browser.fixEvent(evt));
}
};
}();
dojo.event.browser.addListener(_555,tevt,tf,false,true);
}
}
for(var y=0;y<_550.length;y++){
var _563=_555.getAttribute(_550[y]);
if((_563)&&(_563.length)){
var _55d=null;
var _564=_550[y].substr(4);
_55d=dojo.string.trim(_563);
var tf=function(){
var ntf=new String(_55d);
return function(evt){
if(_553[ntf]){
_553[ntf](dojo.event.browser.fixEvent(evt));
}
};
}();
dojo.event.browser.addListener(_555,_564,tf,false,true);
}
}
var _567=_555.getAttribute(this.onBuildProperty);
if(_567){
eval("var node = baseNode; var widget = targetObj; "+_567);
}
_555.id="";
}
};
dojo.widget.getDojoEventsFromStr=function(str){
var re=/(dojoOn([a-z]+)(\s?))=/gi;
var evts=str?str.match(re)||[]:[];
var ret=[];
var lem={};
for(var x=0;x<evts.length;x++){
if(evts[x].legth<1){
continue;
}
var cm=evts[x].replace(/\s/,"");
cm=(cm.slice(0,cm.length-1));
if(!lem[cm]){
lem[cm]=true;
ret.push(cm);
}
}
return ret;
};
dojo.widget.buildAndAttachTemplate=function(obj,_570,_571,_572,_573){
this.buildFromTemplate(obj,_570,_571,_572);
var node=dojo.dom.createNodesFromText(obj.templateString,true)[0];
this.attachTemplateNodes(node,_573||obj,dojo.widget.getDojoEventsFromStr(_572));
return node;
};
dojo.widget.DomWidget=function(){
dojo.widget.Widget.call(this);
if((arguments.length>0)&&(typeof arguments[0]=="object")){
this.create(arguments[0]);
}
};
dojo.inherits(dojo.widget.DomWidget,dojo.widget.Widget);
dojo.lang.extend(dojo.widget.DomWidget,{templateNode:null,templateString:null,preventClobber:false,domNode:null,containerNode:null,addChild:function(_575,_576,pos,ref,_579){
if(!this.isContainer){
dojo.debug("dojo.widget.DomWidget.addChild() attempted on non-container widget");
return null;
}else{
this.addWidgetAsDirectChild(_575,_576,pos,ref,_579);
this.registerChild(_575);
}
return _575;
},addWidgetAsDirectChild:function(_57a,_57b,pos,ref,_57e){
if((!this.containerNode)&&(!_57b)){
this.containerNode=this.domNode;
}
var cn=(_57b)?_57b:this.containerNode;
if(!pos){
pos="after";
}
if(!ref){
ref=cn.lastChild;
}
if(!_57e){
_57e=0;
}
_57a.domNode.setAttribute("dojoinsertionindex",_57e);
if(!ref){
cn.appendChild(_57a.domNode);
}else{
if(pos=="insertAtIndex"){
dojo.dom.insertAtIndex(_57a.domNode,ref.parentNode,_57e);
}else{
if((pos=="after")&&(ref===cn.lastChild)){
cn.appendChild(_57a.domNode);
}else{
dojo.dom.insertAtPosition(_57a.domNode,cn,pos);
}
}
}
},registerChild:function(_580,_581){
_580.dojoInsertionIndex=_581;
var idx=-1;
for(var i=0;i<this.children.length;i++){
if(this.children[i].dojoInsertionIndex<_581){
idx=i;
}
}
this.children.splice(idx+1,0,_580);
_580.parent=this;
_580.addedTo(this);
delete dojo.widget.manager.topWidgets[_580.widgetId];
},removeChild:function(_584){
for(var x=0;x<this.children.length;x++){
if(this.children[x]===_584){
this.children.splice(x,1);
break;
}
}
return _584;
},getFragNodeRef:function(frag){
if(!frag["dojo:"+this.widgetType.toLowerCase()]){
dojo.raise("Error: no frag for widget type "+this.widgetType+", id "+this.widgetId+" (maybe a widget has set it's type incorrectly)");
}
return (frag?frag["dojo:"+this.widgetType.toLowerCase()]["nodeRef"]:null);
},postInitialize:function(args,frag,_589){
var _58a=this.getFragNodeRef(frag);
if(_589&&(_589.snarfChildDomOutput||!_58a)){
_589.addWidgetAsDirectChild(this,"","insertAtIndex","",args["dojoinsertionindex"],_58a);
}else{
if(_58a){
if(this.domNode&&(this.domNode!==_58a)){
var _58b=_58a.parentNode.replaceChild(this.domNode,_58a);
}
}
}
if(_589){
_589.registerChild(this,args.dojoinsertionindex);
}else{
dojo.widget.manager.topWidgets[this.widgetId]=this;
}
if(this.isContainer){
var _58c=dojo.widget.getParser();
_58c.createComponents(frag,this);
}
},startResize:function(_58d){
dj_unimplemented("dojo.widget.DomWidget.startResize");
},updateResize:function(_58e){
dj_unimplemented("dojo.widget.DomWidget.updateResize");
},endResize:function(_58f){
dj_unimplemented("dojo.widget.DomWidget.endResize");
},buildRendering:function(args,frag){
var ts=dojo.widget.DomWidget.templates[this.widgetType];
if((!this.preventClobber)&&((this.templatePath)||(this.templateNode)||((this["templateString"])&&(this.templateString.length))||((typeof ts!="undefined")&&((ts["string"])||(ts["node"]))))){
this.buildFromTemplate(args,frag);
}else{
this.domNode=this.getFragNodeRef(frag);
}
this.fillInTemplate(args,frag);
},buildFromTemplate:function(args,frag){
var ts=dojo.widget.DomWidget.templates[this.widgetType];
if(ts){
if(!this.templateString.length){
this.templateString=ts["string"];
}
if(!this.templateNode){
this.templateNode=ts["node"];
}
}
var _596=false;
var node=null;
var tstr=new String(this.templateString);
if((!this.templateNode)&&(this.templateString)){
_596=this.templateString.match(/\$\{([^\}]+)\}/g);
if(_596){
var hash=this.strings||{};
for(var key in dojo.widget.defaultStrings){
if(dojo.lang.isUndefined(hash[key])){
hash[key]=dojo.widget.defaultStrings[key];
}
}
for(var i=0;i<_596.length;i++){
var key=_596[i];
key=key.substring(2,key.length-1);
var kval=(key.substring(0,5)=="this.")?this[key.substring(5)]:hash[key];
var _59d;
if((kval)||(dojo.lang.isString(kval))){
_59d=(dojo.lang.isFunction(kval))?kval.call(this,key,this.templateString):kval;
tstr=tstr.replace(_596[i],_59d);
}
}
}else{
this.templateNode=this.createNodesFromText(this.templateString,true)[0];
ts.node=this.templateNode;
}
}
if((!this.templateNode)&&(!_596)){
dojo.debug("weren't able to create template!");
return false;
}else{
if(!_596){
node=this.templateNode.cloneNode(true);
if(!node){
return false;
}
}else{
node=this.createNodesFromText(tstr,true)[0];
}
}
this.domNode=node;
this.attachTemplateNodes(this.domNode,this);
if(this.isContainer&&this.containerNode){
var src=this.getFragNodeRef(frag);
if(src){
dojo.dom.moveChildren(src,this.containerNode);
}
}
},attachTemplateNodes:function(_59f,_5a0){
if(!_5a0){
_5a0=this;
}
return dojo.widget.attachTemplateNodes(_59f,_5a0,dojo.widget.getDojoEventsFromStr(this.templateString));
},fillInTemplate:function(){
},destroyRendering:function(){
try{
var _5a1=this.domNode.parentNode.removeChild(this.domNode);
delete _5a1;
}
catch(e){
}
},cleanUp:function(){
},getContainerHeight:function(){
return dojo.html.getInnerHeight(this.domNode.parentNode);
},getContainerWidth:function(){
return dojo.html.getInnerWidth(this.domNode.parentNode);
},createNodesFromText:function(){
dj_unimplemented("dojo.widget.DomWidget.createNodesFromText");
}});
dojo.widget.DomWidget.templates={};
dojo.provide("dojo.widget.HtmlWidget");
dojo.require("dojo.widget.DomWidget");
dojo.require("dojo.html");
dojo.require("dojo.string");
dojo.widget.HtmlWidget=function(args){
dojo.widget.DomWidget.call(this);
};
dojo.inherits(dojo.widget.HtmlWidget,dojo.widget.DomWidget);
dojo.lang.extend(dojo.widget.HtmlWidget,{widgetType:"HtmlWidget",templateCssPath:null,templatePath:null,allowResizeX:true,allowResizeY:true,resizeGhost:null,initialResizeCoords:null,toggle:"plain",toggleDuration:150,animationInProgress:false,initialize:function(args,frag){
},postMixInProperties:function(args,frag){
dojo.lang.mixin(this,dojo.widget.HtmlWidget.Toggle[dojo.string.capitalize(this.toggle)]||dojo.widget.HtmlWidget.Toggle.Plain);
},getContainerHeight:function(){
dj_unimplemented("dojo.widget.HtmlWidget.getContainerHeight");
},getContainerWidth:function(){
return this.parent.domNode.offsetWidth;
},setNativeHeight:function(_5a7){
var ch=this.getContainerHeight();
},startResize:function(_5a9){
_5a9.offsetLeft=dojo.html.totalOffsetLeft(this.domNode);
_5a9.offsetTop=dojo.html.totalOffsetTop(this.domNode);
_5a9.innerWidth=dojo.html.getInnerWidth(this.domNode);
_5a9.innerHeight=dojo.html.getInnerHeight(this.domNode);
if(!this.resizeGhost){
this.resizeGhost=document.createElement("div");
var rg=this.resizeGhost;
rg.style.position="absolute";
rg.style.backgroundColor="white";
rg.style.border="1px solid black";
dojo.html.setOpacity(rg,0.3);
dojo.html.body().appendChild(rg);
}
with(this.resizeGhost.style){
left=_5a9.offsetLeft+"px";
top=_5a9.offsetTop+"px";
}
this.initialResizeCoords=_5a9;
this.resizeGhost.style.display="";
this.updateResize(_5a9,true);
},updateResize:function(_5ab,_5ac){
var dx=_5ab.x-this.initialResizeCoords.x;
var dy=_5ab.y-this.initialResizeCoords.y;
with(this.resizeGhost.style){
if((this.allowResizeX)||(_5ac)){
width=this.initialResizeCoords.innerWidth+dx+"px";
}
if((this.allowResizeY)||(_5ac)){
height=this.initialResizeCoords.innerHeight+dy+"px";
}
}
},endResize:function(_5af){
var dx=_5af.x-this.initialResizeCoords.x;
var dy=_5af.y-this.initialResizeCoords.y;
with(this.domNode.style){
if(this.allowResizeX){
width=this.initialResizeCoords.innerWidth+dx+"px";
}
if(this.allowResizeY){
height=this.initialResizeCoords.innerHeight+dy+"px";
}
}
this.resizeGhost.style.display="none";
},resizeSoon:function(){
if(this.isVisible()){
dojo.lang.setTimeout(this,this.onResized,0);
}
},createNodesFromText:function(txt,wrap){
return dojo.html.createNodesFromText(txt,wrap);
},_old_buildFromTemplate:dojo.widget.DomWidget.prototype.buildFromTemplate,buildFromTemplate:function(args,frag){
if(dojo.widget.DomWidget.templates[this.widgetType]){
var ot=dojo.widget.DomWidget.templates[this.widgetType];
dojo.widget.DomWidget.templates[this.widgetType]={};
}
dojo.widget.buildFromTemplate(this,args["templatePath"],args["templateCssPath"]);
this._old_buildFromTemplate(args,frag);
dojo.widget.DomWidget.templates[this.widgetType]=ot;
},destroyRendering:function(_5b7){
try{
var _5b8=this.domNode.parentNode.removeChild(this.domNode);
if(!_5b7){
dojo.event.browser.clean(_5b8);
}
delete _5b8;
}
catch(e){
}
},isVisible:function(){
return dojo.html.isVisible(this.domNode);
},doToggle:function(){
this.isVisible()?this.hide():this.show();
},show:function(){
this.animationInProgress=true;
this.showMe();
},onShow:function(){
this.animationInProgress=false;
},hide:function(){
this.animationInProgress=true;
this.hideMe();
},onHide:function(){
this.animationInProgress=false;
}});
dojo.widget.HtmlWidget.Toggle={};
dojo.widget.HtmlWidget.Toggle.Plain={showMe:function(){
dojo.html.show(this.domNode);
if(dojo.lang.isFunction(this.onShow)){
this.onShow();
}
},hideMe:function(){
dojo.html.hide(this.domNode);
if(dojo.lang.isFunction(this.onHide)){
this.onHide();
}
}};
dojo.widget.HtmlWidget.Toggle.Fade={showMe:function(){
dojo.fx.html.fadeShow(this.domNode,this.toggleDuration,dojo.lang.hitch(this,this.onShow));
},hideMe:function(){
dojo.fx.html.fadeHide(this.domNode,this.toggleDuration,dojo.lang.hitch(this,this.onHide));
}};
dojo.widget.HtmlWidget.Toggle.Wipe={showMe:function(){
dojo.fx.html.wipeIn(this.domNode,this.toggleDuration,dojo.lang.hitch(this,this.onShow));
},hideMe:function(){
dojo.fx.html.wipeOut(this.domNode,this.toggleDuration,dojo.lang.hitch(this,this.onHide));
}};
dojo.widget.HtmlWidget.Toggle.Explode={showMe:function(){
dojo.fx.html.explode(this.explodeSrc,this.domNode,this.toggleDuration,dojo.lang.hitch(this,this.onShow));
},hideMe:function(){
dojo.fx.html.implode(this.domNode,this.explodeSrc,this.toggleDuration,dojo.lang.hitch(this,this.onHide));
}};
dojo.hostenv.conditionalLoadModule({common:["dojo.xml.Parse","dojo.widget.Widget","dojo.widget.Parse","dojo.widget.Manager"],browser:["dojo.widget.DomWidget","dojo.widget.HtmlWidget"],svg:["dojo.widget.SvgWidget"]});
dojo.hostenv.moduleLoaded("dojo.widget.*");
dojo.provide("dojo.widget.ToolbarContainer");
dojo.provide("dojo.widget.html.ToolbarContainer");
dojo.provide("dojo.widget.Toolbar");
dojo.provide("dojo.widget.html.Toolbar");
dojo.provide("dojo.widget.ToolbarItem");
dojo.provide("dojo.widget.html.ToolbarButtonGroup");
dojo.provide("dojo.widget.html.ToolbarButton");
dojo.provide("dojo.widget.html.ToolbarDialog");
dojo.provide("dojo.widget.html.ToolbarMenu");
dojo.provide("dojo.widget.html.ToolbarSeparator");
dojo.provide("dojo.widget.html.ToolbarSpace");
dojo.provide("dojo.widget.Icon");
dojo.require("dojo.widget.*");
dojo.require("dojo.html");
dojo.widget.html.ToolbarContainer=function(){
dojo.widget.HtmlWidget.call(this);
this.widgetType="ToolbarContainer";
this.isContainer=true;
this.templateString="<div class=\"toolbarContainer\" dojoAttachPoint=\"containerNode\"></div>";
this.templateCssPath=dojo.uri.dojoUri("src/widget/templates/HtmlToolbar.css");
this.getItem=function(name){
if(name instanceof dojo.widget.ToolbarItem){
return name;
}
for(var i=0;i<this.children.length;i++){
var _5bb=this.children[i];
if(_5bb instanceof dojo.widget.html.Toolbar){
var item=_5bb.getItem(name);
if(item){
return item;
}
}
}
return null;
};
this.getItems=function(){
var _5bd=[];
for(var i=0;i<this.children.length;i++){
var _5bf=this.children[i];
if(_5bf instanceof dojo.widget.html.Toolbar){
_5bd=_5bd.concat(_5bf.getItems());
}
}
return _5bd;
};
this.enable=function(){
for(var i=0;i<this.children.length;i++){
var _5c1=this.children[i];
if(_5c1 instanceof dojo.widget.html.Toolbar){
_5c1.enable.apply(_5c1,arguments);
}
}
};
this.disable=function(){
for(var i=0;i<this.children.length;i++){
var _5c3=this.children[i];
if(_5c3 instanceof dojo.widget.html.Toolbar){
_5c3.disable.apply(_5c3,arguments);
}
}
};
this.select=function(name){
for(var i=0;i<this.children.length;i++){
var _5c6=this.children[i];
if(_5c6 instanceof dojo.widget.html.Toolbar){
_5c6.select(arguments);
}
}
};
this.deselect=function(name){
for(var i=0;i<this.children.length;i++){
var _5c9=this.children[i];
if(_5c9 instanceof dojo.widget.html.Toolbar){
_5c9.deselect(arguments);
}
}
};
this.getItemsState=function(){
var _5ca={};
for(var i=0;i<this.children.length;i++){
var _5cc=this.children[i];
if(_5cc instanceof dojo.widget.html.Toolbar){
dojo.lang.mixin(_5ca,_5cc.getItemsState());
}
}
return _5ca;
};
this.getItemsActiveState=function(){
var _5cd={};
for(var i=0;i<this.children.length;i++){
var _5cf=this.children[i];
if(_5cf instanceof dojo.widget.html.Toolbar){
dojo.lang.mixin(_5cd,_5cf.getItemsActiveState());
}
}
return _5cd;
};
this.getItemsSelectedState=function(){
var _5d0={};
for(var i=0;i<this.children.length;i++){
var _5d2=this.children[i];
if(_5d2 instanceof dojo.widget.html.Toolbar){
dojo.lang.mixin(_5d0,_5d2.getItemsSelectedState());
}
}
return _5d0;
};
};
dojo.inherits(dojo.widget.html.ToolbarContainer,dojo.widget.HtmlWidget);
dojo.widget.tags.addParseTreeHandler("dojo:toolbarContainer");
dojo.widget.html.Toolbar=function(){
dojo.widget.HtmlWidget.call(this);
this.widgetType="Toolbar";
this.isContainer=true;
this.templateString="<div class=\"toolbar\" dojoAttachPoint=\"containerNode\" unselectable=\"on\" dojoOnMouseover=\"_onmouseover\" dojoOnMouseout=\"_onmouseout\" dojoOnClick=\"_onclick\" dojoOnMousedown=\"_onmousedown\" dojoOnMouseup=\"_onmouseup\"></div>";
this._getItem=function(node){
var _5d4=new Date();
var _5d5=null;
while(node&&node!=this.domNode){
if(dojo.html.hasClass(node,"toolbarItem")){
var _5d6=dojo.widget.manager.getWidgetsByFilter(function(w){
return w.domNode==node;
});
if(_5d6.length==1){
_5d5=_5d6[0];
break;
}else{
if(_5d6.length>1){
dojo.raise("Toolbar._getItem: More than one widget matches the node");
}
}
}
node=node.parentNode;
}
return _5d5;
};
this._onmouseover=function(e){
var _5d9=this._getItem(e.target);
if(_5d9&&_5d9._onmouseover){
_5d9._onmouseover(e);
}
};
this._onmouseout=function(e){
var _5db=this._getItem(e.target);
if(_5db&&_5db._onmouseout){
_5db._onmouseout(e);
}
};
this._onclick=function(e){
var _5dd=this._getItem(e.target);
if(_5dd&&_5dd._onclick){
_5dd._onclick(e);
}
};
this._onmousedown=function(e){
var _5df=this._getItem(e.target);
if(_5df&&_5df._onmousedown){
_5df._onmousedown(e);
}
};
this._onmouseup=function(e){
var _5e1=this._getItem(e.target);
if(_5e1&&_5e1._onmouseup){
_5e1._onmouseup(e);
}
};
var _5e2=this.addChild;
this.addChild=function(item,pos,_5e5){
var _5e6=dojo.widget.ToolbarItem.make(item,null,_5e5);
var ret=_5e2.call(this,_5e6,null,pos,null);
return ret;
};
this.push=function(){
for(var i=0;i<arguments.length;i++){
this.addChild(arguments[i]);
}
};
this.getItem=function(name){
if(name instanceof dojo.widget.ToolbarItem){
return name;
}
for(var i=0;i<this.children.length;i++){
var _5eb=this.children[i];
if(_5eb instanceof dojo.widget.ToolbarItem&&_5eb._name==name){
return _5eb;
}
}
return null;
};
this.getItems=function(){
var _5ec=[];
for(var i=0;i<this.children.length;i++){
var _5ee=this.children[i];
if(_5ee instanceof dojo.widget.ToolbarItem){
_5ec.push(_5ee);
}
}
return _5ec;
};
this.getItemsState=function(){
var _5ef={};
for(var i=0;i<this.children.length;i++){
var _5f1=this.children[i];
if(_5f1 instanceof dojo.widget.ToolbarItem){
_5ef[_5f1._name]={selected:_5f1._selected,enabled:_5f1._enabled};
}
}
return _5ef;
};
this.getItemsActiveState=function(){
var _5f2=this.getItemsState();
for(var item in _5f2){
_5f2[item]=_5f2[item].enabled;
}
return _5f2;
};
this.getItemsSelectedState=function(){
var _5f4=this.getItemsState();
for(var item in _5f4){
_5f4[item]=_5f4[item].selected;
}
return _5f4;
};
this.enable=function(){
var _5f6=arguments.length?arguments:this.children;
for(var i=0;i<_5f6.length;i++){
var _5f8=this.getItem(_5f6[i]);
if(_5f8 instanceof dojo.widget.ToolbarItem){
_5f8.enable(false,true);
}
}
};
this.disable=function(){
var _5f9=arguments.length?arguments:this.children;
for(var i=0;i<_5f9.length;i++){
var _5fb=this.getItem(_5f9[i]);
if(_5fb instanceof dojo.widget.ToolbarItem){
_5fb.disable();
}
}
};
this.select=function(){
for(var i=0;i<arguments.length;i++){
var name=arguments[i];
var item=this.getItem(name);
if(item){
item.select();
}
}
};
this.deselect=function(){
for(var i=0;i<arguments.length;i++){
var name=arguments[i];
var item=this.getItem(name);
if(item){
item.disable();
}
}
};
this.setValue=function(){
for(var i=0;i<arguments.length;i+=2){
var name=arguments[i],value=arguments[i+1];
var item=this.getItem(name);
if(item){
if(item instanceof dojo.widget.ToolbarItem){
item.setValue(value);
}
}
}
};
};
dojo.inherits(dojo.widget.html.Toolbar,dojo.widget.HtmlWidget);
dojo.widget.tags.addParseTreeHandler("dojo:toolbar");
dojo.widget.ToolbarItem=function(){
dojo.widget.HtmlWidget.call(this);
};
dojo.inherits(dojo.widget.ToolbarItem,dojo.widget.HtmlWidget);
dojo.lang.extend(dojo.widget.ToolbarItem,{templateString:"<span unselectable=\"on\" class=\"toolbarItem\"></span>",_name:null,getName:function(){
return this._name;
},setName:function(_605){
return this._name=_605;
},getValue:function(){
return this.getName();
},setValue:function(_606){
return this.setName(_606);
},_selected:false,isSelected:function(){
return this._selected;
},setSelected:function(is,_608,_609){
if(!this._toggleItem&&!_608){
return;
}
is=Boolean(is);
if(_608||this._enabled&&this._selected!=is){
this._selected=is;
this.update();
if(!_609){
this._fireEvent(is?"onSelect":"onDeselect");
this._fireEvent("onChangeSelect");
}
}
},select:function(_60a,_60b){
return this.setSelected(true,_60a,_60b);
},deselect:function(_60c,_60d){
return this.setSelected(false,_60c,_60d);
},_toggleItem:false,isToggleItem:function(){
return this._toggleItem;
},setToggleItem:function(_60e){
this._toggleItem=Boolean(_60e);
},toggleSelected:function(_60f){
return this.setSelected(!this._selected,_60f);
},_enabled:true,isEnabled:function(){
return this._enabled;
},setEnabled:function(is,_611,_612){
is=Boolean(is);
if(_611||this._enabled!=is){
this._enabled=is;
this.update();
if(!_612){
this._fireEvent(this._enabled?"onEnable":"onDisable");
this._fireEvent("onChangeEnabled");
}
}
return this._enabled;
},enable:function(_613,_614){
return this.setEnabled(true,_613,_614);
},disable:function(_615,_616){
return this.setEnabled(false,_615,_616);
},toggleEnabled:function(_617,_618){
return this.setEnabled(!this._enabled,_617,_618);
},_icon:null,getIcon:function(){
return this._icon;
},setIcon:function(_619){
var icon=dojo.widget.Icon.make(_619);
if(this._icon){
this._icon.setIcon(icon);
}else{
this._icon=icon;
}
var _61b=this._icon.getNode();
if(_61b.parentNode!=this.domNode){
if(this.domNode.hasChildNodes()){
this.domNode.insertBefore(_61b,this.domNode.firstChild);
}else{
this.domNode.appendChild(_61b);
}
}
return this._icon;
},_label:"",getLabel:function(){
return this._label;
},setLabel:function(_61c){
var ret=this._label=_61c;
if(!this.labelNode){
this.labelNode=document.createElement("span");
this.domNode.appendChild(this.labelNode);
}
this.labelNode.innerHTML="";
this.labelNode.appendChild(document.createTextNode(this._label));
this.update();
return ret;
},update:function(){
if(this._enabled){
dojo.html.removeClass(this.domNode,"disabled");
if(this._selected){
dojo.html.addClass(this.domNode,"selected");
}else{
dojo.html.removeClass(this.domNode,"selected");
}
}else{
this._selected=false;
dojo.html.addClass(this.domNode,"disabled");
dojo.html.removeClass(this.domNode,"down");
dojo.html.removeClass(this.domNode,"hover");
}
this._updateIcon();
},_updateIcon:function(){
if(this._icon){
if(this._enabled){
if(this._cssHover){
this._icon.hover();
}else{
if(this._selected){
this._icon.select();
}else{
this._icon.enable();
}
}
}else{
this._icon.disable();
}
}
},_fireEvent:function(evt){
if(typeof this[evt]=="function"){
var args=[this];
for(var i=1;i<arguments.length;i++){
args.push(arguments[i]);
}
this[evt].apply(this,args);
}
},_onmouseover:function(e){
if(!this._enabled){
return;
}
dojo.html.addClass(this.domNode,"hover");
},_onmouseout:function(e){
dojo.html.removeClass(this.domNode,"hover");
dojo.html.removeClass(this.domNode,"down");
if(!this._selected){
dojo.html.removeClass(this.domNode,"selected");
}
},_onclick:function(e){
if(this._enabled&&!this._toggleItem){
this._fireEvent("onClick");
}
},_onmousedown:function(e){
if(e.preventDefault){
e.preventDefault();
}
if(!this._enabled){
return;
}
dojo.html.addClass(this.domNode,"down");
if(this._toggleItem){
if(this.parent.preventDeselect&&this._selected){
return;
}
this.toggleSelected();
}
},_onmouseup:function(e){
dojo.html.removeClass(this.domNode,"down");
},fillInTemplate:function(args,frag){
if(args.name){
this._name=args.name;
}
if(args.selected){
this.select();
}
if(args.disabled){
this.disable();
}
if(args.label){
this.setLabel(args.label);
}
if(args.icon){
this.setIcon(args.icon);
}
if(args.toggleitem||args.toggleItem){
this.setToggleItem(true);
}
}});
dojo.widget.ToolbarItem.make=function(wh,_629,_62a){
var item=null;
if(wh instanceof Array){
item=dojo.widget.createWidget("ToolbarButtonGroup",_62a);
item.setName(wh[0]);
for(var i=1;i<wh.length;i++){
item.addChild(wh[i]);
}
}else{
if(wh instanceof dojo.widget.ToolbarItem){
item=wh;
}else{
if(wh instanceof dojo.uri.Uri){
item=dojo.widget.createWidget("ToolbarButton",dojo.lang.mixin(_62a||{},{icon:new dojo.widget.Icon(wh.toString())}));
}else{
if(_629){
item=dojo.widget.createWidget(wh,_62a);
}else{
if(typeof wh=="string"||wh instanceof String){
switch(wh.charAt(0)){
case "|":
case "-":
case "/":
item=dojo.widget.createWidget("ToolbarSeparator",_62a);
break;
case " ":
if(wh.length==1){
item=dojo.widget.createWidget("ToolbarSpace",_62a);
}else{
item=dojo.widget.createWidget("ToolbarFlexibleSpace",_62a);
}
break;
default:
if(/\.(gif|jpg|jpeg|png)$/i.test(wh)){
item=dojo.widget.createWidget("ToolbarButton",dojo.lang.mixin(_62a||{},{icon:new dojo.widget.Icon(wh.toString())}));
}else{
item=dojo.widget.createWidget("ToolbarButton",dojo.lang.mixin(_62a||{},{label:wh.toString()}));
}
}
}else{
if(wh&&wh.tagName&&/^img$/i.test(wh.tagName)){
item=dojo.widget.createWidget("ToolbarButton",dojo.lang.mixin(_62a||{},{icon:wh}));
}else{
item=dojo.widget.createWidget("ToolbarButton",dojo.lang.mixin(_62a||{},{label:wh.toString()}));
}
}
}
}
}
}
return item;
};
dojo.widget.html.ToolbarButtonGroup=function(){
dojo.widget.ToolbarItem.call(this);
this.widgetType="ToolbarButtonGroup";
this.isContainer=true;
this.templateString="<span unselectable=\"on\" class=\"toolbarButtonGroup\" dojoAttachPoint=\"containerNode\"></span>";
this.defaultButton="";
var _62d=this.addChild;
this.addChild=function(item,pos,_630){
var _631=dojo.widget.ToolbarItem.make(item,null,dojo.lang.mixin(_630||{},{toggleItem:true}));
dojo.event.connect(_631,"onSelect",this,"onChildSelected");
var ret=_62d.call(this,_631,null,pos,null);
if(_631._name==this.defaultButton||(typeof this.defaultButton=="number"&&this.children.length-1==this.defaultButton)){
_631.select(false,true);
}
return ret;
};
this.getItem=function(name){
if(name instanceof dojo.widget.ToolbarItem){
return name;
}
for(var i=0;i<this.children.length;i++){
var _635=this.children[i];
if(_635 instanceof dojo.widget.ToolbarItem&&_635._name==name){
return _635;
}
}
return null;
};
this.getItems=function(){
var _636=[];
for(var i=0;i<this.children.length;i++){
var _638=this.children[i];
if(_638 instanceof dojo.widget.ToolbarItem){
_636.push(_638);
}
}
return _636;
};
this.onChildSelected=function(e){
this.select(e._name);
};
this.enable=function(_63a,_63b){
for(var i=0;i<this.children.length;i++){
var _63d=this.children[i];
if(_63d instanceof dojo.widget.ToolbarItem){
_63d.enable(_63a,_63b);
if(_63d._name==this._value){
_63d.select(_63a,_63b);
}
}
}
};
this.disable=function(_63e,_63f){
for(var i=0;i<this.children.length;i++){
var _641=this.children[i];
if(_641 instanceof dojo.widget.ToolbarItem){
_641.disable(_63e,_63f);
}
}
};
this._value="";
this.getValue=function(){
return this._value;
};
this.select=function(name,_643,_644){
for(var i=0;i<this.children.length;i++){
var _646=this.children[i];
if(_646 instanceof dojo.widget.ToolbarItem){
if(_646._name==name){
_646.select(_643,_644);
this._value=name;
}else{
_646.deselect(true,_644);
}
}
}
if(!_644){
this._fireEvent("onSelect",this._value);
this._fireEvent("onChangeSelect",this._value);
}
};
this.setValue=this.select;
this.preventDeselect=false;
};
dojo.inherits(dojo.widget.html.ToolbarButtonGroup,dojo.widget.ToolbarItem);
dojo.widget.tags.addParseTreeHandler("dojo:toolbarButtonGroup");
dojo.widget.html.ToolbarButton=function(){
dojo.widget.ToolbarItem.call(this);
};
dojo.inherits(dojo.widget.html.ToolbarButton,dojo.widget.ToolbarItem);
dojo.widget.tags.addParseTreeHandler("dojo:toolbarButton");
dojo.lang.extend(dojo.widget.html.ToolbarButton,{widgetType:"ToolbarButton",fillInTemplate:function(args,frag){
dojo.widget.html.ToolbarButton.superclass.fillInTemplate.call(this,args,frag);
dojo.html.addClass(this.domNode,"toolbarButton");
if(this._icon){
this.setIcon(this._icon);
}
if(this._label){
this.setLabel(this._label);
}
if(!this._name){
if(this._label){
this.setName(this._label);
}else{
if(this._icon){
var src=this._icon.getSrc("enabled").match(/[\/^]([^\.\/]+)\.(gif|jpg|jpeg|png)$/i);
if(src){
this.setName(src[1]);
}
}else{
this._name=this._widgetId;
}
}
}
}});
dojo.widget.html.ToolbarDialog=function(){
dojo.widget.html.ToolbarButton.call(this);
};
dojo.inherits(dojo.widget.html.ToolbarDialog,dojo.widget.html.ToolbarButton);
dojo.widget.tags.addParseTreeHandler("dojo:toolbarDialog");
dojo.lang.extend(dojo.widget.html.ToolbarDialog,{widgetType:"ToolbarDialog",fillInTemplate:function(args,frag){
dojo.widget.html.ToolbarDialog.superclass.fillInTemplate.call(this,args,frag);
dojo.event.connect(this,"onSelect",this,"showDialog");
dojo.event.connect(this,"onDeselect",this,"hideDialog");
},showDialog:function(e){
dojo.lang.setTimeout(dojo.event.connect,1,document,"onmousedown",this,"deselect");
},hideDialog:function(e){
dojo.event.disconnect(document,"onmousedown",this,"deselect");
}});
dojo.widget.html.ToolbarMenu=function(){
dojo.widget.html.ToolbarDialog.call(this);
this.widgetType="ToolbarMenu";
};
dojo.inherits(dojo.widget.html.ToolbarMenu,dojo.widget.html.ToolbarDialog);
dojo.widget.tags.addParseTreeHandler("dojo:toolbarMenu");
dojo.widget.ToolbarMenuItem=function(){
};
dojo.widget.html.ToolbarSeparator=function(){
dojo.widget.ToolbarItem.call(this);
this.widgetType="ToolbarSeparator";
this.templateString="<span unselectable=\"on\" class=\"toolbarItem toolbarSeparator\"></span>";
this.defaultIconPath=new dojo.uri.dojoUri("src/widget/templates/buttons/-.gif");
var _64e=this.fillInTemplate;
this.fillInTemplate=function(args,frag,skip){
_64e.call(this,args,frag);
this._name=this.widgetId;
if(!skip){
if(!this._icon){
this.setIcon(this.defaultIconPath);
}
this.domNode.appendChild(this._icon.getNode());
}
};
this._onmouseover=this._onmouseout=this._onclick=this._onmousedown=this._onmouseup=null;
};
dojo.inherits(dojo.widget.html.ToolbarSeparator,dojo.widget.ToolbarItem);
dojo.widget.tags.addParseTreeHandler("dojo:toolbarSeparator");
dojo.widget.html.ToolbarSpace=function(){
dojo.widget.html.ToolbarSeparator.call(this);
this.widgetType="ToolbarSpace";
var _652=this.fillInTemplate;
this.fillInTemplate=function(args,frag,skip){
_652.call(this,args,frag,true);
if(!skip){
dojo.html.addClass(this.domNode,"toolbarSpace");
}
};
};
dojo.inherits(dojo.widget.html.ToolbarSpace,dojo.widget.html.ToolbarSeparator);
dojo.widget.tags.addParseTreeHandler("dojo:toolbarSpace");
dojo.widget.html.ToolbarSelect=function(){
dojo.widget.ToolbarItem.call(this);
this.widgetType="ToolbarSelect";
this.templateString="<span class=\"toolbarItem toolbarSelect\" unselectable=\"on\"><select dojoAttachPoint=\"selectBox\" dojoOnChange=\"changed\"></select></span>";
var _656=this.fillInTemplate;
this.fillInTemplate=function(args,frag){
_656.call(this,args,frag,true);
var keys=args.values;
var i=0;
for(var val in keys){
var opt=document.createElement("option");
opt.setAttribute("value",keys[val]);
opt.innerHTML=val;
this.selectBox.appendChild(opt);
}
};
this.changed=function(e){
this._fireEvent("onSetValue",this.selectBox.value);
};
var _65e=this.setEnabled;
this.setEnabled=function(is,_660,_661){
var ret=_65e.call(this,is,_660,_661);
this.selectBox.disabled=!this._enabled;
return ret;
};
this._onmouseover=this._onmouseout=this._onclick=this._onmousedown=this._onmouseup=null;
};
dojo.inherits(dojo.widget.html.ToolbarSelect,dojo.widget.ToolbarItem);
dojo.widget.tags.addParseTreeHandler("dojo:toolbarSelect");
dojo.widget.Icon=function(_663,_664,_665,_666){
if(arguments.length==0){
throw new Error("Icon must have at least an enabled state");
}
var _667=["enabled","disabled","hover","selected"];
var _668="enabled";
var _669=document.createElement("img");
this.getState=function(){
return _668;
};
this.setState=function(_66a){
if(dojo.lang.inArray(_66a,_667)){
if(this[_66a]){
_668=_66a;
_669.setAttribute("src",this[_668].src);
}
}else{
throw new Error("Invalid state set on Icon (state: "+_66a+")");
}
};
this.setSrc=function(_66b,_66c){
if(/^img$/i.test(_66c.tagName)){
this[_66b]=_66c;
}else{
if(typeof _66c=="string"||_66c instanceof String||_66c instanceof dojo.uri.Uri){
this[_66b]=new Image();
this[_66b].src=_66c.toString();
}
}
return this[_66b];
};
this.setIcon=function(icon){
for(var i=0;i<_667.length;i++){
if(icon[_667[i]]){
this.setSrc(_667[i],icon[_667[i]]);
}
}
this.update();
};
this.enable=function(){
this.setState("enabled");
};
this.disable=function(){
this.setState("disabled");
};
this.hover=function(){
this.setState("hover");
};
this.select=function(){
this.setState("selected");
};
this.getSize=function(){
return {width:_669.width||_669.offsetWidth,height:_669.height||_669.offsetHeight};
};
this.setSize=function(w,h){
_669.width=w;
_669.height=h;
return {width:w,height:h};
};
this.getNode=function(){
return _669;
};
this.getSrc=function(_671){
if(_671){
return this[_671].src;
}
return _669.src||"";
};
this.update=function(){
this.setState(_668);
};
for(var i=0;i<_667.length;i++){
var arg=arguments[i];
var _674=_667[i];
this[_674]=null;
if(!arg){
continue;
}
this.setSrc(_674,arg);
}
this.enable();
};
dojo.widget.Icon.make=function(a,b,c,d){
for(var i=0;i<arguments.length;i++){
if(arguments[i] instanceof dojo.widget.Icon){
return arguments[i];
}else{
if(!arguments[i]){
nullArgs++;
}
}
}
return new dojo.widget.Icon(a,b,c,d);
};
dojo.provide("dojo.widget.ColorPalette");
dojo.provide("dojo.widget.html.ColorPalette");
dojo.require("dojo.widget.*");
dojo.require("dojo.widget.Toolbar");
dojo.require("dojo.html");
dojo.widget.tags.addParseTreeHandler("dojo:ToolbarColorDialog");
dojo.widget.html.ToolbarColorDialog=function(){
dojo.widget.html.ToolbarDialog.call(this);
for(var _67a in this.constructor.prototype){
this[_67a]=this.constructor.prototype[_67a];
}
};
dojo.inherits(dojo.widget.html.ToolbarColorDialog,dojo.widget.html.ToolbarDialog);
dojo.lang.extend(dojo.widget.html.ToolbarColorDialog,{widgetType:"ToolbarColorDialog",palette:"7x10",fillInTemplate:function(args,frag){
dojo.widget.html.ToolbarColorDialog.superclass.fillInTemplate.call(this,args,frag);
this.dialog=dojo.widget.createWidget("ColorPalette",{palette:this.palette});
this.dialog.domNode.style.position="absolute";
dojo.event.connect(this.dialog,"onColorSelect",this,"_setValue");
},_setValue:function(_67d){
this._value=_67d;
this._fireEvent("onSetValue",_67d);
},showDialog:function(e){
dojo.widget.html.ToolbarColorDialog.superclass.showDialog.call(this,e);
var x=dojo.html.getAbsoluteX(this.domNode);
var y=dojo.html.getAbsoluteY(this.domNode)+dojo.html.getInnerHeight(this.domNode);
this.dialog.showAt(x,y);
},hideDialog:function(e){
dojo.widget.html.ToolbarColorDialog.superclass.hideDialog.call(this,e);
this.dialog.hide();
}});
dojo.widget.tags.addParseTreeHandler("dojo:colorpalette");
dojo.widget.html.ColorPalette=function(){
dojo.widget.HtmlWidget.call(this);
};
dojo.inherits(dojo.widget.html.ColorPalette,dojo.widget.HtmlWidget);
dojo.lang.extend(dojo.widget.html.ColorPalette,{widgetType:"colorpalette",palette:"7x10",bgIframe:null,palettes:{"7x10":[["fff","fcc","fc9","ff9","ffc","9f9","9ff","cff","ccf","fcf"],["ccc","f66","f96","ff6","ff3","6f9","3ff","6ff","99f","f9f"],["c0c0c0","f00","f90","fc6","ff0","3f3","6cc","3cf","66c","c6c"],["999","c00","f60","fc3","fc0","3c0","0cc","36f","63f","c3c"],["666","900","c60","c93","990","090","399","33f","60c","939"],["333","600","930","963","660","060","366","009","339","636"],["000","300","630","633","330","030","033","006","309","303"]],"3x4":[["ffffff","00ff00","008000","0000ff"],["c0c0c0","ffff00","ff00ff","000080"],["808080","ff0000","800080","000000"]]},buildRendering:function(){
this.domNode=document.createElement("table");
dojo.html.disableSelection(this.domNode);
dojo.event.connect(this.domNode,"onmousedown",function(e){
e.preventDefault();
});
with(this.domNode){
cellPadding="0";
cellSpacing="1";
border="1";
style.backgroundColor="white";
}
var _683=document.createElement("tbody");
this.domNode.appendChild(_683);
var _684=this.palettes[this.palette];
for(var i=0;i<_684.length;i++){
var tr=document.createElement("tr");
for(var j=0;j<_684[i].length;j++){
if(_684[i][j].length==3){
_684[i][j]=_684[i][j].replace(/(.)(.)(.)/,"$1$1$2$2$3$3");
}
var td=document.createElement("td");
with(td.style){
backgroundColor="#"+_684[i][j];
border="1px solid gray";
width=height="15px";
fontSize="1px";
}
td.color="#"+_684[i][j];
td.onmouseover=function(e){
this.style.borderColor="white";
};
td.onmouseout=function(e){
this.style.borderColor="gray";
};
dojo.event.connect(td,"onmousedown",this,"click");
td.innerHTML="&nbsp;";
tr.appendChild(td);
}
_683.appendChild(tr);
}
if(dojo.render.html.ie){
this.bgIframe=document.createElement("<iframe frameborder='0' src='about:blank'>");
with(this.bgIframe.style){
position="absolute";
left=top="0px";
display="none";
}
dojo.html.body().appendChild(this.bgIframe);
dojo.style.setOpacity(this.bgIframe,0);
}
},click:function(e){
this.onColorSelect(e.currentTarget.color);
e.currentTarget.style.borderColor="gray";
},onColorSelect:function(_68c){
},hide:function(){
this.domNode.parentNode.removeChild(this.domNode);
if(this.bgIframe){
this.bgIframe.style.display="none";
}
},showAt:function(x,y){
with(this.domNode.style){
top=y+"px";
left=x+"px";
zIndex=999;
}
dojo.html.body().appendChild(this.domNode);
if(this.bgIframe){
with(this.bgIframe.style){
display="block";
top=y+"px";
left=x+"px";
zIndex=998;
width=dojo.html.getOuterWidth(this.domNode)+"px";
height=dojo.html.getOuterHeight(this.domNode)+"px";
}
}
}});
dojo.require("dojo.widget.ColorPalette");
dojo.provide("dojo.widget.HtmlColorPalette");
dojo.deprecated("dojo.widget.HtmlColorPalette","use dojo.widget.ColorPalette instead","0.3");
dojo.provide("dojo.widget.Menu2");
dojo.provide("dojo.widget.html.Menu2");
dojo.provide("dojo.widget.PopupMenu2");
dojo.provide("dojo.widget.MenuItem2");
dojo.require("dojo.html");
dojo.require("dojo.style");
dojo.require("dojo.event.*");
dojo.require("dojo.widget.*");
dojo.require("dojo.widget.HtmlWidget");
dojo.widget.PopupMenu2=function(){
dojo.widget.HtmlWidget.call(this);
this.items=[];
};
dojo.inherits(dojo.widget.PopupMenu2,dojo.widget.HtmlWidget);
dojo.lang.extend(dojo.widget.PopupMenu2,{widgetType:"PopupMenu2",isContainer:true,snarfChildDomOutput:true,currentSubmenu:null,currentSubmenuTrigger:null,parentMenu:null,isShowing:false,menuX:0,menuY:0,menuWidth:0,menuHeight:0,menuIndex:0,domNode:null,containerNode:null,templateString:"<div><div dojoAttachPoint=\"containerNode\"></div></div>",templateCssPath:dojo.uri.dojoUri("src/widget/templates/HtmlMenu2.css"),itemHeight:18,iconGap:1,accelGap:10,submenuGap:2,finalGap:5,submenuIconSize:4,separatorHeight:9,submenuDelay:500,submenuOverlap:5,contextMenuForWindow:false,submenuIconSrc:dojo.uri.dojoUri("src/widget/templates/images/submenu_off.gif").toString(),submenuIconOnSrc:dojo.uri.dojoUri("src/widget/templates/images/submenu_on.gif").toString(),postCreate:function(){
dojo.html.addClass(this.domNode,"dojoPopupMenu2");
dojo.html.addClass(this.containerNode,"dojoPopupMenu2Client");
this.domNode.style.left="-9999px";
this.domNode.style.top="-9999px";
if(this.contextMenuForWindow){
var doc=document.documentElement||dojo.html.body();
dojo.event.connect(doc,"oncontextmenu",this,"onOpen");
}
this.layoutMenuSoon();
},layoutMenuSoon:function(){
dojo.lang.setTimeout(this,"layoutMenu",0);
},layoutMenu:function(){
var _690=0;
var _691=0;
for(var i=0;i<this.children.length;i++){
if(this.children[i].getLabelWidth){
_690=Math.max(_690,this.children[i].getLabelWidth());
}
if(dojo.lang.isFunction(this.children[i].getAccelWidth)){
_691=Math.max(_691,this.children[i].getAccelWidth());
}
}
if(isNaN(_690)||isNaN(_691)){
this.layoutMenuSoon();
return;
}
var _693=dojo.style.getPixelValue(this.domNode,"padding-left",true)+dojo.style.getPixelValue(this.containerNode,"padding-left",true);
var _694=dojo.style.getPixelValue(this.domNode,"padding-top",true)+dojo.style.getPixelValue(this.containerNode,"padding-top",true);
if(isNaN(_693)||isNaN(_694)){
this.layoutMenuSoon();
return;
}
var y=_694;
var _696=0;
for(var i=0;i<this.children.length;i++){
var ch=this.children[i];
ch.layoutItem(_690,_691);
ch.topPosition=y;
y+=dojo.style.getOuterHeight(ch.domNode);
_696=Math.max(_696,dojo.style.getOuterWidth(ch.domNode));
}
dojo.style.setContentWidth(this.containerNode,_696);
dojo.style.setContentHeight(this.containerNode,y-_694);
dojo.style.setContentWidth(this.domNode,dojo.style.getOuterWidth(this.containerNode));
dojo.style.setContentHeight(this.domNode,dojo.style.getOuterHeight(this.containerNode));
this.menuWidth=dojo.style.getOuterWidth(this.domNode);
this.menuHeight=dojo.style.getOuterHeight(this.domNode);
},open:function(x,y,_69a,_69b){
if(this.isShowing){
return;
}
if(!_69a){
dojo.widget.html.Menu2Manager.opened(this,_69b);
}
if(this.animationInProgress){
return;
}
var _69c=dojo.html.getViewportSize();
var _69d=dojo.html.getScrollOffset();
var _69e={"left":_69d[0],"right":_69d[0]+_69c[0],"top":_69d[1],"bottom":_69d[1]+_69c[1]};
if(_69a){
if(x+this.menuWidth>_69e.right){
x=x-(this.menuWidth+_69a.menuWidth-(2*this.submenuOverlap));
}
if(y+this.menuHeight>_69e.bottom){
y=y-(this.menuHeight-(this.itemHeight+5));
}
}else{
if(x<_69e.left){
x=_69e.left;
}
if(x+this.menuWidth>_69e.right){
x=x-this.menuWidth;
}
if(y<_69e.top){
y=_69e.top;
}
if(y+this.menuHeight>_69e.bottom){
y=y-this.menuHeight;
}
}
this.parentMenu=_69a;
this.explodeSrc=_69b;
this.menuIndex=_69a?_69a.menuIndex+1:1;
this.menuX=x;
this.menuY=y;
this.domNode.style.zIndex=10+this.menuIndex;
this.domNode.style.left=x+"px";
this.domNode.style.top=y+"px";
this.domNode.style.display="none";
this.show();
this.isShowing=true;
},close:function(){
if(this.animationInProgress){
return;
}
this.closeSubmenu();
this.hide();
this.isShowing=false;
dojo.widget.html.Menu2Manager.closed(this);
},closeAll:function(){
if(this.parentMenu){
this.parentMenu.closeAll();
}else{
this.close();
}
},closeSubmenu:function(){
if(this.currentSubmenu==null){
return;
}
this.currentSubmenu.close();
this.currentSubmenu=null;
this.currentSubmenuTrigger.is_open=false;
this.currentSubmenuTrigger.closedSubmenu();
this.currentSubmenuTrigger=null;
},openSubmenu:function(_69f,_6a0){
var _6a1=dojo.style.getPixelValue(this.domNode,"left");
var _6a2=dojo.style.getPixelValue(this.domNode,"top");
var _6a3=dojo.style.getOuterWidth(this.domNode);
var _6a4=_6a0.topPosition;
var x=_6a1+_6a3-this.submenuOverlap;
var y=_6a2+_6a4;
this.currentSubmenu=_69f;
this.currentSubmenu.open(x,y,this,_6a0.domNode);
this.currentSubmenuTrigger=_6a0;
this.currentSubmenuTrigger.is_open=true;
},onOpen:function(e){
this.open(e.clientX,e.clientY,null,[e.clientX,e.clientY]);
if(e["preventDefault"]){
e.preventDefault();
}
},isPointInMenu:function(x,y){
if(x<this.menuX){
return 0;
}
if(x>this.menuX+this.menuWidth){
return 0;
}
if(y<this.menuY){
return 0;
}
if(y>this.menuY+this.menuHeight){
return 0;
}
return 1;
}});
dojo.widget.MenuItem2=function(){
dojo.widget.HtmlWidget.call(this);
};
dojo.inherits(dojo.widget.MenuItem2,dojo.widget.HtmlWidget);
dojo.lang.extend(dojo.widget.MenuItem2,{widgetType:"MenuItem2",templateString:"<div class=\"dojoMenuItem2\">"+"<div dojoAttachPoint=\"iconNode\" class=\"dojoMenuItem2Icon\"></div>"+"<span dojoAttachPoint=\"labelNode\" class=\"dojoMenuItem2Label\"><span><span></span></span></span>"+"<span dojoAttachPoint=\"accelNode\" class=\"dojoMenuItem2Accel\"><span><span></span></span></span>"+"<div dojoAttachPoint=\"submenuNode\" class=\"dojoMenuItem2Submenu\"></div>"+"<div dojoAttachPoint=\"targetNode\" class=\"dojoMenuItem2Target\" dojoAttachEvent=\"onMouseOver: onHover; onMouseOut: onUnhover; onClick;\">&nbsp;</div>"+"</div>",domNode:null,iconNode:null,labelNode:null,accelNode:null,submenuNode:null,targetNode:null,is_hovering:false,hover_timer:null,is_open:false,topPosition:0,is_disabled:false,caption:"Untitled",accelKey:"",iconSrc:"",submenuId:"",isDisabled:false,postCreate:function(){
dojo.html.disableSelection(this.domNode);
if(this.isDisabled){
this.setDisabled(true);
}
this.labelNode.childNodes[0].appendChild(document.createTextNode(this.caption));
this.accelNode.childNodes[0].appendChild(document.createTextNode(this.accelKey));
this.labelShadowNode=this.labelNode.childNodes[0].childNodes[0];
this.accelShadowNode=this.accelNode.childNodes[0].childNodes[0];
this.labelShadowNode.appendChild(document.createTextNode(this.caption));
this.accelShadowNode.appendChild(document.createTextNode(this.accelKey));
},layoutItem:function(_6aa,_6ab){
var _6ac=this.parent.itemHeight+this.parent.iconGap;
var _6ad=_6ac+_6aa+this.parent.accelGap;
var _6ae=_6ad+_6ab+this.parent.submenuGap;
var _6af=_6ae+this.parent.submenuIconSize+this.parent.finalGap;
this.iconNode.style.left="0px";
this.iconNode.style.top="0px";
if(this.iconSrc){
if((this.iconSrc.toLowerCase().substring(this.iconSrc.length-4)==".png")&&(dojo.render.html.ie)){
this.iconNode.style.filter="progid:DXImageTransform.Microsoft.AlphaImageLoader(src='"+this.iconSrc+"', sizingMethod='image')";
this.iconNode.style.backgroundImage="";
}else{
this.iconNode.style.backgroundImage="url("+this.iconSrc+")";
}
}else{
this.iconNode.style.backgroundImage="";
}
dojo.style.setOuterWidth(this.iconNode,this.parent.itemHeight);
dojo.style.setOuterHeight(this.iconNode,this.parent.itemHeight);
dojo.style.setOuterHeight(this.labelNode,this.parent.itemHeight);
dojo.style.setOuterHeight(this.accelNode,this.parent.itemHeight);
dojo.style.setContentWidth(this.domNode,_6af);
dojo.style.setContentHeight(this.domNode,this.parent.itemHeight);
this.labelNode.style.left=_6ac+"px";
this.accelNode.style.left=_6ad+"px";
this.submenuNode.style.left=_6ae+"px";
dojo.style.setOuterWidth(this.submenuNode,this.parent.submenuIconSize);
dojo.style.setOuterHeight(this.submenuNode,this.parent.itemHeight);
this.submenuNode.style.display=this.submenuId?"block":"none";
this.submenuNode.style.backgroundImage="url("+this.parent.submenuIconSrc+")";
dojo.style.setOuterWidth(this.targetNode,_6af);
dojo.style.setOuterHeight(this.targetNode,this.parent.itemHeight);
},onHover:function(){
if(this.is_hovering){
return;
}
if(this.is_open){
return;
}
this.parent.closeSubmenu();
this.highlightItem();
if(this.is_hovering){
this.stopSubmenuTimer();
}
this.is_hovering=1;
this.startSubmenuTimer();
},onUnhover:function(){
if(!this.is_open){
this.unhighlightItem();
}
this.is_hovering=0;
this.stopSubmenuTimer();
},onClick:function(){
if(this.is_disabled){
return;
}
if(this.submenuId){
if(!this.is_open){
this.stopSubmenuTimer();
this.openSubmenu();
}
}else{
this.parent.closeAll();
}
},highlightItem:function(){
dojo.html.addClass(this.domNode,"dojoMenuItem2Hover");
this.submenuNode.style.backgroundImage="url("+this.parent.submenuIconOnSrc+")";
},unhighlightItem:function(){
dojo.html.removeClass(this.domNode,"dojoMenuItem2Hover");
this.submenuNode.style.backgroundImage="url("+this.parent.submenuIconSrc+")";
},startSubmenuTimer:function(){
this.stopSubmenuTimer();
if(this.is_disabled){
return;
}
var self=this;
var _6b1=function(){
return function(){
self.openSubmenu();
};
}();
this.hover_timer=window.setTimeout(_6b1,this.parent.submenuDelay);
},stopSubmenuTimer:function(){
if(this.hover_timer){
window.clearTimeout(this.hover_timer);
this.hover_timer=null;
}
},openSubmenu:function(){
this.parent.closeSubmenu();
var _6b2=dojo.widget.getWidgetById(this.submenuId);
if(_6b2){
this.parent.openSubmenu(_6b2,this);
}
},closedSubmenu:function(){
this.onUnhover();
},setDisabled:function(_6b3){
if(_6b3==this.is_disabled){
return;
}
this.is_disabled=_6b3;
if(this.is_disabled){
dojo.html.addClass(this.domNode,"dojoMenuItem2Disabled");
}else{
dojo.html.removeClass(this.domNode,"dojoMenuItem2Disabled");
}
},getLabelWidth:function(){
var node=this.labelNode.childNodes[0];
return dojo.style.getOuterWidth(node);
},getAccelWidth:function(){
var node=this.accelNode.childNodes[0];
return dojo.style.getOuterWidth(node);
}});
dojo.widget.MenuSeparator2=function(){
dojo.widget.HtmlWidget.call(this);
};
dojo.inherits(dojo.widget.MenuSeparator2,dojo.widget.HtmlWidget);
dojo.lang.extend(dojo.widget.MenuSeparator2,{widgetType:"MenuSeparator2",domNode:null,topNode:null,bottomNode:null,templateString:"<div>"+"<div dojoAttachPoint=\"topNode\"></div>"+"<div dojoAttachPoint=\"bottomNode\"></div>"+"</div>",postCreate:function(){
dojo.html.addClass(this.domNode,"dojoMenuSeparator2");
dojo.html.addClass(this.topNode,"dojoMenuSeparator2Top");
dojo.html.addClass(this.bottomNode,"dojoMenuSeparator2Bottom");
dojo.html.disableSelection(this.domNode);
this.layoutItem();
},layoutItem:function(_6b6,_6b7){
var _6b8=this.parent.itemHeight+this.parent.iconGap+_6b6+this.parent.accelGap+_6b7+this.parent.submenuGap+this.parent.submenuIconSize+this.parent.finalGap;
if(isNaN(_6b8)){
return;
}
dojo.style.setContentHeight(this.domNode,this.parent.separatorHeight);
dojo.style.setContentWidth(this.domNode,_6b8);
}});
dojo.widget.html.Menu2Manager=new function(){
this.currentMenu=null;
this.currentButton=null;
this.focusNode=null;
this.closed=function(menu){
if(this.currentMenu==menu){
this.currentMenu=null;
this.currentButton=null;
}
};
this.opened=function(menu,_6bb){
if(menu==this.currentMenu){
return;
}
if(this.currentMenu){
this.currentMenu.close();
}
this.currentMenu=menu;
this.currentButton=_6bb;
};
this.onClick=function(e){
if(!this.currentMenu){
return;
}
var x=e.clientX;
var y=e.clientY;
var m=this.currentMenu;
while(m){
if(m.isPointInMenu(x,y)){
return;
}
m=m.currentSubmenu;
}
if(this.currentButton&&dojo.html.overElement(this.currentButton,e)){
return;
}
this.currentMenu.close();
};
dojo.event.browser.addListener(document,"mousedown",dojo.lang.hitch(this,"onClick"));
};
dojo.widget.tags.addParseTreeHandler("dojo:PopupMenu2");
dojo.widget.tags.addParseTreeHandler("dojo:MenuItem2");
dojo.widget.tags.addParseTreeHandler("dojo:MenuSeparator2");
dojo.provide("dojo.widget.Dialog");
dojo.provide("dojo.widget.HtmlDialog");
dojo.require("dojo.widget.*");
dojo.require("dojo.event.*");
dojo.require("dojo.graphics.color");
dojo.require("dojo.fx.*");
dojo.require("dojo.html");
dojo.widget.tags.addParseTreeHandler("dojo:dialog");
dojo.widget.HtmlDialog=function(){
dojo.widget.HtmlWidget.call(this);
this.resizeConnectArgs={srcObj:window,srcFunc:"onresize",adviceObj:this,adviceFunc:"onResize",rate:500};
};
dojo.inherits(dojo.widget.HtmlDialog,dojo.widget.HtmlWidget);
dojo.lang.extend(dojo.widget.HtmlDialog,{templatePath:dojo.uri.dojoUri("src/widget/templates/HtmlDialog.html"),widgetType:"Dialog",isContainer:true,_scrollConnected:false,_resizeConnected:false,focusElement:"",effect:"fade",effectDuration:250,bg:null,bgIframe:null,bgColor:"black",bgOpacity:0.4,followScroll:1,_fromTrap:false,anim:null,trapTabs:function(e){
if(e.target==this.tabStart){
if(this._fromTrap){
this._fromTrap=false;
}else{
this._fromTrap=true;
this.tabEnd.focus();
}
}else{
if(e.target==this.tabEnd){
if(this._fromTrap){
this._fromTrap=false;
}else{
this._fromTrap=true;
this.tabStart.focus();
}
}
}
},clearTrap:function(e){
var _6c2=this;
setTimeout(function(){
_6c2._fromTrap=false;
},100);
},postCreate:function(args,frag,_6c5){
with(this.domNode.style){
position="absolute";
zIndex=999;
display="none";
}
var b=dojo.html.body();
b.appendChild(this.domNode);
this.nodeRef=frag["dojo:"+this.widgetType.toLowerCase()]["nodeRef"];
if(this.nodeRef){
this.setContent(this.nodeRef);
}
this.bgIframe=new dojo.html.BackgroundIframe();
this.bg=document.createElement("div");
this.bg.className="dialogUnderlay";
with(this.bg.style){
position="absolute";
left=top="0px";
zIndex=998;
display="none";
}
this.setBackgroundColor(this.bgColor);
b.appendChild(this.bg);
this.bgIframe.setZIndex(this.bg);
},setContent:function(_6c7){
if(typeof _6c7=="string"){
this.containerNode.innerHTML=_6c7;
}else{
if(_6c7.nodeType!=undefined){
this.containerNode.appendChild(_6c7);
}else{
dojo.raise("Tried to setContent with unknown content ("+_6c7+")");
}
}
},setBackgroundColor:function(_6c8){
if(arguments.length>=3){
_6c8=new dojo.graphics.color.Color(arguments[0],arguments[1],arguments[2]);
}else{
_6c8=new dojo.graphics.color.Color(_6c8);
}
this.bg.style.backgroundColor=_6c8.toString();
return this.bgColor=_6c8;
},setBackgroundOpacity:function(op){
if(arguments.length==0){
op=this.bgOpacity;
}
dojo.style.setOpacity(this.bg,op);
try{
this.bgOpacity=dojo.style.getOpacity(this.bg);
}
catch(e){
this.bgOpacity=op;
}
return this.bgOpacity;
},sizeBackground:function(){
if(this.bgOpacity>0){
var h=document.documentElement.scrollHeight||dojo.html.body().scrollHeight;
var w=dojo.html.getViewportWidth();
this.bg.style.width=w+"px";
this.bg.style.height=h+"px";
this.bgIframe.size([0,0,w,h]);
}else{
this.bgIframe.size(this.domNode);
}
},showBackground:function(){
this.sizeBackground();
this.bgIframe.show();
if(this.bgOpacity>0){
this.bg.style.display="block";
}
},placeDialog:function(){
var _6cc=dojo.html.getScrollOffset();
var _6cd=dojo.html.getViewportSize();
this.domNode.style.display="block";
var w=this.domNode.offsetWidth;
var h=this.domNode.offsetHeight;
this.domNode.style.display="none";
var x=_6cc[0]+(_6cd[0]-w)/2;
var y=_6cc[1]+(_6cd[1]-h)/2;
with(this.domNode.style){
left=x+"px";
top=y+"px";
}
if(this.bgOpacity==0){
this.bgIframe.size([x,y,w,h]);
}
},show:function(){
this.setBackgroundOpacity();
this.placeDialog();
this.showBackground();
switch((this.effect||"").toLowerCase()){
case "fade":
this.domNode.style.display="block";
var _6d2=this;
if(this.anim){
this.anim.stop();
}
this.anim=dojo.fx.fade(this.domNode,this.effectDuration,0,1,function(node){
if(dojo.lang.isFunction(_6d2.onShow)){
_6d2.onShow(node);
}
});
break;
default:
this.domNode.style.display="block";
if(dojo.lang.isFunction(this.onShow)){
this.onShow(this.domNode);
}
break;
}
if(this.followScroll&&!this._scrollConnected){
this._scrollConnected=true;
dojo.event.connect(window,"onscroll",this,"onScroll");
}
if(!this._resizeConnected){
this._resizeConnected=true;
dojo.event.kwConnect(this.resizeConnectArgs);
}
},hide:function(){
if(this.focusElement){
dojo.byId(this.focusElement).focus();
dojo.byId(this.focusElement).blur();
}
switch((this.effect||"").toLowerCase()){
case "fade":
this.bg.style.display="none";
this.bgIframe.hide();
var _6d4=this;
if(this.anim){
this.anim.stop();
}
this.anim=dojo.fx.fadeOut(this.domNode,this.effectDuration,function(node){
node.style.display="none";
if(dojo.lang.isFunction(_6d4.onHide)){
_6d4.onHide(node);
}
_6d4.anim=null;
});
break;
default:
this.bg.style.display="none";
this.bgIframe.hide();
this.domNode.style.display="none";
if(dojo.lang.isFunction(this.onHide)){
this.onHide(node);
}
break;
}
this.bg.style.width=this.bg.style.height="1px";
if(this._scrollConnected){
this._scrollConnected=false;
dojo.event.disconnect(window,"onscroll",this,"onScroll");
}
if(this._resizeConnected){
this._resizeConnected=false;
dojo.event.kwDisconnect(this.resizeConnectArgs);
}
},setCloseControl:function(node){
dojo.event.connect(node,"onclick",this,"hide");
},setShowControl:function(node){
dojo.event.connect(node,"onclick",this,"show");
},onScroll:function(){
this.placeDialog();
this.domNode.style.display="block";
},onResize:function(e){
this.sizeBackground();
}});

