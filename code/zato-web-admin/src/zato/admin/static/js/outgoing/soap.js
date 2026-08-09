
// ////////////////////////////////////////////////////////////////////////////
// Outgoing SOAP connections
// ////////////////////////////////////////////////////////////////////////////

(function($) {

    $.fn.zato.outgoing.soap.config = {

        // The default 40em dialog is too narrow for all the tabs this screen has.
        dialogWidth: '55em',

        // What a cell shows for a field that was never set.
        emptyCellValue: '',

        // What the debug string calls the same absence, where an empty run of characters would
        // read as though the field were missing from the string rather than from the object.
        missingValueLabel: '(none)',

        // The two ways a request parameter's value is read - as typed, or as an expression
        // evaluated each time the request fires.
        textMode: 'text',
        jsonataMode: 'jsonata',

        // The tab the create and edit dialogs open on.
        defaultTab: 'main',

        tabLabels: {
            main:         'Main',
            soap:         'SOAP',
            security:     'Security',
            credentials:  'Body credentials',
            scheduler:    'Scheduler',
            request:      'Request',
            response:     'Response',
            callback:     'Callback',
            health_check: 'Health check'
        },

        // The two kinds of request parameter rows, each with a hidden JSON field of its own.
        paramKinds: ['message', 'soap_headers']
    };

    var config = $.fn.zato.outgoing.soap.config;

    // ////////////////////////////////////////////////////////////////////////

    // An optional field arrives as undefined or null when it was never set, and neither of those
    // is what a reader should be shown. Everything else is read directly.
    function valueOr(value, absent) {

        if(value === undefined) {
            return absent;
        }

        if(value === null) {
            return absent;
        }

        return value;
    }

    // ////////////////////////////////////////////////////////////////////////

    function fieldPrefix(action) {

        if(action === 'edit') {
            return 'edit-';
        }

        return '';
    }

    // ////////////////////////////////////////////////////////////////////////

    // Reads a hidden JSON field into the rows it stands for. A field that was never filled in and
    // one holding something other than JSON both mean there are no rows to build.
    function parseRowsField(selector) {

        var value = $(selector).val();

        if(!value) {
            return [];
        }

        try {
            return JSON.parse(value);
        }
        catch(parseError) {
            return [];
        }
    }

    // ////////////////////////////////////////////////////////////////////////
    // Request parameter rows - each row is a key, a value and the value's Text/JSONata mode,
    // serialized to the form's hidden JSON fields before the form is submitted.
    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.outgoing.soap.add_param_row = function(action, kind, key, value, mode) {

        var row = $('<tr class="request-param-row"></tr>');

        var jsonataCell = $('<td class="request-param-jsonata-cell"></td>');
        var jsonataCheckbox = $('<input type="checkbox" class="request-param-jsonata" title="Evaluate the value as JSONata">');

        if(mode === config.jsonataMode) {
            jsonataCheckbox.prop('checked', true);
        }

        jsonataCell.append(jsonataCheckbox);

        var keyCell = $('<td class="request-param-key-cell"></td>');
        var keyInput = $('<input type="text" class="request-param-key" placeholder="Name">');

        if(key) {
            keyInput.val(key);
        }

        keyCell.append(keyInput);

        var valueCell = $('<td class="request-param-value-cell"></td>');
        var valueInput = $('<input type="text" class="request-param-value" placeholder="Value">');

        if(value) {
            valueInput.val(value);
        }

        valueCell.append(valueInput);

        var removeCell = $('<td class="request-param-remove-cell"></td>');
        var removeLink = $('<a href="javascript:void(0)" class="request-param-remove" title="Remove" aria-label="Remove"></a>');
        removeLink.append($.fn.zato.new_remove_icon());
        removeCell.append(removeLink);

        row.append(jsonataCell);
        row.append(keyCell);
        row.append(valueCell);
        row.append(removeCell);

        $('#request-' + kind + '-rows-' + action).append(row);

        // A newly added row is ready to be typed into right away
        keyInput.focus();
    };

    // ////////////////////////////////////////////////////////////////////////

    function paramRowsField(action, kind) {
        return '#id_' + fieldPrefix(action) + 'request_' + kind;
    }

    // ////////////////////////////////////////////////////////////////////////

    function populateParamRows(action) {

        $.each(config.paramKinds, function(ignored, kind) {

            var container = $('#request-' + kind + '-rows-' + action);
            container.empty();

            var items = parseRowsField(paramRowsField(action, kind));

            for(var itemIdx = 0; itemIdx < items.length; itemIdx++) {
                var item = items[itemIdx];
                $.fn.zato.outgoing.soap.add_param_row(action, kind, item.key, item.value, item.mode);
            }
        });
    }

    // ////////////////////////////////////////////////////////////////////////

    function serializeParamRows(action) {

        $.each(config.paramKinds, function(ignored, kind) {

            var rows = [];

            $('#request-' + kind + '-rows-' + action).find('.request-param-row').each(function() {

                var row = $(this);
                var key = row.find('.request-param-key').val().trim();

                // A row whose name was left blank is not a parameter at all.
                if(!key) {
                    return;
                }

                var isJsonata = row.find('.request-param-jsonata').prop('checked');
                var mode = config.textMode;

                if(isJsonata) {
                    mode = config.jsonataMode;
                }

                rows.push({
                    key: key,
                    value: row.find('.request-param-value').val(),
                    mode: mode
                });
            });

            // No rows at all is stored as nothing rather than as an empty JSON list, which is what
            // the server side reads as a connection having configured none.
            var stored = '';

            if(rows.length) {
                stored = JSON.stringify(rows);
            }

            $(paramRowsField(action, kind)).val(stored);
        });
    }

    // ////////////////////////////////////////////////////////////////////////
    // Body-credential mapping rows
    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.outgoing.soap.add_body_credential_row = function(action, name, position) {

        var row = $('<div class="body-credential-row"></div>');

        var nameInput = $('<input type="text" class="body-credential-name" placeholder="Element name">');

        if(name) {
            nameInput.val(name);
        }

        var positionInput = $('<input type="number" class="body-credential-position" placeholder="Position" min="1">');

        if(position) {
            positionInput.val(position);
        }

        var removeLink = $('<a href="javascript:void(0)" class="body-credential-remove">Remove</a>');

        row.append(nameInput);
        row.append(positionInput);
        row.append(removeLink);

        $('#body-credentials-' + action).append(row);
    };

    // ////////////////////////////////////////////////////////////////////////

    function bodyCredentialsField(action) {
        return '#id_' + fieldPrefix(action) + 'body_credentials';
    }

    // ////////////////////////////////////////////////////////////////////////

    function populateBodyCredentialRows(action) {

        var container = $('#body-credentials-' + action);
        container.empty();

        var items = parseRowsField(bodyCredentialsField(action));

        for(var itemIdx = 0; itemIdx < items.length; itemIdx++) {
            var item = items[itemIdx];
            $.fn.zato.outgoing.soap.add_body_credential_row(action, item.name, item.position);
        }
    }

    // ////////////////////////////////////////////////////////////////////////

    function serializeBodyCredentialRows(action) {

        var rows = [];

        $('#body-credentials-' + action).find('.body-credential-row').each(function() {

            var row = $(this);
            var name = row.find('.body-credential-name').val().trim();

            // A mapping without an element name names nothing.
            if(!name) {
                return;
            }

            var mapping = {name: name};
            var position = row.find('.body-credential-position').val();

            // A mapping without a position prepends, which is what leaving the field empty means.
            if(position) {
                mapping.position = parseInt(position, 10);
            }

            rows.push(mapping);
        });

        var stored = '';

        if(rows.length) {
            stored = JSON.stringify(rows);
        }

        $(bodyCredentialsField(action)).val(stored);
    }

    // ////////////////////////////////////////////////////////////////////////

    function resetTabs(action) {

        var isEdit = action === 'edit';
        var divId = '#create-div';
        var panelPrefix = 'out-soap-create-tab-panel-';

        if(isEdit) {
            divId = '#edit-div';
            panelPrefix = 'out-soap-edit-tab-panel-';
        }

        $.fn.zato.form_tabs.reset({
            div_id:       divId,
            panel_prefix: panelPrefix,
            default_tab:  config.defaultTab,
            tab_labels:   config.tabLabels
        });
    }

    // ////////////////////////////////////////////////////////////////////////

    function toggleCallback(action) {

        var callbackType = $('#id_' + fieldPrefix(action) + 'callback_type').val();

        // Show only the callback widget matching the type selected, hiding its siblings.
        var callbackRows = {
            'service': $('#callback-service-row-' + action),
            'topic':   $('#callback-topic-row-' + action),
            'rest':    $('#callback-rest-row-' + action)
        };

        $.each(callbackRows, function(rowType, row) {
            row.toggleClass('hidden', rowType !== callbackType);
        });
    }

    // ////////////////////////////////////////////////////////////////////////

    function initHowItWorks(action) {

        $.fn.zato.how_it_works.init({
            badgeId: action + '-how-it-works',
            divId: '#' + action + '-div',
            descriptions: $.extend({},
                $.fn.zato.outgoing.soap.field_descriptions,
                $.fn.zato.health_check.field_descriptions)
        });
    }

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.outgoing.soap.before_submit_hook = function(form) {

        // A saved popup rebuilds its row, so the row's security menu is given anew
        // once the new markup is in the table.
        $.fn.zato.data_table.on_submit_complete_callback = function() {
            $.fn.zato.http_soap.inline.init_security_menus();
        };

        var action = 'create';

        if($(form).attr('id') === 'edit-form') {
            action = 'edit';
        }

        serializeBodyCredentialRows(action);

        // The message and SOAP header rows are serialized to their hidden JSON fields the same way
        serializeParamRows(action);

        return true;
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.outgoing.soap.create = function() {
        resetTabs('create');
        $.fn.zato.data_table._create_edit('create', 'Create a new outgoing SOAP connection', null);
        populateBodyCredentialRows('create');
        populateParamRows('create');
        toggleCallback('create');
        initHowItWorks('create');
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.outgoing.soap.edit = function(id) {

        resetTabs('edit');
        $.fn.zato.data_table._create_edit('edit', 'Update the outgoing SOAP connection', id);
        populateBodyCredentialRows('edit');
        populateParamRows('edit');

        // The callback name lands in the widget matching the callback type stored
        var item = $.fn.zato.data_table.data[id];
        var callbackType = item.callback_type;

        if(callbackType) {

            var widgetNames = {
                'service': '#id_edit-callback_service',
                'topic':   '#id_edit-callback_topic',
                'rest':    '#id_edit-callback_rest'
            };

            $(widgetNames[callbackType]).val(item.callback_name);
        }

        toggleCallback('edit');

        // The health check tab's widgets are populated the same way
        $.fn.zato.health_check.populate('edit', item);

        initHowItWorks('edit');
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.outgoing.soap.delete_ = function(id) {
        $.fn.zato.data_table.delete_(id, 'td.item_id_',
            'Outgoing SOAP connection `{0}` deleted',
            'Are you sure you want to delete outgoing SOAP connection `{0}`?',
            true);
    };

    // ////////////////////////////////////////////////////////////////////////

    // The hidden cells a row carries so that an edit can read a connection's whole configuration
    // back out of the table without going to the server for it.
    var hiddenTextFields = [
        'is_active', 'security_id', 'validate_tls', 'ping_method', 'timeout', 'content_type'
    ];

    var hiddenBooleanFields = [
        'use_ws_addressing', 'use_mtom'
    ];

    var hiddenPathFields = [
        'body_credentials', 'tls_client_cert', 'tls_client_key'
    ];

    // Declarative invocation and health check fields
    var hiddenInvocationFields = [
        'request_operation', 'request_message', 'request_message_map', 'request_soap_headers',
        'wsa_action', 'wsa_to', 'wsa_reply_to',
        'response_map', 'response_map_mode',
        'callback_type', 'callback_name',
        'scheduler_run_every', 'scheduler_run_unit', 'scheduler_start_date', 'scheduler_job_id',
        'health_check_run_every', 'health_check_run_unit', 'health_check_notify_on',
        'health_check_job_id', 'health_check_callback_type', 'health_check_callback_name'
    ];

    var hiddenRetryFields = [
        'max_retries', 'retry_sleep_time', 'retry_backoff_threshold', 'retry_backoff_multiplier'
    ];

    // ////////////////////////////////////////////////////////////////////////

    // Django reads a checkbox back from one of these three spellings, so a value going into a
    // hidden cell is normalised to what a form submit will be able to read.
    function toDjangoBool(value) {

        if($.fn.zato.to_bool(value)) {
            return 'True';
        }

        return 'False';
    }

    // ////////////////////////////////////////////////////////////////////////

    function hiddenCells(item, names) {

        var out = '';

        for(var nameIdx = 0; nameIdx < names.length; nameIdx++) {
            var value = valueOr(item[names[nameIdx]], config.emptyCellValue);
            out += String.format('<td class="ignore">{0}</td>', value);
        }

        return out;
    }

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.outgoing.soap.data_table.new_row = function(item, data, include_tr) {

        var row = '';

        if(include_tr) {
            row += String.format('<tr id="tr_{0}" class="updated">', item.id);
        }

        var isActiveLabel = 'No';

        if($.fn.zato.to_bool(item.is_active)) {
            isActiveLabel = 'Yes';
        }

        // A rebuilt cell keeps the select's own label and an empty href - the canonical
        // name and href come back with the first inline save the cell goes through.
        var securityCell = String.format(
            '<a href="javascript:void(0)" class="http-soap-security-cell" data-id="{0}" data-href="">{1}</a>',
            item.id, $.fn.zato.http_soap.inline.config.empty_security_label);

        if(item.security_id && item.security_id !== 'ZATO_NONE') {
            securityCell = String.format(
                '<a href="javascript:void(0)" class="http-soap-security-cell" data-id="{0}" data-href="">{1}</a>',
                item.id, item.security_id_select);
        }

        row += '<td class="numbering">&nbsp;</td>';
        row += '<td class="impexp"><input type="checkbox" /></td>';

        // 1
        row += String.format(
            '<td><a href="javascript:void(0)" data-id="{0}" onclick="$.fn.zato.http_soap.inline.edit_name(\'{0}\', this)"><span class="name-value">{1}</span></a></td>',
            item.id, item.name);
        row += String.format(
            '<td><a href="javascript:void(0)" data-id="{0}" onclick="$.fn.zato.http_soap.inline.toggle_active(\'{0}\', this)">{1}</a></td>',
            item.id, isActiveLabel);

        // 2
        row += String.format('<td>{0}</td>', item.host);
        row += String.format(
            '<td><a href="javascript:void(0)" data-id="{0}" onclick="$.fn.zato.http_soap.inline.edit_url_path(\'{0}\', this)">{1}</a></td>',
            item.id, item.url_path);

        // 3
        row += String.format('<td>{0}</td>', valueOr(item.soap_action, config.emptyCellValue));
        row += String.format('<td>{0}</td>', item.soap_version);
        row += String.format('<td>{0}</td>', securityCell);

        row += String.format(
            '<td><a href="javascript:void(0)" onclick="$.fn.zato.data_table.ping(\'{0}\', this)" class="ping-link">Ping</a></td>',
            item.id);

        row += String.format('<td><a href="javascript:$.fn.zato.outgoing.soap.edit(\'{0}\')">Edit</a></td>', item.id);
        row += String.format('<td><a href="javascript:$.fn.zato.outgoing.soap.delete_(\'{0}\');">Delete</a></td>', item.id);
        row += String.format('<td class="ignore item_id_{0}">{0}</td>', item.id);

        row += hiddenCells(item, hiddenTextFields);

        for(var booleanIdx = 0; booleanIdx < hiddenBooleanFields.length; booleanIdx++) {
            row += String.format('<td class="ignore">{0}</td>', toDjangoBool(item[hiddenBooleanFields[booleanIdx]]));
        }

        row += hiddenCells(item, hiddenPathFields);

        // After a submit the instance carries the callback widgets rather than the resolved name,
        // so the name is derived from the widget matching the callback type selected.
        if(!item.callback_name && item.callback_type) {
            item.callback_name = item['callback_' + item.callback_type];
        }

        if(!item.health_check_callback_name && item.health_check_callback_type) {
            item.health_check_callback_name = item['health_check_callback_' + item.health_check_callback_type];
        }

        row += hiddenCells(item, hiddenInvocationFields);

        row += String.format('<td class="ignore">{0}</td>', toDjangoBool(item.is_audit_log_active));

        row += hiddenCells(item, hiddenRetryFields);

        if(include_tr) {
            row += '</tr>';
        }

        return row;
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.data_table.OutgoingSOAP = new Class({
        toString: function() {
            var template = '<OutgoingSOAP id:{0} name:{1} is_active:{2}>';
            return String.format(template,
                valueOr(this.id, config.missingValueLabel),
                valueOr(this.name, config.missingValueLabel),
                valueOr(this.is_active, config.missingValueLabel));
        }
    });

    // ////////////////////////////////////////////////////////////////////////

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

        // More options in the main tab
        'id_ping_method': 'HTTP method used when pinging<br>the connection, e.g. HEAD or GET.',
        'id_content_type': 'Overrides the default Content-Type header.<br>Leave empty to use the default matching<br>the SOAP version selected.',
        'id_max_retries': 'How many times a failed invocation is retried<br>after a timeout or a connection error.<br>0 means no retries at all.',
        'id_retry_sleep_time': 'How many seconds to sleep before the first retry.<br>Each subsequent sleep is multiplied<br>by the backoff multiplier.',
        'id_retry_backoff_threshold': 'A cap on the total time spent sleeping<br>between retries, in seconds.<br>Once reached, no more retries take place.',
        'id_retry_backoff_multiplier': 'Each retry sleeps this many times longer<br>than the previous one, up to 8 seconds<br>per a single sleep.',

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
        'id_callback_rest': 'The outgoing REST connection<br>the response is sent to.'
    };

    // ////////////////////////////////////////////////////////////////////////

    $(document).ready(function() {

        $('#data-table').tablesorter();
        $.fn.zato.data_table.class_ = $.fn.zato.data_table.OutgoingSOAP;
        $.fn.zato.data_table.new_row_func = $.fn.zato.outgoing.soap.data_table.new_row;
        $.fn.zato.data_table.parse();
        $.fn.zato.data_table.setup_forms([
            'name',
            'host',
            'timeout',
            'ping_method'
        ]);

        // .. widen both popups, the default dialog being too narrow for all the tabs ..
        $('#create-div').dialog('option', 'width', config.dialogWidth);
        $('#edit-div').dialog('option', 'width', config.dialogWidth);

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
        var pickerIds = ['#id_scheduler_start_date', '#id_edit-scheduler_start_date'];

        $.each(pickerIds, function(ignored, pickerId) {
            $(pickerId).datetimepicker({
                'dateFormat': $('#js_date_format').val(),
                'timeFormat': $('#js_time_format').val(),
                'ampm': $.fn.zato.to_bool($('#js_ampm').val())
            });
        });

        // .. and show the callback widget matching the callback type selected ..
        $.each(['create', 'edit'], function(ignored, action) {

            $('#id_' + fieldPrefix(action) + 'callback_type').change(function() {
                toggleCallback(action);
            });

            toggleCallback(action);
        });

        // .. the health check tab manages its own callback widgets the same way.
        $.fn.zato.health_check.init();

        var uniqueConstraints = [
            {field: 'name', entity_type: 'outgoing_soap', attr_name: 'name'}
        ];

        $.each(uniqueConstraints, function(ignored, constraint) {
            $.fn.zato.validate_unique('#id_' + constraint.field, constraint.entity_type, constraint.attr_name);
            $.fn.zato.validate_unique('#id_edit-' + constraint.field, constraint.entity_type, constraint.attr_name);
        });
    });

    // ////////////////////////////////////////////////////////////////////////
    // Live form updates registration
    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.live_form_updates.register('create', [
        {object_type: 'security', target_select: '#id_security_id'}
    ]);

    $.fn.zato.live_form_updates.register('edit', [
        {object_type: 'security', target_select: '#id_edit-security_id'}
    ]);

    // ////////////////////////////////////////////////////////////////////////

})(jQuery);
