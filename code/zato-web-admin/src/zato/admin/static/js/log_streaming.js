
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

            console.log('start_streaming: called');

            if (self.eventSource) {
                console.log('start_streaming: already active, returning');
                return;
            }

            console.log('start_streaming: creating EventSource for /zato/log-streaming/stream');
            self.eventSource = new EventSource('/zato/log-streaming/stream');

            self.eventSource.onopen = function(event) {
                console.log('start_streaming: EventSource connection opened', event);
            };

            self.eventSource.onmessage = function(event) {
                console.log('start_streaming: received message, data length:', event.data ? event.data.length : 0);
                if (event.data && event.data !== '{}') {
                    try {
                        var log_entry = JSON.parse(event.data);
                        console.log('[ZATO LOG]', log_entry);
                    } catch (e) {
                        console.log('[ZATO LOG] Parse error:', e);
                        console.log('[ZATO LOG] Raw:', event.data);
                    }
                } else {
                    console.log('start_streaming: empty or {} data, ignoring');
                }
            };

            self.eventSource.onerror = function(error) {
                console.error('start_streaming: error event', error);
                console.error('start_streaming: readyState:', self.eventSource.readyState);
                self.stop_streaming();
            };

            console.log('start_streaming: EventSource created, readyState:', self.eventSource.readyState);
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

            console.log('init: starting log streaming initialization');

            self.start_streaming();

            console.log('init: checking streaming status');
            $.ajax({
                type: 'GET',
                url: '/zato/log-streaming/status',
                success: function(data) {
                    console.log('init: status response:', data);
                    if (!data.streaming_enabled) {
                        console.log('init: streaming disabled, enabling it');
                        $.ajax({
                            type: 'POST',
                            url: '/zato/log-streaming/toggle',
                            headers: {
                                'X-CSRFToken': $.cookie('csrftoken')
                            },
                            success: function(response) {
                                console.log('init: toggle response:', response);
                            },
                            error: function(xhr, status, error) {
                                console.error('init: toggle error:', status, error);
                            }
                        });
                    } else {
                        console.log('init: streaming already enabled');
                    }
                },
                error: function(xhr, status, error) {
                    console.error('init: status check error:', status, error);
                }
            });
        }

    });

    $.fn.zato.log_streaming = new $.fn.zato.log_streaming();

})(jQuery);
