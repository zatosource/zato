
// ////////////////////////////////////////////////////////////////////////

(function($) {

    $.namespace('zato.pubsub.queue_message');

// ////////////////////////////////////////////////////////////////////////

    $.fn.zato.pubsub.queue_message.init = function(messageData, pollUrl) {

        var kit = $.fn.zato.dashboard_kit;

        // Initialize tabs ..
        $.fn.zato.pubsub.queue_message.initTabs();

        // .. render the metadata cards in the Metadata tab ..
        kit.meta_cards.render({
            container: '#message-metadata-cards',
            data: messageData,
            copy_as_json: true,
            copy_tooltip_follows_cursor: true,
            groups: [
                {fields: [
                    {name: 'msg_id', label: 'Message ID', format: 'mono', copy_key: 'message_id'},
                    {name: 'topic_name', label: 'Topic', copy_key: 'topic_name'}
                ]},
                {fields: [
                    {name: 'pub_time_iso', label: 'Published', format: 'time', copy_key: 'published'},
                    {name: 'recv_time_iso', label: 'Received', format: 'time', copy_key: 'received'},
                    {name: 'expiration_time_iso', label: 'Expires', format: 'time', copy_key: 'expires'}
                ]},
                {fields: [
                    {name: 'data_size', label: 'Size', suffix: ' B', copy_key: 'size'},
                    {name: 'priority', label: 'Priority', copy_key: 'priority'},
                    {name: 'expiration', label: 'Expiration (ms)', copy_key: 'expiration_ms'}
                ]}
            ]
        });

        // .. and render the editable payload in the Message data tab.
        $.fn.zato.highlight_pane.init({
            container: '#record-edit-form',
            text: messageData.data,
            editable: true,
            buttons: [
                $.fn.zato.highlight_pane.buttons.copy(),
                $.fn.zato.highlight_pane.buttons.save({
                    poll_url: pollUrl,
                    save_action: 'update-message',
                    hidden_fields: {
                        msg_id: messageData.msg_id,
                        topic_name: messageData.topic_name,
                        redis_stream_id: messageData.redis_stream_id
                    }
                })
            ]
        });
    };

// ////////////////////////////////////////////////////////////////////////

    $.fn.zato.pubsub.queue_message.initTabs = function() {

        // Bind tab click handlers to switch panels and update the URL ..
        $('.dashboard-tab').on('click', function() {

            var tabName = $(this).data('tab');

            // .. deactivate all tabs ..
            var $allTabs = $('.dashboard-tab');
            $allTabs.removeClass('dashboard-tab-active');
            $allTabs.attr('aria-selected', 'false');

            // .. activate the clicked tab ..
            var $clickedTab = $(this);
            $clickedTab.addClass('dashboard-tab-active');
            $clickedTab.attr('aria-selected', 'true');

            // .. hide all panels and show the target ..
            $('.dashboard-tab-panel').attr('hidden', true);
            $('#dashboard-tab-panel-' + tabName).removeAttr('hidden');

            // .. and persist the tab selection in the URL.
            var url = new URL(window.location.href);
            url.searchParams.set('tab', tabName);
            var urlString = url.toString();
            window.history.replaceState(null, '', urlString);
        });
    };

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
