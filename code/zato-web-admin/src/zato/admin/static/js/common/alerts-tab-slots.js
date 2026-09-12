
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

// Builds the switch and the duration of one slot - the labels are the line's own fields' labels,
// the unit select clones the options of the form's unit select
$.fn.zato.alerts_tab.build_slot_fields = function(line, slot) {

    var tab = $.fn.zato.alerts_tab;
    var kit = $.fn.zato.time_slots;
    var settings = tab.settings;
    var duration_field = tab.slots_duration_field(line);

    var switch_group = kit.add_group(slot);
    kit.add_switch(switch_group, tab.config.slot_is_on, true, settings.field_labels[line.off_field]);

    var options = [];
    tab.field(line.unit_field).find('option').each(function() {
        options.push({value: this.value, label: this.textContent});
    });

    var duration_group = kit.add_group(slot);
    kit.add_text(duration_group, settings.field_labels[duration_field], 'label');
    kit.add_input(duration_group, duration_field, tab.field(duration_field).val());
    kit.add_select(duration_group, line.unit_field, options);
    kit.field(slot, line.unit_field).value = tab.field(line.unit_field).val();
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
        kit.field(slot, duration_field).value = duration.count;
        kit.field(slot, line.unit_field).value = duration.unit;
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
