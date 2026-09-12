
// /////////////////////////////////////////////////////////////////////////////
//
// Time slots - the time suggestions menu, the time inputs and the field group helpers.
// Loads before /static/js/shared/time-slots.js, which holds the constructor.
//
// /////////////////////////////////////////////////////////////////////////////

$.namespace('zato.time_slots');

// /////////////////////////////////////////////////////////////////////////////
// The time suggestions menu
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.time_slots.showMenu = function(anchor, filterText, onSelect) {
    $.fn.zato.dashboard_kit.select.show_menu({
        anchor: anchor,
        groups: $.fn.zato.time_slots.config.timeSuggestions,
        filter: filterText,
        on_select: onSelect,
        excluded: {},
        keep_open: false,
        toggle_pick: false,
        item_style: 'value_label',
        with_filter: false
    });
};

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.time_slots.hideMenu = function() {
    $.fn.zato.dashboard_kit.select.hide_menu();
};

// /////////////////////////////////////////////////////////////////////////////

// Lets only digits into a time input and puts the colon in after the hour
$.fn.zato.time_slots.filterTimeKey = function(event) {

    var config = $.fn.zato.time_slots.config;
    var input = event.target;
    var key = event.key;

    if(config.passthroughKeys.indexOf(key) !== -1) {
        return;
    }

    if(!config.digitPattern.test(key)) {
        event.preventDefault();
        return;
    }

    var current = input.value;

    if(current.length === 2) {
        if(current.indexOf(':') === -1) {
            input.value = current + ':';
        }
    }
};

// /////////////////////////////////////////////////////////////////////////////

// Empties a time input holding anything but HH:MM
$.fn.zato.time_slots.validateTimeInput = function(input) {

    var value = input.value;

    if(value === '') {
        return;
    }

    if(!$.fn.zato.time_slots.config.timePattern.test(value)) {
        input.value = '';
    }
};

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.time_slots.buildTimeInput = function(placeholder, value) {

    var input = document.createElement('input');
    input.type = 'text';
    input.className = 'time-slot-time-input';
    input.placeholder = placeholder;
    input.value = value;
    input.maxLength = $.fn.zato.time_slots.config.timeLength;

    var out = input;
    return out;
};

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.time_slots.rangeLabel = function(timeFrom, timeTo) {
    var out = timeFrom + $.fn.zato.time_slots.config.rangeSeparator + timeTo;
    return out;
};

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.time_slots.hhMmToMinutes = function(hhMm) {
    var parts = hhMm.split(':');
    var hours = parseInt(parts[0]);
    var minutes = parseInt(parts[1]);

    var out = hours * $.fn.zato.time_slots.config.minutesPerHour + minutes;
    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// How many minutes a range spans, one ending at or before its start crossing midnight
$.fn.zato.time_slots.rangeMinutes = function(timeFrom, timeTo) {

    var kit = $.fn.zato.time_slots;
    var fromMinutes = kit.hhMmToMinutes(timeFrom);
    var toMinutes = kit.hhMmToMinutes(timeTo);

    var out = toMinutes - fromMinutes;

    if(out <= 0) {
        out += kit.config.minutesPerDay;
    }

    return out;
};

// /////////////////////////////////////////////////////////////////////////////
// Field group helpers - what a host builds a slot's values with
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.time_slots.addGroup = function(slot) {

    var group = document.createElement('div');
    group.className = 'time-slot-group';
    slot.appendChild(group);

    var out = group;
    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// The role is one of 'label' and 'unit'
$.fn.zato.time_slots.addText = function(group, text, role) {

    var span = document.createElement('span');
    span.className = 'time-slot-' + role;
    span.textContent = text;
    group.appendChild(span);

    var out = span;
    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// A text input named by its data-field, which is what field finds it by
$.fn.zato.time_slots.addInput = function(group, fieldName, value) {

    var input = document.createElement('input');
    input.type = 'text';
    input.className = 'time-slot-input';
    input.setAttribute('data-field', fieldName);
    input.placeholder = value;
    input.value = value;
    group.appendChild(input);

    var out = input;
    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// A select of {value, label} options
$.fn.zato.time_slots.addSelect = function(group, fieldName, options) {

    var select = document.createElement('select');
    select.className = 'time-slot-select';
    select.setAttribute('data-field', fieldName);

    options.forEach(function(item) {
        var option = document.createElement('option');
        option.value = item.value;
        option.textContent = item.label;
        select.appendChild(option);
    });

    group.appendChild(select);

    var out = select;
    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// A switch with its text before it
$.fn.zato.time_slots.addSwitch = function(group, fieldName, isChecked, text) {

    var label = document.createElement('label');
    label.className = 'time-slot-switch';

    var span = document.createElement('span');
    span.className = 'time-slot-switch-text';
    span.textContent = text;
    label.appendChild(span);

    var checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.setAttribute('data-field', fieldName);
    checkbox.checked = isChecked;
    label.appendChild(checkbox);

    group.appendChild(label);

    var out = checkbox;
    return out;
};

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.time_slots.field = function(slot, fieldName) {
    var out = slot.querySelector('[data-field="' + fieldName + '"]');
    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// Sets the width of every action cell under the element to what it is now, so a link
// whose text changes when toggled never moves its neighbours
$.fn.zato.time_slots.lockActionCells = function(element) {

    var cells = element.querySelectorAll('.time-slot-action-cell');

    for(var idx = 0; idx < cells.length; idx++) {
        var cell = cells[idx];
        cell.style.width = cell.offsetWidth + 'px';
    }
};

// /////////////////////////////////////////////////////////////////////////////
