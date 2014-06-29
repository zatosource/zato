
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.CassandraConn = new Class({
    toString: function() {
        var s = '<CassandraConn id:{0} name:{1} value:{2}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.value ? this.value : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = false;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.CassandraConn;
    $.fn.zato.data_table.new_row_func = $.fn.zato.definition.cassandra.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'contact_points', 'port', 'exec_size', 'proto_version', 'default_keyspace']);
})


$.fn.zato.definition.cassandra.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new Cassandra connection', null);
}

$.fn.zato.definition.cassandra.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the Cassandra connection', id);
}

$.fn.zato.definition.cassandra.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var is_active = item.is_active == true

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', is_active ? "Yes" : "No");
    row += String.format('<td>{0}</td>', item.contact_points);
    row += String.format('<td>{0}</td>', item.port);
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.data_table.change_password('{0}')\">Change password</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.definition.cassandra.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.definition.cassandra.delete_({0});'>Delete</a>", item.id));
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", is_active);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.definition.cassandra.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Cassandra connection [{0}] deleted',
        'Are you sure you want to delete the Cassandra connection [{0}]?',
        true);
}
