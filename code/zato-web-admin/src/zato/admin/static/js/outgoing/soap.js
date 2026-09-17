
// ////////////////////////////////////////////////////////////////////////////
// Outgoing SOAP connections
// ////////////////////////////////////////////////////////////////////////////

(function($) {

    $.fn.zato.outgoing.soap.config = {

        // There is always exactly one cluster.
        cluster_id: '1',

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

        // The Alerts tab's own label joins these once the tab reads its config off the page.
        tabLabels: {
            main:         'Main',
            soap:         'SOAP',
            security:     'Security',
            credentials:  'Body credentials',
            scheduler:    'Scheduler',
            request:      'Request',
            response:     'Response',
            callback:     'Callback'
        },

        // The Alerts tab's panels on the create and edit dialogs
        alertsPanelIds: {
            create: 'out-soap-create-tab-panel-alerts',
            edit:   'out-soap-edit-tab-panel-alerts'
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

    // The rows module reads the same prefix, so it is shared rather than spelled twice
    $.fn.zato.outgoing.soap.field_prefix = function(action) {

        if(action === 'edit') {
            return 'edit-';
        }

        return '';
    };

    var fieldPrefix = $.fn.zato.outgoing.soap.field_prefix;

    // ////////////////////////////////////////////////////////////////////////

    function resetTabs(action) {

        var isEdit = action === 'edit';
        var divId = '#create-div';
        var panelPrefix = 'out-soap-create-tab-panel-';

        if(isEdit) {
            divId = '#edit-div';
            panelPrefix = 'out-soap-edit-tab-panel-';
        }

        var tabLabels = $.extend({}, config.tabLabels, {alerts: $.fn.zato.alerts_tab.tab_label()});

        $.fn.zato.form_tabs.reset({
            div_id:       divId,
            panel_prefix: panelPrefix,
            default_tab:  config.defaultTab,
            tab_labels:   tabLabels
        });
    }

    // ////////////////////////////////////////////////////////////////////////

    // The Alerts tab reads and writes the rendered Django form of one dialog at a time
    function bindAlertsTab(action) {

        $.fn.zato.alerts_tab.bind({
            panel_id: config.alertsPanelIds[action],
            field_prefix: fieldPrefix(action)
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

        // The Alerts tab's lines are not table rows, so the walk covers them as well
        $.fn.zato.how_it_works.init({
            badgeId: action + '-how-it-works',
            divId: '#' + action + '-div',
            fieldSelector: 'table.form-data tr, .decision-line',
            descriptions: $.extend({},
                $.fn.zato.outgoing.soap.field_descriptions,
                $.fn.zato.alerts_tab.descriptions())
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

        // The body-credential, message and SOAP header rows are serialized to their hidden JSON fields
        $.fn.zato.outgoing.soap.rows.serialize(action);

        return true;
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.outgoing.soap.create = function() {
        resetTabs('create');
        $.fn.zato.data_table._create_edit('create', 'Create a new outgoing SOAP connection', null);
        $.fn.zato.outgoing.soap.rows.populate('create');
        toggleCallback('create');
        bindAlertsTab('create');
        initHowItWorks('create');
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.outgoing.soap.edit = function(id) {

        resetTabs('edit');
        $.fn.zato.data_table._create_edit('edit', 'Update the outgoing SOAP connection', id);
        $.fn.zato.outgoing.soap.rows.populate('edit');

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

        // The health check line of the Alerts tab reads its hidden inputs, populated the same way
        $.fn.zato.health_check.populate('edit', item);

        bindAlertsTab('edit');
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
        'health_check_run_every', 'health_check_run_unit', 'health_check_job_id'
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

        // A connection created through the UI is never internal, so the cell is always a link
        row += String.format(
            '<td><a href="/zato/audit-log/?source=soap-outgoing&object_name={0}&cluster={1}">Audit log</a></td>',
            encodeURIComponent(item.name), config.cluster_id);

        row += String.format(
            '<td><a href="javascript:void(0)" onclick="$.fn.zato.data_table.ping(\'{0}\', this)" class="ping-link">Ping</a></td>',
            item.id);
        row += String.format('<td><a href="javascript:$.fn.zato.outgoing.soap.invoke(\'{0}\')">Invoke</a></td>', item.id);

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

        row += hiddenCells(item, hiddenInvocationFields);

        row += String.format('<td class="ignore">{0}</td>', toDjangoBool(item.is_audit_log_active));

        row += hiddenCells(item, hiddenRetryFields);

        // The Alerts tab's fields ride in the row for the edit form to read
        row += $.fn.zato.alerts_tab.hidden_cells(item);

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
        'id_name': 'A unique name for this connection. Used to identify it in logs and the dashboard.',
        'id_is_active': 'Whether this connection can be used. Messages are not sent through inactive connections.',
        'id_is_audit_log_active': 'Whether this connection\'s traffic is recorded in the audit log. On by default.',
        'id_host': 'Address of the remote SOAP server, e.g. https://example.com:8443.',
        'id_url_path': 'URL path of the SOAP endpoint on the remote server, e.g. /services/endpoint.',
        'id_soap_action': 'Value of the SOAPAction header sent with each request. ' +
            'Leave empty if the endpoint does not require one.',
        'id_timeout': 'How many seconds to wait for a response before the invocation times out.',

        // SOAP tab
        'id_soap_version': 'SOAP protocol version the endpoint expects. ' +
            '1.2 is the most common choice today, 1.1 is used by older systems.',
        'id_use_ws_addressing': 'When on, WS-Addressing headers - Action, MessageID, To and ReplyTo - ' +
            'are added to each outgoing message.',
        'id_use_mtom': 'When on, binary attachments are sent as MTOM/XOP parts ' +
            'instead of being embedded in the message as Base64.',

        // Security tab
        'id_security_id': 'Security definition applied to outgoing messages, ' +
            'e.g. WS-Security, Basic Auth or an OAuth bearer token.',
        'id_validate_tls': 'Whether the TLS certificate of the remote server must be validated. ' +
            'Turn it off only in test environments.',
        'id_tls_client_cert': 'Path to a PEM file with the client certificate this connection presents ' +
            'to mutual-TLS endpoints. The file is mounted into the container and may hold both ' +
            'the certificate and its private key.',
        'id_tls_client_key': 'Path to the private key matching the client certificate, ' +
            'if it lives in its own PEM file. Leave empty when the certificate file already contains the key.',

        // Body credentials tab
        'id_body_credentials': 'Credentials from the security definition injected into the message body, ' +
            'for endpoints that expect them there rather than in a header. Each mapping is an element name ' +
            'with an optional position among the body\'s child elements.',

        // More options in the main tab
        'id_ping_method': 'HTTP method used when pinging the connection, e.g. HEAD or GET.',
        'id_content_type': 'Overrides the default Content-Type header. ' +
            'Leave empty to use the default matching the SOAP version selected.',
        'id_max_retries': 'How many times a failed invocation is retried after a timeout or a connection error. ' +
            '0 means no retries at all.',
        'id_retry_sleep_time': 'How many seconds to sleep before the first retry. ' +
            'Each subsequent sleep is multiplied by the backoff multiplier.',
        'id_retry_backoff_threshold': 'A cap on the total time spent sleeping between retries, in seconds. ' +
            'Once reached, no more retries take place.',
        'id_retry_backoff_multiplier': 'Each retry sleeps this many times longer than the previous one, ' +
            'up to 8 seconds per a single sleep.',

        // Scheduler tab
        'id_scheduler_run_every': 'How often this connection is invoked, e.g. every 6 hours. ' +
            'Leave empty for no scheduled invocations.',
        'id_scheduler_start_date': 'When the first scheduled invocation takes place, entered in your own timezone.',

        // Request tab
        'id_request_operation': 'The operation every invocation calls, e.g. GetItemDetails. ' +
            'Empty means the caller names it explicitly.',
        'id_request_message': 'Elements of the message each invocation sends. ' +
            'Names may use dot-paths, e.g. <code>order.customer_id</code>. A value is sent exactly as typed ' +
            'unless its JSONata toggle is on, then it is evaluated each time the request fires.',
        'id_request_message_map': 'A single JSONata expression that builds the whole message ' +
            'instead of the rows above, e.g. <code>{"since": $substring($now(), 0, 10)}</code>',
        'id_request_soap_headers': 'Custom elements injected into the soap:Header of every envelope. ' +
            'A value is sent exactly as typed unless its JSONata toggle is on.',
        'id_wsa_action': 'The WS-Addressing Action header sent with every envelope.',
        'id_wsa_to': 'The WS-Addressing To header sent with every envelope.',
        'id_wsa_reply_to': 'The WS-Addressing ReplyTo header sent with every envelope.',

        // Response tab
        'id_response_map_mode': 'Whether the response map below is JSONata, applied to the parsed response, ' +
            'or XPath, applied to the raw XML envelope.',
        'id_response_map': 'An expression that reshapes the response before the callback receives it. ' +
            'Leave empty to pass the response through as-is.',

        // Callback tab
        'id_callback_type': 'Where each response is delivered - to a service, a pub/sub topic ' +
            'or an outgoing REST connection.',
        'id_callback_service': 'The service invoked with the response each time the connection is invoked.',
        'id_callback_topic': 'The pub/sub topic the response is published to.',
        'id_callback_rest': 'The outgoing REST connection the response is sent to.'
    };

    // ////////////////////////////////////////////////////////////////////////

    $(document).ready(function() {

        // The Alerts tab reads its config off the page before anything else reads the tab
        $.fn.zato.alerts_tab.init({config_id: 'out-soap-alerts-tab-config'});
        $.fn.zato.live_form_updates.register('create', $.fn.zato.alerts_tab.live_configs(''));
        $.fn.zato.live_form_updates.register('edit', $.fn.zato.alerts_tab.live_configs('edit-'));

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
