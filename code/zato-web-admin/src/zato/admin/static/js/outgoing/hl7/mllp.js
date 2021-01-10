
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.HL7MLLPOutconn = new Class({
    toString: function() {
        var s = '<HL7MLLPOutconn id:{0} name:{1} is_active:{2}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.is_active ? this.is_active : '(none)');
    }
});

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.HL7MLLPOutconn;
    $.fn.zato.data_table.new_row_func = $.fn.zato.outgoing.hl7.mllp.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms([
        'name',
        'address',
        'pool_size',
        'timeout',
        'max_msg_size',
        'read_buffer_size',
        'recv_timeout',
        'start_seq',
        'end_seq',
    ]);
})

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.hl7.mllp.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new HL7 MLLP outgoing connection', null);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.hl7.mllp.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the HL7 MLLP outgoing connection', id);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.hl7.mllp.data_table.new_row = function(item, data, include_tr) {
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
    row += String.format('<td>{0}</td>', item.address);

    // 2
    row += String.format("<td>{0}</td>", item.pool_size);
    row += String.format('<td><a href="/zato/audit-log/outgoing-hl7-mllp/{0}/?cluster={1}&amp;object_name={2}&amp;object_type_label={3}">View</a></td>',
        item.id, cluster_id, item.name, 'HL7&nbsp;MLLP&nbsp;outgoing&nbsp;connection');
    row += String.format('<td><a href="/zato/outgoing/hl7/mllp/invoke/{0}/{1}/{2}/?cluster={3}">Invoke</a></td>',
        item.id, item.name, $.fn.zato.slugify(item.name), cluster_id);

    // 3
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.outgoing.hl7.mllp.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.outgoing.hl7.mllp.delete_({0});'>Delete</a>", item.id));
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);

    // 4
    row += String.format("<td class='ignore'>{0}</td>", item.is_active);

    // 5
    row += String.format("<td class='ignore'>{0}</td>", item.is_audit_log_sent_active);
    row += String.format("<td class='ignore'>{0}</td>", item.is_audit_log_received_active);
    row += String.format("<td class='ignore'>{0}</td>", item.max_len_messages_sent);

    // 6
    row += String.format("<td class='ignore'>{0}</td>", item.max_len_messages_received);
    row += String.format("<td class='ignore'>{0}</td>", item.max_bytes_per_message_sent);
    row += String.format("<td class='ignore'>{0}</td>", item.max_bytes_per_message_received);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.hl7.mllp.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'HL7 MLLP outgoing connection `{0}` deleted',
        'Are you sure you want to delete HL7 MLLP outgoing connection `{0}`?',
        true);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
