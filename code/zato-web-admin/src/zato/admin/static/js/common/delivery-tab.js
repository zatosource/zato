
// The Delivery tab of an outgoing connection's create and edit forms.

$.fn.zato.delivery_tab.config = {

    idPrefix: 'delivery-tab',
    idPrefixDjango: 'id_',

    popoverClass: 'delivery-tab-popover',
    popupClass: 'alerts-tab-micro-form',

    // The dialog's own How does it work? badge covers the tab
    showHowItWorks: false,

    // The popovers open inside a dialog, so their buttons are the dialog's plain ones
    doneButtonClass: '',
    otherButtonClass: '',

    // The panel is dimmed while the queue is off, the action line while the DLQ is off
    offClass: 'alerts-tab-off',
    lineOffClass: 'alerts-tab-line-off',

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

    // The suffix of the unit select of a count of seconds
    unitFieldSuffix: '_unit',

    retriesLine: 'retries',
    actionLine: 'dlq_action',

    // The kit's numbers start at one, a fractional one at zero
    noRetries: 0,
    retriesStep: 1,

    flatMultiplier: 1,

    summaryNoRetries: 'No retries',
    summaryRetriesGrowing: '{retries}, {sleep} then {multiplier}x longer, {threshold} at most',
    summaryRetriesFlat: '{retries}, {sleep} apart, {threshold} at most',

    actionKeep: 'keep',
    actionRetry: 'retry',
    actionForward: 'forward',
    actionDiscard: 'discard',

    summaryKeep: 'Keep in DLQ',
    summaryRetry: '{retries}, every {interval}',
    summaryForwardWithHeader: 'Forward to {topic} with the DLQ header',
    summaryForwardWithoutHeader: 'Forward to {topic} without the DLQ header',
    summaryForwardNoTopic: 'Forward to topic - none picked yet',
    summaryDiscard: 'Discard',

    retrySingular: 'retry',
    retryPlural: 'retries',

    retriesTitle: 'Retries',
    dlqTitle: 'Dead-letter queue',
    labelUseQueue: 'Use queue',
    labelUseDLQ: 'Use DLQ',
    labelMaxRetries: 'Max. retries',
    labelSleepTime: 'Wait before the first retry',
    labelBackoffThreshold: 'Wait in total at most',
    labelBackoffMultiplier: 'Wait multiplier',

    popoverTitle: 'DLQ action',
    labelAction: 'Action',
    labelRetries: 'Max. retries',
    labelRetryInterval: 'Every',
    labelForwardTo: 'Forward to topic',
    labelKeepHeader: 'Keep the DLQ header',

    helpRetries: 'What happens to a message that fails - how many times it is sent again, how long the first wait is, ' +
        'how much longer each next wait is and how long all the waits may add up to. With no retries a message ' +
        'is sent once.',
    helpMaxRetries: 'How many times a failed invocation is retried. 0 means no retries at all.',
    helpSleepTime: 'How long to wait before the first retry. Each next wait is longer by the multiplier.',
    helpBackoffThreshold: 'A cap on the total time spent waiting between retries. Once reached, no more retries take place.',
    helpBackoffMultiplier: 'Each retry waits this many times longer than the previous one, up to 8 seconds per a single wait.',
    helpUseQueue: 'When on, a message is sent right away and, if the endpoint does not accept it, it is placed in ' +
        'the connection\'s own queue and delivered from there one at a time, in order, retried as the retry settings say. ' +
        'While the queue holds messages, new ones join it behind them. When off, each message is sent and retried on its own.',
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

$.fn.zato.delivery_tab.state = {
    panelId: null,
    fieldPrefix: '',

    // The names of the hidden columns, read once off the page's json_script element
    fieldNames: null
};

// The micro-forms kit installs the popover engine here
$.fn.zato.delivery_tab.forms = {};

// The json_script element a list page hands the tab's settings through
$.fn.zato.delivery_tab.config.settingsId = 'delivery-tab-config';
$.fn.zato.delivery_tab.config.cellEmpty = '';

// The link to a connection's delivery page
$.fn.zato.delivery_tab.config.deliveryPageUrl = '/zato/outgoing/delivery/';
$.fn.zato.delivery_tab.config.deliveryPageTab = 'queue';
$.fn.zato.delivery_tab.config.deliveryLinkLabel = 'Delivery queue';

// /////////////////////////////////////////////////////////////////////////////

// The cell of a new row that links to the connection's delivery page
$.fn.zato.delivery_tab.link_cell = function(connType, item, clusterId) {

    var config = $.fn.zato.delivery_tab.config;

    var url = config.deliveryPageUrl + connType + '/' + item.id + '/?cluster=' + clusterId + '&tab=' + config.deliveryPageTab;

    var out = String.format('<td><a href="{0}">{1}</a></td>', url, config.deliveryLinkLabel);
    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// The hidden columns of a row the tab's fields travel in, in the order the Django side lists them
$.fn.zato.delivery_tab.columns = function() {

    var tab = $.fn.zato.delivery_tab;
    var state = tab.state;

    if(state.fieldNames === null) {
        var settings = JSON.parse(document.getElementById(tab.config.settingsId).textContent);
        state.fieldNames = settings.field_names;
    }

    var out = state.fieldNames.slice();
    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// The hidden cells of a new row, one per column above
$.fn.zato.delivery_tab.row_cells = function(item) {

    var tab = $.fn.zato.delivery_tab;
    var out = '';

    tab.columns().forEach(function(fieldName) {

        var value = item[fieldName];

        if(value === undefined) {
            value = tab.config.cellEmpty;
        }

        out += String.format("<td class='ignore'>{0}</td>", value);
    });

    return out;
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.delivery_tab.init = function() {

    var tab = $.fn.zato.delivery_tab;
    var config = tab.config;

    $.fn.zato.micro_forms.setup(tab, {
        descriptors: tab.buildDescriptors(),
        popupClass: config.popoverClass + ' ' + config.popupClass,
        showHowItWorks: config.showHowItWorks,
        doneButtonClass: config.doneButtonClass,
        otherButtonClass: config.otherButtonClass,
        showCancel: true,
        onDone: tab.render
    });
}

// /////////////////////////////////////////////////////////////////////////////

// The descriptors of the two micro-forms
$.fn.zato.delivery_tab.buildDescriptors = function() {

    var tab = $.fn.zato.delivery_tab;
    var config = tab.config;
    var out = {};

    out[config.retriesLine] = {
        title: config.retriesTitle,
        fitContent: true,
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

// A count of seconds as the form holds it, with its unit
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

// The DOM id of one of the tab's fields
$.fn.zato.delivery_tab.fieldId = function(fieldName) {
    var tab = $.fn.zato.delivery_tab;
    var out = tab.config.idPrefixDjango + tab.state.fieldPrefix + fieldName;
    return out;
}

// One of the tab's fields
$.fn.zato.delivery_tab.field = function(fieldName) {
    var out = $('#' + $.fn.zato.delivery_tab.fieldId(fieldName));
    return out;
}

// The id of one element of the bound panel
$.fn.zato.delivery_tab.elementId = function(part, lineName) {
    var out = $.fn.zato.delivery_tab.state.panelId + '-' + part + '-' + lineName;
    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// The how-it-works texts of the popovers' inputs
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

// The how-it-works texts of the lines
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

// The summary of the retries line
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

// The summary of the action line
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

// Renders the bound panel from the form
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

// Shows only the rows the picked action needs, in the popover of the given micro-forms instance
$.fn.zato.delivery_tab.applyActionRows = function(forms) {

    var tab = $.fn.zato.delivery_tab;
    var config = tab.config;
    var popper = forms._instance.popper;

    var select = popper.querySelector('#' + forms.inputId(config.fieldAction));
    var action = select.value;

    var retryRow = popper.querySelector('#' + forms.inputId(config.fieldRetries)).closest('.micro-form-row');
    var forwardToRow = popper.querySelector('#' + forms.inputId(config.fieldForwardTo)).closest('.micro-form-field');
    var keepHeaderRow = popper.querySelector('#' + forms.inputId(config.fieldKeepHeader)).closest('.micro-form-field');

    retryRow.hidden = action !== config.actionRetry;
    forwardToRow.hidden = action !== config.actionForward;
    keepHeaderRow.hidden = action !== config.actionForward;
}

// /////////////////////////////////////////////////////////////////////////////

// Gives an open popover of another micro-forms instance the tab's own class, under which
// delivery-tab.css lays its rows out and hides the ones an action does not need
$.fn.zato.delivery_tab.markPopover = function(forms) {

    var tab = $.fn.zato.delivery_tab;
    var popper = forms._instance.popper;

    var out = popper.querySelector('#' + forms.config.popupId);
    out.classList.add(tab.config.popoverClass);

    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// Wires the action select of an open popover - the rows follow the pick, and the popover keeps
// the width of all its rows, so it does not resize as rows hide
$.fn.zato.delivery_tab.bindActionRows = function(forms) {

    var tab = $.fn.zato.delivery_tab;
    var config = tab.config;
    var popper = forms._instance.popper;

    var select = popper.querySelector('#' + forms.inputId(config.fieldAction));

    var container = tab.markPopover(forms);
    container.style.width = container.offsetWidth + 'px';

    select.addEventListener('change', function() {
        tab.applyActionRows(forms);
    });

    tab.applyActionRows(forms);
}

// /////////////////////////////////////////////////////////////////////////////

// Opens the action popover
$.fn.zato.delivery_tab.openAction = function(link) {

    var tab = $.fn.zato.delivery_tab;
    var config = tab.config;

    tab.forms.open(config.actionLine, link, config.fieldAction);
    tab.bindActionRows(tab.forms);
}

// /////////////////////////////////////////////////////////////////////////////

// Binds one form's panel, before the dialog opens
$.fn.zato.delivery_tab.bind = function(options) {

    var tab = $.fn.zato.delivery_tab;
    var config = tab.config;

    tab.state.panelId = options.panel_id;
    tab.state.fieldPrefix = options.field_prefix;

    tab.field(config.fieldUseQueue).off('change.delivery_tab').on('change.delivery_tab', tab.render);
    tab.field(config.fieldUseDLQ).off('change.delivery_tab').on('change.delivery_tab', tab.render);

    $('#' + tab.elementId('edit', config.retriesLine)).off('click.delivery_tab').on('click.delivery_tab', function() {
        tab.forms.open(config.retriesLine, this, config.fieldMaxRetries);
    });

    $('#' + tab.elementId('edit', config.actionLine)).off('click.delivery_tab').on('click.delivery_tab', function() {
        tab.openAction(this);
    });

    tab.render();
}

// /////////////////////////////////////////////////////////////////////////////
