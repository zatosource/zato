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
    config.useCustomStatus = true;
    config.resultLabelKey = 'package';

    config.getKeyFromLine = function(lineText) {
        var trimmed = lineText.trim();
        if (!trimmed || trimmed.startsWith('#') || trimmed.startsWith('-')) return null;
        var match = trimmed.match(/^([a-zA-Z0-9_-]+)/);
        return match ? match[1] : null;
    };

    config.renderMessage = function(result) {
        if (result.status === 'ok') {
            var pypiUrl = 'https://pypi.org/project/' + result.package + '/';
            return '<span class="result-message"><a href="' + pypiUrl + '" target="_blank">' + result.message + '</a></span>';
        }
        return '<span class="result-message">' + $.fn.zato.textarea_settings.escapeHtml(result.message || '') + '</span>';
    };

    config.buildTestPayload = function() {
        return {
            requirements: $('#requirements').val(),
            allow_delete: $('#allow-delete-toggle').is(':checked')
        };
    };

    config.buildSavePayload = function() {
        return {
            requirements: $('#requirements').val(),
            allow_delete: $('#allow-delete-toggle').is(':checked')
        };
    };

    config.restartBadgeText = 'Packages installed successfully';

    config.onSaveSuccess = function() {
        var lines = $('#requirements').val().split('\n');
        var count = 0;
        for (var i = 0; i < lines.length; i++) {
            var line = lines[i].trim();
            if (line && !line.startsWith('#') && !line.startsWith('-')) {
                count++;
            }
        }
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
