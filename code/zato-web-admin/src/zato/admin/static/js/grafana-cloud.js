$.fn.zato.grafanaCloud = {};

$.fn.zato.grafanaCloud.init = function() {
    $('#check-button').on('click', $.fn.zato.grafanaCloud.handleTestConnection);
    $('#update-button').on('click', $.fn.zato.grafanaCloud.handleSaveClick);
    
    const toggle = $('#is-enabled');
    const container = $('.progress-panel');
    const instanceIdInput = $('#instance-id');
    const apiKeyInput = $('#api-key');
    const endpointInput = $('#endpoint');
    const saveButton = $('#update-button');
    
    console.log('grafanaCloud.init: toggle checked:', toggle.is(':checked'));
    console.log('grafanaCloud.init: instance_id value:', instanceIdInput.val());
    console.log('grafanaCloud.init: api_key value:', apiKeyInput.val());
    console.log('grafanaCloud.init: endpoint value:', endpointInput.val());
    
    function updateSaveButtonState() {
        const instanceId = instanceIdInput.val().trim();
        const apiKey = apiKeyInput.val().trim();
        const endpoint = endpointInput.val().trim();
        const hasValues = instanceId.length > 0 && apiKey.length > 0 && endpoint.length > 0;
        saveButton.prop('disabled', !hasValues);
        console.log('updateSaveButtonState: instanceId length =', instanceId.length, ', apiKey length =', apiKey.length, ', endpoint length =', endpoint.length, ', disabled =', !hasValues);
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
    console.log('grafanaCloud.init: setting initial state, isEnabled =', initialEnabled);
    updateFieldsState(initialEnabled);
    
    instanceIdInput.on('input', updateSaveButtonState);
    apiKeyInput.on('input', updateSaveButtonState);
    endpointInput.on('input', updateSaveButtonState);
    
    toggle.on('change', function() {
        const isEnabled = $(this).is(':checked');
        console.log('toggle.onChange: isEnabled =', isEnabled);
        updateFieldsState(isEnabled);
        
        $.ajax({
            url: '/zato/monitoring/grafana-cloud/toggle-enabled',
            type: 'POST',
            headers: {
                'X-CSRFToken': $.cookie('csrftoken')
            },
            data: JSON.stringify({
                is_enabled: isEnabled
            }),
            contentType: 'application/json',
            success: function(response) {
                console.log('toggle-enabled: success', response);
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

$.fn.zato.grafanaCloud.handleTestConnection = function() {
    console.log('handleTestConnection: starting');
    $('#progress-test').addClass('hidden').removeClass('error-state');
    const statusMessage = $('.status-message.test-success');
    statusMessage.removeClass('show fade');
    
    $.fn.zato.settings.activateSpinner('.button-spinner');

    const requestData = {
        instance_id: $('#instance-id').val(),
        api_key: $('#api-key').val(),
        endpoint: $('#endpoint').val()
    };
    console.log('handleTestConnection: request data:', JSON.stringify(requestData));

    $.ajax({
        url: '/zato/monitoring/grafana-cloud/test-connection',
        type: 'POST',
        headers: {
            'X-CSRFToken': $.cookie('csrftoken')
        },
        data: JSON.stringify(requestData),
        contentType: 'application/json',
        success: function(response) {
            console.log('handleTestConnection: success response:', JSON.stringify(response));
            $.fn.zato.settings.deactivateSpinner('.button-spinner');
            statusMessage.addClass('show');
            setTimeout(function() {
                statusMessage.addClass('fade');
                setTimeout(function() {
                    statusMessage.removeClass('show fade');
                }, 500);
            }, 3000);
        },
        error: function(xhr, status, error) {
            console.log('handleTestConnection: error status:', status);
            console.log('handleTestConnection: error:', error);
            console.log('handleTestConnection: xhr.status:', xhr.status);
            console.log('handleTestConnection: xhr.responseText:', xhr.responseText);
            $.fn.zato.settings.deactivateSpinner('.button-spinner');
            
            let errorMsg = 'Connection test failed';
            let fullError = errorMsg;
            try {
                const response = JSON.parse(xhr.responseText);
                errorMsg = response.error || errorMsg;
                fullError = errorMsg;
                console.log('handleTestConnection: parsed error:', errorMsg);
            } catch(e) {
                errorMsg = xhr.responseText || errorMsg;
                fullError = errorMsg;
                console.log('handleTestConnection: raw error:', errorMsg);
            }

            $('#progress-test').removeClass('hidden').data('full-error', fullError);
            $.fn.zato.settings.updateProgress('test', 'error', errorMsg);
        }
    });
};

$.fn.zato.grafanaCloud.handleSaveClick = function() {
    const button = $(this);
    button.prop('disabled', true);

    $('#progress-test').addClass('hidden').removeClass('error-state');

    $('#progress-configure').removeClass('hidden error-state');
    $('#progress-install').addClass('hidden').removeClass('error-state');
    $('#progress-install .info-message').removeClass('show');
    $.fn.zato.settings.updateProgress('configure', 'processing', 'Configuring...');

    $.ajax({
        url: '/zato/monitoring/grafana-cloud/save-config',
        type: 'POST',
        headers: {
            'X-CSRFToken': $.cookie('csrftoken')
        },
        data: JSON.stringify({
            is_enabled: $('#is-enabled').is(':checked'),
            instance_id: $('#instance-id').val(),
            api_key: $('#api-key').val(),
            endpoint: $('#endpoint').val()
        }),
        contentType: 'application/json',
        success: function(response) {
            $.fn.zato.settings.updateProgress('configure', 'completed', 'Configuration complete');

            $('#progress-install').removeClass('hidden');
            const isEnabled = $('#is-enabled').is(':checked');
            $.fn.zato.updates.runRestartSteps(button, isEnabled);
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

$.fn.zato.updates.runRestartSteps = function(button, isEnabled) {
    const config = {};
    config.progressKey = 'install';
    config.button = button;
    config.pollUrl = '/zato/monitoring/grafana-cloud/';
    config.completedText = 'All components restarted';
    config.completionBadgeSelector = '#progress-install .info-message';
    config.baseUrl = '/zato/updates';
    config.completionBadgeText = isEnabled ? '⭐ Grafana Cloud configured successfully' : '⭐ Grafana Cloud disabled successfully';

    $.fn.zato.settings.executeSteps(config);
};

$(document).ready(function() {
    $.fn.zato.grafanaCloud.init();
});
