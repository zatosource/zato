
// /////////////////////////////////////////////////////////////////////////////
//
// Delivery tab - the retry settings, the queue switch and the dead-letter
// queue settings of an outgoing connection's create or edit form, a tab
// shared by every connection type that can deliver through a queue.
//
// The tab's lines are in shared/delivery-tab.html and read the way the Alerts
// tab's do - decision lines of common/decision-lines.js, popover micro-forms
// of common/micro-forms/core.js for the retries and the DLQ action - and they
// wear the Alerts tab's own classes, so the two tabs look the same in a dialog.
//
// How to use, in a page's JS:
//
//     // Once, when the page is ready
//     $.fn.zato.delivery_tab.init();
//
//     // Before opening a dialog, after its form is populated
//     $.fn.zato.delivery_tab.bind({
//         panel_id: 'http-soap-create-tab-panel-delivery',
//         field_prefix: ''
//     });
//
//     // When building the how-it-works descriptions
//     var descriptions = $.extend({}, own_descriptions, $.fn.zato.delivery_tab.descriptions());
//
// The field_prefix is the Django form prefix with its trailing dash, the empty
// string for the create form and 'edit-' for the edit form.
//
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.delivery_tab.config = {

    // Every element the popover makes is named after this
    idPrefix: 'delivery-tab',
    idPrefixDjango: 'id_',

    // The popover wears the Alerts tab's look, so it is the same popover in the same dialog,
    // and a layout of its own, shared/delivery-tab.css, where a count is as wide as a count needs
    popoverClass: 'delivery-tab-popover',
    popupClass: 'alerts-tab-micro-form',

    // The lines of the tab are covered by the dialog's own How does it work? badge
    showHowItWorks: false,

    // The Alerts tab's classes that dim the lines - the whole panel while the queue is off,
    // the action line while the DLQ is off
    offClass: 'alerts-tab-off',
    lineOffClass: 'alerts-tab-line-off',

    // The fields of the tab, by role
    fieldMaxRetries: 'max_retries',
    fieldSleepTime: 'retry_sleep_time',
    fieldBackoffThreshold: 'retry_backoff_threshold',
    fieldBackoffMultiplier: 'retry_backoff_multiplier',
    fieldUseQueue: 'use_queue',
    fieldUseDLQ: 'use_dlq',
    fieldAction: 'dlq_action',
    fieldRetries: 'dlq_retries',
    fieldRetryInterval: 'dlq_retry_interval',
    fieldForwardTo: 'dlq_forward_to',
    fieldKeepHeader: 'dlq_keep_header',

    // A count of seconds is edited as a count with a unit select named after it - `retry_sleep_time_unit` -
    // whose option values are the noun in the singular and whose labels are the plural
    unitFieldSuffix: '_unit',

    // The lines the popovers belong to
    retriesLine: 'retries',
    actionLine: 'dlq_action',

    // No retries at all is a count of zero - the kit's numbers start at one, a fractional
    // one at zero, so the count is a fraction stepping by whole numbers
    noRetries: 0,
    retriesStep: 1,

    // A wait that does not grow - each next wait is as long as the first one
    flatMultiplier: 1,

    // What the retries line reads as - with no retries at all, with waits that grow and with waits that do not
    summaryNoRetries: 'No retries',
    summaryRetriesGrowing: 'Retry {retries}, {sleep} before the first, each next wait {multiplier} times the previous one, {threshold} of waiting at most',
    summaryRetriesFlat: 'Retry {retries}, {sleep} apart, {threshold} of waiting at most',

    // The stored values of the DLQ actions
    actionKeep: 'keep',
    actionRetry: 'retry',
    actionForward: 'forward',
    actionDiscard: 'discard',

    // What the action line reads as, per action
    summaryKeep: 'Keep messages for an operator',
    summaryRetry: 'Retry {retries}, {interval} apart',
    summaryForwardWithHeader: 'Forward to {topic} with the DLQ header',
    summaryForwardWithoutHeader: 'Forward to {topic} without the DLQ header',
    summaryForwardNoTopic: 'Forward - no topic picked yet',
    summaryDiscard: 'Discard',

    // The noun of a number of retries
    retrySingular: 'time',
    retryPlural: 'times',

    // The popovers' titles and their labels
    retriesTitle: 'Retries',
    labelMaxRetries: 'Max. retries',
    labelSleepTime: 'Wait before the first retry',
    labelBackoffThreshold: 'Wait in total at most',
    labelBackoffMultiplier: 'Wait multiplier',

    popoverTitle: 'DLQ action',
    labelAction: 'Action',
    labelRetries: 'Max. retries',
    labelRetryInterval: 'Every',
    labelForwardTo: 'Topic',
    labelKeepHeader: 'Keep the DLQ header',

    // The how-it-works texts of the tab's lines and of the popovers' inputs
    helpRetries: 'What happens to a message that fails - how many times it is sent again, how long the first wait is, ' +
        'how much longer each next wait is and how long all the waits may add up to. With no retries a message ' +
        'is sent once.',
    helpMaxRetries: 'How many times a failed invocation is retried. 0 means no retries at all.',
    helpSleepTime: 'How long to wait before the first retry. Each next wait is longer by the multiplier.',
    helpBackoffThreshold: 'A cap on the total time spent waiting between retries. Once reached, no more retries take place.',
    helpBackoffMultiplier: 'Each retry waits this many times longer than the previous one, up to 8 seconds per a single wait.',
    helpUseQueue: 'When on, each message is placed in the connection\'s own queue and delivered one at a time, ' +
        'in order, retried as the retry settings say. When off, each message is sent right away and retried on its own.',
    helpUseDLQ: 'When on, a message that still fails after its last retry moves to the connection\'s DLQ and the ' +
        'queue delivers the next one. When off, the message stays at the head of the queue and is retried in rounds, ' +
        'nothing behind it moves until it goes through or an operator discards it.',
    helpAction: 'What a rule running every minute does with each message in the DLQ - keeps it for an operator, ' +
        'puts it back into the queue a number of times, forwards it to a pub/sub topic or discards it.',
    helpRetries: 'How many times the rule puts a message back into the queue before leaving it in the DLQ.',
    helpRetryInterval: 'How long passes between two rounds of the rule for one message.',
    helpForwardTo: 'The pub/sub topic a forwarded message is published to.',
    helpKeepHeader: 'When on, a forwarded message carries its DLQ header - where it came from, why it failed ' +
        'and how many attempts were made.'
};

// Which form's panel is bound at the moment
$.fn.zato.delivery_tab.state = {
    panelId: null,
    fieldPrefix: ''
};

// The micro-forms kit installs the popover engine here
$.fn.zato.delivery_tab.forms = {};

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.delivery_tab.init = function() {

    var tab = $.fn.zato.delivery_tab;
    var config = tab.config;

    $.fn.zato.micro_forms.setup(tab, {
        descriptors: tab.buildDescriptors(),
        popupClass: config.popoverClass + ' ' + config.popupClass,
        showHowItWorks: config.showHowItWorks,
        showCancel: true,
        onDone: tab.render
    });
}

// /////////////////////////////////////////////////////////////////////////////

// The two micro-forms of the tab - the retries, and the action with what each action needs under it
$.fn.zato.delivery_tab.buildDescriptors = function() {

    var tab = $.fn.zato.delivery_tab;
    var config = tab.config;
    var out = {};

    out[config.retriesLine] = {
        title: config.retriesTitle,
        fitContent: true,
        // Two rows read in order - how many retries and the first wait, then how the waits grow and where they stop -
        // with a plain count in the left column and a count with its unit in the right one, so the columns line up
        pages: [[
            [
                {field: config.fieldMaxRetries, label: config.labelMaxRetries, kind: 'number', fractional: true, step: config.retriesStep},
                {field: config.fieldSleepTime, label: config.labelSleepTime, kind: 'number', unitField: tab.unitField(config.fieldSleepTime)}
            ],
            [
                {field: config.fieldBackoffMultiplier, label: config.labelBackoffMultiplier, kind: 'number'},
                {field: config.fieldBackoffThreshold, label: config.labelBackoffThreshold, kind: 'number', unitField: tab.unitField(config.fieldBackoffThreshold)}
            ]
        ]]
    };

    out[config.actionLine] = {
        title: config.popoverTitle,
        fitContent: true,
        pages: [[
            {field: config.fieldAction, label: config.labelAction, kind: 'select'},
            [
                {field: config.fieldRetries, label: config.labelRetries, kind: 'number'},
                {field: config.fieldRetryInterval, label: config.labelRetryInterval, kind: 'number', unitField: tab.unitField(config.fieldRetryInterval)}
            ],
            {field: config.fieldForwardTo, label: config.labelForwardTo, kind: 'select'},
            {field: config.fieldKeepHeader, label: config.labelKeepHeader, kind: 'checkbox'}
        ]]
    };

    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// The name of the unit select of a count of seconds
$.fn.zato.delivery_tab.unitField = function(fieldName) {
    var out = fieldName + $.fn.zato.delivery_tab.config.unitFieldSuffix;
    return out;
}

// A count of seconds as the form holds it, read with its unit's noun - `1 second`, `2 minutes` -
// the unit select's value being the singular and the label of its option the plural
$.fn.zato.delivery_tab.durationText = function(fieldName) {

    var tab = $.fn.zato.delivery_tab;
    var count = parseInt(tab.field(fieldName).val());
    var unitSelect = tab.field(tab.unitField(fieldName));
    var singular = unitSelect.val();
    var plural = unitSelect.find('option:selected').text();

    var out = $.fn.zato.count_text(count, singular, plural);
    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// The DOM id of one of the tab's fields on the form bound at the moment
$.fn.zato.delivery_tab.fieldId = function(fieldName) {
    var tab = $.fn.zato.delivery_tab;
    var out = tab.config.idPrefixDjango + tab.state.fieldPrefix + fieldName;
    return out;
}

// The one way into the rendered Django form, which is what the popover reads and writes
$.fn.zato.delivery_tab.field = function(fieldName) {
    var out = $('#' + $.fn.zato.delivery_tab.fieldId(fieldName));
    return out;
}

// The id of one element of the bound panel - a line, a summary or an edit link
$.fn.zato.delivery_tab.elementId = function(part, lineName) {
    var out = $.fn.zato.delivery_tab.state.panelId + '-' + part + '-' + lineName;
    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// The how-it-works texts of the popover's inputs, under the ids the micro-forms kit gives them
$.fn.zato.delivery_tab.helpDescriptions = function() {

    var tab = $.fn.zato.delivery_tab;
    var config = tab.config;
    var out = {};

    out[tab.forms.inputId(config.fieldMaxRetries)] = config.helpMaxRetries;
    out[tab.forms.inputId(config.fieldSleepTime)] = config.helpSleepTime;
    out[tab.forms.inputId(config.fieldBackoffThreshold)] = config.helpBackoffThreshold;
    out[tab.forms.inputId(config.fieldBackoffMultiplier)] = config.helpBackoffMultiplier;
    out[tab.forms.inputId(config.fieldAction)] = config.helpAction;
    out[tab.forms.inputId(config.fieldRetries)] = config.helpRetries;
    out[tab.forms.inputId(config.fieldRetryInterval)] = config.helpRetryInterval;
    out[tab.forms.inputId(config.fieldForwardTo)] = config.helpForwardTo;
    out[tab.forms.inputId(config.fieldKeepHeader)] = config.helpKeepHeader;

    return out;
}

// The how-it-works descriptions of the lines of the bound panel, keyed by the
// id each line's label points at - the switch or the edit link
$.fn.zato.delivery_tab.descriptions = function() {

    var tab = $.fn.zato.delivery_tab;
    var config = tab.config;
    var out = {};

    out[tab.elementId('edit', config.retriesLine)] = config.helpRetries;
    out[tab.fieldId(config.fieldUseQueue)] = config.helpUseQueue;
    out[tab.fieldId(config.fieldUseDLQ)] = config.helpUseDLQ;
    out[tab.elementId('edit', config.actionLine)] = config.helpAction;

    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// What the retries line reads as, from the form's fields
$.fn.zato.delivery_tab.formatRetriesSummary = function() {

    var tab = $.fn.zato.delivery_tab;
    var config = tab.config;
    var retries = parseInt(tab.field(config.fieldMaxRetries).val());
    var out;

    if(retries === config.noRetries) {
        out = config.summaryNoRetries;
    }
    else {
        var multiplier = parseInt(tab.field(config.fieldBackoffMultiplier).val());
        var template;

        // Waits that do not grow read as a plain interval
        if(multiplier === config.flatMultiplier) {
            template = config.summaryRetriesFlat;
        }
        else {
            template = config.summaryRetriesGrowing;
        }

        out = template
            .replace('{retries}', $.fn.zato.count_text(retries, config.retrySingular, config.retryPlural))
            .replace('{sleep}', tab.durationText(config.fieldSleepTime))
            .replace('{multiplier}', multiplier)
            .replace('{threshold}', tab.durationText(config.fieldBackoffThreshold));
    }

    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// What the action line reads as, from the form's fields
$.fn.zato.delivery_tab.formatSummary = function() {

    var tab = $.fn.zato.delivery_tab;
    var config = tab.config;
    var action = tab.field(config.fieldAction).val();
    var out;

    if(action === config.actionRetry) {
        var retries = parseInt(tab.field(config.fieldRetries).val());

        out = config.summaryRetry
            .replace('{retries}', $.fn.zato.count_text(retries, config.retrySingular, config.retryPlural))
            .replace('{interval}', tab.durationText(config.fieldRetryInterval));
    }
    else if(action === config.actionForward) {
        var topic = tab.field(config.fieldForwardTo).val();

        if(topic === '') {
            out = config.summaryForwardNoTopic;
        }
        else if(tab.field(config.fieldKeepHeader).is(':checked')) {
            out = config.summaryForwardWithHeader.replace('{topic}', topic);
        }
        else {
            out = config.summaryForwardWithoutHeader.replace('{topic}', topic);
        }
    }
    else if(action === config.actionDiscard) {
        out = config.summaryDiscard;
    }
    else {
        out = config.summaryKeep;
    }

    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// Writes every line of the bound panel from the form - the summaries of the retries and the action lines,
// the whole panel but the retries dimmed while the queue is off, the action line while the DLQ is off
$.fn.zato.delivery_tab.render = function() {

    var tab = $.fn.zato.delivery_tab;
    var config = tab.config;

    var retriesSummary = document.getElementById(tab.elementId('summary', config.retriesLine));
    retriesSummary.textContent = tab.formatRetriesSummary();

    var summary = document.getElementById(tab.elementId('summary', config.actionLine));
    summary.textContent = tab.formatSummary();

    var panel = $('#' + tab.state.panelId);
    var useQueue = tab.field(config.fieldUseQueue).is(':checked');
    panel.toggleClass(config.offClass, !useQueue);

    var actionLine = $('#' + tab.elementId('line', config.actionLine));
    var useDLQ = tab.field(config.fieldUseDLQ).is(':checked');
    actionLine.toggleClass(config.lineOffClass, !useDLQ);
}

// /////////////////////////////////////////////////////////////////////////////

// Shows in the open popover only the rows the action picked in it needs
$.fn.zato.delivery_tab.applyActionRows = function() {

    var tab = $.fn.zato.delivery_tab;
    var config = tab.config;
    var popper = tab.forms._instance.popper;

    var select = popper.querySelector('#' + tab.forms.inputId(config.fieldAction));
    var action = select.value;

    // The two counts share one row, the topic and the header switch have a row each
    var retryRow = popper.querySelector('#' + tab.forms.inputId(config.fieldRetries)).closest('.micro-form-row');
    var forwardToRow = popper.querySelector('#' + tab.forms.inputId(config.fieldForwardTo)).closest('.micro-form-field');
    var keepHeaderRow = popper.querySelector('#' + tab.forms.inputId(config.fieldKeepHeader)).closest('.micro-form-field');

    retryRow.hidden = action !== config.actionRetry;
    forwardToRow.hidden = action !== config.actionForward;
    keepHeaderRow.hidden = action !== config.actionForward;
}

// /////////////////////////////////////////////////////////////////////////////

// Opens the action popover off its link and keeps its rows in step with the action picked in it
$.fn.zato.delivery_tab.openAction = function(link) {

    var tab = $.fn.zato.delivery_tab;
    var config = tab.config;

    tab.forms.open(config.actionLine, link, config.fieldAction);

    var popper = tab.forms._instance.popper;
    var select = popper.querySelector('#' + tab.forms.inputId(config.fieldAction));

    select.addEventListener('change', tab.applyActionRows);
    tab.applyActionRows();
}

// /////////////////////////////////////////////////////////////////////////////

// Wires one form's panel - call it each time before the dialog opens
$.fn.zato.delivery_tab.bind = function(options) {

    var tab = $.fn.zato.delivery_tab;
    var config = tab.config;

    tab.state.panelId = options.panel_id;
    tab.state.fieldPrefix = options.field_prefix;

    tab.field(config.fieldUseQueue).off('change.delivery_tab').on('change.delivery_tab', tab.render);
    tab.field(config.fieldUseDLQ).off('change.delivery_tab').on('change.delivery_tab', tab.render);

    // The cursor lands in the first field of each popover, its value left as it stands
    $('#' + tab.elementId('edit', config.retriesLine)).off('click.delivery_tab').on('click.delivery_tab', function() {
        tab.forms.open(config.retriesLine, this, config.fieldMaxRetries);
    });

    $('#' + tab.elementId('edit', config.actionLine)).off('click.delivery_tab').on('click.delivery_tab', function() {
        tab.openAction(this);
    });

    tab.render();
}

// /////////////////////////////////////////////////////////////////////////////
