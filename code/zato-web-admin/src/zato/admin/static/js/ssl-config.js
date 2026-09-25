
// ////////////////////////////////////////////////////////////////////////////
// SSL config - Let's Encrypt
// ////////////////////////////////////////////////////////////////////////////

(function($) {

    $.fn.zato.ssl_config.config = {
        container_selector: '#ssl-config',
        refresh_url: '/zato/ssl-config/refresh/',
        lets_encrypt_url: '/zato/ssl-config/lets-encrypt/',
        check_port_url: '/zato/ssl-config/check-port/',
        public_endpoint_url: '/zato/ssl-config/public-endpoint/',

        // How long the spinners next to the public IP and DNS name turn before the one request that fills them in is made
        public_endpoint_spinner_ms: 600,
        public_endpoint_error_message: 'Could not check',

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

        // How often the page asks how far enabling Let's Encrypt got while it runs
        progress_poll_ms: 1000,

        // How long each message next to the slider takes to fade in or out, and how long a final one stays before it fades out
        message_fade_ms: 600,
        message_hold_ms: 2500,

        // How old a completion may be for the page to still announce it when it loads
        announce_max_age_ms: 60000,

        // What each step reads as while it runs ..
        step_labels: {
            'port': 'Checking port 443 ..',
            'connect': 'Connecting to Let\'s Encrypt ..',
            'request': 'Requesting a certificate ..',
            'install': 'Installing ..'
        },

        // .. and when it failed
        step_error_labels: {
            'port': 'Port 443 is not reachable',
            'connect': 'Could not connect to Let\'s Encrypt',
            'request': 'Could not get a certificate',
            'install': 'Could not install the certificate'
        },

        // The step whose completion means that the whole of enabling Let's Encrypt is over
        final_step: 'install',

        done_message: 'Certificate installed',
        disabled_message: 'Disabled',
        save_error_message: 'Could not save',
        check_port_error_message: 'Could not check the port'
    };

    // The message next to the slider that is shown now, so that the same one is never faded out and in again.
    $.fn.zato.ssl_config.message_key = '';

    // The timers behind the message - one swaps the text in once the previous one faded out, the other fades a final message out.
    $.fn.zato.ssl_config.swap_timer = null;
    $.fn.zato.ssl_config.hide_timer = null;

    // The completion that was already announced, so that a page refresh does not announce it again.
    $.fn.zato.ssl_config.announced_utc = '';

    // Whether the slider was just moved on, so that the page keeps asking until the first step shows up.
    $.fn.zato.ssl_config.is_expecting = false;

    $.fn.zato.ssl_config.progress_timer = null;

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

        $.fn.zato.ssl_config.load_public_endpoint();
    };

    // ////////////////////////////////////////////////////////////////////////
    // The message next to the slider
    // ////////////////////////////////////////////////////////////////////////

    // Replaces the message next to the slider - the one shown now fades out first and the new one fades in after it.
    $.fn.zato.ssl_config.show_message = function(text, has_spinner, is_error, title) {
        var config = $.fn.zato.ssl_config.config;
        var elem = $('#ssl-config-message');
        var key = text + '|' + has_spinner + '|' + is_error;

        if(key === $.fn.zato.ssl_config.message_key) {
            return;
        }

        clearTimeout($.fn.zato.ssl_config.swap_timer);
        clearTimeout($.fn.zato.ssl_config.hide_timer);

        var swap = function() {
            $('#ssl-config-message-text').text(text);
            elem.toggleClass('has-spinner', has_spinner);
            elem.toggleClass('is-error', is_error);
            elem.attr('title', title);
            elem.addClass('is-visible');
        };

        // Nothing is shown yet, so there is nothing to wait for ..
        if($.fn.zato.ssl_config.message_key === '') {
            $.fn.zato.ssl_config.message_key = key;
            swap();
            return;
        }

        // .. otherwise the new text goes in only once the old one is gone.
        $.fn.zato.ssl_config.message_key = key;
        elem.removeClass('is-visible');
        $.fn.zato.ssl_config.swap_timer = setTimeout(swap, config.message_fade_ms);
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.ssl_config.hide_message = function() {
        clearTimeout($.fn.zato.ssl_config.swap_timer);
        clearTimeout($.fn.zato.ssl_config.hide_timer);
        $.fn.zato.ssl_config.message_key = '';
        $('#ssl-config-message').removeClass('is-visible');
    };

    // ////////////////////////////////////////////////////////////////////////

    // Shows a final message, one that stays for a while and then fades out on its own.
    $.fn.zato.ssl_config.show_message_briefly = function(text, is_error) {
        var config = $.fn.zato.ssl_config.config;

        $.fn.zato.ssl_config.show_message(text, false, is_error, '');

        // The hold starts once the message is fully in, which may be after the previous one faded out.
        $.fn.zato.ssl_config.hide_timer = setTimeout(function() {
            $.fn.zato.ssl_config.hide_message();
        }, config.message_fade_ms * 2 + config.message_hold_ms);
    };

    // ////////////////////////////////////////////////////////////////////////

    // Turns what the server recorded about the current step into the message next to the slider.
    $.fn.zato.ssl_config.apply_progress = function(progress) {
        var config = $.fn.zato.ssl_config.config;

        if(progress === null) {
            return;
        }

        if(progress.state === 'running') {
            $.fn.zato.ssl_config.show_message(config.step_labels[progress.step], true, false, '');
            return;
        }

        if(progress.state === 'error') {
            $.fn.zato.ssl_config.show_message(config.step_error_labels[progress.step], false, true, progress.error);
            return;
        }

        // A step that finished is announced only if it was the last one, only once, and only if it finished a moment ago,
        // so that a page opened long after the fact does not announce it again.
        if(progress.step !== config.final_step) {
            $.fn.zato.ssl_config.hide_message();
            return;
        }

        if(progress.updated_utc === $.fn.zato.ssl_config.announced_utc) {
            return;
        }

        $.fn.zato.ssl_config.announced_utc = progress.updated_utc;

        var age_ms = Date.now() - Date.parse(progress.updated_utc);
        if(age_ms < config.announce_max_age_ms) {
            $.fn.zato.ssl_config.show_message_briefly(config.done_message, false);
        }
    };

    // ////////////////////////////////////////////////////////////////////////

    // Asks how far enabling Let's Encrypt got, once a second, for as long as a step runs.
    $.fn.zato.ssl_config.poll_progress = function() {
        var config = $.fn.zato.ssl_config.config;

        clearTimeout($.fn.zato.ssl_config.progress_timer);

        $.ajax({
            url: config.refresh_url,
            type: 'POST',
            data: {},
            headers: {'X-CSRFToken': $.cookie('csrftoken')},
            success: function(response) {
                $.fn.zato.ssl_config.apply_details(response.details);
                $.fn.zato.ssl_config.set_times(response.details);
            }
        });
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.ssl_config.is_running = function(progress) {
        var out = progress !== null && progress.state === 'running';
        return out;
    };

    // ////////////////////////////////////////////////////////////////////////
    // The public IP and DNS name
    // ////////////////////////////////////////////////////////////////////////

    // Fills in one of the cells that the public endpoint request answers, fading it in once its spinner is gone.
    $.fn.zato.ssl_config.set_public_value = function(selector, value, is_error) {
        var config = $.fn.zato.ssl_config.config;
        var elem = $(selector);

        $(selector + '-spinner').remove();

        if(value === null) {
            $.fn.zato.ssl_config.set_text(selector, config.none_label, true);
        }
        else {
            $.fn.zato.ssl_config.set_text(selector, value, false);
        }

        elem.toggleClass('ssl-config-value-error', is_error);
        elem.addClass('is-visible');
    };

    // ////////////////////////////////////////////////////////////////////////

    // The public IP address and its DNS name are checked from the server once, after the page loaded,
    // because finding them out means reaching out to the internet, which must not hold the page up.
    $.fn.zato.ssl_config.load_public_endpoint = function() {
        var config = $.fn.zato.ssl_config.config;

        $('.ssl-config-spinner').addClass('is-visible');

        setTimeout(function() {
            $.ajax({
                url: config.public_endpoint_url,
                type: 'GET',
                success: function(response) {
                    $.fn.zato.ssl_config.set_public_value('#ssl-config-public-ip', response.public_ip, false);
                    $.fn.zato.ssl_config.set_public_value('#ssl-config-public-dns-name', response.public_dns_name, false);
                },
                error: function(jqXHR) {
                    var message = $.fn.zato.ssl_config.get_error_message(jqXHR, config.public_endpoint_error_message);
                    $.fn.zato.ssl_config.set_public_value('#ssl-config-public-ip', message, true);
                    $.fn.zato.ssl_config.set_public_value('#ssl-config-public-dns-name', message, true);
                }
            });
        }, config.public_endpoint_spinner_ms);
    };

    // ////////////////////////////////////////////////////////////////////////
    // The cells
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
        var progress = details.progress;
        var is_running = $.fn.zato.ssl_config.is_running(progress);

        // The slider cannot be moved while a step runs, nor can another port check be started.
        var is_enabled_elem = document.getElementById('ssl-config-is-enabled');
        is_enabled_elem.checked = details.is_enabled;
        is_enabled_elem.disabled = is_running;
        $('#ssl-config-check-port').toggleClass('is-disabled', is_running);

        $.fn.zato.ssl_config.apply_progress(progress);

        // The first step has shown up, so there is nothing to wait for any longer ..
        if(progress !== null) {
            $.fn.zato.ssl_config.is_expecting = false;
        }

        // .. and the page keeps asking for as long as a step runs, so that each one shows up as it starts.
        if(is_running || $.fn.zato.ssl_config.is_expecting) {
            clearTimeout($.fn.zato.ssl_config.progress_timer);
            $.fn.zato.ssl_config.progress_timer = setTimeout($.fn.zato.ssl_config.poll_progress, config.progress_poll_ms);
        }

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
    // The actions
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

    $.fn.zato.ssl_config.post = function(url, data, error_message, on_success) {

        $.ajax({
            url: url,
            type: 'POST',
            data: data,
            headers: {'X-CSRFToken': $.cookie('csrftoken')},
            success: function(response) {
                $.fn.zato.ssl_config.apply_details(response.details);
                $.fn.zato.ssl_config.set_times(response.details);
                on_success(response.details);
            },
            error: function(jqXHR) {
                var message = $.fn.zato.ssl_config.get_error_message(jqXHR, error_message);
                $.fn.zato.ssl_config.show_message(message, false, true, message);
            }
        });
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.ssl_config.set_lets_encrypt = function(is_enabled) {
        var config = $.fn.zato.ssl_config.config;

        // Whatever was shown before, e.g. the error of the previous try, is gone the moment the slider moves ..
        $.fn.zato.ssl_config.hide_message();

        // .. and enabling is followed step by step, from the moment the first step shows up.
        $.fn.zato.ssl_config.is_expecting = is_enabled;

        $.fn.zato.ssl_config.post(config.lets_encrypt_url, {'is_enabled': is_enabled}, config.save_error_message, function(details) {
            if(!is_enabled) {
                $.fn.zato.ssl_config.show_message_briefly(config.disabled_message, false);
            }
        });
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.ssl_config.check_port = function() {
        var config = $.fn.zato.ssl_config.config;

        $.fn.zato.ssl_config.is_expecting = true;
        $.fn.zato.ssl_config.post(config.check_port_url, {}, config.check_port_error_message, function(details) {});
    };

    // ////////////////////////////////////////////////////////////////////////

})(jQuery);
