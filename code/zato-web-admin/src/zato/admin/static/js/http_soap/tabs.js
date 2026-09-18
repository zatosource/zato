// /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// The tabs of a channel's and an outgoing connection's create and edit forms - which page kind carries which strip,
// the scheduler's date pickers, the request parameter rows, the callback widgets and the Alerts tab's bindings.
// /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.http_soap.tabs = {};

// /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// What the page binds once it is ready - the Alerts tab's config and live updates, the parameter rows' remove links,
// the date pickers of the deprecation and scheduler fields and the callback widget matching the type selected.
$.fn.zato.http_soap.tabs.init = function() {

    if($.fn.zato.http_soap.has_alerts_tab()) {
        $.fn.zato.alerts_tab.init({config_id: 'http-soap-alerts-tab-config'});
        $.fn.zato.live_form_updates.register('create', $.fn.zato.alerts_tab.live_configs(''));
        $.fn.zato.live_form_updates.register('edit', $.fn.zato.alerts_tab.live_configs('edit-'));
    }

    // Removing a request parameter row
    $(document).on('click', '.request-param-remove', function() {
        $(this).closest('.request-param-row').remove();
        return false;
    });

    if($.fn.zato.http_soap.is_rest_channel()) {

        // Attach date-time pickers to the deprecation sunset date fields in both popups
        $.fn.zato.http_soap.attach_datetimepicker(['#id_deprecation_sunset', '#id_edit-deprecation_sunset']);
    }

    if($.fn.zato.http_soap.is_rest_outgoing()) {

        // The Delivery tab's popover is set up once for both popups
        $.fn.zato.delivery_tab.init();

        // Attach date-time pickers to the scheduler start date fields in both popups ..
        $.fn.zato.http_soap.attach_datetimepicker(['#id_scheduler_start_date', '#id_edit-scheduler_start_date']);

        // .. and show the callback widget matching the callback type selected.
        $.each(['create', 'edit'], function(ignored, action) {
            var suffix = action === 'edit' ? 'edit-' : '';
            $('#id_' + suffix + 'callback_type').change(function() {
                $.fn.zato.http_soap.toggle_callback(action);
            });
            $.fn.zato.http_soap.toggle_callback(action);
        });
    }
}

// /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.http_soap.is_rest_outgoing = function() {
    var connection = $('input[name="connection"]').val();
    var transport = $('input[name="transport"]').val();
    return connection === 'outgoing' && transport === 'plain_http';
}

$.fn.zato.http_soap.is_rest_channel = function() {
    var connection = $('input[name="connection"]').val();
    var transport = $('input[name="transport"]').val();
    return connection === 'channel' && transport === 'plain_http';
}

// A channel of either transport and an outgoing REST connection carry the Alerts tab -
// the Django side decides, the page carries its answer in the tab's config element
$.fn.zato.http_soap.has_alerts_tab = function() {
    var configElement = document.getElementById('http-soap-alerts-tab-config');
    var out = configElement !== null;
    return out;
}

// A channel's dialog has a strip of its own - Main and Alerts - where an outgoing connection's Alerts tab joins the strip it has
$.fn.zato.http_soap.has_channel_tabs = function() {
    var connection = $('input[name="connection"]').val();
    var out = $.fn.zato.http_soap.has_alerts_tab() && connection === 'channel';
    return out;
}

$.fn.zato.http_soap.attach_datetimepicker = function(picker_ids) {
    $.each(picker_ids, function(ignored, picker_id) {
        $(picker_id).datetimepicker(
            {
                'dateFormat':$('#js_date_format').val(),
                'timeFormat':$('#js_time_format').val(),
                'ampm':$.fn.zato.to_bool($('#js_ampm').val()),
            }
        );
    });
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// The tabs of an outgoing REST connection's create and edit forms
$.fn.zato.http_soap.outgoingTabLabels = function() {
    var out = {
        config:       'Config',
        alerts:       $.fn.zato.alerts_tab.tab_label(),
        scheduler:    'Scheduler',
        delivery:     'Delivery',
        request:      'Request',
        response:     'Response',
        callback:     'Callback'
    };
    return out;
}

// The tabs of a REST or SOAP channel's create and edit forms
$.fn.zato.http_soap.channelTabLabels = function() {
    var out = {
        main:   'Main',
        alerts: $.fn.zato.alerts_tab.tab_label()
    };
    return out;
}

$.fn.zato.http_soap.reset_tabs = function(action) {

    var is_edit = action === 'edit';
    var default_tab = null;
    var tab_labels = null;

    if($.fn.zato.http_soap.is_rest_outgoing()) {
        default_tab = 'config';
        tab_labels = $.fn.zato.http_soap.outgoingTabLabels();
    }
    else if($.fn.zato.http_soap.has_channel_tabs()) {
        default_tab = 'main';
        tab_labels = $.fn.zato.http_soap.channelTabLabels();
    }

    if(default_tab === null) {
        return;
    }

    $.fn.zato.form_tabs.reset({
        div_id:       is_edit ? '#edit-div' : '#create-div',
        panel_prefix: is_edit ? 'http-soap-edit-tab-panel-' : 'http-soap-create-tab-panel-',
        default_tab:  default_tab,
        tab_labels:   tab_labels
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
    var remove_link = $('<a href="javascript:void(0)" class="request-param-remove" title="Remove" aria-label="Remove"></a>');
    remove_link.append($.fn.zato.new_remove_icon());
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

    // A saved popup rebuilds its row, so the row's menus are given anew
    // once the new markup is in the table.
    $.fn.zato.data_table.on_submit_complete_callback = function() {
        $.fn.zato.http_soap.inline.init_service_menus();
        $.fn.zato.http_soap.inline.init_security_menus();
    };

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

// /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
