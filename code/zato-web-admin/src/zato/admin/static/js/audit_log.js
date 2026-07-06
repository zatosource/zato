

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.audit_log = {};

// /////////////////////////////////////////////////////////////////////////////

(function($) {

$.fn.zato.audit_log.config = {
    pageSize: 25,
    cidPageURLPrefix: '/zato/audit-log/cid/',
    emptyValue: '---'
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

$.fn.zato.audit_log.renderRow = function(row, isCIDPage) {
    var config = $.fn.zato.audit_log.config;
    var escapeHTML = $.fn.zato.audit_log.escapeHTML;
    var renderCell = $.fn.zato.audit_log.renderCell;

    var html = '<tr>';

    // The event time always comes first ..
    html += renderCell(row.event_time_iso);

    // .. each CID links to the cross-source page for that CID ..
    if (row.cid === '') {
        html += '<td>' + config.emptyValue + '</td>';
    } else {
        var cidURL = config.cidPageURLPrefix + encodeURIComponent(row.cid) + '/';
        html += '<td><a href="' + cidURL + '">' + escapeHTML(row.cid) + '</a></td>';
    }

    // .. the source column appears only on the cross-source CID page ..
    if (isCIDPage) {
        html += renderCell(row.source);
    }

    html += renderCell(row.event_type);
    html += renderCell(row.msg_id);
    html += renderCell(row.endpoint);
    html += renderCell(row.server_name);

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
    var renderRow = $.fn.zato.audit_log.renderRow;
    var isCIDPage = $.fn.zato.audit_log._isCIDPage;

    // The table shows a placeholder row when there are no events ..
    if (rows.length === 0) {
        var columnCount = isCIDPage ? 9 : 8;
        $body.html('<tr><td colspan="' + columnCount + '">No events found</td></tr>');
        return;
    }

    // .. otherwise all rows are rebuilt in one go.
    var html = '';

    for (var rowIdx = 0; rowIdx < rows.length; rowIdx++) {
        html += renderRow(rows[rowIdx], isCIDPage);
    }

    $body.html(html);
};

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.audit_log.init = function(initConfig) {
    var kit = $.fn.zato.dashboard_kit;
    var config = $.fn.zato.audit_log.config;

    $.fn.zato.audit_log._isCIDPage = initConfig.is_cid_page;

    // Wire up the paginated table ..
    var pagination = kit.pagination.init({
        poll_url: initConfig.poll_url,
        page_size: config.pageSize,
        filters: {
            source: initConfig.source,
            object_name: initConfig.object_name,
            cid: initConfig.cid,
            query: ''
        },
        table_body: '#audit-log-table-body',
        container_top: '#audit-log-pagination-top',
        container_bottom: '#audit-log-pagination-bottom',
        render_page: $.fn.zato.audit_log.renderPage
    });

    // .. and let the search form filter the events.
    $('#audit-log-search-form').on('submit', function(event) {
        event.preventDefault();

        var query = $('#audit-log-search-input').val();

        pagination.set_filters({query: query});
        pagination.fetch_page(1);
    });
};

// /////////////////////////////////////////////////////////////////////////////

})(jQuery);
