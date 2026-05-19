(function($) {

if (typeof $.fn.zato === 'undefined') { $.fn.zato = {}; }
if (typeof $.fn.zato.pubsub === 'undefined') { $.fn.zato.pubsub = {}; }
$.fn.zato.pubsub.queue = {};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.pubsub.queue.config = {
    pageSize: 50,
    purgeUrl: '/zato/pubsub/subscription/queue/purge/'
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.pubsub.queue._subscriptionKey = '';
$.fn.zato.pubsub.queue._pagination = null;

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.pubsub.queue._renderPage = function($body, rows, total) {
    var kit = $.fn.zato.dashboard_kit;
    var queue = $.fn.zato.pubsub.queue;

    $('#stat-depth').text(kit.format_number_full(total));

    $body.empty();

    if (rows.length === 0) {
        $body.append('<tr><td colspan="5" class="dashboard-inline-empty">No pending messages</td></tr>');
        return;
    }

    for (var rowIdx = 0; rowIdx < rows.length; rowIdx++) {
        $body.append(queue._buildRow(rows[rowIdx]));
    }
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.pubsub.queue._renderNew = function($body, rows, maxRows) {
    var queue = $.fn.zato.pubsub.queue;

    $body.find('.dashboard-inline-empty').closest('tr').remove();

    for (var rowIdx = rows.length - 1; rowIdx >= 0; rowIdx--) {
        $body.prepend(queue._buildRow(rows[rowIdx]));
    }

    while ($body.find('tr').length > maxRows) {
        $body.find('tr:last').remove();
    }
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.pubsub.queue._buildRow = function(message) {
    var kit = $.fn.zato.dashboard_kit;
    var relativeTime = kit.relative_time_past(message.pub_time_iso);
    var localTime = kit.format_local_time(message.pub_time_iso);
    var topicLink = '/zato/pubsub/topic/?cluster=1&query=' + encodeURIComponent(message.topic_name);

    var html = '<tr>';
    html += '<td style="font-family:monospace;font-size:12px">' + kit._esc_html(message.msg_id) + '</td>';
    html += '<td><a href="' + topicLink + '">' + kit._esc_html(message.topic_name) + '</a></td>';
    html += '<td class="data-preview">' + kit._esc_html(message.data_preview) + '</td>';
    html += '<td style="text-align:center">' + message.data_size + ' B</td>';
    html += '<td title="' + kit._esc_html(localTime) + '">' + relativeTime + '</td>';
    html += '</tr>';

    return html;
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.pubsub.queue.purge = function() {
    var queue = $.fn.zato.pubsub.queue;

    if (!confirm('Purge all pending messages from this queue?')) {
        return;
    }

    $.ajax({
        url: queue.config.purgeUrl,
        type: 'POST',
        data: {sub_key: queue._subscriptionKey},
        headers: {'X-CSRFToken': $.cookie('csrftoken')},
        success: function() {
            window.location.reload();
        },
        error: function(xhr) {
            var errorMessage = 'Unknown error';
            if (xhr.responseJSON) {
                errorMessage = xhr.responseJSON.error;
            }
            alert('Error: ' + errorMessage);
        }
    });
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.pubsub.queue.init = function(subKey, clusterID, pollConfig) {
    var kit = $.fn.zato.dashboard_kit;
    var queue = $.fn.zato.pubsub.queue;

    queue._subscriptionKey = subKey;

    queue._pagination = kit.pagination.init({
        poll_url: pollConfig.poll_url,
        action: 'get-queue-messages',
        object_id: subKey,
        page_size: queue.config.pageSize,
        filters: {},
        ts_field: 'pub_time_iso',
        table_body: '#detail-history-table-body',
        container_top: '#detail-history-pagination-top',
        container_bottom: '#detail-history-pagination-bottom',
        render_page: queue._renderPage,
        render_new: queue._renderNew
    });
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
