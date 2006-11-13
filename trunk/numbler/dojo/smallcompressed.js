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
var _106=node.tagName;
if(_106.substr(0,5).toLowerCase()!="dojo:"){
if(_106.substr(0,4).toLowerCase()=="dojo"){
return "dojo:"+_106.substring(4).toLowerCase();
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
var _108=node.className||node.getAttribute("class");
if((_108)&&(_108.indexOf)&&(_108.indexOf("dojo-")!=-1)){
var _109=_108.split(" ");
for(var x=0;x<_109.length;x++){
if((_109[x].length>5)&&(_109[x].indexOf("dojo-")>=0)){
return "dojo:"+_109[x].substr(5).toLowerCase();
}
}
}
}
}
return _106.toLowerCase();
};
dojo.dom.getUniqueId=function(){
do{
var id="dj_unique_"+(++arguments.callee._idIncrement);
}while(document.getElementById(id));
return id;
};
dojo.dom.getUniqueId._idIncrement=0;
dojo.dom.firstElement=dojo.dom.getFirstChildElement=function(_10c,_10d){
var node=_10c.firstChild;
while(node&&node.nodeType!=dojo.dom.ELEMENT_NODE){
node=node.nextSibling;
}
if(_10d&&node&&node.tagName&&node.tagName.toLowerCase()!=_10d.toLowerCase()){
node=dojo.dom.nextElement(node,_10d);
}
return node;
};
dojo.dom.lastElement=dojo.dom.getLastChildElement=function(_10f,_110){
var node=_10f.lastChild;
while(node&&node.nodeType!=dojo.dom.ELEMENT_NODE){
node=node.previousSibling;
}
if(_110&&node&&node.tagName&&node.tagName.toLowerCase()!=_110.toLowerCase()){
node=dojo.dom.prevElement(node,_110);
}
return node;
};
dojo.dom.nextElement=dojo.dom.getNextSiblingElement=function(node,_113){
if(!node){
return null;
}
do{
node=node.nextSibling;
}while(node&&node.nodeType!=dojo.dom.ELEMENT_NODE);
if(node&&_113&&_113.toLowerCase()!=node.tagName.toLowerCase()){
return dojo.dom.nextElement(node,_113);
}
return node;
};
dojo.dom.prevElement=dojo.dom.getPreviousSiblingElement=function(node,_115){
if(!node){
return null;
}
if(_115){
_115=_115.toLowerCase();
}
do{
node=node.previousSibling;
}while(node&&node.nodeType!=dojo.dom.ELEMENT_NODE);
if(node&&_115&&_115.toLowerCase()!=node.tagName.toLowerCase()){
return dojo.dom.prevElement(node,_115);
}
return node;
};
dojo.dom.moveChildren=function(_116,_117,trim){
var _119=0;
if(trim){
while(_116.hasChildNodes()&&_116.firstChild.nodeType==dojo.dom.TEXT_NODE){
_116.removeChild(_116.firstChild);
}
while(_116.hasChildNodes()&&_116.lastChild.nodeType==dojo.dom.TEXT_NODE){
_116.removeChild(_116.lastChild);
}
}
while(_116.hasChildNodes()){
_117.appendChild(_116.firstChild);
_119++;
}
return _119;
};
dojo.dom.copyChildren=function(_11a,_11b,trim){
var _11d=_11a.cloneNode(true);
return this.moveChildren(_11d,_11b,trim);
};
dojo.dom.removeChildren=function(node){
var _11f=node.childNodes.length;
while(node.hasChildNodes()){
node.removeChild(node.firstChild);
}
return _11f;
};
dojo.dom.replaceChildren=function(node,_121){
dojo.dom.removeChildren(node);
node.appendChild(_121);
};
dojo.dom.removeNode=function(node){
if(node&&node.parentNode){
return node.parentNode.removeChild(node);
}
};
dojo.dom.getAncestors=function(node,_124,_125){
var _126=[];
var _127=dojo.lang.isFunction(_124);
while(node){
if(!_127||_124(node)){
_126.push(node);
}
if(_125&&_126.length>0){
return _126[0];
}
node=node.parentNode;
}
if(_125){
return null;
}
return _126;
};
dojo.dom.getAncestorsByTag=function(node,tag,_12a){
tag=tag.toLowerCase();
return dojo.dom.getAncestors(node,function(el){
return ((el.tagName)&&(el.tagName.toLowerCase()==tag));
},_12a);
};
dojo.dom.getFirstAncestorByTag=function(node,tag){
return dojo.dom.getAncestorsByTag(node,tag,true);
};
dojo.dom.isDescendantOf=function(node,_12f,_130){
if(_130&&node){
node=node.parentNode;
}
while(node){
if(node==_12f){
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
dojo.dom.createDocumentFromText=function(str,_133){
if(!_133){
_133="text/xml";
}
if(typeof DOMParser!="undefined"){
var _134=new DOMParser();
return _134.parseFromString(str,_133);
}else{
if(typeof ActiveXObject!="undefined"){
var _135=new ActiveXObject("Microsoft.XMLDOM");
if(_135){
_135.async=false;
_135.loadXML(str);
return _135;
}else{
dojo.debug("toXml didn't work?");
}
}else{
if(document.createElement){
var tmp=document.createElement("xml");
tmp.innerHTML=str;
if(document.implementation&&document.implementation.createDocument){
var _137=document.implementation.createDocument("foo","",null);
for(var i=0;i<tmp.childNodes.length;i++){
_137.importNode(tmp.childNodes.item(i),true);
}
return _137;
}
return tmp.document&&tmp.document.firstChild?tmp.document.firstChild:tmp;
}
}
}
return null;
};
dojo.dom.prependChild=function(node,_13a){
if(_13a.firstChild){
_13a.insertBefore(node,_13a.firstChild);
}else{
_13a.appendChild(node);
}
return true;
};
dojo.dom.insertBefore=function(node,ref,_13d){
if(_13d!=true&&(node===ref||node.nextSibling===ref)){
return false;
}
var _13e=ref.parentNode;
_13e.insertBefore(node,ref);
return true;
};
dojo.dom.insertAfter=function(node,ref,_141){
var pn=ref.parentNode;
if(ref==pn.lastChild){
if((_141!=true)&&(node===ref)){
return false;
}
pn.appendChild(node);
}else{
return this.insertBefore(node,ref.nextSibling,_141);
}
return true;
};
dojo.dom.insertAtPosition=function(node,ref,_145){
if((!node)||(!ref)||(!_145)){
return false;
}
switch(_145.toLowerCase()){
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
dojo.dom.insertAtIndex=function(node,_147,_148){
var _149=_147.childNodes;
if(!_149.length){
_147.appendChild(node);
return true;
}
var _14a=null;
for(var i=0;i<_149.length;i++){
var _14c=_149.item(i)["getAttribute"]?parseInt(_149.item(i).getAttribute("dojoinsertionindex")):-1;
if(_14c<_148){
_14a=_149.item(i);
}
}
if(_14a){
return dojo.dom.insertAfter(node,_14a);
}else{
return dojo.dom.insertBefore(node,_149.item(0));
}
};
dojo.dom.textContent=function(node,text){
if(text){
dojo.dom.replaceChildren(node,document.createTextNode(text));
return text;
}else{
var _14f="";
if(node==null){
return _14f;
}
for(var i=0;i<node.childNodes.length;i++){
switch(node.childNodes[i].nodeType){
case 1:
case 5:
_14f+=dojo.dom.textContent(node.childNodes[i]);
break;
case 3:
case 2:
case 4:
_14f+=node.childNodes[i].nodeValue;
break;
default:
break;
}
}
return _14f;
}
};
dojo.dom.collectionToArray=function(_151){
var _152=new Array(_151.length);
for(var i=0;i<_151.length;i++){
_152[i]=_151[i];
}
return _152;
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
var _159=new dojo.uri.Uri(arguments[i].toString());
var _15a=new dojo.uri.Uri(uri.toString());
if(_159.path==""&&_159.scheme==null&&_159.authority==null&&_159.query==null){
if(_159.fragment!=null){
_15a.fragment=_159.fragment;
}
_159=_15a;
}else{
if(_159.scheme==null){
_159.scheme=_15a.scheme;
if(_159.authority==null){
_159.authority=_15a.authority;
if(_159.path.charAt(0)!="/"){
var path=_15a.path.substring(0,_15a.path.lastIndexOf("/")+1)+_159.path;
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
_159.path=segs.join("/");
}
}
}
}
uri="";
if(_159.scheme!=null){
uri+=_159.scheme+":";
}
if(_159.authority!=null){
uri+="//"+_159.authority;
}
uri+=_159.path;
if(_159.query!=null){
uri+="?"+_159.query;
}
if(_159.fragment!=null){
uri+="#"+_159.fragment;
}
}
this.uri=uri.toString();
var _15e="^(([^:/?#]+):)?(//([^/?#]*))?([^?#]*)(\\?([^#]*))?(#(.*))?$";
var r=this.uri.match(new RegExp(_15e));
this.scheme=r[2]||(r[1]?"":null);
this.authority=r[4]||(r[3]?"":null);
this.path=r[5];
this.query=r[7]||(r[6]?"":null);
this.fragment=r[9]||(r[8]?"":null);
if(this.authority!=null){
_15e="^((([^:]+:)?([^@]+))@)?([^:]*)(:([0-9]+))?$";
r=this.authority.match(new RegExp(_15e));
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
dojo.string.paramString=function(str,_165,_166){
for(var name in _165){
var re=new RegExp("\\%\\{"+name+"\\}","g");
str=str.replace(re,_165[name]);
}
if(_166){
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
var _16a=str.split(" ");
var _16b="";
var len=_16a.length;
for(var i=0;i<len;i++){
var word=_16a[i];
word=word.charAt(0).toUpperCase()+word.substring(1,word.length);
_16b+=word;
if(i<len-1){
_16b+=" ";
}
}
return new String(_16b);
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
var _172=escape(str);
var _173,re=/%u([0-9A-F]{4})/i;
while((_173=_172.match(re))){
var num=Number("0x"+_173[1]);
var _175=escape("&#"+num+";");
ret+=_172.substring(0,_173.index)+_175;
_172=_172.substring(_173.index+_173[0].length);
}
ret+=_172.replace(/\+/g,"%2B");
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
dojo.string.repeat=function(str,_17f,_180){
var out="";
for(var i=0;i<_17f;i++){
out+=str;
if(_180&&i<_17f-1){
out+=_180;
}
}
return out;
};
dojo.string.endsWith=function(str,end,_185){
if(_185){
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
dojo.string.startsWith=function(str,_189,_18a){
if(_18a){
str=str.toLowerCase();
_189=_189.toLowerCase();
}
return str.indexOf(_189)==0;
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
for(var _19a in dojo.string){
if(dojo.lang.isFunction(dojo.string[_19a])){
var func=(function(){
var meth=_19a;
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
String.prototype[_19a]=func;
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
var _1a3=1;
for(var i=1;i<=n;i++){
_1a3*=i;
}
return _1a3;
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
var _1af=dojo.lang.isArray(arguments[0])?arguments[0]:arguments;
var mean=0;
for(var i=0;i<_1af.length;i++){
mean+=_1af[i];
}
return mean/_1af.length;
};
dojo.math.round=function(_1b2,_1b3){
if(!_1b3){
var _1b4=1;
}else{
var _1b4=Math.pow(10,_1b3);
}
return Math.round(_1b2*_1b4)/_1b4;
};
dojo.math.sd=function(){
var _1b5=dojo.lang.isArray(arguments[0])?arguments[0]:arguments;
return Math.sqrt(dojo.math.variance(_1b5));
};
dojo.math.variance=function(){
var _1b6=dojo.lang.isArray(arguments[0])?arguments[0]:arguments;
var mean=0,squares=0;
for(var i=0;i<_1b6.length;i++){
mean+=_1b6[i];
squares+=Math.pow(_1b6[i],2);
}
return (squares/_1b6.length)-Math.pow(mean/_1b6.length,2);
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
dojo.lang.extend(dojo.graphics.color.Color,{toRgb:function(_1be){
if(_1be){
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
},blend:function(_1bf,_1c0){
return dojo.graphics.color.blend(this.toRgb(),new Color(_1bf).toRgb(),_1c0);
}});
dojo.graphics.color.named={white:[255,255,255],black:[0,0,0],red:[255,0,0],green:[0,255,0],blue:[0,0,255],navy:[0,0,128],gray:[128,128,128],silver:[192,192,192]};
dojo.graphics.color.blend=function(a,b,_1c3){
if(typeof a=="string"){
return dojo.graphics.color.blendHex(a,b,_1c3);
}
if(!_1c3){
_1c3=0;
}else{
if(_1c3>1){
_1c3=1;
}else{
if(_1c3<-1){
_1c3=-1;
}
}
}
var c=new Array(3);
for(var i=0;i<3;i++){
var half=Math.abs(a[i]-b[i])/2;
c[i]=Math.floor(Math.min(a[i],b[i])+half+(half*_1c3));
}
return c;
};
dojo.graphics.color.blendHex=function(a,b,_1c9){
return dojo.graphics.color.rgb2hex(dojo.graphics.color.blend(dojo.graphics.color.hex2rgb(a),dojo.graphics.color.hex2rgb(b),_1c9));
};
dojo.graphics.color.extractRGB=function(_1ca){
var hex="0123456789abcdef";
_1ca=_1ca.toLowerCase();
if(_1ca.indexOf("rgb")==0){
var _1cc=_1ca.match(/rgba*\((\d+), *(\d+), *(\d+)/i);
var ret=_1cc.splice(1,3);
return ret;
}else{
var _1ce=dojo.graphics.color.hex2rgb(_1ca);
if(_1ce){
return _1ce;
}else{
return dojo.graphics.color.named[_1ca]||[255,255,255];
}
}
};
dojo.graphics.color.hex2rgb=function(hex){
var _1d0="0123456789ABCDEF";
var rgb=new Array(3);
if(hex.indexOf("#")==0){
hex=hex.substring(1);
}
hex=hex.toUpperCase();
if(hex.replace(new RegExp("["+_1d0+"]","g"),"")!=""){
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
rgb[i]=_1d0.indexOf(rgb[i].charAt(0))*16+_1d0.indexOf(rgb[i].charAt(1));
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
var _1dd=v-min;
s=(v==0)?0:_1dd/v;
if(s==0){
h=0;
}else{
if(r==v){
h=60*(g-b)/_1dd;
}else{
if(g==v){
h=120+60*(b-r)/_1dd;
}else{
if(b==v){
h=240+60*(r-g)/_1dd;
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
var _1e4=h/60;
var i=Math.floor(_1e4);
var f=_1e4-i;
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
var _1f2=max-min;
l=(min+max)/2;
s=0;
if((l>0)&&(l<1)){
s=_1f2/((l<0.5)?(2*l):(2-2*l));
}
h=0;
if(_1f2>0){
if((max==r)&&(max!=g)){
h+=(g-b)/_1f2;
}
if((max==g)&&(max!=b)){
h+=(2+(b-r)/_1f2);
}
if((max==b)&&(max!=r)){
h+=(4+(r-g)/_1f2);
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
var _1fe=dojo.style.getStyle(node,"-moz-box-sizing");
if(!_1fe){
_1fe=dojo.style.getStyle(node,"box-sizing");
}
return (_1fe?_1fe:dojo.style.boxSizing.contentBox);
}
};
dojo.style.isBorderBox=function(node){
return (dojo.style.getBoxSizing(node)==dojo.style.boxSizing.borderBox);
};
dojo.style.getUnitValue=function(_200,_201,_202){
var _203={value:0,units:"px"};
var s=dojo.style.getComputedStyle(_200,_201);
if(s==""||(s=="auto"&&_202)){
return _203;
}
if(dojo.lang.isUndefined(s)){
_203.value=NaN;
}else{
var _205=s.match(/([\d.]+)([a-z%]*)/i);
if(!_205){
_203.value=NaN;
}else{
_203.value=Number(_205[1]);
_203.units=_205[2].toLowerCase();
}
}
return _203;
};
dojo.style.getPixelValue=function(_206,_207,_208){
var _209=dojo.style.getUnitValue(_206,_207,_208);
if(isNaN(_209.value)){
return 0;
}
if((_209.value)&&(_209.units!="px")){
return NaN;
}
return _209.value;
};
dojo.style.getNumericStyle=dojo.style.getPixelValue;
dojo.style.isPositionAbsolute=function(node){
return (dojo.style.getComputedStyle(node,"position")=="absolute");
};
dojo.style.getMarginWidth=function(node){
var _20c=dojo.style.isPositionAbsolute(node);
var left=dojo.style.getPixelValue(node,"margin-left",_20c);
var _20e=dojo.style.getPixelValue(node,"margin-right",_20c);
return left+_20e;
};
dojo.style.getBorderWidth=function(node){
var left=(dojo.style.getStyle(node,"border-left-style")=="none"?0:dojo.style.getPixelValue(node,"border-left-width"));
var _211=(dojo.style.getStyle(node,"border-right-style")=="none"?0:dojo.style.getPixelValue(node,"border-right-width"));
return left+_211;
};
dojo.style.getPaddingWidth=function(node){
var left=dojo.style.getPixelValue(node,"padding-left",true);
var _214=dojo.style.getPixelValue(node,"padding-right",true);
return left+_214;
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
dojo.style.setOuterWidth=function(node,_219){
if(!dojo.style.isBorderBox(node)){
_219-=dojo.style.getPaddingWidth(node)+dojo.style.getBorderWidth(node);
}
_219-=dojo.style.getMarginWidth(node);
if(!isNaN(_219)&&_219>0){
node.style.width=_219+"px";
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
var _21b=dojo.style.isPositionAbsolute(node);
var top=dojo.style.getPixelValue(node,"margin-top",_21b);
var _21d=dojo.style.getPixelValue(node,"margin-bottom",_21b);
return top+_21d;
};
dojo.style.getBorderHeight=function(node){
var top=(dojo.style.getStyle(node,"border-top-style")=="none"?0:dojo.style.getPixelValue(node,"border-top-width"));
var _220=(dojo.style.getStyle(node,"border-bottom-style")=="none"?0:dojo.style.getPixelValue(node,"border-bottom-width"));
return top+_220;
};
dojo.style.getPaddingHeight=function(node){
var top=dojo.style.getPixelValue(node,"padding-top",true);
var _223=dojo.style.getPixelValue(node,"padding-bottom",true);
return top+_223;
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
dojo.style.setOuterHeight=function(node,_228){
if(!dojo.style.isBorderBox(node)){
_228-=dojo.style.getPaddingHeight(node)+dojo.style.getBorderHeight(node);
}
_228-=dojo.style.getMarginHeight(node);
if(!isNaN(_228)&&_228>0){
node.style.height=_228+"px";
return true;
}else{
return false;
}
};
dojo.style.setContentWidth=function(node,_22a){
if(dojo.style.isBorderBox(node)){
_22a+=dojo.style.getPaddingWidth(node)+dojo.style.getBorderWidth(node);
}
if(!isNaN(_22a)&&_22a>0){
node.style.width=_22a+"px";
return true;
}else{
return false;
}
};
dojo.style.setContentHeight=function(node,_22c){
if(dojo.style.isBorderBox(node)){
_22c+=dojo.style.getPaddingHeight(node)+dojo.style.getBorderHeight(node);
}
if(!isNaN(_22c)&&_22c>0){
node.style.height=_22c+"px";
return true;
}else{
return false;
}
};
dojo.style.getContentBoxHeight=dojo.style.getContentHeight;
dojo.style.getBorderBoxHeight=dojo.style.getInnerHeight;
dojo.style.getMarginBoxHeight=dojo.style.getOuterHeight;
dojo.style.setMarginBoxHeight=dojo.style.setOuterHeight;
dojo.style.getTotalOffset=function(node,type,_22f){
var _230=(type=="top")?"offsetTop":"offsetLeft";
var _231=(type=="top")?"scrollTop":"scrollLeft";
var _232=(type=="top")?"y":"x";
var _233=0;
if(node["offsetParent"]){
if(dojo.render.html.safari&&node.style.getPropertyValue("position")=="absolute"&&node.parentNode==dojo.html.body()){
var _234=dojo.html.body();
}else{
var _234=dojo.html.body().parentNode;
}
if(_22f&&node.parentNode!=document.body){
_233-=dojo.style.sumAncestorProperties(node,_231);
}
do{
_233+=node[_230];
node=node.offsetParent;
}while(node!=_234&&node!=null);
}else{
if(node[_232]){
_233+=node[_232];
}
}
return _233;
};
dojo.style.sumAncestorProperties=function(node,prop){
if(!node){
return 0;
}
var _237=0;
while(node){
var val=node[prop];
if(val){
_237+=val-0;
}
node=node.parentNode;
}
return _237;
};
dojo.style.totalOffsetLeft=function(node,_23a){
return dojo.style.getTotalOffset(node,"left",_23a);
};
dojo.style.getAbsoluteX=dojo.style.totalOffsetLeft;
dojo.style.totalOffsetTop=function(node,_23c){
return dojo.style.getTotalOffset(node,"top",_23c);
};
dojo.style.getAbsoluteY=dojo.style.totalOffsetTop;
dojo.style.getAbsolutePosition=function(node,_23e){
var _23f=[dojo.style.getAbsoluteX(node,_23e),dojo.style.getAbsoluteY(node,_23e)];
_23f.x=_23f[0];
_23f.y=_23f[1];
return _23f;
};
dojo.style.styleSheet=null;
dojo.style.insertCssRule=function(_240,_241,_242){
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
_242=dojo.style.styleSheet.cssRules.length;
}else{
if(dojo.style.styleSheet.rules){
_242=dojo.style.styleSheet.rules.length;
}else{
return null;
}
}
}
if(dojo.style.styleSheet.insertRule){
var rule=_240+" { "+_241+" }";
return dojo.style.styleSheet.insertRule(rule,_242);
}else{
if(dojo.style.styleSheet.addRule){
return dojo.style.styleSheet.addRule(_240,_241,_242);
}else{
return null;
}
}
};
dojo.style.removeCssRule=function(_244){
if(!dojo.style.styleSheet){
dojo.debug("no stylesheet defined for removing rules");
return false;
}
if(dojo.render.html.ie){
if(!_244){
_244=dojo.style.styleSheet.rules.length;
dojo.style.styleSheet.removeRule(_244);
}
}else{
if(document.styleSheets[0]){
if(!_244){
_244=dojo.style.styleSheet.cssRules.length;
}
dojo.style.styleSheet.deleteRule(_244);
}
}
return true;
};
dojo.style.insertCssFile=function(URI,doc,_247){
if(!URI){
return;
}
if(!doc){
doc=document;
}
if(doc.baseURI){
URI=new dojo.uri.Uri(doc.baseURI,URI);
}
if(_247&&doc.styleSheets){
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
var _24d;
do{
_24d=dojo.style.getStyle(node,"background-color");
if(_24d.toLowerCase()=="rgba(0, 0, 0, 0)"){
_24d="transparent";
}
if(node==document.getElementsByTagName("body")[0]){
node=null;
break;
}
node=node.parentNode;
}while(node&&dojo.lang.inArray(_24d,["transparent",""]));
if(_24d=="transparent"){
_24d=[255,255,255,0];
}else{
_24d=dojo.graphics.color.extractRGB(_24d);
}
return _24d;
};
dojo.style.getComputedStyle=function(_24e,_24f,_250){
var _251=_250;
if(_24e.style.getPropertyValue){
_251=_24e.style.getPropertyValue(_24f);
}
if(!_251){
if(document.defaultView){
_251=document.defaultView.getComputedStyle(_24e,"").getPropertyValue(_24f);
}else{
if(_24e.currentStyle){
_251=_24e.currentStyle[dojo.style.toCamelCase(_24f)];
}
}
}
return _251;
};
dojo.style.getStyle=function(_252,_253){
var _254=dojo.style.toCamelCase(_253);
var _255=_252.style[_254];
return (_255?_255:dojo.style.getComputedStyle(_252,_253,_255));
};
dojo.style.toCamelCase=function(_256){
var arr=_256.split("-"),cc=arr[0];
for(var i=1;i<arr.length;i++){
cc+=arr[i].charAt(0).toUpperCase()+arr[i].substring(1);
}
return cc;
};
dojo.style.toSelectorCase=function(_259){
return _259.replace(/([A-Z])/g,"-$1").toLowerCase();
};
dojo.style.setOpacity=function setOpacity(node,_25b,_25c){
node=dojo.byId(node);
var h=dojo.render.html;
if(!_25c){
if(_25b>=1){
if(h.ie){
dojo.style.clearOpacity(node);
return;
}else{
_25b=0.999999;
}
}else{
if(_25b<0){
_25b=0;
}
}
}
if(h.ie){
if(node.nodeName.toLowerCase()=="tr"){
var tds=node.getElementsByTagName("td");
for(var x=0;x<tds.length;x++){
tds[x].style.filter="Alpha(Opacity="+_25b*100+")";
}
}
node.style.filter="Alpha(Opacity="+_25b*100+")";
}else{
if(h.moz){
node.style.opacity=_25b;
node.style.MozOpacity=_25b;
}else{
if(h.safari){
node.style.opacity=_25b;
node.style.KhtmlOpacity=_25b;
}else{
node.style.opacity=_25b;
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
dojo.html.disableSelection=function(_264){
_264=_264||dojo.html.body();
var h=dojo.render.html;
if(h.mozilla){
_264.style.MozUserSelect="none";
}else{
if(h.safari){
_264.style.KhtmlUserSelect="none";
}else{
if(h.ie){
_264.unselectable="on";
}else{
return false;
}
}
}
return true;
};
dojo.html.enableSelection=function(_266){
_266=_266||dojo.html.body();
var h=dojo.render.html;
if(h.mozilla){
_266.style.MozUserSelect="";
}else{
if(h.safari){
_266.style.KhtmlUserSelect="";
}else{
if(h.ie){
_266.unselectable="off";
}else{
return false;
}
}
}
return true;
};
dojo.html.selectElement=function(_268){
if(document.selection&&dojo.html.body().createTextRange){
var _269=dojo.html.body().createTextRange();
_269.moveToElementText(_268);
_269.select();
}else{
if(window["getSelection"]){
var _26a=window.getSelection();
if(_26a["selectAllChildren"]){
_26a.selectAllChildren(_268);
}
}
}
};
dojo.html.isSelectionCollapsed=function(){
if(document["selection"]){
return document.selection.createRange().text=="";
}else{
if(window["getSelection"]){
var _26b=window.getSelection();
if(dojo.lang.isString(_26b)){
return _26b=="";
}else{
return _26b.isCollapsed;
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
var _275=node;
type=type.toLowerCase();
while((_275)&&(_275.nodeName.toLowerCase()!=type)){
if(_275==(document["body"]||document["documentElement"])){
return null;
}
_275=_275.parentNode;
}
return _275;
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
dojo.html.hasClass=function(node,_281){
return dojo.lang.inArray(dojo.html.getClasses(node),_281);
};
dojo.html.prependClass=function(node,_283){
if(!node){
return false;
}
_283+=" "+dojo.html.getClass(node);
return dojo.html.setClass(node,_283);
};
dojo.html.addClass=function(node,_285){
if(!node){
return false;
}
if(dojo.html.hasClass(node,_285)){
return false;
}
_285=dojo.string.trim(dojo.html.getClass(node)+" "+_285);
return dojo.html.setClass(node,_285);
};
dojo.html.setClass=function(node,_287){
if(!node){
return false;
}
var cs=new String(_287);
try{
if(typeof node.className=="string"){
node.className=cs;
}else{
if(node.setAttribute){
node.setAttribute("class",_287);
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
dojo.html.removeClass=function(node,_28a,_28b){
if(!node){
return false;
}
var _28a=dojo.string.trim(new String(_28a));
try{
var cs=dojo.html.getClasses(node);
var nca=[];
if(_28b){
for(var i=0;i<cs.length;i++){
if(cs[i].indexOf(_28a)==-1){
nca.push(cs[i]);
}
}
}else{
for(var i=0;i<cs.length;i++){
if(cs[i]!=_28a){
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
dojo.html.replaceClass=function(node,_290,_291){
dojo.html.removeClass(node,_291);
dojo.html.addClass(node,_290);
};
dojo.html.classMatchType={ContainsAll:0,ContainsAny:1,IsOnly:2};
dojo.html.getElementsByClass=function(_292,_293,_294,_295){
if(!_293){
_293=document;
}
var _296=_292.split(/\s+/g);
var _297=[];
if(_295!=1&&_295!=2){
_295=0;
}
var _298=new RegExp("(\\s|^)(("+_296.join(")|(")+"))(\\s|$)");
if(!_294){
_294="*";
}
var _299=_293.getElementsByTagName(_294);
outer:
for(var i=0;i<_299.length;i++){
var node=_299[i];
var _29c=dojo.html.getClasses(node);
if(_29c.length==0){
continue outer;
}
var _29d=0;
for(var j=0;j<_29c.length;j++){
if(_298.test(_29c[j])){
if(_295==dojo.html.classMatchType.ContainsAny){
_297.push(node);
continue outer;
}else{
_29d++;
}
}else{
if(_295==dojo.html.classMatchType.IsOnly){
continue outer;
}
}
}
if(_29d==_296.length){
if(_295==dojo.html.classMatchType.IsOnly&&_29d==_29c.length){
_297.push(node);
}else{
if(_295==dojo.html.classMatchType.ContainsAll){
_297.push(node);
}
}
}
}
return _297;
};
dojo.html.getElementsByClassName=dojo.html.getElementsByClass;
dojo.html.gravity=function(node,e){
var _2a1=e.pageX||e.clientX+dojo.html.body().scrollLeft;
var _2a2=e.pageY||e.clientY+dojo.html.body().scrollTop;
with(dojo.html){
var _2a3=getAbsoluteX(node)+(getInnerWidth(node)/2);
var _2a4=getAbsoluteY(node)+(getInnerHeight(node)/2);
}
with(dojo.html.gravity){
return ((_2a1<_2a3?WEST:EAST)|(_2a2<_2a4?NORTH:SOUTH));
}
};
dojo.html.gravity.NORTH=1;
dojo.html.gravity.SOUTH=1<<1;
dojo.html.gravity.EAST=1<<2;
dojo.html.gravity.WEST=1<<3;
dojo.html.overElement=function(_2a5,e){
var _2a7=e.pageX||e.clientX+dojo.html.body().scrollLeft;
var _2a8=e.pageY||e.clientY+dojo.html.body().scrollTop;
with(dojo.html){
var top=getAbsoluteY(_2a5);
var _2aa=top+getInnerHeight(_2a5);
var left=getAbsoluteX(_2a5);
var _2ac=left+getInnerWidth(_2a5);
}
return (_2a7>=left&&_2a7<=_2ac&&_2a8>=top&&_2a8<=_2aa);
};
dojo.html.renderedTextContent=function(node){
var _2ae="";
if(node==null){
return _2ae;
}
for(var i=0;i<node.childNodes.length;i++){
switch(node.childNodes[i].nodeType){
case 1:
case 5:
var _2b0="unknown";
try{
_2b0=dojo.style.getStyle(node.childNodes[i],"display");
}
catch(E){
}
switch(_2b0){
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
_2ae+="\n";
_2ae+=dojo.html.renderedTextContent(node.childNodes[i]);
_2ae+="\n";
break;
case "none":
break;
default:
if(node.childNodes[i].tagName&&node.childNodes[i].tagName.toLowerCase()=="br"){
_2ae+="\n";
}else{
_2ae+=dojo.html.renderedTextContent(node.childNodes[i]);
}
break;
}
break;
case 3:
case 2:
case 4:
var text=node.childNodes[i].nodeValue;
var _2b2="unknown";
try{
_2b2=dojo.style.getStyle(node,"text-transform");
}
catch(E){
}
switch(_2b2){
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
switch(_2b2){
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
if(/\s$/.test(_2ae)){
text.replace(/^\s/,"");
}
break;
}
_2ae+=text;
break;
default:
break;
}
}
return _2ae;
};
dojo.html.setActiveStyleSheet=function(_2b3){
var i,a,main;
for(i=0;(a=document.getElementsByTagName("link")[i]);i++){
if(a.getAttribute("rel").indexOf("style")!=-1&&a.getAttribute("title")){
a.disabled=true;
if(a.getAttribute("title")==_2b3){
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
var _2ba="none";
if((/^<t[dh][\s>]/mi).test(dojo.string.trimStart(txt))){
txt="<table><tbody><tr>"+txt+"</tr></tbody></table>";
_2ba="cell";
}else{
if((/^<tr[\s>]/mi).test(dojo.string.trimStart(txt))){
txt="<table><tbody>"+txt+"</tbody></table>";
_2ba="row";
}else{
if((/^<(thead|tbody|tfoot)[\s>]/mi).test(dojo.string.trimStart(txt))){
txt="<table>"+txt+"</table>";
_2ba="section";
}
}
}
tn.innerHTML=txt;
tn.normalize();
var _2bb=null;
switch(_2ba){
case "cell":
_2bb=tn.getElementsByTagName("tr")[0];
break;
case "row":
_2bb=tn.getElementsByTagName("tbody")[0];
break;
case "section":
_2bb=tn.getElementsByTagName("table")[0];
break;
default:
_2bb=tn;
break;
}
var _2bc=[];
for(var x=0;x<_2bb.childNodes.length;x++){
_2bc.push(_2bb.childNodes[x].cloneNode(true));
}
tn.style.display="none";
document.body.removeChild(tn);
return _2bc;
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
dojo.html.toCoordinateArray=function(_2c1,_2c2){
if(dojo.lang.isArray(_2c1)){
while(_2c1.length<4){
_2c1.push(0);
}
while(_2c1.length>4){
_2c1.pop();
}
var ret=_2c1;
}else{
var node=dojo.byId(_2c1);
var ret=[dojo.html.getAbsoluteX(node,_2c2),dojo.html.getAbsoluteY(node,_2c2),dojo.html.getInnerWidth(node),dojo.html.getInnerHeight(node)];
}
ret.x=ret[0];
ret.y=ret[1];
ret.w=ret[2];
ret.h=ret[3];
return ret;
};
dojo.html.placeOnScreen=function(node,_2c6,_2c7,_2c8,_2c9){
if(dojo.lang.isArray(_2c6)){
_2c9=_2c8;
_2c8=_2c7;
_2c7=_2c6[1];
_2c6=_2c6[0];
}
if(!isNaN(_2c8)){
_2c8=[Number(_2c8),Number(_2c8)];
}else{
if(!dojo.lang.isArray(_2c8)){
_2c8=[0,0];
}
}
var _2ca=dojo.html.getScrollOffset();
var view=dojo.html.getViewportSize();
node=dojo.byId(node);
var w=node.offsetWidth+_2c8[0];
var h=node.offsetHeight+_2c8[1];
if(_2c9){
_2c6-=_2ca.x;
_2c7-=_2ca.y;
}
var x=_2c6+w;
if(x>view.w){
x=view.w-w;
}else{
x=_2c6;
}
x=Math.max(_2c8[0],x)+_2ca.x;
var y=_2c7+h;
if(y>view.h){
y=view.h-h;
}else{
y=_2c7;
}
y=Math.max(_2c8[1],y)+_2ca.y;
node.style.left=x+"px";
node.style.top=y+"px";
var ret=[x,y];
ret.x=x;
ret.y=y;
return ret;
};
dojo.html.placeOnScreenPoint=function(node,_2d2,_2d3,_2d4,_2d5){
if(dojo.lang.isArray(_2d2)){
_2d5=_2d4;
_2d4=_2d3;
_2d3=_2d2[1];
_2d2=_2d2[0];
}
var _2d6=dojo.html.getScrollOffset();
var view=dojo.html.getViewportSize();
node=dojo.byId(node);
var w=node.offsetWidth;
var h=node.offsetHeight;
if(_2d5){
_2d2-=_2d6.x;
_2d3-=_2d6.y;
}
var x=-1,y=-1;
if(_2d2+w<=view.w&&_2d3+h<=view.h){
x=_2d2;
y=_2d3;
}
if((x<0||y<0)&&_2d2<=view.w&&_2d3+h<=view.h){
x=_2d2-w;
y=_2d3;
}
if((x<0||y<0)&&_2d2+w<=view.w&&_2d3<=view.h){
x=_2d2;
y=_2d3-h;
}
if((x<0||y<0)&&_2d2<=view.w&&_2d3<=view.h){
x=_2d2-w;
y=_2d3-h;
}
if(x<0||y<0||(x+w>view.w)||(y+h>view.h)){
return dojo.html.placeOnScreen(node,_2d2,_2d3,_2d4,_2d5);
}
x+=_2d6.x;
y+=_2d6.y;
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
dojo.math.curves={Line:function(_2e3,end){
this.start=_2e3;
this.end=end;
this.dimensions=_2e3.length;
for(var i=0;i<_2e3.length;i++){
_2e3[i]=Number(_2e3[i]);
}
for(var i=0;i<end.length;i++){
end[i]=Number(end[i]);
}
this.getValue=function(n){
var _2e7=new Array(this.dimensions);
for(var i=0;i<this.dimensions;i++){
_2e7[i]=((this.end[i]-this.start[i])*n)+this.start[i];
}
return _2e7;
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
var _2eb=new Array(this.p[0].length);
for(var k=0;j<this.p[0].length;k++){
_2eb[k]=0;
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
_2eb[j]=C/D;
}
return _2eb;
};
this.p=pnts;
return this;
},CatmullRom:function(pnts,c){
this.getValue=function(step){
var _2f5=step*(this.p.length-1);
var node=Math.floor(_2f5);
var _2f7=_2f5-node;
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
var u=_2f7;
var u2=_2f7*_2f7;
var u3=_2f7*_2f7*_2f7;
var _2ff=new Array(this.p[0].length);
for(var k=0;k<this.p[0].length;k++){
var x1=(-this.c*this.p[i0][k])+((2-this.c)*this.p[i][k])+((this.c-2)*this.p[i1][k])+(this.c*this.p[i2][k]);
var x2=(2*this.c*this.p[i0][k])+((this.c-3)*this.p[i][k])+((3-2*this.c)*this.p[i1][k])+(-this.c*this.p[i2][k]);
var x3=(-this.c*this.p[i0][k])+(this.c*this.p[i1][k]);
var x4=this.p[i][k];
_2ff[k]=x1*u3+x2*u2+x3*u+x4;
}
return _2ff;
};
if(!c){
this.c=0.7;
}else{
this.c=c;
}
this.p=pnts;
return this;
},Arc:function(_305,end,ccw){
var _308=dojo.math.points.midpoint(_305,end);
var _309=dojo.math.points.translate(dojo.math.points.invert(_308),_305);
var rad=Math.sqrt(Math.pow(_309[0],2)+Math.pow(_309[1],2));
var _30b=dojo.math.radToDeg(Math.atan(_309[1]/_309[0]));
if(_309[0]<0){
_30b-=90;
}else{
_30b+=90;
}
dojo.math.curves.CenteredArc.call(this,_308,rad,_30b,_30b+(ccw?-180:180));
},CenteredArc:function(_30c,_30d,_30e,end){
this.center=_30c;
this.radius=_30d;
this.start=_30e||0;
this.end=end;
this.getValue=function(n){
var _311=new Array(2);
var _312=dojo.math.degToRad(this.start+((this.end-this.start)*n));
_311[0]=this.center[0]+this.radius*Math.sin(_312);
_311[1]=this.center[1]-this.radius*Math.cos(_312);
return _311;
};
return this;
},Circle:function(_313,_314){
dojo.math.curves.CenteredArc.call(this,_313,_314,0,360);
return this;
},Path:function(){
var _315=[];
var _316=[];
var _317=[];
var _318=0;
this.add=function(_319,_31a){
if(_31a<0){
dojo.raise("dojo.math.curves.Path.add: weight cannot be less than 0");
}
_315.push(_319);
_316.push(_31a);
_318+=_31a;
computeRanges();
};
this.remove=function(_31b){
for(var i=0;i<_315.length;i++){
if(_315[i]==_31b){
_315.splice(i,1);
_318-=_316.splice(i,1)[0];
break;
}
}
computeRanges();
};
this.removeAll=function(){
_315=[];
_316=[];
_318=0;
};
this.getValue=function(n){
var _31e=false,value=0;
for(var i=0;i<_317.length;i++){
var r=_317[i];
if(n>=r[0]&&n<r[1]){
var subN=(n-r[0])/r[2];
value=_315[i].getValue(subN);
_31e=true;
break;
}
}
if(!_31e){
value=_315[_315.length-1].getValue(1);
}
for(j=0;j<i;j++){
value=dojo.math.points.translate(value,_315[j].getValue(1));
}
return value;
};
function computeRanges(){
var _322=0;
for(var i=0;i<_316.length;i++){
var end=_322+_316[i]/_318;
var len=end-_322;
_317[i]=[_322,end,len];
_322=end;
}
}
return this;
}};
dojo.provide("dojo.animation");
dojo.provide("dojo.animation.Animation");
dojo.require("dojo.lang");
dojo.require("dojo.math");
dojo.require("dojo.math.curves");
dojo.animation.Animation=function(_326,_327,_328,_329,rate){
this.curve=_326;
this.duration=_327;
this.repeatCount=_329||0;
this.rate=rate||25;
if(_328){
if(dojo.lang.isFunction(_328.getValue)){
this.accel=_328;
}else{
var i=0.35*_328+0.5;
this.accel=new dojo.math.curves.CatmullRom([[0],[i],[1]],0.45);
}
}
};
dojo.lang.extend(dojo.animation.Animation,{curve:null,duration:0,repeatCount:0,accel:null,onBegin:null,onAnimate:null,onEnd:null,onPlay:null,onPause:null,onStop:null,handler:null,_animSequence:null,_startTime:null,_endTime:null,_lastFrame:null,_timer:null,_percent:0,_active:false,_paused:false,_startRepeatCount:0,play:function(_32c){
if(_32c){
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
},gotoPercent:function(pct,_330){
clearTimeout(this._timer);
this._active=true;
this._paused=true;
this._percent=pct;
if(_330){
this.play();
}
},stop:function(_331){
clearTimeout(this._timer);
var step=this._percent/100;
if(_331){
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
dojo.animation.AnimationEvent=function(anim,type,_339,_33a,_33b,_33c,dur,pct,fps){
this.type=type;
this.animation=anim;
this.coords=_339;
this.x=_339[0];
this.y=_339[1];
this.z=_339[2];
this.startTime=_33a;
this.currentTime=_33b;
this.endTime=_33c;
this.duration=dur;
this.percent=pct;
this.fps=fps;
};
dojo.lang.extend(dojo.animation.AnimationEvent,{coordsAsInts:function(){
var _340=new Array(this.coords.length);
for(var i=0;i<this.coords.length;i++){
_340[i]=Math.round(this.coords[i]);
}
return _340;
}});
dojo.animation.AnimationSequence=function(_342){
this.repeatCount=_342||0;
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
},play:function(_347){
if(this._anims.length==0){
return;
}
if(_347||!this._anims[this._currAnim]){
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
this._anims[this._currAnim].play(_347);
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
var _34e=dojo.lang.nameAnonFunc(args[2],ao.adviceObj);
ao.adviceObj[_34e]=args[2];
ao.adviceFunc=_34e;
}else{
if((typeof args[0]=="function")&&(typeof args[1]=="object")&&(typeof args[2]=="string")){
ao.adviceType="after";
ao.srcObj=dj_global;
var _34e=dojo.lang.nameAnonFunc(args[0],ao.srcObj);
ao.srcObj[_34e]=args[0];
ao.srcFunc=_34e;
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
this._kwConnectImpl=function(_356,_357){
var fn=(_357)?"disconnect":"connect";
if(typeof _356["srcFunc"]=="function"){
_356.srcObj=_356["srcObj"]||dj_global;
var _359=dojo.lang.nameAnonFunc(_356.srcFunc,_356.srcObj);
_356.srcFunc=_359;
}
if(typeof _356["adviceFunc"]=="function"){
_356.adviceObj=_356["adviceObj"]||dj_global;
var _359=dojo.lang.nameAnonFunc(_356.adviceFunc,_356.adviceObj);
_356.adviceFunc=_359;
}
return dojo.event[fn]((_356["type"]||_356["adviceType"]||"after"),_356["srcObj"]||dj_global,_356["srcFunc"],_356["adviceObj"]||_356["targetObj"]||dj_global,_356["adviceFunc"]||_356["targetFunc"],_356["aroundObj"],_356["aroundFunc"],_356["once"],_356["delay"],_356["rate"],_356["adviceMsg"]||false);
};
this.kwConnect=function(_35a){
return this._kwConnectImpl(_35a,false);
};
this.disconnect=function(){
var ao=interpolateArgs(arguments);
if(!ao.adviceFunc){
return;
}
var mjp=dojo.event.MethodJoinPoint.getForMethod(ao.srcObj,ao.srcFunc);
return mjp.removeAdvice(ao.adviceObj,ao.adviceFunc,ao.adviceType,ao.once);
};
this.kwDisconnect=function(_35d){
return this._kwConnectImpl(_35d,true);
};
};
dojo.event.MethodInvocation=function(_35e,obj,args){
this.jp_=_35e;
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
dojo.event.MethodJoinPoint=function(obj,_366){
this.object=obj||dj_global;
this.methodname=_366;
this.methodfunc=this.object[_366];
this.before=[];
this.after=[];
this.around=[];
};
dojo.event.MethodJoinPoint.getForMethod=function(obj,_368){
if(!obj){
obj=dj_global;
}
if(!obj[_368]){
obj[_368]=function(){
};
}else{
if((!dojo.lang.isFunction(obj[_368]))&&(!dojo.lang.isAlien(obj[_368]))){
return null;
}
}
var _369=_368+"$joinpoint";
var _36a=_368+"$joinpoint$method";
var _36b=obj[_369];
if(!_36b){
var _36c=false;
if(dojo.event["browser"]){
if((obj["attachEvent"])||(obj["nodeType"])||(obj["addEventListener"])){
_36c=true;
dojo.event.browser.addClobberNodeAttrs(obj,[_369,_36a,_368]);
}
}
obj[_36a]=obj[_368];
_36b=obj[_369]=new dojo.event.MethodJoinPoint(obj,_36a);
obj[_368]=function(){
var args=[];
if((_36c)&&(!arguments.length)&&(window.event)){
args.push(dojo.event.browser.fixEvent(window.event));
}else{
for(var x=0;x<arguments.length;x++){
if((x==0)&&(_36c)&&(dojo.event.browser.isEvent(arguments[x]))){
args.push(dojo.event.browser.fixEvent(arguments[x]));
}else{
args.push(arguments[x]);
}
}
}
return _36b.run.apply(_36b,args);
};
}
return _36b;
};
dojo.lang.extend(dojo.event.MethodJoinPoint,{unintercept:function(){
this.object[this.methodname]=this.methodfunc;
},run:function(){
var obj=this.object||dj_global;
var args=arguments;
var _371=[];
for(var x=0;x<args.length;x++){
_371[x]=args[x];
}
var _373=function(marr){
if(!marr){
dojo.debug("Null argument to unrollAdvice()");
return;
}
var _375=marr[0]||dj_global;
var _376=marr[1];
if(!_375[_376]){
dojo.raise("function \""+_376+"\" does not exist on \""+_375+"\"");
}
var _377=marr[2]||dj_global;
var _378=marr[3];
var msg=marr[6];
var _37a;
var to={args:[],jp_:this,object:obj,proceed:function(){
return _375[_376].apply(_375,to.args);
}};
to.args=_371;
var _37c=parseInt(marr[4]);
var _37d=((!isNaN(_37c))&&(marr[4]!==null)&&(typeof marr[4]!="undefined"));
if(marr[5]){
var rate=parseInt(marr[5]);
var cur=new Date();
var _380=false;
if((marr["last"])&&((cur-marr.last)<=rate)){
if(dojo.event.canTimeout){
if(marr["delayTimer"]){
clearTimeout(marr.delayTimer);
}
var tod=parseInt(rate*2);
var mcpy=dojo.lang.shallowCopy(marr);
marr.delayTimer=setTimeout(function(){
mcpy[5]=0;
_373(mcpy);
},tod);
}
return;
}else{
marr.last=cur;
}
}
if(_378){
_377[_378].call(_377,to);
}else{
if((_37d)&&((dojo.render.html)||(dojo.render.svg))){
dj_global["setTimeout"](function(){
if(msg){
_375[_376].call(_375,to);
}else{
_375[_376].apply(_375,args);
}
},_37c);
}else{
if(msg){
_375[_376].call(_375,to);
}else{
_375[_376].apply(_375,args);
}
}
}
};
if(this.before.length>0){
dojo.lang.forEach(this.before,_373,true);
}
var _383;
if(this.around.length>0){
var mi=new dojo.event.MethodInvocation(this,obj,args);
_383=mi.proceed();
}else{
if(this.methodfunc){
_383=this.object[this.methodname].apply(this.object,args);
}
}
if(this.after.length>0){
dojo.lang.forEach(this.after,_373,true);
}
return (this.methodfunc)?_383:null;
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
},addAdvice:function(_388,_389,_38a,_38b,_38c,_38d,once,_38f,rate,_391){
var arr=this.getArr(_38c);
if(!arr){
dojo.raise("bad this: "+this);
}
var ao=[_388,_389,_38a,_38b,_38f,rate,_391];
if(once){
if(this.hasAdvice(_388,_389,_38c,arr)>=0){
return;
}
}
if(_38d=="first"){
arr.unshift(ao);
}else{
arr.push(ao);
}
},hasAdvice:function(_394,_395,_396,arr){
if(!arr){
arr=this.getArr(_396);
}
var ind=-1;
for(var x=0;x<arr.length;x++){
if((arr[x][0]==_394)&&(arr[x][1]==_395)){
ind=x;
}
}
return ind;
},removeAdvice:function(_39a,_39b,_39c,once){
var arr=this.getArr(_39c);
var ind=this.hasAdvice(_39a,_39b,_39c,arr);
if(ind==-1){
return false;
}
while(ind!=-1){
arr.splice(ind,1);
if(once){
break;
}
ind=this.hasAdvice(_39a,_39b,_39c,arr);
}
return true;
}});
dojo.require("dojo.event");
dojo.provide("dojo.event.topic");
dojo.event.topic=new function(){
this.topics={};
this.getTopic=function(_3a0){
if(!this.topics[_3a0]){
this.topics[_3a0]=new this.TopicImpl(_3a0);
}
return this.topics[_3a0];
};
this.registerPublisher=function(_3a1,obj,_3a3){
var _3a1=this.getTopic(_3a1);
_3a1.registerPublisher(obj,_3a3);
};
this.subscribe=function(_3a4,obj,_3a6){
var _3a4=this.getTopic(_3a4);
_3a4.subscribe(obj,_3a6);
};
this.unsubscribe=function(_3a7,obj,_3a9){
var _3a7=this.getTopic(_3a7);
_3a7.unsubscribe(obj,_3a9);
};
this.publish=function(_3aa,_3ab){
var _3aa=this.getTopic(_3aa);
var args=[];
if((arguments.length==2)&&(_3ab.length)&&(typeof _3ab!="string")){
args=_3ab;
}else{
var args=[];
for(var x=1;x<arguments.length;x++){
args.push(arguments[x]);
}
}
_3aa.sendMessage.apply(_3aa,args);
};
};
dojo.event.topic.TopicImpl=function(_3ae){
this.topicName=_3ae;
var self=this;
self.subscribe=function(_3b0,_3b1){
var tf=_3b1||_3b0;
var to=(!_3b1)?dj_global:_3b0;
dojo.event.kwConnect({srcObj:self,srcFunc:"sendMessage",adviceObj:to,adviceFunc:tf});
};
self.unsubscribe=function(_3b4,_3b5){
var tf=(!_3b5)?_3b4:_3b5;
var to=(!_3b5)?null:_3b4;
dojo.event.kwDisconnect({srcObj:self,srcFunc:"sendMessage",adviceObj:to,adviceFunc:tf});
};
self.registerPublisher=function(_3b8,_3b9){
dojo.event.connect(_3b8,_3b9,self,"sendMessage");
};
self.sendMessage=function(_3ba){
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
this.clobber=function(_3bd){
var na;
var tna;
if(_3bd){
tna=_3bd.getElementsByTagName("*");
na=[_3bd];
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
var _3c1={};
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
var _3c5=0;
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
this.addClobberNodeAttrs=function(node,_3c9){
this.addClobberNode(node);
for(var x=0;x<_3c9.length;x++){
node.__clobberAttrs__.push(_3c9[x]);
}
};
this.removeListener=function(node,_3cc,fp,_3ce){
if(!_3ce){
var _3ce=false;
}
_3cc=_3cc.toLowerCase();
if(_3cc.substr(0,2)=="on"){
_3cc=_3cc.substr(2);
}
if(node.removeEventListener){
node.removeEventListener(_3cc,fp,_3ce);
}
};
this.addListener=function(node,_3d0,fp,_3d2,_3d3){
if(!node){
return;
}
if(!_3d2){
var _3d2=false;
}
_3d0=_3d0.toLowerCase();
if(_3d0.substr(0,2)!="on"){
_3d0="on"+_3d0;
}
if(!_3d3){
var _3d4=function(evt){
if(!evt){
evt=window.event;
}
var ret=fp(dojo.event.browser.fixEvent(evt));
if(_3d2){
dojo.event.browser.stopEvent(evt);
}
return ret;
};
}else{
_3d4=fp;
}
if(node.addEventListener){
node.addEventListener(_3d0.substr(2),_3d4,_3d2);
return _3d4;
}else{
if(typeof node[_3d0]=="function"){
var _3d7=node[_3d0];
node[_3d0]=function(e){
_3d7(e);
return _3d4(e);
};
}else{
node[_3d0]=_3d4;
}
if(dojo.render.html.ie){
this.addClobberNodeAttrs(node,[_3d0]);
}
return _3d4;
}
};
this.isEvent=function(obj){
return (typeof obj!="undefined")&&(typeof Event!="undefined")&&(obj.eventPhase);
};
this.currentEvent=null;
this.callListener=function(_3da,_3db){
if(typeof _3da!="function"){
dojo.raise("listener not a function: "+_3da);
}
dojo.event.browser.currentEvent.currentTarget=_3db;
return _3da.call(_3db,dojo.event.browser.currentEvent);
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

