(function($) {

// ////////////////////////////////////////////////////////////////////////
// Test results rendering
// ////////////////////////////////////////////////////////////////////////

$.fn.zato.logging.levels._renderResults = function(results) {
    var $container = $('#logging-levels-results');
    $container.empty();

    for (var resultIdx = 0; resultIdx < results.length; resultIdx++) {
        var result = results[resultIdx];

        // Build the row for this result ..
        var row = document.createElement('div');
        row.className = 'logging-result-row logging-result-' + result.status;

        // .. the logger name or the raw line ..
        var label = document.createElement('span');
        label.className = 'logging-result-label';
        label.textContent = result.label;

        // .. and what will happen to it.
        var message = document.createElement('span');
        message.className = 'logging-result-message';
        message.textContent = result.status + ' - ' + result.message;

        row.appendChild(label);
        row.appendChild(message);
        $container.append(row);
    }
};

// ////////////////////////////////////////////////////////////////////////
// Actions
// ////////////////////////////////////////////////////////////////////////

$.fn.zato.logging.levels._test = function() {
    var logging = $.fn.zato.logging;
    var config = logging.config;
    var $button = $('#logging-levels-test');

    $button.prop('disabled', true);

    $.ajax({
        type: 'POST',
        url: config.testUrl,
        headers: {'X-CSRFToken': $.cookie('csrftoken')},
        data: JSON.stringify({text: $('#logging-config').val()}),
        contentType: 'application/json',
        dataType: 'json',
        success: function(response) {
            logging.levels._renderResults(response.results);
            var changeCount = response.change_count;
            var suffix = changeCount === 1 ? 'change' : 'changes';
            logging.setStatus('logging', changeCount + ' ' + suffix, 'logging-status-saved');
        },
        error: function(jqXHR) {
            var response = JSON.parse(jqXHR.responseText);
            if (response.results) {
                logging.levels._renderResults(response.results);
            }
            var errorText = response.error;
            if (errorText === undefined) {
                errorText = 'Test failed';
            }
            logging.setStatus('logging', errorText, 'logging-status-error');
        },
        complete: function() {
            $button.prop('disabled', false);
        }
    });
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.logging.levels._save = function() {
    var logging = $.fn.zato.logging;
    var config = logging.config;
    var $button = $('#logging-levels-save');

    $button.prop('disabled', true);

    $.ajax({
        type: 'POST',
        url: config.saveUrl,
        headers: {'X-CSRFToken': $.cookie('csrftoken')},
        data: JSON.stringify({text: $('#logging-config').val()}),
        contentType: 'application/json',
        dataType: 'json',
        success: function(response) {
            $('#logging-levels-results').empty();
            logging.setStatus('logging', 'Levels saved - ' + response.message, 'logging-status-saved');
        },
        error: function(jqXHR) {
            var response = JSON.parse(jqXHR.responseText);
            logging.setStatus('logging', response.error, 'logging-status-error');
        },
        complete: function() {
            $button.prop('disabled', false);
        }
    });
};

// ////////////////////////////////////////////////////////////////////////
// Initialization
// ////////////////////////////////////////////////////////////////////////

$.fn.zato.logging.levels.init = function(loggingText) {
    var levels = $.fn.zato.logging.levels;

    // Fill the editor with the current levels ..
    $('#logging-config').val(loggingText);

    // .. and wire up the buttons.
    $('#logging-levels-test').on('click', function() {
        levels._test();
    });

    $('#logging-levels-save').on('click', function() {
        levels._save();
    });
};

})(jQuery);
