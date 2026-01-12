$.fn.zato.datadog = {};

$.fn.zato.datadog.init = function() {
    $('#check-button').on('click', $.fn.zato.datadog.handleTestConnection);
    $('#update-button').on('click', $.fn.zato.datadog.handleSaveClick);
    
    const toggle = $('#is-enabled');
    const container = $('.progress-panel');
    const mainAgentInput = $('#main-agent');
    const metricsAgentInput = $('#metrics-agent');
    const saveButton = $('#update-button');
    
    console.log('datadog.init: toggle checked:', toggle.is(':checked'));
    console.log('datadog.init: main_agent value:', mainAgentInput.val());
    console.log('datadog.init: metrics_agent value:', metricsAgentInput.val());
    
    function updateSaveButtonState() {
        saveButton.prop('disabled', false);
    }
    
    function updateFieldsState(isEnabled) {
        console.log('updateFieldsState: isEnabled =', isEnabled);
        const fieldsToToggle = container.find('input:not(#is-enabled), select, button');
        console.log('updateFieldsState: found', fieldsToToggle.length, 'fields to toggle');
        fieldsToToggle.prop('disabled', !isEnabled);
        if (isEnabled) {
            updateSaveButtonState();
        }
    }
    
    const initialEnabled = toggle.is(':checked');
    console.log('datadog.init: setting initial state, isEnabled =', initialEnabled);
    updateFieldsState(initialEnabled);
    
    mainAgentInput.on('input', updateSaveButtonState);
    metricsAgentInput.on('input', updateSaveButtonState);
    
    toggle.on('change', function() {
        const isEnabled = $(this).is(':checked');
        console.log('toggle.onChange: isEnabled =', isEnabled);
        updateFieldsState(isEnabled);
        
        $.ajax({
            url: '/zato/monitoring/datadog/toggle-enabled',
            type: 'POST',
            headers: {
                'X-CSRFToken': $.cookie('csrftoken')
            },
            data: JSON.stringify({
                is_enabled: isEnabled
            }),
            contentType: 'application/json',
            success: function() {
                console.log('toggle-enabled: success');
            },
            error: function(xhr) {
                console.error('toggle-enabled: error', xhr);
            }
        });
    });

    const tours = {};

    tours.connectionInfo = {};
    tours.connectionInfo.trigger = '#version-info-help';
    tours.connectionInfo.steps = [];

    tours.connectionInfo.steps[0] = {};
    tours.connectionInfo.steps[0].popover = {};
    tours.connectionInfo.steps[0].popover.title = 'Connection info';
    tours.connectionInfo.steps[0].popover.description = 'Lorem ipsum dolor sit amet, <strong>consectetur adipiscing elit</strong>. ' +
        'Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.<br><br>' +
        'Ut enim ad minim veniam, <span style="color: #067f39;">quis nostrud exercitation</span> ' +
        'ullamco laboris nisi ut aliquip ex ea commodo consequat.';

    tours.connectionInfo.steps[1] = {};
    tours.connectionInfo.steps[1].element = '#check-button';
    tours.connectionInfo.steps[1].popover = {};
    tours.connectionInfo.steps[1].popover.title = 'Test connection';
    tours.connectionInfo.steps[1].popover.description = 'Lorem ipsum dolor sit amet, <strong>consectetur adipiscing elit</strong>. ' +
        'Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.<br><br>' +
        'Ut enim ad minim veniam, <span style="color: #067f39;">quis nostrud exercitation</span> ' +
        'ullamco laboris nisi ut aliquip ex ea commodo consequat.';

    tours.connectionInfo.steps[2] = {};
    tours.connectionInfo.steps[2].element = '#update-button';
    tours.connectionInfo.steps[2].popover = {};
    tours.connectionInfo.steps[2].popover.title = 'Save configuration';
    tours.connectionInfo.steps[2].popover.description = 'Lorem ipsum dolor sit amet, <strong>consectetur adipiscing elit</strong>. ' +
        'Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.<br><br>' +
        'Ut enim ad minim veniam, <span style="color: #067f39;">quis nostrud exercitation</span> ' +
        'ullamco laboris nisi ut aliquip ex ea commodo consequat.<br><br>' +
        'Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.';

    tours.config = {};
    tours.config.trigger = '#auto-update-help';
    tours.config.steps = [];

    tours.config.steps[0] = {};
    tours.config.steps[0].popover = {};
    tours.config.steps[0].popover.title = 'Config';
    tours.config.steps[0].popover.description = 'Lorem ipsum dolor sit amet, <strong>consectetur adipiscing elit</strong>. ' +
        'Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.<br><br>' +
        'Ut enim ad minim veniam, <span style="color: #067f39;">quis nostrud exercitation</span> ' +
        'ullamco laboris nisi ut aliquip ex ea commodo consequat.';

    tours.config.steps[1] = {};
    tours.config.steps[1].element = '.config-item';
    tours.config.steps[1].popover = {};
    tours.config.steps[1].popover.title = 'Auto-update';
    tours.config.steps[1].popover.description = 'Lorem ipsum dolor sit amet, <strong>consectetur adipiscing elit</strong>. ' +
        'Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.<br><br>' +
        'Ut enim ad minim veniam, <span style="color: #067f39;">quis nostrud exercitation</span> ' +
        'ullamco laboris nisi ut aliquip ex ea commodo consequat.<br><br>' +
        'Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.';

    tours.logs = {};
    tours.logs.trigger = '#logs-help';
    tours.logs.steps = [];

    tours.logs.steps[0] = {};
    tours.logs.steps[0].popover = {};
    tours.logs.steps[0].popover.title = 'Logs';
    tours.logs.steps[0].popover.description = 'Lorem ipsum dolor sit amet, <strong>consectetur adipiscing elit</strong>. ' +
        'Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.<br><br>' +
        'Ut enim ad minim veniam, <span style="color: #067f39;">quis nostrud exercitation</span> ' +
        'ullamco laboris nisi ut aliquip ex ea commodo consequat.';

    tours.logs.steps[1] = {};
    tours.logs.steps[1].element = '.dashboard-link-item';
    tours.logs.steps[1].popover = {};
    tours.logs.steps[1].popover.title = 'Download logs';
    tours.logs.steps[1].popover.description = 'Lorem ipsum dolor sit amet, <strong>consectetur adipiscing elit</strong>. ' +
        'Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.<br><br>' +
        'Ut enim ad minim veniam, <span style="color: #067f39;">quis nostrud exercitation</span> ' +
        'ullamco laboris nisi ut aliquip ex ea commodo consequat.<br><br>' +
        'Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.';

    $.fn.zato.settings.initDriverTours(Object.values(tours));
};

$.fn.zato.datadog.handleTestConnection = function() {
    $('#progress-test').addClass('hidden').removeClass('error-state');
    const statusMessage = $('.status-message.test-success');
    statusMessage.removeClass('show fade');
    
    $.fn.zato.settings.activateSpinner('.button-spinner');

    $.ajax({
        url: '/zato/monitoring/datadog/test-connection',
        type: 'POST',
        headers: {
            'X-CSRFToken': $.cookie('csrftoken')
        },
        data: JSON.stringify({
            main_agent: $('#main-agent').val(),
            metrics_agent: $('#metrics-agent').val()
        }),
        contentType: 'application/json',
        success: function(response) {
            $.fn.zato.settings.deactivateSpinner('.button-spinner');
            statusMessage.addClass('show');
            setTimeout(function() {
                statusMessage.addClass('fade');
                setTimeout(function() {
                    statusMessage.removeClass('show fade');
                }, 500);
            }, 3000);
        },
        error: function(xhr) {
            $.fn.zato.settings.deactivateSpinner('.button-spinner');
            
            let errorMsg = 'Connection test failed';
            try {
                const response = JSON.parse(xhr.responseText);
                if (response.errors && response.errors.length) {
                    errorMsg = response.errors.join('<br/>');
                } else if (response.error) {
                    errorMsg = response.error;
                }
            } catch(e) {
                errorMsg = xhr.responseText || errorMsg;
            }

            $('#progress-test').removeClass('hidden').data('full-error', errorMsg);
            $.fn.zato.settings.updateProgress('test', 'error', errorMsg);
        }
    });
};

$.fn.zato.datadog.handleSaveClick = function() {
    const button = $(this);
    button.prop('disabled', true);

    $('#progress-test').addClass('hidden').removeClass('error-state');

    $('#progress-configure').removeClass('hidden error-state');
    $('#progress-install').addClass('hidden').removeClass('error-state');
    $('#progress-install .info-message').removeClass('show');
    $.fn.zato.settings.updateProgress('configure', 'processing', 'Configuring...');

    $.ajax({
        url: '/zato/monitoring/datadog/save-config',
        type: 'POST',
        headers: {
            'X-CSRFToken': $.cookie('csrftoken')
        },
        data: JSON.stringify({
            is_enabled: $('#is-enabled').is(':checked'),
            main_agent: $('#main-agent').val(),
            metrics_agent: $('#metrics-agent').val()
        }),
        contentType: 'application/json',
        success: function(response) {
            $.fn.zato.settings.updateProgress('configure', 'completed', 'Configuration complete');

            $('#progress-install').removeClass('hidden');
            $.fn.zato.datadog.runRestartSteps(button);
        },
        error: function(xhr) {
            let errorMsg = 'Configure failed';
            let fullError = errorMsg;
            try {
                const response = JSON.parse(xhr.responseText);
                errorMsg = response.error || errorMsg;
                fullError = errorMsg;
            } catch(e) {
                errorMsg = xhr.responseText || errorMsg;
                fullError = errorMsg;
            }

            $('#progress-configure').data('full-error', fullError);
            $.fn.zato.settings.updateProgress('configure', 'error', errorMsg);
            button.prop('disabled', false);
        }
    });
};

$.fn.zato.datadog.runRestartSteps = function(button) {
    const config = {};
    config.progressKey = 'install';
    config.button = button;
    config.pollUrl = '/zato/monitoring/datadog/';
    config.completedText = 'All components restarted';
    config.completionBadgeSelector = '#progress-install .info-message';
    config.baseUrl = '/zato/updates';
    config.completionBadgeText = '⭐ Datadog configured successfully';

    $.fn.zato.settings.executeSteps(config);
};

$(document).ready(function() {
    $.fn.zato.datadog.init();
});
