
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
    $.fn.zato.data_table.password_required = true;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.MongoDB;
    $.fn.zato.data_table.new_row_func = $.fn.zato.outgoing.mongodb.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'server_list', 'pool_size_max', 'connect_timeout',
        'socket_timeout', 'server_select_timeout', 'wait_queue_timeout', 'max_idle_time', 'hb_frequency']);
})

$.fn.zato.outgoing.mongodb.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new outgoing MongoDB connection', null);
}

$.fn.zato.outgoing.mongodb.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the outgoing MongoDB connection', id);
}

$.fn.zato.outgoing.mongodb.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var is_active = item.is_active == true;
    var is_tls_enabled = item.is_tls_enabled == true;
    var is_tz_aware = item.is_tz_aware == true;
    var is_write_journal_enabled = item.is_write_journal_enabled == true;
    var is_write_fsync_enabled = item.is_write_fsync_enabled == true;
    var is_tls_match_hostname_enabled = item.is_tls_match_hostname_enabled == true;

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";

    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', is_active ? 'Yes' : 'No');
    row += String.format('<td>{0}</td>', item.server_list);

    row += String.format('<td>{0}</td>', item.username ? item.username : $.fn.zato.empty_value);
    row += String.format('<td>{0}</td>', item.app_name ? item.app_name : $.fn.zato.empty_value);
    row += String.format('<td>{0}</td>', is_tls_enabled ? 'Yes' : 'No');

    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.data_table.change_password({0})'>Change password</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.outgoing.mongodb.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.outgoing.mongodb.delete_({0});'>Delete</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.data_table.ping({0});'>Ping</a>", item.id));

    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", is_active);

    // 1 -->
    row += String.format("<td class='ignore'>{0}</td>", item.pool_size_max);
    row += String.format("<td class='ignore'>{0}</td>", item.connect_timeout);
    row += String.format("<td class='ignore'>{0}</td>", item.socket_timeout);
    row += String.format("<td class='ignore'>{0}</td>", item.server_select_timeout);

    // 2 -->
    row += String.format("<td class='ignore'>{0}</td>", item.wait_queue_timeout);
    row += String.format("<td class='ignore'>{0}</td>", item.max_idle_time);
    row += String.format("<td class='ignore'>{0}</td>", item.hb_frequency);
    row += String.format("<td class='ignore'>{0}</td>", item.is_active);

    // 3 -->
    row += String.format("<td class='ignore'>{0}</td>", item.username ? item.username : '');
    row += String.format("<td class='ignore'>{0}</td>", item.app_name ? item.app_name : '');
    row += String.format("<td class='ignore'>{0}</td>", item.replica_set);
    row += String.format("<td class='ignore'>{0}</td>", item.auth_source);

    // 4 -->
    row += String.format("<td class='ignore'>{0}</td>", item.auth_mechanism);
    row += String.format("<td class='ignore'>{0}</td>", item.is_tz_aware);
    row += String.format("<td class='ignore'>{0}</td>", item.document_class);
    row += String.format("<td class='ignore'>{0}</td>", item.compressor_list);

    // 5 -->
    row += String.format("<td class='ignore'>{0}</td>", item.zlib_level);
    row += String.format("<td class='ignore'>{0}</td>", item.write_to_replica);
    row += String.format("<td class='ignore'>{0}</td>", item.write_timeout);
    row += String.format("<td class='ignore'>{0}</td>", item.is_write_journal_enabled);

    // 6 -->
    row += String.format("<td class='ignore'>{0}</td>", item.is_write_fsync_enabled);
    row += String.format("<td class='ignore'>{0}</td>", item.read_pref_type);
    row += String.format("<td class='ignore'>{0}</td>", item.read_pref_tag_list);
    row += String.format("<td class='ignore'>{0}</td>", item.read_pref_max_stale);

    // 7 -->
    row += String.format("<td class='ignore'>{0}</td>", item.is_tls_enabled);
    row += String.format("<td class='ignore'>{0}</td>", item.tls_private_key_file);
    row += String.format("<td class='ignore'>{0}</td>", item.tls_cert_file);
    row += String.format("<td class='ignore'>{0}</td>", item.tls_ca_certs_file);

    // 8 -->
    row += String.format("<td class='ignore'>{0}</td>", item.tls_crl_file);
    row += String.format("<td class='ignore'>{0}</td>", item.tls_version);
    row += String.format("<td class='ignore'>{0}</td>", item.tls_validate);
    row += String.format("<td class='ignore'>{0}</td>", item.tls_pem_passphrase);

    // 9 -->
    row += String.format("<td class='ignore'>{0}</td>", item.is_tls_match_hostname_enabled);
    row += String.format("<td class='ignore'>{0}</td>", item.tls_ciphers);
    row += String.format("<td class='ignore'>{0}</td>", item.should_retry_write);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.outgoing.mongodb.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Outgoing MongoDB connection `{0}` deleted',
        'Are you sure you want to delete outgoing MongoDB connection `{0}`?',
        true);
}
