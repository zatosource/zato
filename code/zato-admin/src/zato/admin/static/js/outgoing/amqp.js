
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.OutgoingAMQP = new Class({
	toString: function() {
		var s = '<OutgoingAMQP id:{0} name:{1} is_active:{2} def_id:{3}>';
		return String.format(s, this.id ? this.id : '(none)', 
								this.name ? this.name : '(none)',
								this.is_active ? this.is_active : '(none)',
								this.def_id ? this.def_id : '(none)');
	}
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() { 
	$('#data-table').tablesorter(); 
	$.fn.zato.data_table.class_ = $.fn.zato.data_table.OutgoingAMQP;
	$.fn.zato.data_table.new_row_func = $.fn.zato.outgoing.amqp.data_table.new_row;
	$.fn.zato.data_table.parse();
	$.fn.zato.data_table.setup_forms(['name', 'delivery_mode', 'priority', 'def_id']);
})

$.fn.zato.outgoing.amqp.create = function() {
	$.fn.zato.data_table._create_edit('create', 'Create a new outgoing AMQP connection', null);
}

$.fn.zato.outgoing.amqp.edit = function(id) {
	$.fn.zato.data_table._create_edit('edit', 'Update the outgoing AMQP connection', id);
}

$.fn.zato.outgoing.amqp.data_table.new_row = function(item, data, include_tr) {
    var row = '';
	
	if(include_tr) {
		row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
	}
	
	var is_active = item.is_active == true
	
	row += "<td class='numbering'>&nbsp;</td>";
	row += "<td><input type='checkbox' /></td>";
	row += String.format('<td>{0}</td>', item.name);
	row += String.format('<td>{0}</td>', is_active ? 'Yes' : 'No');
	row += String.format('<td>{0}</td>', data.delivery_mode_text);
	row += String.format('<td>{0}</td>', '');
	row += String.format('<td>{0}</td>', '');
	row += String.format('<td>{0}</td>', '');
	row += String.format('<td>{0}</td>', '');
	row += String.format('<td>{0}</td>', '');
	row += String.format('<td>{0}</td>', '');
	row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.outgoing.amqp.edit('{0}')\">Edit</a>", item.id));
	row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.outgoing.amqp.delete_({0});'>Delete</a>", item.id));
	row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
	row += String.format("<td class='ignore'>{0}</td>", item.delivery_mode);
	
	if(include_tr) {
		row += '</tr>';
	}
	
	return row;
}

$.fn.zato.outgoing.amqp.delete_ = function(id) {
	$.fn.zato.data_table.delete_(id, 'td.item_id_', 
		'Outgoing AMQP connection [{0}] deleted', 
		'Are you sure you want to delete the outgoing AMQP connection [{0}]?',
		true);
}
