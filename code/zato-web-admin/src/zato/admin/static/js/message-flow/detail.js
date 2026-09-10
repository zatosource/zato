
// /////////////////////////////////////////////////////////////////////////////

// Message flow - the pane under the drawing. One constant size whatever it is
// holding, so opening, switching and closing nodes never moves anything around
// it. A clicked node's exchange opens here in two sides - the request's and
// the reply's, sharing the pane by the bar between them - one tab per event,
// each body fetched from the audit log the first time its tab is opened, the
// files an event carried offered over the bodies.

$.fn.zato.message_flow.detail = {};

// /////////////////////////////////////////////////////////////////////////////

(function($) {

var kit = $.fn.zato.dashboard_kit;
var detail = $.fn.zato.message_flow.detail;

// /////////////////////////////////////////////////////////////////////////////

detail.config = {

    hostId: 'message-flow-detail',
    resizeBarId: 'message-flow-resize',
    pageSelector: '.message-flow-page',

    // What the pane says with nothing picked and while a body is on its way
    hint: 'No node selected',
    charactersLabel: 'characters',

    // What either side of the pane says when the exchange has no events
    // of its own kind for it
    sideHints: {
        'request': '(Empty request)',
        'response': '(Empty reply)'
    },

    // The words of the root's own right side - the message's whole flow
    // summed up, where a reply side would have nothing truthful to say
    summaryLabel: 'FLOW',
    summaryWords: {
        exchanges: 'Exchanges',
        events: 'Events',
        first: 'First event',
        last: 'Last event',
        span: 'End to end',
        errors: 'Errors'
    },

    // How the two sides share the pane - where the browser keeps the share,
    // what it is before anyone pulls the bar, and the least share either
    // side keeps
    splitStorageKey: 'zato.message-flow.detail-split',
    splitDefaultPercent: 50,
    splitMinPercent: 20,

    // What stands between the exchange's name and the words of the event the
    // pane is open on, the same dot the drawing's lines use
    titleSeparator: ' \u00b7 ',

    // The word each kind of line wears, the same words the drawing writes
    roleLabels: {
        'request': 'REQ',
        'response': 'REPLY',
        'none': 'SYS',
        'view': 'VIEW',
        'job': 'SCHEDULER',
        'service': 'SERVICE',
        'transfer': 'TRANSFER',
        'access': 'ACCESS'
    },

    // The one event type that is a person reading rather than a message moving
    viewEventType: 'content-viewed',

    // The outcome worn in the good ink - every other reported outcome reads bad
    goodOutcome: 'ok',

    // How small either side of the split may get when the bar between the
    // drawing and the pane is pulled
    detailMinHeight: 120,
    canvasMinHeight: 160,

    // Lower than this the pane has room for nothing worth reading, so it is shut
    // all the way rather than left standing as a strip - the bar stays where it
    // is and the same pull upward opens it back
    detailSnapHeight: 60,

    // The class the bar wears mid-pull
    resizeActiveClass: 'message-flow-resizing'
};

// /////////////////////////////////////////////////////////////////////////////

// What the pane is holding, which of its events the open tabs stand on, and how
// long each of its bodies turned out to be, by tab index, which is what the
// caption under the body reads
detail.openDetail = null;
detail.currentEventId = null;
detail.bodyLengths = {};

// /////////////////////////////////////////////////////////////////////////////

// The words the pane's header says about the event its tabs stand on - what the
// event's own line on the card reads, the event's kind when the line has no
// words of its own - so the header names both the exchange and the very event
detail.eventWords = function(model) {
    var presenter = $.fn.zato.audit_log.presenterFor(model.raw.source);
    var out = presenter.lineNote(model);

    if (out === '') {
        out = model.eventLabel;
    }

    return out;
};

// The drawing brought to the event the tabs stand on - that event's line on its
// node wears the selection amber on its chips, every other line its own inks
detail.markCurrentLine = function() {
    var wanted = String(detail.currentEventId);
    var lines = document.querySelectorAll('.message-flow-line');

    for (var lineIndex = 0; lineIndex < lines.length; lineIndex++) {
        var line = lines[lineIndex];
        var isCurrent = line.getAttribute('data-event-id') === wanted;

        line.classList.toggle('message-flow-line-current', isCurrent);
    }
};

// The header brought to the event the tabs stand on - the exchange's name, the
// dot, the event's words - and the drawing with it
detail.updateTitle = function() {
    var nodeDetail = detail.openDetail;

    if (nodeDetail === null) {
        return;
    }

    var text = nodeDetail.title;
    var wanted = String(detail.currentEventId);

    for (var modelIndex = 0; modelIndex < nodeDetail.models.length; modelIndex++) {
        var model = nodeDetail.models[modelIndex];

        if (String(model.id) === wanted) {
            text += detail.config.titleSeparator + detail.eventWords(model);
            break;
        }
    }

    var title = detail.host().querySelector('.message-flow-detail-title');
    title.textContent = text;

    detail.markCurrentLine();
};

// /////////////////////////////////////////////////////////////////////////////

detail.host = function() {
    return document.getElementById(detail.config.hostId);
};

// /////////////////////////////////////////////////////////////////////////////

detail.escapeHTML = function(value) {
    return $.fn.zato.audit_log.escapeHTML(value);
};

// /////////////////////////////////////////////////////////////////////////////

// The ink a line's role is written in, on the pane's tabs
detail.roleOf = function(model) {
    var config = detail.config;

    if (model.eventType === config.viewEventType) {
        return 'view';
    }

    return model.role;
};

// /////////////////////////////////////////////////////////////////////////////

// What one tab of the pane wears - the role in its own ink, the event's
// id in amber, and an outcome in the outcome's own colour. The plain label
// stays beside the markup, being what a tab is told apart by. The kind is
// which body of the event the tab opens - empty for the event's own data.
detail.tabOf = function(model, kind) {
    var config = detail.config;

    var role = detail.roleOf(model);
    var roleLabel = config.roleLabels[role];

    var labelHtml = '<span class="message-flow-detail-tab-role-' + role + '">' +
        roleLabel + '</span>';
    labelHtml += '<span class="message-flow-detail-tab-id">' + model.id + '</span>';

    // An event whose word is an outcome carries it on the tab, so a failed leg
    // says so before it is even opened
    if (model.outcome !== '') {
        var outcomeKind = model.outcome === config.goodOutcome ? 'good' : 'bad';

        labelHtml += '<span class="message-flow-detail-tab-outcome-' + outcomeKind + '">' +
            detail.escapeHTML(model.outcome.toUpperCase()) + '</span>';
    }

    var out = {
        label: roleLabel + ' \u00b7 ' + model.id,
        label_html: labelHtml,
        eventId: model.id,
        kind: kind
    };

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// A tab for one further body of an event, its word in amber
detail.extraTabOf = function(model, extra) {
    var labelHtml = '<span class="message-flow-detail-tab-extra">' + detail.escapeHTML(extra.label) + '</span>';

    var out = {
        label: extra.label + ' \u00b7 ' + model.id,
        label_html: labelHtml,
        eventId: model.id,
        kind: extra.kind
    };

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// What a tab's body is remembered under - one event may stand on both sides
// of the pane, each side holding a different body of it
detail.bodyKey = function(tab) {
    return String(tab.eventId) + ':' + tab.kind;
};

// /////////////////////////////////////////////////////////////////////////////

// The pane brought to one exchange - the header, the files its events carried,
// and the body in two sides, the request's and the reply's, each with one tab
// per event, each body asked for the first time its tab is opened
detail.show = function(nodeDetail) {
    var listing = $.fn.zato.audit_log.listing;
    var page = $.fn.zato.message_flow.page;

    var host = detail.host();

    detail.openDetail = nodeDetail;
    detail.bodyLengths = {};

    host.textContent = '';

    var header = document.createElement('div');
    header.className = 'message-flow-detail-header';
    host.appendChild(header);

    var title = document.createElement('span');
    title.className = 'message-flow-detail-title';
    title.textContent = nodeDetail.title;
    header.appendChild(title);

    var meta = document.createElement('span');
    meta.className = 'message-flow-detail-meta';
    header.appendChild(meta);

    var identity = document.createElement('span');
    identity.className = 'message-flow-detail-identity';
    identity.textContent = page.state.identity;
    meta.appendChild(identity);

    var time = document.createElement('span');
    time.className = 'message-flow-detail-time';
    time.textContent = nodeDetail.time;
    meta.appendChild(time);

    // A source with a panel of its own - a run's report, a file's journey - draws it before
    // the bodies. The models arrive newest first, so the newest one is the one the panel is about.
    var newestModel = nodeDetail.models[nodeDetail.models.length - 1];
    var presenter = $.fn.zato.audit_log.presenterFor(newestModel.raw.source);

    if (presenter.detailPanel !== undefined) {
        var sourcePanel = document.createElement('div');
        sourcePanel.className = 'message-flow-detail-source-panel';
        host.appendChild(sourcePanel);

        presenter.detailPanel(nodeDetail.models, $(sourcePanel), 'dark');
    }

    // The files the events carried are asked about the moment the pane holds
    // them - an event carrying none keeps its strip's place empty
    var attachments = document.createElement('div');
    attachments.className = 'message-flow-detail-attachments';
    host.appendChild(attachments);

    // The events split between the two sides - a reply to the right, every
    // other kind of line to the left with the request it belongs to. A source
    // whose one event holds both what was sent and what came back - a file
    // transfer run talking to its server, a service's invocation - puts that
    // same event on both sides, each side reading its own body of it. Each
    // event says this for itself, so a card mixing such events with plain
    // ones - an invocation and the notes its service wrote - reads each right.
    // Each side holds {model, kind} entries, the kind naming which body of the
    // event that side reads, empty for the event's own data.
    var requestEntries = [];
    var responseEntries = [];

    for (var modelIndex = 0; modelIndex < nodeDetail.models.length; modelIndex++) {
        var model = nodeDetail.models[modelIndex];

        var modelPresenter = $.fn.zato.audit_log.presenterFor(model.raw.source);
        var paneKinds = modelPresenter.paneKinds(model);

        if (paneKinds !== null) {
            requestEntries.push({model: model, kind: paneKinds.request});
            responseEntries.push({model: model, kind: paneKinds.response});
        }
        else if (detail.roleOf(model) === 'response') {
            responseEntries.push({model: model, kind: ''});
        }
        else {
            requestEntries.push({model: model, kind: ''});
        }

        var attachmentsHost = document.createElement('div');
        attachmentsHost.className = 'message-flow-detail-attachments-host';

        // The strip only fills in for the record it was asked about, which the
        // kit reads off the host itself
        attachmentsHost.setAttribute('data-attachments-id', model.id);
        attachments.appendChild(attachmentsHost);

        listing.loadAttachments(model, $(attachmentsHost));
    }

    var split = document.createElement('div');
    split.className = 'message-flow-detail-split';
    host.appendChild(split);

    detail.addSide(split, 'request', requestEntries);

    var splitBar = document.createElement('div');
    splitBar.className = 'message-flow-detail-split-bar';
    split.appendChild(splitBar);

    // The root stands for the message itself and has no reply of its own to
    // wait for - its right side sums the whole flow up instead
    if (nodeDetail.flowSummary === null) {
        detail.addSide(split, 'response', responseEntries);
    }
    else {
        detail.addSummarySide(split, nodeDetail.flowSummary);
    }

    detail.applySplit(split);

    // The tabs open on the first event of the request side, the reply side's when
    // the request side has none, and the header says which event that is
    var openEntries = requestEntries;

    if (openEntries.length === 0) {
        openEntries = responseEntries;
    }

    detail.currentEventId = null;

    if (openEntries.length > 0) {
        detail.currentEventId = openEntries[0].model.id;
    }

    detail.updateTitle();
    detail.updateCaption();
};

// /////////////////////////////////////////////////////////////////////////////

// One side of the pane - its events' badges always on top, each tab's body
// fetched the first time it is opened, parsed when the source's reader made
// sense of it, as it went down the wire otherwise. A side the exchange has
// no events for says so. Each entry is {model, kind}, the kind naming which
// body of that event the side reads - empty for the event's own data.
detail.addSide = function(split, role, entries) {
    var listing = $.fn.zato.audit_log.listing;

    var side = document.createElement('div');
    side.className = 'message-flow-detail-side message-flow-detail-side-' + role;
    split.appendChild(side);

    if (entries.length === 0) {
        var hint = document.createElement('div');
        hint.className = 'message-flow-detail-side-hint';
        hint.textContent = detail.config.sideHints[role];
        side.appendChild(hint);

        return;
    }

    var tabs = [];

    for (var entryIndex = 0; entryIndex < entries.length; entryIndex++) {
        var model = entries[entryIndex].model;
        tabs.push(detail.tabOf(model, entries[entryIndex].kind));

        // The event's further bodies this side opens - a failed run's traceback beside its reply
        var presenter = $.fn.zato.audit_log.presenterFor(model.raw.source);
        var extras = presenter.paneExtras(model, role);

        for (var extraIndex = 0; extraIndex < extras.length; extraIndex++) {
            tabs.push(detail.extraTabOf(model, extras[extraIndex]));
        }
    }

    var panelHost = document.createElement('div');
    panelHost.className = 'message-flow-detail-panel';
    side.appendChild(panelHost);

    var caption = document.createElement('div');
    caption.className = 'message-flow-detail-caption';
    side.appendChild(caption);

    kit.payload_panel.lazy($(panelHost), tabs, function(tab, onDone) {
        listing.fetchDetails(tab.eventId, tab.kind, false, function(details) {
            var text = details.data;

            if (details.parsed !== '') {
                text = details.parsed;
            }

            detail.bodyLengths[detail.bodyKey(tab)] = text.length;
            detail.updateCaption();

            onDone(text);
        });
    });
};

// /////////////////////////////////////////////////////////////////////////////

// The root's own right side - the message's whole flow summed up, its badge
// standing where the reply side's badges stand and one row per measure under
// it, the error row wearing the bad ink the moment there is anything to wear
// it for
detail.addSummarySide = function(split, summary) {
    var config = detail.config;
    var words = config.summaryWords;

    var side = document.createElement('div');
    side.className = 'message-flow-detail-side message-flow-detail-side-response';
    split.appendChild(side);

    var bar = document.createElement('div');
    bar.className = 'message-flow-detail-summary-bar';
    side.appendChild(bar);

    var badge = document.createElement('span');
    badge.className = 'message-flow-detail-summary-badge';
    badge.textContent = config.summaryLabel;
    bar.appendChild(badge);

    var rows = document.createElement('div');
    rows.className = 'message-flow-detail-summary';
    side.appendChild(rows);

    var entries = [
        [words.exchanges, String(summary.exchangeCount), false],
        [words.events, String(summary.eventCount), false],
        [words.first, summary.firstLocal, false],
        [words.last, summary.lastLocal, false],
        [words.span, kit.format_duration_ms(summary.spanMs), false],
        [words.errors, String(summary.errorCount), summary.errorCount > 0]
    ];

    for (var entryIndex = 0; entryIndex < entries.length; entryIndex++) {
        var entry = entries[entryIndex];

        var row = document.createElement('div');
        row.className = 'message-flow-detail-summary-row';
        rows.appendChild(row);

        var label = document.createElement('span');
        label.className = 'message-flow-detail-summary-label';
        label.textContent = entry[0];
        row.appendChild(label);

        var value = document.createElement('span');
        value.className = 'message-flow-detail-summary-value';

        if (entry[2]) {
            value.className += ' message-flow-detail-summary-value-bad';
        }

        value.textContent = entry[1];
        row.appendChild(value);
    }
};

// /////////////////////////////////////////////////////////////////////////////

// The words under each side's body - how much of it there is, in the same dim
// ink the list's captions use, and nothing while the open body is still on
// its way. The pane may have been emptied while a body was coming, in which
// case there are simply no captions to bring up.
detail.updateCaption = function() {
    var host = detail.host();
    var captions = host.querySelectorAll('.message-flow-detail-caption');

    for (var captionIndex = 0; captionIndex < captions.length; captionIndex++) {
        var caption = captions[captionIndex];
        var side = caption.parentElement;

        var $openTab = $(side).find('.dashboard-payload-tab.dashboard-panel-action-badge-active');

        var tabs = $(side).find('.dashboard-payload').data('payload_tabs');
        var tab = tabs[parseInt($openTab.attr('data-tab-index'), 10)];

        var length = detail.bodyLengths[detail.bodyKey(tab)];

        if (length === undefined) {
            caption.textContent = '';
            continue;
        }

        caption.textContent = length.toLocaleString('en-US') + ' ' + detail.config.charactersLabel;
    }
};

// /////////////////////////////////////////////////////////////////////////////

// With nothing picked, the pane stands where it always stands and says what
// it is waiting for
detail.hide = function() {
    var host = detail.host();

    detail.openDetail = null;
    detail.currentEventId = null;
    detail.markCurrentLine();

    host.textContent = '';

    var hint = document.createElement('div');
    hint.className = 'message-flow-detail-hint';
    hint.textContent = detail.config.hint;
    host.appendChild(hint);
};

// /////////////////////////////////////////////////////////////////////////////

// The pane's own bars - the one between its sides and the one over it - are
// wired in detail-resize.js
detail.init = function() {
    detail.wireResize();
    detail.wireSplit();
    detail.hide();
};

// /////////////////////////////////////////////////////////////////////////////

// The other side brought to the same event - the two sides read one exchange,
// so a tab picked on one of them picks that event's own tab on the other, the
// event's first tab there when it has several. A side with no tab for the
// event is left as it stands.
detail.followEvent = function($side, eventId) {
    var $otherSide = $side.siblings('.message-flow-detail-side');
    var $otherPanel = $otherSide.find('.dashboard-payload');

    if ($otherPanel.length === 0) {
        return;
    }

    var otherTabs = $otherPanel.data('payload_tabs');

    for (var tabIndex = 0; tabIndex < otherTabs.length; tabIndex++) {
        if (otherTabs[tabIndex].eventId === eventId) {
            kit.payload_panel.open($otherSide, tabIndex);
            return;
        }
    }
};

// Both sides of the open pane brought to one event - its own tab in front on
// each side that has one, the way a click on either of them would do it
detail.openEvent = function(eventId) {
    var wanted = String(eventId);
    var sides = detail.host().querySelectorAll('.message-flow-detail-side');

    for (var sideIndex = 0; sideIndex < sides.length; sideIndex++) {
        var $side = $(sides[sideIndex]);
        var $panel = $side.find('.dashboard-payload');

        if ($panel.length === 0) {
            continue;
        }

        var tabs = $panel.data('payload_tabs');

        for (var tabIndex = 0; tabIndex < tabs.length; tabIndex++) {
            if (String(tabs[tabIndex].eventId) === wanted) {
                kit.payload_panel.open($side, tabIndex);
                break;
            }
        }
    }

    detail.currentEventId = eventId;
    detail.updateTitle();
    detail.updateCaption();
};

// /////////////////////////////////////////////////////////////////////////////

// The panel's own handler has already put the clicked tab in front by the time
// this one runs, so what is left is bringing the other side and the header to
// the same event and saying how much text the open tabs hold
$(document).on('click', '#message-flow-detail .dashboard-payload-tab', function() {
    var $tab = $(this);
    var $panel = $tab.closest('.dashboard-payload');
    var $side = $tab.closest('.message-flow-detail-side');

    var tabs = $panel.data('payload_tabs');
    var tab = tabs[parseInt($tab.attr('data-tab-index'), 10)];

    detail.followEvent($side, tab.eventId);

    detail.currentEventId = tab.eventId;
    detail.updateTitle();
    detail.updateCaption();
});

// /////////////////////////////////////////////////////////////////////////////

})(jQuery);
