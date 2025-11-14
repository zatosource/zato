
(function($) {

    $.fn.zato.log_streaming = new Class({

        toString: function() {
            var s = '<LogStreaming>';
            return s;
        },

        get_status: function() {
            var self = this;

            $.ajax({
                type: 'GET',
                url: '/zato/log-streaming/status',
                success: function(data) {
                    var streaming_enabled = data.streaming_enabled;
                    var status_text = streaming_enabled ? 'enabled' : 'disabled';
                    alert('Log streaming is currently ' + status_text);
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
                    alert('Log streaming has been ' + status_text);
                },
                error: function(xhr, status, error) {
                    alert('Error toggling log streaming: ' + error);
                }
            });
        }

    });

    $.fn.zato.log_streaming = new $.fn.zato.log_streaming();

})(jQuery);
