
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
})

$.fn.zato.outgoing.ldap.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new outgoing LDAP connection', null);
}

$.fn.zato.outgoing.ldap.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the outgoing LDAP connection', id);
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

    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.data_table.change_password({0})'>Change password</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.outgoing.ldap.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.outgoing.ldap.delete_({0});'>Delete</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.data_table.ping({0});'>Ping</a>", item.id));

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
