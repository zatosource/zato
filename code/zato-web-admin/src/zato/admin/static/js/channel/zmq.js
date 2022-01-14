
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.ChannelZMQ = new Class({
    toString: function() {
        var s = '<ChannelZMQ id:{0} name:{1} is_active:{2}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.is_active ? this.is_active : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.ChannelZMQ;
    $.fn.zato.data_table.new_row_func = $.fn.zato.channel.zmq.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'address', 'socket_type', 'socket_method', 'service']);
})

$.fn.zato.channel.zmq.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new ZeroMQ channel', null);
}

$.fn.zato.channel.zmq.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the ZeroMQ channel', id);
}

$.fn.zato.channel.zmq.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var is_active = item.is_active == true;
    var cluster_id = $(document).getUrlParam('cluster');

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', is_active ? 'Yes' : 'No');
    row += String.format('<td>{0}</td>', item.address);
    row += String.format('<td>{0}</td>', item.socket_type);
    row += String.format('<td>{0}</td>', item.socket_method);
    row += String.format('<td>{0}</td>', item.sub_key);
    row += String.format('<td>{0}</td>', $.fn.zato.data_table.service_text(item.service, cluster_id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.channel.zmq.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.channel.zmq.delete_({0});'>Delete</a>", item.id));
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", is_active);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.channel.zmq.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'ZeroMQ channel [{0}] deleted',
        'Are you sure you want to delete the ZeroMQ channel [{0}]?',
        true);
}
