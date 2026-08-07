

// /////////////////////////////////////////////////////////////////////////////

// What one line of a flow opens into - the facts the line itself had no room for, and the
// message the event carried, read parsed or raw and cut to the panel's window until the
// whole of it is asked for, each body fetched the first time it is asked for.

$.fn.zato.audit_log.flow.panel = {};

// /////////////////////////////////////////////////////////////////////////////

(function($) {

var kit = $.fn.zato.dashboard_kit;
var listing = $.fn.zato.audit_log.listing;
var flow = $.fn.zato.audit_log.flow;
var panel = flow.panel;

panel.config = {

    // What the lines standing open are called in the address bar, so a link to the page is a
    // link to the flow as the reader left it, and what separates them there. Within one entry,
    // the choices made on that panel follow the event id - the view when it is not parsed, the
    // kind when it is not the first one, and the word for the whole body being on the screen -
    // so the link carries not only what is open but how each open thing is being read.
    stepURLKey: 'step',
    stepSeparator: ',',
    stepStateSeparator: '.',
    wholeFlag: 'all',

    // How much of a message the panel shows before it stops
    previewLineCount: 24,

    // The way to the rest of a message the panel cut short
    showAllLabel: 'Show all',

    // What the panel says about the event, each one left out when the event has nothing to
    // put there and when the line above it already said it
    cidLabel: 'CID',
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
// for, empty when no Search is to be offered. `valueHTML` is pre-rendered display markup,
// already escaped by its maker, for values with markup of their own inside.
panel.pushFact = function(facts, rowModel, label, value, searchValue, valueHTML) {
    if (value === '') {
        return;
    }

    if (value === rowModel.headline) {
        return;
    }

    if (valueHTML === undefined) {
        valueHTML = flow.escapeHTML(value);
    }

    facts.push({label: label, value_html: valueHTML, copy_value: value,
        search_value: searchValue});
};

// /////////////////////////////////////////////////////////////////////////////

panel.facts = function(rowModel) {
    var config = panel.config;
    var facts = [];

    // What the event is named by is what other events are found by, so each of these is offered
    // for the list to be asked for. The name of the source's own identity - control id,
    // message id - comes from the source's presenter.
    var presenter = $.fn.zato.audit_log.presenterFor(rowModel.source);

    panel.pushFact(facts, rowModel, config.cidLabel, rowModel.cid, rowModel.cid);
    panel.pushFact(facts, rowModel, presenter.identityLabel, rowModel.msgId, rowModel.msgId);
    panel.pushFact(facts, rowModel, config.correlIdLabel, rowModel.correlId, rowModel.correlId);

    // The endpoint is called by the word its own source has for it - the service a channel
    // hands its messages to, the folder a mailbox was read from - the plain word otherwise
    var endpointLabel = $.fn.zato.audit_log.config.endpointLabels[rowModel.source];

    if (endpointLabel === undefined) {
        endpointLabel = config.endpointLabel;
    }

    panel.pushFact(facts, rowModel, endpointLabel, rowModel.endpoint, rowModel.endpoint,
        kit.http_method.html(rowModel.endpoint));
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
    var listingConfig = listing.config;

    var html = '<div class="audit-log-flow-body-bar">';

    // How the body is read - as its source's reader parsed it, which is what it opens on
    // everywhere, or as it went down the wire - the same two views the Data tab offers
    html += '<span class="dashboard-panel-action-badge dashboard-panel-action-badge-dark ' +
        'audit-log-flow-body-view dashboard-panel-action-badge-active" data-view="' +
        listingConfig.parsedView + '">' + listingConfig.parsedTabLabel + '</span>';
    html += '<span class="dashboard-panel-action-badge dashboard-panel-action-badge-dark ' +
        'audit-log-flow-body-view" data-view="' + listingConfig.rawView + '">' +
        listingConfig.rawTabLabel + '</span>';

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

    // The rest of a message cut short is offered right beside the words saying how much of
    // it is shown, as quiet underlined words rather than another button
    html += '<span class="audit-log-flow-show-all">' + config.showAllLabel + '</span>';

    html += '<span class="audit-log-flow-body-actions">';
    html += '<span class="dashboard-panel-action-badge dashboard-panel-action-badge-dark ' +
        'audit-log-flow-copy-body">' + flow.config.copyLabel + '</span>';
    html += '</span>';

    html += '</div>';

    return html;
};

// /////////////////////////////////////////////////////////////////////////////

panel.contentHTML = function(rowModel) {
    var facts = panel.facts(rowModel);
    var kinds = panel.bodyKinds(rowModel);

    var html = kit.fact_rows.render(facts, flow.config.darkVariant);

    // The files the event carried, filled in once their metadata has arrived and only
    // when there are any at all
    html += '<div class="' + listing.config.attachmentsHostClass + '" data-attachments-id="' +
        rowModel.id + '"></div>';

    // Which body is on the screen and how it is being read are the body's own business,
    // since with a single body there is no kind badge to read the first one off - and which
    // kind it woke up on stays written down, being what the address bar leaves unsaid
    html += '<div class="audit-log-flow-body" data-kind="' + kinds[0].kind +
        '" data-default-kind="' + kinds[0].kind + '" data-view="' + listing.config.parsedView + '">';
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

// One loaded body put on the screen - its text, its caption, and the way to the whole of it,
// reading as itself again and offered only while less than the whole of it is what is shown
panel.showLoaded = function($panel, entry) {
    $panel.find('.audit-log-flow-body-text').html(entry.html);
    $panel.find('.audit-log-flow-body-caption').text(entry.caption);

    var $showAll = $panel.find('.audit-log-flow-show-all');

    $showAll.removeClass('audit-log-flow-show-all-loading');
    $showAll.text(panel.config.showAllLabel);
    $showAll.toggleClass('audit-log-flow-show-all-absent', entry.caption === '');
};

// /////////////////////////////////////////////////////////////////////////////

// One body of one event, read the way the panel's body element says it is to be read - which
// kind, which view, and whether the whole of it. A body read one way once is read from what
// it left behind rather than from the server again, because the payload of an event does
// not change.
panel.loadBody = function($panel) {
    var listingConfig = listing.config;
    var eventId = $panel.attr('data-step');
    var $body = $panel.find('.audit-log-flow-body');

    var kind = $body.attr('data-kind');
    var view = $body.attr('data-view');
    var isWhole = $body.attr('data-whole') === '1';

    var loaded = $panel.data('flow_body_loaded');

    if (loaded === undefined) {
        loaded = {};
        $panel.data('flow_body_loaded', loaded);
    }

    var loadedKey = view + '|' + kind + '|' + isWhole;

    if (loaded[loadedKey] !== undefined) {
        panel.showLoaded($panel, loaded[loadedKey]);
        return;
    }

    var token = $panel.data('flow_body_token');

    if (token === undefined) {
        token = 0;
    }

    token = token + 1;
    $panel.data('flow_body_token', token);

    // Whether this body is cut short is not known until it arrives, so nothing offers the
    // whole of it in the meantime - unless it is the offer itself being answered, which
    // stands where it is, already turned into the wait it announces
    $panel.find('.audit-log-flow-show-all:not(.audit-log-flow-show-all-loading)')
        .addClass('audit-log-flow-show-all-absent');

    // Whatever the panel is holding stays there while the next body is on its way, and the
    // wait is only announced once it is long enough to be worth announcing
    var spinnerTimer = setTimeout(function() {
        if ($panel.data('flow_body_token') !== token) {
            return;
        }

        // A wait already announced beside the caption is not announced over the body too -
        // what the body holds stays put, which is the point of announcing it there
        if ($panel.find('.audit-log-flow-show-all').hasClass('audit-log-flow-show-all-loading')) {
            return;
        }

        $panel.find('.audit-log-flow-body-text').html(kit.spinner_label_html());
    }, flow.config.spinnerDelayMs);

    // Only the raw view shown short asks for only the top of the message - the parsed one
    // is built by the server out of the whole message, and Show all asks for all of it
    var isPreview = view === listingConfig.rawView && !isWhole;

    listing.fetchDetails(eventId, kind, isPreview, function(details) {

        // A body the panel has since been switched away from is not shown at all
        if ($panel.data('flow_body_token') !== token) {
            return;
        }

        clearTimeout(spinnerTimer);

        var text = details.data;
        var totalLength = details.total_len;

        // A payload this source's own reader could make nothing of is shown as it stands
        // rather than as a blank panel - the same fallback the Data tab makes
        if (view === listingConfig.parsedView) {
            if (details.parsed !== '') {
                text = details.parsed;
            }

            totalLength = text.length;
        }

        var shown = text;

        // The body is cut to the panel's window unless the whole of it was asked for
        if (!isWhole) {
            shown = panel.cutToLines(text);
        }

        loaded[loadedKey] = {
            html: kit.syntax_highlight(shown),
            caption: panel.captionText(shown.length, totalLength)
        };

        panel.showLoaded($panel, loaded[loadedKey]);
    });
};

// /////////////////////////////////////////////////////////////////////////////

panel.of = function(eventId) {
    var out = flow.host().find(flow.config.panelSelector + '[data-step="' + eventId + '"]');

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// One open panel's entry in the address bar - the event id, followed only by the choices
// made on it that a fresh panel would not make by itself, so an untouched one is its id alone
panel.stepEntry = function($panel) {
    var config = panel.config;
    var $body = $panel.find('.audit-log-flow-body');

    var entry = $panel.attr('data-step');

    if ($body.attr('data-view') !== listing.config.parsedView) {
        entry += config.stepStateSeparator + $body.attr('data-view');
    }

    if ($body.attr('data-kind') !== $body.attr('data-default-kind')) {
        entry += config.stepStateSeparator + $body.attr('data-kind');
    }

    if ($body.attr('data-whole') === '1') {
        entry += config.stepStateSeparator + config.wholeFlag;
    }

    return entry;
};

// /////////////////////////////////////////////////////////////////////////////

// The lines standing open, in the order they were opened and each read the way its reader
// left it, written where a link to the page will carry them. With any of them open the rest
// of the flow steps back, the same way the scheduler's run log does it, so what is open is
// what is read.
panel.writeOpenSteps = function() {
    var openSteps = [];

    flow.host().find(flow.config.panelSelector + '.expanded').each(function() {
        openSteps.push(panel.stepEntry($(this)));
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

// The choices a link made on one panel, put on it before its body is asked for - the badge
// of each choice lit the same as if it had been clicked
panel.applyState = function($panel, state) {
    var $body = $panel.find('.audit-log-flow-body');

    if (state.view !== '') {
        $body.attr('data-view', state.view);

        $panel.find('.audit-log-flow-body-view').removeClass('dashboard-panel-action-badge-active');
        $panel.find('.audit-log-flow-body-view[data-view="' + state.view + '"]')
            .addClass('dashboard-panel-action-badge-active');
    }

    if (state.kind !== '') {
        $body.attr('data-kind', state.kind);

        $panel.find('.audit-log-flow-body-kind').removeClass('dashboard-panel-action-badge-active');
        $panel.find('.audit-log-flow-body-kind[data-kind="' + state.kind + '"]')
            .addClass('dashboard-panel-action-badge-active');
    }

    if (state.whole) {
        $body.attr('data-whole', '1');
    }
};

// /////////////////////////////////////////////////////////////////////////////

// A line opens on top of whatever else is open, so two events of a flow are read side by side
// rather than one after the other, and opens closed when it is already open. A `state` comes
// only from a link being followed, carrying the choices the link's sender had made.
panel.expand = function(eventId, state) {
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

    // A panel is filled the first time it is opened and keeps what it was given after that,
    // and the files its event carried are asked about at the same moment
    if (!$panel.data('flow_panel_built')) {
        var rowModel = flow.rowById(eventId);

        $panel.find('.detail-panel-body').html(panel.contentHTML(rowModel));
        $panel.data('flow_panel_built', true);

        listing.loadAttachments(rowModel,
            $panel.find('.' + listing.config.attachmentsHostClass));
    }

    if (state !== undefined) {
        panel.applyState($panel, state);
    }

    $panel.addClass('expanded');
    $line.attr('aria-expanded', 'true');

    panel.loadBody($panel);

    panel.writeOpenSteps();
};

// /////////////////////////////////////////////////////////////////////////////

// A link naming lines opens on those of them the flow still holds, each one read the way
// the link says it was being read - the view, the kind and the whole body all put back
panel.restoreStep = function() {
    var config = panel.config;
    var wanted = kit.url_state.get(config.stepURLKey);

    if (wanted === null) {
        return;
    }

    if (wanted === '') {
        return;
    }

    var entries = wanted.split(config.stepSeparator);

    for (var stepIndex = 0; stepIndex < entries.length; stepIndex++) {
        var segments = entries[stepIndex].split(config.stepStateSeparator);
        var eventId = segments[0];

        if (flow.rowById(eventId) === null) {
            continue;
        }

        var state = {view: '', kind: '', whole: false};

        // Whatever follows the id names one choice each - a segment that is neither a view
        // nor the whole-body word can only be a kind
        for (var segmentIndex = 1; segmentIndex < segments.length; segmentIndex++) {
            var segment = segments[segmentIndex];

            if (segment === listing.config.rawView || segment === listing.config.parsedView) {
                state.view = segment;
            }
            else if (segment === config.wholeFlag) {
                state.whole = true;
            }
            else {
                state.kind = segment;
            }
        }

        panel.expand(eventId, state);
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

    // The keys a line answers to are bound above the flow rather than on the page, so nothing
    // outside it is walked by them
    var $flowHost = $(flow.config.host);

    $flowHost.on('keydown', flow.config.lineSelector, panel.onLineKeydown);

    // Each kind of body the event stored is read in its turn, and the one being read is
    // the one the panel says it is
    $(document).on('click', '.audit-log-flow-body-kind', function() {
        var $kind = $(this);
        var $panel = $kind.closest(panelSelector);

        $panel.find('.audit-log-flow-body-kind').removeClass('dashboard-panel-action-badge-active');
        $kind.addClass('dashboard-panel-action-badge-active');

        $panel.find('.audit-log-flow-body').attr('data-kind', $kind.attr('data-kind'));

        panel.loadBody($panel);
        panel.writeOpenSteps();
    });

    // A body is read raw or parsed the same way the Data tab reads it, and the view chosen
    // stays chosen as the panel's kinds are walked through
    $(document).on('click', '.audit-log-flow-body-view', function() {
        var $view = $(this);
        var $panel = $view.closest(panelSelector);

        $panel.find('.audit-log-flow-body-view').removeClass('dashboard-panel-action-badge-active');
        $view.addClass('dashboard-panel-action-badge-active');

        $panel.find('.audit-log-flow-body').attr('data-view', $view.attr('data-view'));

        panel.loadBody($panel);
        panel.writeOpenSteps();
    });

    // The rest of a message the panel cut short - the words themselves turn into the wait
    // being announced, staying where they stand so nothing on the panel moves, and only
    // after that is the whole body asked for. From here on this panel shows its bodies
    // whole, whichever kind and view of them is asked for.
    $(document).on('click', '.audit-log-flow-show-all', function() {
        var $link = $(this);
        var $panel = $link.closest(panelSelector);

        // A second click while the first is being answered has nothing more to ask for
        if ($link.hasClass('audit-log-flow-show-all-loading')) {
            return;
        }

        $link.addClass('audit-log-flow-show-all-loading');
        $link.html(kit.spinner_label_html());

        $panel.find('.audit-log-flow-body').attr('data-whole', '1');
        panel.writeOpenSteps();

        setTimeout(function() {
            panel.loadBody($panel);
        }, flow.config.spinnerDelayMs);
    });

    $(document).on('click', '.audit-log-flow-copy-body', function() {
        var $panel = $(this).closest(panelSelector);
        var text = $panel.find('.audit-log-flow-body-text').text();

        kit.copy_to_clipboard(this, text);
    });
};

// /////////////////////////////////////////////////////////////////////////////

})(jQuery);
