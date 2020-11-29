
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.SFTP = new Class({
    toString: function() {
        var s = '<SFTP id:{0} name:{1} is_active:{2}';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.is_active ? this.is_active : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = false;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.SFTP;
    $.fn.zato.data_table.new_row_func = $.fn.zato.outgoing.sftp.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'buffer_size', 'bandwidth_limit', 'sftp_command', 'ping_command', 'host']);
})

$.fn.zato.outgoing.sftp.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new outgoing SFTP connection', null);
}

$.fn.zato.outgoing.sftp.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the outgoing SFTP connection', id);
}

$.fn.zato.outgoing.sftp.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var is_active = item.is_active == true;
    var is_compression_enabled = item.is_compression_enabled == true;
    var should_flush = item.should_flush == true;
    var should_preserve_meta = item.should_preserve_meta == true;

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";

    // 1
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', is_active ? 'Yes' : 'No');
    row += String.format('<td>{0}</td>', item.host ? item.host : $.fn.zato.empty_value);

    // 2
    row += String.format('<td>{0}</td>', item.port ? item.port : $.fn.zato.empty_value);
    row += String.format('<td>{0}</td>', item.username ? item.username : $.fn.zato.empty_value);
    row += String.format('<td>{0}</td>', item.identity_file ? item.identity_file : $.fn.zato.empty_value);

    // 3
    row += String.format('<td>{0}</td>', item.default_directory || $.fn.zato.empty_value);
    row += String.format('<td>{0}</td>',
        String.format("<a href=\"./command-shell/{0}/cluster/{1}/{2}/?name={3}\">Command shell</a>",
        item.id, item.cluster_id, data.name_slug, item.name));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.outgoing.sftp.edit('{0}')\">Edit</a>", item.id));

    // 4
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.outgoing.sftp.delete_({0});'>Delete</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.data_table.ping({0});'>Ping</a>", item.id));
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);

    // 5
    row += String.format("<td class='ignore'>{0}</td>", item.is_active);
    row += String.format("<td class='ignore'>{0}</td>", item.log_level);
    row += String.format("<td class='ignore'>{0}</td>", item.host);

    // 6
    row += String.format("<td class='ignore'>{0}</td>", item.port);
    row += String.format("<td class='ignore'>{0}</td>", item.username ? item.username : '');
    row += String.format("<td class='ignore'>{0}</td>", item.identity_file);

    // 7
    row += String.format("<td class='ignore'>{0}</td>", item.ssh_config_file);
    row += String.format("<td class='ignore'>{0}</td>", item.buffer_size);
    row += String.format("<td class='ignore'>{0}</td>", item.is_compression_enabled);

    // 8
    row += String.format("<td class='ignore'>{0}</td>", item.force_ip_type);
    row += String.format("<td class='ignore'>{0}</td>", item.should_flush);
    row += String.format("<td class='ignore'>{0}</td>", item.should_preserve_meta);

    // 9
    row += String.format("<td class='ignore'>{0}</td>", item.ssh_options);
    row += String.format("<td class='ignore'>{0}</td>", item.sftp_command);
    row += String.format("<td class='ignore'>{0}</td>", item.ping_command);

    // 10
    row += String.format("<td class='ignore'>{0}</td>", item.bandwidth_limit);
    row += String.format("<td class='ignore'>{0}</td>", item.default_directory);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.outgoing.sftp.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Outgoing SFTP connection `{0}` deleted',
        'Are you sure you want to delete outgoing SFTP connection `{0}`?',
        true);
}
