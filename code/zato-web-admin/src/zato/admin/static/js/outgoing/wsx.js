
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.WSX = new Class({
    toString: function() {
        var s = '<WSX id:{0} name:{1} is_active:{2}';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.is_active ? this.is_active : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = true;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.WSX;
    $.fn.zato.data_table.new_row_func = $.fn.zato.outgoing.wsx.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'address', 'security_def']);
})

$.fn.zato.outgoing.wsx.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new outgoing WebSocket connection', null);
}

$.fn.zato.outgoing.wsx.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the outgoing WebSocket connection', id);
}

$.fn.zato.outgoing.wsx.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var is_active = item.is_active == true;
    var is_zato = item.is_zato == true;
    var has_auto_reconnect = item.has_auto_reconnect == true;
    var data_format = item.data_format || '';

    /* 1 */
    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";
    row += String.format('<td>{0}</td>', item.name);

    /* 2 */
    row += String.format('<td>{0}</td>', is_active ? 'Yes' : 'No');
    row += String.format('<td>{0}</td>', item.address_masked);
    row += String.format('<td>{0}</td>', is_zato ? 'Yes' : 'No');

    /* 3 a */
    if(data.on_connect_service_name) {
        row += String.format('<td>{0}</td>',
            String.format("<a href='/zato/service/overview/{0}/?cluster={1}'>{0}</a>",
            data.on_connect_service_name, item.cluster_id));
    }
    else {
        row += $.fn.zato.empty_table_cell;
    }

    /* 3 b */
    if(data.on_message_service_name) {
        row += String.format('<td>{0}</td>',
            String.format("<a href='/zato/service/overview/{0}/?cluster={1}'>{0}</a>",
            data.on_message_service_name, item.cluster_id));
    }
    else {
        row += $.fn.zato.empty_table_cell;
    }

    /* 3 c */
    if(data.on_close_service_name) {
        row += String.format('<td>{0}</td>',
            String.format("<a href='/zato/service/overview/{0}/?cluster={1}'>{0}</a>",
            data.on_close_service_name, item.cluster_id));
    }
    else {
        row += $.fn.zato.empty_table_cell;
    }

    /* 4 */
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.outgoing.wsx.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.outgoing.wsx.delete_({0});'>Delete</a>", item.id));
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);

    /* 5 */
    row += String.format("<td class='ignore'>{0}</td>", is_active);
    row += String.format("<td class='ignore'>{0}</td>", is_zato);
    row += String.format("<td class='ignore'>{0}</td>", item.on_connect_service_name);

    /* 6 */
    row += String.format("<td class='ignore'>{0}</td>", item.on_message_service_name)
    row += String.format("<td class='ignore'>{0}</td>", item.on_close_service_name);
    row += String.format("<td class='ignore'>{0}</td>", item.security_def);

    /* 7 */
    row += String.format("<td class='ignore'>{0}</td>", item.subscription_list);
    row += String.format("<td class='ignore'>{0}</td>", has_auto_reconnect);
    row += String.format("<td class='ignore'>{0}</td>", data_format);

    /* 8 */
    row += String.format("<td class='ignore'>{0}</td>", item.ping_interval);
    row += String.format("<td class='ignore'>{0}</td>", item.pings_missed_threshold);
    row += String.format("<td class='ignore'>{0}</td>", item.socket_read_timeout);

    /* 9 */
    row += String.format("<td class='ignore'>{0}</td>", item.socket_write_timeout);
    row += String.format("<td class='ignore'>{0}</td>", item.address);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.outgoing.wsx.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Outgoing WebSocket connection `{0}` deleted',
        'Are you sure you want to delete outgoing WebSocket connection `{0}`?',
        true);
}
