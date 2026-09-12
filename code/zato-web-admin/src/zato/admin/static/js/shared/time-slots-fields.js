
// /////////////////////////////////////////////////////////////////////////////
//
// Time slots - the pieces a slot is built of. The time suggestions menu under a
// from or to input, the inputs themselves with their HH:MM filtering, and the
// field group helpers a host builds a slot's values with - a label, an input, a
// unit, a select or a switch, all in the kit's own classes.
//
// Loads before /static/js/shared/time-slots.js, which holds the constructor.
//
// /////////////////////////////////////////////////////////////////////////////

$.namespace('zato.time_slots');

// /////////////////////////////////////////////////////////////////////////////
// The time suggestions menu
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.time_slots.show_menu = function(anchor, filter_text, on_select) {
    $.fn.zato.dashboard_kit.select.show_menu({
        anchor: anchor,
        groups: $.fn.zato.time_slots.config.time_suggestions,
        filter: filter_text,
        on_select: on_select,
        excluded: {},
        keep_open: false,
        toggle_pick: false,
        item_style: 'value_label',
        with_filter: false
    });
};

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.time_slots.hide_menu = function() {
    $.fn.zato.dashboard_kit.select.hide_menu();
};

// /////////////////////////////////////////////////////////////////////////////

// Lets only digits into a time input and puts the colon in after the hour
$.fn.zato.time_slots.filter_time_key = function(event) {

    var input = event.target;
    var key = event.key;

    if(key === 'Backspace' || key === 'Delete' || key === 'ArrowLeft' || key === 'ArrowRight' || key === 'Tab' || key === 'Escape' || key === 'Enter') {
        return;
    }

    if(key < '0' || key > '9') {
        event.preventDefault();
        return;
    }

    var current = input.value;

    if(current.length === 2 && current.indexOf(':') === -1) {
        input.value = current + ':';
    }
};

// /////////////////////////////////////////////////////////////////////////////

// Empties a time input holding anything but HH:MM
$.fn.zato.time_slots.validate_time_input = function(input) {

    var value = input.value;

    if(value === '') {
        return;
    }

    if(!$.fn.zato.time_slots.config.time_pattern.test(value)) {
        input.value = '';
    }
};

// /////////////////////////////////////////////////////////////////////////////

// A from or to input, with the suggestions menu under it
$.fn.zato.time_slots.build_time_input = function(placeholder, value) {

    var input = document.createElement('input');
    input.type = 'text';
    input.className = 'time-slot-time-input';
    input.placeholder = placeholder;
    input.value = value;
    input.maxLength = $.fn.zato.time_slots.config.time_length;

    var out = input;
    return out;
};

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.time_slots.range_label = function(time_from, time_to) {
    var out = time_from + $.fn.zato.time_slots.config.range_separator + time_to;
    return out;
};

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.time_slots.hh_mm_to_minutes = function(hh_mm) {
    var parts = hh_mm.split(':');
    var out = parseInt(parts[0]) * $.fn.zato.time_slots.config.minutes_per_hour + parseInt(parts[1]);
    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// How many minutes a range of the day spans, one ending at or before its start crossing midnight
$.fn.zato.time_slots.range_minutes = function(time_from, time_to) {

    var kit = $.fn.zato.time_slots;
    var out = kit.hh_mm_to_minutes(time_to) - kit.hh_mm_to_minutes(time_from);

    if(out <= 0) {
        out += kit.config.minutes_per_day;
    }

    return out;
};

// /////////////////////////////////////////////////////////////////////////////
// Field group helpers - what a host builds a slot's values with
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.time_slots.add_group = function(slot) {

    var group = document.createElement('div');
    group.className = 'time-slot-group';
    slot.appendChild(group);

    var out = group;
    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// A label before an input or a unit after it - the role is one of 'label' and 'unit'
$.fn.zato.time_slots.add_text = function(group, text, role) {

    var span = document.createElement('span');
    span.className = 'time-slot-' + role;
    span.textContent = text;
    group.appendChild(span);

    var out = span;
    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// A text input named by its data-field, which is what read_fields finds it by
$.fn.zato.time_slots.add_input = function(group, field_name, value) {

    var input = document.createElement('input');
    input.type = 'text';
    input.className = 'time-slot-input';
    input.setAttribute('data-field', field_name);
    input.placeholder = value;
    input.value = value;
    group.appendChild(input);

    var out = input;
    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// A select of options, each either a string standing for both value and label, or a {value, label} pair
$.fn.zato.time_slots.add_select = function(group, field_name, options) {

    var select = document.createElement('select');
    select.className = 'time-slot-select';
    select.setAttribute('data-field', field_name);

    options.forEach(function(item) {

        var option = document.createElement('option');

        if(typeof item === 'string') {
            option.value = item;
            option.textContent = item;
        }
        else {
            option.value = item.value;
            option.textContent = item.label;
        }

        select.appendChild(option);
    });

    group.appendChild(select);

    var out = select;
    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// A switch with its text before it
$.fn.zato.time_slots.add_switch = function(group, field_name, is_checked, text) {

    var label = document.createElement('label');
    label.className = 'time-slot-switch';

    var span = document.createElement('span');
    span.className = 'time-slot-switch-text';
    span.textContent = text;
    label.appendChild(span);

    var checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.setAttribute('data-field', field_name);
    checkbox.checked = is_checked;
    label.appendChild(checkbox);

    group.appendChild(label);

    var out = checkbox;
    return out;
};

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.time_slots.field = function(slot, field_name) {
    var out = slot.querySelector('[data-field="' + field_name + '"]');
    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// Sets the width of every action cell to what it is now, so a link whose text
// changes when toggled never moves its neighbours
$.fn.zato.time_slots.lock_action_cells = function(root) {

    var cells = root.querySelectorAll('.time-slot-action-cell');

    for(var idx = 0; idx < cells.length; idx++) {
        var cell = cells[idx];
        if(!cell.style.width) {
            cell.style.width = cell.offsetWidth + 'px';
        }
    }
};
