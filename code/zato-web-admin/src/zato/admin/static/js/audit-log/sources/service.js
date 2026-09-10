

// /////////////////////////////////////////////////////////////////////////////

// What a row of the service source shows. An invocation is named by the service
// that ran, and one event is the whole invocation, the request on one side of the
// flow pane, the response on the other, the traceback beside the response when it
// failed. A note is what a service wrote down about its own work through
// self.audit.write - named by its message, wearing the fields the service gave it
// as chips, its data beside the message when it attached any, and sharing the
// invocation's card in the flow. Everything else reads the way the default
// presenter reads it.

(function($) {

var kit = $.fn.zato.dashboard_kit;

var presenterConfig = {

    // The event type of a note a service wrote itself
    noteEventType: 'note',

    // How an invocation's line on a flow card reads - who invoked the service and how long it took
    invokedByLabel: 'Invoked by',
    lineSeparator: ' \u00b7 ',

    // The body kinds each side of the flow pane reads off one invocation
    paneKinds: {
        request: 'request',
        response: 'response'
    },

    // The body kinds each side of the flow pane reads off a note with data attached -
    // the message on the left, being the event's own data, the attached data on the right
    notePaneKinds: {
        request: '',
        response: 'data'
    },

    // The side of the pane the traceback opens beside, and what its tab is called
    paneTracebackRole: 'response',
    tracebackLabel: 'Traceback',
    errorBodyKind: 'error',

    // The body a note's attached data is kept as, and what the tabs reading a note are called
    dataBodyKind: 'data',
    messageTabLabel: 'Message',
    dataTabLabel: 'Data'
};

// Whether a raw row is a note rather than an invocation
var isNote = function(row) {
    return row.event_type === presenterConfig.noteEventType;
};

// Whether a note carries data of its own beside its message
var hasData = function(row) {
    return row.body_kinds.indexOf(presenterConfig.dataBodyKind) !== -1;
};

$.fn.zato.audit_log.sources['service'] = $.extend({}, $.fn.zato.audit_log.sources['default'], {

    // The source's rows already wear the source's name on the role tag, so the
    // source chip saying it again is left out - every other chip reads the default way,
    // and a note wears each field the service wrote down as a chip of its own
    chips: function(row) {
        var chips = $.fn.zato.audit_log.sources['default'].chips(row);
        var out = [];

        for (var chipIndex = 0; chipIndex < chips.length; chipIndex++) {
            var chip = chips[chipIndex];

            if (chip.key === 'source') {
                continue;
            }

            out.push(chip);
        }

        if (!isNote(row)) {
            return out;
        }

        for (var fieldIndex = 0; fieldIndex < row.fields.length; fieldIndex++) {
            var field = row.fields[fieldIndex];
            out.push({key: field.name, label: field.name, value: field.value, tone: 'neutral'});
        }

        return out;
    },

    // ////////////////////////////////////////////////////////////////////////

    // An invocation is known by the service that ran, a note by what it says
    headline: function(row) {
        if (isNote(row)) {
            return row.data;
        }

        return row.object_name;
    },

    // ////////////////////////////////////////////////////////////////////////

    // The Summary tab says everything the default says, and a note's fields after it
    summaryFacts: function(rowModel) {
        var listing = $.fn.zato.audit_log.listing;
        var out = listing.defaultSummaryFacts(rowModel);
        var row = rowModel.raw;

        if (!isNote(row)) {
            return out;
        }

        for (var fieldIndex = 0; fieldIndex < row.fields.length; fieldIndex++) {
            var field = row.fields[fieldIndex];
            out.push(listing.paneFact(field.name, listing.escapeHTML(field.value), field.value, field.value));
        }

        return out;
    },

    // ////////////////////////////////////////////////////////////////////////

    // A note with data attached reads as its message and as that data, an
    // invocation and a bare note read the default way
    payloadTabs: function(rowModel) {
        var row = rowModel.raw;

        if (!isNote(row) || !hasData(row)) {
            return $.fn.zato.audit_log.sources['default'].payloadTabs(rowModel);
        }

        var out = [
            {label: presenterConfig.messageTabLabel, kind: '', parsed: false},
            {label: presenterConfig.dataTabLabel, kind: presenterConfig.dataBodyKind, parsed: true}
        ];

        return out;
    },

    // ////////////////////////////////////////////////////////////////////////

    // One event is the whole invocation - what the service was given on one side,
    // what it returned on the other. A note reads its message on one side and its
    // data on the other, the data side standing empty for a note that attached none,
    // so picking the note on either side brings both sides to it. The notes of an
    // invocation share its card in the flow, each read by its own kinds.
    paneKinds: function(rowModel) {
        var row = rowModel.raw;

        if (isNote(row)) {
            return presenterConfig.notePaneKinds;
        }

        return presenterConfig.paneKinds;
    },

    // A note's line on the card reads its message after the outcome chip, an
    // invocation's line reads who invoked the service and how long it took
    lineNote: function(model) {
        var row = model.raw;

        if (isNote(row)) {
            return row.data;
        }

        var parts = [];

        if (row.endpoint !== '') {
            parts.push(presenterConfig.invokedByLabel + ' ' + row.endpoint);
        }

        if (row.duration_ms !== null) {
            parts.push(kit.format_duration_ms(row.duration_ms));
        }

        return parts.join(presenterConfig.lineSeparator);
    },

    lineTooltip: function(model) {
        var row = model.raw;

        if (isNote(row)) {
            return row.data;
        }

        return $.fn.zato.audit_log.sources['service'].lineNote(model);
    },

    // A failed invocation opens its traceback beside the response, a note opens nothing more
    paneExtras: function(rowModel, role) {
        var row = rowModel.raw;

        if (isNote(row)) {
            return [];
        }

        if (role !== presenterConfig.paneTracebackRole) {
            return [];
        }

        if (row.body_kinds.indexOf(presenterConfig.errorBodyKind) === -1) {
            return [];
        }

        return [{label: presenterConfig.tracebackLabel, kind: presenterConfig.errorBodyKind}];
    }
});

// /////////////////////////////////////////////////////////////////////////////

})(jQuery);
