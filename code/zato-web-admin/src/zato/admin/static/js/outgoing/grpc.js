
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.GRPCOutconn = new Class({
    toString: function() {
        var description = '<GRPCOutconn id:{0} name:{1} is_active:{2}>';

        var out = String.format(description,
            this.id ? this.id : '(none)',
            this.name ? this.name : '(none)',
            this.is_active ? this.is_active : '(none)');

        return out;
    }
});

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.GRPCOutconn;
    $.fn.zato.data_table.new_row_func = $.fn.zato.outgoing.grpc.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms([
        'name',
        'address',
        'security_id',
    ]);
    // Generic connection names are unique per connection type,
    // so the check is scoped to this page's own type.
    var uniqueConstraints = [
        {field: 'name', entity_type: 'generic_connection', attr_name: 'name',
            filter_name: 'type_', filter_value: 'outconn-grpc'}
    ];
    $.each(uniqueConstraints, function(constraintIndex, constraint) {
        $.fn.zato.validate_unique('#id_' + constraint.field, constraint.entity_type, constraint.attr_name, constraint);
        $.fn.zato.validate_unique('#id_edit-' + constraint.field, constraint.entity_type, constraint.attr_name, constraint);
    });
})

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.grpc.field_descriptions = {
    'id_name': 'A unique name for this gRPC connection.<br>Used to identify it in logs and the dashboard.',
    'id_is_active': 'Whether this connection is active.<br>Inactive connections cannot be used by services.',
    'id_address': 'Host and port of the gRPC server,<br>e.g. billing.example.com:50051.',
    'id_security_id': 'Security definition whose credentials are sent<br>as call metadata with each request.',
    'id_is_tls': 'Whether to connect over TLS.<br>Uncheck only for servers that require plaintext.',
    'id_tls_ca_certs_file': 'Path to a PEM file with CA certificates<br>to verify the server\'s certificate against.',
    'id_proto_path': 'Path to a .proto file on the server.<br>Client code is generated out of it automatically.',
    'id_stub_module': 'Alternatively, the Python module with your own<br>pre-generated stub, e.g. billing_pb2_grpc, and optionally the stub class in it.',
    'id_ping_timeout': 'How many seconds to wait for the server<br>when pinging the connection.',
    'id_max_send_message_size': 'The biggest message that can be sent<br>or received, in bytes.',
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.grpc.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new gRPC connection', null);
    $.fn.zato.how_it_works.init({
        badgeId: 'create-how-it-works',
        divId: '#create-div',
        descriptions: $.fn.zato.outgoing.grpc.field_descriptions
    });
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.grpc.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the gRPC connection', id);
    $.fn.zato.how_it_works.init({
        badgeId: 'edit-how-it-works',
        divId: '#edit-div',
        descriptions: $.fn.zato.outgoing.grpc.field_descriptions
    });
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.grpc.data_table.new_row = function(item, data, includeTR) {
    let row = '';

    if(includeTR) {
        row += String.format('<tr id=\'tr_{0}\' class=\'updated\'>', item.id);
    }

    let isActive = item.is_active == true;

    var securityCell = '<span class="form_hint">---</span>';
    var securityType = '';

    var selectedValue = $('#id_security_id').val();
    if (!selectedValue) {
        selectedValue = $('#id_edit-security_id').val();
    }

    if(item.security_id) {
        if (selectedValue) {
            if (selectedValue.indexOf('/') > -1) {

                var selectedParts = selectedValue.split('/');
                securityType = selectedParts[0];

                var securityName = '';
                if (item.security_id_select) {
                    var selectParts = item.security_id_select.split('/');
                    var nameParts = selectParts.slice(1);
                    securityName = nameParts.join('/');
                }

                var securityHref = '/zato/security/';
                if(securityType === 'oauth') {
                    securityHref += 'oauth/outconn/client-credentials/';
                }
                else if(securityType === 'basic_auth') {
                    securityHref += 'basic-auth/';
                }
                else if(securityType === 'apikey') {
                    securityHref += 'apikey/';
                }
                securityHref += '?cluster=1&query=' + encodeURIComponent(securityName);
                securityCell = String.format('<a href=\'{0}\'>{1}</a>', securityHref, securityName);
            }
        }
    }

    var downloadCell = '<span class="form_hint">---</span>';
    if(item.proto_path) {
        downloadCell = String.format('<a href=\'/zato/outgoing/grpc/download-stubs/{0}/\'>Stubs</a>', item.id);
    }

    row += '<td class=\'numbering\'>&nbsp;</td>';
    row += '<td class=\'impexp\'><input type=\'checkbox\' /></td>';

    // 1
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', isActive ? 'Yes' : 'No');
    row += String.format('<td>{0}</td>', item.address);

    // 2
    row += String.format('<td>{0}</td>', securityCell);

    // 3
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.outgoing.grpc.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.outgoing.grpc.delete_('{0}');\">Delete</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:void(0)\" onclick=\"$.fn.zato.data_table.ping('{0}', this)\">Ping</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.outgoing.grpc.invoke('{0}')\">Invoke</a>", item.id));
    row += String.format('<td>{0}</td>', downloadCell);

    // 4
    row += String.format('<td class=\'ignore item_id_{0}\'>{0}</td>', item.id);
    row += String.format('<td class=\'ignore\'>{0}</td>', item.is_active);
    row += String.format('<td class=\'ignore\'>{0}</td>', item.is_tls);
    row += String.format('<td class=\'ignore\'>{0}</td>', item.tls_ca_certs_file);
    row += String.format('<td class=\'ignore\'>{0}</td>', item.proto_path);
    row += String.format('<td class=\'ignore\'>{0}</td>', item.stub_module);
    row += String.format('<td class=\'ignore\'>{0}</td>', item.stub_class);
    row += String.format('<td class=\'ignore\'>{0}</td>', item.ping_timeout);
    row += String.format('<td class=\'ignore\'>{0}</td>', item.max_send_message_size);
    row += String.format('<td class=\'ignore\'>{0}</td>', item.max_recv_message_size);
    row += String.format('<td class=\'ignore\'>{0}</td>', item.security_id);
    row += String.format('<td class=\'ignore\'>{0}</td>', securityType);

    if(includeTR) {
        row += '</tr>';
    }

    return row;
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.grpc.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'gRPC connection `{0}` deleted',
        'Are you sure you want to delete gRPC connection `{0}`?',
        true);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.grpc.get_invoke_url = function(id) {

    var out = '/zato/outgoing/grpc/invoke/' + id + '/';
    return out;
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.grpc.invoke = function(id) {
    var item = $.fn.zato.data_table.data[id];
    if (!item) {
        return;
    }

    var historyKey = 'zato.invoke-history.outconn-grpc.' + id;

    $.fn.zato.invoker.open_overlay({
        id: id,
        name: item.name,
        connection: 'outconn-grpc',
        history_key: historyKey,
        highlight_lexer: 'json',
        get_invoke_url_func: $.fn.zato.outgoing.grpc.get_invoke_url,
        collect_form_data_func: $.fn.zato.outgoing.grpc.collect_form_data
    });

    $.fn.zato.invoker._request_ace_mode = 'ace/mode/json';

    var pane = $.fn.zato.invoker._request_pane;
    if (pane) {
        if (!pane.getValue()) {
            $.fn.zato.invoker._set_request_value('{}');
        }
        else {
            pane.getEditor().session.setMode('ace/mode/json');
        }
    }

    $('#invoker-more-options').html(
        '<div class="invoker-more-options-row invoker-more-options-row-compact">'
        + '<label>Method</label>'
        + '<input type="text" id="invoker-modal-method" placeholder="e.g. GetInvoice" />'
        + '</div>'
    );

    var saved = $.fn.zato.invoker._load_overlay_state(historyKey);
    if (saved.method) {
        $('#invoker-modal-method').val(saved.method);
    }
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.grpc.collect_form_data = function() {
    var requestValue = '';
    if ($.fn.zato.invoker._request_pane) {
        requestValue = $.fn.zato.invoker._request_pane.getValue();
    }

    return {
        'data-request': requestValue,
        'method': $('#invoker-modal-method').val(),
    };
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Live form updates registration
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.live_form_updates.register('create', [
    {object_type: 'security', target_select: '#id_security_id'}
]);

$.fn.zato.live_form_updates.register('edit', [
    {object_type: 'security', target_select: '#id_edit-security_id'}
]);

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
