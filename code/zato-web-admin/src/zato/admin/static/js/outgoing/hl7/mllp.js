
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
        'max_wait_time',
        'max_msg_size',
        'read_buffer_size',
        'recv_timeout',
        'start_seq',
        'end_seq',
        'logging_level',
        'max_retries',
        'backoff_base_seconds',
        'backoff_cap_seconds',
        'backoff_jitter_percent',
        'circuit_breaker_threshold_percent',
        'circuit_breaker_window_seconds',
        'circuit_breaker_reset_seconds',
        'tls_cert_path',
        'tls_key_path',
        'tls_ca_path',
    ]);
    var unique_constraints = [
        {field: 'name', entity_type: 'generic_connection', attr_name: 'name'}
    ];
    $.each(unique_constraints, function(i, c) {
        $.fn.zato.validate_unique('#id_' + c.field, c.entity_type, c.attr_name);
        $.fn.zato.validate_unique('#id_edit-' + c.field, c.entity_type, c.attr_name);
    });
})

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.hl7.mllp.field_descriptions = {
    'id_name': 'A unique name for this connection.<br>Services send messages through it with<br>self.mllp[name].send(data).',
    'id_address': 'The remote MLLP endpoint as host:port,<br>e.g. 10.20.30.40:2575.',
    'id_is_active': 'Whether this connection can be used.<br>Services cannot look up an inactive connection.',
    'id_pool_size': 'How many connections the pool keeps open<br>to the remote endpoint. Each concurrent send<br>uses one connection. Default is 10.',
    'id_should_log_messages': 'When on, outgoing messages and acknowledgments<br>are logged in full. Development only -<br>HL7 messages contain patient data.',
    'id_max_wait_time': 'Default timeout in seconds for test messages<br>sent from the dashboard\'s Invoke screen.<br>Default is 5.',
    'id_max_msg_size': 'The biggest acknowledgment accepted, in bytes.<br>Larger replies are rejected.<br>Default is 2000000.',
    'id_read_buffer_size': 'Size of the socket read buffer, in bytes.<br>The default of 32768 rarely needs changing.',
    'id_start_seq': 'MLLP frame start bytes, in hex, e.g. 0b.<br>Sent before each message. The default<br>matches the MLLP standard.',
    'id_end_seq': 'MLLP frame end bytes, in hex, e.g. 1c 0d.<br>Sent after each message. The default<br>matches the MLLP standard.',
    'id_recv_timeout': 'How long to wait for the acknowledgment,<br>in milliseconds. Default is 250.',
    'id_logging_level': 'Log level this connection uses for<br>its own log entries, e.g. INFO or DEBUG.',
    'id_max_retries': 'How many times a failed send is retried<br>before giving up. Default is 5.',
    'id_backoff_base_seconds': 'Delay in seconds before the first retry.<br>Each further retry doubles the delay,<br>up to the backoff cap. Default is 1.',
    'id_backoff_cap_seconds': 'Upper limit in seconds for the delay<br>between retries, no matter how many attempts<br>have been made already. Default is 300.',
    'id_backoff_jitter_percent': 'Random percentage applied to each retry delay<br>so that many senders do not all retry<br>at the same moment. Default is 10.',
    'id_circuit_breaker_threshold_percent': 'Failure percentage within the window that opens<br>the circuit and pauses sending to the endpoint.<br>Default is 50.',
    'id_circuit_breaker_window_seconds': 'Length in seconds of the rolling window<br>the failure percentage is computed over.<br>Default is 60.',
    'id_circuit_breaker_reset_seconds': 'How long in seconds the circuit stays open<br>before a trial message is let through again.<br>Default is 60.',
    'id_tls_cert_path': 'Path to the client certificate presented<br>to the server, for mutual TLS.<br>Requires the CA path to be set too.',
    'id_tls_key_path': 'Path to the private key matching<br>the client certificate, for mutual TLS.',
    'id_tls_ca_path': 'Path to the CA bundle used to verify the server.<br>Setting it turns TLS on, minimum version 1.2.<br>Leave empty for a plaintext connection.',
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.hl7.mllp.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new HL7 MLLP outgoing connection', null);
    $.fn.zato.how_it_works.init({
        badgeId: 'create-how-it-works',
        divId: '#create-div',
        descriptions: $.fn.zato.outgoing.hl7.mllp.field_descriptions
    });
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.hl7.mllp.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the HL7 MLLP outgoing connection', id);
    $.fn.zato.how_it_works.init({
        badgeId: 'edit-how-it-works',
        divId: '#edit-div',
        descriptions: $.fn.zato.outgoing.hl7.mllp.field_descriptions
    });
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

    row += String.format("<td>{0}</td>", item.pool_size);
    row += String.format('<td><a href="/zato/outgoing/hl7/mllp/invoke/{0}/{1}/{2}/{3}/?cluster={4}">Invoke</a></td>',
        item.id, item.max_wait_time, item.name, $.fn.zato.slugify(item.name), cluster_id);

    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.outgoing.hl7.mllp.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.outgoing.hl7.mllp.delete_('{0}');\">Delete</a>", item.id));
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);

    row += String.format("<td class='ignore'>{0}</td>", item.is_active);

    row += String.format("<td class='ignore'>{0}</td>", item.should_log_messages);
    row += String.format("<td class='ignore'>{0}</td>", item.logging_level);

    row += String.format("<td class='ignore'>{0}</td>", item.max_msg_size);
    row += String.format("<td class='ignore'>{0}</td>", item.read_buffer_size);
    row += String.format("<td class='ignore'>{0}</td>", item.recv_timeout);

    row += String.format("<td class='ignore'>{0}</td>", item.start_seq);
    row += String.format("<td class='ignore'>{0}</td>", item.end_seq);

    row += String.format("<td class='ignore'>{0}</td>", item.max_wait_time);

    row += String.format("<td class='ignore'>{0}</td>", item.max_retries);
    row += String.format("<td class='ignore'>{0}</td>", item.backoff_base_seconds);
    row += String.format("<td class='ignore'>{0}</td>", item.backoff_cap_seconds);
    row += String.format("<td class='ignore'>{0}</td>", item.backoff_jitter_percent);

    row += String.format("<td class='ignore'>{0}</td>", item.circuit_breaker_threshold_percent);
    row += String.format("<td class='ignore'>{0}</td>", item.circuit_breaker_window_seconds);
    row += String.format("<td class='ignore'>{0}</td>", item.circuit_breaker_reset_seconds);

    row += String.format("<td class='ignore'>{0}</td>", item.tls_cert_path);
    row += String.format("<td class='ignore'>{0}</td>", item.tls_key_path);
    row += String.format("<td class='ignore'>{0}</td>", item.tls_ca_path);

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
