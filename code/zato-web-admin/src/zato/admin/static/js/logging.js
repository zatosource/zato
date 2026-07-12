$(document).ready(function() {

    var config = {};
    config.textareaId = 'logging-config';
    config.apiPrefix = '/zato/logging/';
    config.testUrl = '/zato/logging/test';
    config.saveUrl = '/zato/logging/save';
    config.showRestartSteps = false;
    config.saveProgressLabel = 'Setting levels...';
    config.saveSuccessLabel = 'Levels saved';
    config.saveErrorLabel = 'Save failed';
    config.useCustomStatus = true;
    config.resultLabelKey = 'label';

    config.buildTestPayload = function() {
        return {
            text: $('#logging-config').val()
        };
    };

    config.buildSavePayload = function() {
        return {
            text: $('#logging-config').val()
        };
    };

    config.tourSteps = [];

    config.tourSteps[0] = {};
    config.tourSteps[0].popover = {};
    config.tourSteps[0].popover.title = 'Logging';
    config.tourSteps[0].popover.description = 'View and change log levels for the server process. ' +
        'Use <strong>logger=LEVEL</strong> format, one logger per line.';

    config.tourSteps[1] = {};
    config.tourSteps[1].element = '#check-button';
    config.tourSteps[1].popover = {};
    config.tourSteps[1].popover.title = 'Test';
    config.tourSteps[1].popover.description = 'Shows which log levels will be changed.';

    config.tourSteps[2] = {};
    config.tourSteps[2].element = '#update-button';
    config.tourSteps[2].popover = {};
    config.tourSteps[2].popover.title = 'Save';
    config.tourSteps[2].popover.description = 'Sets the log levels in the server process. ' +
        'Changes take effect immediately, without a restart.';

    $.fn.zato.textarea_settings.init(config);
});
