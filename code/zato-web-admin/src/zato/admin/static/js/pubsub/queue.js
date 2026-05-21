
// ////////////////////////////////////////////////////////////////////////

(function($) {

    $.namespace('zato.pubsub.queue');

// ////////////////////////////////////////////////////////////////////////

    $.fn.zato.pubsub.queue._subKey = '';
    $.fn.zato.pubsub.queue._defaultErrorMessage = 'Unknown error';
    $.fn.zato.pubsub.queue._pagination = null;
    $.fn.zato.pubsub.queue._auto_refresh = null;
    $.fn.zato.pubsub.queue._new_row_count = 0;
    $.fn.zato.pubsub.queue._time_ticker = null;

// ////////////////////////////////////////////////////////////////////////

    $.fn.zato.pubsub.queue._badge_class = 't4';

    $.fn.zato.pubsub.queue._render_row = function(message) {

        var kit = $.fn.zato.dashboard_kit;
        var ns = $.fn.zato.pubsub.queue;
        var subKey = ns._subKey;
        var relativeTime = kit.relative_time_past(message.pub_time_iso);
        var localTime = kit.format_local_time(message.pub_time_iso);
        var topicName = message.topic_name;

        var badgeKey = ns._badge_class;

        var messageLink = '/zato/pubsub/subscription/queue/message/?cluster=1' +
            '&sub_key=' + encodeURIComponent(subKey) +
            '&msg_id=' + encodeURIComponent(message.msg_id) +
            '&topic_name=' + encodeURIComponent(topicName) +
            '&redis_stream_id=' + encodeURIComponent(message.redis_stream_id);

        var topicLink = '/zato/pubsub/topic/?cluster=1&query=' + encodeURIComponent(topicName);

        var row = '<tr>';
        row += '<td class="queue-row-num"></td>';
        row += '<td class="queue-msg-id"><span class="dashboard-outcome-badge dashboard-outcome-' + badgeKey + '"><a href="' + messageLink + '">' + message.msg_id + '</a></span></td>';
        row += '<td><a href="' + topicLink + '">' + topicName + '</a></td>';
        row += '<td class="data-preview">' + $('<span>').text(message.data_preview).html() + '</td>';
        row += '<td>' + message.data_size + ' B</td>';
        row += '<td class="queue-time" data-ts="' + message.pub_time_iso + '" title="' + localTime + '">' + relativeTime + '</td>';
        row += '</tr>';

        return row;
    };

// ////////////////////////////////////////////////////////////////////////

    $.fn.zato.pubsub.queue._render_page = function($body, rows, total) {

        $body.empty();
        $.fn.zato.pubsub.queue._new_row_count = rows.length;

        var depthFormatted = total.toLocaleString();
        var $depth = $('#stat-depth');
        if ($depth.text() !== depthFormatted) {
            $depth.text(depthFormatted);
        }

        if (rows.length === 0) {
            $body.append('<tr><td colspan="6">No messages</td></tr>');
            return;
        }

        for (var i = 0; i < rows.length; i++) {
            $body.append($.fn.zato.pubsub.queue._render_row(rows[i]));
        }

        $.fn.zato.pubsub.queue._apply_recency_gradient();
    };

// ////////////////////////////////////////////////////////////////////////

    $.fn.zato.pubsub.queue._render_new = function($body, rows, max_rows) {

        for (var i = 0; i < rows.length; i++) {
            $body.prepend($.fn.zato.pubsub.queue._render_row(rows[i]));
            $.fn.zato.pubsub.queue._new_row_count++;
        }

        while ($body.children().length > max_rows) {
            $body.children().last().remove();
        }
    };

// ////////////////////////////////////////////////////////////////////////

    $.fn.zato.pubsub.queue._recency_max_alpha = 0.20;

    $.fn.zato.pubsub.queue._apply_recency_gradient = function() {
        var kit = $.fn.zato.dashboard_kit;
        var max_a = $.fn.zato.pubsub.queue._recency_max_alpha;
        var steps = kit.recency.STEPS;
        var limit = Math.min($.fn.zato.pubsub.queue._new_row_count, steps);
        var rgb = '218, 165, 32';
        var $body = $('#messages-body');
        var rows = $body.children('tr');

        rows.each(function(idx) {
            var $row = $(this);
            if (idx < limit) {
                var alpha = max_a * Math.pow(1 - idx / steps, 2.5);
                $row.css('background', 'rgba(' + rgb + ', ' + alpha.toFixed(4) + ')');
            } else {
                $row.css('background', '');
            }
        });
    };

// ////////////////////////////////////////////////////////////////////////

    $.fn.zato.pubsub.queue._tick_times = function() {
        var kit = $.fn.zato.dashboard_kit;
        $('#messages-body .queue-time').each(function() {
            var $cell = $(this);
            $cell.text(kit.relative_time_past($cell.data('ts')));
        });
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

        // .. initialize pagination ..
        $.fn.zato.pubsub.queue._pagination = kit.pagination.init({
            poll_url: config.poll_url,
            action: 'get-queue-messages',
            object_id: subKey,
            page_size: 50,
            filters: {sub_key: subKey, state: config.state},
            ts_field: 'redis_stream_id',
            table_body: '#messages-body',
            container_top: '#queue-pagination-top',
            container_bottom: '#queue-pagination-bottom',
            render_page: $.fn.zato.pubsub.queue._render_page,
            render_new: $.fn.zato.pubsub.queue._render_new,
            initial_data: config.initial_data,
            on_page_change: function() {
            },
            on_new_rows: function(rows, total) {
                $.fn.zato.pubsub.queue._new_row_count += rows.length;
                $('#stat-depth').text(total.toLocaleString());
                $.fn.zato.pubsub.queue._apply_recency_gradient();
            }
        });

        // .. initialize auto-refresh ..
        $.fn.zato.pubsub.queue._auto_refresh = kit.auto_refresh.init({
            pill: '#queue-refresh-pill',
            menu: '#queue-refresh-menu',
            storage_key: 'zato_queue_refresh_' + subKey,
            url_param: 'refresh',
            default_seconds: 5,
            on_tick: function() {
                $.fn.zato.pubsub.queue._pagination.poll_new();
                $.fn.zato.pubsub.queue._tick_times();
            }
        });

        // .. and wire the state pill dropdown.
        var stateLabels = {pending: 'Pending', all: 'All', delivered: 'Delivered'};
        var $statePill = $('#queue-state-pill');
        var $stateMenu = $('#queue-state-menu');

        $statePill.on('click', function(e) {
            e.stopPropagation();
            $stateMenu.toggleClass('dashboard-time-range-menu-open');
        });

        $stateMenu.on('click', '.dashboard-time-range-option', function(e) {
            e.stopPropagation();
            var newState = $(this).data('state');

            $stateMenu.find('.dashboard-time-range-option').removeClass('dashboard-time-range-active');
            $(this).addClass('dashboard-time-range-active');
            $stateMenu.removeClass('dashboard-time-range-menu-open');

            $statePill.text(stateLabels[newState]);

            $.fn.zato.pubsub.queue._pagination.set_filters({state: newState});
            $.fn.zato.pubsub.queue._pagination.fetch_page(1);

            var urlParams = new URLSearchParams(window.location.search);
            urlParams.set('state', newState);
            history.replaceState(null, '', '?' + urlParams.toString());
        });

        $(document).on('click.queue_state', function() {
            $stateMenu.removeClass('dashboard-time-range-menu-open');
        });

        $.fn.zato.pubsub.queue._time_ticker = setInterval(
            $.fn.zato.pubsub.queue._tick_times, 1000);
    };

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
