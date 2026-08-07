
// /////////////////////////////////////////////////////////////////////////////

// Message flow - the page. A search box holding the one thing a person has -
// a control id, a CID or an event id - and under it two equal ways of reading
// what it names: the journey drawn on the Message flow tab, and the same
// journey as the List tab's lines. The address bar carries the term
// and the open tab, so a link reproduces the screen.

$.fn.zato.message_flow.page = {};

// /////////////////////////////////////////////////////////////////////////////

(function($) {

var kit = $.fn.zato.dashboard_kit;
var page = $.fn.zato.message_flow.page;

// /////////////////////////////////////////////////////////////////////////////

page.config = {

    journeyURL: '/zato/message-flow/journey/',

    // The two ways of reading one journey
    tabSelector: '.message-flow-tab',
    tabPanelPrefix: 'message-flow-panel-',
    tabStorageKey: 'zato_message_flow_tab',
    flowTab: 'flow',
    listTab: 'list',

    // What the term and the tab are called in the address bar
    termURLKey: 'term',
    tabURLKey: 'tab',

    // Where the list mounts - the same host the audit log's flow renders into
    listHost: '#audit-log-pane-flow',

    // What the page says before a term is searched, while one is being answered,
    // and when a term names nothing
    idleHint: 'Search a control id, a CID or an event id',
    notFoundHint: 'Nothing found',

    // How long the page waits for a journey before saying it is waiting
    spinnerDelayMs: 150,

    // How the status line says what the term turned out to name
    resolvedLabels: {
        'event-id': 'event id',
        'cid': 'CID',
        'msg-id': 'control id'
    },

    eventWord: 'event',
    eventsWord: 'events',
    foundByLabel: 'found by'
};

// /////////////////////////////////////////////////////////////////////////////

// What the page is holding - the term being read, the message it resolved to,
// and the number of the request the answer on screen belongs to
page.state = {
    term: '',
    identity: '',
    token: 0
};

// The tab group, once the page is up
page.tabs = null;

// /////////////////////////////////////////////////////////////////////////////

// A hint standing in the middle of the canvas - what the drawing has to say
// when there is no drawing
page.showCanvasHint = function(html) {
    var drawing = $.fn.zato.message_flow.drawing;

    drawing.clear();

    var hint = document.createElement('div');
    hint.className = 'message-flow-canvas-hint';
    hint.innerHTML = html;

    drawing.canvas().appendChild(hint);
};

// /////////////////////////////////////////////////////////////////////////////

// The list's own empty state, in the same words the canvas says
page.showListHint = function(html) {
    $(page.config.listHost).html('<div class="dashboard-inline-empty">' + html + '</div>');
};

// /////////////////////////////////////////////////////////////////////////////

page.showStatus = function(text) {
    $('#message-flow-status').text(text);
};

// /////////////////////////////////////////////////////////////////////////////

// The page with nothing searched yet, or searched and cleared
page.showIdle = function() {
    var config = page.config;
    var detail = $.fn.zato.message_flow.detail;
    var flow = $.fn.zato.audit_log.flow;

    page.state.identity = '';

    // The list's own state is let go too, so the next search draws afresh
    flow.seedId = null;
    flow.rows = [];

    page.showCanvasHint(kit._esc_html(config.idleHint));
    page.showListHint(kit._esc_html(config.idleHint));
    page.showStatus('');

    detail.hide();
};

// /////////////////////////////////////////////////////////////////////////////

// A term that names nothing - both tabs say so and nothing else changes
page.showNotFound = function(term) {
    var config = page.config;
    var detail = $.fn.zato.message_flow.detail;
    var flow = $.fn.zato.audit_log.flow;

    page.state.identity = '';

    flow.seedId = null;
    flow.rows = [];

    var hint = kit._esc_html(config.notFoundHint) + ' - <span class="message-flow-hint-term">' +
        kit._esc_html(term) + '</span>';

    page.showCanvasHint(hint);
    page.showListHint(hint);
    page.showStatus('');

    detail.hide();
};

// /////////////////////////////////////////////////////////////////////////////

// One journey on both tabs - the models are built once and the drawing and the
// list read the same rows, so what one shows is what the other says
page.showJourney = function(data) {
    var config = page.config;
    var detail = $.fn.zato.message_flow.detail;
    var drawing = $.fn.zato.message_flow.drawing;
    var flow = $.fn.zato.audit_log.flow;

    var models = flow.buildRows(data.rows);

    // The model of the event the term resolved to - the hub's own words
    var seedModel = null;

    for (var modelIndex = 0; modelIndex < models.length; modelIndex++) {
        if (String(models[modelIndex].id) === String(data.seed_id)) {
            seedModel = models[modelIndex];
            break;
        }
    }

    page.state.identity = seedModel.identity;

    // The drawing reads the journey forward ..
    drawing.render(models, seedModel);
    detail.hide();

    // .. and the list reads it the way the audit log does, newest first,
    // with whatever steps the address bar names already open
    flow.seedId = data.seed_id;
    flow.rows = models;
    flow.render();
    flow.panel.restoreStep();

    // The status line says what the term turned out to name
    var eventWord = models.length === 1 ? config.eventWord : config.eventsWord;

    page.showStatus(models.length + ' ' + eventWord + ' ' + config.foundByLabel + ' ' +
        config.resolvedLabels[data.resolved_by]);
};

// /////////////////////////////////////////////////////////////////////////////

page.search = function(term) {
    var config = page.config;

    term = term.trim();

    page.state.term = term;
    kit.url_state.replace({term: term});

    // A cleared box asks for nothing and the page says it is waiting for a term
    if (term === '') {
        page.showIdle();
        return;
    }

    page.state.token += 1;
    var token = page.state.token;

    // The wait is only announced once it is long enough to be worth announcing
    var spinnerTimer = setTimeout(function() {
        if (page.state.token !== token) {
            return;
        }

        page.showCanvasHint(kit.spinner_label_html());
        page.showListHint(kit.spinner_label_html());
    }, config.spinnerDelayMs);

    $.ajax({
        url: config.journeyURL,
        type: 'POST',
        data: JSON.stringify({term: term}),
        contentType: 'application/json',
        headers: {'X-CSRFToken': $.cookie('csrftoken')},
        success: function(data) {

            // An answer to a term the page has since been brought away from
            // is not drawn at all
            if (page.state.token !== token) {
                return;
            }

            clearTimeout(spinnerTimer);

            if (typeof data === 'string') {
                data = JSON.parse(data);
            }

            if (data.resolved_by === '') {
                page.showNotFound(term);
            }
            else {
                page.showJourney(data);
            }
        }
    });
};

// /////////////////////////////////////////////////////////////////////////////

// Clear stands in the box only while there is a term in it to be cleared
page.showSearchClear = function() {
    $('#message-flow-search-clear').toggle($('#message-flow-search-input').val() !== '');
};

// /////////////////////////////////////////////////////////////////////////////

page.init = function() {
    var config = page.config;

    $.fn.zato.message_flow.drawing.init();
    $.fn.zato.message_flow.detail.init();

    // The list's lines and panels answer to the same handlers they answer to
    // everywhere, bound once for the page
    $.fn.zato.audit_log.flow.init();

    // The two tabs - which one is open goes into the address bar, so a link
    // is a link to the very reading its sender had in front of them
    // The tabs are the same badges every chosen thing on a dark panel wears,
    // the open one lit the way an open payload tab is
    page.tabs = kit.tabs.init({
        tab_selector: config.tabSelector,
        panel_prefix: config.tabPanelPrefix,
        active_cls: 'dashboard-panel-action-badge-active',
        storage_key: config.tabStorageKey,
        default_tab: config.flowTab,
        on_change: function(tab) {
            kit.url_state.replace({tab: tab});
        }
    });

    // A link naming a tab opens in that tab, whatever this screen was last left in
    var urlTab = kit.url_state.get(config.tabURLKey);

    if (urlTab === config.flowTab || urlTab === config.listTab) {
        page.tabs.set_tab(urlTab, true);
    }

    // The search form asks for the journey of whatever is in the box
    $('#message-flow-search-form').on('submit', function(event) {
        event.preventDefault();

        page.showSearchClear();
        page.search($('#message-flow-search-input').val());
    });

    // Clear follows the first character typed and the last one deleted ..
    $('#message-flow-search-input').on('input', page.showSearchClear);

    // .. and clearing the box puts the page back the way it opened.
    $('#message-flow-search-clear').on('click', function() {
        $('#message-flow-search-input').val('');
        page.showSearchClear();
        page.search('');
    });

    // A Search badge in a list panel asks this very page for the value it carries,
    // the box picking the term up so what is being read is never in doubt
    $(document).on('click', '.message-flow-page .dashboard-fact-row-search', function(event) {
        event.stopPropagation();

        var term = $(this).attr('data-search-value');

        $('#message-flow-search-input').val(term);
        page.showSearchClear();
        page.search(term);
    });

    // A link naming a term opens on that term's journey
    var urlTerm = kit.url_state.get(config.termURLKey);

    if (urlTerm !== null && urlTerm !== '') {
        $('#message-flow-search-input').val(urlTerm);
        page.showSearchClear();
        page.search(urlTerm);
    }
    else {
        page.showIdle();
    }
};

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    page.init();
});

// /////////////////////////////////////////////////////////////////////////////

})(jQuery);
