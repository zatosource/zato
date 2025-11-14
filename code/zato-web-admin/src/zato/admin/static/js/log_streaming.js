
(function($) {

    $.fn.zato.log_streaming = new Class({

        toString: function() {
            var s = '<LogStreaming>';
            return s;
        },

        eventSource: null,

        get_status: function() {
            var self = this;

            $.ajax({
                type: 'GET',
                url: '/zato/log-streaming/status',
                success: function(data) {
                    var streaming_enabled = data.streaming_enabled;
                    var status_text = streaming_enabled ? 'enabled' : 'disabled';
                    alert('Current log streaming status: ' + status_text);
                },
                error: function(xhr, status, error) {
                    alert('Error getting log streaming status: ' + error);
                }
            });
        },

        toggle: function() {
            var self = this;

            $.ajax({
                type: 'POST',
                url: '/zato/log-streaming/toggle',
                headers: {
                    'X-CSRFToken': $.cookie('csrftoken')
                },
                success: function(data) {
                    var streaming_enabled = data.streaming_enabled;
                    var status_text = streaming_enabled ? 'enabled' : 'disabled';
                    alert('New log streaming status: ' + status_text);
                },
                error: function(xhr, status, error) {
                    alert('Error toggling log streaming: ' + error);
                }
            });
        },

        start_streaming: function() {
            var self = this;

            if (self.eventSource) {
                console.log('Log streaming already active');
                return;
            }

            self.eventSource = new EventSource('/zato/log-streaming/stream');

            self.eventSource.onmessage = function(event) {
                if (event.data && event.data !== '{}') {
                    try {
                        var log_entry = JSON.parse(event.data);
                        console.log('[ZATO LOG]', log_entry);
                    } catch (e) {
                        console.log('[ZATO LOG] Raw:', event.data);
                    }
                }
            };

            self.eventSource.onerror = function(error) {
                console.error('Log streaming error:', error);
                self.stop_streaming();
            };

            console.log('Log streaming started');
        },

        stop_streaming: function() {
            var self = this;

            if (self.eventSource) {
                self.eventSource.close();
                self.eventSource = null;
                console.log('Log streaming stopped');
            }
        },

        init: function() {
            var self = this;

            self.start_streaming();

            $.ajax({
                type: 'GET',
                url: '/zato/log-streaming/status',
                success: function(data) {
                    console.log('Streaming status:', data.streaming_enabled);
                    if (!data.streaming_enabled) {
                        console.log('Enabling streaming');
                        $.ajax({
                            type: 'POST',
                            url: '/zato/log-streaming/toggle',
                            headers: {
                                'X-CSRFToken': $.cookie('csrftoken')
                            },
                            success: function(response) {
                                console.log('Streaming enabled:', response);
                            }
                        });
                    }
                }
            });
        }

    });

    $.fn.zato.log_streaming = new $.fn.zato.log_streaming();

})(jQuery);
