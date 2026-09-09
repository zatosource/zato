
// /////////////////////////////////////////////////////////////////////////////

// The audit log page - the filters, the actions and the page init.

(function($) {

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
    // so each name is listed once - the log access source borrows the names of the
    // objects whose viewings it records, and a borrowed name stands under its owner alone.
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

        // The owners claim their names first and the log access source keeps only
        // what no other source answered for ..
        for (var ownerIndex = 0; ownerIndex < filterOptions.length; ownerIndex++) {
            if (filterOptions[ownerIndex].source !== config.logAccessSource) {
                claim(filterOptions[ownerIndex]);
            }
        }

        for (var configIndex = 0; configIndex < filterOptions.length; configIndex++) {
            if (filterOptions[configIndex].source === config.logAccessSource) {
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
        excluded_label: config.excludedLabel,

        // An object's name is its own technical name, the same wherever it stands
        except_value_labels: {},
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
        excluded_label: config.excludedLabel,
        except_value_labels: config.sourceExceptLabels,
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
    config.sourceExceptLabels = initConfig.source_except_labels;
    config.objectLinks = initConfig.object_links;
    config.objectLabels = initConfig.object_labels;
    config.sourceLinks = initConfig.source_links;
    config.endpointLinks = initConfig.endpoint_links;
    config.endpointLabels = initConfig.endpoint_labels;
    config.runLinks = initConfig.run_links;
    config.eventLabels = initConfig.event_labels;
    config.fileTransferWords = initConfig.file_transfer_words;

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
            event_types: eventTypes,
            statuses_excluded: listing.statusesExcluded()
        },
        table_body: listing.config.itemsHost,

        // The rows still changing are sent with every request.
        get_active_items: listing.watchedIds,
        active_items_field: 'watched_ids',

        // The page links are read above the list only - the list is as tall as the page and
        // scrolls inside itself, so a second row of them at the foot of it would be reached
        // by scrolling the page it is meant to keep still
        container_top: '#audit-log-pagination-top',

        // The strip follows the listing - the same filters, redrawn whenever a page
        // of it arrives, whoever asked - a filter change, a page turn or the clock
        render_page: function(tableBody, rows, total, updated) {
            listing.renderPage(tableBody, rows, total, updated);

            $.fn.zato.audit_log.refreshStrip();
        }
    });

    // .. the resubmit outcome handler refreshes the table through this reference ..
    $.fn.zato.audit_log.pagination = pagination;

    // .. every rendering of the page gets its source and object filter selects,
    // a per-source one opening with its own source and object picked ..
    $.fn.zato.audit_log.initFilterSelects(initConfig.filter_options);

    // .. Clear follows the first character typed and the last one deleted, starting from
    // whatever term the page came up with, a term the pane set included, and clearing
    // the box asks for the whole log back ..
    $.fn.zato.audit_log.refreshSearchClear = searchClear.init({
        input: document.getElementById('audit-log-search-input'),
        button: document.getElementById('audit-log-search-clear'),
        onClear: function() { $('#audit-log-search-form').submit(); },
    });

    // .. let the search form filter the events - a term put into the box programmatically
    // fires no input event, so the badge is refreshed here as well ..
    $('#audit-log-search-form').on('submit', function(event) {
        event.preventDefault();

        var query = $('#audit-log-search-input').val();

        $.fn.zato.audit_log.refreshSearchClear();

        pagination.set_filters({query: query});
        pagination.fetch_page(1);
    });

    // .. each resubmit link sends its row's payload out again, with the source's warning first if it has one ..
    $(document).on('click', '.audit-log-resubmit-link', function(event) {
        event.preventDefault();

        var rowModel = listing.modelById(this.getAttribute('data-id'));

        if (rowModel !== null) {
            var presenter = $.fn.zato.audit_log.presenterFor(rowModel.raw.source);
            var warning = presenter.resubmitWarning(rowModel);

            if (warning !== '') {
                var $row = $(this).closest('.audit-log-row');
                listing.openResubmitConfirm(rowModel, $row, warning);
                return;
            }
        }

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

})(jQuery);
