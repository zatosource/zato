

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

    // .. and the payload preview concludes the row, linking to the complete message.
    if (row.data === '') {
        html += '<td>' + config.emptyValue + '</td>';
    } else {
        html += '<td class="audit-log-data-preview">';
        html += '<a href="#" class="audit-log-preview-link" data-id="' + row.id + '">' + escapeHTML(row.data) + '</a>';
        html += '</td>';
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

            var title = cid ? 'Message data - ' + cid : 'Message data';

            $.fn.zato.highlight_pane.open_overlay({
                title: title,
                text: data.data,
                editable: false,
                buttons: [
                    $.fn.zato.highlight_pane.buttons.copy()
                ]
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

    // .. let each data preview open the complete message in an overlay ..
    $(document).on('click', '.audit-log-preview-link', function(event) {
        event.preventDefault();

        var eventId = parseInt($(this).attr('data-id'), 10);
        var cid = $(this).closest('tr').find('.audit-log-cid-link').attr('data-cid');

        $.fn.zato.audit_log.openMessageOverlay(eventId, cid);
    });

    // .. and let each CID do the same.
    $(document).on('click', '.audit-log-cid-link', function(event) {
        event.preventDefault();

        var eventId = parseInt($(this).attr('data-id'), 10);
        var cid = $(this).attr('data-cid');

        $.fn.zato.audit_log.openMessageOverlay(eventId, cid);
    });
};

// /////////////////////////////////////////////////////////////////////////////

})(jQuery);
