(function($) {

$.fn.zato.form_settings = {};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.form_settings.init = function(config) {

    var state = {};
    state.config = config;

    $('#check-button').on('click', function() {
        $.fn.zato.form_settings.handleTest(state);
    });

    $('#update-button').on('click', function() {
        $.fn.zato.form_settings.handleSave(state);
    });

    if (config.tourSteps) {
        var tours = {};
        tours.main = {};
        tours.main.trigger = '#version-info-help';
        tours.main.steps = config.tourSteps;
        $.fn.zato.settings.initDriverTours(Object.values(tours));
    }
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.form_settings.escapeHtml = function(text) {
    var container = document.createElement('div');
    container.appendChild(document.createTextNode(text));
    return container.innerHTML;
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.form_settings.clearResults = function() {

    // Remove any leftovers from a previous test or save ..
    $('.test-results').remove();
    $('#progress-configure').addClass('hidden').removeClass('error-state');

    // .. and reset the status message to its resting state.
    var statusMessage = $('.status-message.test-success');
    statusMessage.removeClass('show fade test-error-message').text('OK');
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.form_settings.showResultMessage = function(statusClass, statusText, messageText) {

    // Build a single result row below the buttons ..
    var escapedMessage = $.fn.zato.form_settings.escapeHtml(messageText);
    var html = '<div class="test-results">';
    html += '<div class="result-item">';
    html += '<span class="result-status-cell"><span class="result-status ' + statusClass + '">' + statusText + '</span></span>';
    html += ' <span class="result-message">' + escapedMessage + '</span>';
    html += '</div>';
    html += '</div>';

    // .. and attach it to the page.
    $('.button-container').after(html);
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.form_settings.handleTest = function(state) {

    var config = state.config;
    $.fn.zato.form_settings.clearResults();

    var statusMessage = $('.status-message.test-success');
    $.fn.zato.settings.activateSpinner('.button-spinner');

    $.ajax({
        url: config.testUrl,
        type: 'POST',
        headers: {
            'X-CSRFToken': $.cookie('csrftoken')
        },
        data: JSON.stringify(config.buildTestPayload()),
        contentType: 'application/json',
        success: function(response) {
            $.fn.zato.settings.deactivateSpinner('.button-spinner');

            // Show the OK badge along with the details of the successful test ..
            statusMessage.addClass('show');
            $.fn.zato.form_settings.showResultMessage('ok', 'OK', response.message);

            // .. and let the badge fade out on its own.
            setTimeout(function() {
                statusMessage.addClass('fade');
                setTimeout(function() {
                    statusMessage.removeClass('show fade');
                }, 500);
            }, 3000);
        },
        error: function(xhr) {
            $.fn.zato.settings.deactivateSpinner('.button-spinner');

            // Extract the error details out of the response ..
            var errorMessage = config.testErrorLabel;
            try {
                var response = JSON.parse(xhr.responseText);
                if (response.error) {
                    errorMessage = response.error;
                }
            } catch(ignored) {
                if (xhr.responseText) {
                    errorMessage = xhr.responseText;
                }
            }

            // .. and show them below the buttons, without fading.
            statusMessage.addClass('show test-error-message').text('Error');
            $.fn.zato.form_settings.showResultMessage('error', 'Error', errorMessage);
        }
    });
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.form_settings.handleSave = function(state) {

    var config = state.config;
    var button = $('#update-button');
    button.prop('disabled', true);

    $.fn.zato.form_settings.clearResults();

    // Show the progress item for the save operation ..
    $('#progress-configure').removeClass('hidden error-state');
    $.fn.zato.settings.updateProgress('configure', 'processing', config.saveProgressLabel);

    $.ajax({
        url: config.saveUrl,
        type: 'POST',
        headers: {
            'X-CSRFToken': $.cookie('csrftoken')
        },
        data: JSON.stringify(config.buildSavePayload()),
        contentType: 'application/json',
        success: function(response) {

            // .. on success, the progress item reports what was saved ..
            $.fn.zato.settings.updateProgress('configure', 'completed', response.message);
            button.prop('disabled', false);
        },
        error: function(xhr) {

            // .. on error, it carries the full error text for the copy icon.
            var errorMessage = config.saveErrorLabel;
            try {
                var response = JSON.parse(xhr.responseText);
                if (response.error) {
                    errorMessage = response.error;
                }
            } catch(ignored) {
                if (xhr.responseText) {
                    errorMessage = xhr.responseText;
                }
            }

            $('#progress-configure').data('full-error', errorMessage);
            $.fn.zato.settings.updateProgress('configure', 'error', errorMessage);
            button.prop('disabled', false);
        }
    });
};

})(jQuery);
