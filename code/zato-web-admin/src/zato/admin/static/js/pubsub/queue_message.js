
// ////////////////////////////////////////////////////////////////////////

(function($) {

    $.namespace('zato.pubsub.queue_message');

// ////////////////////////////////////////////////////////////////////////

    $.fn.zato.pubsub.queue_message.init = function(messageData, pollUrl, payloadUrl) {

        var kit = $.fn.zato.dashboard_kit;

        // Initialize tabs ..
        $.fn.zato.pubsub.queue_message.initTabs();

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

        // .. and render the editable payload form in the Message data tab.
        kit.record_edit.init({
            container: '#record-edit-form',
            poll_url: pollUrl,
            save_action: 'update-message',
            show_labels: false,
            show_copy_button: true,
            copy_field: 'data',
            fields: [
                {name: 'data', type: 'textarea', monospace: true}
            ],
            readonly_fields: [],
            hidden_fields: ['msg_id', 'topic_name', 'redis_stream_id'],
            data: messageData,
            on_save_success: function() {
                $.fn.zato.pubsub.queue_message.refreshPayload(payloadUrl, messageData);
            }
        });
    };

// ////////////////////////////////////////////////////////////////////////

    $.fn.zato.pubsub.queue_message.refreshPayload = function(payloadUrl, messageData) {

        var payload = {
            msg_id: messageData.msg_id,
            topic_name: messageData.topic_name
        };

        $.ajax({
            type: 'POST',
            url: payloadUrl,
            headers: {'X-CSRFToken': $.cookie('csrftoken')},
            data: JSON.stringify(payload),
            contentType: 'application/json',
            success: function(response) {
                var $textarea = $('#record-edit-data');
                if ($textarea.length) {
                    $textarea.val(response.data);
                }
            }
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
