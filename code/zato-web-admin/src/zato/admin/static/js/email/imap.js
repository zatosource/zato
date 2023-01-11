
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.IMAP = new Class({
    toString: function() {
        var s = '<IMAP id:{0} name:{1}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = false;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.IMAP;
    $.fn.zato.data_table.new_row_func = $.fn.zato.email.imap.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'server_type']);
})


$.fn.zato.email.imap.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new IMAP connection', null);
}

$.fn.zato.email.imap.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the IMAP connection', id);
}

$.fn.zato.email.imap.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var is_active = item.is_active == true
    var username = item.username ? item.username : "<span class='form_hint'>(None)</span>";

    if(item.server_type == "microsoft-365") {
        var _host = item.tenant_id || $.fn.zato.empty_value;
        var _port = $.fn.zato.empty_value;
        var _server_type_human = "Microsoft 365";
        var _change_secret_link = String.format(
            "<a href=\"javascript:$.fn.zato.data_table.change_password('{0}', 'Change secret', 'Secret', 'secret')\">Change secret</a>",
            item.id
        );
    }
    else {
        var _host = item.host || $.fn.zato.empty_value;
        var _port = item.port || $.fn.zato.empty_value;
        var _server_type_human = "Generic IMAP";
        var _change_secret_link = String.format(
            "<a href=\"javascript:$.fn.zato.data_table.change_password('{0}')\">Change password</a>",
            item.id
        );
    }

    // 1
    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";
    row += String.format('<td>{0}</td>', item.name);

    // 2
    row += String.format('<td>{0}</td>', is_active ? "Yes" : "No");
    row += String.format('<td>{0}</td>', _server_type_human);
    row += String.format("<td>{0}</td>", _host);

    // 3
    row += String.format('<td>{0}</td>', _port);
    row += String.format('<td>{0}</td>', username);
    row += String.format('<td>{0}</td>', _change_secret_link);

    // 4
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.email.imap.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.email.imap.delete_({0});'>Delete</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.data_table.ping({0});'>Ping</a>", item.id));

    // 5
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", is_active);
    row += String.format("<td class='ignore'>{0}</td>", item.timeout);

    // 6
    row += String.format("<td class='ignore'>{0}</td>", item.debug_level);
    row += String.format("<td class='ignore'>{0}</td>", item.mode);
    row += String.format("<td class='ignore'>{0}</td>", item.get_criteria ? item.get_criteria : "");

    // 7
    row += String.format("<td class='ignore'>{0}</td>", item.username ? item.username : "");
    row += String.format("<td class='ignore'>{0}</td>", item.server_type);
    row += String.format("<td class='ignore'>{0}</td>", item.tenant_id ? item.tenant_id : "");

    // 8
    row += String.format("<td class='ignore'>{0}</td>", item.client_id ? item.client_id : "");
    row += String.format("<td class='ignore'>{0}</td>", item.host ? item.host : "");
    row += String.format("<td class='ignore'>{0}</td>", item.port ? item.port : "993");

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.email.imap.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Deleted IMAP connection `{0}`',
        'Are you sure you want to delete the IMAP connection `{0}`?',
        true);
}
