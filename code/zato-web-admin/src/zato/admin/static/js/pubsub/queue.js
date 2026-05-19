
// ////////////////////////////////////////////////////////////////////////

(function($) {

    $.namespace('zato.pubsub.queue');

// ////////////////////////////////////////////////////////////////////////

    $.fn.zato.pubsub.queue._subKey = '';

// ////////////////////////////////////////////////////////////////////////

    $.fn.zato.pubsub.queue.relativeTime = function(isoTimestamp) {

        // Parse the ISO timestamp into epoch seconds ..
        var date = new Date(isoTimestamp);
        var timestampSeconds = date.getTime() / 1000;

        if (timestampSeconds <= 0) {
            return '-';
        }

        // .. compute the difference from now ..
        var nowSeconds = Date.now() / 1000;
        var diff = nowSeconds - timestampSeconds;

        if (diff < 0) {
            diff = 0;
        }

        // .. and format it as a human-readable string.
        if (diff < 60) {
            return Math.floor(diff) + ' sec ago';
        }

        if (diff < 3600) {
            return Math.floor(diff / 60) + ' min ago';
        }

        if (diff < 86400) {
            return Math.floor(diff / 3600) + 'h ago';
        }

        return Math.floor(diff / 86400) + 'd ago';
    };

// ////////////////////////////////////////////////////////////////////////

    $.fn.zato.pubsub.queue.formatLocalTime = function(isoTimestamp) {

        var date = new Date(isoTimestamp);
        var year = date.getFullYear();
        var month = ('0' + (date.getMonth() + 1)).slice(-2);
        var day = ('0' + date.getDate()).slice(-2);
        var hours = ('0' + date.getHours()).slice(-2);
        var minutes = ('0' + date.getMinutes()).slice(-2);
        var seconds = ('0' + date.getSeconds()).slice(-2);

        return year + '-' + month + '-' + day + ' ' + hours + ':' + minutes + ':' + seconds;
    };

// ////////////////////////////////////////////////////////////////////////

    $.fn.zato.pubsub.queue.render = function(data) {

        // Update the depth stat card ..
        var depth = data.depth;
        $('#stat-depth').text(depth.toLocaleString());

        // .. render the messages table ..
        var $messagesBody = $('#messages-body');
        $messagesBody.empty();

        var messages = data.messages;
        var subKey = $.fn.zato.pubsub.queue._subKey;

        if (messages.length === 0) {
            $messagesBody.append('<tr><td colspan="5">No pending messages</td></tr>');
            return;
        }

        for (var messageIdx = 0; messageIdx < messages.length; messageIdx++) {
            var message = messages[messageIdx];
            var relativeTime = $.fn.zato.pubsub.queue.relativeTime(message.pub_time_iso);
            var localTime = $.fn.zato.pubsub.queue.formatLocalTime(message.pub_time_iso);
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
                var errorMessage = 'Unknown error';
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

        // .. and render the page.
        $.fn.zato.pubsub.queue.render(initialData);
    };

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
