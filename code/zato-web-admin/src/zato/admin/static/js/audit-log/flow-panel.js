

// /////////////////////////////////////////////////////////////////////////////

// What one line of a flow opens into - the facts the line itself had no room for, and the top
// of the message the event carried, fetched the first time it is asked for. The whole message
// and its parsed view are read where they already are rather than drawn a second time here.

$.fn.zato.audit_log.flow.panel = {};

// /////////////////////////////////////////////////////////////////////////////

(function($) {

var kit = $.fn.zato.dashboard_kit;
var listing = $.fn.zato.audit_log.listing;
var flow = $.fn.zato.audit_log.flow;
var panel = flow.panel;

panel.config = {

    // What the line standing open is called in the address bar, so a link to the page is a link
    // to that line of that event's flow
    stepURLKey: 'step',

    // The variant of the fact rows the panel sets out, it being inside a dark frame
    factVariant: 'dark',

    // How much of a message the panel shows before it stops
    previewLineCount: 24,

    fullMessageLabel: 'Full message',
    openInDataLabel: 'Open in Data tab',

    // What the panel says about the event, each one left out when the event has nothing to
    // put there and when the line above it already said it
    cidLabel: 'CID',
    msgIdLabel: 'Message id',
    correlIdLabel: 'Correlation id',
    endpointLabel: 'Endpoint',
    statusLabel: 'Status',
    classificationLabel: 'Classification',
    serverLabel: 'Server',
    durationLabel: 'Duration',
    sizeLabel: 'Size',

    // How much of the message the panel is showing, out of how much there is
    charactersLabel: 'characters',
    wholeBodyLabel: 'Whole message',
    firstOfLabel: 'First',
    ofLabel: 'of'
};

// /////////////////////////////////////////////////////////////////////////////

// Which line of the flow stands open, and nothing when none of them does
panel.openStep = null;

// /////////////////////////////////////////////////////////////////////////////

// One fact of the event, left out when the event has nothing to put there and when the line
// the panel hangs under has already said it
panel.pushFact = function(facts, rowModel, label, value) {
    if (value === '') {
        return;
    }

    if (value === rowModel.headline) {
        return;
    }

    facts.push({label: label, value_html: flow.escapeHTML(value), copy_value: value});
};

// /////////////////////////////////////////////////////////////////////////////

panel.facts = function(rowModel) {
    var config = panel.config;
    var facts = [];

    panel.pushFact(facts, rowModel, config.cidLabel, rowModel.cid);
    panel.pushFact(facts, rowModel, config.msgIdLabel, rowModel.msgId);
    panel.pushFact(facts, rowModel, config.correlIdLabel, rowModel.correlId);
    panel.pushFact(facts, rowModel, config.endpointLabel, rowModel.endpoint);
    panel.pushFact(facts, rowModel, config.statusLabel, rowModel.status);
    panel.pushFact(facts, rowModel, config.classificationLabel, rowModel.classification);
    panel.pushFact(facts, rowModel, config.serverLabel, rowModel.serverName);

    // An event that took no measurable time is one nothing was timed for
    if (rowModel.durationMs > 0) {
        var durationText = kit.format_duration_ms(rowModel.durationMs);
        panel.pushFact(facts, rowModel, config.durationLabel, durationText);
    }

    if (rowModel.size > 0) {
        var sizeText = kit.format_number_full(rowModel.size);
        panel.pushFact(facts, rowModel, config.sizeLabel, sizeText);
    }

    return facts;
};

// /////////////////////////////////////////////////////////////////////////////

// Which of the event's message bodies the panel offers, the first of them being the one
// it opens on
panel.bodyKinds = function(rowModel) {
    var labels = listing.config.bodyKindLabels;
    var out = [];

    for (var kindIndex = 0; kindIndex < rowModel.bodyKinds.length; kindIndex++) {
        var kind = rowModel.bodyKinds[kindIndex];

        out.push({kind: kind, label: labels[kind]});
    }

    // A source that keeps its payload in the event row itself names no kind at all
    if (out.length === 0) {
        out.push({kind: '', label: listing.config.rawTabLabel});
    }

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

panel.bodyBarHTML = function(rowModel) {
    var config = panel.config;
    var kinds = panel.bodyKinds(rowModel);

    var html = '<div class="audit-log-flow-body-bar">';

    for (var kindIndex = 0; kindIndex < kinds.length; kindIndex++) {
        var kind = kinds[kindIndex];
        var activeClass = kindIndex === 0 ? ' audit-log-flow-body-kind-active' : '';

        html += '<span class="dashboard-panel-action-badge dashboard-panel-action-badge-dark ' +
            'audit-log-flow-body-kind' + activeClass + '" data-kind="' + kind.kind + '">' +
            kind.label + '</span>';
    }

    html += '<span class="audit-log-flow-body-caption"></span>';

    // The whole message is read in the overlay, and the whole of it beside its parsed view is
    // read in the pane's own Data tab
    html += '<span class="audit-log-flow-body-actions">';
    html += '<span class="dashboard-panel-action-badge dashboard-panel-action-badge-dark ' +
        'audit-log-flow-copy-body">' + flow.config.copyLabel + '</span>';
    html += '<span class="dashboard-panel-action-badge dashboard-panel-action-badge-dark ' +
        'audit-log-flow-full-message">' + config.fullMessageLabel + '</span>';
    html += '<span class="dashboard-panel-action-badge dashboard-panel-action-badge-dark ' +
        'audit-log-flow-open-data">' + config.openInDataLabel + '</span>';
    html += '</span>';

    html += '</div>';

    return html;
};

// /////////////////////////////////////////////////////////////////////////////

panel.contentHTML = function(rowModel) {
    var facts = panel.facts(rowModel);

    var html = kit.fact_rows.render(facts, panel.config.factVariant);

    html += '<div class="audit-log-flow-body">';
    html += panel.bodyBarHTML(rowModel);
    html += '<pre class="audit-log-flow-body-text"></pre>';
    html += '</div>';

    return html;
};

// /////////////////////////////////////////////////////////////////////////////

// How much of the message is on the screen, out of how much of it there is
panel.captionText = function(shownLength, totalLength) {
    var config = panel.config;
    var totalText = kit.format_number_full(totalLength) + ' ' + config.charactersLabel;

    if (shownLength >= totalLength) {
        return config.wholeBodyLabel + ', ' + totalText;
    }

    var shownText = kit.format_number_full(shownLength);

    var out = config.firstOfLabel + ' ' + shownText + ' ' + config.ofLabel + ' ' + totalText;

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// The top of the message, cut to the lines the panel has room for
panel.cutToLines = function(text) {
    var lines = text.split('\n');
    var lineCount = panel.config.previewLineCount;

    if (lines.length <= lineCount) {
        return text;
    }

    var out = lines.slice(0, lineCount).join('\n');

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// One body of one event, asked for the first time the kind holding it is chosen and kept
// from then on, because the payload of an event does not change
panel.loadBody = function($panel, kind) {
    var eventId = $panel.attr('data-step');
    var $text = $panel.find('.audit-log-flow-body-text');
    var $caption = $panel.find('.audit-log-flow-body-caption');

    var loaded = $panel.data('flow_body_loaded');

    if (loaded === undefined) {
        loaded = {};
        $panel.data('flow_body_loaded', loaded);
    }

    // A kind read once is read from what it left behind rather than from the server again
    if (loaded[kind] !== undefined) {
        $text.html(loaded[kind].html);
        $caption.text(loaded[kind].caption);
        return;
    }

    var token = $panel.data('flow_body_token');

    if (token === undefined) {
        token = 0;
    }

    token = token + 1;
    $panel.data('flow_body_token', token);

    // Whatever the panel is holding stays there while the next body is on its way, and the
    // wait is only announced once it is long enough to be worth announcing
    var spinnerTimer = setTimeout(function() {
        if ($panel.data('flow_body_token') !== token) {
            return;
        }

        $text.html(kit.spinner_label_html());
    }, flow.config.spinnerDelayMs);

    // Only the top of the message is asked for, since only the top of it is shown
    listing.fetchDetails(eventId, kind, true, function(details) {

        // A body of a kind the panel has since been switched away from is not shown at all
        if ($panel.data('flow_body_token') !== token) {
            return;
        }

        clearTimeout(spinnerTimer);

        var shown = panel.cutToLines(details.data);

        loaded[kind] = {
            html: kit.syntax_highlight(shown),
            caption: panel.captionText(shown.length, details.total_len)
        };

        $text.html(loaded[kind].html);
        $caption.text(loaded[kind].caption);
    });
};

// /////////////////////////////////////////////////////////////////////////////

panel.of = function(eventId) {
    var out = flow.host().find(flow.config.panelSelector + '[data-step="' + eventId + '"]');

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

panel.closeAll = function() {
    var $host = flow.host();

    $host.find(flow.config.panelSelector).removeClass('expanded');
    $host.find(flow.config.lineSelector).attr('aria-expanded', 'false');
};

// /////////////////////////////////////////////////////////////////////////////

panel.collapse = function() {
    panel.closeAll();

    panel.openStep = null;
    kit.url_state.replace({step: ''});
};

// /////////////////////////////////////////////////////////////////////////////

// One line at a time stands open, so the flow stays a flow rather than a stack of panels
panel.expand = function(eventId) {
    var $host = flow.host();
    var $line = $host.find(flow.config.lineSelector + '[data-step="' + eventId + '"]');

    if (!$line.length) {
        return;
    }

    var $panel = panel.of(eventId);

    // The line already open is the line being closed
    if ($panel.hasClass('expanded')) {
        panel.collapse();
        return;
    }

    panel.closeAll();

    // A panel is filled the first time it is opened and keeps what it was given after that
    if (!$panel.data('flow_panel_built')) {
        var rowModel = flow.rowById(eventId);

        $panel.find('.detail-panel-body').html(panel.contentHTML(rowModel));
        $panel.data('flow_panel_built', true);
    }

    $panel.addClass('expanded');
    $line.attr('aria-expanded', 'true');

    var $kind = $panel.find('.audit-log-flow-body-kind-active');
    panel.loadBody($panel, $kind.attr('data-kind'));

    panel.openStep = eventId;
    kit.url_state.replace({step: eventId});
};

// /////////////////////////////////////////////////////////////////////////////

// A link naming a line opens on that line, and a flow that no longer holds it opens closed
panel.restoreStep = function() {
    var wanted = kit.url_state.get(panel.config.stepURLKey);

    if (wanted === null) {
        return;
    }

    if (wanted === '') {
        return;
    }

    if (flow.rowById(wanted) === null) {
        return;
    }

    panel.expand(wanted);
};

// /////////////////////////////////////////////////////////////////////////////

// One step through the flow from wherever the focus stands, so a flow is walked without
// the pointer
panel.moveBy = function($line, step) {
    var $lines = flow.host().find(flow.config.lineSelector);
    var lineIndex = $lines.index($line) + step;

    if (lineIndex < 0) {
        return;
    }

    if (lineIndex > $lines.length - 1) {
        return;
    }

    $lines.eq(lineIndex).trigger('focus');
};

// /////////////////////////////////////////////////////////////////////////////

panel.onLineKeydown = function(event) {
    var $line = $(this);

    if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        panel.expand($line.attr('data-step'));
    }

    // The list of events answers to the same two keys, so a flow being walked keeps them
    // to itself while the focus stands on one of its lines
    else if (event.key === 'ArrowDown') {
        event.preventDefault();
        event.stopPropagation();
        panel.moveBy($line, 1);
    }

    else if (event.key === 'ArrowUp') {
        event.preventDefault();
        event.stopPropagation();
        panel.moveBy($line, -1);
    }

    else if (event.key === 'Escape') {
        event.preventDefault();
        panel.collapse();
    }
};

// /////////////////////////////////////////////////////////////////////////////

panel.init = function() {
    var panelSelector = flow.config.panelSelector;

    // The keys a line answers to are bound above the list rather than on the page, so nothing
    // outside the listing is walked by them
    var $listing = $(listing.config.host);

    $listing.on('keydown', flow.config.lineSelector, panel.onLineKeydown);

    // Each kind of body the event stored is read in its turn, and the one being read is
    // the one the panel says it is
    $(document).on('click', '.audit-log-flow-body-kind', function() {
        var $kind = $(this);
        var $panel = $kind.closest(panelSelector);

        $panel.find('.audit-log-flow-body-kind').removeClass('audit-log-flow-body-kind-active');
        $kind.addClass('audit-log-flow-body-kind-active');

        panel.loadBody($panel, $kind.attr('data-kind'));
    });

    $(document).on('click', '.audit-log-flow-copy-body', function() {
        var $panel = $(this).closest(panelSelector);
        var text = $panel.find('.audit-log-flow-body-text').text();

        kit.copy_to_clipboard(this, text);
    });

    $(document).on('click', '.audit-log-flow-full-message', function() {
        var $panel = $(this).closest(panelSelector);
        var rowModel = flow.rowById($panel.attr('data-step'));

        $.fn.zato.audit_log.openMessageOverlay(rowModel.id, rowModel.cid);
    });

    $(document).on('click', '.audit-log-flow-open-data', function() {
        var $panel = $(this).closest(panelSelector);
        var eventId = $panel.attr('data-step');

        // An event of this very page is selected in the list and read in its Data tab, and one
        // that belongs to another object is opened on its own page instead
        if (listing.modelById(eventId) === null) {
            var rowModel = flow.rowById(eventId);
            window.location.href = flow.eventURL(rowModel);
            return;
        }

        // The tab is switched before the event is, so that bringing the pane to the event asks
        // for the message rather than for a flow that is about to be left behind
        listing.tabs.set_tab(listing.config.dataTab, true);
        listing.panes.select(eventId);
    });
};

// /////////////////////////////////////////////////////////////////////////////

})(jQuery);
