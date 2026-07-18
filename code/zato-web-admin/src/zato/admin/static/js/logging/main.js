(function($) {

$.fn.zato.logging.config = {
    clusterId: '1',
    testUrl: '/zato/logging/test',
    saveUrl: '/zato/logging/save',
    destinationSaveUrl: '/zato/logging/destination/save',
    destinationDeleteUrl: '/zato/logging/destination/delete',
    destinationPingUrl: '/zato/logging/destination/ping',
    datadogDefaultAddress: 'https://http-intake.logs.datadoghq.com/api/v2/logs',
    statusClearMs: 4000,
    vendors: ['splunk', 'datadog', 'grafana']
};

// ////////////////////////////////////////////////////////////////////////
// State
// ////////////////////////////////////////////////////////////////////////

$.fn.zato.logging._tabHandle = null;

// ////////////////////////////////////////////////////////////////////////
// Status messages
// ////////////////////////////////////////////////////////////////////////

$.fn.zato.logging.setStatus = function(tabName, text, statusClass) {
    var config = $.fn.zato.logging.config;
    var $statusMessage = $('#logging-status-' + tabName);

    $statusMessage.text(text).removeClass('logging-status-saved logging-status-error');

    if (statusClass) {
        $statusMessage.addClass(statusClass);
    }

    // Clear the message after a while, unless it is an error.
    if (statusClass !== 'logging-status-error') {
        setTimeout(function() {
            $statusMessage.text('');
        }, config.statusClearMs);
    }
};

// ////////////////////////////////////////////////////////////////////////
// Initialization
// ////////////////////////////////////////////////////////////////////////

$.fn.zato.logging.init = function(pageData) {
    var logging = $.fn.zato.logging;
    var kit = $.fn.zato.dashboard_kit;

    logging._tabHandle = kit.tabs.init({
        tab_selector: '.logging-card .dashboard-tab',
        panel_prefix: 'logging-tab-panel-',
        default_tab: kit.url_state.get('tab'),
        on_change: function(tabName) {
            kit.url_state.set({tab: tabName});
        }
    });

    // .. handle browser back/forward ..
    kit.url_state.on_pop(function(params) {
        var popTab = params.get('tab');
        if (popTab) {
            logging._tabHandle.set_tab(popTab, true);
        }
    });

    // .. the logger levels editor ..
    logging.levels.init(pageData.logging_text);

    // .. the per-vendor destination lists ..
    logging.destinations.init(pageData.destinations);

    // .. fade in.
    kit.reveal();
};

})(jQuery);
