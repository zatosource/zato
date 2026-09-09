

// /////////////////////////////////////////////////////////////////////////////

// Building the listing on page load.

(function($) {

var kit = $.fn.zato.dashboard_kit;
var listing = $.fn.zato.audit_log.listing;

// /////////////////////////////////////////////////////////////////////////////

listing.initChrome = function(initConfig) {
    var config = listing.config;

    $(config.chromeHost).html(listing.chromeHTML());

    // A page deep-linked to events of one kind opens with the chip already saying so.
    listing.eventFilter = initConfig.event_type;
    listing.initHideUnchanged();
    listing.drawEventFilterChip();

    kit.auto_refresh.init({
        pill: '#audit-log-refresh-pill',
        menu: '#audit-log-refresh-menu',
        storage_key: config.refreshStorageKey,
        url_param: 'refresh',
        default_seconds: config.refreshDefaultSeconds,
        on_tick: listing.refreshLive
    });

    var rangeConfig = {
        pill: '#' + config.rangePillId + '-pill',
        menu: '#' + config.rangePillId + '-menu',
        storage_key: config.rangeStorageKey,
        on_change: function(minutes) {
            listing.setRange(minutes);
            listing.applyRange();
        }
    };

    // A page opened on a window of its own - one clicked on an analytics chart - is read
    // through that window, so the range this screen was last left on does not overwrite it.
    if (initConfig.time_from !== '' || initConfig.time_to !== '') {
        rangeConfig.initial_minutes = 0;
    }

    var range = kit.time_range.init(rangeConfig);

    // The range this screen was left on last time is the one it opens on, and the pill
    // says so before the first page has even arrived.
    listing.setRange(range.get_minutes());

    // A page opened on a window of its own - a reloaded scrub pick, a link handed on -
    // reads that window off the address, so the pill says the window rather than All
    if (initConfig.time_from !== '' && initConfig.time_to !== '') {
        listing.minutes = 0;

        $('#' + config.rangePillId + '-pill').text(kit.time_scrub.window_label(
            new Date(initConfig.time_from), new Date(initConfig.time_to)));
    }

    // The legend offers this source's own outcomes - a delivery running out of time is
    // something only a pub/sub message does, and an HL7 log is not asked about it.
    listing.buildLegend($.fn.zato.audit_log.config.outcomes);

    // Every stamp on the page is a scrubber, and a clicked unit of one becomes the window
    kit.time_scrub.init({
        on_pick: function(picked) {
            listing.applyTimeWindow(picked);
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

        // The log is the page - it takes the room the window has left below the search box and
        // the pills, and the list and the pane are scrolled inside it rather than the page
        // being scrolled to reach the foot of them
        fit_height: true,

        list_html: listHTML,
        items_host: config.itemsHost,
        item_selector: config.itemSelector,

        id_of: function(rowModel) { return rowModel.id; },
        render_item: listing.rowHTML,
        render_empty: listing.emptyRowHTML,
        render_detail: listing.paneHTML,
        update_detail: listing.paneUpdate,
        empty_detail: '<div class="dashboard-inline-empty">' + config.emptyPane + '</div>',
        no_items_detail: '<div class="dashboard-inline-empty">' + config.emptyPaneNoEvents + '</div>',
        on_select: listing.onSelect
    });

    listing.panes.items_host().html(listing.loadingRowHTML());

    // The list is dragged wider and narrower by hand, so what fits is worked out again whenever
    // it changes size rather than only when a page of events arrives, and the rail beside it is
    // brought back level at the same time
    var listElement = listing.panes.items_host().closest('table').parent()[0];

    new ResizeObserver(function() {
        listing.fitColumns();
        listing.rail.sync();
    }).observe(listElement);

    // The rows scroll under the rail, so their marks follow them down it
    listElement.addEventListener('scroll', listing.rail.schedule);
};

// /////////////////////////////////////////////////////////////////////////////

listing.init = function(initConfig) {
    listing.initChrome(initConfig);
    listing.initPanes(initConfig.source);

    // A link naming an event opens on it - the selection is made before the first page has
    // arrived, and the page that arrives keeps whatever is already selected on it.
    var urlEvent = kit.url_state.get(listing.config.eventURLKey);

    if (urlEvent !== null && urlEvent !== '') {
        listing.panes.select(urlEvent);

        // A link out of an alert may additionally ask for the resubmit confirmation
        // on that event - honoured once the page holding the event is on screen
        var urlAction = kit.url_state.get(listing.config.actionURLKey);

        if (urlAction === listing.config.resubmitAction) {
            listing.pendingAction = urlEvent;
        }
    }

    // The events sharing a value are asked for wherever that value is named - the Details tab
    // and the panel a flow line opens
    $(document).on('click', listing.config.host + ' .dashboard-fact-row-search', function(event) {
        event.stopPropagation();

        $.fn.zato.audit_log.search($(this).attr('data-search-value'));
    });

    // An event word narrows the list down to events of its kind, wherever it is worn -
    // on a row or in the pane. The click filters, it does not also select the row under it.
    $(document).on('click', '.audit-log-event-filter', function(event) {
        event.preventDefault();
        event.stopPropagation();

        listing.applyEventFilter($(this).attr('data-event-type'));
    });

    // The chip's cross asks for every kind of event back
    $(document).on('click', '.audit-log-unchanged-toggle', function() {
        listing.toggleHideUnchanged();
    });

    $(document).on('click', '.audit-log-filter-chip-clear', function() {
        listing.clearEventFilter();
    });

    // An outcome badge drives the legend the way clicking the legend itself does
    $(document).on('click', '.audit-log-outcome-filter', function(event) {
        event.stopPropagation();

        listing.applyOutcomeFilter($(this).attr('data-outcome'));
    });

    // The way the message is being read goes into the address bar, parsed being taken as
    // read there the same way it is on the screen
    $(document).on('click', listing.config.payloadHost + ' .dashboard-payload-tab', function() {
        var config = listing.config;
        var tab = listing.detailTabs()[Number($(this).attr('data-tab-index'))];

        var view = '';

        if (!tab.parsed) {
            view = config.rawView;
        }

        var updates = {};
        updates[config.viewURLKey] = view;

        kit.url_state.replace(updates);
    });

    // A lineage marker of an event on this page selects it, and one of an event on
    // a page of its own has nothing to select here.
    $(document).on('click', '.audit-log-lineage', function() {
        var eventId = $(this).attr('data-lineage-id');

        if (listing.modelById(eventId) !== null) {
            listing.panes.select(eventId);
        }
    });

};

})(jQuery);
