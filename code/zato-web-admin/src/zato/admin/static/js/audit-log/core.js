
// /////////////////////////////////////////////////////////////////////////////

// The audit log page - its config, the presenters, the overlay and the activity strip.

$.fn.zato.audit_log = {};

// The per-source presenters saying what a row of that source shows
$.fn.zato.audit_log.sources = {};

// /////////////////////////////////////////////////////////////////////////////

(function($) {

$.fn.zato.audit_log.config = {
    pageSize: 25,
    detailsURL: '/zato/audit-log/details/',
    resubmitURL: '/zato/audit-log/resubmit/',
    attachmentsURL: '/zato/audit-log/attachments/',
    attachmentDownloadURL: '/zato/audit-log/attachment/',
    flowURL: '/zato/audit-log/flow/',
    stripURL: '/zato/audit-log/strip/',

    // The activity strip over the listing - where it renders, what it says with
    // nothing to draw, and how the pill reads a window clicked out of it
    stripHost: '#audit-log-strip',
    stripEmptyText: 'No events in this window',
    stripWindowSeparator: ' - ',

    // The name every source without a presenter of its own is drawn by
    defaultSource: 'default',

    // The overlay tab labels - the raw payload and its parsed EDI document view
    rawTabLabel: 'Raw',
    parsedTabLabel: 'Parsed',

    // The filter selects every rendering of the page carries - what each one is called,
    // what its everything entry says, what several picks at once are counted in, where
    // each one is rendered and the face its trigger wears - the rate limiting forms'
    // control look, kept in the kit under a common name
    sourceSelectLabel: 'Source',
    objectSelectLabel: 'Object',
    allSourcesLabel: 'All',
    allObjectsLabel: 'All',
    manySourcesLabel: 'sources',
    manyObjectsLabel: 'objects',

    // The source whose events record who viewed other sources' objects - the names
    // it carries are borrowed, so the object filter lists them under their owners
    logAccessSource: 'config',

    // The one source whose messages can run out of time, and the outcome only it
    // reports - the legend offers Expired only while this source is picked
    pubsubSource: 'pubsub',
    expiredOutcome: 'expired',
    // Short on purpose - it stands in the same badge All does, so swapping
    // the two must not resize the select
    noMatchesLabel: 'None',
    sourceSelectHost: '#audit-log-filter-source',
    objectSelectHost: '#audit-log-filter-object',
    filterTriggerCls: 'dashboard-select-face',

    // What the selects' picks are called in the address bar - distinct from the
    // per-source page's source and object_name, so the index view keeps serving
    // the all-events layout. The excluded picks travel under keys of their own.
    sourcesURLKey: 'sources',
    objectsURLKey: 'objects',
    sourcesExcludedURLKey: 'sources_excluded',
    objectsExcludedURLKey: 'objects_excluded',

    // What a trigger whose picks amount to everything-but starts its badge with,
    // and how each source's name reads inside that phrase when its casing changes
    // mid-sentence - assigned in init, from the same catalog the labels come from
    exceptLabel: 'All except',
    excludedLabel: 'excluded',
    sourceExceptLabels: {},

    // What the resubmit outcome is reported with - the message itself comes
    // display-ready from the backend
    resubmitModalTitle: 'Resubmit result',
    resubmitErrorLabel: 'Resubmit failed',
    resubmittedMarkerLabel: 'resubmitted',

    // The per-source column list and the resubmit labels keyed by source and event
    // type, both assigned in init
    columns: [],
    resubmitLabels: {},

    // Which source this page lists, which object of it and how this source's exchanges
    // open and close, all assigned in init. The cluster is always the default one -
    // pages that run init overwrite it with the same value the server rendered.
    source: '',
    objectName: '',
    clusterId: '1',
    exchange: {},

    // What one event's source is called on the screen, what its object is called,
    // where the source's and the object's own pages are, where an endpoint leads and
    // how one event type reads - all per source or per event type, all assigned in init
    sourceLabels: {},
    objectLinks: {},
    objectLabels: {},
    sourceLinks: {},
    endpointLinks: {},
    endpointLabels: {},
    runLinks: {},
    eventLabels: {},

    // The words the file transfer runs are described with, assigned in init.
    fileTransferWords: {},

    // What the object row is labelled with for a source the catalog does not know
    defaultObjectLabel: 'Object',

    // Where the audit log and the flow page live, what the flow page's term and
    // its way back are called in the address bar
    auditLogPagePath: '/zato/audit-log/',
    flowPagePath: '/zato/message-flow/',
    termURLKey: 'term',
    backURLKey: 'back'
};

// /////////////////////////////////////////////////////////////////////////////

// The audit log address a flow page opened from here leads back to - the audit log page
// itself with everything its address bar holds, filters and the open event alike, or the
// way back the flow page was itself given, so a search on the flow page keeps it. A page
// that is neither has no way back to offer.
$.fn.zato.audit_log.backURL = function() {
    var config = $.fn.zato.audit_log.config;
    var kit = $.fn.zato.dashboard_kit;

    var carried = kit.url_state.get(config.backURLKey);

    // Only an audit log address is a way back - a link cannot send a reader anywhere else
    if (carried !== null && carried.indexOf(config.auditLogPagePath) === 0) {
        return carried;
    }

    if (window.location.pathname === config.auditLogPagePath) {
        return window.location.pathname + window.location.search;
    }

    return '';
};

// /////////////////////////////////////////////////////////////////////////////

// The address of the flow page opened on one term, carrying the way back to the audit log
// when there is one to carry
$.fn.zato.audit_log.flowPageURL = function(term) {
    var config = $.fn.zato.audit_log.config;

    var params = new URLSearchParams();
    params.set(config.termURLKey, term);

    var backURL = $.fn.zato.audit_log.backURL();

    if (backURL !== '') {
        params.set(config.backURLKey, backURL);
    }

    return config.flowPagePath + '?' + params.toString();
};

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.audit_log.escapeHTML = function(value) {
    return String(value)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
};

// /////////////////////////////////////////////////////////////////////////////

// What one source is called on the screen. The log may hold a source this application's
// catalog does not know yet, which is then called by its own raw name.
$.fn.zato.audit_log.sourceLabel = function(source) {
    var label = $.fn.zato.audit_log.config.sourceLabels[source];

    if (label === undefined) {
        label = source;
    }

    return label;
};

// /////////////////////////////////////////////////////////////////////////////

// How one event type reads on the screen - "Request received" rather than its code.
// An event type the catalog does not know yet reads by its own raw name.
$.fn.zato.audit_log.eventLabel = function(eventType) {
    var label = $.fn.zato.audit_log.config.eventLabels[eventType];

    if (label === undefined) {
        label = eventType;
    }

    return label;
};

// /////////////////////////////////////////////////////////////////////////////

// Which presenter draws a row of a given source. A page reads its own source's rows, and a
// flow crosses sources, so an event is always drawn by the source that wrote it down.
$.fn.zato.audit_log.presenterFor = function(source) {
    var audit_log = $.fn.zato.audit_log;
    var presenter = audit_log.sources[source];

    // Only the sources with details of their own to show have a presenter,
    // every other one is drawn by the neutral default.
    if (presenter === undefined) {
        presenter = audit_log.sources[audit_log.config.defaultSource];
    }

    return presenter;
};

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.audit_log.presenter = function() {
    var audit_log = $.fn.zato.audit_log;

    return audit_log.presenterFor(audit_log.config.source);
};

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.audit_log.guessAceMode = function(text) {
    var trimmed = text.trim();

    // JSON documents start with an object or an array ..
    if (trimmed.indexOf('{') === 0 || trimmed.indexOf('[') === 0) {
        return 'ace/mode/json';
    }

    // .. XML documents start with an opening tag ..
    if (trimmed.indexOf('<') === 0) {
        return 'ace/mode/xml';
    }

    // .. anything else is left to the highlight pane's own detection, e.g. HL7 or tracebacks.
    return null;
};

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.audit_log.openMessageOverlay = function(eventId, cid) {
    var config = $.fn.zato.audit_log.config;

    $.ajax({
        url: config.detailsURL,
        type: 'POST',

        // The overlay reads whichever body the event has, whatever kind it turns out to be,
        // and it reads the whole of it because that is what it is opened for
        data: JSON.stringify({id: eventId, kind: '', preview: false}),
        contentType: 'application/json',
        headers: {'X-CSRFToken': $.cookie('csrftoken')},
        success: function(data) {
            if (typeof data === 'string') {
                data = JSON.parse(data);
            }

            var aceMode = $.fn.zato.audit_log.guessAceMode(data.data);

            // One button copies just the CID ..
            var copyCIDButton = {
                id: 'audit-log-copy-cid',
                label: 'Copy CID',
                on_click: function(buttonElement) {
                    $.fn.zato.ui_helpers.copy_to_clipboard(buttonElement, cid);
                }
            };

            // .. and the other one copies the whole message.
            var copyMessageButton = $.fn.zato.highlight_pane.buttons.copy();
            copyMessageButton.label = 'Copy message';

            var overlayConfig = {
                title: 'Message data',
                title_detail: cid,
                text: data.data,
                editable: false,
                ace_mode: aceMode,
                buttons: [copyCIDButton, copyMessageButton]
            };

            // A payload that carries an EDI document additionally gets its parsed view,
            // as a second tab next to the raw wire format.
            if (data.parsed !== '') {

                var rawMode = aceMode;
                if (rawMode === null) {
                    rawMode = $.fn.zato.highlight_pane.detect_ace_mode(data.data);
                }

                overlayConfig.tabs = [
                    {label: config.rawTabLabel, text: data.data, ace_mode: rawMode},
                    {label: config.parsedTabLabel, text: data.parsed, ace_mode: 'ace/mode/text'}
                ];
            }

            $.fn.zato.highlight_pane.open_overlay(overlayConfig);
        }
    });
};

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.audit_log.parseResubmitResponse = function(jqXHR, textStatus) {
    var config = $.fn.zato.audit_log.config;
    var body = jqXHR.responseText;

    // A non-2xx response carries an exception message rather than the display-ready shape ..
    var isHTTPOK = (jqXHR.status >= 200 && jqXHR.status < 300);

    if (!isHTTPOK) {
        return {
            is_success: false,
            label: config.resubmitErrorLabel,
            details_title: config.resubmitErrorLabel,
            details_body: body,
            details_lexer: '',
            status_code: jqXHR.status
        };
    }

    // .. the backend answers display-ready - a one-line summary for the tippy,
    // the details for the modal and the lexer they highlight with.
    var parsed = JSON.parse(body);

    // The new attempt and the marker on the original row appear once the table refreshes.
    var pagination = $.fn.zato.audit_log.pagination;
    pagination.fetch_page(pagination.current_page());

    // The transport itself answered with 200 whatever the resubmit's outcome,
    // so there is no status code to show
    return {
        is_success: parsed.is_success,
        label: parsed.message,
        details_title: parsed.message,
        details_body: parsed.details,
        details_lexer: parsed.details_lexer,
        status_code: 0
    };
};

// /////////////////////////////////////////////////////////////////////////////

// The activity strip over the listing, drawn out of what the strip endpoint counted -
// the same series and colours the outcome legend wears. A bucket click narrows the
// listing down to that bucket's window, the way a clicked stamp unit does.
$.fn.zato.audit_log.renderStrip = function(serverBuckets) {
    var kit = $.fn.zato.dashboard_kit;
    var config = $.fn.zato.audit_log.config;
    var palette = kit.palette.outcome;

    // The strip reads a count for every series it knows - the endpoint names
    // only the outcomes a bucket actually saw
    var buckets = [];

    for (var bucketIndex = 0; bucketIndex < serverBuckets.length; bucketIndex++) {
        var serverBucket = serverBuckets[bucketIndex];

        var bucket = {
            start: new Date(serverBucket.start_iso).getTime(),
            end: new Date(serverBucket.end_iso).getTime()
        };

        for (var keyIndex = 0; keyIndex < config.outcomes.length; keyIndex++) {
            var key = config.outcomes[keyIndex];

            if (key in serverBucket.counts) {
                bucket[key] = serverBucket.counts[key];
            } else {
                bucket[key] = 0;
            }
        }

        buckets.push(bucket);
    }

    kit.activity_strip.render({
        host: config.stripHost,
        series_keys: config.outcomes,
        colors: palette.bar_colors,
        labels: palette.labels,

        // The legend already filters the poll and the strip endpoint alike, so an
        // outcome switched off up there never reaches the strip in the first place
        hidden: {},
        empty_text: config.stripEmptyText,
        buckets: buckets,
        on_bucket_click: function(startISO, endISO) {
            var listing = $.fn.zato.audit_log.listing;

            var label = kit.format_local_time(startISO) +
                config.stripWindowSeparator + kit.format_local_time(endISO);

            listing.applyTimeWindow({label: label, time_from: startISO, time_to: endISO});
        }
    });
};

// /////////////////////////////////////////////////////////////////////////////

// Asks the strip endpoint for the events the listing's own filters match, counted
// into as many buckets as the strip has room for
$.fn.zato.audit_log.refreshStrip = function() {
    var kit = $.fn.zato.dashboard_kit;
    var config = $.fn.zato.audit_log.config;
    var stripConfig = kit.activity_strip.config;

    // A source whose events report no outcome at all has no series to draw
    if (config.outcomes.length === 0) {
        $(config.stripHost).hide();
        return;
    }

    var width = $(config.stripHost).width();

    var bucketCount = Math.min(stripConfig.max_buckets,
        Math.max(stripConfig.min_buckets, Math.floor(width / stripConfig.px_per_bucket)));

    var filters = $.fn.zato.audit_log.pagination.get_filters();

    var body = {
        sources: filters.sources,
        sources_excluded: filters.sources_excluded,
        object_names: filters.object_names,
        object_names_excluded: filters.object_names_excluded,
        outcomes: filters.outcomes,
        query: filters.query,
        status: filters.status,
        time_from: filters.time_from,
        time_to: filters.time_to,
        event_types: filters.event_types,
        statuses_excluded: filters.statuses_excluded,
        bucket_count: bucketCount
    };

    $.ajax({
        url: config.stripURL,
        type: 'POST',
        data: JSON.stringify(body),
        contentType: 'application/json',
        headers: {'X-CSRFToken': $.cookie('csrftoken')},
        success: function(data) {
            if (typeof data === 'string') {
                data = JSON.parse(data);
            }

            $.fn.zato.audit_log.renderStrip(data.buckets);
        }
    });
};

// /////////////////////////////////////////////////////////////////////////////

// The picks one URL param carries, comma-separated - an absent param is no picks
$.fn.zato.audit_log.filtersFromURL = function(key) {
    var params = new URLSearchParams(window.location.search);
    var value = params.get(key);

    if (value === null || value === '') {
        return [];
    }

    return value.split(',');
};

// /////////////////////////////////////////////////////////////////////////////

// Writes one select's picks into the address bar, so a reloaded page is the same page
$.fn.zato.audit_log.filtersToURL = function(key, values) {
    var params = new URLSearchParams(window.location.search);

    if (values.length) {
        params.set(key, values.join(','));
    } else {
        params.delete(key);
    }

    history.replaceState(null, '', '?' + params.toString());
};

// /////////////////////////////////////////////////////////////////////////////

// Where changed picks lead from a page rendered for one source - its columns were baked
// for that source at render time, so a change of picks is a navigation, not a re-poll.
// One included source with at most one included object and nothing excluded anywhere
// gets that source's own page, any other mix gets the all-events listing with all
// the picks, the excluded ones included, in the address.
$.fn.zato.audit_log.filterPicksURL = function(sources, objects, sourcesExcluded, objectsExcluded) {
    var config = $.fn.zato.audit_log.config;
    var params = new URLSearchParams();

    var hasExcludes = sourcesExcluded.length > 0 || objectsExcluded.length > 0;

    if (sources.length === 1 && objects.length <= 1 && !hasExcludes) {
        params.set('source', sources[0]);

        if (objects.length === 1) {
            params.set('object_name', objects[0]);
        }
    } else {
        if (sources.length) {
            params.set(config.sourcesURLKey, sources.join(','));
        }

        if (objects.length) {
            params.set(config.objectsURLKey, objects.join(','));
        }

        if (sourcesExcluded.length) {
            params.set(config.sourcesExcludedURLKey, sourcesExcluded.join(','));
        }

        if (objectsExcluded.length) {
            params.set(config.objectsExcludedURLKey, objectsExcluded.join(','));
        }
    }

    params.set('cluster', config.clusterId);

    return '/zato/audit-log/?' + params.toString();
};

})(jQuery);
