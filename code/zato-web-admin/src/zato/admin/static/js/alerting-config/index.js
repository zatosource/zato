// Alert rules - the rows screen.
//
// One slim full-width row per rule family, with a master "Everything"
// slider above the rows. Every row says whether its family is active and
// shows the values its rules are driven by, in columns aligned across all
// the rows. Clicking a value opens the row's popover editor - the wizard
// kit's own micro-form - on that very field. This is the UI side only -
// the answers land back in the row, the wiring comes separately.

(function($) {

$(document).ready(function() {

// ////////////////////////////////////////////////////////////////////////

var config = {};

// What a row's badge says about its family
config.statusOnLabel = 'Active';
config.statusOffLabel = 'Inactive';

// What a checkbox value reads as in its cell
config.checkboxOnLabel = 'On';
config.checkboxOffLabel = 'Off';

// Every element the popover makes is named after this
config.idPrefix = 'alert-rules-row';

// How wide a row's popover editor stands
config.popupWidth = '340px';

// What the page-wide help badge explains, anchored at the Everything slider
config.howItWorksText = 'Slide "Everything" to turn all alert rules on or off. ' +
    'Click any value to edit the row it belongs to, ' +
    'and drag a row by its handle to reorder the list.';

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
    canary_checks: {label: 'Canary checks', kind: 'checkbox'},
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
    canary_checks: 'Whether periodic canary transfers run against each connection.',
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
    file_transfer: {title: 'File transfer', fields: ['consecutive_failures', 'warning_failures', 'critical_failures', 'canary_checks']},
    scheduler: {title: 'Scheduler', fields: ['error_rate', 'overdue_multiplier', 'start_delay']},
    channels: {title: 'Channels', fields: ['error_rate']},
    common: {title: 'Common', fields: ['certificate_warning', 'outstanding_backlog', 'feed_silence']}
};

// ////////////////////////////////////////////////////////////////////////

var masterField = $('#id_alert_rules_all');

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

    status.appendChild(statusBadge);
};

// ////////////////////////////////////////////////////////////////////////

// The master slider is on only when every family is
var syncMaster = function() {

    var allOn = true;

    $.each(config.families, function(setName) {
        if(!field(setName).is(':checked')) {
            allOn = false;
        }
    });

    masterField.prop('checked', allOn);
};

// ////////////////////////////////////////////////////////////////////////

var renderAll = function() {

    $.each(config.families, function(setName) {
        renderCard(setName);
    });

    syncMaster();
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

masterField.on('change', function() {

    var isOn = masterField.is(':checked');

    $.each(config.families, function(setName) {
        field(setName).prop('checked', isOn);
        renderCard(setName);
    });
});

// ////////////////////////////////////////////////////////////////////////

// Every row shows its family's state from the moment the page opens,
// in the order the rows were last dragged into ..
restoreOrder();
renderAll();

// .. the page-wide help explains itself at the Everything slider ..
$.fn.zato.how_it_works.init({
    badgeId: 'alert-rules-how-it-works',
    divId: '#alert-rules',
    fieldSelector: '.alert-rules-master',

    // The master row sits at the top of the page, so the one tooltip
    // goes below it, over the rows it talks about
    placement: 'bottom',
    descriptions: {
        'id_alert_rules_all': config.howItWorksText
    }
});

// .. and the page is shown once it is fully filled in.
$.fn.zato.dashboard_kit.reveal();

// ////////////////////////////////////////////////////////////////////////

});

})(jQuery);
