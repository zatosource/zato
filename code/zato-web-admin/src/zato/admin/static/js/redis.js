
// ////////////////////////////////////////////////////////////////////////////
// Redis connection UI
// ////////////////////////////////////////////////////////////////////////////

(function($) {

    var stored_url_base = '';

    $.fn.zato.redis.config = {
        save_ok_message: 'OK, saved',
        save_error_message: 'Could not save',
        test_error_message: 'Could not connect',
        test_spinner_label: 'Testing ..',
        test_spinner_delay_ms: 250,
        test_details_title: 'Test connection response',
        test_ok_hold_ms: 1200,
        status_fade_delay_ms: 750,
        status_fade_duration_ms: 500
    };

    // ////////////////////////////////////////////////////////////////////////

    // The per-field help texts behind the "How does it work?" badge,
    // keyed by the ids of the form fields.
    $.fn.zato.redis.field_descriptions = {
        'redis-host': 'The host the Redis server listens on, e.g. localhost.',
        'redis-port': 'The port the Redis server listens on. Default is 6379.',
        'redis-db': 'The number of the Redis logical database to use. Default is 0.',
        'redis-username': 'Username to authenticate with. Leave empty if the server does not require authentication.',
        'redis-password': 'Password matching the username above. Stored encrypted in secrets.conf. An empty field keeps the current password.',
        'redis-ssl': 'When on, all traffic to the server is encrypted with TLS. Required for the certificate options below to take effect.',
        'redis-ssl-ca-file': 'Path to a PEM file with CA certificates used to verify the server\'s certificate.',
        'redis-ssl-cert-file': 'Path to a PEM file with the client certificate, for mutual TLS.',
        'redis-ssl-key-file': 'Path to a PEM file with the private key of the client certificate above.',
        'redis-ssl-verify': 'When on, the server\'s certificate is verified against the CA file above. Turn it off only with test environments.'
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.redis.init = function(url_base, config) {
        stored_url_base = url_base;

        $.fn.zato.redis.load_config(config);

        // The SSL options follow the SSL/TLS toggle from now on
        $('#redis-ssl').on('change', $.fn.zato.redis.update_ssl_state);

        $.fn.zato.how_it_works.init({
            badgeId: 'redis-how-it-works',
            divId: '#redis',
            fieldSelector: '.redis-row',
            containerSelector: '#markup',
            placement: 'left',
            descriptions: $.fn.zato.redis.field_descriptions
        });
    };

    // ////////////////////////////////////////////////////////////////////////

    // Enables or disables the SSL-dependent rows to match the SSL/TLS toggle
    $.fn.zato.redis.update_ssl_state = function() {

        var is_ssl = document.getElementById('redis-ssl').checked;

        $('.redis-ssl-option').each(function() {
            var row = $(this);
            row.toggleClass('redis-row-disabled', !is_ssl);
            row.find('input').prop('disabled', !is_ssl);
        });
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.redis.load_config = function(config) {

        document.getElementById('redis-host').value = config.host;
        document.getElementById('redis-port').value = config.port;
        document.getElementById('redis-db').value = config.db;
        document.getElementById('redis-username').value = config.username;
        document.getElementById('redis-password').value = config.password;
        document.getElementById('redis-ssl').checked = config.ssl;
        document.getElementById('redis-ssl-ca-file').value = config.ssl_ca_file;
        document.getElementById('redis-ssl-cert-file').value = config.ssl_cert_file;
        document.getElementById('redis-ssl-key-file').value = config.ssl_key_file;
        document.getElementById('redis-ssl-verify').checked = config.ssl_verify;
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.redis.get_config = function() {

        var config = {
            host: document.getElementById('redis-host').value,
            port: document.getElementById('redis-port').value,
            db: document.getElementById('redis-db').value,
            username: document.getElementById('redis-username').value,
            password: document.getElementById('redis-password').value,
            ssl: document.getElementById('redis-ssl').checked,
            ssl_ca_file: document.getElementById('redis-ssl-ca-file').value,
            ssl_cert_file: document.getElementById('redis-ssl-cert-file').value,
            ssl_key_file: document.getElementById('redis-ssl-key-file').value,
            ssl_verify: document.getElementById('redis-ssl-verify').checked
        };

        return config;
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.redis.extract_error = function(jqXHR, default_message) {
        var msg = default_message;

        try {
            var response = JSON.parse(jqXHR.responseText);
            if(response.error) {
                msg = response.error;
            }
            else if(response.message) {
                msg = response.message;
            }
        }
        catch(e) {
            if(jqXHR.responseText) {
                msg = jqXHR.responseText;
            }
        }

        return msg;
    };

    // ////////////////////////////////////////////////////////////////////////

    // Shows a green message in the status slot and fades it out after hold_ms
    $.fn.zato.redis.show_status_success = function(message, hold_ms) {

        var status = $('#redis-status');
        var ui_config = $.fn.zato.redis.config;

        status.removeClass('show fade status-message-success status-message-error');
        status.text(message).addClass('show status-message-success');

        setTimeout(function() {
            status.addClass('fade');
            setTimeout(function() {
                status.removeClass('show fade status-message-success');
            }, ui_config.status_fade_duration_ms);
        }, hold_ms);
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.redis.save = function() {

        var values = $.fn.zato.redis.get_config();
        var status = $('#redis-status');
        var ui_config = $.fn.zato.redis.config;

        status.removeClass('show fade status-message-success status-message-error');

        $.ajax({
            url: stored_url_base + '/save',
            type: 'POST',
            data: JSON.stringify({values: values}),
            contentType: 'application/json',
            headers: {'X-CSRFToken': $.cookie('csrftoken')},
            success: function() {
                $.fn.zato.redis.show_status_success(ui_config.save_ok_message, ui_config.status_fade_delay_ms);
            },
            error: function(jqXHR) {
                var msg = $.fn.zato.redis.extract_error(jqXHR, ui_config.save_error_message);
                status.text(msg).addClass('show status-message-error');
            }
        });
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.redis.parse_test_response = function(jqXHR) {

        var ui_config = $.fn.zato.redis.config;

        // A request that never reached the server has no response text at all
        var body = jqXHR.responseText;
        if(body === undefined) {
            body = '';
        }

        var parsed = null;
        try {
            parsed = JSON.parse(body);
        }
        catch(e) {
            parsed = null;
        }

        // The test service always answers with JSON - success carries a message
        // with the response time, failure carries the Redis client's error,
        // shown in full in the tooltip and again in the copyable details modal.
        if(parsed) {
            if(parsed.success) {
                return {
                    is_success: true,
                    label: parsed.message,
                    details_title: '',
                    details_body: '',
                    details_lexer: '',
                    status_code: 0
                };
            }
            return {
                is_success: false,
                label: parsed.error,
                details_title: parsed.error,
                details_body: parsed.error,
                details_lexer: '',
                status_code: 0
            };
        }

        // A non-JSON body means the request never made it to the test service
        return {
            is_success: false,
            label: ui_config.test_error_message,
            details_title: ui_config.test_error_message,
            details_body: body,
            details_lexer: '',
            status_code: jqXHR.status
        };
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.redis.test = function(test_link) {

        var values = $.fn.zato.redis.get_config();
        var ui_config = $.fn.zato.redis.config;

        $.fn.zato.action_runner.run({
            link_elem: test_link,
            url: stored_url_base + '/test',
            data: JSON.stringify({values: values}),
            spinner_label: ui_config.test_spinner_label,
            show_delay_ms: ui_config.test_spinner_delay_ms,
            details_modal_title: ui_config.test_details_title,
            parse: $.fn.zato.redis.parse_test_response,

            // A successful test does not need the tippy at all - the outcome goes
            // into the green status message to the left of the link instead.
            on_success: function(instance, result) {
                instance.hide();
                instance.destroy();
                $.fn.zato.redis.show_status_success(result.label, ui_config.test_ok_hold_ms);
            }
        });
    };

    // ////////////////////////////////////////////////////////////////////////

})(jQuery);
