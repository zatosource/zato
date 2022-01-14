/*
 * Fabtabulous! Simple tabs using Prototype
 * http://tetlaw.id.au/view/blog/fabtabulous-simple-tabs-using-prototype/
 * Andrew Tetlaw
 * version 1.1 2006-05-06
 * http://creativecommons.org/licenses/by-sa/2.5/
 */
var Fabtabs = Class.create();

Fabtabs.prototype = {
	initialize : function(element) {
		this.element = $(element);
		var options = Object.extend({}, arguments[1] || {});
		this.menu = $A(this.element.getElementsByTagName('a'));
		this.show(this.getInitialTab());
		this.menu.each(this.setupTab.bind(this));
	},
	setupTab : function(elm) {
		Event.observe(elm,'click',this.activate.bindAsEventListener(this),false)
	},
	activate :  function(ev) {
		var elm = Event.findElement(ev, "a");
		//Event.stop(ev);
		this.show(elm);
		this.menu.without(elm).each(this.hide.bind(this));
	},
	hide : function(elm) {
		$(elm).removeClassName('active-tab');
		$(this.tabID(elm)).removeClassName('active-tab-body');
	},
	show : function(elm) {
		$(elm).addClassName('active-tab');
		$(this.tabID(elm)).addClassName('active-tab-body');

	},
	tabID : function(elm) {
		return elm.href.match(/#(\w.+)/)[1];
	},
	getInitialTab : function() {
		if(document.location.href.match(/#(\w.+)/)) {
			var loc = RegExp.$1;
			var elm = this.menu.find(function(value) { return value.href.match(/#(\w.+)/)[1] == loc; });
			return elm || this.menu.first();
		} else {
			return this.menu.first();
		}
	}
}

Event.observe(window,'load',function(){ new Fabtabs('tabs'); },false);
