
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
    $.fn.zato.data_table.setup_forms(['name', 'pickup_from', 'file_patterns']);
})

$.fn.zato.channel.file_transfer.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new file transfer channel', null);
}

$.fn.zato.channel.file_transfer.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the file transfer channel', id);
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

    // 2
    row += String.format('<td>{0}</td>', service_link);
    row += String.format('<td>{0}</td>', item.pickup_from ? item.pickup_from : $.fn.zato.empty_value);
    row += String.format('<td>{0}</td>', item.file_patterns);

    // 3
    row += String.format('<td>{0}</td>', item.move_processed_to ? item.move_processed_to : $.fn.zato.empty_value);
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.channel.file_transfer.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.channel.file_transfer.delete_({0});'>Delete</a>", item.id));

    // 4
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format('<td>{0}</td>', item.is_active);
    row += String.format('<td>{0}</td>', item.service_list);

    // 5
    row += String.format('<td>{0}</td>', item.topic_list);
    row += String.format('<td>{0}</td>', item.read_on_pickup);

    // 6
    row += String.format('<td>{0}</td>', item.parse_on_pickup);
    row += String.format('<td>{0}</td>', item.parse_with);
    row += String.format('<td>{0}</td>', item.delete_after_pickup);

    // 7
    row += String.format('<td>{0}</td>', item.is_internal);

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
