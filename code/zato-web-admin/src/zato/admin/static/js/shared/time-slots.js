
// /////////////////////////////////////////////////////////////////////////////
//
// Time slots - a list of ranges of the day, each with values of its own, under
// an All day slot that answers whenever no range does. The rate limiting pages
// build their rules on it and the Alerts tab its time-of-day silence settings.
//
// The kit owns the slots themselves - the All day slot, the ranges added with
// the from and to inputs and their time suggestions, the editing of a range's
// times, the delete link and the optional disable link - and knows nothing of
// the values a slot carries. The host builds those in a callback, reads them
// back in another and writes them in a third, so what one slot holds is the
// host's business alone.
//
// Works together with /static/css/shared/time-slots.css and needs the dashboard
// kit's select menu, /static/js/dashboard-kit/select.js, for the time suggestions,
// and /static/js/shared/time-slots-fields.js, which must load before this file,
// for the time inputs and the field group helpers.
//
// How to use:
//
//     var slots = $.fn.zato.time_slots.create({
//         container: some_element,
//         with_disable: true,
//         toggles: [{attr: 'disallowed', off_label: 'Disallow traffic', on_label: 'Allow traffic'}],
//         build_fields: function(slot, is_default) { .. append the slot's inputs .. },
//         read_fields: function(slot) { return {rate: ..}; },
//         write_fields: function(slot, entry) { .. },
//         on_time_change: function(slot) { .. a range's times were edited .. }
//     });
//
//     slots.load(entries);           // [{is_all_day: true, ..}, {time_from: '09:00', time_to: '17:00', ..}]
//     var entries = slots.get_entries();
//
// An entry is the kit's own keys - is_all_day, time_from and time_to for a range,
// disabled with with_disable, one boolean per toggle under its attr - plus what
// read_fields returned, and write_fields gets the very same shape back.
//
// The helpers of time-slots-fields.js build the field groups a slot carries - a
// label, an input, a unit, a select or a switch, in the kit's own classes.
//
// /////////////////////////////////////////////////////////////////////////////

$.namespace('zato.time_slots');

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.time_slots.config = {

    all_day_label: 'All day',
    add_label: '+ Add time range',
    delete_label: 'Delete',
    disable_label: 'Disable',
    enable_label: 'Enable',
    from_placeholder: 'from',
    to_placeholder: 'to',

    // What a range reads as between its two times
    range_separator: ' - ',

    // The times of a range are HH:MM, 24 hours
    time_pattern: /^([01]\d|2[0-3]):([0-5]\d)$/,
    time_length: 5,
    minutes_per_hour: 60,
    minutes_per_day: 24 * 60,

    // How long after a time input loses focus the edit closes, so a click into the other input keeps it open
    close_delay_ms: 200,

    // The three lives of a slot - the one All day slot, a range, and a range still being typed in
    slot_default: 'default',
    slot_range: 'range',
    slot_pending: 'pending',

    disabled_attr: 'disabled',

    // The times offered under the from and to inputs
    time_suggestions: [
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
    ]
};

// /////////////////////////////////////////////////////////////////////////////
// The constructor
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.time_slots.create = function(options) {

    var kit = $.fn.zato.time_slots;
    var config = kit.config;

    var labels = $.extend({
        all_day: config.all_day_label,
        add: config.add_label,
        delete: config.delete_label,
        disable: config.disable_label,
        enable: config.enable_label
    }, options.labels);

    var toggles = options.toggles ? options.toggles : [];
    var with_disable = Boolean(options.with_disable);

    var instance = {};

    // The list the slots live in ..
    var root = document.createElement('div');
    root.className = 'time-slots';
    options.container.appendChild(root);

    // .. and the button a range is begun with, right under it.
    var add_button = document.createElement('span');
    add_button.className = 'time-slots-add';
    add_button.textContent = labels.add;
    add_button.onclick = function() {
        instance.begin_add();
    };
    options.container.appendChild(add_button);

    instance.root = root;
    instance.add_button = add_button;

// /////////////////////////////////////////////////////////////////////////////

    // Flips one of a slot's flags - disabled or one of the host's toggles - and its link's text
    instance.set_flag = function(slot, attr, is_on, link, on_label, off_label) {

        if(is_on) {
            slot.setAttribute('data-' + attr, 'true');
            link.textContent = on_label;
        }
        else {
            slot.removeAttribute('data-' + attr);
            link.textContent = off_label;
        }
    };

// /////////////////////////////////////////////////////////////////////////////

    // One link toggling one flag, in a cell of the actions area
    var add_action_link = function(actions, slot, class_name, attr, off_label, on_label) {

        var cell = document.createElement('div');
        cell.className = 'time-slot-action-cell';

        var link = document.createElement('a');
        link.href = 'javascript:void(0)';
        link.className = class_name;
        link.textContent = off_label;
        link.setAttribute('data-toggle-attr', attr);
        link.onclick = function() {
            var is_on = slot.getAttribute('data-' + attr) === 'true';
            instance.set_flag(slot, attr, !is_on, link, on_label, off_label);
        };

        cell.appendChild(link);
        actions.appendChild(cell);

        var out = link;
        return out;
    };

// /////////////////////////////////////////////////////////////////////////////

    var add_pipe = function(actions) {
        var pipe = document.createElement('span');
        pipe.className = 'time-slot-action-pipe';
        pipe.textContent = '|';
        actions.appendChild(pipe);
    };

// /////////////////////////////////////////////////////////////////////////////

    // Builds one slot - the All day one or a range - with the host's fields in the middle
    var build_slot = function(time_from, time_to, is_default) {

        var slot = document.createElement('div');
        slot.className = 'time-slot';

        if(is_default) {
            slot.setAttribute('data-slot-type', config.slot_default);
        }
        else {
            slot.setAttribute('data-slot-type', config.slot_range);
            slot.setAttribute('data-time-from', time_from);
            slot.setAttribute('data-time-to', time_to);
        }

        var time_area = document.createElement('div');
        time_area.className = 'time-slot-time';

        var label = document.createElement('span');
        label.className = 'time-slot-time-label';
        label.textContent = is_default ? labels.all_day : kit.range_label(time_from, time_to);
        time_area.appendChild(label);

        // A range's times are edited in place, the All day slot has none
        if(!is_default) {
            label.classList.add('time-slot-time-label-editable');
            label.onclick = function() {
                instance.edit_time(slot, time_area, label);
            };
        }

        slot.appendChild(time_area);

        options.build_fields(slot, is_default);

        var actions = document.createElement('div');
        actions.className = 'time-slot-actions';

        var needs_pipe = false;

        toggles.forEach(function(toggle) {
            if(needs_pipe) {
                add_pipe(actions);
            }
            add_action_link(actions, slot, 'time-slot-toggle', toggle.attr, toggle.off_label, toggle.on_label);
            needs_pipe = true;
        });

        if(with_disable) {
            if(needs_pipe) {
                add_pipe(actions);
            }
            add_action_link(actions, slot, 'time-slot-disable', config.disabled_attr, labels.disable, labels.enable);
            needs_pipe = true;
        }

        if(!is_default) {
            if(needs_pipe) {
                add_pipe(actions);
            }

            var delete_cell = document.createElement('div');
            delete_cell.className = 'time-slot-action-cell';

            var delete_link = document.createElement('a');
            delete_link.href = 'javascript:void(0)';
            delete_link.className = 'time-slot-delete';
            delete_link.textContent = labels.delete;
            delete_link.onclick = function() {
                root.removeChild(slot);
            };

            delete_cell.appendChild(delete_link);
            actions.appendChild(delete_cell);
        }

        slot.appendChild(actions);
        root.appendChild(slot);

        // A slot built into a list already on screen locks its cells now, one built
        // before the list is attached waits for the host to call lock_widths
        if(slot.offsetParent !== null) {
            kit.lock_action_cells(slot);
        }

        var out = slot;
        return out;
    };

// /////////////////////////////////////////////////////////////////////////////

    instance.add_slot = function(time_from, time_to) {
        var out = build_slot(time_from, time_to, false);
        return out;
    };

// /////////////////////////////////////////////////////////////////////////////

    instance.lock_widths = function() {
        kit.lock_action_cells(root);
    };

// /////////////////////////////////////////////////////////////////////////////

    // Swaps a range's label for two inputs until both hold a time or the edit is left
    instance.edit_time = function(slot, time_area, label) {

        if(time_area.querySelector('.time-slot-time-input')) {
            return;
        }

        label.style.display = 'none';

        var from_input = kit.build_time_input(config.from_placeholder, slot.getAttribute('data-time-from'));
        var to_input = kit.build_time_input(config.to_placeholder, slot.getAttribute('data-time-to'));

        var dash = document.createElement('span');
        dash.className = 'time-slot-time-dash';
        dash.textContent = '-';

        time_area.appendChild(from_input);
        time_area.appendChild(dash);
        time_area.appendChild(to_input);

        var is_finished = false;

        var finish = function() {

            is_finished = true;

            var new_from = from_input.value;
            var new_to = to_input.value;

            var has_new_times = config.time_pattern.test(new_from) && config.time_pattern.test(new_to);

            if(has_new_times) {
                slot.setAttribute('data-time-from', new_from);
                slot.setAttribute('data-time-to', new_to);
                label.textContent = kit.range_label(new_from, new_to);
            }

            time_area.removeChild(from_input);
            time_area.removeChild(dash);
            time_area.removeChild(to_input);

            label.style.display = '';
            kit.hide_menu();

            // The host may size a range's own fields by its length
            if(has_new_times && options.on_time_change) {
                options.on_time_change(slot);
            }
        };

        // Focus moving from one input to the other is not the end of the edit
        var try_close = function() {
            setTimeout(function() {
                if(is_finished) {
                    return;
                }
                if(!time_area.querySelector('.time-slot-time-input:focus')) {
                    finish();
                }
            }, config.close_delay_ms);
        };

        var show_to_menu = function() {
            kit.show_menu(to_input, '', function(selected_value) {
                to_input.value = selected_value;
                finish();
            });
        };

        var show_from_menu = function() {
            kit.show_menu(from_input, '', function(selected_value) {
                from_input.value = selected_value;
                to_input.focus();
                setTimeout(show_to_menu, 0);
            });
        };

        from_input.onkeydown = function(event) {
            kit.filter_time_key(event);
            if(event.key === 'Escape') {
                finish();
            }
        };

        to_input.onkeydown = function(event) {
            kit.filter_time_key(event);
            if(event.key === 'Enter') {
                event.preventDefault();
                finish();
            }
            if(event.key === 'Escape') {
                finish();
            }
        };

        from_input.onfocus = show_from_menu;
        to_input.onfocus = show_to_menu;

        from_input.onblur = function() {
            kit.validate_time_input(from_input);
            try_close();
        };

        to_input.onblur = function() {
            kit.validate_time_input(to_input);
            try_close();
        };

        from_input.focus();
        from_input.select();
    };

// /////////////////////////////////////////////////////////////////////////////

    // Adds a row of two time inputs that turns into a range once both hold a time
    instance.begin_add = function() {

        var existing_input = root.querySelector('.time-slot-time-input');
        if(existing_input) {
            existing_input.focus();
            return;
        }

        var pending = document.createElement('div');
        pending.className = 'time-slot';
        pending.setAttribute('data-slot-type', config.slot_pending);

        var time_area = document.createElement('div');
        time_area.className = 'time-slot-time';

        var from_input = kit.build_time_input(config.from_placeholder, '');
        var to_input = kit.build_time_input(config.to_placeholder, '');

        var dash = document.createElement('span');
        dash.className = 'time-slot-time-dash';
        dash.textContent = '-';

        time_area.appendChild(from_input);
        time_area.appendChild(dash);
        time_area.appendChild(to_input);
        pending.appendChild(time_area);
        root.appendChild(pending);

        var cancel = function() {
            kit.hide_menu();
            root.removeChild(pending);
        };

        var commit = function() {

            var from_value = from_input.value;
            var to_value = to_input.value;

            if(!config.time_pattern.test(from_value) || !config.time_pattern.test(to_value)) {
                return;
            }

            kit.hide_menu();
            root.removeChild(pending);
            instance.add_slot(from_value, to_value);
        };

        var show_to_menu = function() {
            kit.show_menu(to_input, to_input.value, function(selected_value) {
                to_input.value = selected_value;
                commit();
            });
        };

        var show_from_menu = function() {
            kit.show_menu(from_input, from_input.value, function(selected_value) {
                from_input.value = selected_value;
                to_input.focus();

                // The pick has just closed the menu, the to input gets its own a tick later
                setTimeout(show_to_menu, 0);
            });
        };

        from_input.onfocus = show_from_menu;
        from_input.oninput = show_from_menu;
        from_input.onkeydown = function(event) {
            kit.filter_time_key(event);
            if(event.key === 'Escape') {
                cancel();
            }
        };
        from_input.onblur = function() {
            kit.validate_time_input(from_input);
        };

        to_input.onfocus = show_to_menu;
        to_input.oninput = show_to_menu;
        to_input.onkeydown = function(event) {
            kit.filter_time_key(event);
            if(event.key === 'Enter') {
                event.preventDefault();
                commit();
            }
            if(event.key === 'Escape') {
                cancel();
            }
        };
        to_input.onblur = function() {
            kit.validate_time_input(to_input);
        };

        from_input.focus();
    };

// /////////////////////////////////////////////////////////////////////////////

    // Every slot but a pending one, the All day slot first
    instance.slots = function() {
        var out = root.querySelectorAll('.time-slot:not([data-slot-type="' + config.slot_pending + '"])');
        return out;
    };

// /////////////////////////////////////////////////////////////////////////////

    instance.get_entries = function() {

        var out = [];
        var slots = instance.slots();

        for(var idx = 0; idx < slots.length; idx++) {

            var slot = slots[idx];
            var is_all_day = slot.getAttribute('data-slot-type') === config.slot_default;

            var entry = {is_all_day: is_all_day};

            if(with_disable) {
                entry[config.disabled_attr] = slot.getAttribute('data-' + config.disabled_attr) === 'true';
            }

            toggles.forEach(function(toggle) {
                entry[toggle.attr] = slot.getAttribute('data-' + toggle.attr) === 'true';
            });

            $.extend(entry, options.read_fields(slot));

            if(!is_all_day) {
                entry.time_from = slot.getAttribute('data-time-from');
                entry.time_to = slot.getAttribute('data-time-to');
            }

            out.push(entry);
        }

        return out;
    };

// /////////////////////////////////////////////////////////////////////////////

    // Writes one entry's flags and fields into a slot
    var write_slot = function(slot, entry) {

        options.write_fields(slot, entry);

        var links = slot.querySelectorAll('a[data-toggle-attr]');

        for(var idx = 0; idx < links.length; idx++) {
            var link = links[idx];
            var attr = link.getAttribute('data-toggle-attr');

            if(entry[attr]) {
                link.onclick();
            }
        }
    };

// /////////////////////////////////////////////////////////////////////////////

    // Fills the list from entries - the All day entry goes into the All day slot, every other one adds a range
    instance.load = function(entries) {

        entries.forEach(function(entry) {

            var slot;

            if(entry.is_all_day) {
                slot = instance.default_slot;
            }
            else {
                slot = instance.add_slot(entry.time_from, entry.time_to);
            }

            write_slot(slot, entry);
        });
    };

// /////////////////////////////////////////////////////////////////////////////

    // Every range added so far goes, the All day slot stays
    instance.clear_ranges = function() {

        var ranges = root.querySelectorAll('.time-slot:not([data-slot-type="' + config.slot_default + '"])');

        for(var idx = 0; idx < ranges.length; idx++) {
            root.removeChild(ranges[idx]);
        }
    };

// /////////////////////////////////////////////////////////////////////////////

    instance.default_slot = build_slot('', '', true);

    var out = instance;
    return out;
};

// /////////////////////////////////////////////////////////////////////////////
