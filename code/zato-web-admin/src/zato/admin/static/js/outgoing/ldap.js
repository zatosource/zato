
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.LDAP = new Class({
    toString: function() {
        var s = '<LDAP id:{0} name:{1} is_active:{2}';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.is_active ? this.is_active : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = true;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.LDAP;
    $.fn.zato.data_table.new_row_func = $.fn.zato.outgoing.ldap.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'server_list', 'pool_size', 'pool_exhaust_timeout',
        'pool_keep_alive', 'pool_max_cycles', 'pool_lifetime']);
    var unique_constraints = [
        {field: 'name', entity_type: 'generic_connection', attr_name: 'name'}
    ];
    $.each(unique_constraints, function(i, c) {
        $.fn.zato.validate_unique('#id_' + c.field, c.entity_type, c.attr_name);
        $.fn.zato.validate_unique('#id_edit-' + c.field, c.entity_type, c.attr_name);
    });
})

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.ldap.field_descriptions = {
    'id_name': 'A unique name for this connection.<br>Services refer to it by this exact name.',
    'id_is_active': 'Whether this connection can be used.<br>Services cannot look up an inactive connection.',
    'id_pool_size': 'How many LDAP connections the pool keeps open.<br>Each concurrent request needs one connection.',
    'id_username': 'The DN the connection binds as,<br>e.g. cn=admin,dc=example,dc=org.<br>The password is set separately<br>with the Change password link.',
    'id_server_list': 'LDAP servers to connect to, one per line,<br>as host:port, e.g. localhost:389.<br>With multiple servers, the pool\'s HA strategy<br>decides which one each connection uses.',
    'id_pool_name': 'An optional name for the underlying pool,<br>useful when several connections<br>share one server-side pool.',
    'id_pool_max_cycles': 'How many times the pool cycles through<br>all servers before giving up<br>on finding an active one.',
    'id_pool_ha_strategy': 'How the pool picks a server for each connection -<br>one at a time (First), round-robin or random.',
    'id_get_info': 'What server metadata to read after connecting -<br>the schema, DSA info, both or none.<br>Schema is needed for checked names<br>and attribute formatting.',
    'id_auto_bind': 'Whether and how connections bind automatically<br>when taken from the pool, including whether TLS<br>starts before or after the bind.',
    'id_connect_timeout': 'How many seconds to wait for the TCP connection<br>to a server before trying the next one.',
    'id_pool_exhaust_timeout': 'How many seconds to wait for a free connection<br>when the whole pool is busy<br>before raising an error.',
    'id_pool_keep_alive': 'How often, in seconds, idle pooled connections<br>send a keep-alive query so the server<br>does not drop them.',
    'id_auth_type': 'How the bind authenticates - Simple sends<br>the DN and password directly, NTLM uses<br>Windows domain credentials.',
    'id_sasl_mechanism': 'Optional SASL mechanism used for binding<br>instead of a simple bind, e.g. EXTERNAL<br>with TLS client certificates.',
    'id_is_read_only': 'When on, only searches are allowed -<br>add, modify and delete operations are rejected<br>client-side before reaching the server.',
    'id_use_auto_range': 'When on, attributes returned in ranged chunks<br>by Active Directory are fetched in full<br>automatically.',
    'id_should_check_names': 'When on, attribute names in requests<br>are validated against the server schema.<br>Requires schema info to be read.',
    'id_should_return_empty_attrs': 'When on, attributes without a value<br>are returned as empty ones instead of<br>being left out of results.',
};

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.ldap.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new outgoing LDAP connection', null);
    $.fn.zato.how_it_works.init({
        badgeId: 'create-how-it-works',
        divId: '#create-div',
        descriptions: $.fn.zato.outgoing.ldap.field_descriptions
    });
}

$.fn.zato.outgoing.ldap.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the outgoing LDAP connection', id);
    $.fn.zato.how_it_works.init({
        badgeId: 'edit-how-it-works',
        divId: '#edit-div',
        descriptions: $.fn.zato.outgoing.ldap.field_descriptions
    });
}

$.fn.zato.outgoing.ldap.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var is_active = item.is_active == true;
    var has_auto_reconnect = item.has_auto_reconnect == true;
    var is_read_only = item.is_read_only == true;
    var is_stats_enabled = item.is_stats_enabled == true;
    var should_check_names = item.should_check_names == true;
    var use_auto_range = item.use_auto_range == true;
    var should_return_empty_attrs = item.should_return_empty_attrs == true;
    var is_tls_enabled = item.is_tls_enabled == true;

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";

    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', is_active ? 'Yes' : 'No');
    row += String.format('<td>{0}</td>', item.server_list);
    row += String.format('<td>{0}</td>', item.username);

    row += String.format('<td>{0}</td>', item.auth_type);
    row += String.format('<td>{0}</td>', is_tls_enabled ? 'Yes' : 'No');

    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.data_table.change_password('{0}')\">Change password</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.outgoing.ldap.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.outgoing.ldap.delete_('{0}');\">Delete</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:void(0)\" onclick=\"$.fn.zato.data_table.ping('{0}', this)\">Ping</a>", item.id));

    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", is_active);

    // 1 -->
    row += String.format("<td class='ignore'>{0}</td>", item.get_info);
    row += String.format("<td class='ignore'>{0}</td>", item.ip_mode);
    row += String.format("<td class='ignore'>{0}</td>", item.connect_timeout);
    row += String.format("<td class='ignore'>{0}</td>", item.auto_bind);

    console.log('QQQ ' + item.server_list);

    // 2 -->
    row += String.format("<td class='ignore'>{0}</td>", item.server_list);
    row += String.format("<td class='ignore'>{0}</td>", item.pool_size);
    row += String.format("<td class='ignore'>{0}</td>", item.pool_exhaust_timeout);
    row += String.format("<td class='ignore'>{0}</td>", item.pool_keep_alive);

    // 3 -->
    row += String.format("<td class='ignore'>{0}</td>", item.pool_max_cycles);
    row += String.format("<td class='ignore'>{0}</td>", item.pool_lifetime);
    row += String.format("<td class='ignore'>{0}</td>", item.pool_ha_strategy);

    // 4 -->
    row += String.format("<td class='ignore'>{0}</td>", item.pool_name);
    row += String.format("<td class='ignore'>{0}</td>", item.sasl_mechanism);
    row += String.format("<td class='ignore'>{0}</td>", is_read_only ? 'Yes' : 'No');
    row += String.format("<td class='ignore'>{0}</td>", is_stats_enabled ? 'Yes' : 'No');

    // 5 -->
    row += String.format("<td class='ignore'>{0}</td>", should_check_names ? 'Yes' : 'No');
    row += String.format("<td class='ignore'>{0}</td>", use_auto_range ? 'Yes' : 'No');
    row += String.format("<td class='ignore'>{0}</td>", should_return_empty_attrs ? 'Yes' : 'No');
    row += String.format("<td class='ignore'>{0}</td>", is_tls_enabled ? 'Yes' : 'No');

    // 6 -->
    row += String.format("<td class='ignore'>{0}</td>", item.tls_private_key_file);
    row += String.format("<td class='ignore'>{0}</td>", item.tls_cert_file);
    row += String.format("<td class='ignore'>{0}</td>", item.tls_ca_certs_file);
    row += String.format("<td class='ignore'>{0}</td>", item.tls_version);

    // 7 -->
    row += String.format("<td class='ignore'>{0}</td>", item.tls_ciphers);
    row += String.format("<td class='ignore'>{0}</td>", item.tls_validate);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.outgoing.ldap.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Outgoing LDAP connection `{0}` deleted',
        'Are you sure you want to delete outgoing LDAP connection `{0}`?',
        true);
}
