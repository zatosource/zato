
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.HL7MLLPChannel = new Class({
    toString: function() {
        var s = '<HL7MLLPChannel id:{0} name:{1} is_active:{2}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.is_active ? this.is_active : '(none)');
    }
});

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.HL7MLLPChannel;
    $.fn.zato.data_table.new_row_func = $.fn.zato.channel.hl7.mllp.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms([
        'name',
        'address',
        'service',
        'logging_level',
        'data_encoding',
        'max_msg_size',
        'read_buffer_size',
        'recv_timeout',
        'start_seq',
        'end_seq',
    ]);
})

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.hl7.mllp.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new HL7 MLLP channel', null);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.hl7.mllp.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the HL7 MLLP channel', id);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.hl7.mllp.data_table.new_row = function(item, data, include_tr) {
    let row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    let is_active = item.is_active == true;
    let cluster_id = $(document).getUrlParam('cluster');

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";

    // 1
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', is_active ? 'Yes' : 'No');

    // 2
    row += String.format('<td>{0}</td>', item.address);
    row += String.format('<td>{0}</td>', $.fn.zato.data_table.service_text(item.service, cluster_id));
    row += String.format('<td><a href="/zato/audit-log/channel-hl7-mllp/{0}/?cluster={1}&amp;object_name={2}&amp;object_type_label={3}">View</a></td>',
        item.id, cluster_id, item.name, 'Channel&nbsp;HL7&nbsp;MLLP');

    // 3
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.channel.hl7.mllp.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.channel.hl7.mllp.delete_({0});'>Delete</a>", item.id));
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);

    // 4
    row += String.format("<td class='ignore'>{0}</td>", item.is_active);
    row += String.format("<td class='ignore'>{0}</td>", item.service);

    // 5
    row += String.format("<td class='ignore'>{0}</td>", item.should_parse_on_input);
    row += String.format("<td class='ignore'>{0}</td>", item.should_validate);

    // 6
    row += String.format("<td class='ignore'>{0}</td>", item.data_encoding);
    row += String.format("<td class='ignore'>{0}</td>", item.should_return_errors);

    // 7
    row += String.format("<td class='ignore'>{0}</td>", item.is_audit_log_sent_active);
    row += String.format("<td class='ignore'>{0}</td>", item.is_audit_log_received_active);
    row += String.format("<td class='ignore'>{0}</td>", item.max_len_messages_sent);

    // 8
    row += String.format("<td class='ignore'>{0}</td>", item.max_len_messages_received);
    row += String.format("<td class='ignore'>{0}</td>", item.max_bytes_per_message_sent);
    row += String.format("<td class='ignore'>{0}</td>", item.max_bytes_per_message_received);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.hl7.mllp.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'HL7 MLLP channel `{0}` deleted',
        'Are you sure you want to delete HL7 MLLP channel `{0}`?',
        true);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
