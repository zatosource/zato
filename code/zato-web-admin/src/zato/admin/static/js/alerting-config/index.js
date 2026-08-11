// Alert rules - the rows screen.
//
// One slim full-width row per rule type. Every row says whether its
// type is active and shows the values its rules are driven by, in
// columns aligned across all the rows. Clicking a value opens the row's
// popover editor - the wizard kit's own micro-form - on that very field.
// The values come from the live rule documents through the Django view
// and every change goes back the same way - the popover's OK posts the
// row's values, the badge posts the type's active state, and the row
// answers with its Running badge while the request is on its way.

(function($) {

$(document).ready(function() {

// ////////////////////////////////////////////////////////////////////////

var config = {};

// Where a change is posted - the endpoints the template names, one for
// the type rows and one for the notifications row below them
config.saveUrl = document.getElementById('alert-rules').dataset.saveUrl;
config.notificationsSaveUrl = document.getElementById('alert-rules').dataset.notificationsSaveUrl;

// The one fixed row that is not a rule type - the notification targets
config.notificationsName = 'notifications';

// What a request that never reached its endpoint reports
config.applyErrorText = 'The change could not be applied';

// How long a finished change's confirmation stays on screen
config.okVisibleMs = 1500;

// What a finished change confirms itself with
config.okLabel = 'OK';

// What a row's badge says about its type
config.statusOnLabel = 'Active';
config.statusOffLabel = 'Inactive';

// What the badge offers on a hover - clicking it flips the type
config.toggleHintLabel = 'Click to toggle';

// What a checkbox value reads as in its cell
config.checkboxOnLabel = 'On';
config.checkboxOffLabel = 'Off';

// What a notification cell without a value reads as
config.notSetLabel = 'Not set';

// Every element the popover makes is named after this
config.idPrefix = 'alert-rules-row';

// How wide a row's popover editor stands
config.popupWidth = '290px';

// Where the hand-picked row order is kept between visits
config.orderStorageKey = 'zato.alert-rules.order';

// ////////////////////////////////////////////////////////////////////////

// Every value the rows carry, each named once - the label is what the
// popover calls the field, with the unit the cell says through its suffix
config.fields = {
    consecutive_failures: {label: 'Consecutive failures', kind: 'number'},
    error_rate: {label: 'Error rate (%)', kind: 'number'},
    alert_threshold: {label: 'Alert threshold (%)', kind: 'number'},
    max_latency: {label: 'Max latency (ms)', kind: 'number'},
    max_query_time: {label: 'Max query time (ms)', kind: 'number'},
    warning_latency: {label: 'Warning latency (ms)', kind: 'number'},
    critical_latency: {label: 'Critical latency (ms)', kind: 'number'},
    max_tool_call_time: {label: 'Max tool-call time (ms)', kind: 'number'},
    health_alerts: {label: 'Health alerts', kind: 'checkbox'},
    max_call_time: {label: 'Max call time (ms)', kind: 'number'},
    auth_failures: {label: 'Auth failures', kind: 'number'},
    warning_failures: {label: 'Warning failures', kind: 'number'},
    critical_failures: {label: 'Critical failures', kind: 'number'},
    test_transfers: {label: 'Test transfers', kind: 'checkbox'},
    overdue_multiplier: {label: 'Overdue multiplier', kind: 'number'},
    start_delay: {label: 'Start delay (ms)', kind: 'number'},
    certificate_warning: {label: 'Certificate warning (days)', kind: 'number'},
    outstanding_backlog: {label: 'Outstanding backlog', kind: 'number'},
    feed_silence: {label: 'Feed silence (s)', kind: 'number'},
    use_llm: {label: 'Use LLM', kind: 'checkbox'},
    slack_webhook: {label: 'Slack webhook', kind: 'text'},
    teams_webhook: {label: 'Teams webhook', kind: 'text'},
    webhook_url: {label: 'Webhook URL', kind: 'text'},
    email_connection: {label: 'Email connection', kind: 'text'},
    default_to: {label: 'Email to', kind: 'text'},
    from: {label: 'Email from', kind: 'text'},
    dashboard_url: {label: 'Dashboard URL', kind: 'text'}
};

// What a field means, said once and shown wherever the field is edited
config.fieldHelp = {
    consecutive_failures: 'How many failures in a row raise an alert.',
    error_rate: 'The share of failed calls, in percent, that raises an alert.',
    alert_threshold: 'The error rate, in percent, at which an alert is escalated.',
    max_latency: 'Calls slower than this many milliseconds count as slow.',
    max_query_time: 'Queries slower than this many milliseconds count as slow.',
    warning_latency: 'Completions slower than this many milliseconds raise a warning.',
    critical_latency: 'Completions slower than this many milliseconds are critical.',
    max_tool_call_time: 'Tool calls slower than this many milliseconds count as slow.',
    health_alerts: 'Whether the Microsoft service health feed raises alerts of its own.',
    max_call_time: 'Calls slower than this many milliseconds count as slow.',
    auth_failures: 'How many authentication failures in a row raise an alert.',
    warning_failures: 'How many failures in the window raise a warning.',
    critical_failures: 'How many failures in the window count as critical.',
    test_transfers: 'Whether periodic test transfers run against each connection.',
    overdue_multiplier: 'How many intervals late a job may run before an alert.',
    start_delay: 'How many milliseconds late a job may start before an alert.',
    certificate_warning: 'How many days before expiry a certificate raises an alert.',
    outstanding_backlog: 'How many outstanding messages raise an alert.',
    feed_silence: 'How many seconds of silence from a feed raise an alert.',
    use_llm: 'Whether alerts above the alert threshold are diagnosed by the LLM.',
    slack_webhook: 'The Slack webhook alerts are posted to when a rule names none of its own.',
    teams_webhook: 'The Microsoft Teams webhook alerts are posted to when a rule names none of its own.',
    webhook_url: 'The webhook alerts are posted to as JSON - Jira and other workflow backends read it.',
    email_connection: 'The name of the email connection alert emails go out through.',
    default_to: 'The addresses alert emails go to, separated by commas.',
    from: 'The address alert emails come from.',
    dashboard_url: 'The Dashboard address the links in alerts point to.'
};

// One row per rule type, in the order they are rendered, each naming
// the fields its popover edits
config.types = {
    rest: {title: 'REST and SOAP', fields: ['consecutive_failures', 'error_rate', 'alert_threshold', 'max_latency', 'use_llm']},
    sql: {title: 'SQL', fields: ['consecutive_failures', 'error_rate', 'alert_threshold', 'max_query_time', 'use_llm']},
    llm: {title: 'LLM', fields: ['consecutive_failures', 'error_rate', 'warning_latency', 'critical_latency', 'use_llm']},
    mcp: {title: 'MCP', fields: ['consecutive_failures', 'error_rate', 'alert_threshold', 'max_tool_call_time', 'use_llm']},
    microsoft: {title: 'Microsoft cloud', fields: ['consecutive_failures', 'error_rate', 'health_alerts', 'max_call_time', 'use_llm']},
    email: {title: 'Email', fields: ['consecutive_failures', 'error_rate', 'auth_failures', 'alert_threshold', 'use_llm']},
    odoo: {title: 'Odoo', fields: ['consecutive_failures', 'error_rate', 'auth_failures', 'max_call_time', 'use_llm']},
    file_transfer: {title: 'File transfer', fields: ['consecutive_failures', 'warning_failures', 'critical_failures', 'test_transfers', 'use_llm']},
    scheduler: {title: 'Scheduler', fields: ['error_rate', 'alert_threshold', 'overdue_multiplier', 'start_delay', 'use_llm']},
    channels: {title: 'Channels', fields: ['error_rate']},
    common: {title: 'Common', fields: ['certificate_warning', 'outstanding_backlog', 'feed_silence']}
};

// The notifications row's own fields - where alerts go when a rule
// does not name a target of its own
config.notificationFields = [
    'slack_webhook', 'teams_webhook', 'webhook_url', 'email_connection', 'default_to', 'from', 'dashboard_url'
];

// What each type's rules watch, shown at the type's own row header
config.typeHelp = {
    rest: 'Alert rules for REST and SOAP outgoing connections - failures in a row, error rates, escalations and slow calls.',
    sql: 'Alert rules for SQL connection pools - failures in a row, error rates and slow queries.',
    llm: 'Alert rules for LLM connections - failures in a row, error rates and slow completions.',
    mcp: 'Alert rules for MCP servers - failures in a row, error rates and slow tool calls.',
    microsoft: 'Alert rules for Microsoft cloud connections - failures in a row, error rates, service health and slow calls.',
    email: 'Alert rules for SMTP and IMAP connections - failures in a row, error rates and authentication failures.',
    odoo: 'Alert rules for Odoo connections - failures in a row, error rates, authentication failures and slow calls.',
    file_transfer: 'Alert rules for SMB, SFTP and FTP connections - failure counts and periodic test transfers.',
    scheduler: 'Alert rules for scheduler jobs - error rates, overdue runs and late starts.',
    channels: 'Alert rules for channels of every kind - the share of failed requests.',
    common: 'Alert rules that watch the environment as a whole - expiring certificates, backlogs and silent feeds.',
    notifications: 'Where alerts go by default - the webhooks, the email connection and its addressing, and the Dashboard address the links point to. A rule naming its own target overrides these.'
};

// ////////////////////////////////////////////////////////////////////////

var field = function(setName) {
    var out = $('#id_alert_rules_' + setName);
    return out;
};

var card = function(setName) {
    var out = document.getElementById('alert-rules-card-' + setName);
    return out;
};

// Where a failed change explains itself, at the heading of the screen
var errorElement = document.getElementById('alert-rules-error');

// ////////////////////////////////////////////////////////////////////////
//
// The Running badge, the confirmation and the save itself
//
// ////////////////////////////////////////////////////////////////////////

// A row in flight shows its Running badge and takes no further edits
var markBusy = function(setName) {
    card(setName).classList.add('alert-rules-busy');
};

var markDone = function(setName) {
    card(setName).classList.remove('alert-rules-busy');
};

// A finished change confirms itself where its Running badge was,
// then steps back out of the way on its own
var showOkBadge = function(setName) {

    var element = document.getElementById('alert-rules-ok-' + setName);

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
var errorTextFromResponse = function(request) {

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
var postChange = function(setName, url, data, onSuccess, onError) {

    // Whatever the last change said is no longer about what is on screen
    errorElement.textContent = '';

    markBusy(setName);

    $.ajax({
        url: url,
        type: 'POST',
        headers: {'X-CSRFToken': $.cookie('csrftoken')},
        data: JSON.stringify(data),
        contentType: 'application/json',
        success: function() {
            markDone(setName);
            onSuccess();
            showOkBadge(setName);
        },
        error: function(request) {
            markDone(setName);
            errorElement.textContent = errorTextFromResponse(request);
            onError();
        }
    });
};

// ////////////////////////////////////////////////////////////////////////
//
// The popover editor - the wizard kit's micro-form, hosted here on the
// hidden fields the template carries, one set serving every row. The row
// clicked fills them in before the popover opens.
//
// ////////////////////////////////////////////////////////////////////////

var editor = {
    forms: {},
    config: {idPrefix: config.idPrefix}
};

// The hidden fields the popover reads and writes, named the way it expects
editor.field = function(name) {
    var out = $('#id_' + config.idPrefix + '-' + name);
    return out;
};

// A field is explained in the same words wherever it is edited
editor.helpDescriptions = function() {

    var out = {};

    $.each(config.fieldHelp, function(fieldName, text) {
        out[editor.forms.inputId(fieldName)] = text;
    });

    return out;
};

// One micro-form per type, built from the same field list its row shows
var descriptors = {};

$.each(config.types, function(typeName, typeConfig) {

    var entries = [];

    $.each(typeConfig.fields, function(_ignored, fieldName) {
        var fieldConfig = config.fields[fieldName];
        entries.push({field: fieldName, label: fieldConfig.label, kind: fieldConfig.kind});
    });

    descriptors[typeName] = {title: typeConfig.title, width: config.popupWidth, pages: [entries]};
});

// The notifications row's own micro-form - the same popover, all text fields
var notificationEntries = [];

$.each(config.notificationFields, function(_ignored, fieldName) {
    var fieldConfig = config.fields[fieldName];
    notificationEntries.push({field: fieldName, label: fieldConfig.label, kind: fieldConfig.kind});
});

descriptors[config.notificationsName] = {title: 'Notifications', width: config.popupWidth, pages: [notificationEntries]};

// ////////////////////////////////////////////////////////////////////////

// The row whose popover is open, held for the save
var openCard = null;

// ////////////////////////////////////////////////////////////////////////

// Seeds the hidden fields from the row and opens its popover on the very
// value that was clicked
var openEditor = function(link) {

    openCard = link.closest('.alert-rules-set-card');
    var typeName = openCard.id.replace('alert-rules-card-', '');

    openCard.querySelectorAll('.alert-rules-param-edit').forEach(function(edit) {

        var fieldInput = editor.field(edit.dataset.field);

        if(edit.dataset.kind === 'checkbox') {
            fieldInput.prop('checked', edit.dataset.value === 'true');
        }
        else {
            fieldInput.val(edit.dataset.value);
        }
    });

    editor.forms.open(typeName, link, link.dataset.field);
};

// ////////////////////////////////////////////////////////////////////////

// Posts the popover's answers to the backend and, once it says yes,
// writes them back into the row's cells - a save the backend refused
// leaves the cells exactly as they were
var saveRow = function() {

    var savedCard = openCard;
    var typeName = savedCard.id.replace('alert-rules-card-', '');

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
    postChange(typeName, url, payload, applyToCells, function() {});
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.wizard_kit.forms.setup(editor, {
    descriptors: descriptors,
    showCancel: true,
    doneLabel: 'OK',
    labelsLeft: true,
    onDone: saveRow
});

// The value cells of every row, the notifications row included - it sits
// outside the sortable grid, so the delegation runs from the screen's root
$('#alert-rules').on('click', '.alert-rules-param-edit', function() {
    openEditor(this);
});

// Clicking a row's badge flips its type on or off - the badge changes
// at once, the backend flips all the type's rules, and a refused flip
// puts the badge back where it was
$('.alert-rules-grid').on('click', '.alert-rules-state-toggle', function() {

    var cardElem = this.closest('.alert-rules-set-card');
    var setName = cardElem.id.replace('alert-rules-card-', '');

    var fieldInput = field(setName);
    var isOn = !fieldInput.is(':checked');
    fieldInput.prop('checked', isOn);

    // A re-toggle back to active cancels any dimming still waiting
    cardElem.classList.remove('alert-rules-set-off-pending');

    renderCard(setName);

    // Deactivating happens under the pointer - only the badge changes for
    // now, the row keeps its full face until the pointer moves elsewhere
    if(!isOn) {
        cardElem.classList.remove('alert-rules-set-off');
        cardElem.classList.add('alert-rules-set-off-pending');
    }

    var revert = function() {
        fieldInput.prop('checked', !isOn);
        cardElem.classList.remove('alert-rules-set-off-pending');
        renderCard(setName);
    };

    postChange(setName, config.saveUrl, {type: setName, is_active: isOn}, function() {}, revert);
});

// Once the pointer leaves a row whose dimming is waiting, it dims
$('.alert-rules-grid').on('mouseleave', '.alert-rules-set-card', function() {

    if(this.classList.contains('alert-rules-set-off-pending')) {
        this.classList.remove('alert-rules-set-off-pending');
        this.classList.add('alert-rules-set-off');
    }
});

// ////////////////////////////////////////////////////////////////////////
//
// The state badges and the master slider
//
// ////////////////////////////////////////////////////////////////////////

var renderCard = function(setName) {

    var isOn = field(setName).is(':checked');

    var cardElem = card(setName);
    cardElem.classList.toggle('alert-rules-set-off', !isOn);

    // The badge after the name says plainly whether the type is active
    var status = document.getElementById('alert-rules-status-' + setName);
    status.textContent = '';

    // The badge is the shared dashboard tag - the same face the role tags
    // of the message flow and audit log listings wear
    var statusBadge = document.createElement('span');

    if(isOn) {
        statusBadge.className = 'dashboard-tag alert-rules-state-on';
        statusBadge.textContent = config.statusOnLabel;
    }
    else {
        statusBadge.className = 'dashboard-tag alert-rules-state-off';
        statusBadge.textContent = config.statusOffLabel;
    }

    // The badge is also the way to flip the type - it sits in a link
    // whose hover offers the same soft hint the value cells give
    var toggle = document.createElement('a');
    toggle.href = 'javascript:void(0)';
    toggle.className = 'wizard-toggle-edit alert-rules-state-toggle';
    toggle.appendChild(statusBadge);

    var hint = document.createElement('span');
    hint.className = 'zato-soft-hint';
    hint.textContent = config.toggleHintLabel;
    toggle.appendChild(hint);

    status.appendChild(toggle);
};

// ////////////////////////////////////////////////////////////////////////

var renderAll = function() {

    $.each(config.types, function(setName) {
        renderCard(setName);
    });
};

// ////////////////////////////////////////////////////////////////////////
//
// Reordering the rows
//
// ////////////////////////////////////////////////////////////////////////

// The rows keep whatever order they were last dragged into, per browser
var grid = document.querySelector('.alert-rules-grid');

var saveOrder = function() {

    var order = [];
    var cards = grid.querySelectorAll('.alert-rules-set-card');

    for(var cardIdx = 0; cardIdx < cards.length; cardIdx++) {
        order.push(cards[cardIdx].id.replace('alert-rules-card-', ''));
    }

    localStorage.setItem(config.orderStorageKey, JSON.stringify(order));
};

var restoreOrder = function() {

    var stored = localStorage.getItem(config.orderStorageKey);

    // A first visit has no order on record yet
    if(stored === null) {
        return;
    }

    var order = JSON.parse(stored);

    // Appending an element moves it, so walking the saved order rebuilds it -
    // a type the saved order does not know stays where the page put it
    for(var orderIdx = 0; orderIdx < order.length; orderIdx++) {

        var saved = card(order[orderIdx]);

        if(saved) {
            grid.appendChild(saved);
        }
    }
};

// ////////////////////////////////////////////////////////////////////////

// Reordering runs through Sortable, the way the rate limiting rules do -
// rows are picked up by their handle, the ghost marks the drop spot
// and the order that comes out is what the next visit restores.
Sortable.create(grid, {
    handle: '.alert-rules-drag-handle',
    animation: 150,
    ghostClass: 'alert-rules-dragging',
    onEnd: function() {
        saveOrder();
    }
});

// ////////////////////////////////////////////////////////////////////////

// Every row shows its type's state from the moment the page opens,
// in the order the rows were last dragged into ..
restoreOrder();
renderAll();

// .. the help explains each type at its own row header ..
var helpDescriptions = {};

$.each(config.typeHelp, function(setName, text) {
    helpDescriptions['id_alert_rules_' + setName] = text;
});

$.fn.zato.how_it_works.init({
    badgeId: 'alert-rules-how-it-works',
    divId: '#alert-rules',
    fieldSelector: '.alert-rules-set-header',

    // The tooltips go below their anchors, each one's left edge lining
    // up with the left edge of the thing it describes
    placement: 'bottom-start',
    descriptions: helpDescriptions
});

// .. and the page is shown once it is fully filled in.
$.fn.zato.dashboard_kit.reveal();

// ////////////////////////////////////////////////////////////////////////

});

})(jQuery);
