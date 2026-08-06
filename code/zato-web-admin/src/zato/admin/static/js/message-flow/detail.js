
// /////////////////////////////////////////////////////////////////////////////

// Message flow - the pane under the drawing. One constant size whatever it is
// holding, so opening, switching and closing nodes never moves anything around
// it. A clicked node's exchange opens here - one tab per event, each body
// fetched from the audit log the first time its tab is opened, the files an
// event carried offered over the bodies.

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

    // The word each kind of line wears, the same words the drawing writes
    directionLabels: {
        'in': 'IN',
        'out': 'OUT',
        'none': 'SYS',
        'view': 'VIEW'
    },

    // The one event type that is a person reading rather than a message moving
    viewEventType: 'content-viewed',

    // The outcome worn in the good ink - every other reported outcome reads bad
    goodOutcome: 'ok',

    // How small either side of the split may get when the bar between the
    // drawing and the pane is pulled
    detailMinHeight: 120,
    canvasMinHeight: 160
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

// The ink a line's direction is written in, on the pane's tabs
detail.directionOf = function(model) {
    var config = detail.config;

    if (model.eventType === config.viewEventType) {
        return 'view';
    }

    return model.direction;
};

// /////////////////////////////////////////////////////////////////////////////

// What one tab of the pane wears - the direction in its own ink, the event's
// id in amber, and an outcome in the outcome's own colour. The plain label
// stays beside the markup, being what a tab is told apart by.
detail.tabOf = function(model) {
    var config = detail.config;

    var direction = detail.directionOf(model);
    var directionLabel = config.directionLabels[direction];

    var labelHtml = '<span class="message-flow-detail-tab-direction-' + direction + '">' +
        directionLabel + '</span>';
    labelHtml += '<span class="message-flow-detail-tab-id">' + model.id + '</span>';

    // An event whose word is an outcome carries it on the tab, so a failed leg
    // says so before it is even opened
    if (model.outcome !== '') {
        var outcomeKind = model.outcome === config.goodOutcome ? 'good' : 'bad';

        labelHtml += '<span class="message-flow-detail-tab-outcome-' + outcomeKind + '">' +
            detail.escapeHTML(model.outcome.toUpperCase()) + '</span>';
    }

    var out = {
        label: directionLabel + ' \u00b7 ' + model.id,
        label_html: labelHtml,
        eventId: model.id
    };

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// The pane brought to one exchange - the header, the files its events carried,
// and one tab per event, each body asked for the first time its tab is opened
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

    var controlId = document.createElement('span');
    controlId.className = 'message-flow-detail-control-id';
    controlId.textContent = page.state.controlId;
    meta.appendChild(controlId);

    var time = document.createElement('span');
    time.className = 'message-flow-detail-time';
    time.textContent = nodeDetail.time;
    meta.appendChild(time);

    // The files the events carried are asked about the moment the pane holds
    // them - an event carrying none keeps its strip's place empty
    var attachments = document.createElement('div');
    attachments.className = 'message-flow-detail-attachments';
    host.appendChild(attachments);

    var tabs = [];

    for (var modelIndex = 0; modelIndex < nodeDetail.models.length; modelIndex++) {
        var model = nodeDetail.models[modelIndex];

        tabs.push(detail.tabOf(model));

        var attachmentsHost = document.createElement('div');
        attachmentsHost.className = 'message-flow-detail-attachments-host';

        // The strip only fills in for the record it was asked about, which the
        // kit reads off the host itself
        attachmentsHost.setAttribute('data-attachments-id', model.id);
        attachments.appendChild(attachmentsHost);

        listing.loadAttachments(model, $(attachmentsHost));
    }

    var panelHost = document.createElement('div');
    panelHost.className = 'message-flow-detail-panel';
    host.appendChild(panelHost);

    var caption = document.createElement('div');
    caption.className = 'message-flow-detail-caption';
    host.appendChild(caption);

    // Each tab fetches its own body the first time it is opened - parsed when
    // the source's reader made sense of it, as it went down the wire otherwise
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

    detail.updateCaption();
};

// /////////////////////////////////////////////////////////////////////////////

// The words under the body - how much of it there is, in the same dim ink the
// thread's captions use, and nothing while the open body is still on its way
detail.updateCaption = function() {
    var host = detail.host();
    var caption = host.querySelector('.message-flow-detail-caption');

    // The pane may have been emptied while a body was on its way
    if (caption === null) {
        return;
    }

    var $openTab = $(host).find('.dashboard-payload-tab.dashboard-panel-action-badge-active');

    var tabs = $(host).find('.dashboard-payload').data('payload_tabs');
    var tab = tabs[parseInt($openTab.attr('data-tab-index'), 10)];

    var length = detail.bodyLengths[String(tab.eventId)];

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

        if (height < config.detailMinHeight) {
            height = config.detailMinHeight;
        }

        if (height > maxHeight) {
            height = maxHeight;
        }

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
