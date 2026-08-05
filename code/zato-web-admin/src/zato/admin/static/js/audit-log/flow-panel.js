

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

    // What the lines standing open are called in the address bar, so a link to the page is a
    // link to the flow as the reader left it, and what separates them there
    stepURLKey: 'step',
    stepSeparator: ',',

    // How much of a message the panel shows before it stops
    previewLineCount: 24,

    fullMessageLabel: 'Full message',

    // What the panel says about the event, each one left out when the event has nothing to
    // put there and when the line above it already said it
    cidLabel: 'CID',
    controlIdLabel: 'Control id',
    correlIdLabel: 'Correlation id',
    endpointLabel: 'Endpoint',
    statusLabel: 'Status',
    classificationLabel: 'Classification',
    durationLabel: 'Duration',
    sizeLabel: 'Size',

    // What a message too long to show whole says about how much of it is on the screen
    charactersLabel: 'characters',
    firstOfLabel: 'First',
    ofLabel: 'of'
};

// /////////////////////////////////////////////////////////////////////////////

// One fact of the event, left out when the event has nothing to put there and when the line
// the panel hangs under has already said it. `searchValue` is what its Search asks the list
// for, empty when no Search is to be offered.
panel.pushFact = function(facts, rowModel, label, value, searchValue) {
    if (value === '') {
        return;
    }

    if (value === rowModel.headline) {
        return;
    }

    facts.push({label: label, value_html: flow.escapeHTML(value), copy_value: value,
        search_value: searchValue});
};

// /////////////////////////////////////////////////////////////////////////////

panel.facts = function(rowModel) {
    var config = panel.config;
    var facts = [];

    // What the event is named by is what other events are found by, so each of these is offered
    // for the list to be asked for
    panel.pushFact(facts, rowModel, config.cidLabel, rowModel.cid, rowModel.cid);
    panel.pushFact(facts, rowModel, config.controlIdLabel, rowModel.msgId, rowModel.msgId);
    panel.pushFact(facts, rowModel, config.correlIdLabel, rowModel.correlId, rowModel.correlId);
    panel.pushFact(facts, rowModel, config.endpointLabel, rowModel.endpoint, rowModel.endpoint);
    panel.pushFact(facts, rowModel, config.statusLabel, rowModel.status, rowModel.status);
    panel.pushFact(facts, rowModel, config.classificationLabel, rowModel.classification,
        rowModel.classification);

    // An event that took no measurable time is one nothing was timed for. What it was measured
    // with is no way of finding another event, so neither of these two offers a Search.
    if (rowModel.durationMs > 0) {
        var durationText = kit.format_duration_ms(rowModel.durationMs);
        panel.pushFact(facts, rowModel, config.durationLabel, durationText, '');
    }

    if (rowModel.size > 0) {
        var sizeText = kit.format_number_full(rowModel.size);
        panel.pushFact(facts, rowModel, config.sizeLabel, sizeText, '');
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

panel.bodyBarHTML = function(kinds) {
    var config = panel.config;

    var html = '<div class="audit-log-flow-body-bar">';

    // An event that stored one body has nothing to choose between, so it is shown rather
    // than offered
    if (kinds.length > 1) {
        for (var kindIndex = 0; kindIndex < kinds.length; kindIndex++) {
            var kind = kinds[kindIndex];
            var activeClass = kindIndex === 0 ? ' dashboard-panel-action-badge-active' : '';

            html += '<span class="dashboard-panel-action-badge dashboard-panel-action-badge-dark ' +
                'audit-log-flow-body-kind' + activeClass + '" data-kind="' + kind.kind + '">' +
                kind.label + '</span>';
        }
    }

    html += '<span class="audit-log-flow-body-caption"></span>';

    // Only the top of the message is on the screen here, so the whole of it is one click away
    html += '<span class="audit-log-flow-body-actions">';
    html += '<span class="dashboard-panel-action-badge dashboard-panel-action-badge-dark ' +
        'audit-log-flow-copy-body">' + flow.config.copyLabel + '</span>';
    html += '<span class="dashboard-panel-action-badge dashboard-panel-action-badge-dark ' +
        'audit-log-flow-full-message">' + config.fullMessageLabel + '</span>';
    html += '</span>';

    html += '</div>';

    return html;
};

// /////////////////////////////////////////////////////////////////////////////

panel.contentHTML = function(rowModel) {
    var facts = panel.facts(rowModel);
    var kinds = panel.bodyKinds(rowModel);

    var html = kit.fact_rows.render(facts, flow.config.darkVariant);

    // Which body is on the screen is the body's own business, since with a single one there
    // is no badge to read it off
    html += '<div class="audit-log-flow-body" data-kind="' + kinds[0].kind + '">';
    html += panel.bodyBarHTML(kinds);
    html += '<pre class="audit-log-flow-body-text"></pre>';
    html += '</div>';

    return html;
};

// /////////////////////////////////////////////////////////////////////////////

// How much of the message is on the screen, said only by a message that did not fit on it -
// a message shown whole is its own caption
panel.captionText = function(shownLength, totalLength) {
    var config = panel.config;

    if (shownLength >= totalLength) {
        return '';
    }

    var shownText = kit.format_number_full(shownLength);
    var totalText = kit.format_number_full(totalLength) + ' ' + config.charactersLabel;

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

// The lines standing open, in the order they were opened, written where a link to the page
// will carry them. With any of them open the rest of the flow steps back, the same way the
// scheduler's run log does it, so what is open is what is read.
panel.writeOpenSteps = function() {
    var openSteps = [];

    flow.host().find(flow.config.panelSelector + '.expanded').each(function() {
        openSteps.push($(this).attr('data-step'));
    });

    flow.host().find('.audit-log-flow').toggleClass('detail-dimmed', openSteps.length > 0);

    kit.url_state.replace({step: openSteps.join(panel.config.stepSeparator)});
};

// /////////////////////////////////////////////////////////////////////////////

// Everything the reader has opened, closed in one go - and with nothing open any longer,
// every line reads at full strength again
panel.collapse = function() {
    var $host = flow.host();

    $host.find(flow.config.panelSelector).removeClass('expanded');
    $host.find(flow.config.lineSelector).attr('aria-expanded', 'false');

    $host.find('.audit-log-flow').removeClass('detail-dimmed');

    kit.url_state.replace({step: ''});
};

// /////////////////////////////////////////////////////////////////////////////

// A line opens on top of whatever else is open, so two events of a flow are read side by side
// rather than one after the other, and opens closed when it is already open
panel.expand = function(eventId) {
    var $host = flow.host();
    var $line = $host.find(flow.config.lineSelector + '[data-step="' + eventId + '"]');

    if (!$line.length) {
        return;
    }

    var $panel = panel.of(eventId);

    if ($panel.hasClass('expanded')) {
        $panel.removeClass('expanded');
        $line.attr('aria-expanded', 'false');

        panel.writeOpenSteps();
        return;
    }

    // A panel is filled the first time it is opened and keeps what it was given after that
    if (!$panel.data('flow_panel_built')) {
        var rowModel = flow.rowById(eventId);

        $panel.find('.detail-panel-body').html(panel.contentHTML(rowModel));
        $panel.data('flow_panel_built', true);
    }

    $panel.addClass('expanded');
    $line.attr('aria-expanded', 'true');

    var $body = $panel.find('.audit-log-flow-body');
    panel.loadBody($panel, $body.attr('data-kind'));

    panel.writeOpenSteps();
};

// /////////////////////////////////////////////////////////////////////////////

// A link naming lines opens on those of them the flow still holds
panel.restoreStep = function() {
    var wanted = kit.url_state.get(panel.config.stepURLKey);

    if (wanted === null) {
        return;
    }

    if (wanted === '') {
        return;
    }

    var eventIds = wanted.split(panel.config.stepSeparator);

    for (var stepIndex = 0; stepIndex < eventIds.length; stepIndex++) {
        var eventId = eventIds[stepIndex];

        if (flow.rowById(eventId) !== null) {
            panel.expand(eventId);
        }
    }
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
        var kind = $kind.attr('data-kind');

        $panel.find('.audit-log-flow-body-kind').removeClass('dashboard-panel-action-badge-active');
        $kind.addClass('dashboard-panel-action-badge-active');

        $panel.find('.audit-log-flow-body').attr('data-kind', kind);

        panel.loadBody($panel, kind);
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
};

// /////////////////////////////////////////////////////////////////////////////

})(jQuery);
