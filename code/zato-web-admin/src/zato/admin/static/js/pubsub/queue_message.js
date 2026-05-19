
// ////////////////////////////////////////////////////////////////////////

(function($) {

    $.namespace('zato.pubsub.queue_message');

// ////////////////////////////////////////////////////////////////////////

    $.fn.zato.pubsub.queue_message.init = function(messageData, pollUrl) {

        var kit = $.fn.zato.dashboard_kit;

        // Initialize tabs ..
        $.fn.zato.pubsub.queue_message.init_tabs();

        // .. render the metadata cards in the Metadata tab ..
        kit.meta_cards.render({
            container: '#message-metadata-cards',
            data: messageData,
            groups: [
                {fields: [
                    {name: 'msg_id', label: 'Message ID', format: 'mono'},
                    {name: 'topic_name', label: 'Topic'}
                ]},
                {fields: [
                    {name: 'pub_time_iso', label: 'Published', format: 'time'},
                    {name: 'recv_time_iso', label: 'Received', format: 'time'},
                    {name: 'expiration_time_iso', label: 'Expires', format: 'time'}
                ]},
                {fields: [
                    {name: 'data_size', label: 'Size', suffix: ' B'},
                    {name: 'priority', label: 'Priority'},
                    {name: 'expiration', label: 'Expiration (ms)'}
                ]}
            ]
        });

        // .. render the editable payload form in the Message data tab ..
        kit.record_edit.init({
            container: '#record-edit-form',
            poll_url: pollUrl,
            save_action: 'update-message',
            fields: [
                {name: 'data', type: 'textarea', label: 'Payload', monospace: true}
            ],
            readonly_fields: [],
            hidden_fields: ['msg_id', 'topic_name', 'redis_stream_id'],
            data: messageData
        });

    };

// ////////////////////////////////////////////////////////////////////////

    $.fn.zato.pubsub.queue_message.init_tabs = function() {

        $('.dashboard-tab').on('click', function() {
            var tab_name = $(this).data('tab');
            $('.dashboard-tab').removeClass('dashboard-tab-active').attr('aria-selected', 'false');
            $(this).addClass('dashboard-tab-active').attr('aria-selected', 'true');
            $('.dashboard-tab-panel').attr('hidden', true);
            $('#dashboard-tab-panel-' + tab_name).removeAttr('hidden');

            var url = new URL(window.location.href);
            url.searchParams.set('tab', tab_name);
            window.history.replaceState(null, '', url.toString());
        });
    };

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
