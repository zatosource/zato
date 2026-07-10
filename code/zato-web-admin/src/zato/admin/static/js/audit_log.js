

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.audit_log = {};

// /////////////////////////////////////////////////////////////////////////////

(function($) {

$.fn.zato.audit_log.config = {
    pageSize: 25,
    detailsURL: '/zato/audit-log/details/',
    resubmitURL: '/zato/audit-log/resubmit/',
    emptyValue: '---',

    // The overlay tab labels - the raw payload and its parsed EDI document view
    rawTabLabel: 'Raw',
    parsedTabLabel: 'Parsed',

    // The status filter value narrowing the page down to open exchanges
    outstandingStatus: 'outstanding',

    // What the resubmit outcome is reported with
    resubmitModalTitle: 'Resubmit result',
    resubmitErrorLabel: 'Resubmit failed',
    resentLabel: 'Resent',
    reprocessedLabel: 'Reprocessed to',
    resubmittedMarkerLabel: 'resubmitted',

    // The per-source column list and resubmit labels, assigned in init
    columns: [],
    resubmitLabels: {}
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

$.fn.zato.audit_log.renderCell = function(value) {
    var config = $.fn.zato.audit_log.config;
    var escapeHTML = $.fn.zato.audit_log.escapeHTML;

    // Empty values are shown as a placeholder so the table stays readable ..
    if (value === '') {
        return '<td>' + config.emptyValue + '</td>';
    }

    // .. everything else is escaped and shown as-is.
    return '<td>' + escapeHTML(value) + '</td>';
};

// /////////////////////////////////////////////////////////////////////////////

// Each cell type has its own renderer so any source can compose its columns freely
$.fn.zato.audit_log.cellRenderers = {

    // The event time is shown in the browser's timezone and locale format
    'time': function(row, column) {
        var renderCell = $.fn.zato.audit_log.renderCell;
        var eventTime = new Date(row[column.key]);
        return renderCell(eventTime.toLocaleString());
    },

    // Each CID opens the complete message of its event
    'cid': function(row, column) {
        var config = $.fn.zato.audit_log.config;
        var escapeHTML = $.fn.zato.audit_log.escapeHTML;

        var cid = row[column.key];

        if (cid === '') {
            return '<td>' + config.emptyValue + '</td>';
        }

        var html = '<td>';
        html += '<a href="#" class="audit-log-cid-link" data-id="' + row.id + '" data-cid="' + escapeHTML(cid) + '">';
        html += escapeHTML(cid);
        html += '</a>';
        html += '</td>';

        return html;
    },

    // Plain text cells are escaped and shown as-is
    'text': function(row, column) {
        var renderCell = $.fn.zato.audit_log.renderCell;
        return renderCell(row[column.key]);
    },

    // The size is right-aligned like all numeric columns
    'size': function(row, column) {
        return '<td style="text-align:right">' + row[column.key] + '</td>';
    },

    // The payload preview concludes the row
    'data': function(row, column) {
        var config = $.fn.zato.audit_log.config;
        var escapeHTML = $.fn.zato.audit_log.escapeHTML;

        var data = row[column.key];

        if (data === '') {
            return '<td>' + config.emptyValue + '</td>';
        }

        return '<td class="audit-log-data-preview">' + escapeHTML(data) + '</td>';
    },

    // The resubmit action of the row - resend for outbound events, reprocess for inbound ones -
    // plus a marker on rows that were already resubmitted. Event types without a registered
    // action, e.g. the arrival of an MDN, have nothing to resubmit.
    'action': function(row, column) {
        var config = $.fn.zato.audit_log.config;

        var label = config.resubmitLabels[row.event_type];

        if (!label) {
            return '<td>' + config.emptyValue + '</td>';
        }

        var html = '<td>';
        html += '<a href="javascript:void(0)" class="audit-log-resubmit-link" data-id="' + row.id + '">' + label + '</a>';

        if (row.is_resubmitted) {
            html += ' <span class="audit-log-resubmitted-marker">' + config.resubmittedMarkerLabel + '</span>';
        }

        html += '</td>';

        return html;
    }
};

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.audit_log.renderRow = function(row) {
    var config = $.fn.zato.audit_log.config;
    var cellRenderers = $.fn.zato.audit_log.cellRenderers;

    var html = '<tr>';

    // Each cell is rendered by the renderer matching its column's type ..
    for (var columnIdx = 0; columnIdx < config.columns.length; columnIdx++) {
        var column = config.columns[columnIdx];
        html += cellRenderers[column.type](row, column);
    }

    // .. and the row is complete.
    html += '</tr>';

    return html;
};

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.audit_log.renderPage = function($body, rows) {
    var config = $.fn.zato.audit_log.config;
    var renderRow = $.fn.zato.audit_log.renderRow;

    // The table shows a placeholder row when there are no events ..
    if (rows.length === 0) {
        $body.html('<tr><td colspan="' + config.columns.length + '">No events found</td></tr>');
        return;
    }

    // .. otherwise all rows are rebuilt in one go.
    var html = '';

    for (var rowIdx = 0; rowIdx < rows.length; rowIdx++) {
        html += renderRow(rows[rowIdx]);
    }

    $body.html(html);
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
        data: JSON.stringify({id: eventId}),
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

    // .. a reprocess is reported by where the payload went ..
    if (report.action === 'reprocess') {
        return config.reprocessedLabel + ' ' + report.target_kind + ' ' + report.target_name;
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

    // The columns to render and the resubmit labels come from the server, per source ..
    config.columns = initConfig.columns;
    config.resubmitLabels = initConfig.resubmitLabels;

    // .. wire up the paginated table ..
    var pagination = kit.pagination.init({
        poll_url: initConfig.poll_url,
        page_size: config.pageSize,
        filters: {
            source: initConfig.source,
            object_name: initConfig.object_name,
            query: '',
            status: initConfig.status
        },
        table_body: '#audit-log-table-body',
        container_top: '#audit-log-pagination-top',
        container_bottom: '#audit-log-pagination-bottom',
        render_page: $.fn.zato.audit_log.renderPage
    });

    // .. the resubmit outcome handler refreshes the table through this reference ..
    $.fn.zato.audit_log.pagination = pagination;

    // .. let the search form filter the events ..
    $('#audit-log-search-form').on('submit', function(event) {
        event.preventDefault();

        var query = $('#audit-log-search-input').val();

        pagination.set_filters({query: query});
        pagination.fetch_page(1);
    });

    // .. the outstanding pill toggles between all events and the open exchanges,
    // .. keeping the status query parameter of the page URL in sync ..
    $('#audit-log-outstanding-pill').on('click', function(event) {
        event.preventDefault();

        var pill = $(this);
        var wasActive = pill.hasClass('audit-log-filter-pill-active');

        var newStatus = wasActive ? '' : config.outstandingStatus;
        pill.toggleClass('audit-log-filter-pill-active', !wasActive);

        pagination.set_filters({status: newStatus});
        pagination.fetch_page(1);

        var urlParams = new URLSearchParams(window.location.search);

        if (newStatus) {
            urlParams.set('status', newStatus);
        } else {
            urlParams.delete('status');
        }

        history.replaceState(null, '', '?' + urlParams.toString());
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
