
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.SMTP = new Class({
    toString: function() {
        var s = '<SMTP id:{0} name:{1}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = false;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.SMTP;
    $.fn.zato.data_table.new_row_func = $.fn.zato.email.smtp.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'host', 'port', 'timeout', 'mode', 'ping_address']);
})


$.fn.zato.email.smtp.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new SMTP connection', null);
}

$.fn.zato.email.smtp.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the SMTP connection', id);
}

$.fn.zato.email.smtp.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var is_active = item.is_active == true
    var is_debug = item.is_debug == true
    var username = item.username ? item.username : "<span class='form_hint'>(None)</span>";

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', is_active ? "Yes" : "No");
    row += String.format('<td>{0}</td>', item.host);
    row += String.format('<td>{0}</td>', item.port);
    row += String.format('<td>{0}</td>', username);
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.data_table.change_password('{0}')\">Change password</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.email.smtp.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.email.smtp.delete_({0});'>Delete</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.data_table.ping({0});'>Ping</a>", item.id));
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", is_active);
    row += String.format("<td class='ignore'>{0}</td>", item.timeout);
    row += String.format("<td class='ignore'>{0}</td>", item.ping_address);
    row += String.format("<td class='ignore'>{0}</td>", is_debug);
    row += String.format("<td class='ignore'>{0}</td>", item.mode);
    row += String.format("<td class='ignore'>{0}</td>", item.username ? item.username : "");

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.email.smtp.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'SMTP connection [{0}] deleted',
        'Are you sure you want to delete the SMTP connection [{0}]?',
        true);
}
