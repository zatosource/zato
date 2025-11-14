
(function($) {

    var suppressedErrors = [
        'log-streaming',
        'EventSource',
        'interrupted while the page was loading',
        "can't establish a connection",
        'Loading failed for the <script>',
        'Content-Security-Policy'
    ];

    var originalError = console.error;
    console.error = function(message) {
        if (typeof message === 'string') {
            for (var i = 0; i < suppressedErrors.length; i++) {
                if (message.includes(suppressedErrors[i])) {
                    return;
                }
            }
        }
        originalError.apply(console, arguments);
    };

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

            console.debug('start_streaming: called');

            if (self.eventSource) {
                console.debug('start_streaming: already active, returning');
                return;
            }

            console.debug('start_streaming: creating EventSource for /zato/log-streaming/stream');
            self.eventSource = new EventSource('/zato/log-streaming/stream');

            self.eventSource.onopen = function(event) {
                console.debug('start_streaming: EventSource connection opened', event);
            };

            self.eventSource.onmessage = function(event) {
                if (event.data && event.data !== '{}') {
                    try {
                        var log_entry = JSON.parse(event.data);
                        var level = log_entry.level.replace(/\u001b\[[0-9;]*m/g, '').trim();
                        var formatted_message = level + ' - ' + log_entry.logger + ':' + log_entry.lineno + ' - ' + log_entry.message;

                        if (level === 'INFO') {
                            console.info(formatted_message);
                        } else if (level === 'WARNING') {
                            console.warn(formatted_message);
                        } else if (level === 'ERROR' || level === 'CRITICAL') {
                            console.error(formatted_message);
                        } else if (level === 'DEBUG') {
                            console.debug(formatted_message);
                        } else {
                            console.debug(formatted_message);
                        }
                    } catch (e) {
                        console.error('[ZATO LOG] Parse error:', e);
                        console.debug('[ZATO LOG] Raw:', event.data);
                    }
                }
            };

            self.eventSource.onerror = function(error) {
                console.debug('INFO start_streaming: error event', error);
                console.debug('INFO start_streaming: readyState:', self.eventSource.readyState);
                self.stop_streaming();
            };

            console.debug('start_streaming: EventSource created, readyState:', self.eventSource.readyState);
        },

        stop_streaming: function() {
            var self = this;

            if (self.eventSource) {
                self.eventSource.close();
                self.eventSource = null;
            }
        },

        init: function() {
            var self = this;

            console.debug('init: starting log streaming initialization');

            self.start_streaming();

            console.debug('init: checking streaming status');
            $.ajax({
                type: 'GET',
                url: '/zato/log-streaming/status',
                success: function(data) {
                    console.debug('init: status response:', data);
                    if (!data.streaming_enabled) {
                        console.debug('init: streaming disabled, enabling it');
                        $.ajax({
                            type: 'POST',
                            url: '/zato/log-streaming/toggle',
                            headers: {
                                'X-CSRFToken': $.cookie('csrftoken')
                            },
                            success: function(response) {
                                console.debug('init: toggle response:', response);
                            },
                            error: function(xhr, status, error) {
                                console.error('init: toggle error:', status, error);
                            }
                        });
                    } else {
                        console.debug('init: streaming already enabled');
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
