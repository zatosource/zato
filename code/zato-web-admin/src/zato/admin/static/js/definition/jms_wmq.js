
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.ConnDefWMQ = new Class({
    toString: function() {
        var s = '<ConnDefWMQ id:{0} name:{1} cache_open_send_queues:{2}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.cache_open_send_queues ? this.cache_open_send_queues : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.ConnDefWMQ;
    $.fn.zato.data_table.new_row_func = $.fn.zato.definition.jms_wmq.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'host', 'port', 'queue_manager', 'channel', 'max_chars_printed']);
})

$.fn.zato.definition.jms_wmq.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new JMS WebSphere MQ definition', null);
}

$.fn.zato.definition.jms_wmq.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the JMS WebSphere MQ definition', id);
}

$.fn.zato.definition.jms_wmq.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var cache_open_send_queues = item.cache_open_send_queues == true;
    var cache_open_receive_queues = item.cache_open_receive_queues == true;
    var use_shared_connections = item.use_shared_connections == true;
    var ssl = item.ssl == true;
    var ssl_cipher_spec = item.ssl_cipher_spec ? item.ssl_cipher_spec : '';
    var ssl_key_repository = item.ssl_key_repository ? item.ssl_key_repository : '';
    var needs_mcd = item.needs_mcd == true;

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', item.host);
    row += String.format('<td>{0}</td>', item.port);
    row += String.format('<td>{0}</td>', item.queue_manager);
    row += String.format('<td>{0}</td>', item.channel);
    row += String.format('<td>{0}</td>', cache_open_send_queues ? 'Yes' : 'No');
    row += String.format('<td>{0}</td>', cache_open_receive_queues ? 'Yes' : 'No');
    row += String.format('<td>{0}</td>', use_shared_connections ? 'Yes' : 'No');
    row += String.format('<td>{0}</td>', ssl ? 'Yes' : 'No');
    row += String.format('<td>{0}</td>', item.ssl_cipher_spec);
    row += String.format('<td>{0}</td>', item.ssl_key_repository);
    row += String.format('<td>{0}</td>', needs_mcd ? 'Yes' : 'No');
    row += String.format('<td>{0}</td>', item.max_chars_printed);
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.definition.jms_wmq.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.definition.jms_wmq.delete_({0});'>Delete</a>", item.id));
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", cache_open_send_queues);
    row += String.format("<td class='ignore'>{0}</td>", cache_open_receive_queues);
    row += String.format("<td class='ignore'>{0}</td>", use_shared_connections);
    row += String.format("<td class='ignore'>{0}</td>", ssl);
    row += String.format("<td class='ignore'>{0}</td>", needs_mcd);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.definition.jms_wmq.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'JMS WebSphere MQ definition [{0}] deleted',
        'Are you sure you want to delete the JMS WebSphere MQ definition [{0}]?',
        true);
}
