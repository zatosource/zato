

// /////////////////////////////////////////////////////////////////////////////

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
    accessLogSource: 'config',

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

    // What a trigger whose picks amount to everything-but starts its badge with
    exceptLabel: 'All except',

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
    eventLabels: {},

    // What the object row is labelled with for a source the catalog does not know
    defaultObjectLabel: 'Object'
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

// /////////////////////////////////////////////////////////////////////////////

// The filter selects - one for the sources, one for the object. Any number of sources
// can be picked at once - the picks narrow both the list and what the object select
// has to offer - and picking an object narrows the list to it alone.
$.fn.zato.audit_log.initFilterSelects = function(filterOptions) {
    var kit = $.fn.zato.dashboard_kit;
    var config = $.fn.zato.audit_log.config;
    var pagination = $.fn.zato.audit_log.pagination;
    var listing = $.fn.zato.audit_log.listing;

    // Expired is a pub/sub outcome alone, so the legend offers it only while
    // pub/sub is among the picked sources
    var legendOutcomes = function(pickedSources) {
        var out = [];

        for (var outcomeIndex = 0; outcomeIndex < config.outcomes.length; outcomeIndex++) {
            var outcome = config.outcomes[outcomeIndex];

            if (outcome === config.expiredOutcome && pickedSources.indexOf(config.pubsubSource) === -1) {
                continue;
            }

            out.push(outcome);
        }

        return out;
    };

    // Every source there is, whether or not it has events yet
    var sourceItems = [];

    for (var optionIndex = 0; optionIndex < filterOptions.length; optionIndex++) {
        var option = filterOptions[optionIndex];

        sourceItems.push({value: option.source, label: option.label});
    }

    // The sources a set of picks amounts to - the included ones when there are any,
    // every source there is minus the excluded ones when only excludes are on, and
    // the empty list, which stands for everything untouched, when nothing is picked
    // at all. This is what the object groups on offer and the legend's outcomes follow.
    var effectiveSources = function(included, excluded) {
        if (included.length) {
            return included;
        }

        if (excluded.length === 0) {
            return [];
        }

        var out = [];

        for (var sourceIndex = 0; sourceIndex < sourceItems.length; sourceIndex++) {
            var sourceValue = sourceItems[sourceIndex].value;

            if (excluded.indexOf(sourceValue) === -1) {
                out.push(sourceValue);
            }
        }

        return out;
    };

    // The objects on offer, grouped by their source - all of them when no source is
    // picked, the picked sources' own when some are. Nothing picked means every one,
    // so there is no All entry of its own. The filter matches events by name alone,
    // so each name is listed once - the access log borrows the names of the objects
    // whose viewings it records, and a borrowed name stands under its owner alone.
    var objectGroups = function(pickedSources) {
        var out = [];

        var seen = {};
        var itemsBySource = {};

        var claim = function(option) {
            if (pickedSources.length && pickedSources.indexOf(option.source) === -1) {
                return;
            }

            var items = [];

            for (var objectIndex = 0; objectIndex < option.objects.length; objectIndex++) {
                var name = option.objects[objectIndex];

                if (seen[name]) {
                    continue;
                }

                seen[name] = true;
                items.push({value: name, label: name});
            }

            itemsBySource[option.source] = items;
        };

        // The owners claim their names first and the access log keeps only what
        // no other source answered for ..
        for (var ownerIndex = 0; ownerIndex < filterOptions.length; ownerIndex++) {
            if (filterOptions[ownerIndex].source !== config.accessLogSource) {
                claim(filterOptions[ownerIndex]);
            }
        }

        for (var configIndex = 0; configIndex < filterOptions.length; configIndex++) {
            if (filterOptions[configIndex].source === config.accessLogSource) {
                claim(filterOptions[configIndex]);
            }
        }

        // .. and the groups keep the catalog's own order whoever claimed first.
        for (var optionIndex = 0; optionIndex < filterOptions.length; optionIndex++) {
            var option = filterOptions[optionIndex];
            var items = itemsBySource[option.source];

            if (items === undefined || items.length === 0) {
                continue;
            }

            out.push({group: option.label, items: items});
        }

        return out;
    };

    // Whether an object is still on offer once the sources have changed underneath it
    var hasObject = function(groups, value) {
        for (var groupIndex = 0; groupIndex < groups.length; groupIndex++) {
            var items = groups[groupIndex].items;

            for (var itemIndex = 0; itemIndex < items.length; itemIndex++) {
                if (items[itemIndex].value === value) {
                    return true;
                }
            }
        }

        return false;
    };

    // A page rendered for one source opens with that source and its object picked,
    // and any change of picks leaves for the page the new picks belong to
    var isSourcePage = config.source !== '';

    var pickedSources;
    var pickedObjects;
    var pickedSourcesExcluded;
    var pickedObjectsExcluded;

    if (isSourcePage) {
        pickedSources = [config.source];
        pickedObjects = config.objectName === '' ? [] : [config.objectName];

        // A per-source page is its one source whole - nothing of it is excluded
        pickedSourcesExcluded = [];
        pickedObjectsExcluded = [];
    } else {

        // The picks the address bar carries, so a reloaded page starts where it was left
        pickedSources = $.fn.zato.audit_log.filtersFromURL(config.sourcesURLKey);
        pickedObjects = $.fn.zato.audit_log.filtersFromURL(config.objectsURLKey);
        pickedSourcesExcluded = $.fn.zato.audit_log.filtersFromURL(config.sourcesExcludedURLKey);
        pickedObjectsExcluded = $.fn.zato.audit_log.filtersFromURL(config.objectsExcludedURLKey);
    }

    var initialObjectGroups = objectGroups(effectiveSources(pickedSources, pickedSourcesExcluded));

    var objectSelect = kit.select.create({
        host: config.objectSelectHost,
        trigger_cls: config.filterTriggerCls,
        label: config.objectSelectLabel,
        groups: initialObjectGroups,
        multi: true,
        tri_state: true,
        values: pickedObjects,
        excluded_values: pickedObjectsExcluded,
        empty_label: config.allObjectsLabel,
        many_label: config.manyObjectsLabel,
        except_label: config.exceptLabel,
        disabled_label: config.noMatchesLabel,
        on_change: function(values, excluded) {

            // A page baked for one source has no way to redraw itself around the new
            // picks, so they are taken to the page that owns them
            if (isSourcePage) {
                window.location = $.fn.zato.audit_log.filterPicksURL(
                    sourceSelect.get_values(), values, sourceSelect.get_excluded(), excluded);
                return;
            }

            $.fn.zato.audit_log.filtersToURL(config.objectsURLKey, values);
            $.fn.zato.audit_log.filtersToURL(config.objectsExcludedURLKey, excluded);

            pagination.set_filters({object_names: values, object_names_excluded: excluded});
            pagination.fetch_page(1);
        }
    });

    // With no objects on offer there is nothing to filter by and the select stands aside
    objectSelect.set_enabled(initialObjectGroups.length > 0);

    var sourceSelect = kit.select.create({
        host: config.sourceSelectHost,
        trigger_cls: config.filterTriggerCls,
        label: config.sourceSelectLabel,
        groups: [{group: '', items: sourceItems}],
        multi: true,
        tri_state: true,
        values: pickedSources,
        excluded_values: pickedSourcesExcluded,
        empty_label: config.allSourcesLabel,
        many_label: config.manySourcesLabel,
        except_label: config.exceptLabel,
        on_change: function(values, excluded) {
            var newGroups = objectGroups(effectiveSources(values, excluded));

            // An object of some source no longer on offer is no filter for these,
            // whether it was picked in or picked out
            var pickedObjects = objectSelect.get_values();
            var keptObjects = [];

            for (var pickedIndex = 0; pickedIndex < pickedObjects.length; pickedIndex++) {
                if (hasObject(newGroups, pickedObjects[pickedIndex])) {
                    keptObjects.push(pickedObjects[pickedIndex]);
                }
            }

            var excludedObjects = objectSelect.get_excluded();
            var keptObjectsExcluded = [];

            for (var excludedIndex = 0; excludedIndex < excludedObjects.length; excludedIndex++) {
                if (hasObject(newGroups, excludedObjects[excludedIndex])) {
                    keptObjectsExcluded.push(excludedObjects[excludedIndex]);
                }
            }

            // A page baked for one source has no way to redraw itself around the new
            // picks, so they are taken to the page that owns them
            if (isSourcePage) {
                window.location = $.fn.zato.audit_log.filterPicksURL(
                    values, keptObjects, excluded, keptObjectsExcluded);
                return;
            }

            objectSelect.set_groups(newGroups);
            objectSelect.set_values(keptObjects);
            objectSelect.set_excluded(keptObjectsExcluded);
            objectSelect.set_enabled(newGroups.length > 0);

            $.fn.zato.audit_log.filtersToURL(config.sourcesURLKey, values);
            $.fn.zato.audit_log.filtersToURL(config.sourcesExcludedURLKey, excluded);
            $.fn.zato.audit_log.filtersToURL(config.objectsURLKey, keptObjects);
            $.fn.zato.audit_log.filtersToURL(config.objectsExcludedURLKey, keptObjectsExcluded);

            // The legend's offer follows the sources the picks amount to, so what its
            // badges mean as a filter is recomputed along with it
            var newOutcomes = legendOutcomes(effectiveSources(values, excluded));
            listing.buildLegend(newOutcomes);

            pagination.set_filters({
                sources: values,
                sources_excluded: excluded,
                object_names: keptObjects,
                object_names_excluded: keptObjectsExcluded,
                outcomes: listing.pickedOutcomes(newOutcomes)
            });
            pagination.fetch_page(1);
        }
    });

    // A page rendered for one source built its legend from that source's own outcomes
    // already - only the all-events legend follows the picks, without Expired unless
    // pub/sub is among the sources they amount to
    if (!isSourcePage) {
        listing.buildLegend(legendOutcomes(effectiveSources(pickedSources, pickedSourcesExcluded)));
    }
};

// /////////////////////////////////////////////////////////////////////////////

// Puts one term into the search box and asks for the page it narrows down to, which is what
// the Search beside a value in the detail pane does
$.fn.zato.audit_log.search = function(query) {
    $('#audit-log-search-input').val(query);
    $('#audit-log-search-form').submit();
};

// /////////////////////////////////////////////////////////////////////////////

// Clear stands in the box only while there is a term in it to be cleared
$.fn.zato.audit_log.showSearchClear = function() {
    $('#audit-log-search-clear').toggle($('#audit-log-search-input').val() !== '');
};

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.audit_log.resubmit = function(linkElement) {
    var config = $.fn.zato.audit_log.config;

    var eventId = linkElement.getAttribute('data-id');

    $.fn.zato.action_runner.run({
        link_elem: linkElement,
        url: config.resubmitURL,
        data: 'id=' + encodeURIComponent(eventId),
        parse: $.fn.zato.audit_log.parseResubmitResponse,
        details_modal_title: config.resubmitModalTitle
    });
};

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.audit_log.init = function(initConfig) {
    var kit = $.fn.zato.dashboard_kit;
    var config = $.fn.zato.audit_log.config;

    // The columns to render, the outcomes to offer as filters and the resubmit labels come
    // from the server, per source ..
    config.columns = initConfig.columns;
    config.outcomes = initConfig.outcomes;
    config.resubmitLabels = initConfig.resubmitLabels;
    config.source = initConfig.source;
    config.exchange = initConfig.exchange;
    config.objectName = initConfig.object_name;
    config.clusterId = initConfig.cluster_id;
    config.sourceLabels = initConfig.source_labels;
    config.objectLinks = initConfig.object_links;
    config.objectLabels = initConfig.object_labels;
    config.sourceLinks = initConfig.source_links;
    config.endpointLinks = initConfig.endpoint_links;
    config.endpointLabels = initConfig.endpoint_labels;
    config.eventLabels = initConfig.event_labels;

    // .. the listing puts its chrome and its two panes in place before the first page arrives ..
    var listing = $.fn.zato.audit_log.listing;
    listing.init(initConfig);

    // .. the first page is read through whichever window the page was opened on, which is
    // the one the address named or, failing that, the range this screen was last left on ..
    var timeFrom = initConfig.time_from;

    if (timeFrom === '') {
        timeFrom = listing.rangeTimeFrom();
    }

    // .. wire up the paginated listing - a per-source page polls for its one source
    // and one object, the all-events page starts with whatever picks the address
    // bar carries, so a reload keeps the filters ..
    var sources = [];
    var objectNames = [];
    var sourcesExcluded = [];
    var objectNamesExcluded = [];

    if (initConfig.source !== '') {
        sources.push(initConfig.source);

        if (initConfig.object_name !== '') {
            objectNames.push(initConfig.object_name);
        }
    } else {
        sources = $.fn.zato.audit_log.filtersFromURL(config.sourcesURLKey);
        objectNames = $.fn.zato.audit_log.filtersFromURL(config.objectsURLKey);
        sourcesExcluded = $.fn.zato.audit_log.filtersFromURL(config.sourcesExcludedURLKey);
        objectNamesExcluded = $.fn.zato.audit_log.filtersFromURL(config.objectsExcludedURLKey);
    }

    // A page deep-linked to events of one kind opens filtered down to them,
    // with the dismissible chip beside the legend saying so
    var eventTypes = [];

    if (initConfig.event_type !== '') {
        eventTypes.push(initConfig.event_type);
    }

    var pagination = kit.pagination.init({
        poll_url: initConfig.poll_url,
        page_size: config.pageSize,
        filters: {
            sources: sources,
            sources_excluded: sourcesExcluded,
            object_names: objectNames,
            object_names_excluded: objectNamesExcluded,
            outcomes: [],
            query: initConfig.query,
            status: initConfig.status,
            time_from: timeFrom,
            time_to: initConfig.time_to,
            event_types: eventTypes
        },
        table_body: listing.config.itemsHost,

        // The page links are read above the list only - the list is as tall as the page and
        // scrolls inside itself, so a second row of them at the foot of it would be reached
        // by scrolling the page it is meant to keep still
        container_top: '#audit-log-pagination-top',

        // The strip follows the listing - the same filters, redrawn whenever a page
        // of it arrives, whoever asked - a filter change, a page turn or the clock
        render_page: function(tableBody, rows, total) {
            listing.renderPage(tableBody, rows, total);

            $.fn.zato.audit_log.refreshStrip();
        }
    });

    // .. the resubmit outcome handler refreshes the table through this reference ..
    $.fn.zato.audit_log.pagination = pagination;

    // .. every rendering of the page gets its source and object filter selects,
    // a per-source one opening with its own source and object picked ..
    $.fn.zato.audit_log.initFilterSelects(initConfig.filter_options);

    // .. let the search form filter the events ..
    $('#audit-log-search-form').on('submit', function(event) {
        event.preventDefault();

        var query = $('#audit-log-search-input').val();

        $.fn.zato.audit_log.showSearchClear();

        pagination.set_filters({query: query});
        pagination.fetch_page(1);
    });

    // .. Clear follows the first character typed and the last one deleted, starting from
    // whatever term the page came up with, a term the pane set included ..
    $.fn.zato.audit_log.showSearchClear();

    $('#audit-log-search-input').on('input', $.fn.zato.audit_log.showSearchClear);

    // .. and clearing the box asks for the whole log back ..
    $('#audit-log-search-clear').on('click', function() {
        $('#audit-log-search-input').val('');
        $.fn.zato.audit_log.showSearchClear();
        $('#audit-log-search-form').submit();
    });

    // .. each resubmit link sends its row's payload out again ..
    $(document).on('click', '.audit-log-resubmit-link', function(event) {
        event.preventDefault();

        $.fn.zato.audit_log.resubmit(this);
    });

    // .. and let each CID open the complete message of its event in an overlay.
    $(document).on('click', '.audit-log-cid-link', function(event) {
        event.preventDefault();

        var eventId = parseInt($(this).attr('data-id'), 10);
        var cid = $(this).attr('data-cid');

        $.fn.zato.audit_log.openMessageOverlay(eventId, cid);
    });
};

// /////////////////////////////////////////////////////////////////////////////

})(jQuery);
