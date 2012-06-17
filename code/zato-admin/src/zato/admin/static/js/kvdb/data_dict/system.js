
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.System = new Class({
	toString: function() {
		var s = '<System id:{0} name:{1}>';
		return String.format(s, this.id ? this.id : '(none)', 
								this.name ? this.name : '(none)');
	}
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() { 
	$('#data-table').tablesorter(); 
	$.fn.zato.data_table.class_ = $.fn.zato.data_table.System;
	$.fn.zato.data_table.new_row_func = $.fn.zato.kvdb.data_dict.system.data_table.new_row;
	$.fn.zato.data_table.parse();
	$.fn.zato.data_table.setup_forms(['name']);
})

$.fn.zato.kvdb.data_dict.system.create = function() {
	$.fn.zato.data_table._create_edit('create', 'Create a new system', null);
}

$.fn.zato.kvdb.data_dict.system.edit = function(id) {
	$.fn.zato.data_table._create_edit('edit', 'Update the system', id);
}

$.fn.zato.kvdb.data_dict.system.data_table.new_row = function(item, data, include_tr) {
    var row = '';
	
	if(include_tr) {
		row += String.format("<tr id='tr_{0}' class='updated'>", item.name);
	}
	
	row += "<td class='numbering'>&nbsp;</td>";
	row += "<td><input type='checkbox' /></td>";
	row += String.format('<td>{0}</td>', item.name);
	row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.kvdb.data_dict.system.edit('{0}')\">Edit</a>", item.name));
	row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.kvdb.data_dict.system.delete_('{0}')\">Delete</a>", item.name));
	row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.name);
	
	if(include_tr) {
		row += '</tr>';
	}
	
	return row;
}

$.fn.zato.kvdb.data_dict.system.delete_ = function(id) {
	$.fn.zato.data_table.delete_(id, 'td.item_id_', 
		'System [{0}] deleted', 
		'Are you sure you want to delete the system [{0}]?',
		true);
}
