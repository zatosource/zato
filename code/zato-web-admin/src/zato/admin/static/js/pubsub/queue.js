
if (typeof $.fn.zato === 'undefined') { $.fn.zato = {}; }
if (typeof $.fn.zato.pubsub === 'undefined') { $.fn.zato.pubsub = {}; }
$.fn.zato.pubsub.queue = {};

$.fn.zato.pubsub.queue._sub_key = '';
$.fn.zato.pubsub.queue._pagination = null;

$.fn.zato.pubsub.queue._renderPage = function($body, rows, total) {
    var kit = $.fn.zato.dashboard_kit;
    var queue = $.fn.zato.pubsub.queue;

    $('#stat-depth').text(kit.format_number_full(total));

    $body.empty();

    if (!rows || rows.length === 0) {
        $body.append('<tr><td colspan="5" class="dashboard-inline-empty">No pending messages</td></tr>');
        return;
    }

    for (var i = 0; i < rows.length; i++) {
        $body.append(queue._build_row(rows[i]));
    }
};

$.fn.zato.pubsub.queue._renderNew = function($body, rows, max) {
    var queue = $.fn.zato.pubsub.queue;

    $body.find('.dashboard-inline-empty').closest('tr').remove();

    for (var i = rows.length - 1; i >= 0; i--) {
        $body.prepend(queue._build_row(rows[i]));
    }

    while ($body.find('tr').length > max) {
        $body.find('tr:last').remove();
    }
};

$.fn.zato.pubsub.queue._build_row = function(msg) {
    var kit = $.fn.zato.dashboard_kit;
    var relative = kit.relative_time_past(msg.pub_time_iso);
    var local = kit.format_local_time(msg.pub_time_iso);
    var topic_link = '/zato/pubsub/topic/?cluster=1&query=' + encodeURIComponent(msg.topic_name);

    var html = '<tr>';
    html += '<td style="font-family:monospace;font-size:12px">' + kit._esc_html(msg.msg_id) + '</td>';
    html += '<td><a href="' + topic_link + '">' + kit._esc_html(msg.topic_name) + '</a></td>';
    html += '<td class="data-preview">' + kit._esc_html(msg.data_preview) + '</td>';
    html += '<td style="text-align:center">' + msg.data_size + ' B</td>';
    html += '<td title="' + kit._esc_html(local) + '">' + relative + '</td>';
    html += '</tr>';

    return html;
};

$.fn.zato.pubsub.queue.purge = function() {
    if (!confirm('Purge all pending messages from this queue?')) {
        return;
    }

    $.ajax({
        url: '/zato/pubsub/subscription/queue/purge/',
        type: 'POST',
        data: {sub_key: $.fn.zato.pubsub.queue._sub_key},
        headers: {'X-CSRFToken': $.cookie('csrftoken')},
        success: function() {
            window.location.reload();
        },
        error: function(xhr) {
            var error_message = 'Unknown error';
            if (xhr.responseJSON) {
                error_message = xhr.responseJSON.error;
            }
            alert('Error: ' + error_message);
        }
    });
};

$.fn.zato.pubsub.queue.init = function(sub_key, cluster_id, poll_config) {
    var kit = $.fn.zato.dashboard_kit;
    var queue = $.fn.zato.pubsub.queue;

    queue._sub_key = sub_key;

    queue._pagination = kit.pagination.init({
        poll_url: poll_config.poll_url,
        action: 'get-queue-messages',
        object_id: sub_key,
        page_size: 50,
        filters: {},
        ts_field: 'pub_time_iso',
        table_body: '#detail-history-table-body',
        container_top: '#detail-history-pagination-top',
        container_bottom: '#detail-history-pagination-bottom',
        render_page: queue._renderPage,
        render_new: queue._renderNew
    });
};
