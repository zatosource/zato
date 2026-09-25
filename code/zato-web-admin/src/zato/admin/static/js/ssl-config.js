
// ////////////////////////////////////////////////////////////////////////////
// SSL config - Let's Encrypt
// ////////////////////////////////////////////////////////////////////////////

(function($) {

    $.fn.zato.ssl_config.config = {
        container_selector: '#ssl-config',
        refresh_url: '/zato/ssl-config/refresh/',
        lets_encrypt_url: '/zato/ssl-config/lets-encrypt/',
        check_port_url: '/zato/ssl-config/check-port/',

        // The field of each refresh entry the time-ago cells read their timestamps from
        refresh_time_field: 'time_utc',

        none_label: '---',
        none_class: 'form_hint',
        yes_label: 'Yes',
        no_label: 'No',
        not_checked_label: 'Not checked',
        ok_label: 'OK',
        failed_label: 'Failed',
        names_separator: ', ',

        // What the process holding the lock is doing, keyed by the name it writes into the lock file
        running_labels: {
            'certificate': 'Obtaining a certificate ..',
            'port': 'Checking port 443 ..'
        },

        enabled_message: 'OK, enabled',
        disabled_message: 'OK, disabled',
        check_port_message: 'OK, checking',
        save_error_message: 'Could not save',
        check_port_error_message: 'Could not check the port',
        status_fade_delay_ms: 750,
        status_fade_duration_ms: 500
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.ssl_config.init = function(details) {
        var config = $.fn.zato.ssl_config.config;
        var time_ago = $.fn.zato.time_ago;

        time_ago.config.refresh_url = config.refresh_url;
        time_ago.config.refresh_time_field = config.refresh_time_field;
        time_ago.config.never_label = config.none_label;
        time_ago.config.never_class = config.none_class;

        // There are no table rows here to highlight while a tooltip is open.
        time_ago.config.highlight_column = '';

        // The rows without timestamps are refreshed from the same response as the time-ago cells.
        time_ago.config.on_refresh = function(data) {
            $.fn.zato.ssl_config.apply_details(data.details);
        };

        $.fn.zato.ssl_config.apply_details(details);
        $.fn.zato.ssl_config.set_times(details);

        time_ago.init(config.container_selector);
        time_ago.start_auto_refresh(config.container_selector, config.refresh_url);
    };

    // ////////////////////////////////////////////////////////////////////////

    // An error from the ACME client runs over many lines and the last one says what went wrong.
    $.fn.zato.ssl_config.last_line = function(text) {
        var lines = text.trim().split('\n');
        var out = lines[lines.length - 1];
        return out;
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.ssl_config.set_text = function(selector, text, is_none) {
        var config = $.fn.zato.ssl_config.config;
        var elem = $(selector);

        elem.text(text);
        elem.toggleClass(config.none_class, is_none);
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.ssl_config.set_result = function(selector, is_ok, ok_label, error_label) {
        var config = $.fn.zato.ssl_config.config;
        var elem = $(selector);

        elem.removeClass('ssl-config-value-ok ssl-config-value-error ' + config.none_class);

        if(is_ok === null) {
            elem.text(config.not_checked_label).addClass(config.none_class);
        }
        else if(is_ok) {
            elem.text(ok_label).addClass('ssl-config-value-ok');
        }
        else {
            elem.text(error_label).addClass('ssl-config-value-error');
        }
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.ssl_config.set_error = function(selector, error) {
        var elem = $(selector);

        if(error) {
            elem.text($.fn.zato.ssl_config.last_line(error)).attr('title', error);
        }
        else {
            elem.text('').removeAttr('title');
        }
    };

    // ////////////////////////////////////////////////////////////////////////

    // Fills in everything except for the time-ago cells, which the time-ago refresh takes care of.
    $.fn.zato.ssl_config.apply_details = function(details) {
        var config = $.fn.zato.ssl_config.config;
        var status = details.status;
        var certificate = details.certificate;
        var running_operation = details.running_operation;

        document.getElementById('ssl-config-is-enabled').checked = details.is_enabled;

        // The hint next to the slider says what is going on right now.
        var hint;
        if(running_operation) {
            hint = config.running_labels[running_operation];
        }
        else {
            hint = '';
        }
        $('#ssl-config-is-enabled-hint').text(hint);

        // Only one check can run at a time, so a new one cannot be started while another is running.
        $('#ssl-config-check-port').toggleClass('is-disabled', running_operation !== '');

        $.fn.zato.ssl_config.set_result('#ssl-config-port-ready', status.is_port_ready, config.yes_label, config.no_label);
        $.fn.zato.ssl_config.set_error('#ssl-config-port-error', status.port_check_error);

        $.fn.zato.ssl_config.set_result('#ssl-config-last-check-result', status.is_last_check_ok, config.ok_label, config.failed_label);
        $.fn.zato.ssl_config.set_error('#ssl-config-last-check-error', status.last_check_error);

        if(certificate === null) {
            $.fn.zato.ssl_config.set_text('#ssl-config-names', config.none_label, true);
            $.fn.zato.ssl_config.set_text('#ssl-config-issuer', config.none_label, true);
        }
        else {
            $.fn.zato.ssl_config.set_text('#ssl-config-names', certificate.names.join(config.names_separator), false);
            $.fn.zato.ssl_config.set_text('#ssl-config-issuer', certificate.issuer, false);
        }
    };

    // ////////////////////////////////////////////////////////////////////////

    // Updates the time-ago cells at once, rather than waiting for the next refresh.
    $.fn.zato.ssl_config.set_times = function(details) {
        var time_ago = $.fn.zato.time_ago;
        var certificate = details.certificate;
        var not_after_utc;

        if(certificate === null) {
            not_after_utc = null;
        }
        else {
            not_after_utc = certificate.not_after_utc;
        }

        time_ago.update_cell($('#ssl-config-port-check'), details.status.port_check_utc, null);
        time_ago.update_cell($('#ssl-config-last-check'), details.status.last_check_utc, null);
        time_ago.update_cell($('#ssl-config-expires'), not_after_utc, null);
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.ssl_config.show_status = function(message, is_ok) {
        var config = $.fn.zato.ssl_config.config;
        var status = $('#ssl-config-status');

        status.removeClass('show fade status-message-success status-message-error');

        if(!is_ok) {
            status.text(message).addClass('show status-message-error');
            return;
        }

        status.text(message).addClass('show status-message-success');
        setTimeout(function() {
            status.addClass('fade');
            setTimeout(function() {
                status.removeClass('show fade status-message-success');
            }, config.status_fade_duration_ms);
        }, config.status_fade_delay_ms);
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.ssl_config.get_error_message = function(jqXHR, default_message) {
        var out = default_message;

        try {
            var response = JSON.parse(jqXHR.responseText);
            if(response.message) {
                out = response.message;
            }
        }
        catch(e) {
            if(jqXHR.responseText) {
                out = jqXHR.responseText;
            }
        }

        return out;
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.ssl_config.post = function(url, data, ok_message, error_message) {

        $.ajax({
            url: url,
            type: 'POST',
            data: data,
            headers: {'X-CSRFToken': $.cookie('csrftoken')},
            success: function(response) {
                $.fn.zato.ssl_config.apply_details(response.details);
                $.fn.zato.ssl_config.set_times(response.details);
                $.fn.zato.ssl_config.show_status(ok_message, true);
            },
            error: function(jqXHR) {
                var message = $.fn.zato.ssl_config.get_error_message(jqXHR, error_message);
                $.fn.zato.ssl_config.show_status(message, false);
            }
        });
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.ssl_config.set_lets_encrypt = function(is_enabled) {
        var config = $.fn.zato.ssl_config.config;

        var ok_message;
        if(is_enabled) {
            ok_message = config.enabled_message;
        }
        else {
            ok_message = config.disabled_message;
        }

        $.fn.zato.ssl_config.post(config.lets_encrypt_url, {'is_enabled': is_enabled}, ok_message, config.save_error_message);
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.ssl_config.check_port = function() {
        var config = $.fn.zato.ssl_config.config;
        $.fn.zato.ssl_config.post(config.check_port_url, {}, config.check_port_message, config.check_port_error_message);
    };

    // ////////////////////////////////////////////////////////////////////////

})(jQuery);
