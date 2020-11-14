
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.Dropbox = new Class({
    toString: function() {
        var s = '<Dropbox id:{0} name:{1} is_active:{2}';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.is_active ? this.is_active : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = false;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.Dropbox;
    $.fn.zato.data_table.new_row_func = $.fn.zato.cloud.dropbox.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'timeout', 'user_agent']);
})

$.fn.zato.cloud.dropbox.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new Dropbox connection', null);
}

$.fn.zato.cloud.dropbox.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the Dropbox connection', id);
}

$.fn.zato.cloud.dropbox.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var is_active = item.is_active == true;

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";

    // 1
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', is_active ? 'Yes' : 'No');
    row += String.format('<td>{0}</td>', item.user_agent);

    // 2
    row += String.format('<td>{0}</td>', item.default_scope || $.fn.zato.empty_value);
    row += String.format('<td>{0}</td>', item.default_directory || $.fn.zato.empty_value);

    // 3
    row += String.format('<td>{0}</td>',
        String.format("<a href=\"javascript:$.fn.zato.data_table.change_password('{0}', 'Change token')\">Change token</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.cloud.dropbox.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.cloud.dropbox.delete_({0});'>Delete</a>", item.id));

    // 4
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.data_table.ping({0});'>Ping</a>", item.id));
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", item.max_retries_on_error || '');

    // 5
    row += String.format("<td class='ignore'>{0}</td>", item.max_retries_on_rate_limit || '');
    row += String.format("<td class='ignore'>{0}</td>", item.timeout || '');
    row += String.format("<td class='ignore'>{0}</td>", item.oauth2_access_token_expiration || '');

    // 6
    row += String.format("<td class='ignore'>{0}</td>", item.default_scope || '');
    row += String.format("<td class='ignore'>{0}</td>", item.pool_size);

    // 7
    row += String.format("<td class='ignore'>{0}</td>", item.default_directory || '');
    row += String.format("<td class='ignore'>{0}</td>", item.http_headers || '');
    row += String.format("<td class='ignore'>{0}</td>", item.is_active);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.cloud.dropbox.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Outgoing Dropbox connection `{0}` deleted',
        'Are you sure you want to delete Dropbox connection `{0}`?',
        true);
}
