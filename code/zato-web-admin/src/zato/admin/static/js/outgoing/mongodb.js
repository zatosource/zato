
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
    // Generic connection names are unique per connection type,
    // so the check is scoped to this page's own type.
    var uniqueConstraints = [
        {field: 'name', entity_type: 'generic_connection', attr_name: 'name',
            filter_name: 'type_', filter_value: 'outconn-mongodb'}
    ];
    $.each(uniqueConstraints, function(constraintIndex, constraint) {
        $.fn.zato.validate_unique('#id_' + constraint.field, constraint.entity_type, constraint.attr_name, constraint);
        $.fn.zato.validate_unique('#id_edit-' + constraint.field, constraint.entity_type, constraint.attr_name, constraint);
    });
})

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.mongodb.field_descriptions = {
    'id_name': 'A unique name for this connection.<br>Services refer to it by this exact name.',
    'id_is_active': 'Whether this connection can be used.<br>Services cannot look up an inactive connection.',
    'id_server_list': 'MongoDB servers as host:port, one per line,<br>e.g. localhost:27017. List all the members<br>when connecting to a replica set.',
    'id_username': 'Username to authenticate with.<br>Leave empty if the server<br>does not require authentication.',
    'id_secret': 'Password matching the username above.<br>Stored encrypted in the Zato database.',
    'id_auth_source': 'Database the credentials are defined in.<br>MongoDB defaults to admin.',
    'id_replica_set': 'Name of the replica set to require.<br>Leave empty for standalone servers.',
    'id_app_name': 'Application name reported to the server.<br>It shows up in MongoDB logs and currentOp output,<br>making this client easy to identify.',
    'id_pool_size_max': 'Maximum number of connections the client pool<br>keeps open to the server at the same time.',
    'id_connect_timeout': 'How many seconds to wait for the TCP connection<br>to a server before giving up. Default is 10.',
    'id_server_select_timeout': 'How many seconds to keep looking for a suitable<br>server, e.g. a replica set primary,<br>before an operation fails. Default is 5.',
    'id_is_tls_enabled': 'When on, all traffic to the servers is encrypted<br>with TLS. Required for the certificate<br>options below to take effect.',
    'id_is_tls_validation_enabled': 'When on, the server\'s certificate is verified<br>against the CA certs file below.<br>Turn it off only with test environments.',
    'id_tls_ca_certs_file': 'Path to a PEM file with CA certificates<br>used to verify the server\'s certificate.',
    'id_tls_cert_key_file': 'Path to a PEM file with the client certificate<br>and its private key combined, for mutual TLS.',
};

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.mongodb.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new outgoing MongoDB connection', null);
    $.fn.zato.how_it_works.init({
        badgeId: 'create-how-it-works',
        divId: '#create-div',
        descriptions: $.fn.zato.outgoing.mongodb.field_descriptions
    });
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.mongodb.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the outgoing MongoDB connection', id);
    $.fn.zato.how_it_works.init({
        badgeId: 'edit-how-it-works',
        divId: '#edit-div',
        descriptions: $.fn.zato.outgoing.mongodb.field_descriptions
    });
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
