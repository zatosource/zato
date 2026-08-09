
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

    // The word each kind of line wears, the same words the drawing writes
    roleLabels: {
        'request': 'REQ',
        'response': 'REPLY',
        'none': 'SYS',
        'view': 'VIEW',
        'job': 'SCHEDULER'
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
    detailSnapHeight: 60
};

// /////////////////////////////////////////////////////////////////////////////

// What the pane is holding and how long each of its bodies turned out to be,
// by tab index, which is what the caption under the body reads
detail.openDetail = null;
detail.bodyLengths = {};

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
// stays beside the markup, being what a tab is told apart by.
detail.tabOf = function(model) {
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
        eventId: model.id
    };

    return out;
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

    // The files the events carried are asked about the moment the pane holds
    // them - an event carrying none keeps its strip's place empty
    var attachments = document.createElement('div');
    attachments.className = 'message-flow-detail-attachments';
    host.appendChild(attachments);

    // The events split between the two sides - a reply to the right, every
    // other kind of line to the left with the request it belongs to
    var requestModels = [];
    var responseModels = [];

    for (var modelIndex = 0; modelIndex < nodeDetail.models.length; modelIndex++) {
        var model = nodeDetail.models[modelIndex];

        if (detail.roleOf(model) === 'response') {
            responseModels.push(model);
        }
        else {
            requestModels.push(model);
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

    detail.addSide(split, 'request', requestModels);

    var splitBar = document.createElement('div');
    splitBar.className = 'message-flow-detail-split-bar';
    split.appendChild(splitBar);

    // The root stands for the message itself and has no reply of its own to
    // wait for - its right side sums the whole flow up instead
    if (nodeDetail.flowSummary === null) {
        detail.addSide(split, 'response', responseModels);
    }
    else {
        detail.addSummarySide(split, nodeDetail.flowSummary);
    }

    detail.applySplit(split);
    detail.updateCaption();
};

// /////////////////////////////////////////////////////////////////////////////

// One side of the pane - its events' badges always on top, each tab's body
// fetched the first time it is opened, parsed when the source's reader made
// sense of it, as it went down the wire otherwise. A side the exchange has
// no events for says so.
detail.addSide = function(split, role, models) {
    var listing = $.fn.zato.audit_log.listing;

    var side = document.createElement('div');
    side.className = 'message-flow-detail-side message-flow-detail-side-' + role;
    split.appendChild(side);

    if (models.length === 0) {
        var hint = document.createElement('div');
        hint.className = 'message-flow-detail-side-hint';
        hint.textContent = detail.config.sideHints[role];
        side.appendChild(hint);

        return;
    }

    var tabs = [];

    for (var modelIndex = 0; modelIndex < models.length; modelIndex++) {
        tabs.push(detail.tabOf(models[modelIndex]));
    }

    var panelHost = document.createElement('div');
    panelHost.className = 'message-flow-detail-panel';
    side.appendChild(panelHost);

    var caption = document.createElement('div');
    caption.className = 'message-flow-detail-caption';
    side.appendChild(caption);

    kit.payload_panel.lazy($(panelHost), tabs, function(tab, onDone) {
        listing.fetchDetails(tab.eventId, '', false, function(details) {
            var text = details.data;

            if (details.parsed !== '') {
                text = details.parsed;
            }

            detail.bodyLengths[String(tab.eventId)] = text.length;
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

        var length = detail.bodyLengths[String(tab.eventId)];

        if (length === undefined) {
            caption.textContent = '';
            continue;
        }

        caption.textContent = length.toLocaleString('en-US') + ' ' + detail.config.charactersLabel;
    }
};

// /////////////////////////////////////////////////////////////////////////////

// How the two sides share the pane - the remembered share put back on every
// opening, the default an even split
detail.applySplit = function(split) {
    var kept = window.localStorage.getItem(detail.config.splitStorageKey);
    var percent = detail.config.splitDefaultPercent;

    if (kept !== null) {
        percent = Number(kept);
    }

    split.style.setProperty('--message-flow-detail-split', percent + '%');
};

// /////////////////////////////////////////////////////////////////////////////

// The bar between the two sides - a press and a pull shares the pane's width
// between the request and the reply, neither side ever pushed below its least
// share. Wired once, through the document, because the bar itself is built
// anew with every opened node.
detail.wireSplit = function() {
    var config = detail.config;

    var isPressed = false;
    var split = null;
    var splitBar = null;

    document.addEventListener('mousedown', function(event) {

        // Only the main button grabs the bar
        if (event.button !== 0) {
            return;
        }

        if (!event.target.classList.contains('message-flow-detail-split-bar')) {
            return;
        }

        isPressed = true;
        splitBar = event.target;
        split = splitBar.parentElement;

        splitBar.classList.add('message-flow-detail-splitting');

        // The pull must not start selecting the page's text
        event.preventDefault();
    });

    window.addEventListener('mousemove', function(event) {
        if (!isPressed) {
            return;
        }

        var rect = split.getBoundingClientRect();
        var percent = (event.clientX - rect.left) / rect.width * 100;

        if (percent < config.splitMinPercent) {
            percent = config.splitMinPercent;
        }

        if (percent > 100 - config.splitMinPercent) {
            percent = 100 - config.splitMinPercent;
        }

        split.style.setProperty('--message-flow-detail-split', percent + '%');
        window.localStorage.setItem(config.splitStorageKey, String(Math.round(percent)));
    });

    window.addEventListener('mouseup', function() {
        if (isPressed) {
            isPressed = false;
            splitBar.classList.remove('message-flow-detail-splitting');
        }
    });
};

// /////////////////////////////////////////////////////////////////////////////

// With nothing picked, the pane stands where it always stands and says what
// it is waiting for
detail.hide = function() {
    var host = detail.host();

    detail.openDetail = null;

    host.textContent = '';

    var hint = document.createElement('div');
    hint.className = 'message-flow-detail-hint';
    hint.textContent = detail.config.hint;
    host.appendChild(hint);
};

// /////////////////////////////////////////////////////////////////////////////

// The bar between the drawing and the pane - a press on it and a pull shares
// the page between the two, neither side ever pushed below what it needs
detail.wireResize = function() {
    var config = detail.config;

    var page = document.querySelector(config.pageSelector);
    var bar = document.getElementById(config.resizeBarId);
    var host = detail.host();

    var isPressed = false;
    var startPointerY = 0;
    var startHeight = 0;

    bar.addEventListener('mousedown', function(event) {

        // Only the main button grabs the bar
        if (event.button !== 0) {
            return;
        }

        isPressed = true;
        startPointerY = event.clientY;
        startHeight = host.offsetHeight;

        bar.classList.add('message-flow-resizing');

        // The pull must not start selecting the page's text
        event.preventDefault();
    });

    window.addEventListener('mousemove', function(event) {
        if (!isPressed) {
            return;
        }

        // Pulling the bar up grows the pane by as much as the pointer travelled
        var height = startHeight + (startPointerY - event.clientY);

        // Neither side gives up the least room it needs
        var maxHeight = page.clientHeight - config.canvasMinHeight;

        // A pane too low to read anything in is shut all the way rather than
        // left ajar, which is the snap - between shut and the least height it
        // can be read at there is nothing to stand at
        if (height < config.detailSnapHeight) {
            height = 0;
        }
        else if (height < config.detailMinHeight) {
            height = config.detailMinHeight;
        }

        if (height > maxHeight) {
            height = maxHeight;
        }

        // With no height the pane is fully gone, its border included - a shut
        // pane must not linger as a seam over the page's bottom edge
        page.classList.toggle('message-flow-detail-shut', height === 0);

        page.style.setProperty('--message-flow-detail-height', height + 'px');
    });

    window.addEventListener('mouseup', function() {
        if (isPressed) {
            isPressed = false;
            bar.classList.remove('message-flow-resizing');
        }
    });
};

// /////////////////////////////////////////////////////////////////////////////

detail.init = function() {
    detail.wireResize();
    detail.wireSplit();
    detail.hide();
};

// /////////////////////////////////////////////////////////////////////////////

// The panel's own handler has already put the clicked tab in front by the time
// this one runs, so all that is left is saying how much text the tab holds
$(document).on('click', '#message-flow-detail .dashboard-payload-tab', function() {
    detail.updateCaption();
});

// /////////////////////////////////////////////////////////////////////////////

})(jQuery);
