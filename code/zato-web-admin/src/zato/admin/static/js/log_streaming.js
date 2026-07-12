
(function($) {

    var suppressedErrors = [
        'log-streaming',
        'interrupted while the page was loading',
        "can't establish a connection",
        'Loading failed for the <script>'
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

        config: {
            poll_interval_ms: 1000,
            url: '/zato/log-streaming/read'
        },

        connection: null,

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

            console.debug('toggle: called');

            $.ajax({
                type: 'POST',
                url: '/zato/log-streaming/toggle',
                headers: {
                    'X-CSRFToken': $.cookie('csrftoken')
                },
                success: function(data) {
                    console.debug('toggle: success response:', data);
                    var streaming_enabled = data.streaming_enabled;
                    var status_text = streaming_enabled ? 'enabled' : 'disabled';
                    console.debug('toggle: new status:', status_text);
                    alert('New log streaming status: ' + status_text);
                },
                error: function(xhr, status, error) {
                    console.error('toggle: error:', status, error, xhr);
                    alert('Error toggling log streaming: ' + error);
                }
            });
        },

        render_entry: function(log_entry) {
            var self = this;

            var isFirefox = navigator.userAgent.indexOf('Firefox') !== -1;

            function getTimestamp() {
                var now = new Date();
                var hours = String(now.getHours()).padStart(2, '0');
                var minutes = String(now.getMinutes()).padStart(2, '0');
                var seconds = String(now.getSeconds()).padStart(2, '0');
                var milliseconds = String(now.getMilliseconds()).padStart(3, '0');
                return hours + ':' + minutes + ':' + seconds + '.' + milliseconds;
            }

            var level = log_entry.level.trim();
            var message = log_entry.message;

            var timestamp = isFirefox ? '' : getTimestamp() + ' ';

            var firefoxExtra = isFirefox ? ' font-family: monospace; display: inline-block; width: 70px; text-align: center;' : '';

            var levelStyle = '';
            if (level === 'DEBUG') {
                levelStyle = 'background: #e9ecef; color: #495057; padding: 1px 4px; border-radius: 2px;' + firefoxExtra;
            } else if (level === 'INFO') {
                levelStyle = 'background: #d1ecf1; color: #0c5460; padding: 1px 4px; border-radius: 2px;' + firefoxExtra;
            } else if (level === 'WARNING') {
                levelStyle = 'background: #fff3cd; color: #664d03; padding: 1px 4px; border-radius: 2px; font-weight: bold;' + firefoxExtra;
            } else if (level === 'ERROR' || level === 'CRITICAL') {
                levelStyle = 'background: #f8d7da; color: #721c24; padding: 1px 4px; border-radius: 2px;' + firefoxExtra;
            }

            if (message.indexOf('\n') !== -1 && !isFirefox) {
                var lines = message.split('\n');
                var firstLine = lines[0];

                console.groupCollapsed(timestamp + '%c' + level + '%c - ' + firstLine, levelStyle, '');
                console.log(message);
                console.groupEnd();
            } else {
                console.info(timestamp + '%c' + level + '%c - ' + message, levelStyle, '');
            }
        },

        poll: function(connection) {
            var self = this;

            // The loop may have been stopped while a previous poll was in flight
            if (!connection.is_active) {
                return;
            }

            $.ajax({
                type: 'POST',
                url: self.config.url,
                data: JSON.stringify({'last_id': connection.last_id}),
                contentType: 'application/json',
                dataType: 'json',
                headers: {
                    'X-CSRFToken': $.cookie('csrftoken')
                },
                success: function(data) {

                    // Ignore a response that arrives after the loop was stopped
                    if (!connection.is_active) {
                        return;
                    }

                    connection.last_id = data.last_id;

                    for (var entryIdx = 0; entryIdx < data.entries.length; entryIdx++) {
                        self.render_entry(data.entries[entryIdx]);
                    }
                },
                error: function(xhr, status, error) {
                    console.debug('poll: error:', status, error);
                },
                complete: function() {

                    // Schedule the next poll only once this one has fully completed,
                    // so polls never overlap even when the server is slow.
                    if (connection.is_active) {
                        connection.timer_id = setTimeout(function() {
                            self.poll(connection);
                        }, self.config.poll_interval_ms);
                    }
                }
            });
        },

        start_streaming: function() {
            var self = this;

            console.debug('start_streaming: called');

            if (self.connection) {
                console.debug('start_streaming: already active, returning');
                return;
            }

            self.connection = {
                is_active: true,
                last_id: '',
                timer_id: null
            };

            self.poll(self.connection);
        },

        stop_streaming: function() {
            var self = this;

            console.debug('stop_streaming: called');
            if (self.connection) {
                self.connection.is_active = false;
                if (self.connection.timer_id) {
                    clearTimeout(self.connection.timer_id);
                }
                self.connection = null;
                console.debug('stop_streaming: poll loop stopped');
            } else {
                console.debug('stop_streaming: no poll loop to stop');
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
