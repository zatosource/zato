// Alert rules - the Running badge, the confirmation and the save itself.
//
// One request per change - the row it is about wears the Running badge
// until the answer lands, a finished change confirms itself where the
// badge was, and a refused one explains itself at the heading of the
// screen and leaves the cells exactly as they were.

(function($) {

var screen = $.fn.zato.alerting_config;
var config = screen.config;

// ////////////////////////////////////////////////////////////////////////

// Where a failed change explains itself, at the heading of the screen - found by init.js once the page is there
screen.errorElement = null;

// The row whose popover is open, held for the save
screen.openCard = null;

// ////////////////////////////////////////////////////////////////////////

// A row in flight shows its Running badge and takes no further edits
screen.markBusy = function(setName) {
    screen.card(setName).classList.add('alert-rules-busy');
};

screen.markDone = function(setName) {
    screen.card(setName).classList.remove('alert-rules-busy');
};

// A finished change confirms itself where its Running badge was,
// then steps back out of the way on its own
screen.showOkBadge = function(setName) {

    var element = document.getElementById(config.okIdPrefix + setName);

    element.textContent = config.okLabel;
    element.classList.add('alert-rules-ok-visible');

    // A confirmation shown again before the last one faded keeps its full time
    clearTimeout(element._alertRulesOkTimer);

    element._alertRulesOkTimer = setTimeout(function() {
        element.classList.remove('alert-rules-ok-visible');
    }, config.okVisibleMs);
};

// What a failed request has to say for itself - the JSON error when there
// is one, the default line when the request never reached its endpoint
screen.errorTextFromResponse = function(request) {

    var out = config.applyErrorText;
    var text = request.responseText;

    try {
        var payload = JSON.parse(text);
        if(payload.error) {
            out = payload.error;
        }
    }
    catch(ignored) {
    }

    return out;
};

// One request per change - the row it is about wears the Running badge
// until the answer lands, and each way out has its own follow-up
screen.postChange = function(setName, url, data, onSuccess, onError) {

    // Whatever the last change said is no longer about what is on screen
    screen.errorElement.textContent = '';

    screen.markBusy(setName);

    $.ajax({
        url: url,
        type: 'POST',
        headers: {'X-CSRFToken': $.cookie('csrftoken')},
        data: JSON.stringify(data),
        contentType: 'application/json',
        success: function() {
            screen.markDone(setName);
            onSuccess();
            screen.showOkBadge(setName);
        },
        error: function(request) {
            screen.markDone(setName);
            screen.errorElement.textContent = screen.errorTextFromResponse(request);
            onError();
        }
    });
};

// ////////////////////////////////////////////////////////////////////////

// Posts the popover's answers to the backend and, once it says yes,
// writes them back into the row's cells - a save the backend refused
// leaves the cells exactly as they were
screen.saveRow = function() {

    var editor = screen.editor;
    var savedCard = screen.openCard;
    var typeName = screen.setNameOf(savedCard);

    // What the popover holds, in the shape the endpoint reads - numbers
    // as numbers, checkboxes as booleans, notification targets as text
    var values = {};

    savedCard.querySelectorAll('.alert-rules-param-edit').forEach(function(edit) {

        var fieldInput = editor.field(edit.dataset.field);

        if(edit.dataset.kind === 'checkbox') {
            values[edit.dataset.field] = fieldInput.prop('checked');
        }
        else if(edit.dataset.kind === 'text') {
            values[edit.dataset.field] = fieldInput.val().trim();
        }
        else if(edit.dataset.kind === 'duration') {
            var unitValue = editor.field(screen.unitFieldName(edit.dataset.field)).val();
            values[edit.dataset.field] = screen.joinDuration(parseFloat(fieldInput.val()), unitValue);
        }
        else if(edit.dataset.kind === 'amount') {
            var amountUnitValue = editor.field(screen.unitFieldName(edit.dataset.field)).val();
            values[edit.dataset.field] = screen.joinAmount(parseFloat(fieldInput.val()), amountUnitValue);
        }
        else {
            values[edit.dataset.field] = parseFloat(fieldInput.val());
        }
    });

    var applyToCells = function() {

        savedCard.querySelectorAll('.alert-rules-param-edit').forEach(function(edit) {

            var value = values[edit.dataset.field];
            var summary = edit.querySelector('.alert-rules-param-value');

            if(edit.dataset.kind === 'checkbox') {
                edit.dataset.value = value;
                summary.textContent = value ? config.checkboxOnLabel : config.checkboxOffLabel;
            }
            else if(edit.dataset.kind === 'text') {
                edit.dataset.value = value;
                summary.textContent = value === '' ? config.notSetLabel : value;
            }
            else if(edit.dataset.kind === 'duration') {
                edit.dataset.value = value;
                summary.textContent = screen.formatDuration(value);
            }
            else if(edit.dataset.kind === 'amount') {
                edit.dataset.value = value;
                summary.textContent = screen.formatAmount(value);
            }
            else {
                edit.dataset.value = value;
                summary.textContent = value + edit.dataset.suffix;
            }
        });
    };

    // The notifications row posts to its own endpoint - the values go into
    // the sweep job's extra, not into any rule documents
    var url;
    var payload;

    if(typeName === config.notificationsName) {
        url = config.notificationsSaveUrl;
        payload = {values: values};
    }
    else {
        url = config.saveUrl;
        payload = {type: typeName, values: values};
    }

    // A refused save changes nothing on screen - the cells still show
    // what the backend actually holds
    screen.postChange(typeName, url, payload, applyToCells, function() {});
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
