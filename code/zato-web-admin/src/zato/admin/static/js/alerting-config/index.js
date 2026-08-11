// Alert rules - the rows screen.
//
// One slim full-width row per rule family. Every row says whether its
// family is active and shows the values its rules are driven by, in
// columns aligned across all the rows. Clicking a value opens the row's
// popover editor - the wizard kit's own micro-form - on that very field.
// This is the UI side only - the answers land back in the row, the
// wiring comes separately.

(function($) {

$(document).ready(function() {

// ////////////////////////////////////////////////////////////////////////

var config = {};

// What a row's badge says about its family
config.statusOnLabel = 'Active';
config.statusOffLabel = 'Inactive';

// What the badge offers on a hover - clicking it flips the family
config.toggleHintLabel = 'Click to toggle';

// What a checkbox value reads as in its cell
config.checkboxOnLabel = 'On';
config.checkboxOffLabel = 'Off';

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
    incident_threshold: {label: 'Incident threshold (%)', kind: 'number'},
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
    feed_silence: {label: 'Feed silence (s)', kind: 'number'}
};

// What a field means, said once and shown wherever the field is edited
config.fieldHelp = {
    consecutive_failures: 'How many failures in a row raise an alert.',
    error_rate: 'The share of failed calls, in percent, that raises an alert.',
    incident_threshold: 'The error rate, in percent, at which an alert becomes an incident.',
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
    feed_silence: 'How many seconds of silence from a feed raise an alert.'
};

// One row per rule family, in the order they are rendered, each naming
// the fields its popover edits
config.families = {
    rest: {title: 'REST and SOAP', fields: ['consecutive_failures', 'error_rate', 'incident_threshold', 'max_latency']},
    sql: {title: 'SQL', fields: ['consecutive_failures', 'error_rate', 'max_query_time']},
    llm: {title: 'LLM', fields: ['consecutive_failures', 'error_rate', 'warning_latency', 'critical_latency']},
    mcp: {title: 'MCP', fields: ['consecutive_failures', 'error_rate', 'max_tool_call_time']},
    microsoft: {title: 'Microsoft cloud', fields: ['consecutive_failures', 'error_rate', 'health_alerts', 'max_call_time']},
    email: {title: 'Email', fields: ['consecutive_failures', 'error_rate', 'auth_failures']},
    odoo: {title: 'Odoo', fields: ['consecutive_failures', 'error_rate', 'auth_failures', 'max_call_time']},
    file_transfer: {title: 'File transfer', fields: ['consecutive_failures', 'warning_failures', 'critical_failures', 'test_transfers']},
    scheduler: {title: 'Scheduler', fields: ['error_rate', 'overdue_multiplier', 'start_delay']},
    channels: {title: 'Channels', fields: ['error_rate']},
    common: {title: 'Common', fields: ['certificate_warning', 'outstanding_backlog', 'feed_silence']}
};

// What each family's rules watch, shown at the family's own row header
config.familyHelp = {
    rest: 'Alert rules for REST and SOAP outgoing connections - failures in a row, error rates, incidents and slow calls.',
    sql: 'Alert rules for SQL connection pools - failures in a row, error rates and slow queries.',
    llm: 'Alert rules for LLM connections - failures in a row, error rates and slow completions.',
    mcp: 'Alert rules for MCP servers - failures in a row, error rates and slow tool calls.',
    microsoft: 'Alert rules for Microsoft cloud connections - failures in a row, error rates, service health and slow calls.',
    email: 'Alert rules for SMTP and IMAP connections - failures in a row, error rates and authentication failures.',
    odoo: 'Alert rules for Odoo connections - failures in a row, error rates, authentication failures and slow calls.',
    file_transfer: 'Alert rules for SMB, SFTP and FTP connections - failure counts and periodic test transfers.',
    scheduler: 'Alert rules for scheduler jobs - error rates, overdue runs and late starts.',
    channels: 'Alert rules for channels of every kind - the share of failed requests.',
    common: 'Alert rules that watch the environment as a whole - expiring certificates, backlogs and silent feeds.'
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

// One micro-form per family, built from the same field list its row shows
var descriptors = {};

$.each(config.families, function(familyName, family) {

    var entries = [];

    $.each(family.fields, function(_ignored, fieldName) {
        var fieldConfig = config.fields[fieldName];
        entries.push({field: fieldName, label: fieldConfig.label, kind: fieldConfig.kind});
    });

    descriptors[familyName] = {title: family.title, width: config.popupWidth, pages: [entries]};
});

// ////////////////////////////////////////////////////////////////////////

// The row whose popover is open, held for the save
var openCard = null;

// ////////////////////////////////////////////////////////////////////////

// Seeds the hidden fields from the row and opens its popover on the very
// value that was clicked
var openEditor = function(link) {

    openCard = link.closest('.alert-rules-set-card');
    var familyName = openCard.id.replace('alert-rules-card-', '');

    openCard.querySelectorAll('.alert-rules-param-edit').forEach(function(edit) {

        var fieldInput = editor.field(edit.dataset.field);

        if(edit.dataset.kind === 'checkbox') {
            fieldInput.prop('checked', edit.dataset.value === 'true');
        }
        else {
            fieldInput.val(edit.dataset.value);
        }
    });

    editor.forms.open(familyName, link, link.dataset.field);
};

// ////////////////////////////////////////////////////////////////////////

// Writes the popover's answers back into the row's cells - the values are
// the page's own for now, the wiring to the backend comes separately
var saveRow = function() {

    openCard.querySelectorAll('.alert-rules-param-edit').forEach(function(edit) {

        var fieldInput = editor.field(edit.dataset.field);
        var summary = edit.querySelector('.alert-rules-param-value');

        if(edit.dataset.kind === 'checkbox') {
            var isOn = fieldInput.prop('checked');
            edit.dataset.value = isOn;
            summary.textContent = isOn ? config.checkboxOnLabel : config.checkboxOffLabel;
        }
        else {
            edit.dataset.value = fieldInput.val();
            summary.textContent = edit.dataset.value + edit.dataset.suffix;
        }
    });
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.wizard_kit.forms.setup(editor, {
    descriptors: descriptors,
    showCancel: true,
    doneLabel: 'OK',
    labelsLeft: true,
    onDone: saveRow
});

$('.alert-rules-grid').on('click', '.alert-rules-param-edit', function() {
    openEditor(this);
});

// Clicking a row's badge flips its family on or off
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

    // The badge after the name says plainly whether the family is active
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

    // The badge is also the way to flip the family - it sits in a link
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

    $.each(config.families, function(setName) {
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
    // a family the saved order does not know stays where the page put it
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

// Every row shows its family's state from the moment the page opens,
// in the order the rows were last dragged into ..
restoreOrder();
renderAll();

// .. the help explains each family at its own row header ..
var helpDescriptions = {};

$.each(config.familyHelp, function(setName, text) {
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
