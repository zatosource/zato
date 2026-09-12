
// /////////////////////////////////////////////////////////////////////////////
//
// Alerts tab - the time slots kind of its popovers, in a file of its own next to
// common/alerts-tab.js, which registers it and needs it loaded first.
//
// A popover line with a slots field opens the time slots kit of shared/time-slots.js
// instead of a row of numbers - the All day slot carries the line's own switch and
// duration, the fields the line already has on the form, and every range of the day
// added under it carries its own, the ranges kept as one JSON list in the hidden
// slots field, each with its two times, its switch and its duration in seconds.
//
// /////////////////////////////////////////////////////////////////////////////

$.namespace('zato.alerts_tab');

// The relabel function of each slot's unit select, run again when its options are rebuilt
$.fn.zato.alerts_tab.slot_relabels = new WeakMap();

// /////////////////////////////////////////////////////////////////////////////

// The duration fields of a slots line - the one the All day slot edits and the unit select next to it
$.fn.zato.alerts_tab.slots_duration_field = function(line) {

    var settings = $.fn.zato.alerts_tab.settings;
    var out = null;

    line.fields.forEach(function(field_name) {
        if(settings.field_kinds[field_name] === settings.duration_kind) {
            out = field_name;
        }
    });

    return out;
}

// A number of seconds as a count and the largest unit dividing it evenly, the smallest unit when none does
$.fn.zato.alerts_tab.split_duration = function(seconds) {

    var units = $.fn.zato.alerts_tab.settings.duration_units;
    var out = {count: seconds / units[0][1], unit: units[0][0]};

    units.forEach(function(unit) {
        var unit_name = unit[0];
        var unit_seconds = unit[1];

        if(seconds % unit_seconds === 0) {
            out = {count: seconds / unit_seconds, unit: unit_name};
        }
    });

    return out;
}

// The seconds a count of a unit stands for
$.fn.zato.alerts_tab.join_duration = function(count, unit_name) {

    var out = 0;

    $.fn.zato.alerts_tab.settings.duration_units.forEach(function(unit) {
        if(unit[0] === unit_name) {
            out = count * unit[1];
        }
    });

    return out;
}

// The ranges kept in a line's hidden slots field
$.fn.zato.alerts_tab.read_slots = function(line) {
    var out = JSON.parse($.fn.zato.alerts_tab.field(line.slots_field).val());
    return out;
}

// The units a slot's duration may be in - the All day slot has them all, a range only those
// shorter than the range itself, an hour being no unit for a range of one hour
$.fn.zato.alerts_tab.slot_unit_options = function(line, slot) {

    var tab = $.fn.zato.alerts_tab;
    var kit = $.fn.zato.time_slots;
    var is_default = slot.getAttribute('data-slot-type') === kit.config.slot_default;

    var range_seconds = 0;
    if(!is_default) {
        var range_minutes = kit.range_minutes(slot.getAttribute('data-time-from'), slot.getAttribute('data-time-to'));
        range_seconds = range_minutes * tab.config.seconds_per_minute;
    }

    var unit_seconds = {};
    tab.settings.duration_units.forEach(function(unit) {
        unit_seconds[unit[0]] = unit[1];
    });

    var out = [];
    tab.field(line.unit_field).find('option').each(function() {
        if(is_default || unit_seconds[this.value] < range_seconds) {
            out.push({value: this.value, label: this.textContent});
        }
    });

    // The smallest unit stays whatever the range, a range shorter than it being one of a minute
    if(out.length === 0) {
        var first = tab.field(line.unit_field).find('option').first();
        out.push({value: first.val(), label: first.text()});
    }

    return out;
}

// Fills a slot's unit select with the units its range can hold, keeping the picked unit when it may
$.fn.zato.alerts_tab.fill_unit_options = function(line, slot, unit_select, unit_name) {

    var options = $.fn.zato.alerts_tab.slot_unit_options(line, slot);

    unit_select.textContent = '';
    options.forEach(function(item) {
        var option = document.createElement('option');
        option.value = item.value;
        option.textContent = item.label;
        unit_select.appendChild(option);
    });

    // A unit the range no longer holds gives way to the largest one it does
    var has_unit = false;
    options.forEach(function(item) {
        if(item.value === unit_name) {
            has_unit = true;
        }
    });

    unit_select.value = has_unit ? unit_name : options[options.length - 1].value;
}

// Builds the switch and the duration of one slot - the labels are the line's own fields' labels,
// the unit select holds the units the slot's range can, out of the form's unit select
$.fn.zato.alerts_tab.build_slot_fields = function(line, slot) {

    var tab = $.fn.zato.alerts_tab;
    var kit = $.fn.zato.time_slots;
    var settings = tab.settings;
    var duration_field = tab.slots_duration_field(line);

    var switch_group = kit.add_group(slot);
    kit.add_switch(switch_group, tab.config.slot_is_on, true, settings.field_labels[line.off_field]);

    var duration_group = kit.add_group(slot);
    kit.add_text(duration_group, settings.field_labels[duration_field], 'label');
    var count_input = kit.add_input(duration_group, duration_field, tab.field(duration_field).val());
    var unit_select = kit.add_select(duration_group, line.unit_field, []);

    tab.fill_unit_options(line, slot, unit_select, tab.field(line.unit_field).val());
    tab.slot_relabels.set(slot, tab.forms.bindUnitLabels(count_input, unit_select));
}

// A range's times were edited - its unit select offers what the new length can hold
$.fn.zato.alerts_tab.on_slot_time_change = function(line, slot) {

    var tab = $.fn.zato.alerts_tab;
    var kit = $.fn.zato.time_slots;
    var unit_select = kit.field(slot, line.unit_field);

    tab.fill_unit_options(line, slot, unit_select, unit_select.value);
    tab.slot_relabels.get(slot)();
}

// Fills the slots kit of a line's popover - the All day slot from the line's own fields, the ranges from the slots field
$.fn.zato.alerts_tab.load_slots = function(line, slots) {

    var tab = $.fn.zato.alerts_tab;
    var kit = $.fn.zato.time_slots;
    var duration_field = tab.slots_duration_field(line);

    var default_slot = slots.default_slot;
    kit.field(default_slot, tab.config.slot_is_on).checked = tab.field(line.off_field).is(':checked');
    kit.field(default_slot, duration_field).value = tab.field(duration_field).val();
    kit.field(default_slot, line.unit_field).value = tab.field(line.unit_field).val();

    tab.read_slots(line).forEach(function(entry) {
        var slot = slots.add_slot(entry[tab.config.slot_time_from], entry[tab.config.slot_time_to]);
        var duration = tab.split_duration(entry[tab.config.slot_seconds]);

        kit.field(slot, tab.config.slot_is_on).checked = entry[tab.config.slot_is_on];
        tab.fill_unit_options(line, slot, kit.field(slot, line.unit_field), duration.unit);

        // Set by hand rather than typed, so the unit select is told to read with the count itself
        var count_input = kit.field(slot, duration_field);
        count_input.value = duration.count;
        count_input.dispatchEvent(new Event('input'));
    });
}

// Writes the slots kit of a line's popover back - the All day slot into the line's own fields, the ranges into the slots field
$.fn.zato.alerts_tab.save_slots = function(line, slots) {

    var tab = $.fn.zato.alerts_tab;
    var kit = $.fn.zato.time_slots;
    var duration_field = tab.slots_duration_field(line);
    var ranges = [];

    slots.get_entries().forEach(function(entry) {

        var slot = entry.slot;
        var is_on = kit.field(slot, tab.config.slot_is_on).checked;
        var count = parseInt(kit.field(slot, duration_field).value);
        var unit_name = kit.field(slot, line.unit_field).value;

        if(entry.is_all_day) {
            tab.field(line.off_field).prop('checked', is_on);
            tab.field(duration_field).val(count);
            tab.field(line.unit_field).val(unit_name);
            return;
        }

        var range = {};
        range[tab.config.slot_time_from] = entry.time_from;
        range[tab.config.slot_time_to] = entry.time_to;
        range[tab.config.slot_is_on] = is_on;
        range[tab.config.slot_seconds] = tab.join_duration(count, unit_name);
        ranges.push(range);
    });

    tab.field(line.slots_field).val(JSON.stringify(ranges));
}

// Registers the time slots kind with the micro-forms kit - build makes the slots list
// in the popover, save writes it back when the popover is answered
$.fn.zato.alerts_tab.register_slots_kind = function() {

    var tab = $.fn.zato.alerts_tab;

    tab.forms.registerKind(tab.settings.slots_kind, {

        build: function(field_spec, row) {

            var line = field_spec.line;

            // The kit dresses its inputs and selects itself, the popover's own input styles stay off them
            row.classList.add(tab.config.slots_field_class);

            var slots = $.fn.zato.time_slots.create({
                container: row,
                build_fields: function(slot) {
                    tab.build_slot_fields(line, slot);
                },
                on_time_change: function(slot) {
                    tab.on_slot_time_change(line, slot);
                },
                read_fields: function(slot) {
                    var out = {slot: slot};
                    return out;
                },
                write_fields: function() {
                }
            });

            tab.load_slots(line, slots);
            tab.state.slots_kits[line.name] = slots;
        },

        save: function(popper, field_spec) {
            var line = field_spec.line;
            tab.save_slots(line, tab.state.slots_kits[line.name]);
        }
    });
}

// /////////////////////////////////////////////////////////////////////////////
