
// ////////////////////////////////////////////////////////////////////////

(function($) {

    $.namespace('zato.pubsub.queue_message');

// ////////////////////////////////////////////////////////////////////////

    $.fn.zato.pubsub.queue_message.init = function(messageData, pollUrl) {

        var kit = $.fn.zato.dashboard_kit;

        // Initialize the record edit form with message-specific field config ..
        kit.record_edit.init({
            container: '#record-edit-form',
            poll_url: pollUrl,
            save_action: 'update-message',
            fields: [
                {name: 'data', type: 'textarea', label: 'Payload', monospace: true},
                {name: 'priority', type: 'number', label: 'Priority'},
                {name: 'expiration', type: 'number', label: 'Expiration (ms)'},
                {name: 'correl_id', type: 'text', label: 'Correlation ID'},
                {name: 'in_reply_to', type: 'text', label: 'In reply to'},
                {name: 'ext_client_id', type: 'text', label: 'External client ID'}
            ],
            readonly_fields: [
                {name: 'topic_name', label: 'Topic'},
                {name: 'pub_time_iso', label: 'Published', format: 'time'},
                {name: 'recv_time_iso', label: 'Received', format: 'time'},
                {name: 'expiration_time_iso', label: 'Expires', format: 'time'},
                {name: 'data_size', label: 'Size', suffix: ' B'}
            ],
            hidden_fields: ['msg_id', 'topic_name', 'redis_stream_id'],
            data: messageData
        });
    };

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
