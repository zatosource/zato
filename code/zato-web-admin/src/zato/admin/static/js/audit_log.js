

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

    // .. wire up the paginated listing ..
    var pagination = kit.pagination.init({
        poll_url: initConfig.poll_url,
        page_size: config.pageSize,
        filters: {
            source: initConfig.source,
            object_name: initConfig.object_name,
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
