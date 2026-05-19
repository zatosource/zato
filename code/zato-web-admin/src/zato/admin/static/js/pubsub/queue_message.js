
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
            fields: [
                {name: 'msg_id', label: 'Message ID', format: 'mono'},
                {name: 'topic_name', label: 'Topic'},
                {name: 'pub_time_iso', label: 'Published', format: 'time'},
                {name: 'recv_time_iso', label: 'Received', format: 'time'},
                {name: 'expiration_time_iso', label: 'Expires', format: 'time'},
                {name: 'data_size', label: 'Size', suffix: ' B'},
                {name: 'priority', label: 'Priority'},
                {name: 'expiration', label: 'Expiration (ms)'},
                {name: 'redis_stream_id', label: 'Stream ID', format: 'mono'}
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

        var kit = $.fn.zato.dashboard_kit;

        var url_tab = kit.url_state.get('tab');
        if (url_tab) {
            var $target = $('.dashboard-tab[data-tab="' + url_tab + '"]');
            if ($target.length) {
                $('.dashboard-tab').removeClass('dashboard-tab-active').attr('aria-selected', 'false');
                $target.addClass('dashboard-tab-active').attr('aria-selected', 'true');
                $('.dashboard-tab-panel').attr('hidden', true);
                $('#dashboard-tab-panel-' + url_tab).removeAttr('hidden');
            }
        }

        $('.dashboard-tab').on('click', function() {
            var tab_name = $(this).data('tab');
            $('.dashboard-tab').removeClass('dashboard-tab-active').attr('aria-selected', 'false');
            $(this).addClass('dashboard-tab-active').attr('aria-selected', 'true');
            $('.dashboard-tab-panel').attr('hidden', true);
            $('#dashboard-tab-panel-' + tab_name).removeAttr('hidden');
            kit.url_state.set({tab: tab_name});
        });
    };

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
