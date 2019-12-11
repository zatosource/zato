
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.ChannelFileTransfer = new Class({
    toString: function() {
        var s = '<ChannelFileTransfer id:{0} name:{1} is_active:{2}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.is_active ? this.is_active : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.ChannelFileTransfer;
    $.fn.zato.data_table.new_row_func = $.fn.zato.channel.file_transfer.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'address', 'idle_timeout', 'keep_alive_timeout', 'sftp_command']);
})

$.fn.zato.channel.file_transfer.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new SFTP channel', null);
}

$.fn.zato.channel.file_transfer.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the SFTP channel', id);
}

$.fn.zato.channel.file_transfer.data_table.new_row = function(item, data, include_tr) {
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
    row += String.format('<td>{0}</td>', item.host_key ? item.host_key : $.fn.zato.empty_value);

    // 3
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.channel.file_transfer.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.channel.file_transfer.delete_({0});'>Delete</a>", item.id));
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);

    // 4
    row += String.format("<td class='ignore'>{0}</td>", is_active);
    row += String.format("<td class='ignore'>{0}</td>", item.service_name);
    row += String.format("<td class='ignore'>{0}</td>", item.topic_name);

    // 5
    row += String.format("<td class='ignore'>{0}</td>", item.idle_timeout);
    row += String.format("<td class='ignore'>{0}</td>", item.keep_alive_timeout);
    row += String.format("<td class='ignore'>{0}</td>", item.sftp_command);

    // 6
    row += String.format("<td class='ignore'>{0}</td>", item.host_key);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.channel.file_transfer.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'File transfer channel `{0}` deleted',
        'Are you sure you want to delete file transfer channel `{0}`?',
        true);
}
