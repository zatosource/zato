

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

    // The name every source without a presenter of its own is drawn by
    defaultSource: 'default',

    // The overlay tab labels - the raw payload and its parsed EDI document view
    rawTabLabel: 'Raw',
    parsedTabLabel: 'Parsed',

    // The filter selects of the all-events page - what each one is called, what its
    // everything entry says, what several picks at once are counted in, where each
    // one is rendered and the face its trigger wears - the rate limiting forms'
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
    // Short on purpose - it stands in the same badge All does, so swapping
    // the two must not resize the select
    noMatchesLabel: 'None',
    sourceSelectHost: '#audit-log-filter-source',
    objectSelectHost: '#audit-log-filter-object',
    filterTriggerCls: 'dashboard-select-face',

    // What the resubmit outcome is reported with
    resubmitModalTitle: 'Resubmit result',
    resubmitErrorLabel: 'Resubmit failed',
    resentLabel: 'Resent',
    reprocessedLabel: 'Reprocessed to',
    reprocessedDocumentsLabel: 'documents',
    resubmittedMarkerLabel: 'resubmitted',

    // The per-source column list and resubmit labels, assigned in init
    columns: [],
    resubmitLabels: {},

    // Which source this page lists, which object of it and how this source's exchanges
    // open and close, all assigned in init. The cluster is always the default one -
    // pages that run init overwrite it with the same value the server rendered.
    source: '',
    objectName: '',
    clusterId: '1',
    exchange: {}
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

$.fn.zato.audit_log.buildResubmitLabel = function(report) {
    var config = $.fn.zato.audit_log.config;

    // A resubmit that raised an exception carries its traceback in the details ..
    if (report.error) {
        return config.resubmitErrorLabel;
    }

    // .. a reprocess is reported by where the payload went, with the document count
    // added when the delivery carried attachments next to the EDI document ..
    if (report.action === 'reprocess') {
        var label = config.reprocessedLabel + ' ' + report.target_kind + ' ' + report.target_name;

        if (report.message_count > 1) {
            label = label + ' (' + report.message_count + ' ' + config.reprocessedDocumentsLabel + ')';
        }

        return label;
    }

    // .. and a resend by the CID its new attempt travels under.
    return config.resentLabel + '; CID ' + report.cid;
};

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.audit_log.parseResubmitResponse = function(jqXHR, textStatus) {
    var config = $.fn.zato.audit_log.config;
    var body = jqXHR.responseText;

    // A non-2xx response carries an exception message rather than a report ..
    var isHTTPOK = (jqXHR.status >= 200 && jqXHR.status < 300);

    if (!isHTTPOK) {
        return {
            is_success: false,
            label: config.resubmitErrorLabel,
            details_title: config.resubmitErrorLabel,
            details_body: body
        };
    }

    // .. a report is JSON with the outcome inside.
    var report = JSON.parse(body);
    var label = $.fn.zato.audit_log.buildResubmitLabel(report);

    // The new attempt and the marker on the original row appear once the table refreshes.
    var pagination = $.fn.zato.audit_log.pagination;
    pagination.fetch_page(pagination.current_page());

    return {
        is_success: report.is_ok,
        label: label,
        details_title: label,
        details_body: JSON.stringify(report, null, 2)
    };
};

// /////////////////////////////////////////////////////////////////////////////

// The filter selects of the all-events page - one for the sources, one for the object.
// Any number of sources can be picked at once - the picks narrow both the list and what
// the object select has to offer - and picking an object narrows the list to it alone.
$.fn.zato.audit_log.initFilterSelects = function(filterOptions) {
    var kit = $.fn.zato.dashboard_kit;
    var config = $.fn.zato.audit_log.config;
    var pagination = $.fn.zato.audit_log.pagination;

    // Every source there is, whether or not it has events yet
    var sourceItems = [];

    for (var optionIndex = 0; optionIndex < filterOptions.length; optionIndex++) {
        var option = filterOptions[optionIndex];

        sourceItems.push({value: option.source, label: option.label});
    }

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

    var initialObjectGroups = objectGroups([]);

    var objectSelect = kit.select.create({
        host: config.objectSelectHost,
        trigger_cls: config.filterTriggerCls,
        label: config.objectSelectLabel,
        groups: initialObjectGroups,
        multi: true,
        values: [],
        empty_label: config.allObjectsLabel,
        many_label: config.manyObjectsLabel,
        disabled_label: config.noMatchesLabel,
        on_change: function(values) {
            pagination.set_filters({object_names: values});
            pagination.fetch_page(1);
        }
    });

    // With no objects on offer there is nothing to filter by and the select stands aside
    objectSelect.set_enabled(initialObjectGroups.length > 0);

    kit.select.create({
        host: config.sourceSelectHost,
        trigger_cls: config.filterTriggerCls,
        label: config.sourceSelectLabel,
        groups: [{group: '', items: sourceItems}],
        multi: true,
        values: [],
        empty_label: config.allSourcesLabel,
        many_label: config.manySourcesLabel,
        on_change: function(values) {
            var newGroups = objectGroups(values);

            // An object of some source no longer picked is no filter for these
            var pickedObjects = objectSelect.get_values();
            var keptObjects = [];

            for (var pickedIndex = 0; pickedIndex < pickedObjects.length; pickedIndex++) {
                if (hasObject(newGroups, pickedObjects[pickedIndex])) {
                    keptObjects.push(pickedObjects[pickedIndex]);
                }
            }

            objectSelect.set_groups(newGroups);
            objectSelect.set_values(keptObjects);
            objectSelect.set_enabled(newGroups.length > 0);

            pagination.set_filters({sources: values, object_names: keptObjects});
            pagination.fetch_page(1);
        }
    });
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
    // and one object, the all-events page starts with every one of both ..
    var sources = [];

    if (initConfig.source !== '') {
        sources.push(initConfig.source);
    }

    var objectNames = [];

    if (initConfig.object_name !== '') {
        objectNames.push(initConfig.object_name);
    }

    var pagination = kit.pagination.init({
        poll_url: initConfig.poll_url,
        page_size: config.pageSize,
        filters: {
            sources: sources,
            object_names: objectNames,
            query: initConfig.query,
            status: initConfig.status,
            time_from: timeFrom,
            time_to: initConfig.time_to
        },
        table_body: listing.config.itemsHost,

        // The page links are read above the list only - the list is as tall as the page and
        // scrolls inside itself, so a second row of them at the foot of it would be reached
        // by scrolling the page it is meant to keep still
        container_top: '#audit-log-pagination-top',
        render_page: listing.renderPage
    });

    // .. the resubmit outcome handler refreshes the table through this reference ..
    $.fn.zato.audit_log.pagination = pagination;

    // .. the all-events page - the one with sources to choose between at all - gets
    // its source and object filter selects ..
    if (initConfig.filter_options.length) {
        $.fn.zato.audit_log.initFilterSelects(initConfig.filter_options);
    }

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
