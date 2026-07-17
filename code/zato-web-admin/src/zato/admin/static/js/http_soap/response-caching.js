
// ////////////////////////////////////////////////////////////////////////////
// Response caching UI for REST and SOAP channels
// ////////////////////////////////////////////////////////////////////////////

(function($) {

    var stored_entity_id = '';
    var stored_url_base = '';
    var clear_confirm_instance = null;

    $.fn.zato.response_caching.config = {
        save_error_message: 'Could not save',
        clear_error_message: 'Could not clear the cache',
        clear_confirm_message: 'Are you sure?',
        clear_confirm_yes_label: 'Yes',
        clear_confirm_no_label: 'No',
        status_fade_delay_ms: 750,
        status_fade_duration_ms: 500,
        tooltip_ok_hide_ms: 750,
        tooltip_error_hide_ms: 3000,
        tooltip_destroy_ms: 300
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.response_caching.init = function(entity_id, url_base, config, transport) {
        stored_entity_id = entity_id;
        stored_url_base = url_base;

        $.fn.zato.response_caching.load_config(config, transport);
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.response_caching.load_config = function(config, transport) {

        document.getElementById('response-caching-is-enabled').checked = config.is_enabled;
        document.getElementById('response-caching-ttl').value = config.ttl;
        document.getElementById('response-caching-ttl-unit').value = config.ttl_unit;
        document.getElementById('response-caching-cache-on-second-request').checked = config.cache_on_second_request;
        document.getElementById('response-caching-is-shared-across-callers').checked = config.is_shared_across_callers;
        document.getElementById('response-caching-needs-etag').checked = config.needs_etag;
        document.getElementById('response-caching-max-body-size').value = config.max_body_size;
        document.getElementById('response-caching-coalesce-timeout').value = config.coalesce_timeout;

        document.getElementById('response-caching-vary-by-headers').value = config.vary_by_headers.join(', ');
        document.getElementById('response-caching-ignored-query-parameters').value = config.ignored_query_parameters.join(', ');

        // SOAP operations live in the POST body, so the body always joins the key on SOAP channels -
        // the checkbox is forced on and locked.
        var include_body_elem = document.getElementById('response-caching-include-body-in-key');

        if(transport === 'soap') {
            include_body_elem.checked = true;
            include_body_elem.disabled = true;
        }
        else {
            include_body_elem.checked = config.include_body_in_key;
        }
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.response_caching.split_list = function(value) {
        var out = [];
        var parts = value.split(',');

        for(var idx = 0; idx < parts.length; idx++) {
            var item = parts[idx].trim();
            if(item) {
                out.push(item);
            }
        }

        return out;
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.response_caching.get_config = function() {

        var config = {
            is_enabled: document.getElementById('response-caching-is-enabled').checked,
            ttl: parseInt(document.getElementById('response-caching-ttl').value, 10),
            ttl_unit: document.getElementById('response-caching-ttl-unit').value,
            cache_on_second_request: document.getElementById('response-caching-cache-on-second-request').checked,
            is_shared_across_callers: document.getElementById('response-caching-is-shared-across-callers').checked,
            include_body_in_key: document.getElementById('response-caching-include-body-in-key').checked,
            needs_etag: document.getElementById('response-caching-needs-etag').checked,
            max_body_size: parseInt(document.getElementById('response-caching-max-body-size').value, 10),
            coalesce_timeout: parseInt(document.getElementById('response-caching-coalesce-timeout').value, 10),
            vary_by_headers: $.fn.zato.response_caching.split_list(document.getElementById('response-caching-vary-by-headers').value),
            ignored_query_parameters: $.fn.zato.response_caching.split_list(
                document.getElementById('response-caching-ignored-query-parameters').value)
        };

        return config;
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.response_caching.save = function() {

        var config = $.fn.zato.response_caching.get_config();
        var status = $('#response-caching-status');
        var ui_config = $.fn.zato.response_caching.config;

        status.removeClass('show fade status-message-success status-message-error');

        $.ajax({
            url: stored_url_base + '/save/' + stored_entity_id + '/',
            type: 'POST',
            data: {config_json: JSON.stringify(config)},
            headers: {'X-CSRFToken': $.cookie('csrftoken')},
            success: function() {
                status.text('OK, saved').addClass('show status-message-success');
                setTimeout(function() {
                    status.addClass('fade');
                    setTimeout(function() {
                        status.removeClass('show fade status-message-success');
                    }, ui_config.status_fade_duration_ms);
                }, ui_config.status_fade_delay_ms);
            },
            error: function(jqXHR) {
                var msg = ui_config.save_error_message;
                try {
                    var response = JSON.parse(jqXHR.responseText);
                    if(response.message) {
                        msg = response.message;
                    }
                }
                catch(e) {
                    if(jqXHR.responseText) {
                        msg = jqXHR.responseText;
                    }
                }
                status.text(msg).addClass('show status-message-error');
            }
        });
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.response_caching.show_tooltip = function(anchor_elem, message, hide_ms) {
        var ui_config = $.fn.zato.response_caching.config;

        var _tooltip = tippy(anchor_elem, {
            content: message,
            allowHTML: false,
            theme: 'dark',
            trigger: 'manual',
            placement: 'top',
            arrow: true,
            interactive: false,
            inertia: true,
        });

        var instance = Array.isArray(_tooltip) ? _tooltip[0] : _tooltip;
        instance.show();
        setTimeout(function() {
            instance.hide();
            setTimeout(function() { instance.destroy(); }, ui_config.tooltip_destroy_ms);
        }, hide_ms);
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.response_caching.confirm_clear_cache = function(clear_link) {

        // Do not open a second confirmation while one is already visible
        if(clear_confirm_instance) {
            return;
        }

        var ui_config = $.fn.zato.response_caching.config;

        // Hides the confirmation, tippy invokes on_hidden for the cleanup
        function close_confirm() {
            clear_confirm_instance.hide();
        }

        // Confirming means closing the tooltip and actually clearing the cache
        function on_yes() {
            close_confirm();
            $.fn.zato.response_caching.clear_cache(clear_link);
        }

        // Enter anywhere on the page counts as pressing Yes
        function on_keydown(event) {
            if(event.key === 'Enter') {
                event.preventDefault();
                on_yes();
            }
        }

        // Runs after the tooltip is gone, no matter how it was dismissed,
        // e.g. also when it was hidden by a click elsewhere on the page.
        function on_hidden(instance) {
            document.removeEventListener('keydown', on_keydown);
            clear_confirm_instance = null;
            instance.destroy();
        }

        // The question shown above the buttons ..
        var question = document.createElement('div');
        question.className = 'response-caching-confirm-question';
        question.textContent = ui_config.clear_confirm_message;

        // .. the Yes button ..
        var yes_button = document.createElement('button');
        yes_button.type = 'button';
        yes_button.textContent = ui_config.clear_confirm_yes_label;
        yes_button.addEventListener('click', on_yes);

        // .. the No button ..
        var no_button = document.createElement('button');
        no_button.type = 'button';
        no_button.textContent = ui_config.clear_confirm_no_label;
        no_button.addEventListener('click', close_confirm);

        // .. the row that holds both buttons ..
        var button_row = document.createElement('div');
        button_row.className = 'response-caching-confirm-buttons';
        button_row.appendChild(yes_button);
        button_row.appendChild(no_button);

        // .. and the container for the whole tooltip body.
        var content = document.createElement('div');
        content.appendChild(question);
        content.appendChild(button_row);

        var _tooltip = tippy(clear_link, {
            content: content,
            allowHTML: true,
            theme: 'dark',
            trigger: 'manual',
            placement: 'top',
            arrow: true,
            interactive: true,
            inertia: true,
            onHidden: on_hidden,
        });

        clear_confirm_instance = Array.isArray(_tooltip) ? _tooltip[0] : _tooltip;
        clear_confirm_instance.show();

        // Listen for Enter only while the confirmation is on screen
        document.addEventListener('keydown', on_keydown);
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.response_caching.clear_cache = function(clear_link) {
        var ui_config = $.fn.zato.response_caching.config;

        $.ajax({
            url: stored_url_base + '/clear/' + stored_entity_id + '/',
            type: 'POST',
            data: {},
            headers: {'X-CSRFToken': $.cookie('csrftoken')},
            success: function() {
                $.fn.zato.response_caching.show_tooltip(clear_link, 'OK, cleared', ui_config.tooltip_ok_hide_ms);
            },
            error: function(jqXHR) {
                var msg = ui_config.clear_error_message;
                try {
                    var response = JSON.parse(jqXHR.responseText);
                    if(response.message) {
                        msg = response.message;
                    }
                }
                catch(e) {
                    if(jqXHR.responseText) {
                        msg = jqXHR.responseText;
                    }
                }
                $.fn.zato.response_caching.show_tooltip(clear_link, msg, ui_config.tooltip_error_hide_ms);
            }
        });
    };

    // ////////////////////////////////////////////////////////////////////////

})(jQuery);
