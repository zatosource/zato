
// The Producer tab of an outgoing Kafka connection's create and edit forms.

$.fn.zato.outgoing.kafka.producer_tab = {};

$.fn.zato.outgoing.kafka.producer_tab.config = {

    idPrefix: 'kafka-producer-tab',
    idPrefixDjango: 'id_',

    // The popovers share the Delivery tab's layout
    popoverClass: 'delivery-tab-popover',
    popupClass: 'alerts-tab-micro-form',

    // The dialog's own How does it work? badge covers the tab
    showHowItWorks: false,

    // The popovers open inside a dialog, so their buttons are the dialog's plain ones
    doneButtonClass: '',
    otherButtonClass: '',

    fieldCompression: 'compression',
    fieldAcks: 'acks',
    fieldIsIdempotent: 'is_idempotent',
    fieldMaxMessageSize: 'max_message_size',
    fieldLinger: 'linger_ms',
    fieldSendTimeout: 'send_timeout',

    // The suffix of the unit select of a stored number
    unitFieldSuffix: '_unit',

    batchesLine: 'batches',
    acksLine: 'acks',

    // The kit's numbers start at one, a fractional one at zero - a linger of zero sends each message at once
    noLinger: 0,
    lingerStep: 1,

    summaryBatches: '{linger}, {size} at most',
    summaryLingerNone: 'Each sent at once',
    summaryLinger: 'Gathered for {linger}',
    summaryAcks: '{acks}, {timeout} to confirm',

    // The value of the acks option that asks for no confirmation at all
    acksNone: '0',

    batchesTitle: 'Batches',
    acksTitle: 'Acknowledgments',
    labelLinger: 'Gather messages for',
    labelMaxMessageSize: 'Max. message size',
    labelAcks: 'Confirmed by',
    labelSendTimeout: 'Wait for a confirmation at most',

    helpBatches: 'How messages leave this connection - how long they are collected into one batch before the batch ' +
        'is sent and how large a single message may be.',
    helpCompression: 'How messages are compressed before they are sent to Kafka, so that they take less space and ' +
        'bandwidth. None sends them as they are.',
    helpLinger: 'How long to collect messages into one batch before sending it. Zero sends each message immediately.',
    helpMaxMessageSize: 'The largest message this connection will send. A larger one is rejected before it reaches Kafka.',
    helpAcks: 'Kafka runs as several instances and each message is stored on more than one of them. This says how many ' +
        'of these instances have to confirm they stored the message before the send is considered successful, and how ' +
        'long to wait for that confirmation before the send fails and the retry settings of the Delivery tab take over.',
    helpAcksSelect: 'All Kafka instances is the safest. One Kafka instance is faster but the message is lost if that ' +
        'instance crashes before the others receive their copies. No confirmation is the fastest, the send is ' +
        'considered successful the moment the message leaves Zato, and a message can be lost without anyone knowing.',
    helpSendTimeout: 'How long to wait for Kafka to confirm a message before the send fails.',
    helpIsIdempotent: 'A send can fail after Kafka has already stored the message, e.g. the network drops before Kafka ' +
        'confirms it. Zato then sends the message again and, when this is off, Kafka stores it a second time, so the ' +
        'same message appears twice. When this is on, Kafka knows it has already stored the message and keeps one copy ' +
        'only. Requires the confirmation to be set to all Kafka instances.'
};

$.fn.zato.outgoing.kafka.producer_tab.state = {
    panelId: null,
    fieldPrefix: '',

    // The names of the hidden columns, read once off the page's json_script element
    fieldNames: null
};

// The micro-forms kit installs the popover engine here
$.fn.zato.outgoing.kafka.producer_tab.forms = {};

// The json_script element a list page hands the tab's settings through
$.fn.zato.outgoing.kafka.producer_tab.config.settingsId = 'kafka-producer-tab-config';
$.fn.zato.outgoing.kafka.producer_tab.config.cellEmpty = '';

// /////////////////////////////////////////////////////////////////////////////

// The hidden columns of a row the tab's fields travel in, in the order the Django side lists them
$.fn.zato.outgoing.kafka.producer_tab.columns = function() {

    var tab = $.fn.zato.outgoing.kafka.producer_tab;
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
$.fn.zato.outgoing.kafka.producer_tab.row_cells = function(item) {

    var tab = $.fn.zato.outgoing.kafka.producer_tab;
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

$.fn.zato.outgoing.kafka.producer_tab.init = function() {

    var tab = $.fn.zato.outgoing.kafka.producer_tab;
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
$.fn.zato.outgoing.kafka.producer_tab.buildDescriptors = function() {

    var tab = $.fn.zato.outgoing.kafka.producer_tab;
    var config = tab.config;
    var out = {};

    out[config.batchesLine] = {
        title: config.batchesTitle,
        fitContent: true,
        pages: [[
            {field: config.fieldLinger, label: config.labelLinger, kind: 'number', fractional: true, step: config.lingerStep, unitField: tab.unitField(config.fieldLinger)},
            {field: config.fieldMaxMessageSize, label: config.labelMaxMessageSize, kind: 'number', unitField: tab.unitField(config.fieldMaxMessageSize)}
        ]]
    };

    out[config.acksLine] = {
        title: config.acksTitle,
        fitContent: true,
        pages: [[
            {field: config.fieldAcks, label: config.labelAcks, kind: 'select'},
            {field: config.fieldSendTimeout, label: config.labelSendTimeout, kind: 'number', unitField: tab.unitField(config.fieldSendTimeout)}
        ]]
    };

    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// The name of the unit select of a stored number
$.fn.zato.outgoing.kafka.producer_tab.unitField = function(fieldName) {
    var out = fieldName + $.fn.zato.outgoing.kafka.producer_tab.config.unitFieldSuffix;
    return out;
}

// A stored number as the form holds it, with its unit
$.fn.zato.outgoing.kafka.producer_tab.unitText = function(fieldName) {

    var tab = $.fn.zato.outgoing.kafka.producer_tab;
    var count = parseInt(tab.field(fieldName).val());
    var unitSelect = tab.field(tab.unitField(fieldName));
    var singular = unitSelect.val();
    var plural = unitSelect.find('option:selected').text();

    var out = $.fn.zato.count_text(count, singular, plural);
    return out;
}

// The label of the picked option of one of the tab's selects
$.fn.zato.outgoing.kafka.producer_tab.selectText = function(fieldName) {
    var out = $.fn.zato.outgoing.kafka.producer_tab.field(fieldName).find('option:selected').text();
    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// The DOM id of one of the tab's fields
$.fn.zato.outgoing.kafka.producer_tab.fieldId = function(fieldName) {
    var tab = $.fn.zato.outgoing.kafka.producer_tab;
    var out = tab.config.idPrefixDjango + tab.state.fieldPrefix + fieldName;
    return out;
}

// One of the tab's fields
$.fn.zato.outgoing.kafka.producer_tab.field = function(fieldName) {
    var out = $('#' + $.fn.zato.outgoing.kafka.producer_tab.fieldId(fieldName));
    return out;
}

// The id of one element of the bound panel
$.fn.zato.outgoing.kafka.producer_tab.elementId = function(part, lineName) {
    var out = $.fn.zato.outgoing.kafka.producer_tab.state.panelId + '-' + part + '-' + lineName;
    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// The how-it-works texts of the popovers' inputs
$.fn.zato.outgoing.kafka.producer_tab.helpDescriptions = function() {

    var tab = $.fn.zato.outgoing.kafka.producer_tab;
    var config = tab.config;
    var out = {};

    out[tab.forms.inputId(config.fieldLinger)] = config.helpLinger;
    out[tab.forms.inputId(config.fieldMaxMessageSize)] = config.helpMaxMessageSize;
    out[tab.forms.inputId(config.fieldAcks)] = config.helpAcksSelect;
    out[tab.forms.inputId(config.fieldSendTimeout)] = config.helpSendTimeout;

    return out;
}

// The how-it-works texts of the lines - a field always by its create form's id,
// since how-it-works maps an edit form's id back to that one before the lookup
$.fn.zato.outgoing.kafka.producer_tab.descriptions = function() {

    var tab = $.fn.zato.outgoing.kafka.producer_tab;
    var config = tab.config;
    var out = {};

    out[config.idPrefixDjango + config.fieldCompression] = config.helpCompression;
    out[tab.elementId('edit', config.batchesLine)] = config.helpBatches;
    out[tab.elementId('edit', config.acksLine)] = config.helpAcks;
    out[config.idPrefixDjango + config.fieldIsIdempotent] = config.helpIsIdempotent;

    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// The summary of the batches line
$.fn.zato.outgoing.kafka.producer_tab.formatBatchesSummary = function() {

    var tab = $.fn.zato.outgoing.kafka.producer_tab;
    var config = tab.config;

    var linger = parseInt(tab.field(config.fieldLinger).val());
    var lingerText;

    if(linger === config.noLinger) {
        lingerText = config.summaryLingerNone;
    }
    else {
        lingerText = config.summaryLinger.replace('{linger}', tab.unitText(config.fieldLinger));
    }

    var out = config.summaryBatches
        .replace('{linger}', lingerText)
        .replace('{size}', tab.unitText(config.fieldMaxMessageSize));

    return out;
}

// The summary of the acks line
$.fn.zato.outgoing.kafka.producer_tab.formatAcksSummary = function() {

    var tab = $.fn.zato.outgoing.kafka.producer_tab;
    var config = tab.config;

    var out;

    // With no confirmation asked for there is nothing to wait for
    if(tab.field(config.fieldAcks).val() === config.acksNone) {
        out = tab.selectText(config.fieldAcks);
    }
    else {
        out = config.summaryAcks
            .replace('{acks}', tab.selectText(config.fieldAcks))
            .replace('{timeout}', tab.unitText(config.fieldSendTimeout));
    }

    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// Renders the bound panel from the form
$.fn.zato.outgoing.kafka.producer_tab.render = function() {

    var tab = $.fn.zato.outgoing.kafka.producer_tab;
    var config = tab.config;

    var batchesSummary = document.getElementById(tab.elementId('summary', config.batchesLine));
    batchesSummary.textContent = tab.formatBatchesSummary();

    var acksSummary = document.getElementById(tab.elementId('summary', config.acksLine));
    acksSummary.textContent = tab.formatAcksSummary();
}

// /////////////////////////////////////////////////////////////////////////////

// Binds one form's panel, before the dialog opens
$.fn.zato.outgoing.kafka.producer_tab.bind = function(options) {

    var tab = $.fn.zato.outgoing.kafka.producer_tab;
    var config = tab.config;

    tab.state.panelId = options.panel_id;
    tab.state.fieldPrefix = options.field_prefix;

    $('#' + tab.elementId('edit', config.batchesLine)).off('click.producer_tab').on('click.producer_tab', function() {
        tab.forms.open(config.batchesLine, this, config.fieldLinger);
    });

    $('#' + tab.elementId('edit', config.acksLine)).off('click.producer_tab').on('click.producer_tab', function() {
        tab.forms.open(config.acksLine, this, config.fieldAcks);
    });

    tab.render();
}

// /////////////////////////////////////////////////////////////////////////////
