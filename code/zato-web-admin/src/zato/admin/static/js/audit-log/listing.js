

// /////////////////////////////////////////////////////////////////////////////

// The audit log listing - a main list of events beside a pane holding the selected one whole,
// with a timeline and its legend above them. Everything about it that is not about audit events
// lives in the dashboard kit, and everything a particular source shows lives in its presenter.

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
    timelineHost: '#audit-log-timeline',
    legendHost: '#audit-log-legend',
    payloadHost: '#audit-log-pane-payload',
    rangePillId: 'audit-log-range',

    // What the proportions of one source's listing are remembered under
    storagePrefix: 'zato_audit_log_layout_',
    refreshStorageKey: 'zato_audit_log_refresh',
    rangeStorageKey: 'zato_audit_log_range',

    // How wide the list starts out, which is wider than the kit's own default because
    // a row of it says a lot at once
    defaultListWidth: 760,

    // How many cells one row of the list has, which is what a row standing in for
    // the whole list spans
    columnCount: 9,

    emptyValue: '---',
    emptyListing: 'No events found',
    emptyPane: 'No event selected',
    loadingLabel: 'Loading...',

    rawTabLabel: 'Raw',
    parsedTabLabel: 'Parsed',
    copyCIDLabel: 'Copy CID',

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

    // The outcomes an audit event reports, in the order they stack in the timeline
    outcomeKeys: ['ok', 'error', 'expired'],

    // The outcome an event that reports none of its own is counted as
    neutralOutcomeKey: 'ok',

    // The tint the newest rows carry and how far down the list it reaches
    recencyRGB: '218, 165, 32',
    recencySteps: 10,

    // How often the listing asks for what has arrived since, until it is told otherwise
    refreshDefaultSeconds: 0,

    // The smallest a size bar is drawn as, so a one-byte payload is still visible
    minSizeBarPercent: 2,

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

    // What the pane says about every event whatever source it came from, each one left out
    // when the source already declares a column of its own for it
    paneFields: [
        {label: 'Time', key: 'timeLocal', columnKey: 'event_time_iso'},
        {label: 'Correlation id', key: 'correlId', columnKey: 'correl_id'},
        {label: 'Status', key: 'status', columnKey: 'status'},
        {label: 'Classification', key: 'classification', columnKey: 'classification'},
        {label: 'Endpoint', key: 'endpoint', columnKey: 'endpoint'}
    ],

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

// Which way one event went - the audit event types are shared across sources,
// so this reads the same everywhere
listing.directions = {
    'received': 'in',
    'request-received': 'in',
    'response-received': 'in',
    'message-received': 'in',
    'interchange-received': 'in',
    'ack-received': 'in',
    'mdn-received': 'in',
    'receipt-received': 'in',
    'request-sent': 'out',
    'response-sent': 'out',
    'message-sent': 'out',
    'interchange-sent': 'out',
    'ack-sent': 'out',
    'mdn-sent': 'out',
    'receipt-sent': 'out',
    'delivered': 'out',
    'delivery-failed': 'out'
};

// /////////////////////////////////////////////////////////////////////////////

// One page of events as the listing reads them, and what the chrome has narrowed them down to
listing.rowModels = [];
listing.visible = [];
listing.hidden = {};
listing.minutes = 0;

// The largest payload on the page, which every size bar is drawn against
listing.maxSize = 1;

// The events already on the page before the last refresh, so only what is new puffs.
// Nothing has been drawn yet while this is null, and a first drawing puffs nothing.
listing.seenIds = null;

// The two panes, once they are built
listing.panes = null;

// /////////////////////////////////////////////////////////////////////////////

listing.escapeHTML = function(value) {
    return $.fn.zato.audit_log.escapeHTML(value);
};

// /////////////////////////////////////////////////////////////////////////////

listing.directionOf = function(eventType) {
    var direction = listing.directions[eventType];

    // An event type that is neither one way nor the other, e.g. a message expiring.
    if (direction === undefined) {
        direction = 'none';
    }

    return direction;
};

// /////////////////////////////////////////////////////////////////////////////

listing.outcomeBadgeHTML = function(rowModel) {

    // Not every event type reports an outcome - a message arriving is neither
    // a success nor a failure until something is done with it.
    if (rowModel.outcome === '') {
        return '<span class="audit-log-outcome-none">' + listing.config.emptyValue + '</span>';
    }

    var out = kit.outcome.badge(rowModel.outcome, kit.palette.outcome_palette);

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

listing.sizeText = function(size) {
    if (size === null) {
        return listing.config.emptyValue;
    }

    var out = kit.format_number_full(size);
    return out;
};

// /////////////////////////////////////////////////////////////////////////////

listing.durationText = function(durationMs) {
    if (durationMs === null) {
        return listing.config.emptyValue;
    }

    var out = kit.format_duration_ms(durationMs);
    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// One row of the poll as everything drawing it reads it
listing.buildRow = function(row) {
    var config = listing.config;
    var presenter = $.fn.zato.audit_log.presenter();

    var out = {
        raw: row,
        id: row.id,
        cid: row.cid,
        msgId: row.msg_id,
        correlId: row.correl_id,
        endpoint: row.endpoint,
        eventType: row.event_type,
        outcome: row.outcome,
        status: row.status,
        classification: row.classification,
        timeIso: row.event_time_iso,
        timeLocal: kit.format_local_time(row.event_time_iso),
        size: row.size,
        durationMs: row.duration_ms,
        preview: row.data,
        parents: row.parents,
        children: row.children,
        bodyKinds: row.body_kinds,
        isResubmitted: row.is_resubmitted,
        direction: listing.directionOf(row.event_type),
        actionLabel: $.fn.zato.audit_log.config.resubmitLabels[row.event_type]
    };

    // A source names its messages by whatever it calls a control id, and one with no
    // name of its own for them is read by the CID the message travelled under.
    if (out.msgId === '') {
        out.controlId = out.cid;
    }
    else {
        out.controlId = out.msgId;
    }

    // An event reporting an outcome the timeline knows still counts as one that went through,
    // and so does one reporting none at all.
    if (config.outcomeKeys.indexOf(out.outcome) === -1) {
        out.chartKey = config.neutralOutcomeKey;
    }
    else {
        out.chartKey = out.outcome;
    }

    out.chips = presenter.chips(row);
    out.headline = presenter.headline(row);

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

listing.actionHTML = function(rowModel) {
    var config = $.fn.zato.audit_log.config;
    var html = '';

    // Only the event types their source declared resubmittable have anything to offer here.
    if (rowModel.actionLabel !== undefined) {
        html += '<a href="javascript:void(0)" class="audit-log-resubmit-link" data-id="' +
            rowModel.id + '">' + rowModel.actionLabel + '</a>';
    }

    if (rowModel.isResubmitted) {
        html += ' <span class="audit-log-resubmitted-marker">' + config.resubmittedMarkerLabel + '</span>';
    }

    return html;
};

// /////////////////////////////////////////////////////////////////////////////

// The payload of one row against the largest one on the page
listing.sizeBarHTML = function(rowModel) {
    var config = listing.config;

    if (rowModel.size === null) {
        return '<span class="audit-log-size-text audit-log-muted">' + config.emptyValue + '</span>';
    }

    var percent = (rowModel.size / listing.maxSize) * 100;

    if (percent < config.minSizeBarPercent) {
        percent = config.minSizeBarPercent;
    }

    var html = '<span class="audit-log-size-bar">';
    html += '<span class="audit-log-size-bar-fill" style="width:' + percent.toFixed(1) + '%"></span>';
    html += '</span>';
    html += '<span class="audit-log-size-text">' + listing.sizeText(rowModel.size) + '</span>';

    return html;
};

// /////////////////////////////////////////////////////////////////////////////

listing.rowHTML = function(rowModel) {
    var config = listing.config;

    var html = '<tr class="audit-log-row" data-item-id="' + rowModel.id +
        '" data-ts="' + listing.escapeHTML(rowModel.timeIso) + '">';

    // The time of day is what tells two events of the same minute apart, and the whole
    // timestamp is one hover away.
    html += '<td class="audit-log-cell-time" title="' + listing.escapeHTML(rowModel.timeLocal) + '">' +
        listing.escapeHTML(rowModel.timeLocal.slice(11)) + '</td>';

    html += '<td class="audit-log-cell-direction">' +
        kit.direction.tag(rowModel.direction, rowModel.eventType) + '</td>';

    html += '<td class="audit-log-cell-id">' + listing.escapeHTML(rowModel.controlId) + '</td>';
    html += '<td class="audit-log-cell-event">' + listing.escapeHTML(rowModel.eventType) + '</td>';
    html += '<td class="audit-log-cell-outcome">' + listing.outcomeBadgeHTML(rowModel) + '</td>';
    html += '<td class="audit-log-cell-chips">' + kit.chips.render(rowModel.chips) + '</td>';
    html += '<td class="audit-log-cell-size">' + listing.sizeBarHTML(rowModel) + '</td>';
    html += '<td class="audit-log-cell-preview">' + listing.escapeHTML(rowModel.preview) + '</td>';
    html += '<td class="audit-log-cell-action">' + listing.actionHTML(rowModel) + '</td>';

    html += '</tr>';

    return html;
};

// /////////////////////////////////////////////////////////////////////////////

listing.emptyRowHTML = function() {
    var config = listing.config;

    var out = '<tr class="audit-log-empty-row"><td colspan="' + config.columnCount + '">' +
        config.emptyListing + '</td></tr>';

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

listing.loadingRowHTML = function() {
    var config = listing.config;

    var out = '<tr class="detail-loading-row"><td colspan="' + config.columnCount + '">' +
        '<img src="/static/gfx/spinner.svg" class="detail-spinner"> ' + config.loadingLabel + '</td></tr>';

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// The cells of the pane's grid - what this source says about its events, then what
// every source says about all of them. An attribute with no value reads as empty rather
// than being left out, so the grid does not move as the selection walks the list.
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
        out.push({label: column.label, value: rowModel.raw[column.key]});
    }

    for (var fieldIndex = 0; fieldIndex < config.paneFields.length; fieldIndex++) {
        var field = config.paneFields[fieldIndex];

        // A source naming one of these its own way, e.g. an endpoint it calls a folder,
        // has already had its say above.
        if (seen[field.columnKey]) {
            continue;
        }

        out.push({label: field.label, value: rowModel[field.key]});
    }

    out.push({label: config.durationLabel, value: listing.durationText(rowModel.durationMs)});
    out.push({label: config.sizeLabel, value: listing.sizeText(rowModel.size)});

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

listing.paneGridHTML = function(rowModel) {
    var config = listing.config;
    var attrs = listing.paneAttrs(rowModel);

    var html = '<div class="audit-log-pane-grid">';

    // The CID leads the grid because it is what the whole message is opened by.
    html += '<div>';
    html += '<div class="audit-log-pane-cell-label">' + config.cidLabel + '</div>';
    html += '<div class="audit-log-pane-cell-value">';
    html += '<a href="#" class="audit-log-cid-link" data-id="' + rowModel.id + '" data-cid="' +
        listing.escapeHTML(rowModel.cid) + '">' + listing.escapeHTML(rowModel.cid) + '</a>';
    html += '</div>';
    html += '</div>';

    for (var attrIndex = 0; attrIndex < attrs.length; attrIndex++) {
        var attr = attrs[attrIndex];
        var value = attr.value;

        if (value === '') {
            value = config.emptyValue;
        }

        html += '<div>';
        html += '<div class="audit-log-pane-cell-label">' + listing.escapeHTML(attr.label) + '</div>';
        html += '<div class="audit-log-pane-cell-value">' + listing.escapeHTML(value) + '</div>';
        html += '</div>';
    }

    html += '</div>';

    return html;
};

// /////////////////////////////////////////////////////////////////////////////

// What this event came out of and what came out of it, each one selecting its own event
listing.lineageHTML = function(rowModel) {
    var config = listing.config;
    var html = '';

    for (var parentIndex = 0; parentIndex < rowModel.parents.length; parentIndex++) {
        html += listing.lineageLinkHTML(config.lineageParentLabel, rowModel.parents[parentIndex].id);
    }

    for (var childIndex = 0; childIndex < rowModel.children.length; childIndex++) {
        html += listing.lineageLinkHTML(config.lineageChildLabel, rowModel.children[childIndex].id);
    }

    return html;
};

// /////////////////////////////////////////////////////////////////////////////

listing.lineageLinkHTML = function(label, eventId) {
    var out = '<span class="audit-log-lineage" data-lineage-id="' + eventId + '">' +
        label + ' ' + eventId + '</span>';

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// The tabs of one event's payload - one per body kind the event actually has,
// and one for the wire format of a source that keeps its payload in the event itself
listing.bodyTabs = function(rowModel) {
    var config = listing.config;
    var out = [];

    for (var kindIndex = 0; kindIndex < rowModel.bodyKinds.length; kindIndex++) {
        var kind = rowModel.bodyKinds[kindIndex];

        out.push({label: config.bodyKindLabels[kind], kind: kind, parsed: false});
    }

    if (out.length === 0) {
        out.push({label: config.rawTabLabel, kind: '', parsed: false});
    }

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

listing.parsedTab = function() {
    var out = {label: listing.config.parsedTabLabel, kind: '', parsed: true};
    return out;
};

// /////////////////////////////////////////////////////////////////////////////

listing.fetchDetails = function(eventId, kind, onDone) {
    var config = $.fn.zato.audit_log.config;

    $.ajax({
        url: config.detailsURL,
        type: 'POST',
        data: JSON.stringify({id: eventId, kind: kind}),
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

listing.paneHTML = function(rowModel) {
    var html = '<div class="audit-log-pane-head">';

    html += kit.direction.tag(rowModel.direction, rowModel.eventType);
    html += '<span class="audit-log-pane-title">' + listing.escapeHTML(rowModel.headline) + '</span>';
    html += listing.outcomeBadgeHTML(rowModel);

    html += '<span class="audit-log-pane-actions">';
    html += listing.actionHTML(rowModel);
    html += '<input type="button" class="audit-log-copy-cid" data-cid="' + listing.escapeHTML(rowModel.cid) +
        '" value="' + listing.config.copyCIDLabel + '">';
    html += '</span>';
    html += '</div>';

    html += '<div class="audit-log-pane-chips">';
    html += kit.chips.render(rowModel.chips);
    html += listing.lineageHTML(rowModel);
    html += '</div>';

    html += listing.paneGridHTML(rowModel);
    html += '<div id="' + listing.config.payloadHost.slice(1) + '"></div>';

    return html;
};

// /////////////////////////////////////////////////////////////////////////////

// Each tab of the selected event asks for its own body the first time it is opened
listing.onSelect = function(rowModel) {
    var presenter = $.fn.zato.audit_log.presenter();
    var tabs = presenter.detailTabs(rowModel);

    kit.payload_panel.lazy($(listing.config.payloadHost), tabs, function(tab, onDone) {
        listing.fetchDetails(rowModel.id, tab.kind, function(details) {
            onDone(tab.parsed ? details.parsed : details.data);
        });
    });
};

// /////////////////////////////////////////////////////////////////////////////

// The rows of the current page left after the range and the legend have had their say
listing.filterRows = function() {
    var out = [];
    var cutoff = 0;

    if (listing.minutes > 0) {
        cutoff = Date.now() - listing.minutes * 60000;
    }

    for (var rowIndex = 0; rowIndex < listing.rowModels.length; rowIndex++) {
        var rowModel = listing.rowModels[rowIndex];

        if (listing.hidden[rowModel.chartKey]) {
            continue;
        }

        if (cutoff > 0) {
            var rowTime = new Date(rowModel.timeIso).getTime();

            if (rowTime < cutoff) {
                continue;
            }
        }

        out.push(rowModel);
    }

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// The largest payload of whatever is on the page, which every size bar is drawn against
listing.updateMaxSize = function() {
    var maxSize = 1;

    for (var rowIndex = 0; rowIndex < listing.visible.length; rowIndex++) {
        var size = listing.visible[rowIndex].size;

        if (size !== null && size > maxSize) {
            maxSize = size;
        }
    }

    listing.maxSize = maxSize;
};

// /////////////////////////////////////////////////////////////////////////////

// The newest rows carry a fading tint, and a row that arrived on a live refresh puffs once
listing.markNewRows = function() {
    var $itemsHost = listing.panes.items_host();
    var seenIds = {};

    var timestamps = [];
    var limit = listing.config.recencySteps;

    for (var rowIndex = 0; rowIndex < listing.visible.length; rowIndex++) {
        var rowModel = listing.visible[rowIndex];
        seenIds[rowModel.id] = true;

        if (rowIndex < limit) {
            timestamps.push(rowModel.timeIso);
        }

        // Nothing puffs on a first drawing - the whole page is new then, and a page
        // of puffing rows says nothing about which of them just arrived.
        if (listing.seenIds !== null && !listing.seenIds[rowModel.id]) {
            $itemsHost.find('[data-item-id="' + rowModel.id + '"]').addClass('kit-puff');
        }
    }

    listing.seenIds = seenIds;

    kit.recency.apply({
        container: listing.config.itemsHost,
        recent_ts: timestamps,
        rgb: listing.config.recencyRGB
    });
};

// /////////////////////////////////////////////////////////////////////////////

listing.drawTimeline = function() {
    kit.timeline.render($(listing.config.timelineHost), listing.visible, {
        keys: listing.config.outcomeKeys,
        key_of: function(rowModel) { return rowModel.chartKey; },
        ts_of: function(rowModel) { return new Date(rowModel.timeIso).getTime(); },
        colors: kit.palette.outcome.bar_colors,

        // The rows the legend switched off are not on the page at all by now
        hidden: {},
        empty_html: '<div class="dashboard-inline-empty">' + listing.config.emptyListing + '</div>'
    });
};

// /////////////////////////////////////////////////////////////////////////////

listing.draw = function() {
    listing.visible = listing.filterRows();

    listing.updateMaxSize();
    listing.panes.set_items(listing.visible);
    listing.markNewRows();
    listing.drawTimeline();
};

// /////////////////////////////////////////////////////////////////////////////

listing.renderPage = function(_$body, rows) {
    listing.rowModels = listing.buildRows(rows);
    listing.draw();
};

// /////////////////////////////////////////////////////////////////////////////

// The timeline, the legend that filters it, the range pill and the live pill
listing.chromeHTML = function() {
    var config = listing.config;
    var rangePillId = config.rangePillId;

    var html = '<div class="detail-header-controls audit-log-chrome-controls">';

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

    html += '<div class="dashboard-chart-legend" id="' + config.legendHost.slice(1) + '"></div>';
    html += '</div>';

    html += '<div class="dashboard-timeline" id="' + config.timelineHost.slice(1) + '"></div>';

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

listing.refresh = function() {
    var pagination = $.fn.zato.audit_log.pagination;
    pagination.fetch_page(pagination.current_page());
};

// /////////////////////////////////////////////////////////////////////////////

listing.initChrome = function() {
    var config = listing.config;
    var palette = kit.palette.outcome;

    $(config.chromeHost).html(listing.chromeHTML());

    kit.auto_refresh.init({
        pill: '#audit-log-refresh-pill',
        menu: '#audit-log-refresh-menu',
        storage_key: config.refreshStorageKey,
        url_param: 'refresh',
        default_seconds: config.refreshDefaultSeconds,
        on_tick: listing.refresh
    });

    var range = kit.time_range.init({
        pill: '#' + config.rangePillId + '-pill',
        menu: '#' + config.rangePillId + '-menu',
        storage_key: config.rangeStorageKey,
        on_change: function(minutes) {
            listing.setRange(minutes);
            listing.draw();
        }
    });

    // The range this screen was left on last time is the one it opens on, and the pill
    // says so before the first page has even arrived.
    listing.setRange(range.get_minutes());

    kit.build_legend({
        container: config.legendHost,
        series_keys: config.outcomeKeys,
        palette: palette.bar_colors,
        labels: palette.labels,
        text_colors: palette.colors,
        backgrounds: palette.backgrounds,
        hidden: listing.hidden,
        on_toggle: function() {
            listing.draw();
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

        list_html: listHTML,
        items_host: config.itemsHost,
        item_selector: config.itemSelector,

        id_of: function(rowModel) { return rowModel.id; },
        render_item: listing.rowHTML,
        render_empty: listing.emptyRowHTML,
        render_detail: listing.paneHTML,
        empty_detail: '<div class="dashboard-inline-empty">' + config.emptyPane + '</div>',
        on_select: listing.onSelect
    });

    listing.panes.items_host().html(listing.loadingRowHTML());
};

// /////////////////////////////////////////////////////////////////////////////

listing.init = function(initConfig) {
    listing.initChrome();
    listing.initPanes(initConfig.source);

    // A chip says what its row has in common with others, so clicking one asks for them
    $(document).on('click', '.dashboard-chip', function() {
        $.fn.zato.audit_log.search($(this).attr('data-chip-value'));
    });

    // A lineage marker of an event on this page selects it, and one of an event on
    // a page of its own has nothing to select here.
    $(document).on('click', '.audit-log-lineage', function() {
        var eventId = $(this).attr('data-lineage-id');

        if (listing.modelById(eventId) !== null) {
            listing.panes.select(eventId);
        }
    });

    $(document).on('click', '.audit-log-copy-cid', function() {
        kit.copy_to_clipboard(this, $(this).attr('data-cid'));
    });
};

// /////////////////////////////////////////////////////////////////////////////

})(jQuery);
