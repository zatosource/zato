

// /////////////////////////////////////////////////////////////////////////////

// The chrome above the list - the range, the legend and the filters.

(function($) {

var kit = $.fn.zato.dashboard_kit;
var listing = $.fn.zato.audit_log.listing;

// /////////////////////////////////////////////////////////////////////////////

// The live pill, the range pill and the legend that narrows the list down to one outcome
listing.chromeHTML = function() {
    var config = listing.config;
    var rangePillId = config.rangePillId;

    var html = '<div class="detail-header-controls">';

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

    // A source whose events report no outcome at all is offered no legend either.
    if ($.fn.zato.audit_log.config.outcomes.length) {
        html += '<div class="dashboard-chart-legend" id="' + config.legendHost.slice(1) + '"></div>';
    }

    // Where the event filter says which kind of event the list is narrowed down to,
    // holding nothing while no event word has been clicked
    html += '<span id="' + config.eventChipHost.slice(1) + '"></span>';

    html += '</div>';

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

// The moment the range now picked reaches back to, as the poll reads it, and nothing at all
// when the range is the whole log. Event times are stored as UTC with the offset spelled out,
// and the comparison is made on the text of them, so the cutoff is written the same way.
listing.rangeTimeFrom = function() {
    if (listing.minutes === 0) {
        return '';
    }

    var cutoff = new Date(Date.now() - listing.minutes * 60000);
    var out = cutoff.toISOString().replace('Z', '+00:00');

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// A window the reader has just picked, asked of the whole log rather than of the page that
// happens to be open, so the count and the pages agree with what is on the screen. A preset
// replaces whatever window a clicked stamp had picked, its far edge and its address included.
listing.applyRange = function() {
    var pagination = $.fn.zato.audit_log.pagination;

    kit.url_state.replace({time_from: '', time_to: ''});

    pagination.set_filters({time_from: listing.rangeTimeFrom(), time_to: ''});
    pagination.fetch_page(1);
};

// /////////////////////////////////////////////////////////////////////////////

// The window one clicked stamp unit means - the range pill reads it back and the address
// bar carries it, so the view deep-links. It is not a rolling range, so the live refresh
// leaves its edges where the click put them.
listing.applyTimeWindow = function(picked) {
    listing.minutes = 0;

    $('#' + listing.config.rangePillId + '-pill').text(picked.label);

    kit.url_state.replace({time_from: picked.time_from, time_to: picked.time_to});

    var pagination = $.fn.zato.audit_log.pagination;
    pagination.set_filters({time_from: picked.time_from, time_to: picked.time_to});
    pagination.fetch_page(1);
};

// /////////////////////////////////////////////////////////////////////////////

listing.refresh = function() {
    var pagination = $.fn.zato.audit_log.pagination;
    pagination.fetch_page(pagination.current_page());
};

// /////////////////////////////////////////////////////////////////////////////

// The same page asked for again by the clock rather than by the reader, which is the one
// case where what has arrived since is worth pointing out
listing.refreshLive = function() {
    listing.isLive = true;

    // A window reaching back from now rolls with it, so the cutoff is worked out again at
    // every tick rather than staying where it stood when the range was picked. A page
    // opened on a window of its own reports no range and keeps the window it was given.
    if (listing.minutes > 0) {
        $.fn.zato.audit_log.pagination.set_filters({time_from: listing.rangeTimeFrom()});
    }

    listing.refresh();
};

// /////////////////////////////////////////////////////////////////////////////

// What the legend still has switched on, as the filter the poll takes - the badges
// name the outcomes to show, and all of them on means no filter at all, so events
// reporting no outcome of their own stay on the page too
listing.pickedOutcomes = function(outcomes) {
    var visible = [];

    for (var outcomeIndex = 0; outcomeIndex < outcomes.length; outcomeIndex++) {
        var outcome = outcomes[outcomeIndex];

        if (!listing.hidden[outcome]) {
            visible.push(outcome);
        }
    }

    if (visible.length === outcomes.length) {
        return [];
    }

    return visible;
};

// The legend that narrows the list down to one outcome - built afresh whenever what
// the rows can report changes, e.g. the picked sources no longer include the one
// whose messages can expire. A toggled badge asks the server for page one of what
// is left, it does not hide rows of the page already here.
listing.buildLegend = function(outcomes) {
    var config = listing.config;
    var palette = kit.palette.outcome;

    // A clicked outcome badge elsewhere on the page drives this same legend,
    // so what it now offers is kept at hand
    listing.currentOutcomes = outcomes;

    if (!outcomes.length) {
        return;
    }

    kit.build_legend({
        container: config.legendHost,
        series_keys: outcomes,
        palette: palette.bar_colors,
        labels: palette.labels,
        text_colors: palette.colors,
        backgrounds: palette.backgrounds,
        hidden: listing.hidden,
        on_toggle: function() {
            var pagination = $.fn.zato.audit_log.pagination;

            pagination.set_filters({outcomes: listing.pickedOutcomes(outcomes)});
            pagination.fetch_page(1);
        }
    });
};

// /////////////////////////////////////////////////////////////////////////////

// The chip beside the legend saying which kind of event the list is narrowed down to -
// standing empty, and taking no room, while the list is not narrowed down at all
listing.drawEventFilterChip = function() {
    var config = listing.config;
    var host = $(listing.config.eventChipHost);
    var html = '';

    if (listing.eventFilter !== '') {
        var eventWord = $.fn.zato.audit_log.eventLabel(listing.eventFilter);

        html += '<span class="dashboard-pill audit-log-filter-chip">' + listing.escapeHTML(eventWord) +
            '<span class="audit-log-filter-chip-clear" title="Show every kind of event">&times;</span></span>';
    }

    // The sources with unchanged runs say whether those are on the list.
    if (listing.hasUnchangedToggle()) {
        var label = config.showUnchangedLabel;

        if (listing.hideUnchanged) {
            label = config.hideUnchangedLabel;
        }

        html += '<span class="dashboard-pill dashboard-pill-clickable audit-log-unchanged-toggle">' + label + '</span>';
    }

    host.html(html);
};

// /////////////////////////////////////////////////////////////////////////////

listing.hasUnchangedToggle = function() {
    var source = $.fn.zato.audit_log.config.source;
    var out = listing.config.hideUnchangedSources[source] === true;

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// The statuses the poll leaves out.
listing.statusesExcluded = function() {
    var out = [];

    if (listing.hideUnchanged) {
        out.push(listing.config.unchangedStatus);
    }

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// The unchanged runs start out hidden on the sources that have them unless the reader chose otherwise.
listing.initHideUnchanged = function() {
    if (!listing.hasUnchangedToggle()) {
        listing.hideUnchanged = false;
        return;
    }

    var stored = window.localStorage.getItem(listing.config.hideUnchangedStorageKey);

    if (stored === null) {
        listing.hideUnchanged = true;
    }
    else {
        listing.hideUnchanged = stored === '1';
    }
};

// /////////////////////////////////////////////////////////////////////////////

listing.toggleHideUnchanged = function() {
    listing.hideUnchanged = !listing.hideUnchanged;
    window.localStorage.setItem(listing.config.hideUnchangedStorageKey, listing.hideUnchanged ? '1' : '0');

    listing.drawEventFilterChip();

    var pagination = $.fn.zato.audit_log.pagination;
    pagination.set_filters({statuses_excluded: listing.statusesExcluded()});
    pagination.fetch_page(1);
};

// /////////////////////////////////////////////////////////////////////////////

// The filter one clicked event word applies - the log narrows down to events of that kind,
// the chip beside the legend says so and the address bar carries it, so the view deep-links
listing.applyEventFilter = function(eventType) {
    listing.eventFilter = eventType;
    listing.drawEventFilterChip();

    kit.url_state.replace({event_type: eventType});

    var pagination = $.fn.zato.audit_log.pagination;
    pagination.set_filters({event_types: [eventType]});
    pagination.fetch_page(1);
};

// /////////////////////////////////////////////////////////////////////////////

listing.clearEventFilter = function() {
    listing.eventFilter = '';
    listing.drawEventFilterChip();

    kit.url_state.replace({event_type: ''});

    var pagination = $.fn.zato.audit_log.pagination;
    pagination.set_filters({event_types: []});
    pagination.fetch_page(1);
};

// /////////////////////////////////////////////////////////////////////////////

// A clicked outcome badge narrows the legend down to its own outcome - every other badge
// goes dim, and switching them back on is done up there, where the filter lives
listing.applyOutcomeFilter = function(outcome) {
    var outcomes = listing.currentOutcomes;

    listing.hidden = {};

    for (var outcomeIndex = 0; outcomeIndex < outcomes.length; outcomeIndex++) {
        if (outcomes[outcomeIndex] !== outcome) {
            listing.hidden[outcomes[outcomeIndex]] = true;
        }
    }

    listing.buildLegend(outcomes);

    var pagination = $.fn.zato.audit_log.pagination;
    pagination.set_filters({outcomes: listing.pickedOutcomes(outcomes)});
    pagination.fetch_page(1);
};

})(jQuery);
