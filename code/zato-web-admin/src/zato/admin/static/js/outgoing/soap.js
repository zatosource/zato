
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.OutgoingSOAP = new Class({
    toString: function() {
        var s = '<OutgoingSOAP id:{0} name:{1} is_active:{2}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.is_active ? this.is_active : '(none)');
    }
});

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.OutgoingSOAP;
    $.fn.zato.data_table.new_row_func = $.fn.zato.outgoing.soap.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms([
        'name',
        'host',
        'timeout',
        'ping_method',
    ]);

    $.fn.zato.data_table.before_submit_hook = $.fn.zato.outgoing.soap.before_submit_hook;

    // .. removing a body-credential mapping row ..
    $(document).on('click', '.body-credential-remove', function() {
        $(this).closest('.body-credential-row').remove();
        return false;
    });

    // .. removing a request parameter row ..
    $(document).on('click', '.request-param-remove', function() {
        $(this).closest('.request-param-row').remove();
        return false;
    });

    // .. attach date-time pickers to the scheduler start date fields in both popups ..
    var picker_ids = ['#id_scheduler_start_date', '#id_edit-scheduler_start_date'];
    $.each(picker_ids, function(ignored, picker_id) {
        $(picker_id).datetimepicker(
            {
                'dateFormat':$('#js_date_format').val(),
                'timeFormat':$('#js_time_format').val(),
                'ampm':$.fn.zato.to_bool($('#js_ampm').val()),
            }
        );
    });

    // .. and show the callback widget matching the callback type selected ..
    $.each(['create', 'edit'], function(ignored, action) {
        var suffix = action === 'edit' ? 'edit-' : '';
        $('#id_' + suffix + 'callback_type').change(function() {
            $.fn.zato.outgoing.soap.toggle_callback(action);
        });
        $.fn.zato.outgoing.soap.toggle_callback(action);
    });

    // .. the health check tab manages its own callback widgets the same way.
    $.fn.zato.health_check.init();

    var unique_constraints = [
        {field: 'name', entity_type: 'outgoing_soap', attr_name: 'name'},
    ];
    $.each(unique_constraints, function(i, c) {
        $.fn.zato.validate_unique('#id_' + c.field, c.entity_type, c.attr_name);
        $.fn.zato.validate_unique('#id_edit-' + c.field, c.entity_type, c.attr_name);
    });
})

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.soap.tab_labels = {
    main:         'Main',
    soap:         'SOAP',
    security:     'Security',
    credentials:  'Body credentials',
    scheduler:    'Scheduler',
    request:      'Request',
    response:     'Response',
    callback:     'Callback',
    health_check: 'Health check',
    more:         'More'
};

$.fn.zato.outgoing.soap._reset_tabs = function(action) {
    var is_edit = action === 'edit';
    $.fn.zato.form_tabs.reset({
        div_id:       is_edit ? '#edit-div' : '#create-div',
        panel_prefix: is_edit ? 'out-soap-edit-tab-panel-' : 'out-soap-create-tab-panel-',
        default_tab:  'main',
        tab_labels:   $.fn.zato.outgoing.soap.tab_labels
    });
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Request parameter rows - each row is a key, a value and the value's Text/JSONata mode,
// serialized to the form's hidden JSON fields before the form is submitted.
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.soap.param_kinds = ['message', 'soap_headers'];

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.soap.add_param_row = function(action, kind, key, value, mode) {

    var row = $('<tr class="request-param-row"></tr>');

    var jsonata_cell = $('<td class="request-param-jsonata-cell"></td>');
    var jsonata_checkbox = $('<input type="checkbox" class="request-param-jsonata" title="Evaluate the value as JSONata">');
    if(mode === 'jsonata') {
        jsonata_checkbox.prop('checked', true);
    }
    jsonata_cell.append(jsonata_checkbox);

    var key_cell = $('<td class="request-param-key-cell"></td>');
    var key_input = $('<input type="text" class="request-param-key" placeholder="Name">');
    if(key) {
        key_input.val(key);
    }
    key_cell.append(key_input);

    var value_cell = $('<td class="request-param-value-cell"></td>');
    var value_input = $('<input type="text" class="request-param-value" placeholder="Value">');
    if(value) {
        value_input.val(value);
    }
    value_cell.append(value_input);

    var remove_cell = $('<td class="request-param-remove-cell"></td>');
    var remove_link = $('<a href="javascript:void(0)" class="request-param-remove" title="Remove" aria-label="Remove">x</a>');
    remove_cell.append(remove_link);

    row.append(jsonata_cell);
    row.append(key_cell);
    row.append(value_cell);
    row.append(remove_cell);

    $('#request-' + kind + '-rows-' + action).append(row);

    // A newly added row is ready to be typed into right away
    key_input.focus();
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.soap._param_rows_field = function(action, kind) {
    var suffix = action === 'edit' ? 'edit-' : '';
    return '#id_' + suffix + 'request_' + kind;
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.soap.populate_param_rows = function(action) {

    $.each($.fn.zato.outgoing.soap.param_kinds, function(ignored, kind) {

        var container = $('#request-' + kind + '-rows-' + action);
        container.empty();

        var value = $($.fn.zato.outgoing.soap._param_rows_field(action, kind)).val();
        if(!value) {
            return;
        }

        var items = [];
        try {
            items = JSON.parse(value);
        }
        catch(e) {
            return;
        }

        for(var idx = 0; idx < items.length; idx++) {
            $.fn.zato.outgoing.soap.add_param_row(action, kind, items[idx].key, items[idx].value, items[idx].mode);
        }
    });
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.soap.serialize_param_rows = function(action) {

    $.each($.fn.zato.outgoing.soap.param_kinds, function(ignored, kind) {

        var out = [];

        $('#request-' + kind + '-rows-' + action).find('.request-param-row').each(function() {
            var key = $(this).find('.request-param-key').val().trim();
            if(!key) {
                return;
            }
            var is_jsonata = $(this).find('.request-param-jsonata').prop('checked');
            out.push({
                key: key,
                value: $(this).find('.request-param-value').val(),
                mode: is_jsonata ? 'jsonata' : 'text'
            });
        });

        $($.fn.zato.outgoing.soap._param_rows_field(action, kind)).val(out.length ? JSON.stringify(out) : '');
    });
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.soap.toggle_callback = function(action) {

    var suffix = action === 'edit' ? 'edit-' : '';
    var callback_type = $('#id_' + suffix + 'callback_type').val();

    // Show only the callback widget matching the type selected, hiding its siblings.
    var callback_rows = {
        'service': $('#callback-service-row-' + action),
        'topic':   $('#callback-topic-row-' + action),
        'rest':    $('#callback-rest-row-' + action)
    };

    $.each(callback_rows, function(row_type, row) {
        row.toggleClass('hidden', row_type !== callback_type);
    });
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Body-credential mapping rows
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.soap.add_body_credential_row = function(action, name, position) {

    var row = $('<div class="body-credential-row" style="margin-bottom:4px"></div>');

    var name_input = $('<input type="text" class="body-credential-name" placeholder="Element name" style="width:40%">');
    if(name) {
        name_input.val(name);
    }

    var position_input = $('<input type="number" class="body-credential-position" placeholder="Position" min="1" style="width:15%">');
    if(position) {
        position_input.val(position);
    }

    var remove_link = $('<a href="javascript:void(0)" class="body-credential-remove">Remove</a>');

    row.append(name_input);
    row.append('&nbsp;');
    row.append(position_input);
    row.append('&nbsp;');
    row.append(remove_link);

    $('#body-credentials-' + action).append(row);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.soap._body_credentials_field = function(action) {
    return action === 'edit' ? '#id_edit-body_credentials' : '#id_body_credentials';
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.soap._populate_body_credential_rows = function(action) {

    var container = $('#body-credentials-' + action);
    container.empty();

    var value = $($.fn.zato.outgoing.soap._body_credentials_field(action)).val();
    if(!value) {
        return;
    }

    var items = [];
    try {
        items = JSON.parse(value);
    }
    catch(e) {
        return;
    }

    for(var idx = 0; idx < items.length; idx++) {
        $.fn.zato.outgoing.soap.add_body_credential_row(action, items[idx].name, items[idx].position);
    }
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.soap.before_submit_hook = function(form) {

    var is_edit = $(form).attr('id') === 'edit-form';
    var action = is_edit ? 'edit' : 'create';

    var out = [];

    $('#body-credentials-' + action).find('.body-credential-row').each(function() {
        var name = ($(this).find('.body-credential-name').val() || '').trim();
        if(!name) {
            return;
        }
        var elem = {name: name};
        var position = $(this).find('.body-credential-position').val();
        if(position) {
            elem.position = parseInt(position, 10);
        }
        out.push(elem);
    });

    $($.fn.zato.outgoing.soap._body_credentials_field(action)).val(out.length ? JSON.stringify(out) : '');

    // The message and SOAP header rows are serialized to their hidden JSON fields the same way
    $.fn.zato.outgoing.soap.serialize_param_rows(action);

    return true;
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.soap.create = function() {
    $.fn.zato.outgoing.soap._reset_tabs('create');
    $.fn.zato.data_table._create_edit('create', 'Create a new outgoing SOAP connection', null);
    $.fn.zato.outgoing.soap._populate_body_credential_rows('create');
    $.fn.zato.outgoing.soap.populate_param_rows('create');
    $.fn.zato.outgoing.soap.toggle_callback('create');
    $.fn.zato.how_it_works.init({
        badgeId: 'create-how-it-works',
        divId: '#create-div',
        descriptions: $.extend({},
            $.fn.zato.outgoing.soap.field_descriptions,
            $.fn.zato.health_check.field_descriptions)
    });
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.soap.field_descriptions = {

    // Main tab
    'id_name': 'A unique name for this connection.<br>Used to identify it in logs and the dashboard.',
    'id_is_active': 'Whether this connection can be used.<br>Messages are not sent through<br>inactive connections.',
    'id_is_audit_log_active': 'Whether this connection\'s traffic is recorded<br>in the audit log. On by default.',
    'id_host': 'Address of the remote SOAP server,<br>e.g. https://example.com:8443.',
    'id_url_path': 'URL path of the SOAP endpoint<br>on the remote server,<br>e.g. /services/endpoint.',
    'id_soap_action': 'Value of the SOAPAction header<br>sent with each request. Leave empty<br>if the endpoint does not require one.',
    'id_timeout': 'How many seconds to wait for a response<br>before the invocation times out.',

    // SOAP tab
    'id_soap_version': 'SOAP protocol version the endpoint expects.<br>1.2 is the most common choice today,<br>1.1 is used by older systems.',
    'id_use_ws_addressing': 'When on, WS-Addressing headers - Action,<br>MessageID, To and ReplyTo - are added<br>to each outgoing message.',
    'id_use_mtom': 'When on, binary attachments are sent<br>as MTOM/XOP parts instead of being<br>embedded in the message as Base64.',

    // Security tab
    'id_security_id': 'Security definition applied to outgoing messages,<br>e.g. WS-Security, Basic Auth<br>or an OAuth bearer token.',
    'id_validate_tls': 'Whether the TLS certificate of the remote<br>server must be validated. Turn it off<br>only in test environments.',
    'id_tls_client_cert': 'Path to a PEM file with the client certificate<br>this connection presents to mutual-TLS endpoints.<br>The file is mounted into the container and may<br>hold both the certificate and its private key.',
    'id_tls_client_key': 'Path to the private key matching the client<br>certificate, if it lives in its own PEM file.<br>Leave empty when the certificate file<br>already contains the key.',

    // Body credentials tab
    'id_body_credentials': 'Credentials from the security definition injected<br>into the message body, for endpoints that expect<br>them there rather than in a header.<br>Each mapping is an element name with an optional<br>position among the body\'s child elements.',

    // More tab
    'id_ping_method': 'HTTP method used when pinging<br>the connection, e.g. HEAD or GET.',
    'id_content_type': 'Overrides the default Content-Type header.<br>Leave empty to use the default matching<br>the SOAP version selected.',

    // Scheduler tab
    'id_scheduler_run_every': 'How often this connection is invoked,<br>e.g. every 6 hours.<br>Leave empty for no scheduled invocations.',
    'id_scheduler_start_date': 'When the first scheduled invocation takes place,<br>entered in your own timezone.',

    // Request tab
    'id_request_operation': 'The operation every invocation calls,<br>e.g. GetItemDetails.<br>Empty means the caller names it explicitly.',
    'id_request_message': 'Elements of the message each invocation sends.<br>Names may use dot-paths, e.g. <code>order.customer_id</code>.<br>A value is sent exactly as typed unless its JSONata toggle<br>is on, then it is evaluated each time the request fires.',
    'id_request_message_map': 'A single JSONata expression that builds<br>the whole message instead of the rows above, e.g.<br><code>{"since": $substring($now(), 0, 10)}</code>',
    'id_request_soap_headers': 'Custom elements injected into the soap:Header<br>of every envelope. A value is sent exactly as typed<br>unless its JSONata toggle is on.',
    'id_wsa_action': 'The WS-Addressing Action header<br>sent with every envelope.',
    'id_wsa_to': 'The WS-Addressing To header<br>sent with every envelope.',
    'id_wsa_reply_to': 'The WS-Addressing ReplyTo header<br>sent with every envelope.',

    // Response tab
    'id_response_map_mode': 'Whether the response map below is JSONata,<br>applied to the parsed response,<br>or XPath, applied to the raw XML envelope.',
    'id_response_map': 'An expression that reshapes the response<br>before the callback receives it.<br>Leave empty to pass the response through as-is.',

    // Callback tab
    'id_callback_type': 'Where each response is delivered - to a service,<br>a pub/sub topic or an outgoing REST connection.',
    'id_callback_service': 'The service invoked with the response<br>each time the connection is invoked.',
    'id_callback_topic': 'The pub/sub topic the response is published to.',
    'id_callback_rest': 'The outgoing REST connection<br>the response is sent to.',
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.soap.edit = function(id) {
    $.fn.zato.outgoing.soap._reset_tabs('edit');
    $.fn.zato.data_table._create_edit('edit', 'Update the outgoing SOAP connection', id);
    $.fn.zato.outgoing.soap._populate_body_credential_rows('edit');
    $.fn.zato.outgoing.soap.populate_param_rows('edit');

    // The callback name lands in the widget matching the callback type stored
    var item = $.fn.zato.data_table.data[id];
    var callback_type = item.callback_type;
    if(callback_type) {
        var widget_names = {
            'service': '#id_edit-callback_service',
            'topic':   '#id_edit-callback_topic',
            'rest':    '#id_edit-callback_rest'
        };
        $(widget_names[callback_type]).val(item.callback_name);
    }
    $.fn.zato.outgoing.soap.toggle_callback('edit');

    // The health check tab's widgets are populated the same way
    $.fn.zato.health_check.populate('edit', item);

    $.fn.zato.how_it_works.init({
        badgeId: 'edit-how-it-works',
        divId: '#edit-div',
        descriptions: $.extend({},
            $.fn.zato.outgoing.soap.field_descriptions,
            $.fn.zato.health_check.field_descriptions)
    });
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.soap.data_table.new_row = function(item, data, include_tr) {
    let row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    let is_active = item.is_active == true;

    let security_name = '<span class="form_hint">---</span>';
    if(item.security_id && item.security_id != 'ZATO_NONE') {
        security_name = item.security_id_select;
    }

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";

    // 1
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', is_active ? 'Yes' : 'No');

    // 2
    row += String.format('<td>{0}</td>', item.host);
    row += String.format('<td>{0}</td>', item.url_path);

    // 3
    row += String.format('<td>{0}</td>', item.soap_action ? item.soap_action : '');
    row += String.format('<td>{0}</td>', item.soap_version);
    row += String.format('<td>{0}</td>', security_name);

    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:void(0)\" onclick=\"$.fn.zato.data_table.ping('{0}', this)\" class=\"ping-link\">Ping</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.outgoing.soap.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.outgoing.soap.delete_('{0}');\">Delete</a>", item.id));
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);

    row += String.format("<td class='ignore'>{0}</td>", item.is_active);
    row += String.format("<td class='ignore'>{0}</td>", item.security_id);
    row += String.format("<td class='ignore'>{0}</td>", item.validate_tls);

    row += String.format("<td class='ignore'>{0}</td>", item.ping_method);
    row += String.format("<td class='ignore'>{0}</td>", item.timeout);

    row += String.format("<td class='ignore'>{0}</td>", item.content_type ? item.content_type : '');
    row += String.format("<td class='ignore'>{0}</td>", item.serialization_type);

    let to_django_bool = function(value) {
        return (value === true || value == 'on' || value == 'True') ? 'True' : 'False';
    };

    row += String.format("<td class='ignore'>{0}</td>", to_django_bool(item.use_ws_addressing));
    row += String.format("<td class='ignore'>{0}</td>", to_django_bool(item.use_mtom));
    row += String.format("<td class='ignore'>{0}</td>", item.body_credentials ? item.body_credentials : '');
    row += String.format("<td class='ignore'>{0}</td>", item.tls_client_cert ? item.tls_client_cert : '');
    row += String.format("<td class='ignore'>{0}</td>", item.tls_client_key ? item.tls_client_key : '');

    // After a submit the instance carries the callback widgets rather than the resolved name,
    // so the name is derived from the widget matching the callback type selected.
    if(!item.callback_name && item.callback_type) {
        item.callback_name = item['callback_' + item.callback_type];
    }
    if(!item.health_check_callback_name && item.health_check_callback_type) {
        item.health_check_callback_name = item['health_check_callback_' + item.health_check_callback_type];
    }

    // Declarative invocation and health check fields
    var invocation_fields = [
        'request_operation', 'request_message', 'request_message_map', 'request_soap_headers',
        'wsa_action', 'wsa_to', 'wsa_reply_to',
        'response_map', 'response_map_mode',
        'callback_type', 'callback_name',
        'scheduler_run_every', 'scheduler_run_unit', 'scheduler_start_date', 'scheduler_job_id',
        'health_check_run_every', 'health_check_run_unit', 'health_check_notify_on',
        'health_check_job_id', 'health_check_callback_type', 'health_check_callback_name'
    ];
    $.each(invocation_fields, function(ignored, name) {
        row += String.format("<td class='ignore'>{0}</td>", item[name] ? item[name] : '');
    });

    row += String.format("<td class='ignore'>{0}</td>", to_django_bool(item.is_audit_log_active));

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.soap.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Outgoing SOAP connection `{0}` deleted',
        'Are you sure you want to delete outgoing SOAP connection `{0}`?',
        true);
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
