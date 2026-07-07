

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.audit_log = {};

// /////////////////////////////////////////////////////////////////////////////

(function($) {

$.fn.zato.audit_log.config = {
    pageSize: 25,
    detailsURL: '/zato/audit-log/details/',
    emptyValue: '---',
    columnCount: 7
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

$.fn.zato.audit_log.renderRow = function(row) {
    var config = $.fn.zato.audit_log.config;
    var escapeHTML = $.fn.zato.audit_log.escapeHTML;
    var renderCell = $.fn.zato.audit_log.renderCell;

    var html = '<tr>';

    // The event time always comes first, shown in the browser's timezone and locale format ..
    var eventTime = new Date(row.event_time_iso);
    html += renderCell(eventTime.toLocaleString());

    // .. each CID opens the complete message of its event ..
    if (row.cid === '') {
        html += '<td>' + config.emptyValue + '</td>';
    } else {
        html += '<td>';
        html += '<a href="#" class="audit-log-cid-link" data-id="' + row.id + '" data-cid="' + escapeHTML(row.cid) + '">';
        html += escapeHTML(row.cid);
        html += '</a>';
        html += '</td>';
    }

    html += renderCell(row.event_type);
    html += renderCell(row.msg_id);
    html += renderCell(row.endpoint);

    // .. the size is right-aligned like all numeric columns ..
    html += '<td style="text-align:right">' + row.size + '</td>';

    // .. and the payload preview concludes the row.
    if (row.data === '') {
        html += '<td>' + config.emptyValue + '</td>';
    } else {
        html += '<td class="audit-log-data-preview">' + escapeHTML(row.data) + '</td>';
    }

    html += '</tr>';

    return html;
};

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.audit_log.renderPage = function($body, rows) {
    var config = $.fn.zato.audit_log.config;
    var renderRow = $.fn.zato.audit_log.renderRow;

    // The table shows a placeholder row when there are no events ..
    if (rows.length === 0) {
        $body.html('<tr><td colspan="' + config.columnCount + '">No events found</td></tr>');
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

            $.fn.zato.highlight_pane.open_overlay({
                title: 'Message data',
                title_detail: cid,
                text: data.data,
                editable: false,
                ace_mode: aceMode,
                buttons: [copyCIDButton, copyMessageButton]
            });
        }
    });
};

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.audit_log.init = function(initConfig) {
    var kit = $.fn.zato.dashboard_kit;
    var config = $.fn.zato.audit_log.config;

    // Wire up the paginated table ..
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
