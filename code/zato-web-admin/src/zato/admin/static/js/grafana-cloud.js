$.fn.zato.grafanaCloud = {};

$.fn.zato.grafanaCloud.init = function() {
    $('#check-button').on('click', $.fn.zato.grafanaCloud.handleTestConnection);
    $('#update-button').on('click', $.fn.zato.grafanaCloud.handleSaveClick);
    $.fn.zato.settings.initIsEnabledToggle('#is-enabled', '.progress-panel');

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
    $('#progress-test').addClass('hidden').removeClass('error-state');
    const statusMessage = $('.status-message.test-success');
    statusMessage.removeClass('show fade');
    
    $.fn.zato.settings.activateSpinner('.button-spinner');

    $.ajax({
        url: '/zato/observability/grafana-cloud/test-connection',
        type: 'POST',
        headers: {
            'X-CSRFToken': $.cookie('csrftoken')
        },
        data: JSON.stringify({
            instance_id: $('#instance-id').val(),
            api_token: $('#api-token').val()
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
            let fullError = errorMsg;
            try {
                const response = JSON.parse(xhr.responseText);
                errorMsg = response.error || errorMsg;
                fullError = errorMsg;
            } catch(e) {
                errorMsg = xhr.responseText || errorMsg;
                fullError = errorMsg;
            }

            $('#progress-test').removeClass('hidden').data('full-error', fullError);
            $.fn.zato.settings.updateProgress('test', 'error', errorMsg);
        }
    });
};

$.fn.zato.grafanaCloud.handleSaveClick = function() {
    const button = $(this);
    button.prop('disabled', true);

    $('#progress-configure').removeClass('hidden error-state');
<<<<<<< Updated upstream
    $('#progress-scheduler').addClass('hidden').removeClass('error-state');
    $('#progress-server').addClass('hidden').removeClass('error-state');
    $('#progress-proxy').addClass('hidden').removeClass('error-state');
    $('#progress-dashboard').addClass('hidden').removeClass('error-state');
    $('#progress-test').addClass('hidden').removeClass('error-state');
    $.fn.zato.settings.updateProgress('configure', 'processing', 'Configuring...');

    $.ajax({
        url: '/zato/observability/grafana-cloud/save-configuration',
=======
    $('#progress-install').addClass('hidden').removeClass('error-state');
    $('#progress-install .info-message').removeClass('show');
    $.fn.zato.settings.updateProgress('configure', 'processing', 'Configuring...');

    $.ajax({
        url: '/zato/observability/grafana-cloud/save-config',
>>>>>>> Stashed changes
        type: 'POST',
        headers: {
            'X-CSRFToken': $.cookie('csrftoken')
        },
        data: JSON.stringify({
            is_enabled: $('#is-enabled').is(':checked'),
            instance_id: $('#instance-id').val(),
            api_token: $('#api-token').val()
        }),
        contentType: 'application/json',
        success: function(response) {
<<<<<<< Updated upstream
            $.fn.zato.settings.updateProgress('configure', 'completed', 'Configuration completed');
            $.fn.zato.grafanaCloud.runRestartSteps(button);
        },
        error: function(xhr) {
            let errorMsg = 'Save configuration failed';
=======
            $.fn.zato.settings.updateProgress('configure', 'completed', 'Configure complete');

            $('#progress-install').removeClass('hidden');
            $.fn.zato.updates.runRestartSteps(button);
        },
        error: function(xhr) {
            let errorMsg = 'Configure failed';
>>>>>>> Stashed changes
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

<<<<<<< Updated upstream
$.fn.zato.grafanaCloud.runRestartSteps = function(button) {
    const steps = [
        { key: 'scheduler', url: '/zato/observability/grafana-cloud/restart-scheduler', text: 'Restarting...' },
        { key: 'server', url: '/zato/observability/grafana-cloud/restart-server', text: 'Restarting...' },
        { key: 'proxy', url: '/zato/observability/grafana-cloud/restart-proxy', text: 'Restarting...' },
        { key: 'dashboard', url: '/zato/observability/grafana-cloud/restart-dashboard', text: 'Restarting...' }
    ];
    
    let currentStep = 0;
    
    const runNextStep = function() {
        if (currentStep >= steps.length) {
            button.prop('disabled', false);
            return;
        }
        
        const step = steps[currentStep];
        $('#progress-' + step.key).removeClass('hidden');
        $.fn.zato.settings.updateProgress(step.key, 'processing', step.text);
        
        $.ajax({
            url: step.url,
            type: 'POST',
            headers: {
                'X-CSRFToken': $.cookie('csrftoken')
            },
            success: function(response) {
                $.fn.zato.settings.updateProgress(step.key, 'completed', 'Completed');
                
                if (step.key === 'dashboard') {
                    let pollAttempts = 0;
                    const maxPollAttempts = 60;
                    
                    const pollDashboard = function() {
                        pollAttempts++;
                        $.ajax({
                            url: '/zato/observability/grafana-cloud/',
                            type: 'GET',
                            timeout: 2000,
                            success: function() {
                                currentStep++;
                                runNextStep();
                            },
                            error: function() {
                                if (pollAttempts < maxPollAttempts) {
                                    setTimeout(pollDashboard, 1000);
                                } else {
                                    $.fn.zato.settings.updateProgress(step.key, 'error', 'Dashboard did not restart');
                                    button.prop('disabled', false);
                                }
                            }
                        });
                    };
                    
                    setTimeout(pollDashboard, 2000);
                } else {
                    currentStep++;
                    setTimeout(runNextStep, 500);
                }
            },
            error: function(xhr) {
                let errorMsg = 'Restart failed';
                try {
                    const response = JSON.parse(xhr.responseText);
                    errorMsg = response.error || errorMsg;
                } catch(e) {
                    errorMsg = xhr.responseText || errorMsg;
                }
                
                $.fn.zato.settings.updateProgress(step.key, 'error', errorMsg);
                button.prop('disabled', false);
            }
        });
    };
=======
$.fn.zato.updates.runRestartSteps = function(button) {
    const config = {};
    config.progressKey = 'install';
    config.button = button;
    config.pollUrl = '/zato/observability/grafana-cloud/';
    config.completedText = 'Installation complete';
    config.completionBadgeSelector = '#progress-install .info-message';
    config.baseUrl = '/zato/updates';
    config.completionBadgeText = '⭐ Configuration saved';

    $.fn.zato.settings.executeSteps(config);
};


$.fn.zato.updates.renderAuditLogEntry = function(entry, extraClass) {
    const template = document.getElementById('audit-log-entry-template');
    const clone = template.content.cloneNode(true);
    const entryDiv = clone.querySelector('.audit-log-entry');
>>>>>>> Stashed changes
    
    runNextStep();
};

$(document).ready(function() {
    $.fn.zato.grafanaCloud.init();
});
