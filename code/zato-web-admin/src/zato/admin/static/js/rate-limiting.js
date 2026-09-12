
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

    var window_units = ['minute', 'hour', 'day', 'month'];

    // What a fresh slot holds before anything is typed into it
    var slot_defaults = {rate: '10', burst: '20', limit: '100'};

    // The slot lists of every rule on the page, keyed by the rule element
    var slot_kits = new WeakMap();

    var rule_counter = 0;
    var stored_entity_id = '';
    var stored_url_base = '';
    var stored_with_clear_counters = false;

    var row_accent_color = '#2e7d6a';

    // ////////////////////////////////////////////////////////////////////////
    // The CIDR dropdown - the menu itself is the dashboard kit's
    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.rate_limiting.show_dropdown = function(anchor_elem, grouped_items, filter_text, on_select, excluded, keep_open) {
        $.fn.zato.dashboard_kit.select.show_menu({
            anchor: anchor_elem,
            groups: grouped_items,
            filter: filter_text,
            on_select: on_select,
            excluded: excluded,
            keep_open: keep_open,
            toggle_pick: false,
            item_style: 'value_label',
            with_filter: false
        });
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.rate_limiting.hide_dropdown = function() {
        $.fn.zato.dashboard_kit.select.hide_menu();
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.rate_limiting.init = function(container_id, mode, entity_id, url_base, with_clear_counters) {
        var container = document.getElementById(container_id);
        container.innerHTML = '';
        rule_counter = 0;
        stored_entity_id = entity_id;
        stored_url_base = url_base;
        stored_with_clear_counters = Boolean(with_clear_counters);
        $.fn.zato.rate_limiting.setup_drag(container_id);

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

        rule_elem.style.setProperty('--time-slot-accent', row_accent_color);

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

        // Counters exist per entity on the server, tier editor pages have none
        if(stored_with_clear_counters) {
            var clear_link = document.createElement('a');
            clear_link.href = 'javascript:void(0)';
            clear_link.textContent = 'Clear counters';
            clear_link.onclick = function() {
                $.fn.zato.rate_limiting.clear_counters(container_id, rule_elem, clear_link);
            };
            header.appendChild(clear_link);

            var separator = document.createElement('span');
            separator.textContent = ' | ';
            separator.style.color = '#888';
            header.appendChild(separator);
        }

        var remove_button = document.createElement('a');
        remove_button.href = 'javascript:void(0)';
        remove_button.textContent = 'Delete row';
        remove_button.onclick = function() {
            $.fn.zato.rate_limiting.remove_row(container_id, rule_elem);
        };
        header.appendChild(remove_button);

        rule_elem.appendChild(header);

        // The time slots - the All day one first, the kit adds the ranges
        var slots = $.fn.zato.time_slots.create({
            container: rule_elem,
            with_disable: true,
            labels: {add: '+ Add rule', delete: 'Delete rule', disable: 'Disable rule', enable: 'Enable rule'},
            toggles: [{attr: 'disallowed', off_label: 'Disallow traffic', on_label: 'Allow traffic'}],
            build_fields: $.fn.zato.rate_limiting.build_slot_fields,
            read_fields: $.fn.zato.rate_limiting.read_slot_fields,
            write_fields: $.fn.zato.rate_limiting.write_slot_fields
        });
        slot_kits.set(rule_elem, slots);

        container.appendChild(rule_elem);

        // Now that the rule is in the DOM, lock action cell widths
        // so toggling text never causes layout shifts.
        slots.lock_widths();

        $.fn.zato.rate_limiting.renumber(container_id);
    };

    // ////////////////////////////////////////////////////////////////////////
    // The rate, burst and limit of one slot
    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.rate_limiting.build_slot_fields = function(slot) {

        var kit = $.fn.zato.time_slots;

        var rate_group = kit.add_group(slot);
        kit.add_text(rate_group, 'Rate:', 'label');
        kit.add_input(rate_group, 'rate', slot_defaults.rate);
        kit.add_text(rate_group, 'req/s', 'unit');

        var burst_group = kit.add_group(slot);
        kit.add_text(burst_group, 'Burst:', 'label');
        kit.add_input(burst_group, 'burst', slot_defaults.burst);
        kit.add_text(burst_group, 'req/s', 'unit');

        var limit_group = kit.add_group(slot);
        kit.add_text(limit_group, 'Limit:', 'label');
        kit.add_input(limit_group, 'limit', slot_defaults.limit);
        kit.add_text(limit_group, 'req/', 'unit');
        kit.add_select(limit_group, 'window_unit', window_units);
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.rate_limiting.read_slot_fields = function(slot) {

        var kit = $.fn.zato.time_slots;

        var out = {
            rate: kit.field(slot, 'rate').value,
            burst: kit.field(slot, 'burst').value,
            limit: kit.field(slot, 'limit').value,
            limit_unit: kit.field(slot, 'window_unit').value
        };

        return out;
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.rate_limiting.write_slot_fields = function(slot, entry) {

        var kit = $.fn.zato.time_slots;

        kit.field(slot, 'rate').value = entry.rate;
        kit.field(slot, 'burst').value = entry.burst;
        kit.field(slot, 'limit').value = entry.limit;
        kit.field(slot, 'window_unit').value = entry.limit_unit;
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
        text_node.onmousedown = function(event) {
            event.preventDefault();
            var cidr_input = pills.querySelector('.rate-limiting-pill-input');

            // Commit the previously editing pill first
            var prev = pills.querySelector('.rate-limiting-pill[data-editing="true"]');
            if(prev && prev !== pill) {
                var prev_value = cidr_input.value.trim();
                if(prev_value) {
                    prev.querySelector('span:first-child').textContent = prev_value;
                }
                prev.removeAttribute('data-editing');
            }

            pill.setAttribute('data-editing', 'true');
            cidr_input.value = text_node.textContent;
            cidr_input.focus();
            cidr_input.setSelectionRange(0, 0);
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

            // Collect time ranges
            var time_range = slot_kits.get(rule_elem).get_entries();

            rules.push({
                cidr_list: cidr_list,
                time_range: time_range
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

            // Restore the time slots - the All day one is already there, the kit fills it and adds the ranges
            if(rule.time_range) {
                slot_kits.get(rule_elem).load(rule.time_range);
            }
        }
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.rate_limiting.clear_counters = function(container_id, rule_elem, clear_link) {
        var container = document.getElementById(container_id);
        var rule_index = Array.prototype.indexOf.call(container.children, rule_elem);

        $.ajax({
            url: stored_url_base + '/clear-counters/' + stored_entity_id + '/',
            type: 'POST',
            data: {rule_index: rule_index},
            headers: {'X-CSRFToken': $.cookie('csrftoken')},
            success: function() {
                var _tooltip = tippy(clear_link, {
                    content: 'OK, cleared',
                    allowHTML: false,
                    theme: 'dark',
                    trigger: 'manual',
                    placement: 'left',
                    arrow: true,
                    interactive: false,
                    inertia: true,
                });
                var instance = Array.isArray(_tooltip) ? _tooltip[0] : _tooltip;
                if(instance) {
                    instance.show();
                    setTimeout(function() {
                        instance.hide();
                        setTimeout(function() { instance.destroy(); }, 300);
                    }, 750);
                }
            },
            error: function(jqXHR) {
                var msg = 'Could not clear counters';
                try {
                    var response = JSON.parse(jqXHR.responseText);
                    if(response.error) {
                        msg = response.error;
                    }
                }
                catch(e) {
                    msg = jqXHR.responseText || msg;
                }
                var _tooltip = tippy(clear_link, {
                    content: msg,
                    allowHTML: false,
                    theme: 'dark',
                    trigger: 'manual',
                    placement: 'left',
                    arrow: true,
                    interactive: false,
                    inertia: true,
                });
                var instance = Array.isArray(_tooltip) ? _tooltip[0] : _tooltip;
                if(instance) {
                    instance.show();
                    setTimeout(function() {
                        instance.hide();
                        setTimeout(function() { instance.destroy(); }, 300);
                    }, 3000);
                }
            }
        });
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.rate_limiting.save = function(container_id) {
        var rules_json = $.fn.zato.rate_limiting.get_rules(container_id);
        console.log('[rate_limiting.save] rules_json:', rules_json);
        var status = $('#rate-limiting-status');

        status.removeClass('show fade status-message-success status-message-error');

        var data = {rules_json: rules_json};

        // Rate limiting pages carry a quota tier vs. custom rules choice expressed
        // with tabs - an entity governed by a tier does not send its own rules.
        var tier_tab = document.querySelector('.dashboard-tab[data-mode="tier"]');
        var tier_select = document.getElementById('quota-tier-select');

        if(tier_tab) {
            var use_tier = tier_tab.classList.contains('dashboard-tab-active');
            data.quota_tier = use_tier && tier_select ? tier_select.value : '';
            if(use_tier) {
                data.rules_json = '[]';
            }
        }

        $.ajax({
            url: stored_url_base + '/save/' + stored_entity_id + '/',
            type: 'POST',
            data: data,
            headers: {'X-CSRFToken': $.cookie('csrftoken')},
            success: function() {
                status.text('OK, saved').addClass('show status-message-success');
                setTimeout(function() {
                    status.addClass('fade');
                    setTimeout(function() {
                        status.removeClass('show fade status-message-success');
                    }, 500);
                }, 750);
            },
            error: function(jqXHR) {
                var msg = 'Could not save';
                try {
                    var response = JSON.parse(jqXHR.responseText);
                    if(response.error) {
                        msg = response.error;
                    }
                }
                catch(e) {
                    msg = jqXHR.responseText || msg;
                }
                status.text(msg).addClass('show status-message-error');
            }
        });
    };

    // ////////////////////////////////////////////////////////////////////////
    // Quota tier vs. custom rules - tab-based mode toggle
    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.rate_limiting.init_mode_toggle = function(container_id) {
        var tabs = document.querySelectorAll('.dashboard-tab[data-mode]');
        var tier_panel = document.getElementById('rate-limiting-tier-panel');
        var has_tiers = Boolean(document.getElementById('quota-tier-select'));

        var activate = function(mode) {
            tabs.forEach(function(tab) {
                var is_active = tab.dataset.mode === mode;
                tab.classList.toggle('dashboard-tab-active', is_active);
                tab.setAttribute('aria-selected', is_active ? 'true' : 'false');
            });

            var use_tier = mode === 'tier';
            tier_panel.hidden = !use_tier;
            $('#' + container_id).toggle(!use_tier);
            $('.rate-limiting-button-add, .time-slots-add').toggle(!use_tier);

            // With no tiers to pick from there is nothing to save on the tier tab
            $('.rate-limiting-save-group').toggle(!use_tier || has_tiers);
        };

        tabs.forEach(function(tab) {
            tab.addEventListener('click', function() {
                activate(tab.dataset.mode);
            });
        });

        var initial = document.querySelector('.dashboard-tab[data-mode].dashboard-tab-active');
        activate(initial ? initial.dataset.mode : 'custom');
    };

    // ////////////////////////////////////////////////////////////////////////

})(jQuery);
