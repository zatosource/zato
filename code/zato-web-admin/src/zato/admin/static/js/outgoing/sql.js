
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.SQL = new Class({
    toString: function() {
        var s = '<SQL id:{0} name:{1} is_active:{2}';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.is_active ? this.is_active : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = true;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.SQL;
    $.fn.zato.data_table.new_row_func = $.fn.zato.outgoing.sql.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'username', 'db_name', 'engine', 'host', 'port', 'pool_size']);
})

$.fn.zato.outgoing.sql.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new outgoing SQL connection', null);
}

$.fn.zato.outgoing.sql.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the outgoing SQL connection', id);
}

$.fn.zato.outgoing.sql.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var is_active = item.is_active == true;

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', is_active ? 'Yes' : 'No');
    row += String.format('<td>{0}</td>', data.engine_display_name);
    row += String.format('<td>{0}</td>', item.host);
    row += String.format('<td>{0}</td>', item.port);
    row += String.format('<td>{0}</td>', item.db_name);
    row += String.format('<td>{0}</td>', item.username);
    row += String.format('<td>{0}</td>', item.pool_size);
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.data_table.change_password({0})'>Change password</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.outgoing.sql.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.outgoing.sql.delete_({0});'>Delete</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.data_table.ping('{0}')\">Ping</a>", item.id));
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", is_active);
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.engine);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.outgoing.sql.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Outgoing SQL connection [{0}] deleted',
        'Are you sure you want to delete the outgoing SQL connection [{0}]?',
        true);
}
