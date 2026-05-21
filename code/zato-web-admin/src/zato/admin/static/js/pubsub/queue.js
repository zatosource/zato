
// ////////////////////////////////////////////////////////////////////////

(function($) {

    $.namespace('zato.pubsub.queue');

// ////////////////////////////////////////////////////////////////////////

    $.fn.zato.pubsub.queue._subKey = '';
    $.fn.zato.pubsub.queue._defaultErrorMessage = 'Unknown error';
    $.fn.zato.pubsub.queue._pagination = null;

// ////////////////////////////////////////////////////////////////////////

    $.fn.zato.pubsub.queue._render_row = function(message) {

        var kit = $.fn.zato.dashboard_kit;
        var subKey = $.fn.zato.pubsub.queue._subKey;
        var relativeTime = kit.relative_time_past(message.pub_time_iso);
        var localTime = kit.format_local_time(message.pub_time_iso);
        var topicName = message.topic_name;

        var messageLink = '/zato/pubsub/subscription/queue/message/?cluster=1' +
            '&sub_key=' + encodeURIComponent(subKey) +
            '&msg_id=' + encodeURIComponent(message.msg_id) +
            '&topic_name=' + encodeURIComponent(topicName) +
            '&redis_stream_id=' + encodeURIComponent(message.redis_stream_id);

        var topicLink = '/zato/pubsub/topic/?cluster=1&query=' + encodeURIComponent(topicName);

        var row = '<tr>';
        row += '<td style="font-family:monospace; font-size:12px"><a href="' + messageLink + '">' + message.msg_id + '</a></td>';
        row += '<td><a href="' + topicLink + '">' + topicName + '</a></td>';
        row += '<td class="data-preview">' + $('<span>').text(message.data_preview).html() + '</td>';
        row += '<td>' + message.data_size + ' B</td>';
        row += '<td title="' + localTime + '">' + relativeTime + '</td>';
        row += '</tr>';

        return row;
    };

// ////////////////////////////////////////////////////////////////////////

    $.fn.zato.pubsub.queue._render_page = function($body, rows, total) {

        $body.empty();

        var depthFormatted = total.toLocaleString();
        var $depth = $('#stat-depth');
        if ($depth.text() !== depthFormatted) {
            $depth.text(depthFormatted);
        }

        if (rows.length === 0) {
            $body.append('<tr><td colspan="5">No messages</td></tr>');
            return;
        }

        for (var i = 0; i < rows.length; i++) {
            $body.append($.fn.zato.pubsub.queue._render_row(rows[i]));
        }
    };

// ////////////////////////////////////////////////////////////////////////

    $.fn.zato.pubsub.queue._render_new = function($body, rows, max_rows) {

        for (var i = 0; i < rows.length; i++) {
            $body.prepend($.fn.zato.pubsub.queue._render_row(rows[i]));
        }

        while ($body.children().length > max_rows) {
            $body.children().last().remove();
        }
    };

// ////////////////////////////////////////////////////////////////////////

    $.fn.zato.pubsub.queue.purge = function() {

        if (!confirm('Purge all pending messages from this queue?')) {
            return;
        }

        $.ajax({
            url: '/zato/pubsub/subscription/queue/purge/',
            type: 'POST',
            data: {
                sub_key: $.fn.zato.pubsub.queue._subKey
            },
            headers: {'X-CSRFToken': $.cookie('csrftoken')},
            success: function() {
                window.location.reload();
            },
            error: function(xhr) {
                var errorMessage = $.fn.zato.pubsub.queue._defaultErrorMessage;
                if (xhr.responseJSON) {
                    errorMessage = xhr.responseJSON.error;
                }
                alert('Error: ' + errorMessage);
            }
        });
    };

// ////////////////////////////////////////////////////////////////////////

    $.fn.zato.pubsub.queue.init = function(subKey, config) {

        var kit = $.fn.zato.dashboard_kit;

        // Store the sub_key for purge operations ..
        $.fn.zato.pubsub.queue._subKey = subKey;

        // .. bind the purge button ..
        $('#purge-queue-button').on('click', function() {
            $.fn.zato.pubsub.queue.purge();
        });

        // .. and initialize pagination.
        $.fn.zato.pubsub.queue._pagination = kit.pagination.init({
            poll_url: config.poll_url,
            action: 'get-queue-messages',
            object_id: subKey,
            page_size: 50,
            filters: {sub_key: subKey, state: config.state},
            ts_field: 'pub_time_iso',
            table_body: '#messages-body',
            container_top: '#queue-pagination-top',
            container_bottom: '#queue-pagination-bottom',
            render_page: $.fn.zato.pubsub.queue._render_page,
            render_new: $.fn.zato.pubsub.queue._render_new,
            initial_data: config.initial_data,
            filter_tabs: {
                selector: '.dashboard-tab[data-state]',
                filter_key: 'state',
                url_key: 'state'
            },
            on_page_change: function() {
            },
            on_new_rows: function(rows, total) {
                $('#stat-depth').text(total.toLocaleString());
            }
        });
    };

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
