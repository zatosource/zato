

// /////////////////////////////////////////////////////////////////////////////

// The rows of the audit log listing.

(function($) {

var kit = $.fn.zato.dashboard_kit;
var listing = $.fn.zato.audit_log.listing;

// /////////////////////////////////////////////////////////////////////////////

// Not every event type reports an outcome - a message arriving is neither a success nor
// a failure until something is done with it, and an event with nothing to say here says nothing.
// The badge doubles as a filter - clicking it narrows the legend down to its own outcome.
listing.outcomeBadgeHTML = function(rowModel) {
    if (rowModel.outcome === '') {
        return '';
    }

    var out = '<span class="audit-log-outcome-filter" data-outcome="' +
        listing.escapeHTML(rowModel.outcome) + '">' +
        kit.outcome.badge(rowModel.outcome, kit.palette.outcome_palette) + '</span>';

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// One row of the poll as everything drawing it reads it. Each row is drawn by the source
// that wrote it down - on a single-source page that is the page's own source, and on the
// all-events page the sources mix on one list.
listing.buildRow = function(row) {
    var presenter = $.fn.zato.audit_log.presenterFor(row.source);

    var out = {
        raw: row,
        id: row.id,
        cid: row.cid,
        msgId: row.msg_id,
        correlId: row.correl_id,
        endpoint: row.endpoint,
        eventType: row.event_type,
        eventLabel: $.fn.zato.audit_log.eventLabel(row.event_type),
        outcome: row.outcome,
        status: row.status,
        classification: row.classification,
        timeIso: row.event_time_iso,
        timeLocal: kit.format_local_time_precise(row.event_time_iso),
        size: row.size,
        durationMs: row.duration_ms,
        parents: row.parents,
        children: row.children,
        bodyKinds: row.body_kinds,
        isResubmitted: row.is_resubmitted,
        role: presenter.role(row)
    };

    // The labels come keyed by source, so any row of any listing knows what its action
    // link says - a source with no resubmit of its own is simply absent from the map.
    var sourceLabels = $.fn.zato.audit_log.config.resubmitLabels[row.source];

    if (sourceLabels !== undefined) {
        out.actionLabel = sourceLabels[row.event_type];
    }

    // A source names its messages by something of its own - its control id, its message
    // id - and the presenter is where the source says what that is.
    out.identity = presenter.identity(row);

    out.chips = presenter.chips(row);
    out.headline = presenter.headline(row);

    // An event a source has no name of its own for is still called something, so the pane
    // heading it always reads as the message the list was pointed at.
    if (out.headline === '') {
        out.headline = out.identity;
    }

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

listing.buildRows = function(rows) {
    var out = [];

    for (var rowIndex = 0; rowIndex < rows.length; rowIndex++) {
        out.push(listing.buildRow(rows[rowIndex]));
    }

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// The event of one id among the ones the list currently holds, and null for an event
// that is on a page of its own
listing.modelById = function(eventId) {
    var out = null;

    for (var rowIndex = 0; rowIndex < listing.visible.length; rowIndex++) {
        if (String(listing.visible[rowIndex].id) === String(eventId)) {
            out = listing.visible[rowIndex];
            break;
        }
    }

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// The action cell holds the link alone - being resubmitted already is a fact about the
// message, so it stands among the row's other badges, not next to an action
listing.actionHTML = function(rowModel) {
    var html = '';

    // Only the event types their source declared resubmittable have anything to offer here.
    if (rowModel.actionLabel !== undefined) {
        html += '<a href="javascript:void(0)" class="audit-log-resubmit-link" data-id="' +
            rowModel.id + '">' + rowModel.actionLabel + '</a>';
    }

    return html;
};

// /////////////////////////////////////////////////////////////////////////////

// Which cells the events now on the page have anything to say in
listing.updateColumns = function() {
    var columns = {action: false};

    for (var rowIndex = 0; rowIndex < listing.visible.length; rowIndex++) {
        var rowModel = listing.visible[rowIndex];

        if (rowModel.actionLabel !== undefined) {
            columns.action = true;
        }
    }

    listing.columns = columns;
};

// /////////////////////////////////////////////////////////////////////////////

// How many cells a row of the list currently has, which is what a row standing in
// for the whole list spans
listing.columnCount = function() {
    var columns = listing.columns;

    // Where a row stands, when it happened, which way it went, what it was, and the cell at the
    // end that takes up whatever room the row has over, are the five the list always holds.
    var out = 5;

    if (columns.action) {
        out += 1;
    }

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// The chips a row carries, which is the first few of the ones the presenter named
listing.rowChips = function(rowModel) {
    var presenter = $.fn.zato.audit_log.presenterFor(rowModel.raw.source);

    var out = rowModel.chips.slice(0, presenter.rowChipLimit);
    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// The event word as a chip - a good tone for an event that went well and a bad one for
// an event that failed, so the row says how it went in the same breath as what it was
listing.eventChip = function(rowModel) {
    var config = listing.config;
    var tone = config.eventChipTone;
    var text = rowModel.eventLabel;

    if (rowModel.outcome === config.errorOutcome) {
        tone = config.eventChipErrorTone;
    }

    // A running event reads as such in the running tone.
    if (rowModel.outcome === config.runningOutcome) {
        tone = config.eventChipRunningTone;
        text = config.runningLabel;
    }

    var chip = {key: 'event_type', label: '', value: rowModel.eventType, text: text, tone: tone};

    // The source has the last word on the chip.
    var presenter = $.fn.zato.audit_log.presenterFor(rowModel.raw.source);
    var out = presenter.eventChip(rowModel, chip);

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// The one line the source sums an event up with, empty for a source without one.
listing.sentenceOf = function(rowModel) {
    var presenter = $.fn.zato.audit_log.presenterFor(rowModel.raw.source);
    return presenter.sentence(rowModel.raw);
};

// /////////////////////////////////////////////////////////////////////////////

// When an event happened - which day it was, read as how far back that day is, then the time of
// day down to the last digit it was written down with, two events of one exchange sharing
// everything above that digit. The list is scanned, not scrubbed - the scrubber lives on
// the pane's Time row, where one event is being read on its own.
listing.timeCellHTML = function(rowModel) {
    var out = '<span class="audit-log-cell-day">' +
        listing.escapeHTML(kit.time_ago_label(rowModel.timeIso)) + '</span>' +
        listing.escapeHTML(listing.config.dayTimeSeparator) +
        listing.escapeHTML(rowModel.timeLocal.slice(11));

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// One event as one line - which event it is, when it happened, which way it went, what it
// is and the one thing it is best known by, how it turned out and what can be done with it.
// Everything else an event says is read in the pane.
listing.rowHTML = function(rowModel) {
    var columns = listing.columns;
    var rowClass = 'audit-log-row';

    // What failed is found by looking rather than by reading down the rows, so it is marked
    // on the row itself and not left to a column that a narrow list would have dropped
    if (rowModel.outcome === listing.config.errorOutcome) {
        rowClass += ' ' + listing.config.errorRowClass;
    }

    var html = '<tr class="' + rowClass + '" data-item-id="' + rowModel.id + '">';

    // The event's own number, the one the address bar carries, so a row points at the same
    // event tomorrow as it does now - where it happens to stand in the list does not.
    html += '<td class="audit-log-cell-number">' + rowModel.id + '</td>';

    // Which day it was and the time of day, with the whole stamp one hover away
    html += '<td class="audit-log-cell-time" title="' + listing.escapeHTML(rowModel.timeLocal) + '">' +
        listing.timeCellHTML(rowModel) + '</td>';

    html += '<td class="audit-log-cell-role">' +
        kit.role.tag(rowModel.role, rowModel.eventLabel) + '</td>';

    // What the message is called by its protocol is read in the pane rather than on the row -
    // a control id is a number to be copied, not a number to be scanned down a list.
    // The source's sentence is the cell's tooltip.
    var sentence = listing.sentenceOf(rowModel);

    html += '<td class="audit-log-cell-main"';

    if (sentence !== '') {
        html += ' title="' + listing.escapeHTML(sentence) + '"';
    }

    html += '>';

    // Saying an event is a request next to a tag already reading REQ is saying it twice.
    // An event whose tag does not say what it was - a platform record or a log access
    // record, whose tag names the log and not the kind - says so itself, except a view
    // record, whose chips already name the viewer and the viewed thing, so its row says
    // nothing twice either. The words are read, not clicked - filtering by an event's
    // kind is the pane's affair.
    var saysNothingOfKind = rowModel.role === 'none' || rowModel.role === 'access';
    var saysItsKind = saysNothingOfKind && rowModel.eventType !== listing.config.viewEventType;

    // A source whose rows are known by what they name first, e.g. a schedule, wears its
    // event word as one more chip after the others, coloured by how the event turned out,
    // rather than as the word leading the row
    var presenter = $.fn.zato.audit_log.presenterFor(rowModel.raw.source);
    var chipsHTML = kit.chips.render(listing.rowChips(rowModel));

    if (presenter.eventWordAsChip === true) {
        html += chipsHTML;

        if (saysItsKind) {
            html += '<span class="audit-log-row-event-chip">' + kit.chips.render_one(listing.eventChip(rowModel)) + '</span>';
        }
    }
    else {
        if (saysItsKind) {
            html += '<span class="audit-log-row-event">' + listing.escapeHTML(rowModel.eventLabel) + '</span>';
        }

        html += chipsHTML;
    }

    // A message that went out again wears that as one more badge after the others
    if (rowModel.isResubmitted) {
        html += '<span class="audit-log-resubmitted-marker">' +
            listing.escapeHTML($.fn.zato.audit_log.config.resubmittedMarkerLabel) + '</span>';
    }

    html += '</td>';

    if (columns.action) {
        html += '<td class="audit-log-cell-action">' + listing.actionHTML(rowModel) + '</td>';
    }

    // Every column of a fixed table gives its width, and the room the row has over has to go
    // somewhere - it goes into this last empty cell, so no column that is being read is stretched
    // to swallow it and every one of them stands where it says it does.
    html += '<td class="audit-log-cell-filler"></td>';

    html += '</tr>';

    return html;
};

// /////////////////////////////////////////////////////////////////////////////

listing.emptyRowHTML = function() {
    var config = listing.config;

    var out = '<tr class="audit-log-empty-row"><td colspan="' + listing.columnCount() + '">' +
        config.emptyListing + '</td></tr>';

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

listing.loadingRowHTML = function() {
    var out = '<tr class="detail-loading-row"><td colspan="' + listing.columnCount() + '">' +
        kit.spinner_label_html() + '</td></tr>';

    return out;
};

})(jQuery);
