
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.IBMMQOutconn = new Class({
    toString: function() {
        var s = '<IBMMQOutconn id:{0} name:{1} is_active:{2}';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.is_active ? this.is_active : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = false;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.IBMMQOutconn;
    $.fn.zato.data_table.new_row_func = $.fn.zato.outgoing.ibm_mq.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'address', 'queue_manager', 'mq_channel_name', 'queue']);
    var unique_constraints = [
        {field: 'name', entity_type: 'generic_connection', attr_name: 'name'}
    ];
    $.each(unique_constraints, function(i, c) {
        $.fn.zato.validate_unique('#id_' + c.field, c.entity_type, c.attr_name);
        $.fn.zato.validate_unique('#id_edit-' + c.field, c.entity_type, c.attr_name);
    });
})

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.ibm_mq.tab_labels = {
    basic:    'Basic',
    security: 'Security'
};

$.fn.zato.outgoing.ibm_mq._reset_tabs = function(action) {
    var is_edit = action === 'edit';
    $.fn.zato.form_tabs.reset({
        div_id:       is_edit ? '#edit-div' : '#create-div',
        panel_prefix: is_edit ? 'out-ibm-mq-edit-tab-panel-' : 'out-ibm-mq-create-tab-panel-',
        default_tab:  'basic',
        tab_labels:   $.fn.zato.outgoing.ibm_mq.tab_labels
    });
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.ibm_mq.field_descriptions = {

    // Basic tab
    'id_name': 'A unique name for this connection.<br>Services send messages through it<br>with self.ibm_mq[name].send(data).',
    'id_is_active': 'Whether this connection can be used.<br>Messages are not sent through<br>inactive connections.',
    'id_address': 'Address of the queue manager as host:port,<br>e.g. localhost:1414.',
    'id_queue_manager': 'Name of the queue manager to connect to,<br>e.g. QM1.',
    'id_mq_channel_name': 'Name of the server-connection (SVRCONN) channel<br>the connection goes through,<br>e.g. DEV.APP.SVRCONN.',
    'id_queue': 'Queue that messages are sent to,<br>e.g. DEV.QUEUE.1.',

    // Security tab
    'id_username': 'Username the connection authenticates with.<br>Leave empty if the queue manager<br>does not require credentials.<br>The password is set separately<br>with the Change password link.',
    'id_ssl': 'Whether the connection uses TLS.<br>When on, the cipher spec and certificate<br>files below apply.',
    'id_cipher_spec': 'TLS cipher specification the SVRCONN channel<br>requires, e.g. ANY_TLS12_OR_HIGHER<br>or TLS_AES_256_GCM_SHA384.',
    'id_ssl_ca_file': 'Path to a PEM file with the CA certificate<br>that signed the queue manager\'s certificate.',
    'id_ssl_cert_file': 'Path to a PEM file with the client certificate,<br>needed only when the queue manager<br>requires mutual TLS.',
    'id_ssl_key_file': 'Path to the PEM private key matching<br>the client certificate.',
};

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.ibm_mq.create = function() {
    $.fn.zato.outgoing.ibm_mq._reset_tabs('create');
    $.fn.zato.data_table._create_edit('create', 'Create a new outgoing IBM MQ connection', null);
    $.fn.zato.how_it_works.init({
        badgeId: 'create-how-it-works',
        divId: '#create-div',
        descriptions: $.fn.zato.outgoing.ibm_mq.field_descriptions
    });
}

$.fn.zato.outgoing.ibm_mq.edit = function(id) {
    $.fn.zato.outgoing.ibm_mq._reset_tabs('edit');
    $.fn.zato.data_table._create_edit('edit', 'Update the outgoing IBM MQ connection', id);
    $.fn.zato.how_it_works.init({
        badgeId: 'edit-how-it-works',
        divId: '#edit-div',
        descriptions: $.fn.zato.outgoing.ibm_mq.field_descriptions
    });
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.ibm_mq.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var is_active = item.is_active == true;
    var ssl = item.ssl == true;

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";

    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', is_active ? 'Yes' : 'No');
    row += String.format('<td>{0}</td>', item.address);
    row += String.format('<td>{0}</td>', item.queue_manager);
    row += String.format('<td>{0}</td>', item.queue);

    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.data_table.change_password('{0}')\">Change password</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.outgoing.ibm_mq.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.outgoing.ibm_mq.delete_('{0}');\">Delete</a>", item.id));

    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", is_active);
    row += String.format("<td class='ignore'>{0}</td>", item.mq_channel_name);
    row += String.format("<td class='ignore'>{0}</td>", item.username);
    row += String.format("<td class='ignore'>{0}</td>", ssl);
    row += String.format("<td class='ignore'>{0}</td>", item.cipher_spec);
    row += String.format("<td class='ignore'>{0}</td>", item.ssl_ca_file);
    row += String.format("<td class='ignore'>{0}</td>", item.ssl_cert_file);
    row += String.format("<td class='ignore'>{0}</td>", item.ssl_key_file);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.ibm_mq.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Outgoing IBM MQ connection `{0}` deleted',
        'Are you sure you want to delete outgoing IBM MQ connection `{0}`?',
        true);
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.ibm_mq.import_demo_config = function() {
    var cluster_id = '1';
    var import_url = '/zato/outgoing/ibm-mq/import-demo-config?cluster=' + cluster_id;

    var spinner_html = '<div id="import-spinner" style="position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background: white; padding: 20px; border: 2px solid #ccc; border-radius: 5px; z-index: 9999;"><div style="display: inline-block; width: 16px; height: 16px; border: 2px solid #ccc; border-top: 2px solid #333; border-radius: 50%; animation: spin 1s linear infinite; margin-right: 8px; vertical-align: middle;"></div>Importing ...</div><style>@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }</style>';
    $('body').append(spinner_html);

    $.ajax({
        url: import_url,
        method: 'GET',
        success: function() {
            $('#import-spinner').remove();
            window.location.reload();
        },
        error: function() {
            $('#import-spinner').remove();
            alert('Import failed. Check server logs.');
        }
    });
}
