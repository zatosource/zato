
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

    var time_input_pattern = /^([01]\d|2[0-3]):([0-5]\d)$/;

    var window_units = ['minute', 'hour', 'day', 'month'];

    var rule_counter = 0;

    var row_accent_color = '#2e7d6a';

    // ////////////////////////////////////////////////////////////////////////
    // Generic dropdown - used by both CIDR pills and time range inputs
    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.rate_limiting.show_dropdown = function(anchor_elem, grouped_items, filter_text, on_select, excluded, keep_open) {

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
                var row = $.fn.zato.rate_limiting.make_dropdown_item(match, on_select, keep_open);
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

    $.fn.zato.rate_limiting.make_dropdown_item = function(item, on_select, keep_open) {
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
            if(keep_open) {
                row.parentNode.removeChild(row);
            }
            else {
                $.fn.zato.rate_limiting.hide_dropdown();
            }
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

    $.fn.zato.rate_limiting.filter_time_input = function(event) {
        var input = event.target;
        var key = event.key;

        // Allow navigation and editing keys
        if(key === 'Backspace' || key === 'Delete' || key === 'ArrowLeft' || key === 'ArrowRight' || key === 'Tab' || key === 'Escape') {
            return;
        }

        // Block everything except digits
        if(key < '0' || key > '9') {
            event.preventDefault();
            return;
        }

        // Auto-insert colon after two digits
        var current = input.value;

        if(current.length === 2 && current.indexOf(':') === -1) {
            input.value = current + ':';
        }
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.rate_limiting.validate_time_input = function(input) {
        var value = input.value;

        if(value === '') {
            return;
        }

        if(!time_input_pattern.test(value)) {
            input.value = '';
        }
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.rate_limiting.close_dropdown_on_outside_click = function() {
        $(document).on('mousedown.rate_limiting', function(event) {
            var target = $(event.target);
            if(!target.closest('.rate-limiting-suggestions').length && !target.hasClass('rate-limiting-pill-input') && !target.hasClass('rate-limiting-time-input')) {
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

        // Start with one empty row
        $.fn.zato.rate_limiting.add_rule(container_id);
    };

    // ////////////////////////////////////////////////////////////////////////
    // Rule structure: header row (CIDRs) + time slots (each with its own config)
    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.rate_limiting.add_rule = function(container_id) {
        var container = document.getElementById(container_id);

        rule_counter += 1;
        var rule_index = container.children.length;

        // The rule card is a vertical flex container
        var rule_elem = document.createElement('div');
        rule_elem.className = 'rate-limiting-rule';
        rule_elem.setAttribute('data-rule-index', rule_index);

        rule_elem.style.setProperty('--slot-accent', row_accent_color);

        // Header row: drag handle + number + CIDR pills + delete
        var header = document.createElement('div');
        header.className = 'rate-limiting-rule-header';

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
        header.appendChild(handle);

        // Rule number
        var number = document.createElement('span');
        number.className = 'rate-limiting-rule-number';
        number.textContent = '#' + (rule_index + 1);
        header.appendChild(number);

        // Pills area (CIDRs) with always-visible input
        var pills = document.createElement('div');
        pills.className = 'rate-limiting-pills';

        var cidr_input = document.createElement('input');
        cidr_input.type = 'text';
        cidr_input.className = 'rate-limiting-pill-input';
        cidr_input.placeholder = 'e.g. 10.0.0.0/8';

        cidr_input.onkeydown = function(event) {
            if(event.key === 'Enter') {
                event.preventDefault();
                cidr_input.blur();
            }
            if(event.key === 'Escape') {
                $.fn.zato.rate_limiting.hide_dropdown();
                cidr_input.value = '';
                // If editing a pill, restore it
                var editing_pill = pills.querySelector('.rate-limiting-pill[data-editing="true"]');
                if(editing_pill) {
                    editing_pill.removeAttribute('data-editing');
                    cidr_input.removeAttribute('data-editing-pill');
                }
                cidr_input.blur();
            }
        };

        var show_cidr_dropdown = function() {
            var excluded = $.fn.zato.rate_limiting.get_existing_cidrs(rule_elem);
            $.fn.zato.rate_limiting.show_dropdown(cidr_input, cidr_suggestions, cidr_input.value, function(selected_value) {
                $.fn.zato.rate_limiting.add_pill(rule_elem, selected_value);
                cidr_input.value = '';
            }, excluded, true);
        };

        cidr_input.onblur = function() {
            var editing_pill = pills.querySelector('.rate-limiting-pill[data-editing="true"]');

            if(editing_pill) {
                var new_value = cidr_input.value.trim();
                if(new_value) {
                    editing_pill.querySelector('span:first-child').textContent = new_value;
                }
                editing_pill.removeAttribute('data-editing');
                cidr_input.removeAttribute('data-editing-pill');
                cidr_input.value = '';
                return;
            }

            var value = cidr_input.value.trim();
            if(value) {
                $.fn.zato.rate_limiting.add_pill(rule_elem, value);
                cidr_input.value = '';
            }
        };

        cidr_input.onfocus = show_cidr_dropdown;
        cidr_input.oninput = show_cidr_dropdown;

        var add_pill_button = document.createElement('span');
        add_pill_button.className = 'rate-limiting-pill-add-button';
        add_pill_button.textContent = '+';
        add_pill_button.onclick = function() {
            cidr_input.focus();
        };

        pills.appendChild(cidr_input);
        pills.appendChild(add_pill_button);

        header.appendChild(pills);

        // Delete row link
        var remove_button = document.createElement('a');
        remove_button.href = 'javascript:void(0)';
        remove_button.textContent = 'Delete row';
        remove_button.onclick = function() {
            $.fn.zato.rate_limiting.remove_row(container_id, rule_elem);
        };
        header.appendChild(remove_button);

        rule_elem.appendChild(header);

        // Time slots area
        var slots = document.createElement('div');
        slots.className = 'rate-limiting-slots';
        rule_elem.appendChild(slots);

        // The first slot is always "all day" - it cannot be removed
        $.fn.zato.rate_limiting.add_slot(slots, 'All day', '', '', true);

        // "Add rule" button inside the row
        var add_slot_button = document.createElement('span');
        add_slot_button.className = 'rate-limiting-button-add';
        add_slot_button.textContent = '+ Add rule';
        add_slot_button.onclick = function() {
            $.fn.zato.rate_limiting.begin_add_slot(slots, add_slot_button);
        };
        rule_elem.appendChild(add_slot_button);

        container.appendChild(rule_elem);
        $.fn.zato.rate_limiting.renumber(container_id);
    };

    // ////////////////////////////////////////////////////////////////////////
    // A single time slot row with its own rate/burst/limit/window config
    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.rate_limiting.add_slot = function(slots_container, time_label_text, time_from, time_to, is_default) {

        var slot = document.createElement('div');
        slot.className = 'rate-limiting-slot';

        if(is_default) {
            slot.setAttribute('data-slot-type', 'default');
        }
        else {
            slot.setAttribute('data-slot-type', 'range');
            slot.setAttribute('data-time-from', time_from);
            slot.setAttribute('data-time-to', time_to);
        }

        // Time label
        var time_area = document.createElement('div');
        time_area.className = 'rate-limiting-slot-time';

        var label = document.createElement('span');
        label.className = 'rate-limiting-slot-time-label';
        label.textContent = time_label_text;
        time_area.appendChild(label);

        if(!is_default) {
            label.style.cursor = 'pointer';
            label.onclick = function() {
                $.fn.zato.rate_limiting.edit_slot_time(slot, time_area, label);
            };
        }

        slot.appendChild(time_area);

        // Rate config group
        var rate_group = document.createElement('div');
        rate_group.className = 'rate-limiting-config-group';

        var rate_label = document.createElement('span');
        rate_label.className = 'rate-limiting-config-label';
        rate_label.textContent = 'Rate:';
        rate_group.appendChild(rate_label);

        var rate_input = document.createElement('input');
        rate_input.type = 'text';
        rate_input.className = 'rate-limiting-config-input';
        rate_input.setAttribute('data-field', 'rate');
        rate_input.placeholder = '10';
        rate_input.value = '10';
        rate_group.appendChild(rate_input);

        var rate_unit = document.createElement('span');
        rate_unit.className = 'rate-limiting-config-unit';
        rate_unit.textContent = 'req/s';
        rate_group.appendChild(rate_unit);

        slot.appendChild(rate_group);

        // Burst config group
        var burst_group = document.createElement('div');
        burst_group.className = 'rate-limiting-config-group';

        var burst_label = document.createElement('span');
        burst_label.className = 'rate-limiting-config-label';
        burst_label.textContent = 'Burst:';
        burst_group.appendChild(burst_label);

        var burst_input = document.createElement('input');
        burst_input.type = 'text';
        burst_input.className = 'rate-limiting-config-input';
        burst_input.setAttribute('data-field', 'burst');
        burst_input.placeholder = '20';
        burst_input.value = '20';
        burst_group.appendChild(burst_input);

        var burst_unit = document.createElement('span');
        burst_unit.className = 'rate-limiting-config-unit';
        burst_unit.textContent = 'req/s';
        burst_group.appendChild(burst_unit);

        slot.appendChild(burst_group);

        // Limit/window config group
        var limit_group = document.createElement('div');
        limit_group.className = 'rate-limiting-config-group';

        var limit_label = document.createElement('span');
        limit_label.className = 'rate-limiting-config-label';
        limit_label.textContent = 'Limit:';
        limit_group.appendChild(limit_label);

        var limit_input = document.createElement('input');
        limit_input.type = 'text';
        limit_input.className = 'rate-limiting-config-input';
        limit_input.setAttribute('data-field', 'limit');
        limit_input.placeholder = '100';
        limit_input.value = '100';
        limit_group.appendChild(limit_input);

        var slash_label = document.createElement('span');
        slash_label.className = 'rate-limiting-config-unit';
        slash_label.textContent = 'req/';
        limit_group.appendChild(slash_label);

        var unit_select = document.createElement('select');
        unit_select.className = 'rate-limiting-config-select';
        unit_select.setAttribute('data-field', 'window_unit');
        for(var unit_idx = 0; unit_idx < window_units.length; unit_idx++) {
            var opt = document.createElement('option');
            opt.value = window_units[unit_idx];
            opt.textContent = window_units[unit_idx];
            unit_select.appendChild(opt);
        }
        limit_group.appendChild(unit_select);

        slot.appendChild(limit_group);

        // Slot actions area
        var actions = document.createElement('span');
        actions.className = 'rate-limiting-slot-actions';

        // Disable/Enable toggle
        var toggle_link = document.createElement('a');
        toggle_link.href = 'javascript:void(0)';
        toggle_link.className = 'rate-limiting-slot-toggle';
        toggle_link.textContent = 'Disable';
        toggle_link.onclick = function() {
            $.fn.zato.rate_limiting.toggle_slot(slot, toggle_link);
        };
        actions.appendChild(toggle_link);

        // Delete rule (only for non-default slots)
        if(!is_default) {
            var delete_link = document.createElement('a');
            delete_link.href = 'javascript:void(0)';
            delete_link.className = 'rate-limiting-slot-delete';
            delete_link.textContent = 'Delete rule';
            delete_link.onclick = function() {
                slot.parentNode.removeChild(slot);
            };
            actions.appendChild(delete_link);
        }

        slot.appendChild(actions);

        slots_container.appendChild(slot);
        return slot;
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.rate_limiting.toggle_slot = function(slot, toggle_link) {
        var is_disabled = slot.getAttribute('data-disabled') === 'true';

        if(is_disabled) {
            slot.removeAttribute('data-disabled');
            toggle_link.textContent = 'Disable';
        }
        else {
            slot.setAttribute('data-disabled', 'true');
            toggle_link.textContent = 'Enable';
        }
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.rate_limiting.edit_slot_time = function(slot, time_area, label) {

        // Already editing - do nothing
        if(time_area.querySelector('.rate-limiting-time-input')) {
            return;
        }

        var current_from = slot.getAttribute('data-time-from');
        var current_to = slot.getAttribute('data-time-to');

        label.style.display = 'none';

        var from_input = document.createElement('input');
        from_input.type = 'text';
        from_input.className = 'rate-limiting-time-input';
        from_input.value = current_from;
        from_input.maxLength = 5;

        var dash = document.createElement('span');
        dash.className = 'rate-limiting-time-dash';
        dash.textContent = '\u2013';

        var to_input = document.createElement('input');
        to_input.type = 'text';
        to_input.className = 'rate-limiting-time-input';
        to_input.value = current_to;
        to_input.maxLength = 5;

        time_area.appendChild(from_input);
        time_area.appendChild(dash);
        time_area.appendChild(to_input);

        var finish_edit = function() {
            var new_from = from_input.value;
            var new_to = to_input.value;

            if(time_input_pattern.test(new_from) && time_input_pattern.test(new_to)) {
                slot.setAttribute('data-time-from', new_from);
                slot.setAttribute('data-time-to', new_to);
                label.textContent = new_from + ' \u2013 ' + new_to;
            }

            // Remove the editing inputs ..
            if(from_input.parentNode) {
                from_input.parentNode.removeChild(from_input);
            }
            if(dash.parentNode) {
                dash.parentNode.removeChild(dash);
            }
            if(to_input.parentNode) {
                to_input.parentNode.removeChild(to_input);
            }

            // .. and show the label again.
            label.style.display = '';
            $.fn.zato.rate_limiting.hide_dropdown();
        };

        from_input.onkeydown = function(event) {
            $.fn.zato.rate_limiting.filter_time_input(event);
            if(event.key === 'Escape') {
                finish_edit();
            }
        };

        to_input.onkeydown = function(event) {
            $.fn.zato.rate_limiting.filter_time_input(event);
            if(event.key === 'Enter') {
                event.preventDefault();
                finish_edit();
            }
            if(event.key === 'Escape') {
                finish_edit();
            }
        };

        var editing_finished = false;

        var try_close = function() {
            setTimeout(function() {
                if(editing_finished) {
                    return;
                }
                if(!time_area.querySelector('.rate-limiting-time-input:focus')) {
                    editing_finished = true;
                    finish_edit();
                }
            }, 200);
        };

        // Show full time list (no filter) so the user sees all options
        var show_from_dropdown = function() {
            $.fn.zato.rate_limiting.show_dropdown(from_input, time_suggestions, '', function(selected_value) {
                from_input.value = selected_value;
                to_input.focus();
                setTimeout(show_to_dropdown, 0);
            });
        };

        var show_to_dropdown = function() {
            $.fn.zato.rate_limiting.show_dropdown(to_input, time_suggestions, '', function(selected_value) {
                to_input.value = selected_value;
                editing_finished = true;
                finish_edit();
            });
        };

        from_input.onfocus = show_from_dropdown;
        to_input.onfocus = show_to_dropdown;

        from_input.onblur = function() {
            $.fn.zato.rate_limiting.validate_time_input(from_input);
            try_close();
        };

        to_input.onblur = function() {
            $.fn.zato.rate_limiting.validate_time_input(to_input);
            try_close();
        };

        from_input.focus();
        from_input.select();
    };

    // ////////////////////////////////////////////////////////////////////////
    // Begin adding a new time slot - show from/to inputs inline
    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.rate_limiting.begin_add_slot = function(slots_container, add_slot_button) {

        // If there is already a pending slot being added, focus its input
        var existing_input = slots_container.querySelector('.rate-limiting-time-input');
        if(existing_input) {
            existing_input.focus();
            return;
        }

        // Create a temporary slot row for entering the time range
        var pending_slot = document.createElement('div');
        pending_slot.className = 'rate-limiting-slot';
        pending_slot.setAttribute('data-slot-type', 'pending');

        var time_area = document.createElement('div');
        time_area.className = 'rate-limiting-slot-time';

        var from_input = document.createElement('input');
        from_input.type = 'text';
        from_input.className = 'rate-limiting-time-input';
        from_input.placeholder = 'from';
        from_input.maxLength = 5;

        var dash = document.createElement('span');
        dash.className = 'rate-limiting-time-dash';
        dash.textContent = '\u2013';

        var to_input = document.createElement('input');
        to_input.type = 'text';
        to_input.className = 'rate-limiting-time-input';
        to_input.placeholder = 'to';
        to_input.maxLength = 5;

        time_area.appendChild(from_input);
        time_area.appendChild(dash);
        time_area.appendChild(to_input);
        pending_slot.appendChild(time_area);

        slots_container.appendChild(pending_slot);

        // Wire from-input
        var show_from_dropdown = function() {
            $.fn.zato.rate_limiting.show_dropdown(from_input, time_suggestions, from_input.value, function(selected_value) {
                from_input.value = selected_value;
                to_input.focus();
                // The dropdown was just hidden by the item click,
                // so we re-show it for the "to" field after a tick.
                setTimeout(show_to_dropdown, 0);
            });
        };

        from_input.onfocus = show_from_dropdown;
        from_input.oninput = show_from_dropdown;
        from_input.onkeydown = function(event) {
            $.fn.zato.rate_limiting.filter_time_input(event);
            if(event.key === 'Tab' && !event.shiftKey && from_input.value.length === 5) {
                // Let Tab naturally move to to_input
                return;
            }
            if(event.key === 'Escape') {
                $.fn.zato.rate_limiting.hide_dropdown();
                pending_slot.parentNode.removeChild(pending_slot);
            }
        };
        from_input.onblur = function() {
            $.fn.zato.rate_limiting.validate_time_input(from_input);
        };

        // Wire to-input
        var show_to_dropdown = function() {
            $.fn.zato.rate_limiting.show_dropdown(to_input, time_suggestions, to_input.value, function(selected_value) {
                to_input.value = selected_value;
                $.fn.zato.rate_limiting.commit_pending_slot(slots_container, pending_slot, from_input, to_input);
            });
        };

        to_input.onfocus = show_to_dropdown;
        to_input.oninput = show_to_dropdown;
        to_input.onkeydown = function(event) {
            $.fn.zato.rate_limiting.filter_time_input(event);
            if(event.key === 'Enter') {
                event.preventDefault();
                $.fn.zato.rate_limiting.commit_pending_slot(slots_container, pending_slot, from_input, to_input);
            }
            if(event.key === 'Escape') {
                $.fn.zato.rate_limiting.hide_dropdown();
                pending_slot.parentNode.removeChild(pending_slot);
            }
        };
        to_input.onblur = function() {
            $.fn.zato.rate_limiting.validate_time_input(to_input);
        };

        from_input.focus();
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.rate_limiting.commit_pending_slot = function(slots_container, pending_slot, from_input, to_input) {
        var from_value = from_input.value;
        var to_value = to_input.value;

        // Both must be valid HH:MM
        if(!time_input_pattern.test(from_value) || !time_input_pattern.test(to_value)) {
            return;
        }

        $.fn.zato.rate_limiting.hide_dropdown();

        var label_text = from_value + ' \u2013 ' + to_value;

        // Remove the pending row ..
        pending_slot.parentNode.removeChild(pending_slot);

        // .. and replace it with a real slot.
        $.fn.zato.rate_limiting.add_slot(slots_container, label_text, from_value, to_value, false);
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.rate_limiting.remove_row = function(container_id, rule_elem) {
        rule_elem.parentNode.removeChild(rule_elem);
        $.fn.zato.rate_limiting.renumber(container_id);
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
    // CIDR pills
    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.rate_limiting.add_pill = function(rule_elem, cidr_text) {
        cidr_text = cidr_text.trim();
        if(!cidr_text) {
            return;
        }

        var pills = rule_elem.querySelector('.rate-limiting-pills');

        var pill = document.createElement('span');
        pill.className = 'rate-limiting-pill';

        var text_node = document.createElement('span');
        text_node.textContent = cidr_text;
        text_node.style.cursor = 'pointer';
        text_node.onclick = function() {
            var cidr_input = pills.querySelector('.rate-limiting-pill-input');
            pill.setAttribute('data-editing', 'true');
            cidr_input.value = text_node.textContent;
            cidr_input.focus();
            cidr_input.select();
        };
        pill.appendChild(text_node);

        var remove_x = document.createElement('span');
        remove_x.className = 'rate-limiting-pill-remove';
        remove_x.textContent = '\u00d7';
        remove_x.onclick = function() {
            pill.parentNode.removeChild(pill);
        };
        pill.appendChild(remove_x);

        pills.appendChild(pill);
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
    // Drag and drop
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
    // Serialization
    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.rate_limiting.get_rules = function(container_id) {
        var container = document.getElementById(container_id);
        var rule_elems = container.querySelectorAll('.rate-limiting-rule');
        var rules = [];

        for(var rule_idx = 0; rule_idx < rule_elems.length; rule_idx++) {
            var rule_elem = rule_elems[rule_idx];

            // Collect CIDRs
            var pill_elems = rule_elem.querySelectorAll('.rate-limiting-pills .rate-limiting-pill');
            var cidr_list = [];

            for(var pill_idx = 0; pill_idx < pill_elems.length; pill_idx++) {
                var text_span = pill_elems[pill_idx].querySelector('span:first-child');
                cidr_list.push(text_span.textContent);
            }

            // Collect time slots
            var slot_elems = rule_elem.querySelectorAll('.rate-limiting-slot:not([data-slot-type="pending"])');
            var slots = [];

            for(var slot_idx = 0; slot_idx < slot_elems.length; slot_idx++) {
                var slot_elem = slot_elems[slot_idx];
                var slot_type = slot_elem.getAttribute('data-slot-type');

                var slot_data = {
                    type: slot_type,
                    disabled: slot_elem.getAttribute('data-disabled') === 'true',
                    rate: slot_elem.querySelector('[data-field="rate"]').value,
                    burst: slot_elem.querySelector('[data-field="burst"]').value,
                    limit: slot_elem.querySelector('[data-field="limit"]').value,
                    window_unit: slot_elem.querySelector('[data-field="window_unit"]').value
                };

                if(slot_type === 'range') {
                    slot_data.time_from = slot_elem.getAttribute('data-time-from');
                    slot_data.time_to = slot_elem.getAttribute('data-time-to');
                }

                slots.push(slot_data);
            }

            rules.push({
                cidr_list: cidr_list,
                slots: slots
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

        // Clear the default empty rule added by init
        var container = document.getElementById(container_id);
        container.innerHTML = '';
        rule_counter = 0;

        for(var rule_idx = 0; rule_idx < rules.length; rule_idx++) {
            $.fn.zato.rate_limiting.add_rule(container_id);

            var container_ref = document.getElementById(container_id);
            var rule_elem = container_ref.children[container_ref.children.length - 1];

            var rule = rules[rule_idx];

            // Restore CIDRs
            for(var cidr_idx = 0; cidr_idx < rule.cidr_list.length; cidr_idx++) {
                $.fn.zato.rate_limiting.add_pill(rule_elem, rule.cidr_list[cidr_idx]);
            }

            // Restore slot config values
            var slot_elems = rule_elem.querySelectorAll('.rate-limiting-slot');

            if(rule.slots) {
                // The first slot (all day) is already created by add_rule
                var default_slot = slot_elems[0];

                if(rule.slots.length > 0 && rule.slots[0].type === 'default') {
                    default_slot.querySelector('[data-field="rate"]').value = rule.slots[0].rate;
                    default_slot.querySelector('[data-field="burst"]').value = rule.slots[0].burst;
                    default_slot.querySelector('[data-field="limit"]').value = rule.slots[0].limit;
                    default_slot.querySelector('[data-field="window_unit"]').value = rule.slots[0].window_unit;

                    if(rule.slots[0].disabled) {
                        var toggle_link = default_slot.querySelector('.rate-limiting-slot-toggle');
                        $.fn.zato.rate_limiting.toggle_slot(default_slot, toggle_link);
                    }
                }

                // Restore additional time-range slots
                var slots_container = rule_elem.querySelector('.rate-limiting-slots');

                for(var slot_idx = 1; slot_idx < rule.slots.length; slot_idx++) {
                    var slot_data = rule.slots[slot_idx];

                    if(slot_data.type === 'range') {
                        var label_text = slot_data.time_from + ' \u2013 ' + slot_data.time_to;
                        var new_slot = $.fn.zato.rate_limiting.add_slot(slots_container, label_text, slot_data.time_from, slot_data.time_to, false);

                        new_slot.querySelector('[data-field="rate"]').value = slot_data.rate;
                        new_slot.querySelector('[data-field="burst"]').value = slot_data.burst;
                        new_slot.querySelector('[data-field="limit"]').value = slot_data.limit;
                        new_slot.querySelector('[data-field="window_unit"]').value = slot_data.window_unit;

                        if(slot_data.disabled) {
                            var toggle_link = new_slot.querySelector('.rate-limiting-slot-toggle');
                            $.fn.zato.rate_limiting.toggle_slot(new_slot, toggle_link);
                        }
                    }
                }
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
