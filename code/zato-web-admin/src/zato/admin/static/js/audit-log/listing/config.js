

// /////////////////////////////////////////////////////////////////////////////

// The audit log listing - a main list of events beside a pane holding the selected one whole.

$.fn.zato.audit_log.listing = {};

// /////////////////////////////////////////////////////////////////////////////

(function($) {

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

    // The pane's tabs - everything said about the event, the message itself, and for a source
    // with a panel of its own what that panel shows. The whole flow the message belongs to
    // is a page of its own, which the pane head links to.
    tabSelector: '.audit-log-pane-tab',
    tabPanelPrefix: 'audit-log-pane-panel-',
    tabStorageKey: 'zato_audit_log_pane_tab',
    summaryTab: 'summary',
    dataTab: 'data',
    detailsTab: 'details',
    summaryTabLabel: 'Summary',
    dataTabLabel: 'Data',
    detailsTabLabel: 'Details',

    // What the doorway to the event's whole flow says
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

    // The tones of the event chip for an event that succeeded, failed or is still running.
    eventChipTone: 'good',
    eventChipErrorTone: 'bad',
    eventChipRunningTone: 'running',

    // The outcome of a row that is still changing and what its event word reads while it is.
    runningOutcome: 'running',
    runningLabel: 'Running',

    // The chip of a changing row that pulses when its words change.
    progressChipClass: 'audit-log-progress',

    // The unchanged runs, hidden by default on the sources that have them.
    unchangedStatus: 'unchanged',
    hideUnchangedLabel: 'Hiding unchanged runs',
    showUnchangedLabel: 'Showing unchanged runs',
    hideUnchangedStorageKey: 'zato_audit_log_hide_unchanged',
    hideUnchangedSources: {'file-outgoing': true},

    // What the confirm button says when the same content has gone out before.
    resubmitAnywayLabel: 'Deliver again anyway',

    // The order a row gives its columns up in as the list is narrowed, from the one least missed
    // to the one it holds on to longest - the action, the role tag, the event word, the chips
    // and then the time. Each name is the class the list carries while that column is being
    // left out, and the event's own number is not on the list at all - it is what a row is
    // pointed at by, so it is never given up.
    dropOrder: ['action', 'role', 'event', 'chips', 'time'],
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
    outcomeLabel: 'Outcome',
    statusLabel: 'Status',

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
    correlIdColumnKey: 'correl_id',

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
    'service-request': 'service-request',
    'service-response': 'service-response',
    'note': 'service',

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

// The last words of each changing row, by id.
listing.progressWords = {};

// Whether the page now being drawn arrived by itself rather than because the reader
// asked for it, which is the only time anything puffs
listing.isLive = false;

// The two panes, once they are built, the tab group of the detail pane, once it holds
// an event, and the event it is holding
listing.panes = null;
listing.tabs = null;
listing.selected = null;

// The row the pane keeps after the page no longer holds it.
listing.detached = null;

// Whether the unchanged runs are kept off the list.
listing.hideUnchanged = false;

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

})(jQuery);
