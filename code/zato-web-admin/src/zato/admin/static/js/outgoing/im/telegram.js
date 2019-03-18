
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.Telegram = new Class({
    toString: function() {
        var s = '<Telegram id:{0} name:{1} is_active:{2}';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.is_active ? this.is_active : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = true;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.Telegram;
    $.fn.zato.data_table.new_row_func = $.fn.zato.outgoing.im.telegram.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'address', 'connect_timeout', 'invoke_timeout']);
})

$.fn.zato.outgoing.im.telegram.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new outgoing Telegram connection', null);
}

$.fn.zato.outgoing.im.telegram.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the outgoing Telegram connection', id);
}

$.fn.zato.outgoing.im.telegram.data_table.new_row = function(item, data, include_tr) {
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
    row += String.format('<td>{0}</td>', item.http_proxy_list ? item.http_proxy_list : $.fn.zato.empty_value);
    row += String.format('<td>{0}</td>', item.https_proxy_list ? item.https_proxy_list : $.fn.zato.empty_value);

    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.data_table.change_password(\"{0}\", \"{1}\")'>Change token</a>", item.id, 'Change token'));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.outgoing.im.telegram.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.outgoing.im.telegram.delete_({0});'>Delete</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.data_table.ping({0});'>Ping</a>", item.id));

    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", is_active);

    // 1 -->
    row += String.format("<td class='ignore'>{0}</td>", item.connect_timeout);
    row += String.format("<td class='ignore'>{0}</td>", item.invoke_timeout);
    row += String.format("<td class='ignore'>{0}</td>", item.http_proxy_list);
    row += String.format("<td class='ignore'>{0}</td>", item.https_proxy_list);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.outgoing.im.telegram.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Outgoing Telegram connection `{0}` deleted',
        'Are you sure you want to delete outgoing Telegram connection `{0}`?',
        true);
}
