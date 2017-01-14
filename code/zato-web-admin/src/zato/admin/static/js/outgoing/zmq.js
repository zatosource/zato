
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.OutgoingZMQ = new Class({
    toString: function() {
        var s = '<OutgoingZMQ id:{0} name:{1} is_active:{2}';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.is_active ? this.is_active : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.OutgoingZMQ;
    $.fn.zato.data_table.new_row_func = $.fn.zato.outgoing.zmq.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'address', 'socket_type', 'socket_method']);
})

$.fn.zato.outgoing.zmq.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new outgoing ZeroMQ connection', null);
}

$.fn.zato.outgoing.zmq.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the outgoing ZeroMQ connection', id);
}

$.fn.zato.outgoing.zmq.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var is_active = item.is_active == true;

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', is_active ? 'Yes' : 'No');
    row += String.format('<td>{0}</td>', item.address);
    row += String.format('<td>{0}</td>', item.socket_type);
    row += String.format('<td>{0}</td>', item.socket_method);
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.outgoing.zmq.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.outgoing.zmq.delete_({0});'>Delete</a>", item.id));
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", is_active);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.outgoing.zmq.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Outgoing ZeroMQ connection [{0}] deleted',
        'Are you sure you want to delete the outgoing ZeroMQ connection [{0}]?',
        true);
}
