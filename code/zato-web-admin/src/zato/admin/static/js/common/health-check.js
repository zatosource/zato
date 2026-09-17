
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Health check tab - a generic component attachable to any connection type that has a ping.
// Pages include this file next to health-check-tab.html and call $.fn.zato.health_check.populate('edit', item)
// when the edit form opens. Each ping's outcome lands in the connection's audit log under its health source,
// which is what the Alerts tab's rules read.
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// UI defaults for connections that never configured a health check - the select
// names a unit in the singular, the way the form's own choices do
$.fn.zato.health_check.config = {
    defaultRunUnit: 'minute'
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// Fills the tab's widgets from a data table item when a form opens
$.fn.zato.health_check.populate = function(action, item) {

    var suffix = action === 'edit' ? 'edit-' : '';
    var config = $.fn.zato.health_check.config;

    // The data table cells always carry these fields, empty for connections without a health check
    var runUnit = item.health_check_run_unit;
    if(!runUnit) {
        runUnit = config.defaultRunUnit;
    }

    $('#id_' + suffix + 'health_check_run_every').val(item.health_check_run_every);
    $('#id_' + suffix + 'health_check_run_unit').val(runUnit);
    $('#id_' + suffix + 'health_check_job_id').val(item.health_check_job_id);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// Field descriptions merged into a page's how-it-works map
$.fn.zato.health_check.field_descriptions = {
    'id_health_check_run_every': 'How often this connection is pinged, e.g. every 5 minutes. ' +
        'Leave empty for no health checks. A failed ping counts towards the alerts of the Alerts tab.'
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
