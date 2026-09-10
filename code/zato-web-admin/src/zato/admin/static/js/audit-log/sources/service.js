


// /////////////////////////////////////////////////////////////////////////////

(function($) {

var dashboardKit = $.fn.zato.dashboard_kit;
var sources = $.fn.zato.audit_log.sources;
var defaultPresenter = sources['default'];

var presenterConfig = {

    requestEventType: 'service-request',
    responseEventType: 'service-response',
    noteEventType: 'note',

    invokedByLabel: 'Invoked by',

    tracebackLabel: 'Traceback',
    errorBodyKind: 'error',

    dataBodyKind: 'data',
    messageTabLabel: 'Message',
    dataTabLabel: 'Data',

    chipTone: 'neutral',
    emptyChipLabel: '',

    // A note field named after a unit of time holds a duration in that unit
    durationUnitMilliseconds: {
        'ms': 1,
        'milliseconds': 1,
        'seconds': 1000,
        'minutes': 60000,
        'hours': 3600000
    },

    // Shortest unit first, each used for durations below its bound
    durationWords: [
        {word: 'ms', unitMilliseconds: 1, below: 1000},
        {word: 'sec', unitMilliseconds: 1000, below: 60000},
        {word: 'min', unitMilliseconds: 60000, below: 3600000},
        {word: 'h', unitMilliseconds: 3600000, below: Infinity}
    ]
};

// /////////////////////////////////////////////////////////////////////////////

var durationText = function(milliseconds) {
    var words = presenterConfig.durationWords;
    var out = '';

    for (var wordIndex = 0; wordIndex < words.length; wordIndex++) {
        var entry = words[wordIndex];

        if (milliseconds < entry.below) {
            var units = milliseconds / entry.unitMilliseconds;
            var rounded = Math.round(units);

            out = rounded + ' ' + entry.word;
            break;
        }
    }

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

var isDurationField = function(field) {
    var unitMilliseconds = presenterConfig.durationUnitMilliseconds[field.name];
    var out = unitMilliseconds !== undefined;

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// The attr table stores every value as text
var durationFieldMilliseconds = function(field) {
    var value = Number(field.value);
    var unitMilliseconds = presenterConfig.durationUnitMilliseconds[field.name];

    var out = value * unitMilliseconds;

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

var isNote = function(row) {
    var out = row.event_type === presenterConfig.noteEventType;
    return out;
};

// /////////////////////////////////////////////////////////////////////////////

var isRequest = function(row) {
    var out = row.event_type === presenterConfig.requestEventType;
    return out;
};

// /////////////////////////////////////////////////////////////////////////////

var hasData = function(row) {
    var dataIndex = row.body_kinds.indexOf(presenterConfig.dataBodyKind);
    var out = dataIndex !== -1;

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

var hasError = function(row) {
    var errorIndex = row.body_kinds.indexOf(presenterConfig.errorBodyKind);
    var out = errorIndex !== -1;

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

var servicePresenter = $.extend({}, defaultPresenter, {

    chips: function(row) {
        var defaultChips = defaultPresenter.chips(row);
        var out = [];

        for (var chipIndex = 0; chipIndex < defaultChips.length; chipIndex++) {
            var chip = defaultChips[chipIndex];

            if (chip.key === 'source') {
                continue;
            }

            out.push(chip);
        }

        if (isNote(row)) {
            for (var fieldIndex = 0; fieldIndex < row.fields.length; fieldIndex++) {
                var field = row.fields[fieldIndex];
                var fieldChip;

                if (isDurationField(field)) {
                    var milliseconds = durationFieldMilliseconds(field);
                    var text = durationText(milliseconds);

                    fieldChip = {key: field.name, label: presenterConfig.emptyChipLabel, value: text,
                        tone: presenterConfig.chipTone};
                }
                else {
                    fieldChip = {key: field.name, label: field.name, value: field.value,
                        tone: presenterConfig.chipTone};
                }

                out.push(fieldChip);
            }
        }

        return out;
    },

    // ////////////////////////////////////////////////////////////////////////

    headline: function(row) {
        var out;

        if (isNote(row)) {
            out = row.data;
        }
        else {
            out = row.object_name;
        }

        return out;
    },

    // ////////////////////////////////////////////////////////////////////////

    summaryFacts: function(rowModel) {
        var listing = $.fn.zato.audit_log.listing;
        var row = rowModel.raw;
        var out = listing.defaultSummaryFacts(rowModel);

        if (isNote(row)) {
            for (var fieldIndex = 0; fieldIndex < row.fields.length; fieldIndex++) {
                var field = row.fields[fieldIndex];
                var valueHTML = listing.escapeHTML(field.value);
                var fact = listing.paneFact(field.name, valueHTML, field.value, field.value);

                out.push(fact);
            }
        }

        return out;
    },

    // ////////////////////////////////////////////////////////////////////////

    payloadTabs: function(rowModel) {
        var row = rowModel.raw;
        var isNoteWithData = false;

        if (isNote(row)) {
            if (hasData(row)) {
                isNoteWithData = true;
            }
        }

        var out;

        if (isNoteWithData) {
            out = [
                {label: presenterConfig.messageTabLabel, kind: '', parsed: false},
                {label: presenterConfig.dataTabLabel, kind: presenterConfig.dataBodyKind, parsed: true}
            ];
        }
        else {
            out = defaultPresenter.payloadTabs(rowModel);
        }

        return out;
    },

    // ////////////////////////////////////////////////////////////////////////

    lineTypeLabel: function(model) {
        var out = '';

        if (!isRequest(model.raw)) {
            out = model.eventLabel;
        }

        return out;
    },

    // ////////////////////////////////////////////////////////////////////////

    lineNote: function(model) {
        var row = model.raw;
        var out = '';

        if (isNote(row)) {
            out = row.data;
        }
        else if (isRequest(row)) {
            if (row.endpoint !== '') {
                out = presenterConfig.invokedByLabel + ' ' + row.endpoint;
            }
        }
        else if (row.duration_ms !== null) {
            out = dashboardKit.format_duration_ms(row.duration_ms);
        }

        return out;
    },

    // ////////////////////////////////////////////////////////////////////////

    headerNote: function(model) {
        var out = '';

        if (!isNote(model.raw)) {
            out = servicePresenter.lineNote(model);
        }

        return out;
    },

    // ////////////////////////////////////////////////////////////////////////

    paneExtras: function(rowModel) {
        var out = [];

        if (hasError(rowModel.raw)) {
            var tracebackTab = {label: presenterConfig.tracebackLabel, kind: presenterConfig.errorBodyKind};
            out.push(tracebackTab);
        }

        return out;
    }
});

sources['service'] = servicePresenter;

// /////////////////////////////////////////////////////////////////////////////

})(jQuery);
