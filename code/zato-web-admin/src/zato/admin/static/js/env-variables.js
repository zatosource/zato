$(document).ready(function() {

    var config = {};
    config.textareaId = 'env-variables';
    config.apiPrefix = '/zato/env-variables/';
    config.testUrl = '/zato/env-variables/test';
    config.saveUrl = '/zato/env-variables/save';
    config.showRestartSteps = false;
    config.saveProgressLabel = 'Setting variables...';
    config.saveSuccessLabel = 'Variables saved';
    config.saveErrorLabel = 'Save failed';
    config.useCustomStatus = true;
    config.resultLabelKey = 'label';

    config.buildTestPayload = function() {
        return {
            variables: $('#env-variables').val(),
            allow_delete: $('#allow-delete-toggle').is(':checked')
        };
    };

    config.buildSavePayload = function() {
        return {
            variables: $('#env-variables').val(),
            allow_delete: $('#allow-delete-toggle').is(':checked')
        };
    };

    config.tourSteps = [];

    config.tourSteps[0] = {};
    config.tourSteps[0].popover = {};
    config.tourSteps[0].popover.title = 'Environment variables';
    config.tourSteps[0].popover.description = 'View and edit environment variables for the server process. ' +
        'Use <strong>KEY=value</strong> format, one variable per line.';

    config.tourSteps[1] = {};
    config.tourSteps[1].element = '#check-button';
    config.tourSteps[1].popover = {};
    config.tourSteps[1].popover.title = 'Test';
    config.tourSteps[1].popover.description = 'Shows which variables will be added or changed.';

    config.tourSteps[2] = {};
    config.tourSteps[2].element = '#update-button';
    config.tourSteps[2].popover = {};
    config.tourSteps[2].popover.title = 'Save';
    config.tourSteps[2].popover.description = 'Sets the environment variables in the server process. ' +
        'Changes take effect immediately for all Python services.';

    $.fn.zato.textarea_settings.init(config);
});
