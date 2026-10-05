
// The Consumer tab of a Kafka channel's create and edit forms.

$.fn.zato.channel.kafka.consumer_tab = {};

$.fn.zato.channel.kafka.consumer_tab.config = {

    idPrefix: 'kafka-consumer-tab',
    idPrefixDjango: 'id_',

    popoverClass: 'delivery-tab-popover',
    popupClass: 'alerts-tab-micro-form',

    showHowItWorks: false,

    doneButtonClass: '',
    otherButtonClass: '',

    fieldTopics: 'topics',
    fieldAutoOffsetReset: 'auto_offset_reset',
    fieldMaxMessageSize: 'max_message_size',
    fieldMaxInFlight: 'max_in_flight',
    fieldShouldDeliverTombstones: 'should_deliver_tombstones',
    fieldDeduplicationHeader: 'dedup_header',
    fieldDeduplicationTTL: 'dedup_ttl',

    // The suffix of the unit select of a stored number
    unitFieldSuffix: '_unit',

    limitsLine: 'limits',
    deduplicationLine: 'dedup',

    summaryLimits: '{size} per message, {inFlight} in flight',
    summaryDeduplicationOff: 'Off',
    summaryDeduplicationOn: 'By header {header}, remembered for {ttl}',

    messageSingular: 'message',
    messagePlural: 'messages',

    limitsTitle: 'Limits',
    deduplicationTitle: 'Deduplication',
    labelMaxMessageSize: 'Message size',
    labelMaxInFlight: 'In flight',
    labelDeduplicationHeader: 'Header',
    labelDeduplicationTTL: 'Remembered for',

    helpTopics: 'The topics this channel reads, one per line.',
    helpAutoOffsetReset: 'Where to start reading a topic the consumer group has no position in yet - at its latest ' +
        'message or at its earliest.',
    helpLimits: 'The largest message read and how many messages may be unconfirmed at once.',
    helpMaxMessageSize: 'The largest message this channel will read.',
    helpMaxInFlight: 'How many messages may be read ahead and not yet confirmed.',
    helpShouldDeliverTombstones: 'Whether a message with a key and no payload invokes the service, with an empty payload ' +
        'and the kafka.is_tombstone header. When off, it is confirmed and skipped.',
    helpDeduplication: 'Whether a message that arrives twice invokes the service twice. With a header picked, a repeat ' +
        'with the same value is confirmed and skipped.',
    helpDeduplicationHeader: 'The header whose value tells one message from another, empty to turn deduplication off.',
    helpDeduplicationTTL: 'How long a value is remembered.'
};

$.fn.zato.channel.kafka.consumer_tab.state = {
    panelId: null,
    fieldPrefix: '',

    // The names of the hidden columns, read once off the page's json_script element
    fieldNames: null
};

$.fn.zato.channel.kafka.consumer_tab.forms = {};

// The json_script element a list page hands the tab's settings through
$.fn.zato.channel.kafka.consumer_tab.config.settingsId = 'kafka-consumer-tab-config';

// /////////////////////////////////////////////////////////////////////////////

// The settings the page hands over, read once
$.fn.zato.channel.kafka.consumer_tab.settings = function() {

    var tab = $.fn.zato.channel.kafka.consumer_tab;
    var state = tab.state;

    if(state.fieldNames === null) {
        var settings = JSON.parse(document.getElementById(tab.config.settingsId).textContent);
        state.fieldNames = settings.field_names;
        state.settings = settings;
    }

    var out = state.settings;
    return out;
}

// The hidden columns of a row the tab's fields travel in, in the order the Django side lists them
$.fn.zato.channel.kafka.consumer_tab.columns = function() {

    var tab = $.fn.zato.channel.kafka.consumer_tab;
    tab.settings();

    var out = tab.state.fieldNames.slice();
    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// The hidden cells of a new row, one per column above
$.fn.zato.channel.kafka.consumer_tab.row_cells = function(item) {

    var tab = $.fn.zato.channel.kafka.consumer_tab;
    var out = '';

    tab.columns().forEach(function(fieldName) {
        out += String.format("<td class='ignore'>{0}</td>", _.escape(item[fieldName]));
    });

    return out;
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.kafka.consumer_tab.init = function() {

    var tab = $.fn.zato.channel.kafka.consumer_tab;
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
$.fn.zato.channel.kafka.consumer_tab.buildDescriptors = function() {

    var tab = $.fn.zato.channel.kafka.consumer_tab;
    var config = tab.config;
    var out = {};

    out[config.limitsLine] = {
        title: config.limitsTitle,
        fitContent: true,
        pages: [[
            {field: config.fieldMaxMessageSize, label: config.labelMaxMessageSize, kind: 'number', unitField: tab.unitField(config.fieldMaxMessageSize)},
            {field: config.fieldMaxInFlight, label: config.labelMaxInFlight, kind: 'number'}
        ]]
    };

    out[config.deduplicationLine] = {
        title: config.deduplicationTitle,
        fitContent: true,
        pages: [[
            {field: config.fieldDeduplicationHeader, label: config.labelDeduplicationHeader, kind: 'text'},
            {field: config.fieldDeduplicationTTL, label: config.labelDeduplicationTTL, kind: 'number', unitField: tab.unitField(config.fieldDeduplicationTTL)}
        ]]
    };

    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// The name of the unit select of a stored number
$.fn.zato.channel.kafka.consumer_tab.unitField = function(fieldName) {
    var out = fieldName + $.fn.zato.channel.kafka.consumer_tab.config.unitFieldSuffix;
    return out;
}

// A stored number as the form holds it, with its unit
$.fn.zato.channel.kafka.consumer_tab.unitText = function(fieldName) {

    var tab = $.fn.zato.channel.kafka.consumer_tab;
    var count = parseInt(tab.field(fieldName).val());
    var unitSelect = tab.field(tab.unitField(fieldName));
    var singular = unitSelect.val();
    var plural = unitSelect.find('option:selected').text();

    var out = $.fn.zato.count_text(count, singular, plural);
    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// The DOM id of one of the tab's fields
$.fn.zato.channel.kafka.consumer_tab.fieldId = function(fieldName) {
    var tab = $.fn.zato.channel.kafka.consumer_tab;
    var out = tab.config.idPrefixDjango + tab.state.fieldPrefix + fieldName;
    return out;
}

// One of the tab's fields
$.fn.zato.channel.kafka.consumer_tab.field = function(fieldName) {
    var out = $('#' + $.fn.zato.channel.kafka.consumer_tab.fieldId(fieldName));
    return out;
}

// The id of one element of the bound panel
$.fn.zato.channel.kafka.consumer_tab.elementId = function(part, lineName) {
    var out = $.fn.zato.channel.kafka.consumer_tab.state.panelId + '-' + part + '-' + lineName;
    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// The how-it-works texts of the popovers' inputs
$.fn.zato.channel.kafka.consumer_tab.helpDescriptions = function() {

    var tab = $.fn.zato.channel.kafka.consumer_tab;
    var config = tab.config;
    var out = {};

    out[tab.forms.inputId(config.fieldMaxMessageSize)] = config.helpMaxMessageSize;
    out[tab.forms.inputId(config.fieldMaxInFlight)] = config.helpMaxInFlight;
    out[tab.forms.inputId(config.fieldDeduplicationHeader)] = config.helpDeduplicationHeader;
    out[tab.forms.inputId(config.fieldDeduplicationTTL)] = config.helpDeduplicationTTL;

    return out;
}

// The how-it-works texts of the lines, keyed by the create form's ids
$.fn.zato.channel.kafka.consumer_tab.descriptions = function() {

    var tab = $.fn.zato.channel.kafka.consumer_tab;
    var config = tab.config;
    var out = {};

    out[config.idPrefixDjango + config.fieldTopics] = config.helpTopics;
    out[config.idPrefixDjango + config.fieldAutoOffsetReset] = config.helpAutoOffsetReset;
    out[tab.elementId('edit', config.limitsLine)] = config.helpLimits;
    out[config.idPrefixDjango + config.fieldShouldDeliverTombstones] = config.helpShouldDeliverTombstones;
    out[tab.elementId('edit', config.deduplicationLine)] = config.helpDeduplication;

    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// The summary of the limits line
$.fn.zato.channel.kafka.consumer_tab.formatLimitsSummary = function() {

    var tab = $.fn.zato.channel.kafka.consumer_tab;
    var config = tab.config;

    var inFlight = parseInt(tab.field(config.fieldMaxInFlight).val());

    var out = config.summaryLimits
        .replace('{size}', tab.unitText(config.fieldMaxMessageSize))
        .replace('{inFlight}', $.fn.zato.count_text(inFlight, config.messageSingular, config.messagePlural));

    return out;
}

// The summary of the deduplication line
$.fn.zato.channel.kafka.consumer_tab.formatDeduplicationSummary = function() {

    var tab = $.fn.zato.channel.kafka.consumer_tab;
    var config = tab.config;

    var header = tab.field(config.fieldDeduplicationHeader).val().trim();
    var out;

    if(header === '') {
        out = config.summaryDeduplicationOff;
    }
    else {
        out = config.summaryDeduplicationOn
            .replace('{header}', header)
            .replace('{ttl}', tab.unitText(config.fieldDeduplicationTTL));
    }

    return out;
}

// /////////////////////////////////////////////////////////////////////////////

// Renders the bound panel from the form
$.fn.zato.channel.kafka.consumer_tab.render = function() {

    var tab = $.fn.zato.channel.kafka.consumer_tab;
    var config = tab.config;

    var limitsSummary = document.getElementById(tab.elementId('summary', config.limitsLine));
    limitsSummary.textContent = tab.formatLimitsSummary();

    var deduplicationSummary = document.getElementById(tab.elementId('summary', config.deduplicationLine));
    deduplicationSummary.textContent = tab.formatDeduplicationSummary();
}

// /////////////////////////////////////////////////////////////////////////////

// Binds one form's panel, before the dialog opens
$.fn.zato.channel.kafka.consumer_tab.bind = function(options) {

    var tab = $.fn.zato.channel.kafka.consumer_tab;
    var config = tab.config;

    tab.state.panelId = options.panel_id;
    tab.state.fieldPrefix = options.field_prefix;

    $('#' + tab.elementId('edit', config.limitsLine)).off('click.consumer_tab').on('click.consumer_tab', function() {
        tab.forms.open(config.limitsLine, this, config.fieldMaxMessageSize);
    });

    $('#' + tab.elementId('edit', config.deduplicationLine)).off('click.consumer_tab').on('click.consumer_tab', function() {
        tab.forms.open(config.deduplicationLine, this, config.fieldDeduplicationHeader);
    });

    tab.render();
}

// /////////////////////////////////////////////////////////////////////////////
