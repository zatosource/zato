
// ////////////////////////////////////////////////////////////////////////

(function($) {

    $.namespace('zato.pubsub.queue');

// ////////////////////////////////////////////////////////////////////////

    $.fn.zato.pubsub.queue._subKey = '';
    $.fn.zato.pubsub.queue._queueName = '';
    $.fn.zato.pubsub.queue._defaultErrorMessage = 'Unknown error';
    $.fn.zato.pubsub.queue._pagination = null;
    $.fn.zato.pubsub.queue._auto_refresh = null;
    $.fn.zato.pubsub.queue._new_row_count = 0;
    $.fn.zato.pubsub.queue._page_size = 50;

// ////////////////////////////////////////////////////////////////////////

    $.fn.zato.pubsub.queue._badge_class = 't4';

    $.fn.zato.pubsub.queue._render_row = function(message) {

        var kit = $.fn.zato.dashboard_kit;
        var queue = $.fn.zato.pubsub.queue;
        var subKey = queue._subKey;
        var relativeTime = kit.relative_time_past(message.pub_time_iso);
        var localTime = kit.format_local_time(message.pub_time_iso);
        var topicName = message.topic_name;

        var badgeKey = queue._badge_class;

        var messageLink = '/zato/pubsub/subscription/queue/message/?cluster=1' +
            '&sub_key=' + encodeURIComponent(subKey) +
            '&queue_name=' + encodeURIComponent(queue._queueName) +
            '&msg_id=' + encodeURIComponent(message.msg_id) +
            '&topic_name=' + encodeURIComponent(topicName) +
            '&redis_stream_id=' + encodeURIComponent(message.redis_stream_id);

        var topicLink = '/zato/pubsub/topic/?cluster=1&query=' + encodeURIComponent(topicName);

        var row = '<tr>';
        row += '<td class="queue-row-num"></td>';
        var deliveredLabel = message.is_delivered ? 'Yes' : 'No';

        if (message.is_delivered) {
            row += '<td class="queue-msg-id"><span class="dashboard-outcome-badge dashboard-outcome-' + badgeKey + '">' + message.msg_id + '</span></td>';
        } else {
            row += '<td class="queue-msg-id"><span class="dashboard-outcome-badge dashboard-outcome-' + badgeKey + '"><a href="' + messageLink + '">' + message.msg_id + '</a></span></td>';
        }

        row += '<td><a href="' + topicLink + '">' + topicName + '</a></td>';
        row += '<td>' + deliveredLabel + '</td>';
        row += '<td class="data-preview"><a href="#" class="queue-preview-link"' +
            ' data-msg-id="' + message.msg_id + '"' +
            ' data-topic-name="' + topicName + '"' +
            ' data-redis-stream-id="' + message.redis_stream_id + '"' +
            ' data-is-delivered="' + (message.is_delivered ? '1' : '0') + '"' +
            '><span class="syntax-light">' + message.data_preview_highlighted + '</span></a></td>';
        row += '<td>' + message.data_size + ' B</td>';
        row += '<td class="queue-time" data-ts="' + message.pub_time_iso + '" title="' + localTime + '">' + relativeTime + '</td>';

        if (message.is_delivered) {
            row += '<td><span class="form_hint">Delete</span></td>';
        } else {
            row += '<td><a href="#" class="queue-delete-link"' +
                ' data-msg-id="' + message.msg_id + '"' +
                ' data-topic-name="' + topicName + '"' +
                ' data-redis-stream-id="' + message.redis_stream_id + '"' +
                '>Delete</a></td>';
        }

        row += '</tr>';

        return row;
    };

// ////////////////////////////////////////////////////////////////////////

    $.fn.zato.pubsub.queue._render_page = function($body, rows, total) {

        var kit = $.fn.zato.dashboard_kit;

        $body.empty();
        $.fn.zato.pubsub.queue._new_row_count = rows.length;

        var depthFormatted = total.toLocaleString();
        var $depth = $('#stat-depth');
        if ($depth.text() !== depthFormatted) {
            $depth.text(depthFormatted);
        }

        if (rows.length === 0) {
            $body.append('<tr><td colspan="8">No messages</td></tr>');
            return;
        }

        for (var rowIdx = 0; rowIdx < rows.length; rowIdx++) {
            $body.append($.fn.zato.pubsub.queue._render_row(rows[rowIdx]));
        }

        var queue = $.fn.zato.pubsub.queue;
        var pagination = queue._pagination;
        var offset = pagination ? (pagination.current_page() - 1) * queue._page_size : 0;
        $body.find('.queue-row-num').each(function(idx) {
            $(this).text(kit.format_number_full(offset + idx + 1));
        });

        $.fn.zato.pubsub.queue._apply_recency_gradient();
    };

// ////////////////////////////////////////////////////////////////////////

    $.fn.zato.pubsub.queue._render_new = function($body, rows, max_rows) {

        var kit = $.fn.zato.dashboard_kit;

        for (var rowIdx = 0; rowIdx < rows.length; rowIdx++) {
            $body.prepend($.fn.zato.pubsub.queue._render_row(rows[rowIdx]));
            $.fn.zato.pubsub.queue._new_row_count++;
        }

        while ($body.children().length > max_rows) {
            $body.children().last().remove();
        }

        var queue = $.fn.zato.pubsub.queue;
        var pagination = queue._pagination;
        var offset = pagination ? (pagination.current_page() - 1) * queue._page_size : 0;
        $body.find('.queue-row-num').each(function(idx) {
            $(this).text(kit.format_number_full(offset + idx + 1));
        });
    };

// ////////////////////////////////////////////////////////////////////////

    $.fn.zato.pubsub.queue._recency_max_alpha = 0.20;

    $.fn.zato.pubsub.queue._apply_recency_gradient = function() {
        var kit = $.fn.zato.dashboard_kit;
        var maxAlpha = $.fn.zato.pubsub.queue._recency_max_alpha;
        var steps = kit.recency.STEPS;
        var limit = Math.min($.fn.zato.pubsub.queue._new_row_count, steps);
        var rgb = '218, 165, 32';
        var $body = $('#messages-body');
        var rows = $body.children('tr');

        rows.each(function(idx) {
            var $row = $(this);
            if (idx < limit) {
                var alpha = maxAlpha * Math.pow(1 - idx / steps, 2.5);
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

    $.fn.zato.pubsub.queue.clear_queue = function() {

        if (!confirm('Clear all pending messages from this queue?')) {
            return;
        }

        $.ajax({
            url: '/zato/pubsub/subscription/queue/clear/',
            type: 'POST',
            data: {
                sub_key: $.fn.zato.pubsub.queue._subKey
            },
            headers: {'X-CSRFToken': $.cookie('csrftoken')},
            success: function() {
                window.location.reload();
            },
            error: function(request) {
                var errorMessage = $.fn.zato.pubsub.queue._defaultErrorMessage;
                if (request.responseJSON) {
                    errorMessage = request.responseJSON.error;
                }
                alert('Error: ' + errorMessage);
            }
        });
    };

// ////////////////////////////////////////////////////////////////////////

    $.fn.zato.pubsub.queue.init = function(subKey, config) {

        var kit = $.fn.zato.dashboard_kit;

        // Store the sub_key and queue_name ..
        $.fn.zato.pubsub.queue._subKey = subKey;
        $.fn.zato.pubsub.queue._queueName = config.queue_name;

        // .. apply detail layout toggles ..
        kit.detail_layout.apply({
            show_dashboard_tabs: false,
            show_help_icon: false,
            show_table_header: true
        });

        // .. bind the clear button ..
        $('#clear-queue-button').on('click', function() {
            $.fn.zato.pubsub.queue.clear_queue();
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

        // .. wire data preview clicks to the overlay ..
        $(document).on('click', '.queue-preview-link', function(e) {
            e.preventDefault();
            var $link = $(this);
            var msgId = $link.data('msg-id');
            var topicName = $link.data('topic-name');
            var streamId = $link.data('redis-stream-id');

            var previewText = $link.text();

            $.ajax({
                type: 'POST',
                url: config.poll_url,
                data: JSON.stringify({
                    action: 'get-message-detail',
                    msg_id: msgId,
                    topic_name: topicName,
                    redis_stream_id: streamId
                }),
                contentType: 'application/json',
                headers: {'X-CSRFToken': $.cookie('csrftoken')},
                dataType: 'json',
                success: function(response) {
                    if (response.has_data) {
                        $.fn.zato.highlight_pane.open_overlay({
                            title: 'Data',
                            text: response.data,
                            editable: true,
                            buttons: [
                                $.fn.zato.highlight_pane.buttons.copy(),
                                $.fn.zato.highlight_pane.buttons.save({
                                    poll_url: config.poll_url,
                                    save_action: 'update-message',
                                    hidden_fields: {
                                        msg_id: msgId,
                                        topic_name: topicName,
                                        redis_stream_id: streamId
                                    }
                                })
                            ]
                        });
                    }
                    else {
                        $.fn.zato.highlight_pane.open_overlay({
                            title: 'Data preview',
                            text: previewText,
                            editable: false,
                            buttons: [
                                $.fn.zato.highlight_pane.buttons.copy()
                            ]
                        });
                    }
                }
            });
        });

        // .. build the delete confirmation overlay (once) ..
        var $deleteOverlay = null;
        var _deleteAceEditor = null;
        var _deleteContext = null;

        function _build_delete_overlay() {
            var html = '' +
                '<div class="queue-delete-overlay hidden" id="queue-delete-overlay">' +
                    '<div class="queue-delete-overlay-backdrop"></div>' +
                    '<div class="queue-delete-overlay-content">' +
                        '<div class="queue-delete-overlay-header">' +
                            '<h2 class="queue-delete-overlay-title">Delete message</h2>' +
                            '<button class="queue-delete-overlay-close-btn" type="button">\u00d7</button>' +
                        '</div>' +
                        '<div class="queue-delete-overlay-body">' +
                            '<p class="queue-delete-overlay-msg-id"></p>' +
                            '<div class="queue-delete-overlay-editor" id="queue-delete-editor"></div>' +
                        '</div>' +
                        '<div class="queue-delete-overlay-footer">' +
                            '<button class="zato-action-button queue-delete-overlay-cancel" type="button">Cancel</button>' +
                            '<button class="zato-action-button queue-delete-overlay-confirm" type="button">Delete</button>' +
                        '</div>' +
                    '</div>' +
                '</div>';

            $('body').append(html);
            $deleteOverlay = $('#queue-delete-overlay');

            _deleteAceEditor = ace.edit('queue-delete-editor');
            _deleteAceEditor.setTheme('ace/theme/monokai');
            _deleteAceEditor.session.setMode('ace/mode/json');
            _deleteAceEditor.setShowPrintMargin(false);
            _deleteAceEditor.setFontSize(13);

            $deleteOverlay.find('.queue-delete-overlay-backdrop').on('click', _close_delete_overlay);
            $deleteOverlay.find('.queue-delete-overlay-close-btn').on('click', _close_delete_overlay);
            $deleteOverlay.find('.queue-delete-overlay-cancel').on('click', _close_delete_overlay);

            $deleteOverlay.find('.queue-delete-overlay-confirm').on('click', function() {
                _perform_delete();
            });

            $(document).on('keydown.queue_delete_overlay', function(e) {
                if (e.key === 'Escape' && $deleteOverlay && !$deleteOverlay.hasClass('hidden')) {
                    _close_delete_overlay();
                }
            });
        }

        function _open_delete_overlay(msgId, data, $row, topicName, streamId) {
            if (!$deleteOverlay) {
                _build_delete_overlay();
            }

            _deleteContext = {
                msgId: msgId,
                topicName: topicName,
                streamId: streamId,
                $row: $row
            };

            $deleteOverlay.find('.queue-delete-overlay-msg-id').text(msgId);
            _deleteAceEditor.setValue(data, -1);
            $deleteOverlay.removeClass('hidden');
        }

        function _close_delete_overlay() {
            if ($deleteOverlay) {
                $deleteOverlay.addClass('hidden');
            }
            _deleteContext = null;
        }

        function _perform_delete() {
            var ctx = _deleteContext;

            $.ajax({
                type: 'POST',
                url: '/zato/pubsub/subscription/queue/message/delete/',
                data: JSON.stringify({
                    msg_id: ctx.msgId,
                    topic_name: ctx.topicName,
                    sub_key: subKey,
                    redis_stream_id: ctx.streamId
                }),
                contentType: 'application/json',
                headers: {'X-CSRFToken': $.cookie('csrftoken')},
                dataType: 'json',
                success: function() {
                    ctx.$row.remove();

                    var queue = $.fn.zato.pubsub.queue;
                    var pagination = queue._pagination;
                    var newTotal = pagination.total() - 1;
                    pagination.set_total(newTotal);
                    $('#stat-depth').text(newTotal.toLocaleString());

                    _close_delete_overlay();
                },
                error: function(request) {
                    var errorMessage = $.fn.zato.pubsub.queue._defaultErrorMessage;
                    if (request.responseJSON) {
                        errorMessage = request.responseJSON.error;
                    }
                    alert('Error: ' + errorMessage);
                }
            });
        }

        // .. wire delete link clicks ..
        $(document).on('click', '.queue-delete-link', function(e) {
            e.preventDefault();

            var $link = $(this);
            var $row = $link.closest('tr');
            var msgId = $link.data('msg-id');
            var topicName = $link.data('topic-name');
            var streamId = $link.data('redis-stream-id');
            var previewText = $row.find('.data-preview').text();

            $.ajax({
                type: 'POST',
                url: '/zato/pubsub/subscription/queue/message/payload/',
                data: JSON.stringify({
                    msg_id: msgId,
                    topic_name: topicName
                }),
                contentType: 'application/json',
                headers: {'X-CSRFToken': $.cookie('csrftoken')},
                dataType: 'json',
                success: function(response) {
                    var data = response.data ? response.data : previewText;
                    _open_delete_overlay(msgId, data, $row, topicName, streamId);
                },
                error: function() {
                    _open_delete_overlay(msgId, previewText, $row, topicName, streamId);
                }
            });
        });

        $(document).on('click.queue_state', function() {
            $stateMenu.removeClass('dashboard-time-range-menu-open');
        });
    };

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
