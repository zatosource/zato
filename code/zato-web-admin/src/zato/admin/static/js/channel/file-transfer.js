
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
    $.fn.zato.data_table.setup_forms(['name', 'source_type', 'pickup_from_list', 'file_patterns']);

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

        let ftp       = $(id_prefix + 'ftp_source_id');
        let sftp      = $(id_prefix + 'sftp_source_id');

        let scheduler_create_row = $('#tr_create_scheduler_job_id');
        let scheduler_edit_row = $('#tr_edit_scheduler_job_id');

        if(source_type == 'local') {

            scheduler_create_row.addClass('hidden');
            scheduler_edit_row.addClass('hidden');

            ftp.addClass('hidden');
            sftp.addClass('hidden');
        }

        else if(source_type == 'ftp') {

            scheduler_create_row.removeClass('hidden');
            scheduler_edit_row.removeClass('hidden');

            ftp.removeClass('hidden');
            sftp.addClass('hidden');
        }

        else if(source_type == 'sftp') {

            scheduler_create_row.removeClass('hidden');
            scheduler_edit_row.removeClass('hidden');

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

    if(instance.source_type != "local") {

        let scheduler_create_row = $('#tr_create_scheduler_job_id');
        let scheduler_edit_row = $('#tr_edit_scheduler_job_id');

        scheduler_create_row.removeClass('hidden');
        scheduler_edit_row.removeClass('hidden');
    };

    $('#id_edit-ftp_source_name').val(instance.ftp_source_name);
    $('#id_edit-sftp_source_name').val(instance.sftp_source_name);

    $.fn.zato.data_table.multirow.remove_multirow_added();
    $.fn.zato.data_table.edit('edit', 'Update the file transfer channel', id, false);

    $.fn.zato.data_table.multirow.populate_field('service_list', instance.service_list);
    $.fn.zato.data_table.multirow.populate_field('topic_list', instance.topic_list);
    $.fn.zato.data_table.multirow.populate_field('outconn_rest_list', instance.outconn_rest_list);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.file_transfer.data_table.new_row = function(item, data, include_tr) {
    let row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    let is_active = item.is_active == true;
    let cluster_id = $(document).getUrlParam('cluster');

    let source_html = $.fn.zato.empty_value;
    let pickup_from_list_html = '';
    let recipients_html = data.recipients_html || '<span class="form_hint">---</span>';

    if(item.source_type == 'local') {
        source_html = 'Local';
    }
    else if(item.source_type == 'ftp') {
        if(item.ftp_source_name) {
            source_html = `<a href="/zato/outgoing/ftp/?cluster=${item.cluster_id}&amp;query=${item.ftp_source_name}">${item.ftp_source_name}</a>`;
        }
        else {
            source_html = 'FTP <span class="form_hint"><br/>(No connection assigned)</span>';
        }
    }
    else if(item.source_type == 'sftp') {
        if(item.sftp_source_name) {
            source_html = `<a href="/zato/outgoing/sftp/?cluster=${item.cluster_id}&amp;type_=outconn-sftp&amp;query=${item.sftp_source_name}">${item.sftp_source_name}</a>`;
        }
        else {
            source_html = 'SFTP <span class="form_hint"><br/>(No connection assigned)</span>';
        }
    }

    pickup_from_list_html += String.replace(item.pickup_from_list.replace("\n", "<br/>"));
    pickup_from_list_html += '<br/>';
    pickup_from_list_html += item.file_patterns;

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";

    // 1
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', is_active ? 'Yes' : 'No');
    row += String.format('<td>{0}</td>', source_html);

    // 2
    row += String.format('<td>{0}</td>', pickup_from_list_html);
    row += String.format('<td>{0}</td>', item.move_processed_to ? item.move_processed_to : $.fn.zato.empty_value);

    // 3
    row += String.format('<td>{0}</td>', recipients_html);
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.channel.file_transfer.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.channel.file_transfer.delete_({0});'>Delete</a>", item.id));

    // 4
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", item.is_active);

    // 5
    row += String.format("<td class='ignore'>{0}</td>", item.should_read_on_pickup);
    row += String.format("<td class='ignore'>{0}</td>", data.service_list);
    row += String.format("<td class='ignore'>{0}</td>", data.topic_list);

    // 6
    row += String.format("<td class='ignore'>{0}</td>", item.should_parse_on_pickup);
    row += String.format("<td class='ignore'>{0}</td>", item.parse_with);
    row += String.format("<td class='ignore'>{0}</td>", item.should_delete_after_pickup);

    // 7
    row += String.format("<td class='ignore'>{0}</td>", item.is_internal);
    row += String.format("<td class='ignore'>{0}</td>", item.source_type);
    row += String.format("<td class='ignore'>{0}</td>", item.ftp_source_id);

    // 8
    row += String.format("<td class='ignore'>{0}</td>", item.sftp_source_id);
    row += String.format("<td class='ignore'>{0}</td>", item.file_patterns);
    row += String.format("<td class='ignore'>{0}</td>", item.scheduler_job_id);

    // 9
    row += String.format("<td class='ignore'>{0}</td>", item.is_line_by_line);

    // 10
    row += String.format("<td class='ignore'>{0}</td>", item.pickup_from_list);
    row += String.format("<td class='ignore'>{0}</td>", item.ftp_source_name);
    row += String.format("<td class='ignore'>{0}</td>", item.sftp_source_name);

    // 11
    row += String.format("<td class='ignore'>{0}</td>", item.is_case_sensitive);
    row += String.format("<td class='ignore'>{0}</td>", item.move_processed_to);
    row += String.format("<td class='ignore'>{0}</td>", item.is_hot_deploy);

    // 12
    row += String.format("<td class='ignore'>{0}</td>", item.binary_file_patterns);
    row += String.format("<td class='ignore'>{0}</td>", item.data_encoding);
    row += String.format("<td class='ignore'>{0}</td>", data.outconn_rest_list);

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
