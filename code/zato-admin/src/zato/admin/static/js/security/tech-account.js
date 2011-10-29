
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.TechAccount = new Class({
	toString: function() {
		var s = '<TechAccount id:{0} name:{1} is_active:{2}>';
		return String.format(s, this.id ? this.id : '(none)', 
								this.name ? this.name : '(none)', 
								this.is_active ? this.is_active : '(none)');
	}
});

$(document).ready(function() { 
	$('#data-table').tablesorter(); 
	$.fn.zato.data_table.parse($.fn.zato.data_table.TechAccount);
	
	var actions = ['create', 'edit'];

	/* Dynamically prepare pop-up windows.
	*/
	$.each(actions, function(ignored, action) {
		var form_id = String.format('#{0}-form', action);
		var div_id = String.format('#{0}-div', action);

		// Pop-up				
		$(div_id).dialog({
			autoOpen: false,
			width: '40em',
			height: '10em',
			close: function(e, ui) {
				$.fn.zato.data_table.reset_form(form_id);
			}
		});
	});
	
	// Change password pop-up
	$.fn.zato.data_table.setup_change_password();
	
	/* Prepare the validators here so that it's all still a valid HTML
	   even with bValidator's custom attributes.
	*/

	var attrs = ['name'];		
	var field_id = '';
	var form_id = '';
	
	$.each(['', 'edit'], function(ignored, action) {
		$.each(attrs, function(ignored, attr) {
			if(action) {
				field_id = String.format('#id_{0}', attr);
			}
			else {
				field_id = String.format('#id_{0}-{1}', action, attr);
			}
			
			$(field_id).attr('data-bvalidator', 'required');
			$(field_id).attr('data-bvalidator-msg', 'This is a required field');
		});
		
		// Doh, not exactly the cleanest approach.
		if(action) {
			form_id = '#edit-form';
		}
		else {
			form_id = '#create-form';
		}
		$(form_id).bValidator();
	});

	/* Assign form submition handlers.
	*/
	
	$.each(actions, function(ignored, action) {
		$('#'+ action +'-form').submit(function() {
			$.fn.zato.scheduler.data_table.on_submit(action);
			return false;
		});
	});
})


$.fn.zato.security.tech_account._create_edit = function(action, id) {

	var title = 'Create a new technical account';
		
	if(action == 'edit') {

		var form = $(String.format('#{0}-form', action));
		var name_prefix = action + '-';
		var id_prefix = String.format('#id_{0}', name_prefix);
		var instance = $.fn.zato.data_table.data[id];
		
		$.fn.zato.form.populate(form, instance, name_prefix, id_prefix);
	}

	var div = $(String.format('#{0}-div', action));
	div.prev().text(title); // prev() is a .ui-dialog-titlebar
	div.dialog('open');
}

$.fn.zato.security.tech_account.create = function() {
	$.fn.zato.security.tech_account._create_edit('create');
}

$.fn.zato.security.tech_account.edit = function(id) {
	$.fn.zato.security.tech_account._create_edit('edit', id);
}

$.fn.zato.security.tech_account.data_table.on_submit_complete = function(data, status, 
	action) {

	if(status == 'success') {
		var json = $.parseJSON(data.responseText);
		var include_tr = true ? action == 'create' : false;
		var row = $.fn.zato.security.tech_account.data_table.add_row(json, action, include_tr);
		if(action == 'create') {
			$('#data-table > tbody:last').prepend(row);
		}
		else {
			var tr = $('#tr_'+ json.id).html(row);
			tr.addClass('updated');
		}	
	}

	$.fn.zato.data_table._on_submit_complete(data, status);
	$.fn.zato.data_table.cleanup('#'+ action +'-form');
}

$.fn.zato.security.tech_account.data_table.on_submit = function(action) {
	var form = $('#' + action +'-form');
	var callback = function(data, status) {
			return $.fn.zato.scheduler.data_table.on_submit_complete(data, 
				status, action);
		}
	return $.fn.zato.data_table._on_submit(form, callback);
}

$.fn.zato.security.tech_account.data_table.new_row = function(item, data, include_tr) {
    var row = '';
	
	if(include_tr) {
		row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
	}
	
	row += "<td class='numbering'>&nbsp;</td>";
	row += "<td><input type='checkbox' /></td>";
	row += String.format('<td>{0}</td>', item.name);
	row += String.format('<td>{0}</td>', item.is_active ? 'Yes' : 'No');
	row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.data_table.change_password({0})'>Change password</a>", item.id));
	row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.security.tech_account.edit('{0}')\">Edit</a>", item.id));
	row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.security.tech_account.delete_({0});'>Delete</a>", item.id));
	row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
	row += String.format("<td class='ignore'>{0}</td>", item.is_active);
	
	if(include_tr) {
		row += '</tr>';
	}
	
	return row;
}

$.fn.zato.security.tech_account.data_table.add_row = function(data, action, include_tr) {

	var item = new $.fn.zato.data_table.TechAccount();
	var form = $(String.format('#{0}-form', action));
	var prefix = action + '-';
	var name = '';
	var _columns = $.fn.zato.data_table.get_columns();
	
	$.each(form.serializeArray(), function(idx, elem) {
		name = elem.name.replace(prefix, '');
		item[name] = elem.value;
	})
	if(!item.id) {
		item.id = data.id;
	}
	
	item.is_active = $.fn.zato.to_bool(item.is_active);
	
	$.fn.zato.data_table.data[item.id] = item;
	return $.fn.zato.security.tech_account.data_table.new_row(item, data, include_tr);
}

$.fn.zato.security.tech_account.delete_ = function(id) {
	$.fn.zato.data_table.delete_(id, 'td.item_id_', 
		'Technical account [{0}] deleted', 
		'Are you sure you want to delete the technical account [{0}]?');
}
