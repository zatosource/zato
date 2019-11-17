
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.ChannelFTP = new Class({
    toString: function() {
        var s = '<ChannelFTP id:{0} name:{1} is_active:{2}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.is_active ? this.is_active : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.ChannelFTP;
    $.fn.zato.data_table.new_row_func = $.fn.zato.channel.ftp.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms([
        'name', 'address', 'base_directory',
        'max_connections', 'max_conn_per_ip', 'command_timeout',
        'read_throttle', 'write_throttle', 'log_level',
        'log_prefix', 'banner'
    ]);
})

$.fn.zato.channel.ftp.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new FTP channel', null);
}

$.fn.zato.channel.ftp.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the FTP channel', id);
}

$.fn.zato.channel.ftp.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var is_active = item.is_active == true;
    var cluster_id = $(document).getUrlParam('cluster');

    var service_link = $.fn.zato.empty_value;
    var topic_link = $.fn.zato.empty_value;

    if(item.service_name) {
        service_link = $.fn.zato.data_table.service_text(item.service_name, cluster_id);
    }

    if(item.topic_name) {
        topic_link = $.fn.zato.data_table.topic_text(item.topic_name, cluster_id);
    }

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";

    // 1
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', is_active ? 'Yes' : 'No');
    row += String.format('<td>{0}</td>', item.address);

    // 2
    row += String.format('<td>{0}</td>', service_link);
    row += String.format('<td>{0}</td>', topic_link);
    row += String.format('<td>{0}</td>', item.base_directory);

    // 3
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.channel.ftp.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.channel.ftp.delete_({0});'>Delete</a>", item.id));
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);

    // 4
    row += String.format("<td class='ignore'>{0}</td>", is_active);
    row += String.format("<td class='ignore'>{0}</td>", item.max_connections);
    row += String.format("<td class='ignore'>{0}</td>", item.command_timeout);

    // 5
    row += String.format("<td class='ignore'>{0}</td>", item.banner);
    row += String.format("<td class='ignore'>{0}</td>", item.log_prefix);
    row += String.format("<td class='ignore'>{0}</td>", item.read_throttle);

    // 6
    row += String.format("<td class='ignore'>{0}</td>", item.write_throttle);

    // 7
    row += String.format("<td class='ignore'>{0}</td>", item.max_conn_per_ip);
    row += String.format("<td class='ignore'>{0}</td>", item.service_name);

    // 8
    row += String.format("<td class='ignore'>{0}</td>", item.topic_name);
    row += String.format("<td class='ignore'>{0}</td>", item.log_level);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.channel.ftp.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'FTP channel `{0}` deleted',
        'Are you sure you want to delete FTP channel `{0}`?',
        true);
}
