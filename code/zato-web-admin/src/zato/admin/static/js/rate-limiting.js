
// ////////////////////////////////////////////////////////////////////////////
// Rate limiting UI for CIDR-based rules
// ////////////////////////////////////////////////////////////////////////////

(function($) {

    // Suggested CIDR ranges - IPv4 first, then IPv6
    var suggestions = [
        {cidr: '0.0.0.0/0',      label: 'all IPv4'},
        {cidr: '10.0.0.0/8',     label: 'private 10.x'},
        {cidr: '172.16.0.0/12',  label: 'private 172.16.x'},
        {cidr: '192.168.0.0/16', label: 'private 192.168.x'},
        {cidr: '127.0.0.0/8',    label: 'loopback'},
        {cidr: '::/0',           label: 'all IPv6'},
        {cidr: '::1/128',        label: 'loopback'},
        {cidr: 'fe80::/10',      label: 'link-local'}
    ];

    var window_units = ['minute', 'hour', 'day', 'month'];

    var rule_counter = 0;

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.rate_limiting.init = function(container_id, mode) {
        var container = document.getElementById(container_id);
        container.innerHTML = '';
        rule_counter = 0;
        $.fn.zato.rate_limiting.setup_drag(container_id);
        $.fn.zato.rate_limiting.close_suggestions_on_outside_click();
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.rate_limiting.add_rule = function(container_id) {
        var container = document.getElementById(container_id);

        rule_counter += 1;
        var rule_index = container.children.length;

        var rule_elem = document.createElement('div');
        rule_elem.className = 'rate-limiting-rule';
        rule_elem.setAttribute('data-rule-index', rule_index);

        // Drag handle
        var handle = document.createElement('div');
        handle.className = 'rate-limiting-drag-handle';
        for(var row_idx = 0; row_idx < 3; row_idx++) {
            var dot_row = document.createElement('div');
            dot_row.className = 'rate-limiting-drag-handle-dot-row';
            for(var dot_idx = 0; dot_idx < 2; dot_idx++) {
                var dot = document.createElement('div');
                dot.className = 'rate-limiting-drag-handle-dot';
                dot_row.appendChild(dot);
            }
            handle.appendChild(dot_row);
        }
        rule_elem.appendChild(handle);

        // Rule number
        var number = document.createElement('span');
        number.className = 'rate-limiting-rule-number';
        number.textContent = '#' + (rule_index + 1);
        rule_elem.appendChild(number);

        // Pills area
        var pills = document.createElement('div');
        pills.className = 'rate-limiting-pills';

        // Add pill button
        var add_pill_button = document.createElement('span');
        add_pill_button.className = 'rate-limiting-pill-add-button';
        add_pill_button.textContent = '+';
        add_pill_button.onclick = function() {
            $.fn.zato.rate_limiting.show_input(pills, add_pill_button);
        };
        pills.appendChild(add_pill_button);

        rule_elem.appendChild(pills);

        // Time range config group
        var time_group = document.createElement('div');
        time_group.className = 'rate-limiting-config-group';

        var time_toggle = document.createElement('span');
        time_toggle.className = 'rate-limiting-time-toggle';
        time_toggle.textContent = '\u23f0';
        time_toggle.title = 'Toggle time range';
        time_toggle.onclick = function() {
            $.fn.zato.rate_limiting.toggle_time_range(rule_elem);
        };
        time_group.appendChild(time_toggle);

        var time_fields = document.createElement('div');
        time_fields.className = 'rate-limiting-time-fields';

        var time_from_input = document.createElement('input');
        time_from_input.type = 'time';
        time_from_input.className = 'rate-limiting-config-input';
        time_from_input.setAttribute('data-field', 'time_from');
        time_fields.appendChild(time_from_input);

        var time_dash = document.createElement('span');
        time_dash.className = 'rate-limiting-time-dash';
        time_dash.textContent = '\u2013';
        time_fields.appendChild(time_dash);

        var time_to_input = document.createElement('input');
        time_to_input.type = 'time';
        time_to_input.className = 'rate-limiting-config-input';
        time_to_input.setAttribute('data-field', 'time_to');
        time_fields.appendChild(time_to_input);

        time_group.appendChild(time_fields);
        rule_elem.appendChild(time_group);

        // Token bucket config group
        var tb_group = document.createElement('div');
        tb_group.className = 'rate-limiting-config-group';

        var rate_label = document.createElement('span');
        rate_label.className = 'rate-limiting-config-label';
        rate_label.textContent = 'Rate:';
        tb_group.appendChild(rate_label);

        var rate_input = document.createElement('input');
        rate_input.type = 'text';
        rate_input.className = 'rate-limiting-config-input';
        rate_input.setAttribute('data-field', 'rate');
        rate_input.placeholder = '10';
        tb_group.appendChild(rate_input);

        var rate_unit = document.createElement('span');
        rate_unit.className = 'rate-limiting-config-unit';
        rate_unit.textContent = '/s';
        tb_group.appendChild(rate_unit);

        var burst_label = document.createElement('span');
        burst_label.className = 'rate-limiting-config-label';
        burst_label.textContent = 'Burst:';
        tb_group.appendChild(burst_label);

        var burst_input = document.createElement('input');
        burst_input.type = 'text';
        burst_input.className = 'rate-limiting-config-input';
        burst_input.setAttribute('data-field', 'burst');
        burst_input.placeholder = '20';
        tb_group.appendChild(burst_input);

        var burst_unit = document.createElement('span');
        burst_unit.className = 'rate-limiting-config-unit';
        burst_unit.textContent = '/s';
        tb_group.appendChild(burst_unit);

        rule_elem.appendChild(tb_group);

        // Fixed window config group
        var fw_group = document.createElement('div');
        fw_group.className = 'rate-limiting-config-group';

        var limit_label = document.createElement('span');
        limit_label.className = 'rate-limiting-config-label';
        limit_label.textContent = 'Limit:';
        fw_group.appendChild(limit_label);

        var limit_input = document.createElement('input');
        limit_input.type = 'text';
        limit_input.className = 'rate-limiting-config-input';
        limit_input.setAttribute('data-field', 'limit');
        limit_input.placeholder = '100';
        fw_group.appendChild(limit_input);

        var slash_label = document.createElement('span');
        slash_label.className = 'rate-limiting-config-unit';
        slash_label.textContent = '/';
        fw_group.appendChild(slash_label);

        var unit_select = document.createElement('select');
        unit_select.className = 'rate-limiting-config-select';
        unit_select.setAttribute('data-field', 'window_unit');
        for(var unit_idx = 0; unit_idx < window_units.length; unit_idx++) {
            var opt = document.createElement('option');
            opt.value = window_units[unit_idx];
            opt.textContent = window_units[unit_idx];
            unit_select.appendChild(opt);
        }
        fw_group.appendChild(unit_select);

        rule_elem.appendChild(fw_group);

        // Remove button
        var remove_button = document.createElement('a');
        remove_button.href = 'javascript:void(0)';
        remove_button.textContent = 'Delete rule';
        remove_button.onclick = function() {
            $.fn.zato.rate_limiting.remove_rule(container_id, rule_elem);
        };
        rule_elem.appendChild(remove_button);

        container.appendChild(rule_elem);
        $.fn.zato.rate_limiting.renumber(container_id);
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.rate_limiting.remove_rule = function(container_id, rule_elem) {
        rule_elem.parentNode.removeChild(rule_elem);
        $.fn.zato.rate_limiting.renumber(container_id);
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.rate_limiting.toggle_time_range = function(rule_elem) {

        var toggle_button = rule_elem.querySelector('.rate-limiting-time-toggle');
        var time_fields = rule_elem.querySelector('.rate-limiting-time-fields');
        var is_active = toggle_button.classList.contains('rate-limiting-time-active');

        if(is_active) {

            // Hide the fields and clear values ..
            toggle_button.classList.remove('rate-limiting-time-active');
            time_fields.classList.remove('rate-limiting-time-visible');

            var time_from = rule_elem.querySelector('[data-field="time_from"]');
            var time_to = rule_elem.querySelector('[data-field="time_to"]');

            time_from.value = '';
            time_to.value = '';
        }
        else {

            // .. show the fields.
            toggle_button.classList.add('rate-limiting-time-active');
            time_fields.classList.add('rate-limiting-time-visible');
        }
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.rate_limiting.renumber = function(container_id) {
        var container = document.getElementById(container_id);
        var rules = container.querySelectorAll('.rate-limiting-rule');
        for(var rule_idx = 0; rule_idx < rules.length; rule_idx++) {
            rules[rule_idx].setAttribute('data-rule-index', rule_idx);
            var number = rules[rule_idx].querySelector('.rate-limiting-rule-number');
            if(number) {
                number.textContent = '#' + (rule_idx + 1);
            }
        }
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.rate_limiting.add_pill = function(rule_elem, cidr_text) {
        cidr_text = cidr_text.trim();
        if(!cidr_text) {
            return;
        }

        var pills = rule_elem.querySelector('.rate-limiting-pills');
        var add_button = pills.querySelector('.rate-limiting-pill-add-button');

        var pill = document.createElement('span');
        pill.className = 'rate-limiting-pill';

        var text_node = document.createElement('span');
        text_node.textContent = cidr_text;
        pill.appendChild(text_node);

        var remove_x = document.createElement('span');
        remove_x.className = 'rate-limiting-pill-remove';
        remove_x.textContent = '\u00d7';
        remove_x.onclick = function() {
            $.fn.zato.rate_limiting.remove_pill(pill);
        };
        pill.appendChild(remove_x);

        pills.insertBefore(pill, add_button);
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.rate_limiting.remove_pill = function(pill_elem) {
        pill_elem.parentNode.removeChild(pill_elem);
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.rate_limiting.show_input = function(pills_container, add_button) {

        // If there's already an input visible, focus it instead of adding another
        var existing = pills_container.querySelector('.rate-limiting-pill-input');
        if(existing) {
            existing.focus();
            return;
        }

        var input = document.createElement('input');
        input.type = 'text';
        input.className = 'rate-limiting-pill-input';
        input.placeholder = 'e.g. 10.0.0.0/8';

        input.onkeydown = function(e) {
            if(e.key === 'Enter') {
                e.preventDefault();
                var value = input.value.trim();
                if(value) {
                    var rule_elem = pills_container.closest('.rate-limiting-rule');
                    $.fn.zato.rate_limiting.add_pill(rule_elem, value);
                }
                input.value = '';
                $.fn.zato.rate_limiting.hide_suggestions();
            }
            if(e.key === 'Escape') {
                $.fn.zato.rate_limiting.hide_suggestions();
                input.parentNode.removeChild(input);
            }
        };

        input.onfocus = function() {
            $.fn.zato.rate_limiting.show_suggestions(input);
        };

        input.oninput = function() {
            $.fn.zato.rate_limiting.show_suggestions(input);
        };

        pills_container.insertBefore(input, add_button);
        input.focus();
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.rate_limiting.get_existing_cidrs = function(rule_elem) {
        var pill_elems = rule_elem.querySelectorAll('.rate-limiting-pill');
        var existing = {};

        for(var pill_idx = 0; pill_idx < pill_elems.length; pill_idx++) {
            var text_span = pill_elems[pill_idx].querySelector('span:first-child');
            existing[text_span.textContent] = true;
        }

        return existing;
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.rate_limiting.show_suggestions = function(input_elem) {
        $.fn.zato.rate_limiting.hide_suggestions();

        var filter = input_elem.value.trim().toLowerCase();
        var rule_elem = input_elem.closest('.rate-limiting-rule');
        var existing = $.fn.zato.rate_limiting.get_existing_cidrs(rule_elem);

        var dropdown = document.createElement('div');
        dropdown.className = 'rate-limiting-suggestions';
        dropdown.id = 'rate-limiting-suggestions-active';

        var ipv4_header = document.createElement('div');
        ipv4_header.className = 'rate-limiting-suggestion-header';
        ipv4_header.textContent = 'IPv4';
        dropdown.appendChild(ipv4_header);

        var has_ipv4 = false;
        var ipv6_items = [];

        for(var suggestion_idx = 0; suggestion_idx < suggestions.length; suggestion_idx++) {
            var suggestion = suggestions[suggestion_idx];

            if(existing[suggestion.cidr]) {
                continue;
            }

            if(filter && suggestion.cidr.toLowerCase().indexOf(filter) === -1 && suggestion.label.toLowerCase().indexOf(filter) === -1) {
                continue;
            }

            var is_ipv6 = suggestion.cidr.indexOf(':') !== -1;

            if(is_ipv6) {
                ipv6_items.push(suggestion);
                continue;
            }

            has_ipv4 = true;
            dropdown.appendChild($.fn.zato.rate_limiting.make_suggestion_item(suggestion, input_elem));
        }

        if(!has_ipv4) {
            dropdown.removeChild(ipv4_header);
        }

        if(ipv6_items.length > 0) {
            if(has_ipv4) {
                var sep = document.createElement('div');
                sep.className = 'rate-limiting-suggestion-separator';
                dropdown.appendChild(sep);
            }

            var ipv6_header = document.createElement('div');
            ipv6_header.className = 'rate-limiting-suggestion-header';
            ipv6_header.textContent = 'IPv6';
            dropdown.appendChild(ipv6_header);

            for(var ipv6_idx = 0; ipv6_idx < ipv6_items.length; ipv6_idx++) {
                dropdown.appendChild($.fn.zato.rate_limiting.make_suggestion_item(ipv6_items[ipv6_idx], input_elem));
            }
        }

        if(!has_ipv4 && ipv6_items.length === 0) {
            return;
        }

        var rect = input_elem.getBoundingClientRect();
        dropdown.style.position = 'fixed';
        dropdown.style.top = (rect.bottom + 2) + 'px';
        dropdown.style.left = rect.left + 'px';

        document.body.appendChild(dropdown);
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.rate_limiting.make_suggestion_item = function(suggestion, input_elem) {
        var item = document.createElement('div');
        item.className = 'rate-limiting-suggestion-item';

        var cidr_span = document.createElement('span');
        cidr_span.className = 'rate-limiting-suggestion-cidr';
        cidr_span.textContent = suggestion.cidr;
        item.appendChild(cidr_span);

        var label_span = document.createElement('span');
        label_span.className = 'rate-limiting-suggestion-label';
        label_span.textContent = suggestion.label;
        item.appendChild(label_span);

        item.onclick = function() {
            var rule_elem = input_elem.closest('.rate-limiting-rule');
            $.fn.zato.rate_limiting.add_pill(rule_elem, suggestion.cidr);
            input_elem.value = '';
            $.fn.zato.rate_limiting.hide_suggestions();
            input_elem.focus();
        };

        return item;
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.rate_limiting.hide_suggestions = function() {
        var existing = document.getElementById('rate-limiting-suggestions-active');
        if(existing) {
            existing.parentNode.removeChild(existing);
        }
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.rate_limiting.close_suggestions_on_outside_click = function() {
        $(document).on('mousedown.rate_limiting', function(e) {
            var target = $(e.target);
            if(!target.closest('.rate-limiting-suggestions').length && !target.hasClass('rate-limiting-pill-input')) {
                $.fn.zato.rate_limiting.hide_suggestions();
            }
        });
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.rate_limiting.setup_drag = function(container_id) {
        var container = document.getElementById(container_id);
        if(!container) {
            return;
        }

        if(typeof Sortable === 'undefined') {
            return;
        }

        Sortable.create(container, {
            handle: '.rate-limiting-drag-handle',
            animation: 150,
            ghostClass: 'rate-limiting-dragging',
            onEnd: function() {
                $.fn.zato.rate_limiting.renumber(container_id);
            }
        });
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.rate_limiting.get_rules = function(container_id) {
        var container = document.getElementById(container_id);
        var rule_elems = container.querySelectorAll('.rate-limiting-rule');
        var rules = [];

        for(var rule_idx = 0; rule_idx < rule_elems.length; rule_idx++) {
            var rule_elem = rule_elems[rule_idx];
            var pill_elems = rule_elem.querySelectorAll('.rate-limiting-pill');
            var cidr_list = [];

            for(var pill_idx = 0; pill_idx < pill_elems.length; pill_idx++) {
                var text_span = pill_elems[pill_idx].querySelector('span:first-child');
                cidr_list.push(text_span.textContent);
            }

            var rate_input = rule_elem.querySelector('[data-field="rate"]');
            var burst_input = rule_elem.querySelector('[data-field="burst"]');
            var limit_input = rule_elem.querySelector('[data-field="limit"]');
            var unit_select = rule_elem.querySelector('[data-field="window_unit"]');
            var time_from_input = rule_elem.querySelector('[data-field="time_from"]');
            var time_to_input = rule_elem.querySelector('[data-field="time_to"]');

            rules.push({
                cidr_list: cidr_list,
                rate: rate_input.value,
                burst: burst_input.value,
                limit: limit_input.value,
                window_unit: unit_select.value,
                time_from: time_from_input.value,
                time_to: time_to_input.value
            });
        }

        return JSON.stringify(rules);
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.rate_limiting.load_rules = function(container_id, rules_json) {
        if(!rules_json) {
            return;
        }

        var rules;
        if(typeof rules_json === 'string') {
            rules = JSON.parse(rules_json);
        }
        else {
            rules = rules_json;
        }

        for(var rule_idx = 0; rule_idx < rules.length; rule_idx++) {
            $.fn.zato.rate_limiting.add_rule(container_id);

            var container = document.getElementById(container_id);
            var rule_elem = container.children[container.children.length - 1];

            var rule = rules[rule_idx];

            for(var cidr_idx = 0; cidr_idx < rule.cidr_list.length; cidr_idx++) {
                $.fn.zato.rate_limiting.add_pill(rule_elem, rule.cidr_list[cidr_idx]);
            }

            var rate_input = rule_elem.querySelector('[data-field="rate"]');
            var burst_input = rule_elem.querySelector('[data-field="burst"]');
            var limit_input = rule_elem.querySelector('[data-field="limit"]');
            var unit_select = rule_elem.querySelector('[data-field="window_unit"]');

            rate_input.value = rule.rate;
            burst_input.value = rule.burst;
            limit_input.value = rule.limit;
            unit_select.value = rule.window_unit;

            // Restore time range if saved values are present
            if(rule.time_from && rule.time_to) {
                var time_from_input = rule_elem.querySelector('[data-field="time_from"]');
                var time_to_input = rule_elem.querySelector('[data-field="time_to"]');

                time_from_input.value = rule.time_from;
                time_to_input.value = rule.time_to;

                $.fn.zato.rate_limiting.toggle_time_range(rule_elem);
            }
        }
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.rate_limiting.save = function(container_id, channel_id) {
        var rules_json = $.fn.zato.rate_limiting.get_rules(container_id);

        $.ajax({
            url: '/zato/http-soap/rate-limiting/save/' + channel_id + '/',
            type: 'POST',
            data: {rules: rules_json},
            headers: {'X-CSRFToken': $.cookie('csrftoken')},
            success: function() {
                $.fn.zato.user_message(true, 'Rate limiting rules saved');
            },
            error: function(jqXHR) {
                $.fn.zato.user_message(false, 'Could not save: ' + jqXHR.responseText);
            }
        });
    };

    // ////////////////////////////////////////////////////////////////////////

})(jQuery);
