
// /////////////////////////////////////////////////////////////////////////////

// Message flow - the pane under the drawing. One constant size whatever it is
// holding, so opening, switching and closing nodes never moves anything around
// it. A clicked node's exchange opens here as one body with one tab per event,
// in the order the card reads them, each body fetched from the audit log the
// first time its tab is opened, the files an event carried offered over it.

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

    // What the tab of an event's second body says - the reply of a source whose
    // one event holds both what was sent and what came back
    responseTabLabel: 'Response',

    // The words of the root's own strip - the message's whole flow summed up
    summaryLabel: 'FLOW',
    summaryWords: {
        exchanges: 'Exchanges',
        events: 'Events',
        first: 'First event',
        last: 'Last event',
        span: 'End to end',
        errors: 'Errors'
    },

    // What stands between the exchange's name and the words of the event the
    // pane is open on, the same dot the drawing's lines use
    titleSeparator: ' \u00b7 ',

    // The word each kind of line wears, the same words the drawing writes
    roleLabels: {
        'request': 'REQUEST',
        'response': 'RESPONSE',
        'none': 'SYS',
        'view': 'VIEW',
        'job': 'SCHEDULER',
        'service': 'AUDIT WRITE',
        'service-request': 'REQUEST',
        'service-response': 'RESPONSE',
        'transfer': 'TRANSFER',
        'access': 'ACCESS'
    },

    // The word the header names an event's role by, before the event's own words
    headerRoleWords: {
        'request': 'Request',
        'response': 'Response',
        'none': 'System',
        'view': 'View',
        'job': 'Scheduler',
        'service': 'Audit write',
        'service-request': 'Request',
        'service-response': 'Response',
        'transfer': 'Transfer',
        'access': 'Access'
    },

    // The roles whose event is a response - what a source hangs a response's further bodies on
    responseRoles: {
        'response': true,
        'service-response': true
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

// The words the pane's header says about the event its tabs stand on - the
// event's role, and after a dot what the source has to say of the event - so
// the header names both the exchange and the very event
detail.eventWords = function(model) {
    var config = detail.config;

    var presenter = $.fn.zato.audit_log.presenterFor(model.raw.source);
    var out = config.headerRoleWords[detail.roleOf(model)];

    var note = presenter.headerNote(model);

    if (note !== '') {
        out += config.titleSeparator + note;
    }

    return out;
};

// The drawing brought to the event the tabs stand on - that event's line on its
// node wears the selection amber on its chips, every other line its own inks.
// The root stands for the message and has no line of its own, so with the root
// open no line is marked, though its pane reads the seed event.
detail.markCurrentLine = function() {
    var wanted = String(detail.currentEventId);

    if (detail.openDetail !== null && detail.openDetail.key === '') {
        wanted = '';
    }

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

// What a tab's body is remembered under - one event may have several tabs,
// each holding a different body of it
detail.bodyKey = function(tab) {
    return String(tab.eventId) + ':' + tab.kind;
};

// /////////////////////////////////////////////////////////////////////////////

// The pane's entries for one exchange - one per event in the order the card
// reads them, as {model, kind, role, isSecond}, the kind naming which body of
// the event the entry opens, empty for the event's own data. A source whose one
// event holds both what was sent and what came back - a file transfer run
// talking to its server - gives that event two entries, the second one the
// reply's body. The role is the part the entry plays, which is what a source
// hangs its further bodies on.
detail.entriesOf = function(models) {
    var config = detail.config;
    var out = [];

    for (var modelIndex = 0; modelIndex < models.length; modelIndex++) {
        var model = models[modelIndex];

        var presenter = $.fn.zato.audit_log.presenterFor(model.raw.source);
        var paneKinds = presenter.paneKinds(model);

        if (paneKinds !== null) {
            out.push({model: model, kind: paneKinds.request, role: 'request', isSecond: false});
            out.push({model: model, kind: paneKinds.response, role: 'response', isSecond: true});
        }
        else if (config.responseRoles[detail.roleOf(model)] === true) {
            out.push({model: model, kind: '', role: 'response', isSecond: false});
        }
        else {
            out.push({model: model, kind: '', role: 'request', isSecond: false});
        }
    }

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// The pane brought to one exchange - the header, the files its events carried,
// and the body with one tab per event, each body asked for the first time its
// tab is opened
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

    // The root stands for the message itself, so its pane sums the whole flow
    // up in a strip before the message's own body
    if (nodeDetail.flowSummary !== null) {
        detail.addSummary(host, nodeDetail.flowSummary);
    }

    // The files the events carried are asked about the moment the pane holds
    // them - an event carrying none keeps its strip's place empty
    var attachments = document.createElement('div');
    attachments.className = 'message-flow-detail-attachments';
    host.appendChild(attachments);

    for (var modelIndex = 0; modelIndex < nodeDetail.models.length; modelIndex++) {
        var model = nodeDetail.models[modelIndex];

        var attachmentsHost = document.createElement('div');
        attachmentsHost.className = 'message-flow-detail-attachments-host';

        // The strip only fills in for the record it was asked about, which the
        // kit reads off the host itself
        attachmentsHost.setAttribute('data-attachments-id', model.id);
        attachments.appendChild(attachmentsHost);

        listing.loadAttachments(model, $(attachmentsHost));
    }

    var entries = detail.entriesOf(nodeDetail.models);

    detail.addBody(host, entries);

    // The tabs open on the first event, and the header says which event that is
    detail.currentEventId = entries[0].model.id;

    detail.updateTitle();
    detail.updateCaption();
};

// /////////////////////////////////////////////////////////////////////////////

// The pane's body - its events' badges always on top, each tab's body fetched
// the first time it is opened, parsed when the source's reader made sense of
// it, as it went down the wire otherwise
detail.addBody = function(host, entries) {
    var config = detail.config;
    var listing = $.fn.zato.audit_log.listing;

    var body = document.createElement('div');
    body.className = 'message-flow-detail-body';
    host.appendChild(body);

    var tabs = [];

    for (var entryIndex = 0; entryIndex < entries.length; entryIndex++) {
        var entry = entries[entryIndex];
        var model = entry.model;

        // An event's second body wears the reply's word, its first the event's own
        if (entry.isSecond) {
            tabs.push(detail.extraTabOf(model, {label: config.responseTabLabel, kind: entry.kind}));
        }
        else {
            tabs.push(detail.tabOf(model, entry.kind));
        }

        // The event's further bodies after that one - a failed run's traceback beside its response
        var presenter = $.fn.zato.audit_log.presenterFor(model.raw.source);
        var extras = presenter.paneExtras(model, entry.role);

        for (var extraIndex = 0; extraIndex < extras.length; extraIndex++) {
            tabs.push(detail.extraTabOf(model, extras[extraIndex]));
        }
    }

    var panelHost = document.createElement('div');
    panelHost.className = 'message-flow-detail-panel';
    body.appendChild(panelHost);

    var caption = document.createElement('div');
    caption.className = 'message-flow-detail-caption';
    body.appendChild(caption);

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

// The root's own strip - the message's whole flow summed up, one measure after
// another on a single line, the error count wearing the bad ink the moment
// there is anything to wear it for
detail.addSummary = function(host, summary) {
    var config = detail.config;
    var words = config.summaryWords;

    var strip = document.createElement('div');
    strip.className = 'message-flow-detail-summary';
    host.appendChild(strip);

    var badge = document.createElement('span');
    badge.className = 'message-flow-detail-summary-badge';
    badge.textContent = config.summaryLabel;
    strip.appendChild(badge);

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

        var item = document.createElement('span');
        item.className = 'message-flow-detail-summary-item';
        strip.appendChild(item);

        var label = document.createElement('span');
        label.className = 'message-flow-detail-summary-label';
        label.textContent = entry[0];
        item.appendChild(label);

        var value = document.createElement('span');
        value.className = 'message-flow-detail-summary-value';

        if (entry[2]) {
            value.className += ' message-flow-detail-summary-value-bad';
        }

        value.textContent = entry[1];
        item.appendChild(value);
    }
};

// /////////////////////////////////////////////////////////////////////////////

// The words under the body - how much of it there is, in the same dim ink the
// list's captions use, and nothing while the open body is still on its way.
// The pane may have been emptied while a body was coming, in which case there
// is simply no caption to bring up.
detail.updateCaption = function() {
    var host = detail.host();
    var caption = host.querySelector('.message-flow-detail-caption');

    if (caption === null) {
        return;
    }

    var $body = $(caption.parentElement);
    var $openTab = $body.find('.dashboard-payload-tab.dashboard-panel-action-badge-active');

    var tabs = $body.find('.dashboard-payload').data('payload_tabs');
    var tab = tabs[parseInt($openTab.attr('data-tab-index'), 10)];

    var length = detail.bodyLengths[detail.bodyKey(tab)];

    if (length === undefined) {
        caption.textContent = '';
        return;
    }

    caption.textContent = length.toLocaleString('en-US') + ' ' + detail.config.charactersLabel;
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

// The bar over the pane is wired in detail-resize.js
detail.init = function() {
    detail.wireResize();
    detail.hide();
};

// /////////////////////////////////////////////////////////////////////////////

// The open pane brought to one event - its first tab in front, the way a click
// on it would do it, the header and the drawing following
detail.openEvent = function(eventId) {
    var wanted = String(eventId);
    var $body = $(detail.host()).find('.message-flow-detail-body');
    var $panel = $body.find('.dashboard-payload');

    if ($panel.length === 0) {
        return;
    }

    var tabs = $panel.data('payload_tabs');

    for (var tabIndex = 0; tabIndex < tabs.length; tabIndex++) {
        if (String(tabs[tabIndex].eventId) === wanted) {
            kit.payload_panel.open($body, tabIndex);
            break;
        }
    }

    detail.currentEventId = eventId;
    detail.updateTitle();
    detail.updateCaption();
};

// /////////////////////////////////////////////////////////////////////////////

// The panel's own handler has already put the clicked tab in front by the time
// this one runs, so what is left is bringing the header and the drawing to the
// tab's event and saying how much text the open tab holds
$(document).on('click', '#message-flow-detail .dashboard-payload-tab', function() {
    var $tab = $(this);
    var $panel = $tab.closest('.dashboard-payload');

    var tabs = $panel.data('payload_tabs');
    var tab = tabs[parseInt($tab.attr('data-tab-index'), 10)];

    detail.currentEventId = tab.eventId;
    detail.updateTitle();
    detail.updateCaption();
});

// /////////////////////////////////////////////////////////////////////////////

})(jQuery);
