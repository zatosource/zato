
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.http_soap.gateway_trigger_service = 'helpers.service-gateway';
$.fn.zato.http_soap.gateway_fade_duration = 100;
$.fn.zato.http_soap.previous_url_path = {'': '', 'edit-': ''};
$.fn.zato.http_soap.needs_random_prefix = false;

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.HTTPSOAP = new Class({
    toString: function() {
        var s = '<HTTPSOAP id:{0} name:{1} is_active:{2} merge_url_params_req:{3} data_format:{4} serialization_type:{5}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.is_active ? this.is_active : '(none)',
                                this.merge_url_params_req ? this.merge_url_params_req : '(none)',
                                this.data_format ? this.data_format : '(none)',
                                this.serialization_type ? this.serialization_type : '(none)'
                                );
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
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

            // The soap_action field exists only on SOAP pages.
            var soap_action_elem = $('#id_' + suffix + 'soap_action');
            var soap_action = soap_action_elem.length ? soap_action_elem.val() : '';

            return {
                'soap_action': soap_action,
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

    // Removing a request parameter row
    $(document).on('click', '.request-param-remove', function() {
        $(this).closest('.request-param-row').remove();
        return false;
    });

    if($.fn.zato.http_soap.is_rest_outgoing()) {

        // Attach date-time pickers to the scheduler start date fields in both popups ..
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
                $.fn.zato.http_soap.toggle_callback(action);
            });
            $.fn.zato.http_soap.toggle_callback(action);
        });

        // .. the health check tab manages its own callback widgets the same way.
        $.fn.zato.health_check.init();
    }

    $.each(['', 'edit-'], function(ignored, suffix) {

        var elem = $(String.format('#id_{0}serialization_type', suffix));
        elem.ready(function() {
            $.fn.zato.http_soap.data_table.toggle_validate_tls(suffix, elem.val() == 'suds');
            elem.change($.fn.zato.http_soap.data_table.on_serialization_change);
        });

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
        var elem = $(String.format('#id_{0}serialization_type', suffix));
        $.fn.zato.http_soap.data_table.toggle_validate_tls(suffix, elem.val() == 'suds');

        var service_elem = $(String.format('#id_{0}service', suffix));
        $.fn.zato.http_soap.toggle_gateway_service_list(suffix, service_elem.val());
    });

    if($.fn.zato.http_soap.is_rest_outgoing()) {
        $.each(['create', 'edit'], function(ignored, action) {
            $.fn.zato.http_soap.toggle_callback(action);
            $.fn.zato.health_check.toggle_callback(action);
        });
    }
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.http_soap.is_rest_outgoing = function() {
    var connection = $('input[name="connection"]').val();
    var transport = $('input[name="transport"]').val();
    return connection === 'outgoing' && transport === 'plain_http';
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.http_soap.tab_labels = {
    config:       'Config',
    scheduler:    'Scheduler',
    request:      'Request',
    response:     'Response',
    callback:     'Callback',
    health_check: 'Health check'
};

$.fn.zato.http_soap.reset_tabs = function(action) {
    if(!$.fn.zato.http_soap.is_rest_outgoing()) {
        return;
    }
    var is_edit = action === 'edit';
    $.fn.zato.form_tabs.reset({
        div_id:       is_edit ? '#edit-div' : '#create-div',
        panel_prefix: is_edit ? 'http-soap-edit-tab-panel-' : 'http-soap-create-tab-panel-',
        default_tab:  'config',
        tab_labels:   $.fn.zato.http_soap.tab_labels
    });
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Request parameter rows - each row is a key, a value and the value's Text/JSONata mode,
// serialized to a hidden JSON field before the form is submitted.
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.http_soap.param_kinds = ['query_string', 'path_params', 'headers'];

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.http_soap.add_param_row = function(action, kind, key, value, mode) {

    var row = $('<tr class="request-param-row"></tr>');

    var jsonata_cell = $('<td class="request-param-jsonata-cell"></td>');
    var jsonata_toggle = $('<label class="toggle-switch" title="Evaluate the value as JSONata"></label>');
    var jsonata_checkbox = $('<input type="checkbox" class="request-param-jsonata">');
    if(mode === 'jsonata') {
        jsonata_checkbox.prop('checked', true);
    }
    var jsonata_slider = $('<span class="toggle-slider"></span>');
    jsonata_toggle.append(jsonata_checkbox);
    jsonata_toggle.append(jsonata_slider);
    jsonata_cell.append(jsonata_toggle);

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

$.fn.zato.http_soap._param_rows_field = function(action, kind) {
    var suffix = action === 'edit' ? 'edit-' : '';
    return '#id_' + suffix + 'request_' + kind;
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.http_soap.populate_param_rows = function(action) {

    $.each($.fn.zato.http_soap.param_kinds, function(ignored, kind) {

        var container = $('#request-' + kind + '-rows-' + action);
        container.empty();

        var value = $($.fn.zato.http_soap._param_rows_field(action, kind)).val();
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
            $.fn.zato.http_soap.add_param_row(action, kind, items[idx].key, items[idx].value, items[idx].mode);
        }
    });
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.http_soap.serialize_param_rows = function(action) {

    $.each($.fn.zato.http_soap.param_kinds, function(ignored, kind) {

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

        $($.fn.zato.http_soap._param_rows_field(action, kind)).val(out.length ? JSON.stringify(out) : '');
    });
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.http_soap.data_table.before_submit_hook = function(form) {

    // Only outgoing REST connections use row-based parameters
    if(!$.fn.zato.http_soap.is_rest_outgoing()) {
        return true;
    }

    var is_edit = $(form).attr('id') === 'edit-form';
    $.fn.zato.http_soap.serialize_param_rows(is_edit ? 'edit' : 'create');

    return true;
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.http_soap.toggle_callback = function(action) {

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

    'id_name': 'A unique name for this endpoint.<br>Used to identify it in logs and the dashboard.',
    'id_is_active': 'Whether this endpoint accepts messages.<br>Requests to inactive endpoints are rejected.',
    'id_url_path': 'URL path this endpoint listens on,<br>e.g. /services/endpoint.',
    'id_service': 'The service invoked for each message<br>this endpoint receives.',
    'id_security': 'Security definition each incoming message<br>must satisfy, e.g. WS-Security<br>or Basic Auth.',

    'id_soap_action': 'Value of the SOAPAction header expected<br>with each request. Leave empty if callers<br>do not send one.',
    'id_soap_version': 'SOAP protocol version this endpoint speaks.<br>1.2 is the most common choice today,<br>1.1 is used by older systems.',
    'id_use_mtom': 'When on and your service returns files or images,<br>this channel sends them back to the caller as they are (MTOM) instead of converting them to Base64 text, which would make them bigger and slower to transfer.',

    'id_url_params_pri': 'Whether parameters from the query string<br>or from the URL path win<br>when both carry the same name.',
    'id_params_pri': 'Whether parameters from the URL<br>or from the message body win<br>when both carry the same name.',
    'id_method': 'HTTP method required for incoming requests.<br>Leave empty to accept any method.',
    'id_http_accept': 'Accept header required for incoming requests.<br>Leave the default to accept any content.',
    'id_data_format': 'Format of the messages exchanged, e.g. JSON.<br>With a format selected, payloads are parsed<br>before your service sees them.',
    'id_merge_url_params_req': 'When on, parameters from the URL path<br>and the query string are merged into the request,<br>so services read them like regular input.',
    'id_match_slash': 'When on, {placeholders} in the URL path<br>can also match values that contain slashes.<br>When off, a placeholder stops at each slash,<br>matching exactly one path segment.',
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.http_soap.rest_outgoing_field_descriptions = {

    // Config tab
    'id_name': 'A unique name for this connection.<br>Used to identify it in logs and the dashboard.',
    'id_url_path': 'URL path on the remote server,<br>e.g. /api/employees.<br>May contain {placeholders} filled in<br>by the Request tab\'s path params.',
    'id_security': 'Security definition used with each request,<br>e.g. Basic Auth or an OAuth bearer token.',
    'id_data_format': 'Format of the data this connection exchanges,<br>e.g. JSON. Responses are parsed accordingly,<br>so services receive ready-to-use objects.',

    // Scheduler tab
    'id_scheduler_run_every': 'How often this connection is invoked,<br>e.g. every 6 hours.<br>Leave empty for no scheduled invocations.',
    'id_scheduler_start_date': 'When the first scheduled invocation takes place,<br>entered in your own timezone.',

    // Request tab
    'id_request_method': 'HTTP method every invocation uses.<br>Empty means the connection\'s own method.',
    'id_request_query_string': 'Query parameters sent with each request.<br>A value is sent exactly as typed unless its JSONata toggle<br>is on, then it is an expression evaluated<br>each time the request fires, e.g.<br>' +
        '<code>"Date ge \'" & $substring($now(), 0, 10) & "\'"</code>',
    'id_request_path_params': 'Values for the {placeholders} in the URL path.<br>A value is sent exactly as typed, e.g. <code>emea</code>,<br>unless its JSONata toggle is on, then it is evaluated<br>each time the request fires, e.g.<br>' +
        '<code>$substring($now(), 0, 10)</code>',
    'id_request_headers': 'Extra HTTP headers sent with each request.<br>A value is sent exactly as typed unless its JSONata toggle<br>is on, then it is evaluated each time the request fires.',
    'id_request_data': 'Request body sent with each request.<br>It is either sent exactly as typed<br>or it is JSONata that builds the body, e.g.<br>' +
        '<code>{"since": $substring($now(), 0, 10)}</code>',

    // Response tab
    'id_response_map_mode': 'Whether the response map below is JSONata or XPath.',
    'id_response_map': 'An expression that reshapes the response<br>before the callback receives it, e.g.<br>' +
        '<code>$.{ "id": item_id, "email": email }</code><br>Leave empty to pass the response through as-is.',

    // Callback tab
    'id_callback_type': 'Where each response is delivered - to a service,<br>a pub/sub topic or another REST connection.',
    'id_callback_service': 'The service invoked with the response<br>each time the connection is invoked.',
    'id_callback_topic': 'The pub/sub topic the response is published to.',
    'id_callback_rest': 'The outgoing REST connection<br>the response is sent to.',
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.http_soap.init_how_it_works = function(action) {

    var transport = $('input[name="transport"]').val();
    var descriptions;

    if(transport == 'soap') {
        descriptions = $.fn.zato.http_soap.field_descriptions;
    }
    else if($.fn.zato.http_soap.is_rest_outgoing()) {
        descriptions = $.extend({},
            $.fn.zato.http_soap.rest_outgoing_field_descriptions,
            $.fn.zato.health_check.field_descriptions);
    }
    else {
        return;
    }

    $.fn.zato.how_it_works.init({
        badgeId: action + '-how-it-works',
        divId: '#' + action + '-div',
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

        // The health check tab's widgets are populated the same way
        $.fn.zato.health_check.populate('edit', item);
    }

    $.fn.zato.http_soap.init_how_it_works('edit');
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.http_soap.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    $.fn.zato.toggle_visible_hidden(".api-client-groups-options-block", false);

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var audit_object_type_label = '';
    var is_active = item.is_active == true;
    var merge_url_params_req = item.merge_url_params_req == true;

    var cluster_id = $(document).getUrlParam('cluster');
    var connection = $(document).getUrlParam('connection');
    var is_channel = connection == 'channel';
    var is_outgoing = connection == 'outgoing';
    var is_soap = data.transport == 'soap';

    var soap_action_tr = '';
    var soap_version_tr = '';
    var service_tr = '';
    var host_tr = '';
    var merge_url_params_req_tr = '';
    var url_params_pri_tr = '';
    var params_pri_tr = '';

    var data_encoding = '';

    var serialization_type = item.serialization_type ? item.serialization_type : 'string';
    var security_name = item.security_id ? item.security_select : '<span class="form_hint">---</span>';

    if(is_soap) {
        soap_action_tr += String.format('<td>{0}</td>', item.soap_action);
        soap_version_tr += String.format('<td>{0}</td>', item.soap_version);
        audit_object_type_label += 'SOAP ';
    }
    else {
        audit_object_type_label += 'REST ';
    }

    if(is_channel) {
        service_tr += String.format('<td>{0}</td>', $.fn.zato.data_table.service_text(item.service, cluster_id));
        merge_url_params_req_tr += String.format('<td class="ignore">{0}</td>', merge_url_params_req);
        url_params_pri_tr += String.format('<td class="ignore">{0}</td>', item.url_params_pri);
        params_pri_tr += String.format('<td class="ignore">{0}</td>', item.params_pri);
        audit_object_type_label += 'channel';
    }

    if(is_outgoing) {
        host_tr += String.format('<td>{0}</td>', item.host);
        audit_object_type_label += 'outgoing connection';
    }

    /* 1, 2 */
    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";

    /* 3 */
    var is_gateway_channel = false;
    if(is_channel) {
        if(!is_soap) {
            is_gateway_channel = item.service === $.fn.zato.http_soap.gateway_trigger_service;
        }
    }
    if(is_gateway_channel) {
        row += String.format('<td><span class="gateway-badge">GW</span><span class="name-value">{0}</span></td>', item.name);
    }
    else {
        row += String.format('<td><span class="name-value">{0}</span></td>', item.name);
    }

    /* 4 */
    row += String.format('<td style="text-align:center">{0}</td>', is_active ? 'Yes' : 'No');

    /* 5 */
    if(is_outgoing) {
        row += host_tr;
    }

    /* 6 */
    row += String.format('<td>{0}</td>', item.url_path);

    /* 7 */
    if(is_channel) {
        row += service_tr;
    }

    /* 9, 9b */
    row += String.format('<td>{0}</td>', security_name);

    if(is_channel) {
        row += String.format('<td>{0}</td>', data.security_groups_info);
    }

    /* 10, 11, 11a */
    if(is_soap) {
        row += soap_action_tr;
        row += soap_version_tr;
        row += String.format("<td class='ignore'>{0}</td>", item.use_mtom == true ? 'True' : 'False');
    }

    /* 12, 13 */
    if(is_channel) {
        row += String.format("<td class='ignore'>{0}</td>", data.service);
    }

    /* 14, 15, 16 */
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", is_active);
    row += String.format("<td class='ignore'>{0}</td>", item.security_id);

    if(is_channel) {
    }

    /* 20 */
    row += String.format("<td class='ignore'>{0}</td>", item.data_format);

    /* 22, 23a, 23b, 23c */
    row += String.format("<td class='ignore'>{0}</td>", item.timeout);
    if(is_outgoing) {
        row += String.format("<td class='ignore'>{0}</td>", item.validate_tls);
    }
    if(is_channel) {
        row += String.format("<td class='ignore'>{0}</td>", item.match_slash);
        row += String.format("<td class='ignore'>{0}</td>", item.http_accept);
    }

    /* 24, 25, 26, 27 */
    if(is_outgoing) {
        row += String.format("<td class='ignore'>{0}</td>", item.ping_method);
        row += String.format("<td class='ignore'>{0}</td>", item.pool_size);
        row += String.format("<td class='ignore'>{0}</td>", serialization_type);
        row += String.format("<td class='ignore'>{0}</td>", item.content_type);
    }

    /* 28, 29, 30, 30a */
    if(is_channel) {
        row += merge_url_params_req_tr;
        row += url_params_pri_tr;
        row += params_pri_tr;
        row += String.format("<td class='ignore'>{0}</td>", item.method || '');
    }

    if(is_channel) {
        row += String.format('<td><a href="/zato/http-soap/rate-limiting/{0}/?cluster={1}">Rate limiting</a></td>', item.id, cluster_id);
    }

    /* Audit log (REST channels and REST outgoing connections only) */
    if(is_channel && !is_soap) {
        row += String.format('<td><a href="/zato/audit-log/?source=rest-channel&object_name={0}&cluster={1}">Audit log</a></td>', encodeURIComponent(item.name), cluster_id);
    }

    if(is_outgoing && !is_soap) {
        row += String.format('<td><a href="/zato/audit-log/?source=rest-outgoing&object_name={0}&cluster={1}">Audit log</a></td>', encodeURIComponent(item.name), cluster_id);
    }

    /* 31, 32 */
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.http_soap.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.http_soap.delete_('{0}');\">Delete</a>", item.id));

    if(is_outgoing) {
        /* 33 */
        row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:void(0)\" onclick=\"$.fn.zato.data_table.ping('{0}', this)\" class=\"ping-link\">Ping</a>", item.id));
    }

    /* Invoke (REST only) */
    if(!is_soap) {
        row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.http_soap.invoke('{0}')\">Invoke</a>", item.id));
    }

    /* 38a */
    row += String.format("<td class='ignore'>{0}</td>", data.data_encoding || data_encoding);

    /* 39 - gateway_service_list for REST channels */
    if(is_channel && !is_soap) {
        row += String.format("<td class='ignore'>{0}</td>", item.gateway_service_list || '');
    }

    /* 40 - declarative invocation and health check fields for REST outgoing connections */
    if(is_outgoing && !is_soap) {

        // After a submit the instance carries the callback widgets rather than the resolved name,
        // so the name is derived from the widget matching the callback type selected.
        if(!item.callback_name && item.callback_type) {
            item.callback_name = item['callback_' + item.callback_type];
        }
        if(!item.health_check_callback_name && item.health_check_callback_type) {
            item.health_check_callback_name = item['health_check_callback_' + item.health_check_callback_type];
        }

        var invocation_fields = [
            'scheduler_run_every', 'scheduler_run_unit', 'scheduler_start_date', 'scheduler_job_id',
            'request_method', 'request_query_string', 'request_path_params', 'request_headers',
            'request_data', 'request_data_mode',
            'response_map', 'response_map_mode',
            'callback_type', 'callback_name',
            'health_check_run_every', 'health_check_run_unit', 'health_check_notify_on',
            'health_check_job_id', 'health_check_callback_type', 'health_check_callback_name'
        ];
        $.each(invocation_fields, function(ignored, name) {
            row += String.format("<td class='ignore'>{0}</td>", item[name] ? item[name] : '');
        });
    }

    if(include_tr) {
        row += '</tr>';
    }

    return row;

}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

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

$.fn.zato.http_soap.data_table.toggle_validate_tls = function(suffix, is_suds) {
    $(String.format('#id_{0}validate_tls', suffix)).prop('disabled', is_suds);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.http_soap.data_table.on_serialization_change = function() {

    var is_edit = this.id.indexOf('edit') > 1;
    var suffix = is_edit ? 'edit-' : '';
    $.fn.zato.http_soap.data_table.toggle_validate_tls(suffix, this.value == 'suds');
}

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
    var is_channel = connection === 'channel';

    var create_configs = [
        {
            object_type: 'security',
            target_select: '#id_security'
        }
    ];

    var edit_configs = [
        {
            object_type: 'security',
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
