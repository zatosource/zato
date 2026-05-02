
// ////////////////////////////////////////////////////////////////////////////
// Rate limiting UI for CIDR-based rules
// ////////////////////////////////////////////////////////////////////////////

(function($) {

    // Suggested CIDR ranges grouped by protocol
    var cidr_suggestions = [
        {group: 'IPv4', items: [
            {value: '0.0.0.0/0',      label: 'all IPv4'},
            {value: '10.0.0.0/8',     label: 'private 10.x'},
            {value: '172.16.0.0/12',  label: 'private 172.16.x'},
            {value: '192.168.0.0/16', label: 'private 192.168.x'},
            {value: '127.0.0.0/8',    label: 'loopback'}
        ]},
        {group: 'IPv6', items: [
            {value: '::/0',           label: 'all IPv6'},
            {value: '::1/128',       label: 'loopback'},
            {value: 'fe80::/10',     label: 'link-local'}
        ]}
    ];

    // Common time-of-day presets grouped by category
    var time_suggestions = [
        {group: 'Business hours', items: [
            {value: '06:00', label: '6 AM'},
            {value: '07:00', label: '7 AM'},
            {value: '08:00', label: '8 AM'},
            {value: '09:00', label: '9 AM'},
            {value: '10:00', label: '10 AM'},
            {value: '11:00', label: '11 AM'},
            {value: '12:00', label: 'noon'},
            {value: '13:00', label: '1 PM'},
            {value: '14:00', label: '2 PM'},
            {value: '15:00', label: '3 PM'},
            {value: '16:00', label: '4 PM'},
            {value: '17:00', label: '5 PM'},
            {value: '18:00', label: '6 PM'}
        ]},
        {group: 'Off hours', items: [
            {value: '19:00', label: '7 PM'},
            {value: '20:00', label: '8 PM'},
            {value: '21:00', label: '9 PM'},
            {value: '22:00', label: '10 PM'},
            {value: '23:00', label: '11 PM'},
            {value: '00:00', label: 'midnight'},
            {value: '01:00', label: '1 AM'},
            {value: '02:00', label: '2 AM'},
            {value: '03:00', label: '3 AM'},
            {value: '04:00', label: '4 AM'},
            {value: '05:00', label: '5 AM'}
        ]}
    ];

    var window_units = ['minute', 'hour', 'day', 'month'];

    var rule_counter = 0;

    // ////////////////////////////////////////////////////////////////////////
    // Generic dropdown - used by both CIDR pills and time range inputs
    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.rate_limiting.show_dropdown = function(anchor_elem, grouped_items, filter_text, on_select, excluded) {

        $.fn.zato.rate_limiting.hide_dropdown();

        var dropdown = document.createElement('div');
        dropdown.className = 'rate-limiting-suggestions';
        dropdown.id = 'rate-limiting-dropdown-active';

        var filter = (filter_text || '').trim().toLowerCase();
        var total_items = 0;

        for(var group_idx = 0; group_idx < grouped_items.length; group_idx++) {
            var group = grouped_items[group_idx];
            var matching_items = [];

            for(var item_idx = 0; item_idx < group.items.length; item_idx++) {
                var item = group.items[item_idx];

                // Skip already-selected values
                if(excluded && excluded[item.value]) {
                    continue;
                }

                // Apply text filter
                if(filter && item.value.toLowerCase().indexOf(filter) === -1 && item.label.toLowerCase().indexOf(filter) === -1) {
                    continue;
                }

                matching_items.push(item);
            }

            if(matching_items.length === 0) {
                continue;
            }

            // Add separator between groups
            if(total_items > 0) {
                var separator = document.createElement('div');
                separator.className = 'rate-limiting-suggestion-separator';
                dropdown.appendChild(separator);
            }

            // Group header
            var header = document.createElement('div');
            header.className = 'rate-limiting-suggestion-header';
            header.textContent = group.group;
            dropdown.appendChild(header);

            // Items
            for(var match_idx = 0; match_idx < matching_items.length; match_idx++) {
                var match = matching_items[match_idx];
                var row = $.fn.zato.rate_limiting.make_dropdown_item(match, on_select);
                dropdown.appendChild(row);
                total_items++;
            }
        }

        if(total_items === 0) {
            return;
        }

        // Position below the anchor element
        var rect = anchor_elem.getBoundingClientRect();
        dropdown.style.position = 'fixed';
        dropdown.style.top = (rect.bottom + 2) + 'px';
        dropdown.style.left = rect.left + 'px';

        document.body.appendChild(dropdown);
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.rate_limiting.make_dropdown_item = function(item, on_select) {
        var row = document.createElement('div');
        row.className = 'rate-limiting-suggestion-item';

        var value_span = document.createElement('span');
        value_span.className = 'rate-limiting-suggestion-cidr';
        value_span.textContent = item.value;
        row.appendChild(value_span);

        var label_span = document.createElement('span');
        label_span.className = 'rate-limiting-suggestion-label';
        label_span.textContent = item.label;
        row.appendChild(label_span);

        row.onclick = function() {
            on_select(item.value);
            $.fn.zato.rate_limiting.hide_dropdown();
        };

        return row;
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.rate_limiting.hide_dropdown = function() {
        var existing = document.getElementById('rate-limiting-dropdown-active');
        if(existing) {
            existing.parentNode.removeChild(existing);
        }
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.rate_limiting.close_dropdown_on_outside_click = function() {
        $(document).on('mousedown.rate_limiting', function(event) {
            var target = $(event.target);
            if(!target.closest('.rate-limiting-suggestions').length && !target.hasClass('rate-limiting-pill-input') && !target.hasClass('rate-limiting-config-input')) {
                $.fn.zato.rate_limiting.hide_dropdown();
            }
        });
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.rate_limiting.init = function(container_id, mode) {
        var container = document.getElementById(container_id);
        container.innerHTML = '';
        rule_counter = 0;
        $.fn.zato.rate_limiting.setup_drag(container_id);
        $.fn.zato.rate_limiting.close_dropdown_on_outside_click();
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
            $.fn.zato.rate_limiting.show_cidr_input(pills, add_pill_button);
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
        time_from_input.type = 'text';
        time_from_input.className = 'rate-limiting-config-input';
        time_from_input.setAttribute('data-field', 'time_from');
        time_from_input.placeholder = 'from';
        time_from_input.readOnly = true;

        time_from_input.onclick = function() {
            $.fn.zato.rate_limiting.show_dropdown(time_from_input, time_suggestions, '', function(selected_value) {
                time_from_input.value = selected_value;
            });
        };

        time_fields.appendChild(time_from_input);

        var time_dash = document.createElement('span');
        time_dash.className = 'rate-limiting-time-dash';
        time_dash.textContent = '\u2013';
        time_fields.appendChild(time_dash);

        var time_to_input = document.createElement('input');
        time_to_input.type = 'text';
        time_to_input.className = 'rate-limiting-config-input';
        time_to_input.setAttribute('data-field', 'time_to');
        time_to_input.placeholder = 'to';
        time_to_input.readOnly = true;

        time_to_input.onclick = function() {
            $.fn.zato.rate_limiting.show_dropdown(time_to_input, time_suggestions, '', function(selected_value) {
                time_to_input.value = selected_value;
            });
        };

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

    $.fn.zato.rate_limiting.show_cidr_input = function(pills_container, add_button) {

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

        input.onkeydown = function(event) {
            if(event.key === 'Enter') {
                event.preventDefault();
                var value = input.value.trim();
                if(value) {
                    var rule_elem = pills_container.closest('.rate-limiting-rule');
                    $.fn.zato.rate_limiting.add_pill(rule_elem, value);
                }
                input.value = '';
                $.fn.zato.rate_limiting.hide_dropdown();
            }
            if(event.key === 'Escape') {
                $.fn.zato.rate_limiting.hide_dropdown();
                input.parentNode.removeChild(input);
            }
        };

        var show_cidr_dropdown = function() {
            var rule_elem = pills_container.closest('.rate-limiting-rule');
            var excluded = $.fn.zato.rate_limiting.get_existing_cidrs(rule_elem);

            $.fn.zato.rate_limiting.show_dropdown(input, cidr_suggestions, input.value, function(selected_value) {
                var rule_elem = pills_container.closest('.rate-limiting-rule');
                $.fn.zato.rate_limiting.add_pill(rule_elem, selected_value);
                input.value = '';
                input.focus();
            }, excluded);
        };

        input.onfocus = show_cidr_dropdown;
        input.oninput = show_cidr_dropdown;

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
