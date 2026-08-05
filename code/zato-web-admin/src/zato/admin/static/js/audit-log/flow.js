

// /////////////////////////////////////////////////////////////////////////////

// One event's whole flow - every event related to it on a line of its own, the newest first
// the way the list reads. The shape of a line and of the shell under it comes from the
// dashboard kit, what goes into them is the audit log's business, and what a line opens
// into is in flow-panel.js.

$.fn.zato.audit_log.flow = {};

// /////////////////////////////////////////////////////////////////////////////

(function($) {

var kit = $.fn.zato.dashboard_kit;
var listing = $.fn.zato.audit_log.listing;
var flow = $.fn.zato.audit_log.flow;

flow.config = {

    host: '#audit-log-pane-flow',
    lineSelector: '.audit-log-flow-line',
    panelSelector: '.audit-log-flow-panel',

    // What the line the flow was read from wears, so where the reader stands is never in doubt
    seedAccent: 'rgb(246, 166, 5)',

    // The stripe of an event that reports no outcome of its own - a message arriving is neither
    // a success nor a failure until something is done with it
    neutralStripe: '#5a5a72',

    // How long the flow and its panels wait for what they asked for before saying they are waiting
    spinnerDelayMs: 150,

    // The variant the direction tags and the fact rows wear, the flow being a dark frame
    darkVariant: 'dark',

    copyLabel: 'Copy',
    openLabel: 'Open',

    // What one relation of an event to the flow is called. The operation itself is left unnamed,
    // because a line of the same operation is what a flow is mostly made of - and so is sharing
    // a message id, which is why a line found by it wears no tag either.
    relationLabels: {
        'parent': 'Came out of',
        'child': 'Led to',
        'resubmit-of': 'Repeat of',
        'resubmitted-as': 'Repeated as'
    }
};

// /////////////////////////////////////////////////////////////////////////////

// The event whose flow is drawn and the events of it
flow.seedId = null;
flow.rows = [];

// Each request the flow makes is numbered, so a flow arriving after the pane has been brought
// to another event is dropped rather than drawn over it
flow.token = 0;

// /////////////////////////////////////////////////////////////////////////////

flow.escapeHTML = function(value) {
    return $.fn.zato.audit_log.escapeHTML(value);
};

// /////////////////////////////////////////////////////////////////////////////

flow.host = function() {
    return $(flow.config.host);
};

// /////////////////////////////////////////////////////////////////////////////

// One event of the flow as everything drawing it reads it - what a row of the list is,
// plus why this event is in the flow at all
flow.buildRow = function(row) {
    var out = listing.buildRow(row);

    out.relation = row.relation;
    out.isSeed = row.is_seed;
    out.source = row.source;
    out.objectName = row.object_name;

    // A flow crosses sources, so a line of another one is named by that source rather than by
    // the one the page happens to be listing
    var presenter = $.fn.zato.audit_log.presenterFor(row.source);

    out.headline = presenter.headline(row);

    // A headline that is only the message id says what the flow already says - most lines of
    // a flow share it, and the panel's facts carry it - so what happened stands in its place
    if (out.headline === '' || out.headline === row.msg_id) {
        out.headline = out.eventType;
    }

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

flow.buildRows = function(rows) {
    var out = [];

    for (var rowIndex = 0; rowIndex < rows.length; rowIndex++) {
        out.push(flow.buildRow(rows[rowIndex]));
    }

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

flow.rowById = function(eventId) {
    var out = null;

    for (var rowIndex = 0; rowIndex < flow.rows.length; rowIndex++) {
        if (String(flow.rows[rowIndex].id) === String(eventId)) {
            out = flow.rows[rowIndex];
            break;
        }
    }

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

flow.fetch = function(seedId, onDone) {
    var config = $.fn.zato.audit_log.config;

    $.ajax({
        url: config.flowURL,
        type: 'POST',
        data: JSON.stringify({id: seedId}),
        contentType: 'application/json',
        headers: {'X-CSRFToken': $.cookie('csrftoken')},
        success: function(data) {
            if (typeof data === 'string') {
                data = JSON.parse(data);
            }
            onDone(data);
        }
    });
};

// /////////////////////////////////////////////////////////////////////////////

// The stripe down a line's left edge - the colour of how the event turned out, the accent
// of the line the flow was read from, and a neutral one for an event that reports neither
flow.stripeOf = function(rowModel) {
    var config = flow.config;

    if (rowModel.isSeed) {
        return config.seedAccent;
    }

    if (rowModel.outcome === '') {
        return config.neutralStripe;
    }

    return kit.palette.outcome.bar_colors[rowModel.outcome];
};

// /////////////////////////////////////////////////////////////////////////////

// When the event happened - which day, said the way the list says it, then the time of day
// whole, with the full stamp one hover away
flow.leadHTML = function(rowModel) {
    var html = '<span class="audit-log-flow-time" title="' + flow.escapeHTML(rowModel.timeLocal) + '">' +
        '<span class="audit-log-cell-day">' + flow.escapeHTML(kit.time_ago_label(rowModel.timeIso)) +
        '</span>' + flow.escapeHTML(listing.config.dayTimeSeparator) +
        flow.escapeHTML(rowModel.timeLocal.slice(11)) + '</span>';

    return html;
};

// /////////////////////////////////////////////////////////////////////////////

flow.elapsedHTML = function(previous, rowModel) {
    var previousMs = new Date(previous.timeIso).getTime();
    var currentMs = new Date(rowModel.timeIso).getTime();
    var elapsedMs = currentMs - previousMs;

    // Two events written down within the same millisecond have nothing to say here
    if (elapsedMs <= 0) {
        return '';
    }

    var out = '<span class="audit-log-flow-elapsed">+' + kit.format_duration_ms(elapsedMs) + '</span>';

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// What the event is - how long after the line below it it happened, the line below being
// the one before it in time, which source wrote it down when that is not the source of the
// page, what happened, what the message is known by, and why the event is in the flow
flow.messageHTML = function(rowModel, previous) {
    var config = flow.config;
    var pageSource = $.fn.zato.audit_log.config.source;
    var html = '';

    // The elapsed time reads after the direction rather than before it, so the tag saying
    // which way the event went stands right against the time it went that way at
    if (previous !== null) {
        html += flow.elapsedHTML(previous, rowModel);
    }

    // A flow crosses sources, so a line of another one says which it came from
    if (rowModel.source !== pageSource) {
        html += '<span class="audit-log-flow-source">' + flow.escapeHTML(rowModel.source) + '</span>';
    }

    // An event whose headline is what happened does not say it a second time beside itself
    if (rowModel.eventType !== rowModel.headline) {
        html += '<span class="audit-log-flow-event">' + flow.escapeHTML(rowModel.eventType) + '</span>';
    }

    html += '<span class="audit-log-flow-headline">' + flow.escapeHTML(rowModel.headline) + '</span>';

    // The operation itself is left unnamed, and so is the line the flow was read from
    var relationLabel = config.relationLabels[rowModel.relation];

    if (relationLabel !== undefined) {
        html += '<span class="audit-log-flow-relation">' + relationLabel + '</span>';
    }

    return html;
};

// /////////////////////////////////////////////////////////////////////////////

// What can be done with the event from the line itself - taking the line away as it reads,
// and going to the event's own page, which is a real link so it opens in a tab of its own
flow.actionsHTML = function(rowModel) {
    var config = flow.config;

    var html = '<span class="dashboard-panel-action-badge dashboard-panel-action-badge-dark ' +
        'audit-log-flow-copy-line">' + config.copyLabel + '</span>';

    html += '<a class="dashboard-panel-action-badge dashboard-panel-action-badge-dark ' +
        'audit-log-flow-open" href="' + flow.eventURL(rowModel) + '">' + config.openLabel + '</a>';

    return html;
};

// /////////////////////////////////////////////////////////////////////////////

// The address of one event's own audit log page, opened on that event with its flow showing
flow.eventURL = function(rowModel) {
    var config = $.fn.zato.audit_log.config;

    var params = new URLSearchParams();

    params.set('source', rowModel.source);
    params.set('object_name', rowModel.objectName);
    params.set('cluster', config.clusterId);
    params.set('event', rowModel.id);
    params.set('tab', listing.config.flowTab);

    var out = window.location.pathname + '?' + params.toString();

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// The line itself as it reads on one line, which is what taking it away puts on the clipboard
flow.lineText = function(rowModel) {
    var directionLabel = kit.direction.config.labels[rowModel.direction];

    var parts = [rowModel.timeLocal, directionLabel, rowModel.source,
        rowModel.eventType, rowModel.headline];

    var out = parts.join(' - ');

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

flow.lineHTML = function(rowModel, previous) {
    var lineClasses = 'audit-log-flow-line';

    if (rowModel.isSeed) {
        lineClasses += ' audit-log-flow-line-seed';
    }

    var out = kit.log_line.render({
        classes: lineClasses,
        attrs: {
            'data-step': rowModel.id,
            'role': 'button',
            'tabindex': '0',
            'aria-expanded': 'false'
        },
        stripe: flow.stripeOf(rowModel),
        lead_html: flow.leadHTML(rowModel),
        badge_html: kit.direction.tag(rowModel.direction, rowModel.eventType, flow.config.darkVariant),
        message_html: flow.messageHTML(rowModel, previous),
        actions_html: flow.actionsHTML(rowModel)
    });

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// One line and the shell it opens into, which stays empty until it is opened
flow.stepHTML = function(rowModel, previous) {
    var out = flow.lineHTML(rowModel, previous);

    out += kit.log_line.panel({
        tag: 'div',
        classes: 'audit-log-flow-panel',
        attrs: {'data-step': rowModel.id},
        is_framed: false
    });

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

flow.render = function() {
    var html = '<div class="detail-panel-log audit-log-flow">';

    for (var rowIndex = 0; rowIndex < flow.rows.length; rowIndex++) {
        var rowModel = flow.rows[rowIndex];

        // With the newest first, the event before this one in time is the row after it
        var previous = null;

        if (rowIndex + 1 < flow.rows.length) {
            previous = flow.rows[rowIndex + 1];
        }

        html += flow.stepHTML(rowModel, previous);
    }

    html += '</div>';

    flow.host().html(html);
};

// /////////////////////////////////////////////////////////////////////////////

flow.show = function(rowModel) {

    // The flow already drawn for this event is the flow it is owed - switching tabs back and
    // forth, or a refresh that leaves the same event selected, redraws nothing.
    if (String(flow.seedId) === String(rowModel.id)) {
        return;
    }

    flow.seedId = rowModel.id;

    flow.token = flow.token + 1;
    var token = flow.token;

    var $host = flow.host();

    // The wait is only announced once it is long enough to be worth announcing
    var spinnerTimer = setTimeout(function() {
        if (flow.token !== token) {
            return;
        }

        $host.html('<div class="dashboard-inline-empty">' + kit.spinner_label_html() + '</div>');
    }, flow.config.spinnerDelayMs);

    flow.fetch(rowModel.id, function(data) {

        // A flow of an event the pane has since been brought away from is not drawn at all
        if (flow.token !== token) {
            return;
        }

        clearTimeout(spinnerTimer);

        flow.rows = flow.buildRows(data.rows);

        flow.render();
        flow.panel.restoreStep();
    });
};

// /////////////////////////////////////////////////////////////////////////////

// The same flow asked for again by the clock rather than by the reader - only what has
// arrived since is added, and the line standing open keeps whatever it has already loaded
flow.refreshLive = function() {
    if (flow.seedId === null) {
        return;
    }

    var token = flow.token;

    flow.fetch(flow.seedId, function(data) {
        if (flow.token !== token) {
            return;
        }

        flow.merge(flow.buildRows(data.rows));
    });
};

// /////////////////////////////////////////////////////////////////////////////

flow.merge = function(rows) {
    var $flow = flow.host().find('.audit-log-flow');

    // A frame that is not there is a tab that was never opened, so there is nothing to add to
    if (!$flow.length) {
        return;
    }

    // What arrives reads newest first like everything else, and each new line goes on top of
    // the flow - so the arrivals are walked from the oldest of them up, each landing above
    // the one before it and the newest of them ending up topmost
    for (var rowIndex = rows.length - 1; rowIndex >= 0; rowIndex--) {
        var rowModel = rows[rowIndex];

        // A line already on the screen is left as it stands, open panel and loaded body and all
        if (flow.rowById(rowModel.id) !== null) {
            continue;
        }

        // The newest line already drawn is the one before this one in time
        var previous = null;

        if (flow.rows.length) {
            previous = flow.rows[0];
        }

        var $step = $(flow.stepHTML(rowModel, previous));
        var $line = $step.filter(flow.config.lineSelector);

        $line.addClass('kit-fade-in');
        $line.one('animationend', function() { $(this).removeClass('kit-fade-in'); });

        $flow.prepend($step);
        flow.rows.unshift(rowModel);
    }
};

// /////////////////////////////////////////////////////////////////////////////

flow.init = function() {
    var config = flow.config;

    $(document).on('click', config.lineSelector, function(event) {

        // A badge or a link inside the line is what was clicked, not the line itself
        if ($(event.target).closest('a, .dashboard-panel-action-badge').length) {
            return;
        }

        flow.panel.expand($(this).attr('data-step'));
    });

    $(document).on('click', '.audit-log-flow-copy-line', function() {
        var $line = $(this).closest(config.lineSelector);
        var rowModel = flow.rowById($line.attr('data-step'));

        kit.copy_to_clipboard(this, flow.lineText(rowModel));
    });

    flow.panel.init();
};

// /////////////////////////////////////////////////////////////////////////////

})(jQuery);
