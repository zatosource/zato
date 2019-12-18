
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.ChannelFileTransfer = new Class({
    toString: function() {
        var s = '<ChannelFileTransfer id:{0} name:{1} is_active:{2}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.is_active ? this.is_active : '(none)');
    }
});

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.ChannelFileTransfer;
    $.fn.zato.data_table.new_row_func = $.fn.zato.channel.file_transfer.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'source_type', 'pickup_from', 'file_patterns']);

    $('#id_source_type').change(function() {
        $.fn.zato.channel.file_transfer.on_source_type_changed('');
    });

    $('#id_edit-source_type').change(function() {
        $.fn.zato.channel.file_transfer.on_source_type_changed('edit-');
    });

})

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.file_transfer.on_source_type_changed = function(prefix) {

    let id_prefix = '#id_'+ prefix;
    let source_type = $(id_prefix + 'source_type').val();

    if(source_type) {

        let ftp = $(id_prefix + 'ftp_source_id');
        let sftp = $(id_prefix + 'sftp_source_id');

        if(source_type=='local') {
            ftp.addClass('hidden');
            sftp.addClass('hidden');
        }

        else if(source_type=='ftp') {
            ftp.removeClass('hidden');
            sftp.addClass('hidden');
        }

        else if(source_type=='sftp') {
            sftp.removeClass('hidden');
            ftp.addClass('hidden');
        }
    }
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.file_transfer.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new file transfer channel', null);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.file_transfer.edit = function(id) {

    let instance = $.fn.zato.data_table.data[id];
    let source_type = $('#id_edit-'+ instance.source_type +'_source_id');
    source_type.removeClass('hidden');

    $.fn.zato.data_table.multirow.remove_multirow_added();
    $.fn.zato.data_table.edit('edit', 'Update the file transfer channel', id, false);
    $.fn.zato.data_table.multirow.populate_select_field('service_list', JSON.parse(instance.service_list_json));
    $.fn.zato.data_table.multirow.populate_select_field('topic_list', JSON.parse(instance.topic_list_json));
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

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
    row += String.format('<td>{0}</td>', item.source_html);

    // 2
    row += String.format('<td>{0}</td>', item.pickup_from ? item.pickup_from : $.fn.zato.empty_value);
    row += String.format('<td>{0}</td>', item.move_processed_to ? item.move_processed_to : $.fn.zato.empty_value);

    // 3
    row += String.format('<td>{0}</td>', service_link);
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.channel.file_transfer.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.channel.file_transfer.delete_({0});'>Delete</a>", item.id));

    // 4
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", item.is_active);
    row += String.format("<td class='ignore'>{0}</td>", item.service_list);

    // 5
    row += String.format("<td class='ignore'>{0}</td>", item.topic_list);
    row += String.format("<td class='ignore'>{0}</td>", item.read_on_pickup);

    // 6
    row += String.format("<td class='ignore'>{0}</td>", item.parse_on_pickup);
    row += String.format("<td class='ignore'>{0}</td>", item.parse_with);
    row += String.format("<td class='ignore'>{0}</td>", item.delete_after_pickup);

    // 7
    row += String.format("<td class='ignore'>{0}</td>", item.is_internal);
    row += String.format("<td class='ignore'>{0}</td>", item.source_type);
    row += String.format("<td class='ignore'>{0}</td>", item.ftp_source_id);

    // 8
    row += String.format("<td class='ignore'>{0}</td>", item.sftp_source_id);
    row += String.format("<td class='ignore'>{0}</td>", item.file_patterns);
    row += String.format("<td class='ignore'>{0}</td>", item.scheduler_job_id);

    // 9
    row += String.format("<td class='ignore'>{0}</td>", item.service_list_json);
    row += String.format("<td class='ignore'>{0}</td>", item.topic_list_json);
    row += String.format("<td class='ignore'>{0}</td>", item.line_by_line);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.file_transfer.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'File transfer channel `{0}` deleted',
        'Are you sure you want to delete file transfer channel `{0}`?',
        true);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
