

// /////////////////////////////////////////////////////////////////////////////

// What a row of the service source shows. An invocation is two events named by
// the service that ran - its request, written down before the service runs, and
// its response, written after, the traceback beside the response when it failed.
// A note is what a service wrote down about its own work through self.audit.write -
// named by its message, wearing the fields the service gave it as chips, its data
// beside the message when it attached any. All three share the invocation's card
// in the flow. Everything else reads the way the default presenter reads it.

(function($) {

var kit = $.fn.zato.dashboard_kit;

var presenterConfig = {

    // The event types of the three things a service writes down
    requestEventType: 'service-request',
    responseEventType: 'service-response',
    noteEventType: 'note',

    // How a request's line on a flow card reads - who invoked the service
    invokedByLabel: 'Invoked by',

    // What the flow pane's tab of a failed response's traceback is called, and the body it opens
    tracebackLabel: 'Traceback',
    errorBodyKind: 'error',

    // The body a note's attached data is kept as, and what the listing's tabs reading a note are called
    dataBodyKind: 'data',
    messageTabLabel: 'Message',
    dataTabLabel: 'Data'
};

// Whether a raw row is a note rather than a request or a response
var isNote = function(row) {
    return row.event_type === presenterConfig.noteEventType;
};

// Whether a raw row is the request a service was given
var isRequest = function(row) {
    return row.event_type === presenterConfig.requestEventType;
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

    // A note with data attached reads as its message and as that data, a request,
    // a response and a bare note read the default way
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

    // A request reports no outcome and its role chip already says it is a request,
    // so its line writes no kind of its own
    lineTypeLabel: function(model) {
        if (isRequest(model.raw)) {
            return '';
        }

        return model.eventLabel;
    },

    // A note's line on the card reads its message after the outcome chip, a
    // request's line reads who invoked the service, a response's how long it took
    lineNote: function(model) {
        var row = model.raw;

        if (isNote(row)) {
            return row.data;
        }

        if (isRequest(row)) {
            if (row.endpoint === '') {
                return '';
            }

            return presenterConfig.invokedByLabel + ' ' + row.endpoint;
        }

        if (row.duration_ms === null) {
            return '';
        }

        return kit.format_duration_ms(row.duration_ms);
    },

    lineTooltip: function(model) {
        return $.fn.zato.audit_log.sources['service'].lineNote(model);
    },

    // A failed response opens its traceback beside itself, a request and a note open nothing more
    paneExtras: function(rowModel) {
        var row = rowModel.raw;

        if (row.body_kinds.indexOf(presenterConfig.errorBodyKind) === -1) {
            return [];
        }

        return [{label: presenterConfig.tracebackLabel, kind: presenterConfig.errorBodyKind}];
    }
});

// /////////////////////////////////////////////////////////////////////////////

})(jQuery);
