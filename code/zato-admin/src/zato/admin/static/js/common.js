(function($){
if ({}.__proto__){
    // mozilla  & webkit expose the prototype chain directly
    $.namespace = function(n){
        var names=n.split('.');
        var f=$.fn;
        for(var i=0;i<names.length;i++) {
            var name=names[i];
            if(!f[name]) {
                f[name] = function namespace() { // insert this function in the prototype chain
                    this.__proto__ = arguments.callee;
                    return this;
                };
                f[name].__proto__ = f;
            }
            f=f[name];
        }
    };
    $.fn.$ = function(){
        this.__proto__ = $.fn;
        return this;
    };
}else{
    // every other browser; need to copy methods
    $.namespace = function(n){
        var names=n.split('.');
        var f=$.fn;
        for(var i=0;i<names.length;i++) {
            var name=names[i];
            if(!f[name]) {
                f[name] = function namespace() { return this.extend(arguments.callee); };
            }
            f=f[name];
        }
    };
    $.fn.$ = function() { // slow but restores the default namespace
        var len = this.length;
        this.extend($.fn);
        this.length = len; // $.fn has length = 0, which messes everything up
        return this;
    };
}
})(jQuery);

$.namespace('zato');
$.namespace('zato.data_table');
$.namespace('zato.scheduler');

//
// A simple function for returning a random string.
//
function get_random_string() {
    var elems = '1234567890qwertyuiopasdfghjklzxcvbnm'.split('');
    var s = "";
    var length = 32;

    for(var i = 0; i < length; i++) {
        s += elems[Math.floor(Math.random() * elems.length)];
    }
    return s;
}

//
// A utility function for providing a feedback to the user.
//
function update_user_message(is_success, response, user_message_elem,
                                user_message_container_elem) {

    if(!user_message_elem)
        user_message_elem = "user-message";

    if(!user_message_container_elem)
        user_message_container_elem = "user-message-div";

    var css_class_name = "user-message ";

    if(is_success) {
        css_class_name += "user-message-success"
    }
    else {
        css_class_name += "user-message-failure"
    };

    $(user_message_elem).className = css_class_name;
    $(user_message_elem).innerHTML = new String(response).escapeHTML();
    Effect.Fade(user_message_container_elem, {duration: 0.4, from:1.0, to:0.1, queue:"start"}),
    Effect.Appear(user_message_container_elem, {duration: 0.4, queue:"end"});
}

function to_bool(item) {
    return new String(item).toLowerCase() == "true";
}

String.prototype.capitalize = function() {
    return this.charAt(0).toUpperCase() + this.slice(1);
}

$.fn.zato.data_table.data = {}

$.fn.zato.data_table.parse = function(class_) {

	var rows = $('#data-table tr').not('[class="ignore"]');
	var columns = $.fn.zato.data_table.get_columns();
	
	$.each(rows, function(row_idx, row) {
		var instance = new class_()
		var tds = $(row).find('td');
		$.each(tds, function(td_idx, td) {
		
			var attr_name = columns[td_idx];
			var attr_value = $(td).text().trim();

			// Don't bother with ignored attributes.
			if(attr_name[0] != '_') {
				instance[attr_name] = attr_value;
			}
		});
		$.fn.zato.data_table.data[instance.id] = instance;
	});
}