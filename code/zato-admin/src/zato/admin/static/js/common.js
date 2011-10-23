//
// Namespaces
//

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

$.fn.zato.user_message = function(is_success, msg) {
	var pre = $('#user-message');
	var new_css_class = ''
	
	if(is_success) {
		css_class = 'user-message-success';
	}
	else {
		css_class = 'user-message-failure';
	}

	pre.removeClass('user-message-success').
		removeClass('user-message-failure').addClass(css_class);
	pre.text(msg);
	
	var div = $('#user-message-div');
	div.fadeOut(100, function() {
		div.fadeIn(250);
	});		
}

//
// Data table
//

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

$.fn.zato.data_table.reset_form = function(form_id) {
	$(form_id).each(function() {
	  this.reset();
	});
}

$.fn.zato.data_table.cleanup = function(form_id) {

	/* Clear out the values and close the dialog.
	*/
	$.fn.zato.data_table.reset_form(form_id);
	var parts = form_id.split('form-');
	var div_id = parts[0] + parts[1];
	$(div_id).dialog('close');
}

$.fn.zato.data_table.dialog_div = function(action, job_type) {
	return $('#'+ action +'-'+ job_type);
}

$.fn.zato.data_table.form_info = function(button) {
	var form = $(button).closest('form');
	var form_id = form.attr('id');
	return {
		'form': form,
		'form_id': '#' + form_id,
	}
}

$.fn.zato.data_table.close = function(button) {
	var form_info = $.fn.zato.data_table.form_info(button);
	$.fn.zato.data_table.cleanup(form_info['form_id']);
}

$.fn.zato.data_table._on_submit_complete = function(data, status) {

	var msg = '';
	var success = status == 'success';
	
	if(success) {
		var response = $.parseJSON(data.responseText);
		msg = response.message; 
	}
	else {
		msg = data.responseText; 
	}
	$.fn.zato.user_message(success, msg);
}

$.fn.zato.data_table._on_submit = function(form, callback) {

	$.ajax({
		type: 'POST',
		url: form.attr('action'),
		data: form.serialize(),
		dataType: 'json',
		complete: callback
	});
}

//
// Misc
//
$.fn.zato.get_random_string = function() {
    var elems = '1234567890qwertyuiopasdfghjklzxcvbnm'.split('');
    var s = "";
    var length = 32;

    for(var i = 0; i < length; i++) {
        s += elems[Math.floor(Math.random() * elems.length)];
    }
    return s;
}

$.fn.zato.to_bool = function(item) {
	var s = new String(item).toLowerCase();
    return(s == "true" || s == 'on'); // 'on' too because it may be a form's field
}

String.prototype.capitalize = function() {
    return this.charAt(0).toUpperCase() + this.slice(1);
}
