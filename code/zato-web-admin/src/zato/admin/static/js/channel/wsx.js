
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.ChannelWebSocket = new Class({
    toString: function() {
        var s = '<ChannelWebSocket id:{0} name:{1} is_active:{2}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.is_active ? this.is_active : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.ChannelWebSocket;
    $.fn.zato.data_table.new_row_func = $.fn.zato.channel.wsx.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms([
        'name',
        'address',
        'service_name',
        'security_id',
        'new_token_wait_time',
        'token_ttl',
        'ping_interval',
        'pings_missed_threshold',
    ]);
})

$.fn.zato.channel.wsx.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new WebSocket channel', null);
}

$.fn.zato.channel.wsx.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the WebSocket channel', id);
}

$.fn.zato.channel.wsx.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var is_active = item.is_active == true;
    var cluster_id = $(document).getUrlParam('cluster');

    // 1
    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";

    // 2
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', is_active ? 'Yes' : 'No');
    row += String.format('<td>{0}</td>', item.address);

    // 3
    row += String.format('<td>{0}</td>', $.fn.zato.data_table.service_text(item.service_name, cluster_id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"/zato/channel/wsx/connection-list/{0}/?cluster={1}&amp;channel_name={2}\">Connections</a>",
        item.id, cluster_id, item.name));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.channel.wsx.edit('{0}')\">Edit</a>", item.id));

    // 4
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.channel.wsx.delete_({0});'>Delete</a>", item.id));
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", item.data_format ? item.data_format : '');

    // 5
    row += String.format("<td class='ignore'>{0}</td>", is_active);
    row += String.format("<td class='ignore'>{0}</td>", item.security_id ? item.security_id : '');
    row += String.format("<td class='ignore'>{0}</td>", item.new_token_wait_time);

    // 6
    row += String.format("<td class='ignore'>{0}</td>", item.token_ttl);

    row += String.format("<td class='ignore'>{0}</td>", item.is_audit_log_sent_active);
    row += String.format("<td class='ignore'>{0}</td>", item.is_audit_log_received_active);
    row += String.format("<td class='ignore'>{0}</td>", item.max_len_messages_sent);

    row += String.format("<td class='ignore'>{0}</td>", item.max_len_messages_received);
    row += String.format("<td class='ignore'>{0}</td>", item.max_bytes_per_message_sent);
    row += String.format("<td class='ignore'>{0}</td>", item.max_bytes_per_message_received);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.channel.wsx.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'WebSocket channel [{0}] deleted',
        'Are you sure you want to delete the WebSocket channel [{0}]?',
        true);
}
