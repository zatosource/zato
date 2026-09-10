

// /////////////////////////////////////////////////////////////////////////////

// The pane holding the selected event.

(function($) {

var kit = $.fn.zato.dashboard_kit;
var listing = $.fn.zato.audit_log.listing;

// /////////////////////////////////////////////////////////////////////////////

// The cells of the pane's grid - what this source says about its events, then what every
// source says about all of them. An attribute this event has no value for is left out
// altogether, because a label above a dash says less than nothing. Each one also carries what
// the list is asked for by its Search, which is empty for what an event was measured with -
// nothing is found by having taken the same number of milliseconds.
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

        var columnValue = rowModel.raw[column.key];

        if (columnValue !== '') {
            var columnSearch = columnValue;

            if (config.nonSearchColumnKeys[column.key]) {
                columnSearch = '';
            }

            out.push({key: column.key, label: column.label, value: columnValue, search: columnSearch});
        }
    }

    // A scheduler row carries its run number even on a page whose columns do not name it -
    // the all-sources listing - so the pane says it here, after the page's own columns
    if (!seen['current_run']) {
        var currentRun = rowModel.raw.current_run;

        if (currentRun !== undefined) {
            if (currentRun !== '') {
                out.push({key: 'current_run', label: config.runLabel, value: currentRun, search: currentRun});
            }
        }
    }

    for (var fieldIndex = 0; fieldIndex < config.paneFields.length; fieldIndex++) {
        var field = config.paneFields[fieldIndex];

        // A source naming one of these its own way, e.g. an endpoint it calls a folder,
        // has already had its say above.
        if (seen[field.columnKey]) {
            continue;
        }

        var fieldValue = rowModel[field.key];

        // An event that is its own correlation, e.g. a file transfer run, has said its CID already.
        if (field.columnKey === config.correlIdColumnKey) {
            if (fieldValue === rowModel.cid) {
                continue;
            }
        }

        if (fieldValue !== '') {
            var fieldSearch = '';

            if (field.searchable) {
                fieldSearch = fieldValue;
            }

            out.push({key: field.columnKey, label: field.label, value: fieldValue, search: fieldSearch});
        }
    }

    // An event that took no measurable time is one nothing was timed for, e.g. a message
    // being written down rather than being answered.
    if (rowModel.durationMs > 0) {
        out.push({key: 'duration', label: config.durationLabel,
            value: kit.format_duration_ms(rowModel.durationMs), search: ''});
    }

    if (rowModel.size > 0) {
        out.push({key: 'size', label: config.sizeLabel,
            value: kit.format_number_full(rowModel.size), search: ''});
    }

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// One thing said about the event, in the shape the kit's fact rows read
// One fact of the pane - `searchValue` is what its Search asks the list for, empty when no
// Search is to be offered
listing.paneFact = function(label, valueHTML, copyValue, searchValue) {
    var out = {label: label, value_html: valueHTML, copy_value: copyValue, search_value: searchValue};
    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// What this event came out of and what came out of it, each one selecting its own event
listing.lineageFacts = function(rowModel) {
    var config = listing.config;
    var out = [];

    for (var parentIndex = 0; parentIndex < rowModel.parents.length; parentIndex++) {
        out.push(listing.lineageFact(config.lineageParentLabel, rowModel.parents[parentIndex].id));
    }

    for (var childIndex = 0; childIndex < rowModel.children.length; childIndex++) {
        out.push(listing.lineageFact(config.lineageChildLabel, rowModel.children[childIndex].id));
    }

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// An event's own id is a number in the database and a piece of text everywhere on the screen,
// which is where it turns into one
listing.lineageFact = function(label, eventId) {
    var idText = String(eventId);

    var value = '<a href="javascript:void(0)" class="audit-log-lineage" data-lineage-id="' +
        idText + '">' + listing.config.eventLabel + ' ' + idText + '</a>';

    // The event named here is opened by clicking it, rather than searched for
    var out = listing.paneFact(label, value, idText, '');

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// The two ways of reading one event's payload - as it went over the wire, which is where the
// reading of it starts whatever source wrote it down, and as that source's own reader makes
// sense of it. Every event of every source is read through these same two tabs, so moving down
// the list swaps the text inside the frame rather than taking the frame down and putting it up.
// The ways the event's message can be read, which its source decides.
listing.detailTabs = function(rowModel) {
    var presenter = $.fn.zato.audit_log.presenterFor(rowModel.raw.source);
    return presenter.payloadTabs();
};

// /////////////////////////////////////////////////////////////////////////////

// The payload tab standing open is the one the address bar names, so a copied link opens
// on the very reading its sender had in front of them.
listing.openPayloadIndex = function(tabs) {
    var config = listing.config;

    if (kit.url_state.get(config.viewURLKey) !== config.rawView) {
        return 0;
    }

    for (var tabIndex = 0; tabIndex < tabs.length; tabIndex++) {
        if (!tabs[tabIndex].parsed) {
            return tabIndex;
        }
    }

    return 0;
};

// /////////////////////////////////////////////////////////////////////////////

// One event's payload, whole or only the top of it - a pane showing a message asks for all
// of it, and a line of a flow opened for a look asks for as much of it as it will show
listing.fetchDetails = function(eventId, kind, isPreview, onDone) {
    var config = $.fn.zato.audit_log.config;

    $.ajax({
        url: config.detailsURL,
        type: 'POST',
        data: JSON.stringify({id: eventId, kind: kind, preview: isPreview}),
        contentType: 'application/json',
        headers: {'X-CSRFToken': $.cookie('csrftoken')},
        success: function(data) {
            if (typeof data === 'string') {
                data = JSON.parse(data);
            }
            onDone(data);
        },

        // A failed read says so where the body would have stood - without this,
        // whatever pane asked keeps its spinner up forever
        error: function(jqXHR) {
            onDone({
                data: listing.config.detailsErrorLabel + ' - HTTP ' + jqXHR.status,
                parsed: '',
                total_len: 0
            });
        }
    });
};

// /////////////////////////////////////////////////////////////////////////////

// One tab of the pane, drawn the way every tab on the dashboard is drawn
listing.paneTabHTML = function(name, label) {
    var out = '<button type="button" class="dashboard-tab audit-log-pane-tab" role="tab" data-tab="' +
        name + '">' + label + '</button>';

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// What the pane says about the event it is holding, above its two tabs
listing.paneHeadHTML = function(rowModel) {
    var config = listing.config;

    // Which event is being read comes first, because it is what the address bar carries
    // and what a row is picked out of the list by
    var html = '<span class="audit-log-pane-event">' + config.eventLabel + ' ' + rowModel.id + '</span>';

    html += kit.role.tag(rowModel.role, rowModel.eventLabel);
    html += '<span class="audit-log-pane-title">' + listing.escapeHTML(rowModel.headline) + '</span>';
    html += listing.outcomeBadgeHTML(rowModel);

    // An event with nothing to act on gets no actions holder either - an empty one would
    // still claim a flex gap of its own and hold the badge away from the head's right edge
    var actionHTML = listing.actionHTML(rowModel);

    if (actionHTML) {
        html += '<span class="audit-log-pane-actions">' + actionHTML + '</span>';
    }

    return html;
};

// /////////////////////////////////////////////////////////////////////////////

// A value that leads to a page, drawn the way every other way out of the pane is drawn -
// wearing the sign that it leads off this page, in its own ink
listing.linkHTML = function(url, text) {
    var out = '<a href="' + listing.escapeHTML(url) + '" class="audit-log-object-link">' +
        listing.escapeHTML(text) + listing.config.externalIconHTML + '</a>';

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// One object's name as the pane shows it - a link to the object's own page for a source
// that has one, and the name as it stands for a source that does not
listing.objectValueHTML = function(rowModel, name) {
    var linkTemplate = $.fn.zato.audit_log.config.objectLinks[rowModel.raw.source];

    if (linkTemplate === undefined) {
        return listing.escapeHTML(name);
    }

    var url = linkTemplate.replace('{name}', encodeURIComponent(name));

    return listing.linkHTML(url, name);
};

// /////////////////////////////////////////////////////////////////////////////

// One attribute's value as the pane draws it - the source by its human name and as a way
// to its own main page, the object as a way to its page, the event by what it reads as,
// an endpoint as a way to the service it names or with its method in the method's own
// ink, and everything else as the text it is
listing.paneAttrValueHTML = function(rowModel, attr) {
    var config = $.fn.zato.audit_log.config;

    // The source's own HTML for the value comes first, null leaves it to the list.
    var presenter = $.fn.zato.audit_log.presenterFor(rowModel.raw.source);
    var presenterHTML = presenter.attrValueHTML(rowModel, attr);

    if (presenterHTML !== null) {
        return presenterHTML;
    }

    if (attr.key === 'source') {
        var sourceLabel = $.fn.zato.audit_log.sourceLabel(attr.value);
        var sourceLink = config.sourceLinks[attr.value];

        if (sourceLink === undefined) {
            return listing.escapeHTML(sourceLabel);
        }

        return listing.linkHTML(sourceLink, sourceLabel);
    }

    if (attr.key === 'object_name') {
        return listing.objectValueHTML(rowModel, attr.value);
    }

    // The event word filters the log down to events of its kind, and the outcome drives
    // the legend the same way clicking its badge up there does
    if (attr.key === 'event_type') {
        var eventWord = $.fn.zato.audit_log.eventLabel(attr.value);

        return '<a href="javascript:void(0)" class="audit-log-event-filter" data-event-type="' +
            listing.escapeHTML(attr.value) + '">' + listing.escapeHTML(eventWord) + '</a>';
    }

    if (attr.key === 'outcome') {
        return '<a href="javascript:void(0)" class="audit-log-outcome-filter" data-outcome="' +
            listing.escapeHTML(attr.value) + '">' + listing.escapeHTML(attr.value) + '</a>';
    }

    if (attr.key === 'endpoint') {
        var endpointTemplate = config.endpointLinks[rowModel.raw.source];

        if (endpointTemplate === undefined) {
            return kit.http_method.html(attr.value);
        }

        var url = endpointTemplate.replace('{name}', encodeURIComponent(attr.value));

        return listing.linkHTML(url, attr.value);
    }

    // A run leads to its own page, keyed by whatever of the job's id, the run's number
    // and the CID its source's page is found by, all carried by the event itself
    if (attr.key === 'current_run') {
        var runTemplate = config.runLinks[rowModel.raw.source];

        if (runTemplate === undefined) {
            return listing.escapeHTML(attr.value);
        }

        var runURL = runTemplate.replace('{job_id}', encodeURIComponent(rowModel.raw.job_id))
            .replace('{run}', encodeURIComponent(attr.value))
            .replace('{cid}', encodeURIComponent(rowModel.cid));

        return listing.linkHTML(runURL, attr.value);
    }

    return listing.escapeHTML(attr.value);
};

// /////////////////////////////////////////////////////////////////////////////

// One attribute's name as the pane draws it - the object and the endpoint are labelled
// by the word their own source has for them, a channel by Channel, a service by Service,
// a mailbox folder by Folder, so no row is headed by a word that names nothing
listing.paneAttrLabel = function(rowModel, attr) {
    var config = $.fn.zato.audit_log.config;

    // The source's own label comes first, an empty label leaves it to the list.
    var presenter = $.fn.zato.audit_log.presenterFor(rowModel.raw.source);
    var presenterLabel = presenter.attrLabel(rowModel, attr);

    if (presenterLabel !== '') {
        return presenterLabel;
    }

    if (attr.key === 'object_name') {
        var label = config.objectLabels[rowModel.raw.source];

        if (label === undefined) {
            label = config.defaultObjectLabel;
        }

        return label;
    }

    if (attr.key === 'endpoint') {
        var endpointLabel = config.endpointLabels[rowModel.raw.source];

        if (endpointLabel !== undefined) {
            return endpointLabel;
        }
    }

    return attr.label;
};

// /////////////////////////////////////////////////////////////////////////////

// Everything said about the event, which is what the Summary tab holds - one thing to a
// line, read from the top down, rather than several of them side by side to be picked out
listing.defaultSummaryFacts = function(rowModel) {
    var config = listing.config;
    var attrs = listing.paneAttrs(rowModel);
    var facts = [];

    // The CID leads, because it is what the whole message is opened by
    var cidValue = '<a href="#" class="audit-log-cid-link" data-id="' + rowModel.id + '" data-cid="' +
        listing.escapeHTML(rowModel.cid) + '">' + listing.escapeHTML(rowModel.cid) + '</a>';

    facts.push(listing.paneFact(config.cidLabel, cidValue, rowModel.cid, ''));

    for (var attrIndex = 0; attrIndex < attrs.length; attrIndex++) {
        var attr = attrs[attrIndex];

        facts.push(listing.paneFact(listing.paneAttrLabel(rowModel, attr),
            listing.paneAttrValueHTML(rowModel, attr), attr.value, attr.search));
    }

    // What response shaping did to this event - one line per finding, each already
    // worded by the backend in the grammatical number its count calls for
    var traceLines = rowModel.raw.trace_lines;

    if (traceLines !== undefined) {
        for (var traceIndex = 0; traceIndex < traceLines.length; traceIndex++) {
            var traceLine = traceLines[traceIndex];

            facts.push(listing.paneFact(traceLine.label, listing.escapeHTML(traceLine.text),
                traceLine.text, ''));
        }
    }

    // The source's own facts follow the shared ones.
    var presenter = $.fn.zato.audit_log.presenterFor(rowModel.raw.source);
    facts = facts.concat(presenter.detailFacts(rowModel));

    facts = facts.concat(listing.lineageFacts(rowModel));

    // When the event happened reads last of everything - a moment in time is shared by
    // nothing, so no Search stands beside it either. The stamp itself is the scrubber
    // with every unit on it, the year and the month included.
    facts.push(listing.paneFact(config.timeLabel, kit.time_scrub.stamp(rowModel.timeIso),
        rowModel.timeLocal, ''));

    return facts;
};

// /////////////////////////////////////////////////////////////////////////////

// The Summary tab - the facts the source has to say about the event, then the files it carried.
listing.paneSummaryHTML = function(rowModel) {
    var config = listing.config;
    var presenter = $.fn.zato.audit_log.presenterFor(rowModel.raw.source);
    var facts = presenter.summaryFacts(rowModel);

    var html = kit.fact_rows.render(facts, config.paneFactVariant);

    // The files the event carried, filled in once their metadata has arrived and only
    // when there are any at all
    html += '<div class="' + config.attachmentsHostClass + '" data-attachments-id="' +
        rowModel.id + '"></div>';

    return html;
};

// /////////////////////////////////////////////////////////////////////////////

// Whether the event's source has a Details tab to show for this very event.
listing.hasDetailsTab = function(rowModel) {
    var presenter = $.fn.zato.audit_log.presenterFor(rowModel.raw.source);
    return presenter.hasDetails(rowModel);
};

// /////////////////////////////////////////////////////////////////////////////

// The pane's tabs - Summary and Data for every event, Details for one whose source has a panel for it.
listing.paneTabsHTML = function(rowModel) {
    var config = listing.config;

    var html = listing.paneTabHTML(config.summaryTab, config.summaryTabLabel);
    html += listing.paneTabHTML(config.dataTab, config.dataTabLabel);

    if (listing.hasDetailsTab(rowModel)) {
        html += listing.paneTabHTML(config.detailsTab, config.detailsTabLabel);
    }

    return html;
};

// /////////////////////////////////////////////////////////////////////////////

// The files the event carried are asked about when the event is opened - an event
// carrying none keeps the strip's place empty
listing.loadAttachments = function(rowModel, $host) {
    var config = $.fn.zato.audit_log.config;

    kit.attachments.load($host, {
        list_url: config.attachmentsURL,
        download_url: config.attachmentDownloadURL,
        id: rowModel.id,
        variant: listing.config.paneFactVariant
    });
};

// /////////////////////////////////////////////////////////////////////////////

listing.paneHTML = function(rowModel) {
    var config = listing.config;

    var html = '<div class="audit-log-pane-head">' + listing.paneHeadHTML(rowModel) + '</div>';

    // Everything said about the event, the message itself and the source's own panel are
    // ways of reading one event, so the pane is one of them at a time rather than all at once.
    // The flow the event belongs to is a page of its own, and its doorway stands to the right
    // of the tabs - beside the strip, not inside it, being a way out rather than a way to turn the page.
    html += '<div class="audit-log-pane-tabs-row">';
    html += '<div class="dashboard-tabs audit-log-pane-tabs" role="tablist">';
    html += listing.paneTabsHTML(rowModel);
    html += '</div>';
    html += '<a class="audit-log-open-flow" data-event-id="' + rowModel.id + '" href="' +
        $.fn.zato.audit_log.flowPageURL(rowModel.id) + '">' + config.openFlowLabel + '</a>';
    html += '</div>';

    // Only the panels scroll - the head and the tabs stand outside the scrolling body, so
    // the scrollbar the panels bring never pushes the head's right edge away from the page's
    html += '<div class="audit-log-pane-body">';

    html += '<div class="dashboard-tab-panel" role="tabpanel" id="' +
        config.tabPanelPrefix + config.summaryTab + '">';
    html += '<div class="audit-log-pane-frame audit-log-pane-summary">' + listing.paneSummaryHTML(rowModel) + '</div>';
    html += '</div>';

    html += '<div class="dashboard-tab-panel" role="tabpanel" id="' +
        config.tabPanelPrefix + config.dataTab + '">';
    html += '<div id="' + config.payloadHost.slice(1) + '"></div>';
    html += '</div>';

    // The source's panel is drawn into the frame once the pane holds the event.
    html += '<div class="dashboard-tab-panel" role="tabpanel" id="' +
        config.tabPanelPrefix + config.detailsTab + '">';
    html += '<div class="audit-log-pane-frame audit-log-pane-details audit-log-pane-source-panel"></div>';
    html += '</div>';

    html += '</div>';

    return html;
};

// /////////////////////////////////////////////////////////////////////////////

// The pane brought from one event to the next where it stands - the frame and whichever tab
// is open stay as they are, and only what they hold is replaced. The message and the source's
// panel are left alone here, each of them deciding for itself whether the event it is holding
// is still the one being read.
listing.paneUpdate = function(rowModel, $pane) {
    $pane.find('.audit-log-pane-head').html(listing.paneHeadHTML(rowModel));
    $pane.find('.audit-log-pane-tabs').html(listing.paneTabsHTML(rowModel));
    $pane.find('.audit-log-pane-summary').html(listing.paneSummaryHTML(rowModel));
};

// /////////////////////////////////////////////////////////////////////////////

// The source's own panel, which is what the Details tab holds.
listing.fillSourcePanel = function(rowModel, $pane) {
    var presenter = $.fn.zato.audit_log.presenterFor(rowModel.raw.source);
    var $host = $pane.find('.audit-log-pane-source-panel');

    presenter.detailPanel([rowModel], $host, listing.config.paneFactVariant);
};

// /////////////////////////////////////////////////////////////////////////////

// The source's panel is redrawn for another event and at every poll while the event is or was running.
listing.syncSourcePanel = function(rowModel, $pane) {
    var config = listing.config;

    var idBefore = $pane.data('source_panel_event_id');
    var outcomeBefore = $pane.data('source_panel_outcome');

    var isSameEvent = String(idBefore) === String(rowModel.id);
    var isRunning = rowModel.outcome === config.runningOutcome;
    var wasRunning = outcomeBefore === config.runningOutcome;

    var needsRedraw = !isSameEvent;

    if (isRunning) {
        needsRedraw = true;
    }

    if (wasRunning) {
        needsRedraw = true;
    }

    if (needsRedraw) {
        listing.fillSourcePanel(rowModel, $pane);
    }

    $pane.data('source_panel_event_id', rowModel.id);
    $pane.data('source_panel_outcome', rowModel.outcome);
};

// /////////////////////////////////////////////////////////////////////////////

// Each tab of the payload asks for its own body the first time it is opened, and the
// payload itself is only asked for once the tab holding it is the one being looked at.
listing.showPayload = function() {
    var $host = $(listing.config.payloadHost);
    var rowModel = listing.selected;

    // The panel already holding this event is the panel it was given - a refresh that leaves
    // the same event selected leaves the message being read on the screen as it is.
    if ($host.data('payload_event_id') === rowModel.id) {
        return;
    }

    $host.data('payload_event_id', rowModel.id);

    var tabs = listing.detailTabs(rowModel);
    var openIndex = listing.openPayloadIndex(tabs);

    kit.payload_panel.swap($host, tabs, function(tab, onDone) {
        listing.fetchDetails(rowModel.id, tab.kind, false, function(details) {

            if (!tab.parsed) {
                onDone(details.data);
                return;
            }

            // A payload this source's own reader could make nothing of - a JSON alert in
            // an HL7 log, say - is shown as it stands rather than as a blank pane.
            if (details.parsed === '') {
                onDone(details.data);
            }
            else {
                onDone(details.parsed);
            }
        });
    }, openIndex);
};

// /////////////////////////////////////////////////////////////////////////////

// Whichever way of reading an event is open asks for what it shows, and the ones that
// are not open ask for nothing until their turn comes
listing.showTab = function(tab) {
    var config = listing.config;

    if (tab === config.dataTab) {
        listing.showPayload();
    }
};

// /////////////////////////////////////////////////////////////////////////////

// The tab the pane opens the event in - the one already open, unless that is a Details tab
// the event does not have, in which case the Summary stands in for it.
listing.tabFor = function(rowModel, openTab) {
    var config = listing.config;

    if (openTab === config.detailsTab) {
        if (!listing.hasDetailsTab(rowModel)) {
            return config.summaryTab;
        }
    }

    return openTab;
};

// /////////////////////////////////////////////////////////////////////////////

listing.onSelect = function(rowModel, $pane) {
    var config = listing.config;

    listing.selected = rowModel;

    // The files the event carried and the source's panel are asked about the moment the pane holds it.
    listing.loadAttachments(rowModel, $pane.find('.' + config.attachmentsHostClass));
    listing.syncSourcePanel(rowModel, $pane);

    // The tab group is bound to the pane the first time the pane holds one, and every
    // pane after that is put into whichever tab is already open.
    if (listing.tabs === null) {
        listing.tabs = kit.tabs.init({
            tab_selector: config.tabSelector,
            panel_prefix: config.tabPanelPrefix,
            storage_key: config.tabStorageKey,
            default_tab: config.summaryTab,
            on_change: function(tab) {
                kit.url_state.replace({tab: tab});
                listing.showTab(tab);
            }
        });

        // A link naming a tab opens in that tab, whatever this screen was last left in.
        var urlTab = listing.urlTab();

        if (urlTab !== '') {
            listing.tabs.set_tab(listing.tabFor(rowModel, urlTab), true);
        }
    }
    else {
        listing.tabs.set_tab(listing.tabFor(rowModel, listing.tabs.get_tab()), true);
    }

    // A link to this page is a link to the event being read on it, in the tab it is
    // being read in.
    kit.url_state.replace({event: rowModel.id, tab: listing.tabs.get_tab()});

    listing.showTab(listing.tabs.get_tab());
};

// /////////////////////////////////////////////////////////////////////////////

// The tab a link to this page asked for, and nothing when it asked for none
listing.urlTab = function() {
    var config = listing.config;
    var wanted = kit.url_state.get(config.tabURLKey);

    // Only the tabs the pane actually has are honoured, so a hand-typed address cannot
    // leave the pane with no tab open at all.
    if (wanted === config.summaryTab) {
        return wanted;
    }

    if (wanted === config.dataTab) {
        return wanted;
    }

    if (wanted === config.detailsTab) {
        return wanted;
    }

    return '';
};

})(jQuery);
