
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
    $.fn.zato.data_table.setup_forms(['name', 'host', 'port', 'channel', 'max_chars_printed']);
})

$.fn.zato.definition.jms_wmq.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new IBM MQ definition', null);
}

$.fn.zato.definition.jms_wmq.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update IBM MQ definition', id);
}

$.fn.zato.definition.jms_wmq.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var ssl = item.ssl == true;
    var ssl_cipher_spec = item.ssl_cipher_spec ? item.ssl_cipher_spec : '';
    var ssl_key_repository = item.ssl_key_repository ? item.ssl_key_repository : '';
    var needs_mcd = item.needs_mcd == true;
    var use_jms = item.use_jms == true;
    var username = item.username ? item.username : '';
    var queue_manager = item.queue_manager ? item.queue_manager : '';

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', item.host);
    row += String.format('<td>{0}</td>', item.port);

    row += String.format('<td>{0}</td>', item.queue_manager ? item.queue_manager : $.fn.zato.empty_value);
    row += String.format('<td>{0}</td>', item.channel);
    row += String.format('<td>{0}</td>', item.username ? item.username : $.fn.zato.empty_value);
    row += String.format('<td>{0}</td>', ssl ? 'Yes' : 'No');
    row += String.format('<td>{0}</td>', item.ssl_cipher_spec ? item.ssl_cipher_spec : $.fn.zato.empty_value);

    row += String.format('<td>{0}</td>', item.ssl_key_repository ? item.ssl_key_repository : $.fn.zato.empty_value);
    row += String.format('<td>{0}</td>', item.max_chars_printed);
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.data_table.change_password({0})'>Change password</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.definition.jms_wmq.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.definition.jms_wmq.delete_({0});'>Delete</a>", item.id));

    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.data_table.ping({0});'>Ping</a>", item.id));
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", item.cache_open_send_queues);
    row += String.format("<td class='ignore'>{0}</td>", item.cache_open_receive_queues);
    row += String.format("<td class='ignore'>{0}</td>", item.use_shared_connections);

    row += String.format("<td class='ignore'>{0}</td>", ssl);
    row += String.format("<td class='ignore'>{0}</td>", username);
    row += String.format("<td class='ignore'>{0}</td>", queue_manager);
    row += String.format("<td class='ignore'>{0}</td>", ssl_cipher_spec);
    row += String.format("<td class='ignore'>{0}</td>", ssl_key_repository);
    row += String.format("<td class='ignore'>{0}</td>", use_jms);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.definition.jms_wmq.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'IBM MQ definition `{0}` deleted',
        'Are you sure you want to delete IBM MQ definition `{0}`?',
        true);
}
