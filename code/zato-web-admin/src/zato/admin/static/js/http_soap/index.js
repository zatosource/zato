
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.http_soap.gateway_trigger_service = 'helpers.service-gateway';
$.fn.zato.http_soap.gateway_fade_duration = 100;
$.fn.zato.http_soap.previous_url_path = {'': '', 'edit-': ''};
$.fn.zato.http_soap.needs_random_prefix = false;

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.HTTPSOAP = new Class({
    toString: function() {
        var s = '<HTTPSOAP id:{0} name:{1} is_active:{2} merge_url_params_req:{3} data_format:{4}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.is_active ? this.is_active : '(none)',
                                this.merge_url_params_req ? this.merge_url_params_req : '(none)',
                                this.data_format ? this.data_format : '(none)'
                                );
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {

    $.fn.zato.http_soap.tabs.init();

    $('#data-table').tablesorter();
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.HTTPSOAP;
    $.fn.zato.data_table.new_row_func = $.fn.zato.http_soap.data_table.new_row;
    $.fn.zato.data_table.parse();

    var _connection = $('input[name="connection"]').val();
    var _transport = $('input[name="transport"]').val();
    var _is_channel = (_connection === 'channel');
    var _transport_suffix = _transport === 'plain_http' ? 'rest' : 'soap';
    var _entity_type = (_is_channel ? 'channel_' : 'outgoing_') + _transport_suffix;

    var _required_fields = ['name', 'service', 'security', 'validate_tls'];
    if(_is_channel) {
        _required_fields.splice(1, 0, 'url_path');
    }
    if(!_is_channel) {
        _required_fields.push('host');
    }
    $.fn.zato.data_table.setup_forms(_required_fields);

    // Returns a function that reads the current values of the fields the server compares
    // in ensure_channel_is_unique, so the url_path check mirrors the create service exactly.
    var _get_url_path_check_context = function(suffix) {
        return function() {
            return {
                'method': $('#id_' + suffix + 'method').val(),
                'http_accept': $('#id_' + suffix + 'http_accept').val()
            };
        };
    };

    var unique_constraints = [
        {field: 'name', entity_type: _entity_type, attr_name: 'name'}
    ];
    if(_is_channel) {
        unique_constraints.push({field: 'url_path', entity_type: _entity_type, attr_name: 'url_path', needs_context: true});
    }
    $.each(unique_constraints, function(i, c) {
        var create_filter = c.needs_context ? _get_url_path_check_context('') : null;
        var edit_filter = c.needs_context ? _get_url_path_check_context('edit-') : null;
        $.fn.zato.validate_unique('#id_' + c.field, c.entity_type, c.attr_name, create_filter);
        $.fn.zato.validate_unique('#id_edit-' + c.field, c.entity_type, c.attr_name, edit_filter);
    });

    $.fn.zato.data_table.before_submit_hook = $.fn.zato.http_soap.data_table.before_submit_hook;

    $.each(['', 'edit-'], function(ignored, suffix) {

        var service_elem = $(String.format('#id_{0}service', suffix));
        service_elem.change(function() {
            $.fn.zato.http_soap.toggle_gateway_service_list(suffix, this.value);
            $.fn.zato.http_soap.set_gateway_url_path(suffix, this.value);
        });
    });
})

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.after_populate = function() {
    $.each(['', 'edit-'], function(ignored, suffix) {
        var service_elem = $(String.format('#id_{0}service', suffix));
        $.fn.zato.http_soap.toggle_gateway_service_list(suffix, service_elem.val());
    });

    if($.fn.zato.http_soap.is_rest_outgoing()) {
        $.each(['create', 'edit'], function(ignored, action) {
            $.fn.zato.http_soap.toggle_callback(action);
        });
    }
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.http_soap.populate_groups = function(
    item_list,
    item_html_prefix,
    html_elem_id_selector
) {

    let id_field = "id";
    let name_field = "name";
    let is_taken_field = "is_assigned";
    let url_template = "/zato/groups/group/zato-api-creds/?cluster=1&query={1}&highlight={2}";
    let html_table_id = "multi-select-table";
    let checkbox_field_name = "id";
    let disable_if_is_taken = false;

    $.fn.zato.populate_multi_checkbox(
        item_list,
        item_html_prefix,
        id_field,
        name_field,
        is_taken_field,
        url_template,
        html_table_id,
        html_elem_id_selector,
        checkbox_field_name,
        disable_if_is_taken
    );
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.http_soap.create_populate_groups = function(item_list) {
    let item_html_prefix = "http_soap_security_group_checkbox_";
    let html_elem_id_selector = "#multi-select-div-create";
    $.fn.zato.http_soap.populate_groups(item_list, item_html_prefix, html_elem_id_selector);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.http_soap.edit_populate_groups = function(item_list) {
    let item_html_prefix = "edit-http_soap_security_group_checkbox_";
    let html_elem_id_selector = "#multi-select-div-edit";
    $.fn.zato.http_soap.populate_groups(item_list, item_html_prefix, html_elem_id_selector);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.http_soap.create_populate_groups_callback = function(data, status) {
    var success = status == 'success';
    if(success) {
        var item_list = $.parseJSON(data.responseText);
        if(item_list && item_list.length) {
            $.fn.zato.http_soap.create_populate_groups(item_list);
        }
        else {
            let elem = $("#multi-select-div-create");
            elem.removeClass("multi-select-div");
            elem.html("No security groups found. Click to <a href='/zato/groups/group/zato-api-creds/?cluster=1' target='_blank'>create one</a>.");
        }
    }
    else {
        console.log(data.responseText);
    }
}
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.http_soap.edit_populate_groups_callback = function(data, status) {
    var success = status == 'success';
    if(success) {
        var item_list = $.parseJSON(data.responseText);
        if(item_list.length) {
            $.fn.zato.http_soap.edit_populate_groups(item_list);
        }
        else {
            let elem = $("#multi-select-div-edit");
            elem.removeClass("multi-select-div");
            elem.html("No security groups found. Click to <a href='/zato/groups/group/zato-api-creds/?cluster=1' target='_blank'>create one</a>.");
        }
    }
    else {
        console.log(data.responseText);
    }
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.http_soap.field_descriptions = {

    'id_name': 'A unique name for this endpoint. Used to identify it in logs and the dashboard.',
    'id_is_active': 'Whether this endpoint accepts messages. Requests to inactive endpoints are rejected.',
    'id_is_audit_log_active': 'Whether this endpoint\'s traffic is recorded in the audit log. On by default.',
    'id_should_include_in_openapi': 'Whether this endpoint appears in OpenAPI documents. On by default.',
    'id_is_deprecated': 'Whether this endpoint is deprecated. Deprecated endpoints announce their status ' +
        'in response headers and OpenAPI documents.',
    'id_deprecation_sunset': 'The date this deprecated endpoint is retired, e.g. 2026-12-31. ' +
        'Sent to callers in the Sunset header.',
    'id_deprecation_successor': 'URL path of the endpoint that replaces this deprecated one, ' +
        'e.g. /api/v2/example. Sent to callers in the Link header.',
    'id_url_path': 'URL path this endpoint listens on, e.g. /services/endpoint.',
    'id_service': 'The service invoked for each message this endpoint receives.',
    'id_security': 'Security definition each incoming message must satisfy, e.g. WS-Security or Basic Auth.',

    'id_soap_action': 'Value of the SOAPAction header expected with each request. ' +
        'Leave empty if callers do not send one.',
    'id_soap_version': 'SOAP protocol version this endpoint accepts. 1.2 is the most common choice today, ' +
        '1.1 is used by older systems.',
    'id_use_mtom': 'When on and your service returns files or images, this channel sends them back ' +
        'to the caller as they are (MTOM) instead of converting them to Base64 text, ' +
        'which would make them bigger and slower to transfer.',

    'id_url_params_pri': 'Whether parameters from the query string or from the URL path win ' +
        'when both carry the same name.',
    'id_params_pri': 'Whether parameters from the URL or from the message body win ' +
        'when both carry the same name.',
    'id_method': 'HTTP method required for incoming requests. Leave empty to accept any method.',
    'id_http_accept': 'Accept header required for incoming requests. Leave the default to accept any content.',
    'id_data_format': 'Format of the messages exchanged, e.g. JSON. With a format selected, payloads are parsed ' +
        'before they reach your service.',
    'id_merge_url_params_req': 'When on, parameters from the URL path and the query string are merged ' +
        'into the request, so services read them like regular input.',
    'id_match_slash': 'When on, {placeholders} in the URL path can also match values that contain slashes. ' +
        'When off, a placeholder stops at each slash, matching exactly one path segment.',
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.http_soap.rest_outgoing_field_descriptions = {

    // Config tab
    'id_name': 'A unique name for this connection. Used to identify it in logs and the dashboard.',
    'id_url_path': 'URL path on the remote server, e.g. /api/employees. ' +
        'May contain {placeholders} filled in by the Request tab\'s path params.',
    'id_security': 'Security definition used with each request, e.g. Basic Auth or an OAuth bearer token.',
    'id_data_format': 'Format of the data this connection exchanges, e.g. JSON. ' +
        'Responses are parsed accordingly, so services receive ready-to-use objects.',

    // Scheduler tab
    'id_scheduler_run_every': 'How often this connection is invoked, e.g. every 6 hours. ' +
        'Leave empty for no scheduled invocations.',
    'id_scheduler_start_date': 'When the first scheduled invocation takes place, entered in your own timezone.',

    // Request tab
    'id_request_method': 'HTTP method every invocation uses. Empty means the connection\'s own method.',
    'id_request_query_string': 'Query parameters sent with each request. A value is sent exactly as typed ' +
        'unless its JSONata toggle is on, then it is an expression evaluated each time the request fires, e.g. ' +
        '<code>"Date ge \'" & $substring($now(), 0, 10) & "\'"</code>',
    'id_request_path_params': 'Values for the {placeholders} in the URL path. ' +
        'A value is sent exactly as typed, e.g. <code>emea</code>, unless its JSONata toggle is on, ' +
        'then it is evaluated each time the request fires, e.g. ' +
        '<code>$substring($now(), 0, 10)</code>',
    'id_request_headers': 'Extra HTTP headers sent with each request. A value is sent exactly as typed ' +
        'unless its JSONata toggle is on, then it is evaluated each time the request fires.',
    'id_request_data': 'Request body sent with each request. It is either sent exactly as typed ' +
        'or it is JSONata that builds the body, e.g. ' +
        '<code>{"since": $substring($now(), 0, 10)}</code>',

    // Response tab
    'id_response_map_mode': 'Whether the response map below is JSONata or XPath.',
    'id_response_map': 'An expression that reshapes the response before the callback receives it, e.g. ' +
        '<code>$.{ "id": item_id, "email": email }</code> Leave empty to pass the response through as-is.',

    // Callback tab
    'id_callback_type': 'Where each response is delivered - to a service, a pub/sub topic ' +
        'or another REST connection.',
    'id_callback_service': 'The service invoked with the response each time the connection is invoked.',
    'id_callback_topic': 'The pub/sub topic the response is published to.',
    'id_callback_rest': 'The outgoing REST connection the response is sent to.',
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.http_soap.init_how_it_works = function(action) {

    var transport = $('input[name="transport"]').val();
    var descriptions;
    var fieldSelector = 'table.form-data tr';

    if(transport == 'soap') {

        // A SOAP channel's Alerts tab lines are described next to its own fields
        descriptions = $.extend({},
            $.fn.zato.http_soap.field_descriptions,
            $.fn.zato.alerts_tab.descriptions());
        fieldSelector = 'table.form-data tr, .decision-line';
    }
    else if($.fn.zato.http_soap.is_rest_outgoing()) {

        // An outgoing connection's Alerts and Delivery tab lines are described next to its own fields
        descriptions = $.extend({},
            $.fn.zato.http_soap.rest_outgoing_field_descriptions,
            $.fn.zato.delivery_tab.descriptions(),
            $.fn.zato.alerts_tab.descriptions());
        fieldSelector = 'table.form-data tr, .decision-line';
    }
    else if($.fn.zato.http_soap.is_rest_channel()) {

        // The Alerts tab's lines are not table rows, so the walk covers them as well
        descriptions = $.fn.zato.alerts_tab.descriptions();
        fieldSelector = 'table.form-data tr, .decision-line';
    }
    else {
        return;
    }

    $.fn.zato.how_it_works.init({
        badgeId: action + '-how-it-works',
        divId: '#' + action + '-div',
        fieldSelector: fieldSelector,
        descriptions: descriptions
    });
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.http_soap.create = function(object_type) {

    var url = String.format('/zato/http-soap/get-security-groups/zato-api-creds/');
    $.fn.zato.post(url, $.fn.zato.http_soap.create_populate_groups_callback, '', '', true);
    $.fn.zato.http_soap.reset_tabs('create');
    $.fn.zato.data_table._create_edit('create', 'Create a new ' + object_type, null);

    if($.fn.zato.http_soap.is_rest_outgoing()) {
        $.fn.zato.http_soap.populate_param_rows('create');
        $.fn.zato.http_soap.toggle_callback('create');

        $.fn.zato.delivery_tab.bind({
            panel_id: 'http-soap-create-tab-panel-delivery',
            field_prefix: ''
        });
    }

    if($.fn.zato.http_soap.has_alerts_tab()) {
        $.fn.zato.alerts_tab.bind({
            panel_id: 'http-soap-create-tab-panel-alerts',
            field_prefix: ''
        });
    }

    $.fn.zato.http_soap.init_how_it_works('create');
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.http_soap.edit = function(id) {
    var url = String.format('/zato/http-soap/get-security-groups/zato-api-creds/?http_soap_channel_id=' + id);
    $.fn.zato.post(url, $.fn.zato.http_soap.edit_populate_groups_callback, '', '', true);
    $.fn.zato.http_soap.reset_tabs('edit');
    $.fn.zato.data_table._create_edit('edit', 'Update the object', id);

    if($.fn.zato.http_soap.is_rest_outgoing()) {

        $.fn.zato.http_soap.populate_param_rows('edit');

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
        $.fn.zato.http_soap.toggle_callback('edit');

        // The health check line of the Alerts tab reads its hidden inputs, populated the same way
        $.fn.zato.health_check.populate('edit', item);

        // The Delivery tab reads the form the item was populated into
        $.fn.zato.delivery_tab.bind({
            panel_id: 'http-soap-edit-tab-panel-delivery',
            field_prefix: 'edit-'
        });
    }

    if($.fn.zato.http_soap.has_alerts_tab()) {
        $.fn.zato.alerts_tab.bind({
            panel_id: 'http-soap-edit-tab-panel-alerts',
            field_prefix: 'edit-'
        });
    }

    $.fn.zato.http_soap.init_how_it_works('edit');
}

// /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.http_soap.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Object `{0}` deleted',
        'Are you sure you want to delete object `{0}`?',
        true);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.http_soap.toggle_gateway_service_list = function(suffix, service_name) {
    var row_id = suffix ? 'gateway-service-list-row-edit' : 'gateway-service-list-row-create';
    var row = $('#' + row_id);
    var duration = $.fn.zato.http_soap.gateway_fade_duration;

    if(service_name === $.fn.zato.http_soap.gateway_trigger_service) {
        row.fadeIn(duration);
    }
    else {
        row.fadeOut(duration);
    }
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.http_soap.set_gateway_url_path = function(suffix, service_name) {
    var url_path_elem = $(String.format('#id_{0}url_path', suffix));

    if(service_name === $.fn.zato.http_soap.gateway_trigger_service) {
        $.fn.zato.http_soap.previous_url_path[suffix] = url_path_elem.val();
        var url_path = '/zato/gateway/{service}';

        if($.fn.zato.http_soap.needs_random_prefix) {
            var random_array = new Uint32Array(1);
            crypto.getRandomValues(random_array);
            var random_int = random_array[0] % 100000001;
            var pad_char = String((random_array[0] % 9) + 1);
            var padded_int = String(random_int).padStart(9, pad_char);
            url_path = '/zato/gateway/' + padded_int + '/{service}';
        }

        url_path_elem.val(url_path);
    }
    else {
        if($.fn.zato.http_soap.previous_url_path[suffix]) {
            url_path_elem.val($.fn.zato.http_soap.previous_url_path[suffix]);
            $.fn.zato.http_soap.previous_url_path[suffix] = '';
        }
    }
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.http_soap.get_invoke_url = function(id) {
    var connection = $(document).getUrlParam('connection');
    if (connection === 'channel') {
        return '/zato/http-soap/invoke-channel/' + id + '/';
    }
    return '/zato/http-soap/invoke-outconn/' + id + '/';
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.http_soap.invoke = function(id) {
    var item = $.fn.zato.data_table.data[id];
    if (!item) {
        return;
    }

    var connection = $(document).getUrlParam('connection');
    var history_key = 'zato.invoke-history.' + (connection === 'channel' ? 'channel' : 'outconn') + '.' + id;

    $.fn.zato.invoker.open_overlay({
        id: id,
        name: item.name,
        connection: connection,
        history_key: history_key,
        get_invoke_url_func: $.fn.zato.http_soap.get_invoke_url
    });
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Live form updates registration
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

;(function() {
    var connection = $(document).getUrlParam('connection');
    var transport = $(document).getUrlParam('transport');
    var is_channel = connection === 'channel';

    // The poll's list must match what the page itself renders - channels never offer
    // outgoing-only security types and outgoing REST connections only offer their supported set
    var security_object_type = 'security';
    if(is_channel) {
        security_object_type = 'security_channel';
    }
    else if(transport === 'plain_http') {
        security_object_type = 'security_rest_outgoing';
    }

    var create_configs = [
        {
            object_type: security_object_type,
            target_select: '#id_security'
        }
    ];

    var edit_configs = [
        {
            object_type: security_object_type,
            target_select: '#id_edit-security'
        }
    ];

    if(is_channel) {
        create_configs.push({
            object_type: 'service',
            target_select: '#id_service'
        });
        create_configs.push({
            object_type: 'security_group',
            handler: 'multi_checkbox',
            container: '#multi-select-div-create',
            reload_callback: function() {
                var url = '/zato/http-soap/get-security-groups/zato-api-creds/';
                $.fn.zato.post(url, $.fn.zato.http_soap.create_populate_groups_callback, '', '', true);
            }
        });

        edit_configs.push({
            object_type: 'service',
            target_select: '#id_edit-service'
        });
        edit_configs.push({
            object_type: 'security_group',
            handler: 'multi_checkbox',
            container: '#multi-select-div-edit',
            reload_callback: function() {
                var url = '/zato/http-soap/get-security-groups/zato-api-creds/';
                $.fn.zato.post(url, $.fn.zato.http_soap.edit_populate_groups_callback, '', '', true);
            }
        });
    }

    $.fn.zato.live_form_updates.register('create', create_configs);
    $.fn.zato.live_form_updates.register('edit', edit_configs);
})();

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
