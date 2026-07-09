
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.IBMMQChannel = new Class({
    toString: function() {
        var s = '<IBMMQChannel id:{0} name:{1} is_active:{2}';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.is_active ? this.is_active : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = false;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.IBMMQChannel;
    $.fn.zato.data_table.new_row_func = $.fn.zato.channel.ibm_mq.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'address', 'queue_manager', 'mq_channel_name', 'queue', 'service']);
    var unique_constraints = [
        {field: 'name', entity_type: 'generic_connection', attr_name: 'name'}
    ];
    $.each(unique_constraints, function(i, c) {
        $.fn.zato.validate_unique('#id_' + c.field, c.entity_type, c.attr_name);
        $.fn.zato.validate_unique('#id_edit-' + c.field, c.entity_type, c.attr_name);
    });
})

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.ibm_mq.tab_labels = {
    basic:    'Basic',
    security: 'Security',
    more:     'More options'
};

$.fn.zato.channel.ibm_mq._reset_tabs = function(action) {
    var is_edit = action === 'edit';
    $.fn.zato.form_tabs.reset({
        div_id:       is_edit ? '#edit-div' : '#create-div',
        panel_prefix: is_edit ? 'channel-ibm-mq-edit-tab-panel-' : 'channel-ibm-mq-create-tab-panel-',
        default_tab:  'basic',
        tab_labels:   $.fn.zato.channel.ibm_mq.tab_labels
    });
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.ibm_mq.field_descriptions = {

    // Basic tab
    'id_name': 'A unique name for this channel.<br>Used to identify it in logs and the dashboard.',
    'id_is_active': 'Whether this channel consumes messages.<br>Inactive channels leave their queue untouched.',
    'id_address': 'Address of the queue manager as host:port,<br>e.g. localhost:1414.',
    'id_queue_manager': 'Name of the queue manager to connect to,<br>e.g. QM1.',
    'id_mq_channel_name': 'Name of the server-connection (SVRCONN) channel<br>the connection goes through,<br>e.g. DEV.APP.SVRCONN.',
    'id_queue': 'Queue to consume messages from,<br>e.g. DEV.QUEUE.1. Each message on this queue<br>invokes the service below.',
    'id_service': 'Service invoked for each message taken<br>off the queue. The message body is in<br>self.request.payload and MQMD and MQRFH2 headers<br>are in self.request.headers.',

    // Security tab
    'id_username': 'Username the connection authenticates with.<br>Leave empty if the queue manager<br>does not require credentials.<br>The password is set separately<br>with the Change password link.',
    'id_ssl': 'Whether the connection uses TLS.<br>When on, the cipher spec and certificate<br>files below apply.',
    'id_cipher_spec': 'TLS cipher specification the SVRCONN channel<br>requires, e.g. ANY_TLS12_OR_HIGHER<br>or TLS_AES_256_GCM_SHA384.',
    'id_ssl_ca_file': 'Path to a PEM file with the CA certificate<br>that signed the queue manager\'s certificate.',
    'id_ssl_cert_file': 'Path to a PEM file with the client certificate,<br>needed only when the queue manager<br>requires mutual TLS.',
    'id_ssl_key_file': 'Path to the PEM private key matching<br>the client certificate.',

    // More options tab
    'id_remove_jms_headers': 'When on, MQRFH2 (JMS) headers are stripped<br>from the message body before the service<br>runs, so self.request.payload is the bare body.<br>The headers are still available<br>in self.request.headers either way.',
};

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.ibm_mq.create = function() {
    $.fn.zato.channel.ibm_mq._reset_tabs('create');
    $.fn.zato.data_table._create_edit('create', 'Create a new IBM MQ channel', null);
    $.fn.zato.how_it_works.init({
        badgeId: 'create-how-it-works',
        divId: '#create-div',
        descriptions: $.fn.zato.channel.ibm_mq.field_descriptions
    });
}

$.fn.zato.channel.ibm_mq.edit = function(id) {
    $.fn.zato.channel.ibm_mq._reset_tabs('edit');
    $.fn.zato.data_table._create_edit('edit', 'Update the IBM MQ channel', id);
    $.fn.zato.how_it_works.init({
        badgeId: 'edit-how-it-works',
        divId: '#edit-div',
        descriptions: $.fn.zato.channel.ibm_mq.field_descriptions
    });
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.ibm_mq.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var is_active = item.is_active == true;
    var ssl = item.ssl == true;
    var remove_jms_headers = item.remove_jms_headers == true;

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";

    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', is_active ? 'Yes' : 'No');
    row += String.format('<td>{0}</td>', item.address);
    row += String.format('<td>{0}</td>', item.queue_manager);
    row += String.format('<td>{0}</td>', item.queue);
    row += String.format('<td>{0}</td>', item.service);

    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.data_table.change_password('{0}')\">Change password</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.channel.ibm_mq.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.channel.ibm_mq.delete_('{0}');\">Delete</a>", item.id));

    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", is_active);
    row += String.format("<td class='ignore'>{0}</td>", item.mq_channel_name);
    row += String.format("<td class='ignore'>{0}</td>", item.username);
    row += String.format("<td class='ignore'>{0}</td>", ssl);
    row += String.format("<td class='ignore'>{0}</td>", item.cipher_spec);
    row += String.format("<td class='ignore'>{0}</td>", item.ssl_ca_file);
    row += String.format("<td class='ignore'>{0}</td>", item.ssl_cert_file);
    row += String.format("<td class='ignore'>{0}</td>", item.ssl_key_file);
    row += String.format("<td class='ignore'>{0}</td>", remove_jms_headers);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.ibm_mq.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'IBM MQ channel `{0}` deleted',
        'Are you sure you want to delete IBM MQ channel `{0}`?',
        true);
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.ibm_mq.import_demo_config = function() {
    var cluster_id = '1';
    var import_url = '/zato/channel/ibm-mq/import-demo-config?cluster=' + cluster_id;

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
