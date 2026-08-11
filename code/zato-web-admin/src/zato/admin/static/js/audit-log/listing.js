

// /////////////////////////////////////////////////////////////////////////////

// The audit log listing - a main list of events beside a pane holding the selected one whole.
// Everything about it that is not about audit events lives in the dashboard kit, and everything
// a particular source shows lives in its presenter.

$.fn.zato.audit_log.listing = {};

// /////////////////////////////////////////////////////////////////////////////

(function($) {

var kit = $.fn.zato.dashboard_kit;
var listing = $.fn.zato.audit_log.listing;

listing.config = {

    // Where on the page the listing and its chrome are built
    chromeHost: '#audit-log-chrome',
    host: '#audit-log-listing',
    itemsHost: '#audit-log-table-body',
    itemSelector: '.audit-log-row',
    legendHost: '#audit-log-legend',
    eventChipHost: '#audit-log-event-chip',
    payloadHost: '#audit-log-pane-payload',
    rangePillId: 'audit-log-range',

    // The pane's two halves - the message itself and everything said about it. The whole
    // flow the message belongs to is a page of its own, which the pane head links to.
    tabSelector: '.audit-log-pane-tab',
    tabPanelPrefix: 'audit-log-pane-panel-',
    tabStorageKey: 'zato_audit_log_pane_tab',
    dataTab: 'data',
    detailsTab: 'details',
    dataTabLabel: 'Data',
    detailsTabLabel: 'Details',

    // Where the event's whole flow is read, and what the doorway to it says
    flowPagePath: '/zato/message-flow/',
    openFlowLabel: 'Open flow',

    // What stands in for a message body that could not be read
    detailsErrorLabel: 'Could not load the message',

    // What the proportions of one source's listing are remembered under
    storagePrefix: 'zato_audit_log_layout_',
    refreshStorageKey: 'zato_audit_log_refresh',
    rangeStorageKey: 'zato_audit_log_range',

    // What the event being read and the tab it is being read in are called in the address
    // bar, so a link to the page is a link to that event in that tab
    eventURLKey: 'event',
    tabURLKey: 'tab',

    // What a deep link may additionally ask this page to do with the event it names,
    // and the one thing it may ask for - the resubmit confirmation on that event,
    // which is how an alert notification points at the message that failed
    actionURLKey: 'action',
    resubmitAction: 'resubmit',

    // What the resubmit confirmation says - nothing goes out again until
    // the confirm button inside is pressed
    resubmitConfirmTitle: 'Resubmit this message?',
    resubmitConfirmConnectionLabel: 'Connection',
    resubmitConfirmMessageLabel: 'Message',
    resubmitConfirmYesLabel: 'Yes, resubmit',
    resubmitConfirmCancelLabel: 'Cancel',
    resubmitAlreadyDoneText: 'This message has already been resubmitted.',
    resubmitAlreadyDoneCloseLabel: 'Close',

    // The confirmation floats over the pane, which has an elevated z-index of its own
    resubmitPopoverZIndex: 100001,

    // How wide the list starts out, which is wider than the kit's own default because
    // a row of it carries a chip of whatever source it is listing
    defaultListWidth: 700,

    // How many of an event's chips a row of the list carries. A presenter names the most
    // telling ones first, and the rest of what an event says about itself is read in the pane
    // rather than shouted across the list.
    rowChipLimit: 2,

    // The order a row gives its columns up in as the list is narrowed, from the one least missed
    // to the one it holds on to longest. Each name is the class the list carries while that
    // column is being left out, and the event's own number is not on the list at all - it is
    // what a row is pointed at by, so it is never given up.
    dropOrder: ['action', 'chips', 'time', 'role'],
    dropClassPrefix: 'audit-log-drop-',

    emptyListing: 'No events found',
    emptyPane: 'No event selected',

    // What the pane says when there is nothing to select at all
    emptyPaneNoEvents: 'No events found',

    // What stands between the day a row belongs to and the time of day
    dayTimeSeparator: ' \u00b7 ',

    // The one outcome a row is marked for on sight, being the one a reader came to the list for,
    // the class it is marked with, and the rail beside the list its mark stands in
    errorOutcome: 'error',
    errorRowClass: 'audit-log-row-error',
    railClass: 'audit-log-error-rail',
    railMarkClass: 'audit-log-error-rail-dot',

    rawTabLabel: 'Raw',
    parsedTabLabel: 'Parsed',

    // The two ways a body is read wherever one is read, parsed being the one every reader
    // starts on, and the name the way chosen goes into the address bar under
    rawView: 'raw',
    parsedView: 'parsed',
    viewURLKey: 'view',

    // What is known about the event is set out on the same dark frame the message and the flow
    // are read on, so moving between the pane's tabs is not moving between two kinds of page
    paneFactVariant: 'dark',

    // Where the files the event carried are offered, below everything said about it
    attachmentsHostClass: 'audit-log-pane-attachments',

    // What the pane calls the event it is holding, before anything else it says about it
    eventLabel: 'Event',

    cidLabel: 'CID',
    durationLabel: 'Duration',
    sizeLabel: 'Size',

    lineageParentLabel: 'Repeat of',
    lineageChildLabel: 'Repeated as',

    // What each kind of message body a source stores is called
    bodyKindLabels: {
        'request': 'Request',
        'response': 'Response',
        'error': 'Error'
    },

    // The tint the newest rows carry, how far down the list it reaches being the kit's own
    recencyRGB: '218, 165, 32',

    // How often the listing asks for what has arrived since, until it is told otherwise
    refreshDefaultSeconds: 5,

    // The columns the list draws places of its own for, so the neutral presenter knows
    // which of a source's columns are left to become chips
    coreColumnKeys: {
        'event_time_iso': true,
        'cid': true,
        'msg_id': true,
        'event_type': true,
        'outcome': true,
        'size': true,
        'data': true,
        'action': true
    },

    // The columns of a source the pane's grid draws out of the row model itself rather than
    // out of the source's own list, plus the two that are no attribute of an event at all
    nonAttrColumnKeys: {
        'data': true,
        'action': true,
        'event_time_iso': true,
        'cid': true,
        'size': true
    },

    // The columns the pane shows but offers no Search by - the outcome has a filter of its own
    nonSearchColumnKeys: {
        'outcome': true
    },

    // What the pane says about every event whatever source it came from, each one left out when
    // the source already declares a column of its own for it. `searchable` says whether Search is
    // offered beside it. When the event happened is not here - a moment in time reads last of
    // everything, so the pane adds it at the very end itself.
    paneFields: [
        {label: 'Correlation id', key: 'correlId', columnKey: 'correl_id', searchable: true},
        {label: 'Status', key: 'status', columnKey: 'status', searchable: true},
        {label: 'Classification', key: 'classification', columnKey: 'classification', searchable: true},
        {label: 'Endpoint', key: 'endpoint', columnKey: 'endpoint', searchable: true}
    ],

    // What the moment the event happened at is called, on the pane's own last line
    timeLabel: 'Time',

    // What a scheduled job's run number is called on a page whose own columns do not name it
    runLabel: 'Run',

    // The log access view record - the one event whose row says nothing about its kind,
    // because its chips already name the viewer and the viewed thing
    viewEventType: 'content-viewed',

    // The sign a value leading off this page wears - the box with the arrow leaving it,
    // drawn in the link's own ink
    externalIconHTML: '<svg class="audit-log-external-icon" viewBox="0 0 24 24" fill="none"' +
        ' stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"' +
        ' aria-hidden="true"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1' +
        ' 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>',

    // How far back the range pill reaches, in the order it offers the choice,
    // with the whole page last because it is where the page starts out
    rangeOptions: [
        {minutes: 5, label: 'Last 5 minutes'},
        {minutes: 60, label: 'Last 1 hour'},
        {minutes: 360, label: 'Last 6 hours'},
        {minutes: 1440, label: 'Today'},
        {minutes: 10080, label: 'This week'},
        {minutes: 0, label: 'All'}
    ]
};

// /////////////////////////////////////////////////////////////////////////////

// The role one event plays in its exchange - a request is the request whichever way
// it travelled, so a pair reads the same on a channel and on an outgoing connection.
// The audit event types are shared across sources, so this reads the same everywhere.
listing.roles = {
    'received': 'request',
    'request-received': 'request',
    'request-sent': 'request',
    'message-received': 'request',
    'message-sent': 'request',
    'interchange-received': 'request',
    'interchange-sent': 'request',
    'published': 'request',
    'delivered': 'request',
    'delivery-failed': 'request',
    'response-received': 'response',
    'response-sent': 'response',
    'ack-received': 'response',
    'ack-sent': 'response',
    'mdn-received': 'response',
    'mdn-sent': 'response',
    'receipt-received': 'response',
    'receipt-sent': 'response',
    'job-executed': 'job',

    // The log access records - config changes and someone reading a message body -
    // read by the log they belong to rather than by a part they play in no exchange
    'config-created': 'access',
    'config-edited': 'access',
    'config-deleted': 'access',
    'content-viewed': 'access'
};

// /////////////////////////////////////////////////////////////////////////////

// One page of events as the listing reads them, and what the chrome has narrowed them down to
listing.rowModels = [];
listing.visible = [];
listing.hidden = {};
listing.minutes = 0;

// The kind of event the list is narrowed down to, empty while no event word has been
// clicked, and the outcomes the legend now offers, so a clicked badge can redraw it
listing.eventFilter = '';
listing.currentOutcomes = [];

// Which cells the events now on the page have anything to say in, so a list of events
// that report no outcome of their own is not given a column of blanks
listing.columns = {outcome: false, action: false};

// The events already on the page before the last refresh, so only what is new puffs
listing.seenIds = {};

// Whether the page now being drawn arrived by itself rather than because the reader
// asked for it, which is the only time anything puffs
listing.isLive = false;

// The two panes, once they are built, the tab group of the detail pane, once it holds
// an event, and the event it is holding
listing.panes = null;
listing.tabs = null;
listing.selected = null;

// The event id a deep link asked to open the resubmit confirmation on, honoured once
// the page holding that event is on screen and then never again
listing.pendingAction = null;

// /////////////////////////////////////////////////////////////////////////////

listing.escapeHTML = function(value) {
    return $.fn.zato.audit_log.escapeHTML(value);
};

// /////////////////////////////////////////////////////////////////////////////

listing.roleOf = function(eventType) {
    var role = listing.roles[eventType];

    // An event type that is neither a request nor a reply, e.g. a message expiring.
    if (role === undefined) {
        role = 'none';
    }

    return role;
};

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
        role: listing.roleOf(row.event_type)
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
    var out = rowModel.chips.slice(0, listing.config.rowChipLimit);
    return out;
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
    html += '<td class="audit-log-cell-main">';

    // Saying an event is a request next to a tag already reading REQ is saying it twice.
    // An event whose tag does not say what it was - a platform record or a log access
    // record, whose tag names the log and not the kind - says so itself, except a view
    // record, whose chips already name the viewer and the viewed thing, so its row says
    // nothing twice either. The words are read, not clicked - filtering by an event's
    // kind is the pane's affair.
    var saysNothingOfKind = rowModel.role === 'none' || rowModel.role === 'access';

    if (saysNothingOfKind && rowModel.eventType !== listing.config.viewEventType) {
        html += '<span class="audit-log-row-event">' + listing.escapeHTML(rowModel.eventLabel) + '</span>';
    }

    html += kit.chips.render(listing.rowChips(rowModel));

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

// /////////////////////////////////////////////////////////////////////////////

// The cells of the pane's grid - what this source says about its events, then what every
// source says about all of them. An attribute this event has no value for is left out
// altogether, because a label above a dash says less than nothing. Each one also carries what
// the list is asked for by its Search, which is empty for what an event was measured with -
// nothing is found by having taken the same number of milliseconds.
listing.paneAttrs = function(rowModel) {
    var config = listing.config;
    var columns = $.fn.zato.audit_log.config.columns;
    var seen = {};
    var out = [];

    for (var columnIndex = 0; columnIndex < columns.length; columnIndex++) {
        var column = columns[columnIndex];

        if (config.nonAttrColumnKeys[column.key]) {
            continue;
        }

        seen[column.key] = true;

        var columnValue = rowModel.raw[column.key];

        if (columnValue !== '') {
            var columnSearch = columnValue;

            if (config.nonSearchColumnKeys[column.key]) {
                columnSearch = '';
            }

            out.push({key: column.key, label: column.label, value: columnValue, search: columnSearch});
        }
    }

    // A scheduler row carries its run number even on a page whose columns do not name it -
    // the all-sources listing - so the pane says it here, after the page's own columns
    if (!seen['current_run']) {
        var currentRun = rowModel.raw.current_run;

        if (currentRun !== undefined) {
            if (currentRun !== '') {
                out.push({key: 'current_run', label: config.runLabel, value: currentRun, search: currentRun});
            }
        }
    }

    for (var fieldIndex = 0; fieldIndex < config.paneFields.length; fieldIndex++) {
        var field = config.paneFields[fieldIndex];

        // A source naming one of these its own way, e.g. an endpoint it calls a folder,
        // has already had its say above.
        if (seen[field.columnKey]) {
            continue;
        }

        var fieldValue = rowModel[field.key];

        if (fieldValue !== '') {
            var fieldSearch = '';

            if (field.searchable) {
                fieldSearch = fieldValue;
            }

            out.push({key: field.columnKey, label: field.label, value: fieldValue, search: fieldSearch});
        }
    }

    // An event that took no measurable time is one nothing was timed for, e.g. a message
    // being written down rather than being answered.
    if (rowModel.durationMs > 0) {
        out.push({key: 'duration', label: config.durationLabel,
            value: kit.format_duration_ms(rowModel.durationMs), search: ''});
    }

    if (rowModel.size > 0) {
        out.push({key: 'size', label: config.sizeLabel,
            value: kit.format_number_full(rowModel.size), search: ''});
    }

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// One thing said about the event, in the shape the kit's fact rows read
// One fact of the pane - `searchValue` is what its Search asks the list for, empty when no
// Search is to be offered
listing.paneFact = function(label, valueHTML, copyValue, searchValue) {
    var out = {label: label, value_html: valueHTML, copy_value: copyValue, search_value: searchValue};
    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// What this event came out of and what came out of it, each one selecting its own event
listing.lineageFacts = function(rowModel) {
    var config = listing.config;
    var out = [];

    for (var parentIndex = 0; parentIndex < rowModel.parents.length; parentIndex++) {
        out.push(listing.lineageFact(config.lineageParentLabel, rowModel.parents[parentIndex].id));
    }

    for (var childIndex = 0; childIndex < rowModel.children.length; childIndex++) {
        out.push(listing.lineageFact(config.lineageChildLabel, rowModel.children[childIndex].id));
    }

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// An event's own id is a number in the database and a piece of text everywhere on the screen,
// which is where it turns into one
listing.lineageFact = function(label, eventId) {
    var idText = String(eventId);

    var value = '<a href="javascript:void(0)" class="audit-log-lineage" data-lineage-id="' +
        idText + '">' + listing.config.eventLabel + ' ' + idText + '</a>';

    // The event named here is opened by clicking it, rather than searched for
    var out = listing.paneFact(label, value, idText, '');

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// The two ways of reading one event's payload - as it went over the wire, which is where the
// reading of it starts whatever source wrote it down, and as that source's own reader makes
// sense of it. Every event of every source is read through these same two tabs, so moving down
// the list swaps the text inside the frame rather than taking the frame down and putting it up.
listing.detailTabs = function() {
    var config = listing.config;

    // Parsed reads first, being what a message is opened to be read as - the wire form is
    // there for whoever asks for it
    var out = [
        {label: config.parsedTabLabel, kind: '', parsed: true},
        {label: config.rawTabLabel, kind: '', parsed: false}
    ];

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// One event's payload, whole or only the top of it - a pane showing a message asks for all
// of it, and a line of a flow opened for a look asks for as much of it as it will show
listing.fetchDetails = function(eventId, kind, isPreview, onDone) {
    var config = $.fn.zato.audit_log.config;

    $.ajax({
        url: config.detailsURL,
        type: 'POST',
        data: JSON.stringify({id: eventId, kind: kind, preview: isPreview}),
        contentType: 'application/json',
        headers: {'X-CSRFToken': $.cookie('csrftoken')},
        success: function(data) {
            if (typeof data === 'string') {
                data = JSON.parse(data);
            }
            onDone(data);
        },

        // A failed read says so where the body would have stood - without this,
        // whatever pane asked keeps its spinner up forever
        error: function(jqXHR) {
            onDone({
                data: listing.config.detailsErrorLabel + ' - HTTP ' + jqXHR.status,
                parsed: '',
                total_len: 0
            });
        }
    });
};

// /////////////////////////////////////////////////////////////////////////////

// One tab of the pane, drawn the way every tab on the dashboard is drawn
listing.paneTabHTML = function(name, label) {
    var out = '<button type="button" class="dashboard-tab audit-log-pane-tab" role="tab" data-tab="' +
        name + '">' + label + '</button>';

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// What the pane says about the event it is holding, above its two tabs
listing.paneHeadHTML = function(rowModel) {
    var config = listing.config;

    // Which event is being read comes first, because it is what the address bar carries
    // and what a row is picked out of the list by
    var html = '<span class="audit-log-pane-event">' + config.eventLabel + ' ' + rowModel.id + '</span>';

    html += kit.role.tag(rowModel.role, rowModel.eventLabel);
    html += '<span class="audit-log-pane-title">' + listing.escapeHTML(rowModel.headline) + '</span>';
    html += listing.outcomeBadgeHTML(rowModel);

    // An event with nothing to act on gets no actions holder either - an empty one would
    // still claim a flex gap of its own and hold the badge away from the head's right edge
    var actionHTML = listing.actionHTML(rowModel);

    if (actionHTML) {
        html += '<span class="audit-log-pane-actions">' + actionHTML + '</span>';
    }

    return html;
};

// /////////////////////////////////////////////////////////////////////////////

// A value that leads to a page, drawn the way every other way out of the pane is drawn -
// wearing the sign that it leads off this page, in its own ink
listing.linkHTML = function(url, text) {
    var out = '<a href="' + listing.escapeHTML(url) + '" class="audit-log-object-link">' +
        listing.escapeHTML(text) + listing.config.externalIconHTML + '</a>';

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// One object's name as the pane shows it - a link to the object's own page for a source
// that has one, and the name as it stands for a source that does not
listing.objectValueHTML = function(rowModel, name) {
    var linkTemplate = $.fn.zato.audit_log.config.objectLinks[rowModel.raw.source];

    if (linkTemplate === undefined) {
        return listing.escapeHTML(name);
    }

    var url = linkTemplate.replace('{name}', encodeURIComponent(name));

    return listing.linkHTML(url, name);
};

// /////////////////////////////////////////////////////////////////////////////

// One attribute's value as the pane draws it - the source by its human name and as a way
// to its own main page, the object as a way to its page, the event by what it reads as,
// an endpoint as a way to the service it names or with its method in the method's own
// ink, and everything else as the text it is
listing.paneAttrValueHTML = function(rowModel, attr) {
    var config = $.fn.zato.audit_log.config;

    if (attr.key === 'source') {
        var sourceLabel = $.fn.zato.audit_log.sourceLabel(attr.value);
        var sourceLink = config.sourceLinks[attr.value];

        if (sourceLink === undefined) {
            return listing.escapeHTML(sourceLabel);
        }

        return listing.linkHTML(sourceLink, sourceLabel);
    }

    if (attr.key === 'object_name') {
        return listing.objectValueHTML(rowModel, attr.value);
    }

    // The event word filters the log down to events of its kind, and the outcome drives
    // the legend the same way clicking its badge up there does
    if (attr.key === 'event_type') {
        var eventWord = $.fn.zato.audit_log.eventLabel(attr.value);

        return '<a href="javascript:void(0)" class="audit-log-event-filter" data-event-type="' +
            listing.escapeHTML(attr.value) + '">' + listing.escapeHTML(eventWord) + '</a>';
    }

    if (attr.key === 'outcome') {
        return '<a href="javascript:void(0)" class="audit-log-outcome-filter" data-outcome="' +
            listing.escapeHTML(attr.value) + '">' + listing.escapeHTML(attr.value) + '</a>';
    }

    if (attr.key === 'endpoint') {
        var endpointTemplate = config.endpointLinks[rowModel.raw.source];

        if (endpointTemplate === undefined) {
            return kit.http_method.html(attr.value);
        }

        var url = endpointTemplate.replace('{name}', encodeURIComponent(attr.value));

        return listing.linkHTML(url, attr.value);
    }

    // A run of a scheduled job leads to its own page on the scheduler dashboard,
    // keyed by the job's id and the run's number, both carried by the event itself
    if (attr.key === 'current_run') {
        var runTemplate = config.runLinks[rowModel.raw.source];

        if (runTemplate === undefined) {
            return listing.escapeHTML(attr.value);
        }

        var runURL = runTemplate.replace('{job_id}', encodeURIComponent(rowModel.raw.job_id))
            .replace('{run}', encodeURIComponent(attr.value));

        return listing.linkHTML(runURL, attr.value);
    }

    return listing.escapeHTML(attr.value);
};

// /////////////////////////////////////////////////////////////////////////////

// One attribute's name as the pane draws it - the object and the endpoint are labelled
// by the word their own source has for them, a channel by Channel, a service by Service,
// a mailbox folder by Folder, so no row is headed by a word that names nothing
listing.paneAttrLabel = function(rowModel, attr) {
    var config = $.fn.zato.audit_log.config;

    if (attr.key === 'object_name') {
        var label = config.objectLabels[rowModel.raw.source];

        if (label === undefined) {
            label = config.defaultObjectLabel;
        }

        return label;
    }

    if (attr.key === 'endpoint') {
        var endpointLabel = config.endpointLabels[rowModel.raw.source];

        if (endpointLabel !== undefined) {
            return endpointLabel;
        }
    }

    return attr.label;
};

// /////////////////////////////////////////////////////////////////////////////

// Everything said about the event, which is what the Details tab holds - one thing to a
// line, read from the top down, rather than several of them side by side to be picked out
listing.paneDetailsHTML = function(rowModel) {
    var config = listing.config;
    var attrs = listing.paneAttrs(rowModel);
    var facts = [];

    // The CID leads, because it is what the whole message is opened by
    var cidValue = '<a href="#" class="audit-log-cid-link" data-id="' + rowModel.id + '" data-cid="' +
        listing.escapeHTML(rowModel.cid) + '">' + listing.escapeHTML(rowModel.cid) + '</a>';

    facts.push(listing.paneFact(config.cidLabel, cidValue, rowModel.cid, ''));

    for (var attrIndex = 0; attrIndex < attrs.length; attrIndex++) {
        var attr = attrs[attrIndex];

        facts.push(listing.paneFact(listing.paneAttrLabel(rowModel, attr),
            listing.paneAttrValueHTML(rowModel, attr), attr.value, attr.search));
    }

    facts = facts.concat(listing.lineageFacts(rowModel));

    // When the event happened reads last of everything - a moment in time is shared by
    // nothing, so no Search stands beside it either. The stamp itself is the scrubber
    // with every unit on it, the year and the month included.
    facts.push(listing.paneFact(config.timeLabel, kit.time_scrub.stamp(rowModel.timeIso),
        rowModel.timeLocal, ''));

    var html = kit.fact_rows.render(facts, config.paneFactVariant);

    // The files the event carried, filled in once their metadata has arrived and only
    // when there are any at all
    html += '<div class="' + config.attachmentsHostClass + '" data-attachments-id="' +
        rowModel.id + '"></div>';

    return html;
};

// /////////////////////////////////////////////////////////////////////////////

// The files the event carried are asked about when the event is opened - an event
// carrying none keeps the strip's place empty
listing.loadAttachments = function(rowModel, $host) {
    var config = $.fn.zato.audit_log.config;

    kit.attachments.load($host, {
        list_url: config.attachmentsURL,
        download_url: config.attachmentDownloadURL,
        id: rowModel.id,
        variant: listing.config.paneFactVariant
    });
};

// /////////////////////////////////////////////////////////////////////////////

listing.paneHTML = function(rowModel) {
    var config = listing.config;

    var html = '<div class="audit-log-pane-head">' + listing.paneHeadHTML(rowModel) + '</div>';

    // The message itself and everything said about it are two ways of reading one event,
    // so the pane is one of them at a time rather than both at once. The flow the event
    // belongs to is a page of its own, and its doorway stands to the right of the tabs -
    // beside the strip, not inside it, being a way out rather than a way to turn the page.
    html += '<div class="audit-log-pane-tabs-row">';
    html += '<div class="dashboard-tabs audit-log-pane-tabs" role="tablist">';
    html += listing.paneTabHTML(config.dataTab, config.dataTabLabel);
    html += listing.paneTabHTML(config.detailsTab, config.detailsTabLabel);
    html += '</div>';
    html += '<a class="audit-log-open-flow" href="' + config.flowPagePath + '?term=' + rowModel.id +
        '">' + config.openFlowLabel + '</a>';
    html += '</div>';

    // Only the panels scroll - the head and the tabs stand outside the scrolling body, so
    // the scrollbar the panels bring never pushes the head's right edge away from the page's
    html += '<div class="audit-log-pane-body">';

    html += '<div class="dashboard-tab-panel" role="tabpanel" id="' +
        config.tabPanelPrefix + config.dataTab + '">';
    html += '<div id="' + config.payloadHost.slice(1) + '"></div>';
    html += '</div>';

    html += '<div class="dashboard-tab-panel" role="tabpanel" id="' +
        config.tabPanelPrefix + config.detailsTab + '">';
    html += '<div class="audit-log-pane-details">' + listing.paneDetailsHTML(rowModel) + '</div>';
    html += '</div>';

    html += '</div>';

    return html;
};

// /////////////////////////////////////////////////////////////////////////////

// The pane brought from one event to the next where it stands - the frame, the tabs and
// whichever of them is open all stay as they are, and only what they hold is replaced.
// The message and the flow are left alone here, each of them deciding for itself whether
// the event it is holding is still the one being read.
listing.paneUpdate = function(rowModel, $pane) {
    $pane.find('.audit-log-pane-head').html(listing.paneHeadHTML(rowModel));
    $pane.find('.audit-log-pane-details').html(listing.paneDetailsHTML(rowModel));
};

// /////////////////////////////////////////////////////////////////////////////

// Each tab of the payload asks for its own body the first time it is opened, and the
// payload itself is only asked for once the tab holding it is the one being looked at.
listing.showPayload = function() {
    var $host = $(listing.config.payloadHost);
    var rowModel = listing.selected;

    // The panel already holding this event is the panel it was given - a refresh that leaves
    // the same event selected leaves the message being read on the screen as it is.
    if ($host.data('payload_event_id') === rowModel.id) {
        return;
    }

    $host.data('payload_event_id', rowModel.id);

    var tabs = listing.detailTabs();

    // The tab standing open is the one the address bar names, so a copied link opens on the
    // very reading its sender had in front of them
    var openIndex = 0;

    if (kit.url_state.get(listing.config.viewURLKey) === listing.config.rawView) {
        openIndex = 1;
    }

    kit.payload_panel.swap($host, tabs, function(tab, onDone) {
        listing.fetchDetails(rowModel.id, tab.kind, false, function(details) {

            if (!tab.parsed) {
                onDone(details.data);
                return;
            }

            // A payload this source's own reader could make nothing of - a JSON alert in
            // an HL7 log, say - is shown as it stands rather than as a blank pane.
            if (details.parsed === '') {
                onDone(details.data);
            }
            else {
                onDone(details.parsed);
            }
        });
    }, openIndex);
};

// /////////////////////////////////////////////////////////////////////////////

// Whichever of the two ways of reading an event is open asks for what it shows, and the
// one that is not open asks for nothing until its turn comes
listing.showTab = function(tab) {
    var config = listing.config;

    if (tab === config.dataTab) {
        listing.showPayload();
    }
};

// /////////////////////////////////////////////////////////////////////////////

listing.onSelect = function(rowModel, $pane) {
    var config = listing.config;

    listing.selected = rowModel;

    // The files the event carried are asked about the moment the pane holds it
    listing.loadAttachments(rowModel, $pane.find('.' + config.attachmentsHostClass));

    // The tab group is bound to the pane the first time the pane holds one, and every
    // pane after that is put into whichever tab is already open.
    if (listing.tabs === null) {
        listing.tabs = kit.tabs.init({
            tab_selector: config.tabSelector,
            panel_prefix: config.tabPanelPrefix,
            storage_key: config.tabStorageKey,
            default_tab: config.dataTab,
            on_change: function(tab) {
                kit.url_state.replace({tab: tab});
                listing.showTab(tab);
            }
        });

        // A link naming a tab opens in that tab, whatever this screen was last left in.
        var urlTab = listing.urlTab();

        if (urlTab !== '') {
            listing.tabs.set_tab(urlTab, true);
        }
    }
    else {
        listing.tabs.set_tab(listing.tabs.get_tab(), true);
    }

    // A link to this page is a link to the event being read on it, in the tab it is
    // being read in.
    kit.url_state.replace({event: rowModel.id, tab: listing.tabs.get_tab()});

    listing.showTab(listing.tabs.get_tab());
};

// /////////////////////////////////////////////////////////////////////////////

// The tab a link to this page asked for, and nothing when it asked for none
listing.urlTab = function() {
    var config = listing.config;
    var wanted = kit.url_state.get(config.tabURLKey);

    // Only the two the pane actually has are honoured, so a hand-typed address cannot
    // leave the pane with no tab open at all.
    if (wanted === config.dataTab) {
        return wanted;
    }

    if (wanted === config.detailsTab) {
        return wanted;
    }

    return '';
};

// /////////////////////////////////////////////////////////////////////////////

// The newest rows carry a fading tint, and a row that arrived on a live refresh puffs once.
// A page the reader asked for - a search, a page turned, a filter - puffs nothing, because
// everything on it is new and a whole list blinking says nothing about any of it.
listing.markNewRows = function() {
    var $itemsHost = listing.panes.items_host();
    var seenIds = {};

    for (var rowIndex = 0; rowIndex < listing.visible.length; rowIndex++) {
        var rowModel = listing.visible[rowIndex];
        seenIds[rowModel.id] = true;

        if (listing.isLive && !listing.seenIds[rowModel.id]) {
            $itemsHost.find('[data-item-id="' + rowModel.id + '"]').addClass('kit-puff');
        }
    }

    listing.seenIds = seenIds;

    // The list is drawn newest first, so the tint goes by where a row stands. It is laid on
    // without animating unless the page came in by itself - the rows are drawn afresh every
    // time, and fading each of them in would blink the whole list at every draw.
    kit.recency.apply_by_position({
        container: listing.config.itemsHost,
        item_selector: listing.config.itemSelector,
        rgb: listing.config.recencyRGB,
        animate: listing.isLive
    });
};

// /////////////////////////////////////////////////////////////////////////////

// A row keeps every column it has room for and gives up the next one at the moment it has not.
// Which moment that is, is measured rather than guessed - the columns are as wide as the data
// makes them, and a width written down here could only ever be a guess at what that comes to.
listing.fitColumns = function() {
    var config = listing.config;
    var $host = $(config.host);
    var listElement = listing.panes.items_host().closest('table').parent()[0];

    // Everything is put back before the row is measured, so a pane being widened takes its
    // columns back in the reverse of the order it gave them up
    for (var index = 0; index < config.dropOrder.length; index++) {
        $host.removeClass(config.dropClassPrefix + config.dropOrder[index]);
    }

    for (var dropIndex = 0; dropIndex < config.dropOrder.length; dropIndex++) {

        // Reading the width is what settles the layout, so the row that is measured next is the
        // row as it stands with the column just given up already gone
        if (listElement.scrollWidth <= listElement.clientWidth) {
            break;
        }

        $host.addClass(config.dropClassPrefix + config.dropOrder[dropIndex]);
    }
};

// A list scrolls, and a scrolling box shows nothing painted outside it, so a mark that is to stand
// outside the rows cannot be part of one. The marks for the failed rows are drawn in a rail of their
// own beside the list, in the room the page already leaves at its edge, and each is held level with
// the row it belongs to. Nothing is added to the table, so no row moves and no column changes.
listing.rail = {};

listing.rail.parts = function() {
    var config = listing.config;
    var $list = listing.panes.items_host().closest('table').parent();

    // The rail stands next to the list rather than inside it, so it is a child of the pair
    var $pair = $list.parent();
    var $rail = $pair.children('.' + config.railClass);

    if ($rail.length === 0) {
        $rail = $('<div class="' + config.railClass + '"></div>');
        $pair.append($rail);
    }

    return {list: $list[0], pair: $pair[0], $rail: $rail};
};

// /////////////////////////////////////////////////////////////////////////////

listing.rail.sync = function() {
    var config = listing.config;
    var parts = listing.rail.parts();
    var listRect = parts.list.getBoundingClientRect();
    var pairRect = parts.pair.getBoundingClientRect();

    // The rail stands level with the list and no taller than it, which is what cuts a mark off as
    // the row it belongs to is scrolled out of sight rather than leaving it above the list
    parts.$rail.css({
        top: (listRect.top - pairRect.top) + 'px',
        height: listRect.height + 'px'
    });

    var rows = listing.panes.items_host().find('.' + config.errorRowClass);
    var marks = parts.$rail.children();

    // One mark per failed row. They are drawn again only when their number changes - a scroll
    // moves the ones already there rather than making them afresh.
    if (marks.length !== rows.length) {
        var html = '';

        for (var rowIndex = 0; rowIndex < rows.length; rowIndex++) {
            html += '<div class="' + config.railMarkClass + '"></div>';
        }

        parts.$rail.html(html);
        marks = parts.$rail.children();
    }

    for (var markIndex = 0; markIndex < rows.length; markIndex++) {
        var rowRect = rows[markIndex].getBoundingClientRect();

        // Where the middle of the row falls inside the list, the mark being centred on that point
        marks[markIndex].style.top = (rowRect.top + rowRect.height / 2 - listRect.top) + 'px';
    }
};

// /////////////////////////////////////////////////////////////////////////////

// A scroll asks for the marks to be moved far oftener than they can be drawn, so what it asks for
// is one move on the next frame and nothing more until that frame has been drawn.
listing.rail.pending = false;

listing.rail.schedule = function() {
    if (listing.rail.pending) {
        return;
    }

    listing.rail.pending = true;

    window.requestAnimationFrame(function() {
        listing.rail.pending = false;
        listing.rail.sync();
    });
};

// /////////////////////////////////////////////////////////////////////////////

listing.draw = function() {

    // Every row of the page is drawn - what the legend switches off never reaches
    // the page at all, the poll filters it out in the database
    listing.visible = listing.rowModels;

    // Which cells a row holds is settled before a single one of them is drawn.
    listing.updateColumns();

    listing.panes.set_items(listing.visible);
    listing.markNewRows();

    // What the rows just drawn are holding is what settles how much room the row needs, so which
    // columns fit is worked out after they are on the page rather than before
    listing.fitColumns();

    // Where the failed rows now stand is where their marks stand beside them
    listing.rail.sync();
};

// /////////////////////////////////////////////////////////////////////////////

listing.renderPage = function(_$body, rows) {
    listing.rowModels = listing.buildRows(rows);
    listing.draw();

    // Whatever brought the next page, it will have to say for itself that it came by
    // the clock rather than by the reader.
    listing.isLive = false;

    // A deep link may have asked for the resubmit confirmation on one of these rows
    listing.runPendingAction();
};

// /////////////////////////////////////////////////////////////////////////////

// The confirmation a resubmit deep link opens - an alert notification points here
listing.openResubmitConfirm = function(rowModel, $row) {
    var config = listing.config;

    // The row's own action link is the anchor - a narrow list may have dropped the
    // action cell, in which case the pane head carries the same link, the pane
    // already holding this event by now
    var $link = $row.find('.audit-log-resubmit-link');

    if ($link.length === 0) {
        $link = $(config.host).find('.audit-log-pane-actions .audit-log-resubmit-link');
    }

    // An event its source never declared resubmittable has no link and no confirmation -
    // a hand-edited address cannot resubmit what the page itself does not offer to
    if ($link.length === 0) {
        return;
    }

    var linkElement = $link[0];

    var content = document.createElement('div');
    content.className = 'audit-log-resubmit-confirm';

    var title = document.createElement('div');
    title.className = 'audit-log-resubmit-confirm-title';
    title.textContent = config.resubmitConfirmTitle;
    content.appendChild(title);

    var buttons = document.createElement('div');
    buttons.className = 'audit-log-resubmit-confirm-buttons';

    var instance = tippy(linkElement, {
        content: content,
        placement: 'left',
        trigger: 'manual',
        arrow: true,
        animation: 'fade',
        duration: [50, 50],
        hideOnClick: false,
        interactive: true,
        appendTo: document.body,
        zIndex: config.resubmitPopoverZIndex,

        // The instance is one-shot - once its hide animation finishes, it goes away
        onHidden: function(hiddenInstance) {
            hiddenInstance.destroy();
        }
    });

    var close = function() {
        instance.hide();
    };

    if (rowModel.isResubmitted) {
        var doneText = document.createElement('div');
        doneText.className = 'audit-log-resubmit-confirm-text';
        doneText.textContent = config.resubmitAlreadyDoneText;
        content.appendChild(doneText);

        var closeButton = document.createElement('button');
        closeButton.type = 'button';
        closeButton.className = 'audit-log-resubmit-confirm-cancel';
        closeButton.textContent = config.resubmitAlreadyDoneCloseLabel;
        closeButton.addEventListener('click', close);

        buttons.appendChild(closeButton);
        content.appendChild(buttons);

        instance.show();
        return;
    }

    // Which connection the message goes through again and what it is known by,
    // named in full before anything is sent
    var addFact = function(label, value) {
        var line = document.createElement('div');
        line.className = 'audit-log-resubmit-confirm-text';

        var labelPart = document.createElement('span');
        labelPart.className = 'audit-log-resubmit-confirm-label';
        labelPart.textContent = label;

        var valuePart = document.createElement('span');
        valuePart.textContent = value;

        line.appendChild(labelPart);
        line.appendChild(valuePart);
        content.appendChild(line);
    };

    addFact(config.resubmitConfirmConnectionLabel, rowModel.raw.object_name);
    addFact(config.resubmitConfirmMessageLabel, rowModel.identity);

    var cancelButton = document.createElement('button');
    cancelButton.type = 'button';
    cancelButton.className = 'audit-log-resubmit-confirm-cancel';
    cancelButton.textContent = config.resubmitConfirmCancelLabel;
    cancelButton.addEventListener('click', close);

    var yesButton = document.createElement('button');
    yesButton.type = 'button';
    yesButton.className = 'audit-log-resubmit-confirm-yes';
    yesButton.textContent = config.resubmitConfirmYesLabel;

    // Only confirming runs the POST - the same one the row's own link runs,
    // through the same per-source service registration
    yesButton.addEventListener('click', function() {
        close();
        $.fn.zato.audit_log.resubmit(linkElement);
    });

    buttons.appendChild(cancelButton);
    buttons.appendChild(yesButton);
    content.appendChild(buttons);

    instance.show();
};

// /////////////////////////////////////////////////////////////////////////////

// The action a deep link asked for, run once the page holding its event has arrived -
// the row is brought into view and marked, and the confirmation opens anchored on it
listing.runPendingAction = function() {
    if (listing.pendingAction === null) {
        return;
    }

    var rowModel = listing.modelById(listing.pendingAction);

    // The event may sit on a later page or outside the current window -
    // the action keeps waiting for a page that holds it
    if (rowModel === null) {
        return;
    }

    listing.pendingAction = null;

    // A refresh of the page is not asked to open the confirmation all over again
    kit.url_state.replace({action: ''});

    var $row = listing.panes.items_host().find('[data-item-id="' + rowModel.id + '"]');

    $row[0].scrollIntoView({block: 'center'});
    $row.addClass('kit-puff');

    listing.openResubmitConfirm(rowModel, $row);
};

// /////////////////////////////////////////////////////////////////////////////

// The live pill, the range pill and the legend that narrows the list down to one outcome
listing.chromeHTML = function() {
    var config = listing.config;
    var rangePillId = config.rangePillId;

    var html = '<div class="detail-header-controls">';

    html += '<span class="dashboard-time-range-wrapper">';
    html += '<span class="dashboard-pill dashboard-pill-clickable dashboard-refresh-badge" ' +
        'id="audit-log-refresh-pill">Paused</span>';
    html += '<div class="dashboard-time-range-menu" id="audit-log-refresh-menu"></div>';
    html += '</span>';

    html += '<span class="dashboard-time-range-wrapper">';
    html += '<span class="dashboard-pill dashboard-pill-clickable" id="' + rangePillId + '-pill"></span>';
    html += '<div class="dashboard-time-range-menu" id="' + rangePillId + '-menu">';

    for (var optionIndex = 0; optionIndex < config.rangeOptions.length; optionIndex++) {
        var option = config.rangeOptions[optionIndex];

        html += '<div class="dashboard-time-range-option" data-minutes="' + option.minutes + '">' +
            option.label + '</div>';
    }

    html += '</div>';
    html += '</span>';

    // A source whose events report no outcome at all is offered no legend either.
    if ($.fn.zato.audit_log.config.outcomes.length) {
        html += '<div class="dashboard-chart-legend" id="' + config.legendHost.slice(1) + '"></div>';
    }

    // Where the event filter says which kind of event the list is narrowed down to,
    // holding nothing while no event word has been clicked
    html += '<span id="' + config.eventChipHost.slice(1) + '"></span>';

    html += '</div>';

    return html;
};

// /////////////////////////////////////////////////////////////////////////////

listing.rangeLabel = function(minutes) {
    var options = listing.config.rangeOptions;
    var out = '';

    for (var optionIndex = 0; optionIndex < options.length; optionIndex++) {
        if (options[optionIndex].minutes === minutes) {
            out = options[optionIndex].label;
            break;
        }
    }

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

listing.setRange = function(minutes) {
    listing.minutes = minutes;
    $('#' + listing.config.rangePillId + '-pill').text(listing.rangeLabel(minutes));
};

// /////////////////////////////////////////////////////////////////////////////

// The moment the range now picked reaches back to, as the poll reads it, and nothing at all
// when the range is the whole log. Event times are stored as UTC with the offset spelled out,
// and the comparison is made on the text of them, so the cutoff is written the same way.
listing.rangeTimeFrom = function() {
    if (listing.minutes === 0) {
        return '';
    }

    var cutoff = new Date(Date.now() - listing.minutes * 60000);
    var out = cutoff.toISOString().replace('Z', '+00:00');

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// A window the reader has just picked, asked of the whole log rather than of the page that
// happens to be open, so the count and the pages agree with what is on the screen. A preset
// replaces whatever window a clicked stamp had picked, its far edge and its address included.
listing.applyRange = function() {
    var pagination = $.fn.zato.audit_log.pagination;

    kit.url_state.replace({time_from: '', time_to: ''});

    pagination.set_filters({time_from: listing.rangeTimeFrom(), time_to: ''});
    pagination.fetch_page(1);
};

// /////////////////////////////////////////////////////////////////////////////

// The window one clicked stamp unit means - the range pill reads it back and the address
// bar carries it, so the view deep-links. It is not a rolling range, so the live refresh
// leaves its edges where the click put them.
listing.applyTimeWindow = function(picked) {
    listing.minutes = 0;

    $('#' + listing.config.rangePillId + '-pill').text(picked.label);

    kit.url_state.replace({time_from: picked.time_from, time_to: picked.time_to});

    var pagination = $.fn.zato.audit_log.pagination;
    pagination.set_filters({time_from: picked.time_from, time_to: picked.time_to});
    pagination.fetch_page(1);
};

// /////////////////////////////////////////////////////////////////////////////

listing.refresh = function() {
    var pagination = $.fn.zato.audit_log.pagination;
    pagination.fetch_page(pagination.current_page());
};

// /////////////////////////////////////////////////////////////////////////////

// The same page asked for again by the clock rather than by the reader, which is the one
// case where what has arrived since is worth pointing out
listing.refreshLive = function() {
    listing.isLive = true;

    // A window reaching back from now rolls with it, so the cutoff is worked out again at
    // every tick rather than staying where it stood when the range was picked. A page
    // opened on a window of its own reports no range and keeps the window it was given.
    if (listing.minutes > 0) {
        $.fn.zato.audit_log.pagination.set_filters({time_from: listing.rangeTimeFrom()});
    }

    listing.refresh();
};

// /////////////////////////////////////////////////////////////////////////////

// What the legend still has switched on, as the filter the poll takes - the badges
// name the outcomes to show, and all of them on means no filter at all, so events
// reporting no outcome of their own stay on the page too
listing.pickedOutcomes = function(outcomes) {
    var visible = [];

    for (var outcomeIndex = 0; outcomeIndex < outcomes.length; outcomeIndex++) {
        var outcome = outcomes[outcomeIndex];

        if (!listing.hidden[outcome]) {
            visible.push(outcome);
        }
    }

    if (visible.length === outcomes.length) {
        return [];
    }

    return visible;
};

// The legend that narrows the list down to one outcome - built afresh whenever what
// the rows can report changes, e.g. the picked sources no longer include the one
// whose messages can expire. A toggled badge asks the server for page one of what
// is left, it does not hide rows of the page already here.
listing.buildLegend = function(outcomes) {
    var config = listing.config;
    var palette = kit.palette.outcome;

    // A clicked outcome badge elsewhere on the page drives this same legend,
    // so what it now offers is kept at hand
    listing.currentOutcomes = outcomes;

    if (!outcomes.length) {
        return;
    }

    kit.build_legend({
        container: config.legendHost,
        series_keys: outcomes,
        palette: palette.bar_colors,
        labels: palette.labels,
        text_colors: palette.colors,
        backgrounds: palette.backgrounds,
        hidden: listing.hidden,
        on_toggle: function() {
            var pagination = $.fn.zato.audit_log.pagination;

            pagination.set_filters({outcomes: listing.pickedOutcomes(outcomes)});
            pagination.fetch_page(1);
        }
    });
};

// /////////////////////////////////////////////////////////////////////////////

// The chip beside the legend saying which kind of event the list is narrowed down to -
// standing empty, and taking no room, while the list is not narrowed down at all
listing.drawEventFilterChip = function() {
    var host = $(listing.config.eventChipHost);

    if (listing.eventFilter === '') {
        host.html('');
        return;
    }

    var eventWord = $.fn.zato.audit_log.eventLabel(listing.eventFilter);

    var html = '<span class="dashboard-pill audit-log-filter-chip">' + listing.escapeHTML(eventWord) +
        '<span class="audit-log-filter-chip-clear" title="Show every kind of event">&times;</span></span>';

    host.html(html);
};

// /////////////////////////////////////////////////////////////////////////////

// The filter one clicked event word applies - the log narrows down to events of that kind,
// the chip beside the legend says so and the address bar carries it, so the view deep-links
listing.applyEventFilter = function(eventType) {
    listing.eventFilter = eventType;
    listing.drawEventFilterChip();

    kit.url_state.replace({event_type: eventType});

    var pagination = $.fn.zato.audit_log.pagination;
    pagination.set_filters({event_types: [eventType]});
    pagination.fetch_page(1);
};

// /////////////////////////////////////////////////////////////////////////////

listing.clearEventFilter = function() {
    listing.eventFilter = '';
    listing.drawEventFilterChip();

    kit.url_state.replace({event_type: ''});

    var pagination = $.fn.zato.audit_log.pagination;
    pagination.set_filters({event_types: []});
    pagination.fetch_page(1);
};

// /////////////////////////////////////////////////////////////////////////////

// A clicked outcome badge narrows the legend down to its own outcome - every other badge
// goes dim, and switching them back on is done up there, where the filter lives
listing.applyOutcomeFilter = function(outcome) {
    var outcomes = listing.currentOutcomes;

    listing.hidden = {};

    for (var outcomeIndex = 0; outcomeIndex < outcomes.length; outcomeIndex++) {
        if (outcomes[outcomeIndex] !== outcome) {
            listing.hidden[outcomes[outcomeIndex]] = true;
        }
    }

    listing.buildLegend(outcomes);

    var pagination = $.fn.zato.audit_log.pagination;
    pagination.set_filters({outcomes: listing.pickedOutcomes(outcomes)});
    pagination.fetch_page(1);
};

// /////////////////////////////////////////////////////////////////////////////

listing.initChrome = function(initConfig) {
    var config = listing.config;

    $(config.chromeHost).html(listing.chromeHTML());

    // A page deep-linked to events of one kind opens with the chip already saying so
    listing.eventFilter = initConfig.event_type;
    listing.drawEventFilterChip();

    kit.auto_refresh.init({
        pill: '#audit-log-refresh-pill',
        menu: '#audit-log-refresh-menu',
        storage_key: config.refreshStorageKey,
        url_param: 'refresh',
        default_seconds: config.refreshDefaultSeconds,
        on_tick: listing.refreshLive
    });

    var rangeConfig = {
        pill: '#' + config.rangePillId + '-pill',
        menu: '#' + config.rangePillId + '-menu',
        storage_key: config.rangeStorageKey,
        on_change: function(minutes) {
            listing.setRange(minutes);
            listing.applyRange();
        }
    };

    // A page opened on a window of its own - one clicked on an analytics chart - is read
    // through that window, so the range this screen was last left on does not overwrite it.
    if (initConfig.time_from !== '' || initConfig.time_to !== '') {
        rangeConfig.initial_minutes = 0;
    }

    var range = kit.time_range.init(rangeConfig);

    // The range this screen was left on last time is the one it opens on, and the pill
    // says so before the first page has even arrived.
    listing.setRange(range.get_minutes());

    // A page opened on a window of its own - a reloaded scrub pick, a link handed on -
    // reads that window off the address, so the pill says the window rather than All
    if (initConfig.time_from !== '' && initConfig.time_to !== '') {
        listing.minutes = 0;

        $('#' + config.rangePillId + '-pill').text(kit.time_scrub.window_label(
            new Date(initConfig.time_from), new Date(initConfig.time_to)));
    }

    // The legend offers this source's own outcomes - a delivery running out of time is
    // something only a pub/sub message does, and an HL7 log is not asked about it.
    listing.buildLegend($.fn.zato.audit_log.config.outcomes);

    // Every stamp on the page is a scrubber, and a clicked unit of one becomes the window
    kit.time_scrub.init({
        on_pick: function(picked) {
            listing.applyTimeWindow(picked);
        }
    });
};

// /////////////////////////////////////////////////////////////////////////////

listing.initPanes = function(source) {
    var config = listing.config;

    var listHTML = '<table class="detail-table audit-log-list-table">';
    listHTML += '<tbody id="' + config.itemsHost.slice(1) + '"></tbody>';
    listHTML += '</table>';

    listing.panes = kit.list_detail.create({
        host: config.host,

        // An HL7 log remembers its own proportions apart from a pub/sub or an AS2 one
        storage_key: config.storagePrefix + source,
        default_list_width: config.defaultListWidth,

        // The log is the page - it takes the room the window has left below the search box and
        // the pills, and the list and the pane are scrolled inside it rather than the page
        // being scrolled to reach the foot of them
        fit_height: true,

        list_html: listHTML,
        items_host: config.itemsHost,
        item_selector: config.itemSelector,

        id_of: function(rowModel) { return rowModel.id; },
        render_item: listing.rowHTML,
        render_empty: listing.emptyRowHTML,
        render_detail: listing.paneHTML,
        update_detail: listing.paneUpdate,
        empty_detail: '<div class="dashboard-inline-empty">' + config.emptyPane + '</div>',
        no_items_detail: '<div class="dashboard-inline-empty">' + config.emptyPaneNoEvents + '</div>',
        on_select: listing.onSelect
    });

    listing.panes.items_host().html(listing.loadingRowHTML());

    // The list is dragged wider and narrower by hand, so what fits is worked out again whenever
    // it changes size rather than only when a page of events arrives, and the rail beside it is
    // brought back level at the same time
    var listElement = listing.panes.items_host().closest('table').parent()[0];

    new ResizeObserver(function() {
        listing.fitColumns();
        listing.rail.sync();
    }).observe(listElement);

    // The rows scroll under the rail, so their marks follow them down it
    listElement.addEventListener('scroll', listing.rail.schedule);
};

// /////////////////////////////////////////////////////////////////////////////

listing.init = function(initConfig) {
    listing.initChrome(initConfig);
    listing.initPanes(initConfig.source);

    // A link naming an event opens on it - the selection is made before the first page has
    // arrived, and the page that arrives keeps whatever is already selected on it.
    var urlEvent = kit.url_state.get(listing.config.eventURLKey);

    if (urlEvent !== null && urlEvent !== '') {
        listing.panes.select(urlEvent);

        // A link out of an alert may additionally ask for the resubmit confirmation
        // on that event - honoured once the page holding the event is on screen
        var urlAction = kit.url_state.get(listing.config.actionURLKey);

        if (urlAction === listing.config.resubmitAction) {
            listing.pendingAction = urlEvent;
        }
    }

    // The events sharing a value are asked for wherever that value is named - the Details tab
    // and the panel a flow line opens
    $(document).on('click', listing.config.host + ' .dashboard-fact-row-search', function(event) {
        event.stopPropagation();

        $.fn.zato.audit_log.search($(this).attr('data-search-value'));
    });

    // An event word narrows the list down to events of its kind, wherever it is worn -
    // on a row or in the pane. The click filters, it does not also select the row under it.
    $(document).on('click', '.audit-log-event-filter', function(event) {
        event.preventDefault();
        event.stopPropagation();

        listing.applyEventFilter($(this).attr('data-event-type'));
    });

    // The chip's cross asks for every kind of event back
    $(document).on('click', '.audit-log-filter-chip-clear', function() {
        listing.clearEventFilter();
    });

    // An outcome badge drives the legend the way clicking the legend itself does
    $(document).on('click', '.audit-log-outcome-filter', function(event) {
        event.stopPropagation();

        listing.applyOutcomeFilter($(this).attr('data-outcome'));
    });

    // The way the message is being read goes into the address bar, parsed being taken as
    // read there the same way it is on the screen
    $(document).on('click', listing.config.payloadHost + ' .dashboard-payload-tab', function() {
        var config = listing.config;
        var tab = listing.detailTabs()[Number($(this).attr('data-tab-index'))];

        var view = '';

        if (!tab.parsed) {
            view = config.rawView;
        }

        var updates = {};
        updates[config.viewURLKey] = view;

        kit.url_state.replace(updates);
    });

    // A lineage marker of an event on this page selects it, and one of an event on
    // a page of its own has nothing to select here.
    $(document).on('click', '.audit-log-lineage', function() {
        var eventId = $(this).attr('data-lineage-id');

        if (listing.modelById(eventId) !== null) {
            listing.panes.select(eventId);
        }
    });

};

// /////////////////////////////////////////////////////////////////////////////

})(jQuery);
