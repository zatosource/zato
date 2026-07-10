

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.audit_log = {};

// /////////////////////////////////////////////////////////////////////////////

(function($) {

$.fn.zato.audit_log.config = {
    pageSize: 25,
    detailsURL: '/zato/audit-log/details/',
    emptyValue: '---',

    // The overlay tab labels - the raw payload and its parsed EDI document view
    rawTabLabel: 'Raw',
    parsedTabLabel: 'Parsed',

    // The per-source column list, assigned in init
    columns: []
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

$.fn.zato.audit_log.init = function(initConfig) {
    var kit = $.fn.zato.dashboard_kit;
    var config = $.fn.zato.audit_log.config;

    // The columns to render come from the server, per source ..
    config.columns = initConfig.columns;

    // .. wire up the paginated table ..
    var pagination = kit.pagination.init({
        poll_url: initConfig.poll_url,
        page_size: config.pageSize,
        filters: {
            source: initConfig.source,
            object_name: initConfig.object_name,
            query: ''
        },
        table_body: '#audit-log-table-body',
        container_top: '#audit-log-pagination-top',
        container_bottom: '#audit-log-pagination-bottom',
        render_page: $.fn.zato.audit_log.renderPage
    });

    // .. let the search form filter the events ..
    $('#audit-log-search-form').on('submit', function(event) {
        event.preventDefault();

        var query = $('#audit-log-search-input').val();

        pagination.set_filters({query: query});
        pagination.fetch_page(1);
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
