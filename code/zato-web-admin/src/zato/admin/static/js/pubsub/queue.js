
// ////////////////////////////////////////////////////////////////////////

(function($) {

    $.namespace('zato.pubsub.queue');

// ////////////////////////////////////////////////////////////////////////

    $.fn.zato.pubsub.queue._subKey = '';
    $.fn.zato.pubsub.queue._defaultErrorMessage = 'Unknown error';

// ////////////////////////////////////////////////////////////////////////

    $.fn.zato.pubsub.queue.render = function(data) {

        var kit = $.fn.zato.dashboard_kit;

        // Update the depth stat card ..
        var depth = data.total;
        var depthFormatted = depth.toLocaleString();
        $('#stat-depth').text(depthFormatted);

        // .. render the messages table ..
        var $messagesBody = $('#messages-body');
        $messagesBody.empty();

        var messages = data.rows;
        var subKey = $.fn.zato.pubsub.queue._subKey;

        var messageCount = messages.length;

        if (messageCount === 0) {
            $messagesBody.append('<tr><td colspan="5">No pending messages</td></tr>');
            return;
        }

        for (var messageIndex = 0; messageIndex < messageCount; messageIndex++) {
            var message = messages[messageIndex];
            var relativeTime = kit.relative_time_past(message.pub_time_iso);
            var localTime = kit.format_local_time(message.pub_time_iso);
            var topicName = message.topic_name;

            // .. build the message detail link ..
            var messageLink = '/zato/pubsub/subscription/queue/message/?cluster=1' +
                '&sub_key=' + encodeURIComponent(subKey) +
                '&msg_id=' + encodeURIComponent(message.msg_id) +
                '&topic_name=' + encodeURIComponent(topicName) +
                '&redis_stream_id=' + encodeURIComponent(message.redis_stream_id);

            // .. build the topic link ..
            var topicLink = '/zato/pubsub/topic/?cluster=1&query=' + encodeURIComponent(topicName);

            // .. and render the row.
            var row = '<tr>';
            row += '<td style="font-family:monospace; font-size:12px"><a href="' + messageLink + '">' + message.msg_id + '</a></td>';
            row += '<td><a href="' + topicLink + '">' + topicName + '</a></td>';
            row += '<td class="data-preview">' + $('<span>').text(message.data_preview).html() + '</td>';
            row += '<td>' + message.data_size + ' B</td>';
            row += '<td title="' + localTime + '">' + relativeTime + '</td>';
            row += '</tr>';

            $messagesBody.append(row);
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

    $.fn.zato.pubsub.queue.init = function(subKey, initialData) {

        // Store the sub_key for purge operations ..
        $.fn.zato.pubsub.queue._subKey = subKey;

        // .. parse the initial data if it is a string ..
        if (typeof initialData === 'string') {
            initialData = JSON.parse(initialData);
        }

        // .. bind the purge button ..
        $('#purge-queue-button').on('click', function() {
            $.fn.zato.pubsub.queue.purge();
        });

        // .. and render the page.
        $.fn.zato.pubsub.queue.render(initialData);
    };

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
