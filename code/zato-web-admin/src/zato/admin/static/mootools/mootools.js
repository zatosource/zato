/*
---
MooTools: the javascript framework

web build:
 - http://mootools.net/core/58f64dfefa42b08cb566c95a6244e613

packager build:
 - packager build Core/Class

copyrights:
  - [MooTools](http://mootools.net)

licenses:
  - [MIT License](http://mootools.net/license.txt)
...
*/
(function(){this.MooTools={version:"1.4.1",build:"d1fb25710e3c5482a219ab9dc675a4e0ad2176b6"};var o=this.typeOf=function(i){if(i==null){return"null";}if(i.$family){return i.$family();
}if(i.nodeName){if(i.nodeType==1){return"element";}if(i.nodeType==3){return(/\S/).test(i.nodeValue)?"textnode":"whitespace";}}else{if(typeof i.length=="number"){if(i.callee){return"arguments";
}if("item" in i){return"collection";}}}return typeof i;};var j=this.instanceOf=function(t,i){if(t==null){return false;}var s=t.$constructor||t.constructor;
while(s){if(s===i){return true;}s=s.parent;}return t instanceof i;};var f=this.Function;var p=true;for(var k in {toString:1}){p=null;}if(p){p=["hasOwnProperty","valueOf","isPrototypeOf","propertyIsEnumerable","toLocaleString","toString","constructor"];
}f.prototype.overloadSetter=function(s){var i=this;return function(u,t){if(u==null){return this;}if(s||typeof u!="string"){for(var v in u){i.call(this,v,u[v]);
}if(p){for(var w=p.length;w--;){v=p[w];if(u.hasOwnProperty(v)){i.call(this,v,u[v]);}}}}else{i.call(this,u,t);}return this;};};f.prototype.overloadGetter=function(s){var i=this;
return function(u){var v,t;if(s||typeof u!="string"){v=u;}else{if(arguments.length>1){v=arguments;}}if(v){t={};for(var w=0;w<v.length;w++){t[v[w]]=i.call(this,v[w]);
}}else{t=i.call(this,u);}return t;};};f.prototype.extend=function(i,s){this[i]=s;}.overloadSetter();f.prototype.implement=function(i,s){this.prototype[i]=s;
}.overloadSetter();var n=Array.prototype.slice;f.from=function(i){return(o(i)=="function")?i:function(){return i;};};Array.from=function(i){if(i==null){return[];
}return(a.isEnumerable(i)&&typeof i!="string")?(o(i)=="array")?i:n.call(i):[i];};Number.from=function(s){var i=parseFloat(s);return isFinite(i)?i:null;
};String.from=function(i){return i+"";};f.implement({hide:function(){this.$hidden=true;return this;},protect:function(){this.$protected=true;return this;
}});var a=this.Type=function(u,t){if(u){var s=u.toLowerCase();var i=function(v){return(o(v)==s);};a["is"+u]=i;if(t!=null){t.prototype.$family=(function(){return s;
}).hide();}}if(t==null){return null;}t.extend(this);t.$constructor=a;t.prototype.$constructor=t;return t;};var e=Object.prototype.toString;a.isEnumerable=function(i){return(i!=null&&typeof i.length=="number"&&e.call(i)!="[object Function]");
};var q={};var r=function(i){var s=o(i.prototype);return q[s]||(q[s]=[]);};var b=function(t,x){if(x&&x.$hidden){return;}var s=r(this);for(var u=0;u<s.length;
u++){var w=s[u];if(o(w)=="type"){b.call(w,t,x);}else{w.call(this,t,x);}}var v=this.prototype[t];if(v==null||!v.$protected){this.prototype[t]=x;}if(this[t]==null&&o(x)=="function"){m.call(this,t,function(i){return x.apply(i,n.call(arguments,1));
});}};var m=function(i,t){if(t&&t.$hidden){return;}var s=this[i];if(s==null||!s.$protected){this[i]=t;}};a.implement({implement:b.overloadSetter(),extend:m.overloadSetter(),alias:function(i,s){b.call(this,i,this.prototype[s]);
}.overloadSetter(),mirror:function(i){r(this).push(i);return this;}});new a("Type",a);var d=function(s,w,u){var t=(w!=Object),A=w.prototype;if(t){w=new a(s,w);
}for(var x=0,v=u.length;x<v;x++){var B=u[x],z=w[B],y=A[B];if(z){z.protect();}if(t&&y){delete A[B];A[B]=y.protect();}}if(t){w.implement(A);}return d;};d("String",String,["charAt","charCodeAt","concat","indexOf","lastIndexOf","match","quote","replace","search","slice","split","substr","substring","trim","toLowerCase","toUpperCase"])("Array",Array,["pop","push","reverse","shift","sort","splice","unshift","concat","join","slice","indexOf","lastIndexOf","filter","forEach","every","map","some","reduce","reduceRight"])("Number",Number,["toExponential","toFixed","toLocaleString","toPrecision"])("Function",f,["apply","call","bind"])("RegExp",RegExp,["exec","test"])("Object",Object,["create","defineProperty","defineProperties","keys","getPrototypeOf","getOwnPropertyDescriptor","getOwnPropertyNames","preventExtensions","isExtensible","seal","isSealed","freeze","isFrozen"])("Date",Date,["now"]);
Object.extend=m.overloadSetter();Date.extend("now",function(){return +(new Date);});new a("Boolean",Boolean);Number.prototype.$family=function(){return isFinite(this)?"number":"null";
}.hide();Number.extend("random",function(s,i){return Math.floor(Math.random()*(i-s+1)+s);});var g=Object.prototype.hasOwnProperty;Object.extend("forEach",function(i,t,u){for(var s in i){if(g.call(i,s)){t.call(u,i[s],s,i);
}}});Object.each=Object.forEach;Array.implement({forEach:function(u,v){for(var t=0,s=this.length;t<s;t++){if(t in this){u.call(v,this[t],t,this);}}},each:function(i,s){Array.forEach(this,i,s);
return this;}});var l=function(i){switch(o(i)){case"array":return i.clone();case"object":return Object.clone(i);default:return i;}};Array.implement("clone",function(){var s=this.length,t=new Array(s);
while(s--){t[s]=l(this[s]);}return t;});var h=function(s,i,t){switch(o(t)){case"object":if(o(s[i])=="object"){Object.merge(s[i],t);}else{s[i]=Object.clone(t);
}break;case"array":s[i]=t.clone();break;default:s[i]=t;}return s;};Object.extend({merge:function(z,u,t){if(o(u)=="string"){return h(z,u,t);}for(var y=1,s=arguments.length;
y<s;y++){var w=arguments[y];for(var x in w){h(z,x,w[x]);}}return z;},clone:function(i){var t={};for(var s in i){t[s]=l(i[s]);}return t;},append:function(w){for(var v=1,t=arguments.length;
v<t;v++){var s=arguments[v]||{};for(var u in s){w[u]=s[u];}}return w;}});["Object","WhiteSpace","TextNode","Collection","Arguments"].each(function(i){new a(i);
});var c=Date.now();String.extend("uniqueID",function(){return(c++).toString(36);});})();Array.implement({every:function(c,d){for(var b=0,a=this.length>>>0;
b<a;b++){if((b in this)&&!c.call(d,this[b],b,this)){return false;}}return true;},filter:function(d,e){var c=[];for(var b=0,a=this.length>>>0;b<a;b++){if((b in this)&&d.call(e,this[b],b,this)){c.push(this[b]);
}}return c;},indexOf:function(c,d){var b=this.length>>>0;for(var a=(d<0)?Math.max(0,b+d):d||0;a<b;a++){if(this[a]===c){return a;}}return -1;},map:function(c,e){var d=this.length>>>0,b=Array(d);
for(var a=0;a<d;a++){if(a in this){b[a]=c.call(e,this[a],a,this);}}return b;},some:function(c,d){for(var b=0,a=this.length>>>0;b<a;b++){if((b in this)&&c.call(d,this[b],b,this)){return true;
}}return false;},clean:function(){return this.filter(function(a){return a!=null;});},invoke:function(a){var b=Array.slice(arguments,1);return this.map(function(c){return c[a].apply(c,b);
});},associate:function(c){var d={},b=Math.min(this.length,c.length);for(var a=0;a<b;a++){d[c[a]]=this[a];}return d;},link:function(c){var a={};for(var e=0,b=this.length;
e<b;e++){for(var d in c){if(c[d](this[e])){a[d]=this[e];delete c[d];break;}}}return a;},contains:function(a,b){return this.indexOf(a,b)!=-1;},append:function(a){this.push.apply(this,a);
return this;},getLast:function(){return(this.length)?this[this.length-1]:null;},getRandom:function(){return(this.length)?this[Number.random(0,this.length-1)]:null;
},include:function(a){if(!this.contains(a)){this.push(a);}return this;},combine:function(c){for(var b=0,a=c.length;b<a;b++){this.include(c[b]);}return this;
},erase:function(b){for(var a=this.length;a--;){if(this[a]===b){this.splice(a,1);}}return this;},empty:function(){this.length=0;return this;},flatten:function(){var d=[];
for(var b=0,a=this.length;b<a;b++){var c=typeOf(this[b]);if(c=="null"){continue;}d=d.concat((c=="array"||c=="collection"||c=="arguments"||instanceOf(this[b],Array))?Array.flatten(this[b]):this[b]);
}return d;},pick:function(){for(var b=0,a=this.length;b<a;b++){if(this[b]!=null){return this[b];}}return null;},hexToRgb:function(b){if(this.length!=3){return null;
}var a=this.map(function(c){if(c.length==1){c+=c;}return c.toInt(16);});return(b)?a:"rgb("+a+")";},rgbToHex:function(d){if(this.length<3){return null;}if(this.length==4&&this[3]==0&&!d){return"transparent";
}var b=[];for(var a=0;a<3;a++){var c=(this[a]-0).toString(16);b.push((c.length==1)?"0"+c:c);}return(d)?b:"#"+b.join("");}});String.implement({test:function(a,b){return((typeOf(a)=="regexp")?a:new RegExp(""+a,b)).test(this);
},contains:function(a,b){return(b)?(b+this+b).indexOf(b+a+b)>-1:String(this).indexOf(a)>-1;},trim:function(){return String(this).replace(/^\s+|\s+$/g,"");
},clean:function(){return String(this).replace(/\s+/g," ").trim();},camelCase:function(){return String(this).replace(/-\D/g,function(a){return a.charAt(1).toUpperCase();
});},hyphenate:function(){return String(this).replace(/[A-Z]/g,function(a){return("-"+a.charAt(0).toLowerCase());});},capitalize:function(){return String(this).replace(/\b[a-z]/g,function(a){return a.toUpperCase();
});},escapeRegExp:function(){return String(this).replace(/([-.*+?^${}()|[\]\/\\])/g,"\\$1");},toInt:function(a){return parseInt(this,a||10);},toFloat:function(){return parseFloat(this);
},hexToRgb:function(b){var a=String(this).match(/^#?(\w{1,2})(\w{1,2})(\w{1,2})$/);return(a)?a.slice(1).hexToRgb(b):null;},rgbToHex:function(b){var a=String(this).match(/\d{1,3}/g);
return(a)?a.rgbToHex(b):null;},substitute:function(a,b){return String(this).replace(b||(/\\?\{([^{}]+)\}/g),function(d,c){if(d.charAt(0)=="\\"){return d.slice(1);
}return(a[c]!=null)?a[c]:"";});}});Function.extend({attempt:function(){for(var b=0,a=arguments.length;b<a;b++){try{return arguments[b]();}catch(c){}}return null;
}});Function.implement({attempt:function(a,c){try{return this.apply(c,Array.from(a));}catch(b){}return null;},bind:function(e){var a=this,b=arguments.length>1?Array.slice(arguments,1):null,d=function(){};
var c=function(){var g=e,h=arguments.length;if(this instanceof c){d.prototype=a.prototype;g=new d;}var f=(!b&&!h)?a.call(g):a.apply(g,b&&h?b.concat(Array.slice(arguments)):b||arguments);
return g==e?f:g;};return c;},pass:function(b,c){var a=this;if(b!=null){b=Array.from(b);}return function(){return a.apply(c,b||arguments);};},delay:function(b,c,a){return setTimeout(this.pass((a==null?[]:a),c),b);
},periodical:function(c,b,a){return setInterval(this.pass((a==null?[]:a),b),c);}});Number.implement({limit:function(b,a){return Math.min(a,Math.max(b,this));
},round:function(a){a=Math.pow(10,a||0).toFixed(a<0?-a:0);return Math.round(this*a)/a;},times:function(b,c){for(var a=0;a<this;a++){b.call(c,a,this);}},toFloat:function(){return parseFloat(this);
},toInt:function(a){return parseInt(this,a||10);}});Number.alias("each","times");(function(b){var a={};b.each(function(c){if(!Number[c]){a[c]=function(){return Math[c].apply(null,[this].concat(Array.from(arguments)));
};}});Number.implement(a);})(["abs","acos","asin","atan","atan2","ceil","cos","exp","floor","log","max","min","pow","sin","sqrt","tan"]);(function(){var a=this.Class=new Type("Class",function(h){if(instanceOf(h,Function)){h={initialize:h};
}var g=function(){e(this);if(g.$prototyping){return this;}this.$caller=null;var i=(this.initialize)?this.initialize.apply(this,arguments):this;this.$caller=this.caller=null;
return i;}.extend(this).implement(h);g.$constructor=a;g.prototype.$constructor=g;g.prototype.parent=c;return g;});var c=function(){if(!this.$caller){throw new Error('The method "parent" cannot be called.');
}var g=this.$caller.$name,h=this.$caller.$owner.parent,i=(h)?h.prototype[g]:null;if(!i){throw new Error('The method "'+g+'" has no parent.');}return i.apply(this,arguments);
};var e=function(g){for(var h in g){var j=g[h];switch(typeOf(j)){case"object":var i=function(){};i.prototype=j;g[h]=e(new i);break;case"array":g[h]=j.clone();
break;}}return g;};var b=function(g,h,j){if(j.$origin){j=j.$origin;}var i=function(){if(j.$protected&&this.$caller==null){throw new Error('The method "'+h+'" cannot be called.');
}var l=this.caller,m=this.$caller;this.caller=m;this.$caller=i;var k=j.apply(this,arguments);this.$caller=m;this.caller=l;return k;}.extend({$owner:g,$origin:j,$name:h});
return i;};var f=function(h,i,g){if(a.Mutators.hasOwnProperty(h)){i=a.Mutators[h].call(this,i);if(i==null){return this;}}if(typeOf(i)=="function"){if(i.$hidden){return this;
}this.prototype[h]=(g)?i:b(this,h,i);}else{Object.merge(this.prototype,h,i);}return this;};var d=function(g){g.$prototyping=true;var h=new g;delete g.$prototyping;
return h;};a.implement("implement",f.overloadSetter());a.Mutators={Extends:function(g){this.parent=g;this.prototype=d(g);},Implements:function(g){Array.from(g).each(function(j){var h=new j;
for(var i in h){f.call(this,i,h[i],true);}},this);}};})();