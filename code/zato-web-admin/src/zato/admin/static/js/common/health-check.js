
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Health check tab - a generic component attachable to any connection type that has a ping.
// Pages include this file next to health-check-tab.html and call $.fn.zato.health_check.init()
// on document ready, then $.fn.zato.health_check.populate('edit', item) when the edit form opens.
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// UI defaults for connections that never configured a health check - the empty
// callback type is the "no callback" choice of the select.
$.fn.zato.health_check.config = {
    default_run_unit: 'minutes',
    default_notify_on: 'failures',
    default_callback_type: ''
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// Attaches the callback-type change handlers to both popups
$.fn.zato.health_check.init = function() {
    $.each(['create', 'edit'], function(ignored, action) {
        var suffix = action === 'edit' ? 'edit-' : '';
        $('#id_' + suffix + 'health_check_callback_type').change(function() {
            $.fn.zato.health_check.toggle_callback(action);
        });
        $.fn.zato.health_check.toggle_callback(action);
    });
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// Shows only the callback widget matching the type selected, hiding its siblings
$.fn.zato.health_check.toggle_callback = function(action) {

    var suffix = action === 'edit' ? 'edit-' : '';
    var callback_type = $('#id_' + suffix + 'health_check_callback_type').val();

    var callback_rows = {
        'service': $('#health-check-callback-service-row-' + action),
        'topic':   $('#health-check-callback-topic-row-' + action),
        'rest':    $('#health-check-callback-rest-row-' + action)
    };

    $.each(callback_rows, function(row_type, row) {
        row.toggleClass('hidden', row_type !== callback_type);
    });
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// Fills the tab's widgets from a data table item when a form opens
$.fn.zato.health_check.populate = function(action, item) {

    var suffix = action === 'edit' ? 'edit-' : '';
    var config = $.fn.zato.health_check.config;

    // The data table cells always carry these fields, empty for connections without a health check
    var run_unit = item.health_check_run_unit;
    if(!run_unit) {
        run_unit = config.default_run_unit;
    }

    var notify_on = item.health_check_notify_on;
    if(!notify_on) {
        notify_on = config.default_notify_on;
    }

    var callback_type = item.health_check_callback_type;
    if(!callback_type) {
        callback_type = config.default_callback_type;
    }

    $('#id_' + suffix + 'health_check_run_every').val(item.health_check_run_every);
    $('#id_' + suffix + 'health_check_run_unit').val(run_unit);
    $('#id_' + suffix + 'health_check_notify_on').val(notify_on);
    $('#id_' + suffix + 'health_check_job_id').val(item.health_check_job_id);

    $('#id_' + suffix + 'health_check_callback_type').val(callback_type);

    // The one name is carried by the widget matching the callback type
    var widget_ids = {
        'service': '#id_' + suffix + 'health_check_callback_service',
        'topic':   '#id_' + suffix + 'health_check_callback_topic',
        'rest':    '#id_' + suffix + 'health_check_callback_rest'
    };
    $.each(widget_ids, function(ignored, widget_id) {
        $(widget_id).val('');
    });
    if(item.health_check_callback_name) {
        $(widget_ids[callback_type]).val(item.health_check_callback_name);
    }

    $.fn.zato.health_check.toggle_callback(action);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// Field descriptions merged into a page's how-it-works map
$.fn.zato.health_check.field_descriptions = {
    'id_health_check_run_every': 'How often this connection is pinged,<br>e.g. every 5 minutes.<br>Leave empty for no health checks.',
    'id_health_check_notify_on': 'Whether the callback hears about failures only<br>or about every ping result.',
    'id_health_check_callback_type': 'Where each health check outcome is delivered -<br>to a service, a pub/sub topic or a REST connection.',
    'id_health_check_callback_service': 'The service invoked with each outcome.',
    'id_health_check_callback_topic': 'The pub/sub topic each outcome is published to.',
    'id_health_check_callback_rest': 'The outgoing REST connection<br>each outcome is sent to.',
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
