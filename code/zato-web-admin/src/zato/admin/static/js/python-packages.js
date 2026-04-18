$.fn.zato.python_packages = {};

$.fn.zato.python_packages.countPackages = function(requirements) {
    var lines = requirements.split('\n');
    var count = 0;
    for (var i = 0; i < lines.length; i++) {
        var line = lines[i].trim();
        if (line && !line.startsWith('#') && !line.startsWith('-')) {
            count++;
        }
    }
    return count;
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

$(document).ready(function() {

    var config = {};
    config.textareaId = 'requirements';
    config.apiPrefix = '/zato/python-packages/';
    config.testUrl = '/zato/python-packages/test-packages';
    config.saveUrl = '/zato/python-packages/save-config';
    config.showRestartSteps = true;
    config.saveProgressLabel = 'Installing packages...';
    config.saveSuccessLabel = 'Packages installed';
    config.saveErrorLabel = 'Installation failed';
    config.restartCompletedText = 'All components restarted';

    config.buildTestPayload = function() {
        return { requirements: $('#requirements').val() };
    };

    config.buildSavePayload = function() {
        return { requirements: $('#requirements').val() };
    };

    config.showTestResults = $.fn.zato.python_packages.showTestResults;

    var packageCount = 0;

    config.restartBadgeText = 'Packages installed successfully';

    config.onSaveSuccess = function() {
        var count = $.fn.zato.python_packages.countPackages($('#requirements').val());
        config.restartBadgeText = count === 1 ? 'Package installed successfully' : 'Packages installed successfully';
        var installedText = count === 1 ? 'Package installed' : 'Packages installed';
        $.fn.zato.settings.updateProgress('configure', 'completed', installedText);
    };

    config.tourSteps = [];

    config.tourSteps[0] = {};
    config.tourSteps[0].popover = {};
    config.tourSteps[0].popover.title = 'Python packages';
    config.tourSteps[0].popover.description = 'Enter your Python package requirements in the textarea below. ' +
        'Use the same format as a <strong>requirements.txt</strong> file.<br><br>' +
        'For example:<br><code>requests==2.31.0</code><br><code>pandas>=2.0.0</code>';

    config.tourSteps[1] = {};
    config.tourSteps[1].element = '#check-button';
    config.tourSteps[1].popover = {};
    config.tourSteps[1].popover.title = 'Test packages';
    config.tourSteps[1].popover.description = 'Click this button to verify that the packages exist on PyPI ' +
        'before installing them.<br><br>' +
        'Packages from custom indexes or git repositories will be <strong>skipped</strong>.';

    config.tourSteps[2] = {};
    config.tourSteps[2].element = '#update-button';
    config.tourSteps[2].popover = {};
    config.tourSteps[2].popover.title = 'Save and install';
    config.tourSteps[2].popover.description = 'Click this button to save the requirements and install the packages.<br><br>' +
        'After installation, all Zato components will be <strong>restarted</strong> to load the new packages.';

    $.fn.zato.textarea_settings.init(config);
});
