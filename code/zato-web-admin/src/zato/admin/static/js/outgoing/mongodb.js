
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.MongoDB = new Class({
    toString: function() {
        var s = '<MongoDB id:{0} name:{1} is_active:{2}';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.is_active ? this.is_active : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = false;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.MongoDB;
    $.fn.zato.data_table.new_row_func = $.fn.zato.outgoing.mongodb.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'server_list', 'pool_size_max', 'connect_timeout', 'server_select_timeout']);
    var uniqueConstraints = [
        {field: 'name', entity_type: 'generic_connection', attr_name: 'name'}
    ];
    $.each(uniqueConstraints, function(constraintIdx, constraint) {
        $.fn.zato.validate_unique('#id_' + constraint.field, constraint.entity_type, constraint.attr_name);
        $.fn.zato.validate_unique('#id_edit-' + constraint.field, constraint.entity_type, constraint.attr_name);
    });
})

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.mongodb.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new outgoing MongoDB connection', null);
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.mongodb.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the outgoing MongoDB connection', id);
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.mongodb.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var isActive = item.is_active == true;
    var isTLSEnabled = item.is_tls_enabled == true;

    // The visible cell shows each server on its own line
    var serverListDisplay = item.server_list.replace(/\n/g, '<br/>');

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";

    // 1
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', isActive ? 'Yes' : 'No');
    row += String.format('<td>{0}</td>', serverListDisplay);
    row += String.format('<td>{0}</td>', isTLSEnabled ? 'Yes' : 'No');

    // 2
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.outgoing.mongodb.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.outgoing.mongodb.delete_('{0}');\">Delete</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:void(0)\" onclick=\"$.fn.zato.data_table.ping('{0}', this)\">Ping</a>", item.id));

    // 3
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", item.is_active);
    row += String.format("<td class='ignore'>{0}</td>", item.server_list);

    // 4
    row += String.format("<td class='ignore'>{0}</td>", item.username ? item.username : '');
    row += String.format("<td class='ignore'>{0}</td>", item.auth_source ? item.auth_source : '');
    row += String.format("<td class='ignore'>{0}</td>", item.replica_set ? item.replica_set : '');
    row += String.format("<td class='ignore'>{0}</td>", item.app_name ? item.app_name : '');

    // 5
    row += String.format("<td class='ignore'>{0}</td>", item.pool_size_max);
    row += String.format("<td class='ignore'>{0}</td>", item.connect_timeout);
    row += String.format("<td class='ignore'>{0}</td>", item.server_select_timeout);

    // 6
    row += String.format("<td class='ignore'>{0}</td>", item.is_tls_enabled);
    row += String.format("<td class='ignore'>{0}</td>", item.tls_ca_certs_file ? item.tls_ca_certs_file : '');
    row += String.format("<td class='ignore'>{0}</td>", item.tls_cert_key_file ? item.tls_cert_key_file : '');
    row += String.format("<td class='ignore'>{0}</td>", item.is_tls_validation_enabled);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.mongodb.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Outgoing MongoDB connection `{0}` deleted',
        'Are you sure you want to delete outgoing MongoDB connection `{0}`?',
        true);
}
