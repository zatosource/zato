$.fn.zato.python_packages = {};

$.fn.zato.python_packages.init = function() {
    $('#check-button').on('click', $.fn.zato.python_packages.handleTestPackages);
    $('#update-button').on('click', $.fn.zato.python_packages.handleSaveClick);

    var tours = {};

    tours.connectionInfo = {};
    tours.connectionInfo.trigger = '#version-info-help';
    tours.connectionInfo.steps = [];

    tours.connectionInfo.steps[0] = {};
    tours.connectionInfo.steps[0].popover = {};
    tours.connectionInfo.steps[0].popover.title = 'Python packages';
    tours.connectionInfo.steps[0].popover.description = 'Enter your Python package requirements in the textarea below. ' +
        'Use the same format as a <strong>requirements.txt</strong> file.<br><br>' +
        'For example:<br><code>requests==2.31.0</code><br><code>pandas>=2.0.0</code>';

    tours.connectionInfo.steps[1] = {};
    tours.connectionInfo.steps[1].element = '#check-button';
    tours.connectionInfo.steps[1].popover = {};
    tours.connectionInfo.steps[1].popover.title = 'Test packages';
    tours.connectionInfo.steps[1].popover.description = 'Click this button to verify that the packages exist on PyPI ' +
        'before installing them.<br><br>' +
        'Packages from custom indexes or git repositories will be <strong>skipped</strong>.';

    tours.connectionInfo.steps[2] = {};
    tours.connectionInfo.steps[2].element = '#update-button';
    tours.connectionInfo.steps[2].popover = {};
    tours.connectionInfo.steps[2].popover.title = 'Save and install';
    tours.connectionInfo.steps[2].popover.description = 'Click this button to save the requirements and install the packages.<br><br>' +
        'After installation, all Zato components will be <strong>restarted</strong> to load the new packages.';

    $.fn.zato.settings.initDriverTours(Object.values(tours));
};

$.fn.zato.python_packages.handleTestPackages = function() {
    $('#progress-test').addClass('hidden').removeClass('error-state');
    $('#progress-configure').addClass('hidden').removeClass('error-state');
    $('#progress-scheduler').addClass('hidden');
    $('#progress-server').addClass('hidden');
    $('#progress-proxy').addClass('hidden');
    $('#progress-dashboard').addClass('hidden');
    var statusMessage = $('.status-message.test-success');
    statusMessage.removeClass('show fade');

    $.fn.zato.settings.activateSpinner('.button-spinner');

    $.ajax({
        url: '/zato/python-packages/test-packages',
        type: 'POST',
        headers: {
            'X-CSRFToken': $.cookie('csrftoken')
        },
        data: JSON.stringify({
            requirements: $('#requirements').val()
        }),
        contentType: 'application/json',
        success: function(response) {
            $.fn.zato.settings.deactivateSpinner('.button-spinner');
            statusMessage.addClass('show');

            if (response.results && response.results.length) {
                $.fn.zato.python_packages.showTestResults(response.results);
            }

            setTimeout(function() {
                statusMessage.addClass('fade');
                setTimeout(function() {
                    statusMessage.removeClass('show fade');
                }, 500);
            }, 3000);
        },
        error: function(xhr) {
            $.fn.zato.settings.deactivateSpinner('.button-spinner');

            var errorMsg = 'Test failed';
            var results = [];
            try {
                var response = JSON.parse(xhr.responseText);
                if (response.error) {
                    errorMsg = response.error;
                }
                if (response.results) {
                    results = response.results;
                }
            } catch(e) {
                errorMsg = xhr.responseText || errorMsg;
            }

            if (results.length) {
                $.fn.zato.python_packages.showTestResults(results);
            }

            // Results table shows the error, no need for progress panel
            
        }
    });
};

$.fn.zato.python_packages.showTestResults = function(results) {
    var existingResults = $('.test-results');
    if (existingResults.length) {
        existingResults.remove();
    }

    var html = '<div class="test-results">';
    for (var i = 0; i < results.length; i++) {
        var result = results[i];
        var statusClass = result.status;
        var statusText = result.status === 'ok' ? 'OK' : result.status.charAt(0).toUpperCase() + result.status.slice(1);
        html += '<div class="result-item">';
        html += '<span class="result-package">' + result.package + '</span>';
        html += '<span class="result-status-cell"><span class="result-status ' + statusClass + '">' + statusText + '</span></span>';
        if (result.status === 'ok') {
            var pypiUrl = 'https://pypi.org/project/' + result.package + '/';
            html += '<span class="result-message"><a href="' + pypiUrl + '" target="_blank">' + result.message + '</a></span>';
        } else {
            html += '<span class="result-message">' + result.message + '</span>';
        }
        html += '</div>';
    }
    html += '</div>';

    $('.button-container').after(html);
};

$.fn.zato.python_packages.handleSaveClick = function() {
    var requirements = $('#requirements').val().trim();
    if (!requirements) {
        return;
    }

    var button = $(this);
    button.prop('disabled', true);

    $('#progress-test').addClass('hidden').removeClass('error-state');
    $('#progress-configure').addClass('hidden').removeClass('error-state');
    $('#progress-scheduler').addClass('hidden');
    $('#progress-server').addClass('hidden');
    $('#progress-proxy').addClass('hidden');
    $('#progress-dashboard').addClass('hidden');
    $('.test-results').remove();

    $('#progress-configure').removeClass('hidden error-state');
    $('#progress-install').addClass('hidden').removeClass('error-state');
    $('#progress-install .info-message').removeClass('show');
    $.fn.zato.settings.updateProgress('configure', 'processing', 'Installing packages...');

    $.ajax({
        url: '/zato/python-packages/save-config',
        type: 'POST',
        headers: {
            'X-CSRFToken': $.cookie('csrftoken')
        },
        data: JSON.stringify({
            requirements: $('#requirements').val()
        }),
        contentType: 'application/json',
        success: function(response) {
            $.fn.zato.settings.updateProgress('configure', 'completed', 'Packages installed');

            $('#progress-install').removeClass('hidden');
            $.fn.zato.python_packages.runRestartSteps(button);
        },
        error: function(xhr) {
            var errorMsg = 'Installation failed';
            var fullError = errorMsg;
            try {
                var response = JSON.parse(xhr.responseText);
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

$.fn.zato.python_packages.runRestartSteps = function(button) {
    var config = {};
    config.progressKey = 'install';
    config.button = button;
    config.pollUrl = '/zato/python-packages/';
    config.completedText = 'All components restarted';
    config.completionBadgeSelector = '#progress-install .info-message';
    config.baseUrl = '/zato/python-packages';
    config.completionBadgeText = 'Packages installed successfully';

    $.fn.zato.settings.executeSteps(config);
};

$(document).ready(function() {
    $.fn.zato.python_packages.init();
});
